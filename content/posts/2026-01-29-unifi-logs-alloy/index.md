---
title: Unifi Syslog with Alloy and Loki
description: Send Unifi Syslog to Loki with Alloy
date: 2026-01-29
draft: false
categories:
  - Network
  - Unifi
tags:
  - unifi
  - loki
  - logs
  - alloy
cover: cover.jpg
---

Unifi network devices generate valuable logs that can help you troubleshoot network issues and monitor your devices. By sending these syslog messages to Loki using Grafana Alloy, you can centralize your network logs alongside your application logs for unified observability.

This guide we will only focus on device logs. Securtiy and firewall logs are out of scope.

## Prerequisites

- Grafana Alloy installed (or can be deployed via Docker)
- Grafana and Loki instance running (see my [Log Monitoring with Loki & Promtail]({{< ref "/posts/2024-06-24-log-monitoring-with" >}}) post)
- Unifi Controller with network devices configured

## Why Grafana Alloy?

Grafana Alloy is the next-generation telemetry collector that replaces Promtail. It supports multiple data formats including logs, metrics, traces, and profiles. For syslog collection, Alloy provides:

- Native syslog receiver (no need for external syslog daemons)
- Powerful log processing and relabeling capabilities
- Lower resource usage compared to traditional collectors
- Unified configuration for all telemetry types

## Setup Grafana Alloy

First, create a folder to hold the Docker Compose file and Alloy configuration:

```bash
mkdir alloy
```

Create the Docker Compose file:

```bash
nano alloy/docker-compose.yml
```

Paste the following content:

```yaml {filename="docker-compose.yml"}
services:
  alloy:
    image: grafana/alloy:latest
    container_name: alloy
    restart: unless-stopped
    environment:
      - TZ=Europe/Amsterdam
    ports:
      - "12345:12345"
      - "514:514/udp"  # Syslog UDP
    volumes:
      - ./config.alloy:/etc/alloy/config.alloy:ro
      - alloy-data:/var/lib/alloy/data
    command:
      - run
      - --server.http.listen-addr=0.0.0.0:12345
      - --storage.path=/var/lib/alloy/data
      - /etc/alloy/config.alloy
    networks:
      - backend

networks:
  backend:
    name: backend

volumes:
  alloy-data:
    name: alloy-data
```

## Configure Alloy for Syslog

Create the Alloy configuration file:

```bash
nano alloy/config.alloy
```

Paste the following configuration:

