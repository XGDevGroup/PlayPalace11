from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Set, get_args

import pytest

from server.network.packet_models import (
    CLIENT_TO_SERVER_PACKET_ADAPTER,
    SERVER_TO_CLIENT_PACKET_ADAPTER,
    ClientToServerPacket,
    ServerToClientPacket,
)


CLIENT_TO_SERVER_SAMPLES = [
    {"type": "authorize", "username": "user", "password": "pw"},
    {"type": "authorize", "username": "user", "session_token": "token"},
    {"type": "register", "username": "user", "password": "pw", "email": "e@example.com"},
    {
        "type": "refresh_session",
        "refresh_token": "rtok",
        "username": "user",
        "client_type": "Desktop",
        "platform": "Linux",
    },
    {"type": "menu", "menu_id": "main", "selection": 1},
    {"type": "keybind", "key": "f1"},
    {"type": "escape", "menu_id": "main"},
    {"type": "editbox", "text": "hello", "input_id": "chat"},
    {"type": "chat", "convo": "local", "message": "hi", "language": "English"},
    {"type": "ping"},
    {"type": "list_online"},
    {"type": "list_online_with_games"},
    {
        "type": "playlist_duration_response",
        "request_id": "req",
        "playlist_id": "pid",
        "duration_type": "total",
        "duration": 0,
    },
    {"type": "client_options", "options": {"theme": "dark"}},
    {"type": "slash_command", "command": "foo", "args": "bar"},
    {"type": "admins_cmd"},
    {"type": "broadcast_cmd", "message": "hello"},
    {"type": "set_table_visibility_cmd", "state": True},
    {"type": "check_table_visibility_cmd"},
    {"type": "set_table_pw_cmd", "password": "secret"},
    {"type": "remove_table_pw_cmd"},
    {"type": "check_table_pw_cmd"},
]


SERVER_TO_CLIENT_SAMPLES = [
    {
        "type": "authorize_success",
        "username": "user",
        "version": "11.0.0",
        "session_token": "atok",
        "session_expires_at": 999999,
        "refresh_token": "rtok",
        "refresh_expires_at": 999999,
    },
    {
        "type": "refresh_session_success",
        "username": "user",
        "version": "11.0.0",
        "session_token": "atok",
        "session_expires_at": 999999,
        "refresh_token": "rtok",
        "refresh_expires_at": 999999,
    },
    {"type": "refresh_session_failure", "message": "Session expired"},
    {"type": "speak", "text": "hello", "buffer": "activity"},
    {"type": "play_sound", "name": "ding", "volume": 80, "pan": 0, "pitch": 90},
    {"type": "play_music", "name": "theme", "looping": False},
    {"type": "stop_music"},
    {"type": "play_ambience", "loop": "rain"},
    {"type": "stop_ambience"},
    {"type": "menu", "menu_id": "main", "items": ["Play"]},
    {"type": "request_input", "input_id": "chat", "prompt": "Say something"},
    {"type": "clear_ui"},
    {
        "type": "disconnect",
        "reconnect": False,
        "show_message": True,
        "return_to_login": True,
    },
    {
        "type": "server_status",
        "mode": "maintenance",
        "retry_after": 30,
        "message": "Applying updates",
        "resume_at": "2026-02-07T18:00:00Z",
    },
    {"type": "table_create", "host": "Alice", "game": "Poker"},
    {"type": "update_options_lists", "games": [{"type": "poker", "name": "Poker"}]},
    {"type": "pong"},
    {"type": "chat", "convo": "global", "sender": "Alice", "message": "hi", "language": "English"},
    {
        "type": "game_list",
        "games": [
            {"id": "table1", "name": "Poker", "type": "poker", "players": 2, "max_players": 4}
        ],
    },
    {"type": "add_playlist", "playlist_id": "main", "tracks": ["intro.ogg"]},
    {"type": "start_playlist", "playlist_id": "main"},
    {"type": "remove_playlist", "playlist_id": "main"},
    {
        "type": "get_playlist_duration",
        "playlist_id": "main",
        "duration_type": "total",
        "request_id": "abc",
    },
    {"type": "open_client_options", "options": {}},
    {"type": "open_server_options", "options": {}},
]


def _packet_type_names(packet_union: object) -> Set[str]:
    union = get_args(packet_union)[0]
    names = set()
    for model_cls in get_args(union):
        field = model_cls.model_fields["type"]
        names.add(field.default)
    return names


@pytest.mark.parametrize("payload", CLIENT_TO_SERVER_SAMPLES)
def test_client_packets_round_trip(payload: dict) -> None:
    model = CLIENT_TO_SERVER_PACKET_ADAPTER.validate_python(payload)
    assert model.type == payload["type"]
    assert model.model_dump(exclude_none=True)["type"] == payload["type"]


@pytest.mark.parametrize("payload", SERVER_TO_CLIENT_SAMPLES)
def test_server_packets_round_trip(payload: dict) -> None:
    model = SERVER_TO_CLIENT_PACKET_ADAPTER.validate_python(payload)
    assert model.type == payload["type"]
    assert model.model_dump(exclude_none=True)["type"] == payload["type"]


def _extract_literal_types(paths: Iterable[Path]) -> Set[str]:
    pattern = re.compile(r'"type"\s*:\s*"([^"]+)"')
    found: Set[str] = set()
    for base in paths:
        if base.is_file():
            files = [base]
        else:
            files = list(base.rglob("*.py"))
        for file in files:
            text = file.read_text(encoding="utf-8", errors="ignore")
            found.update(pattern.findall(text))
    return found


def test_all_literal_types_are_in_schema() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    scan_paths = [
        repo_root / "server" / "core",
        repo_root / "clients" / "desktop" / "ui",
        repo_root / "clients" / "desktop" / "network_manager.py",
        repo_root / "clients" / "desktop" / "ui" / "slash_commands.py",
    ]
    found = _extract_literal_types(scan_paths)
    # Filter out literals that aren't protocol packets but appear in UI widgets or helpers
    noise = {
        "bool",
        "int",
        "integer",
        "string",
        "number",
        "array",
        "object",
        "nullable",
        "null",
        "typed-dict",
        "typed-dict-field",
    }
    found -= noise
    schema_types = _packet_type_names(ClientToServerPacket) | _packet_type_names(
        ServerToClientPacket
    )
    assert found <= schema_types, f"Missing schema entries for: {sorted(found - schema_types)}"


def test_packet_schema_files_are_up_to_date(tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2]
    server_dir = repo_root / "server"
    server_out = tmp_path / "server_schema.json"
    client_out = tmp_path / "client_schema.json"
    web_out = tmp_path / "web_schema.json"
    subprocess.run(
        [
            sys.executable,
            "tools/export_packet_schema.py",
            "--server-out",
            str(server_out),
            "--client-out",
            str(client_out),
            "--web-out",
            str(web_out),
        ],
        cwd=server_dir,
        check=True,
    )
    assert server_out.read_text(encoding="utf-8") == (server_dir / "packet_schema.json").read_text(
        encoding="utf-8"
    )
    assert client_out.read_text(encoding="utf-8") == (
        repo_root / "clients" / "desktop" / "packet_schema.json"
    ).read_text(encoding="utf-8")
    assert web_out.read_text(encoding="utf-8") == (
        repo_root / "clients" / "web" / "packet_schema.json"
    ).read_text(encoding="utf-8")
