---
title: "Grafana Observability: Alerting"
description: Set up Grafana alert rules against your Prometheus metrics and get notified via Discord when something breaks.
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

### Structure

Each rule uses two query steps — a Prometheus query (refId `A`) and a threshold expression (refId `B`). Keeping the threshold separate from the PromQL prevents Grafana from treating an empty result (condition not met) as missing data and firing a false `DatasourceNoData` alert.

```yaml {filename="alerting/rules.yaml"}
apiVersion: 1
groups:
  - orgId: 1
    name: infrastructure
    folder: Infrastructure
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
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "1"
          summary: "{{ $labels.instance }} is unreachable"

      - uid: cpu-high
        title: CPU Usage High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[2m])) * 100)
              instant: true
              refId: A
          - refId: B
            datasourceUid: "__expr__"
            model:
              type: threshold
              expression: "A"
              refId: B
              conditions:
                - evaluator:
                    params:
                      - 80
                    type: gt
                  operator:
                    type: and
                  query:
                    params:
                      - A
                  reducer:
                    type: last
        noDataState: OK
        execErrState: Error
        for: 5m
        labels:
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "5"
          summary: "{{ $labels.instance }} CPU above 80% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"

      - uid: disk-low
        title: Disk Space Low
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100
              instant: true
              refId: A
          - refId: B
            datasourceUid: "__expr__"
            model:
              type: threshold
              expression: "A"
              refId: B
              conditions:
                - evaluator:
                    params:
                      - 10
                    type: lt
                  operator:
                    type: and
                  query:
                    params:
                      - A
                  reducer:
                    type: last
        noDataState: OK
        execErrState: Error
        for: 5m
        labels:
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "16"
          summary: "{{ $labels.instance }} disk below 10% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"
```

### Dashboard Linking

The `__dashboardUid__` and `__panelId__` annotations link each rule to a specific panel. When an alert fires, Grafana adds a red annotation line directly on the chart and a **Go to dashboard** button appears in the alert detail view, making it easy to jump straight to the relevant graph.

Replace `ddmvax2tzuv40c` with your own dashboard UID, found at the bottom of the dashboard JSON or in the dashboard URL.

## Apply Configuration

Restart Grafana to load the provisioned files:

```bash
docker restart grafana
```

## Verification

Open Grafana → **Alerting → Alert rules** and confirm all three rules appear under the **Infrastructure** folder with state **Normal**.

To trigger a test notification, open **Alerting → Contact points**, find Discord, and click **Test**.

To verify the CPU alert end-to-end, stress all cores for long enough to survive the 5-minute pending window:

```bash
stress-ng --cpu $(nproc) --timeout 360s
```
