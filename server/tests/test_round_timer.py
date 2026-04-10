"""Tests for RoundTransitionTimer countdown and pause."""

from dataclasses import dataclass, field

from server.game_utils.round_timer import RoundTransitionTimer


@dataclass
class DummyGame:
    """Minimal game stub with the fields RoundTransitionTimer expects."""

    round_timer_state: str = "idle"
    round_timer_ticks: int = 0
    broadcast_calls: list = field(default_factory=list)
    round_ready_calls: int = 0

    def broadcast_l(self, message_id: str, **kwargs) -> None:
        self.broadcast_calls.append((message_id, kwargs))

    def on_round_timer_ready(self) -> None:
        self.round_ready_calls += 1


class TestTimerStart:
    def test_start_sets_counting_state(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, delay_seconds=5.0)
        timer.start()
        assert game.round_timer_state == "counting"
        assert game.round_timer_ticks == 100  # 5 * 20

    def test_start_with_override_delay(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, delay_seconds=15.0)
        timer.start(delay_seconds=3.0)
        assert game.round_timer_ticks == 60  # 3 * 20

    def test_is_active_when_counting(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        assert timer.is_active is False
        timer.start()
        assert timer.is_active is True


class TestTimerTick:
    def test_on_tick_decrements(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, delay_seconds=1.0)
        timer.start()
        initial = game.round_timer_ticks
        timer.on_tick()
        assert game.round_timer_ticks == initial - 1

    def test_on_tick_fires_ready_at_zero(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, delay_seconds=0.05)
        timer.start()  # 1 tick (0.05 * 20 = 1)
        timer.on_tick()
        assert game.round_timer_state == "idle"
        assert game.round_ready_calls == 1

    def test_on_tick_noop_when_idle(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        game.round_timer_ticks = 10
        timer.on_tick()  # state is idle, should not decrement
        assert game.round_timer_ticks == 10

    def test_on_tick_noop_when_paused(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.start()
        timer.toggle_pause()  # pause
        ticks_before = game.round_timer_ticks
        timer.on_tick()
        assert game.round_timer_ticks == ticks_before

    def test_countdown_to_completion(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, delay_seconds=0.15)
        timer.start()  # 3 ticks
        for _ in range(3):
            timer.on_tick()
        assert game.round_timer_state == "idle"
        assert game.round_ready_calls == 1


class TestTimerPause:
    def test_toggle_pause_pauses_counting(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.start()
        timer.toggle_pause(player_name="Host")
        assert game.round_timer_state == "paused"
        assert timer.is_paused is True
        assert timer.is_active is True

    def test_toggle_pause_broadcasts_message(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game, pause_message="round-timer-paused")
        timer.start()
        timer.toggle_pause(player_name="Host")
        assert len(game.broadcast_calls) == 1
        assert game.broadcast_calls[0][0] == "round-timer-paused"

    def test_toggle_pause_when_paused_skips_to_ready(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.start()
        timer.toggle_pause()  # pause
        timer.toggle_pause()  # skip to ready
        assert game.round_timer_state == "idle"
        assert game.round_ready_calls == 1

    def test_toggle_pause_when_idle_does_nothing(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.toggle_pause()  # idle, should be a no-op
        assert game.round_timer_state == "idle"
        assert game.round_ready_calls == 0


class TestTimerStop:
    def test_stop_resets_to_idle(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.start()
        timer.stop()
        assert game.round_timer_state == "idle"
        assert game.round_timer_ticks == 0
        assert timer.is_active is False

    def test_stop_does_not_fire_ready(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        timer.start()
        timer.stop()
        assert game.round_ready_calls == 0


class TestTimerRemainingSeconds:
    def test_remaining_seconds_rounds_up(self):
        game = DummyGame()
        timer = RoundTransitionTimer(game)
        game.round_timer_ticks = 1
        assert timer.remaining_seconds == 1  # (1 + 19) // 20 = 1
        game.round_timer_ticks = 20
        assert timer.remaining_seconds == 1
        game.round_timer_ticks = 21
        assert timer.remaining_seconds == 2
        game.round_timer_ticks = 0
        assert timer.remaining_seconds == 0
