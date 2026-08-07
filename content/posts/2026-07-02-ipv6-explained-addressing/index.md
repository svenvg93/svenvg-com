---
title: "IPv6 Explained: Addressing"
description: How IPv6 addresses are notated and typed, how the 64-bit prefix/interface-ID split and subnetting work, and how the packet header is structured.
date: 2026-07-02
draft: false
categories:
  - Networking
tags:
  - ipv6
  - addressing
series:
  - "IPv6 Explained"
series_order: 1
---

IPv4 uses 32-bit addresses. That gives roughly 4.3 billion unique values — a number that made sense in 1981 and became a serious problem by the 2000s. IANA exhausted its IPv4 pool in 2011. IPv6 uses 128-bit addresses, which provides 340 undecillion unique values — enough that address conservation is no longer a design constraint.

The address space alone justifies the switch, but IPv6 also changes how addresses are notated, typed, and structured, and moves everything IPv4 handled with a variable-length options field into a chain of extension headers instead. This guide covers all of that: notation, address types and scopes, the prefix/interface-ID split, subnetting, and the packet header itself.

## Notation

An IPv6 address is 128 bits written as eight groups of four hexadecimal digits, separated by colons:

```
2001:0db8:0000:0000:0000:0000:0000:0001
```

Two shortening rules apply. First, leading zeros within each group can be dropped:

```
2001:db8:0:0:0:0:0:1
```

Second, one contiguous run of all-zero groups can be replaced with `::`:

```
2001:db8::1
```

The `::` can only appear once in an address. `::1` is the loopback address (equivalent to `127.0.0.1`). `::` alone is the unspecified address.

![IPv6 address notation — full form, zero-compressed, and double-colon shorthand](address-notation.svg "IPv6 address notation — full form, zero-compressed, and double-colon shorthand")

## Address Types

IPv6 has no broadcast. Instead it has three address types:

**Unicast** — identifies a single interface. Packets delivered to exactly one destination. The common case.

**Multicast** — identifies a group of interfaces. Packets delivered to all members of the group. Replaces broadcast for most purposes and underpins Neighbor Discovery.

**Anycast** — the same address assigned to multiple interfaces. Packets routed to whichever interface is topologically nearest. Used for DNS root servers and CDN infrastructure.

## Scope and Address Ranges

Not all unicast addresses are the same. IPv6 defines several ranges with different scopes:

**Global Unicast Addresses (GUA)** — publicly routable, globally unique. The `2000::/3` block covers most of this range. These are what devices use to communicate on the internet. ISPs assign GUA prefixes to home and business networks.

**Unique Local Addresses (ULA)** — private, not routed on the internet. The `fc00::/7` range (in practice `fd00::/8`). Equivalent to [RFC 1918][1] space in IPv4 (`192.168.x.x`, `10.x.x.x`). Use these for internal services that should never be reachable from outside.

**Link-Local Addresses** — valid only on a single link (network segment), never forwarded by routers. Always start with `fe80::/10`. Every IPv6 interface has one automatically — they're used for router discovery and Neighbor Discovery Protocol before any other address is configured.

**Documentation prefix** — `2001:db8::/32` is reserved by IANA ([RFC 3849][2]) exclusively for documentation and examples. It is never routed on the internet. All address examples throughout this guide use `2001:db8::` addresses for this reason — they cannot be confused with real addresses.

Because every interface has its own link-local address, and a host with several interfaces has one per interface, the address alone doesn't say which interface to use it on. Connecting to one requires a **zone ID** (also called scope ID) appended to the address: `fe80::1%eth0` on Linux, `fe80::1%en0` on macOS, `fe80::1%12` (interface index) on Windows. Forgetting the zone ID is the most common reason `ping fe80::...` or `ssh fe80::...` fails outright — the address by itself is ambiguous, not invalid.

![IPv6 address types — GUA, ULA, and link-local with their prefixes and scopes](address-types.svg "IPv6 address types — GUA, ULA, and link-local with their prefixes and scopes")

## Address Structure

A GUA address has two parts: a **network prefix** and an **interface identifier**.

