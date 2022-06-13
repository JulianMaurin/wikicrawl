import logging
import time

import requests
from retry import retry
from wikicrawl.core.settings import LOGGING_SERVICE

LOGGING_URL = f"http://{LOGGING_SERVICE}:3100/loki/api/v1/push"


def now():
    return str(int(time.time() * 1e9))


LOG_RECORD_KEYS_TO_EXCLUDE = [
    "args",
    "created",
    "exc_info",
    "exc_text",
    "extra",
    "filename",
    "funcName",
    "getMessage",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "msg",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "threadName",
]


class LokiHandler(logging.Handler):
    def emit(self, record: logging.LogRecord):
        try:
            payload = self.build_payload(record)
            self._emit(payload)
        except Exception:  # nosec: B110
            pass

    @retry(Exception, tries=3, delay=2)
    def _emit(self, payload: dict):
        """Send log record to Loki."""
        requests.post(LOGGING_URL, json=payload, timeout=3)

    def build_payload(self, record: logging.LogRecord):
        tags = {
            attr: getattr(record, attr)
            for attr in dir(record)
            if ("__" not in attr and attr not in LOG_RECORD_KEYS_TO_EXCLUDE)
        }
        tags["level"] = tags.pop("levelname")
        return {"streams": [{"stream": tags, "values": [[now(), self.format(record)]]}]}
