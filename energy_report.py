#!/usr/bin/env python3
import argparse
import csv
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).parent / "home-assistant_v2.db"


def get_weekly_data():
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT created_ts, mean FROM statistics WHERE metadata_id = '83' ORDER BY created_ts"
    ).fetchall()
    conn.close()

    # Group by ISO week (Monday-Sunday)
    weeks = {}
    for ts, mean in rows:
        dt = datetime.fromtimestamp(ts)
        year, week, _ = dt.isocalendar()
        key = (year, week)
        if key not in weeks:
            weeks[key] = {"import_kwh": 0.0, "export_kwh": 0.0, "hours": 0}
        if mean >= 0:
            weeks[key]["import_kwh"] += mean
        else:
            weeks[key]["export_kwh"] += abs(mean)
        weeks[key]["hours"] += 1

    result = []
    for (year, week), data in sorted(weeks.items()):
        monday = datetime.fromisocalendar(year, week, 1)
        sunday = monday + timedelta(days=6)
        imp = data["import_kwh"]
        exp = data["export_kwh"]
        result.append({
            "week_start": monday.strftime("%Y-%m-%d"),
            "week_end": sunday.strftime("%Y-%m-%d"),
            "label": f"{monday:%b %d} - {sunday:%b %d, %Y}",
            "import_kwh": imp,
            "export_kwh": exp,
            "net_kwh": imp - exp,
            "hours": data["hours"],
        })
    return result


def print_report(data):
    print(f"{'Week':<22} {'Import (kWh)':>13} {'Export (kWh)':>13} {'Net (kWh)':>11} {'Hours':>5}")
    print("-" * 68)

    total_import = 0.0
    total_export = 0.0

    for row in data:
        total_import += row["import_kwh"]
        total_export += row["export_kwh"]
        print(
            f"{row['label']:<22} {row['import_kwh']:>13.2f} {row['export_kwh']:>13.2f} "
            f"{row['net_kwh']:>+11.2f} {row['hours']:>5}"
        )

    print("-" * 68)
    print(f"{'TOTAL':<22} {total_import:>13.2f} {total_export:>13.2f} {total_import - total_export:>+11.2f}")
    print(
        f"\nWeeks: {len(data)}  |  Avg import/week: {total_import / len(data):.2f} kWh"
        f"  |  Avg export/week: {total_export / len(data):.2f} kWh"
    )


def write_csv(data, path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Week Start", "Week End", "Import (kWh)", "Export (kWh)", "Net (kWh)", "Hours"])
        for row in data:
            writer.writerow([
                row["week_start"],
                row["week_end"],
                f"{row['import_kwh']:.2f}",
                f"{row['export_kwh']:.2f}",
                f"{row['net_kwh']:.2f}",
                row["hours"],
            ])
    print(f"CSV written to {path}")


def write_chart(data, path):
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates

    dates = [datetime.strptime(row["week_start"], "%Y-%m-%d") for row in data]
    imports = [row["import_kwh"] for row in data]
    exports = [row["export_kwh"] for row in data]
    nets = [row["net_kwh"] for row in data]

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(dates, imports, label="Import", color="#e74c3c", linewidth=1.5)
    ax.plot(dates, exports, label="Export", color="#2ecc71", linewidth=1.5)
    ax.plot(dates, nets, label="Net", color="#3498db", linewidth=1.5, linestyle="--")
    ax.axhline(0, color="gray", linewidth=0.5)

    ax.set_title("Weekly Energy Import / Export")
    ax.set_ylabel("kWh")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    fig.autofmt_xdate(rotation=45)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Chart saved to {path}")


def main():
    parser = argparse.ArgumentParser(description="Weekly energy import/export report")
    parser.add_argument("--csv", metavar="FILE", help="Export report to CSV file")
    parser.add_argument("--chart", metavar="FILE", help="Save line chart to image file (e.g. chart.png)")
    args = parser.parse_args()

    data = get_weekly_data()
    print_report(data)

    if args.csv:
        write_csv(data, args.csv)
    if args.chart:
        write_chart(data, args.chart)


if __name__ == "__main__":
    main()
