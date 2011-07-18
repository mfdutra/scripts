#!/usr/bin/python

# Generate an hexa-represented DNS zone of a given CIDR
#
# Marlon Dutra
# January 12th, 2009
#
# Dependencies:
#   apt-get install python-ipy

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
