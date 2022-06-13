import re
from unittest import mock

import pytest
from aioresponses import aioresponses
from wikicrawl.crawl import HTTPCrawlError, crawl_page, crawl_pages


async def test_crawl_page():
    mock_callback = mock.MagicMock()
    mock_logger = mock.MagicMock()
    page_name = "page name"
    page_content = "page content"

    with aioresponses() as mock_aioresponses:
        mock_aioresponses.get(re.compile(r".*"), status=200, body=page_content)
        await crawl_page(page_name, mock_callback, mock_logger)

    mock_callback.assert_called_once_with(page_name, page_content, mock_logger)
    mock_logger.debug.called_once()


async def test_crawl_page_http_error():
    mock_logger = mock.MagicMock()
    mock_callback = mock.MagicMock()
    with aioresponses() as mock_aioresponses, pytest.raises(HTTPCrawlError):
        mock_aioresponses.get(re.compile(r".*"), status=429)
        await crawl_page("page name", mock_callback, mock_logger)

    mock_callback.assert_not_called()


async def test_crawl_page_silent_http_error():
    mock_logger = mock.MagicMock()
    mock_callback = mock.MagicMock()
    with (
        mock.patch("wikicrawl.crawl.settings.CRAWL_SILENT_HTTP_STATUS_CODES", "404,503"),
        aioresponses() as mock_aioresponses,
    ):
        mock_aioresponses.get(re.compile(r".*"), status=404)
        await crawl_page("page name", mock_callback, mock_logger)

    mock_callback.assert_not_called()


async def test_crawl_pages():
    mock_callback = mock.MagicMock()
    mock_logger = mock.MagicMock()
    with mock.patch("wikicrawl.crawl.crawl_page") as mock_crawl_page:
        await crawl_pages(["1", "2", "3"], mock_callback, mock_logger)

    calls = [
        mock.call(page_name="1", callback=mock_callback, logger=mock_logger),
        mock.call(page_name="2", callback=mock_callback, logger=mock_logger),
        mock.call(page_name="3", callback=mock_callback, logger=mock_logger),
    ]
    mock_crawl_page.assert_has_calls(calls, any_order=True)
