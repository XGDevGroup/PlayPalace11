#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

DELIM=";"
if [[ "$(uname -s)" != MINGW* && "$(uname -s)" != CYGWIN* ]]; then
  DELIM=":"
fi

uv run --no-sync --with pyinstaller --with pyinstaller-hooks-contrib --project . pyinstaller -y --clean --onedir --noconsole --name PlayPalace \
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
