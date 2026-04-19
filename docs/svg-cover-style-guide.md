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

Used for MikroTik and any central router/device node.

```xml
<!-- Outer hex, pointy-top, center (600,Y), circumradius r -->
<!-- Vertices: (cx, cy-r), (cx+r*0.866, cy-r*0.5), (cx+r*0.866, cy+r*0.5),
               (cx, cy+r), (cx-r*0.866, cy+r*0.5), (cx-r*0.866, cy-r*0.5) -->
<polygon points="600,120 671,161 671,243 600,284 529,243 529,161"
         fill="url(#hex-fill)" stroke="ACCENT" stroke-width="2.5"/>
<!-- Inner border ring (~10px inset) -->
<polygon points="600,132 661,168 661,236 600,272 539,236 539,168"
         fill="none" stroke="ACCENT" stroke-width="0.8" stroke-opacity="0.3"/>

<!-- Labels -->
<text x="600" y="Y+some" text-anchor="middle" font-size="20"
      font-weight="700" fill="LIGHT_ACCENT" letter-spacing="1">Device Name</text>
<text x="600" y="Y+some" text-anchor="middle" font-size="10"
      fill="ACCENT" letter-spacing="3" opacity="0.8">subtitle</text>
```

The hex-fill gradient is a dark tinted version of the accent color:
```xml
<!-- Blue (MikroTik) -->
<linearGradient id="hex-fill" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#0e2040"/>
  <stop offset="100%" stop-color="#071428"/>
</linearGradient>
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