```
| <-- 64 bits prefix --> | <-- 64 bits interface ID --> |
  2001:db8:1234:abcd     :     0201:c0ff:fee0:1234
```

The prefix identifies the network — assigned by the ISP down to the router, then subdivided per subnet. The interface identifier uniquely identifies the device within that network.

The `/64` boundary is the standard subnet size in IPv6. Routers are not expected to subnet below `/64` (with few exceptions). This means every IPv6 subnet has 2⁶⁴ addresses — more than enough that address conservation within a subnet is irrelevant.

## Interface Identifiers

The interface identifier can be generated several ways:

**Modified EUI-64** — derived from the device's MAC address. The 48-bit MAC is split in two, `fffe` is inserted in the middle, and bit 6 of the first byte is flipped (the Universal/Local bit, signalling the address was derived from a MAC) — the bit flip is what makes it "modified" rather than plain IEEE EUI-64. This produces a globally unique 64-bit identifier — but also embeds the MAC, which is a privacy concern.

![Modified EUI-64 construction — MAC address split, fffe inserted, U/L bit flipped to produce the 64-bit interface ID](eui64-construction.svg "Modified EUI-64 construction — MAC address split, fffe inserted, U/L bit flipped to produce the 64-bit interface ID")

**Privacy extensions ([RFC 8981][3])** — the interface ID is randomly generated and rotated periodically. Most modern operating systems use this by default for outbound connections to prevent tracking across networks.

**Manual / static** — set explicitly. Common on routers, servers, and infrastructure where a stable address matters.

## Source Address Selection

A single interface often ends up with several valid addresses at once — a GUA, sometimes a ULA, and if privacy extensions are enabled, both a stable and a temporary GUA. When a device opens an outbound connection, something has to decide which one to use as the source. **[RFC 6724][4]** defines the default algorithm every major OS implements. The rules that matter in practice, in order:

