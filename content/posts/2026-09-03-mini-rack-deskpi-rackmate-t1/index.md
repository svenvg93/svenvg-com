---
title: "Building a Mini Rack with the DeskPi RackMate T1"
description: A build log for a 10-inch, 8U mini rack based on the DeskPi RackMate T1 — planning the layout, assembling the frame, mounting gear on 0.5U and 1U shelves, and sorting power and cooling.
date: 2026-09-03
draft: true
categories:
  - Homelab
tags:
  - homelab
  - mini-rack
  - deskpi
---

A full 19-inch rack is overkill for a home setup that's really just a gateway, a switch, a Pi or two, and a small NAS. A 10-inch mini rack fits the same gear on a desk or shelf without dominating the room. The [DeskPi RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2) is one of the more common options: a die-cast aluminium frame, 8U tall, 10 inches wide, flat-packed, with a whole ecosystem of 0.5U and 1U accessories built around it.

This is a build log for putting one together — what to plan for before ordering, how the frame goes together, and how to mount gear that was never designed for a 10-inch rack.

<!-- TODO(Sven): drop in a hero photo of the finished rack here -->

## What the RackMate T1 Actually Is

- **10-inch rack width.** The mounting rails sit 254 mm apart on centre — narrower than the 19-inch (483 mm) rails on a standard rack. Vertically it still follows the normal standard: 1U = 44.45 mm, so 8U of usable mounting height.
- **8U of space**, open front and back — the base T1 has no door, just translucent acrylic side panels for dust and looks.
- **Die-cast aluminium frame.** It's rigid once assembled and heavier than it looks.
- **Roughly 280 × 200 × 405 mm** overall on the base model (W × D × H). Depth is the number that matters — see below.

There are a few variants (T1, T1 Plus, T1 Light) that differ mainly in depth, panel material, and whether a glass door is included. <!-- TODO(Sven): state exactly which variant you bought, where from, and what you paid -->

## The Depth Trap

The single biggest mistake with a 10-inch rack is assuming your gear fits front-to-back. It's shallow. Usable depth behind the rails is on the order of 180–200 mm, and some of that is eaten by connectors and the bend radius of whatever you plug in.

Before ordering anything, measure the deepest thing you plan to rack — including the power brick if it's an inline type, and cables sticking out the back. A lot of "10-inch rack" builds end up with the switch or NAS mounted on a shelf facing sideways, or sitting on a shelf with the rails purely structural.

<!-- TODO(Sven): list the actual devices going in, with their measured depth, and note which ones fit on the rails vs. which sit on a shelf. Photo of the tape measure moment optional but on-brand. -->

## Planning the Layout

Work out the U budget before assembly — it's much easier to plan on paper than to reshuffle a populated rack.

| U | Item | Mounting |
|---|------|----------|
| 8 | <!-- TODO --> | |
| 7 | | |
| 6 | | |
| 5 | | |
| 4 | | |
| 3 | | |
| 2 | | |
| 1 | | |

A few rules of thumb:

- **Heaviest at the bottom.** A NAS or anything with spinning disks goes in the lowest U so the rack isn't top-heavy on a desk.
- **Leave a gap above anything warm.** Passive cooling in an open frame works, but only if hot air can rise away from the device instead of straight into the next one.
- **Reserve 0.5U or 1U for a patch/cable-management panel** near the top or middle — it's the difference between a tidy build and a bird's nest.
- **Blank the gaps you're not using** if you later add a door or want the airflow to behave predictably.

![Rack elevation — what goes in each U, front view](rack-elevation.svg "DeskPi RackMate T1 rack elevation — final layout by U")

<!-- TODO(Sven): this SVG needs creating in the house dark-diagram style — a simple 8U front elevation with the final device layout labelled. -->

## What's in the Box

The T1 ships flat. <!-- TODO(Sven): confirm against your kit --> expect:

- 4 corner posts (the die-cast aluminium extrusions)
- Top and bottom plates
- 2 acrylic side panels
- A bag of frame screws, plus a bag of M6 (or equivalent) cage-style screws for mounting equipment
- Rubber feet
- A hex key

Count the screws against the manual before you start — it's a DIY kit and a short bag is not unheard of. <!-- TODO(Sven): note if anything was missing or extra -->

## Assembling the Frame

The frame is four posts joined by the top and bottom plates, with the side panels going on last.

