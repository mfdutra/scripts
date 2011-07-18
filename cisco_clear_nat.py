#!/usr/bin/python

import sys

# $Id: cisco_clear_nat.py 3904 2010-09-19 16:31:02Z marlon $

# Get output from 'show ip nat translations' in STDIN and print 'clear ip nat
# translation' lines to STDOUT

for line in sys.stdin:
	line = line.strip()
	line = line.replace(':', ' ')
	fields = line.split()

	print 'clear ip nat translation %s inside %s %s %s %s outside %s %s %s %s' % tuple(fields)
