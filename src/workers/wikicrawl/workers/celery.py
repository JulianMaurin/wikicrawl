import celery
from kombu import Queue
from wikicrawl.core import logging
from wikicrawl.workers import settings

app = celery.Celery(
    "wikicrawl.workers.celery",
    backend="rpc://",
    broker=settings.WORKER_BROKER_URL,
    result_backend=settings.WORKER_RESULT_BACKEND,
)
app.conf.task_queues = [
    Queue(
        settings.WORKER_QUEUE_CRAWL_NAME,
        queue_arguments={
            "x-max-length": settings.WORKER_QUEUE_CRAWL_MAX_LENGTH,
        },
    ),
    Queue(
        settings.WORKER_QUEUE_RECORD_NAME,
        queue_arguments={
            "x-max-length": settings.WORKER_QUEUE_RECORD_MAX_LENGTH,
        },
    ),
]
app.conf.task_routes = {
    settings.WORKER_QUEUE_CRAWL_TASK: {"queue": settings.WORKER_QUEUE_CRAWL_NAME},
    settings.WORKER_QUEUE_RECORD_TASK: {"queue": settings.WORKER_QUEUE_RECORD_NAME},
}
app.conf.ONCE = {
    "backend": "celery_once.backends.Redis",
    "settings": {"url": settings.WORKER_TASK_CACHE_URL, "default_timeout": settings.WORKER_TASK_CACHE_TIMEOUT},
}


@celery.signals.after_setup_logger.connect
def after_setup_logger(*args, **kwargs):
    logging.setup()


@celery.signals.after_setup_task_logger.connect
def after_setup_task_logger(*args, **kwargs):
    logging.setup()
