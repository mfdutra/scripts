#!/opt/homebrew/bin/python3.6

# Convert fixes/waypoints from the FAA format to KML

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from math import radians, cos, sin, asin, sqrt, degrees

latLonRe = re.compile(r'^(\d+)-(\d+)-([\d\.]+)([NSWE])')

def decCoord(s):
    match = latLonRe.match(s.strip())

    deg = int(match.group(1))
    min = int(match.group(2))
    sec = float(match.group(3))
    side = match.group(4)

    if side in ('W', 'S'):
        deg = deg * -1
        min = min * -1
        sec = sec * -1

    return deg + (min / 60) + (sec / 3600)

def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return degrees(c) * 60

def withinRadius(args, lat, lon):
    return haversine(lon, lat, args.longitude, args.latitude) <= args.radius

def main(args):
    if (args.latitude and not args.longitude) or \
            (args.longitude and not args.latitude):
        fatal('Latitude and longitude must be passed together')

    tree = ET.ElementTree()
    kml = ET.Element('kml')
    tree._setroot(kml)
    doc = ET.SubElement(kml, 'Document')
    ET.SubElement(doc, 'name').text = 'FIXES'

    with open(args.file, 'r', encoding='ascii') as f:
        for line in f:
            if not line.startswith('FIX1'):
                continue

            line = line.strip()
            name = line[4:34].strip()
            lat = decCoord(line[66:80])
            lon = decCoord(line[80:94])

            if args.latitude and not withinRadius(args, lat, lon):
                continue

            place = ET.SubElement(doc, 'Placemark')
            ET.SubElement(place, 'name').text = name
            point = ET.SubElement(place, 'Point')
            ET.SubElement(point, 'coordinates').text = '{},{}'.format(lon, lat)

    tree.write(args.output, xml_declaration=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert fixes/waypoints from the FAA format to KML',
        epilog='Get current databases at https://nfdc.faa.gov')
    parser.add_argument('file', help='FAA FIX.txt file')
    parser.add_argument('output', help='KML output file')

    parser.add_argument('--latitude', type=float,
        help='eg: 37.61946088067242 (KSFO)')
    parser.add_argument('--longitude', type=float,
        help='eg: -122.3738855647427 (KSFO)')
    parser.add_argument('--radius', type=int, default=50,
        help='Radius in nautical miles from location to include [%(default)s]')

    main(parser.parse_args())
