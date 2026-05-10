---
title: "Policy-Based Routing on UniFi"
description: Steer specific traffic through a chosen WAN uplink or VPN tunnel on UniFi using policy-based routing rules.
date: 2026-06-20
draft: true
categories:
  - Networking
tags:
  - unifi
  - policy-based routing
  - firewall
cover: cover.svg
---

By default, your UniFi gateway sends all traffic out through whichever WAN is set as the primary uplink. Policy-based routing (PBR) overrides that decision on a per-flow basis — you define a rule that matches specific sources or destinations, and the gateway steers that traffic out through a different interface instead. That interface can be a secondary WAN, a WireGuard tunnel, or a VPN provider.

In this post, we'll walk through the most common homelab use case: routing traffic from a specific device over a WireGuard VPN.

> **Note:** This post is based on UniFi Network Application version 10.3.58.

## Prerequisites

- UniFi Network Application running and accessible
- A VPN provider with a WireGuard configuration file (e.g., Mullvad, ProtonVPN)

## Add a VPN Client

Before creating a policy route, add the VPN tunnel as a client connection so the gateway knows how to reach it.

- Go to **Settings → VPN**
- Click **Create New**
- Enter a name for the VPN connection
- Upload the WireGuard configuration file from your VPN provider
- Leave **Device Wizard** and **Content Wizard** off — you'll create the policies manually

## Create a Policy Route

With the VPN tunnel in place, create a policy that tells the gateway to send specific traffic through it.

- Go to **Settings → Policy Engine → Policy Table**
- Click **Create New Policy**
- Select **Route** and enter a name
- Set **Type** to **Policy based**
- Set **Destination Interface** to the VPN connection you just created
- Set **Source** to **Device/Network**
- Select the device or network whose traffic should route through the VPN

## Verification

Run the following command from the device covered by the policy to confirm its external IP has changed.

**Before the policy route:**

```bash
sven@un100p:~$ curl -s https://ifconfig.co/json | jq '{ip, country, asn_org}'
{
  "ip": "92.254.xxx.xxx",
  "country": "The Netherlands",
  "asn_org": "Odido Netherlands B.V."
}
```

**After the policy route:**

```bash
sven@un100p:~$ curl -s https://ifconfig.co/json | jq '{ip, country, asn_org}'
{
  "ip": "193.32.xxx.xxx",
  "country": "France",
  "asn_org": "31173 Services AB"
}
```

The IP address, country, and ASN have all changed — traffic from this device is now leaving through the VPN tunnel rather than the default WAN.
