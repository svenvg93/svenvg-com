---
title: Trusted HTTPS on Unifi with Let's Encrypt
description: Replace the Unifi self-signed certificate with a trusted Let's Encrypt TLS certificate for a browser-warning-free admin UI.
date: 2026-07-02
draft: true
categories:
  - Networking
  - Security
tags:
  - unifi
  - letsencrypt
  - ssl
cover: cover.svg
---

By default, the Unifi Network application uses a self-signed certificate that triggers browser warnings every time you open the admin UI. Replacing it with a Let's Encrypt certificate gives you a trusted HTTPS connection and enables clean access from external tools and scripts. In this post, we'll cover how to generate a certificate using the DNS challenge, import it into Unifi, and set up automatic renewal so it never expires.
