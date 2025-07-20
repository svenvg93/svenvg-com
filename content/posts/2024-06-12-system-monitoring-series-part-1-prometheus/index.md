---
title: System Monitoring Series Part 1 | Host & Container Monitoring with Prometheus
description: In Part 1 of the System Monitoring series, learn how to set up performance monitoring for your systems and containers using Prometheus and Grafana.
date: 2024-06-12
draft: false
categories:
  - Monitoring
  - Metrics
tags:
  - docker
  - prometheus
  - grafana
cover: cover.jpg
---

Monitoring your systems and containers is essential for maintaining a reliable homelab or home server. A popular setup involves Prometheus, Node Exporter, and cAdvisor for collecting metrics, combined with Grafana for creating insightful dashboards.

In this guide, we’ll set up a complete monitoring solution by:
1.	Configuring Prometheus to scrape metrics from Node Exporter and cAdvisor.
2.	Using Grafana to visualize the data with intuitive dashboards.

Let’s dive in and build a robust monitoring stack!

##  Setup Node Exporter & Cadvisor

To organize and store configuration files for monitoring, create dedicated folders for Node Exporter and cAdvisor.

Run the following commands to create the required directories:

```bash
mkdir nodeexporter
mkdir cadvisor
```

Next, we’ll set up a docker-compose.yml` file in each folder to configure the respective services.


### Node Exporter

Open a new <kbd>docker-compose.yml</kbd> file for editing:

```bash
nano nodeexporter/docker-compose.yml
```
Paste the following content into the file:
```yaml {filename="docker-compose.yml"}
services:
  nodeexporter:
    image: prom/node-exporter
    container_name: nodeexporter
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped
    network_mode: host
```

The <kbd>network_mode: host</kbd> setting allows Node Exporter to access the host network interfaces, enabling it to collect networking metrics.

### cAdvisor

Open a new <kbd>docker-compose.yml</kbd> file for editing:

```bash
nano cadvisor/docker-compose.yml
```
Paste the following content into the file:
```yaml {filename="docker-compose.yml"}
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor
    container_name: cadvisor
    privileged: true
    devices:
      - /dev/kmsg:/dev/kmsg
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker:/var/lib/docker:ro
      - /cgroup:/cgroup:ro
    command: 
      - '--housekeeping_interval=15s'
      - '--docker_only=true'
    restart: unless-stopped
    networks:
      - backend
networks:
  backend:
    name: backend
```

Now that we have the configurations in place, we can start Node Exporter and cAdvisor by running the following commands:

```bash
docker compose -f nodeexporter/docker-compose.yml up -d
docker compose -f cadvisor/docker-compose.yml up -d
```

## Setup Prometheus

To collect the metrics from Node Exporter and cAdvisor, we’ll create a dedicated directory for Prometheus to store its configuration and Docker Compose files.

First, create the Prometheus folder:
```bash
mkdir prometheus
```

Next, create a <kbd>docker-compose.yml</kbd> file for Prometheus:

```bash
nano prometheus/docker-compose.yml
```
Add the following configuration to the file:
```yaml {filename="docker-compose.yml"}
services:
  prometheus:
    image: prom/prometheus
    container_name: prometheus
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.size=100GB'
      - '--web.enable-lifecycle'
    restart: unless-stopped
    expose:
      - 9090
    networks:
      - backend
    extra_hosts:       
      - "host.docker.internal:host-gateway"
networks:
  backend:
    name: backend
volumes:
    prometheus:
      name: prometheus
```

Prometheus requires a configuration file to define which services to scrape for metrics. Create the configuration file:

```bash
nano prometheus/prometheus.yml
```
Add the following configuration to the file:
```yaml {filename="prometheus.yml"}
global:
  scrape_interval:     15s
  evaluation_interval: 15s
scrape_configs:
  - job_name: 'cadvisor'
    scrape_interval: 10s
    static_configs:
      - targets: ['cadvisor:8080']
  - job_name: 'prometheus'
    scrape_interval: 10s
    static_configs:
      - targets: ['localhost:9090']
  - job_name: 'nodeexporter'
    scrape_interval: 10s
    static_configs:
      - targets: ['hostip:9100']
    metric_relabel_configs:
      - source_labels: [nodename]
        target_label: "instance"
        action: "replace"
```

Since Node Exporter is using the host network, you need to replace <kbd>hostip</kbd> with your actual host IP address. The <kbd>metric_relabel_configs</kbd> will help in relabeling the <kbd>hostip:9100</kbd> to the actual hostname, making it easier to identify.

Now that you have configured Prometheus, you can start it with the following command:

```bash
docker compose -f prometheus/docker-compose.yml up -d
```

This command starts the Prometheus container, which will begin collecting metrics from both Node Exporter and cAdvisor, providing comprehensive monitoring for your systems and containers.

## Setup Grafana

To finalize your monitoring setup, we’ll create a directory for Grafana to store its Docker Compose and configuration files.

First, create the Grafana folder:
```bash
mkdir grafana
```

Next, create a <kbd>docker-compose.yml</kbd> file for Grafana:

```bash
nano grafana/docker-compose.yml
```
Add the following configuration to the file:
```yaml {filename="docker-compose.yml"}
services:
  grafana:
    image: grafana/grafana
    container_name: grafana
    environment:
      - TZ=Europe/Amsterdam
    volumes:
      - grafana_data:/var/lib/grafana
    restart: unless-stopped
    ports:
      - 3000:3000
    networks:
      - backend
networks:
  backend:
    name: backend
volumes:
    grafana_data:
      name: grafana_data
```

Now you can start Grafana by running:

```bash
docker compose -f grafana/docker-compose.yml up -d
```

Once Grafana is running, open your browser and navigate to:
http://<HOST_IP>:3000

- Default login credentials:
  - Username: **admin**
  - Password: **admin**

### Datasource

To visualize the data collected by Prometheus, you need to add it as a data source in Grafana:

1.  Click **Connections** in the left-side menu.
2.  Search for **Prometheus**
3.  Click **Add new Datasource**
4.  Enter the name **prometheus**
5.  Fill in the Prometheus server URL <kbd>http://prometheus:9090</kbd>

Dashboards

To see all the metrics we need to dashboards. You can make your own dashboards or use mine as a starter:

*   [NodeExporter](https://github.com/svenvg93/Grafana-Dashboard/tree/master/node_expoter)
*   [cAdvisor](https://github.com/svenvg93/Grafana-Dashboard/tree/master/cadvisor)

## Conclusion

Congratulations! You have successfully set up host and container monitoring with Prometheus and Grafana. Your monitoring system is now capable of visualizing the metrics from your applications and self-hosting.
