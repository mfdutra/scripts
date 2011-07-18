#!/usr/bin/python

# Watch an Asterisk's module via inotify to determite when it's starting up and
# then load res_config_pgsql.so afterwards.
#
# This is necessary due to a bug in Asterisk startup sequence. If
# res_config_pgsql.so is loaded with Asterisk, it segfaults 90% of the times.
#
# Marlon Dutra -- Fri, 16 Apr 2010 14:42:45 -0300

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

ASTERISK = '/usr/sbin/asterisk'
MONITOR = '/usr/lib/asterisk/modules/chan_sip.so'
TIMEOUT = 5

import pyinotify # apt-get install python-pyinotify
import subprocess
import time
import syslog

syslog.openlog('asterisk_mon_start', syslog.LOG_PID, syslog.LOG_DAEMON)
syslog.syslog('Asterisk start monitor running')

class HandleEvents(pyinotify.ProcessEvent):
	def process_IN_ACCESS(self, event):
		'''Event triggered'''

		syslog.syslog('Caught access event in %s' % (MONITOR))

		ast = subprocess.Popen((ASTERISK, '-rx', 'module show like res_config_pgsql.so'), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		stdout, stderr = ast.communicate()
		loaded = stdout.split('\n')[-2].split()[0] # 1st char in last line

		if loaded == '0':
			time.sleep(TIMEOUT)
			syslog.syslog('Loading res_config_pgsql.so in Asterisk')
			ast = subprocess.Popen((ASTERISK, '-rx', 'module load res_config_pgsql.so'), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
			retcode = ast.wait()

			if retcode > 0:
				syslog.syslog(syslog.LOG_ERR, 'Error connecting to running Asterisk to launch res_config_pgsql.so, via %s' % (ASTERISK))

######################################################################

wm = pyinotify.WatchManager()
p = HandleEvents()
notifier = pyinotify.Notifier(wm, p)
wdd = wm.add_watch(MONITOR, pyinotify.IN_ACCESS)
notifier.loop()
