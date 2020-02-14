#!/opt/homebrew/bin/python3.7

import argparse
import time
from subprocess import check_output, run

def main():
    parser = argparse.ArgumentParser(description='Notify when interface changes status.')
    parser.add_argument("iface", help="Interface to monitor")
    args = parser.parse_args()

    iface_before = False
    iface_now = False
    while True:
        ipv4 = False
        ipv6 = False
        out = check_output(("/sbin/ifconfig", args.iface), encoding="utf-8")
        for line in out.splitlines():
            line = line.strip()

            if line.startswith("inet "):
                ipv4 = True
            if line.startswith("inet6") and "fe80::" not in line:
                ipv6 = True

        if ipv4 and ipv6:
            iface_now = True
        else:
            iface_now = False

        if iface_before != iface_now:
            status = "UP" if iface_now else "DOWN"
            run((
                "/usr/bin/osascript",
                "-e",
                f"display notification \"Interface {args.iface} is {status}\" "
                "with title \"Network status\""
            ))

            iface_before = iface_now

        time.sleep(1)


if __name__ == "__main__":
    main()
