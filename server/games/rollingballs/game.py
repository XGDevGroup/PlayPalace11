"""
Rolling Balls Game Implementation for PlayPalace v11.

Take turns picking 1, 2, or 3 balls from a pipe. Watch out for negative balls!
The player with the most points when the pipe empties wins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
import random
from pathlib import Path

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MultiSelectOption, multi_select_field, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


# Cached ball packs data
_ball_packs: dict[str, dict[str, int]] | None = None


def load_ball_packs() -> dict[str, dict[str, int]]:
    """Load ball packs from JSON file. Results are cached."""
    global _ball_packs
    if _ball_packs is None:
        packs_path = Path(__file__).parent / "ball_packs.json"
        with open(packs_path, "r", encoding="utf-8") as f:
            _ball_packs = json.load(f)
    return _ball_packs


def get_pack_names() -> list[str]:
    """Get available pack IDs."""
    return list(load_ball_packs().keys())


@dataclass
class RollingBallsPlayer(Player):
    """Player state for Rolling Balls game."""

    score: int = 0
    has_reshuffled: bool = False  # Reset each turn
    view_pipe_uses: int = 0  # Total uses this game
    reshuffle_uses: int = 0  # Total uses this game
    last_viewed_pipe: list[dict] | None = None  # Snapshot of pipe at last view
    bot_pipe_memory: int = 0  # Balls from front the bot remembers (bots only)


@dataclass
class RollingBallsOptions(GameOptions):
    """Options for Rolling Balls game."""

    min_take: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=5,
            value_key="count",
            label="rb-set-min-take",
            prompt="rb-enter-min-take",
            change_msg="rb-option-changed-min-take",
        )
    )
    max_take: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=5,
            value_key="count",
            label="rb-set-max-take",
            prompt="rb-enter-max-take",
            change_msg="rb-option-changed-max-take",
        )
    )
    view_pipe_limit: int = option_field(
        IntOption(
            default=5,
            min_val=0,
            max_val=100,
            value_key="count",
            label="rb-set-view-pipe-limit",
            prompt="rb-enter-view-pipe-limit",
            change_msg="rb-option-changed-view-pipe-limit",
        )
    )
    reshuffle_limit: int = option_field(
        IntOption(
            default=3,
            min_val=0,
            max_val=100,
            value_key="count",
            label="rb-set-reshuffle-limit",
            prompt="rb-enter-reshuffle-limit",
            change_msg="rb-option-changed-reshuffle-limit",
        )
    )
    reshuffle_penalty: int = option_field(
        IntOption(
            default=1,
            min_val=0,
            max_val=5,
            value_key="points",
            label="rb-set-reshuffle-penalty",
            prompt="rb-enter-reshuffle-penalty",
            change_msg="rb-option-changed-reshuffle-penalty",
        ),
        visible_when=("reshuffle_limit", lambda v: v > 0),
    )
    ball_packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=[get_pack_names()[0]],
            choices=get_pack_names,
            label="rb-set-ball-packs",
            change_msg="rb-option-changed-ball-packs",
            min_selected=1,
        )
    )


@dataclass
@register_game
class RollingBallsGame(ActionGuardMixin, Game):
    """
    Rolling Balls pipe game.

    Players take turns picking 1, 2, or 3 balls from a pipe. Each ball has
    a value from -5 to +5 with a flavor description. The player with the
    highest score when the pipe empties wins.
    """

    players: list[RollingBallsPlayer] = field(default_factory=list)
    options: RollingBallsOptions = field(default_factory=RollingBallsOptions)
    pipe: list[dict] = field(default_factory=list)
    _ball_reveal_queue: list[dict] = field(default_factory=list)
    _ball_reveal_tick: int = 0
    _ball_reveal_player_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Rolling Balls"

    @classmethod
    def get_type(cls) -> str:
        return "rollingballs"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> RollingBallsPlayer:
        """Create a new player with Rolling Balls state."""
        return RollingBallsPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Option change handling
    # ==========================================================================

    def _handle_option_change(self, option_name: str, value: str) -> None:
        """Handle option changes, rebuilding turn actions when min/max take change."""
        super()._handle_option_change(option_name, value)

        if option_name == "min_take":
            # Clamp max_take up if needed
            if self.options.max_take < self.options.min_take:
                self.options.max_take = self.options.min_take
            self._rebuild_turn_actions()
        elif option_name == "max_take":
            # Clamp min_take down if needed
            if self.options.min_take > self.options.max_take:
                self.options.min_take = self.options.max_take
            self._rebuild_turn_actions()

    def _rebuild_turn_actions(self) -> None:
        """Rebuild the turn action set for all players to reflect min/max take changes."""
        for player in self.players:
            turn_set = self.get_action_set(player, "turn")
            if turn_set:
                # Remove old take actions
                turn_set.remove_by_prefix("take_")
                # Add new take actions
                user = self.get_user(player)
                locale = user.locale if user else "en"
                for n in range(self.options.min_take, self.options.max_take + 1):
                    turn_set.add(
                        Action(
                            id=f"take_{n}",
                            label=Localization.get(locale, "rb-take", count=n),
                            handler="_action_take",
                            is_enabled="_is_take_enabled",
                            is_hidden="_is_take_hidden",
                        )
                    )
        self.rebuild_all_menus()

    # ==========================================================================
    # Pipe management
    # ==========================================================================

    def _get_active_packs(self) -> list[str]:
        """Get list of active pack IDs."""
        return list(self.options.ball_packs)

    def fill_pipe(self) -> int:
        """Fill the pipe with balls based on player count."""
        player_count = len(self.get_active_players())
        if player_count >= 4:
            total_balls = 50
        elif player_count == 3:
            total_balls = 35
        else:
            total_balls = 25

        # Build combined ball pool from active packs
        packs = load_ball_packs()
        ball_pool: list[tuple[str, int]] = []
        for pack_id in self._get_active_packs():
            pack = packs.get(pack_id, {})
            ball_pool.extend(pack.items())

        self.pipe = []
        for _ in range(total_balls):
            description, value = random.choice(ball_pool)  # nosec B311
            self.pipe.append({"value": value, "description": description})
        return total_balls

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: RollingBallsPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # View pipe (always visible during play, doesn't require turn)
        if self.options.view_pipe_limit > 0:
            remaining = self.options.view_pipe_limit - player.view_pipe_uses
            action_set.add(
                Action(
                    id="view_pipe",
                    label=Localization.get(locale, "rb-view-pipe-action", remaining=remaining),
                    handler="_action_view_pipe",
                    is_enabled="_is_view_pipe_enabled",
                    is_hidden="_is_view_pipe_hidden",
                    get_label="_get_view_pipe_label",
                    show_in_actions_menu=True,
                )
            )

        # Reshuffle pipe
        if self.options.reshuffle_limit > 0:
            remaining = self.options.reshuffle_limit - player.reshuffle_uses
            action_set.add(
                Action(
                    id="reshuffle",
                    label=Localization.get(locale, "rb-reshuffle-action", remaining=remaining),
                    handler="_action_reshuffle",
                    is_enabled="_is_reshuffle_enabled",
                    is_hidden="_is_reshuffle_hidden",
                    get_label="_get_reshuffle_label",
                )
            )

        # Take N balls (dynamic based on min/max options)
        for n in range(self.options.min_take, self.options.max_take + 1):
            action_set.add(
                Action(
                    id=f"take_{n}",
                    label=Localization.get(locale, "rb-take", count=n),
                    handler="_action_take",
                    is_enabled="_is_take_enabled",
                    is_hidden="_is_take_hidden",
                )
            )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        for n in range(1, 6):
            label = f"Take {n} ball{'s' if n != 1 else ''}"
            self.define_keybind(str(n), label, [f"take_{n}"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Reshuffle pipe", ["reshuffle"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "View pipe", ["view_pipe"], state=KeybindState.ACTIVE)

    # ==========================================================================
    # is_enabled callbacks
    # ==========================================================================

    def _is_take_enabled(self, player: Player, action_id: str) -> str | None:
        if self._ball_reveal_player_id:
            return "action-not-your-turn"
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        count = int(action_id.removeprefix("take_"))
        if len(self.pipe) < count:
            return "rb-not-enough-balls"
        return None

    def _is_reshuffle_enabled(self, player: Player) -> str | None:
        if self._ball_reveal_player_id:
            return "action-not-your-turn"
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        rb_player: RollingBallsPlayer = player  # type: ignore
        if rb_player.reshuffle_uses >= self.options.reshuffle_limit:
            return "rb-no-reshuffles-left"
        if rb_player.has_reshuffled:
            return "rb-already-reshuffled"
        if len(self.pipe) < 6:
            return "rb-not-enough-balls"
        return None

    def _is_view_pipe_enabled(self, player: Player) -> str | None:
        error = self.guard_game_active()
        if error:
            return error
        rb_player: RollingBallsPlayer = player  # type: ignore
        if rb_player.view_pipe_uses >= self.options.view_pipe_limit:
            return "rb-no-views-left"
        return None

    # ==========================================================================
    # is_hidden callbacks
    # ==========================================================================

    def _is_take_hidden(self, player: Player, action_id: str) -> Visibility:
        count = int(action_id.removeprefix("take_"))
        return self.turn_action_visibility(player, extra_condition=len(self.pipe) >= count)

    def _is_reshuffle_hidden(self, player: Player) -> Visibility:
        rb_player: RollingBallsPlayer = player  # type: ignore
        can_reshuffle = (
            self.options.reshuffle_limit > 0
            and rb_player.reshuffle_uses < self.options.reshuffle_limit
            and not rb_player.has_reshuffled
            and len(self.pipe) >= 6
        )
        return self.turn_action_visibility(player, extra_condition=can_reshuffle)

    def _is_view_pipe_hidden(self, player: Player) -> Visibility:
        rb_player: RollingBallsPlayer = player  # type: ignore
        can_view = (
            self.options.view_pipe_limit > 0
            and rb_player.view_pipe_uses < self.options.view_pipe_limit
            and self.status == "playing"
        )
        if can_view:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # get_label callbacks
    # ==========================================================================

    def _get_reshuffle_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        rb_player: RollingBallsPlayer = player  # type: ignore
        remaining = self.options.reshuffle_limit - rb_player.reshuffle_uses
        return Localization.get(locale, "rb-reshuffle-action", remaining=remaining)

    def _get_view_pipe_label(self, player: Player, action_id: str) -> str:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        rb_player: RollingBallsPlayer = player  # type: ignore
        remaining = self.options.view_pipe_limit - rb_player.view_pipe_uses
        return Localization.get(locale, "rb-view-pipe-action", remaining=remaining)

    # ==========================================================================
    # Action handlers
    # ==========================================================================

    def _action_take(self, player: Player, action_id: str) -> None:
        count = int(action_id.removeprefix("take_"))
        self._take_balls(player, count)

    def _take_balls(self, player: Player, count: int) -> None:
        """Take balls from the pipe, queuing reveals for on_tick."""
        rb_player: RollingBallsPlayer = player  # type: ignore

        self.broadcast_personal_l(player, "rb-you-take", "rb-player-takes", count=count)
        self.play_sound(f"game_rollingballs/take{random.randint(1, 3)}.ogg")

        # Pop balls from pipe and queue them for reveal
        balls = []
        for _ in range(count):
            if not self.pipe:
                break
            balls.append(self.pipe.pop(0))

        # Erode bot pipe memory (balls removed from front)
        taken = len(balls)
        for p in self.players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            if rb_p.is_bot:
                rb_p.bot_pipe_memory = max(0, rb_p.bot_pipe_memory - taken)

        # Apply scores immediately (game state is updated now)
        for ball in balls:
            rb_player.score += ball["value"]

        # Queue balls for synchronized sound+speech reveal in on_tick
        for i, ball in enumerate(balls, 1):
            ball["num"] = i
        self._ball_reveal_queue = balls
        self._ball_reveal_player_id = player.id
        self._ball_reveal_tick = self.sound_scheduler_tick + 8  # ~400 ms initial delay

    def _reveal_next_ball(self) -> None:
        """Reveal the next ball from the queue with synchronized sound and speech."""
        ball = self._ball_reveal_queue.pop(0)
        ball_num = ball["num"]

        # Play value sound and broadcast description
        value = ball["value"]
        description = ball["description"]
        abs_value = abs(value)
        sound_value = abs_value if abs_value <= 5 else 5

        # Play takeball sound immediately, schedule value sound 1 tick later
        self.play_sound("game_rollingballs/takeball.ogg")
        if value > 0:
            self.schedule_sound(
                f"game_rollingballs/plus{sound_value}.ogg", delay_ticks=1, volume=80
            )
            self.broadcast_l("rb-ball-plus", num=ball_num, description=description, value=abs_value)
        elif value < 0:
            self.schedule_sound(f"game_rollingballs/minus{sound_value}.ogg", delay_ticks=1)
            self.broadcast_l(
                "rb-ball-minus", num=ball_num, description=description, value=abs_value
            )
        else:
            self.broadcast_l("rb-ball-zero", num=ball_num, description=description)

        if self._ball_reveal_queue:
            # More balls to reveal - schedule next in 1200ms (24 ticks)
            self._ball_reveal_tick = self.sound_scheduler_tick + 12
        else:
            # All balls revealed - finish after 1500ms delay
            self._ball_reveal_tick = self.sound_scheduler_tick + 15

    def _finish_ball_reveals(self) -> None:
        """Announce score and end turn after all balls are revealed."""
        player = self.get_player_by_id(self._ball_reveal_player_id)
        self._ball_reveal_player_id = ""

        if not player:
            return
        rb_player: RollingBallsPlayer = player  # type: ignore

        self.broadcast_l("rb-new-score", player=player.name, score=rb_player.score)
        self.end_turn()

    def _action_reshuffle(self, player: Player, action_id: str) -> None:
        """Reshuffle a portion of the pipe."""
        rb_player: RollingBallsPlayer = player  # type: ignore

        self.broadcast_personal_l(player, "rb-you-reshuffle", "rb-player-reshuffles")
        self.play_sound(
            f"game_rollingballs/disrupt{random.randint(1, 2)}.ogg"  # nosec B311
        )

        # Shuffle the first min(len(pipe), 15) balls
        shuffle_count = min(len(self.pipe), 15)
        section = self.pipe[:shuffle_count]
        random.shuffle(section)
        self.pipe[:shuffle_count] = section

        # Invalidate bot pipe memory (pipe order changed)
        for p in self.players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            if rb_p.is_bot:
                rb_p.bot_pipe_memory = 0

        self.broadcast_l("rb-reshuffled")

        # Apply penalty
        if self.options.reshuffle_penalty > 0:
            rb_player.score -= self.options.reshuffle_penalty
            self.broadcast_l(
                "rb-reshuffle-penalty",
                player=player.name,
                points=self.options.reshuffle_penalty,
            )

        rb_player.has_reshuffled = True
        rb_player.reshuffle_uses += 1

        # Jolt bot
        BotHelper.jolt_bot(player, ticks=random.randint(8, 12))  # nosec B311

        # Rebuild menus to reflect updated remaining count
        self.rebuild_all_menus()

    def _action_view_pipe(self, player: Player, action_id: str) -> None:
        """View the pipe contents (private to the requesting player)."""
        rb_player: RollingBallsPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        # Only count as a use if the pipe changed since last view
        if rb_player.last_viewed_pipe != self.pipe:
            rb_player.view_pipe_uses += 1
            rb_player.last_viewed_pipe = [b.copy() for b in self.pipe]

        locale = user.locale

        # Build pipe contents as a status box
        lines = [Localization.get(locale, "rb-view-pipe-header", count=len(self.pipe))]
        for i, ball in enumerate(self.pipe, 1):
            lines.append(
                Localization.get(
                    locale,
                    "rb-view-pipe-ball",
                    num=i,
                    description=ball["description"],
                    value=ball["value"],
                )
            )
        self.status_box(player, lines)

        # Rebuild menus to reflect updated remaining count
        self.rebuild_all_menus()

    # ==========================================================================
    # Score overrides (rolling balls tracks scores on players, not TeamManager)
    # ==========================================================================

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        parts = [f"{p.name}: {p.score}" for p in sorted_players]  # type: ignore
        user.speak(". ".join(parts) + ".")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        lines = [
            f"{p.name}: {p.score} points"  # type: ignore
            for p in sorted_players
        ]
        self.status_box(player, lines)

    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Reset player state
        for p in active_players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            rb_p.score = 0
            rb_p.has_reshuffled = False
            rb_p.view_pipe_uses = 0
            rb_p.reshuffle_uses = 0
            rb_p.last_viewed_pipe = None
            rb_p.bot_pipe_memory = 0

        # Fill pipe
        total_balls = self.fill_pipe()

        # Play music
        self.play_music("game_pig/mus.ogg")

        # Announce
        self.broadcast_l("rb-pipe-filled", count=total_balls)

        # Pipe filling sounds
        delay = 0
        for _ in range(10):
            self.schedule_sound(
                f"game_uno/intercept{random.randint(1, 4)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 3  # ~150ms at 20 ticks/sec

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Refresh turn order
        self.set_turn_players(self.get_active_players())

        self.play_sound("game_pig/roundstart.ogg", volume=60)
        self.broadcast_l("game-round-start", round=self.round)
        self.broadcast_l("rb-balls-remaining", count=len(self.pipe))

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            return

        rb_player: RollingBallsPlayer = player  # type: ignore
        rb_player.has_reshuffled = False

        # If remaining balls are below minimum take, auto-take them
        if 0 < len(self.pipe) < self.options.min_take:
            self._take_balls(player, len(self.pipe))
            return

        # Announce turn
        self.play_sound("game_3cardpoker/turn.ogg", volume=70)
        self.announce_turn()

        # Set up bot if needed
        if player.is_bot:
            BotHelper.set_target(player, 0)

        # Rebuild menus, resetting focus to first item for current player
        # (view_pipe shifts position when turn actions appear/disappear)
        for p in self.players:
            if p == player:
                self.rebuild_player_menu(p, position=1)
            else:
                self.rebuild_player_menu(p)

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI, ball reveals, and scheduled sounds."""
        super().on_tick()

        if not self.game_active:
            return

        # Process ball reveal queue (blocks bot actions while active)
        if self._ball_reveal_player_id:
            if self.sound_scheduler_tick >= self._ball_reveal_tick:
                if self._ball_reveal_queue:
                    self._reveal_next_ball()
                else:
                    self._finish_ball_reveals()
            return

        BotHelper.on_tick(self)

    def _get_bot_perceived_pipe(self, player: RollingBallsPlayer) -> list[dict]:
        """Get the pipe as the bot perceives it, with limited information.

        Bots auto-use view pipe charges and remember up to 6 balls.
        Beyond their memory, ball values are randomized.
        """
        # Auto-use a view if available and the pipe has changed
        if (
            player.view_pipe_uses < self.options.view_pipe_limit
            and player.last_viewed_pipe != self.pipe
        ):
            player.view_pipe_uses += 1
            player.last_viewed_pipe = [b.copy() for b in self.pipe]
            player.bot_pipe_memory = min(6, len(self.pipe))
            self.rebuild_all_menus()

        perceived = []
        for i, ball in enumerate(self.pipe):
            if i < player.bot_pipe_memory:
                perceived.append(ball)
            else:
                perceived.append(
                    {
                        **ball,
                        "value": random.randint(-5, 5),  # nosec B311
                    }
                )
        return perceived

    def bot_think(self, player: RollingBallsPlayer) -> str | None:
        """Bot AI decision making."""
        perceived_pipe = self._get_bot_perceived_pipe(player)

        # Check if we should reshuffle
        if (
            not player.has_reshuffled
            and player.reshuffle_uses < self.options.reshuffle_limit
            and len(self.pipe) >= 6
        ):
            # Count negative balls in the first 3 positions
            negative_count = sum(
                1 for i in range(min(3, len(self.pipe))) if perceived_pipe[i]["value"] <= -2
            )
            if negative_count >= 2:
                return "reshuffle"

        # Decide how many balls to take
        min_take = self.options.min_take
        max_take = min(self.options.max_take, len(self.pipe))
        if max_take < min_take:
            return None

        best_take = min_take
        best_value = -999
        for test_take in range(min_take, max_take + 1):
            cumulative = sum(perceived_pipe[i]["value"] for i in range(test_take))
            if cumulative > best_value or (
                cumulative == best_value and random.randint(0, 1) == 0  # nosec B311
            ):
                best_value = cumulative
                best_take = test_take

        return f"take_{best_take}"

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check if pipe is empty
        if not self.pipe:
            self._announce_winner()
            return

        # Check if round is over
        if self.turn_index >= len(self.turn_players) - 1:
            self._on_round_end()
        else:
            self.advance_turn(announce=False)
            self._start_turn()

    def _on_round_end(self) -> None:
        """Handle end of a round."""
        if not self.pipe:
            self._announce_winner()
        else:
            self._start_round()

    def _announce_winner(self) -> None:
        """Announce the winner and finish the game."""
        self.broadcast_l("rb-pipe-empty")

        active_players = self.get_active_players()

        # Find highest score
        best_score = max(
            (p.score for p in active_players),  # type: ignore
            default=0,
        )
        winners = [
            p
            for p in active_players
            if p.score == best_score  # type: ignore
        ]

        if len(winners) == 1:
            winner = winners[0]
            rb_winner: RollingBallsPlayer = winner  # type: ignore
            self.play_sound("game_rollingballs/wingame.ogg")
            self.broadcast_personal_l(
                winner,
                "rb-you-win",
                "rb-winner",
                score=rb_winner.score,
            )
        else:
            # Tie
            names = [w.name for w in winners]
            for p in self.players:
                user = self.get_user(p)
                if user:
                    names_str = Localization.format_list_and(user.locale, names)
                    user.speak_l("rb-tie", players=names_str, score=best_score, buffer="table")

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result."""
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )

        final_scores = {}
        for p in sorted_players:
            rb_p: RollingBallsPlayer = p  # type: ignore
            final_scores[p.name] = rb_p.score

        winner = sorted_players[0] if sorted_players else None
        rb_winner: RollingBallsPlayer = winner  # type: ignore

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                    is_virtual_bot=getattr(p, "is_virtual_bot", False),
                )
                for p in self.get_active_players()
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": rb_winner.score if rb_winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        lines = [Localization.get(locale, "game-final-scores-header")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            lines.append(f"{i}. {name}: {score}")

        return lines

    def end_turn(self, jolt_min: int = 20, jolt_max: int = 30) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))  # nosec B311
        self._on_turn_end()
