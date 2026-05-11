"""Xiaohongshu video downloader: short URL → page data → video download.

Extracts video info from __INITIAL_STATE__ embedded in page HTML.
No external XHS-Downloader dependency required.
"""

import re
from pathlib import Path
from typing import Optional

import httpx
import yaml
from lxml import etree


class XHSError(Exception):
    pass


def _make_client(proxy: Optional[str]) -> httpx.AsyncClient:
    kwargs: dict = {"timeout": 30, "verify": False}
    if proxy:
        kwargs["proxy"] = proxy
    return httpx.AsyncClient(**kwargs)


async def _resolve_short_url(url: str, client: httpx.AsyncClient) -> str:
    resp = await client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return str(resp.url)


async def _fetch_page(url: str, client: httpx.AsyncClient, cookie: str = "") -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    if cookie:
        headers["Cookie"] = cookie

    resp = await client.get(url, headers=headers, follow_redirects=True)
    if resp.status_code != 200:
        raise XHSError(f"Page returned status {resp.status_code}, cookie may be required")
    return resp.text


def _extract_initial_state(html: str) -> dict:
    """Parse __INITIAL_STATE__ from page HTML.

    The value is a JS object literal, not strict JSON, so we use
    yaml.safe_load() — same approach as XHS-Downloader.
    """
    tree = etree.HTML(html)
    scripts = tree.xpath("//script/text()")
    for script in reversed(scripts):
        if script.startswith("window.__INITIAL_STATE__"):
            text = script[len("window.__INITIAL_STATE__="):]
            cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
            return yaml.safe_load(cleaned)
    raise XHSError("__INITIAL_STATE__ not found in page")


def _extract_note_data(state: dict) -> dict:
    note_data = (
        state.get("noteData", {}).get("data", {}).get("noteData")
        or state.get("note", {}).get("noteDetailMap", {})
    )
    if not note_data:
        raise XHSError("Could not extract note data from page")

    if isinstance(note_data, dict):
        if "note" in note_data:
            note_data = note_data["note"]
        else:
            vals = list(note_data.values())
            if vals and isinstance(vals[0], dict) and "note" in vals[0]:
                note_data = vals[0]["note"]

    return note_data


def _get_video_url(note: dict) -> Optional[str]:
    video = note.get("video", {}) or {}
    consumer = video.get("consumer", {}) or {}
    origin_key = consumer.get("originVideoKey", "")
    if origin_key:
        return f"https://sns-video-bd.xhscdn.com/{origin_key}"

    media = video.get("media", {}) or {}
    stream = media.get("stream", {}) or {}
    for codec in ("h264", "h265"):
        items = stream.get(codec, [])
        if items:
            best = max(items, key=lambda x: x.get("height", 0) or 0)
            backup = best.get("backupUrls", [])
            if backup:
                return backup[0]
            if best.get("masterUrl"):
                return best["masterUrl"]

    return None


async def _download_file(url: str, save_path: Path, client: httpx.AsyncClient):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.xiaohongshu.com/",
    }
    resp = await client.get(url, headers=headers, follow_redirects=True)
    resp.raise_for_status()
    save_path.write_bytes(resp.content)


async def download_video(
    url: str,
    output_dir: str,
    cookie: str = "",
    proxy: str = "",
) -> dict:
    """Download a Xiaohongshu video and return metadata.

    Args:
        url: Share link (xhslink.com or xiaohongshu.com)
        output_dir: Output directory path
        cookie: Xiaohongshu cookie (optional but helps avoid rate-limiting)
        proxy: HTTP proxy address (optional)

    Returns:
        dict: {title, author, video_path, description}
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    proxy_arg = proxy or None

    async with _make_client(proxy_arg) as client:
        if "xhslink.com" in url:
            url = await _resolve_short_url(url, client)

        html = await _fetch_page(url, client, cookie)

        state = _extract_initial_state(html)
        note = _extract_note_data(state)

        title = note.get("title", "") or note.get("displayTitle", "")
        desc = note.get("desc", "")
        user_info = note.get("user", {}) or {}
        author = user_info.get("nickname") or user_info.get("nickName") or ""

        video_url = _get_video_url(note)
        if video_url:
            ext = ".mp4"
            match = re.search(r"/([^/?]+\.(mp4|mov|webm|mkv))", video_url)
            if match:
                ext = "." + match.group(2)
            safe_title = re.sub(r'[\\/:*?"<>|]', "_", title)[:40]
            filename = f"{safe_title}{ext}"
            video_path = out / filename

            await _download_file(video_url, video_path, client)
        else:
            video_path = None

    return {
        "title": title or "untitled",
        "author": author or "unknown",
        "description": desc,
        "video_path": str(video_path) if video_path else "",
    }
