#!/usr/bin/python

# Move messages from a folder to another one according to a search criterion
#
# Marlon Dutra -- Fri, 09 Apr 2010 15:31:28 -0300

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

import getpass
import imaplib
import datetime
import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option('-s', '--server', dest='server', default='imap')
parser.add_option('-p', '--port', dest='port', default=143, type='int')
parser.add_option('-f', '--folder', dest='folder', default='INBOX')
parser.add_option('-u', '--user', dest='user', default=getpass.getuser())
parser.add_option('-c', '--criterion', dest='criterion', default='ALL')
parser.add_option('-t', '--to-folder', dest='to_folder', metavar='FOLDER')

# Criterion example: SENTSINCE 01-Oct-2009 SENTBEFORE 31-Oct-2009

(options, args) = parser.parse_args()

if not options.to_folder:
	print 'ERROR: destination folder is mandatory'
	sys.exit(1)

print 'Connecting to %s:%d...' % (options.server, options.port),
M = imaplib.IMAP4(options.server, options.port)
print 'connected'

print 'Authenticating user %s' % options.user
M.login(options.user, getpass.getpass())

print 'Checking destination folder %s' % (options.to_folder)
status, result = M.select(options.to_folder)

if status != 'OK':
	print 'ERROR: %s' % (result[0])
	sys.exit(1)

print 'Selecting IMAP folder %s' % options.folder
status, result = M.select(options.folder)

if status == 'OK':
	print '%s messages in the folder' % (result[0])
else:
	print 'ERROR: %s' % (result[0])
	sys.exit(1)

print 'Search messages matching criterion: %s' % (options.criterion)
status, result = M.search(None, '(UNDELETED %s)' % (options.criterion))

messages = result[0].split()
comma_msg = ','.join(messages)

print '%d messages matching the criterion' % (len(messages))

if len(messages) == 0:
	print 'Aborting. Nothing to do.'
	sys.exit()

print 'Copying %d messages from %s to %s' % (len(messages), options.folder, options.to_folder)
M.copy(comma_msg, options.to_folder)

print 'Deleting messages from %s' % (options.folder)
M.store(comma_msg, '+FLAGS', '\\Deleted')

print 'Expunging deleted messages'
M.expunge()

print 'Done.'
