# Ubiquitous language

## entry point

[Page name](#page-name) is used to start the crawling process.

eg. _Running the crawler with `Test` as an entry point will start crawling the page `wikipedia.org/wiki/Test`._

## page name

Unique wiki page identifier. Used in the URL to access the page.

eg. _If the page name is `Main_Page` then the URL is  `wikipedia.org/wiki/Main_Page`._

## graph

> Graph is an abstract data type that is meant to implement the undirected graph and directed graph concepts from the field of graph theory within mathematics. [wikipedia](https://en.wikipedia.org/wiki/Graph_(abstract_data_type))

The database used by  `wikicrawl`,  [Neo4J](https://neo4j.com), is a [graph database](https://en.wikipedia.org/wiki/Graph_database). Have a look at the [graph database concepts chapter in the Neo4J documentation](https://neo4j.com/docs/getting-started/current/graphdb-concepts/) to find all the details on the related vocabulary. __Being aware of the concepts of `nodes` and `relations` is the minimum requirement to read this documentation.__

## origin/target page

In a [graph](#graph) context a page is, or the origin, or the target page, depending on the direction of the relation: `(origin)-->(target)`.

In a crawling context:

- the origin page is the working page, downloaded and parsed by the crawler
- the target page is the page that as a reference (`href`) in the content of the origin page

## stub

> stubs are programs that simulate the behaviours of software components ([wikipedia](https://en.wikipedia.org/wiki/Test_stub)).

See: [wikicrawl stub documentation](/doc/services/stub.md).

## web crawler

> An Internet bot that systematically browses the World Wide Web ([wikipedia](https://en.wikipedia.org/wiki/Web_crawler)).

In the case of `wikicrawl` we can talk about a [semantic-focused crawler](https://en.wikipedia.org/wiki/Web_crawler#Semantic_focused_crawler).
