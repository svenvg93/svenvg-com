# SVG Cover & Diagram Style Guide

Reference for all cover images and inline diagrams across the blog. Follow this guide when creating new covers or editing existing ones.

---

## Canvas

| Property | Value |
|----------|-------|
| Width | `1200` |
| Height | `630` |
| viewBox | `0 0 1200 630` |
| Aspect ratio | 1.905:1 (standard OG image) |

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 630" width="1200" height="630"
     font-family="system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
```

---

## Typography

### Font stacks

| Use | Stack |
|-----|-------|
| All UI text | `system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif` (set on root `<svg>`) |
| Code / terminal | `'Courier New',monospace` (set per element) |

### Title block (bottom of every cover)

Both elements are horizontally centered at `x="600"` with `text-anchor="middle"`.

| Element | `y` | `font-size` | `font-weight` | `fill` | `letter-spacing` |
|---------|-----|-------------|---------------|--------|-----------------|
| Series label | `500` | `13` | `600` | Series accent color (see below) | `3` |
| Post title | `538` | `34` | `700` | `#f1f5f9` | — |

```xml
<!-- Series label -->
<text x="600" y="500" text-anchor="middle" font-size="13"
      fill="SERIES_COLOR" letter-spacing="3" font-weight="600">Series Name</text>

<!-- Post title -->
<text x="600" y="538" text-anchor="middle" font-size="34"
      font-weight="700" fill="#f1f5f9">Post Title Here</text>
```

> **Rule**: Never use `font-size` larger than 34 for the main title. Never change `fill="#f1f5f9"` on the title.

---

## Background

### Base gradient

All covers use a diagonal dark gradient. Pick the variant closest to your series accent color.

**Dark navy (Traefik, Smokeping, MikroTik, neutral)**
```xml
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#080c14"/>
  <stop offset="100%" stop-color="#0d1520"/>
</linearGradient>
```

**Dark blue-navy (WiFi MLO, Roaming)**
```xml
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#050814"/>
  <stop offset="100%" stop-color="#0a1028"/>
</linearGradient>
```

**Dark amber-black (WiFi Channels)**
```xml
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#0a0800"/>
  <stop offset="100%" stop-color="#190f00"/>
</linearGradient>
```

**Dark green-black (WiFi WPA3)**
```xml
<linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0%" stop-color="#020d0a"/>
  <stop offset="100%" stop-color="#071a12"/>
</linearGradient>
```

Apply it as the first child of `<svg>`:
```xml
<rect width="1200" height="630" fill="url(#bg)"/>
```

### Bottom text overlay gradient

Every cover must include this gradient. It fades to opaque at the bottom to ensure the title block is always legible. Match the `stop-color` to your background's darkest shade.

```xml
<linearGradient id="textbg" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%"   stop-color="#080c14" stop-opacity="0"/>
  <stop offset="60%"  stop-color="#080c14" stop-opacity="0.93"/>
  <stop offset="100%" stop-color="#080c14" stop-opacity="1"/>
</linearGradient>

<!-- Always at y=390, height=240 — never move this rect -->
<rect x="0" y="390" width="1200" height="240" fill="url(#textbg)"/>
```

> **Critical rule**: All diagram content must end above `y=390`. Content between y=390 and y=500 will be progressively obscured by this gradient. If your diagram needs more space, compress it upward — never lower the `textbg` rect.

---

## Content area

| Zone | y range | Notes |
|------|---------|-------|
| Safe diagram area | `0` – `390` | Fully visible |
| Gradient fade zone | `390` – `500` | Increasingly obscured — avoid placing content here |
| Text block | `500` – `538` | Series label and title only |
| Dead zone | `538` – `630` | Background only, nothing rendered here |

### Vertical centering

The visual "center" of the safe zone (y=0–390) is y=195. For flow-based covers (left → center → right), aim for the primary element (router, central node) to be centered around **y=210–260** — slightly below mathematical center — so the composition doesn't feel top-heavy when viewed with the title block below.

> **Rule**: Don't place the center of the main diagram element above y=180 or below y=280.

---

## Horizontal layout & centering

For flow-based covers with a central element (router/hexagon) and flanking elements (devices, branches):

1. **The central element is always at `x=600`** (canvas center).
2. **Equal edge padding**: leftmost content and rightmost content should have roughly equal distance from the canvas edges — aim for ~100–170px on each side.
3. **Measure the content span**: add up the left half (left edge → x=600) and right half (x=600 → right edge). They should be within ~40px of each other.

```
Left padding  ≈  Right padding  ≈  100–170px
Left span     ≈  Right span     (within ~40px)
```

**How to balance an asymmetric layout:**
- If left span > right span: move the left element(s) rightward (closer to center).
- If right span > left span: move the right element(s) leftward, or widen them.
- Never move the central element away from x=600 to compensate.

