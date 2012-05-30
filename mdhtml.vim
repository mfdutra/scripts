" Shortcuts for HTML
" Marlon Dutra <marlon@propus.com.br>

" Copyright 2011 Marlon Dutra
"
" This program is free software: you can redistribute it and/or modify
" it under the terms of the GNU General Public License as published by
" the Free Software Foundation, either version 3 of the License, or
" (at your option) any later version.
"
" This program is distributed in the hope that it will be useful,
" but WITHOUT ANY WARRANTY; without even the implied warranty of
" MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
" GNU General Public License for more details.
"
" You should have received a copy of the GNU General Public License
" along with this program.  If not, see <http://www.gnu.org/licenses/>.

inoremap <C-CR> <br><CR>

inoremap ,a <a href=""></a><ESC>hhhi

inoremap ,b <b></b><ESC>hhhi

inoremap ,cl class=""<ESC>i

inoremap ,co <!--  --><ESC>hhhi

inoremap ,d <div class=""><CR><TAB><CR><BS></div><ESC>kA

inoremap ,em <i></i><ESC>hhhi

inoremap ,fr <form method="POST" action="" id="form1" name="form1"><CR></form>

inoremap ,h1 <h1></h1><ESC>hhhhi
inoremap ,h2 <h2></h2><ESC>hhhhi
inoremap ,h3 <h3></h3><ESC>hhhhi
inoremap ,h4 <h4></h4><ESC>hhhhi
inoremap ,h5 <h5></h5><ESC>hhhhi
inoremap ,h6 <h6></h6><ESC>hhhhi

" inoremap ,ht <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd"><CR><html><CR><head><CR><TAB><meta http-equiv="Content-Type" content="text/html; charset=ISO-8859-1"><CR><title></title><CR><BS></head><CR><CR><body><CR><CR></body><CR></html><ESC>kkkkkklla

inoremap ,ht <?xml version="1.0" encoding="utf-8"?><CR><!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd"><CR><html xmlns="http://www.w3.org/1999/xhtml" xml:lang="pt_BR"><CR><head><CR><TAB><meta http-equiv="Content-Type" content="text/html; charset=UTF-8" /><CR><title></title><CR><BS></head><CR><CR><body><CR><CR></body><CR></html><ESC>kkkkkklla

inoremap ,hr <hr /><CR>

inoremap ,img <img src="" alt="" width="" height="" /><ESC>bbbbbbbla

inoremap ,in <input type="" name="" value="" maxlength="" size="" /><ESC>bbbbbbbbbla

inoremap ,js <script type="text/javascript"><CR><CR></script><ESC>ki

inoremap ,pa <p><CR></p><ESC>ka

inoremap ,pr <pre></pre><ESC>hhhhhi

inoremap ,sp <span class=""></span><ESC>bbla

inoremap ,tb <table><CR><TAB><tr><CR><TAB><td><CR></td><CR><BS></tr><CR><BS></table>
inoremap ,th <th></th><ESC>hhhhi
inoremap ,tr <tr><CR><TAB><td><CR></td><CR><BS></tr><ESC>kkA
inoremap ,td <td><CR></td><ESC>kA
inoremap ,tx <textarea name="" rows="" cols=""></textarea><ESC>bbbbbbla

inoremap ,tt {t}{/t}<ESC>bba

inoremap ,{ {ldelim}<CR><TAB><CR><BS>{rdelim}<ESC>kA

vmap ,a "zdi<a href=""><C-R>z</a><ESC>
vmap ,b "zdi<b><C-R>z</b><ESC>
vmap ,em "zdi<i><C-R>z</i><ESC>
vmap ,sp "zdi<span class=""><C-R>z</span><ESC>
