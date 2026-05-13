#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_DIR"

echo "Installing ClipNote..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip

pip install -r requirements.txt

echo "ClipNote installed!"
echo "Usage: paste a Xiaohongshu link in Claude Code to get started"
