---
title: "Smokeping Essentials: Setup"
description: A step-by-step guide to deploying Smokeping with Docker to monitor your internet connection latency and packet loss over time.
date: 2026-04-30
draft: false
categories:
  - Monitoring
  - Networking
tags:
  - docker
cover: cover.svg
series:
  - Smokeping Essentials
series_order: 3
---

With a solid understanding of [which protocols to use and how to find good targets]({{< ref "/posts/2026-04-09-smokeping-essentials-targets" >}}) — including [CDN edge nodes and local ISP-hosted caches]({{< ref "/posts/2026-04-16-smokeping-essentials-cdn-targets" >}}) — it's time to put it all together with Smokeping. Smokeping tracks latency and packet loss over time and presents them visually, making it easy to spot patterns like evening congestion or flapping links.

## What is Smokeping?

Smokeping probes your targets every few minutes and stores the results in a round-robin database. Instead of a one-off ping, you get a graph showing latency and packet loss over hours, days, and weeks. A spike at 21:00 every evening is hard to miss — and impossible to catch with a single ping.

## Prerequisites

- Docker and Docker Compose installed
- A list of monitoring targets (see the previous posts in this series)

## Docker Compose Setup

```yaml {filename="docker-compose.yml"}
services:
  smokeping:
    image: lscr.io/linuxserver/smokeping:latest
    container_name: smokeping
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Europe/Amsterdam  # change to your timezone
    volumes:
      - ./config:/config
      - ./data:/data
    ports:
      - 8080:80
    restart: unless-stopped
```

Start it with `docker compose up -d`. On first run the image generates default config files under `./config/`. Stop the container before editing them:

```bash
docker compose down
```

## Configuration

Smokeping's configuration lives in files under `./config/`. The two you need to edit are `Probes` and `Targets`.

### Probes

Probes define how Smokeping measures each target. Add the probes you need to `./config/Probes`:

``` {filename="Probes"}
*** Probes ***

+FPing
binary = /usr/sbin/fping

+FPing6
binary = /usr/sbin/fping6

+DNS
binary = /usr/bin/dig
lookup = google.com
pings = 5
step = 300

+TCPPing
binary = /usr/bin/tcpping
port = 443
```

| Probe | Protocol | Use for |
|-------|----------|---------|
| FPing | ICMP (IPv4) | ISP gateway, local CDN caches |
| FPing6 | ICMP (IPv6) | IPv6 equivalents of the above |
| DNS | DNS | ISP and public resolvers |
| TCPPing | TCP | CDN edge nodes (port 80/443) |

### Targets

Targets define what to probe and how to organise the results in the web UI. The file below is an example — replace the IPs with the ones you found in the previous posts. IPv6 targets use the `FPing6` probe; add them only if your ISP provides IPv6 connectivity.

``` {filename="Targets"}
*** Targets ***

probe = FPing

menu = Top
title = Internet Monitoring

+ ISP
menu = ISP
title = ISP Infrastructure

++ Gateway
menu = Gateway
title = ISP Gateway
host = 192.0.2.1        # your ISP gateway IP (IPv4)

++ Gateway_v6
menu = Gateway IPv6
title = ISP Gateway IPv6
probe = FPing6
host = 2001:db8::1      # your ISP gateway IP (IPv6)

++ DNS_ISP
menu = ISP DNS
title = ISP Resolver
probe = DNS
host = 192.0.2.53       # your ISP's DNS resolver

++ DNS_Public
menu = Quad9
title = Quad9
probe = DNS
host = 9.9.9.9

+ CDN
menu = CDN
title = CDN Edge Nodes
probe = TCPPing

++ Cloudflare
menu = Cloudflare
title = Cloudflare
host = speed.cloudflare.com

+ Local_CDN
menu = Local CDN
title = ISP-Hosted Caches
probe = FPing

++ Netflix_OCA
menu = Netflix OCA
title = Netflix OCA
host = 192.0.2.100      # your local OCA IP
```

Start Smokeping again after saving:

```bash
docker compose up -d
```

## Accessing the Web UI

Open `http://localhost:8080/smokeping/` in your browser. It takes a few minutes to collect enough data before graphs appear.

If you're running this on a separate machine on your network, replace `localhost` with its IP address.

## Alerts

Smokeping can send an alert when packet loss or latency crosses a threshold. Add this to `./config/Alerts`:

``` {filename="Alerts"}
*** Alerts ***

to = your@email.com
from = smokeping@yourdomain.com

+lossAlert
type = loss
pattern = >0%,>0%,>0%,>0%,>0%
comment = packet loss detected for 5 consecutive probes

+highLatency
type = rtt
pattern = >100,>100,>100
comment = latency above 100ms for 3 consecutive probes
```

Each value in `pattern` represents one probe cycle. `>0%,>0%,>0%,>0%,>0%` means "more than 0% loss in five consecutive cycles" — Smokeping only fires the alert when the pattern matches in sequence, avoiding false positives from a single dropped probe.

Then reference the alert in any target by adding `alerts = lossAlert,highLatency` under the target definition.

## What to Look For

Once you have a few hours of data, the graphs tell a clear story:

- **Flat line, low RTT** — healthy connection
- **Regular evening spikes** — congestion on your ISP's network at peak hours
- **Packet loss on ISP gateway but not CDN** — problem between your home and your ISP
- **Packet loss on CDN but not ISP gateway** — problem further upstream, beyond your ISP
- **All targets degraded simultaneously** — your home network or router is the bottleneck
- **Only one CDN degraded** — that CDN's peering with your ISP is having issues

The value is in the layers: ISP gateway, CDN edge, and local OCA each sit at a different point in the network. When something goes wrong, the combination of which targets degrade tells you exactly where the problem is.
