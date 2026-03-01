---
title: Monitoring MikroTik with Grafana
description: Collect MikroTik router metrics via SNMP and forward syslog to Loki using Grafana Alloy for full observability.
date: 2026-02-17
draft: true
categories:
  - Networking
  - Monitoring
tags:
  - mikrotik
  - snmp
  - loki
  - alloy
  - grafana
  - prometheus
cover: cover.jpg

---

MikroTik routers don't expose a native Prometheus endpoint, but they support both SNMP and remote syslog — making it straightforward to integrate them into a Grafana observability stack. This guide covers collecting system metrics via SNMP and centralizing logs in Loki, both using Grafana Alloy.

## Prerequisites

- Grafana, Alloy, Prometheus, and Loki already running. See the [Log Monitoring with Grafana Alloy and Loki]({{< ref "/posts/2026-02-05-log-monitoring-with-alloy" >}}) post for the observability stack setup.
- A MikroTik router configured as per the [Setting up a MikroTik Router]({{< ref "/posts/2025-01-05-setup-mikrotik-router" >}}) guide.

## Metrics via SNMP

### Enable SNMP on MikroTik

Enable SNMP on the router and restrict access to your LAN subnet:

```bash
/snmp
set enabled=yes contact="" location=""
set trap-community=public trap-version=2
/snmp community
set public addresses=192.168.1.0/24 read-access=yes write-access=no
```

Adjust `addresses=192.168.1.0/24` to match your LAN subnet.

### Configure Grafana Alloy

Create a new Alloy config file for SNMP collection:

```bash
nano alloy/config/mikrotik-snmp.alloy
```

```hcl {filename="mikrotik-snmp.alloy"}
// MikroTik SNMP metrics
prometheus.exporter.snmp "mikrotik" {
  config_file = "/etc/alloy/config/snmp.yml"

  target "router" {
    address     = "192.168.1.1"
    module      = "mikrotik"
    walk_params = "mikrotik"
  }

  walk_param "mikrotik" {
    retries         = 3
    timeout         = "10s"
    max_repetitions = 25
  }
}

prometheus.scrape "mikrotik" {
  targets         = prometheus.exporter.snmp.mikrotik.targets
  forward_to      = [prometheus.remote_write.default.receiver]
  job_name        = "mikrotik"
  scrape_interval = "60s"
}
```

Replace `192.168.1.1` with your router's IP. The 60s scrape interval is recommended since SNMP walks can be resource-intensive.

### SNMP Module Configuration

Create the `snmp.yml` module definition that specifies which OIDs to collect:

```bash
nano alloy/config/snmp.yml
```