---

## Zone color coding (topology covers)

When a cover shows a network flow across zones (e.g. Internet → Router → LAN), use consistent zone colors so readers can orient immediately:

| Zone | Color | Hex | Usage |
|------|-------|-----|-------|
| Internet / WAN / external client | Red | `#ef4444` | Globe, device frame, WAN badge |
| Router / central device | Blue | `#38bdf8` | Hexagon border, text, config pills |
| LAN / trusted network | Green | `#34d399` | Bridge block, device nodes, LAN labels |
| VPN / encrypted tunnel | Orange | `#f97316` | Tunnel body, packet dashes, lock icon |
| VPN subnet / overlay network | Purple | `#8b5cf6` | Route branch, subnet box |

**Light variants** for text inside colored elements:

| Zone color | Light text variant |
|------------|-------------------|
| Red `#ef4444` | `#fca5a5` |
| Blue `#38bdf8` | `#bae6fd` |
| Green `#34d399` | `#86efac` / `#4ade80` |
| Orange `#f97316` | `#fed7aa` |
| Purple `#8b5cf6` | `#c4b5fd` / `#a78bfa` |

> **Rule**: Never use a zone color that matches the diagram content as the series label color. Series label color is always the series accent (see below).

### Gradient arrows between zones

When an arrow crosses two color zones, use a `linearGradient` with `gradientUnits="userSpaceOnUse"` matching the line's exact coordinates:

```xml
<!-- In <defs> — matches line from x=265,y=210 to x=519,y=210 -->
<linearGradient id="arr-wan" x1="265" y1="210" x2="519" y2="210" gradientUnits="userSpaceOnUse">
  <stop offset="0%" stop-color="#ef4444"/>   <!-- source zone color -->
  <stop offset="100%" stop-color="#38bdf8"/> <!-- destination zone color -->
</linearGradient>
<marker id="arr-blue" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
  <polygon points="0,0 8,3 0,6" fill="#38bdf8"/> <!-- destination zone color -->
</marker>

<!-- Usage -->
<line x1="265" y1="210" x2="519" y2="210"
      stroke="url(#arr-wan)" stroke-width="2" marker-end="url(#arr-blue)"/>
```

### Zone glows

Add one `radialGradient` glow per zone, positioned at the zone's horizontal center:

```xml
<radialGradient id="glow-red" cx="16%" cy="50%" r="22%">
  <stop offset="0%" stop-color="#ef4444" stop-opacity="0.14"/>
  <stop offset="100%" stop-color="#ef4444" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow-blue" cx="50%" cy="50%" r="22%">
  <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.10"/>
  <stop offset="100%" stop-color="#38bdf8" stop-opacity="0"/>
</radialGradient>
<radialGradient id="glow-green" cx="82%" cy="50%" r="22%">
  <stop offset="0%" stop-color="#34d399" stop-opacity="0.10"/>
  <stop offset="100%" stop-color="#34d399" stop-opacity="0"/>
</radialGradient>
```

Keep glow `stop-opacity` ≤ 0.15 — subtle texture only, not a spotlight.

---

## Router / node hexagon pattern

All router and device nodes — whether central or left-side — use the same **pointy-top hexagon** shape. Size and position vary by role.

### Central node (r=82, at x=600)

Used for MikroTik, Alloy, Traefik, Smokeping — the primary processing element at the canvas center.

```xml
<!-- Outer hex, pointy-top, center (600,215), r=82 -->
<!-- Vertices: top(600,133) tr(671,174) br(671,256) bot(600,297) bl(529,256) tl(529,174) -->
<polygon points="600,133 671,174 671,256 600,297 529,256 529,174"
         fill="url(#hex-fill)" stroke="ACCENT" stroke-width="2.5"/>
<!-- Inner border ring (~8px inset) -->
<polygon points="600,141 663,179 663,251 600,289 537,251 537,179"
         fill="none" stroke="ACCENT" stroke-width="0.8" stroke-opacity="0.3"/>

<!-- Brand name + subtitle below -->
<text x="600" y="Y+103" text-anchor="middle" font-size="13"
      font-weight="700" fill="ACCENT" letter-spacing="4">SERVICE NAME</text>
```

### Left-side device node (r=70, at x=220)

Used for source devices that sit on the left of a monitoring flow. Smaller than the central node — not a processor, just a source.

**cy position depends on the flow type:**

- **cy=215** — use when all three elements in the row share the same y (three-hex inline flow). Arrow departs horizontally at y=215.
- **cy=255** — use when the left source diverges upward/downward to mini destination nodes at cx=880 (e.g. GL.iNet → Alloy → Prometheus/Loki/Grafana stacked vertically). Arrow departs at y=255.

