---
title: "Building a Mini Rack with the DeskPi RackMate T1"
date: 2026-09-13
draft: false
description: A build log for a 10-inch, 8U mini rack based on the DeskPi RackMate T1 — planning the layout, assembling the frame, mounting gear on 0.5U and 1U shelves, and sorting power and cooling.
summary: A build log for a 10-inch, 8U mini rack based on the DeskPi RackMate T1 — planning the layout, assembling the frame, mounting gear on 0.5U and 1U shelves, and sorting power and cooling.
featured: true
tags:
  - homelab
  - mini-rack
  - deskpi
categories:
  - Homelab
cover: "cover.jpg"
status: "completed"
---

A full 19-inch rack is overkill for a home setup that's really just a gateway, a switch, a Pi or two, and a small NAS. A 10-inch mini rack fits the same gear on a desk or shelf without dominating the room. The [DeskPi RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2) is one of the more common options: a die-cast aluminium frame, 8U tall, 10 inches wide, flat-packed, with a whole ecosystem of 0.5U and 1U accessories built around it. (DeskPi sent me the RackMate T1 to try out.)

## What the RackMate T1 Actually Is

- **10-inch rack width.** The mounting rails sit 254 mm apart on centre — narrower than the 19-inch (483 mm) rails on a standard rack. Vertically it still follows the normal standard: 1U = 44.45 mm, so 8U of usable mounting height.
- **8U of space**, open front and back — the base T1 has no door, just translucent acrylic side panels for dust and looks.
- **Die-cast aluminium frame.** It's rigid once assembled and heavier than it looks.
- **Roughly 280 × 200 × 405 mm** overall on the base model (W × D × H). Depth is the dimension that actually catches people out.

## The Depth Trap

The single biggest mistake with a 10-inch rack is assuming your gear fits front-to-back. Usable depth behind the rails is only around 180–200 mm, and connectors and cable bend radius eat into that further — so measure the deepest thing you plan to rack, including any inline power brick, before ordering anything. Skip this and you'll end up like a lot of "10-inch rack" builds: the switch or NAS on a shelf facing sideways, rails purely structural.

## Planning the Layout

Work out the U budget before assembly — it's much easier to plan on paper than to reshuffle a populated rack.

| U | Item | Mounting |
|---|------|----------|
| 8 | Ubiquiti Cloud Gateway Fiber | 1U vented shelf |
| 7 | Ubiquiti Flex 2.5G PoE | 1U vented shelf |
| 6 | Patch Panel | Rail-mounted |
| 5 | Blank Panel | Rail-mounted |
| 4 | Open | Airflow gap |
| 3 | Open | Airflow gap |
| 2 | Minisforum UN100P Mini PC | 1U vented shelf |
| 1 | Blank Panel | Rail-mounted |

A few rules of thumb:

- **Heaviest at the bottom.** A NAS or anything with spinning disks goes in the lowest U so the rack isn't top-heavy on a desk.
- **Leave a gap above anything warm.** Passive cooling in an open frame works, but only if hot air can rise away from the device instead of straight into the next one.
- **Reserve 0.5U or 1U for a patch/cable-management panel** near the top or middle — it's the difference between a tidy build and a bird's nest.
- **Blank the gaps you're not using** if you later add a door or want the airflow to behave predictably.

![Rack elevation — what goes in each U, front view](rack-elevation.svg "DeskPi RackMate T1 rack elevation — layout by U")

U3 and U4 were the last slots I had to decide on. In the end I left both open: they give the mini PC two units of clear air above it, and they leave room to add something later without moving anything else.

That's the plan on paper — next is actually getting each device to stay put.

## Mounting the Gear

None of this gear ships with 10-inch rack ears, so it's all riding on shelves rather than bolted straight to the rails:

- **Ubiquiti Cloud Gateway Fiber**, **Ubiquiti Flex 2.5G PoE** and **Minisforum UN100P Mini PC** each sit on their own 1U vented shelf, held with cable ties or hook-and-loop.
- **Patch Panel** is DeskPi's own 10-inch panel. It has its own ears, so it mounts straight to the rails.
- **Blank panels** close off U5 and U1; U3 and U4 stay open.

![The RackMate T1 partway through the build, with the Cloud Gateway Fiber on its shelf in the top unit](IMG_2446.jpeg#small "Partway through the build: Cloud Gateway Fiber racked at the top, shelves going in below")

With everything physically mounted, the next job is getting power to it.

## Power

I went with the [DIGITUS 10" PDU](https://www.amazon.nl/dp/B0H8354DHB) — the only affordable EU-plug PDU I could find for a rack this size. It's mounted at the rear, and gives 4 plugs, which is enough for now to power the gateway, switch, and mini PC.

Power sorted, the next question is how much of that turns into heat.

## Cooling

An open frame with the side panels on is mostly passive — fine for a gateway, a switch, and a couple of Pis. It stops being fine when you add anything that runs hot continuously (a NAS under load, a mini PC doing transcoding).

Options if you need airflow:

- **A 1U or 2U fan panel** (DeskPi sells a 1U quad and a 2U dual) mounted above the warm device, pulling air up and out.
- **A single USB or Noctua fan** zip-tied to a post, aimed across the hot spot. Quieter, less tidy.
- **A fan panel at the bottom of the rack**, pushing air up from below instead of pulling it out above — works well when the heat source is low in the stack.
- **Just leave a 1U gap** above anything warm and skip active cooling entirely — often enough at this scale.

I went with the last option. The mini PC is the only thing in the rack that gets properly warm, and with U3 and U4 open above it there's enough room for the heat to rise away before it reaches the patch panel and switch. The gateway and switch run fine on their vented shelves, so the rack has no fans at all and makes no noise.

Airflow sorted, the last mechanical job is keeping all the resulting cabling under control.

## Cable Management

- A **0.5U cable-management panel with D-rings**, mounted at the rear facing inward, near the middle of the rack gives every patch cable a defined path.
- Use short cables. A 2 m patch lead in a 280 mm-wide rack is 1.7 m of loop to hide. DeskPi and others sell 0.2 m and 0.5 m CAT6 leads sized for this.
- Velcro, not zip ties, on anything you'll re-patch.
- Label both ends of every cable now, not later.

That's the build mechanics covered — here's what it cost.

## Cost and Time

| Item | Cost |
|------|------|
| [RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2) | €143,20 |
| [Shelves](https://deskpi.com/products/deskpi) | €45,99 |
| [Cable management panel](https://deskpi.com/products/10inch-server-rack-0-5u-rack-cable-management-panel-with-3-d-rings) | €11,99 | 
| PDU or power strip | €19,95 |
| **Total** | **€221,13** |

The total doesn't include the patch panel or the Flex's shelf, which came later. The network gear and mini PC were already in use, so they aren't counted either.

Assembly and racking everything: about 2 hours.

## The Result

The rack is done. The gateway, switch and mini PC share one 8U frame, all on a single PDU. Patching runs through one panel, and with passive cooling there's no fan noise. With U3 and U4 still open, there's room for a small NAS or a second mini PC later without rearranging the rest.
