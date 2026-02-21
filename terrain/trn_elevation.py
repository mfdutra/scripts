#!/usr/bin/env python3

"""
Query elevation from a Garmin trn.dat terrain database (TDB2 format).

Returns min/max/midpoint elevation for the finest-resolution tile containing
the given latitude and longitude. Typical accuracy is ±14m (median tile range
is ~28m at the finest 0.176° resolution).

Usage:
    from trn_elevation import query_elevation, open_terrain_db

    db = open_terrain_db("trn.dat")
    result = query_elevation(db, lat=46.8523, lon=-121.7603)
    print(result)
    # {'lat': 46.8523, 'lon': -121.7603, 'elevation': 2623,
    #  'min_elevation': 855, 'max_elevation': 4392, 'unit': 'meters', ...}
    db.close()

    # Or as a one-shot:
    result = get_elevation("trn.dat", lat=46.8523, lon=-121.7603)
"""

import struct
import math
from typing import Optional

# File layout constants
HEADER_SIZE = 7
LEVEL_RECORD_SIZE = 41
NUM_LEVELS = 10
ROOT_POINTER_SIZE = 6
INDEX_ENTRY_SIZE = 11
TILE_HEADER_SIZE = 17

# Level table starts right after the file header
LEVEL_TABLE_OFFSET = HEADER_SIZE

# Root pointer follows level table
ROOT_POINTER_OFFSET = LEVEL_TABLE_OFFSET + NUM_LEVELS * LEVEL_RECORD_SIZE

# Flat tile index follows root pointer
FLAT_INDEX_OFFSET = ROOT_POINTER_OFFSET + ROOT_POINTER_SIZE

# Semicircle conversion
SEMICIRCLE_TO_DEG = 180.0 / (2 ** 31)


class TerrainDB:
    """Handle to an open Garmin trn.dat terrain database."""

    def __init__(self, f, levels, total_entries):
        self.f = f
        self.levels = levels  # list of (resolution_semicircles, lat_tiles, lon_tiles)
        self.total_entries = total_entries
        # Precompute the starting entry index for each level.
        # Level 0 (finest) comes first in the flat index.
        self._level_offsets = []
        offset = 0
        for _, lat_t, lon_t in self.levels:
            self._level_offsets.append(offset)
            offset += lat_t * lon_t

    def close(self):
        self.f.close()


def open_terrain_db(path: str) -> TerrainDB:
    """Open a trn.dat file and parse its level table."""
    f = open(path, "rb")

    # Read level table
    levels = []
    for i in range(NUM_LEVELS):
        f.seek(LEVEL_TABLE_OFFSET + i * LEVEL_RECORD_SIZE)
        rec = f.read(LEVEL_RECORD_SIZE)
        resolution = struct.unpack_from("<I", rec, 4)[0]
        res_deg = resolution * SEMICIRCLE_TO_DEG
        lat_tiles = round(180.0 / res_deg)
        lon_tiles = round(360.0 / res_deg)
        levels.append((resolution, lat_tiles, lon_tiles))

    # Count total entries
    # (sum of lat_tiles * lon_tiles for all levels)
    total = sum(lt * lo for _, lt, lo in levels)

    return TerrainDB(f, levels, total)


def _read_index_entry(db: TerrainDB, entry_index: int):
    """Read a single tile index entry. Returns (offset, size, flags)."""
    db.f.seek(FLAT_INDEX_OFFSET + entry_index * INDEX_ENTRY_SIZE)
    rec = db.f.read(INDEX_ENTRY_SIZE)
    if len(rec) < INDEX_ENTRY_SIZE:
        return None, 0, 0
    file_offset = struct.unpack_from("<I", rec, 0)[0]
    size = rec[4] | (rec[5] << 8) | (rec[6] << 16)
    flags = struct.unpack_from("<H", rec, 9)[0]
    return file_offset, size, flags


def _read_tile_header(db: TerrainDB, file_offset: int):
    """Read the 17-byte tile header. Returns (max_elev, min_elev, data_size)."""
    db.f.seek(file_offset)
    hdr = db.f.read(TILE_HEADER_SIZE)
    if len(hdr) < TILE_HEADER_SIZE:
        return None, None, 0
    max_elev = struct.unpack_from("<h", hdr, 11)[0]
    min_elev = struct.unpack_from("<h", hdr, 13)[0]
    data_size = struct.unpack_from("<H", hdr, 15)[0]
    return max_elev, min_elev, data_size


