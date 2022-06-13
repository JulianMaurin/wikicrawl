from unittest import mock

from wikicrawl.workers.celery import after_setup_logger, after_setup_task_logger


def test_after_setup_logger():
    with mock.patch("wikicrawl.workers.celery.logging.setup") as mock_logging_setup:
        after_setup_logger()
        mock_logging_setup.assert_called_once()


def test_after_setup_task_logger():
    with mock.patch("wikicrawl.workers.celery.logging.setup") as mock_logging_setup:
        after_setup_task_logger()
        mock_logging_setup.assert_called_once()
