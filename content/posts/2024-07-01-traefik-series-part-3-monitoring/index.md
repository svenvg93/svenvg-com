---
title: Traefik Series Part 3 | Monitoring with Grafana, Prometheus, and Loki
description: In Part 3 of the Traefik series, learn how to monitor your Traefik instance’s performance using Prometheus, Loki, and Grafana.
date: 2024-07-01
draft: false
categories:
  - Networking
  - Reverse Proxy
tags:
  - traefik
  - metrics
  - logging
cover: cover.jpg
---

We all enjoy visually appealing graphs filled with data, especially for the services we host. Thankfully, Traefik exposes useful metrics on EntryPoints, Routers, Services, and more. By using Prometheus to scrape these metrics and integrating Promtail with Loki for log collection, we can create a complete monitoring solution.

Setting up Grafana, Prometheus, Promtail and Loki is out of scope of this Story. See my other stories on how to setup [Grafana & Prometheus](../system-monitoring-series-part-1-prometheus) and [Promtail & Loki](../system-monitoring-series-part-2-loki-promtail)

## Key Components

1. Traefik - Exposes metrics for monitoring various components of your services.
2. Prometheus - Scrapes and stores metrics data from Traefik, providing a time-series database for easy access.
3. Loki - Aggregates log data, allowing for centralized logging alongside metrics.
4. Promtail - Ships logs from your applications to Loki for efficient storage and querying.


## Metrics

### Traefik

To enable Traefik to expose metrics for Prometheus, you’ll need to modify the Traefik configuration file (<kbd>traefik.yml</kbd>) by adding a metrics section. This allows Prometheus to scrape the relevant metrics from Traefik.

Add the following configuration to your existing <kbd>traefik.yml</kbd> file:

```yaml
metrics:
  prometheus:
    addEntryPointsLabels: true
    addRoutersLabels: true
    addServicesLabels: true
```
By default, Traefik will expose metrics on the EntryPoint <kbd>traefik</kbd>. Metrics will be available at <kbd>:8080/metrics</kbd>.

After making these changes, restart your Traefik container to apply the new configuration:

```bash
docker restart traefik
```
You can verify if the metrics are available by visiting <kbd>http://traefik-ip:8080/metrics</kbd>.

Once this is set up, Traefik will expose the necessary metrics, and Prometheus can scrape them for monitoring and visualization.

### Prometheus
To ensure Prometheus collects metrics from Traefik, you need to add a scrape configuration to your existing prometheus configuration.

Add the following configuration to your <kbd>prometheus.yml</kbd>:
```yaml
scrape_configs:
  - job_name: 'traefik'
    scrape_interval: 5s
    static_configs:
      - targets: ['traefik-ip:8080']
```
Replace <kbd>traefik-ip</kbd> with the IP address of the Traefik container.

To apply the configuration changes, restart the Prometheus containers:

```bash
docker restart  prometheus
```

After the container is restarted, Prometheus will start scraping metrics from Traefik at the defined interval. You can now visualize these metrics in Grafana or any other monitoring tool you are using.

## Log files

To effectively monitor logs in Traefik, you’ll need to configure both Traefik logs and access logs. Follow these steps to set everything up.

### Traefik

Add the following sections to your existing <kbd>traefik.yml</kbd> configuration file:

```yaml
accessLog:
  filePath: "/log/access.log"
  format: json
  fields:
    defaultMode: keep
    names:
      StartUTC: drop
log:
  filePath: "/log/traefik.log"
  format: json
```
Explanation:
 - Access Logs: This configuration logs every request made to your services, including details like client IP, HTTP status codes, request method, etc. The log format is set to JSON for structured logging, and StartUTC is dropped to avoid UTC timestamps.
 - Traefik Logs: This captures logs about the Traefik service itself (startup, shutdown, configuration changes, etc.) in JSON format.

Next, you need to ensure that Traefik has access to the directory where logs will be stored. Modify your Traefik <kbd>docker-compose.yml</kbd> to include a volume mapping for the log directory:

```yaml
  volumes:
    - /var/log/traefik:/log
```
This will mount the host directory /var/log/traefik into the container at /log, where Traefik will write its log files.
To apply all the configuration changes (including the new volume), you’ll need to re-create the Traefik container. Run the following command:

```bash
docker compose up -d --force-recreate
```

### Promtail

To enable Promtail to scrape Traefik logs, you’ll need to add a new scrape configuration to your <kbd>promtail-config.yaml</kbd>. Here’s how to do it:

```yaml
scrape_configs:
- job_name: traefik
  static_configs:
  - targets:
      - traefik
    labels:
      job: traefik
      __path__: /logs/traefik/*log
```
After updating the configuration, you need to restart the Promtail service for the changes to take effect. Run the following command:

```bash
docker restart promtail
```

## Grafana Dashboard
Now that you’ve set up monitoring for Traefik using Grafana, Prometheus, Promtail, and Loki, it’s time to create a dashboard to visualize all the collected metrics and logs.

Traefik exposes a variety of metrics that you can use to monitor the health and performance of your services. You can find a comprehensive overview of these metrics [here](https://doc.traefik.io/traefik/observability/metrics/overview/#global-metrics). This documentation provides insights into what each metric represents and how you can use them.

If you prefer not to create your own dashboard from scratch, you can use the pre-built Traefik dashboard available in the following GitHub repository:

* [Traefik Dashboard](https://github.com/svenvg93/Grafana-Dashboard/tree/master/traefik)

![captionless image](./tailscale_dashoard.png)

Feel free to customize the dashboard further to meet your specific monitoring needs, and explore other metrics that Traefik provides!

Congratulations! You have successfully set up a monitoring solution for Traefik using Grafana, Prometheus, Promtail, and Loki. Your dashboard will now provide you with valuable insights into your application’s performance and help you quickly identify any issues.

