---
title: Troubleshoot WiFi with Unifi Wireless Packet Capture
description: Use the built-in Unifi wireless packet capture to troubleshoot Wi-Fi issues and analyze traffic without extra hardware.
date: 2026-07-13
draft: true
categories:
  - Networking
tags:
  - unifi
  - wifi
  - packet-capture
cover: cover.svg
---

When Wi-Fi problems are hard to reproduce or diagnose, a packet capture at the access point level is often the fastest path to the root cause. Unifi has a built-in wireless packet capture that lets you record raw 802.11 frames directly from your APs and analyze them in Wireshark — no extra hardware or network taps required. In this post, we'll walk through how to start a capture, what to look for, and common issues you can diagnose with it.
