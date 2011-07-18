#!/usr/bin/python

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
