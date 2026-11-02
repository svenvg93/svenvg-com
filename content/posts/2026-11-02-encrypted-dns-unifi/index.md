---
title: "How to Set Up Encrypted DNS on UniFi — and Make Every Device Use It"
description: A step-by-step guide to UniFi's Encrypted DNS. Encrypt the gateway's upstream DNS, pick a resolver that blocks malicious domains, and redirect or block devices that try to go around it — with a test for every step.
date: 2026-11-02
draft: false
categories:
  - Networking
  - Security
tags:
  - dns
  - unifi
---

The [Encrypted DNS]({{< ref "/posts/2026-05-21-encrypted-dns" >}}) post ended on a recommendation: for a home network, encrypt DNS at the resolver level. One place to configure, every device covered, and local DNS keeps working. On a UniFi network, that resolver is the gateway, and UniFi has a built-in setting for it.

This guide sets it up end to end:

1. Check what your gateway uses today
2. Choose a resolver — for privacy only, or privacy plus threat blocking
3. Turn on Encrypted DNS
4. Verify it
5. Redirect devices with hard-coded DNS to the gateway
6. Block encrypted DNS that bypasses the gateway

**You'll need:** a UniFi gateway on Network 9 or later, admin access to the UniFi Network app, and a computer on the LAN with `dig` (built into macOS and most Linux distributions). The examples use `192.168.1.1` as the gateway address — replace it with yours.

## How It Works

UniFi's **Encrypted DNS** (called **DNS Shield** before Network 9) changes one hop of every lookup: the gateway's connection to its upstream resolver, which switches from plain DNS to DoH (DNS over HTTPS).

![DNS lookup path with UniFi Encrypted DNS — only the gateway-to-resolver hop is encrypted (DoH on 443); client-to-gateway and resolver-to-authoritative stay plain DNS](dns-hops.svg "DNS lookup path with UniFi Encrypted DNS — only the gateway-to-resolver hop is encrypted (DoH on 443); client-to-gateway and resolver-to-authoritative stay plain DNS")

Clients keep sending plain DNS to the gateway on port 53, so nothing changes on your devices, and local DNS records you've defined on the gateway keep working. Hop 1 stays on your own network. Hop 3 is outside your control — resolvers talk to authoritative servers in plain DNS. Hop 2 is the one that crosses your ISP, and that's the one this fixes.

## Check What Your Gateway Uses Today

Before changing anything, record a baseline. Akamai runs a domain that reports the address of whichever resolver asked it:

```bash
dig +short @192.168.1.1 TXT whoami.ds.akahelp.net
```

Look at the `"ns"` line. On a default setup, it's your ISP's resolver, or whatever DNS servers your WAN connection is configured with. Keep the output — you'll compare against it in step 4.

## Choose a Resolver

Encryption decides who can *see* your DNS. The resolver decides what it will *answer*. Some providers run filtering variants that refuse to resolve domains on their threat feeds — malware, phishing, command-and-control servers. A device that can't resolve a malicious domain can't connect to it.

| Resolver | Blocks | Blocked domains return |
|---|---|---|
| Cloudflare 1.1.1.1 | Nothing | — |
| Cloudflare 1.1.1.2 | Malware | `0.0.0.0` |
| Cloudflare 1.1.1.3 | Malware and adult content | `0.0.0.0` |
| Quad9 9.9.9.9 | Malicious domains | NXDOMAIN |
| Google 8.8.8.8 | Nothing | — |
| NextDNS, AdGuard DNS | Your choice of blocklists | Configurable |

Some things to weigh:

- **Auto doesn't filter.** UniFi's Auto mode uses Cloudflare's and Google's standard resolvers. Fine for privacy, but no blocking.
- **Each provider blocks its own list.** Quad9 and Cloudflare use different threat feeds, so "filtered" means filtered by *that* provider's judgment.
- **Fixed filters have no allowlist.** If Quad9 or Cloudflare blocks something you need, you can't override it. NextDNS and AdGuard DNS let you add your own allow and block entries, and show what was blocked.
- **You're moving trust, not removing it.** Whichever provider you pick sees every domain your network looks up, instead of your ISP.

## Turn On Encrypted DNS

In the UniFi Network app, open **Settings → CyberSecure** and find **Encrypted DNS**. Choose one of:

- **Auto** — Cloudflare and Google, no filtering.
- **A predefined provider** — pick it from the list.
- **Custom** — for anything else. Give it a name and paste the provider's **DNS stamp**: a single `sdns://` string that describes the resolver. NextDNS and AdGuard DNS show yours on their setup pages; Quad9 and Cloudflare stamps are in the DNSCrypt project's public resolver list.

Apply the change. Note that with Encrypted DNS on, the gateway stops using the DNS servers from your WAN settings — the provider you chose here replaces them.

## Verify It

Run the baseline query again, a few times:

```bash
dig +short @192.168.1.1 TXT whoami.ds.akahelp.net
```

