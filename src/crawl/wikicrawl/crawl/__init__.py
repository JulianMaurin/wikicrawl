from __future__ import annotations

import asyncio
import logging
from typing import Callable, Union

import aiohttp
from wikicrawl.core.utils import chunks
from wikicrawl.crawl import settings
from wikicrawl.crawl.utils import handle_redirect, page_name_to_url

CrawlCallBack = Callable[[str, str, Union[logging.Logger, logging.LoggerAdapter]], None]


class HTTPCrawlError(Exception):
    pass


async def crawl_pages(
    pages_names: list[str],
    callback: CrawlCallBack,
    logger: logging.Logger | None = None,
):
    async_tasks = [
        asyncio.create_task(crawl_page(page_name=page_name, callback=callback, logger=logger))
        for page_name in pages_names
    ]
    for async_tasks_batch in chunks(async_tasks, settings.CRAWL_DOWNLOAD_MAXIMUM_BATCH_SIZE):
        await asyncio.gather(*async_tasks_batch)


async def crawl_page(
    page_name: str, callback: CrawlCallBack, logger: logging.Logger | logging.LoggerAdapter | None = None
):
    page_url = page_name_to_url(page_name=page_name)
    logger = logger or logging.getLogger("crawl")
    logger.debug("Crawl page (url: %s).", page_url)
    async with aiohttp.ClientSession() as session:
        async with session.get(page_url) as response:
            if response.status == 200:
                page_content = await response.text()
                page_name = handle_redirect(page_name, response)
                callback(page_name, page_content, logger)
            elif str(response.status) in settings.CRAWL_SILENT_HTTP_STATUS_CODES:
                pass
            else:
                raise HTTPCrawlError(
                    "Error downloading page (code: %s, url: %s)",
                    response.status,
                    page_url,
                )
