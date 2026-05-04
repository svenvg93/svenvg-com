---
title: Setting Up Native IPv6 on Unifi
description: Enable native IPv6 on your Unifi network with prefix delegation, proper firewall rules, and working SLAAC for all your devices.
date: 2026-06-15
draft: true
categories:
  - Networking
tags:
  - unifi
  - ipv6
cover: cover.svg
---

Getting IPv6 working properly on Unifi involves more than just flipping a switch — you need to configure prefix delegation from your ISP, set up SLAAC or DHCPv6 for client addressing, and make sure your firewall rules don't inadvertently block all IPv6 traffic. In this post, we'll walk through a complete Unifi IPv6 setup from ISP handoff to verified end-to-end connectivity on all your devices.