The `"ns"` address should now belong to your chosen provider. On Auto, you'll see it alternate between Google and Cloudflare addresses. This confirms the upstream changed; seeing the encryption itself would take a packet capture on the WAN side.

If you chose a filtering resolver, test that it blocks. Each provider publishes a test domain:

```bash
dig +short @192.168.1.1 malware.testcategory.com   # Cloudflare 1.1.1.2/1.1.1.3: expect 0.0.0.0
dig @192.168.1.1 isitblocked.org | grep status      # Quad9: expect NXDOMAIN
```

Finally, check that a normal site and one of your local DNS records still resolve.

## Redirect Hard-Coded DNS to the Gateway

Encrypted DNS only covers devices that use the gateway as their resolver, and on a default network any device can ignore it. Try it from your computer:

```bash
dig +short @8.8.8.8 example.com
```

If that returns an answer, a device with a hard-coded resolver — some smart TVs, streaming boxes, IoT devices — is sending plain DNS straight past the gateway: unencrypted, and unfiltered.

The fix is a **destination NAT** rule that catches those queries and answers them from the gateway instead. The device asks `8.8.8.8`, the gateway answers, and the reply is rewritten to look like it came from `8.8.8.8` — so nothing breaks.

### Create the Rule

1. In the UniFi Network app, go to **Settings** and open the **NAT** section (under **Policy Engine** on recent versions).
2. Create a new rule and give it a name you'll recognize later, like `Redirect DNS to gateway`.
3. Set the **Type** to **Destination NAT**.
4. Set the **Interface** to your LAN network. If you have several VLANs, create one rule per network you want covered.
5. Set the **Protocol** to **TCP/UDP**. DNS mostly uses UDP, but falls back to TCP for large answers.
6. Set the **Translated IP address** to the gateway's own address on that network, e.g. `192.168.1.1`. This is where matching queries get sent instead.
7. Leave **Source** on any, and leave the **source port empty**.
8. Under **Destination**, enter the gateway's address and turn on **exclude**, so the rule matches every destination *except* the gateway. Set the **destination port** to `53`.
9. Save the rule.

Step 7 is the easy one to get wrong. A device sends its DNS query *to* port 53, but *from* a random high port like 54123 — so a rule with source port 53 never matches anything, and the redirect silently does nothing.

Step 8's exclude keeps the rule from matching queries that already go to the gateway. There's no loop to worry about: with Encrypted DNS on, the gateway's own upstream traffic goes out as HTTPS, not port 53.

### Test the Rule

Query a resolver your gateway *doesn't* use, and check who really answered:

```bash
dig +short @9.9.9.9 TXT whoami.ds.akahelp.net
```

Without the rule, the `"ns"` line shows a Quad9 address. With it, it shows your gateway's upstream from step 4 instead. Pick a resolver that isn't your own provider for this test — if your gateway uses Google and you query `8.8.8.8`, the answer looks the same either way. And remember the redirect exists when troubleshooting later: `dig @9.9.9.9` from your network no longer reaches Quad9.

The rule covers IPv4. If your network has IPv6 internet access, a device can still reach an outside resolver over IPv6, so add a matching rule for IPv6 as well.

## Step 6: Block Encrypted DNS That Bypasses the Gateway

DoT and DoH can't be redirected that way. Their clients check the resolver's TLS certificate, and the gateway can't present Cloudflare's or Google's, so a redirected connection just fails. Block them instead, with two firewall policies from your **Internal** zone to **External**:

| Policy | Action | Matches |
|---|---|---|
| Reject DoT/DoQ | Reject | TCP and UDP port 853 |
| Reject DoH | Reject | Application: DNS over HTTPS (DoH) |

Use **Reject**, not Block. Block drops the query silently and the device waits for a timeout; Reject refuses immediately, so many devices fall back to the gateway's resolver straight away. These policies don't affect the gateway itself — its own DoH traffic is in the Gateway zone, not Internal.

**Verify:** from your computer, the DoT port should now be refused:

```bash
nc -z -w 3 1.1.1.1 853 && echo "still open" || echo "blocked"
```

The port 853 policy is reliable. The DoH policy can't be: DoH is ordinary HTTPS on port 443, and the gateway recognizes it from metadata like known resolver addresses, so it catches the big public services and misses smaller ones. For browsers, two more levers help:

- **Firefox** skips automatic DoH if the network's resolver returns NXDOMAIN for the canary domain `use-application-dns.net`.
- **Managed browsers** — Chrome, Edge, Firefox — can have DoH turned off by policy.

## What This Doesn't Cover

With all six steps done, almost all DNS on your network goes through the gateway: encrypted on the way out, and filtered if you chose a filtering resolver. A few gaps remain:

- **The hostname still leaks in TLS.** The SNI field in the TLS handshake shows the site name in plain text, unless the site supports ECH.
- **DoH detection is best-effort.** A determined app or piece of malware with its own DoH can still get out.
- **DNS filtering is one layer.** A connection made straight to an IP address never touches DNS — that's what the firewall and [IDS/IPS]({{< ref "/posts/2026-08-21-ids-ips-explained" >}}) are for.
