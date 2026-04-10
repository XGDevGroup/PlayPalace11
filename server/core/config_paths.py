"""Helpers for resolving configuration paths across platforms."""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Any

import tomllib

_MODULE_DIR = Path(__file__).resolve().parent.parent
_WINDOWS_APP_DIR = "PlayPalace"


def _running_on_windows() -> bool:
    """Return True when executing on Windows."""
    return platform.system().lower() == "windows"


def get_default_config_dir() -> Path:
    """Return the default directory that should contain config.toml.

    When running from a source checkout (config.example.toml present next to
    the package) the module directory is used on every platform so that a
    developer's ``server/config.toml`` is always found.  The Windows
    ProgramData path is only used for an installed application where the
    example template has been removed.
    """
    if (_MODULE_DIR / "config.example.toml").exists():
        return _MODULE_DIR
    if _running_on_windows():
        program_data = os.environ.get("PROGRAMDATA")
        if program_data:
            return Path(program_data) / _WINDOWS_APP_DIR
    return _MODULE_DIR


def get_default_config_path() -> Path:
    """Return the default config.toml location for the current platform."""
    return get_default_config_dir() / "config.toml"


def get_example_config_path() -> Path:
    """Return the path to the repository's config example file."""
    return _MODULE_DIR / "config.example.toml"


def ensure_default_config_dir() -> Path:
    """Create the default config directory if it does not exist."""
    target_dir = get_default_config_dir()
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


def load_full_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load the full config.toml contents as a dictionary.

    Returns an empty dict if the file is missing or unreadable.
    """
    if path is None:
        path = get_default_config_path()
    path = Path(path)
    if not path.exists():
        return {}
    try:
        with path.open("rb") as fh:
            return tomllib.load(fh)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        import logging
        logging.getLogger("playpalace.config").error(
            "Failed to load config from %s: %s", path, exc,
        )
        return {}
