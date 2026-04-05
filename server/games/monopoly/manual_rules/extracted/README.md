# Monopoly Manual Extraction Artifacts

This folder stores deterministic extraction artifacts for manual-auth work:

- `<board_id>.txt`: extracted PDF text split by page markers.
- `<board_id>.json`: checksum and extraction metadata for that board.
- `manifest.json`: summary rows for all selected boards in the extraction run.

## Current Scope

- All boards in `server/games/monopoly/catalog/special_board_anchor_index.json` (55 boards).

Generated via:

```bash
./.venv/bin/python server/scripts/monopoly/extract_manual_text.py \
  --family animal --family barbie --family black --family deadpool --family disney \
  --family fortnite --family game --family ghostbusters --family harry --family junior \
  --family jurassic --family lord --family mario --family marvel --family pokemon \
  --family star --family stranger --family toy --family transformers
```

`marvel_flip` is handled by a fallback mode:

- Primary mode: `pypdf` extraction.
- Fallback mode: `strings_fallback` after bounded decompression retries.
