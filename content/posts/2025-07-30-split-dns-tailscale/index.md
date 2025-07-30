---
title: Configure Split DNS with Tailscale and Local DNS
description: Route Tailscale domains through Tailscale DNS, while keeping local DNS for everything else
date: 2025-07-30
draft: false
categories:
  - networking
tags:
  - linux
  - tailscale
cover: cover.jpg
---

Tailscale is a fantastic tool for securely accessing all your systems and applications remotely.
However, it does come with some trade-offs — especially when it comes to DNS. By default, Tailscale takes over your system’s DNS settings. While non-Tailscale domains are generally forwarded to your local resolver, that behavior depends on Tailscale functioning correctly.

Recently, I ran into an issue where one of my nodes had an expired key and couldn’t connect to the tailnet anymore. As a result, all DNS queries on that system failed, even for unrelated domains.

While this might have been a rare edge case, it made me wonder: Can I configure my system to only use Tailscale’s DNS (100.100.100.100) for .ts.net domains, while keeping my normal DNS resolver for everything else?

The answer is yes — by using systemd-resolved, you can set up true split DNS and direct specific domains like *.ts.net to Tailscale’s DNS while keeping everything else on your local DNS.


## Install systemd-resolved

First, ensure that systemd-resolved is installed and enabled on your system:

```bash
sudo apt update
sudo apt install systemd-resolved
sudo systemctl enable systemd-resolved
sudo systemctl start systemd-resolved
```
Also, make sure /etc/resolv.conf is pointing to the systemd stub resolver:

```bash
sudo ln -sf /run/systemd/resolve/stub-resolv.conf /etc/resolv.conf
```

## Create Tailscale DNS Split Configuration

To configure systemd-resolved to use Tailscale’s DNS server only for .ts.net domains, we’ll create a network configuration file that is applied at boot.

Open the file:

```bash
sudo nano /etc/systemd/network/99-tailscale.network
```

Paste the following:

```bash
[Match]
Name=tailscale0

[Network]
DNS=100.100.100.100
Domains=~ts.net
```
This tells systemd-resolved to use 100.100.100.100 (Tailscale’s MagicDNS) only for `.ts.net` queries on the tailscale0 interface.

Apply the changes by restarting the systemd network daemon:

```bash
sudo systemctl restart systemd-networkd
```

After setting up split DNS with systemd-resolved, you can use the `resolvectl status` command to confirm that your system is routing DNS queries correctly.

In the example below, you can see that:
- The default DNS resolver is your local network DNS (192.168.1.1 on eth0)
- Tailscale’s DNS server (100.100.100.100) is only used for .ts.net domains and associated reverse zones on the tailscale0 interface

```bash {filename="output"}
Global
       Protocols: +LLMNR +mDNS -DNSOverTLS DNSSEC=no/unsupported
resolv.conf mode: uplink

Link 2 (eth0)
    Current Scopes: DNS LLMNR/IPv4 LLMNR/IPv6
         Protocols: +DefaultRoute +LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 192.168.1.1
       DNS Servers: 192.168.1.1
        DNS Domain: home

Link 3 (tailscale0)
    Current Scopes: DNS
         Protocols: -DefaultRoute -LLMNR -mDNS -DNSOverTLS DNSSEC=no/unsupported
Current DNS Server: 100.100.100.100
       DNS Servers: 100.100.100.100
        DNS Domain: tail43c135.ts.net ~0.e.1.a.c.5.1.1.a.7.d.f.ip6.arpa ~100.100.in-addr.arpa ~101.100.in-addr.arpa
                    ~102.100.in-addr.arpa ~103.100.in-addr.arpa ~104.100.in-addr.arpa ~105.100.in-addr.arpa ~106.100.in-addr.arpa
                    ~107.100.in-addr.arpa ~108.100.in-addr.arpa ~109.100.in-addr.arpa ~110.100.in-addr.arpa ~111.100.in-addr.arpa
                    ~112.100.in-addr.arpa ~113.100.in-addr.arpa ~114.100.in-addr.arpa ~115.100.in-addr.arpa ~116.100.in-addr.arpa
                    ~117.100.in-addr.arpa ~118.100.in-addr.arpa ~119.100.in-addr.arpa ~120.100.in-addr.arpa ~121.100.in-addr.arpa
                    ~122.100.in-addr.arpa ~123.100.in-addr.arpa ~124.100.in-addr.arpa ~125.100.in-addr.arpa ~126.100.in-addr.arpa
                    ~127.100.in-addr.arpa ~64.100.in-addr.arpa ~65.100.in-addr.arpa ~66.100.in-addr.arpa ~67.100.in-addr.arpa
                    ~68.100.in-addr.arpa ~69.100.in-addr.arpa ~70.100.in-addr.arpa ~71.100.in-addr.arpa ~72.100.in-addr.arpa
                    ~73.100.in-addr.arpa ~74.100.in-addr.arpa ~75.100.in-addr.arpa ~76.100.in-addr.arpa ~77.100.in-addr.arpa
                    ~78.100.in-addr.arpa ~79.100.in-addr.arpa ~80.100.in-addr.arpa ~81.100.in-addr.arpa ~82.100.in-addr.arpa
                    ~83.100.in-addr.arpa ~84.100.in-addr.arpa ~85.100.in-addr.arpa ~86.100.in-addr.arpa ~87.100.in-addr.arpa
                    ~88.100.in-addr.arpa ~89.100.in-addr.arpa ~90.100.in-addr.arpa ~91.100.in-addr.arpa ~92.100.in-addr.arpa
                    ~93.100.in-addr.arpa ~94.100.in-addr.arpa ~95.100.in-addr.arpa ~96.100.in-addr.arpa ~97.100.in-addr.arpa
                    ~98.100.in-addr.arpa ~99.100.in-addr.arpa ~ts.net

```

The long list of ~100.in-addr.arpa entries is used for reverse DNS (PTR) lookups in Tailscale’s subnet.

## Testing Resolution

Use resolvectl query to check which DNS server is used per domain:

### Query a public domain (uses local DNS):

```bash
resolvectl query google.com
```

```bash {filename="output"}
google.com: 172.217.23.206                     -- link: eth0
            2a00:1450:400e:802::200e           -- link: eth0

-- Information acquired via protocol DNS in 8.3ms.
-- Data is authenticated: no; Data was acquired via local or encrypted transport: no
-- Data from: network
```

### Query a Tailscale domain (uses Tailscale DNS):

```bash
resolvectl query  beszel.tail43c135.ts.net
```

```bash {filename="output"}
beszel.tail43c135.ts.net: 100.80.20.240        -- link: tailscale0

-- Information acquired via protocol DNS in 4.2ms.
-- Data is authenticated: no; Data was acquired via local or encrypted transport: no
-- Data from: network
```