- **Scope match first** — a global destination gets a global (GUA) source, a link-local destination gets a link-local source. This is why adding a [ULA]({{< ref "/posts/2026-07-06-ipv6-explained-routing-security-transition" >}}#ula-for-internal-services) to a network doesn't disrupt normal internet-bound traffic: ULA only gets selected as a source when the destination is also ULA.
- **Prefer temporary over stable, when both exist** — if privacy extensions are enabled, the OS defaults to the temporary address for new outbound connections, which is what actually makes privacy extensions private. A device with only a stable address (typical for a server or router) just uses it — there's nothing to prefer over.
- **Longest matching prefix** — among otherwise-equal candidates, prefer the source address that shares the most prefix bits with the destination.

This is worth knowing when something behaves unexpectedly: a server binding to "any" address may still answer from a temporary address that rotates, breaking a firewall rule or allowlist written against its stable one — the fix is either disabling privacy extensions on that host or binding the service to the specific stable address explicitly.

## Subnetting

ISPs typically hand a `/48` or `/56` prefix to a customer. The bits between the ISP's prefix and `/64` are yours to allocate as subnets.

With a `/48`, you have 16 bits of subnet space — 65,536 possible `/64` subnets. With a `/56`, you have 8 bits — 256 subnets. Either is enough for any homelab or small business, with room to spare.

```
ISP assigns:   2001:db8:abcd::/48
Your subnets:  2001:db8:abcd:0001::/64  ← VLAN 1
               2001:db8:abcd:0002::/64  ← VLAN 2
               2001:db8:abcd:0003::/64  ← VLAN 3
               ...
```

The notation `/64` after the address specifies the prefix length — how many bits are the network part. Everything after is the interface ID.

## Packet Header

The IPv6 base header is fixed at **40 bytes**. Unlike IPv4 — which has a variable-length header with an options field — all options in IPv6 are pushed into extension headers, keeping the base header constant-length and router-friendly.

| Field | Bits | Description |
|---|---|---|
| Version | 4 | Always 6 |
| Traffic Class | 8 | Upper 6 bits: DSCP (QoS marking). Lower 2 bits: ECN (Explicit Congestion Notification). Equivalent to the IPv4 DS field. |
| Flow Label | 20 | Identifies a flow between source and destination. Routers use it for consistent ECMP path selection without inspecting upper-layer headers. |
| Payload Length | 16 | Length of everything after the 40-byte header, in bytes. Does not include the header itself. |
| Next Header | 8 | Type of the next header — either an extension header or an upper-layer protocol (6=TCP, 17=UDP, 58=ICMPv6). |
| Hop Limit | 8 | Decremented by each router. Packet dropped and ICMPv6 Time Exceeded sent when it reaches zero. Equivalent to IPv4's TTL. |
| Source Address | 128 | — |
| Destination Address | 128 | — |

There is no header checksum. IPv4 included one because routers modified the TTL field in transit, requiring recomputation at every hop. IPv6's Hop Limit fills the same role but without a checksum — upper-layer protocols carry their own integrity checks, and link layers provide error detection.

![IPv6 base header — 40-byte fixed structure with field sizes and purpose](ipv6-packet-header.svg "IPv6 base header — 40-byte fixed structure with field sizes and purpose")

## Extension Headers

IPv6 replaces the IPv4 options field with **extension headers** — additional headers chained between the base header and the upper-layer protocol. Each header identifies the next via its own Next Header field, forming a linked list that terminates at the upper-layer protocol or at Next Header 59 (No Next Header).

| Next Header | Extension Header | Purpose |
|---|---|---|
| 0 | Hop-by-Hop Options | Processed by every node along the path. Rarely encountered — often filtered as a DoS vector. |
| 60 | Destination Options | Options for the packet's destination(s). Can appear twice (see below). Rarely encountered. |
| 43 | Routing | Specifies an explicit path through the network. The original type (RH0) was deprecated as a DoS vector. Rarely encountered. |
| 44 | Fragment | Carries fragmentation state when a source has split a packet that exceeds path MTU — see [Fragmentation]({{< ref "/posts/2026-07-06-ipv6-explained-routing-security-transition" >}}#fragmentation) for how routers handle oversized packets. |
| 51 | AH | IPsec Authentication Header — integrity and origin authentication without encryption. |
| 50 | ESP | IPsec Encapsulating Security Payload — encryption. |
| 60 | Destination Options | A second occurrence: options meant only for the final destination, versus the earlier occurrence, meant for intermediate destinations listed in a Routing header. |
| 59 | No Next Header | Terminates the chain when there's no upper-layer payload. |

Extension headers must appear in the order listed above, as defined by [RFC 8200][5]. In practice, the only ones you'll actually encounter are Fragment (source fragmentation and PMTUD) and ESP/AH (VPN traffic).

![Extension header chaining — Next Header field links base header to extension headers to upper-layer protocol](extension-headers.svg "Extension header chaining — Next Header field links base header to extension headers to upper-layer protocol")

## Recap

- IPv6 addresses are 128 bits, written as eight hex groups with two shortening rules: leading zeros dropped, one run of zero groups collapsed to `::`.
- Three address types: unicast, multicast, anycast — no broadcast.
- GUA, ULA, and link-local cover the three scopes that matter day to day; `2001:db8::/32` is reserved for documentation.
- The standard subnet is `/64`: 64 bits of prefix, 64 bits of interface ID. ISPs typically delegate a `/48` or `/56`, leaving plenty of `/64` subnets to allocate.
- Interface IDs come from Modified EUI-64, RFC 8981 privacy extensions, or manual assignment — each with different stability and privacy trade-offs.
- The 40-byte fixed base header pushes all options into a chain of extension headers, removing the need for a header checksum.

With addressing and the packet format covered, the next question is how a device actually gets one of these addresses in the first place — see [SLAAC, Neighbor Discovery & Multicast]({{< ref "/posts/2026-07-04-ipv6-explained-slaac-multicast" >}}).

[1]: https://datatracker.ietf.org/doc/html/rfc1918
[2]: https://datatracker.ietf.org/doc/html/rfc3849
[3]: https://datatracker.ietf.org/doc/html/rfc8981
[4]: https://datatracker.ietf.org/doc/html/rfc6724
[5]: https://datatracker.ietf.org/doc/html/rfc8200
