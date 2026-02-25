---
title: Remote Packet Capture with Wireshark
description: A guide to setting up Wireshark for secure remote packet capture via SSH.
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

- **Wireshark installed** on your local machine.
- **SSH access** to the remote host:
  - Regular SSH with `sudo` privileges, **or**
- Remote host must have `tcpdump` installed.

## Setup Wireshark with Remote SSH Capture

### In Wireshark:

1. Go to: `Capture` → `Options` → `Manage Interfaces`
2. Click on the options icon next **SSH Remote Capture**
3. Set the interface details:
   - **Remote SSH Server Address:** `ip-address of the server`
   - **Remote SSH Server port:** `22`
4. In the **Authentication** tab fill in 
   - **Remote SSH Server Username**
   - **Remote SSH Server Password**
5. In the **Capture** tab specify the **Remote Capture Command**. For example:

    ```bash
    sudo /usr/sbin/tcpdump -U -i eth0 -w - not port 22
    ```

    This captures traffic from `eth0` while excluding SSH (port 22).

    **Tip** To exclude more ports, simply add filters like `not port 41641`. Repeat this for each port you want to omit from the capture.
    
6. Save and **Start** the capture.

## Notes

- Replace `eth0` with the correct physical interface.

You're now ready to securely and cleanly capture packets from a remote system using Wireshark — even with Tailscale!
