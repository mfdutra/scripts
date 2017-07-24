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
import pdb
import re
import sys
import xml.etree.ElementTree as ET
from math import radians, cos, sin, asin, sqrt, degrees

# Namespaces
AIXM = '{http://www.aixm.aero/schema/5.1}'
GML = '{http://www.opengis.net/gml/3.2}'

def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def strip(s):
    return s[s.find('}')+1:]

def main(args):
    # Input
    inXml = ET.parse(args.file)
    inRoot = inXml.getroot()

    # Output
    tree = ET.ElementTree()
    kml = ET.Element('kml')
    tree._setroot(kml)
    doc = ET.SubElement(kml, 'Document')
    ET.SubElement(doc, 'name').text = 'NAV'

    for member in inRoot:
        aid = member[0]
        aidType = strip(aid.tag)

        if aidType == 'Navaid':

            try:
                des = member.findall('.//' + AIXM + 'designator')[0].text
                pos = member.findall('.//' + GML + 'pos')[0].text
                name = member.findall('.//' + AIXM + 'name')[0].text
                typ = member.findall('.//' + AIXM + 'type')[0].text

            except IndexError:
                continue

            # Skip unwanted types
            if typ in ('OTHER:VOT', 'TACAN'):
                continue

            place = ET.SubElement(doc, 'Placemark')
            ET.SubElement(place, 'name').text = des
            ET.SubElement(place, 'description').text = \
                '{}\n{}'.format(name, typ)
            point = ET.SubElement(place, 'Point')
            ET.SubElement(point, 'coordinates').text = pos.replace(' ', ',')

    tree.write(args.output, xml_declaration=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert NAV data from the FAA format to KML',
        epilog='Get current databases at https://nfdc.faa.gov')
    parser.add_argument('file', help='FAA NAV_AIXM.xml file')
    parser.add_argument('output', help='KML output file')

    main(parser.parse_args())
