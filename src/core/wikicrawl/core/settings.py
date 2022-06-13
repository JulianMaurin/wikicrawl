from __future__ import annotations

from environs import Env

env = Env()

DEBUG: bool = env.bool("DEBUG", False)

LOGGING_LEVEL: str = "DEBUG" if DEBUG else env("LOGGING_LEVEL", "INFO")
LOGGING_ENGINES: str = env("LOGGING_ENGINES", "STREAM")
LOGGING_SERVICE: str | None = env("LOGGING_SERVICE", None)


WIKI_LANGUAGE: str = env("WIKI_LANGUAGE", "en")
WIKI_BASE_URL: str = env("WIKI_BASE_URL", f"https://{WIKI_LANGUAGE}.wikipedia.org")
WIKI_PAGE_ENDPOINT: str = env("WIKI_PAGE_ENDPOINT", "/wiki")
