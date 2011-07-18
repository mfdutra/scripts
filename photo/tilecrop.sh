#!/bin/bash

# $Id: tilecrop.sh 4266 2011-06-05 19:00:11Z marlon $

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
