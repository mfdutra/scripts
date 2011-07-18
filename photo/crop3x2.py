#!/usr/bin/python

# $Id: crop3x2.py 3782 2010-08-01 23:06:55Z marlon $

# Transform images with aspect ratio of 4x3 to 3x2, considering the orientation

# Depends: exiv2 imagemagick

# Marlon Dutra
# Sun, 01 Aug 2010 19:50:34 -0300

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
