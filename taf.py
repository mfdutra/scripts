#!/usr/bin/python

# TAF getter and formatter

# Marlon Dutra
# Thu, 24 Feb 2011 09:22:14 -0300

# Copyright 2011 Marlon Dutra
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

import httplib
import re
import sys

station = sys.argv[1].upper()

conn = httplib.HTTPConnection("weather.noaa.gov")
conn.request('GET', '/pub/data/forecasts/taf/stations/%s.TXT' % station)
r1 = conn.getresponse()

if r1.status != 200:
	print >> sys.stderr, 'Could not get TAF information: %d %s' % (r1.status, r1.reason)
	sys.exit(1)

data = r1.read()

# Clean up
data = data.replace('\n', ' ')
data = data.replace('\r', '')
data = re.sub('\s+', ' ', data)
data = re.sub('^.*TAF ', 'TAF ', data)
data = data.strip()

# Formatting
data = re.sub(' (PROB.0)', '\n  \\1', data)
data = re.sub(r'(PROB.0) TEMPO', r'\1XXTEMPO', data)
data = data.replace(' TEMPO', '\n  TEMPO')
data = re.sub(r'(PROB.0)XXTEMPO', r'\1 TEMPO', data)
data = data.replace(' RMK', '\n  RMK')
data = data.replace(' BECMG', '\n  BECMG')
data = re.sub(' (FM\d+)', '\n  \\1', data)

print data
