#!/usr/bin/env python3
"""Comprehensive tests for sunrise_sunset.py."""

import math
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from sunrise_sunset import sunrise_sunset, main


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _minutes(dt):
    """Return total minutes since midnight for easy comparison."""
    return dt.hour * 60 + dt.minute


def _assert_within_minutes(dt, expected_hour, expected_minute, tolerance=5):
    """Assert a datetime is within `tolerance` minutes of an expected HH:MM."""
    actual = _minutes(dt)
    expected = expected_hour * 60 + expected_minute
    diff = abs(actual - expected)
    # Handle wrap-around midnight
    diff = min(diff, 1440 - diff)
    assert diff <= tolerance, (
        f"Expected ~{expected_hour:02d}:{expected_minute:02d}, "
        f"got {dt.strftime('%H:%M:%S')} (off by {diff} min)"
    )


# ---------------------------------------------------------------------------
# Known-location tests — validated against NOAA / timeanddate.com references
# ---------------------------------------------------------------------------

class TestKnownLocations:
    """Compare results against well-known reference values (±5 min)."""

    def test_new_york_winter(self):
        rise, sset = sunrise_sunset(40.7128, -74.0060, date(2026, 1, 15), utc_offset=-5)
        _assert_within_minutes(rise, 7, 16)
        _assert_within_minutes(sset, 16, 54)

    def test_new_york_summer(self):
        rise, sset = sunrise_sunset(40.7128, -74.0060, date(2026, 6, 21), utc_offset=-4)
        _assert_within_minutes(rise, 5, 25)
        _assert_within_minutes(sset, 20, 31)

    def test_london_equinox(self):
        rise, sset = sunrise_sunset(51.5074, -0.1278, date(2026, 3, 20), utc_offset=0)
        _assert_within_minutes(rise, 6, 4)
        _assert_within_minutes(sset, 18, 15)

    def test_tokyo_spring(self):
        rise, sset = sunrise_sunset(35.6762, 139.6503, date(2026, 4, 1), utc_offset=9)
        _assert_within_minutes(rise, 5, 28)
        _assert_within_minutes(sset, 18, 2)

    def test_sydney_winter(self):
        # Southern hemisphere winter = June
        # AEST = UTC+10 (no daylight saving in June)
        rise, sset = sunrise_sunset(-33.8688, 151.2093, date(2026, 6, 21), utc_offset=10)
        _assert_within_minutes(rise, 7, 0)
        _assert_within_minutes(sset, 16, 53)

    def test_equator(self):
        # Quito, Ecuador — near-equator, ~12 h daylight year-round
        rise, sset = sunrise_sunset(-0.1807, -78.4678, date(2026, 6, 21), utc_offset=-5)
        daylight_min = (_minutes(sset) - _minutes(rise)) % 1440
        assert 700 <= daylight_min <= 740, f"Expected ~12h daylight, got {daylight_min} min"

    def test_reykjavik_summer(self):
        # Very long day near solstice
        rise, sset = sunrise_sunset(64.1466, -21.9426, date(2026, 6, 21), utc_offset=0)
        if rise is not None:
            daylight_min = (_minutes(sset) - _minutes(rise)) % 1440
            assert daylight_min >= 1200, f"Expected 20+ h daylight, got {daylight_min} min"

    def test_cape_town(self):
        rise, sset = sunrise_sunset(-33.9249, 18.4241, date(2026, 12, 21), utc_offset=2)
        _assert_within_minutes(rise, 5, 32)
        _assert_within_minutes(sset, 19, 57)


# ---------------------------------------------------------------------------
# Polar edge cases
# ---------------------------------------------------------------------------

