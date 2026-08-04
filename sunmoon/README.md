# Sun &amp; Moon

A small, installable web app that shows where the sun and moon are in your sky right now — elevation, azimuth, rise and set times, day length, and the current moon phase — for any location, date, and time.

**👉 Try it: [mfdutra.com/sunmoon/](https://mfdutra.com/sunmoon/)**

It works offline and can be installed to your home screen or desktop like a native app.

## Features

- **Sun card** — elevation, azimuth (with a compass arrow), sunrise, sunset, solar noon and day length, plus a plot of the sun's altitude across the day with a marker for its current position.
- **Moon card** — elevation, azimuth, moonrise, moonset, illumination percentage and phase name, with an icon that draws the illuminated limb at the correct angle as seen from where you are.
- **Sky track** — a whole-sky view of the selected day: zenith at the centre, horizon at the rim, north up and east right. Shows the body's path across the sky with hour markers, rise/set points on the horizon, and its current position. Step forward and back a day at a time.
- **Any location** — uses your device's location, or type in a latitude and longitude by hand. The last location is remembered, so the app renders instantly on the next launch.
- **Any date and time** — pick a moment to see where things were, or will be.
- **Works offline** — a service worker caches the whole app; no network needed after the first visit, and no data is sent anywhere.
- **Handles the polar cases** — at high latitudes where the sun never rises or never sets, the app says so instead of showing nonsense.

## Install

Open [mfdutra.com/sunmoon/](https://mfdutra.com/sunmoon/) and use your browser's "Install app" / "Add to Home Screen" option. It then runs standalone, without browser chrome, and works with no connection.

## Running it yourself

There's no build step, no package manager and no bundler — it's static files. Serve the directory with anything:

```bash
python3 -m http.server 8765
```

Then open <http://localhost:8765>. Note that geolocation requires a secure context, so use `localhost` (which browsers treat as secure) or serve over HTTPS.

## How it works

All the astronomy is done by [SunCalc](https://github.com/mourner/suncalc); the app formats the results and draws the two SVG visualizations by hand. jQuery and SunCalc are vendored into `vendor/` rather than loaded from a CDN, because cross-origin script responses are opaque and can't be reliably cached by the service worker — which would break offline use.

| File | Purpose |
| --- | --- |
| `index.html` | Markup and all CSS |
| `app.js` | Everything else: state, formatting, the SVG sun path and sky track |
| `sw.js` | Service worker (stale-while-revalidate, precaches the app shell) |
| `manifest.json` | PWA manifest |
| `vendor/` | Pinned copies of jQuery and SunCalc |
| `icons/` | App icons and their SVG sources |

See [CLAUDE.md](CLAUDE.md) for implementation notes, including the timezone and projection gotchas.

## License

Copyright (C) 2026 Marlon Dutra. Licensed under the GNU General Public License, version 3 or (at your option) any later version — see [LICENSE](LICENSE).

The vendored libraries keep their own licenses: jQuery is MIT (OpenJS Foundation), SunCalc is BSD-2-Clause (Vladimir Agafonkin).

## Accuracy

Positions come straight from SunCalc's algorithms and are plenty good for knowing where to look, when the light will be right, or which window the moon will pass. They are not survey-grade. The rise/set *times* shown account for atmospheric refraction (and the sun's upper limb), while the geometric horizon crossings drawn on the sky track do not — expect the two to differ by a couple of minutes.
