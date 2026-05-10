---
title: "Unifi Multi-WAN: Load Balancing and Automatic Failover"
description: Configure two WAN connections on Unifi for automatic failover and load balancing so your network stays online when one ISP goes down.
date: 2026-06-30
draft: true
categories:
  - Networking
tags:
  - unifi
  - multi-wan
  - failover
cover: cover.svg
---

With two WAN connections — a primary fibre link and a backup LTE or cable line — Unifi can automatically switch traffic to the healthy uplink the moment it detects an outage, keeping your network online with no manual intervention. In this post, we'll cover configuring both WAN interfaces, setting up health checks, choosing between failover and load-balancing modes, and using policy-based routing to pin specific devices or services to a preferred uplink.
