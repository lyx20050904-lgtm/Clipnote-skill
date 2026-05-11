#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "🔧 Installing ClipNote..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip

pip install -r requirements.txt --no-deps

pip install funasr==1.3.1 --no-deps
pip install torch torchaudio librosa soundfile jieba sentencepiece \
    omegaconf hydra-core kaldiio modelscope einops scipy transformers \
    pyyaml tqdm requests filelock typing-extensions

echo "✅ ClipNote installed!"
echo "📌 Usage: paste a Xiaohongshu link in Claude Code to get started"
