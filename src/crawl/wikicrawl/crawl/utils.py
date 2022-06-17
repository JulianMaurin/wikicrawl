import aiohttp

from wikicrawl.core import settings as core_settings


def handle_redirect(page_name: str, response: aiohttp.client.ClientResponse) -> str:
    """
    When redirecting to another page, the page name need to be updated.

        eg: https://en.wikipedia.org/wiki/Special:Random
    """
    if len(response.history) and response.history[0].status == 302:
        return page_name_from_url(response.url)
    return page_name


def page_name_from_url(url: str) -> str:
    url_part = f"{core_settings.WIKI_DOMAIN}{core_settings.WIKI_PAGE_ENDPOINT}/"
    if not url.startswith(url_part):
        raise Exception(f"Unexpected url (url: {url}).")
    return url.replace(url_part, "")


def page_name_to_url(page_name: str) -> str:
    return f"{core_settings.WIKI_DOMAIN}{core_settings.WIKI_PAGE_ENDPOINT}/{page_name}"
