---
title: "Traefik Reverse Proxy: TCP and UDP Routing"
description: Traefik isn't just for HTTP — it can route raw TCP and UDP traffic too. This guide covers how to expose non-HTTP services like databases, game servers, and DNS through Traefik.
date: 2026-06-15
draft: false
categories:
  - Networking
  - Reverse Proxy
tags:
  - traefik
series:
  - "Traefik Reverse Proxy"
series_order: 4
---

HTTP routing works because Traefik can read the request — the hostname, the path, the headers — and make a decision based on what it sees. Not every service speaks HTTP. For databases, DNS resolvers, game servers, or anything else that uses raw TCP or UDP, Traefik operates at Layer 4: it sees the port and, for TLS connections, the SNI name. That is enough to route most non-HTTP traffic without running a separate proxy.

## Prerequisites

- Traefik running — see the [installation guide][1]
- The file provider enabled for the `conf.d/` examples — see [Enable the File Provider][2]

## How TCP/UDP Routing Differs from HTTP

HTTP routing happens at Layer 7. Traefik reads the full request and can match on host, path, method, or headers. TCP and UDP routing is more limited:

- **TCP with TLS**: Traefik can read the SNI name from the TLS ClientHello before the handshake completes. This allows routing to different backends based on hostname — without decrypting the traffic.
- **TCP without TLS**: No application data to inspect. Every connection on that port goes to the same backend.
- **UDP**: No connections, no handshake, no SNI. One entry point maps to one service.

The config structure mirrors this. HTTP config lives under `http:` and uses `Host()` rules. TCP config lives under `tcp:` and uses `HostSNI()` rules. UDP config lives under `udp:` with no rules at all.

## Configuring Entry Points

TCP and UDP entry points are defined the same way as HTTP ones — in the static config, one per port. `/udp` at the end of the address marks the port as UDP.

**Docker:**

Add each port to both the `command` flags and the `ports` list:

```yaml {filename="docker-compose.yml"}
command:
  - "--entryPoints.postgres.address=:5432"
  - "--entryPoints.dns-udp.address=:53/udp"
  # ... rest of your existing flags

ports:
  - "80:80"
  - "443:443"
  - "5432:5432"
  - "53:53/udp"
```

**Bare metal:**

Add the entry points to the static config alongside your existing HTTP ones:

```yaml {filename="/etc/traefik/traefik.yml"}
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
  postgres:
    address: ":5432"
  dns-udp:
    address: ":53/udp"
```

## TCP Router and SNI Routing

### TLS Passthrough

The most common TCP use case is forwarding TLS traffic without terminating it — the backend handles TLS itself, and Traefik reads only the SNI name to decide where to send it. Set `passthrough: true` so Traefik does not attempt to decrypt the connection.

![TLS passthrough — Traefik reads the SNI from the ClientHello and routes to the matching backend without decrypting](tcp-sni-routing.svg "TLS passthrough — Traefik reads the SNI from the ClientHello and routes to the matching backend without decrypting")

```yaml {filename="conf.d/https-passthrough.yml"}
tcp:
  routers:
    https-passthrough:
      entryPoints: [websecure]
      rule: "HostSNI(`app.example.com`)"
      service: app-backend
      tls:
        passthrough: true

  services:
    app-backend:
      loadBalancer:
        servers:
          - address: "192.168.1.10:443"
```

To match all TLS connections on the entry point without inspecting the hostname, use `HostSNI(`*`)`. This is useful when you have one backend or want to catch all traffic that did not match a more specific rule:

```yaml
rule: "HostSNI(`*`)"
```

> [!WARNING]
> On an entry point shared with HTTP routers, TCP routers are evaluated first. ``HostSNI(`*`)`` with passthrough on `websecure` captures *every* TLS connection on :443 — all your HTTPS services stop working. Only use the wildcard on an entry point dedicated to that backend.

### Plain TCP (No TLS)

For services without TLS — PostgreSQL, MQTT, SMTP — there is no SNI to inspect. Use `HostSNI(`*`)` without a `tls` block. Traefik forwards the raw bytes unchanged:

```yaml {filename="conf.d/postgres.yml"}
tcp:
  routers:
    postgres:
      entryPoints: [postgres]
      rule: "HostSNI(`*`)"
      service: postgres

  services:
    postgres:
      loadBalancer:
        servers:
          - address: "192.168.1.20:5432"
```

Because there is no way to distinguish between plain-TCP connections on the same port, one entry point per service is the cleanest approach — you cannot multiplex two plain-TCP backends on `:5432`.

