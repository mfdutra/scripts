#!/usr/bin/python

# Resize photos in multithread, to take advantage of multi-core CPUs

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
