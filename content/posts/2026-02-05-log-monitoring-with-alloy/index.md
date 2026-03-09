---
title: Log Monitoring with Grafana Alloy and Loki
description: Collect system logs and Docker container logs using Grafana Alloy and forward them to Loki for centralized log management in Grafana.
date: 2026-02-05
draft: false
categories:
  - Monitoring
tags:
  - docker
  - grafana
  - loki
  - alloy
cover: cover.jpg
aliases:
  - /log-monitoring-with-loki-promtail
  - /posts/log-monitoring-with-loki-promtail
---

Monitoring isn't just about metrics — centralized logging provides deeper insights by letting you search and correlate events across your entire infrastructure. This guide uses Grafana Alloy to collect both system logs and Docker container logs, forwarding them to Loki for querying in Grafana.

## Prerequisites

- Loki running and reachable
- Grafana running with Loki added as a datasource
- Grafana Alloy installed and running — see [Setting Up Your Observability Stack]({{< ref "/posts/2026-01-08-observability-stack-setup" >}})

## System Logs

Create an Alloy config file to collect `auth.log` and `syslog` from the host:

```bash
nano alloy/config/syslog.alloy
```

```hcl {filename="syslog.alloy"}
// System auth.log collection
local.file_match "authlog" {
  path_targets = [{
    __path__ = "/var/log/auth.log",
  }]
}

loki.source.file "authlog" {
  targets    = local.file_match.authlog.targets
  forward_to = [loki.process.authlog.receiver]
}

loki.process "authlog" {
  stage.static_labels {
    values = {
      job = "authlog",
    }
  }
  forward_to = [loki.write.default.receiver]
}

// System syslog collection
local.file_match "syslog" {
  path_targets = [{
    __path__ = "/var/log/syslog",
  }]
}

loki.source.file "syslog" {
  targets    = local.file_match.syslog.targets
  forward_to = [loki.process.syslog.receiver]
}

loki.process "syslog" {
  stage.static_labels {
    values = {
      job = "syslog",
    }
  }
  forward_to = [loki.write.default.receiver]
}
```

The `path_targets` field supports wildcards — you can use `/var/log/*.log` to collect all log files in a directory at once.

### Log Directory Access

Alloy needs access to the host's log directory. Add the following volume mount to your Alloy `docker-compose.yml` and recreate the container:

```yaml {filename="docker-compose.yml"}
volumes:
  - /var/log:/var/log:ro
```

## Docker Container Logs

Alloy can automatically discover and collect logs from all running Docker containers — no manual configuration needed per container.

Create an Alloy config file for Docker log collection:

```bash
nano alloy/config/docker-logs.alloy
```

```hcl {filename="docker-logs.alloy"}
// Discover all running Docker containers
discovery.docker "containers" {
  host = "unix:///var/run/docker.sock"
}

// Extract useful labels from container metadata
discovery.relabel "containers" {
  targets = discovery.docker.containers.targets

  rule {
    source_labels = ["__meta_docker_container_name"]
    target_label  = "container"
    regex         = "/(.*)"
    replacement   = "$1"
  }

  rule {
    source_labels = ["__meta_docker_container_log_stream"]
    target_label  = "stream"
  }
}

// Collect logs from discovered containers
loki.source.docker "containers" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.relabel.containers.output
  forward_to = [loki.process.containers.receiver]
}

// Add a static job label and forward to Loki
loki.process "containers" {
  stage.static_labels {
    values = {
      job = "docker",
    }
  }
  forward_to = [loki.write.default.receiver]
}
```

This automatically picks up containers as they start and stop — no Alloy restart required.

### Docker Socket Access

Alloy needs the Docker socket mounted. Add it alongside the log directory volume in your Alloy `docker-compose.yml`:

```yaml {filename="docker-compose.yml"}
volumes:
  - /var/log:/var/log:ro
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

Recreate the Alloy container to apply the volume changes:

```bash
docker compose up -d alloy
```

## Apply Configuration

Restart Alloy to load the new config files:

```bash
docker restart alloy
```

## Verification

Open the Alloy Web UI and confirm the components are healthy:

- `loki.source.file`
- `loki.source.docker`

Then query in Grafana's Explore view to confirm logs are flowing:

```logql
{job="syslog"}
```

```logql
{job="docker"}
```

Filter by container name for more targeted queries:

```logql
{job="docker", container="traefik"}
```
