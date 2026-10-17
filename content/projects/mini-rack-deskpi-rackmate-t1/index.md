---
title: "Building a Mini Rack with the DeskPi RackMate T1"
date: 2026-09-13
lastmod: 2026-10-17
draft: false
description: A build log for my 10-inch, 8U mini rack based on the DeskPi RackMate T1 — planning the layout, assembling the frame, mounting gear on 1U shelves, and sorting power and cooling. Compute hardware is still to come.
summary: A build log for my 10-inch, 8U mini rack based on the DeskPi RackMate T1 — planning the layout, assembling the frame, mounting gear on 1U shelves, and sorting power and cooling. Compute hardware is still to come.
featured: true
tags:
  - homelab
  - mini-rack
  - deskpi
categories:
  - Homelab
cover: "cover.jpg"
status: "in_progress"
---

My home setup is a gateway, a switch and a mini PC, with some compute still to come. A full 19-inch rack would be overkill for that. A 10-inch mini rack holds the same gear on a desk or shelf without taking over the room. I built mine on the [DeskPi RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2), one of the more common options: a die-cast aluminium frame, 8U tall, 10 inches wide, flat-packed, with plenty of 0.5U and 1U accessories made for it. (DeskPi sent me the RackMate T1 to try out.)

## What the RackMate T1 Actually Is

- **10-inch rack width.** The mounting rails sit 254 mm apart on centre, narrower than the 483 mm of a standard 19-inch rack. Vertically it follows the normal standard: 1U = 44.45 mm, so 8U of usable mounting height.
- **8U of space**, open front and back. The base T1 has no door, just translucent acrylic side panels for dust and looks.
- **Die-cast aluminium frame.** Once I'd assembled it, it was rigid and heavier than it looks.
- **Roughly 280 × 200 × 405 mm** overall on the base model (W × D × H). Depth is the dimension to watch.

## Checking the Depth First

The usual mistake with a 10-inch rack is assuming your gear fits front-to-back. Usable depth behind the rails is only around 180–200 mm, and connectors and cable bend radius take up some of that. Before ordering anything, I measured the deepest thing I planned to rack, including any inline power brick. Plenty of "10-inch rack" builds end up with the switch or NAS sitting sideways on a shelf and the rails doing nothing but holding the frame together. I wanted to avoid that.

## Planning the Layout

I worked out the U budget on paper before assembling anything. That's much easier than reshuffling a populated rack.

| U | Item | Mounting |
|---|------|----------|
| 8 | Ubiquiti Cloud Gateway Fiber | 1U vented shelf |
| 7 | Ubiquiti Flex 2.5G PoE | 1U vented shelf |
| 6 | Patch Panel | Rail-mounted |
| 5 | Blank Panel | Rail-mounted |
| 4 | Compute (hardware TBD) | TBD |
| 3 | Compute (hardware TBD) | TBD |
| 2 | Minisforum UN100P Mini PC | 1U vented shelf |
| 1 | Blank Panel | Rail-mounted |

The table shows the front rails. The PDU and the 0.5U cable-management panel sit on the rear rails, so they don't take up any of these slots.

These are the rules I planned around:

- **Heavy gear low down.** Nothing in the rack is heavy yet, but whatever goes in later belongs in the lower half so the rack isn't top-heavy on a desk. That's one reason the compute slots are U3 and U4.
- **Leave room above anything warm.** Passive cooling in an open frame works, but only if hot air can rise away from a device instead of straight into the next one.
- **Keep a slot for patching** near the top or middle. In my rack that's the patch panel in U6, right below the switch.
- **Blank the slots I'm not using**, so the front looks finished and airflow stays predictable if I add a door later.

I've reserved U3 and U4 for compute hardware. I haven't decided what goes there yet. Until it arrives, the two slots stay empty and give the mini PC clear air above it.

With the plan done, the next job was getting each device to stay put.

## Mounting the Gear

None of my gear came with 10-inch rack ears, so it all rides on shelves rather than being bolted straight to the rails:

