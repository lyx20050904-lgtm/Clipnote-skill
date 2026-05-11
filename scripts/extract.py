#!/usr/bin/env python3
"""Extract audio from video file using ffmpeg.

Usage: python scripts/extract.py <video_path> <output_audio_path>

Prints the output audio path on success.
"""

import sys
import subprocess
from pathlib import Path


def extract_audio(video_path: str, output_path: str) -> str:
    """Extract mono 16kHz PCM audio from video."""
    cmd = [
        "ffmpeg",
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "16000",
        "-ac", "1",
        "-y",
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
    return output_path


def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/extract.py <video_path> <output_audio_path>", file=sys.stderr)
        sys.exit(1)

    video_path = sys.argv[1]
    output_path = sys.argv[2]

    if not Path(video_path).exists():
        print(f"Error: video not found: {video_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = extract_audio(video_path, output_path)
        print(result)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
