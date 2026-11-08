#!/usr/bin/env python3

# Loudness-normalize audio files (e.g. one track per podcast speaker) so they
# all sound equally loud. Uses ffmpeg's loudnorm filter (EBU R128 / LUFS) in
# two passes: the first measures, the second applies a linear gain. An
# optional gentle compressor runs first to even out level swings within a
# track. Output files get a "-normalized" suffix next to the originals.

# Copyright 2026 Marlon Dutra
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

# Gentle speech compressor: ~2.5:1 above -24 dBFS (RMS), no makeup gain
# since loudnorm sets the final level anyway.
COMPRESSOR = "acompressor=threshold={:.6f}:ratio=2.5:attack=20:release=250".format(
    10 ** (-24 / 20)
)

# Encoders to use for lossless containers, so ffmpeg doesn't fall back to
# 16-bit. Other formats use ffmpeg's default encoder for the extension.
LOSSLESS_CODECS = {
    ".wav": ["-c:a", "pcm_s24le"],
    ".aif": ["-c:a", "pcm_s24be"],
    ".aiff": ["-c:a", "pcm_s24be"],
    ".flac": ["-c:a", "flac", "-sample_fmt", "s32"],
}


class Status:
    """Log lines plus, on a terminal, a self-updating line with each file's
    progress, e.g. "host.wav 42% | guest.wav 17%". Thread-safe."""

    def __init__(self):
        self.tty = sys.stdout.isatty()
        self.percent = {}
        self.lock = threading.Lock()

    def _draw(self):
        if self.tty:
            width = shutil.get_terminal_size().columns - 1
            line = " | ".join(f"{n} {p}%" for n, p in self.percent.items())
            sys.stdout.write("\r\033[K" + line[:width])
            sys.stdout.flush()

    def log(self, msg):
        with self.lock:
            if self.tty:
                sys.stdout.write("\r\033[K")
            print(msg, flush=True)
            self._draw()

    def update(self, name, percent):
        with self.lock:
            if self.percent.get(name) != percent:
                self.percent[name] = percent
                self._draw()

    def done(self, name):
        with self.lock:
            self.percent.pop(name, None)
            self._draw()


status = Status()


def run_ffmpeg(cmd, duration, on_progress):
    """Run ffmpeg, reporting progress (0.0-1.0) and returning its stderr.
    Raises with the last stderr line on failure."""
    cmd = cmd[:1] + ["-nostats", "-progress", "pipe:1"] + cmd[1:]
    with tempfile.TemporaryFile("w+") as err:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, text=True)
        for line in proc.stdout:
            key, _, value = line.strip().partition("=")
            if key == "out_time_us" and value.isdigit() and duration:
                on_progress(min(1.0, int(value) / 1e6 / duration))
        proc.wait()
        err.seek(0)
        stderr = err.read()
    if proc.returncode != 0:
        raise RuntimeError(stderr.strip().splitlines()[-1])
    return stderr


def last_json(text):
    """Extract the JSON object loudnorm prints at the end of ffmpeg's stderr."""
    return json.loads(text[text.rindex("{") : text.rindex("}") + 1])


def probe(path):
    """Return (duration in seconds, sample rate) of the first audio stream."""
    info = json.loads(
        subprocess.run(
            [
                "ffprobe", "-v", "error", "-select_streams", "a:0",
                "-show_entries", "format=duration:stream=sample_rate",
                "-of", "json", str(path),
            ],
            capture_output=True, text=True, check=True,
        ).stdout
    )
    return float(info["format"].get("duration", 0)), info["streams"][0]["sample_rate"]


def output_path(path):
    return path.with_name(f"{path.stem}-normalized{path.suffix}")


def normalize(path, args):
    pre = [COMPRESSOR] if args.compress else []
    target = f"I={args.target}:TP={args.true_peak}"
    ffmpeg = ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path)]
    duration, rate = probe(path)

    # Each pass is half of the file's progress
    def progress(start):
        return lambda f: status.update(path.name, int(start + f * 50))

    # Pass 1: measure loudness (after the compressor, if enabled)
    status.log(f"{path.name}: measuring loudness...")
    measure_filter = ",".join(pre + [f"loudnorm={target}:print_format=json"])
    m = last_json(
        run_ffmpeg(
            ffmpeg + ["-af", measure_filter, "-f", "null", "-"], duration, progress(0)
        )
    )

    # Pass 2: apply. LRA target >= measured LRA keeps loudnorm in linear
    # (pure gain) mode instead of its dynamic compressor. loudnorm treats a
    # measured LRA of 0 as "not given" and refuses linear mode, so floor it.
    measured_lra = max(0.1, float(m["input_lra"]))
    lra = min(50.0, max(1.0, measured_lra + 0.1))
    apply = (
        f"loudnorm={target}:LRA={lra:.1f}:linear=true"
        f":measured_I={m['input_i']}:measured_TP={m['input_tp']}"
        f":measured_LRA={measured_lra}:measured_thresh={m['input_thresh']}"
        f":offset={m['target_offset']}:print_format=json"
    )
    out = output_path(path)
    if out.exists() and not args.force:
        raise RuntimeError(f"{out.name} already exists (use -f to overwrite)")
    status.log(f"{path.name}: measured {m['input_i']} LUFS, writing {out.name}...")
    result = last_json(
        run_ffmpeg(
            ffmpeg
            + ["-af", ",".join(pre + [apply])]
            + ["-ar", rate]  # loudnorm upsamples to 192 kHz
            + LOSSLESS_CODECS.get(path.suffix.lower(), [])
            + ["-y", str(out)],
            duration,
            progress(50),
        )
    )

    mode = result["normalization_type"].lower()
    warning = "" if mode == "linear" else "  (true-peak limit hit: dynamic mode used)"
    return (
        f"{path.name}: {m['input_i']} -> {result['output_i']} LUFS, "
        f"peak {result['output_tp']} dBTP, {mode} -> {out.name}{warning}"
    )


def process(path, args):
    """Normalize one file, printing the outcome. Returns True on success."""
    try:
        msg, ok = normalize(path, args), True
    except (RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as e:
        msg, ok = f"{path.name}: ERROR: {e}", False
    status.done(path.name)
    status.log(msg)
    return ok


def main():
    parser = argparse.ArgumentParser(
        description="Loudness-normalize audio files to the same LUFS target "
        "with ffmpeg (two-pass loudnorm). Writes <name>-normalized.<ext>."
    )
    parser.add_argument("files", nargs="+", type=Path, help="input audio files")
    parser.add_argument(
        "-t", "--target", type=float, default=-19.0,
        help="integrated loudness target in LUFS (default: -19, mono voice)",
    )
    parser.add_argument(
        "-p", "--true-peak", type=float, default=-1.5,
        help="true-peak ceiling in dBTP (default: -1.5)",
    )
    parser.add_argument(
        "--no-compress", dest="compress", action="store_false",
        help="skip the gentle compressor applied before normalizing",
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="overwrite existing outputs"
    )
    parser.add_argument(
        "-j", "--jobs", type=int, default=os.cpu_count(),
        help="files to process in parallel (default: CPU count)",
    )
    args = parser.parse_args()

    missing = [str(f) for f in args.files if not f.is_file()]
    if missing:
        sys.exit(f"Not found: {', '.join(missing)}")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda f: process(f, args), args.files))

    failed = results.count(False)
    status.log(f"Done: {len(results) - failed} normalized, {failed} failed.")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
