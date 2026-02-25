---
title: Access Unifi Controller Through Traefik
description: Proxy Unifi Controller through Traefik using file-based configuration
date: 2025-12-14
draft: false
categories:
  - Networking
tags:
  - unifi
  - traefik
cover: cover.jpg
series:
  - Unifi Homelab
---

While Traefik excels at auto-discovering Docker containers through labels, some services like the Unifi Controller require a different approach. The Unifi Controller uses self-signed certificates and runs on HTTPS, making it a perfect candidate for Traefik's file-based configuration with `insecureSkipVerify`.

## Prerequisites

- Traefik installed and configured (see my [Traefik Essentials Setup]({{< ref "/posts/2024-05-21-traefik-essentials-setup" >}}) post)
- Unifi Controller running and accessible on your network

## Traefik Configuration

### Enable File Provider

First, ensure Traefik can read dynamic configuration files. Add the following to your Traefik container in `docker-compose.yml`:

**Command arguments:**
```yaml
command:
  - "--providers.file.directory=/etc/traefik/dynamic"
  - "--providers.file.watch=true"
  # ... your other Traefik arguments
```

**Volume mounts:**
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
  - traefik:/certs
  - ./config:/etc/traefik/dynamic:ro
```

The `--providers.file.directory` tells Traefik where to find dynamic configuration files, and `--providers.file.watch=true` enables automatic reloading when files change. The `./config` directory will hold our dynamic configuration files.

### Create Dynamic Configuration File

Create a new file at `./config/unifi.yml` with the following configuration:

```yaml
http:
  routers:
    unifi:
      rule: "Host(`unifi.lab.example.com`)"
      service: unifi-service
      entryPoints:
        - websecure
      tls:
        certResolver: le

  services:
    unifi-service:
      loadBalancer:
        servers:
          - url: "https://192.168.1.1"
        serversTransport: unifi-transport

  serversTransports:
    unifi-transport:
      insecureSkipVerify: true
```

### Configuration Breakdown

**Router Configuration:**
- `rule`: The domain that will route to your Unifi Controller (adjust to match your setup)
- `service`: References the service definition below
- `entryPoints`: Uses the secure HTTPS entry point
- `tls.certResolver`: Uses Let's Encrypt for valid SSL certificates

**Service Configuration:**
- `url`: The IP address and protocol of your Unifi Controller
- `serversTransport`: References the custom transport configuration

**Servers Transport:**
- `insecureSkipVerify: true`: Required because Unifi uses self-signed certificates internally

## How It Works

When you navigate to `unifi.lab.example.com`:

1. **DNS Resolution**: Your DNS resolves the domain to your Traefik server
2. **SSL Termination**: Traefik presents a valid SSL certificate to your browser
3. **Backend Connection**: Traefik connects to the Unifi Controller's HTTPS interface at `192.168.1.1`
4. **Certificate Bypass**: The `insecureSkipVerify` setting allows Traefik to accept Unifi's self-signed certificate
5. **Secure Access**: You access your Unifi Controller with a valid SSL certificate, no browser warnings

This file-based approach gives you full control over services that can't use Docker labels, while still benefiting from Traefik's reverse proxy capabilities and automatic SSL certificate management.
