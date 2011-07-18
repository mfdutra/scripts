#!/usr/bin/env python

# $Id: mtime.py 912 2008-04-23 00:36:54Z marlon $

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
