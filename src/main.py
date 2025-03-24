import json

from fast_bitrix24 import BitrixAsync
from fastapi import FastAPI, Request
import redis.asyncio as redis
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

from Logs.logging_setup import app_logger as logger
from Configs.config import settings, Task
from Metrics.metrics import TASKS_IN_QUEUE, TASKS_IN_QUEUE_ERRORS
from Workers.worker import process_task

app = FastAPI()


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger.info(f"Incoming request: {request.method} {request.url}")
        response = await call_next(request)
        return response


app.add_middleware(LoggingMiddleware)
app.mount("/metrics", make_asgi_app())


@app.post('/CarexRandom')
async def handle_random(deal_id: int, cont_id: int) -> str:
    """
        Обрабатывает запрос на распределение ответсвенных за сделку и контакт.
        Создает задачу и добавляет в очередь TASKS.
        """
    logger.info(
        "Endpoint catch /CarexRandom",
        extra={"deal_id": deal_id, "cont_id": cont_id}
    )
    task_type = 'process_carex_random'
    task = Task(task_type=task_type, payload={'deal_id': deal_id, 'cont_id': cont_id})
    async with redis.Redis.from_url(settings.REDIS_URL) as r:
        await r.rpush(settings.TASKS, json.dumps(task.model_dump()))
        queue_length = await r.llen(settings.TASKS)
        TASKS_IN_QUEUE.set(queue_length)  # Обновляем метрику задач в очереди
        logger.info(
            f"Task added to queue: {settings.TASKS}",
            extra={'task': task.model_dump()}
        )
    return f'processing_task: {task_type}'


@app.get('/retry-errors')
async def retry_errors() -> dict:
    """
    Повторно обрабатывает задачи из очереди TASKS_ERROR.
    Возвращает количество оставшихся задач с ошибкой и успешно выполненных задач.
    """
    b = BitrixAsync(settings.WEBHOOK_CAREX)
    successful_tasks_count = 0

    async with redis.Redis.from_url(settings.REDIS_URL, decode_responses=True) as r:
        # Получаем все задачи из очереди TASKS_ERROR
        error_tasks = await r.lrange(settings.TASKS_ERROR, 0, 20)
        error_tasks_count = len(error_tasks)

        if error_tasks_count == 0:
            return {
                "error_tasks_remaining": 0,
                "successful_tasks": 0,
                "message": "No tasks in error queue"
            }

        # Очищаем очередь перед обработкой, чтобы избежать дублирования
        await r.delete(settings.TASKS_ERROR)

        # Повторно обрабатываем каждую задачу
        for task_json in error_tasks:
            task = json.loads(task_json)
            logger.info("Retrying task from error queue", extra={'task': task})
            success = await process_task(task, b)
            if success:
                successful_tasks_count += 1
            else:
                # Если задача снова не удалась, возвращаем её в TASKS_ERROR
                await r.rpush(settings.TASKS_ERROR, task_json)

        # Обновляем количество оставшихся задач с ошибкой
        error_tasks_remaining = await r.llen(settings.TASKS_ERROR)
        TASKS_IN_QUEUE_ERRORS.set(error_tasks_remaining)

    return {
        "error_tasks_remaining": error_tasks_remaining,
        "successful_tasks": successful_tasks_count,
        "message": f"Processed {error_tasks_count} tasks from error queue"
    }
