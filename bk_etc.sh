#!/bin/bash

# $Id: bk_etc.sh 3880 2010-09-10 15:00:29Z marlon $

KEEP=30
DIR=/var/backups/etc

umask 077
mkdir -p "$DIR"

cd "$DIR" || exit 1

DATA=`date +"%Y%m%d"`
FILE="etc-$DATA.tar.gz"

tar czf $FILE /etc > /dev/null 2> /dev/null

find "$DIR" -mtime +$KEEP -name 'etc-*' -exec rm -f {} \;
