---
title: "IPv6 Explained: Prefix Delegation"
description: ISPs don't just give your router a single IPv6 address — they delegate an entire prefix. Here's how DHCPv6-PD works, what prefix sizes mean, and how a router subdivides the block for its networks.
date: 2026-06-04
draft: false
cover: cover.svg
categories:
  - Networking
tags:
  - ipv6
series:
  - IPv6 Explained
series_order: 4
---

In IPv4, a home router gets one public IP address from the ISP — typically via DHCP on the WAN interface — and uses NAT to share it across all devices on the LAN. IPv6 is designed differently: there's no NAT, so every device needs a public address. The mechanism that makes this work at scale is **prefix delegation**.

Instead of assigning a single address, the ISP delegates an entire address block to your router. The router then subdivides that block and advertises smaller prefixes to each of its networks. Every device on the LAN gets a globally routable IPv6 address directly.

## DHCPv6-PD

Prefix delegation is negotiated through **DHCPv6-PD** (DHCPv6 Prefix Delegation), defined in [RFC 8415][1]. The router acts as a DHCPv6-PD client on its WAN interface, requesting a prefix. The ISP's DHCPv6 server assigns one.

The exchange:

1. Router sends a **Solicit** with an IA_PD (Identity Association for Prefix Delegation) option, optionally requesting a specific prefix length.
2. ISP server replies with an **Advertise** containing the delegated prefix and its lease time.
3. Router sends a **Request** to confirm.
4. Server confirms with a **Reply** — delegation complete.

The router now owns that prefix for the duration of the lease and is responsible for routing all traffic destined to it.

![](pd-exchange.svg "DHCPv6-PD exchange — router requests prefix delegation from ISP, receives /48 or /56")

## Prefix Sizes

ISPs vary in how much space they delegate:

| Prefix | Subnets available (/64) | Typical assignment |
|--------|------------------------|-------------------|
| `/48`  | 65,536 | Business, some residential ISPs |
| `/56`  | 256 | Common residential |
| `/60`  | 16 | Some ISPs, minimal allocation |
| `/64`  | 1 | Single subnet — no room to divide |

A `/64` delegation is the worst case: the router can use it for exactly one subnet and cannot subdivide it further (since `/64` is the standard subnet size). A `/56` is the practical minimum for a homelab — 256 subnets is enough for VLANs, containers, and any reasonable segmentation. A `/48` gives essentially unlimited subnets.

If your ISP only delegates a `/64`, you cannot create separate IPv6 subnets for VLANs without additional mechanisms like NPTv6.

## Subdividing the Prefix

Once the router has a delegated prefix, it carves it into `/64` subnets and assigns one to each interface or VLAN. It then sends Router Advertisements on each interface with the appropriate prefix, triggering SLAAC on the clients.

With a `/56` delegation of `2001:db8:abcd:ab00::/56`, the router has 8 bits of subnet space — bits 56 to 63. In the fourth 16-bit group `abXX`, the first byte `ab` is part of the ISP's fixed /56 prefix; the second byte `XX` (00–ff) is the subnet field the router controls:

```
2001:db8:abcd:ab00::/64  ← LAN (VLAN 1)
2001:db8:abcd:ab01::/64  ← IoT (VLAN 2)
2001:db8:abcd:ab02::/64  ← Servers (VLAN 3)
2001:db8:abcd:ab03::/64  ← Guest (VLAN 4)
...
2001:db8:abcd:abff::/64  ← subnet 255
```

![](pd-subdivision.svg "Prefix subdivision — /56 from ISP split into /64 subnets per VLAN")

The router adds a route for the entire delegated prefix pointing to itself on the WAN side, and routes individual `/64` subnets to the correct internal interfaces.

## Prefix Stability

Delegated prefixes are not always stable. Many ISPs rotate prefixes on reconnect or lease expiry, which means every device's public address changes. This matters if:

- You're running services reachable by IPv6 address
- DNS records point to specific IPv6 addresses
- Firewall rules reference specific prefixes

Some ISPs offer stable prefix delegation (sometimes called a static IPv6 prefix) as an add-on. Alternatively, dynamic DNS that updates IPv6 records on prefix change can mitigate the problem.

ULA addresses (`fd00::/8`) are immune to this — they're generated locally and never change regardless of what the ISP does. Services that only need to be reachable within the network can use ULA addresses for a stable target, regardless of the delegated prefix.

[1]: https://datatracker.ietf.org/doc/html/rfc8415
