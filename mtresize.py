#!/usr/bin/python

# $Id: mtresize.py 1019 2008-07-27 23:41:12Z marlon $

import os
import sys
import thread
import time

# Cores in CPU
cores = 2

# Threads running counter
threads = 0

# Skip the 1st element (process name)
sys.argv.pop(0)

# Check if 1st argument is integer (new image size)
try:
	size = int(sys.argv.pop(0))
	size = str(size)
except ValueError:
		print >> sys.stderr, "Usage: mtresize newsize file1 file2 filen"
		sys.exit(1)

## THREAD ############################################################

def resize(thr, photos):
	global threads
	global size
	threads += 1

	for i in photos:
		file = sys.argv[i]
		base = os.path.basename(file)

		os.system('convert -verbose -resize ' + size + 'x' + size + ' ' + file + ' ./' + base)

	threads -= 1

######################################################################

total = len(sys.argv)

for i in range(cores):
	rge = range(i, total, cores)
	thread.start_new_thread(resize, (i, rge))

time.sleep(1)
# Wait for the threads to die and to be buried
while threads:
	time.sleep(1)
