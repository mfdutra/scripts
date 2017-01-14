#!/usr/bin/python3

from requests import post
from subprocess import Popen, PIPE
import json
import re

uri = 'http://127.0.0.1:8123/api/events/custom_scene'
apiKey = '***'

eventRe = re.compile(r'Info, (Node\d+), Received Central Scene.*scene id=(\d+) in (\d+) seconds\.')

log = Popen(('/usr/bin/tail', '-F', '-n', '0', '/home/hass/hass/OZW_Log.txt'), stdout=PIPE)
while True:
  line = log.stdout.readline()
  if not line:
    break
  line = line.strip().decode('utf-8')

  # Fast match to discard non-info log messages
  if 'Info,' not in line:
    continue

  match = eventRe.search(line)
  if match:
    data = {'button': '_'.join(match.groups())}
    post(uri, data=json.dumps(data), headers={'x-ha-access': apiKey, 'content-type': 'application/json'})
