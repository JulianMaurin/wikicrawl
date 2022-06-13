from functools import cache

from py2neo import Graph
from wikicrawl.database import settings


@cache
def get_engine():
    return Graph(settings.DATABASE_URL, auth=(settings.DATABASE_USER, settings.DATABASE_PASSWORD))
