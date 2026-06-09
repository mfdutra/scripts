#!/usr/bin/env python3
import argparse
import math

EARTH_RADIUS_NM = 3440.065
FEET_PER_NM = 6076.115


def horizon_distance_nm(altitude_ft: float) -> float:
    altitude_nm = altitude_ft / FEET_PER_NM
    return EARTH_RADIUS_NM * math.acos(EARTH_RADIUS_NM / (EARTH_RADIUS_NM + altitude_nm))


def main():
    parser = argparse.ArgumentParser(
        description="Calculate horizon distance from altitude.")
    parser.add_argument("altitude", type=float, metavar="altitude_ft",
                        help="Observer altitude in feet")
    parser.add_argument("-f", "--freezing-level", type=float, metavar="altitude_ft",
                        help="Target altitude in feet; calculates max distance to see it")
    args = parser.parse_args()

    if args.altitude < 0:
        parser.error("altitude must be non-negative")
    if args.freezing_level is not None and args.freezing_level < 0:
        parser.error("--freezing-level must be non-negative")

    if args.freezing_level is not None:
        distance_nm = horizon_distance_nm(
            args.altitude) + horizon_distance_nm(args.freezing_level)
        print(f"{distance_nm:.1f} nm")
    else:
        print(f"{horizon_distance_nm(args.altitude):.1f} nm")


if __name__ == "__main__":
    main()
