#!/usr/bin/env python3
"""Transcribe audio file to text using SenseVoice.

Usage: python scripts/transcribe.py <audio_path>

Prints JSON with transcribed text to stdout.
"""

import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def load_config() -> dict:
    config_path = Path(__file__).parent.parent / "config.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text())


def transcribe(audio_path: str) -> str:
    """Transcribe audio to text using SenseVoice (chunked to avoid OOM)."""
    from funasr import AutoModel
    import librosa

    config = load_config()
    model_name = config.get("sensevoice_model", "small")

    if model_name == "small":
        model_id = "iic/SenseVoiceSmall"
    else:
        model_id = "iic/SenseVoiceLarge"

    cache_dir = Path.home() / ".cache" / "modelscope" / "hub" / "models" / model_id
    model_local_path = str(cache_dir) if cache_dir.exists() else model_id

    import logging
    logging.getLogger("funasr").setLevel(logging.ERROR)
    logging.getLogger("modelscope").setLevel(logging.ERROR)

    model = AutoModel(
        model=model_local_path,
        model_path=model_local_path,
        hub="ms",
        check_latest=False,
        device="cpu",
        disable_update=True,
    )

    # Load audio and split into 30-second chunks to limit peak memory
    audio, sr = librosa.load(audio_path, sr=16000, mono=True)
    chunk_len = 30 * sr  # 30 seconds
    chunks = [audio[i:i + chunk_len] for i in range(0, len(audio), chunk_len)]

    import re

    texts = []
    for i, chunk in enumerate(chunks):
        result = model.generate(input=chunk)
        if result and isinstance(result, list):
            text = result[0].get("text", "")
            # Strip SenseVoice special tokens: <|zh|>, <|NEUTRAL|>, <|BGM|>, etc.
            text = re.sub(r"<\|[^|]+\|>", "", text).strip()
            texts.append(text)

    return "".join(texts)


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/transcribe.py <audio_path>", file=sys.stderr)
        sys.exit(1)

    audio_path = sys.argv[1]
    if not Path(audio_path).exists():
        print(f"Error: audio not found: {audio_path}", file=sys.stderr)
        sys.exit(1)

    try:
        text = transcribe(audio_path)
        print(json.dumps({"text": text}, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
