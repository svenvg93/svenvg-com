---
title: "TR-369 Explained: Messages vs CWMP's RPCs"
description: The USP overview post mentioned that CWMP's RPCs become a smaller, more uniform set of USP messages — this post shows exactly what that looks like, with the actual message shapes for Get, Set, and error reporting side by side with their CWMP equivalents.
date: 2026-10-06
draft: false
categories:
  - Networking
tags:
  - tr-369
  - cwmp
  - usp
  - isp
---

The [RPCs and data model post]({{< ref "/posts/2026-09-01-tr069-explained-rpcs-data-model" >}}) walked through CWMP's SOAP envelope and its RPC set. The [USP overview post]({{< ref "/posts/2026-09-15-tr369-explained-what-changes" >}}) mentioned in passing that USP collapses those RPCs into a smaller, more uniform set of messages. This post puts them side by side — the actual message shapes, not just the naming change.

One note before diving in: USP normally encodes messages as binary Protocol Buffers, not human-readable text. The JSON shown below is the same structure in the readable form the Broadband Forum's own [message documentation][1] and [conformance tests][2] use — it's not the literal bytes on the wire, the way the CWMP SOAP/XML in the earlier posts genuinely was.

## The Envelope: SOAP vs Record + Msg

CWMP has one layer: the SOAP envelope carried directly over HTTP(S) is both the transport framing and the message. USP splits this into two:

- A **Record** — the transport-facing outer layer: `version`, `to_id` and `from_id` (Endpoint Identifiers — a Record whose `to_id` doesn't match is discarded outright), and `payload_security` (`PLAINTEXT` or `TLS12`, describing whether the payload inside is itself protected independently of whatever the MTP connection already provides).
- A **Msg** — carried as the Record's payload: a `header` (`msg_id` for correlating requests with responses and catching duplicates, `msg_type` naming the operation) and a `body` (`request`, `response`, or `error`).

CWMP's `cwmp:ID` SOAP header does the same correlation job as `msg_id`, but without the separate transport-facing envelope around it — CWMP doesn't need one, since a SOAP session is already scoped to a single authenticated CPE/ACS pair. USP's Record layer exists because a single Agent might be addressed by several different Controllers, each needing their own Records routed correctly.

![CWMP's single SOAP envelope vs USP's two-layer Record wrapping a Msg](record-msg-layering.svg "CWMP's single SOAP envelope vs USP's two-layer Record wrapping a Msg")

## Get vs GetParameterValues

```json {filename="USP Get request"}
{
  "header": { "msg_id": "1001", "msg_type": "GET" },
  "body": {
    "request": {
      "get": { "param_paths": ["Device.WiFi.SSID.1.SSID"] }
    }
  }
}
```

```json {filename="USP GetResp"}
{
  "header": { "msg_id": "1001", "msg_type": "GET_RESP" },
  "body": {
    "response": {
      "get_resp": {
        "req_path_results": [{
          "requested_path": "Device.WiFi.SSID.1.SSID",
          "resolved_path_results": [{
            "resolved_path": "Device.WiFi.SSID.1.SSID",
            "result_params": [{ "key": "SSID", "value": "MyHomeNetwork" }]
          }]
        }]
      }
    }
  }
}
```

Structurally this is doing the same job as `GetParameterValues`/`GetParameterValuesResponse` from the RPCs post — but notice `param_paths` isn't restricted to leaf parameters. A `Get` against an *object* path (`Device.WiFi.SSID.` rather than a specific instance's `SSID` parameter) resolves to every matching instance and its children in one call. That's most of what CWMP needed `GetParameterNames` for, folded into the same message used for reading values, rather than kept as a separate discovery RPC.

## Set vs SetParameterValues

```json {filename="USP Set request"}
{
  "header": { "msg_id": "1002", "msg_type": "SET" },
  "body": {
    "request": {
      "set": {
        "allow_partial": true,
        "update_objs": [{
          "obj_path": "Device.WiFi.SSID.1.",
          "param_settings": [{ "param": "SSID", "value": "MyHomeNetwork-5G" }]
        }]
      }
    }
  }
}
```

The interesting field here is `allow_partial`. CWMP's `SetParameterValues`, covered in the RPCs post, is always all-or-nothing — one bad parameter fails the entire call. USP's `Set` makes that a choice: `allow_partial: false` keeps CWMP's atomic behavior, but `allow_partial: true` lets the Agent apply whatever parameters it can and report failures only for the ones that didn't take. USP added a strictness dial CWMP never had at all.

