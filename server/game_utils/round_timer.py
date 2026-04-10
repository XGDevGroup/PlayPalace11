"""Round timer utility for managing delays between rounds.

This is a stateless helper that operates on serialized Game fields:
- game.round_timer_state: "idle", "counting", or "paused"
- game.round_timer_ticks: Remaining ticks in countdown
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..games.base import Game


class RoundTransitionTimer:
    """Manage delays between rounds using serialized game fields.

    The timer is stateless; all data lives on the Game instance. The host can
    pause/resume the countdown via the pause key.

    Usage:
        self._round_timer = RoundTransitionTimer(self)
        self._round_timer.start()
        self._round_timer.on_tick()

        # Override in your game:
        def on_round_timer_ready(self) -> None:
            self._start_round()
    """

    # Timer states (stored in game.round_timer_state)
    IDLE = "idle"  # Not running
    COUNTING = "counting"  # Counting down
    PAUSED = "paused"  # Paused by host

    def __init__(
        self,
        game: "Game",
        delay_seconds: float = 15.0,
        pause_message: str = "round-timer-paused",
    ):
        """
        Initialize the round timer.

        Args:
            game: The game instance.
            delay_seconds: Seconds to wait between rounds (default 15).
            pause_message: Localization key for pause announcement.
        """
        self._game = game
        self._delay_ticks = int(delay_seconds * 20)  # assumes default tick rate
        self._pause_message = pause_message

    @property
    def is_active(self) -> bool:
        """Check if the timer is running (counting or paused)."""
        return self._game.round_timer_state in (self.COUNTING, self.PAUSED)

    @property
    def is_paused(self) -> bool:
        """Check if the timer is paused."""
        return self._game.round_timer_state == self.PAUSED

    @property
    def remaining_seconds(self) -> int:
        """Get remaining seconds (rounded up)."""
        return (self._game.round_timer_ticks + 19) // 20

    def start(self, delay_seconds: float | None = None) -> None:
        """
        Start the countdown timer.

        Args:
            delay_seconds: Override the default delay for this countdown.
        """
        if delay_seconds is not None:
            self._game.round_timer_ticks = int(delay_seconds * 20)
        else:
            self._game.round_timer_ticks = self._delay_ticks
        self._game.round_timer_state = self.COUNTING

    def stop(self) -> None:
        """Stop the timer without triggering the callback."""
        self._game.round_timer_state = self.IDLE
        self._game.round_timer_ticks = 0

    def toggle_pause(self, player_name: str | None = None) -> None:
        """
        Toggle pause state. Called when host presses 'p'.

        - If counting: pause the timer
        - If paused: skip remaining time and start next round
        - If idle: do nothing

        Args:
            player_name: Name of the player who triggered the action.
        """
        if self._game.round_timer_state == self.COUNTING:
            # Pause the countdown
            self._game.round_timer_state = self.PAUSED
            self._game.broadcast_l(self._pause_message, player=player_name or "")
        elif self._game.round_timer_state == self.PAUSED:
            # Skip to next round
            self._game.round_timer_state = self.IDLE
            self._game.round_timer_ticks = 0
            self._game.on_round_timer_ready()

    def on_tick(self) -> None:
        """Called every game tick. Decrements timer if counting."""
        if self._game.round_timer_state != self.COUNTING:
            return

        self._game.round_timer_ticks -= 1

        # Check if timer expired
        if self._game.round_timer_ticks <= 0:
            self._game.round_timer_state = self.IDLE
            self._game.on_round_timer_ready()
