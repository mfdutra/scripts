#!/usr/bin/env zsh
# Format an SD card volume as ExFAT on macOS, keeping its volume name.
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <device>   (e.g. /dev/disk4s1)" >&2
  exit 1
fi

if (( EUID != 0 )); then
  echo "This script must be run as root." >&2
  exit 1
fi

device="$1"

if [ ! -b "$device" ]; then
  echo "$device is not a block device." >&2
  exit 1
fi

info="$(diskutil info -plist "$device")"

info_get() {
  plutil -extract "$1" raw -o - - <<<"$info" 2>/dev/null || true
}

# built-in SD readers report Internal=true, so check for removable/external instead
if [ "$(info_get RemovableMediaOrExternalDevice)" != "true" ]; then
  echo "Refusing to format $device: it is not removable or external media." >&2
  exit 1
fi

if [ "$(info_get WholeDisk)" = "true" ]; then
  echo "Refusing to format $device: it is a whole disk, pass a partition (e.g. ${device}s1)." >&2
  exit 1
fi

name="$(info_get VolumeName)"
if [ -z "$name" ]; then
  echo "Could not determine the volume name of $device." >&2
  exit 1
fi

read -r "answer?Erase $device ($name) and format as ExFAT? [y/N] "
if [[ ! "$answer" =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

if [ "$(info_get MountPoint)" != "" ]; then
  diskutil unmount "$device"
fi

diskutil eraseVolume ExFAT "$name" "$device"

mount_point() {
  diskutil info -plist "$device" | plutil -extract MountPoint raw -o - - 2>/dev/null || true
}

# eraseVolume usually mounts the new volume; mount it if it didn't
if [ -z "$(mount_point)" ]; then
  diskutil mount "$device"
fi

mnt="$(mount_point)"
if [ -z "$mnt" ]; then
  echo "Could not determine the mount point of $device." >&2
  exit 1
fi

# keep Spotlight from indexing the volume
touch "$mnt/.metadata_never_index"
mdutil -i off "$mnt"
