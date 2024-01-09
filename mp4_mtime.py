#!/usr/bin/env python3

# Set filesystem modification time according to video time of creation

# Copyright 2024 Marlon Dutra
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

import os
import sys
import subprocess
import time

for file in sys.argv[1:]:
	if os.path.isfile(file) and os.access(file, os.R_OK):
		p = subprocess.run("ffprobe " + file, capture_output=True, shell=True)

		datetime = ''
		for line in p.stderr.decode('utf-8').split("\n"):
			if 'creation_time' in line:
				datetime = line.split(':', maxsplit=1)[1].strip()

				mtime = time.strptime(datetime, '%Y-%m-%dT%H:%M:%S.000000Z')

				print(file + ": " + datetime)
				os.utime(file, (-1, int(time.mktime(mtime))))

				break

		if not datetime:
			print("Unable to read capture date from " + file)
			continue