```yaml {filename="snmp.yml"}
auths:
  mikrotik_v2:
    community: public
    version: 2

modules:
  mikrotik:
    walk:
      - sysUpTime
      - interfaces
      - ifXTable
      - 1.3.6.1.2.1.25.3.3.1.2  # CPU load
      - 1.3.6.1.2.1.25.2         # Storage/Memory
      - 1.3.6.1.4.1.14988.1.1.3  # MikroTik health OIDs
    metrics:
      - name: sysUpTime
        oid: 1.3.6.1.2.1.1.3
        type: gauge
        help: System uptime in hundredths of a second.

      - name: ifNumber
        oid: 1.3.6.1.2.1.2.1
        type: gauge
        help: Number of network interfaces.

      - name: ifHCInOctets
        oid: 1.3.6.1.2.1.31.1.1.1.6
        type: counter
        help: Total bytes received on the interface.
        indexes:
          - labelname: ifIndex
            type: Integer
        lookups:
          - labels: [ifIndex]
            labelname: ifDescr
            oid: 1.3.6.1.2.1.2.2.1.2
            type: DisplayString
          - labels: [ifIndex]
            labelname: ifAlias
            oid: 1.3.6.1.2.1.31.1.1.1.18
            type: DisplayString

      - name: ifHCOutOctets
        oid: 1.3.6.1.2.1.31.1.1.1.10
        type: counter
        help: Total bytes transmitted on the interface.
        indexes:
          - labelname: ifIndex
            type: Integer
        lookups:
          - labels: [ifIndex]
            labelname: ifDescr
            oid: 1.3.6.1.2.1.2.2.1.2
            type: DisplayString
          - labels: [ifIndex]
            labelname: ifAlias
            oid: 1.3.6.1.2.1.31.1.1.1.18
            type: DisplayString

      - name: ifOperStatus
        oid: 1.3.6.1.2.1.2.2.1.8
        type: gauge
        help: "Operational status of the interface: up(1), down(2)."
        indexes:
          - labelname: ifIndex
            type: Integer
        lookups:
          - labels: [ifIndex]
            labelname: ifDescr
            oid: 1.3.6.1.2.1.2.2.1.2
            type: DisplayString

      - name: hrProcessorLoad
        oid: 1.3.6.1.2.1.25.3.3.1.2
        type: gauge
        help: CPU load percentage per core.
        indexes:
          - labelname: hrDeviceIndex
            type: Integer

      - name: hrStorageUsed
        oid: 1.3.6.1.2.1.25.2.3.1.6
        type: gauge
        help: Amount of storage used (in allocation units).
        indexes:
          - labelname: hrStorageIndex
            type: Integer
        lookups:
          - labels: [hrStorageIndex]
            labelname: hrStorageDescr
            oid: 1.3.6.1.2.1.25.2.3.1.3
            type: DisplayString

      - name: hrStorageSize
        oid: 1.3.6.1.2.1.25.2.3.1.5
        type: gauge
        help: Total storage size (in allocation units).
        indexes:
          - labelname: hrStorageIndex
            type: Integer
        lookups:
          - labels: [hrStorageIndex]
            labelname: hrStorageDescr
            oid: 1.3.6.1.2.1.25.2.3.1.3
            type: DisplayString

      - name: hrStorageAllocationUnits
        oid: 1.3.6.1.2.1.25.2.3.1.4
        type: gauge
        help: Size of an allocation unit in bytes.
        indexes:
          - labelname: hrStorageIndex
            type: Integer
        lookups:
          - labels: [hrStorageIndex]
            labelname: hrStorageDescr
            oid: 1.3.6.1.2.1.25.2.3.1.3
            type: DisplayString

      - name: mtxrHlTemperature
        oid: 1.3.6.1.4.1.14988.1.1.3.10
        type: gauge
        help: Router board temperature in degrees Celsius (x0.1).

      - name: mtxrHlVoltage
        oid: 1.3.6.1.4.1.14988.1.1.3.8
        type: gauge
        help: Router board voltage in volts (x0.1).

    auth:
      community: public
      version: 2
```

The OIDs cover system uptime, interface traffic (64-bit RX/TX counters), interface status, CPU load, memory/storage, and MikroTik-specific board temperature and voltage.

> **Tip:** If you followed the Install Alloy guide, files in the `config/` directory are already mounted at `/etc/alloy/config/` inside the container.

## Logs via Syslog

### Configure MikroTik

Enable remote syslog forwarding on the router. Replace `172.16.10.2` with the IP address of your Alloy instance.

```bash
/system logging action
add name=loki remote=172.16.10.2 remote-log-format=syslog syslog-facility=local0 target=remote
/system logging
add action=loki topics=info
add action=loki topics=warning
add action=loki topics=error
add action=loki topics=critical
```

Add or remove topics to control what gets forwarded. Common options: `info`, `warning`, `error`, `critical`, `firewall`, `dhcp`, `dns`, `wireless`.

To also capture firewall drop events, enable logging on the relevant rules:

```bash
/system logging
add action=loki topics=firewall

/ip firewall filter
set [find comment="drop all else" chain=forward] log=yes log-prefix="FW-DROP-FWD"
set [find comment="Drop all else" chain=input] log=yes log-prefix="FW-DROP-IN"
```

### Configure Grafana Alloy

Create a new Alloy config file for syslog collection:

```bash
nano alloy/config/mikrotik-syslog.alloy
```

```hcl {filename="mikrotik-syslog.alloy"}
/* MikroTik Syslog (BSD/RFC3164) */
loki.relabel "mikrotik_syslog" {
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

loki.source.syslog "mikrotik" {
  listener {
    address                = "0.0.0.0:514"
    protocol               = "udp"
    syslog_format          = "rfc3164"
    use_incoming_timestamp = false
    labels                 = {
      job = "mikrotik",
    }
  }

  relabel_rules = loki.relabel.mikrotik_syslog.rules
  forward_to    = [loki.write.default.receiver]
}
```

Restart Alloy to load the new configuration:

```bash
docker restart alloy
```

## Verification

**Metrics** — Open the Alloy Web UI and verify the `prometheus.exporter.snmp` component is healthy, then query in Grafana:

```promql
ifHCInOctets{job="mikrotik"}
```

**Logs** — Verify the `loki.source.syslog` component is healthy, then query in Grafana:

```logql
{job="mikrotik"}
```
