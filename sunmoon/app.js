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

  const setNow = () => {
    const now = new Date();
    $("#dateInput").val(toDateInputValue(now));
    $("#timeInput").val(toTimeInputValue(now));
  };

  const degrees = (radians) => (radians * 180) / Math.PI;

  const formatDegrees = (radians) => `${degrees(radians).toFixed(1)}°`;

  const TWO_PI = 2 * Math.PI;
  const normalizeAngle = (radians) => {
    const wrapped = ((radians + Math.PI) % TWO_PI + TWO_PI) % TWO_PI;
    return wrapped - Math.PI;
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

  const setLocationStatus = (text, isError) => {
    $("#locationStatus")
      .text(text)
      .toggleClass("error", Boolean(isError));
  };

  const showManualLocation = () => {
    $("#manualLocation").show();
  };

  const setLocation = (lat, lon, statusText) => {
    state.lat = lat;
    state.lon = lon;
    $("#latInput").val(lat.toFixed(6));
    $("#lonInput").val(lon.toFixed(6));
    setLocationStatus(statusText || `Location: ${lat.toFixed(4)}, ${lon.toFixed(4)}`);
    recalculate();
  };

  const requestGeolocation = () => {
    if (!navigator.geolocation) {
      setLocationStatus("Geolocation not supported by this browser. Enter coordinates manually.", true);
      showManualLocation();
      return;
    }
    setLocationStatus("Requesting your location…");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation(position.coords.latitude, position.coords.longitude);
      },
      () => {
        setLocationStatus("Location permission denied or unavailable. Enter coordinates manually.", true);
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

  const updateMoonIcon = (fraction, localLimbAngleRad) => {
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
    const svgRotationDeg = -degrees(localLimbAngleRad);
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

  const renderSunPath = (date, lat, lon, times, currentAltitudeRad) => {
    const hasValidWindow =
      times.sunrise instanceof Date && !isNaN(times.sunrise) &&
      times.sunset instanceof Date && !isNaN(times.sunset);

    if (!hasValidWindow) {
      hideSunPath();
      return;
    }

    const startTime = times.sunrise.getTime() - SUN_PATH_BUFFER_MS;
    const endTime = times.sunset.getTime() + SUN_PATH_BUFFER_MS;
    const span = endTime - startTime;

    const altitudeDegAt = (t) => degrees(SunCalc.getPosition(new Date(t), lat, lon).altitude);

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

    const now = date.getTime();
    const isWithinWindow = now >= startTime && now <= endTime;
    $("#sunMarker").attr({
      cx: xForTime(Math.min(Math.max(now, startTime), endTime)),
      cy: yForAltitude(degrees(currentAltitudeRad)),
      opacity: isWithinWindow ? 1 : 0,
    });
  };

  const renderSun = (date, lat, lon) => {
    const position = SunCalc.getPosition(date, lat, lon);
    const times = SunCalc.getTimes(date, lat, lon);
    const dayLengthMs = times.sunset - times.sunrise;

    const sunAzimuthRad = position.azimuth + Math.PI;
    $("#sunElevation").text(formatDegrees(position.altitude)).toggleClass("negative", position.altitude < 0);
    $("#sunAzimuth").text(formatDegrees(sunAzimuthRad));
    $("#sunAzimuthArrow").css("transform", `rotate(${degrees(sunAzimuthRad)}deg)`);
    $("#sunrise").text(formatTime(times.sunrise));
    $("#sunset").text(formatTime(times.sunset));
    $("#solarNoon").text(formatTime(times.solarNoon));
    $("#dayLength").text(formatDuration(dayLengthMs));
    renderSunPath(date, lat, lon, times, position.altitude);
  };

  const renderMoon = (date, lat, lon) => {
    const position = SunCalc.getMoonPosition(date, lat, lon);
    const illumination = SunCalc.getMoonIllumination(date);
    const times = SunCalc.getMoonTimes(date, lat, lon, true);
    const phase = moonPhaseInfo(illumination.phase);
    // illumination.angle is the bright limb's position angle from celestial north,
    // independent of the observer; subtracting the parallactic angle expresses it
    // relative to the observer's local zenith ("up"), matching what's actually seen.
    const localLimbAngle = normalizeAngle(illumination.angle - position.parallacticAngle);

    const moonAzimuthRad = position.azimuth + Math.PI;
    $("#moonElevation").text(formatDegrees(position.altitude)).toggleClass("negative", position.altitude < 0);
    $("#moonAzimuth").text(formatDegrees(moonAzimuthRad));
    $("#moonAzimuthArrow").css("transform", `rotate(${degrees(moonAzimuthRad)}deg)`);
    $("#moonrise").text(times.rise ? formatTime(times.rise) : "None today");
    $("#moonset").text(times.set ? formatTime(times.set) : "None today");
    $("#moonIllumination").text(`${(illumination.fraction * 100).toFixed(0)}%`);
    $("#moonPhase").text(phase.name);
    $("#moonAngle").text(formatDegrees(localLimbAngle));
    updateMoonIcon(illumination.fraction, localLimbAngle);
  };

  const recalculate = () => {
    if (state.lat === null || state.lon === null) return;
    const date = currentSelectedDate();
    renderSun(date, state.lat, state.lon);
    renderMoon(date, state.lat, state.lon);
    const dateLabel = date.toLocaleDateString();
    const timeLabel = date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", hour12: false });
    $("#calcNote")
      .removeClass("hidden")
      .text(`Calculated for ${dateLabel} ${timeLabel}`);
  };

  $("#useLocationBtn").on("click", requestGeolocation);
  $("#enterManualBtn").on("click", showManualLocation);
  $("#useManualBtn").on("click", useManualLocation);
  $("#nowBtn").on("click", () => {
    setNow();
    recalculate();
  });
  $("#dateInput").on("change", recalculate);
  $("#timeInput").on("change", recalculate);

  setNow();
  requestGeolocation();

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("sw.js");
  }
});
