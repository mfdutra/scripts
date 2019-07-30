#!/opt/homebrew/bin/python3.7

import random

for i in range(10):
    out = ''
    out += str(random.randint(0,9))
    out += ' x '
    out += str(random.randint(0,9))

    print(out)
