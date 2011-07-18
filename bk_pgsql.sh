#!/bin/bash

# Script to backup Postgresql daily

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

DIR=/var/backups/postgres
KEEP=30

if [ "`id -un`" != "postgres" ]
then
        echo This should be run by user postgres > /dev/stderr
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
