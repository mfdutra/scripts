#!/usr/bin/env python3

# MacOS only
#
# Shows the default route interface and its IP for v4 and v6

# Copyright 2024 Marlon Dutra
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

import re
import subprocess

IPV4 = re.compile(r'\d+\.\d+\.\d+\.\d+')

def get_ip(iface):
    p = subprocess.run(('/sbin/ifconfig', iface), capture_output=True, encoding='ascii')

    v4 = None
    v6 = None
    for line in p.stdout.split('\n'):
        if 'fe80::' in line:  # skip link-local
            continue

        line = line.strip()
        if v4 is None and line.startswith('inet '):
            v4 = line.split()[1]
        if v6 is None and line.startswith('inet6 '):
            v6 = line.split()[1]

    return (v4, v6)

def main():
    p = subprocess.run(('/usr/sbin/netstat', '-rn'), capture_output=True, encoding='ascii')

    v4gw = None
    v6gw = None
    for line in p.stdout.split('\n'):
        if not line.startswith('default'):
            continue

        if v4gw is None and IPV4.search(line):
            v4gw = line.split()
        if v6gw is None and '::' in line:
            v6gw = line.split()

    print(f'V4: {v4gw[3]}   {get_ip(v4gw[3])[0]}')
    print(f'V6: {v6gw[3]}   {get_ip(v6gw[3])[1]}')

if __name__ == '__main__':
    main()
