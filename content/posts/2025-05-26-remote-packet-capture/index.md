---
title: Remote Packet Capture with Wireshark
description: Capture network packets remotely using Wireshark over SSH — no local install needed on the target host, ideal for homelab troubleshooting.
date: 2025-05-26
draft: false
categories:
  - Networking
tags:
  - wireshark
  - ssh
  - tcpdump
cover: cover.jpg
---

This guide shows how to set up **Wireshark** to remotely capture traffic via **SSH** using `tcpdump`.

## Prerequisites

- **Wireshark** installed on your local machine
- **SSH access** to the remote host
- **tcpdump** installed on the remote host

## Setup Remote Host

Wireshark runs `tcpdump` non-interactively over SSH, so `sudo` will fail if it requires a password prompt. Grant `tcpdump` the capture capability directly on the remote host instead:

```bash
sudo setcap cap_net_raw+ep $(which tcpdump)
```

## Setup Wireshark

1. Go to: `Capture` → `Options` → `Manage Interfaces`
2. Click the gear icon next to **SSH Remote Capture**
3. Set the interface details:
   - **Remote SSH Server Address:** IP address of the remote host
   - **Remote SSH Server Port:** `22`
4. In the **Authentication** tab, fill in:
   - **Remote SSH Server Username**
   - **Remote SSH Server Password** or **Path to SSH Private Key** (e.g. `~/.ssh/id_rsa`)
5. In the **Capture** tab, configure what to capture:
   - **Remote Interface:** the network interface on the remote host (e.g. `eth0`)
   - **Remote Capture Filter:** a BPF filter to limit captured traffic (e.g. `not port 22`)
6. Save and **Start** the capture.
