#!/usr/bin/python

# A CGI proxy to snmpget, to allow javascript to retrieve snmp data from remote
# hosts

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

varBind = netsnmp.Varbind(form.getvalue('oid'))
netsnmp.snmpget(varBind, Version=1, DestHost=form.getvalue('host'), Community=form.getvalue('community', 'public'))

print 'Content-type: application/json\n'

if varBind.val:
	print json.dumps({'result': varBind.val})
else:
	print json.dumps({'error': 'No data from SNMP server'})
