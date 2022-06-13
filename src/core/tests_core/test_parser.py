from wikicrawl.core.parser import parse_href_from_link_tags


def test_parse_href_from_link_tags():
    html = (
        '<a href="/wiki/Alan_Cumming" title="Alan Cumming">Alan Cumming</a>'
        '<a href="http://google.com/xxx" title="Google">Google</a>'
    )
    links = parse_href_from_link_tags(html)
    assert len(links) == 2
    assert "/wiki/Alan_Cumming" in links
    assert "http://google.com/xxx" in links
