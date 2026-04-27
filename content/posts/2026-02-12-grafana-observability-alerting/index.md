---
title: "Grafana Observability: Alerting"
description: Set up Grafana alert rules against your Prometheus metrics and get notified via Discord when something breaks in your homelab.
date: 2026-02-12
draft: true
categories:
  - Monitoring
tags:
  - docker
  - grafana
  - prometheus
cover: cover.svg
series:
  - Grafana Observability
series_order: 4
lightbox:
  enabled: true
---

Collecting metrics is only half the picture — you also need to know when something breaks. Grafana Alerting evaluates rules against your Prometheus data and fires notifications to a contact point of your choice.

## Prerequisites

- Prometheus running with metrics flowing in
- Grafana running with Prometheus added as a datasource
- Setup from [Setting Up Your Observability Stack]({{< ref "/posts/2026-01-08-grafana-observability-setup" >}})

## How Grafana Alerting Works

Three components work together:

- **Alert Rules** — PromQL expressions evaluated on a schedule; fire when a condition is met
- **Contact Points** — where notifications are sent (Discord, webhook, email)
- **Notification Policies** — route alerts to the right contact point

All three can be provisioned from YAML files, keeping your alerting config in version control alongside the rest of your stack.

## Directory Structure

Add an `alerting/` folder inside your existing Grafana provisioning directory:

```bash
grafana/
└── provisioning/
    ├── datasources/
    └── alerting/
        ├── contact-points.yaml
        ├── policies.yaml
        └── rules.yaml
```

## Contact Point

In your Discord server go to **Settings → Integrations → Webhooks → New Webhook** and copy the webhook URL, then provision the contact point:

```yaml {filename="alerting/contact-points.yaml"}
apiVersion: 1
contactPoints:
  - orgId: 1
    name: Discord
    receivers:
      - uid: discord
        type: discord
        settings:
          url: "${DISCORD_WEBHOOK_URL}"
```

Add the webhook URL to your Grafana container environment:

```yaml {filename="docker-compose.yml"}
environment:
  - DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your-id/your-token
```

## Notification Policy

Route all alerts to Discord by default:

```yaml {filename="alerting/policies.yaml"}
apiVersion: 1
policies:
  - orgId: 1
    receiver: Discord
```

## Alert Rules

Create rules for the two most important homelab alerts — host down and disk filling up:

```yaml {filename="alerting/rules.yaml"}
apiVersion: 1
groups:
  - orgId: 1
    name: homelab
    folder: Homelab
    interval: 1m
    rules:
      - uid: host-down
        title: Host Down
        condition: A
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: up == 0
              instant: true
              refId: A
        noDataState: Alerting
        execErrState: Alerting
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "{{ $labels.instance }} is unreachable"

      - uid: disk-low
        title: Disk Space Low
        condition: A
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: |
                (node_filesystem_avail_bytes{mountpoint="/"}
                  / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
              instant: true
              refId: A
        noDataState: NoData
        execErrState: Error
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "{{ $labels.instance }} disk below 10%"
```

## Apply Configuration

Restart Grafana to load the provisioned files:

```bash
docker restart grafana
```

## Verification

Open Grafana → **Alerting → Alert rules** and confirm both rules appear with state **Normal**.

To trigger a test notification, open **Alerting → Contact points**, find Discord, and click **Test**.