```xml
<!-- cy=215 variant (three-hex inline flow) -->
<!-- Vertices: top(220,145) tr(281,180) br(281,250) bot(220,285) bl(159,250) tl(159,180) -->
<polygon points="220,145 281,180 281,250 220,285 159,250 159,180"
         fill="url(#hex-fill)" stroke="ACCENT" stroke-width="2.5"/>
<polygon points="220,153 274,184 274,246 220,277 166,246 166,184"
         fill="none" stroke="ACCENT" stroke-width="0.8" stroke-opacity="0.3"/>

<!-- cy=255 variant (diverging monitoring flow) -->
<!-- Vertices: top(220,185) tr(281,220) br(281,290) bot(220,325) bl(159,290) tl(159,220) -->
<polygon points="220,185 281,220 281,290 220,325 159,290 159,220"
         fill="url(#hex-fill)" stroke="ACCENT" stroke-width="2.5"/>
<polygon points="220,193 274,224 274,286 220,317 166,286 166,224"
         fill="none" stroke="ACCENT" stroke-width="0.8" stroke-opacity="0.3"/>
```

The right face of r=70 at cx=220 is always at **x=281** regardless of cy.

### hex-fill gradient variants

The hex-fill gradient is a dark tint of the accent color. One `id="hex-fill"` per file.

| Device / service | Top stop | Bottom stop |
|-----------------|----------|-------------|
| MikroTik / WiFi (blue) | `#0e2040` | `#071428` |
| Alloy / Grafana (blue) | `#0e2040` | `#071428` |
| Traefik (teal) | `#0e3040` | `#071e2a` |
| Smokeping (sky) | `#042a40` | `#021828` |
| GL.iNet (green) | `#0e4030` | `#072a1e` |
| Cloudflare / tunnel (orange) | `#1f0e04` | `#130800` |
| Prometheus / red service | `#200808` | `#140404` |
| Dependabot / purple service | `#1a0a2e` | `#0f051e` |

---

## Three-zone router topology pattern

Used when a post is about **setting up a router or gateway** — shows the classic Internet → Router → LAN flow. Used by MikroTik, VyOS, Travel Router, and Cloudflare Tunnels covers.

### Layout

| Zone | Element | Key coordinates |
|------|---------|-----------------|
| Left | Internet globe | cx=190, cy=210, r=74 |
| Center | Router hexagon | r=90 at (600, 210) — larger than the r=82 central node |
| Right | LAN bridge + device circles | rect x=874 y=180 w=168 h=58; circles at cx=918/958/998 cy=290 r=13 |
| Below center | Config pills row | y=318 |

> **Note**: The router hex uses r=90 (not r=82). The center y is 210 (not 215). These differ from the standard central node.

### Globe (left, red zone)

```xml
<circle cx="190" cy="210" r="74" fill="#150808" stroke="#7f1d1d" stroke-width="1.5"/>
<ellipse cx="190" cy="210" rx="37" ry="74" fill="none" stroke="#7f1d1d" stroke-width="1"/>
<line x1="116" y1="210" x2="264" y2="210" stroke="#7f1d1d" stroke-width="1"/>
<line x1="122" y1="173" x2="258" y2="173" stroke="#7f1d1d" stroke-width="1" opacity="0.4"/>
<line x1="122" y1="247" x2="258" y2="247" stroke="#7f1d1d" stroke-width="1" opacity="0.4"/>
<text x="190" y="216" text-anchor="middle" font-size="14" fill="#f87171" font-weight="600">Internet</text>
<!-- Badge below globe — adjust width to fit label text -->
<rect x="140" y="299" width="100" height="22" fill="#150808" stroke="#7f1d1d" stroke-width="1" rx="3"/>
<text x="190" y="314" text-anchor="middle" font-size="10" fill="#f87171" letter-spacing="1">WAN · eth1</text>
```

### Router hexagon (center)

```xml
<!-- Outer hex, pointy-top, center (600,210), r=90 -->
<!-- Vertices: top(600,120) tr(678,165) br(678,255) bot(600,300) bl(522,255) tl(522,165) -->
<polygon points="600,120 678,165 678,255 600,300 522,255 522,165"
         fill="url(#hex-fill)" stroke="ACCENT" stroke-width="2.5"/>
<!-- Inner border ring -->
<polygon points="600,134 666,172 666,248 600,286 534,248 534,172"
         fill="none" stroke="ACCENT" stroke-width="0.8" stroke-opacity="0.3"/>
<text x="600" y="202" text-anchor="middle" font-size="24" font-weight="700"
      fill="LIGHT_ACCENT" letter-spacing="1">RouterOS</text>
<text x="600" y="222" text-anchor="middle" font-size="10"
      fill="ACCENT" letter-spacing="3" opacity="0.8">subtitle</text>
```

### Config pills (below hex, y=318)

Four pills positioned symmetrically around x=600. Total pill width + gaps = 264px, start at x=468:

