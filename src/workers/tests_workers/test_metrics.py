from unittest import mock

from wikicrawl.workers.metrics import count, timing

from .conftest import metrics


def test_count(metrics):
    count("a")
    metrics().incr.assert_called_once_with("a.count", 1, 1)


def test_count_error(metrics):
    metrics().incr.side_effect = Exception()
    with (mock.patch("wikicrawl.workers.metrics.logging.getLogger") as mock_logger):
        count("a")
        mock_logger().exception.assert_called_once()


def test_timing(metrics):
    with mock.patch("wikicrawl.workers.metrics.time.perf_counter", return_value=10.0):
        timing("a", 4.5)
    metrics().timing.assert_called_once_with("a.duration", 550.0)


def test_timing_error(metrics):
    metrics().timing.side_effect = Exception()
    with (mock.patch("wikicrawl.workers.metrics.logging.getLogger") as mock_logger):
        timing("a", 4.5)
        mock_logger().exception.assert_called_once()
