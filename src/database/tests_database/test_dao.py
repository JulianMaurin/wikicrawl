import logging
from unittest import mock

import pytest
from wikicrawl.database.dao import (
    PAGE_RELATIONSHIP,
    create_constraints,
    filter_pages_not_recorded,
    insert_bulk_relations,
)
from wikicrawl.database.neo4j import get_engine

from . import conftest


def test_filter_pages_not_recorded():
    get_engine().delete_all()
    insert_bulk_relations([("a", "b"), ("a", "c")], logging.getLogger(""))
    assert sorted(filter_pages_not_recorded(["x", "a", "y", "c"])) == ["c", "x", "y"]


def test_create_constraints():
    with (mock.patch("wikicrawl.database.dao.get_engine") as mock_engine,):
        create_constraints()
    mock_engine().run.assert_called_once()


def test_create_constraints_error():
    with (
        mock.patch("wikicrawl.database.dao.logging") as mock_logging,
        mock.patch("wikicrawl.database.dao.get_engine") as mock_engine,
        pytest.raises(Exception),
    ):
        mock_engine().run.side_effect = Exception()
        create_constraints.__wrapped__()
        mock_logging.getLogger().exception.assert_called_once()


def test_insert_bulk_relations():
    engine = get_engine()
    engine.delete_all()
    relations = [("a", "b"), ("a", "c"), ("b", "c"), ("x", "y")]
    insert_bulk_relations(relations, logging.getLogger(""))

    nodes = [result.get("n") for result in engine.run("MATCH (n) RETURN n;")]
    labels = [str(node.labels) for node in nodes]
    assert labels == [":Page", ":Page", ":Page", ":Page", ":Page"]
    names = sorted([node["name"] for node in nodes])
    assert names == ["a", "b", "c", "x", "y"]

    existing_relations = sorted(
        [
            (rel.get("a")["name"], rel.get("b")["name"])
            for rel in engine.run(f"MATCH (a:Page)-[r:{PAGE_RELATIONSHIP}]->(b:Page) RETURN a, b")
        ]
    )
    assert existing_relations == relations
