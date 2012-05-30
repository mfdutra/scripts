#!/usr/bin/python

# Compare the packages installed in two computers and show the difference
# between them, considering the version of the packages

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
#
# $Id$

import re
import os
import subprocess
import sys

remoteHost = sys.argv[1]

# Get local
dpkg = subprocess.Popen(('/usr/bin/dpkg-query', '--show'), stdout=subprocess.PIPE)
localList = set(dpkg.communicate()[0].split('\n')[:-1])

# Get remote
dpkg = subprocess.Popen(('/usr/bin/ssh', remoteHost, '/usr/bin/dpkg-query', '--show'), stdout=subprocess.PIPE)
remoteList = set(dpkg.communicate()[0].split('\n')[:-1])

# Check what is different in the local host
diffLocal = list(localList - remoteList)

if diffLocal:
	for i in range(len(diffLocal)):
		diffLocal[i] = diffLocal[i].replace('\t', '=')

	print '#\n# There is a difference between the hosts. Run:\n#'

	print 'apt-get install ' + ' '.join(diffLocal)

# Check packages installed in the remote host but not here

# Remove version information from the lists
localList = list(localList)
remoteList = list(remoteList)
throwVersion = re.compile('\t.*')
for i in range(len(localList)):
	localList[i] = throwVersion.sub('', localList[i])
for i in range(len(remoteList)):
	remoteList[i] = throwVersion.sub('', remoteList[i])

localList = set(localList)
remoteList = set(remoteList)
deletePkg = remoteList - localList

if deletePkg:
	print '#\n# There are too many packages in the remote host. Run:\n#'
	print 'apt-get remove ' + ' '.join(deletePkg)
