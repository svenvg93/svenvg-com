# SVG Inline Diagram Style Guide

Reference for all inline diagrams embedded inside post content. These are smaller than covers and sit between paragraphs, but must visually match the cover style — same dark background, same color palette, same typography conventions.

See [`svg-cover-style-guide.md`](svg-cover-style-guide.md) for cover-specific rules. This guide covers only the delta for inline diagrams.

---

## Canvas

Inline diagrams are narrower and shorter than covers. Standard sizes:

| Use case | Width | Height | viewBox |
|----------|-------|--------|---------|
| Simple flow (2–3 nodes) | `700` | `220` | `0 0 700 220` |
| Standard flow (3–4 nodes, labels) | `700` | `260` | `0 0 700 260` |
| Tall flow (many branches / rows) | `700` | `300` | `0 0 700 300` |

Always set both `width`/`height` attributes and `viewBox`. Use `rx="8"` on the background rect.

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 260" width="700" height="260"
     font-family="system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif">
```

**Sizing rule:** After placing all content, verify that the last element's bottom edge is at least 20 px above the canvas bottom (30 px if you have a two-line footer). If it is not, increase the canvas height rather than cramming text into the margin. Also verify that circles or arcs do not exceed the canvas — a circle at `cy=150, r=140` has its bottom at `y=290`; a 280 px canvas clips it.

---

## Captions

If a caption is needed it must be defined after the filename like:

```
![](filename.svg "Caption")
```

---

## Background

Use the same dark navy gradient as the covers, applied to a rounded rect:

```xml
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#080c14"/>
    <stop offset="100%" stop-color="#0d1520"/>
  </linearGradient>
</defs>

<rect width="700" height="260" fill="url(#bg)" rx="8"/>
```

> **Rule**: Inline diagrams do **not** use the `textbg` gradient or the title block. Those are cover-only elements.

---

## Subtle grid

Add a single light grid to give depth — one or two lines max. Use the same dark stroke color as covers:

```xml
<g stroke="#0d1a2a" stroke-width="1">
  <line x1="0"   y1="93"  x2="700" y2="93"/>   <!-- horizontal divider -->
  <line x1="350" y1="0"   x2="350" y2="260"/>  <!-- vertical center -->
</g>
```

Adjust line positions to match the natural divisions of your diagram (e.g. between the header label and the main content area). Never add more than two grid lines.

---

## Title / header label

Inline diagrams use a short uppercase label at the top as a caption, not a full title block. Place it at `y="22"`, centered:

```xml
<text x="350" y="22" text-anchor="middle"
      font-size="11" font-weight="600" fill="#94a3b8" letter-spacing="1">
  TOPIC — SHORT DESCRIPTION OF WHAT IS SHOWN
</text>
```

Use `fill="#94a3b8"` (slate-400) — muted but readable on the dark background. The diagram content should draw the eye, not the label.

---

## Footer caption

Optional. Two-line maximum. Place the last line at `y = height - 16`, the first line 14 px above that:

```xml
<text x="350" y="244" text-anchor="middle" font-size="9" fill="#94a3b8">
  Explanatory note about the diagram — keep to one line.
</text>
```

> **Rule**: Footer text color is `#94a3b8`, not `#334155`. Dark slate text is nearly invisible on the `#080c14` background — always use slate-400 or brighter for any text that must be readable.

---

## Zone colors

Identical to the cover guide. Use the same colors for the same zones so inline diagrams feel continuous with their cover:

| Zone | Color | Hex | Dark fill (box background) |
|------|-------|-----|---------------------------|
| Internet / ISP / WAN | Red | `#7f1d1d` stroke · `#f87171` text | `#150808` |
| Router / gateway | Blue | `#3b82f6` stroke · `#93c5fd` text | `#0e1a3a` |
| LAN / trusted | Green | `#166534` stroke · `#86efac` text | `#071810` |
| IoT / untrusted | Amber | `#92400e` stroke · `#fcd34d` text | `#1a1000` |
| VPN / encrypted | Orange | `#c2410c` stroke · `#fb923c` text | `#1a0800` |
| Security / alert | Amber-yellow | `#d97706` stroke · `#fde68a` text | `#1a1200` |

---

## Boxes

Boxes use dark fills with a 1.5px colored border and `rx="5"`:

```xml
<!-- LAN box example -->
<rect x="20" y="172" width="270" height="72" fill="#071810" stroke="#166534" stroke-width="1.5" rx="5"/>
<text x="155" y="192" text-anchor="middle" font-size="11" font-weight="600" fill="#86efac">LAN</text>
<text x="155" y="210" text-anchor="middle" font-size="9"  fill="#4ade80"  font-family="'Courier New',monospace">2001:db8:0000::/64</text>
<text x="155" y="226" text-anchor="middle" font-size="8"  fill="#166534">secondary note</text>
```

**Box typography:**

| Role | font-size | font-weight | fill |
|------|-----------|-------------|------|
| Title / name | `11` | `600` | Light variant (e.g. `#86efac`) |
| Address / value | `9` | — | Mid variant (e.g. `#4ade80`), monospace |
| Secondary note | `8` | — | Dark variant (e.g. `#166534`) |

