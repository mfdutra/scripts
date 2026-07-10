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

- **`index.html`** — all markup and CSS (inline `<style>` block) for the three cards: Location, Date & Time, Sun, Moon. Loads jQuery and [SunCalc](https://github.com/mourner/suncalc) from local vendored copies in `vendor/` (not a CDN — cross-origin CDN scripts produce opaque fetch responses that the service worker can't reliably cache, which breaks offline use), then `app.js`. Date input is a native `<input type="date">` (no datepicker library).
- **`app.js`** — a single jQuery-driven IIFE with no modules/build step. All astronomy math is delegated to the global `SunCalc` object (`SunCalc.getPosition`, `getTimes`, `getMoonPosition`, `getMoonIllumination`, `getMoonTimes`); `app.js` only formats results and drives two hand-rolled SVG visualizations. **SunCalc v2 emits all angles in degrees** (altitude, azimuth, parallacticAngle, bright-limb angle) — there is no radians conversion anywhere in `app.js`, and azimuth is already north-based clockwise (0 = N), so no `+ 180°` adjustment is needed before displaying or rotating the compass arrows.
  - The moon icon (`#moonIcon`) draws the illuminated limb as an SVG arc path whose vertical radius encodes the illumination fraction, rotated to show the correct bright-limb angle as seen by the observer (illumination angle minus parallactic angle).
  - The sun path (`#sunPath`) samples altitude across the day (sunrise → sunset, padded by an hour on each side) and renders it as an SVG polyline, with a marker for the current sun position.
  - `state.lat` / `state.lon` hold the current location; every location or date/time change funnels through `recalculate()`, which re-renders both the Sun and Moon cards. Nothing recalculates until a location is set.
  - `SunCalc.getMoonTimes(date, lat, lng)` always scans the UTC calendar day (00:00–24:00 UTC) of whatever instant `date` falls in — it cannot be shifted by a fractional-hour timezone offset, so a local civil day almost always straddles two different UTC-day buckets and a rise/set near either end of the local day can land in the "wrong" one. `moonTimesForLocalDay()` works around this by calling `getMoonTimes` once for each UTC day the local day can overlap and keeping only the event(s) that actually fall inside the local `[midnight, midnight+24h)` window. `SunCalc.getTimes` (sun) doesn't need this treatment — it derives its day boundary from the location's longitude (true local solar time) rather than truncating to UTC.
- **`sw.js`** — service worker with a stale-while-revalidate strategy (serves cached response immediately, updates cache from network in the background). Precaches the core app shell — including the vendored `vendor/jquery-*.js` and `vendor/suncalc-*.js` — under `CACHE_NAME`, bypassing the HTTP cache (`cache: "reload"`) so stale copies are never precached. Cache lookups use `ignoreSearch: true` (Android can launch the installed PWA with a query string appended), and offline navigations that miss the cache fall back to the cached `index.html`. The fetch handler must never resolve `respondWith()` with `undefined` — that renders the browser's own offline error page. **Bump `CACHE_NAME` (e.g. `sunmoon-v14`) whenever precached files change**, so the old cache is evicted on activate. The `<footer id="appFooter">` in `index.html` displays this value — `app.js` fetches it at runtime from the active service worker over a `MessageChannel` (`GET_VERSION` request handled by the `message` listener in `sw.js`), so `CACHE_NAME` never needs to be duplicated elsewhere.
- **`vendor/`** — local copies of third-party libraries (jQuery, SunCalc), pinned to specific versions and checked in so the app has no runtime CDN dependency. Loading these from a CDN instead would break offline use, since cross-origin `<script>` fetches (opaque responses) can't be cached by the service worker's `response.ok` check. `vendor/suncalc-2.0.0.js` is the UMD bundle built from the upstream ESM source (`npm run build` in a checkout of [mourner/suncalc](https://github.com/mourner/suncalc), via its rolldown config) — SunCalc's source itself is ESM-only starting with v2, so the browser-global build has to be produced rather than copied directly. To upgrade, rebuild that bundle from the new version and swap the file (renaming to match), then update the `<script>` src in `index.html`, the precache list in `sw.js`, and bump `CACHE_NAME`.
- **`manifest.json`** — PWA manifest (name, icons, standalone display, theme colors). Icon sources live in `icons/` (`icon-source.svg` / `icon-maskable-source.svg` are the editable sources; the PNGs are generated from them).

## Conventions in this codebase

- Non-obvious geometry/astronomy logic is commented inline (e.g. terminator ellipse math, position-angle sign flips) — preserve these comments when touching that code, and add similar ones for new non-obvious math.
- Formatting/parsing helpers (`pad2`, `formatDegrees`, `formatTime`, `formatDuration`, etc.) are small pure functions defined at the top of `app.js` — reuse them rather than reformatting dates/angles inline.
