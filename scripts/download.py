#!/usr/bin/env python3
"""Download a Xiaohongshu video from a share link.

Usage: python scripts/download.py <url> <output_dir>
Outputs JSON to stdout, errors to stderr (exit 1 on failure).
"""

import sys
import json
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from xhs_core.downloader import download_video, XHSError


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text())


async def main():
    if len(sys.argv) < 3:
        print("Usage: python scripts/download.py <url> <output_dir>", file=sys.stderr)
        sys.exit(1)

    url = sys.argv[1]
    output_dir = sys.argv[2]
    config = load_config()

    try:
        result = await download_video(
            url, output_dir,
            cookie=config.get("xhs_cookie", ""),
            proxy=config.get("xhs_proxy", ""),
        )
        print(json.dumps(result, ensure_ascii=False))
    except XHSError as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
