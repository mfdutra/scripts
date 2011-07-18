#!/usr/bin/python

# $Id: today.py 3225 2010-03-22 19:25:14Z marlon $

from datetime import datetime, timedelta
import sys

op, delta = sys.argv[1:3]

assert op in ('+', '-')

delta = int(delta)

today = datetime.now()

if op == '+':
	new = today + timedelta(delta)

else:
	new = today - timedelta(delta)

print new
