# Task queue

View from the top,  the idea is quite simple, we are downloading wikipedia and recording [nodes and relations](/docs/ubiquitousLanguage.md#graph) using a distributed task queue system.

![pipeline-overview](/docs/images/pipeline-overview.svg)

## Workers

If we focus on the task queue part of the previous diagram we can see that the pipeline is composed by two kind of python workers scheduled by a celery instance relying on rabbitmq.

![task-queue](/docs/images/workers.svg)

_Celery and RabbitMQ instances will be replicable as well (see: [roadmap](/docs/roadmap.md))_

_Celery is using [Redis](https://github.com/redis/redis) as backend, deliberately not included in the diagram for reasons of clarity._

### Crawling

This worker is scheduled to handle task from the crawling queue (1).
It will download and parse the page (2) to build the list of the of pages referenced in it.

The resulting list is filtered using the database to avoid useless processing (3).
_We assume this filtering is not fully reliable due to the worker concurrency but it still has a notable impact._

Once the list is filtered, notice that we could face an empty list in this case, it will create for each page (4):

- a crawling task: feeding himself as a common crawler
- a recoding task: the job for the other worker

### Recording

Handling task previously created, this worker is scheduled to consomme the recording queue.
Its responsibility is straight forward, recording the [node and relations](/docs/ubiquitousLanguage.md#graph) resulting from the crawling to the graph database.

## Scheduling

Celery provides a rate limiting feature that allows to control the processing rate of the pipeline.
Thanks to it, we are avoiding bottleneck that have not been identified yet.
Tunning it will be the cornerstone of the global performance improvement, have a look to the [roadmap](/docs/roadmap.md) to know more about this subject.

In addition of the rate limiting, a queue max size is enforced as safeguard (see: [worker settings](/docs/configuration.md)).

## How to create a crawling task

A [Makefile](/Makefile) target is available to easily create a crawling task with a random page from the stub:

```sh
make crawl-random-stub
```
