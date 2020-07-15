#!/usr/bin/env python3

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen

def main():
    response = urlopen('https://cirrus-locator-v2-stage.herokuapp.com/api/v1/asc')
    centers = json.loads(response.read())

    # Output
    tree = ET.ElementTree()
    kml = ET.Element('kml')
    tree._setroot(kml)
    doc = ET.SubElement(kml, 'Document')
    ET.SubElement(doc, 'name').text = 'Service Centers'

    for c in centers['data']:
        place = ET.SubElement(doc, 'Placemark')
        ET.SubElement(place, 'name').text = c['airport_name']
        ET.SubElement(place, 'description').text = c['account_name']
        point = ET.SubElement(place, 'Point')
        ET.SubElement(point, 'coordinates').text = f"{c['longitude__c']},{c['latitude__c']}"

    with open(sys.argv[1], 'wb') as fd:
        tree.write(fd, xml_declaration=True)

if __name__ == '__main__':
    main()
