#!/usr/bin/env python3
"""Force a Wi-Fi client to reconnect via the Unifi Network Controller API."""

import argparse
import os
import sys
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Force a Wi-Fi client to reconnect on Unifi Network Controller"
    )
    parser.add_argument("mac", help="Client MAC address (e.g. aa:bb:cc:dd:ee:ff)")
    parser.add_argument(
        "--host",
        default=os.environ.get("UNIFI_HOST", "https://192.168.1.1"),
        help="Controller URL (default: $UNIFI_HOST or https://192.168.1.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("UNIFI_PORT", 443)),
        help="Controller port (default: $UNIFI_PORT or 443)",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("UNIFI_USERNAME", "admin"),
        help="Controller username (default: $UNIFI_USERNAME or admin)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("UNIFI_PASSWORD"),
        help="Controller password (default: $UNIFI_PASSWORD)",
    )
    parser.add_argument(
        "--site",
        default=os.environ.get("UNIFI_SITE", "default"),
        help="Site name (default: $UNIFI_SITE or default)",
    )
    parser.add_argument(
        "--unifi-os",
        action="store_true",
        default=os.environ.get("UNIFI_OS", "").lower() in ("1", "true", "yes"),
        help="Use UnifiOS API paths (UDM/UDM-Pro). Set $UNIFI_OS=true to enable.",
    )
    parser.add_argument(
        "--no-verify",
        action="store_true",
        help="Disable SSL certificate verification",
    )
    parser.add_argument(
        "--block",
        action="store_true",
        help="Block the client for 60 seconds, then unblock (instead of just kicking)",
    )
    return parser.parse_args()


def build_base_url(host: str, port: int) -> str:
    host = host.rstrip("/")
    if not host.startswith(("http://", "https://")):
        host = f"https://{host}"
    # Only append port if it's non-standard for the scheme
    if (host.startswith("https://") and port != 443) or (
        host.startswith("http://") and port != 80
    ):
        host = f"{host}:{port}"
    return host


def stamgr_cmd(session: requests.Session, cmd_url: str, cmd: str, mac: str) -> dict:
    resp = session.post(cmd_url, json={"cmd": cmd, "mac": mac})
    resp.raise_for_status()
    return resp.json()


def check_rc(data: dict, action: str) -> bool:
    if data.get("meta", {}).get("rc") == "ok":
        return True
    print(f"Unexpected response for {action}: {data}", file=sys.stderr)
    return False


def reconnect_client(
    base_url: str,
    username: str,
    password: str,
    site: str,
    mac: str,
    unifi_os: bool,
    verify: bool,
    block: bool,
) -> None:
    session = requests.Session()
    session.verify = verify

    # --- Login ---
    if unifi_os:
        login_url = f"{base_url}/api/auth/login"
    else:
        login_url = f"{base_url}/api/login"

    login_payload = {"username": username, "password": password}
    resp = session.post(login_url, json=login_payload)
    resp.raise_for_status()

    # UnifiOS uses a bearer token; legacy controllers use a session cookie.
    if unifi_os:
        token = resp.json().get("token") or resp.headers.get("x-auth-token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})

    print(f"Logged in as '{username}'")

    mac = mac.lower()
    if unifi_os:
        cmd_url = f"{base_url}/proxy/network/api/s/{site}/cmd/stamgr"
    else:
        cmd_url = f"{base_url}/api/s/{site}/cmd/stamgr"

    if block:
        # --- Block ---
        data = stamgr_cmd(session, cmd_url, "block-sta", mac)
        if not check_rc(data, "block"):
            sys.exit(1)
        print(f"Client {mac} blocked. Waiting 60 seconds...")
        time.sleep(60)

        # --- Unblock ---
        data = stamgr_cmd(session, cmd_url, "unblock-sta", mac)
        if not check_rc(data, "unblock"):
            sys.exit(1)
        print(f"Client {mac} unblocked — it will reconnect automatically.")
    else:
        # --- Kick (force reconnect) ---
        data = stamgr_cmd(session, cmd_url, "kick-sta", mac)
        if not check_rc(data, "kick"):
            sys.exit(1)
        print(f"Client {mac} has been kicked — it will reconnect automatically.")

    # --- Logout ---
    if unifi_os:
        session.post(f"{base_url}/api/auth/logout")
    else:
        session.get(f"{base_url}/logout")


def main():
    args = parse_args()

    if not args.password:
        import getpass
        args.password = getpass.getpass("Controller password: ")

    base_url = build_base_url(args.host, args.port)
    verify = not args.no_verify

    print(f"Connecting to {base_url} (site: {args.site})")

    try:
        reconnect_client(
            base_url=base_url,
            username=args.username,
            password=args.password,
            site=args.site,
            mac=args.mac,
            unifi_os=args.unifi_os,
            verify=verify,
            block=args.block,
        )
    except requests.HTTPError as e:
        print(f"HTTP error: {e.response.status_code} — {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except requests.ConnectionError as e:
        print(f"Connection error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
