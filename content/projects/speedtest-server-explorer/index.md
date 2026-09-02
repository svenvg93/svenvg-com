---
title: "Speedtest Server Explorer"
date: 2026-04-18
draft: false
slug: speedtest-server-explorer
description: "A searchable, interactive interface for exploring Speedtest's global server network"
summary: "Search Speedtest's public server network by ISP, operator, or city, inspect any server, and launch a test in one click. Built on React and a Cloudflare Worker that returns geolocation-aware, proximity-sorted results."
featured: true
tags:
  - React
  - TypeScript
  - Cloudflare Workers
categories:
  - projects
cover: ""
link: "https://speedtest-server-explorer.svenvanginkel.workers.dev/"
status: "completed"
---

## Project Overview

Speedtest Server Explorer is a web app that puts a searchable, sortable interface on top of Speedtest's public server network. Speedtest.net picks a server for you and offers little visibility into the rest. This tool exposes the full list so you can find servers by ISP, operator, or city, inspect the details of any one of them, and launch a test against it directly.

Requests go through a Cloudflare Worker that proxies the Speedtest API and reads geolocation data from Cloudflare's edge network, so results come back sorted by proximity to wherever you actually are rather than from a single central location.

- **Live app:** [speedtest-server-explorer.svenvanginkel.workers.dev](https://speedtest-server-explorer.svenvanginkel.workers.dev/)
- **Source:** [github.com/svenvg93/speedtest-server-explorer](https://github.com/svenvg93/speedtest-server-explorer)

## Key Features

- **Search by ISP, operator, or city** — the first word of the query hits the Speedtest API, and any additional terms are applied as a local filter on top of the results
- **Interactive server table** — sorting, filtering, and pagination powered by TanStack Table v8
- **Geolocation-aware results** — the Cloudflare Worker uses edge geolocation to return servers near you, sorted by distance
- **Server detail panel** — host, coordinates, HTTPS support, and links out to a map for any selected server
- **One-click speed testing** — jump straight to the Speedtest test page for a specific server
- **Shareable views** — filters and table state are persisted in URL parameters, so a filtered view can be copied and shared
- **Dark and light themes** — a manual toggle that also respects system preference
- **Keyboard accessible** — press <kbd>/</kbd> to focus the search field

## Technologies Used

- **Frontend:** React 18, TypeScript, Vite
- **UI:** shadcn/ui, Tailwind CSS
- **Table:** TanStack Table v8
- **Backend / proxy:** Cloudflare Workers, deployed with Wrangler

## Architecture

The browser never calls the Speedtest API directly. Instead:

1. The React app sends the search query to a Cloudflare Worker.
2. The Worker attaches geolocation data from Cloudflare's edge network and forwards the request to the Speedtest API.
3. The Speedtest API returns servers ordered by proximity to the request's location.
4. The Worker passes the results back to the app, which handles any additional multi-word filtering, sorting, and pagination client-side.

This keeps the app "local-first" in feel — results reflect the user's real location — without shipping API credentials or CORS workarounds to the client.

## Running It Locally

```bash
npm install

# Frontend dev server
npm run dev

# Cloudflare Worker (in a second terminal)
npm run worker:dev
```

Deployment builds the frontend and ships the Worker together:

```bash
npm run deploy
```

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Ookla, LLC or Speedtest.net. It uses the publicly available Speedtest API.
