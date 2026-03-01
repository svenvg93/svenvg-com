---
title: Monitoring GL.iNet with Grafana
description: Monitor your GL.iNet (OpenWRT) router with Prometheus metrics and forward syslog to Loki using Grafana Alloy.
date: 2026-03-01
draft: false
categories:
  - Networking
  - Monitoring
tags:
  - gl-inet
  - prometheus
  - loki
  - alloy
  - grafana
  - openwrt
cover: cover.jpg

---

GL.iNet routers run OpenWRT, which has native Prometheus exporter packages and remote syslog support. This guide covers installing the Lua-based node exporter for metrics and forwarding syslog to Loki via Grafana Alloy — giving you full observability of your GL.iNet router.

> **Note:** This guide is written for GL.iNet routers, but the same steps apply to any router running standard OpenWRT.

## Prerequisites

- Grafana, Alloy, Prometheus, and Loki already running. See the [Log Monitoring with Grafana Alloy and Loki]({{< ref "/posts/2026-02-05-log-monitoring-with-alloy" >}}) post for the observability stack setup.
- A GL.iNet router set up as per the [GL.iNet Travel Router Setup]({{< ref "/posts/2025-04-05-setup-travel-router" >}}) guide.

## Metrics

### Install the Prometheus Exporter

Connect to your router via SSH and install the exporter packages:

```bash
opkg update
opkg install prometheus-node-exporter-lua \
  prometheus-node-exporter-lua-openwrt \
  prometheus-node-exporter-lua-wifi \
  prometheus-node-exporter-lua-wifi_stations \
  prometheus-node-exporter-lua-netstat \
  prometheus-node-exporter-lua-nat_traffic \
  prometheus-node-exporter-lua-thermal \
  prometheus-node-exporter-lua-hwmon \
  prometheus-node-exporter-lua-uci_dhcp_host
```

Alternatively, install packages through **Admin Panel** → **Applications** → **Plug-ins**.

| Package | Description |
|---------|-------------|
| `prometheus-node-exporter-lua` | Core exporter — CPU, memory, disk, network |
| `prometheus-node-exporter-lua-openwrt` | OpenWRT-specific metrics |
| `prometheus-node-exporter-lua-wifi` | Wi-Fi interface statistics |
| `prometheus-node-exporter-lua-wifi_stations` | Connected Wi-Fi client metrics |
| `prometheus-node-exporter-lua-netstat` | TCP/UDP connection statistics |
| `prometheus-node-exporter-lua-nat_traffic` | NAT traffic counters |
| `prometheus-node-exporter-lua-thermal` | Thermal zone temperatures |
| `prometheus-node-exporter-lua-hwmon` | Hardware sensor readings |
| `prometheus-node-exporter-lua-uci_dhcp_host` | DHCP host information |

### Enable the Exporter

By default the exporter only listens on localhost. Expose it on the LAN interface:

```bash
uci set prometheus-node-exporter-lua.main.listen_interface='lan'
uci set prometheus-node-exporter-lua.main.listen_port='9100'
uci commit prometheus-node-exporter-lua
/etc/init.d/prometheus-node-exporter-lua enable
/etc/init.d/prometheus-node-exporter-lua restart
```

Verify from another machine on the same network:

```bash
curl http://192.168.8.1:9100/metrics
```

### Add Prometheus Scrape Job

Add the following to your `prometheus.yml`, then restart Prometheus:

```yaml {filename="prometheus.yml"}
  - job_name: 'glinet'
    scrape_interval: 15s
    static_configs:
      - targets: ['192.168.8.1:9100']
        labels:
          router: glinet
```

```bash
docker restart prometheus
```

Use the pre-built [GL.iNet / OpenWRT Dashboard](https://github.com/svenvg93/Grafana-Dashboard/tree/master/openwrt) to visualize the metrics in Grafana.

## Logs via Syslog

### Configure GL.iNet

#### Via SSH

Replace `192.168.8.101` with the IP of your Alloy instance:

```bash
uci set system.@system[0].log_ip='192.168.8.101'
uci set system.@system[0].log_port='514'
uci set system.@system[0].log_proto='udp'
uci set system.@system[0].conloglevel='7'
uci commit system
/etc/init.d/log restart
```

The `conloglevel` controls verbosity: `7` = debug, `6` = info, `4` = warning, `3` = error.

#### Via LuCI

> **Tip:** LuCI is not installed by default on GL.iNet routers. Enable it under **Admin Panel** → **System** → **Advanced Settings**.

1. Navigate to **System** → **System** → **Logging**
2. Set **External system log server** to your Alloy instance IP
3. Set port to `514`, protocol to **UDP**, log level to **Info**
4. Click **Save & Apply**

### Configure Grafana Alloy

Create a new Alloy config file for GL.iNet syslog collection:

```bash
nano alloy/config/glinet-syslog.alloy
```

```hcl {filename="glinet-syslog.alloy"}
/* GL.iNet Syslog (BSD/RFC3164) */
loki.relabel "glinet_syslog" {
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

loki.source.syslog "glinet" {
  listener {
    address                = "0.0.0.0:514"
    protocol               = "udp"
    syslog_format          = "rfc3164"
    use_incoming_timestamp = false
    labels                 = {
      job = "glinet",
    }
  }

  relabel_rules = loki.relabel.glinet_syslog.rules
  forward_to    = [loki.write.default.receiver]
}
```

Restart Alloy to load the new configuration:

```bash
docker restart alloy
```

## Verification

**Metrics** — Query in Grafana to confirm data is flowing:

```promql
node_cpu_seconds_total{router="glinet"}
```

**Logs** — Query in Grafana's Explore view:

```logql
{job="glinet"}
```
