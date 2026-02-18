#!/usr/bin/env python3
"""Fetch long-term statistics from Home Assistant via the WebSocket API."""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta, timezone

import aiohttp

HA_URL = "http://a.b.c.d:8123"
HA_TOKEN = "**"

VALID_PERIODS = ("5minute", "hour", "day", "week", "month")


async def fetch_statistics(entity_id: str, period: str, start: str | None, end: str | None):
    now = datetime.now(timezone.utc)
    if end:
        end_dt = datetime.fromisoformat(end)
    else:
        end_dt = now

    if start:
        start_dt = datetime.fromisoformat(start)
    else:
        start_dt = end_dt - timedelta(days=30)

    ws_url = f"{HA_URL.replace('http', 'ws', 1)}/api/websocket"

    async with aiohttp.ClientSession() as session:
        async with session.ws_connect(ws_url) as ws:
            # Phase 1: receive auth_required
            msg = await ws.receive_json()
            if msg.get("type") != "auth_required":
                print(f"Unexpected message: {msg}", file=sys.stderr)
                sys.exit(1)

            # Phase 2: authenticate
            await ws.send_json({"type": "auth", "access_token": HA_TOKEN})
            msg = await ws.receive_json()
            if msg.get("type") != "auth_ok":
                print(f"Authentication failed: {msg}", file=sys.stderr)
                sys.exit(1)

            # Phase 3: request statistics
            await ws.send_json({
                "id": 1,
                "type": "recorder/statistics_during_period",
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "statistic_ids": [entity_id],
                "period": period,
            })
            msg = await ws.receive_json()

            if not msg.get("success"):
                print(f"Error: {msg}", file=sys.stderr)
                sys.exit(1)

            return msg["result"]


def print_statistics(result: dict, entity_id: str):
    entries = result.get(entity_id, [])
    if not entries:
        print(f"No statistics found for {entity_id}")
        return

    # Determine which value columns are present
    sample = entries[0]
    has_mean = sample.get("mean") is not None
    has_sum = sample.get("sum") is not None
    has_state = sample.get("state") is not None

    # Build header
    cols = ["start"]
    if has_mean:
        cols += ["mean", "min", "max"]
    if has_state:
        cols.append("state")
    if has_sum:
        cols.append("sum")

    print("\t".join(cols))

    for entry in entries:
        start_ts = entry["start"]
        if isinstance(start_ts, (int, float)):
            row = [datetime.fromtimestamp(start_ts / 1000, tz=timezone.utc).isoformat()]
        else:
            row = [str(start_ts)]
        if has_mean:
            row += [f"{entry['mean']:.2f}", f"{entry['min']:.2f}", f"{entry['max']:.2f}"]
        if has_state:
            row.append(f"{entry['state']:.2f}" if entry["state"] is not None else "")
        if has_sum:
            row.append(f"{entry['sum']:.2f}" if entry["sum"] is not None else "")
        print("\t".join(row))


def main():
    parser = argparse.ArgumentParser(description="Fetch long-term statistics from Home Assistant")
    parser.add_argument("entity", help="Entity ID (e.g. sensor.temperature)")
    parser.add_argument(
        "-p", "--period",
        choices=VALID_PERIODS,
        default="hour",
        help="Aggregation period (default: hour)",
    )
    parser.add_argument("-s", "--start", help="Start time (ISO 8601, default: 30 days ago)")
    parser.add_argument("-e", "--end", help="End time (ISO 8601, default: now)")
    parser.add_argument("-j", "--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    result = asyncio.run(fetch_statistics(args.entity, args.period, args.start, args.end))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_statistics(result, args.entity)


if __name__ == "__main__":
    main()