def query_elevation(
    db: TerrainDB,
    lat: float,
    lon: float,
    level: int = 0,
) -> Optional[dict]:
    """
    Query terrain elevation at a given latitude and longitude.

    Args:
        db: An open TerrainDB handle.
        lat: Latitude in degrees (-90 to +90).
        lon: Longitude in degrees (-180 to +180).
        level: Zoom level (0 = finest ~0.176°, 9 = coarsest 90°).
               Default is 0 (finest available resolution).

    Returns:
        A dict with elevation info, or None if the tile is empty (ocean/void).

        Keys:
            lat, lon: Input coordinates.
            elevation: Midpoint estimate in meters (average of min and max).
            min_elevation: Minimum elevation in the tile (meters).
            max_elevation: Maximum elevation in the tile (meters).
            uncertainty: Half the tile's elevation range (meters).
            unit: Always "meters".
            level: Zoom level used.
            tile_lat_south: Southern boundary of the tile (degrees).
            tile_lat_north: Northern boundary of the tile (degrees).
            tile_lon_west: Western boundary of the tile (degrees).
            tile_lon_east: Eastern boundary of the tile (degrees).
            resolution_deg: Tile size in degrees.
    """
    if not (0 <= level < NUM_LEVELS):
        raise ValueError(f"level must be 0-{NUM_LEVELS-1}, got {level}")
    if not (-90 <= lat <= 90):
        raise ValueError(f"lat must be -90 to 90, got {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"lon must be -180 to 180, got {lon}")

    resolution, lat_tiles, lon_tiles = db.levels[level]
    res_deg = resolution * SEMICIRCLE_TO_DEG

    # Tile indices (row-major, south to north, west to east)
    lat_idx = int((lat + 90.0) / res_deg)
    lon_idx = int((lon + 180.0) / res_deg)

    # Clamp to valid range
    lat_idx = min(lat_idx, lat_tiles - 1)
    lon_idx = min(lon_idx, lon_tiles - 1)

    # Entry index in the flat tile array
    entry_index = db._level_offsets[level] + lat_idx * lon_tiles + lon_idx

    file_offset, size, flags = _read_index_entry(db, entry_index)

    if flags != 2 or size < TILE_HEADER_SIZE:
        # Empty tile (ocean or void). Try coarser levels.
        if level < NUM_LEVELS - 1:
            return query_elevation(db, lat, lon, level + 1)
        return None

    max_elev, min_elev, data_size = _read_tile_header(db, file_offset)
    if max_elev is None:
        return None

    midpoint = (max_elev + min_elev) / 2.0
    uncertainty = (max_elev - min_elev) / 2.0

    # Tile boundaries
    tile_lat_south = -90.0 + lat_idx * res_deg
    tile_lat_north = tile_lat_south + res_deg
    tile_lon_west = -180.0 + lon_idx * res_deg
    tile_lon_east = tile_lon_west + res_deg

    return {
        "lat": lat,
        "lon": lon,
        "elevation": round(midpoint),
        "min_elevation": min_elev,
        "max_elevation": max_elev,
        "uncertainty": round(uncertainty),
        "unit": "meters",
        "level": level,
        "tile_lat_south": round(tile_lat_south, 6),
        "tile_lat_north": round(tile_lat_north, 6),
        "tile_lon_west": round(tile_lon_west, 6),
        "tile_lon_east": round(tile_lon_east, 6),
        "resolution_deg": round(res_deg, 6),
    }


def get_elevation(path: str, lat: float, lon: float, level: int = 0) -> Optional[dict]:
    """One-shot elevation query. Opens the file, queries, and closes."""
    db = open_terrain_db(path)
    try:
        return query_elevation(db, lat, lon, level)
    finally:
        db.close()


# ---------------------------------------------------------------------------
# CLI interface
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    def usage():
        print("Usage: python trn_elevation.py <trn.dat> <lat> <lon>")
        print("       python trn_elevation.py <trn.dat> --test")
        sys.exit(1)

    if len(sys.argv) < 3:
        usage()

    db_path = sys.argv[1]

    if sys.argv[2] == "--test":
        db = open_terrain_db(db_path)
        test_cases = [
            ("Mount Rainier", 46.8523, -121.7603, 4392),
            ("Mount Everest", 27.9881, 86.925, 8848),
            ("Denver, CO", 39.7392, -104.9903, 1609),
            ("Death Valley", 36.23, -116.83, -86),
            ("Dead Sea", 31.5, 35.5, -430),
            ("San Francisco", 37.7749, -122.4194, 0),
            ("Tokyo", 35.68, 139.69, 40),
            ("La Paz, Bolivia", -16.5, -68.15, 3640),
            ("Kilimanjaro", -3.07, 37.35, 5895),
            ("Amsterdam", 52.37, 4.89, -2),
            ("Pacific Ocean", 30.0, -150.0, 0),
        ]

        print(f"{'Location':<20s} {'Expected':>8s} {'Min':>6s} {'Mid':>6s} {'Max':>6s} {'±':>4s}  Level")
        print("-" * 75)
        for name, lat, lon, expected in test_cases:
            result = query_elevation(db, lat, lon)
            if result:
                print(
                    f"{name:<20s} {expected:>8d} {result['min_elevation']:>6d} "
                    f"{result['elevation']:>6d} {result['max_elevation']:>6d} "
                    f"{result['uncertainty']:>4d}  L{result['level']}"
                )
            else:
                print(f"{name:<20s} {expected:>8d}   (no data)")
        db.close()

    elif len(sys.argv) >= 4:
        lat = float(sys.argv[2])
        lon = float(sys.argv[3])
        result = get_elevation(db_path, lat, lon)
        if result is None:
            print(f"No elevation data for ({lat}, {lon})")
            sys.exit(1)
        print(f"Location:    ({lat}, {lon})")
        print(f"Elevation:   {result['elevation']}m (±{result['uncertainty']}m)")
        print(f"Range:       {result['min_elevation']}m to {result['max_elevation']}m")
        print(f"Tile:        [{result['tile_lat_south']}, {result['tile_lon_west']}] to "
              f"[{result['tile_lat_north']}, {result['tile_lon_east']}]")
        print(f"Resolution:  {result['resolution_deg']}° (level {result['level']})")
    else:
        usage()
