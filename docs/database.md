# Database

The very principle of `wikicrawl` is based on the usage of a [graph database](/docs/ubiquitousLanguage.md#graph).
This section will introduce the tool and how to use it.

## Neo4J

The database used in this project is [Neo4j](https://neo4j.com/).

### Alternative

There is many alternative available (see: [wikipedia](https://en.wikipedia.org/wiki/Graph_database#List_of_graph_databases)).

However, this solution was chosen for the following reasons:

- GPL3-licensed [source-available](https://github.com/neo4j)
- Available [docker image](https://hub.docker.com/_/neo4j)
- Integrated [browser](https://neo4j.com/docs/operations-manual/current/installation/neo4j-browser/)
- Rich [documentation](https://neo4j.com/docs/)

### Cypher

[Cypher](https://en.wikipedia.org/wiki/Cypher_(query_language)) is the query language used by the database.
More details are available at: <https://neo4j.com/developer/cypher/>.

### Limitation

Using the community edition, the maximum number of nodes to display on the browser is limited.

## Data

### Model

Database constraint enforces the uniqueness of nodes but, unlike a relational database, it does not enforce data schema.

However, the software is working with a unique type of node `Page`, with only one properties `name` and a unique kind of relation `REFERS_TO`.

Example:

![model](/docs/images/model.svg)

*According to the diagram above, the page <https://en.wikipedia.org/wiki/Apple> contains a reference to the page <https://en.wikipedia.org/wiki/Fruit>.*

### Manipulation

Database operations are executed at workers level (see: [task queue](/docs/taskQueue.md#workers)) using dedicated python package [py2neo](https://github.com/py2neo-org/py2neo). *Notice that we are not using the [official library](https://neo4j.com/developer/python/) to enjoy [bulk operations](https://py2neo.org/2021.1/bulk/index.html?highlight=bulk#module-py2neo.bulk) from `py2neo`.*

The connection is powered by the TCP-based protocol [bolt](https://boltprotocol.org/).

*[Graphana](/docs/monitoring.md#grafana) handle Neo4J datasource (see: [configuration](/.config/grafana/provisioning/datasources/datasource.yml)).*

### Representation
