#!/opt/homebrew/bin/python3.7

# Creates a KML with the desired airports

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

# Namespaces
AIXM = '{http://www.aixm.aero/schema/5.1}'
GML = '{http://www.opengis.net/gml/3.2}'

def fatal(msg):
    print(msg, file=sys.stderr)
    sys.exit(1)

def log(msg):
    print(msg, file=sys.stderr)
    sys.stderr.flush()

def load_foreflight(fname):
    airports = set()
    begin = False
    with open(fname, 'r', encoding='utf-8') as fd:
        for line in fd:
            if line.startswith('Date,AircraftID'):
                begin = True
                continue

            # Skip aircraft information on the top of the file
            if not begin:
                continue

            # Skip simulator flights
            fields = line.split(',')
            if fields[1] == 'SIM':
                continue

            # Get all airports from FROM and TO, separated by spaces
            for apt in (fields[2].split() + fields[3].split()):
                airports.add(apt)

    return airports

def main(args):
    # Desired airports
    log('Loading desired airports...')

    if args.foreflight:
        airports = load_foreflight(args.airports)

    else:
        airports = open(args.airports, 'r', encoding='utf-8').readlines()
        airports = set([a.strip() for a in airports])

    # FAA Database
    log('Loading airport database (may take a while)...')
    dbXml = ET.parse(args.database)
    dbRoot = dbXml.getroot()

    # Output
    tree = ET.ElementTree()
    kml = ET.Element('kml')
    tree._setroot(kml)
    doc = ET.SubElement(kml, 'Document')
    ET.SubElement(doc, 'name').text = 'Airports'

    log('Processing...')
    for member in dbRoot:
        m = member[0]
        if m.tag != f'{AIXM}AirportHeliport':
            continue

        try:
            icao = m.findall(f'.//{AIXM}locationIndicatorICAO')
            if icao:
                loc = icao[0].text
            else:
                loc = m.findall(f'.//{AIXM}designator')[0].text

            if loc not in airports:
                continue

            pos = m.findall(f'.//{AIXM}ARP/{AIXM}ElevatedPoint/{GML}pos')[0].text
            log(loc)

        except IndexError:
            continue

        place = ET.SubElement(doc, 'Placemark')
        ET.SubElement(place, 'name').text = loc
        point = ET.SubElement(place, 'Point')
        ET.SubElement(point, 'coordinates').text = pos.replace(' ', ',')

    log('Writing KML...')
    tree.write(args.output, xml_declaration=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert NAV data from the FAA format to KML',
        epilog='Get current databases at https://nfdc.faa.gov')
    parser.add_argument('database', help='FAA APT_AIXM.xml file')
    parser.add_argument('airports', help='List of desired airports')
    parser.add_argument('output', help='KML output file')
    parser.add_argument('--foreflight', action='store_true',
        help='Parse desired airports from a Foreflight logbook')

    main(parser.parse_args())
