#!/opt/homebrew/bin/python3.7

import argparse
import os
import sys

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

args = None
keys = [
    'Lcl Date',
    'Lcl Time',
    'UTCOfst',
    'AtvWpt',
    'Latitude',
    'Longitude',
    'AltInd',
    'BaroA',
    'AltMSL',
    'OAT',
    'IAS',
    'GndSpd',
    'VSpd',
    'Pitch',
    'Roll',
    'LatAc',
    'NormAc',
    'HDG',
    'TRK',
    'volt1',
    'volt2',
    'amp1',
    'FQtyL',
    'FQtyR',
    'E1 FFlow',
    'E1 OilT',
    'E1 OilP',
    'E1 MAP',
    'E1 RPM',
    'E1 %Pwr',
    'E1 CHT1',
    'E1 CHT2',
    'E1 CHT3',
    'E1 CHT4',
    'E1 CHT5',
    'E1 CHT6',
    'E1 EGT1',
    'E1 EGT2',
    'E1 EGT3',
    'E1 EGT4',
    'E1 EGT5',
    'E1 EGT6',
    'E1 TIT1',
    'E1 TIT2',
    'E1 Torq',
    'E1 NG',
    'E1 ITT',
    'E2 FFlow',
    'E2 MAP',
    'E2 RPM',
    'E2 Torq',
    'E2 NG',
    'E2 ITT',
    'AltGPS',
    'TAS',
    'HSIS',
    'CRS',
    'NAV1',
    'NAV2',
    'COM1',
    'COM2',
    'HCDI',
    'VCDI',
    'WndSpd',
    'WndDr',
    'WptDst',
    'WptBrg',
    'MagVar',
    'AfcsOn',
    'RollM',
    'PitchM',
    'RollC',
    'PichC',
    'VSpdG',
    'GPSfix',
    'HAL',
    'VAL',
    'HPLwas',
    'HPLfd',
    'VPLwas',
]
count = 1
flightTime = 0

def readCSV(name):
    with open(name, 'r', encoding='ascii') as f:
        for line in f:
            parse(line.strip())

def parse(line):
    if not line.startswith('2'):
        return

    fields = line.split(',')
    data = {}

    try:
        for i in range(len(keys)):
            data[keys[i]] = fields[i].strip()

    except IndexError:
        return

    process(data)

def process(data):
    global count
    global flightTime

    gps = getLatLon(data['Latitude'], data['Longitude'])
    power = int(float(data['E1 %Pwr']) * 100)
    ias = intOrZero(data['IAS'])
    if ias > 60:
        flightTime += 1
    flightTimeStr = getTimeStr(flightTime)

    text = f'''{data['Lcl Date']} {data['Lcl Time']}
IAS / TAS / GS: {intOrZero(data['IAS'])} / {intOrZero(data['TAS'])} / {intOrZero(data['GndSpd'])}
ALT / BARO: {intOrZero(data['AltInd'])} / {data['BaroA']}
VS: {intOrZero(data['VSpd'])}
GPS: {gps}
HDG / TRK: {intOrZero(data['HDG'])} / {intOrZero(data['TRK'])}
OAT: {data['OAT']}C
PWR / MAP / RPM: {power}% / {data['E1 MAP']} / {intOrZero(data['E1 RPM'])}
FLT TIME: {flightTimeStr}
'''

    img = Image.new('RGB', (args.width, args.height))

    fnt = ImageFont.truetype('/Library/Fonts/Courier New Bold.ttf', 14)
    d = ImageDraw.Draw(img)
    d.text((10, 10), text, fill=(0, 255, 0), font=fnt)

    img.save(args.outdir + f'/{count:06d}.png')
    count += 1

    print(data['Lcl Date'] + ' ' + data['Lcl Time'])
    sys.stdout.flush()

def err(msg):
    print(f'[1;31m{msg}[0m', file=sys.stderr)

def getLatLon(lat, lon):
    if not lat or not lon:
        return 'NO GPS'

    lat = float(lat)
    lon = float(lon)

    lathem = 'N' if lat >= 0 else 'S'
    latmin = lat % 1 * 60
    latsec = latmin % 1 * 60
    latstr = f'{abs(int(lat))}°{int(latmin)}\'{int(latsec)}"{lathem}'

    lonhem = 'E' if lon >= 0 else 'W'
    lonmin = lon % 1 * 60
    lonsec = lonmin % 1 * 60
    lonstr = f'{abs(int(lon))}°{int(lonmin)}\'{int(lonsec)}"{lonhem}'

    return f'{latstr} {lonstr}'

def getTimeStr(sec):
    hour = sec // 3600
    sec = sec % 3600
    minute = sec // 60
    sec = sec % 60
    return f'{hour:02d}:{minute:02d}:{sec:02d}'

def intOrZero(n):
    try:
        return int(float(n))
    except ValueError:
        return 0

def main():
    parser = argparse.ArgumentParser(
        description='Create PNG sequence out of Garmin G1000 data log'
    )
    parser.add_argument('log', help='Data log file')
    parser.add_argument('--outdir', default=os.getcwd(),
        help='Output directory [%(default)s]')
    parser.add_argument('--width', default=1920,
        help='Image width [%(default)s]')
    parser.add_argument('--height', default=1080,
        help='Image height [%(default)s]')
    global args
    args = parser.parse_args()

    readCSV(args.log)

    print(f'Data points missing: {misses}\n')

    print('Create the mp4 sequence with:')
    print(f"ffmpeg -r 1 -f image2 -i '%06d.png' -s {args.width}x{args.height} -pix_fmt yuv420p -r 29.97 g1000.mp4")

if __name__ == '__main__':
    main()
