#!/usr/bin/python -u

import sys

BUFFER = 4 * 1024 * 1024 # 4 MB

devName = sys.argv[1]

device = open(devName, 'r')
current = 0
vcalFound = 0

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

			vcalFound += 1
			ics = open(str(vcalFound) + '.ics', 'w')

			while True:
				if data[byte:].find('END:VCALENDAR') == 0:
					ics.write(data[byte:byte+13])
					ics.close()
					byte += 13
					break

				else:
					ics.write(data[byte])
					byte += 1

				if byte > BUFFER: # buffer overflow
					break

		else: # no vcal in this buffer
			break
