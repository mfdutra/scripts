#!/bin/bash

# Baixa o arquivo Central CNL para todos os estados brasileiros
#
# Marlon -- Mon, 22 Mar 2010 17:30:50 -0300

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

for ST in AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO
do
	POST="varTIPO=CentralCNL&varPRESTADORA=&varCENTRAL=F&varUF=${ST}&varPERIODO=&acao=c&cmd=&varMOD=Publico"

	echo
	echo "*** $ST ***"
	echo

	wget --post-data="$POST" --output-document="${ST}.zip" 'http://sistemas.anatel.gov.br/areaarea/N_Download/Tela.asp'

	unzip ${ST}.zip '*TXT'
done

cat *TXT > todos.txt
