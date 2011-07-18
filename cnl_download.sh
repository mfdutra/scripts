#!/bin/bash

# $Id: cnl_download.sh 3227 2010-03-22 21:28:53Z marlon $

# Baixa o arquivo Central CNL para todos os estados brasileiros
#
# Marlon -- Mon, 22 Mar 2010 17:30:50 -0300

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
