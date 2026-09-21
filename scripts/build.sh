#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/build.py
printf 'Run it with:  %s\n' "$ROOT_DIR/dist/mdr"
