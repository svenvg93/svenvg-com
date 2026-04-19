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

**Dark navy (Traefik, Smokeping, neutral)**
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

---

## Series accent colors

Each series has one accent color used for: series label text, primary glows, key UI elements.

| Series | Color | Hex |
|--------|-------|-----|
| WiFi Explained | Sky 400 | `#38bdf8` |
| Traefik Essentials | Teal | `#37BEC3` |
| Smokeping Essentials | Sky 500 | `#0ea5e9` |
| Ansible Essentials | Red 600 | `#dc2626` |

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

## Checklist for new covers

- [ ] Canvas is exactly 1200×630
- [ ] Root `<svg>` has correct `font-family` attribute
- [ ] All gradients and markers are inside a single top-level `<defs>` block
- [ ] `textbg` gradient rect is at `y="390"` with `height="240"`
- [ ] All diagram content ends above `y=390`
- [ ] Series label: `x="600" y="500"`, `font-size="13"`, `letter-spacing="3"`, `font-weight="600"`, correct series accent color
- [ ] Post title: `x="600" y="538"`, `font-size="34"`, `font-weight="700"`, `fill="#f1f5f9"`
- [ ] No `<animate>` elements
- [ ] No emoji characters in `<text>` elements
- [ ] No second `<defs>` block