## Error Reporting: Fault vs OperationFailure

```json {filename="USP SetResp — failure"}
{
  "header": { "msg_id": "1002", "msg_type": "SET_RESP" },
  "body": {
    "response": {
      "set_resp": {
        "updated_obj_results": [{
          "requested_path": "Device.WiFi.SSID.1.",
          "oper_status": {
            "oper_failure": {
              "err_code": 7012,
              "err_msg": "Invalid parameter value",
              "param_errs": [{
                "param": "SSID",
                "err_code": 7012,
                "err_msg": "Value exceeds maximum length"
              }]
            }
          }
        }]
      }
    }
  }
}
```

Line this up against the [`SetParameterValuesFault` example]({{< ref "/posts/2026-09-01-tr069-explained-rpcs-data-model" >}}) from the RPCs post and the shape is nearly identical: a top-level failure code, plus a `param_errs` list naming exactly which parameter caused it and why — the same problem (atomic writes need per-parameter blame) solved the same way, just wearing USP's field names instead of CWMP's `SetParameterValuesFault`/`FaultCode`/`FaultString`.

## The Ad Hoc RPCs Collapse into Operate

CWMP has no single mechanism for "do a thing" — `Reboot`, `FactoryReset`, `Download`, and `Upload` are each their own SOAP RPC, defined independently. USP has exactly one message for invoking any of them: **`Operate`**, called against a command path in the data model — `Device.Reboot()` instead of a `Reboot` RPC, `Device.DeviceInfo.FirmwareImage.1.Download()` instead of a `Download` RPC. Whatever action-shaped capability a device exposes, it's invoked the same way, rather than each one needing its own message definition.

![CWMP's RPC set mapped to USP messages — Get and Set fold in their discovery/strictness siblings, and four independent one-off RPCs collapse into a single Operate](rpc-message-mapping.svg "CWMP's RPC set mapped to USP messages — Get and Set fold in their discovery/strictness siblings, and four independent one-off RPCs collapse into a single Operate")

## Quick Reference

| CWMP RPC | USP Message | Notes |
|----------|-------------|-------|
| `GetParameterValues` | `Get` | Object-path `Get` also covers most `GetParameterNames` discovery use cases |
| `GetParameterNames` | *(folded into `Get`)* | A separate `GetSupportedDM` message exists for schema-level "what could exist," a different question |
| `SetParameterValues` | `Set` | Adds `allow_partial` — CWMP has no equivalent, it's always atomic |
| `AddObject` | `Add` | |
| `DeleteObject` | `Delete` | |
| `Reboot` / `FactoryReset` / `Download` / `Upload` | `Operate` | Four separate RPCs collapse into one generic command-invocation message |
| SOAP `Fault` | `Error` response / `oper_failure` + `param_errs` | Same shape — top-level code plus per-parameter detail |

Notification is deliberately missing from this table — CWMP's active/passive parameter attributes and USP's `Notify` message plus `Subscription` objects work differently enough to need their own comparison, next.

## Recap

- CWMP's SOAP envelope is one layer; USP splits transport framing (**Record**: `to_id`/`from_id`/`payload_security`) from the operation itself (**Msg**: `header` + `body`) — because one Agent may need to route Records to and from several different Controllers.
- `Get` subsumes most of what `GetParameterValues` *and* `GetParameterNames` did in CWMP, since a `Get` against an object path resolves every matching instance.
- `Set` adds `allow_partial`, a strictness choice CWMP's always-atomic `SetParameterValues` never offered.
- Error reporting keeps the same shape as CWMP's `SetParameterValuesFault` — a top-level failure code plus a per-parameter `param_errs` list — just with USP's own field names.
- CWMP's four independent one-off RPCs (`Reboot`, `FactoryReset`, `Download`, `Upload`) all become a single `Operate` message invoked against a command path in the data model.

See [TR-369 Explained: Subscriptions and the Notify Message]({{< ref "/posts/2026-10-13-tr369-explained-notify-subscriptions" >}}) for the notification side left out of this table.

[1]: https://tr369.org/understanding-usp-messages/
[2]: https://usp-test.broadband-forum.org/