- I put the **Ubiquiti Cloud Gateway Fiber**, the **Ubiquiti Flex 2.5G PoE** and the **Minisforum UN100P Mini PC** each on their own 1U vented shelf and held them down with cable ties or Velcro.
- The **patch panel** is DeskPi's own 10-inch panel. It has its own ears, so I mounted it straight to the rails.
- **Blank panels** close off U5 and U1. U3 and U4 are waiting for the compute hardware.

![The RackMate T1 partway through the build, with the Cloud Gateway Fiber on its shelf in the top unit](IMG_2446.jpeg#small "Partway through the build: Cloud Gateway Fiber racked at the top, shelves going in below")

Once everything was mounted, I needed to get power to it.

## Power

I went with the [DIGITUS 10" PDU](https://www.amazon.nl/dp/B0H8354DHB), the only affordable EU-plug PDU I could find for a rack this size. I mounted it at the rear. Its 4 sockets are enough for now to power the gateway, switch and mini PC. The compute hardware may mean I need more sockets later.

With power in, the next question was how much of it turns into heat.

## Cooling

An open frame with the side panels on is mostly passive cooling. That's fine for a gateway and a switch. It stops being fine once you add something that runs hot all the time, like a NAS under load or a mini PC doing transcoding.

These are the options I looked at:

- **A 1U or 2U fan panel** (DeskPi sells a 1U quad and a 2U dual) mounted above the warm device, pulling air up and out.
- **A single USB or Noctua fan** zip-tied to a post and aimed at the hot spot. Quieter, but less tidy.
- **A fan panel at the bottom of the rack**, pushing air up from below. This works well when the heat source is low in the stack.
- **Leaving a gap** above anything warm and skipping active cooling entirely. At this scale that's often enough.

For now I've gone with the last option. The mini PC is the only thing in the rack that gets properly warm, and with U3 and U4 empty above it, the heat rises away before it reaches the patch panel and switch. The gateway and switch run fine on their vented shelves, so the rack has no fans and makes no noise. Filling U3 and U4 with compute takes that gap away, so I'll revisit cooling once that hardware is in.

The last mechanical job was keeping the cabling under control.

## Cable Management

- I mounted a **0.5U cable-management panel with D-rings** at the rear, facing inward, near the middle of the rack. It gives every patch cable a set path.
- I used short cables. A 2 m patch lead in a 280 mm-wide rack leaves about 1.7 m of loop to hide. DeskPi and others sell 0.2 m and 0.5 m CAT6 leads sized for racks like this.
- I used Velcro instead of zip ties on anything I'll re-patch.
- I labelled both ends of every cable while building, not afterwards.

That covers the build so far. Here's what it cost.

## Cost and Time

| Item | Cost |
|------|------|
| [RackMate T1](https://deskpi.com/products/deskpi-rackmate-t1-2) | €143,20 |
| [Shelves](https://deskpi.com/products/deskpi) | €45,99 |
| [Cable management panel](https://deskpi.com/products/10inch-server-rack-0-5u-rack-cable-management-panel-with-3-d-rings) | €11,99 |
| [DIGITUS 10" PDU](https://www.amazon.nl/dp/B0H8354DHB) | €19,95 |
| **Total** | **€221,13** |

The total doesn't include the patch panel or the Flex's shelf, which I added later. The network gear and mini PC were already in use, so I haven't counted them. The compute hardware isn't included yet either.

Assembling the frame and racking everything took me about 2 hours.

## Where It Stands

The build isn't finished yet. The networking side is done: the gateway, switch and mini PC share one 8U frame and run off a single PDU. Patching runs through one panel, and with passive cooling there's no fan noise. U3 and U4 are reserved for compute hardware. I haven't decided what that will be yet. Once it's in, I'll update this post with what I picked, how it's mounted, and whether the rack still works without fans. I'll also add a photo of the finished rack.

## To Do

- [ ] Choose the compute hardware for U3 and U4
- [ ] Mount the compute hardware in the rack
- [ ] Sort power for the new hardware (the PDU has only 4 sockets)
- [ ] Check temperatures and add a fan panel if passive cooling isn't enough
- [ ] Redo the cable management to include the compute
- [ ] Update the cost table with the compute parts
- [ ] Add a photo of the finished rack
