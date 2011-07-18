#!/usr/bin/python
# -*- coding: utf-8 -*-

# Marlon Dutra
# Oct 4th, 2008

# http://www.planalto.gov.br/ccivil_03/_ato2007-2010/2008/decreto/d6558.htm
#
# Script to calculate the daylight saving time end date according to the new
# Brazilian rule, that is valid for the following states: Rio Grande do Sul,
# Santa Catarina, Paraná, São Paulo, Rio de Janeiro, Espírito Santo, Minas
# Gerais, Goiás, Mato Grosso, Mato Grosso do Sul and Distrito Federal. All the
# other states don't observe DST.
#
# The rule says that the DST ends always on the 3rd sunday of february, except
# when that date is the carnival sunday. In such a case, the DST ends on the
# next sunday, the 4th sunday of february.
#
# FYI, the carnival sunday is 49 days before the easter.

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

# Returns the easter date for a given year
def easter(year):
	a = year % 19
	b = year / 100
	c = year % 100
	d = b / 4
	e = b % 4
	f = (b + 8) / 25
	g = (b - f + 1) / 3
	h = ((19 * a) + b - d - g + 15) % 30
	i = c / 4
	k = c % 4
	l = (32 + 2*e + 2*i - h - k) % 7
	m = (a + 11*h + 22*l) / 451

	month = (h + l - 7*m + 114) / 31
	day = ((h + l - 7*m + 114) % 31) + 1

	return datetime.date(year, month, day)

# Return the carnival sunday based on an easter day
def carnivalSunday(easter):
	diff = datetime.timedelta(days=49)
	return (easter - diff)

# Return the date plus 7 days
def nextWeek(date):
	diff = datetime.timedelta(days=7)
	return (date + diff)

# Return the 3rd sunday of february of a given year
def dstRuleEnd(year):
	dt = datetime.date(year, 2, 1)
	diff = datetime.timedelta(days = (6 - dt.weekday() + 14))
	dt = dt + diff
	return dt

# Return the DST end date considering the carnival rule
def dstEnd(year):
	easterDate = easter(year)
	carnsunDate = carnivalSunday(easterDate)
	dstEndDate = dstRuleEnd(year)

	if carnsunDate == dstEndDate:
		return nextWeek(dstEndDate)
	else:
		return dstEndDate

######################################################################

try:
	tzFormat = 0
	if sys.argv[1] == '-t':
		tzFormat = 1
		sys.argv.pop(1)

	for year in sys.argv[1:]:
		year = int(year)

		if tzFormat:
			dt = dstEnd(year)
			print 'Rule\tBrazil\t%d\tonly\t-\tFeb\t%d\t 0:00\t0\t-' % (year, dt.day)
		else:
			print dstEnd(year)

except (IndexError, ValueError):
	print >> sys.stderr, 'Usage:', sys.argv[0], '[-t] year1 year2 yearN...'
	print >> sys.stderr, '\n  -t: timezone format'