```xml
<g font-size="10" font-weight="600" letter-spacing="1" text-anchor="middle">
  <rect x="468" y="318" width="72" height="22" fill="HEX_DARK" stroke="ACCENT"
        stroke-width="1" stroke-opacity="0.5" rx="3"/>
  <text x="504" y="333" fill="LIGHT_ACCENT">Pill One</text>
  <!-- repeat for remaining pills, advancing x by pill-width + 8px gap -->
</g>
```

### LAN zone (right, green)

```xml
<rect x="874" y="180" width="168" height="58" fill="#071810" stroke="#166534" stroke-width="1.5" rx="5"/>
<text x="958" y="205" text-anchor="middle" font-size="13" fill="#86efac" font-weight="600">br0</text>
<text x="958" y="224" text-anchor="middle" font-size="9" fill="#4ade80" letter-spacing="1">ether2 – ether8</text>
<!-- Vertical lines to device circles -->
<line x1="918" y1="238" x2="918" y2="278" stroke="#14532d" stroke-width="1.5"/>
<line x1="958" y1="238" x2="958" y2="278" stroke="#14532d" stroke-width="1.5"/>
<line x1="998" y1="238" x2="998" y2="278" stroke="#14532d" stroke-width="1.5"/>
<!-- Device circles -->
<circle cx="918" cy="290" r="13" fill="#071810" stroke="#166534" stroke-width="1.5"/>
<circle cx="958" cy="290" r="13" fill="#071810" stroke="#166534" stroke-width="1.5"/>
<circle cx="998" cy="290" r="13" fill="#071810" stroke="#166534" stroke-width="1.5"/>
<text x="918" y="294" text-anchor="middle" font-size="7" fill="#4ade80">PC</text>
<text x="958" y="294" text-anchor="middle" font-size="7" fill="#4ade80">PC</text>
<text x="998" y="294" text-anchor="middle" font-size="7" fill="#4ade80">PC</text>
<text x="958" y="330" text-anchor="middle" font-size="10" fill="#166534" letter-spacing="1">DHCP 192.168.1.100–200</text>
```

### Arrows

```xml
<!-- WAN → Router: dashed, gradient red → router accent -->
<line x1="265" y1="210" x2="519" y2="210"
      stroke="url(#arr-wan)" stroke-width="2" stroke-dasharray="6,4" marker-end="url(#arr-ACCENT)"/>
<text x="392" y="198" text-anchor="middle" font-size="9" fill="#6b2020" letter-spacing="1">DHCP · PPPoE · Static</text>

<!-- Router → LAN: solid, gradient router accent → green -->
<line x1="680" y1="210" x2="869" y2="210"
      stroke="url(#arr-lan)" stroke-width="2" marker-end="url(#arr-green)"/>
<text x="775" y="198" text-anchor="middle" font-size="9" fill="#0a4040" letter-spacing="1">192.168.1.0/24</text>
```

---

## Three-hex monitoring flow pattern

Used when a post shows a **source → processor → destination** flow with three peer services of roughly equal importance. All three hexes share the same center y (cy=215).

### Layout

| Position | Role | cx | r | Right-face x |
|----------|------|----|---|-------------|
| Left | Source (e.g. Tailscale) | 220 | 70 | 281 |
| Center | Processor (e.g. Prometheus) | 600 | 82 | 671 |
| Right | Destination (e.g. Grafana) | 940 | 70 | 1001 |

Arrows are horizontal lines at y=215:

```xml
<!-- Source → Processor -->
<line x1="281" y1="215" x2="529" y2="215"
      stroke="url(#arr-src-proc)" stroke-width="2" marker-end="url(#arr-PROC_COLOR)"/>
<text x="405" y="203" text-anchor="middle" font-size="9" fill="#64748b" letter-spacing="1">scrape :9100</text>

<!-- Processor → Destination -->
<line x1="671" y1="215" x2="879" y2="215"
      stroke="url(#arr-proc-dest)" stroke-width="2" marker-end="url(#arr-DEST_COLOR)"/>
<text x="775" y="203" text-anchor="middle" font-size="9" fill="#64748b" letter-spacing="1">query</text>
```

### Hex vertices

```
Left  (cx=220, cy=215, r=70):  outer "220,145 281,180 281,250 220,285 159,250 159,180"
                                inner "220,153 274,184 274,246 220,277 166,246 166,184"
Center (cx=600, cy=215, r=82): outer "600,133 671,174 671,256 600,297 529,256 529,174"
                                inner "600,141 663,179 663,251 600,289 537,251 537,179"
Right (cx=940, cy=215, r=70):  outer "940,145 1001,180 1001,250 940,285 879,250 879,180"
                                inner "940,153 994,184 994,246 940,277 886,246 886,184"
```

