"""Shared bot scaffolding for push-your-luck dice games."""

from __future__ import annotations

import random
from typing import ClassVar

from .bot_helper import BotHelper


class PushYourLuckBotMixin:
    """Provides reusable logic for target-based push-your-luck bots."""

    push_target_range: ClassVar[tuple[int, int]] = (10, 25)

    def on_tick(self) -> None:
        """Ensure bot targets persist across reloads and drive BotHelper."""
        super().on_tick()
        if not getattr(self, "game_active", False):
            return

        player = getattr(self, "current_player", None)
        if player and player.is_bot and BotHelper.get_target(player) is None:
            self._set_push_bot_target(player)

        BotHelper.on_tick(self)

    def prepare_push_bot_turn(self, player) -> None:
        """Call at start of a bot's turn to (re)initialize its target."""
        if player and player.is_bot:
            self._set_push_bot_target(player)

    # ------------------------------------------------------------------
    # Hooks for subclasses
    # ------------------------------------------------------------------
    def _set_push_bot_target(self, player) -> None:
        target = self._calculate_push_bot_target(player)
        BotHelper.set_target(player, max(0, target))

    def _calculate_push_bot_target(self, player) -> int:
        low, high = self.push_target_range
        base = random.randint(low, high)  # nosec B311
        return self._adjust_push_bot_target(player, base)

    def _adjust_push_bot_target(self, player, target: int) -> int:
        """Override to tweak the per-turn target using game-specific heuristics."""
        return target


__all__ = ["PushYourLuckBotMixin"]
