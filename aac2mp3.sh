#!/bin/bash

for AAC in "$@"
do
	BASE=`basename "$AAC" .m4a`

	mplayer -ao pcm:file="$BASE.wav" "$AAC"
	lame "$BASE.wav" "$BASE.mp3"
	rm -f "$BASE.wav"
done
