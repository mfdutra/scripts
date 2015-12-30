#!/usr/bin/python

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from __future__ import print_function

import sys

def main():
    fd = open(sys.argv[1])

    print('{|')

    for line in fd:
        line = line.strip()
        if not line:
            continue

        for f in line.split('\t'):
            print('|%s' % f)

        print('|-')

    print('|}')

    fd.close()

if __name__ == '__main__':
    main()
