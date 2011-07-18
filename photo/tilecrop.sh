#!/bin/bash

# Cut a photo in multiple tiles of a given size

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

SIZE=$1
FILE=$2

if [ -z "$FILE" ]
then
	echo "Usage: $0 size filename"
	exit 1
fi

BASE=`echo "$FILE" | cut -d. -f1`
EXT=`echo "$FILE" | cut -d. -f2`

NEWFILE="${BASE}%02d.${EXT}"

convert "$FILE" -crop "$SIZE" +repage +adjoin "$NEWFILE"

for I in ${BASE}??.${EXT}
do
	convert -trim "$I" "$I"
done
