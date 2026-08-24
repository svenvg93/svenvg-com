---
title: Setting Up a UniFi Gateway
description: Configure a UniFi gateway from scratch for your homelab — adoption, WAN, LAN, DHCP, and firewall basics on UniFi OS.
date: 2026-08-20
draft: true
categories:
  - Networking
  - Router
tags:
  - unifi
---

UniFi gateways trade the command-line configuration of MikroTik and VyOS for a GUI-driven workflow — there's no CLI equivalent for configuration, everything happens in the UniFi Network application. This guide walks through adopting a fresh UniFi gateway (a UCG-Fiber here) and configuring it with the same LAN, WAN, DHCP, and firewall baseline covered in the [MikroTik]({{< ref "/posts/2025-01-05-setup-mikrotik-router" >}}) and [VyOS]({{< ref "/posts/2025-03-25-setup-vyos-router" >}}) posts.

This post covers a single flat LAN — no VLANs. If you want network segmentation, that's a good follow-up once this baseline is working.

## Prerequisites

- A UniFi gateway (UCG-Fiber, UDM, UDM-Pro, UDM-SE, or Cloud Gateway family)
- A UniFi account (Ubiquiti SSO) or the option to set up local-only access during adoption
- The UniFi Network mobile app, or a browser on the same network as the gateway

## Adoption

1. Connect the gateway's WAN port to your internet connection and a LAN port to your computer (or join the gateway's temporary setup Wi-Fi network if offered).
2. Open the UniFi Network mobile app, or browse to the gateway's local address, and follow the device's own setup wizard — this runs before you ever reach the full Network application.
3. When prompted, configure the **internet connection** — this is where the WAN connection type is set; see below.
4. Sign in with your Ubiquiti account, or choose the local-access-only option if you'd rather not tie management to the cloud.
5. Let the wizard apply any pending UniFi OS and Network application updates before continuing — firmware version affects which menus below are available.
6. Name the site so it's identifiable if you manage more than one.

<!-- TODO(Sven): confirm exact wizard steps/screenshots for your firmware version, and whether you used local-only or cloud SSO -->

## WAN

The setup wizard asks for the WAN connection type as one of its first steps, before handing off to the Network application. UniFi exposes the connection type as a dropdown rather than separate commands:

{{< tabs >}}
{{< tab label="DHCP with VLAN" >}}
1. Set **IPv4 Connection** to **DHCP**.
2. Enable **VLAN ID** and enter the VLAN tag your ISP requires.
{{< /tab >}}
{{< tab label="DHCP" >}}
1. Set **IPv4 Connection** to **DHCP**.
2. Leave **VLAN ID** disabled.
{{< /tab >}}
{{< tab label="PPPoE" >}}
1. Set **IPv4 Connection** to **PPPoE**.
2. Enter the username and password provided by your ISP.
{{< /tab >}}
{{< tab label="Static IP" >}}
1. Set **IPv4 Connection** to **Static**.
2. Enter the IP address, subnet mask, gateway, and DNS servers provided by your ISP.
{{< /tab >}}
{{< /tabs >}}

If you need to revisit this later, the same settings live under **Settings → Internet** in the Network application.

<!-- TODO(Sven): confirm the exact VLAN ID field placement/label on current firmware, and your VLAN tag if you want it shown as an example -->

## LAN

UniFi gateways ship with a **Default** network already created. Open **Settings → Networks → Default** to adjust it:

- **Gateway IP/Subnet** — the router's address and LAN subnet, e.g. `192.168.1.1/24`
- **DHCP Mode** — DHCP Server, with a range for client leases
- **DHCP Name Server** — leave as Auto to hand out the gateway's own IP, or set custom resolvers

<!-- TODO(Sven): confirm your actual LAN subnet/DHCP range, or if you're fine with the 192.168.1.0/24 placeholder used in the MikroTik/VyOS posts for consistency -->

## Firewall

Unlike MikroTik and VyOS, a UniFi gateway ships with a working default-deny firewall out of the box — traffic between security zones (Internal, External, Gateway, VPN, Hotspot) is filtered automatically without any rules to write by hand. Open **Settings → Security → Firewall** to review the built-in zone matrix before adding anything custom.

<!-- TODO(Sven): do you want to document any custom rules here (e.g. allowing a specific inbound service), or leave this section as "review the defaults, add rules only as needed"? -->

## System

### Hostname / device name

Set an identifiable name for the gateway under **Settings → System → Device**.

### SSH access

SSH is disabled by default. Enable it under **Settings → System → Advanced** only if you need CLI access for troubleshooting, and restrict it to your LAN.

### Admin account

If you signed in with cloud SSO during adoption, consider adding a local-only admin account under **Settings → Admins** as a fallback in case cloud access is ever unavailable.

<!-- TODO(Sven): confirm whether you actually run a local fallback admin, and whether SSH is enabled on your UCG-Fiber -->

---

Your UniFi gateway is now configured with a secure baseline. From here you can expand into VLANs and network segmentation, or feed its logs into your observability stack with [Unifi Syslog with Alloy and Loki]({{< ref "/posts/2026-01-29-unifi-logs-alloy" >}}).