> **Use this pattern instead of the diverging mini-node pattern** when the destination is a single well-known service (Grafana) rather than a stack of three tools. The right hex at cx=940 stops at x=1001 — just within the canvas.

---

## Setup flow pattern

Used when a post is about **installing or configuring** a tool, rather than showing its data flows. Shows the progression: config file → service → running result.

### Layout

| Zone | x range | Element |
|------|---------|---------|
| Left | 60–320 | Terminal panel with docker-compose.yml (or config file) |
| Center | 529–671 | Service hexagon at (600, 215), r=82 |
| Right | 880–1140 | Terminal panel with `docker ps` / running output |

Arrows connect left-panel edge to hex left face, and hex right face to right-panel edge:

```xml
<!-- Config → hex -->
<path d="M 320,215 C 400,215 460,215 529,215"
      fill="none" stroke="ACCENT" stroke-width="2" marker-end="url(#arr)"/>
<!-- Hex → result -->
<path d="M 671,215 C 740,215 800,215 880,215"
      fill="none" stroke="ACCENT" stroke-width="2" marker-end="url(#arr)"/>
```

Use a single arrow marker `id="arr"` in `<defs>` filled with the series accent color.

### Left panel — config file

```xml
<rect x="60" y="80" width="260" height="270" fill="#0a1628" stroke="#334155" stroke-width="1.5" rx="8"/>
<!-- Title bar -->
<rect x="60" y="80" width="260" height="24" fill="#1e293b" rx="8"/>
<rect x="60" y="92"  width="260" height="12" fill="#1e293b"/>
<!-- Traffic lights -->
<circle cx="82" cy="92" r="5" fill="#ef4444" fill-opacity="0.7"/>
<circle cx="97" cy="92" r="5" fill="#f59e0b" fill-opacity="0.7"/>
<circle cx="112" cy="92" r="5" fill="#4ade80" fill-opacity="0.7"/>
<text x="190" y="96" text-anchor="middle" font-size="9" fill="#64748b">docker-compose.yml</text>
```

### Right panel — running result

```xml
<rect x="880" y="80" width="260" height="270" fill="#0a1628" stroke="#334155" stroke-width="1.5" rx="8"/>
<!-- Title bar -->
<rect x="880" y="80" width="260" height="24" fill="#1e293b" rx="8"/>
<rect x="880" y="92"  width="260" height="12" fill="#1e293b"/>
<!-- Traffic lights -->
<circle cx="902" cy="92" r="5" fill="#ef4444" fill-opacity="0.7"/>
<circle cx="917" cy="92" r="5" fill="#f59e0b" fill-opacity="0.7"/>
<circle cx="932" cy="92" r="5" fill="#4ade80" fill-opacity="0.7"/>
<text x="1010" y="96" text-anchor="middle" font-size="9" fill="#64748b">bash</text>
```

> **Rule**: Panels should be vertically centered around y=215 and have equal width (260px). Keep panel bottom edge ≤ y=380.

---

## Monitoring tool mini hexagon nodes

Used on monitoring-flow covers to represent destination tools (Prometheus, Loki, Grafana). Each tool gets a **pointy-top mini hexagon** at cx=880 on the right side of the canvas.

### Positions (three tools)

Three tools stack vertically with 90px spacing. When the source diverges from y=255 (center), place them at cy=165, 255, 345:

| Tool | cy | Hex vertices (r=35) |
|------|----|---------------------|
| Prometheus | 165 | `880,130 910,148 910,182 880,200 850,182 850,148` |
| Loki | 255 | `880,220 910,238 910,272 880,290 850,272 850,238` |
| Grafana | 345 | `880,310 910,328 910,362 880,380 850,362 850,328` |

### Per-tool colors and markup

```xml
<!-- Prometheus — red -->
<polygon points="880,130 910,148 910,182 880,200 850,182 850,148"
         fill="#200808" stroke="#ef4444" stroke-width="2"/>
<polygon points="880,135 906,150 906,180 880,195 854,180 854,150"
         fill="none" stroke="#ef4444" stroke-width="0.7" stroke-opacity="0.3"/>
<text x="880" y="170" text-anchor="middle" font-size="18" font-weight="800" fill="#ef4444">P</text>
<text x="922" y="162" font-size="12" font-weight="700" fill="#ef4444" letter-spacing="1">PROMETHEUS</text>
<text x="922" y="176" font-size="9" fill="#64748b" font-family="'Courier New',monospace">metrics · time-series db</text>

<!-- Loki — purple -->
<polygon points="880,220 910,238 910,272 880,290 850,272 850,238"
         fill="#160a2a" stroke="#a78bfa" stroke-width="2"/>
<polygon points="880,225 906,240 906,270 880,285 854,270 854,240"
         fill="none" stroke="#a78bfa" stroke-width="0.7" stroke-opacity="0.3"/>
<text x="880" y="261" text-anchor="middle" font-size="18" font-weight="800" fill="#a78bfa">L</text>
<text x="922" y="252" font-size="12" font-weight="700" fill="#a78bfa" letter-spacing="1">LOKI</text>
<text x="922" y="266" font-size="9" fill="#64748b" font-family="'Courier New',monospace">logs · label-indexed</text>

<!-- Grafana — orange (#f97316) or amber (#f59e0b) depending on context -->
<polygon points="880,310 910,328 910,362 880,380 850,362 850,328"
         fill="#1a0c00" stroke="#f97316" stroke-width="2"/>
<polygon points="880,315 906,330 906,360 880,375 854,360 854,330"
         fill="none" stroke="#f97316" stroke-width="0.7" stroke-opacity="0.3"/>
<text x="880" y="351" text-anchor="middle" font-size="18" font-weight="800" fill="#f97316">G</text>
<text x="922" y="342" font-size="12" font-weight="700" fill="#f97316" letter-spacing="1">GRAFANA</text>
<text x="922" y="356" font-size="9" fill="#64748b" font-family="'Courier New',monospace">visualization · dashboards</text>
```

