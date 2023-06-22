# Monitoring

This part of the stack is a must-have.
First of all, it enables the readability of [logging](https://en.wikipedia.org/wiki/Logging_(software)) by providing a way to sort and organize entries emitted by workers running concurrently.
Then, thanks to the [metrics](https://en.wikipedia.org/wiki/Metric_(mathematics)) we can identify processing bottlenecks and the global health of the system. It will be helpful knowing that the pipeline is destined to run over a long period.

## Overview

![monitoring](/docs/images/monitoring.svg)

## Grafana

[Grafana](https://github.com/grafana/grafana) offers connectors to many [datasources](https://grafana.com/docs/grafana/latest/datasources) and a great graphic interface to visualize logs and metrics. It is a perfect alternative to [Datadog](https://www.datadoghq.com/) in an open-source context.

_(See: [configuration files](/.config/grafana/))._

### Dashboard

The [Wikicrawl dashboard](/docs/images/dashboard.png) is the watchtower of the application.

Running the application locally using [docker compose](/docs/dockerCompose.md), you can access the dashboard at: <http://localhost:8015/d/lERNI69nk/wikicrawl>.

## Loki

> Loki is a log aggregation system designed to store and query logs from all your applications and infrastructure. ([Grafana.com](https://grafana.com/oss/loki/))

Logs are sent to Loki by the Wikicrawl workers using HTTP. The integration is made at the python logging library level using custom [handler](https://docs.python.org/3/library/logging.handlers.html).

_(See: [configuration files](/.config/grafana/))_

## Prometheus

> Prometheus is an open-source monitoring system. ([Grafana.com](https://grafana.com/oss/prometheus/))

The role of Prometheus is to collect the metrics from applications to make them available to Grafana.
In our case, the only application metrics that are collected are the ones from [RabbitMQ](/docs/taskQueue.md).
RabbitMQ offers a [plugin](https://www.rabbitmq.com/prometheus.html) that makes this integration easy.

_(See: [configuration files](/.config/prometheus/))_

_Notice that Prometheus is going to be deprecated. (see: [roadmap](/docs/roadmap.md))._

## Statsd

[Statsd](https://github.com/statsd/statsd) listens for [metrics](https://github.com/statsd/statsd/blob/master/docs/metric_types.md) and aggregate them. It relies on [Graphite](https://github.com/graphite-project/graphite-web) as the backend to store data and make it available to Grafana.

Metrics are sent to Statsd by the Wikicrawl workers using TCP.
