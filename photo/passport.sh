#!/bin/zsh

set -xeuo pipefail

montage "$1" "$1" "$1" "$1" "$1" "$1" -tile 3x2 -geometry +0+0 $(basename "$1" .jpg)-grid.jpg
