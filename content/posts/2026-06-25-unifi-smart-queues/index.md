---
title: Fix Bufferbloat with Unifi Smart Queues
description: Eliminate bufferbloat and prioritize latency-sensitive traffic on your Unifi network with Smart Queues and traffic shaping.
date: 2026-06-25
draft: true
categories:
  - Networking
tags:
  - unifi
  - qos
cover: cover.svg
---

Bufferbloat is one of the most common causes of sluggish-feeling internet connections, especially during high-bandwidth activities like file uploads or video calls. Unifi's Smart Queues feature uses FQ-CoDel to actively manage your upload and download queues, keeping latency low even under load. In this post, we'll cover how to enable and tune Smart Queues, how to measure bufferbloat before and after, and when traffic shaping rules can complement it.
