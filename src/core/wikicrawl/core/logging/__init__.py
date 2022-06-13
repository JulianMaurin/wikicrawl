import copy
from logging.config import dictConfig

from wikicrawl.core import settings

FORCE_WARNING_LEVEL = ["celery", "kombu", "py2neo", "asyncio", "amqp"]

LOGGING_CONFIG = {
    "version": 1,
    "root": {"level": settings.LOGGING_LEVEL, "handlers": []},
    "handlers": {
        "STREAM": {
            "class": "logging.StreamHandler",
            "formatter": "STREAM",
        },
        "LOKI": {
            "class": "wikicrawl.core.logging.loki.LokiHandler",
            "formatter": "LOKI",
        },
    },
    "formatters": {
        "STREAM": {
            "format": "(%(asctime)s) [%(levelname)8s] [%(name)s] %(message)s",
        },
        "LOKI": {
            "format": "%(message)s",
        },
    },
    "loggers": {logger_name: {"level": "WARNING"} for logger_name in FORCE_WARNING_LEVEL},
}


def setup():
    engines = set(settings.LOGGING_ENGINES.split(",")) - {""}
    available_engines = set(LOGGING_CONFIG["handlers"].keys())

    unavailable_engines = engines - available_engines
    if unavailable_engines:
        raise Exception(f"Logging engine(s) not available: {unavailable_engines}")

    if settings.DEBUG:
        engines.add("STREAM")

    if not engines:
        return

    config = copy.deepcopy(LOGGING_CONFIG)
    for engine in engines:
        config["root"]["handlers"].append(engine)
    dictConfig(config)
