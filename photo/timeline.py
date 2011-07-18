#!/usr/bin/env python

# $Id: timeline.py 912 2008-04-23 00:36:54Z marlon $

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
