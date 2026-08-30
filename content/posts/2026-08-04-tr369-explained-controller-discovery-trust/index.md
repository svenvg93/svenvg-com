---
title: "TR-369 Explained: Controller Discovery and Trust"
description: How an Agent finds a Controller in the first place — DHCP options 124/125, DNS-SD, and mDNS — and what stops multiple Controllers managing the same Agent from stepping on each other once they're connected.
date: 2026-08-04
draft: false
categories:
  - Networking
tags:
  - tr-369
  - cwmp
  - usp
  - isp
series:
  - "TR-369 Explained"
series_order: 2
---

The [previous post]({{< ref "/posts/2026-08-03-tr369-explained-what-changes" >}}) covered why USP supports multiple independent Controllers managing one Agent. This one covers both halves of what that actually requires: how an Agent finds a Controller to talk to in the first place, since USP doesn't have a single "ACS URL" field the way a CWMP Endpoint does — [Discovery][1] is a defined process with three distinct mechanisms — and, once it's found one or several, what stops those Controllers from reaching into each other's territory.

## What the Agent Actually Needs to Learn

To reach a Controller, an Agent needs four things: which **MTP** to use (CoAP, MQTT, WebSockets, or STOMP), an **address**, a **port**, and — for MTPs that need one — a **resource path**. Discovery can hand the Agent all of this bundled as a single URL, or as an FQDN that the Agent resolves further via DNS-SD to get the rest.

