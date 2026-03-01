---
title: Monitoring VyOS with Grafana
description: Monitor your VyOS router with Prometheus for real-time system and connection metrics, and collect syslog events with Grafana Alloy and Loki.
date: 2026-03-03
lastmod: 2026-03-03
draft: true
categories:
  - Networking
  - Monitoring
tags:
  - vyos
  - prometheus
  - loki
  - alloy
  - grafana
cover: cover.jpg

---

VyOS has built-in support for Prometheus exporters, making it easy to integrate your router into an existing monitoring stack. This guide covers collecting system metrics via Node Exporter, connection metrics via Blackbox Exporter, and centralizing syslog in Loki — all using Grafana Alloy.

## Prerequisites

- Grafana, Alloy, Prometheus, and Loki already running. See the [Log Monitoring with Grafana Alloy and Loki]({{< ref "/posts/2026-02-05-log-monitoring-with-alloy" >}}) post for the observability stack setup.
- A VyOS router configured as per the [Setting up a VyOS Router]({{< ref "/posts/2025-03-25-setup-vyos-router" >}}) guide.

## Metrics

### System Metrics with Node Exporter

VyOS includes a built-in Node Exporter that exposes CPU, memory, disk, and network statistics.

Enable it on VyOS, replacing `192.168.1.1` with your router's LAN IP:

```bash
set service monitoring prometheus node-exporter listen-address 192.168.1.1
set service monitoring prometheus node-exporter port 9100
commit; save
```

Add a scrape job to your `prometheus.yml`:

```yaml {filename="prometheus.yml"}
  - job_name: 'vyos'
    scrape_interval: 5s
    static_configs:
      - targets: ['192.168.1.1:9100']
        labels:
          router: vyos
```

### Connection Metrics with Blackbox Exporter

VyOS also includes a built-in Blackbox Exporter that measures internet reachability and latency via ICMP probes.

Enable it on VyOS:

```bash
set service monitoring prometheus blackbox-exporter listen-address '192.168.1.1'
set service monitoring prometheus blackbox-exporter modules icmp name icmp preferred-ip-protocol ipv4
commit; save
```

Add a scrape job to your `prometheus.yml`:

```yaml {filename="prometheus.yml"}
  - job_name: 'blackbox_icmp'
    scrape_interval: 15s
    metrics_path: /probe
    params:
      module: [icmp]
    static_configs:
      - targets: ['connectivitycheck.gstatic.com']
        labels:
          endpoint: "Google"
      - targets: ['dualstack.nonssl.global.fastly.net']
        labels:
          endpoint: "Fastly"
      - targets: ['workers.dev']
        labels:
          endpoint: "Cloudflare"
    relabel_configs:
      - source_labels: [__address__]
        target_label: __param_target
      - target_label: router
        replacement: vyos
      - target_label: __address__
        replacement: 192.168.1.1:9115
```

Restart Prometheus to apply both scrape jobs:

```bash
docker restart prometheus
```

You can use the pre-built [VyOS Dashboard](https://github.com/svenvg93/Grafana-Dashboard/tree/master/vyos) from GitHub to visualize the collected metrics.

## Logs via Syslog

### Configure VyOS

Enable syslog forwarding to Alloy. Replace `192.168.1.101` with your Alloy instance's IP:

```bash
set system syslog local facility all level 'info'
set system syslog local facility local7 level 'debug'
set system syslog remote 192.168.1.101 facility all level 'all'
set system syslog remote 192.168.1.101 port '514'
set system syslog remote 192.168.1.101 protocol 'udp'
commit; save
```

### Configure Grafana Alloy

Create a new Alloy config file for VyOS log collection:

```bash
nano alloy/config/vyos-syslog.alloy
```

```hcl {filename="vyos-syslog.alloy"}
/* VyOS Syslog (RFC3164) */
loki.relabel "vyos_syslog" {
  forward_to = []

  rule {
    source_labels = ["__syslog_message_hostname"]
    target_label  = "host"
  }

  rule {
    source_labels = ["__syslog_message_app_name"]
    target_label  = "service_name"
  }

  rule {
    source_labels = ["__syslog_message_severity"]
    target_label  = "detected_level"
  }
}

loki.source.syslog "vyos" {
  listener {
    address                = "0.0.0.0:514"
    protocol               = "udp"
    syslog_format          = "rfc3164"
    use_incoming_timestamp = false
    labels                 = {
      job = "vyos",
    }
  }

  relabel_rules = loki.relabel.vyos_syslog.rules
  forward_to    = [loki.write.default.receiver]
}
```

Restart Alloy to pick up the new configuration:

```bash
docker restart alloy
```

## Verification

**Metrics** — Query in Grafana to confirm data is flowing:

```promql
node_cpu_seconds_total{router="vyos"}
```

**Logs** — Query in Grafana's Explore view:

```logql
{job="vyos"}
```
