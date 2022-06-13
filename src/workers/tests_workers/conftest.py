import os
from unittest import mock

import pytest
from environs import Env

env = Env()

os.environ["WORKER_BROKER_URL"] = "http://WORKER_BROKER_URL/"
os.environ["WORKER_TASK_CACHE_URL"] = "http://WORKER_TASK_CACHE_URL/"
os.environ["WORKER_RESULT_BACKEND"] = "http://WORKER_RESULT_BACKEND/"


@pytest.fixture
def celery():
    from wikicrawl.workers.celery import app

    app.conf.task_always_eager = True
    yield


@pytest.fixture
def metrics():
    with (
        mock.patch("wikicrawl.workers.metrics.statsd.StatsClient") as client_mock,
        mock.patch(
            "wikicrawl.workers.metrics.settings",
            mock.MagicMock(WORKER_STATSD_HOST="WORKER_STATSD_HOST", WORKER_STATSD_PORT="WORKER_STATSD_PORT"),
        ),
    ):
        from wikicrawl.workers.metrics import get_client

        get_client.cache_clear()
        yield client_mock
