#!/bin/bash

# Script to backup /etc daily

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

KEEP=30
DIR=/var/backups/etc

umask 077
mkdir -p "$DIR"

cd "$DIR" || exit 1

DATA=`date +"%Y%m%d"`
FILE="etc-$DATA.tar.gz"

tar czf $FILE /etc > /dev/null 2> /dev/null

find "$DIR" -mtime +$KEEP -name 'etc-*' -exec rm -f {} \;
