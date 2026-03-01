---
title: WireGuard VPN Server on MikroTik
description: Set up a WireGuard VPN server on a MikroTik router for secure remote access to your homelab.
date: 2026-02-03
draft: true
categories:
  - Networking
  - Router
tags:
  - mikrotik
  - wireguard
  - vpn
cover: cover.jpg

---

WireGuard is a modern, high-performance VPN protocol that is simple to configure and provides excellent security. MikroTik routers running RouterOS v7 and above have built-in WireGuard support, making it easy to set up a VPN server for secure remote access to your homelab network.

> **Tip:** Replace the placeholder variables with values that match your environment.

## WireGuard Interface

Create a WireGuard interface on the router. This will automatically generate a private and public key pair for the server.

```bash
/interface wireguard
add name=wireguard1 listen-port=13231 mtu=1420 comment="Remote VPN"
```

Assign an IP address to the WireGuard interface. This will be the gateway address for the VPN subnet.

```bash
/ip address
add address=172.16.20.1/24 interface=wireguard1 comment="WG subnet"
```

## Firewall Rules

Add firewall rules to allow WireGuard traffic and permit communication between VPN clients and your LAN.

```bash
/ip firewall filter
add chain=input action=accept protocol=udp dst-port=13231 in-interface=ether1 comment="Allow WireGuard"
add chain=forward action=accept in-interface=wireguard1 out-interface=bridge1 comment="WG to LAN"
add chain=forward action=accept in-interface=bridge1 out-interface=wireguard1 comment="LAN to WG"
```

> **Warning:** Make sure these rules are placed **before** any drop rules in their respective chains. Adjust `in-interface=ether1` to match your WAN interface name.

## Peers

Add a peer for each client that should connect to the VPN. You'll need the public key from the client's WireGuard configuration.

```bash
/interface wireguard peers
add allowed-address=172.16.20.2/32 comment=Sven interface=wireguard1 public-key="<CLIENT-PUBLIC-KEY>"
```

Each peer should have a unique IP address within the WireGuard subnet (`172.16.20.0/24`). Increment the last octet for each additional peer (e.g., `172.16.20.3/32`, `172.16.20.4/32`).

## Client Configuration

On the client side, configure WireGuard with the following settings:

- **Endpoint**: Your router's public IP or hostname and the WireGuard listen port (e.g., `your-public-ip:13231`)
- **Allowed IPs**: `172.16.20.0/24, 192.168.1.0/24` (VPN subnet and LAN subnet)
- **Server public key**: Retrieve it from the router with `/interface wireguard print`

With WireGuard configured on your MikroTik, you now have a fast and secure VPN tunnel into your homelab from anywhere.