class TestPolarConditions:
    """Test locations where the sun never rises or never sets."""

    def test_north_pole_winter(self):
        rise, sset = sunrise_sunset(89.0, 0.0, date(2026, 12, 21), utc_offset=0)
        assert rise is None and sset is None

    def test_north_pole_summer(self):
        rise, sset = sunrise_sunset(89.0, 0.0, date(2026, 6, 21), utc_offset=0)
        assert rise is None and sset is None  # midnight sun

    def test_south_pole_winter(self):
        rise, sset = sunrise_sunset(-89.0, 0.0, date(2026, 6, 21), utc_offset=0)
        assert rise is None and sset is None  # polar night

    def test_south_pole_summer(self):
        rise, sset = sunrise_sunset(-89.0, 0.0, date(2026, 12, 21), utc_offset=0)
        assert rise is None and sset is None  # midnight sun

    def test_arctic_circle_boundary(self):
        # Just inside the Arctic Circle on summer solstice — should be near polar
        rise, sset = sunrise_sunset(66.0, 0.0, date(2026, 6, 21), utc_offset=0)
        # Should either be None (midnight sun) or have very long daylight
        if rise is not None:
            daylight_min = (_minutes(sset) - _minutes(rise)) % 1440
            assert daylight_min >= 1300


# ---------------------------------------------------------------------------
# Seasonal daylight patterns
# ---------------------------------------------------------------------------

class TestSeasonalPatterns:
    """Verify that daylight duration changes correctly across seasons."""

    def _daylight_minutes(self, lat, lon, d, utc_offset):
        rise, sset = sunrise_sunset(lat, lon, d, utc_offset=utc_offset)
        if rise is None:
            return None
        return (_minutes(sset) - _minutes(rise)) % 1440

    def test_northern_summer_longer_than_winter(self):
        summer = self._daylight_minutes(48.8566, 2.3522, date(2026, 6, 21), 2)
        winter = self._daylight_minutes(48.8566, 2.3522, date(2026, 12, 21), 1)
        assert summer > winter

    def test_southern_hemisphere_reversed(self):
        # In the southern hemisphere, December has more daylight
        june = self._daylight_minutes(-33.8688, 151.2093, date(2026, 6, 21), 11)
        december = self._daylight_minutes(-33.8688, 151.2093, date(2026, 12, 21), 11)
        assert december > june

    def test_equinox_approx_12h(self):
        # Mid-latitude location near equinox should have ~12h daylight
        dl = self._daylight_minutes(40.0, -3.0, date(2026, 3, 20), 1)
        assert 700 <= dl <= 740

    def test_solstice_is_extremum(self):
        # Days near solstice should have similar daylight
        d1 = self._daylight_minutes(52.0, 13.0, date(2026, 6, 20), 2)
        d2 = self._daylight_minutes(52.0, 13.0, date(2026, 6, 21), 2)
        d3 = self._daylight_minutes(52.0, 13.0, date(2026, 6, 22), 2)
        assert abs(d1 - d2) <= 3
        assert abs(d2 - d3) <= 3


# ---------------------------------------------------------------------------
# Return value properties
# ---------------------------------------------------------------------------

class TestReturnValues:
    """Verify structural properties of the returned datetimes."""

    def test_sunrise_before_sunset(self):
        rise, sset = sunrise_sunset(34.0522, -118.2437, date(2026, 3, 15), utc_offset=-7)
        assert rise < sset

    def test_timezone_attached(self):
        rise, sset = sunrise_sunset(34.0522, -118.2437, date(2026, 3, 15), utc_offset=-7)
        assert rise.tzinfo is not None
        assert sset.tzinfo is not None
        assert rise.utcoffset() == timedelta(hours=-7)

    def test_correct_date(self):
        d = date(2026, 8, 10)
        rise, sset = sunrise_sunset(51.5074, -0.1278, d, utc_offset=1)
        assert rise.date() == d
        assert sset.date() == d

    def test_returns_tuple(self):
        result = sunrise_sunset(0.0, 0.0, date(2026, 1, 1), utc_offset=0)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_polar_returns_none_tuple(self):
        result = sunrise_sunset(89.0, 0.0, date(2026, 12, 21), utc_offset=0)
        assert result == (None, None)


# ---------------------------------------------------------------------------
# UTC offset handling
# ---------------------------------------------------------------------------

