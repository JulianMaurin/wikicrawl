from unittest import mock

import redis
from wikicrawl.stub import Stub, settings

from .conftest import fake_redis


def test_generate(fake_redis):
    page_name_1 = "page name 1"
    page_name_2 = "page name 2"
    with (
        mock.patch(
            "wikicrawl.stub.Stub.get_pages_names_to_crawl_next",
            return_value=set([page_name_1, page_name_2]),
        ),
        mock.patch("wikicrawl.stub.crawl_pages", side_effect=mock.AsyncMock()) as mock_crawl_pages,
        mock.patch("wikicrawl.stub.WireMock") as mock_generator,
        mock.patch("wikicrawl.stub.tempfile.TemporaryDirectory") as mock_temp_directory,
    ):
        mock_temp_directory().__enter__.return_value = "/tmp"

        stub = Stub(entry_point=page_name_1, pages_count=10)
        stub.generate()
        crawl_pages_calls = [
            mock.call(pages_names=[page_name_1], callback=mock.ANY, logger=stub.logger),
            mock.call(pages_names=[page_name_2], callback=mock.ANY, logger=stub.logger),
        ]
        mock_crawl_pages.assert_has_awaits(crawl_pages_calls)
        call_args_list = mock_generator.call_args_list
        assert len(call_args_list) == 1
        assert call_args_list[0] == mock.call(pages_files_paths=mock.ANY)
        assert sorted(call_args_list[0][1]["pages_files_paths"]) == [
            f"/tmp/{page_name_1}",
            f"/tmp/{page_name_2}",
        ]
        mock_generator().generate.assert_called_once_with()


async def test_crawl_limit_size(fake_redis):
    pages_names = [f"page name {i}" for i in range(10)]
    with (
        mock.patch(
            "wikicrawl.stub.Stub.get_pages_names_to_crawl_next",
            return_value=set(pages_names),
        ),
        mock.patch("wikicrawl.stub.crawl_pages", side_effect=mock.AsyncMock()) as mock_crawl_pages,
        mock.patch("wikicrawl.stub.WireMock"),
    ):
        stub = Stub(entry_point=pages_names[0], pages_count=2)
        await stub.crawl(download_directory="download_directory")

        crawl_pages_calls = [
            mock.call(pages_names=[pages_names[0]], callback=mock.ANY, logger=stub.logger),
            mock.call(pages_names=[pages_names[1]], callback=mock.ANY, logger=stub.logger),
        ]
        mock_crawl_pages.assert_has_awaits(crawl_pages_calls)


async def test_crawl_callback(fake_redis):
    page_name = "page name"
    page_content = "page content"
    stub = Stub(entry_point=page_name, pages_count=10)

    async def call_callback(*args, **kwargs):
        kwargs["callback"](page_name=page_name, page_content=page_content, logger=mock.MagicMock())

    with (
        mock.patch("wikicrawl.stub.crawl_pages", call_callback),
        mock.patch("wikicrawl.stub.Stub.save_page_to_disk") as mock_save_page_to_disk,
        mock.patch("wikicrawl.stub.Stub.record_pages_links") as mock_record_pages_links,
    ):
        await stub._crawl(pages_names=["a", "b"], download_directory="download_directory")
        mock_save_page_to_disk.assert_called_with(
            page_name=page_name,
            page_content=page_content,
            download_directory="download_directory",
        )
        mock_record_pages_links.assert_called_with(page_name=page_name, page_content=page_content)


def test_save_page_to_disk(fake_redis):
    page_name = "page name"
    page_content = "page content"
    mock_open = mock.mock_open()
    stub = Stub(entry_point=page_name, pages_count=10)
    with mock.patch("wikicrawl.stub.open", mock_open):
        stub.save_page_to_disk(
            page_name=page_name,
            page_content=page_content,
            download_directory="download directory",
        )
    mock_open().write.assert_called_once_with(page_content)


def test_save_page_to_disk_file_exists(fake_redis):
    page_name = "page name"
    page_content = "page content"
    mock_open = mock.mock_open()
    stub = Stub(entry_point=page_name, pages_count=10)
    with (
        mock.patch("wikicrawl.stub.open", mock_open),
        mock.patch("wikicrawl.stub.Path.exists", return_value=True),
    ):
        stub.save_page_to_disk(
            page_name=page_name,
            page_content=page_content,
            download_directory="download directory",
        )
    mock_open().write.assert_not_called()


def test_record_pages_links(fake_redis):
    page_name = "page name"
    page_content = "page content"
    pages_names = set([page_name, "a", "b"])
    stub = Stub(entry_point=page_name, pages_count=10)
    with (
        mock.patch("wikicrawl.stub.page_names_from_urls", return_value=pages_names),
        mock.patch("wikicrawl.stub.uuid4", return_value="xxx"),
    ):
        stub.record_pages_links(page_name=page_name, page_content=page_content)
    assert len(stub.redis.keys()) == 1
    assert stub.redis.get("pages-xxx").decode() == settings.STUB_REDIS_KEY_PAGES_SEPARATOR.join(
        pages_names - {page_name}
    )


def test_record_pages_links_redis_error(fake_redis):
    page_name = "page name"
    page_content = "page content"
    stub = Stub(entry_point=page_name, pages_count=10)
    stub.logger = mock.MagicMock()
    with mock.patch("wikicrawl.stub.Stub._record_pages_links", side_effect=redis.RedisError):
        stub.record_pages_links(page_name=page_name, page_content=page_content)
        stub.logger.exception.assert_called_once()


def test_get_pages_names_to_crawl_next(fake_redis):
    page_name = "page name"
    pages_names_1 = {
        "a",
        "b",
    }
    pages_names_2 = {
        "c",
        "d",
    }
    stub = Stub(entry_point=page_name, pages_count=10)
    stub.redis.set("key-a", settings.STUB_REDIS_KEY_PAGES_SEPARATOR.join(pages_names_1))
    stub.redis.set("key-b", settings.STUB_REDIS_KEY_PAGES_SEPARATOR.join(pages_names_2))
    assert stub.get_pages_names_to_crawl_next() == pages_names_1 | pages_names_2
    assert stub.redis.keys() == []


def test_get_pages_names_to_crawl_next_empty_key(fake_redis):
    page_name = "page name"
    stub = Stub(entry_point=page_name, pages_count=10)
    stub.redis.set("key", "")
    assert stub.get_pages_names_to_crawl_next() == set()
    assert stub.redis.keys() == []


def test_get_pages_names_to_crawl_next_error(fake_redis):
    page_name = "page name"
    stub = Stub(entry_point=page_name, pages_count=10)
    stub.logger = mock.MagicMock()
    with mock.patch(
        "wikicrawl.stub.Stub._get_pages_names_to_crawl_next",
        side_effect=redis.RedisError,
    ):
        stub.get_pages_names_to_crawl_next()
        stub.logger.exception.assert_called_once()
