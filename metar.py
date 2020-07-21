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
from urllib.request import urlopen

station = ','.join(sys.argv[1:]).upper()

r1 = urlopen(f'https://www.aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=xml&hoursBeforeNow=1&stationString={station}')
root = ET.fromstring(r1.read())

for m in root.findall('./data/METAR'):
    print(m.find('./raw_text').text)
