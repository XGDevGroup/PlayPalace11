"""
Pirates of the Lost Seas - Main Game Class.

A complex RPG adventure with sailing, combat, and leveling.
Players sail across four oceans, collecting gems and battling other pirates.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import GameOptions, FloatOption, MenuOption, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState

from .player import PiratesPlayer
from . import gems
from . import combat
from . import skills
from . import bot as bot_ai

# Ocean names for random selection
OCEAN_NAMES = [
    "Rory's Ocean",
    "Developer's Deep",
    "Programmer's Paradise Sea",
    "The Palace Waters",
    "Silva's Strait",
    "Kai's Current",
    "Gamer's Gulf",
    "Server Room Sea",
    "Battle Bay",
    "Code Compilation Channel",
]


@dataclass
class PiratesOptions(GameOptions):
    """Game options for Pirates of the Lost Seas."""

    combat_xp_multiplier: float = option_field(
        FloatOption(
            default=1.0,
            min_val=0.1,
            max_val=3.0,
            decimal_places=2,
            value_key="combat_multiplier",
            label="pirates-set-combat-xp-multiplier",
            prompt="pirates-enter-combat-xp-multiplier",
            change_msg="pirates-option-changed-combat-xp",
        )
    )

    find_gem_xp_multiplier: float = option_field(
        FloatOption(
            default=1.0,
            min_val=0.1,
            max_val=3.0,
            decimal_places=2,
            value_key="find_gem_multiplier",
            label="pirates-set-find-gem-xp-multiplier",
            prompt="pirates-enter-find-gem-xp-multiplier",
            change_msg="pirates-option-changed-find-gem-xp",
        )
    )

    gem_stealing: str = option_field(
        MenuOption(
            default="with_roll_bonus",
            value_key="mode",
            choices=["with_roll_bonus", "no_roll_bonus", "disabled"],
            choice_labels={
                "with_roll_bonus": "pirates-stealing-with-bonus",
                "no_roll_bonus": "pirates-stealing-no-bonus",
                "disabled": "pirates-stealing-disabled",
            },
            label="pirates-set-gem-stealing",
            prompt="pirates-select-gem-stealing",
            change_msg="pirates-option-changed-stealing",
            description="pirates-desc-gem-stealing",
        )
    )


@dataclass
@register_game
class PiratesGame(Game):
    """
    Pirates of the Lost Seas - A complex RPG adventure.

    Features:
    - 40-tile map across 4 oceans
    - 18 gems to collect
    - Skill system that unlocks as players level up
    - Combat with cannonballs, buffs, and gem stealing
    - Golden Moon event every 3rd round (3x XP)
    """

    players: list[PiratesPlayer] = field(default_factory=list)
    options: PiratesOptions = field(default_factory=PiratesOptions)

    # Game state
    selected_oceans: list[str] = field(default_factory=list)
    charted_tiles: dict[int, bool] = field(default_factory=dict)
    gem_positions: dict[int, int] = field(default_factory=dict)
    gems_collected: int = 0
    total_gems: int = 18
    golden_moon_active: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "Pirates of the Lost Seas"

    @classmethod
    def get_type(cls) -> str:
        return "pirates"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    def __post_init__(self):
        """Initialize non-serialized state."""
        super().__post_init__()

    def rebuild_runtime_state(self) -> None:
        """Rebuild runtime state after deserialization."""
        super().rebuild_runtime_state()
        # Skills are now on each player, no need to rebuild here

        # Fix dict keys that became strings after JSON deserialization
        if self.gem_positions:
            self.gem_positions = {int(k): v for k, v in self.gem_positions.items()}
        if self.charted_tiles:
            self.charted_tiles = {int(k): v for k, v in self.charted_tiles.items()}

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> PiratesPlayer:
        """Create a new Pirates player."""
        # Skills are initialized in PiratesPlayer.__post_init__
        return PiratesPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: Player) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Movement actions
        action_set.add(
            Action(
                id="move_left",
                label=Localization.get(locale, "pirates-move-left"),
                handler="_action_move_left",
                is_enabled="_is_move_enabled",
                is_hidden="_is_move_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_right",
                label=Localization.get(locale, "pirates-move-right"),
                handler="_action_move_right",
                is_enabled="_is_move_enabled",
                is_hidden="_is_move_hidden",
                show_in_actions_menu=False,
            )
        )

        # Level 15+ movements
        action_set.add(
            Action(
                id="move_2_left",
                label=Localization.get(locale, "pirates-move-2-left"),
                handler="_action_move_2_left",
                is_enabled="_is_move_2_enabled",
                is_hidden="_is_move_2_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_2_right",
                label=Localization.get(locale, "pirates-move-2-right"),
                handler="_action_move_2_right",
                is_enabled="_is_move_2_enabled",
                is_hidden="_is_move_2_hidden",
                show_in_actions_menu=False,
            )
        )

        # Level 150+ movements
        action_set.add(
            Action(
                id="move_3_left",
                label=Localization.get(locale, "pirates-move-3-left"),
                handler="_action_move_3_left",
                is_enabled="_is_move_3_enabled",
                is_hidden="_is_move_3_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="move_3_right",
                label=Localization.get(locale, "pirates-move-3-right"),
                handler="_action_move_3_right",
                is_enabled="_is_move_3_enabled",
                is_hidden="_is_move_3_hidden",
                show_in_actions_menu=False,
            )
        )

        """# Cannonball attack (always available)
        action_set.add(
            Action(
                id="cannonball",
                label=Localization.get(locale, "pirates-cannonball"),
                handler="_action_cannonball",
                is_enabled="_is_cannonball_enabled",
                is_hidden="_is_cannonball_hidden",
            )
        )"""

        # Skill menu
        action_set.add(
            Action(
                id="use_skill",
                label=Localization.get(locale, "pirates-use-skill"),
                handler="_action_use_skill",
                is_enabled="_is_skill_enabled",
                is_hidden="_is_skill_hidden",
                input_request=MenuInput(
                    options="_get_skill_options",
                    prompt="pirates-select-skill",
                ),
            )
        )

        # Status actions (keybind only)
        action_set.add(
            Action(
                id="check_moon",
                label=Localization.get(locale, "pirates-check-moon"),
                handler="_action_check_moon",
                is_enabled="_is_moon_check_enabled",
                is_hidden="_is_moon_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_position",
                label=Localization.get(locale, "pirates-check-position"),
                handler="_action_check_position",
                is_enabled="_is_status_enabled",
                is_hidden="_is_status_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_status",
                label=Localization.get(locale, "pirates-check-status"),
                handler="_action_check_status",
                is_enabled="_is_status_enabled",
                is_hidden="_is_status_hidden",
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        """Create the standard action set and add detailed status."""
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action = Action(
            id="check_status_detailed",
            label=Localization.get(locale, "pirates-check-status-detailed"),
            handler="_action_check_status_detailed",
            is_enabled="_is_status_enabled",
            is_hidden="_is_always_hidden",
        )
        action_set.add(action)
        if action.id in action_set._order:
            action_set._order.remove(action.id)
        action_set._order.insert(0, action.id)
        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        self.define_keybind(
            "p",
            "Check position",
            ["check_position"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "m",
            "Check moon brightness",
            ["check_moon"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "s",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "shift+s",
            "Detailed status",
            ["check_status_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "k",
            "Use skill",
            ["use_skill"],
            state=KeybindState.ACTIVE,
            include_spectators=False,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_move_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_move_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_2_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return "pirates-requires-level-15"
        return None

    def _is_move_2_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 15:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_move_3_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return "pirates-requires-level-150"
        return None

    def _is_move_3_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, PiratesPlayer) else None
        if not p or p.level < 150:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_cannonball_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_cannonball_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_skill_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_skill_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_skill_options(self, player: Player) -> list[str]:
        """Get available skills for the skill menu."""
        if not isinstance(player, PiratesPlayer):
            return []

        options = []
        for skill in skills.get_available_skills(player):
            options.append(skill.get_menu_label(player))
        return options

    def _is_status_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_status_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_moon_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if not self.golden_moon_active:
            return "pirates-no-golden-moon"
        return None

    def _is_moon_check_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if not self.golden_moon_active:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_always_hidden(self, player: Player) -> Visibility:
        """Always return hidden - for keybind-only actions."""
        return Visibility.HIDDEN

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        # Play music and ambience
        self.play_music("game_pirates/mus.ogg")
        self.play_ambience("game_pirates/amloop.ogg", intro="game_pirates/am_intro.ogg")

        self.broadcast_l("pirates-welcome")

        # Select 4 random oceans
        available = list(OCEAN_NAMES)
        random.shuffle(available)
        self.selected_oceans = available[:4]

        self.broadcast_l("pirates-oceans", oceans=", ".join(self.selected_oceans))

        # Initialize player positions randomly
        for player in self.get_active_players():
            player.position = random.randint(1, 40)  # nosec B311

        # Initialize charted tiles
        self.charted_tiles = {i: False for i in range(1, 41)}

        # Place gems
        self.gem_positions = gems.place_gems(40)
        self.total_gems = 18
        self.gems_collected = 0

        self.broadcast_l("pirates-gems-placed", total=self.total_gems)

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Rebuild menus and start first turn
        self.rebuild_all_menus()
        self._start_round()

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(10, 30))  # nosec B311

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Check for Golden Moon (every 3rd round)
        self.golden_moon_active = self.round % 3 == 0
        if self.golden_moon_active:
            self.play_sound("game_pirates/goldenmoon.ogg")
            self.broadcast_l("pirates-golden-moon")

        # Announce first turn
        self._announce_turn()

    def _announce_turn(self) -> None:
        """Announce whose turn it is."""
        player = self.current_player
        if not player or not isinstance(player, PiratesPlayer):
            return

        # Update skill timers
        skills.on_turn_start(self, player)

        # Play turn sound
        if not player.is_bot:
            user = self.get_user(player)
            if user and user.preferences.get_effective(
                "play_turn_sound", game_type=self.get_type()
            ):
                user.play_sound("game_pig/turn.ogg")

        self.broadcast_l("pirates-turn", player=player.name, position=player.position)

    def on_tick(self) -> None:
        """Called every game tick."""
        super().on_tick()

        if self.status != "playing":
            return

        # Process bot thinking
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Determine what action a bot should take."""
        if not isinstance(player, PiratesPlayer):
            return None
        return bot_ai.bot_think(self, player)

    def end_turn(self) -> None:
        """End the current player's turn."""
        current = self.current_player
        if not current or not isinstance(current, PiratesPlayer):
            return

        # Check for gem at current position
        self._check_gem_collection(current)

        # Check for win condition
        if self.total_gems <= 0:
            self._end_game()
            return

        # Advance to next player
        self.advance_turn(announce=False)

        # Check if we've completed a round
        if self.turn_index == 0:
            self._start_round()
        else:
            self._announce_turn()

        # Rebuild menus, resetting focus to first item for current player
        # (always-visible actions shift position when turn actions appear)
        current = self.current_player
        for p in self.players:
            if p == current:
                self.rebuild_player_menu(p, position=1)
            else:
                self.rebuild_player_menu(p)

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(80, 120))  # nosec B311

    def _check_gem_collection(self, player: PiratesPlayer) -> None:
        """Check if player is on a gem and collect it."""
        gem_type = self.gem_positions.get(player.position, -1)
        if gem_type == -1:
            return

        gem_value = gems.get_gem_value(gem_type)
        gem_name = gems.get_gem_name(gem_type)

        # Play collection sound
        sound_num = random.randint(1, 3)  # nosec B311
        self.play_sound(f"game_pirates/grabgem{sound_num}.ogg", volume=70)

        # Add gem to player
        player.add_gem(gem_type, gem_value)

        user = self.get_user(player)
        if user:
            user.speak_l(
                "pirates-gem-found-you",
                gem=gem_name,
                value=gem_value,
                buffer="table",
            )
        self.broadcast_l(
            "pirates-gem-found", player=player.name, gem=gem_name, value=gem_value, exclude=player
        )

        # Give XP for finding gem
        xp_gain = random.randint(150, 300)  # nosec B311
        moon_mult = 3.0 if self.golden_moon_active else 1.0
        player.leveling.give_xp(
            self, player.name, xp_gain, moon_mult, self.options.find_gem_xp_multiplier
        )

        # Mark gem as collected
        self.gem_positions[player.position] = -1
        self.total_gems -= 1
        self.gems_collected += 1
        self.charted_tiles[player.position] = True

    def _end_game(self) -> None:
        """End the game and determine winner."""
        self.broadcast_l("pirates-all-gems-collected")

        # Find winner by highest score
        active_players = self.get_active_players()
        if not active_players:
            return

        highest_score = max(p.score for p in active_players)
        winners = [p for p in active_players if p.score == highest_score]

        # If tie, pick random winner
        winner = random.choice(winners)  # nosec B311

        self.play_sound("game_pig/win.ogg", volume=80)
        self.broadcast_l("pirates-winner", player=winner.name, score=winner.score)

        # Store winner info for result
        self._winner_name = winner.name
        self._winner_score = winner.score

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Pirates-specific data."""
        active_players = self.get_active_players()
        sorted_players = sorted(active_players, key=lambda p: p.score, reverse=True)

        # Build final scores and levels
        final_scores = {}
        final_levels = {}
        final_gems = {}
        for p in sorted_players:
            final_scores[p.name] = p.score
            final_levels[p.name] = p.level
            final_gems[p.name] = gems.format_gem_list(p.gems)

        winner_name = getattr(self, "_winner_name", None)
        winner_score = getattr(self, "_winner_score", 0)

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
                "winner_score": winner_score,
                "final_scores": final_scores,
                "final_levels": final_levels,
                "final_gems": final_gems,
                "rounds_played": self.round,
                "gems_collected": self.gems_collected,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Pirates game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        final_levels = result.custom_data.get("final_levels", {})

        for i, (name, score) in enumerate(final_scores.items(), 1):
            level = final_levels.get(name, 0)
            lines.append(f"{i}. {name}: {score} points, level {level}")

        return lines

    # ==========================================================================
    # Movement Actions
    # ==========================================================================

    def _move_player(self, player: PiratesPlayer, amount: int) -> bool:
        """
        Move a player by the specified amount.

        Returns:
            True if move was successful, False if blocked by map edge
        """
        old_position = player.position

        if amount > 0:
            new_position = min(40, player.position + amount)
        else:
            new_position = max(1, player.position + amount)

        if new_position == old_position:
            # Blocked by map edge
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-map-edge", position=old_position, buffer="table")
            return False

        player.position = new_position

        # Play movement sound
        abs_amount = abs(amount)
        if abs_amount == 1:
            sound_num = random.randint(1, 3)  # nosec B311
            self.play_sound(f"game_pirates/move{sound_num}.ogg", volume=60)
        elif abs_amount == 2:
            sound_num = random.randint(1, 3)  # nosec B311
            self.play_sound(f"game_pirates/boat{sound_num}.ogg", volume=60)
        elif abs_amount == 3:
            sound_num = random.randint(1, 2)  # nosec B311
            self.play_sound(f"game_pirates/future{sound_num}.ogg", volume=60)

        direction = "right" if amount > 0 else "left"
        user = self.get_user(player)
        if user:
            if abs_amount == 1:
                user.speak_l(
                    "pirates-move-you",
                    direction=direction,
                    position=player.position,
                    buffer="table",
                )
            else:
                user.speak_l(
                    "pirates-move-you-tiles",
                    tiles=abs_amount,
                    direction=direction,
                    position=player.position,
                    buffer="table",
                )

        self.broadcast_l(
            "pirates-move",
            player=player.name,
            direction=direction,
            position=player.position,
            exclude=player,
        )

        self.charted_tiles[player.position] = True
        return True

    def _action_move_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -1):
            self.end_turn()

    def _action_move_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 1):
            self.end_turn()

    def _action_move_2_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -2):
            self.end_turn()

    def _action_move_2_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 2):
            self.end_turn()

    def _action_move_3_left(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, -3):
            self.end_turn()

    def _action_move_3_right(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PiratesPlayer):
            return
        if self._move_player(player, 3):
            self.end_turn()

    def _action_cannonball(self, player: Player, action_id: str) -> None:
        """Fire a cannonball at a target in range."""
        if not isinstance(player, PiratesPlayer):
            return
        if self.current_player != player:
            return

        result = self.handle_cannonball_attack(player)
        if result == "end_turn":
            self.end_turn()

    # ==========================================================================
    # Skill Actions
    # ==========================================================================

    def _action_use_skill(self, player: Player, skill_choice: str, action_id: str) -> None:
        """Handle skill menu selection."""
        if not isinstance(player, PiratesPlayer):
            return

        # Find the skill by matching the label
        for skill in skills.get_available_skills(player):
            if skill.get_menu_label(player) == skill_choice:
                can_use, reason = skill.can_perform(self, player)
                if can_use:
                    result = skill.do_action(self, player)
                    if result == "end_turn":
                        self.end_turn()
                else:
                    user = self.get_user(player)
                    if user and reason:
                        user.speak(reason, buffer="table")
                return

    # ==========================================================================
    # Status Actions
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show game status to the player."""
        if not isinstance(player, PiratesPlayer):
            return
        user = self.get_user(player)
        if not user:
            return

        lines = []
        for p in self.get_active_players():
            gem_str = gems.format_gem_list(p.gems)
            lines.append(f"{p.name}: Level {p.level}, {p.xp} XP, {p.score} points, {gem_str}")

        for line in lines:
            user.speak(line)

    def _action_check_status_detailed(self, player: Player, action_id: str) -> None:
        """Show detailed status in a status box."""
        if not isinstance(player, PiratesPlayer):
            return
        lines = []
        for p in self.get_active_players():
            gem_str = gems.format_gem_list(p.gems)
            lines.append(f"{p.name}: Level {p.level}, {p.xp} XP, {p.score} points, {gem_str}")
        self.status_box(player, lines)

    def _action_check_position(self, player: Player, action_id: str) -> None:
        """Announce player's current position."""
        if not isinstance(player, PiratesPlayer):
            return

        ocean_index = (player.position - 1) // 10
        ocean_name = (
            self.selected_oceans[ocean_index]
            if ocean_index < len(self.selected_oceans)
            else "Unknown"
        )

        user = self.get_user(player)
        if user:
            user.speak_l("pirates-your-position", position=player.position, ocean=ocean_name)

    def _action_check_moon(self, player: Player, action_id: str) -> None:
        """Check moon brightness (gems collected percentage)."""
        brightness = (self.gems_collected * 100) // 18

        user = self.get_user(player)
        if user:
            user.speak_l(
                "pirates-moon-brightness",
                brightness=brightness,
                collected=self.gems_collected,
                total=18,
            )

    # ==========================================================================
    # Combat Helpers
    # ==========================================================================

    def get_targets_in_range(self, attacker: PiratesPlayer) -> list[PiratesPlayer]:
        """Get all valid targets within attack range."""
        return combat.get_targets_in_range(self, attacker)

    def handle_cannonball_attack(self, player: PiratesPlayer) -> str:
        """Handle a cannonball attack action."""
        targets = self.get_targets_in_range(player)

        if not targets:
            max_range = skills.get_attack_range(player)
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-no-targets", range=max_range, buffer="table")
            return "continue"

        # For human players, show target selection menu
        if not player.is_bot:
            # This would need to be handled via the action input system
            # For now, simplified to auto-select first target
            pass

        # Select target (bot or simplified)
        target = bot_ai.bot_select_target(self, player, targets)
        if target:
            combat.do_attack(
                self,
                player,
                target,
                self.golden_moon_active,
                self.options.combat_xp_multiplier,
                self.options.gem_stealing,
            )
            return "end_turn"

        return "continue"

    def handle_portal(self, player: PiratesPlayer, skill) -> str:
        """Handle the portal skill."""
        # Find oceans with other players
        occupied_oceans: list[tuple[int, str]] = []
        for p in self.get_active_players():
            if p.id == player.id:
                continue
            ocean_num = (p.position - 1) // 10
            ocean_name = (
                self.selected_oceans[ocean_num]
                if ocean_num < len(self.selected_oceans)
                else "Unknown"
            )
            if not any(o[0] == ocean_num for o in occupied_oceans):
                occupied_oceans.append((ocean_num, ocean_name))

        if not occupied_oceans:
            user = self.get_user(player)
            if user:
                user.speak_l("pirates-portal-no-ships", buffer="table")
            self.broadcast_l("pirates-portal-fizzle", player=player.name, exclude=player)
            return "continue"

        # Select ocean (bot or human)
        if player.is_bot:
            chosen_ocean = bot_ai.bot_select_portal_ocean(self, player, occupied_oceans)
        else:
            # For now, simplified to random selection
            chosen_ocean = random.choice(occupied_oceans)[0]  # nosec B311

        if chosen_ocean is None:
            return "continue"

        # Teleport to random position in chosen ocean
        ocean_start = chosen_ocean * 10 + 1
        ocean_end = (chosen_ocean + 1) * 10
        new_pos = random.randint(ocean_start, ocean_end)  # nosec B311

        player.position = new_pos
        skill.start_cooldown(player)

        sound_num = random.randint(1, 2)  # nosec B311
        self.play_sound(f"game_pirates/portal{sound_num}.ogg", volume=60)

        ocean_name = (
            self.selected_oceans[chosen_ocean]
            if chosen_ocean < len(self.selected_oceans)
            else "Unknown"
        )
        self.broadcast_l(
            "pirates-portal-success", player=player.name, ocean=ocean_name, position=new_pos
        )

        self.charted_tiles[new_pos] = True
        return "end_turn"

    def handle_battleship(self, player: PiratesPlayer) -> str:
        """Handle the battleship skill (two attacks)."""
        self.play_sound("game_pirates/battleship.ogg", volume=60)

        user = self.get_user(player)
        if user:
            user.speak_l("pirates-battleship-activated", buffer="table")
        self.broadcast_l(
            "pirates-skill-activated", player=player.name, skill="Battleship", exclude=player
        )

        for shot in range(1, 3):
            targets = self.get_targets_in_range(player)
            if not targets:
                if user:
                    user.speak_l("pirates-battleship-no-targets", shot=shot, buffer="table")
                break

            if user:
                user.speak_l("pirates-battleship-shot", shot=shot, buffer="table")

            target = bot_ai.bot_select_target(self, player, targets)
            if target:
                combat.do_attack(
                    self,
                    player,
                    target,
                    self.golden_moon_active,
                    self.options.combat_xp_multiplier,
                    self.options.gem_stealing,
                )

        return "end_turn"

    def request_boarding_choice(self, attacker: PiratesPlayer, defender: PiratesPlayer) -> str:
        """Request boarding action choice from player (simplified for bot/default)."""
        can_steal = self.options.gem_stealing != "disabled" and defender.has_gems()
        return bot_ai.bot_select_boarding_action(self, attacker, defender, can_steal)
