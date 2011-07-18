#!/usr/bin/python

# Generate an hexa-represented DNS zone of a given CIDR
#
# Marlon Dutra
# January 12th, 2009
#
# $Id: gen_hex_dns.py 4070 2011-02-26 13:43:44Z marlon $
#
# Dependencies:
#   apt-get install python-ipy

from ip_to_hex import ip_to_hex
import sys
import os
from IPy import IP

def usage():
	print >> sys.stderr, 'Usage: %s cidr domain type ("a" or "ptr")' % sys.argv[0]
	sys.exit(1)
#####

if len(sys.argv) < 4:
	usage()

cidr = sys.argv[1]
domain = sys.argv[2]
type = sys.argv[3]

if type != 'a' and type != 'ptr':
	usage()

# Force domain to end with a dot
if not domain.endswith('.'):
	domain += '.'

iplist = IP(cidr)

for ip in iplist:
	if type == 'a':
		print '%s.%s IN A %s' % (ip_to_hex(ip.strNormal()), domain, ip)
	elif type == 'ptr':
		print '%s IN PTR %s.%s' % (ip.reverseName(), ip_to_hex(ip.strNormal()), domain)
