---
title: System Monitoring Series Part 2 | Log Monitoring with Loki & Promtail
description: In Part 2 of the System Monitoring series, discover how to configure log monitoring for your systems using Loki and Promtail, visualized with Grafana.
date: 2024-06-24
draft: false
categories:
  - Monitoring
  - Logging
tags:
  - docker
  - grafana
  - loki
cover: cover.jpg
      
---

Monitoring isn’t just about metrics—it’s about ensuring application health. Centralized logging with Loki and Grafana provides deeper insights by visualizing and searching logs, helping you quickly identify and resolve issues.

## Setup Loki

To set up Loki, we need to create a folder to hold both the <kbd>docker-compose.yml</kbd> and the configuration file.

First, create the folder for Loki:
```bash
mkdir loki
```

Open a new <kbd>docker-compose.yml</kbd> file for editing:

```bash
nano loki/docker-compose.yml
```
Paste the following content into the file:
```yaml
services:
  loki:
    image: grafana/loki
    container_name: loki
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam
    expose:
      - 3100
    volumes:
      - ./loki-config.yaml:/etc/loki/loki-config.yaml:ro
      - loki:/tmp
    command: -config.file=/etc/loki/loki-config.yaml
    networks:
      - backend
networks:
  backend:
    name: backend
volumes:
    loki:
      name: loki
```

Loki requires a configuration file to define which services to scrape for metrics. Create the configuration file:
```bash
nano loki/loki-config.yaml
```
Paste the following content into the file:
```yaml
auth_enabled: false
server:
  http_listen_port: 3100
  grpc_listen_port: 9096
common:
  instance_addr: 127.0.0.1
  path_prefix: /tmp/loki
  storage:
    filesystem:
      chunks_directory: /tmp/loki/chunks
      rules_directory: /tmp/loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
query_range:
  results_cache:
    cache:
      embedded_cache:
        enabled: true
        max_size_mb: 100
querier:
  max_concurrent: 500
query_scheduler:
  max_outstanding_requests_per_tenant: 1000
frontend:
  max_outstanding_per_tenant: 2000
limits_config:
  max_global_streams_per_user: 5000
  ingestion_rate_mb: 50
  per_stream_rate_limit: 50MB
```

## Setup Promtail

To finalize your logging setup with Loki, you’ll need to configure Promtail to send logs to Loki.

Start by creating a folder to store the <kbd>docker-compose.yml</kbd> and <kbd>promtail-config.yaml</kbd> files.

```bash
mkdir promtail
```

Open a new <kbd>docker-compose.yml</kbd> file for editing:

```bash
nano promtail/docker-compose.yml
```
Paste the following content into the file:
```yaml
services:
  promtail:
    image: grafana/promtail
    container_name: promtail
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - ./promtail-config.yaml:/etc/promtail/promtail-config.yaml:ro
      - /var/log/:/logs
    command: -config.file=/etc/promtail/promtail-config.yaml
    networks:
      - backend
networks:
  backend:
    name: backend
```

Now, create a configuration file named <kbd>promtail-config.yaml</kbd>:

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0
positions:
  filename: /tmp/positions.yaml
clients:
  - url: http://loki:3100/loki/api/v1/push
scrape_configs:
- job_name: authlog
  static_configs:
  - targets:
      - authlog
    labels:
      job: authlog
      __path__: /logs/auth.log
- job_name: syslog
  static_configs:
  - targets:
      - syslog
    labels:
      job: syslog
      __path__: /logs/syslog
```

This configuration will scrape the system’s auth and syslog logs.

Note: You can customize the job_name, <kbd>targets</kbd>, <kbd>job</kbd>, and <kbd>__path__</kbd> under scrape_configs according to your logging requirements.

Finally, start the Loki and Promtail services by running the following commands:

```bash
docker compose -f loki/docker-compose.yml up -d
docker compose -f promtail/docker-compose.yml up -d
```

## Grafana

To visualize logs from Loki in Grafana, you need to configure Loki as a datasource. Here’s how to do it:

1.	Open Grafana:
2.  Click **Connections** in the left-side menu.
3.  Search for **Loki**
4.  Click **Add new Datasource**
5.  Enter the name **loki**
6.  Fill in the Prometheus server URL <kbd>http://loki:3100</kbd>

### Exploring Logs in Grafana

Now that you have added Loki as a datasource, you can explore your logs:

1. In the left sidebar, click on Explore.
2. In the top-left dropdown menu, choose Loki as your datasource.
3. In the query section, select the label filename and set the value to /logs/syslog

## Summary

With Loki configured as a datasource in Grafana, Promtail will continuously send log files to Loki, allowing you to visualize and analyze logs easily. This setup provides a comprehensive monitoring solution, enabling you to monitor both metrics and logs from your applications.
