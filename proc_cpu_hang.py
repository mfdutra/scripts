#!/usr/bin/python

# Check if a process is sucking the CPU
#
# Marlon Dutra
# Mar 29, 2012

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
