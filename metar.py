#!/usr/bin/python

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

import httplib
import sys

station = sys.argv[1].upper()

conn = httplib.HTTPConnection("weather.noaa.gov")
conn.request('GET', '/pub/data/observations/metar/stations/%s.TXT' % station)
r1 = conn.getresponse()

if r1.status != 200:
	print >> sys.stderr, 'Could not get METAR information: %d %s' % (r1.status, r1.reason)
	sys.exit(1)

data = r1.read()

print data.strip()
