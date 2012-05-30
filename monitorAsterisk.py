#!/usr/bin/python

# Function to monitor Asterisk CPU usage. If the CPU usage is constant over 90%
# for more than a couple seconds, the function returns true.

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

import time
import subprocess

def checkAsteriskCpu():
	REPEAT=5 # check CPU 5 times
	DELAY=1 # wait 1 second between each check
	THRESHOLD=90 # 90% CPU in average

	# Find Asterisk PID
	ps = subprocess.Popen(('/bin/ps', 'axf'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	ps = ps.communicate()[0]
	pid = None

	for line in ps.split('\n'):
		if '/usr/sbin/asterisk' in line and '/etc/asterisk/asterisk.conf' in line:
			pid = line.split()[0]
			break

	if pid is None:
		raise Exception('Asterisk is not running or socket is invalid')

	cpuReads = []
	for i in range(REPEAT):
		ps = subprocess.Popen(('/bin/ps', '-p', pid, '-o', '%cpu='), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		cpuReads.append(float(ps.communicate()[0].strip()))
		time.sleep(DELAY)

	avg = sum(cpuReads) / len(cpuReads)

	return (avg > THRESHOLD)

######################################################################

if __name__ == '__main__':
	print checkAsteriskCpu()
