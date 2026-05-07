---
title: Secure Remote Access with Unifi Identity
description: Use Unifi Identity to set up secure remote access to your home network, managing who can connect and from where.
date: 2026-06-29
draft: true
categories:
  - Networking
  - Security
tags:
  - unifi
  - identity
cover: cover.svg
---

Unifi Identity is the replacement for Teleport — Ubiquiti's older one-shot VPN invite system. Instead of generating a 24-hour link and hoping the recipient connects before it expires, Identity gives you a persistent user management platform: invite people once, configure which services they can reach, enforce MFA, and revoke access any time. For a homelab with a handful of trusted users, it's the cleanest way to hand out secure remote access without running your own VPN server.

## What Unifi Identity Provides

At its core, Identity is a zero-trust access layer on top of your existing UniFi gateway. Each user gets an account that authenticates with a username, password, and optional MFA. Once authenticated, that account unlocks specific services — a WireGuard-based VPN back to your home network and automatic WiFi authentication when on-site.

The free tier covers everything a homelab needs: multiple users, One-Click VPN, One-Click WiFi, and MFA. The paid Enterprise tier ($4.50/user/month) adds SSO against Azure AD or Google Workspace and SCIM provisioning, which is overkill for home use.

## Requirements

- A **UniFi Console** running **UniFi OS 3.2.5+** (any Dream Machine, Dream Wall, NVR, or Cloud Gateways+)
- **UniFi Endpoint** app on iOS, Android, or desktop

## Enabling Unifi Identity

Open **UniFi Site Manager** (`unifi.ui.com`), select your console, then go to **Settings → Identity**. Toggle **Enable UniFi Identity** on. The console provisions the Identity service in the background — this takes about a minute.

Once enabled, a new **Users** section appears in the Identity settings. Your admin account is listed here automatically.

## Inviting Users

Go to **Settings → Identity → Users → Invite User**. Enter the recipient's email address, optionally set an expiry for the invite link (default 30 days), and send. The user receives an email with a link to activate their Endpoint app.

On their device, they open the invite link, install **UniFi Endpoint**, and complete the activation wizard. After that, their account is permanent — no re-inviting when the link expires, unlike Teleport.

To remove access, go to **Users**, find the account, and delete it. The Endpoint app on their device loses access immediately.

## Configuring One-Click VPN

One-Click VPN creates a WireGuard tunnel from the user's device back to your UniFi gateway. To enable it:

1. In Site Manager, go to **Settings → UniFi Consoles**
2. Select your console
3. Under **One-Click VPN**, click **Add Service**
4. Choose the network the VPN should land users on (your main LAN or a dedicated VLAN)
5. Save

Users open the Endpoint app, tap **VPN**, and connect — no server address, no pre-shared key, no certificate to manage. The tunnel uses WireGuard under the hood, so performance is solid.

**Split tunneling** is on by default: only traffic destined for your home network goes through the tunnel. General internet traffic continues to use the user's local connection. You can change this to full-tunnel if you want all traffic routed through your gateway.

## Configuring One-Click WiFi

When a user with Endpoint on their phone walks into your home, they can connect to WiFi without typing a password. To enable it:

1. Go to **Settings → UniFi Consoles → [your console] → One-Click WiFi**
2. Click **Add Service**
3. Select the SSID to associate with Identity authentication
4. Save

Users tap **WiFi** in the Endpoint app and the phone associates automatically. The authentication is identity-based rather than a pre-shared key, so you can revoke a user's WiFi access without changing the password for everyone else.

## Enforcing MFA

Go to **Settings → Identity → Security Policy**. Toggle **Require MFA** on. Users will be prompted to set up an authenticator app (TOTP) the next time they authenticate.

You can also set a **re-authentication interval** — for example, require users to re-authenticate every 7 days. This is useful if you want to ensure a lost device doesn't silently retain access indefinitely.

Supported MFA methods on the free tier: TOTP authenticator apps (Google Authenticator, Authy, 1Password, etc.).

## Teleport vs Identity

If you currently use Teleport and are wondering whether to switch:

| | Teleport | Identity |
|---|---|---|
| User accounts | No — device invites only | Yes — persistent per-user accounts |
| MFA | No | Yes |
| Invite expiry | 24 hours | 30 days (configurable) |
| Revoke access | Delete the invite | Delete the user |
| Multiple users | Awkward | Native |
| WiFi auth | No | Yes |
| App required | No (WireGuard config) | Yes (Endpoint app) |

Teleport is still useful for quick one-off access — hand someone a temporary link, they connect, done. For recurring users (family, a trusted friend), Identity is the better choice.

## Accessing Your Network

Once a user has Endpoint installed and One-Click VPN configured, the workflow is:

1. Open the Endpoint app
2. Tap the VPN tile
3. The tunnel connects within a few seconds
4. All traffic to your home network routes through the tunnel

From the app, users can also see which services they have access to and toggle WiFi auth when switching networks. There's no separate VPN client to manage.

## Monitoring Active Sessions

In Site Manager, go to **Identity → Active Sessions**. This shows every user currently connected, which service they're using (VPN or WiFi), and when they connected. You can terminate any session from here without revoking the account permanently.

For audit purposes, the **Activity Log** under Identity shows the full connection history — who connected, when, from which IP, and for how long.
