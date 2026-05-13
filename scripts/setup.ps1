# FILE: scripts/setup.ps1

$ErrorActionPreference = "Stop"
$REPO_DIR = Split-Path -LiteralPath $PSScriptRoot -Parent
Set-Location $REPO_DIR

Write-Host "Installing ClipNote..."

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

Write-Host "ClipNote installed!"
Write-Host "Usage: paste a Xiaohongshu link in Claude Code to get started"
