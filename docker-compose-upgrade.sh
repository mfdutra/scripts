#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -eq 0 ]; then
  echo "Usage: $0 <dir1> [dir2 ...]" >&2
  exit 1
fi

image_state() {
  docker-compose config --images 2>/dev/null | xargs -I{} sh -c \
    'printf "%s %s\n" "{}" "$(docker image inspect --format "{{.Id}}" "{}" 2>/dev/null || echo missing)"' \
    | sort
}

for dir in "$@"; do
  if [ ! -d "$dir" ]; then
    echo "Skipping $dir: not a directory" >&2
    continue
  fi

  echo "==> $dir"
  (
    cd "$dir"

    before="$(image_state)"
    docker-compose pull
    after="$(image_state)"

    if [ "$before" != "$after" ]; then
      echo "Updates found for $dir, recreating containers..."
      docker-compose up -d
    else
      echo "No updates for $dir, skipping."
    fi
  )
done
