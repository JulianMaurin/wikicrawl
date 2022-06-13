import logging
from logging.config import dictConfig
from unittest import mock

import pytest
from freezegun import freeze_time
from wikicrawl.core.logging import setup
from wikicrawl.core.logging.loki import LokiHandler


@pytest.fixture
def loki():
    with (
        mock.patch("wikicrawl.core.logging.settings.LOGGING_ENGINES", "LOKI"),
        mock.patch("wikicrawl.core.logging.loki.LokiHandler._emit") as emit_mock,
    ):
        setup()
        yield emit_mock
        for handler in [handler for handler in logging.getLogger().root.handlers if isinstance(handler, LokiHandler)]:
            logging.getLogger("").root.removeHandler(handler)


def test_emit_error(loki):
    loki.side_effect = Exception()
    logger = logging.getLogger("loki")
    logger.info("x")  # Silent failure


def test_emit():
    with (
        mock.patch("wikicrawl.core.logging.settings.LOGGING_ENGINES", "LOKI"),
        mock.patch("wikicrawl.core.logging.loki.LOGGING_URL", "https://xxx/"),
        mock.patch("wikicrawl.core.logging.loki.requests.post") as emit_post,
    ):
        setup()
        logger = logging.getLogger("loki")
        logger.disabled = False
        logger.info("x")
        emit_post.assert_called_with("https://xxx/", json=mock.ANY, timeout=mock.ANY)


@freeze_time("2022-01-01 12:00")
def test_logging_info(loki):
    logger = logging.getLogger("loki")
    logger.disabled = False
    logger.info("x")
    loki.assert_called_with(
        {
            "streams": [
                {
                    "stream": {"level": "INFO", "name": "loki", "thread": mock.ANY},
                    "values": [["1641038400000000000", "x"]],
                }
            ]
        }
    )


def test_logging_debug(loki):
    logger = logging.getLogger("loki")
    logger.debug("x")
    loki.assert_not_called()


@freeze_time("2022-01-01 12:00")
def test_logging_exception(loki):
    logger = logging.getLogger("loki")
    logger.disabled = False
    try:
        raise Exception
    except Exception:
        logger.exception("LOG EXCEPTION")
    loki.assert_called_with(
        {
            "streams": [
                {
                    "stream": {"name": "loki", "thread": mock.ANY, "level": "ERROR"},
                    "values": [["1641038400000000000", mock.ANY]],
                }
            ]
        }
    )


def test_extra(loki):
    logger = logging.getLogger("xxx")
    logger.disabled = False
    logger.warning("x", extra={"a": "b"})
    loki.assert_called_with(
        {
            "streams": [
                {
                    "stream": {"name": "xxx", "thread": mock.ANY, "level": "WARNING", "a": "b"},
                    "values": [[mock.ANY, "x"]],
                }
            ]
        }
    )


def test_setup_no_engine():
    with (
        mock.patch("wikicrawl.core.logging.settings.LOGGING_ENGINES", ""),
        mock.patch("wikicrawl.core.logging.dictConfig") as mock_set_config,
    ):
        setup()
        mock_set_config.assert_not_called()


def test_setup_fallback_on_stream_if_debug():
    with (
        mock.patch("wikicrawl.core.logging.settings.DEBUG", True),
        mock.patch("wikicrawl.core.logging.settings.LOGGING_ENGINES", "LOKI"),
        mock.patch("wikicrawl.core.logging.dictConfig") as mock_set_config,
    ):
        setup()
        call_args_list = mock_set_config.call_args_list
        assert len(call_args_list) == 1
        assert sorted(mock_set_config.call_args_list[0][0][0]["root"]["handlers"]) == ["LOKI", "STREAM"]


def test_handler_not_available():
    test_config = {
        "handlers": {
            "STREAM": {},
        },
    }

    with (
        mock.patch("wikicrawl.core.logging.LOGGING_CONFIG", test_config),
        mock.patch("wikicrawl.core.logging.settings.LOGGING_ENGINES", "UNAVAILABLE"),
        pytest.raises(Exception),
    ):
        setup()
