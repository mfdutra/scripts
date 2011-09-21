#!/usr/bin/python

# A CGI script to query a device via snmp about if/outOctets of a network
# interface
#
# Expected call: snmpget-if.cgi?ifIndex=1&host=router.domain

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

import cgi
import json
import netsnmp # apt-get install libsnmp-python
import sys

form = cgi.FieldStorage()

ifIndex = form.getvalue('ifIndex')
inOctets = netsnmp.Varbind('.1.3.6.1.2.1.2.2.1.10.%s' % ifIndex)
outOctets = netsnmp.Varbind('.1.3.6.1.2.1.2.2.1.16.%s' % ifIndex)
netsnmp.snmpget(inOctets, outOctets, Version=1, DestHost=form.getvalue('host'), Community=form.getvalue('community', 'public'))

print 'Content-type: application/json\n'

if inOctets.val:
	print json.dumps({'inOctets': inOctets.val, 'outOctets': outOctets.val})
else:
	print json.dumps({'error': 'No data from SNMP server'})
