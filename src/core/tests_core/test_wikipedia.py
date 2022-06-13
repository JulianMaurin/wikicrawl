from os import link

from wikicrawl.core.wikipedia import is_year_page, page_names_from_urls


def test_is_year_page():
    assert not is_year_page("ABC")
    assert is_year_page("1999")


def test_page_names_from_urls():
    links = [
        "/wiki/Alan_Cumming",
        "http://google.com/xxx",
        "https://foundation.wikimedia.org/wiki/Cookie_statement",
        "/wiki/Wikipedia:xxx",
        "/wiki/Special:Random",
    ]
    page_names = list(page_names_from_urls(links))
    assert len(page_names) == 1
    assert "Alan_Cumming" in page_names
