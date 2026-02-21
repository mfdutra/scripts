# Garmin trn.dat Terrain Database (TDB2 Format)

## File Overview
- **File**: `trn.dat` — Garmin TDB2 terrain database, ~3.4 GB
- **Coverage**: Global, 10 zoom levels
- **Finest resolution**: ~4.9 arcseconds (0.175781° tiles, ~19.5 km)
- **Elevations**: Signed int16, in **meters**

## File Structure

### 1. File Header (7 bytes) @ 0x0000
- byte 0: version (0x04)
- bytes 1-6: signature/metadata (`VnE...`)

### 2. Level Table (10 × 41 bytes) @ 0x0007
Each 41-byte level record:
- bytes 0-1: flags/identifier
- bytes 2-3: u16 LE metadata
- bytes 4-7: u32 LE resolution in semicircles (convert: `val * 180 / 2^31` = degrees)
- bytes 8-39: bounding box in semicircles (lat ±90°, lon ±180°)
- byte 40: constant 0x03

| Level | Resolution (semicircles) | Resolution (degrees) |
|-------|--------------------------|---------------------|
| 0 (finest) | 2^21 | 0.175781° |
| 1 | 2^22 | 0.351562° |
| 2 | 2^23 | 0.703125° |
| 3 | 2^24 | 1.406250° |
| 4 | 2^25 | 2.812500° |
| 5 | 2^26 | 5.625° |
| 6 | 2^27 | 11.25° |
| 7 | 2^28 | 22.5° |
| 8 | 2^29 | 45° |
| 9 (coarsest) | 2^30 | 90° |

### 3. Root Pointer (6 bytes) @ 0x01A1
- u32 LE: file offset to hierarchical tree root data
- u16 LE: flags (0x0002)

### 4. Flat Tile Index (~2,796,191 × 11 bytes) @ 0x01A7
Each 11-byte entry:
- bytes 0-3: u32 LE file offset to tile data
- bytes 4-6: u24 LE (3-byte little-endian) tile data size
- bytes 7-8: u16 LE padding (always 0x0000)
- bytes 9-10: u16 LE flags: `1` = empty/ocean, `2` = has elevation data

**Tile ordering**: Finest level first (level 0), then progressively coarser.
Within each level: row-major, **south-to-north**, **west-to-east**.

| Level | Grid | Tiles |
|-------|------|-------|
| 0 | 1024 lat × 2048 lon | 2,097,152 |
| 1 | 512 × 1024 | 524,288 |
| 2 | 256 × 512 | 131,072 |
| ... | ... | ... |
| 9 | 2 × 4 | 8 |
| **Total** | | **~2,796,200** |

### 5. Tile Data (variable size, scattered throughout file)
Each tile:
- bytes 0-10: 11 zero bytes (reserved/alignment)
- bytes 11-12: u16 LE **max elevation** (meters, signed)
- bytes 13-14: u16 LE **min elevation** (meters, signed)
- bytes 15-16: u16 LE compressed data payload size
- bytes 17-22: 6-byte data sub-header
- bytes 23+: compressed elevation grid (quadtree bitmask + delta-coded values, not fully decoded)

### 6. Hierarchical Tree Index (near end of file)
Parallel access structure using same 11-byte record format. Root → 8 sub-regions → tile data.

## Statistics
- Empty tiles (ocean/void): 1,741,769 (62.3%)
- Data tiles: 1,054,422 (37.7%)
- Tile data sizes: 17–15,789 bytes (avg ~3,371)
- Level 0 elevation range: median 28m, mean 117m

## Verified Landmarks
| Location | max_elev | min_elev | Actual |
|----------|----------|----------|--------|
| Mt. Rainier | 4392m | 855m | 4392m peak |
| Everest | 8848m | 5124m | 8849m peak |
| Dead Sea | 432m | -432m | -430m |
| Death Valley | 1741m | -85m | -86m low |
| Denver | 1722m | 1548m | ~1609m |

## Code
- `trn_elevation.py` — Python module to query elevation by lat/lon
  - `open_terrain_db(path)` → `TerrainDB` handle
  - `query_elevation(db, lat, lon)` → dict with elevation info
  - `get_elevation(path, lat, lon)` → one-shot query
  - CLI: `python trn_elevation.py trn.dat <lat> <lon>` or `--test`

## What's Not Decoded
The compressed elevation grid within each tile uses an interleaved quadtree bitstream with delta-coded elevation values. The bit convention is: `0` = subdivide (read 4 children), `1` = leaf (read N-bit elevation delta). The exact bits-per-value and sub-header fields (bytes 17-22) are not fully understood. Currently the script returns the tile's min/max/midpoint as an approximation.
