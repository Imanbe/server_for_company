from prometheus_client import Counter, Histogram, Gauge

# Метрики для задач
TASK_PROCESSED = Counter(
    "company_tasks_processed_total", "Total number of tasks processed", ["status"]
)

TASK_PROCESSED_TIME = Histogram(
    "company_task_processing_time_second",
    "Time spent processing tasks",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, float("inf")],
)

TASKS_IN_QUEUE = Gauge("company_tasks_in_queue", "Number of tasks currently in queue")

TASKS_IN_QUEUE_ERRORS = Gauge(
    "company_tasks_in_queue_errors", "Number of tasks currently in queue_errors"
)

# Метрики для ошибок
REDIS_ERRORS = Counter(
    "company_redis_errors_total", "Total number of Redis-related errors"
)

BITRIX_ERRORS = Counter(
    "company_bitrix_errors_total", "Total number of Bitrix API errors"
)
