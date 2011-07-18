#!/usr/bin/python -u

# $Id: bw-meter.py 4080 2011-03-01 18:56:34Z marlon $

# Measure the bandwidth of an interface based on a sample time

# Marlon Dutra
# Tue Mar 1st, 2011

from optparse import OptionParser
import netsnmp # apt-get install libsnmp-python
import sys
import time

parser = OptionParser()

parser.add_option('-c', '--community', default='public')
parser.add_option('-r', '--router', metavar='ROUTER-IP')
parser.add_option('-i', '--interface', metavar='IFACE-SNMP-ID', type='int')
parser.add_option('-s', '--sample', metavar='SECONDS', type='int', default=5)
parser.add_option('-l', '--list', action='store_true', help='List interfaces')

(options, args) = parser.parse_args()

if not options.router:
	parser.print_help()
	sys.exit(1)

if options.list: # list router interfaces
	ifDescr = netsnmp.VarList('.1.3.6.1.2.1.2.2.1.2')
	netsnmp.snmpwalk(ifDescr, Version=1, DestHost=options.router, Community=options.community)

	print 'Interfaces in router %s' % options.router
	print
	print 'SNMP-ID\tDESCRIPTION'
	for i in ifDescr:
		print '%s\t%s' % (i.iid, i.val)

	sys.exit()

if not options.interface:
	parser.print_help()
	sys.exit(1)

ifDescr = netsnmp.Varbind('.1.3.6.1.2.1.2.2.1.2.%d' % (options.interface))
netsnmp.snmpget(ifDescr, Version=1, DestHost=options.router, Community=options.community)

if not ifDescr.val:
	print >> sys.stderr, 'Invalid interface id %d' % options.interface
	sys.exit(1)

print 'Router: %s' % options.router
print 'Interface: %d (%s)' % (options.interface, ifDescr.val)
print 'Sampling: %d seconds' % (options.sample)
print

# Get first values
oidIn  = netsnmp.Varbind('.1.3.6.1.2.1.2.2.1.10.%d' % options.interface)
oidOut = netsnmp.Varbind('.1.3.6.1.2.1.2.2.1.16.%d' % options.interface)
netsnmp.snmpget(oidIn, oidOut, Version=1, DestHost=options.router, Community=options.community)

input  = int(oidIn.val)
output = int(oidOut.val)

try:
	while True:
		time.sleep(options.sample)

		netsnmp.snmpget(oidIn, oidOut, Version=1, DestHost=options.router, Community=options.community)

		deltaIn = int(oidIn.val) - input
		deltaOut = int(oidOut.val) - output
		input  = int(oidIn.val)
		output = int(oidOut.val)

		rateIn = float(deltaIn) / options.sample * 8 / 1024
		rateOut = float(deltaOut) / options.sample * 8 / 1024

		print 'IN: %.2f Kbps   OUT: %.2f Kbps         \r' % (rateIn, rateOut),

except KeyboardInterrupt:
	print '\nExiting'
	sys.exit()
