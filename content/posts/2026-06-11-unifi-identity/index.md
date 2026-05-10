---
title: "UniFi Identity: Zero-Trust Access for Your Homelab"
description: Use UniFi Identity to set up secure remote access to your home network, managing who can connect and from where.
date: 2026-06-11
draft: true
categories:
  - Networking
  - Security
tags:
  - unifi
  - identity
cover: cover.svg
---

UniFi Identity gives you a persistent user management platform: invite people once, configure which services they can reach, and revoke access any time. For a homelab with a handful of trusted users, it's the cleanest way to hand out secure remote access without running your own VPN server.

> **Note:** This post is based on UniFi Network Application version 10.3.58.

## What UniFi Identity Provides

At its core, Identity is a zero-trust access layer on top of your existing UniFi gateway. Each user gets an account that authenticates with a username, password, and optional MFA. Once authenticated, that account unlocks specific services — a WireGuard-based VPN back to your home network and automatic WiFi authentication when on-site.

The free tier covers everything a homelab needs: multiple users, One-Click VPN, One-Click WiFi, and MFA. The paid Enterprise tier ($4.50/user/month) adds SSO against Azure AD or Google Workspace and SCIM provisioning, which is overkill for home use.

## Requirements

- A **UniFi Console** (any UniFi Dream Machine, or UniFi Cloud Gateway)
- **UniFi Endpoint** app on iOS, Android, or desktop

## Enabling UniFi Identity

Open **UniFi Site Manager** (`unifi.ui.com`), select your console, then go to **Settings → Identity** and turn on **Enable UniFi Identity**. The console provisions the Identity service in the background — this takes about a minute.

Once enabled, a new **Identity Settings** section appears in the UniFi Console. It will prompt you to send invite links to any users already set up on the console. You can also configure the expiration duration for invite links here.

## Changing VPN Settings

### Split Tunneling vs All Traffic

On the **Identity Settings** page, click **Service Settings** to choose whether all traffic is sent over the VPN or only traffic destined for your defined subnets.

### IP Ranges

Under **Settings → VPN**, you can edit the settings for the **One-Click VPN**.

Use **Use Alternate Address for Client** to specify a custom IP address or DNS name that clients connect to — for example, a Dynamic DNS name like `vpn.example.com`. This way clients use the DNS name instead of your public IP address, which is useful if your ISP assigns a dynamic IP.

In the **Advanced** section, you can define which IP ranges are assigned to VPN clients.

## Inviting Users

Go to **People → Create New → Create new User**, enter the recipient's email address, and send. The user receives an email with a link to activate their Endpoint app.

On their device, they open the invite link, install **UniFi Endpoint**, and complete the activation wizard. After that, their account is permanent — the link expiry no longer matters.

To remove access, go to **Users**, find the account, and delete it. The Endpoint app on their device loses access immediately.

## Accessing Your Network

Once a user has Endpoint installed and One-Click VPN configured, the workflow is:

1. Open the Endpoint app
2. Tap the VPN tile
3. The tunnel connects within a few seconds
4. All traffic to your home network routes through the tunnel

From the app, users can also see which services they have access to and toggle WiFi auth when switching networks. There's no separate VPN client to manage.

## Monitoring Active Sessions

In Site Manager, go to **Client Devices** and filter by **Identity Users**. This shows every Identity user currently connected, which service they're using (VPN or WiFi), and when they connected.

For audit purposes, go to **Log → VPN** to see the full connection history — who connected, when, from which IP, and for how long.

## Restricting Network and VLAN Access

By default, a VPN user can reach every subnet behind your gateway. If you run separate VLANs — for example, a trusted network and an IoT network — you probably don't want VPN users hitting IoT devices.

You control this through firewall rules in **Settings → Policy Engine → Zones**. Each VLAN you create in UniFi can be assigned to a zone, so instead of specifying IP ranges you just reference zones directly. Create a rule from the **VPN** zone to the **Internal** zone that drops traffic to any zone you want to block — for example, a dedicated IoT zone.

Add one rule per zone you want to restrict, and order them above any broader allow rules. Users will still reach the zones you haven't blocked, so you can whitelist-by-default or blacklist-by-default depending on your preference.

## Conclusion

UniFi Identity removes the friction of sharing home network access. There's no VPN server to maintain, no certificates to distribute, and no shared keys to rotate — each user gets their own account that you can revoke instantly. Paired with firewall rules to scope which VLANs they can reach, it's a solid zero-trust access layer for a homelab without the complexity of a full enterprise solution.
