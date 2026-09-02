---
title: "TR-369 Explained: What Actually Changes from TR-069"
description: TR-369, the User Services Platform, is the Broadband Forum's designated successor to CWMP — not a hypothetical future standard. This post covers what actually changes for a device that speaks USP instead of TR-069, and why most of what came before still applies.
date: 2026-08-03
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
series_order: 1
---

TR-069's CPE WAN Management Protocol — CWMP — has run ISP-managed device provisioning for well over a decade. The Broadband Forum's designated successor is **[TR-369, the User Services Platform (USP)][1]**. It's not a hypothetical future replacement; it's a published, deployed standard, and understanding what it actually changes (and what it deliberately keeps) matters for anyone working with CWMP today.

## Same Data Model, Different Protocol

Start with the good news: CWMP's parameter tree — the `Device.` data model an ACS reads and writes — mostly carries over unchanged. TR-181 Issue 2 is explicitly titled "Device Data Model for **CWMP Endpoints and USP Agents**" — the same `Device.WiFi.SSID.1.SSID`-style tree serves both protocols. What changes with USP isn't what gets managed, it's how the message asking for it gets there.

This is deliberate: a CPE vendor can adopt USP without redesigning its entire parameter model, and an ACS/Controller platform that already understands TR-181 isn't starting from zero.

## Terminology Shift: ACS/CPE Becomes Controller/Agent

USP renames the two roles — the management platform is a **Controller**, the managed device is an **Agent** — but the more consequential change isn't the naming, it's the cardinality. CWMP's practical model is one ACS managing a CPE (Connection Request, periodic Inform, and the STUN NAT-traversal workaround all assume a single management relationship). USP explicitly supports **multiple Controllers managing one Agent at the same time** — an ISP, the device manufacturer, and a smart-home platform can each hold an independent management relationship with the same device, without one having to proxy through another.

![CWMP's effectively single-ACS model vs USP's explicit multi-Controller model over one Agent](controller-agent-comparison.svg "CWMP's effectively single-ACS model vs USP's explicit multi-Controller model over one Agent")

## Transport-Agnostic by Design: The MTP Layer

CWMP is welded to SOAP over HTTP(S) — that's not a configuration choice, it's the protocol. USP separates the message layer from the transport entirely, through a **Message Transfer Protocol (MTP)** abstraction. The same USP message can travel over WebSockets, MQTT, STOMP, or a local Unix Domain Socket, chosen to fit the device and the deployment — a device managed from an ISP's cloud platform and one managed by a controller process running on the device itself don't have to use the same transport just because they both speak USP. No MTP is mandatory; an implementation supports whichever ones its deployment needs.

The MTPs split along one line that matters: whether a broker sits in the middle. **WebSocket and UDS are direct** — the Agent holds a connection straight to the Controller (or, with UDS, to a Controller process on the same box). **MQTT and STOMP are broker-based** — the Agent connects to a message broker and so does the Controller, with neither holding a connection to the other. What all four share is that they're connection-oriented: the Agent opens one long-lived connection and both directions ride on top of it, which is exactly what the next section relies on.

| MTP | Model | Transport | Security | Best fit |
|-----|-------|-----------|----------|----------|
| WebSocket | Direct Agent↔Controller, no broker | TCP, upgraded from HTTP — rides port 443 through firewalls and proxies | TLS (`wss://`) | ISP cloud management and straightforward onboarding — the common default |
| MQTT | Broker-based pub/sub | TCP | TLS | Large fleets fanning out through a broker; already common in smart-home and IoT |
| STOMP | Broker-based, text-framed | TCP | TLS | Slotting into an existing enterprise message queue; rare in consumer CPE, effectively legacy |
| UDS | Direct, local IPC only | Unix domain socket — no network | OS file permissions | Agent and Controller on the *same* device, e.g. a local controller process on a gateway |

![The four current USP MTPs — WebSocket and UDS connect directly, MQTT and STOMP go through a broker](mtp-comparison.svg "The four current USP MTPs — WebSocket and UDS are direct, MQTT and STOMP are broker-based")

