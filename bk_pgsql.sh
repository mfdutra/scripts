#!/bin/bash

# $Id: bk_pgsql.sh 3880 2010-09-10 15:00:29Z marlon $

DIR=/var/backups/postgres
KEEP=30

if [ "`id -un`" != "postgres" ]
then
        echo So o usuario 'postgres' pode rodar este comando > /dev/stderr
        exit 1
fi

DATA=`date +"%Y-%m-%d"`
umask 077
mkdir -p "$DIR"

if [ ! -w "$DIR" ]
then
        echo $DIR not writable. Aborting. > /dev/null
        exit 1
fi

pg_dumpall -c | gzip -c > "$DIR/$DATA.sql.gz"

find "$DIR" -mtime +$KEEP -exec rm -f {} \;
