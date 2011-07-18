#!/usr/bin/python

# Calculate the easter day for a given year

# Copyright 2011 Marlon Dutra
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

import sys
import math
import datetime

def week(day):
	return int(math.ceil(day/7.0))

ano = int(sys.argv[1])

a = ano % 19
b = ano / 100
c = ano % 100
d = b / 4
e = b % 4
f = (b + 8) / 25
g = (b - f + 1) / 3
h = ((19 * a) + b - d - g + 15) % 30
i = c / 4
k = c % 4
l = (32 + 2*e + 2*i - h - k) % 7
m = (a + 11*h + 22*l) / 451

mes = (h + l - 7*m + 114) / 31

dia = ((h + l - 7*m + 114) % 31) + 1

pascoa = datetime.date(ano, mes, dia)
diff = datetime.timedelta(days=47)
carnaval = pascoa - diff
print pascoa, carnaval

# print '%02d/%02d/%d' % (dia, mes, ano, week)
