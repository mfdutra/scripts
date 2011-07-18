#!/usr/bin/env python

# Set filesystem modification time according to EXIF's time of creation

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
import os
import shutil
import time

for file in sys.argv[1:]:
	# Extract EXIF info
	if os.path.isfile(file) and os.access(file, os.R_OK):
		exif = os.popen('exif -i ' + file).readlines()

		datetime = ''
		# Look for capture date (tag 0x9003)
		for line in exif:
			if line.find('0x9003|') == 0:
				datetime = line.split('|')[1].strip()
	
		if not datetime:
			print "Unable to read capture date from " + file
			continue

		mtime = time.strptime(datetime, '%Y:%m:%d %H:%M:%S')

		print file + ": " + datetime
		os.utime(file, (-1, int(time.mktime(mtime))))
