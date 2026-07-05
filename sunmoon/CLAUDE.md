# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A single-page installable PWA that shows sun and moon position, rise/set times, and phase for a given location, date, and time. No build step, no package manager, no bundler — just static files served as-is.

## Running locally

There is no npm/build tooling. Serve the directory with any static file server, e.g.:

```
python3 -m http.server 8765
```

A launch config for this already exists at `.claude/launch.json` (name `sunmoon`, port 8765) for use with the preview tool.

There are no lint or test commands/frameworks in this repo.

## Architecture

- **`index.html`** — all markup and CSS (inline `<style>` block) for the three cards: Location, Date & Time, Sun, Moon. Loads jQuery and [SunCalc](https://github.com/mourner/suncalc) from CDNs, then `app.js`. Date input is a native `<input type="date">` (no datepicker library).
- **`app.js`** — a single jQuery-driven IIFE with no modules/build step. All astronomy math is delegated to the global `SunCalc` object (`SunCalc.getPosition`, `getTimes`, `getMoonPosition`, `getMoonIllumination`, `getMoonTimes`); `app.js` only formats results and drives two hand-rolled SVG visualizations:
  - The moon icon (`#moonIcon`) draws the illuminated limb as an SVG arc path whose vertical radius encodes the illumination fraction, rotated to show the correct bright-limb angle as seen by the observer (illumination angle minus parallactic angle).
  - The sun path (`#sunPath`) samples altitude across the day (sunrise → sunset, padded by an hour on each side) and renders it as an SVG polyline, with a marker for the current sun position.
  - `state.lat` / `state.lon` hold the current location; every location or date/time change funnels through `recalculate()`, which re-renders both the Sun and Moon cards. Nothing recalculates until a location is set.
- **`sw.js`** — service worker with a stale-while-revalidate strategy (serves cached response immediately, updates cache from network in the background). Precaches the core app shell under `CACHE_NAME`. **Bump `CACHE_NAME` (e.g. `sunmoon-v6`) whenever precached files change**, so the old cache is evicted on activate.
- **`manifest.json`** — PWA manifest (name, icons, standalone display, theme colors). Icon sources live in `icons/` (`icon-source.svg` / `icon-maskable-source.svg` are the editable sources; the PNGs are generated from them).

## Conventions in this codebase

- Non-obvious geometry/astronomy logic is commented inline (e.g. terminator ellipse math, position-angle sign flips) — preserve these comments when touching that code, and add similar ones for new non-obvious math.
- Formatting/parsing helpers (`pad2`, `formatDegrees`, `formatTime`, `formatDuration`, etc.) are small pure functions defined at the top of `app.js` — reuse them rather than reformatting dates/angles inline.
