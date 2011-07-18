#!/usr/bin/python

# $Id: timestamp.py 3222 2010-03-19 00:40:41Z marlon $

# Convert a timestamp to a human-reading date/time in the current timezone

# Copyright 2010 Marlon Dutra

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

import sys
from datetime import datetime

for ts in sys.argv[1:]:
	dt = datetime.fromtimestamp(int(ts))
	print dt