### Gradient arrows to tool nodes

Arrows from the source node diverge to three y-positions. Use `gradientUnits="userSpaceOnUse"` so the gradient tracks the actual line path:

```xml
<!-- In <defs> — source node right face at (697, source_y ± offset) -->
<linearGradient id="arr-src-prom" x1="697" y1="243" x2="850" y2="165" gradientUnits="userSpaceOnUse">
  <stop offset="0%" stop-color="SOURCE_ACCENT"/>
  <stop offset="100%" stop-color="#ef4444"/>
</linearGradient>
<linearGradient id="arr-src-loki" x1="697" y1="255" x2="850" y2="255" gradientUnits="userSpaceOnUse">
  <stop offset="0%" stop-color="SOURCE_ACCENT"/>
  <stop offset="100%" stop-color="#a78bfa"/>
</linearGradient>
<linearGradient id="arr-src-graf" x1="697" y1="267" x2="850" y2="345" gradientUnits="userSpaceOnUse">
  <stop offset="0%" stop-color="SOURCE_ACCENT"/>
  <stop offset="100%" stop-color="#f97316"/>
</linearGradient>

<!-- Colored tip markers matching destination tool -->
<marker id="arr-red"    markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
  <polygon points="0,0 8,3 0,6" fill="#ef4444"/>
</marker>
<marker id="arr-purple" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
  <polygon points="0,0 8,3 0,6" fill="#a78bfa"/>
</marker>
<marker id="arr-orange" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
  <polygon points="0,0 8,3 0,6" fill="#f97316"/>
</marker>
```

```xml
<!-- Arrow paths -->
<path d="M 697,243 C 730,220 780,165 850,165" fill="none" stroke="url(#arr-src-prom)" stroke-width="2" marker-end="url(#arr-red)"/>
<path d="M 697,255 L 850,255"                 fill="none" stroke="url(#arr-src-loki)" stroke-width="2" marker-end="url(#arr-purple)"/>
<path d="M 697,267 C 730,290 780,345 850,345" fill="none" stroke="url(#arr-src-graf)" stroke-width="2" marker-end="url(#arr-orange)"/>
```

> **Rule**: The center arrow (to Loki) is always a straight horizontal line. The top and bottom arrows use cubic bezier curves that arc symmetrically. Departure points from the source node should be offset ±12px from center (e.g. y=243, 255, 267 for a flat-top hex with right vertex at y=255).

### Two-tool variant

When only two tools are shown (e.g. Prometheus + Grafana only), center them at cy=155 and cy=275 to keep balanced vertical spacing around y=215:

| Tool | cy | Hex vertices (r=35) |
|------|----|---------------------|
| Prometheus | 155 | `880,120 910,138 910,172 880,190 850,172 850,138` |
| Grafana | 275 | `880,240 910,258 910,292 880,310 850,292 850,258` |

### Single large tool node (solo destination)

When only one tool is the destination (e.g. Loki-only cover), use a larger hexagon (r=45) centered at cy=215 for visual weight:

```xml
<!-- Loki solo, r=45, center (900,215) -->
<polygon points="900,170 939,192 939,238 900,260 861,238 861,192"
         fill="#160a2a" stroke="#a78bfa" stroke-width="2.5"/>
<polygon points="900,176 934,195 934,235 900,254 866,235 866,195"
         fill="none" stroke="#a78bfa" stroke-width="0.8" stroke-opacity="0.3"/>
<text x="900" y="222" text-anchor="middle" font-size="22" font-weight="800" fill="#a78bfa">L</text>
<text x="952" y="209" font-size="13" font-weight="700" fill="#a78bfa" letter-spacing="1">LOKI</text>
<text x="952" y="224" font-size="9" fill="#64748b" font-family="'Courier New',monospace">logs · label-indexed</text>
```

