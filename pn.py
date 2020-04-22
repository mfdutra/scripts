#!/opt/homebrew/bin/python3.7

# Output an 8-digit PRNG number

import os
import struct

rand = os.urandom(8)
n = struct.unpack('Q', rand)[0]
print(str(n)[:8])
