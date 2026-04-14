---
title: "Smokeping Essentials: The Right Targets"
description: Which protocols to use for internet monitoring, how to find reliable ISP targets, and how to verify them with MTR.
date: 2026-04-09
draft: false
categories:
  - Monitoring
  - Networking
tags:
  - smokeping
  - mtr
cover: cover.jpg
series:
  - Smokeping Essentials
series_order: 1
---

Good internet monitoring comes down to two choices: the right protocol and the right target. A bad target — one that rate-limits probes or sits outside your ISP's network — produces data that reflects the target's behaviour, not your connection. This post covers both.

## Protocols

| Protocol | What it measures | Best for | Watch out for |
|----------|-----------------|----------|---------------|
| ICMP | Round-trip latency, packet loss | Baseline connectivity, packet loss trends | Can be deprioritized or blocked by routers under load |
| DNS | Resolver response time | Detecting DNS outages, ISP resolver issues | Caching can mask latency; slow DNS ≠ slow internet |
| TCP | Connection establishment time to a specific port | Realistic reachability check without app overhead | Requires an open port on the target; firewalls may interfere |

## Targets

### ICMP

Use your **ISP's default gateway** — the first hop out of your router. Always responds, always local. Find it with `traceroute`.

Avoid using intermediate traceroute hops as targets. Routers deprioritize ICMP to their own interfaces by design, so a hop showing packet loss may be forwarding your traffic just fine. It tells you nothing about your connection to the actual endpoint.

### DNS

Monitor two resolvers and compare them:

- **Your ISP's assigned resolver** — handed out via DHCP. Find it with `cat /etc/resolv.conf` on Linux/Mac or `ipconfig /all` on Windows. Slow response points to a DNS issue on your ISP's side.
- **A secondary public resolver** (`9.9.9.9` from Quad9) — if your ISP resolver is slow but this is fine, the problem is your ISP's DNS, not your connection.

### TCP

CDN edge nodes are the best option — they have port 80/443 open, stable IPs, and are anchored close to your region. Covered in depth in the [next post]({{< ref "/posts/2026-04-16-smokeping-essentials-cdn-targets" >}}).

## Multi-Target Strategy

Monitor at multiple network distances to isolate where a problem is:

1. **Your CPE/router** (your modem/router) — problem inside your home network
2. **ISP first hop** — problem on your local loop (DSL line, cable, fibre ONT)
3. **CDN edge** — problem between your ISP and the wider internet

## Discovering Your ISP's Infrastructure

Run a traceroute to any external address — the first couple of hops typically belong to your ISP:

```bash
traceroute 1.1.1.1
```

Use [bgp.tools][1] or [ipinfo.io][2] to confirm which ASN an IP belongs to — both are free tools for looking up which network owns an IP address. Note that ISPs sometimes use private ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`) or Carrier-Grade NAT space (`100.64.0.0/10`) on their infrastructure — hops in these ranges are still inside your ISP's network.

Once you have a candidate, verify it with MTR before adding it to your monitoring setup. MTR combines traceroute and ping into a single tool, continuously updating per-hop latency and packet loss — making it easy to confirm a target responds consistently:

```bash
mtr --aslookup --report-cycles 60 --report-wide <target-ip>
```

Example:

```bash
Start: 2026-04-13T20:09:02+0200
HOST: un100p                                    Loss%   Snt   Last   Avg  Best  Wrst StDev
  1. AS???    home                               0.0%    60    0.8   0.9   0.7   1.2   0.1
  2. AS50266  1-96-254-92.ftth.glasoperator.nl   0.0%    60    3.1   3.1   2.3   4.1   0.3
  3. AS???    10.227.161.253                     0.0%    60    4.6   4.1   3.3   4.6   0.3
  4. AS???    10.226.11.40                       0.0%    60    4.3   4.2   3.6   5.0   0.3
  5. AS13335  141.101.65.28                      6.7%    60    7.8  70.1   5.2 165.1  51.0
  6. AS???    ams-ix.as13335.net                 0.0%    60   29.9  12.6   4.4  31.8   8.0
  7. AS13335  141.101.65.28                      0.0%    60    5.2   7.6   4.5  31.1   5.0
  8. AS13335  141.101.65.14                      0.0%    60    8.5   9.0   4.7  37.3   5.9
  9. AS13335  one.one.one.one                    0.0%    60    4.7   4.7   4.1   6.0   0.3
```

In this example, `1.1.1.1` is used as the destination only to reveal the path — not as a monitoring target. The good ICMP candidates are hops 3 and 4 (private IPs inside the ISP's network) and hop 2 (the FTTH gateway with a resolvable hostname). Hop 5 shows 6.7% packet loss — this is rate-limiting on a Cloudflare router interface, not real loss on the path, which is exactly the intermediate hop problem described above. Hop 9 reaches the destination with 0% loss, confirming the connection itself is fine.

[1]: https://bgp.tools
[2]: https://ipinfo.io
