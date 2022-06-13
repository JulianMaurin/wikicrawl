from unittest import mock

import pytest
from wikicrawl.workers import settings
from wikicrawl.workers.recorder import record

from .conftest import celery


def test_task(celery):
    with (
        mock.patch("wikicrawl.workers.recorder.insert_bulk_relations") as mock_record,
        mock.patch("wikicrawl.workers.recorder.metrics") as mock_metrics,
    ):
        tasks_batch = [
            mock.MagicMock(kwargs=dict(origin_page_name="a", target_page_name="b")),
            mock.MagicMock(kwargs=dict(origin_page_name="x", target_page_name="y")),
        ]
        record(tasks_batch)
        mock_metrics.count.assert_called_once_with(f"{settings.WORKER_QUEUE_RECORD_TASK}.success", 2)
        mock_metrics.timing.assert_called_once()
        mock_record.assert_called_once_with(relations=[("a", "b"), ("x", "y")], logger=mock.ANY)


def test_task_nothing_to_do(celery):
    with (
        mock.patch("wikicrawl.workers.recorder.insert_bulk_relations") as mock_record,
        mock.patch("wikicrawl.workers.recorder.metrics") as mock_metrics,
    ):
        record(tasks_batch=[])
        mock_record.assert_not_called()
        mock_metrics.count.assert_not_called()
        mock_metrics.timing.assert_called_once()


def test_task_error(celery):
    with (
        mock.patch("wikicrawl.workers.recorder.insert_bulk_relations", side_effect=Exception()),
        mock.patch("wikicrawl.workers.recorder.logging.getLogger") as mock_logging,
        mock.patch("wikicrawl.workers.recorder.metrics") as mock_metrics,
        pytest.raises(Exception),
    ):
        record(tasks_batch=[("a", "b")])
        mock_logging().exception.assert_called_once()
        mock_metrics.count.assert_called_once_with(f"{settings.WORKER_QUEUE_RECORD_TASK}.failure", 1)
        mock_metrics.timing.assert_called_once()
