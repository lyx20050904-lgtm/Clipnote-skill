#!/usr/bin/env python3
"""Write a ClipNote markdown note to Obsidian vault.

Usage: python scripts/write_note.py '<json_data>'

Where json_data contains: title, author, url, duration, summary, transcript
"""

import sys
import json
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text())


def sanitize_filename(s: str, max_len: int = 20) -> str:
    """Keep only safe chars and truncate."""
    safe = "".join(c if c.isalnum() or c in " _-." else "_" for c in s)
    return safe[:max_len].strip()


AUTHOR_SIGNATURE = """\
---
*created by Clipnote Ethan*
*Contact: lyx20050904@gmail.com*
"""


def resolve_output_dir(config: dict) -> Path:
    """Determine output directory: Obsidian vault or fallback to Desktop."""
    vault_path_str = config.get("vault_path", "")
    vault_path = Path(vault_path_str).expanduser() if vault_path_str else Path()
    output_subdir = config.get("output_dir", "ClipNote")

    if vault_path_str and vault_path.exists():
        return vault_path / output_subdir
    # Fallback: ~/Desktop/ClipNote
    fallback = Path.home() / "Desktop" / "ClipNote"
    return fallback


def write_note(data: dict) -> str:
    """Write formatted markdown note. Returns absolute file path."""
    config = load_config()
    note_dir = resolve_output_dir(config)
    note_dir.mkdir(parents=True, exist_ok=True)

    today = date.today().isoformat()
    author_part = sanitize_filename(data.get("author", "unknown"), 10)
    title_part = sanitize_filename(data.get("title", "untitled"), 20)
    filename = f"{today}_{author_part}_{title_part}.md"
    filepath = note_dir / filename

    transcript = data.get("transcript", "")
    uncertain = data.get("uncertain_sections", [])
    uncertain_block = ""
    if uncertain:
        items = "\n".join(f"  - `{s['text'][:60]}` — {s['reason']}" for s in uncertain)
        uncertain_block = f"\n**标注的不确定内容：**\n{items}\n"

    content = f"""---
date: {today}
source: 小红书
tags: [clipnote, 待整理]
---

# {data.get("title", "无标题")}

## AI 摘要

{data.get("summary", "")}

## 关键信息

- 博主：{data.get("author", "未知")}
- 链接：{data.get("url", "")}
- 时长：{data.get("duration", "未知")}

## 逐字稿

{transcript}{uncertain_block}

{AUTHOR_SIGNATURE}
"""

    filepath.write_text(content, encoding="utf-8")
    return str(filepath)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Missing JSON data argument"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(sys.argv[1])
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON: {e}"}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)

    try:
        path = write_note(data)
        print(json.dumps({"path": path}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
