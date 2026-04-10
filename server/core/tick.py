"""Tick scheduler for game updates."""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Callable

LOG = logging.getLogger("playpalace.tick")

DEFAULT_TICK_INTERVAL_MS = 50


from .config_paths import get_default_config_path


def load_server_config(path: str | Path | None = None) -> dict:
    """
    Load server configuration from config.toml.

    Args:
        path: Path to config file. If None, uses server/config.toml.

    Returns:
        Dictionary with server config values.
    """
    if path is None:
        path = get_default_config_path()

    path = Path(path)
    if not path.exists():
        return {}

    import tomllib

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as exc:
        print(f"ERROR: Failed to parse configuration file '{path}': {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    except OSError as exc:
        print(f"ERROR: Failed to read configuration file '{path}': {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    return data.get("server", {})


class TickScheduler:
    """
    Schedules game ticks at a fixed interval.

    The tick callback is called synchronously within the async context.
    This keeps game logic simple while allowing async network I/O.

    The tick interval can be configured via config.toml [server] section
    or passed directly to the constructor.
    """

    def __init__(self, on_tick: Callable[[], None], tick_interval_ms: int | None = None):
        """
        Initialize the tick scheduler.

        Args:
            on_tick: Callback function to call on each tick.
            tick_interval_ms: Tick interval in milliseconds. If None, uses default (50ms).
        """
        self._on_tick = on_tick
        self._running = False
        self._task: asyncio.Task | None = None

        if tick_interval_ms is None:
            tick_interval_ms = DEFAULT_TICK_INTERVAL_MS
        self.tick_interval_ms = tick_interval_ms
        self.tick_interval_s = tick_interval_ms / 1000.0

    async def start(self) -> None:
        """Start the tick scheduler."""
        self._running = True
        self._task = asyncio.create_task(self._tick_loop())

    async def stop(self) -> None:
        """Stop the tick scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _tick_loop(self) -> None:
        """Main tick loop."""
        while self._running:
            try:
                self._on_tick()
            except Exception:
                LOG.exception("Error in tick callback")

            await asyncio.sleep(self.tick_interval_s)
