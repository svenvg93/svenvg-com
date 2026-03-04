---
title: WireGuard VPN Server on MikroTik
description: Configure a WireGuard VPN server on a MikroTik router to enable secure, encrypted remote access to your homelab network from any device.
date: 2026-02-03
lastmod: 2026-02-03
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

## Prerequisites

Before starting, ensure you have:

- **MikroTik router** running RouterOS v7 or later with WireGuard package installed. See the [Setting Up a MikroTik Router]({{< ref "/posts/2025-01-05-setup-mikrotik-router" >}}) guide for initial setup.
- **SSH or terminal access** to your MikroTik router
- **Client devices** where you'll install WireGuard (Linux, macOS, Windows, iOS, or Android)
- **Public IP address** or dynamic DNS hostname for your router (for remote access)
- **Understanding of your network topology** (WAN interface name, LAN subnet, etc.)

> Replace the placeholder variables with values that match your environment.

## WireGuard Interface

Create a WireGuard interface on the router. This will automatically generate a private and public key pair for the server.

```bash {filename="WireGuard Interface"}
/interface wireguard
add name=wireguard1 listen-port=13231 mtu=1420 comment="Remote VPN"
```

Assign an IP address to the WireGuard interface. This will be the gateway address for the VPN subnet.

```bash {filename="IP Address Configuration"}
/ip address
add address=192.168.100.1/24 interface=wireguard1 comment="WG subnet"
```

## Firewall Rules

Add firewall rules to allow WireGuard traffic and permit communication between VPN clients and your LAN.

```bash {filename="Firewall Configuration"}
/ip firewall filter
add chain=input action=accept protocol=udp dst-port=13231 in-interface=ether1 comment="Allow WireGuard"
add chain=forward action=accept in-interface=wireguard1 out-interface=bridge1 comment="WG to LAN"
add chain=forward action=accept in-interface=bridge1 out-interface=wireguard1 comment="LAN to WG"
```

>  Make sure these rules are placed **before** any drop rules in their respective chains. Adjust `in-interface=ether1` to match your WAN interface name.

## Peers

On your MikroTik router, you must add a peer for **each client** that should connect to the VPN.

You will need the **client’s public key** from its WireGuard configuration.

```bash {filename="Add Peer"}
/interface wireguard peers
add interface=wireguard1 public-key="[CLIENT-PUBLIC-KEY]" allowed-address=192.168.100.2/32 name=RemoteUser1
```

Each peer should have a unique IP address within the WireGuard subnet (`192.168.100.0/24`). The `allowed-address` value must match the Address configured on the client.

## Client Configuration

On the client device, configure WireGuard as follows:

```ini {filename="Client"}
[Interface]
PrivateKey = [CLIENT-PRIVATE-KEY]
ListenPort = 51821
Address = 192.168.100.2/32

[Peer]
PublicKey = [ROUTER-PUBLIC-KEY]
AllowedIPs = 192.168.100.0/24, 192.168.1.0/24
Endpoint = [YOUR-PUBLIC-IP]:13231
```

- **Endpoint**: Your router’s public IP address or hostname and the WireGuard listen port. (e.g., `your-public-ip:13231`)
- **AllowedIPs**: Defines which networks are reachable through the VPN tunnel.
- **PublicKey**: Retrieve it from the router with `/interface wireguard print`. This must be the **router's public key**, not the client's.

## Internet over the VPN
The configuration above is a **split-tunnel** setup. Only traffic destined for the specified networks in `AllowedIPs` is sent through the VPN.

If you want **all internet traffic** to go through the VPN (full-tunnel setup), additional configuration is required.

### Modify the Client Configuration

On the client, change `AllowedIPs` to:

```ini
[Peer]
AllowedIPs = 0.0.0.0/0
```

#### DNS Considerations
When using full-tunnel mode, DNS should also go through the VPN. Use your MikroTik's address or any DNS server reachable through the VPN:

```ini
[Interface]
DNS = 192.168.100.1
```

This ensures DNS queries are also routed through the VPN tunnel. Alternatively, use a public DNS server like `1.1.1.1` or `8.8.8.8`.

### Firewall Rules for Full-Tunnel

To enable internet traffic through the VPN, add these rules:

```bash {filename="Full-Tunnel Firewall Rules"}
/ip firewall filter
add action=accept chain=forward comment="WG to Internet" in-interface=wireguard1 out-interface=ether1
add action=accept chain=input comment="Allow traffic from WG to router" in-interface=wireguard1
```

> Replace `ether1` with your actual WAN interface name. Check with `/interface print` if unsure.

## Conclusion

With WireGuard configured on your MikroTik, you now have a fast, modern, and secure VPN tunnel into your homelab from anywhere. The setup is straightforward and significantly simpler than older VPN protocols like OpenVPN or IPSec, while maintaining excellent performance and security.