---

## Symmetric branch layout

When showing multiple route/output branches from a central node, branches **must be placed symmetrically** around the node's vertical center. Equal vertical offset above and below:

```
node center y = Y
branch 1 end y = Y - offset
branch 2 end y = Y + offset   ← same offset value
```

Use cubic bezier curves for clean arcs:
```xml
<!-- Branch arcing UP from node right edge -->
<path d="M Rx,Y-17 C Cx,Y-17 Cx,Y-offset Bx,Y-offset"
      fill="none" stroke="COLOR" stroke-width="2" marker-end="url(#arr)"/>

<!-- Branch arcing DOWN — mirror of above -->
<path d="M Rx,Y+17 C Cx,Y+17 Cx,Y+offset Bx,Y+offset"
      fill="none" stroke="COLOR" stroke-width="2" marker-end="url(#arr)"/>
```

Branch destination boxes should share the same `x` start position and the same `width`:
```xml
<rect x="Bx+4" y="Y-offset-14" width="168" height="28" fill="..." rx="4"/>
<rect x="Bx+4" y="Y+offset-14" width="168" height="28" fill="..." rx="4"/>
```

---

## Series accent colors

Each series has one accent color used for: series label text, primary glows, key UI elements.

| Series | Color | Hex |
|--------|-------|-----|
| WiFi Explained | Sky 400 | `#38bdf8` |
| Traefik Essentials | Teal | `#37BEC3` |
| Smokeping Essentials | Sky 500 | `#0ea5e9` |
| Ansible Essentials | Red 600 | `#dc2626` |
| MikroTik (standalone) | Red 500 | `#ef4444` |
| Grafana Observability | Orange | `#f97316` |

> **Rule**: The series label `fill` must always use the series accent color. Never use a color from the diagram content itself as the series label color.

---

## WiFi band colors

Used across all WiFi Explained covers for 2.4 / 5 / 6 GHz visual elements.

| Band | Color | Hex | Glow / light variant |
|------|-------|-----|---------------------|
| 2.4 GHz | Orange | `#f97316` | `#fed7aa` |
| 5 GHz | Sky blue | `#38bdf8` | `#bae6fd` |
| 6 GHz | Emerald | `#34d399` | `#a7f3d0` |

When showing bandwidth as stroke width (e.g. MLO diagram), scale proportionally:

| Band | Max bandwidth | Stroke width |
|------|--------------|-------------|
| 6 GHz | 320 MHz | `36` |
| 5 GHz | 160 MHz | `26` |
| 2.4 GHz | 40 MHz | `16` |

---

## Subtle background textures

Use sparingly — one texture type per cover.

**Line grid** (horizontal and/or vertical, very dark):
```xml
<g stroke="#0d1a2a" stroke-width="1">
  <line x1="0"    y1="100" x2="1200" y2="100"/>
  <line x1="0"    y1="200" x2="1200" y2="200"/>
  <!-- etc. -->
</g>
```

**Dot grid**:
```xml
<g fill="#0f1f44" opacity="0.8">
  <circle cx="200" cy="100" r="1.5"/>
  <!-- etc. -->
</g>
```

**Hex grid** (for security/network topology themes):
```xml
<g stroke="#0a2016" stroke-width="1" fill="none" opacity="0.7">
  <polygon points="600,60 660,95 660,165 600,200 540,165 540,95"/>
  <!-- etc. -->
</g>
```

---

## SVG `<defs>` rules

1. **All markers, gradients, and filters must be in the single top-level `<defs>` block** — never in a second `<defs>` block added mid-file. Forward-referenced markers fail in static renderers and OG crawlers.
2. Gradient `id` names: `bg`, `textbg`, and then descriptive names (`band24`, `band5`, `shield-fill`, etc.).

```xml
<svg ...>
  <defs>
    <!-- ALL gradients, markers, filters here -->
    <linearGradient id="bg" .../>
    <linearGradient id="textbg" .../>
    <marker id="arrow" .../>
  </defs>

  <!-- Content below -->
  <rect width="1200" height="630" fill="url(#bg)"/>
  ...
</svg>
```

---

## Animations and emoji

| Element | Rule |
|---------|------|
| `<animate>` | **Do not use.** Static in OG crawlers, invisible in rasterizers. Use a static SVG marker instead. |
| Emoji in `<text>` | **Do not use.** Render as blank boxes in most rasterizers. Use SVG shapes or text labels. |

**Static arrow replacement pattern:**
```xml
<!-- In <defs> -->
<marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
  <polygon points="0,0 8,3 0,6" fill="#4ade80"/>
</marker>

<!-- Usage -->
<path d="M 100,100 L 200,100" fill="none" stroke="#4ade80"
      stroke-width="2" marker-end="url(#arr)"/>
```

---

