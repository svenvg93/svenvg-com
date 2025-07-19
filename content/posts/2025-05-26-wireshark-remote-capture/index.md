---
title: Remote Packet Capture with Wireshark
description: A guide to setting up Wireshark for secure remote packet capture via SSH.
date: 2025-05-26
draft: false
categories:
  - Networking
tags:
  - Wireshark
cover: cover.jpg
---

This guide shows how to set up **Wireshark** to remotely capture traffic via **SSH** using <kbd>tcpdump</kbd>.

## Prerequisites

- **Wireshark installed** on your local machine.
- **SSH access** to the remote host:
  - Regular SSH with <kbd>sudo</kbd> privileges, **or**
- Remote host must have <kbd>tcpdump</kbd> installed.

## Setup Wireshark with Remote SSH Capture

### In Wireshark:

1. Go to: <kbd>Capture</kbd> → <kbd>Options</kbd> → <kbd>Manage Interfaces</kbd>
2. Click on the options icon next **SSH Remote Capture**
3. Set the interface details:
   - **Remote SSH Server Address:** <kbd>ip-address of the server</kbd>
   - **Remote SSH Server port:** <kbd>22</kbd>
4. In the **Authentication** tab fill in 
   - **Remote SSH Server Username**
   - **Remote SSH Server Password**
5. In the **Capture** tab specify the **Remote Capture Command**. For example:

    ```bash
    sudo /usr/sbin/tcpdump -U -i eth0 -w - not port 22
    ```

    This captures traffic from <kbd>eth0</kbd> while excluding SSH (port 22).

    **Tip:** Exclude additional ports like Tailscale (41641) or WireGuard (51820) if they're in use, for cleaner results.
    
6. Save and **Start** the capture.

## Notes

- Replace <kbd>eth0</kbd> with the correct physical interface.

You're now ready to securely and cleanly capture packets from a remote system using Wireshark — even with Tailscale!
