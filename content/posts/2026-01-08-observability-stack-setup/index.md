---
title: Setting Up Your Observability Stack
description: Install Prometheus, Loki, Grafana, and Grafana Alloy with Docker to build the foundation of your homelab monitoring stack.
date: 2026-01-08
draft: false
categories:
  - Monitoring
tags:
  - docker
  - grafana
  - prometheus
  - loki
  - alloy
cover: cover.jpg

---

Before you can collect metrics or centralize logs, you need somewhere to store and visualize them — and an agent to collect the data. This post sets up all four components of a Grafana observability stack:

- **Prometheus** — metrics storage
- **Loki** — log storage
- **Grafana** — visualization
- **Grafana Alloy** — telemetry collection agent

## Prometheus

Prometheus is a time-series database that stores metrics. We'll enable the remote write receiver so Alloy can push metrics directly to it.

Create a directory and Docker Compose file:

```bash
mkdir prometheus
nano prometheus/docker-compose.yml
```

```yaml {filename="docker-compose.yml"}
services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--storage.tsdb.retention.time=90d'
      - '--storage.tsdb.retention.size=100GB'
      - '--web.enable-lifecycle'
      - '--web.enable-remote-write-receiver'
    restart: unless-stopped
    networks:
      - backend

networks:
  backend:
    name: backend

volumes:
  prometheus:
    name: prometheus
```

Create the Prometheus config file:

```bash
nano prometheus/prometheus.yml
```

```yaml {filename="prometheus.yml"}
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs: []
```

`scrape_configs` is empty because Alloy pushes metrics via remote write. Adjust `retention.time` and `retention.size` to match your available disk space — whichever limit is hit first triggers cleanup.

Start Prometheus:

```bash
docker compose -f prometheus/docker-compose.yml up -d
```

Verify it's ready:

```bash
curl -s http://localhost:9090/-/ready
```

## Loki

Loki stores logs indexed by labels rather than full-text, making it storage-efficient and fast for label-based queries.

Create a directory and Docker Compose file:

```bash
mkdir loki
nano loki/docker-compose.yml
```

```yaml {filename="docker-compose.yml"}
services:
  loki:
    image: grafana/loki
    container_name: loki
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - ./loki-config.yaml:/etc/loki/loki-config.yaml:ro
      - loki-data:/loki
    command: -config.file=/etc/loki/loki-config.yaml
    networks:
      - backend

networks:
  backend:
    name: backend

volumes:
  loki-data:
    name: loki-data
```

Create the Loki config file:

```bash
nano loki/loki-config.yaml
```

```yaml {filename="loki-config.yaml"}
auth_enabled: false

server:
  http_listen_address: 0.0.0.0
  http_listen_port: 3100
  grpc_listen_port: 9095
  log_level: info

common:
  instance_addr: 127.0.0.1
  path_prefix: /loki
  storage:
    filesystem:
      chunks_directory: /loki/chunks
      rules_directory: /loki/rules
  replication_factor: 1
  ring:
    kvstore:
      store: memberlist

schema_config:
  configs:
    - from: 2020-10-24
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h

limits_config:
  query_timeout: 600s
  retention_period: "365d"
  ingestion_rate_mb: 4
  ingestion_burst_size_mb: 6
  max_streams_per_user: 10000
  max_line_size: 256000
  reject_old_samples: true
  reject_old_samples_max_age: 168h
  creation_grace_period: 15m
  discover_log_levels: false
```

Adjust `retention_period` based on your available disk space.

Start Loki:

```bash
docker compose -f loki/docker-compose.yml up -d
```

Verify it's ready:

```bash
curl -s http://localhost:3100/ready
```

## Grafana

Grafana is the visualization layer — it connects to Prometheus and Loki and lets you build dashboards and explore data.

Create a directory and Docker Compose file:

```bash
mkdir grafana
nano grafana/docker-compose.yml
```

```yaml {filename="docker-compose.yml"}
services:
  grafana:
    image: grafana/grafana
    container_name: grafana
    hostname: ${HOSTNAME}
    environment:
      - TZ=Europe/Amsterdam
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    ports:
      - 3000:3000
    networks:
      - backend

networks:
  backend:
    name: backend

volumes:
  grafana_data:
    name: grafana_data
```

Change `GF_SECURITY_ADMIN_PASSWORD` to a secure password before starting.

Start Grafana:

```bash
docker compose -f grafana/docker-compose.yml up -d
```

Open `http://<HOST_IP>:3000` and log in with username `admin` and your password.

### Add Datasources

Connect Grafana to Prometheus and Loki:

**Prometheus:**
1. Click **Connections** → search for **Prometheus** → **Add new Datasource**
2. Set name `prometheus`, URL `http://prometheus:9090`
3. Click **Save & Test**

**Loki:**
1. Click **Connections** → search for **Loki** → **Add new Datasource**
2. Set name `loki`, URL `http://loki:3100`
3. Click **Save & Test**

## Grafana Alloy

Alloy is the telemetry collection agent that replaces Promtail and Grafana Agent. It collects metrics, logs, and traces and forwards them to Prometheus and Loki using a modular config — each collector lives in its own `.alloy` file.

Create a directory for Alloy and its config files:

```bash
mkdir -p alloy/config
nano alloy/docker-compose.yml
```

```yaml {filename="docker-compose.yml"}
services:
  alloy:
    image: grafana/alloy:latest
    container_name: alloy
    hostname: ${HOSTNAME}
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam
    ports:
      - "12345:12345"
    volumes:
      - ./config/:/etc/alloy/config/:ro
      - alloy-data:/var/lib/alloy/data
    command:
      - run
      - --server.http.listen-addr=0.0.0.0:12345
      - --storage.path=/var/lib/alloy/data
      - /etc/alloy/config/
    networks:
      - backend

networks:
  backend:
    name: backend

volumes:
  alloy-data:
    name: alloy-data
```

Alloy loads every `.alloy` file in the `config/` directory automatically — adding a new collector is as simple as dropping in a new file. Port `12345` is the Alloy web UI for debugging component status.

### Endpoints

Create `endpoint.alloy` to centralize write destinations. All collector configs reference these by name:

```bash
nano alloy/config/endpoint.alloy
```

```hcl {filename="endpoint.alloy"}
loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}

prometheus.remote_write "default" {
  endpoint {
    url = "http://prometheus:9090/api/v1/write"
  }
}
```

### Self-Monitoring

Create `self.alloy` so Alloy reports its own health metrics to Prometheus:

```bash
nano alloy/config/self.alloy
```

```hcl {filename="self.alloy"}
prometheus.exporter.self "alloy_metrics" {}

prometheus.scrape "alloy_metrics" {
  targets         = prometheus.exporter.self.alloy_metrics.targets
  scrape_interval = "60s"
  forward_to      = [prometheus.remote_write.default.receiver]
}
```

Start Alloy:

```bash
docker compose -f alloy/docker-compose.yml up -d
```

Open the Alloy web UI at `http://<HOST_IP>:12345` to verify all components are green.

## What's Next

With the full stack running, start adding collectors:

- [Host & Container Monitoring]({{< ref "/posts/2026-01-22-host-container-monitoring" >}}) — CPU, memory, disk, and Docker container metrics
- [Log Monitoring with Loki]({{< ref "/posts/2026-02-05-log-monitoring-with-alloy" >}}) — system logs and Docker container logs
