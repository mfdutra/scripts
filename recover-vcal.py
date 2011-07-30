#!/usr/bin/python -u

# Walk through a whole file or device (like a hard disk) looking for
# VCalendars. Useful when you format a disk and accidentally lose your iCal.

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

BUFFER = 4 * 1024 * 1024 # 4 MB

devName = sys.argv[1]

device = open(devName, 'r')
current = 0
vcalFound = 0
broken = 0

while True: # itter the whole file
	data = device.read(BUFFER)
	if not data: break
	current += BUFFER
	print '%.2f\r' % (current / 1024.0 / 1024.0),
	byte = 0

	while byte <= BUFFER:
		# Find a vcal ocurrence in the buffer
		pos = data[byte:].find('BEGIN:VCALENDAR')
		if pos >= 0:
			byte += pos # skip directly to the vcal

			pos2 = data[byte:].find('END:VCALENDAR')
			if pos2 >= 0: # found a whole vcal block
				vcalFound += 1
				ics = open(str(vcalFound) + '.ics', 'w')
				ics.write(data[byte:byte+pos2+13])
				byte += pos2
				ics.close()

				print 'VCalendar %d written' % (vcalFound)

			else: # block end not found
				broken += 1
				ics = open('broken-' + str(broken) + '.ics', 'w')
				ics.write(data[byte:byte+1024])
				ics.close()
				print 'Broken VCalendar %d written' % (broken)
				break

		else: # no vcal in this buffer
			break
