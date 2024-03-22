#!/usr/bin/env python3

import os
import socket

# Generate a random IPv6 Unique local address prefix
# according to RFC 4193
#
# https://en.wikipedia.org/wiki/Unique_local_address

# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <https://www.gnu.org/licenses/>.

def main():
    prefix = b'\xfd'

    # Append 40 random bits
    prefix += os.urandom(5)

    # Append the suffix
    prefix += b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    ipv6 = socket.inet_ntop(socket.AF_INET6, prefix)

    print(f'{ipv6}/48')

if __name__ == '__main__':
    main()
