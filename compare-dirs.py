#!/usr/bin/env python3

# Recursively compare two directories by file names and sizes only.
# Files are never opened, only stat()'ed. Exits 1 if there are differences.

# Copyright 2026 Marlon Dutra
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

import argparse
import os
import stat
import sys


def scan(root):
    """Map each relative path under root to its size (None for directories)."""

    def entry(dirpath, name):
        full = os.path.join(dirpath, name)
        st = os.lstat(full)
        size = None if stat.S_ISDIR(st.st_mode) else st.st_size
        return os.path.relpath(full, root), size

    return dict(
        entry(dirpath, name)
        for dirpath, dirnames, filenames in os.walk(root)
        for name in dirnames + filenames
    )


def describe(size):
    return "directory" if size is None else f"{size} bytes"


def main():
    parser = argparse.ArgumentParser(
        description="Compare two directories by file names and sizes."
    )
    parser.add_argument("dir1")
    parser.add_argument("dir2")
    args = parser.parse_args()

    for d in (args.dir1, args.dir2):
        if not os.path.isdir(d):
            parser.error(f"not a directory: {d}")

    a, b = scan(args.dir1), scan(args.dir2)

    only_a = [f"Only in {args.dir1}: {p}" for p in sorted(a.keys() - b.keys())]
    only_b = [f"Only in {args.dir2}: {p}" for p in sorted(b.keys() - a.keys())]
    differ = [
        f"Differs: {p} ({describe(a[p])} vs {describe(b[p])})"
        for p in sorted(a.keys() & b.keys())
        if a[p] != b[p]
    ]

    diffs = only_a + only_b + differ
    if diffs:
        print(*diffs, sep="\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
