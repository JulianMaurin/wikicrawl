from unittest import mock

import pytest
from celery_once import AlreadyQueued
from wikicrawl.workers.crawler import crawl, crawl_callback

from .conftest import celery


def test_task(celery):
    with (mock.patch("wikicrawl.workers.crawler.crawl_page") as mock_crawl):
        crawl(page_name="page name")
        mock_crawl.assert_called_once_with(page_name="page name", callback=mock.ANY, logger=mock.ANY)


def test_task_error(celery):
    with (
        mock.patch("wikicrawl.workers.crawler.crawl_page", side_effect=Exception()),
        pytest.raises(Exception),
    ):
        crawl(page_name="page name")


def test_callback():
    mock_logger = mock.MagicMock()
    with (
        mock.patch("wikicrawl.workers.crawler.page_names_from_urls"),
        mock.patch("wikicrawl.workers.crawler.filter_pages_not_recorded", return_value=["1", "2", "3"]),
        mock.patch("wikicrawl.workers.crawler.record.delay") as mock_record,
        mock.patch("wikicrawl.workers.crawler.crawl.delay") as mock_crawl,
    ):
        crawl_callback(page_name="1", page_content="1 content", logger=mock_logger)
        record_calls = [
            mock.call(origin_page_name="1", target_page_name="2"),
            mock.call(origin_page_name="1", target_page_name="3"),
        ]
        mock_record.assert_has_calls(record_calls, any_order=True)
        crawl_calls = [
            mock.call(page_name="2"),
            mock.call(page_name="3"),
        ]
        mock_crawl.assert_has_calls(crawl_calls, any_order=True)


def test_callback_already_queued():
    mock_logger = mock.MagicMock()
    with (
        mock.patch("wikicrawl.workers.crawler.page_names_from_urls"),
        mock.patch("wikicrawl.workers.crawler.filter_pages_not_recorded", return_value=["2"]),
        mock.patch("wikicrawl.workers.crawler.record.delay"),
        mock.patch("wikicrawl.workers.crawler.crawl.delay", side_effect=AlreadyQueued(countdown=0)),
    ):
        crawl_callback(page_name="1", page_content="1 content", logger=mock_logger)
