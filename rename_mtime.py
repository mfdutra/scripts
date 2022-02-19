#!/usr/bin/env python3

import datetime
import os
import sys

for f in sys.argv[1:]:
    mtime = datetime.datetime.fromtimestamp(os.stat(f)[8])
    if '.' in f:
        ext = '.' + f.rpartition('.')[2]
    else:
        ext = ''
    new = mtime.strftime('%Y%m%d-%H%M%S') + ext

    if os.path.exists(new):
        print('{} already exists'.format(new), file=sys.stderr)
    else:
        print('{} -> {}'.format(f, new))
        os.rename(f, new)