**Box sizing:** Ensure the box is wide enough to give its label ~9 px of padding on each side. A label like "Client A" rendered at `font-size="10"` is roughly 45 px wide — it needs a box at least 63 px wide (use 64 px). Cramped boxes make text appear to touch the border.

---

## Arrows

Use the same gradient arrow pattern as covers, with `gradientUnits="userSpaceOnUse"` matching the line's exact coordinates:

```xml
<defs>
  <linearGradient id="arr-isp-gw" x1="170" y1="64" x2="258" y2="64" gradientUnits="userSpaceOnUse">
    <stop offset="0%" stop-color="#6366f1"/>   <!-- source zone color -->
    <stop offset="100%" stop-color="#3b82f6"/> <!-- destination zone color -->
  </linearGradient>
  <marker id="arr-blue" markerWidth="8" markerHeight="6" refX="7" refY="3"
          orient="auto" markerUnits="userSpaceOnUse">
    <polygon points="0,0 8,3 0,6" fill="#3b82f6"/> <!-- destination zone color -->
  </marker>
</defs>

<line x1="170" y1="64" x2="256" y2="64"
      stroke="url(#arr-isp-gw)" stroke-width="1.5" stroke-dasharray="5,3" marker-end="url(#arr-blue)"/>
```

Use `stroke-dasharray="5,3"` for conceptual/delegated flows (e.g. DHCP, tunnels). Use a solid stroke for physical or direct connections.

Arrow `stroke-width` in inline diagrams is `1.5` (covers use `2`).

### Marker sizing

Always set `markerUnits="userSpaceOnUse"` on every `<marker>`. Without it the default is `markerUnits="strokeWidth"`, which scales the arrowhead by the stroke-width — a `stroke-width="2"` line produces a marker rendered at 16 × 12 user units instead of 8 × 6, visually oversized and overlapping adjacent labels.

### Arrow direction

Always use `orient="auto"` with the **right-pointing** polygon `points="0,0 8,3 0,6"` for every marker, regardless of line direction. SVG auto-rotates the marker to match the line's direction at its endpoint — a leftward line automatically gets a leftward arrowhead. Never use `orient="auto-start-reverse"` with a manually flipped polygon; the combination produces incorrect results in most renderers.

### Arrow tips and box boundaries

The arrow tip must touch the destination box edge, not overlap into it. When using `marker-end`, the `refX` value controls how far the tip overhangs the line endpoint — set `refX="7"` so the tip sits 1 user unit past the endpoint, stopping at (not inside) the box. When using manual `<polygon>` arrowheads, place the tip coordinate exactly at the destination box's left (or right) edge:

```xml
<!-- DEVICE right edge = 110, NAT left edge = 130, gap = 20 px -->
<!-- Line ends 8 px short; polygon tip sits exactly at x=130 -->
<line x1="112" y1="80" x2="122" y2="80" stroke="url(#arr-grad)" stroke-width="1.5"/>
<polygon points="122,77 130,80 122,83" fill="#f87171"/>
```

---

## Labels on arrows

### Horizontal arrows

Place the label text **8 px above** the arrow's y coordinate (baseline = `arrow_y - 8`). A 3 px gap is too tight — the label baseline nearly touches the line stroke and is difficult to read.

```xml
<!-- Arrow at y=111 — label baseline at y=103 (8 px clearance) -->
<line x1="408" y1="111" x2="518" y2="111" stroke="#4ade80" stroke-width="1.5" marker-end="url(#arr-green)"/>
<text x="463" y="103" text-anchor="middle" font-size="9" fill="#4ade80">Commit (scalar, element)</text>
```

### Diagonal arrows

When a label sits on or near a diagonal line, always add a background rect to knock out the line behind the text. Match the fill to the background gradient color:

```xml
<!-- Draw the line first, then the label rect, then the text — order matters -->
<line x1="308" y1="92" x2="190" y2="168" stroke="url(#arr-gw-lan)" stroke-width="1.5" marker-end="url(#arr-green)"/>

<!-- Background rect — sized to wrap the text with ~4px horizontal padding -->
<rect x="148" y="122" width="64" height="14" fill="#080c14" rx="2"/>
<text x="180" y="133" text-anchor="middle" font-size="9" fill="#60a5fa">Prefix ID 0</text>
```

**Avoiding line overlap:** calculate where the diagonal line crosses the label's y-range, then ensure the rect's inner edge clears that x position by at least 6 px. Move the label toward the destination box side of the arrow, not the midpoint.

### Labels beside vertical arrows (branch / fork diagrams)

Do not place branch labels on top of vertical arrow lines. Instead position them to the side using `text-anchor="end"` (left branch) or `text-anchor="start"` (right branch):

```xml
<!-- Arrows at x=175 and x=525 — labels placed well to the side -->
<text x="100" y="192" text-anchor="end"   font-size="9" font-weight="600" fill="#4ade80">no reply received</text>
<text x="600" y="192" text-anchor="start" font-size="9" font-weight="600" fill="#f87171">NA reply received</text>
```

---

## Left / right split layouts

When the canvas is divided into two columns by a vertical divider:

