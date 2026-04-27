---
title: "Grafana Observability: Alerting"
description: Set up Grafana alert rules against your Prometheus metrics and get notified via Discord when something breaks.
date: 2026-02-12
draft: false
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
    ├── dashboards/
    └── alerting/
        ├── contact-points.yaml
        ├── policies.yaml
        ├── rules.yaml
        └── templates.yaml
```

## Contact Point

In your Discord server go to **Settings → Integrations → Webhooks → New Webhook** and copy the webhook URL.

Instead of sending Grafana's default Discord payload, define a notification template so the message is easier to scan in chat:

```yaml {filename="alerting/templates.yaml"}
apiVersion: 1
templates:
  - orgId: 1
    name: discord.message
    template: |
      {{ define "discord.message" }}
      {{ if eq .Status "resolved" }}✅ **Resolved**{{ else }}🔴 **Firing**{{ end }}
      {{ range .Alerts }}
      **{{ .Labels.alertname }}**
      {{ .Annotations.summary }}
      {{ if .Labels.name }}Container: `{{ .Labels.name }}`{{ else if .Labels.cn }}Certificate: `{{ .Labels.cn }}`{{ else if .Labels.instance }}Instance: `{{ .Labels.instance }}`{{ end }}{{ if .Labels.severity }} | Severity: {{ .Labels.severity }}{{ end }}
      {{ end }}
      {{ end }}
```

Then provision the Discord contact point and render that template into the message body:

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
          message: "{{ template \"discord.message\" . }}"
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

You can also split alerts into categories such as `system`, `infra`, and `docker`. The useful part is not just the folder layout in Grafana, but the labels on each rule. Once a rule carries a label like `scope: system`, you can route or filter it however you like later.

```yaml {filename="alerting/policies.yaml"}
apiVersion: 1
policies:
  - orgId: 1
    receiver: Discord
    routes:
      - receiver: Discord
        object_matchers:
          - ["scope", "=", "system"]
      - receiver: Discord
        object_matchers:
          - ["scope", "=", "infra"]
      - receiver: Discord
        object_matchers:
          - ["scope", "=", "docker"]