Traefik is just forwarding raw bytes here — it isn't terminating TLS or doing any authentication on this path, so a plain-TCP entry point gives the backend's own auth the same exposure it would have if the port were opened directly on the firewall. Only expose entry points like this to the internet for services that are safe to expose directly (e.g. already require strong auth); for anything else, keep the entry point bound to your LAN or a VPN instead.

**Docker labels:**

The entry point still needs to be in the static config, but the router can be wired up via labels on the service container:

```yaml {filename="docker-compose.yml"}
labels:
  - "traefik.enable=true"
  - "traefik.tcp.routers.postgres.entrypoints=postgres"
  - "traefik.tcp.routers.postgres.rule=HostSNI(`*`)"
  - "traefik.tcp.services.postgres.loadbalancer.server.port=5432"
```

## UDP Routing

UDP has no connection state and no SNI. Traefik maps an entry point directly to a service — there are no routing rules to write:

```yaml {filename="conf.d/dns.yml"}
udp:
  routers:
    dns:
      entryPoints: [dns-udp]
      service: dns

  services:
    dns:
      loadBalancer:
        servers:
          - address: "192.168.1.1:53"
```

**Docker labels:**

```yaml {filename="docker-compose.yml"}
labels:
  - "traefik.enable=true"
  - "traefik.udp.routers.dns.entrypoints=dns-udp"
  - "traefik.udp.services.dns.loadbalancer.server.port=53"
```

UDP labels use `traefik.udp.` instead of `traefik.tcp.` or `traefik.http.`. There is no `rule` key — UDP routing does not support rules.

## Putting It Together

The example below combines all three in one config: TLS passthrough on `:443`, a PostgreSQL backend on `:5432`, and DNS forwarding on `:53/udp`.

Static config:

```yaml {filename="/etc/traefik/traefik.yml"}
entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"
  postgres:
    address: ":5432"
  dns-udp:
    address: ":53/udp"
```

Dynamic config:

```yaml {filename="conf.d/layer4.yml"}
tcp:
  routers:
    tls-passthrough:
      entryPoints: [websecure]
      rule: "HostSNI(`app.example.com`)"
      service: backend-https
      tls:
        passthrough: true

    db:
      entryPoints: [postgres]
      rule: "HostSNI(`*`)"
      service: backend-db

  services:
    backend-https:
      loadBalancer:
        servers:
          - address: "192.168.1.10:443"
    backend-db:
      loadBalancer:
        servers:
          - address: "192.168.1.20:5432"

udp:
  routers:
    dns:
      entryPoints: [dns-udp]
      service: backend-dns

  services:
    backend-dns:
      loadBalancer:
        servers:
          - address: "192.168.1.1:53"
```

A TLS connection to `:443` for `app.example.com` is matched by SNI and forwarded encrypted to `192.168.1.10:443`; every other hostname on `:443` still reaches your HTTP routers as before. A connection to `:5432` goes straight to the PostgreSQL server on `192.168.1.20`. A UDP packet to `:53` is forwarded to the DNS resolver on `192.168.1.1`.

## Troubleshooting

**Traefik won't start: `bind: address already in use` on port 53.** On Ubuntu and other systemd distributions, `systemd-resolved` already listens on port 53. Check with `sudo ss -lunp 'sport = :53'`. Either publish the port on the host's LAN address only (`"192.168.1.5:53:53/udp"` in `ports`, or `address: "192.168.1.5:53/udp"` on bare metal) or disable the resolved stub listener (`DNSStubListener=no` in `/etc/systemd/resolved.conf`, then `sudo systemctl restart systemd-resolved`).

**All HTTPS sites broke after adding a TCP router.** A TCP router with ``HostSNI(`*`)`` on `websecure` is catching every connection — see the warning under [TLS Passthrough](#tls-passthrough).

**A passthrough route doesn't match.** SNI routing only works when the client sends a hostname. Connecting by IP address (`https://192.168.1.5`) sends no SNI, so only a ``HostSNI(`*`)`` router can catch it. Test with the hostname: `openssl s_client -connect <traefik-ip>:443 -servername app.example.com`.

**A plain-TCP or UDP service gets no traffic.** The entry point must be in both the `command` flags and the `ports` list — a missing port mapping means packets never reach the container. Check with `docker port traefik`.

That covers HTTP, TCP, and UDP — between this and the rest of the series, Traefik is now handling routing, security, and observability for everything running behind it.

[1]: {{< ref "/posts/2024-05-21-traefik-reverse-proxy-install" >}}
[2]: {{< ref "/posts/2024-05-22-traefik-reverse-proxy-middlewares-dashboard#enable-the-file-provider" >}}
