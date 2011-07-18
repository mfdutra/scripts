#!/usr/bin/python

# $Id: udpflood.py 4304 2011-06-27 19:04:19Z marlon $

import socket
import sys

HOST = sys.argv[1]
PORT = int(sys.argv[2])
PKTLEN = 1472

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect((HOST, PORT))

while True:
	try:
		s.send('x' * PKTLEN)
	except KeyboardInterrupt: sys.exit()
	except: pass
