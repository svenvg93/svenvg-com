---
title: SmokePing Generator
date: 2026-03-15T00:00:00Z
description: A browser-based visual editor for generating SmokePing configuration files without manual coding.
summary: Build and export SmokePing configs through a visual interface — define probes, targets, and dual-stack hosts, then copy the result straight into your setup.
featured: true
tags:
  - typescript
  - react
  - github
categories:
  - projects
cover: cover.jpg
status: "completed"
link: https://svenvg93.github.io/smokeping-generator
---

## Project Overview

SmokePing Generator is a browser-based visual editor for creating SmokePing configuration files. Instead of hand-writing the config with the right indentation and syntax, you build your monitoring setup through a structured UI and export a ready-to-use config file.

The motivation was simple: SmokePing is a great tool for tracking network latency over time, but its configuration format is tedious to write and easy to get wrong. I wanted something that let me define probes and targets visually and just copy out the result.

## Features

- **Visual hierarchy builder** — construct Section → Group → Target structures with drag-and-drop reordering
- **Dual-stack support** — configure separate IPv4 and IPv6 hosts per target, with optional combined charting
- **Probe types** — FPing, DNS, HTTP, Curl, TCPPing, and custom binaries
- **Configuration import** — load an existing SmokePing config file to edit it in the UI
- **Real-time preview** — the configuration tab updates instantly as you make changes
- **Persistent storage** — work is automatically saved to localStorage across sessions

## Technologies Used

| Component | Technology |
|-----------|------------|
| Frontend | React 19, TypeScript, Vite |
| UI | shadcn/ui, Tailwind CSS |
| Deployment | GitHub Pages, GitHub Actions |

## How It Works

1. Set global options — default probe, title, and labels
2. Define your probe types in the Probes section
3. Build out monitoring targets in the Targets section
4. Copy the generated config from the Configuration tab
5. Optionally import an existing SmokePing file to edit it
