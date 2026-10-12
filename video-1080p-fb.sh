#!/bin/zsh

set -euo pipefail

for f in $@; do
  ffmpeg -hwaccel videotoolbox -i "$f" \
    -vf "fps=30,scale=1920:1080:flags=lanczos" \
    -c:v h264_videotoolbox -b:v 12M -maxrate 16M -bufsize 24M \
    -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart \
    "${f:r}_1080p.mp4"

done
