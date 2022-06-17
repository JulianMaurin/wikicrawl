from unittest import mock

import pytest

from wikicrawl.crawl.utils import handle_redirect, page_name_from_url, page_name_to_url


def test_handle_redirect():
    with (
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_DOMAIN", "http://test.com"),
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_PAGE_ENDPOINT", "/v1"),
    ):
        new_page_name = handle_redirect(
            page_name="xxx",
            response=mock.MagicMock(url="http://test.com/v1/abc", history=[mock.MagicMock(status=302)]),
        )

    assert new_page_name == "abc"


def test_page_name_from_url():
    with (
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_DOMAIN", "http://test.com"),
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_PAGE_ENDPOINT", "/v1"),
    ):
        assert page_name_from_url(url="http://test.com/v1/xxx") == "xxx"


def test_page_name_from_url_error():
    with (
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_DOMAIN", "http://test.com"),
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_PAGE_ENDPOINT", "/v1"),
        pytest.raises(Exception),
    ):
        page_name_from_url(url="http://another-domain.com/v1/xxx")


def test_page_name_to_url():
    with (
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_DOMAIN", "http://test.com"),
        mock.patch("wikicrawl.crawl.utils.core_settings.WIKI_PAGE_ENDPOINT", "/v1"),
    ):
        assert page_name_to_url(page_name="xxx") == "http://test.com/v1/xxx"
