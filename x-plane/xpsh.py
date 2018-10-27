#!/usr/bin/env python3

# X-Plane Shell, to send some commands to X-Plane UDP interface

# Copyright 2018 Marlon Dutra
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

import argparse
import cmd
import re
import socket
import struct
import sys

# readline makes the shell much better
try:
    import readline
except ImportError:
    pass

def err(msg):
    print('❌ ' + msg, file=sys.stderr)

COM_DREFS = {
    ('1', None): b'sim/cockpit/radios/com1_freq_hz',
    ('2', None): b'sim/cockpit/radios/com2_freq_hz',
    ('1', 's'): b'sim/cockpit/radios/com1_stdby_freq_hz',
    ('2', 's'): b'sim/cockpit/radios/com2_stdby_freq_hz',
}

NAV_DREFS = {
    ('1', None): b'sim/cockpit/radios/nav1_freq_hz',
    ('2', None): b'sim/cockpit/radios/nav2_freq_hz',
    ('1', 's'): b'sim/cockpit/radios/nav1_stdby_freq_hz',
    ('2', 's'): b'sim/cockpit/radios/nav2_stdby_freq_hz',
}

XPDR_REGEX = re.compile(r'^[0-7]{4}$')

class XplaneShell(cmd.Cmd):
    intro = 'X-Plane Shell. Type help or ? to list commands.\n'
    prompt = '<xpsh> '
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)

    def send(self, dref, value):
        data = struct.pack("<4sx", b'DREF')
        fmt = '<f{0}s'.format(len(dref))
        data += struct.pack(fmt, value, dref)

        data += (509 - len(data)) * b'\x00'
        self.sock.sendto(data, (ARGS.host, ARGS.port))

    def cmnd(self, command):
        data = struct.pack("<4sx", b'CMND')
        fmt = '<{0}s'.format(len(command))
        data += struct.pack(fmt, command)

        self.sock.sendto(data, (ARGS.host, ARGS.port))

    def emptyline(self):
        pass

    def do_exit(self, arg):
        sys.exit()

    def do_quit(self, arg):
        sys.exit()

    def do_EOF(self, arg):
        sys.exit()

    def do_com(self, args):
        '''Sets COM frequency

        # Set COM1 active frequency
        > com 1 121.6

        # Set COM2 stand-by frequency
        > com 2 119.0 s'''

        if not args:
            err(self.do_com.__doc__)
            return

        args = args.split()
        com = args[0]

        if com not in ('1', '2'):
            err('Invalid radio. Use 1 or 2.')
            return

        try:
            freq = float(args[1])
        except (ValueError, IndexError):
            err('Invalid frequency')
            return

        if freq < 118 or freq > 137:
            err('Frequency out of range')
            return

        try:
            opt = args[2]
        except IndexError:
            opt = None

        if opt is not None and opt != 's':
            err('Invalid option. Use "s" for stand-by.')
            return

        self.send(COM_DREFS[(com, opt)], freq * 100)

    def do_nav(self, args):
        '''Sets NAV frequency

        # Set NAV1 active frequency
        > nav 1 109

        # Set NAV2 stand-by frequency
        > nav 2 116.5 s'''

        if not args:
            err(self.do_nav.__doc__)
            return

        args = args.split()
        nav = args[0]

        if nav not in ('1', '2'):
            err('Invalid radio. Use 1 or 2.')
            return

        try:
            freq = float(args[1])
        except (ValueError, IndexError):
            err('Invalid frequency')
            return

        if freq < 108 or freq > 117.95:
            err('Frequency out of range')
            return

        try:
            opt = args[2]
        except IndexError:
            opt = None

        if opt is not None and opt != 's':
            err('Invalid option. Use "s" for stand-by.')
            return

        self.send(NAV_DREFS[(nav, opt)], freq * 100)

    def do_crs(self, args):
        '''Sets NAV course (does not work on all aircraft)

        > crs 256'''

        if not args:
            err(self.do_crs.__doc__)
            return

        try:
            crs = int(args)
        except ValueError:
            err('Invalid course')
            return

        if crs < 0 or crs > 360:
            err('Course out of range')
            return

        self.send(b'sim/cockpit/radios/nav1_course_degm', crs)
        self.send(b'sim/cockpit/radios/nav2_course_degm', crs)
        self.send(b'sim/cockpit/radios/nav1_course_degm2', crs)
        self.send(b'sim/cockpit/radios/nav2_course_degm2', crs)

    def do_ils(self, args):
        '''Sets both NAV radios to ILS frequency and sets the course

        > ils 109.5 251'''

        try:
            args = args.split()
            freq = float(args[0])
            crs = int(args[1])

        except (ValueError, IndexError):
            err(self.do_ils.__doc__)
            return

        if freq < 108.1 or freq > 111.95:
            err('ILS frequency out of range 108.1 - 111.95')
            return

        self.do_crs(crs)
        self.do_nav('1 {0}'.format(freq))
        self.do_nav('2 {0}'.format(freq))

    def do_xpdr(self, args):
        '''Sets transponder code and activate it

        > xpdr 4211'''

        if not XPDR_REGEX.match(args):
            err('Invalid transponder code')
            return

        xpdr = int(args)

        self.send(b'sim/cockpit/radios/transponder_code', xpdr)
        self.cmnd(b'sim/transponder/transponder_alt')

    def do_hdg(self, args):
        '''Sets HDG bug on autopilot (does not work on all aircraft)

        > hdg 256'''

        if not args:
            err(self.do_hdg.__doc__)
            return

        try:
            hdg = int(args)
        except ValueError:
            err('Invalid heading')
            return

        if hdg < 0 or hdg > 360:
            err('Heading out of range')
            return

        self.send(b'sim/cockpit/autopilot/heading_mag', hdg)

    def do_alt(self, args):
        '''Sets altitude bug on autopilot (does not work on all aircraft)

        > alt 24000'''

        if not args:
            err(self.do_alt.__doc__)
            return

        try:
            alt = float(args)
        except ValueError:
            err('Invalid altitude')
            return

        self.send(b'sim/cockpit/autopilot/altitude', alt)

    def do_ident(self, args):
        '''Transponder ident'''

        self.cmnd(b'sim/transponder/transponder_ident')

    def do_flip(self, args):
        '''Flip active/stand-by on COM or NAV radios

        > flip com1
        > flip nav2'''

        if not args:
            err(self.do_flip.__doc__)
            return

        if args not in ('com1', 'com2', 'nav1', 'nav2'):
            err('Invalid radio')
            return

        self.cmnd('sim/radios/{}_standy_flip'.format(args).encode('ascii'))

def get_args():
    parser = argparse.ArgumentParser(description='X-Plane shell')
    parser.add_argument('--host', default='127.0.0.1',
        help='X-Plane IP address')
    parser.add_argument('--port', default=49000,
        help='X-Plane UDP port')

    return parser.parse_args()

if __name__ == '__main__':
    ARGS = get_args()
    try:
        XplaneShell().cmdloop()

    except KeyboardInterrupt:
        sys.exit()