class TestUTCOffset:
    """Test various UTC offset scenarios."""

    def test_utc_zero(self):
        rise, sset = sunrise_sunset(51.5074, -0.1278, date(2026, 6, 1), utc_offset=0)
        assert rise.utcoffset() == timedelta(hours=0)

    def test_positive_offset(self):
        rise, sset = sunrise_sunset(35.6762, 139.6503, date(2026, 6, 1), utc_offset=9)
        assert rise.utcoffset() == timedelta(hours=9)

    def test_negative_offset(self):
        rise, sset = sunrise_sunset(40.7128, -74.0060, date(2026, 6, 1), utc_offset=-4)
        assert rise.utcoffset() == timedelta(hours=-4)

    def test_half_hour_offset(self):
        # India (UTC+5:30)
        rise, sset = sunrise_sunset(28.6139, 77.2090, date(2026, 3, 15), utc_offset=5.5)
        assert rise.utcoffset() == timedelta(hours=5, minutes=30)

    def test_different_offsets_shift_times(self):
        # Same location, different UTC offsets should shift the displayed time
        rise_utc, _ = sunrise_sunset(51.5074, -0.1278, date(2026, 6, 1), utc_offset=0)
        rise_bst, _ = sunrise_sunset(51.5074, -0.1278, date(2026, 6, 1), utc_offset=1)
        # BST time should be 1 hour ahead
        diff = _minutes(rise_bst) - _minutes(rise_utc)
        assert 55 <= diff <= 65

    def test_default_offset_uses_system(self):
        # When utc_offset is None, function should still return valid results
        rise, sset = sunrise_sunset(40.7128, -74.0060, date(2026, 6, 1))
        assert rise is not None
        assert sset is not None


# ---------------------------------------------------------------------------
# Default date handling
# ---------------------------------------------------------------------------

class TestDefaultDate:
    """Test that omitting the date defaults to today."""

    def test_default_date_is_today(self):
        rise, sset = sunrise_sunset(40.7128, -74.0060, utc_offset=-5)
        today = datetime.now().date()
        assert rise.date() == today
        assert sset.date() == today


# ---------------------------------------------------------------------------
# Longitude / hemisphere coverage
# ---------------------------------------------------------------------------

class TestGeographicCoverage:
    """Test various geographic positions."""

    def test_prime_meridian(self):
        rise, sset = sunrise_sunset(51.5074, 0.0, date(2026, 3, 20), utc_offset=0)
        assert rise is not None

    def test_international_date_line_east(self):
        rise, sset = sunrise_sunset(0.0, 179.0, date(2026, 3, 20), utc_offset=12)
        assert rise is not None

    def test_international_date_line_west(self):
        rise, sset = sunrise_sunset(0.0, -179.0, date(2026, 3, 20), utc_offset=-12)
        assert rise is not None

    def test_all_four_hemispheres(self):
        coords = [
            (45.0, 10.0),    # NE
            (45.0, -10.0),   # NW
            (-45.0, 10.0),   # SE
            (-45.0, -10.0),  # SW
        ]
        for lat, lon in coords:
            rise, sset = sunrise_sunset(lat, lon, date(2026, 3, 20), utc_offset=0)
            assert rise is not None, f"Failed for ({lat}, {lon})"
            assert rise < sset, f"Sunrise not before sunset for ({lat}, {lon})"


# ---------------------------------------------------------------------------
# Year-boundary and leap-year dates
# ---------------------------------------------------------------------------

class TestEdgeDates:
    """Test boundary dates."""

    def test_jan_1(self):
        rise, sset = sunrise_sunset(40.0, -74.0, date(2026, 1, 1), utc_offset=-5)
        assert rise is not None

    def test_dec_31(self):
        rise, sset = sunrise_sunset(40.0, -74.0, date(2026, 12, 31), utc_offset=-5)
        assert rise is not None

    def test_leap_year_feb_29(self):
        rise, sset = sunrise_sunset(40.0, -74.0, date(2028, 2, 29), utc_offset=-5)
        assert rise is not None

    def test_different_years_similar_results(self):
        rise_a, _ = sunrise_sunset(40.0, -74.0, date(2025, 6, 21), utc_offset=-4)
        rise_b, _ = sunrise_sunset(40.0, -74.0, date(2026, 6, 21), utc_offset=-4)
        assert abs(_minutes(rise_a) - _minutes(rise_b)) <= 3


