from __future__ import annotations

import logging
import time

from celery_once import AlreadyQueued, QueueOnce
from wikicrawl.core.parser import parse_href_from_link_tags
from wikicrawl.core.wikipedia import page_names_from_urls
from wikicrawl.crawl import asyncio, crawl_page
from wikicrawl.database.dao import filter_pages_not_recorded
from wikicrawl.workers import metrics, settings
from wikicrawl.workers.celery import app
from wikicrawl.workers.recorder import record


@app.task(
    bind=True,
    base=QueueOnce,
    name=settings.WORKER_QUEUE_CRAWL_TASK,
    autoretry_for=(Exception,),
    max_retries=2,
    rate_limit=settings.WORKER_QUEUE_CRAWL_RATE_LIMIT,
)
def crawl(self, page_name: str) -> None:
    start = time.perf_counter()
    try:
        logger = logging.LoggerAdapter(
            logging.getLogger("crawl"),
            extra={
                "service": "wikicrawl-worker",
                "task": settings.WORKER_QUEUE_CRAWL_TASK,
                "task_id": self.request.id if self.request else None,
            },
        )
        asyncio.run(async_crawl(page_name=page_name, logger=logger))
        metrics.count(f"{self.name}.success")
    except Exception as err:
        logger.exception("Error crawling page (error: %s).", err.__class__.__name__)
        metrics.count(f"{self.name}.failure")
        raise
    finally:
        metrics.timing(self.name, start)


async def async_crawl(page_name: str, logger: logging.LoggerAdapter) -> None:
    await crawl_page(page_name=page_name, callback=crawl_callback, logger=logger)


def crawl_callback(page_name: str, page_content: str, logger: logging.LoggerAdapter):
    page_names_to_crawl = page_names_from_urls(parse_href_from_link_tags(page_content))
    page_names_to_crawl = filter_pages_not_recorded(list(page_names_to_crawl))
    for page_name_to_crawl in page_names_to_crawl:
        if page_name_to_crawl == page_name:
            continue
        record.delay(origin_page_name=page_name, target_page_name=page_name_to_crawl)
        try:
            crawl.delay(page_name=page_name_to_crawl)
        except AlreadyQueued:
            pass
    else:
        logger.debug("Page already fully crawled (page name: %s).", page_name)
