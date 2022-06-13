import asyncio
import logging
import tempfile
from pathlib import Path
from uuid import uuid4

import redis
from wikicrawl.core.parser import parse_href_from_link_tags
from wikicrawl.core.wikipedia import page_names_from_urls
from wikicrawl.crawl import crawl_pages
from wikicrawl.stub import settings
from wikicrawl.stub.generators import WireMock


class Stub:
    def __init__(self, entry_point: str, pages_count: int) -> None:
        self.entry_point = entry_point
        self.expected_pages_count = pages_count
        self.crawled_pages_names: set[str] = set()
        self.generator = WireMock
        self.redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)
        self.redis.flushall()
        self.logger = logging.getLogger("stub")

    def generate(self):
        with tempfile.TemporaryDirectory() as download_directory:
            asyncio.run(self.crawl(download_directory))
            pages_files_paths = [str(Path(download_directory, page_name)) for page_name in self.crawled_pages_names]
            self.generator(pages_files_paths=pages_files_paths).generate()

    async def crawl(self, download_directory: str) -> None:
        self.logger.info(f"Wikipedia crawling start (entry point: {self.entry_point}).")
        await self._crawl([self.entry_point], download_directory)
        self.crawled_pages_names.add(self.entry_point)
        while len(self.crawled_pages_names) < self.expected_pages_count:
            pages_names_to_crawl_next = self.get_pages_names_to_crawl_next() - self.crawled_pages_names
            if not pages_names_to_crawl_next:
                self.logger.warning(
                    "Unable to crawl the expected count of pages. (current pages count: %s)",
                    len(self.crawled_pages_names),
                )
                break
            future_crawled_pages_count = len(pages_names_to_crawl_next) + len(self.crawled_pages_names)
            if future_crawled_pages_count > self.expected_pages_count:
                missing_crawled_pages_count = self.expected_pages_count - len(self.crawled_pages_names)
                pages_names_to_crawl_next = set(sorted(list(pages_names_to_crawl_next))[:missing_crawled_pages_count])
            await self._crawl(list(pages_names_to_crawl_next), download_directory)
            self.crawled_pages_names |= pages_names_to_crawl_next
        self.logger.info("Wikipedia crawling end.")

    async def _crawl(self, pages_names: list[str], download_directory: str) -> None:
        def callback(page_name: str, page_content: str, logger: logging.Logger):
            self.save_page_to_disk(
                page_name=page_name,
                page_content=page_content,
                download_directory=download_directory,
            )
            self.record_pages_links(page_name=page_name, page_content=page_content)

        await crawl_pages(pages_names=pages_names, callback=callback, logger=self.logger)

    def save_page_to_disk(self, page_name: str, page_content: str, download_directory: str) -> None:
        file_path = Path(download_directory, page_name)
        if file_path.exists():
            return
        self.logger.debug("Create file (file path: %s).", file_path)
        with open(file_path, "w+") as stream:
            stream.write(page_content)

    def record_pages_links(self, page_name: str, page_content: str) -> None:
        try:
            self._record_pages_links(page_name=page_name, page_content=page_content)
        except redis.RedisError as err:
            self.logger.exception(
                "Unable to record (page name: %s, error: %s).",
                page_name,
                err.__class__.__name__,
            )

    def _record_pages_links(self, page_name: str, page_content: str) -> None:
        page_names = page_names_from_urls(parse_href_from_link_tags(page_content))
        page_names = list(set(page_names) - {page_name})
        record_key = f"pages-{uuid4()}"
        record_value = settings.STUB_REDIS_KEY_PAGES_SEPARATOR.join(page_names)
        self.logger.debug("Record links (key: %s).", record_key)
        self.redis.set(record_key, record_value)

    def get_pages_names_to_crawl_next(self) -> set[str]:
        try:
            return self._get_pages_names_to_crawl_next()
        except redis.RedisError as err:
            self.logger.exception(
                "Unable to get pages names to crawl next (error: %s).",
                err.__class__.__name__,
            )
            return set()

    def _get_pages_names_to_crawl_next(self) -> set[str]:
        pages_names = set()
        for record_key in self.redis.keys():
            record_values = self.redis.get(record_key)
            if record_values:
                pages_names |= set(record_values.decode().split(settings.STUB_REDIS_KEY_PAGES_SEPARATOR))
            self.redis.delete(record_key)
        return pages_names
