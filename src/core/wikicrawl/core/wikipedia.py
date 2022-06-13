import re
from typing import Generator

YEAR_REGEX = re.compile(r"^\d{0,4}$")
WIKI_PAGE_NAME_REGEX = re.compile(r"^\/wiki\/(\w*)$")


def is_year_page(page_name: str) -> bool:
    return re.match(YEAR_REGEX, page_name) is not None


def page_names_from_urls(urls: list[str]) -> Generator[str, None, None]:
    for url in urls:
        page_name_match = WIKI_PAGE_NAME_REGEX.search(url)
        if page_name_match:
            yield page_name_match.groups()[0]
