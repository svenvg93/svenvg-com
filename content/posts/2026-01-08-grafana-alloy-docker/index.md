---
title: "Grafana Alloy: Installing on Docker"
description: Install Grafana Alloy as a Docker container and configure it to forward metrics and logs to Prometheus and Loki.
date: 2026-01-08
draft: false
categories:
  - Monitoring
tags:
  - docker
  - alloy
  - grafana
---

## What is Grafana Alloy

Alloy is the telemetry collection agent that replaces Promtail and Grafana Agent. It collects metrics, logs, and traces and forwards them to Prometheus and Loki using a modular config — each collector lives in its own `.alloy` file, and every file in the config directory is loaded automatically.

This guide installs Alloy as a Docker container — simplest if the rest of your stack is already containerized on the same host. Prefer running it directly on the host instead? See [Installing on Bare Metal][bare-metal].

This assumes Prometheus, Loki, and Grafana are already running — see [Building the Stack][stack] if you haven't set those up yet.

## Install Alloy with Docker Compose

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

## Endpoints

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

## Self-Monitoring

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

## Start Alloy

```bash
docker compose -f alloy/docker-compose.yml up -d
```

Open the Alloy web UI at `http://<HOST_IP>:12345` to verify all components are green.

With Alloy running, head back to [Building the Stack][stack-collectors] to configure host, container, and log collectors.

[stack]: {{< ref "/posts/2026-01-08-grafana-observability-building-the-stack" >}}
[stack-collectors]: {{< ref "/posts/2026-01-08-grafana-observability-building-the-stack" >}}#host-metrics
[bare-metal]: {{< ref "/posts/2026-01-08-grafana-alloy-bare-metal" >}}
