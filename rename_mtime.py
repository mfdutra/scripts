#!/usr/bin/env python3

# Rename a file to its mtime in strftime("%Y%m%d-%H%M%S")

# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.

# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.

# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

import datetime
import os
import sys

for f in sys.argv[1:]:
    mtime = datetime.datetime.fromtimestamp(os.stat(f)[8])
    mtime_str = mtime.strftime("%Y%m%d-%H%M%S")
    if "." in f:
        ext = "." + f.rpartition(".")[2]
    else:
        ext = ""
    new = mtime_str + ext

    if f == new:
        print(f"{f} skipping", file=sys.stderr)
        continue

    # Find a suitable name if one is already used
    i = 2
    while os.path.exists(new):
        new = f"{mtime_str}-{i}{ext}"
        i += 1

    print(f"{f} -> {new}")
    os.rename(f, new)
