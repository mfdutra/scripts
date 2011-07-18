#!/usr/bin/python

# $Id: makepasswd.py 4191 2011-04-22 19:38:21Z marlon $

import random

CHARS=8

data = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9')

result = ''
for i in range(CHARS):
	result += random.choice(data)

print result
