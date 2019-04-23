#!/usr/bin/env python3.6

# Generate a random password

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

import base64
import crypt
import getpass
import os

CHARS=32

rand = os.urandom(CHARS * 2)
passwd = base64.b64encode(rand)[:CHARS].decode('ascii')
sha512 = crypt.crypt(passwd, crypt.mksalt(crypt.METHOD_SHA512))

print(passwd)
print(sha512)
