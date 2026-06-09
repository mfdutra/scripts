#!/usr/bin/env python3
import sys
import math

EARTH_RADIUS_NM = 3440.065
FEET_PER_NM = 6076.115

def horizon_distance_nm(altitude_ft: float) -> float:
    altitude_nm = altitude_ft / FEET_PER_NM
    return math.sqrt(2 * EARTH_RADIUS_NM * altitude_nm)

def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <altitude_ft>")
        sys.exit(1)
    try:
        altitude_ft = float(sys.argv[1])
    except ValueError:
        print(f"Error: '{sys.argv[1]}' is not a valid number")
        sys.exit(1)
    if altitude_ft < 0:
        print("Error: altitude must be non-negative")
        sys.exit(1)
    distance_nm = horizon_distance_nm(altitude_ft)
    print(f"{distance_nm:.1f} nm")

if __name__ == "__main__":
    main()