**CoAP was a fifth MTP, now gone.** The original USP spec defined a CoAP binding — UDP-based, modeled on HTTP's request/response pattern rather than a persistent session, aimed at battery-powered constrained devices that can't afford to hold a connection open. It never fit cleanly: a CoAP Agent behind NAT is back to something close to CWMP's original problem, needing periodic keepalives to hold a NAT binding open (or CoAP's `Observe` extension for subscribe-style notifications) instead of getting reachability for free from a persistent connection. USP 1.2 deprecated it, USP 1.3 obsoleted it, and that same release added the UDS binding above.

## Solving the NAT Problem for Real

This is where the change actually matters in practice. CWMP handles an ACS needing to reach a CPE behind CGNAT with a Connection Request to a WAN-side listener when possible, and a STUN-mediated UDP workaround when it isn't — a workaround built on top of a fundamentally poll/request-response protocol.

With MQTT (or WebSockets or STOMP) as the MTP, the problem doesn't need a workaround at all. The Agent holds a persistent outbound connection — to an MQTT broker, or a WebSocket held open to a Controller-side endpoint — the same kind of long-lived connection a chat app keeps open. The Controller sends a message whenever it needs to, and it's delivered over the connection the Agent already has open. There's no WAN-side listener to reach, no CGNAT mapping to punch through, because the Agent never needed to accept an inbound connection in the first place.

![CWMP's Connection Request/STUN workaround vs USP's persistent MQTT connection — the Agent is always reachable because it never stopped being connected](mtp-pubsub.svg "CWMP's Connection Request/STUN workaround vs USP's persistent MQTT connection — the Agent is always reachable because it never stopped being connected")

## RPCs Become Uniform: Get/Set/Add/Delete/Operate

CWMP's RPC set mixes generic parameter access (`GetParameterValues`, `SetParameterValues`) with a handful of special-purpose methods bolted on separately (`Reboot`, `FactoryReset`, `Download`, `Upload` are each their own SOAP RPC). USP keeps the same four core verbs — Get, Set, Add, Delete — but formalizes actions as **Operate**, invoked against a command path in the data model itself, rather than as one-off RPCs outside it. Rebooting a USP Agent means calling Operate against `Device.Reboot()` in the data model, not calling a specially-defined `Reboot` method — one uniform mechanism instead of a growing list of special cases.

## Migration: Dual-Stack Devices

Because the data model is shared, a device isn't forced into a flag-day cutover. A CPE can run as a CWMP Endpoint and a USP Agent simultaneously during a transition period, exposing the same TR-181 tree to both an existing ACS and a new USP Controller. For an ISP with millions of deployed CWMP devices, this is what makes USP adoption a gradual migration rather than a fleet-wide replacement.

## Recap

- USP (TR-369) is the Broadband Forum's actual designated successor to CWMP, not a speculative future protocol.
- The data model doesn't change — TR-181 Issue 2 explicitly serves both CWMP Endpoints and USP Agents with the same parameter tree.
- ACS/CPE becomes Controller/Agent, and USP explicitly supports multiple Controllers managing one Agent at once — a real architectural shift from CWMP's single-management-relationship model.
- USP separates messages from transport via the MTP layer — WebSockets or MQTT in practice, STOMP for message-queue integration, UDS for a same-device Controller — instead of CWMP's fixed SOAP-over-HTTP(S). CoAP was an early MTP, deprecated in USP 1.2 and obsoleted in 1.3.
- MQTT's persistent connection makes CWMP's Connection Request/STUN NAT workaround unnecessary — the Agent is always reachable because it's always connected.
- CWMP's ad hoc special RPCs (`Reboot`, `Download`, ...) become a single uniform `Operate` verb against command paths in the data model.
- Shared data models let a device run as both a CWMP Endpoint and a USP Agent during migration — adoption doesn't require a hard cutover.

Multiple Controllers is the model — but how does an Agent find any of them in the first place, and what stops them from stepping on each other once it has? See [TR-369 Explained: Controller Discovery and Trust]({{< ref "/posts/2026-08-04-tr369-explained-controller-discovery-trust" >}}) for the DHCP, DNS-SD, and mDNS discovery mechanisms, plus the Role/Permission model that keeps multiple Controllers safely scoped.

[1]: https://usp.technology/specification/
