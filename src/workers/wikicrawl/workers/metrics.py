from __future__ import annotations

import logging
import time
from functools import cache

import statsd
from wikicrawl.workers import settings


@cache
def get_client():
    if settings.WORKER_STATSD_HOST and settings.WORKER_STATSD_PORT:
        return statsd.StatsClient(settings.WORKER_STATSD_HOST, settings.WORKER_STATSD_PORT)


def timing(name: str, start: float) -> None:
    try:
        client = get_client()
        if client:
            client.timing(f"{name}.duration", (time.perf_counter() - start) * 100)
    except Exception as err:
        logging.getLogger("statsd").exception("Error publishing timing (error: %s).", err.__class__.__name__)


def count(name: str, value: int = 1, rate: float = 1) -> None:
    try:
        client = get_client()
        if client:
            client.incr(f"{name}.count", value, rate)
    except Exception as err:
        logging.getLogger("statsd").exception("Error publishing count (error: %s).", err.__class__.__name__)