USP defines three ways an Agent can learn this: **DHCP**, **DNS-SD**, and **mDNS**. Which one applies depends mostly on whether the Controller is somewhere on the internet (an ISP's own platform) or sitting on the same local network as the Agent (a smart-home hub, say).

## DHCP-Based Discovery

This is the USP analog of the [ACS URL via DHCP option 43]({{< ref "/posts/2026-07-31-tr069-explained-provisioning" >}}) covered in the provisioning post — but built to avoid the exact problem option 43 has. Option 43 is a flat, vendor-specific blob with no standard internal structure, so when a network has several unrelated vendors all repurposing the same option for their own provisioning needs, nothing stops their data from colliding or being misread by the wrong device.

USP avoids this by using DHCP's **vendor-identifying** options instead, which are keyed to an IANA-assigned enterprise number rather than shared blindly:

- The Agent's request carries the **DHCPv4 Vendor-Identifying Vendor Class Option (124)** — or **DHCPv6 Vendor Class (16)** — containing the Broadband Forum's enterprise number (`3561` / `0x0DE9`) and the literal string `usp`. This is how the Agent signals "I'm asking specifically for USP Controller information," not just any vendor data.
- The DHCP server responds with the **DHCPv4 Vendor-Identifying Vendor-Specific Information Option (125)** — or **DHCPv6 equivalent (17)** — scoped to that same enterprise number, carrying a defined set of encapsulated sub-options:

| Sub-option | Carries | Maps to |
|------------|---------|---------|
| `25` | Controller URL or FQDN | The MTP connection endpoint |
| `26` | Provisioning Code | `Device.LocalAgent.Controller.{i}.ProvisioningCode` |
| `27` | Retry minimum wait interval | `Device.LocalAgent.Controller.{i}.USPNotifRetryMinimumWaitInterval` |
| `28` | Retry interval multiplier | `Device.LocalAgent.Controller.{i}.USPNotifRetryIntervalMultiplier` |
| `29` | Controller Endpoint ID | `Device.LocalAgent.Controller.{i}.EndpointID` |

All five are decoded as strings — including the two that look numeric (the retry interval and multiplier) — so an Agent implementation can't assume it's safe to read them as raw integers off the wire.

![DHCP-based USP discovery — the Agent's vendor class option 124 identifies it as a USP request, and the server's option 125 response carries five encapsulated Controller sub-options](dhcp-discovery-flow.svg "DHCP-based USP discovery — the Agent's vendor class option 124 identifies it as a USP request, and the server's option 125 response carries five encapsulated Controller sub-options")

Because DHCP itself has no built-in security, the specification is explicit that this is only safe to rely on when the link between the DHCP server and the Agent is one the operator actually controls — and that trust between the Agent and whatever Controller it discovers this way still needs to be established separately, typically with pre-configured certificates rather than assuming the DHCP response itself is trustworthy.

## DNS-SD Discovery

Where DHCP hands the Agent a Controller directly, DNS-SD (DNS Service Discovery) lets it look one up by service type — useful when the Controller's actual endpoint can change without the Agent needing reconfiguration. USP registers eight service names with IANA, one pair per MTP for each role:

| Service Name | MTP | Role |
|--------------|-----|------|
| `usp-agt-coap` | CoAP | Agent |
| `usp-agt-mqtt` | MQTT | Agent |
| `usp-agt-stomp` | STOMP | Agent |
| `usp-agt-ws` | WebSocket | Agent |
| `usp-ctr-coap` | CoAP | Controller |
| `usp-ctr-mqtt` | MQTT | Controller |
| `usp-ctr-stomp` | STOMP | Controller |
| `usp-ctr-ws` | WebSocket | Controller |

A lookup walks the standard DNS-SD record chain: a **PTR** record finds service instances of a given type, an **SRV** record for that instance gives the actual host and port, a **TXT** record carries attributes (a required `path` for both Agents and Controllers, a `name` for Agents, and an optional `encrypt` flag), and finally an **A**/**AAAA** record resolves the host to an address.

![DNS-SD Controller lookup — PTR finds service instances, SRV gives host and port, TXT carries the resource path, A/AAAA resolves the address](dns-sd-lookup-flow.svg "DNS-SD Controller lookup — PTR finds service instances, SRV gives host and port, TXT carries the resource path, A/AAAA resolves the address")

## mDNS on the Local Network

DHCP and DNS-SD both assume some shared infrastructure — a DHCP server or a real DNS zone. On a local network with neither, USP falls back to **mDNS** (RFC 6762) — the same `.local` multicast mechanism used for LAN service discovery generally. An Agent resolving a Controller FQDN ending in `.local` does it via mDNS instead of the ordinary DNS hierarchy, and any USP Endpoint supporting mDNS is required to implement both the client and server sides — since a Controller discovering Agents on the LAN needs to receive queries, not just send them.

This is the path a local smart-home hub would use to find Agents on its own network, as distinct from an ISP's cloud platform reaching a device over the internet via DHCP or DNS-SD.

## Controller Trust: Keeping Multiple Controllers From Stepping on Each Other

Finding a Controller is only half the story. USP explicitly allows an ISP, a device vendor, and a smart-home platform to all manage the same Agent independently — which raises an obvious question: what stops one Controller from reconfiguring settings another Controller depends on, or reading data it has no business seeing? The answer is **[Controller Trust][2]**: a role-based permission model that decides exactly what each Controller is allowed to touch.

### Roles: The Unit of Trust

A Controller in USP doesn't get default access to anything. It's assigned a **Role** — defined under `Device.LocalAgent.ControllerTrust.Role.{i}` — and a Role is nothing more than a named set of permissions. No Role, no access: whatever a Controller's Role doesn't explicitly grant, it doesn't have.

This is a structural difference from CWMP, which has no concept of a partially-trusted ACS at all — a CWMP session either authenticates successfully and gets full access to everything, or it doesn't authenticate and gets none. USP needed something more granular the moment it allowed more than one Controller to exist.

### Permissions: rwxn Across Four Target Types

Each Role holds one or more `Permission.{i}` entries, and each entry targets one of four things:

| Target | Covers |
|--------|--------|
| `Param` | Individual parameters |
| `Obj` | Objects — specifically, whether new instances can be created under them |
| `InstantiatedObj` | Already-existing object instances |
| `CommandEvent` | Commands (Operate) and events (subscriptions) |

Against each target, the permission is a four-character string — **`rwxn`** — Read, Write, Execute, Notify — with the meaning of `x` shifting slightly by target: on `Obj` it governs adding new instances, on `InstantiatedObj` it governs deleting existing ones, and on `CommandEvent` it governs invoking a command or subscribing to an event. A dash in any position means that right isn't granted; a Role with `r--n` on a parameter can read its value and get notified when it changes, but can't write to it at all.

![A Controller is assigned a Role; the Role's Permission entries grant rwxn rights across four target types scoped to specific data model paths](role-permission-model.svg "A Controller is assigned a Role; the Role's Permission entries grant rwxn rights across four target types scoped to specific data model paths")

### A Concrete Example: ISP vs. Smart-Home Controller

This is exactly the scenario an ISP's Controller and a smart-home platform's Controller both managing the same Agent runs into, with neither able to touch the other's territory:

| Path | ISP Controller's Role | Smart-Home Controller's Role |
|------|------------------------|-------------------------------|
| `Device.WAN.*` | `rwxn` — full control | `----` — no access at all |
| `Device.WiFi.*` | `r--n` — read and get notified only | `rwxn` — full control |
| `Device.LocalAgent.*` | `r---` — read-only | `----` — no access |

The ISP's Controller can change WAN configuration but only observe WiFi settings; the smart-home platform's Controller can manage WiFi and connected IoT devices but has no path into WAN configuration at all, and doesn't even know the Agent's own management configuration exists. Neither Controller needs to trust the other, and neither can accidentally (or otherwise) reach into the other's scope — the Agent enforces the boundary, not either Controller's good behavior.

![Two Controllers, two Roles, disjoint permission scopes over the same Agent — the ISP owns WAN, the smart-home platform owns WiFi and IoT](isp-vs-smarthome-roles.svg "Two Controllers, two Roles, disjoint permission scopes over the same Agent — the ISP owns WAN, the smart-home platform owns WiFi and IoT")

### Enforcement Happens Per-Request

Every message a Controller sends is checked against its Role's permissions before the Agent acts on it — the same way [SetParameterValues fault checking]({{< ref "/posts/2026-08-02-tr069-explained-rpcs-data-model" >}}) validates a request before applying it, just with an added layer of "is this Controller even allowed to ask this at all." A `Get` for a parameter the Role has no `r` on simply doesn't return that value; an `Operate` call against a command the Role has no `x` on for `CommandEvent` is refused outright. The Agent, not the Controller, is what's actually trusted to hold the line.

### What Permissions Don't Solve

Roles scope what each Controller *can* touch — they don't arbitrate what happens when two Controllers are both allowed to touch the *same* thing at the *same* time. USP has no distributed locking or transaction mechanism for overlapping writes; if two Controllers both hold `w` on the same parameter and write to it in quick succession, the usual last-write-wins outcome applies, same as any shared-state system without explicit coordination. The permission model's job is to make that scenario rare by design — an ISP and a smart-home platform simply shouldn't be granted overlapping write access to the same parameter in the first place — not to resolve it gracefully if it happens anyway.

## Recap

- An Agent needs an MTP, address, port, and (if the MTP requires it) a resource path to reach a Controller — delivered either as one URL or as an FQDN resolved further via DNS-SD.
- **DHCP discovery** uses vendor-identifying options keyed to the Broadband Forum's enterprise number (`3561`) rather than a flat blob like CWMP's option 43 — the Agent requests via option 124/16, the server responds via option 125/17 with five defined sub-options (URL, provisioning code, retry parameters, Endpoint ID), all decoded as strings.
- DHCP has no built-in security, so trust with a DHCP-discovered Controller still has to be established separately — usually with pre-configured certificates.
- **DNS-SD discovery** uses eight IANA-registered service names (`usp-agt-*`/`usp-ctr-*`, one pair per MTP) and the standard PTR → SRV → TXT → A/AAAA record chain to resolve a Controller.
- **mDNS** handles discovery on a local network with no DHCP or DNS infrastructure to lean on, resolving `.local` addresses directly between Agent and Controller.
- USP Controllers get no default access; each is assigned a **Role** (`Device.LocalAgent.ControllerTrust.Role.{i}`) that defines exactly what it can do, via `Permission` entries scoped to `Param`, `Obj`, `InstantiatedObj`, or `CommandEvent` and granted as an `rwxn` string.
- This is how an ISP Controller and a smart-home platform's Controller can manage the same Agent safely: disjoint Roles give each exactly the scope it needs, enforced per-request at the Agent — not arbitration of simultaneous writes within a scope two Controllers both happen to share, which permissions don't solve.

This has all been about who can reach the Agent and what they're allowed to do once there — not what the messages doing it actually look like. See [TR-369 Explained: Messages, RPCs, and Notifications]({{< ref "/posts/2026-08-06-tr369-explained-messages-and-notifications" >}}) for `Get`, `Set`, and the rest, lined up against their CWMP equivalents.

[1]: https://github.com/BroadbandForum/usp/blob/master/specification/discovery/index.md
[2]: https://github.com/BroadbandForum/usp-test/blob/master/02-authentication-and-access-control.md
