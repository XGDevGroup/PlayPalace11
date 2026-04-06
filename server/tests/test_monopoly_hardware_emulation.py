from pathlib import Path

from server.games.monopoly import hardware_emulation


def test_resolve_hardware_sound_asset_prefers_desktop_client_original(monkeypatch, tmp_path: Path):
    desktop_root = tmp_path / "clients" / "desktop" / "sounds"
    asset_path = desktop_root / "game_monopoly_hardware" / "original" / "jurassic_park_gate_theme.ogg"
    asset_path.parent.mkdir(parents=True, exist_ok=True)
    asset_path.write_bytes(b"ogg")

    monkeypatch.setattr(hardware_emulation, "_repo_root", lambda: tmp_path)

    sound_asset, source = hardware_emulation.resolve_hardware_sound_asset(
        "jurassic_park_gate_theme"
    )

    assert sound_asset == "game_monopoly_hardware/original/jurassic_park_gate_theme.ogg"
    assert source == "original"


def test_resolve_hardware_sound_asset_falls_back_to_placeholder_when_original_missing(
    monkeypatch, tmp_path: Path
):
    monkeypatch.setattr(hardware_emulation, "_repo_root", lambda: tmp_path)

    sound_asset, source = hardware_emulation.resolve_hardware_sound_asset(
        "jurassic_park_gate_roar"
    )

    assert sound_asset == "game_monopoly_hardware/jurassic_park_gate_roar_placeholder.ogg"
    assert source == "placeholder"