# ---------------------------------------------------------------------------
# CLI (main) tests
# ---------------------------------------------------------------------------

class TestCLI:
    """Test the command-line interface."""

    def test_basic_invocation(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py", "40.7128", "-74.0060",
             "-d", "2026-02-10", "-u", "-5"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert result.returncode == 0
        assert "Sunrise" in result.stdout
        assert "Sunset" in result.stdout
        assert "Daylight" in result.stdout

    def test_location_display_north_east(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py", "35.6762", "139.6503",
             "-d", "2026-04-01", "-u", "9"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert "N" in result.stdout
        assert "E" in result.stdout

    def test_location_display_south_west(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py", "-33.8688", "-70.0",
             "-d", "2026-04-01", "-u", "-4"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert "S" in result.stdout
        assert "W" in result.stdout

    def test_polar_message(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py", "89.0", "0.0",
             "-d", "2026-12-21", "-u", "0"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert result.returncode == 0
        assert "does not rise" in result.stdout or "Could not compute" in result.stdout

    def test_missing_required_args(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert result.returncode != 0

    def test_invalid_date_format(self):
        result = subprocess.run(
            [sys.executable, "sunrise_sunset.py", "40.0", "-74.0",
             "-d", "not-a-date", "-u", "0"],
            capture_output=True, text=True, cwd="/Users/mfdutra/mug"
        )
        assert result.returncode != 0


# ---------------------------------------------------------------------------
# Symmetry and consistency checks
# ---------------------------------------------------------------------------

class TestSymmetry:
    """Sanity checks based on physical properties."""

    def test_symmetric_latitudes_equinox(self):
        # On equinox, +lat and -lat should have similar daylight
        rise_n, sset_n = sunrise_sunset(45.0, 0.0, date(2026, 3, 20), utc_offset=0)
        rise_s, sset_s = sunrise_sunset(-45.0, 0.0, date(2026, 3, 20), utc_offset=0)
        dl_n = (_minutes(sset_n) - _minutes(rise_n)) % 1440
        dl_s = (_minutes(sset_s) - _minutes(rise_s)) % 1440
        assert abs(dl_n - dl_s) <= 10

    def test_higher_latitude_more_extreme(self):
        # At summer solstice, higher northern latitude = more daylight
        _, sset_40 = sunrise_sunset(40.0, 0.0, date(2026, 6, 21), utc_offset=0)
        rise_40, _ = sunrise_sunset(40.0, 0.0, date(2026, 6, 21), utc_offset=0)
        _, sset_60 = sunrise_sunset(60.0, 0.0, date(2026, 6, 21), utc_offset=0)
        rise_60, _ = sunrise_sunset(60.0, 0.0, date(2026, 6, 21), utc_offset=0)
        dl_40 = (_minutes(sset_40) - _minutes(rise_40)) % 1440
        dl_60 = (_minutes(sset_60) - _minutes(rise_60)) % 1440
        assert dl_60 > dl_40

    def test_consecutive_days_change_gradually(self):
        # Sunrise shouldn't jump more than ~3 min between consecutive days
        for day_offset in range(28):
            d1 = date(2026, 4, 1 + day_offset)
            d2 = date(2026, 4, 2 + day_offset)
            rise1, _ = sunrise_sunset(48.0, 11.0, d1, utc_offset=2)
            rise2, _ = sunrise_sunset(48.0, 11.0, d2, utc_offset=2)
            diff = abs(_minutes(rise1) - _minutes(rise2))
            assert diff <= 4, f"Sunrise jumped {diff} min between {d1} and {d2}"
