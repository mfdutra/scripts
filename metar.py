#!/usr/bin/env python3

# Metar retriever

# Formats supported:
# ./metar KHWD KSFO KJFK
# ./metar @CA  # all airports in California
# ./metar '~BR'  # all airports in Brazil

# Copyright 2012-2020 Marlon Dutra
#
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

import sys
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from urllib.parse import urlencode

station = ','.join(sys.argv[1:]).upper()

params = {
    'dataSource': 'metars',
    'format': 'xml',
    'hoursBeforeNow': '2',
    'mostRecentForEachStation': 'constraint',
    'requestType': 'retrieve',
    'stationString': station,
}

url = 'https://www.aviationweather.gov/adds/dataserver_current/httpparam?' + urlencode(params)
req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    r1 = urlopen(req)
except Exception as e:
    print(f'Error fetching {url}', file=sys.stderr)
    raise

root = ET.fromstring(r1.read())

for m in root.findall('./data/METAR'):
    print(m.find('./raw_text').text)
