---
title: Optimize Latency with MikroTik Queueing
description: Reduce lag and improve network performance for a smoother online experience
date: 2025-07-14
draft: true
categories:
  - Networking
  - Router
tags:
  - mikrotik
  - firewall
cover: cover.jpg
---

Few things are more frustrating than sudden latency spikes during online gaming—especially when it costs you the match. One effective way to prevent this is by configuring queueing on your router. Queueing helps ensure a small amount of bandwidth is always available and prevents packet bursts that can cause those disruptive lag spikes.

## What is Queueing?

Queueing enforces traffic shaping and Active Queue Management (AQM), such as FQ-CoDel, which prioritizes latency-sensitive packets and prevents bufferbloat by smoothing out traffic bursts and maintaining low queue occupancy under load. 

Unfortunately, queueing isn’t available on all routers or modems. In this post, we’ll use the same MikroTik router I configured in this [earlier post](/posts/setup-mikrotik). 

## What are we going to configure?

To optimize latency under high load, we’ll implement a queueing system using MikroTik’s mangle and queue tree features. This setup ensures consistent traffic prioritization and bandwidth shaping regardless of interface.

- Define mangle rules to mark upload and download traffic at the packet level
- Implement FQ-CoDel as the active queue discipline for Active Queue Management (AQM)
- Use parent=global in the queue tree to apply shaping globally across interfaces
- Set max-limit to ~900 Mbps to prevent bufferbloat during saturation
- Ensure all routed traffic flows through the queue system for consistent latency control

## Mangle Rules to Mark Upload & Download

The first step is to classify traffic by marking packets as either upload or download. This is done using mangle rules in the forward chain. These marks will later be used in the queue tree to apply shaping and prioritization.

```bash
/ip firewall mangle
add chain=forward action=mark-packet new-packet-mark=download passthrough=yes out-interface=bridge1 comment="Mark download traffic"
add chain=forward action=mark-packet new-packet-mark=upload passthrough=yes out-interface=internet comment="Mark upload traffic"
```

> Replace <kbd>bridge1</kbd> with your LAN interface and <kbd>internet</kbd> with your WAN interface name as appropriate for your setup.


### Create FQ-CoDel Queue Types*

Next, we define custom queue types using **FQ-CoDel** (Fair Queuing Controlled Delay), a modern Active Queue Management (AQM) algorithm designed to reduce bufferbloat and maintain low latency under load.

```bash
/queue type
add name=fq_codel_download kind=fq-codel fq-codel-target=3ms
add name=fq_codel_upload kind=fq-codel fq-codel-target=3ms
```
> <kbd>fq-codel-target=3ms</kbd> defines the maximum acceptable queuing delay. You can tune this value based on your latency goals.

## Queue Tree (FQ-CoDel with Marks)

With packet marks and FQ-CoDel queue types in place, we now configure the queue tree to apply bandwidth shaping. Using parent=global ensures that traffic is queued regardless of the physical interface, which is essential for consistent shaping across complex routing or VLAN setups.

```bash
/queue tree
add name=queue-download parent=global packet-mark=download queue=fq_codel_download limit-at=850M max-limit=900M
add name=queue-upload parent=global packet-mark=upload queue=fq_codel_upload limit-at=850M max-limit=900M
```

**Explanation**:
- <kbd>packet-mark</kbd>: Links to the mangle rules defined earlier.
- <kbd>queue</kbd>: Specifies the FQ-CoDel type to enforce low-latency AQM.
- <kbd>limit-at</kbd>: Guaranteed minimum bandwidth.
-	<kbd>max-limit</kbd>: Absolute ceiling; used to slightly undersubscribe your WAN link (to avoid ISP-side buffering).

> Tune <kbd>max-limit</kbd> down slightly (e.g., 880M) if latency spikes persist during peak usage.


## Disbale HW 

To ensure that traffic passes through the CPU (and thus through mangle, firewall, and queue processing), hardware offloading must be disabled on all bridge ports. This is especially important when using <kbd>parent=global</kbd> in the queue tree.

```bash
/interface bridge port            
set [find] hw=no
```

> This disables the H (hardware offload) flag on all bridge ports, forcing traffic to be processed in software where queues and firewall rules are applied.

> On high-throughput setups, this may increase CPU usage. Monitor with <kbd>/tool</kbd> profile during load.
{: .prompt-warning }

## Verifying Queue Operation

Once everything is configured, you can verify that traffic is being properly classified and queued by checking queue statistics in real time:

```bash
/queue tree print stats interval=1
```

```bash
Flags: X - disabled, I - invalid 
 0   name="queue-download" parent=global packet-mark=download rate=52320 packet-rate=45 queued-bytes=0 queued-packets=0 bytes=28192979120 packets=25350209 dropped=0 
 1   name="queue-upload" parent=global packet-mark=upload rate=338232 packet-rate=72 queued-bytes=0 queued-packets=0 bytes=26698400069 packets=23484974 dropped=0 
 ```

**What to Look For**:
- <kbd>rate</kbd> and <kbd>packet-rate</kbd> should increase during active traffic.
- <kbd>queued-bytes</kbd> and <kbd>queued-packets</kbd> should stay low — this indicates FQ-CoDel is doing its job, avoiding large buffer build-up.
- <kbd>dropped=0</kbd> is ideal, but occasional drops are normal under sustained saturation.

If you see zero values consistently during active use, double-check your mangle rules, interface names, and hardware offload settings.
