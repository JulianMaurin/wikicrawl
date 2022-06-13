import re

LINK_TAG_REGEX = re.compile(r'<a href="(.*?)"')


def parse_href_from_link_tags(html: str) -> list[str]:
    return re.findall(LINK_TAG_REGEX, html)
