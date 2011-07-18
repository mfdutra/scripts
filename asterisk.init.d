#!/bin/bash

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
