#!/usr/bin/env python3

######################################################################
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
######################################################################

# Script to add scene controls of Remotec ZRC-90 to the OpenZwave XML config
#
# It works well with Home Assistant. Last tested with version 0.76.2.
#
# Stop Home Assistant before editing zwcfg_0xffffffff.xml
# Back up your original config

import argparse
import sys
import xml.etree.ElementTree as ET
from copy import copy

def main(args):
    xml = ET.ElementTree()
    xml.parse(args.input)

    ns = {'ns': 'http://code.google.com/p/open-zwave/'}

    nodes = xml.findall("./ns:Node[@type='Remote Control Simple']", ns)
    if not nodes:
        error('Could not find any node element with type = Remote Control Simple')
        return 1

    for node in nodes:
        man = node.find('./ns:Manufacturer', ns)
        if not man:
            error(f'Could not find manufacturer of node {node.attrib["id"]}')
            continue

        if man.attrib['name'] != 'Remotec':
            error(f'Skipping node {node.attrib["id"]} as manufacturer is not Remotec')
            continue

        cmdclass = node.find('./ns:CommandClasses/ns:CommandClass[@name="COMMAND_CLASS_CENTRAL_SCENE"]', ns)
        if not cmdclass:
            error(f'Could not find central scene command class in node {node.attrib["id"]}')
            continue

        values = cmdclass.findall('./ns:Value', ns)
        if not values:
            error(f'Could not find any Value element inside command class in node {node.attrib["id"]}')
            continue

        if len(values) > 1:
            error(f'Node {node.attrib["id"]} seems to be fixed already')
            continue

        for i in range(1, 9):
            attr = copy(values[0].attrib)
            attr['index'] = str(i)
            attr['label'] = f'Scene {i}'

            ET.SubElement(cmdclass, 'Value', attr)

        print(f'Fixed node {node.attrib["id"]}')

    ET.register_namespace('', ns['ns'])
    xml.write(args.output, xml_declaration=True)

def error(msg):
    print(msg, file=sys.stderr)

def getArgs():
    parser = argparse.ArgumentParser(
        description='Add Remotec ZRC-90 scenes to zwcfg file')
    parser.add_argument('input', help='Input file')
    parser.add_argument('output', help='Output file')
    return parser.parse_args()

if __name__ == '__main__':
    sys.exit(main(getArgs()))
