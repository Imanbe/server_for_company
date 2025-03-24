import json
import signal
import asyncio
import time

import redis.asyncio as redis
from fast_bitrix24 import BitrixAsync

from ..Configs.config import settings
from ..Logs.logging_setup import app_logger as logger
from ..Utils.utils import load_handlers
from ..Metrics.metrics import TASK_PROCESSED, TASK_PROCESSED_TIME, TASKS_IN_QUEUE, REDIS_ERRORS

HANDLERS = load_handlers(settings.HANDLERS)

stop_event = asyncio.Event()


def shutdown():
    stop_event.set()


signal.signal(signal.SIGINT, lambda *_: shutdown())
signal.signal(signal.SIGTERM, lambda *_: shutdown())


async def process_task(task: dict, b: BitrixAsync) -> bool:
    task_type = task.get('task_type')
    payload = task.get('payload', {})
    handler = HANDLERS.get(task_type)
    if not handler:
        logger.error('Unknown task type', extra={'task_type': task_type})
        TASK_PROCESSED.labels(status='failed').inc()
        return False
    start_time = time.time()
    try:
        result = await handler(payload, b)
        TASK_PROCESSED.labels(status='successful' if result else 'failed').inc()
        TASK_PROCESSED_TIME.observe(time.time() - start_time)
        return result
    except Exception as e:
        logger.error(f'Error in process task: {e}', extra={'task': task}, exc_info=True)
        TASK_PROCESSED.labels(status='failed').inc()
        TASK_PROCESSED_TIME.observe(time.time() - start_time)
        raise e


async def worker():
    logger.info('Worker started for carex_main')
    b = BitrixAsync(settings.WEBHOOK_CAREX)
    while not stop_event.set():
        while True:
            try:
                async with redis.Redis.from_url(settings.REDIS_URL) as r:
                    item = await r.brpop(settings.TASKS, timeout=5)
                    if not item:
                        logger.info('No tasks in queue, waiting...')
                        TASKS_IN_QUEUE.set(0)  # Обновляем метрику, если очередь пуста
                        continue
                    _, task_json = item
                    task = json.loads(task_json)
                    logger.info(f"Received task: {task}", extra={'task': task})
                    success = await process_task(task, b)
                    queue_length = await r.llen(settings.TASKS)
                    TASKS_IN_QUEUE.set(queue_length) # Обновляем метрику после обработки
                    if not success:
                        await r.rpush(settings.TASKS_ERROR, task_json)
                        queue_length_err = await r.llen(settings.TASKS_ERROR)
                        TASKS_IN_QUEUE.set(queue_length_err)
                        logger.warning(f"Task failed and moved to {settings.TASKS_ERROR}", extra={"task": task})
                        continue
                    logger.info(f'Task completed successfully: {task.get("task_type")}', extra={'task': task})
            except redis.RedisError as e:
                REDIS_ERRORS.inc()  # Считаем ошибки Redis
                logger.error(f"Redis connection error: {e}", exc_info=True)
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                await asyncio.sleep(1)

if __name__ == '__main__':
    asyncio.run(worker())
