#!/usr/bin/python

# Calcula os feriados lunares no Brasil
#
# $Id: feriados_lunares.py 1730 2009-04-04 16:00:20Z marlon $

import sys
import math
import datetime

def pascoa(ano):
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

	return datetime.date(ano, mes, dia)

######################################################################

def insertIntoPg(holidays):
	import psycopg2

	print 'Hostname: ',
	host = sys.stdin.readline().strip()
	print 'Senha: ',
	passwd = sys.stdin.readline().strip()

	conn = psycopg2.connect('dbname=asterisk host=%s user=asterisk password=%s' % (host, passwd))
	curs = conn.cursor()

	values = ','.join([ str(h) for h in holidays ])
	sql = 'INSERT INTO holidays ("descr", "date") VALUES %s' % values

	curs.execute(sql)

	conn.commit()

######################################################################

inicio, fim = sys.argv[1:3]

carnaval = datetime.timedelta(days=-47)
sextasanta = datetime.timedelta(days=-2)
corpus = datetime.timedelta(days=60)

result = []
for ano in range(int(inicio), int(fim)):
	pasc = pascoa(ano)
	
	result.append(('Carnaval', (pasc + carnaval).isoformat()))
	result.append(('Sexta-feira santa', (pasc + sextasanta).isoformat()))
	result.append(('Corpus Christi', (pasc + corpus).isoformat()))

insertIntoPg(result)
