import os

from environs import Env

env = Env()

os.environ["DATABASE_USER"] = env("DATABASE_USER", "neo4j")
os.environ["DATABASE_PASSWORD"] = env("DATABASE_PASSWORD", "wikicrawl")
os.environ["DATABASE_URL"] = env("DATABASE_URL", "bolt://localhost")

from wikicrawl.database.dao import create_constraints  # noqa: E402

create_constraints()
