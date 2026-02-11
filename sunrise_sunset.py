#!/usr/bin/env python3
"""Calculate sunrise and sunset times for a given location and date.

Uses a simplified version of the NOAA solar position algorithm based on
Jean Meeus' "Astronomical Algorithms". The method models Earth's elliptical
orbit and axial tilt to determine when the Sun crosses the horizon at any
point on the globe, accounting for atmospheric refraction.

Accuracy: typically within 1-2 minutes of official NOAA predictions for
mid-latitudes; less precise near the polar circles where the Sun grazes
the horizon at a shallow angle.
"""

import argparse
import math
from datetime import datetime, timezone, timedelta


def sunrise_sunset(lat, lon, date=None, utc_offset=None):
    """Calculate sunrise and sunset times.

    Args:
        lat: Latitude in degrees (positive north).
        lon: Longitude in degrees (positive east).
        date: A datetime.date object (defaults to today).
        utc_offset: Hours offset from UTC (defaults to system local offset).

    Returns:
        Tuple of (sunrise, sunset) as datetime objects, or (None, None)
        for polar day/night conditions.
    """
    if date is None:
        date = datetime.now().date()
    if utc_offset is None:
        utc_offset = datetime.now(timezone.utc).astimezone().utcoffset().total_seconds() / 3600

    # ── Step 1: Day of year ──────────────────────────────────────────────
    # Number the days starting from Jan 1 = 1. This is the main time input
    # for all subsequent solar position formulas.
    n = date.timetuple().tm_yday

    # ── Step 2: Approximate solar noon ───────────────────────────────────
    # Estimate when the Sun is highest in the sky at this longitude.
    # Dividing longitude by 360 converts degrees to a fractional day offset
    # from the Greenwich meridian (Earth rotates 360° per day).
    j_star = n - (lon / 360)

    # ── Step 3: Solar mean anomaly ───────────────────────────────────────
    # The "mean anomaly" M is the angle (in degrees) describing where Earth
    # would be in its orbit if the orbit were a perfect circle. It advances
    # by ~0.9856° per day (360° / 365.25 days). The constant 357.5291° is
    # the anomaly at the J2000 epoch (Jan 1, 2000 at noon).
    M = (357.5291 + 0.98560028 * j_star) % 360

    # ── Step 4: Equation of the center ───────────────────────────────────
    # Earth's orbit is an ellipse, not a circle, so it speeds up when closer
    # to the Sun (perihelion) and slows down when farther away (aphelion).
    # The "equation of the center" C corrects for this difference between
    # the mean (circular) position and the true (elliptical) position.
    #
    # It is computed as a trigonometric series in the mean anomaly:
    #   - 1st term (1.9148°): the dominant correction from orbital eccentricity
    #   - 2nd term (0.0200°): a small refinement for the ellipse shape
    #   - 3rd term (0.0003°): an even finer correction (nearly negligible)
    # The sum C can swing roughly ±2° over the course of a year.
    M_rad = math.radians(M)
    C = 1.9148 * math.sin(M_rad) + 0.0200 * math.sin(2 * M_rad) + 0.0003 * math.sin(3 * M_rad)

    # ── Step 5: Ecliptic longitude of the Sun ────────────────────────────
    # The ecliptic longitude (lambda) is the Sun's position along the
    # ecliptic plane (the plane of Earth's orbit). It combines:
    #   - M: where the Sun would be on a circular orbit
    #   - C: the elliptical correction from Step 4
    #   - 102.9372°: the longitude of Earth's perihelion (closest approach)
    #   - 180°: flips the perspective from Earth-centric to Sun-centric
    # The result is wrapped to 0-360° with modulo.
    lam = (M + C + 180 + 102.9372) % 360

    # ── Step 6: Solar transit (exact solar noon) ─────────────────────────
    # Refine the solar noon estimate from Step 2 using two small corrections:
    #   - 0.0053 * sin(M): adjusts for the non-uniform orbital speed
    #   - 0.0069 * sin(2*lambda): adjusts for the tilt of the ecliptic
    # Together these form a simplified "equation of time" — the difference
    # between clock time and sundial time, which varies by up to ~16 minutes
    # throughout the year.
    j_transit = j_star + 0.0053 * math.sin(M_rad) - 0.0069 * math.sin(2 * math.radians(lam))

    # ── Step 7: Solar declination ────────────────────────────────────────
    # The declination is how far north or south of the celestial equator
    # the Sun appears. It ranges from +23.44° (summer solstice, northern
    # hemisphere) to -23.44° (winter solstice). This is caused by Earth's
    # axial tilt of 23.4397°.
    #
    # sin(declination) = sin(ecliptic_longitude) * sin(axial_tilt)
    # We also need cos(declination) for the hour angle calculation below.
    sin_dec = math.sin(math.radians(lam)) * math.sin(math.radians(23.4397))
    cos_dec = math.cos(math.asin(sin_dec))

    # ── Step 8: Hour angle (how far the Sun travels from noon to sunset) ─
    # The hour angle (omega) is the angular distance the Sun must travel
    # from its highest point (solar noon) to reach the horizon. A larger
    # hour angle means a longer day.
    #
    # The formula solves for when the Sun's center is 0.833° below the
    # horizon, which accounts for:
    #   - 0.533°: the apparent radius of the solar disc (we want the moment
    #     the upper edge touches the horizon, not the center)
    #   - 0.300°: atmospheric refraction bends sunlight upward, making the
    #     Sun visible even when it is geometrically below the horizon
    #
    # cos(omega) = [sin(-0.833°) - sin(lat)*sin(dec)] / [cos(lat)*cos(dec)]
    lat_rad = math.radians(lat)
    cos_omega = (math.sin(math.radians(-0.833)) - math.sin(lat_rad) * sin_dec) / (
        math.cos(lat_rad) * cos_dec
    )

    # If cos(omega) is out of the [-1, +1] range, the Sun never crosses
    # the horizon on this day at this latitude:
    #   > 1  → the Sun never rises (polar night)
    #   < -1 → the Sun never sets (midnight sun / polar day)
    if cos_omega > 1:
        return None, None  # Polar night
    if cos_omega < -1:
        return None, None  # Midnight sun

    # Convert from cosine back to an angle (in degrees).
    omega = math.degrees(math.acos(cos_omega))

    # ── Step 9: Sunrise and sunset times ─────────────────────────────────
    # Sunrise = solar noon minus the hour angle (Sun hasn't reached noon yet)
    # Sunset  = solar noon plus the hour angle (Sun has passed noon)
    # Dividing omega by 360 converts the angle to a fractional day, since
    # the Earth rotates 360° in one day.
    j_rise = j_transit - (omega / 360)
    j_set = j_transit + (omega / 360)

    # ── Step 10: Convert fractional day-of-year to a clock time ──────────
    def day_frac_to_time(j_frac):
        # j_frac is a day-of-year value centered around solar noon.
        # Subtracting n re-centers it around the current day, then
        # multiplying by 24 converts days to hours. Adding 12 shifts
        # from "hours relative to noon" to "hours relative to midnight".
        total_hours_utc = (j_frac - n) * 24 + 12

        # Shift from UTC to the requested local timezone.
        total_hours_local = total_hours_utc + utc_offset

        # Wrap into 0-24 range (e.g. -1 hour becomes 23:00).
        total_hours_local %= 24

        # Split fractional hours into hours, minutes, seconds.
        h = int(total_hours_local)
        m = int((total_hours_local - h) * 60)
        s = int(((total_hours_local - h) * 60 - m) * 60)
        return datetime(date.year, date.month, date.day, h, m, s,
                        tzinfo=timezone(timedelta(hours=utc_offset)))

    return day_frac_to_time(j_rise), day_frac_to_time(j_set)


