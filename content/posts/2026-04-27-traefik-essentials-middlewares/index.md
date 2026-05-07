---
title: "Traefik Essentials: Middlewares"
description: Protect your homelab services with IPAllowList, BasicAuth, and security headers — without touching the app.
date: 2026-04-27
draft: false
categories:
  - Networking
  - Reverse Proxy
tags:
  - traefik
cover: cover.svg
series:
  - Traefik Essentials
series_order: 4
---

When a request reaches Traefik, it is matched against a router. Before that request is forwarded to your service, middlewares have a chance to inspect or modify it. A middleware can reject the request outright (wrong IP, missing credentials), rewrite headers, or add security headers to the response on the way back.

Middlewares are reusable — you define one and attach it to as many routers as you want. You never change the app itself.

## Prerequisites

- Traefik running from the [Docker setup][1] or [bare metal install][2]

## How Middlewares Work

Each middleware has two parts: a **definition** (what it does and how it is configured) and an **attachment** (which routers it applies to).

In Docker, both happen in labels on the service container. For bare metal, or when you want to share a middleware across many services, you define them once in a `conf.d/` file and reference them by name from any router.

Throughout this guide we use `lan-only`, `my-auth`, and `secure-headers` as the middleware names. You can name them anything — the name is just how Traefik identifies them internally.

## IPAllowList

IPAllowList lets requests through only if the source IP matches an allowed range. Everything else gets a 403 immediately, before the request reaches your service.

This is useful for services that should only be reachable from your home network — Grafana, Home Assistant, internal dashboards.

```yaml {filename="docker-compose.yml"}
labels:
  - "traefik.http.middlewares.lan-only.ipallowlist.sourcerange=192.168.0.0/16,127.0.0.1/32"
  - "traefik.http.routers.myapp.middlewares=lan-only"
```

For bare metal, or to reuse the middleware across multiple services, define it once in a shared file:

```yaml {filename="conf.d/middlewares.yml"}
http:
  middlewares:
    lan-only:
      ipAllowList:
        sourceRange:
          - "192.168.0.0/16"
          - "127.0.0.1/32"
```

Then reference it by name from any router config:

```yaml {filename="conf.d/myapp.yml"}
http:
  routers:
    myapp:
      rule: "Host(`myapp.example.com`)"
      entryPoints: [websecure]
      middlewares: [lan-only]
      service: myapp
      tls:
        certResolver: letsencrypt
```

## BasicAuth

BasicAuth adds a username/password prompt in the browser before the request reaches your service. The browser sends the credentials as a base64-encoded header on every request — Traefik checks the hash and either forwards or rejects.

This is a good fit for services that have no built-in login page, like Prometheus or a simple status page.

First, generate a hashed password with `htpasswd`:

```bash
sudo apt install apache2-utils
htpasswd -nb admin your-password
# admin:$apr1$xyz...
```

Copy the full output — you need the hash, not the plain password.

In Docker labels, every `$` in the hash must be escaped as `$$` because Docker interprets single `$` as a variable:

```yaml {filename="docker-compose.yml"}
labels:
  - "traefik.http.middlewares.my-auth.basicauth.users=admin:$$apr1$$xyz..."
  - "traefik.http.routers.myapp.middlewares=my-auth"
```

In dynamic config no escaping is needed — paste the hash directly:

```yaml {filename="conf.d/middlewares.yml"}
http:
  middlewares:
    my-auth:
      basicAuth:
        users:
          - "admin:$apr1$xyz..."
```

## Security Headers

Browsers trust a lot of content by default. Security headers are instructions you send back in the HTTP response that tell the browser to be stricter — don't load this page in an iframe, don't sniff the content type, only connect over HTTPS.

These headers protect your users even if someone finds a URL to one of your services.

Because there are many options and the values are long, defining them as Docker labels is impractical. Use a dynamic config file:

```yaml {filename="conf.d/middlewares.yml"}
http:
  middlewares:
    secure-headers:
      headers:
        stsSeconds: 31536000          # tell browsers to use HTTPS for 1 year
        stsIncludeSubdomains: true
        forceSTSHeader: true          # send HSTS even on plain HTTP responses
        contentTypeNosniff: true      # stop browsers guessing content types
        frameDeny: true               # block the page from loading in an iframe
        browserXssFilter: true        # enable browser XSS protection
        referrerPolicy: "strict-origin-when-cross-origin"
```

## Chaining

You can attach multiple middlewares to a single router. Traefik runs them in the order listed — if one rejects the request, the rest are skipped.

A sensible order for homelab use: filter by IP first (cheapest check), then require auth, then add headers on the way out.

In Docker labels, list them comma-separated:

```yaml {filename="docker-compose.yml"}
labels:
  - "traefik.http.routers.myapp.middlewares=lan-only,my-auth,secure-headers"
```

In dynamic config:

```yaml
http:
  routers:
    myapp:
      middlewares:
        - lan-only
        - my-auth
        - secure-headers
```

A request from outside your LAN is blocked by `lan-only` and never reaches `my-auth`. A request from inside with wrong credentials is blocked by `my-auth` and never reaches the service. Only a request that passes all checks gets through — and it arrives at your service with the security headers already attached to the response.

## Further Reading

The three middlewares above cover the most common homelab needs, but Traefik has many more — rate limiting, redirects, compression, and request rewriting among them. The full list is in the [Traefik middleware documentation][3].

[1]: {{< ref "/posts/2024-05-21-traefik-essentials-setup" >}}
[2]: {{< ref "/posts/2026-03-23-traefik-essentials-bare-metal" >}}
[3]: https://doc.traefik.io/traefik/middlewares/http/overview/