1. **Lay out the posts** so the rail hole numbering runs the same way on all four — the mounting holes are asymmetric, and it's easy to build the frame with one rail upside down.
2. **Attach the bottom plate first.** Get all four screws started loose before tightening any of them, so the frame can still square up.
3. **Add the top plate** the same way — loose, then square the frame against a flat edge, then tighten.
4. **Check it's square** by measuring both diagonals across the front opening. If they're equal, the frame is true. Tighten everything down.
5. **Fit the feet**, then stand it up.
6. **Slide the acrylic side panels in last.** Peel the protective film, handle them by the edges, and don't force them — if a panel binds, the frame isn't square.

<!-- TODO(Sven): confirm the exact screw sequence and callouts against the DeskPi manual for your kit, and add a photo or two of the part-built frame. Note assembly time. -->

The whole thing takes about <!-- TODO: X --> minutes with a single hex key.

## Mounting the Gear

Almost nothing in a home setup ships with 10-inch rack ears, so most devices get mounted one of these ways:

- **1U or 0.5U shelf.** The general-purpose option. DeskPi's vented 1U shelf takes a Pi, a small switch, or a mini PC sitting on top, held with cable ties or hook-and-loop. The 0.5U shelf is enough for a single SBC.
- **SBC shelf.** A 1U tray with mounting holes matched to Raspberry Pi / common SBC footprints, so the board bolts down properly instead of floating on a shelf.
- **Mini-ITX shelf.** A 1U shelf for a Mini-ITX board or a small NAS build.
- **Rails, directly.** Only for the handful of 10-inch-native devices — some managed switches and patch panels come with the right ears.
- **Blank panels** for the empty U's.

<!-- TODO(Sven): for each device, say which shelf/accessory it's on and link the product page. Mention the actual part numbers you bought (DP-00xx). -->

## Power

Two approaches:

{{< tabs >}}
{{< tab label="DC PDU (rack-mounted)" >}}
DeskPi's **DC PDU Lite** is a 0.5U unit with 7 channels, front and rear input, and per-channel fuses that auto-recover after an overcurrent trip. It takes a single DC input (up to 24 V / 8 A) and fans it out — handy if your gear is all 5 V / 12 V barrel-jack devices and you want one upstream supply instead of seven wall warts.

Check the voltage of every device first. A PDU that outputs one voltage per rail is no good if you're mixing 5 V and 12 V, unless it has per-channel regulation.
{{< /tab >}}
{{< tab label="Surge strip (simple)" >}}
A short desktop surge strip cable-tied to a rear post, with each device's own adapter plugged in. Less tidy, zero compatibility risk, and nothing new to fail. Perfectly fine for a first build.
{{< /tab >}}
{{< /tabs >}}

<!-- TODO(Sven): say which you went with and why. If DC PDU, list what's on each channel and the upstream supply. -->

Run power up one rear corner and data up the other so they're not bundled together.

## Cooling

An open frame with the side panels on is mostly passive — fine for a gateway, a switch, and a couple of Pis. It stops being fine when you add anything that runs hot continuously (a NAS under load, a mini PC doing transcoding).

Options if you need airflow:

- **A 1U or 2U fan panel** (DeskPi sells a 1U quad and a 2U dual) mounted above the warm device, pulling air up and out.
- **A single USB or Noctua fan** zip-tied to a post, aimed across the hot spot. Quieter, less tidy.
- **Just leave a 1U gap** above anything warm and skip active cooling entirely — often enough at this scale.

<!-- TODO(Sven): note idle vs. load temps of the warmest device before/after whatever cooling you added. -->

## Cable Management

- A **0.5U cable-management panel with D-rings** near the middle of the rack gives every patch cable a defined path.
- Use short cables. A 2 m patch lead in a 280 mm-wide rack is 1.7 m of loop to hide. DeskPi and others sell 0.2 m and 0.5 m CAT6 leads sized for this.
- Velcro, not zip ties, on anything you'll re-patch.
- Label both ends of every cable now, not later.

<!-- TODO(Sven): photo of the rear, and a note on what cable lengths you ended up standardising on. -->

## What I'd Do Differently

<!-- TODO(Sven): fill this in after living with it for a week or two — depth surprises, an accessory you should have bought up front, whether the acrylic panels stay on, noise, whether it actually stays on the desk or moved to a shelf. -->

## Cost and Time

| Item | Cost |
|------|------|
| RackMate T1 | <!-- TODO --> |
| Shelves / accessories | <!-- TODO --> |
| PDU or power strip | <!-- TODO --> |
| Fan panel (if any) | <!-- TODO --> |
| Cables | <!-- TODO --> |
| **Total** | <!-- TODO --> |

Assembly and racking everything: about <!-- TODO --> hours.

## Related

If the gear going into this rack includes a UniFi gateway, the [Setting Up a UniFi Gateway]({{< ref "/posts/2026-08-20-setup-unifi-gateway" >}}) walkthrough covers getting it configured once it's mounted.
