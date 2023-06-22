# Python

## Packaging

![python package](/docs/images/packages.svg)

Wikicrawl is composed of multiple python packages sharing the same `wikicrawl` namespace (see: [sources](/src)).

Packages build and dependencies management is powered by [Poetry](https://python-poetry.org/).

## Tests

The test suite is based on [Pytest](https://docs.pytest.org/en/7.1.x/). Running the test locally is possible, but as some tests are relying on the database the recommended usage is to run them using docker-compose. Running [in memory database, as SQLite](https://www.sqlite.org/inmemorydb.html#:~:text=An%20SQLite%20database%20is%20normally,filename%20%22%3Amemory%3A%22.), was not an option due to the usage of the [graph](/docs/ubiquitousLanguage.md#graph) database.

This way the code will be executed on a python alpine image with dependencies installed (see: [Dockerfile](/Dockerfile.dev)).

The suite output [coverage report](https://github.com/pytest-dev/pytest-cov) and [junit report](https://docs.pytest.org/en/7.1.x/how-to/output.html?highlight=report#creating-junitxml-format-files) (see: [Pytest settings](/pyproject.toml)).

To run the tests suite:

```sh
make build-tests-image  # if not already built
# [...]
make tests
# [...]
```