```hcl {filename="config.alloy"}
/* UniFi Syslog (RFC3164) - Relabel rules to capture syslog metadata */
loki.relabel "unifi_syslog" {
  forward_to = []

  // Copy severity first (for error, debug, or unknown values)
  rule {
    source_labels = ["__syslog_message_severity"]
    target_label  = "detected_level"
  }
  // Then normalize specific values (these overwrite the above)
  rule {
    source_labels = ["__syslog_message_severity"]
    regex         = "(?i)(emergency|alert|critical)"
    target_label  = "detected_level"
    replacement   = "critical"
  }
  rule {
    source_labels = ["__syslog_message_severity"]
    regex         = "(?i)(warning)"
    target_label  = "detected_level"
    replacement   = "warn"
  }
  rule {
    source_labels = ["__syslog_message_severity"]
    regex         = "(?i)(notice|informational)"
    target_label  = "detected_level"
    replacement   = "info"
  }

  // Map hostname from syslog header
  rule {
    source_labels = ["__syslog_message_hostname"]
    target_label  = "host"
  }

  // Map app name from syslog header
  rule {
    source_labels = ["__syslog_message_app_name"]
    target_label  = "app"
  }
}

loki.source.syslog "unifi" {
  listener {
    address       = "0.0.0.0:514"
    protocol      = "udp"
    syslog_format = "rfc3164"
    use_incoming_timestamp = false
    labels        = {
      job      = "unifi",
    }
  }

  relabel_rules = loki.relabel.unifi_syslog.rules
  forward_to    = [loki.process.unifi.receiver]
}

loki.process "unifi" {
  // Extract app and message from UniFi syslog content
  // Format 1 (AP/Switch): "mac,device-firmware: process[pid]: message"
  //   Example: "6c63f8863465,U7-Pro-Wall-8.3.2+18064: hostapd[5343]: wifi1ap6: STA ..."
  // Format 2 (Gateway): "hostname process[pid]: message"
  //   Example: "UCG-Fiber bash[2616997]: HISTORY: ..."
  stage.regex {
    expression = "^(?:[\\w,\\-\\.\\+]+:\\s+|[\\w\\-]+\\s+)?(?P<app>[\\w\\-]+)(?:\\[\\d+\\])?:\\s*(?P<message>.*)$"
  }

  // Set app label from regex
  stage.labels {
    values = {
      app = "",
    }
  }

  // Output just the message content
  stage.output {
    source = "message"
  }

  forward_to = [loki.write.default.receiver]
}

// Loki write endpoint
loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

### Configuration Breakdown

This configuration includes three main components that work together to collect, process, and forward Unifi syslog messages to Loki.

#### 1. Relabel Rules (`loki.relabel "unifi_syslog"`)

The relabel component extracts and normalizes metadata from the syslog headers:

**Severity Normalization:**
- Converts syslog severity levels (emergency, alert, critical etc) to standardized labels
- Creates a `detected_level` label for filtering logs by severity in Grafana

**Metadata Extraction:**
- `host`: Captures the hostname of the device sending logs (e.g., "UCG-Fiber", "U7-Pro-Wall")
- `app`: Extracts the application or process name from the syslog header

These labels make it easy to filter logs by device or severity without parsing the log content.

#### 2. Syslog Listener (`loki.source.syslog "unifi"`)

The syslog source receives incoming log messages:

**Listener Configuration:**
- `address`: Binds to all interfaces on port 514 (standard syslog port)
- `protocol`: Uses UDP, the most common syslog transport protocol
- `syslog_format`: Parses RFC3164 format, which Unifi devices use
- `use_incoming_timestamp`: Set to false to use Alloy's timestamp instead of the device timestamp

**Static Labels:**
- `job="unifi"`: Identifies all logs from this source as Unifi logs
- `platform="network"`: Categorizes these as network infrastructure logs

**Pipeline:**
- Applies the relabel rules defined above
- Forwards logs to the processing stage

#### 3. Log Processing (`loki.process "unifi"`)

This component parses and cleans Unifi-specific log formats:

**Regex Extraction:**
Unifi devices use different log formats depending on the device type:
- **Access Points/Switches**: Include MAC address and firmware version
  - Example: `6c63f8863465,U7-Pro-Wall-8.3.2+18064: hostapd[5343]: wifi1ap6: STA connected`
- **Gateways**: Use hostname and process name
  - Example: `UCG-Fiber bash[2616997]: HISTORY: command executed`

The regex pattern captures:
- `app`: The process or service name (hostapd, bash, kernel, etc.)
- `message`: The actual log message content

**Output Stage:**
- Extracts just the message content, removing metadata already captured as labels
- Results in cleaner, more readable logs in Grafana

#### 4. Loki Write (`loki.write "default"`)

The final component sends processed logs to Loki:

- `endpoint.url`: The Loki push API endpoint
- Uses the Docker network name `loki` to connect to Loki running in the same Docker network
- Handles batching and retries automatically

## Start Alloy

Deploy the Alloy container:

```bash
docker compose -f alloy/docker-compose.yml up -d
```

Verify Alloy is running and check the logs:

```bash
docker logs alloy
```

You should see messages indicating that Alloy has started and the syslog listener is active.

## Configure Unifi Devices

Now configure your Unifi Controller to send syslog messages to Alloy.

### Using Unifi Controller

1. Open your Unifi Controller
2. Navigate to **Settings** > **Cyber Secure**
3. Go to  to **Traffic Logging**
4. Set **Activity Logging (Syslog)** to **SIEM Server**
5. Set the **IP Address** to your Alloy server IP (e.g., `192.168.1.100`)
6. Set the **Port** to `514`
7. Click **Apply Changes**

## Verify Log Collection

After configuring your Unifi devices, logs should start flowing to Loki within seconds.

### Check in Grafana

1. Open Grafana and navigate to **Explore**
2. Select **Loki** as the datasource
3. Run a query to see Unifi logs:

```
{job="unifi"}
```

You should see syslog messages from your Unifi devices, including authentication events, DHCP assignments, wireless connections, and security events.

## Example Queries

With the labels and processing configured above, you can create powerful queries to analyze your network logs.

### Basic Queries

**All Unifi logs:**
```
{job="unifi"}
```

**Logs from a specific device:**
```
{job="unifi", host="UCG-Fiber"}
```

**Logs from a specific application:**
```
{job="unifi", app="hostapd"}
```

## Summary

With Grafana Alloy configured to receive Unifi syslog messages, you now have centralized network logging alongside your application logs in Loki. This unified observability platform makes it easier to correlate network events with application behavior, troubleshoot issues, and maintain security.

The modern Alloy architecture provides better performance and more flexible log processing compared to traditional syslog daemons, while integrating seamlessly with the Grafana ecosystem.
