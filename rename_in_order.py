#!/usr/bin/env python3

import os
import sys

def main():
    i = 1
    for f in sys.argv[1:]:
        extension = os.path.splitext(f)[1]
        print(f'{f} -> {i:03d}{extension}')
        os.rename(f, f'{i:03d}{extension}')
        i += 1

if __name__ == '__main__':
    main()
