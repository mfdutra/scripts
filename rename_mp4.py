#!/usr/bin/env python3
"""
Rename MP4 file(s) based on creation time metadata.
Usage: python rename_mp4.py <file1.mp4> [file2.mp4 ...]
"""

import subprocess
import json
import sys
import os
from datetime import datetime, timezone
from pathlib import Path


def get_creation_time(filepath):
    """Extract creation time from MP4 metadata using ffprobe."""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            filepath
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Try to get creation_time from format tags
        if 'format' in data and 'tags' in data['format']:
            tags = data['format']['tags']
            # Check various possible tag names
            for key in ['creation_time', 'Creation Time', 'com.apple.quicktime.creationdate']:
                if key in tags:
                    return tags[key]

        raise ValueError("No creation_time found in metadata")

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffprobe failed: {e.stderr}")
    except json.JSONDecodeError:
        raise RuntimeError("Failed to parse ffprobe output")


def rename_file(filepath):
    """Rename MP4 file according to its creation time."""
    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    if filepath.suffix.lower() != '.mp4':
        raise ValueError("File must be an MP4 file")

    # Get creation time from metadata
    creation_time_str = get_creation_time(str(filepath))

    # Parse the UTC time (typically in ISO 8601 format)
    # Example: "2024-01-15T10:30:45.000000Z"
    try:
        # Remove 'Z' suffix and parse
        creation_time_str = creation_time_str.rstrip('Z')
        utc_time = datetime.fromisoformat(creation_time_str)

        # Add UTC timezone info and convert to local timezone
        utc_time = utc_time.replace(tzinfo=timezone.utc)
        local_time = utc_time.astimezone()

    except ValueError as e:
        raise ValueError(f"Failed to parse creation time '{creation_time_str}': {e}")

    # Format new filename
    new_name = local_time.strftime("%Y%m%d%H%M%S.mp4")
    new_path = filepath.parent / new_name

    # Check if target file already exists
    if new_path.exists():
        raise FileExistsError(f"Target file already exists: {new_path}")

    # Rename the file
    filepath.rename(new_path)
    print(f"Renamed: {filepath.name} -> {new_name}")
    return new_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rename_mp4.py <file1.mp4> [file2.mp4 ...]")
        sys.exit(1)

    input_files = sys.argv[1:]
    errors = []

    for input_file in input_files:
        try:
            rename_file(input_file)
        except Exception as e:
            error_msg = f"{input_file}: {e}"
            print(f"Error: {error_msg}", file=sys.stderr)
            errors.append(error_msg)

    if errors:
        sys.exit(1)
