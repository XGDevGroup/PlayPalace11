#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! uv run --project . pyinstaller --version >/dev/null 2>&1; then
  echo "PyInstaller not found in uv environment. Installing..."
  uv add --dev pyinstaller pyinstaller-hooks-contrib
fi

DELIM=";"
if [[ "$(uname -s)" != MINGW* && "$(uname -s)" != CYGWIN* ]]; then
  DELIM=":"
fi

uv run --project . pyinstaller -y --clean --onedir --noconsole --name PlayPalace \
  --add-data "sounds${DELIM}sounds" \
  --add-data "defaults${DELIM}defaults" \
  client.py

DIST_DIR="dist/PlayPalace"
INTERNAL="$DIST_DIR/_internal/sounds"
TARGET="$DIST_DIR/sounds"
if [[ -d "$INTERNAL" ]]; then
  rm -rf "$TARGET"
  mv "$INTERNAL" "$TARGET"
fi

DEFAULTS_INTERNAL="$DIST_DIR/_internal/defaults"
DEFAULTS_TARGET="$DIST_DIR/defaults"
if [[ -d "$DEFAULTS_INTERNAL" ]]; then
  rm -rf "$DEFAULTS_TARGET"
  mv "$DEFAULTS_INTERNAL" "$DEFAULTS_TARGET"
fi

echo "Client build complete: $DIST_DIR"
