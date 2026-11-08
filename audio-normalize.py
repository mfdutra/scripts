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
import subprocess
import sys
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


def run(cmd):
    """Run a command, returning stderr. Raises with stderr on failure."""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip().splitlines()[-1])
    return proc.stderr


def last_json(text):
    """Extract the JSON object loudnorm prints at the end of ffmpeg's stderr."""
    return json.loads(text[text.rindex("{") : text.rindex("}") + 1])


def sample_rate(path):
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=sample_rate", "-of", "csv=p=0", str(path),
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    return out.strip()


def output_path(path):
    return path.with_name(f"{path.stem}-normalized{path.suffix}")


def normalize(path, args):
    pre = [COMPRESSOR] if args.compress else []
    target = f"I={args.target}:TP={args.true_peak}"
    ffmpeg = ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(path)]

    # Pass 1: measure loudness (after the compressor, if enabled)
    measure_filter = ",".join(pre + [f"loudnorm={target}:print_format=json"])
    m = last_json(run(ffmpeg + ["-af", measure_filter, "-f", "null", "-"]))

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
    result = last_json(
        run(
            ffmpeg
            + ["-af", ",".join(pre + [apply])]
            + ["-ar", sample_rate(path)]  # loudnorm upsamples to 192 kHz
            + LOSSLESS_CODECS.get(path.suffix.lower(), [])
            + ["-y", str(out)]
        )
    )

    mode = result["normalization_type"].lower()
    warning = "" if mode == "linear" else "  (true-peak limit hit: dynamic mode used)"
    return (
        f"{path.name}: {m['input_i']} -> {result['output_i']} LUFS, "
        f"peak {result['output_tp']} dBTP, {mode} -> {out.name}{warning}"
    )


def process(path, args):
    try:
        return True, normalize(path, args)
    except (RuntimeError, ValueError, KeyError, subprocess.CalledProcessError) as e:
        return False, f"{path.name}: ERROR: {e}"


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

    print("\n".join(msg for _, msg in results))
    sys.exit(0 if all(ok for ok, _ in results) else 1)


if __name__ == "__main__":
    main()
