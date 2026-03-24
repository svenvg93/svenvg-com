---
title: Speedtest Server Explorer
date: 2026-03-01T15:21:19Z
description: A searchable web interface for discovering Speedtest servers worldwide, built with React and Cloudflare Workers.
summary: Browse and discover Ookla Speedtest servers by ISP, city, or country with geolocation-aware results and one-click speed tests.
featured: true
tags:
  - typescript
  - cloudflare
  - ookla
categories:
  - projects
cover: cover.jpg
status: "completed"
link: https://speedtest-server-explorer.svenvanginkel.workers.dev/
---

## Project Overview

Ookla Server Explorer is a web application for browsing and discovering Speedtest servers worldwide. It provides a clean, searchable interface to explore servers by ISP, city, or country — and launch a speed test directly from the app.

The idea came from wanting a better way to find and compare Speedtest servers without having to dig through the Speedtest interface itself. I wanted something fast, filterable, and shareable.

## Features

- **Search by ISP, operator, or city** — the first search term queries the Speedtest API, additional words apply client-side filtering
- **Interactive data table** — sortable, filterable, and paginated server listings powered by TanStack Table
- **Server details panel** — side sheet showing host info, coordinates, HTTPS status, and map links
- **Geolocation-aware results** — uses your IP location via Cloudflare's edge network to surface nearby servers first
- **Shareable URLs** — filter and sort state is synced to the URL so you can share a specific view
- **Dark/light mode** — system preference detection with a manual toggle
- **Keyboard shortcut** — press `/` to focus the search input instantly

## Technologies Used

| Component | Technology |
|-----------|------------|
| Frontend | React 18, TypeScript, Vite |
| UI | shadcn/ui, Tailwind CSS |
| Table | TanStack Table v8 |
| Backend | Cloudflare Workers |
| Deployment | Wrangler |

The backend is a lightweight Cloudflare Worker that proxies the Speedtest API. Because the worker runs at the edge, it can read the user's geolocation from Cloudflare's request headers and use that to sort results by proximity — no GPS or browser permissions needed.

In production, static assets are served through the same worker, so there's only one deployment to manage.

## Challenges and Solutions

**CORS and API proxying** — The Speedtest API doesn't allow direct browser requests, so all API calls go through the Cloudflare Worker. This also gave a natural place to inject geolocation data without needing any client-side location APIs.

**Search UX** — A single search term that hits the API is fast, but narrowing results further (e.g., filtering by city within an ISP search) needed to stay snappy. Splitting into an API query for the first term and client-side filtering for the rest kept it responsive without extra round trips.

**State in the URL** — Keeping filters, sort state, and pagination in the URL params required some care to avoid infinite re-renders and to handle edge cases like invalid or missing params on load.


> **Disclaimer**: This tool is not affiliated with, endorsed by, or connected to Ookla, LLC or Speedtest.net.
