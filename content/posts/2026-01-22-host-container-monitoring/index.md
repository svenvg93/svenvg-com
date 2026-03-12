---
title: Host & Container Monitoring with Grafana Alloy
description: Collect host system and Docker container metrics using Grafana Alloy's built-in exporters, stored in Prometheus and visualized in Grafana.
date: 2026-01-22
draft: false
categories:
  - Monitoring
tags:
  - docker
  - prometheus
  - grafana
  - alloy
cover: cover.jpg
aliases:
  - /posts/host-container-monitoring-with-prometheus
  - /host-container-monitoring-with-prometheus
---

Monitoring your systems and containers is essential for maintaining a reliable homelab or home server. This guide uses Grafana Alloy's built-in exporters to collect host and container metrics, with Prometheus for storage and Grafana for visualization — all managed through a single agent instead of separate containers per exporter.

## Prerequisites

- Prometheus running and reachable
- Grafana running with Prometheus added as a datasource
- Grafana Alloy installed and running — see [Setting Up Your Observability Stack]({{< ref "/posts/2026-01-08-observability-stack-setup" >}})

## Host Metrics

Create an Alloy config file for host system metrics:

```bash
nano alloy/config/unix.alloy
```

```hcl {filename="unix.alloy"}
// Host system metrics (CPU, memory, disk, network)
prometheus.exporter.unix "host" {
  set_collectors = ["cpu", "diskstats", "filesystem", "loadavg", "meminfo", "netdev", "uname"]
  filesystem {
    mount_points_exclude = "^/(sys|proc|dev|host|etc)($$|/)"
  }
  netdev {
    device_exclude = "^(veth.*|br.*|docker.*|virbr.*|lo)$$"
  }
}

prometheus.scrape "host" {
  targets    = prometheus.exporter.unix.host.targets
  forward_to = [prometheus.remote_write.default.receiver]
  job_name   = "host"
}
```

The `set_collectors` list controls which metrics are gathered. The filesystem and netdev excludes prevent virtual mounts and Docker bridge interfaces from cluttering your dashboards.

## Container Metrics

Create an Alloy config file for Docker container metrics:

```bash
nano alloy/config/docker-metrics.alloy
```

```hcl {filename="docker-metrics.alloy"}
// Docker container metrics (CPU, memory, network per container)
prometheus.exporter.cadvisor "dockermetrics" {
  docker_host      = "unix:///var/run/docker.sock"
  storage_duration = "5m"
}

prometheus.relabel "docker_filter" {
  forward_to = [prometheus.remote_write.default.receiver]

  rule {
    target_label = "job"
    replacement  = "docker"
  }
  rule {
    target_label = "instance"
    replacement  = constants.hostname
  }
  // Drop container_spec metrics that frequently contain NaN values
  rule {
    source_labels = ["__name__"]
    regex         = "container_spec_(cpu_period|cpu_quota|cpu_shares|memory_limit_bytes|memory_swap_limit_bytes|memory_reservation_limit_bytes)"
    action        = "drop"
  }
}

prometheus.scrape "dockermetrics" {
  targets         = prometheus.exporter.cadvisor.dockermetrics.targets
  forward_to      = [prometheus.relabel.docker_filter.receiver]
  scrape_interval = "10s"
}
```

### Docker Socket Access

Alloy needs access to the Docker socket to discover containers. Add the following volume mount to your Alloy `docker-compose.yml` and recreate the container:

```yaml {filename="docker-compose.yml"}
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

```bash
docker compose up -d alloy
```

## Apply Configuration

Restart Alloy to load the new config files:

```bash
docker restart alloy
```

## Verification

Open the Alloy Web UI and confirm both components are healthy:

- `prometheus.exporter.unix`
- `prometheus.exporter.cadvisor`

Then verify data is flowing in Grafana's Explore view:

```promql
node_cpu_seconds_total{job="host"}
```

```promql
container_cpu_usage_seconds_total{job="docker"}
```

## Grafana Dashboards

You can create your own dashboards or use these as a starting point:

- [System Dashboard][1] — host metrics
- [Docker Dashboard][2] — container metrics

[1]: https://github.com/svenvg93/Grafana-Dashboard/tree/master/systems
[2]: https://github.com/svenvg93/Grafana-Dashboard/tree/master/docker
