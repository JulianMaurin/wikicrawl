from __future__ import annotations

import logging
from typing import Tuple

from py2neo.bulk import merge_nodes, merge_relationships
from retry import retry
from wikicrawl.core.logging import setup
from wikicrawl.database.neo4j import get_engine

PAGE_RELATIONSHIP = "REFERS_TO"


@retry(Exception, tries=3, delay=5)
def create_constraints():
    setup()
    logger = logging.getLogger("constraints")
    try:
        get_engine().run("CREATE CONSTRAINT pages IF NOT EXISTS ON (p:Page) ASSERT p.name IS UNIQUE")
    except Exception as e:
        logger.exception("Error creating constraints.")
        raise e


def filter_pages_not_recorded(pages_names: list[str]) -> set[str]:
    query = (
        f"WITH {pages_names} as pages "
        f"MATCH (a:Page)-[:{PAGE_RELATIONSHIP}]->(b:Page) "
        "WHERE a.name IN pages "
        "RETURN a;"
    )
    nodes = [node.get("a") for node in get_engine().run(query)]
    page_names_to_exclude = [node["name"] for node in nodes]
    return set(pages_names) - set(page_names_to_exclude)


def insert_bulk_relations(relations: list[Tuple[str, str]], logger: logging.LoggerAdapter) -> None:
    pages = set()
    for origin, target in relations:
        pages.add(origin)
        pages.add(target)

    merge_nodes(
        get_engine().auto(),
        [
            [
                page,
            ]
            for page in pages
        ],
        ("Page", "name"),
        keys=["name"],
    )

    merge_relationships(
        get_engine().auto(),
        [((origin,), {}, (target)) for origin, target in relations],
        PAGE_RELATIONSHIP,
        start_node_key=("Page", "name"),
        end_node_key=("Page", "name"),
    )

    logger.debug("Record relations (nodes: %s, edges: %s).", len(pages), len(relations))
