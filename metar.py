#!/usr/bin/env python3

# Metar retriever

# Copyright 2012-2023 Marlon Dutra
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
from urllib.request import urlopen, Request
from urllib.parse import urlencode

if len(sys.argv) < 2:
    print("Usage: metar AIRPORT1 [AIRPORT2...]", file=sys.stderr)
    sys.exit(1)

params = {
    'ids': ','.join(sys.argv[1:]),
    'format': 'raw',
}

url = 'https://aviationweather.gov/api/data/metar?' + urlencode(params)

req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    r1 = urlopen(req)
except Exception as e:
    print(f'Error fetching {url}', file=sys.stderr)
    raise

print(r1.read().decode('ascii').strip())
