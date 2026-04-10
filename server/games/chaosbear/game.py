"""
Chaos Bear - A chase game where players run from a bear.

Players roll dice to move forward. When on multiples of 5, they can draw
cards for special effects. The bear chases from behind, catching players
who fall too far back. Last player standing (or furthest distance) wins!
"""

import random
from dataclasses import dataclass, field
from datetime import datetime

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from ...messages.localization import Localization


@dataclass
class ChaosBearPlayer(Player):
    """Player state for Chaos Bear."""

    position: int = 0
    alive: bool = True


@dataclass
@register_game
class ChaosBearGame(Game):
    """
    Chaos Bear - run from the bear!

    Players start 30 squares ahead of the bear and must keep moving forward.
    Roll dice to advance, draw cards on multiples of 5 for bonuses/penalties.
    If the bear catches you, you're out! Last player alive wins.
    """

    players: list[ChaosBearPlayer] = field(default_factory=list)

    # Game state
    bear_position: int = 0
    bear_energy: int = 1
    round_number: int = 0
    players_moved_this_round: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Chaos Bear"

    @classmethod
    def get_type(cls) -> str:
        return "chaosbear"

    @classmethod
    def get_category(cls) -> str:
        return "category-rb-play-center"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ChaosBearPlayer:
        """Create a new player."""
        return ChaosBearPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: ChaosBearPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="roll_dice",
                label=Localization.get(locale, "chaosbear-roll-dice"),
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
            )
        )

        action_set.add(
            Action(
                id="draw_card",
                label=Localization.get(locale, "chaosbear-draw-card"),
                handler="_action_draw_card",
                is_enabled="_is_draw_card_enabled",
                is_hidden="_is_draw_card_hidden",
            )
        )

        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "chaosbear-check-status"),
                handler="_action_check_status",
                is_enabled="_is_check_status_enabled",
                is_hidden="_is_check_status_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        self.define_keybind(
            "r",
            "Roll dice",
            ["roll_dice"],
            state=KeybindState.ACTIVE,
        )

        self.define_keybind(
            "d",
            "Draw card",
            ["draw_card"],
            state=KeybindState.ACTIVE,
        )

        self.define_keybind(
            "c",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        """Check if roll dice action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.is_animating:
            return "action-game-in-progress"
        if self.current_player != player:
            return "action-not-your-turn"
        cb_player: ChaosBearPlayer = player  # type: ignore
        if not cb_player.alive:
            return "chaosbear-you-are-caught"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        """Check if roll dice is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        cb_player: ChaosBearPlayer = player  # type: ignore
        if not cb_player.alive:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_draw_card_enabled(self, player: Player) -> str | None:
        """Check if draw card action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.is_animating:
            return "action-game-in-progress"
        if self.current_player != player:
            return "action-not-your-turn"
        cb_player: ChaosBearPlayer = player  # type: ignore
        if not cb_player.alive:
            return "chaosbear-you-are-caught"
        can_draw = cb_player.position % 5 == 0 and cb_player.position > 0
        if not can_draw:
            return "chaosbear-not-on-multiple"
        return None

    def _is_draw_card_hidden(self, player: Player) -> Visibility:
        """Check if draw card is hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        cb_player: ChaosBearPlayer = player  # type: ignore
        if not cb_player.alive:
            return Visibility.HIDDEN
        can_draw = cb_player.position % 5 == 0 and cb_player.position > 0
        if not can_draw:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_status_enabled(self, player: Player) -> str | None:
        """Check if check status action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        """Check status is visible to all during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # ==========================================================================
    # Event Queue
    # ==========================================================================

    def on_game_event(self, event_type: str, data: dict) -> None:
        """Handle a scheduled game event."""
        player_id = data.get("player_id")
        player = self.get_player_by_id(player_id) if player_id else None

        if event_type == "player_roll":
            self.broadcast_l("chaosbear-roll", player=data["name"], roll=data["roll"])

        elif event_type == "player_position":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-position",
                    player=player.name,
                    position=player.position,
                )

        elif event_type == "end_player_turn":
            self._handle_end_player_turn()

        elif event_type == "bear_roll":
            self.broadcast_l(
                "chaosbear-bear-roll",
                roll=data["die"],
                energy=data["energy"],
                total=data["total"],
            )

        elif event_type == "bear_energy_up":
            self.bear_energy = data["new_energy"]
            self.broadcast_l("chaosbear-bear-energy-up", energy=self.bear_energy)

        elif event_type == "bear_position":
            self.bear_position = data["new_position"]
            self.broadcast_l("chaosbear-bear-position", position=self.bear_position)

        elif event_type == "player_caught":
            if player:
                player.alive = False
                self.broadcast_l("chaosbear-player-caught", player=player.name)

        elif event_type == "bear_feast":
            self.bear_energy = data["new_energy"]
            if data["energy_changed"]:
                self.broadcast_l("chaosbear-bear-feast")

        elif event_type == "end_bear_turn":
            self._handle_end_bear_turn()

        elif event_type == "draw_announce":
            self.broadcast_l("chaosbear-draws-card", player=data["name"])

        elif event_type == "card_random_gift_announce":
            self.broadcast_l("chaosbear-card-random-gift")

        elif event_type == "card_effect":
            self._apply_card_effect(data)

    def _apply_card_effect(self, data: dict) -> None:
        """Apply a pre-calculated card effect."""
        effect = data["effect"]
        player = self.get_player_by_id(data["player_id"]) if data.get("player_id") else None

        if effect == "impulsion":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-card-impulsion",
                    player=player.name,
                    position=player.position,
                )

        elif effect == "super_impulsion":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-card-super-impulsion",
                    player=player.name,
                    position=player.position,
                )

        elif effect == "tiredness":
            self.bear_energy = data["new_energy"]
            self.broadcast_l("chaosbear-card-tiredness", energy=self.bear_energy)

        elif effect == "hunger":
            self.bear_energy = data["new_energy"]
            self.broadcast_l("chaosbear-card-hunger", energy=self.bear_energy)

        elif effect == "backward":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-card-backward",
                    player=player.name,
                    position=player.position,
                )

        elif effect == "gift_back":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-gift-back",
                    player=player.name,
                    position=player.position,
                )

        elif effect == "gift_forward":
            if player:
                player.position = data["new_position"]
                self.broadcast_l(
                    "chaosbear-gift-forward",
                    player=player.name,
                    position=player.position,
                )

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round_number = 1
        self.players_moved_this_round = 0

        # Set starting positions (fixed at 30 like v10)
        self.bear_position = 0
        self.bear_energy = 1
        for player in self.get_active_players():
            player.position = 30
            player.alive = True

        # Initialize turn order
        alive_players = self.get_active_players()
        self.set_turn_players(alive_players)

        # Play music and ambience
        self.play_music("game_chaosbear/music.ogg")
        self.play_ambience("game_chaosbear/amloop.ogg")
        self.play_sound("game_3cardpoker/roundstart.ogg")

        # Announce game start (3 messages like v10)
        self.broadcast_l("chaosbear-intro-1")
        self.broadcast_l("chaosbear-intro-2")
        self.broadcast_l("chaosbear-intro-3")

        # Rebuild menus and announce first turn
        self.rebuild_all_menus()

        self._announce_turn()

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(30, 60))  # nosec B311

    def _announce_turn(self) -> None:
        """Announce whose turn it is."""
        player = self.current_player
        if not player:
            return

        # Play begin turn sound for human players only
        if not player.is_bot:
            user = self.get_user(player)
            if user:
                user.play_sound("game_squares/begin turn.ogg", volume=50)

        self.broadcast_l("chaosbear-turn", player=player.name, position=player.position)

    def on_tick(self) -> None:
        """Called every game tick."""
        super().on_tick()
        self.process_scheduled_events()

        if self.status != "playing":
            return

        # Process bot thinking
        BotHelper.on_tick(self)

    def bot_think(self, player: ChaosBearPlayer) -> str | None:
        """Determine what action a bot should take."""
        if not player.alive:
            return None

        # AI: draw card if on multiple of 5, otherwise roll
        if player.position % 5 == 0 and player.position > 0:
            return "draw_card"

        # Otherwise roll the dice
        return "roll_dice"

    def _start_next_turn(self, previous_player: "ChaosPlayer | None" = None) -> None:
        """Start the next player's turn with menu rebuild and bot jolt.

        Args:
            previous_player: The player whose turn just ended. Only that player
                and the new current player need menu rebuilds (their turn actions
                changed). Pass None to rebuild all players (e.g. on round start).
        """
        self.is_animating = False
        self._announce_turn()

        current = self.current_player
        if previous_player is not None:
            # Only rebuild the two affected players:
            # - previous player: turn actions disappeared
            # - current player: turn actions appeared
            self.rebuild_player_menu(current, position=1)
            if previous_player != current:
                self.rebuild_player_menu(previous_player)
        else:
            # Round start or first turn — rebuild everyone
            for p in self.players:
                if p == current:
                    self.rebuild_player_menu(p, position=1)
                else:
                    self.rebuild_player_menu(p)

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(30, 60))  # nosec B311

    def _handle_end_player_turn(self) -> None:
        """Handle end of a player's turn (called from event queue)."""
        self.players_moved_this_round += 1

        alive_players = [p for p in self.players if p.alive and not p.is_spectator]

        # Check if all alive players have moved this round
        if self.players_moved_this_round >= len(alive_players):
            # Bear's turn — queue bear events
            self._start_bear_turn()
            return

        # Advance to next player within the round (no advance_turn — it
        # rebuilds menus, and _start_next_turn already handles that)
        previous = self.current_player
        self.turn_index = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
        self._start_next_turn(previous_player=previous)

    def _handle_end_bear_turn(self) -> None:
        """Handle end of the bear's turn (called from event queue)."""
        self.players_moved_this_round = 0
        self.round_number += 1

        # Check for winner after bear moves
        if self._check_for_winner():
            self.is_animating = False
            return

        # Rebuild turn order with alive players (resets turn_index to 0)
        alive_players = [p for p in self.players if p.alive and not p.is_spectator]
        if alive_players:
            self.set_turn_players(alive_players)

        # Start first player's turn (no advance_turn — index is already 0)
        self._start_next_turn()

    def _start_bear_turn(self) -> None:
        """Pre-calculate bear turn outcomes and queue events."""
        # Check if any players are close — play warning
        for player in self.players:
            if player.alive and not player.is_spectator:
                if player.position - self.bear_position <= 10:
                    self.play_sound(
                        f"game_chaosbear/bearwarn{random.randint(1, 2)}.ogg"  # nosec B311
                    )
                    break

        # Bear dice roll sounds
        self.schedule_sound("game_chaosbear/beardice0.ogg", delay_ticks=10)
        self.schedule_sound(
            f"game_chaosbear/beardice{random.randint(1, 3)}.ogg",
            delay_ticks=18,  # nosec B311
        )

        # Pre-calculate outcomes
        bear_die = random.randint(1, 3)  # nosec B311
        original_energy = self.bear_energy
        move_distance = bear_die + original_energy
        energy_gained = bear_die == 3

        if energy_gained:
            new_energy = original_energy + 1
            # Don't count the extra energy toward movement this turn
            move_distance -= 1
        else:
            new_energy = original_energy

        new_bear_position = self.bear_position + move_distance

        # Step sounds use new energy for bonus calculation
        bonus_steps = new_energy // 3
        num_steps = bear_die + bonus_steps

        # Pre-calculate catches
        caught_ids = []
        for p in self.players:
            if p.alive and not p.is_spectator:
                if new_bear_position >= p.position:
                    caught_ids.append(p.id)

        # Pre-calculate feast
        kills = len(caught_ids)
        energy_after_feast = new_energy
        if kills > 0:
            energy_after_feast = max(1, new_energy - 3)

        # --- Schedule events with relative delays ---
        delay = 22

        # Bear roll announcement
        self.schedule_event(
            "bear_roll",
            {
                "die": bear_die,
                "energy": original_energy,
                "total": bear_die + original_energy,
            },
            delay_ticks=delay,
        )
        delay += 6

        # Energy up (if rolled 3)
        if energy_gained:
            self.schedule_sound(
                f"game_chaosbear/energyup{random.randint(1, 2)}.ogg",
                delay_ticks=25,  # nosec B311
            )
            self.schedule_event(
                "bear_energy_up",
                {
                    "new_energy": new_energy,
                },
                delay_ticks=delay,
            )
            delay += 6

        # Bear step sounds
        step_base = 35
        for i in range(num_steps):
            self.schedule_sound(
                f"game_chaosbear/bearstep{random.randint(1, 5)}.ogg",  # nosec B311
                delay_ticks=step_base + i * 4,
            )

        last_step_delay = step_base + max(0, num_steps - 1) * 4
        delay = max(delay, last_step_delay + 4)

        # Bear position announcement
        self.schedule_event(
            "bear_position",
            {
                "new_position": new_bear_position,
            },
            delay_ticks=delay,
        )
        delay += 6

        # Caught players
        if caught_ids:
            for pid in caught_ids:
                self.schedule_sound(
                    f"game_chaosbear/playerdie{random.randint(1, 2)}.ogg",  # nosec B311
                    delay_ticks=delay,
                )
                self.schedule_event(
                    "player_caught",
                    {
                        "player_id": pid,
                    },
                    delay_ticks=delay + 2,
                )
                self.schedule_sound(
                    f"game_chaosbear/energydown{random.randint(1, 3)}.ogg",  # nosec B311
                    delay_ticks=delay + 40,
                )
                delay += 50

            # Bear feast
            self.schedule_event(
                "bear_feast",
                {
                    "new_energy": energy_after_feast,
                    "energy_changed": energy_after_feast != new_energy,
                },
                delay_ticks=delay,
            )
            delay += 8

        # End bear turn
        self.schedule_event("end_bear_turn", {}, delay_ticks=delay + 5)

    def _check_for_winner(self) -> bool:
        """Check if there's a winner."""
        alive_players = [p for p in self.players if p.alive and not p.is_spectator]

        if len(alive_players) == 1:
            # One player left - they win!
            winner = alive_players[0]
            self._end_game(winner)
            return True
        elif len(alive_players) == 0:
            # Everyone caught - furthest distance wins
            all_players = [p for p in self.players if not p.is_spectator]
            max_pos = max(p.position for p in all_players)
            winners = [p for p in all_players if p.position == max_pos]
            if len(winners) > 1:
                self._end_game_tie(max_pos)
            else:
                self._end_game(winners[0])
            return True

        return False

    def _end_game(self, winner: ChaosBearPlayer) -> None:
        """End the game with a winner."""
        self._winner_name = winner.name
        self._winner_position = winner.position
        self._is_tie = False

        self.schedule_sound("game_pig/win.ogg", delay_ticks=5)
        self.broadcast_l("chaosbear-winner", player=winner.name, position=winner.position)

        self.finish_game()

    def _end_game_tie(self, position: int) -> None:
        """End the game with a tie."""
        self._winner_name = None
        self._winner_position = position
        self._is_tie = True

        self.broadcast_l("chaosbear-tie", position=position)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with ChaosBear-specific data."""
        all_players = [
            p for p in self.players if isinstance(p, ChaosBearPlayer) and not p.is_spectator
        ]
        sorted_players = sorted(all_players, key=lambda p: p.position, reverse=True)

        # Build final positions
        final_positions = {}
        alive_status = {}
        for p in sorted_players:
            final_positions[p.name] = p.position
            alive_status[p.name] = p.alive

        winner_name = getattr(self, "_winner_name", None)
        winner_position = getattr(self, "_winner_position", 0)
        is_tie = getattr(self, "_is_tie", False)

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
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner_name,
                "winner_position": winner_position,
                "is_tie": is_tie,
                "final_positions": final_positions,
                "alive_status": alive_status,
                "bear_position": self.bear_position,
                "rounds_played": self.round_number,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for ChaosBear game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_positions = result.custom_data.get("final_positions", {})
        alive_status = result.custom_data.get("alive_status", {})

        for i, (name, position) in enumerate(final_positions.items(), 1):
            status = "" if alive_status.get(name, True) else " (caught)"
            lines.append(f"{i}. {name}: {position} squares{status}")

        return lines

    # ==========================================================================
    # Actions
    # ==========================================================================

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        """Roll dice to move forward."""
        if not isinstance(player, ChaosBearPlayer):
            return
        if self.current_player != player or not player.alive:
            return

        self.is_animating = True

        # Roll sound (immediate)
        self.play_sound("game_pig/roll.ogg")

        # Pre-calculate outcome
        roll = random.randint(1, 6)  # nosec B311
        new_position = player.position + roll

        # Announce roll result (after roll sound)
        self.schedule_event(
            "player_roll",
            {
                "name": player.name,
                "roll": roll,
            },
            delay_ticks=8,
        )

        # Schedule player step sounds
        for i in range(roll):
            self.schedule_sound(
                f"game_chaosbear/playerstep{random.randint(1, 5)}.ogg",  # nosec B311
                delay_ticks=6 + i * 4,
            )

        # Update position after steps finish
        position_delay = 6 + (roll - 1) * 4 + 4
        self.schedule_event(
            "player_position",
            {
                "player_id": player.id,
                "new_position": new_position,
            },
            delay_ticks=position_delay,
        )

        # End turn after position announcement
        self.schedule_event("end_player_turn", {}, delay_ticks=position_delay + 6)

    def _action_draw_card(self, player: Player, action_id: str) -> None:
        """Draw a card for a special effect."""
        if not isinstance(player, ChaosBearPlayer):
            return
        if self.current_player != player or not player.alive:
            return
        if player.position % 5 != 0 or player.position == 0:
            return

        self.is_animating = True

        # Draw sound (immediate)
        self.play_sound(f"game_chaosbear/draw{random.randint(1, 2)}.ogg")  # nosec B311

        # Announce draws card
        delay = 6
        self.schedule_event(
            "draw_announce",
            {
                "name": player.name,
            },
            delay_ticks=delay,
        )
        delay += 6

        # Pre-calculate card and effects
        card = random.randint(0, 5)  # nosec B311

        if card == 0:
            # Impulsion - forward 3
            new_pos = player.position + 3
            self.schedule_sound(
                f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 6
            self.schedule_event(
                "card_effect",
                {
                    "effect": "impulsion",
                    "player_id": player.id,
                    "new_position": new_pos,
                },
                delay_ticks=delay,
            )

        elif card == 1:
            # Super impulsion - forward 5
            new_pos = player.position + 5
            self.schedule_sound(
                f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 6
            self.schedule_event(
                "card_effect",
                {
                    "effect": "super_impulsion",
                    "player_id": player.id,
                    "new_position": new_pos,
                },
                delay_ticks=delay,
            )

        elif card == 2:
            # Tiredness - bear energy -1
            new_energy = max(1, self.bear_energy - 1)
            self.schedule_sound(
                f"game_chaosbear/tiredness{random.randint(1, 2)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 6
            self.schedule_event(
                "card_effect",
                {
                    "effect": "tiredness",
                    "new_energy": new_energy,
                },
                delay_ticks=delay,
            )
            self.schedule_sound(
                f"game_chaosbear/energydown{random.randint(1, 3)}.ogg",  # nosec B311
                delay_ticks=delay + 8,
            )

        elif card == 3:
            # Hunger - bear energy +1
            new_energy = self.bear_energy + 1
            self.schedule_sound(
                f"game_chaosbear/hunger{random.randint(1, 2)}.ogg",  # nosec B311
                delay_ticks=delay,
            )
            delay += 6
            self.schedule_event(
                "card_effect",
                {
                    "effect": "hunger",
                    "new_energy": new_energy,
                },
                delay_ticks=delay,
            )
            self.schedule_sound(
                f"game_chaosbear/energyup{random.randint(1, 2)}.ogg",  # nosec B311
                delay_ticks=delay + 8,
            )

        elif card == 4:
            # Backward push - back 3
            new_pos = max(0, player.position - 3)
            self.schedule_sound(
                "game_chaosbear/backpush.ogg",
                delay_ticks=delay,
            )
            delay += 6
            self.schedule_event(
                "card_effect",
                {
                    "effect": "backward",
                    "player_id": player.id,
                    "new_position": new_pos,
                },
                delay_ticks=delay,
            )

        else:
            # Random gift - forward/back 1-6
            amount = random.randint(1, 6)  # nosec B311
            is_back = random.random() < 0.5  # nosec B311

            self.schedule_event("card_random_gift_announce", {}, delay_ticks=delay)
            delay += 4

            if is_back:
                new_pos = max(0, player.position - amount)
                self.schedule_sound(
                    "game_chaosbear/backpush.ogg",
                    delay_ticks=delay,
                )
                delay += 6
                self.schedule_event(
                    "card_effect",
                    {
                        "effect": "gift_back",
                        "player_id": player.id,
                        "new_position": new_pos,
                    },
                    delay_ticks=delay,
                )
            else:
                new_pos = player.position + amount
                self.schedule_sound(
                    f"game_chaosbear/impulsion{random.randint(1, 2)}.ogg",  # nosec B311
                    delay_ticks=delay,
                )
                delay += 6
                self.schedule_event(
                    "card_effect",
                    {
                        "effect": "gift_forward",
                        "player_id": player.id,
                        "new_position": new_pos,
                    },
                    delay_ticks=delay,
                )

        # End player turn after card effect
        delay += 6
        self.schedule_event("end_player_turn", {}, delay_ticks=delay)

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Check the current game status."""
        if not isinstance(player, ChaosBearPlayer):
            return

        user = self.get_user(player)
        if not user:
            return

        # Show all player positions first
        for p in self.players:
            if not p.is_spectator:
                if p.alive:
                    user.speak_l(
                        "chaosbear-status-player-alive",
                        player=p.name,
                        position=p.position,
                    )
                else:
                    user.speak_l(
                        "chaosbear-status-player-caught",
                        player=p.name,
                        position=p.position,
                    )

        # Show bear status
        user.speak_l(
            "chaosbear-status-bear",
            position=self.bear_position,
            energy=self.bear_energy,
        )

    # ==========================================================================
    # Scoring
    # ==========================================================================

    def get_scores(self) -> list[tuple[str, int]]:
        """Get player scores (distance traveled)."""
        scores = []
        for player in self.players:
            if not player.is_spectator:
                scores.append((player.name, player.position))
        return sorted(scores, key=lambda x: x[1], reverse=True)

    def format_standings(self) -> str:
        """Format the final standings."""
        lines = []
        for i, (name, distance) in enumerate(self.get_scores(), 1):
            player = self.get_player_by_name(name)
            status = "caught" if (player and not player.alive) else "survived"
            lines.append(f"{i}. {name}: {distance} squares ({status})")
        return "\n".join(lines)
