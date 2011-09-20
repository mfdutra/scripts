#!/usr/bin/python

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

import sys

group = (0, 128, 255)

print '<html><body>'

colors = []

for r in group:
	for g in group:
		for b in group:
			colors.append('#%02X%02X%02X' % (r,g,b))
			print '<div style="background-color: #%02X%02X%02X">&nbsp;</div>' % (r,g,b)

print '</body></html>'

print >> sys.stderr, colors