- **Plan total width before coding.** Sum every block and gap on each side. A row of 4 client blocks (64 px each) + 4 contention gaps (14 px each) = 312 px — verify this fits in the available half-width before writing any coordinates.
- **All content — including time axes and labels — must stay strictly within its column.** An element that crosses the divider visually merges the two sections and makes both unreadable.
- **Center captions within their column.** A caption centered at the midpoint of the full canvas (x=350) placed in the left column will overflow into the right column. Use `x = column_center`.

---

## Labels near circles

Labels positioned inside or at the boundary of a coverage circle are visually swallowed by the circle fill or stroke. Always verify that a label is outside its circle before rendering.

To check: at the label's y coordinate, the horizontal reach of a circle centered at `(cx, cy)` with radius `r` is:

```
x_edge = cx ± sqrt(r² - (y - cy)²)
```

If the label's x falls between `cx - x_edge` and `cx + x_edge`, move the label further out. Corner positions (top-left / top-right of the canvas) are usually safe.

---

## Typography

Same font stack as covers (set on the root `<svg>` element). Per-element rules:

| Use | font-size | fill |
|-----|-----------|------|
| Header label | `11` | `#94a3b8` |
| Box title | `11` | Light zone variant |
| Box address / code | `9` | Mid zone variant, `font-family="'Courier New',monospace"` |
| Box note | `8` | Dark zone variant |
| Arrow label | `8`–`9` | Zone accent or `#94a3b8` for neutral |
| Axis / legend label | `9` | `#94a3b8` |
| Footer caption | `9` | `#94a3b8` |

> **Rule**: Never go above `font-size="12"` inside an inline diagram. These are supporting visuals, not headlines.

### Grey text on dark backgrounds

The background is `#080c14` – `#0d1520`. Use only colours that achieve ≥ 5:1 contrast:

| Color | Hex | Contrast vs `#080c14` | Use |
|-------|-----|----------------------|-----|
| slate-400 | `#94a3b8` | ~5.5 : 1 ✓ | All muted / grey text |
| slate-300 | `#cbd5e1` | ~9 : 1 ✓ | Emphasis on muted text |

**Never use** `#334155` (slate-700, ~2.5:1), `#475569` (slate-600, ~3.2:1), or `#64748b` (slate-500, ~4:1) as text fills — all are too dark to read on this background.

---

## Series accent colors

Use the same accent colors as the cover for the series this diagram belongs to. The header label and arrow labels may use the series accent; box content uses zone colors.

| Series | Accent | Hex |
|--------|--------|-----|
| Unifi | Blue / Indigo | `#818cf8` / `#60a5fa` |
| WiFi Explained | Sky 400 | `#38bdf8` |
| Traefik Essentials | Teal | `#37BEC3` |
| Ansible Essentials | Red 600 | `#dc2626` |
| Grafana Observability | Orange | `#f97316` |
| IPv6 Explained | Indigo | `#6366f1` |

---

## Checklist for new inline diagrams

- [ ] Canvas is 700 px wide; height chosen from the standard sizes (220 / 260 / 300)
- [ ] Root `<svg>` has correct `font-family` attribute
- [ ] Background is the dark navy gradient with `rx="8"`
- [ ] All gradients and markers are in a single top-level `<defs>` block
- [ ] No `textbg` gradient — that is covers only
- [ ] No title block at y=500/538 — that is covers only
- [ ] Header label at `y="22"`, `font-size="11"`, `fill="#94a3b8"`, uppercase, `letter-spacing="1"`
- [ ] No grey text uses `#334155`, `#475569`, or `#64748b` — all muted text is `#94a3b8` or brighter
- [ ] Footer text has ≥ 20 px clearance below last content element (30 px for two-line footer)
- [ ] No circle or arc extends beyond the canvas boundary
- [ ] Zone colors follow the red/blue/green/amber/orange convention from the cover guide
- [ ] Box stroke is 1.5 px (not 2 px)
- [ ] Box width provides ~9 px padding on each side of the widest label
- [ ] Arrow `stroke-width` is 1.5 (not 2)
- [ ] All `<marker>` elements include `markerUnits="userSpaceOnUse"`
- [ ] All `<marker>` elements use `orient="auto"` with the right-pointing polygon — never a manually flipped polygon
- [ ] Arrow tip (`refX="7"` or manual polygon) stops at the destination box edge, not inside it
- [ ] Gradient arrows use `gradientUnits="userSpaceOnUse"` with coordinates matching the actual line
- [ ] Arrow tip marker color matches the destination zone
- [ ] Horizontal arrow labels have baseline ≥ 8 px above the arrow line
- [ ] Vertical arrow branch labels are positioned to the side, not overlaid on the line
- [ ] Diagonal arrow labels have a `fill="#080c14"` background rect drawn before the text
- [ ] Label rects are positioned so the rect edge clears the line by ≥ 6 px
- [ ] Labels near circles are verified to be outside the circle boundary
- [ ] In split layouts, all content stays within its column; total block width calculated before coding
- [ ] All text uses light zone variants, not dark base colors
- [ ] No `<animate>` elements
- [ ] No emoji characters in `<text>` elements
