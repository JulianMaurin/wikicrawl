# Wikicrawl

![python-badge](https://img.shields.io/badge/Python-3.9.11-green.svg)
[![ci-badge](https://github.com/JulianMaurin/wikicrawl/actions/workflows/CI.yaml/badge.svg)](https://github.com/JulianMaurin/wikicrawl/actions)
[![codecov-badge](https://codecov.io/gh/JulianMaurin/wikicrawl/branch/dev/graph/badge.svg?token=8I8M0B7G5D)](https://codecov.io/gh/JulianMaurin/wikicrawl)

## Introduction

Wikicrawl is a [web crawler](https://en.wikipedia.org/wiki/Web_crawler) written in Python3 and based on [Celery](https://github.com/celery/celery). Its particularity is to focus on [wikipedia.org](https://wikipedia.org) and to exploit a [graph database](https://en.wikipedia.org/wiki/Graph_database).

Have a look to the [architecture diagram](/docs/overview.md#diagram) and to the [data representation](/docs/database.md#representation) to have a quick overview of the software.

### Motivation

Wikipedia is one of the richest knowledge base of the internet, such dataset could offers great capabilities to develop [semantic technology](https://en.wikipedia.org/wiki/Semantic_technology).

Wikicrawl have been designed to operate with any [wikimedia](https://www.wikimedia.org/) website in any language (see [configuration](/docs/configuration.md#wiki)), increasing the possibilities.

This perspective encouraged me to polish this personal project and to make it open source.

## Documentations

- [Getting started](/docs/gettingStarted.md)
- [Tests](/docs/python.md#tests)
- The stack:
    - [Stub](/docs/stub.md)
    - [Task queue](/docs/taskQueue.md)
    - [Database](/docs/database.md)
    - [Monitoring](/docs/monitoring.md)
- [Roadmap](/docs/roadmap.md)
- [Contributing](/docs/contributing.md)