```

## Notification Template

Grafana notification templates use Go templating syntax. In this example, the template does three things:

- Shows a different header for firing and resolved alerts
- Loops over `.Alerts` so grouped notifications still include every alert
- Pulls fields from labels and annotations, including the `summary` we define on each rule

That keeps the Discord message compact while still including the instance and severity at a glance.

## Alert Rules

### Structure

Each rule uses two query steps — a Prometheus query (refId `A`) and a threshold expression (refId `B`). Keeping the threshold separate from the PromQL prevents Grafana from treating an empty result (condition not met) as missing data and firing a false `DatasourceNoData` alert.

You do not need to keep everything in one alert group either. A common split is:

- `Systems` for host-level CPU, memory, disk, temperature, and reboot alerts
- `Infrastructure` for service availability and network-level checks
- `Docker` for container restarts, unhealthy containers, or missing exporters

Here is the full ruleset, split into three groups:

```yaml {filename="alerting/rules.yaml"}
apiVersion: 1
groups:
  - orgId: 1
    name: systems
    folder: Systems
    interval: 1m
    rules:
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
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "5"
          summary: "{{ $labels.instance }} CPU above 80% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"

      - uid: memory-high
        title: Memory Usage High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100
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
                      - 85
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
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "6"
          summary: "{{ $labels.instance }} memory above 85% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"

      - uid: swap-high
        title: Swap Usage High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: (1 - (node_memory_SwapFree_bytes / node_memory_SwapTotal_bytes)) * 100
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
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "14"
          summary: "{{ $labels.instance }} swap above 80% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"

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
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "16"
          summary: "{{ $labels.instance }} disk below 10% (current: {{ $values.A.Value | printf \"%.1f\" }}%)"

      - uid: load-high
        title: High Load Average
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: node_load15 / count without(cpu, mode) (node_cpu_seconds_total{mode="idle"})
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
                      - 1
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
        for: 10m
        labels:
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "17"
          summary: "{{ $labels.instance }} load average high (current: {{ $values.A.Value | printf \"%.2f\" }} per CPU)"

      - uid: temp-high
        title: High Temperature
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: max by(instance) (node_hwmon_temp_celsius)
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
                      - 85
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
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "18"
          summary: "{{ $labels.instance }} temperature above 85°C (current: {{ $values.A.Value | printf \"%.0f\" }}°C)"

      - uid: system-reboot
        title: System Reboot Detected
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: time() - node_boot_time_seconds
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
                      - 300
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
        for: 0m
        labels:
          scope: system
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "1"
          summary: "{{ $labels.instance }} has rebooted (uptime: {{ $values.A.Value | printf \"%.0f\" }}s)"

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
              expr: up{job="unix"} == 0
              instant: true
              refId: A
        noDataState: Alerting
        execErrState: Alerting
        for: 2m
        labels:
          scope: infra
          severity: critical
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "1"
          summary: "{{ $labels.instance }} is unreachable"

      - uid: network-errors
        title: Network Errors
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: sum by(instance) (rate(node_network_receive_errs_total{device!~"veth.+|br.+|docker0|lo"}[5m]) + rate(node_network_transmit_errs_total{device!~"veth.+|br.+|docker0|lo"}[5m]))
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
          scope: infra
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "20"
          summary: "{{ $labels.instance }} network errors detected"

      - uid: network-high
        title: Network Throughput High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: sum by(instance) (rate(node_network_receive_bytes_total{device!~"veth.+|br.+|docker0|lo"}[5m]) + rate(node_network_transmit_bytes_total{device!~"veth.+|br.+|docker0|lo"}[5m]))
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
                      - 100000000
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
          scope: infra
          severity: warning
        annotations:
          __dashboardUid__: "ddmvax2tzuv40c"
          __panelId__: "8"
          summary: "{{ $labels.instance }} network throughput above 100 MB/s (current: {{ humanize1024 $values.A.Value }}/s)"

      - uid: traefik-down
        title: Traefik Down
        condition: A
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: up{job="traefik"} == 0
              instant: true
              refId: A
        noDataState: Alerting
        execErrState: Alerting
        for: 2m
        labels:
          scope: infra
          severity: critical
        annotations:
          __dashboardUid__: "ddmlqvk12uozka"
          __panelId__: "1"
          summary: "Traefik metrics endpoint {{ $labels.instance }} is unreachable"

      - uid: traefik-5xx-high
        title: Traefik 5xx Rate High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: sum by(instance) (rate(traefik_service_requests_total{code=~"5..", protocol="http"}[5m]))
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
                      - 0.1
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
          scope: infra
          severity: warning
        annotations:
          __dashboardUid__: "ddmlqvk12uozka"
          __panelId__: "6"
          summary: "{{ $labels.instance }} Traefik 5xx rate is high (current: {{ $values.A.Value | printf \"%.2f\" }} req/s)"

      - uid: traefik-latency-high
        title: Traefik Response Time High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: sum by(instance) (rate(traefik_service_request_duration_seconds_sum[5m])) / sum by(instance) (rate(traefik_service_request_duration_seconds_count[5m]))
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
                      - 1
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
        for: 10m
        labels:
          scope: infra
          severity: warning
        annotations:
          __dashboardUid__: "ddmlqvk12uozka"
          __panelId__: "7"
          summary: "{{ $labels.instance }} Traefik response time is high (current: {{ $values.A.Value | printf \"%.2f\" }}s)"

      - uid: traefik-cert-expiring
        title: Traefik Certificate Expiring Soon
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: (traefik_tls_certs_not_after{san=~".*"} - time()) / 86400
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
                      - 14
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
        for: 0m
        labels:
          scope: infra
          severity: warning
        annotations:
          __dashboardUid__: "ddmlqvk12uozka"
          __panelId__: "34"
          summary: "Certificate {{ $labels.cn }} expires soon ({{ $values.A.Value | printf \"%.1f\" }} days left)"

  - orgId: 1
    name: docker
    folder: Docker
    interval: 1m
    rules:
      - uid: docker-container-down
        title: Docker Container Down
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: time() - container_last_seen{container_label_com_docker_compose_project!="", name!=""} > 60
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
                      - 0
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
        for: 2m
        labels:
          scope: docker
          severity: critical
        annotations:
          __dashboardUid__: "docker-metrics"
          __panelId__: "200"
          summary: "{{ $labels.name }} has not reported metrics for more than 60 seconds"

      - uid: docker-container-restart-loop
        title: Docker Container Restart Loop
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 900
              to: 0
            model:
              expr: changes(container_start_time_seconds{container_label_com_docker_compose_project!="", name!=""}[15m])
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
                      - 2
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
        for: 0m
        labels:
          scope: docker
          severity: critical
        annotations:
          __dashboardUid__: "docker-metrics"
          __panelId__: "200"
          summary: "{{ $labels.name }} restarted {{ $values.A.Value | printf \"%.0f\" }} times in the last 15 minutes"

      - uid: docker-container-cpu-high
        title: Docker Container CPU High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: sum by(name) (rate(container_cpu_usage_seconds_total{container_label_com_docker_compose_project!="", name!=""}[5m]))
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
                      - 0.8
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
        for: 10m
        labels:
          scope: docker
          severity: warning
        annotations:
          __dashboardUid__: "docker-metrics"
          __panelId__: "2"
          summary: "{{ $labels.name }} CPU usage is high (current: {{ $values.A.Value | printf \"%.2f\" }} cores)"

      - uid: docker-container-memory-high
        title: Docker Container Memory High
        condition: B
        data:
          - refId: A
            datasourceUid: prometheus
            relativeTimeRange:
              from: 300
              to: 0
            model:
              expr: container_memory_working_set_bytes{container_label_com_docker_compose_project!="", name!=""}
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
                      - 1073741824
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
        for: 10m
        labels:
          scope: docker
          severity: warning
        annotations:
          __dashboardUid__: "docker-metrics"
          __panelId__: "3"
          summary: "{{ $labels.name }} memory usage is high (current: {{ humanize1024 $values.A.Value }})"
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

Open Grafana → **Alerting → Alert rules** and confirm the rules appear under the expected folders such as **Systems**, **Infrastructure**, or **Docker**, with state **Normal**.

To trigger a test notification, open **Alerting → Contact points**, find Discord, and click **Test**.

To verify the CPU alert end-to-end, stress all cores for long enough to survive the 5-minute pending window:

```bash
stress-ng --cpu $(nproc) --timeout 360s
```
