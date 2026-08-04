$(function () {
  "use strict";

  const MOON_PHASES = [
    { max: 0.02, name: "New Moon" },
    { max: 0.25, name: "Waxing Crescent" },
    { max: 0.27, name: "First Quarter" },
    { max: 0.48, name: "Waxing Gibbous" },
    { max: 0.52, name: "Full Moon" },
    { max: 0.73, name: "Waning Gibbous" },
    { max: 0.75, name: "Last Quarter" },
    { max: 0.98, name: "Waning Crescent" },
    { max: 1.01, name: "New Moon" },
  ];

  const state = {
    lat: null,
    lon: null,
  };

  const $ = window.jQuery;

  const pad2 = (n) => String(n).padStart(2, "0");

  const toDateInputValue = (d) =>
    [d.getFullYear(), pad2(d.getMonth() + 1), pad2(d.getDate())].join("-");

  const toTimeInputValue = (d) =>
    [pad2(d.getHours()), pad2(d.getMinutes())].join(":");

  const currentSelectedDate = () => {
    const dateStr = $("#dateInput").val();
    const timeStr = $("#timeInput").val() || "00:00";
    const [year, month, day] = dateStr.split("-").map(Number);
    const [hours, minutes] = timeStr.split(":").map(Number);
    return new Date(year, month - 1, day, hours, minutes, 0, 0);
  };

  const localMidnightOf = (date) =>
    new Date(date.getFullYear(), date.getMonth(), date.getDate());

  const isSameLocalDay = (a, b) =>
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate();

  // SunCalc.getTimes picks its sunrise/sunset day from the UTC calendar day of the
  // instant it's given, not the local one — passing the exact selected time means that
  // once local time-of-day has rolled past the UTC day boundary (e.g. after 17:00 in
  // Pacific time), it silently returns tomorrow's sunrise/sunset. Anchoring to local
  // noon picks the right calendar day for any realistic timezone offset.
  const sunTimesForLocalDay = (date, lat, lon) =>
    SunCalc.getTimes(
      new Date(date.getFullYear(), date.getMonth(), date.getDate(), 12),
      lat,
      lon
    );

  // SunCalc.getMoonTimes always scans the UTC calendar day (00:00-24:00 UTC) of whatever
  // Date it's given — it can't be shifted by a fractional-hour timezone offset. So the
  // local civil day (e.g. 00:00-24:00 PDT) generally straddles two different UTC days;
  // an event near either end of the local day can land in either bucket. Probe both UTC
  // days the local window can overlap, then keep only the rise/set that actually falls
  // inside the local window.
  const moonTimesForLocalDay = (date, lat, lon) => {
    const start = localMidnightOf(date);
    const end = new Date(start.getTime() + 24 * 60 * 60 * 1000);
    const inWindow = (d) => d instanceof Date && d >= start && d < end;

    const candidates = [
      SunCalc.getMoonTimes(start, lat, lon),
      SunCalc.getMoonTimes(new Date(end.getTime() - 1), lat, lon),
    ];

    return {
      rise: candidates.map((t) => t.rise).find(inWindow),
      set: candidates.map((t) => t.set).find(inWindow),
    };
  };

  const setNow = () => {
    const now = new Date();
    $("#dateInput").val(toDateInputValue(now));
    $("#timeInput").val(toTimeInputValue(now));
  };

  const formatDegrees = (deg) => `${deg.toFixed(1)}°`;

  const normalizeAngle = (deg) => {
    const wrapped = ((deg + 180) % 360 + 360) % 360;
    return wrapped - 180;
  };

  const formatTime = (date) =>
    date instanceof Date && !isNaN(date)
      ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false })
      : "N/A";

  const formatDuration = (ms) => {
    if (isNaN(ms) || ms <= 0) return "N/A";
    const totalMinutes = Math.round(ms / 60000);
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return `${hours}h ${pad2(minutes)}m`;
  };

  const moonPhaseInfo = (fraction) =>
    MOON_PHASES.find((phase) => fraction <= phase.max) ||
    MOON_PHASES[MOON_PHASES.length - 1];

  const LOCATION_STORAGE_KEY = "sunmoon.lastLocation";

  // localStorage can throw (private browsing, quota, disabled storage) — a cache
  // miss just means we fall back to the normal "requesting your location" flow.
  const loadCachedLocation = () => {
    try {
      const { lat, lon } = JSON.parse(localStorage.getItem(LOCATION_STORAGE_KEY));
      return typeof lat === "number" && typeof lon === "number" ? { lat, lon } : null;
    } catch (e) {
      return null;
    }
  };

  const saveCachedLocation = (lat, lon) => {
    try {
      localStorage.setItem(LOCATION_STORAGE_KEY, JSON.stringify({ lat, lon }));
    } catch (e) {
      // ignore — nothing to fall back to next launch, but this launch is unaffected
    }
  };

  // kind: undefined (normal), "error", or "pending" (background refresh in progress)
  const setLocationStatus = (text, kind) => {
    $("#locationStatus")
      .text(text)
      .toggleClass("error", kind === "error")
      .toggleClass("pending", kind === "pending");
  };

  const showManualLocation = () => {
    $("#manualLocation").show();
  };

  const setLocation = (lat, lon, statusText, statusKind) => {
    state.lat = lat;
    state.lon = lon;
    $("#latInput").val(lat.toFixed(6));
    $("#lonInput").val(lon.toFixed(6));
    saveCachedLocation(lat, lon);
    setLocationStatus(statusText || `Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}`, statusKind);
    recalculate();
  };

  // isBackground: true when refreshing a location that's already cached/displayed —
  // failures then keep showing the cached position instead of blocking on an error.
  const requestGeolocation = (isBackground) => {
    if (!navigator.geolocation) {
      if (!isBackground) {
        setLocationStatus("Geolocation not supported by this browser. Enter coordinates manually.", "error");
        showManualLocation();
      }
      return;
    }
    if (isBackground) {
      setLocationStatus(
        `Using last known location: ${state.lat.toFixed(4)}, ${state.lon.toFixed(4)} — refreshing…`,
        "pending"
      );
    } else {
      setLocationStatus("Requesting your location…");
    }
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation(position.coords.latitude, position.coords.longitude);
      },
      () => {
        if (isBackground) {
          setLocationStatus(
            `Using last known location: ${state.lat.toFixed(4)}, ${state.lon.toFixed(4)}. Could not refresh — enter coordinates manually if this is wrong.`,
            "error"
          );
        } else {
          setLocationStatus("Location permission denied or unavailable. Enter coordinates manually.", "error");
        }
        showManualLocation();
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
    );
  };

  const useManualLocation = () => {
    const lat = parseFloat($("#latInput").val());
    const lon = parseFloat($("#lonInput").val());
    if (isNaN(lat) || isNaN(lon) || lat < -90 || lat > 90 || lon < -180 || lon > 180) {
      setLocationStatus("Enter a valid latitude (-90 to 90) and longitude (-180 to 180).", true);
      return;
    }
    setLocation(lat, lon);
  };

  const MOON_ICON_CENTER = 50;
  const MOON_ICON_RADIUS = 40;

  const updateMoonIcon = (fraction, localLimbAngleDeg) => {
    const R = MOON_ICON_RADIUS;
    const left = MOON_ICON_CENTER - R;
    const right = MOON_ICON_CENTER + R;
    // The terminator (day/night line) is a great circle on the moon's sphere,
    // which projects as an ellipse when viewed from Earth: its vertical radius
    // shrinks to 0 at half moon and grows back to R at full/new moon.
    const terminatorRadius = R * Math.abs(1 - 2 * fraction);
    const sweep = fraction < 0.5 ? 0 : 1;
    const path = `M ${left} ${MOON_ICON_CENTER} A ${R} ${R} 0 0 1 ${right} ${MOON_ICON_CENTER} A ${R} ${terminatorRadius} 0 0 ${sweep} ${left} ${MOON_ICON_CENTER}`;
    $("#moonIconBright").attr("d", path);
    // Astronomical position angles run eastward from north, which renders to the
    // viewer's left (you're looking up at the sky, not down at a map), so the
    // angle is negated here to get the correct on-screen rotation direction.
    const svgRotationDeg = -localLimbAngleDeg;
    $("#moonIconBulge").attr("transform", `rotate(${svgRotationDeg} ${MOON_ICON_CENTER} ${MOON_ICON_CENTER})`);
  };

  const SUN_PATH_WIDTH = 300;
  const SUN_PATH_HORIZON_Y = 100;
  const SUN_PATH_TOP_MARGIN = 14;
  const SUN_PATH_SAMPLE_COUNT = 48;
  const SUN_PATH_BUFFER_MS = 60 * 60 * 1000;

  const hideSunPath = () => {
    $("#sunArc").attr("d", "");
    $("#sunMarker, #sunDotRise, #sunDotSet, #sunDotRiseFar, #sunDotSetFar").attr("opacity", 0);
  };

  const renderSunPath = (date, lat, lon, times, currentAltitudeDeg) => {
    const hasValidWindow =
      times.sunrise instanceof Date && !isNaN(times.sunrise) &&
      times.sunset instanceof Date && !isNaN(times.sunset);

    // At high latitudes SunCalc.getTimes has no sunrise/sunset to report and sets
    // alwaysUp/alwaysDown instead. During polar night there's nothing to plot, but
    // during polar day the sun is up the whole time — fall back to the full local
    // calendar day instead of hiding the path.
    if (!hasValidWindow && !times.alwaysUp) {
      hideSunPath();
      return;
    }

    const startTime = hasValidWindow
      ? times.sunrise.getTime() - SUN_PATH_BUFFER_MS
      : new Date(date.getFullYear(), date.getMonth(), date.getDate()).getTime();
    const endTime = hasValidWindow ? times.sunset.getTime() + SUN_PATH_BUFFER_MS : startTime + 24 * 60 * 60 * 1000;
    const span = endTime - startTime;

    const altitudeDegAt = (t) => SunCalc.getPosition(new Date(t), lat, lon).altitude;

    const samples = Array.from({ length: SUN_PATH_SAMPLE_COUNT + 1 }, (_, i) => {
      const t = startTime + (span * i) / SUN_PATH_SAMPLE_COUNT;
      return { t, altitudeDeg: altitudeDegAt(t) };
    });

    const maxAltitude = Math.max(...samples.map((s) => s.altitudeDeg), 1);
    const scale = (SUN_PATH_HORIZON_Y - SUN_PATH_TOP_MARGIN) / maxAltitude;

    const xForTime = (t) => (SUN_PATH_WIDTH * (t - startTime)) / span;
    const yForAltitude = (deg) => SUN_PATH_HORIZON_Y - deg * scale;

    const pathData = samples
      .map((s, i) => `${i === 0 ? "M" : "L"} ${xForTime(s.t).toFixed(1)} ${yForAltitude(s.altitudeDeg).toFixed(1)}`)
      .join(" ");
    $("#sunArc").attr("d", pathData);

    if (hasValidWindow) {
      const farOffsetMs = SUN_PATH_BUFFER_MS * 0.7;
      $("#sunDotRise").attr({ cx: xForTime(times.sunrise.getTime()), cy: SUN_PATH_HORIZON_Y, opacity: 0.6 });
      $("#sunDotSet").attr({ cx: xForTime(times.sunset.getTime()), cy: SUN_PATH_HORIZON_Y, opacity: 0.6 });
      $("#sunDotRiseFar").attr({
        cx: xForTime(times.sunrise.getTime() - farOffsetMs),
        cy: yForAltitude(altitudeDegAt(times.sunrise.getTime() - farOffsetMs)),
        opacity: 0.3,
      });
      $("#sunDotSetFar").attr({
        cx: xForTime(times.sunset.getTime() + farOffsetMs),
        cy: yForAltitude(altitudeDegAt(times.sunset.getTime() + farOffsetMs)),
        opacity: 0.3,
      });
    } else {
      // Polar day: there's no rise/set event to mark.
      $("#sunDotRise, #sunDotSet, #sunDotRiseFar, #sunDotSetFar").attr("opacity", 0);
    }

    const now = date.getTime();
    const isWithinWindow = now >= startTime && now <= endTime;
    $("#sunMarker").attr({
      cx: xForTime(Math.min(Math.max(now, startTime), endTime)),
      cy: yForAltitude(currentAltitudeDeg),
      opacity: isWithinWindow ? 1 : 0,
    });
  };

  const renderSun = (date, lat, lon) => {
    const position = SunCalc.getPosition(date, lat, lon);
    const times = sunTimesForLocalDay(date, lat, lon);
    const dayLengthMs = times.sunset - times.sunrise;

    $("#sunElevation").text(formatDegrees(position.altitude)).toggleClass("negative", position.altitude < 0);
    $("#sunAzimuth").text(formatDegrees(position.azimuth));
    $("#sunAzimuthArrow").css("transform", `rotate(${position.azimuth}deg)`);
    $("#sunrise").text(formatTime(times.sunrise));
    $("#sunset").text(formatTime(times.sunset));
    $("#solarNoon").text(formatTime(times.solarNoon));
    $("#dayLength").text(formatDuration(dayLengthMs));
    renderSunPath(date, lat, lon, times, position.altitude);
  };

  const renderMoon = (date, lat, lon) => {
    const position = SunCalc.getMoonPosition(date, lat, lon);
    const illumination = SunCalc.getMoonIllumination(date);
    const times = moonTimesForLocalDay(date, lat, lon);
    const phase = moonPhaseInfo(illumination.phase);
    // illumination.angle is the bright limb's position angle from celestial north,
    // independent of the observer; subtracting the parallactic angle expresses it
    // relative to the observer's local zenith ("up"), matching what's actually seen.
    const localLimbAngle = normalizeAngle(illumination.angle - position.parallacticAngle);

    $("#moonElevation").text(formatDegrees(position.altitude)).toggleClass("negative", position.altitude < 0);
    $("#moonAzimuth").text(formatDegrees(position.azimuth));
    $("#moonAzimuthArrow").css("transform", `rotate(${position.azimuth}deg)`);
    $("#moonrise").text(times.rise ? formatTime(times.rise) : "None today");
    $("#moonset").text(times.set ? formatTime(times.set) : "None today");
    $("#moonIllumination").text(`${(illumination.fraction * 100).toFixed(0)}%`);
    $("#moonPhase").text(phase.name);
    updateMoonIcon(illumination.fraction, localLimbAngle);
  };

  // ---- Sky track overlay -------------------------------------------------
  // Whole-sky plot as seen looking straight up: zenith at the centre of the disc,
  // horizon at the rim.

  const SKY_CENTER = 160;
  const SKY_RADIUS = 132;
  const SKY_SAMPLE_MINUTES = 2;
  const SKY_BISECT_STEPS = 20;
  const SKY_HOUR_LABEL_LIMIT = 10;
  const DAY_MS = 24 * 60 * 60 * 1000;

  // Altitude maps linearly to radius, so the zenith collapses to the centre and
  // the horizon lands exactly on the rim.
  const skyRadiusForAltitude = (altitudeDeg) => (SKY_RADIUS * (90 - altitudeDeg)) / 90;

  // North up, east right — the map/compass orientation, which is the mirror of the
  // star-chart view you'd get lying on your back (there east falls to the left). It
  // makes the track run clockwise. SunCalc azimuth is already north-based clockwise,
  // which is also the screen's clockwise direction, so it needs no adjustment here.
  const skyPolar = (radius, azimuthDeg) => {
    const rad = (azimuthDeg * Math.PI) / 180;
    return {
      x: SKY_CENTER + radius * Math.sin(rad),
      y: SKY_CENTER - radius * Math.cos(rad),
    };
  };

  const skyPoint = (altitudeDeg, azimuthDeg) =>
    skyPolar(skyRadiusForAltitude(altitudeDeg), azimuthDeg);

  const SKY_BODIES = {
    sun: {
      label: "Sun",
      color: "#ffd166",
      position: (date, lat, lon) => SunCalc.getPosition(date, lat, lon),
      times: (date, lat, lon) => {
        const times = sunTimesForLocalDay(date, lat, lon);
        return { rise: times.sunrise, set: times.sunset };
      },
    },
    moon: {
      label: "Moon",
      color: "#eef1f8",
      position: (date, lat, lon) => SunCalc.getMoonPosition(date, lat, lon),
      times: moonTimesForLocalDay,
    },
  };

  // Refine a horizon crossing bracketed by two samples down to sub-second precision,
  // so a drawn segment ends exactly on the rim instead of one sample short of it.
  const skyHorizonCrossing = (positionAt, belowTime, aboveTime) => {
    const bounds = Array.from({ length: SKY_BISECT_STEPS }).reduce(
      (b) => {
        const mid = (b.below + b.above) / 2;
        return positionAt(mid).altitude < 0
          ? { below: mid, above: b.above }
          : { below: b.below, above: mid };
      },
      { below: belowTime, above: aboveTime }
    );
    const t = (bounds.below + bounds.above) / 2;
    // Pin altitude to 0 rather than using the sampled value, which is only near-zero.
    return { t, altitude: 0, azimuth: positionAt(t).azimuth, isCrossing: true };
  };

  const sampleSkyTrack = (date, lat, lon, body) => {
    const start = localMidnightOf(date).getTime();
    const stepMs = SKY_SAMPLE_MINUTES * 60000;
    const positionAt = (t) => {
      const position = body.position(new Date(t), lat, lon);
      return { t, altitude: position.altitude, azimuth: position.azimuth };
    };

    const samples = Array.from({ length: DAY_MS / stepMs + 1 }, (_, i) =>
      positionAt(start + i * stepMs)
    );

    // Insert a refined crossing wherever consecutive samples straddle the horizon.
    const points = samples.flatMap((sample, i) => {
      const prev = samples[i - 1];
      if (!prev || prev.altitude < 0 === sample.altitude < 0) return [sample];
      const rising = prev.altitude < 0;
      return [
        skyHorizonCrossing(
          positionAt,
          rising ? prev.t : sample.t,
          rising ? sample.t : prev.t
        ),
        sample,
      ];
    });

    // Split into above-horizon runs: the moon can rise and set twice in one local day.
    const segments = points
      .reduce(
        (acc, point) => {
          const current = acc[acc.length - 1];
          if (point.altitude < 0) {
            if (current.length) acc.push([]);
            return acc;
          }
          current.push(point);
          return acc;
        },
        [[]]
      )
      .filter((segment) => segment.length > 1);

    return {
      segments,
      crossings: points.filter((point) => point.isCrossing),
      peak: samples.reduce((best, s) => (s.altitude > best.altitude ? s : best)),
    };
  };

  const skyTrackMarkup = (segments, color) =>
    segments
      .map((segment) => {
        const d = segment
          .map((point, i) => {
            const { x, y } = skyPoint(point.altitude, point.azimuth);
            return `${i === 0 ? "M" : "L"} ${x.toFixed(1)} ${y.toFixed(1)}`;
          })
          .join(" ");
        return `<path d="${d}" fill="none" stroke="${color}" stroke-width="2.5" stroke-opacity="0.7" stroke-linecap="round"/>`;
      })
      .join("");

  const skyHoursMarkup = (date, lat, lon, body) => {
    const midnight = localMidnightOf(date);
    const hours = Array.from({ length: 24 }, (_, hour) => {
      const at = new Date(midnight.getTime() + hour * 60 * 60 * 1000);
      const position = body.position(at, lat, lon);
      return { hour, altitude: position.altitude, azimuth: position.azimuth };
    }).filter((h) => h.altitude >= 0);

    // A long summer day would smear into an unreadable strip of labels.
    const step = hours.length > SKY_HOUR_LABEL_LIMIT ? 2 : 1;

    return hours
      .filter((h) => h.hour % step === 0)
      .map((h) => {
        const tick = skyPoint(h.altitude, h.azimuth);
        const radius = skyRadiusForAltitude(h.altitude);
        // Offset the label away from the rim so it never spills outside the disc.
        const labelRadius = radius < SKY_RADIUS - 26 ? radius + 15 : radius - 15;
        const label = skyPolar(labelRadius, h.azimuth);
        return (
          `<circle cx="${tick.x.toFixed(1)}" cy="${tick.y.toFixed(1)}" r="2.5" fill="#9fb3ff"/>` +
          `<text x="${label.x.toFixed(1)}" y="${label.y.toFixed(1)}" font-size="11" fill="#8ea0d0" text-anchor="middle" dominant-baseline="middle">${pad2(h.hour)}</text>`
        );
      })
      .join("");
  };

  // Label the altitude rings on the side opposite the track's high point — that's
  // where the track is furthest away, so the labels can't end up underneath it.
  const skyRingLabelsMarkup = (peakAzimuthDeg) =>
    [30, 60]
      .map((altitude) => {
        const { x, y } = skyPoint(altitude, peakAzimuthDeg + 180);
        return `<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" font-size="10" fill="#5a6a9a" text-anchor="middle" dominant-baseline="middle">${altitude}&#176;</text>`;
      })
      .join("");

  const skyCrossingsMarkup = (crossings, color) =>
    crossings
      .map((crossing) => {
        const { x, y } = skyPoint(crossing.altitude, crossing.azimuth);
        return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4.5" fill="${color}" stroke="#0f1626" stroke-width="1.5"/>`;
      })
      .join("");

  const skyMarkerMarkup = (position, color) => {
    if (position.altitude < 0) return "";
    const { x, y } = skyPoint(position.altitude, position.azimuth);
    return `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="7" fill="${color}" filter="url(#skyGlow)"/>`;
  };

  // Which body the overlay is showing, or null when it's closed.
  let skyBody = null;

  const renderSkyTrack = () => {
    if (!skyBody || state.lat === null || state.lon === null) return;
    const body = SKY_BODIES[skyBody];
    const lat = state.lat;
    const lon = state.lon;
    const date = currentSelectedDate();
    const track = sampleSkyTrack(date, lat, lon, body);
    const times = body.times(date, lat, lon);
    const position = body.position(date, lat, lon);
    // The marker means "where it is right now", so it only makes sense on today's
    // track — on any other day there is no current position to point at.
    const showMarker = isSameLocalDay(date, new Date());

    $("#skyTitle").text(`${body.label} track`);
    $("#skySubtitle").text(
      `${date.toLocaleDateString()} · ${lat.toFixed(4)}, ${lon.toFixed(4)}`
    );

    // innerHTML on an SVG element parses in the SVG namespace; jQuery's .html()
    // routes through an HTML parser, which would strip these shapes.
    $("#skyDynamic")[0].innerHTML = [
      skyRingLabelsMarkup(track.peak.azimuth),
      skyTrackMarkup(track.segments, body.color),
      skyHoursMarkup(date, lat, lon, body),
      skyCrossingsMarkup(track.crossings, body.color),
      showMarker ? skyMarkerMarkup(position, body.color) : "",
    ].join("");

    // Rise/set text comes from SunCalc (which allows for refraction and, for the sun,
    // the upper limb) while the rim dots sit on the geometric altitude = 0 crossing —
    // the two differ by a couple of minutes.
    $("#skyRise").text(times.rise ? formatTime(times.rise) : "None");
    $("#skySet").text(times.set ? formatTime(times.set) : "None");
    $("#skyPeak")
      .text(formatDegrees(track.peak.altitude))
      .toggleClass("negative", track.peak.altitude < 0);
    $("#skyPeakTime").text(formatTime(new Date(track.peak.t)));

    // The second note explains a missing marker, so it's only relevant when a marker
    // would have been drawn at all.
    const note = !track.segments.length
      ? `The ${body.label.toLowerCase()} stays below the horizon all day.`
      : showMarker && position.altitude < 0
      ? `The ${body.label.toLowerCase()} is below the horizon at the selected time.`
      : "";
    $("#skyNote").text(note);
  };

  // Day arithmetic via the Date constructor's overflow handling, so month/year
  // boundaries and DST-shortened days take care of themselves.
  const shiftSelectedDay = (days) => {
    const date = currentSelectedDate();
    const shifted = new Date(
      date.getFullYear(),
      date.getMonth(),
      date.getDate() + days
    );
    $("#dateInput").val(toDateInputValue(shifted));
    recalculate();
  };

  const openSkyTrack = (bodyKey) => {
    const wasOpen = skyBody !== null;
    skyBody = bodyKey;
    $("#skyOverlay").removeClass("hidden");
    // A history entry makes the Android back button close the overlay instead of
    // leaving the app, which is the only way out in standalone PWA mode. Only one
    // entry per opening, so a single back always unwinds it exactly.
    if (!wasOpen) history.pushState({ skyOverlay: true }, "");
    renderSkyTrack();
  };

  const closeSkyTrack = () => {
    if (!skyBody) return;
    skyBody = null;
    $("#skyOverlay").addClass("hidden");
  };

  // Unwind our own history entry so back/close leave the stack as we found it;
  // popstate then does the actual closing.
  const dismissSkyTrack = () => {
    if (history.state && history.state.skyOverlay) history.back();
    else closeSkyTrack();
  };

  const recalculate = () => {
    if (state.lat === null || state.lon === null) return;
    const date = currentSelectedDate();
    renderSun(date, state.lat, state.lon);
    renderMoon(date, state.lat, state.lon);
    renderSkyTrack();
    const dateLabel = date.toLocaleDateString();
    const timeLabel = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    $("#calcNote")
      .removeClass("hidden")
      .text(`Calculated for ${dateLabel} ${timeLabel}`);
  };

  $("#useLocationBtn").on("click", () => requestGeolocation(false));
  $("#enterManualBtn").on("click", showManualLocation);
  $("#useManualBtn").on("click", useManualLocation);
  $("#nowBtn, #skyTodayBtn").on("click", () => {
    setNow();
    recalculate();
  });
  $("#dateInput").on("change", recalculate);
  $("#timeInput").on("change", recalculate);
  $("[data-sky]").on("click", function () {
    openSkyTrack($(this).data("sky"));
  });
  $("#skyCloseBtn").on("click", dismissSkyTrack);
  $("#skyPrevDay").on("click", () => shiftSelectedDay(-1));
  $("#skyNextDay").on("click", () => shiftSelectedDay(1));
  $(window).on("popstate", closeSkyTrack);
  $(document).on("keydown", (event) => {
    if (event.key === "Escape") dismissSkyTrack();
  });

  // Refresh to the current date/time whenever the app returns to the foreground
  // (e.g. after being backgrounded on mobile), so a stale time isn't left showing.
  $(document).on("visibilitychange", () => {
    if (document.visibilityState !== "visible") return;
    setNow();
    recalculate();
  });

  setNow();

  const cachedLocation = loadCachedLocation();
  if (cachedLocation) {
    setLocation(
      cachedLocation.lat,
      cachedLocation.lon,
      `Using last known location: ${cachedLocation.lat.toFixed(4)}, ${cachedLocation.lon.toFixed(4)} — refreshing…`,
      "pending"
    );
    requestGeolocation(true);
  } else {
    requestGeolocation(false);
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js");

    // Ask the active service worker for its CACHE_NAME (the single source of
    // truth for the app version) rather than duplicating it in this file.
    navigator.serviceWorker.ready.then((registration) => {
      if (!registration.active) return;
      const channel = new MessageChannel();
      channel.port1.onmessage = (event) => {
        if (event.data && event.data.version) {
          $("#appFooter").text(event.data.version);
        }
      };
      registration.active.postMessage({ type: "GET_VERSION" }, [channel.port2]);
    });
  }
});