## Terminal / code panel pattern

Used in Traefik Bare Metal and Smokeping covers. Standard panel with macOS-style traffic lights.

```xml
<!-- Panel -->
<rect x="X" y="Y" width="W" height="H" fill="#0a1628" stroke="#334155" stroke-width="1.5" rx="8"/>
<!-- Title bar -->
<rect x="X" y="Y" width="W" height="24" fill="#1e293b" rx="8"/>
<rect x="X" y="Y+12" width="W" height="12" fill="#1e293b"/>
<!-- Traffic lights -->
<circle cx="X+22" cy="Y+12" r="5" fill="#ef4444" fill-opacity="0.7"/>
<circle cx="X+37" cy="Y+12" r="5" fill="#f59e0b" fill-opacity="0.7"/>
<circle cx="X+52" cy="Y+12" r="5" fill="#4ade80" fill-opacity="0.7"/>
<!-- Filename label -->
<text x="X+W/2" y="Y+16" text-anchor="middle" font-size="9" fill="#64748b">filename</text>
```

Code text uses `font-family="'Courier New',monospace"` with these color conventions:

| Token type | Color |
|------------|-------|
| YAML key / keyword | `#7dd3fc` |
| Service / section name | `#a3e635` |
| String value (highlighted) | `#fb923c` |
| Regular value / comment | `#94a3b8` |
| Dimmed / secondary | `#64748b` |
| systemd active/running | `#4ade80` |

---

## Callout labels

Short annotation labels (e.g. "evening congestion", "IXP → CDN") follow this pattern:

```xml
<!-- Optional leader line -->
<line x1="X" y1="Y-20" x2="X" y2="Y-4" stroke="#ef4444" stroke-width="1" stroke-dasharray="3,2"/>
<!-- Label -->
<text x="X" y="Y" text-anchor="middle" font-size="8" fill="#ef4444">Label text</text>
```

Use `font-size="8"` for chart annotations, `font-size="10"–"13"` for section labels.

---

## Text contrast

Labels inside or adjacent to colored elements must be legible against dark backgrounds. Never use a zone's base color as text — always use its light variant:

| Background | Avoid | Use instead |
|------------|-------|-------------|
| Purple element | `#5b21b6`, `#4c1d95` | `#c4b5fd`, `#a78bfa` |
| Orange element | `#c2410c`, `#7c2d12` | `#fed7aa`, `#fb923c` |
| Blue element | `#075985`, `#0e2040` | `#bae6fd`, `#7dd3fc` |
| Green element | `#064e3b`, `#166534` | `#86efac`, `#4ade80` |
| Red element | `#7f1d1d`, `#450a0a` | `#fca5a5`, `#f87171` |

---

## Checklist for new covers

- [ ] Canvas is exactly 1200×630
- [ ] Root `<svg>` has correct `font-family` attribute
- [ ] All gradients and markers are inside a single top-level `<defs>` block
- [ ] `textbg` gradient rect is at `y="390"` with `height="240"`
- [ ] All diagram content ends above `y=390`
- [ ] Main diagram element is centered at `x=600`
- [ ] Left edge padding ≈ right edge padding (within ~40px)
- [ ] Diagram vertical center is between `y=180` and `y=280`
- [ ] Zone colors follow the red/blue/green/orange/purple convention
- [ ] Branch routes from a central node are placed symmetrically (equal y offset above and below)
- [ ] All text labels use light variants of zone colors, not the dark base colors
- [ ] Series label: `x="600" y="500"`, `font-size="13"`, `letter-spacing="3"`, `font-weight="600"`, correct series accent color
- [ ] Post title: `x="600" y="538"`, `font-size="34"`, `font-weight="700"`, `fill="#f1f5f9"`
- [ ] No `<animate>` elements
- [ ] No emoji characters in `<text>` elements
- [ ] No second `<defs>` block
- [ ] **Setup flow covers**: left panel and right panel both 260px wide, panels at y=80 (centered on y=215); arrows at y=215; all content ≤ y=380
- [ ] **Monitoring tool nodes**: mini hexagons at cx=880; three-tool layout at cy=165/255/345; two-tool at cy=155/275; gradient arrows use `gradientUnits="userSpaceOnUse"`; tip markers match destination tool color
- [ ] **Device source nodes**: left-side device hexagon at cx=220 (r=70); cy=215 for three-hex inline flow, cy=255 for diverging monitoring flow; right face departure at x=281
- [ ] **Three-zone router topology**: globe at cx=190 cy=210 r=74; router hex r=90 at (600,210); LAN bridge x=874 y=180; config pills at y=318; WAN arrow dashed, LAN arrow solid
- [ ] **Three-hex monitoring flow**: all three hexes at cy=215; left r=70 at cx=220, center r=82 at cx=600, right r=70 at cx=940; horizontal arrows at y=215
