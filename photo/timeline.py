#!/usr/bin/env python

# Organize photos in a yyyy/mm/dd directory structure based on EXIF date/time
# creation

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

def usage():
	print >> sys.stderr, "Usage: " + sys.argv[0] + " output_directory file1.jpg file2.jpg fileN.jpg..."

###########################################################################

if len(sys.argv) < 3:
	usage()
	sys.exit(1)

args = sys.argv

# Remove the 0th array element, the script itself
args.pop(0)
output = args.pop(0)

# Check if the output directory isn't actually a file
if os.path.isfile(output):
	print >> sys.stderr, output + " is a file, not a directory."
	usage()
	sys.exit(2)

# Create the output directory in case of it doesn't exist yet
if not os.path.isdir(output):
	try:
		print "Creating " + output
		os.makedirs(output)
	except OSError, (errno, strerror):
		print >> sys.stderr, "Unable to create " + output + ": " + strerror
		sys.exit(3)

# Check access to output dir
if not os.access(output, os.W_OK):
	print >> sys.stderr, "Permission denied to write in " + output
	sys.exit(4)

# Iterate all the files
for file in args:

	# Extract EXIF info
	if os.path.isfile(file) and os.access(file, os.R_OK):
		exif = os.popen('exif -i ' + file).readlines()

		date = ''
		datetime = ''
		# Look for capture date (tag 0x9003)
		for line in exif:
			if line.find('0x9003|') == 0:
				datetime = line.split('|')[1]
				date = datetime[:10]
	
		if not date:
			print "Unable to read capture date from " + file
			continue

		date = date.replace(':', '/')
		dst = output + '/' + date

		# Create the directory if it doesn't exist yet
		if not os.path.isdir(dst):
			print "Creating " + dst
			os.makedirs(dst)

		# Move the file to there
		print "Moving %s to %s" % (file, dst)
		shutil.move(file, dst)

	else:
		print >> sys.stderr, 'Unable to read ' + file
