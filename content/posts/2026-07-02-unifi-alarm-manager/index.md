---
title: "Unifi Alarm Manager: Network Alerts That Actually Matter"
description: Configure Unifi's Alarm Manager to surface real network issues — and silence the noise — with push notifications, email, and webhook alerts.
date: 2026-07-02
draft: true
categories:
  - Networking
  - Security
tags:
  - unifi
  - alerts
  - monitoring
cover: cover.svg
---

Out of the box, Unifi generates an alert for almost everything — a device reconnects, a client roams between APs, an IP conflict resolves itself. By the time anything serious happens, the real alert is buried under dozens of noise events. The Alarm Manager lets you define exactly which events are worth waking up for, where those alerts go, and how to route critical security events to an external system like Discord or a webhook.

## Where to Find It

Open **UniFi Network → Settings → Notifications**. This is where you configure both which events generate alarms and how those alarms are delivered.

Alarms themselves live under the bell icon in the top navigation bar. The **Alarm Manager** view shows all active and resolved alarms with timestamps, severity, and context.

## Alarm Categories

| Category | Examples |
|----------|---------|
| **Security** | IPS/IDS threat detected, port scan, blocked country |
| **Connectivity** | WAN failover, uplink down, VPN tunnel dropped |
| **Device** | AP offline, switch port flapping, gateway reboot |
| **Client** | Unauthorized client, IP conflict, rogue DHCP |

Security and Connectivity alarms are almost always worth keeping on. Device alarms are useful in production but noisy in a homelab where you regularly reboot things. Client alarms depend heavily on how stable your network is.

## Configuring Notification Channels

Unifi supports three delivery methods:

**Push notifications** via the UniFi app — enabled by default once you're signed into a UI account. Zero config required, works immediately.

**Email** — go to **Settings → Notifications → Email** and enter an SMTP server or use Ubiquiti's hosted email relay. Useful for low-urgency events you want a paper trail for.

**Webhook** — the most flexible option. Unifi POSTs a JSON payload to any URL you provide, making it straightforward to pipe alerts into Discord, Slack, ntfy, or any home automation system.

## Setting Up a Webhook

Go to **Settings → Notifications → Webhooks** and add a new endpoint:

```
URL:    https://your-webhook-receiver/unifi
Secret: (optional HMAC signing key)
```

Unifi sends a POST with a JSON body like this:

```json
{
  "type": "IPS_ALERT",
  "severity": "HIGH",
  "message": "Exploit attempt blocked from 185.220.101.42",
  "site": "default",
  "timestamp": 1751234567
}
```

For Discord, use a Discord webhook URL directly — Unifi's payload isn't the Discord embed format, so you'll need a small relay (an ntfy bridge or a simple serverless function) to transform it. For **ntfy**, Unifi webhooks work natively if you point the URL at your ntfy topic.

## Tuning Out the Noise

The default alert profile is too broad for most homelabs. A practical starting point:

**Keep on:**
- IPS/IDS detections
- WAN failover / uplink down
- VPN tunnel state changes
- Rogue DHCP server detected

**Turn off or reduce to email-only:**
- AP offline (if you intentionally power cycle APs)
- Client roaming events
- IP conflict resolved (self-healing, not actionable)
- Firmware update available (check on your own schedule)

Go to **Settings → Notifications → Alert Types** and toggle each category individually. You can set some to push, some to email-only, and disable others entirely.

## Pairing with IPS/IDS

If you've enabled IPS (covered in the [IPS/IDS post](/posts/network-intrusion-prevention-with-unifi-ips/)), security alarms in the Alarm Manager become your real-time feed of blocked threats. Each IPS event creates an alarm entry with:

- Source IP and geolocation
- Matched signature name and CVE (where applicable)
- Action taken (blocked vs. detected)

Set IPS alarms to push notification so you see them immediately, and to webhook if you want them logged in an external system alongside your other homelab observability data.

## Recap

You've learned how to:

- Navigate the Alarm Manager and understand alarm categories
- Configure push, email, and webhook notification channels
- Tune which alerts fire to reduce noise
- Route IPS/IDS security events to external systems
