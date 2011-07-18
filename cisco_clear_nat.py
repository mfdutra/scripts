#!/usr/bin/python

# Get output from 'show ip nat translations' in STDIN and print 'clear ip nat
# translation' lines to STDOUT

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

for line in sys.stdin:
	line = line.strip()
	line = line.replace(':', ' ')
	fields = line.split()

	print 'clear ip nat translation %s inside %s %s %s %s outside %s %s %s %s' % tuple(fields)
