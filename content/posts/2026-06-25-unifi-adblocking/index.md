---
title: Network-Wide Adblocking on Unifi
description: Block ads and trackers network-wide on Unifi using DNS-based traffic policies without running a separate Pi-hole or AdGuard instance.
date: 2026-06-25
draft: true
categories:
  - Networking
  - Security
tags:
  - unifi
  - adblock
  - dns
cover: cover.svg
---

Unifi's traffic and DNS policies let you block ads and trackers at the network level for every device on your LAN — no per-device setup, no separate Pi-hole required. In this post, we'll walk through how to configure DNS filtering policies in the Unifi Network application, which blocklists to use, and how to apply them selectively per VLAN or device group.
