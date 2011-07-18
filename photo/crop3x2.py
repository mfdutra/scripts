#!/usr/bin/python

# Transform images with aspect ratio of 4x3 to 3x2, considering the orientation

# Depends: exiv2 imagemagick

# Marlon Dutra
# Sun, 01 Aug 2010 19:50:34 -0300

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

import os
import sys
import subprocess
import re

sizeRe = re.compile('^Image size +: (\d+) x (\d+)')	

for file in sys.argv[1:]:
	if not os.access(file, os.R_OK):
		print >> sys.stderr, 'ERROR: could not read %s' % (file)
		continue

	width = 0
	height = 0

	identify = subprocess.Popen(('exiv2', file), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	info, stderr = identify.communicate()

	for line in info.split('\n'):
		match = sizeRe.search(line)
		if match:
			width, height = match.groups()
			break

	if width and height:
		width = float(width)
		height = float(height)
		aspect = width / height

		if aspect < 1: # portrait
			aspect = 1.0 / aspect

		if int(round(aspect * 1000)) == 1333: # 4x3
			if width > height: # landscape
				newHeight = int(round(width / 1.5))
				offset = int(round((height - newHeight) / 2.0))

				convert = subprocess.Popen(('convert', '-crop', '%dx%d+0+%d' % (width, newHeight, offset), '-verbose', file, file))
				convert.wait()

			else: # portrait
				newWidth = int(round(height / 1.5))
				offset = int(round((width - newWidth) / 2.0))

				convert = subprocess.Popen(('convert', '-crop', '%dx%d+%d+0' % (newWidth, height, offset), '-verbose', file, file))
				convert.wait()

		else: # not 4x3
			print >> sys.stderr, 'ERROR: aspect of %s is not 4x3' % (file)

	else:
		print >> sys.stderr, 'ERROR: could not identify image size in file %s' % (file)
