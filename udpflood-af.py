#!/usr/bin/python

# Create a multiprocess UDP flood, with one flood in each DiffServ AF class, to
# stress test QoS mechanisms based in DiffServ

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

import multiprocessing
import socket
import sys
import time

HOST = sys.argv[1]
PORT = int(sys.argv[2])
PKTLEN = 1472

# All AF members
AFs = (10, 12, 14, 18, 20, 22, 26, 28, 30, 34, 36, 38)

kill = False

def worker(af, host, port):
	global PKTLEN, kill

	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, af << 2)
	s.connect((host, port))

	while not kill:
		try:
			s.send('x' * PKTLEN)
		except: pass

forks = []
for af in AFs:
	print 'Starting worker to %s:%d AF %d' % (HOST, PORT, af)
	p = multiprocessing.Process(target=worker, args=(af, HOST, PORT))
	forks.append(p)
	p.start()
	PORT += 1

try:
	while True:
		time.sleep(1)

except:
	print 'Killing sub processes',
	for p in forks:
		p.terminate()
		print '.',
	print