def main():
    parser = argparse.ArgumentParser(description="Calculate sunrise and sunset times.")
    parser.add_argument("lat", type=float, help="Latitude (degrees, positive N)")
    parser.add_argument("lon", type=float, help="Longitude (degrees, positive E)")
    parser.add_argument("-d", "--date", type=str, default=None,
                        help="Date in YYYY-MM-DD format (default: today)")
    parser.add_argument("-u", "--utc-offset", type=float, default=None,
                        help="UTC offset in hours (default: system local)")
    args = parser.parse_args()

    date = datetime.strptime(args.date, "%Y-%m-%d").date() if args.date else None

    rise, sset = sunrise_sunset(args.lat, args.lon, date=date, utc_offset=args.utc_offset)

    # Display results
    target_date = date or datetime.now().date()
    print(f"Location : {abs(args.lat):.4f}°{'N' if args.lat >= 0 else 'S'}, "
          f"{abs(args.lon):.4f}°{'E' if args.lon >= 0 else 'W'}")
    print(f"Date     : {target_date}")

    if rise is None:
        lat_abs = abs(args.lat)
        if lat_abs > 60:
            print("Sun does not rise or set at this location on this date (polar region).")
        else:
            print("Could not compute sunrise/sunset for this location and date.")
    else:
        print(f"Sunrise  : {rise.strftime('%H:%M:%S %Z')}")
        print(f"Sunset   : {sset.strftime('%H:%M:%S %Z')}")
        delta = sset - rise
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes = remainder // 60
        print(f"Daylight : {hours}h {minutes}m")


if __name__ == "__main__":
    main()
