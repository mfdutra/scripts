#!/usr/bin/env python3
import argparse
import json
import xml.etree.ElementTree as ET
from pathlib import Path

# Source of truth:
# https://www.diamondaircraft.com/en/map.xhr?location_map[category]=102


def main():
    parser = argparse.ArgumentParser(
        description="Convert Diamond Aircraft service centers JSON to KML")
    parser.add_argument("input", help="Path to the service centers JSON file")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = input_path.with_suffix(".kml")

    with open(input_path) as f:
        data = json.load(f)

    kml = ET.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
    doc = ET.SubElement(kml, "Document")
    ET.SubElement(doc, "name").text = "Diamond Aircraft Service Centers"

    for sc in data["addresses"]:
        pm = ET.SubElement(doc, "Placemark")
        ET.SubElement(pm, "name").text = sc["name"]
        pt = ET.SubElement(pm, "Point")
        ET.SubElement(pt, "coordinates").text = f"{sc['lng']},{sc['lat']},0"

    tree = ET.ElementTree(kml)
    ET.indent(tree, space="  ")
    tree.write(output_path, encoding="unicode", xml_declaration=True)
    print(f"Saved {len(data['addresses'])} service centers to {output_path}")


if __name__ == "__main__":
    main()
