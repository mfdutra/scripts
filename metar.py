#!/usr/bin/env python3

# METAR

# Marlon Dutra
# Fri Jul  6 16:38:34 BRT 2012

# Copyright 2012 Marlon Dutra
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

import re
import sys
from urllib.request import urlopen

metar_re = re.compile(r'<code>(.*)</code>')

for station in sys.argv[1:]:
    station = station.upper()

    r1 = urlopen(f'https://www.aviationweather.gov/metar/data?ids={station}&format=raw&hours=0&taf=off&layout=off')

    data = r1.read().decode('utf-8')
    match = metar_re.search(data, re.M)

    try:
        print(match.group(1).strip())

    except AttributeError:
        print(f'Could not find METAR for {station}', file=sys.stderr)
