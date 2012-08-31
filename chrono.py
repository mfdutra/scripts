#!/usr/bin/python

import datetime, time

start = datetime.datetime.now()

while 1:
	now = datetime.datetime.now()
	print '%s' % str(now - start)

	time.sleep(1)
