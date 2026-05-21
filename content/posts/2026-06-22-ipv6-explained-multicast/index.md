---
title: "IPv6 Explained: Multicast and MLD"
description: IPv6 eliminates broadcast and replaces it entirely with multicast. Here's how IPv6 multicast addressing works, what MLD does, and why switches need to handle it correctly for NDP to function.
date: 2026-06-22
draft: false
cover: cover.svg
categories:
  - Networking
tags:
  - ipv6
series:
  - IPv6 Explained
series_order: 5
---

IPv4 has broadcast — a packet sent to all devices on a segment, whether they care about it or not. IPv6 removes broadcast entirely. Everything broadcast was used for — router discovery, address resolution, group membership — is handled by multicast, which delivers packets only to devices that have expressed interest in receiving them.

This is not just a naming change. Multicast in IPv6 is a structured system with scoped address space, mandatory group management, and deep integration into NDP and SLAAC. Understanding it is essential for understanding why IPv6 behaves the way it does on a switched network.

## Multicast Address Structure

IPv6 multicast addresses always start with `ff`. The next 8 bits encode two fields:

```
ff  |flags (4 bits)| scope (4 bits) | group ID (112 bits)
```

**Flags** — the most significant flag bit is unused (0). The remaining three bits are:

- **R (Rendezvous Point)** — used in PIM-SM multicast routing; the RP address is embedded in the group address (RFC 3956).
- **P (Prefix-based)** — the group address is derived from a unicast prefix (RFC 3306), allowing locally scoped multicast without a central allocation.
- **T (Transient)** — 0 means the address is a well-known, permanently assigned group. 1 means it was dynamically assigned and is not a permanent IANA allocation.

**Scope** — controls how far the multicast packet travels:

| Scope value | Name | Reach |
|---|---|---|
| 1 | Interface-local | Loopback only — never leaves the interface |
| 2 | Link-local | Single link segment — routers do not forward |
| 4 | Admin-local | Administratively defined local scope |
| 5 | Site-local | A site — routers may forward within a site |
| 8 | Organization-local | An organisation — forwarded within an org |
| e | Global | Internet-wide |

Most multicast traffic relevant to NDP and SLAAC uses scope 2 (link-local). These packets never cross a router, regardless of the routing table.

![](multicast-address-structure.svg "IPv6 multicast address structure — ff prefix, flags (R/P/T), scope, and 112-bit group ID")

## Well-Known Multicast Groups

Several multicast addresses are permanently assigned and used by every IPv6 host:

| Address | Group | Who listens |
|---|---|---|
| `ff02::1` | All nodes (link-local) | Every IPv6 interface |
| `ff02::2` | All routers (link-local) | Every IPv6 router |
| `ff02::1:2` | All DHCPv6 relay/server agents | DHCPv6 servers and relays |
| `ff02::fb` | mDNS | Hosts running mDNS (e.g. Avahi, Apple Bonjour) |
| `ff02::101` | NTP | NTP servers |
| `ff02::1:ff00:0/104` | Solicited-node multicast | Per-address group used by NDP |

The **solicited-node multicast address** deserves special mention. Every unicast and anycast address has a corresponding solicited-node group: `ff02::1:ff` followed by the last 24 bits of the unicast address. When NDP needs to resolve a neighbor, it sends a Neighbor Solicitation to this multicast group rather than to all nodes — ensuring only the device with a matching address (or at most a handful of devices sharing those 24 bits) processes the packet.

## Multicast Listener Discovery (MLD)

On a link with multiple devices and a multicast-capable switch, the switch needs to know which ports have listeners for which groups. Without this information, it floods multicast to every port — the same problem broadcast causes. **MLD (Multicast Listener Discovery)** is the protocol that solves this.

MLD is IPv6's replacement for IGMP (used in IPv4). It runs between hosts and their directly connected router, letting hosts signal which multicast groups they want to receive. The router uses this information, and switches running MLD snooping use the same signalling to populate their multicast forwarding tables.

### MLD Versions

**MLDv1** (RFC 2710) — works at the group level. A host joins or leaves a group. The router periodically sends General Queries; hosts respond with Reports for each group they belong to. A leave triggers a Group-Specific Query to check whether any other host on the link still wants the group before the router stops forwarding.

**MLDv2** (RFC 3810) — adds source filtering. A host can specify not just which groups it wants, but also which sources within a group it will accept (INCLUDE mode) or exclude (EXCLUDE mode). This is required for SSM (Source-Specific Multicast) and allows more precise traffic control.

Most modern deployments use MLDv2. MLDv1 interoperability is maintained.

### MLD Message Types (ICMPv6)

| Type | Name | Direction |
|---|---|---|
| 130 | Multicast Listener Query | Router → hosts. General query (all groups) or group-specific. |
| 131 | Multicast Listener Report (v1) | Host → router. Announces group membership. |
| 132 | Multicast Listener Done (v1) | Host → router. Announces departure from a group. |
| 143 | Multicast Listener Report (v2) | Host → router. Includes source-filter information. |

All MLD messages are sent with a Hop Limit of 1 and the Router Alert option in a [Hop-by-Hop extension header](/posts/2026-05-25-ipv6-explained-addressing/) — this ensures they are not forwarded beyond the local link and that routers process them even if they are not the destination.

## MLD Snooping

A switch that does not understand MLD treats multicast as broadcast and floods it to every port. This is fine for correctness but wasteful at scale — and becomes a real problem when multicast traffic is high-rate (video streams, for example) or when there are many groups.

**MLD snooping** is a switch feature that listens to MLD exchanges between hosts and routers, building a table of which ports have active listeners for each group. Multicast is then forwarded only to ports with interested receivers, plus the router port.

For IPv6, MLD snooping has one critical implication: **solicited-node multicast groups must always be forwarded correctly**. These groups underpin NDP — if a switch incorrectly filters solicited-node multicast, Neighbor Solicitations do not reach their target, neighbor resolution fails, and connectivity breaks entirely. A switch running MLD snooping must either:

- Forward all `ff02::1:ff::/104` traffic to all ports (treating the entire solicited-node range as always-flooded), or
- Learn which ports subscribe to specific solicited-node groups via MLD snooping and forward selectively.

Switches that implement MLD snooping without correctly handling the solicited-node range are a common source of intermittent IPv6 connectivity failures on managed networks.

![](mld-snooping.svg "MLD snooping — switch floods multicast without it; with it, only subscribed ports receive traffic")

## Multicast in Routing

On a single link, multicast is handled by MLD and the switch. Across multiple links, multicast requires a multicast routing protocol. The most common is **PIM (Protocol Independent Multicast)**:

- **PIM-SM (Sparse Mode)** — builds trees rooted at a Rendezvous Point (RP). Receivers join the tree; sources register with the RP. Used where receivers are distributed sparsely across the network.
- **PIM-SSM (Source-Specific Multicast)** — receivers subscribe to a specific source address, not just a group. No RP required. More scalable for one-to-many streams (e.g. IPTV). Uses the `ff3x::/32` address range.
- **PIM-DM (Dense Mode)** — floods multicast everywhere and prunes back branches with no receivers. Rarely used in modern deployments.

IPv6 multicast routing is outside the scope of a typical dual-stack deployment, but understanding that multicast does not automatically traverse routers — and that it requires explicit routing support beyond the local link — is important when designing networks that use multicast-dependent services.
