"""Export packet schemas for both server and client consumers."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from server.network.packet_models import (  # pylint: disable=wrong-import-position
    CLIENT_TO_SERVER_PACKET_ADAPTER,
    SERVER_TO_CLIENT_PACKET_ADAPTER,
)


def _default_paths() -> tuple[Path, Path, Path]:
    base_dir = Path(__file__).resolve().parents[1]
    repo_root = Path(__file__).resolve().parents[2]
    server_path = base_dir / "packet_schema.json"
    desktop_path = repo_root / "clients" / "desktop" / "packet_schema.json"
    web_path = repo_root / "clients" / "web" / "packet_schema.json"
    return server_path, desktop_path, web_path


def _write_schema(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    server_default, desktop_default, web_default = _default_paths()

    parser = argparse.ArgumentParser(description="Export packet JSON schemas.")
    parser.add_argument(
        "--server-out",
        type=Path,
        default=server_default,
        help="Path to write the server copy of the schema JSON.",
    )
    parser.add_argument(
        "--client-out",
        type=Path,
        default=desktop_default,
        help="Path to write the client copy of the schema JSON.",
    )
    parser.add_argument(
        "--web-out",
        type=Path,
        default=web_default,
        help="Path to write the web client copy of the schema JSON.",
    )
    args = parser.parse_args()

    CLIENT_TO_SERVER_PACKET_ADAPTER.rebuild()
    SERVER_TO_CLIENT_PACKET_ADAPTER.rebuild()

    payload = {
        "client_to_server": CLIENT_TO_SERVER_PACKET_ADAPTER.json_schema(),
        "server_to_client": SERVER_TO_CLIENT_PACKET_ADAPTER.json_schema(),
    }

    for target in (args.server_out, args.client_out, args.web_out):
        _write_schema(target, payload)
        print(f"Wrote schema to {target}")


if __name__ == "__main__":
    main()
