import logging
import time
from typing import Tuple

from celery.worker.request import Request
from celery_batches import Batches
from wikicrawl.database.dao import insert_bulk_relations
from wikicrawl.workers import metrics, settings
from wikicrawl.workers.celery import app


@app.task(
    base=Batches,
    flush_every=settings.WORKER_QUEUE_RECORD_BATCH_SIZE,
    flush_interval=settings.WORKER_QUEUE_RECORD_BATCH_TIMEOUT,
    name=settings.WORKER_QUEUE_RECORD_TASK,
    rate_limit=settings.WORKER_QUEUE_RECORD_RATE_LIMIT,
    autoretry_for=(Exception,),
    max_retries=2,
)
def record(tasks_batch: list[Request]):
    logger = logging.LoggerAdapter(
        logging.getLogger("crawl"),
        extra={
            "task": settings.WORKER_QUEUE_RECORD_TASK,
            "service": "wikicrawl-worker",
        },
    )
    start = time.perf_counter()
    try:
        if tasks_batch:
            _record(tasks_batch, logger)
            metrics.count(f"{settings.WORKER_QUEUE_RECORD_TASK}.success", len(tasks_batch))
    except Exception as err:
        metrics.count(f"{settings.WORKER_QUEUE_RECORD_TASK}.failure", len(tasks_batch))
        logger.exception("Error recording pages relation (error: %s).", err.__class__.__name__)
        raise
    finally:
        metrics.timing(settings.WORKER_QUEUE_RECORD_TASK, start)


def _record(tasks_batch: list[Request], logger: logging.LoggerAdapter):
    relations: list[Tuple[str, str]] = [
        (task.kwargs["origin_page_name"], task.kwargs["target_page_name"]) for task in tasks_batch
    ]
    insert_bulk_relations(relations=relations, logger=logger)
