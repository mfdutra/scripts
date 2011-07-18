#!/usr/bin/python

# $Id: udpflood-af.py 4304 2011-06-27 19:04:19Z marlon $

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
