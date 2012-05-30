#!/usr/bin/python

# Check if a process is sucking the CPU
#
# Marlon Dutra
# Mar 29, 2012

# Copyright 2012 Marlon Dutra
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

import subprocess
import sys
import time

TIMES=5
SLEEP=0.2
THRESHOLD=90

try:
	procName = sys.argv[1]
except:
	print 'Usage: %s process-name' % (sys.argv[0])
	sys.exit(10)

pid = subprocess.Popen(('pgrep', '-x', procName), stdout=subprocess.PIPE).communicate()[0].split()

if not pid:
	print 'No process %s running' % (procName)
	sys.exit(11)

count = 0
for i in range(TIMES):
	pcpu = float(subprocess.Popen(('ps', '-p', pid[0], '-o', 'pcpu='), stdout=subprocess.PIPE).communicate()[0].strip())

	if pcpu > THRESHOLD:
		count += 1

	time.sleep(SLEEP)

if count >= TIMES:
	print 'Process %s (PID %s) is sucking the CPU' % (procName, pid[0])
	sys.exit(1)
else:
	print 'Process %s (PID %s) is performing ok' % (procName, pid[0])
