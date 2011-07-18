#!/bin/bash

# A better init script for Asterisk

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

CONFIG=/storage/asterisk/etc/asterisk.conf
DAEMON=/usr/sbin/safe_asterisk

case $1 in
	start)
		if [ ! -r "$CONFIG" ]
		then
			echo $CONFIG not found. Aborting.
			exit 1
		fi
		
		if ! pgrep -f $DAEMON
		then
			/usr/sbin/safe_asterisk -C $CONFIG
			echo "Starting $DAEMON"
		else
			echo "$DAEMON already started"
		fi
		sleep 1
		pgrep -l safe_asterisk
		;;
	stop)
		if pgrep -f $DAEMON
		then
			/usr/sbin/asterisk -rx "stop now"
		else
			echo "$DAEMON already stopped"
		fi
		;;
	reload)
		/usr/sbin/asterisk -rx "reload"
		;;
	restart)
		/usr/sbin/asterisk -rx "restart now"
		;;
	*)
		echo "$0 start | stop | reload | restart"
		;;
esac

exit 0
