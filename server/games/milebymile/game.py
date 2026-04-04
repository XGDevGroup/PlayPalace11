"""
Mile by Mile Game Implementation for PlayPalace v11.

A racing card game based on Mille Bornes. Players race to reach a target distance
while playing hazards on opponents and defending with safeties.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from server.core.users.base import MenuItem, EscapeBehavior
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.round_timer import RoundTransitionTimer
from ...game_utils.teams import Team, TeamManager
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState

from .cards import (
    Card,
    Deck,
    CardType,
    HazardType,
    RemedyType,
    SafetyType,
    HAZARD_TO_SAFETY,
    SAFETY_TO_HAZARD,
)
from .options import MileByMileOptions
from .player import MileByMilePlayer
from .state import RaceState

# Hand size
HAND_SIZE = 6


@dataclass
@register_game
class MileByMileGame(Game):
    """
    Mile by Mile - A racing card game based on Mille Bornes.

    Players race to reach a target distance by playing distance cards.
    Hazards slow opponents, remedies fix problems, and safeties provide
    permanent protection. First team to reach the winning score wins.
    """

    players: list[MileByMilePlayer] = field(default_factory=list)
    options: MileByMileOptions = field(default_factory=MileByMileOptions)

    # Game state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    protections_pile: list[Card] = field(default_factory=list)  # Safeties, never reshuffled
    race_states: list[RaceState] = field(default_factory=list)  # Per-team race state
    current_race: int = 0
    race_winner_team_index: int | None = None

    # Dirty trick window
    dirty_trick_window_team: int | None = None
    dirty_trick_window_hazard: str | None = None
    dirty_trick_window_ticks: int = 0

    # Round timer state (serialized)
    round_timer_state: str = "idle"
    round_timer_ticks: int = 0

    def __post_init__(self):
        """Initialize runtime state."""
        super().__post_init__()
        self._round_timer = RoundTransitionTimer(self, delay_seconds=10.0)
        self._pending_discard_slot: dict[str, int] = {}

    def rebuild_runtime_state(self) -> None:
        """Rebuild non-serialized state after deserialization."""
        super().rebuild_runtime_state()
        self._round_timer = RoundTransitionTimer(self, delay_seconds=10.0)
        self._pending_discard_slot: dict[str, int] = {}

    @classmethod
    def get_name(cls) -> str:
        return "Mile by Mile"

    @classmethod
    def get_type(cls) -> str:
        return "milebymile"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 9

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> MileByMilePlayer:
        """Create a new player."""
        return MileByMilePlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Team Management
    # ==========================================================================

    def _setup_teams(self) -> None:
        """Set up teams using TeamManager."""
        active_players = self.get_active_players()
        player_names = [p.name for p in active_players]

        # options.team_mode should be in internal format, but handle old display format for backwards compatibility
        team_mode = self.options.team_mode
        # If it contains spaces or uppercase (except 'v'), it's likely old display format
        if " " in team_mode or any(c.isupper() for c in team_mode if c != "v"):
            team_mode = TeamManager.parse_display_to_team_mode(team_mode)
        self._team_manager.team_mode = team_mode
        self._team_manager.setup_teams(player_names)

        # Set player team indices
        for player in active_players:
            team = self._team_manager.get_team(player.name)
            if team:
                player.team_index = team.index

        # Initialize race states for each team
        self.race_states = [RaceState() for _ in self._team_manager.teams]

    def get_race_state(self, team_index: int) -> RaceState | None:
        """Get the race state for a team by index."""
        if 0 <= team_index < len(self.race_states):
            return self.race_states[team_index]
        return None

    def get_player_race_state(self, player: MileByMilePlayer) -> RaceState | None:
        """Get the race state for a player's team."""
        return self.get_race_state(player.team_index)

    def get_team_name(self, team_index: int) -> str:
        """Get display name for a team by index."""
        if team_index < len(self._team_manager.teams):
            return self._team_manager.get_team_name(self._team_manager.teams[team_index])
        return f"Team {team_index + 1}"

    def is_individual_mode(self) -> bool:
        """Check if game is in individual mode."""
        return self.options.team_mode == "individual"

    def get_num_teams(self) -> int:
        """Get the number of teams."""
        return len(self._team_manager.teams)

    def get_team_score(self, team_index: int) -> int:
        """Get total score for a team."""
        if team_index < len(self._team_manager.teams):
            return self._team_manager.teams[team_index].total_score
        return 0

    def add_team_score(self, team_index: int, points: int) -> None:
        """Add points to a team's score."""
        if team_index < len(self._team_manager.teams):
            self._team_manager.teams[team_index].total_score += points

    def set_team_round_score(self, team_index: int, points: int) -> None:
        """Set the round score for a team."""
        if team_index < len(self._team_manager.teams):
            self._team_manager.teams[team_index].round_score = points

    def iter_teams(self):
        """Iterate over (team_index, race_state) pairs."""
        for i, race_state in enumerate(self.race_states):
            yield i, race_state

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: MileByMilePlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")

        # Card slot actions will be dynamically added/removed

        # Dirty trick action (hidden, triggered by keybind)
        action_set.add(
            Action(
                id="dirty_trick",
                label="Play dirty trick",
                handler="_action_dirty_trick",
                is_enabled="_is_dirty_trick_enabled",
                is_hidden="_is_dirty_trick_hidden",
                show_in_actions_menu=False,
            )
        )

        # Junk card action (hidden, triggered by shift+enter or backspace keybind)
        action_set.add(
            Action(
                id="junk_card",
                label="Discard card",
                handler="_action_junk_card",
                is_enabled="_is_junk_card_enabled",
                is_hidden="_is_junk_card_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: MileByMilePlayer) -> ActionSet:
        """Create the standard action set with Mile by Mile overrides."""
        action_set = super().create_standard_action_set(player)
        action = Action(
            id="check_status",
            label="Check status",
            handler="_action_check_status",
            is_enabled="_is_check_status_enabled",
            is_hidden="_is_check_status_hidden",
        )
        action_set.add(action)
        if action.id in action_set._order:
            action_set._order.remove(action.id)
        action_set._order.insert(0, action.id)

        action = Action(
            id="check_status_detailed",
            label="Detailed status",
            handler="_action_check_status_detailed",
            is_enabled="_is_check_status_enabled",
            is_hidden="_is_check_status_hidden",
        )
        action_set.add(action)
        if action.id in action_set._order:
            action_set._order.remove(action.id)
        action_set._order.insert(1, action.id)

        for action_id in ("check_scores", "check_scores_detailed"):
            existing = action_set.get_action(action_id)
            if existing:
                existing.show_in_actions_menu = False
        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Remove base class's 's' and 'shift+s' keybinds before adding ours
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        # Override 's' to only show status (not scores from base class)
        self.define_keybind(
            "s",
            "Check status",
            ["check_status"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Override 'shift+s' to show detailed status (not just scores)
        self.define_keybind(
            "shift+s",
            "Detailed status",
            ["check_status_detailed"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Dirty trick keybind
        self.define_keybind("d", "Play dirty trick", ["dirty_trick"], state=KeybindState.ACTIVE)

        # Number keys for card slots (1-6)
        # Number keybinds for card slots removed (menu/arrow selection only)

        # Shift+Enter or Backspace to discard the selected card
        self.define_keybind("shift+enter", "Discard card", ["junk_card"], state=KeybindState.ACTIVE)
        self.define_keybind("backspace", "Discard card", ["junk_card"], state=KeybindState.ACTIVE)

    def _update_card_actions(self, player: MileByMilePlayer) -> None:
        """Update card slot actions based on player's hand."""
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        # Remove old card actions and ensure they're removed from _order
        # Note: HAND_SIZE + 2 to account for the card drawn at start of turn
        for i in range(1, HAND_SIZE + 2):
            action_id = f"card_slot_{i}"
            if turn_set.get_action(action_id):
                turn_set.remove(action_id)
            # Also ensure it's not lingering in _order
            if action_id in turn_set._order:
                turn_set._order.remove(action_id)

        # Add actions for cards in hand
        for i, card in enumerate(player.hand, 1):
            action_id = f"card_slot_{i}"
            playable = self._can_play_card(player, card)

            # Check if hazard with multiple targets needs menu
            input_request = None
            if card.card_type == CardType.HAZARD and playable:
                targets = self._get_valid_hazard_targets(player, card.value)
                if len(targets) > 1:
                    input_request = MenuInput(
                        prompt="milebymile-select-target",
                        options="_hazard_target_options",
                        bot_select="_bot_select_hazard_target",
                    )

            # Always show cards in menu, but enable/disable based on state
            # Use dynamic label to ensure locale changes are reflected
            turn_set.add(
                Action(
                    id=action_id,
                    label="",  # Fallback, dynamic label used instead
                    handler="_action_play_card",
                    is_enabled="_is_card_action_enabled",
                    is_hidden="_is_card_action_hidden",
                    get_label="_get_card_slot_label",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_check_status_enabled(self, player: Player) -> str | None:
        """Check if check status action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_status_hidden(self, player: Player) -> Visibility:
        """Check status is always hidden (triggered by keybind only)."""
        return Visibility.HIDDEN

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        """Hide base score actions (custom status replaces them)."""
        return Visibility.HIDDEN

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        """Hide base detailed score actions (custom status replaces them)."""
        return Visibility.HIDDEN

    def _is_dirty_trick_enabled(self, player: Player) -> str | None:
        """Check if dirty trick action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        mbm_player: MileByMilePlayer = player  # type: ignore
        if self.dirty_trick_window_team is None:
            return "milebymile-no-dirty-trick-window"
        if mbm_player.team_index != self.dirty_trick_window_team:
            return "milebymile-not-your-dirty-trick"
        return None

    def _is_dirty_trick_hidden(self, player: Player) -> Visibility:
        """Dirty trick is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_junk_card_enabled(self, player: Player) -> str | None:
        """Check if junk card action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        return None

    def _is_junk_card_hidden(self, player: Player) -> Visibility:
        """Junk card is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_card_action_enabled(self, player: Player) -> str | None:
        """Check if card actions are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self._round_timer.is_active:
            return "milebymile-between-races"
        return None

    def _is_card_action_hidden(self, player: Player) -> Visibility:
        """Card actions are visible during play."""
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_card_slot_label(self, player: Player, action_id: str) -> str:
        """Get dynamic label for a card slot action."""
        if not isinstance(player, MileByMilePlayer):
            return ""
        # Extract slot number from action_id (e.g., "card_slot_1" -> 0)
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except (ValueError, IndexError):
            return ""
        if slot < 0 or slot >= len(player.hand):
            return ""
        card = player.hand[slot]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return self._get_localized_card_name(card, locale)

    def _update_turn_actions(self, player: MileByMilePlayer) -> None:
        """Update dynamic card actions for a player."""
        self._update_card_actions(player)

    def _update_all_turn_actions(self) -> None:
        """Update card actions for all players."""
        for player in self.players:
            self._update_turn_actions(player)

    # ==========================================================================
    # Card Logic
    # ==========================================================================

    def _can_play_card(self, player: MileByMilePlayer, card: Card) -> bool:
        """Check if a card can be played."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return False

        if card.card_type == CardType.DISTANCE:
            return self._can_play_distance(race_state, card)
        elif card.card_type == CardType.HAZARD:
            return self._can_play_hazard(player, card)
        elif card.card_type == CardType.REMEDY:
            return self._can_play_remedy(race_state, card)
        elif card.card_type == CardType.SAFETY:
            return not race_state.has_safety(card.value)
        elif card.card_type == CardType.SPECIAL:
            if card.value == "false_virtue":
                return not race_state.has_karma
        return False

    def _get_unplayable_reason(
        self, player: MileByMilePlayer, card: Card, locale: str = "en"
    ) -> str:
        """Get a human-readable reason why a card can't be played."""
        from ...messages.localization import Localization

        race_state = self.get_player_race_state(player)
        if not race_state:
            return Localization.get(locale, "milebymile-reason-not-on-team")

        if card.card_type == CardType.DISTANCE:
            return self._get_distance_unplayable_reason(race_state, card, locale)
        if card.card_type == CardType.HAZARD:
            return Localization.get(locale, "milebymile-reason-no-targets")
        if card.card_type == CardType.REMEDY:
            return self._get_remedy_unplayable_reason(race_state, card, locale)
        if card.card_type == CardType.SAFETY:
            return Localization.get(locale, "milebymile-reason-has-safety")
        if card.card_type == CardType.SPECIAL and card.value == "false_virtue":
            return Localization.get(locale, "milebymile-reason-has-karma")

        return Localization.get(locale, "milebymile-reason-generic")

    def _get_distance_unplayable_reason(
        self,
        race_state: RaceState,
        card: Card,
        locale: str,
    ) -> str:
        from ...messages.localization import Localization

        distance = card.distance
        if not race_state.can_play_distance():
            if race_state.has_problem(HazardType.STOP):
                return Localization.get(locale, "milebymile-reason-stopped")
            return Localization.get(locale, "milebymile-reason-has-problem")
        if race_state.has_problem(HazardType.SPEED_LIMIT) and distance > 50:
            return Localization.get(locale, "milebymile-reason-speed-limit")
        if self.options.only_allow_perfect_crossing:
            if race_state.miles + distance > self.options.round_distance:
                return Localization.get(
                    locale,
                    "milebymile-reason-exceeds-distance",
                    miles=self.options.round_distance,
                )
        return Localization.get(locale, "milebymile-reason-generic")

    def _get_remedy_unplayable_reason(
        self,
        race_state: RaceState,
        card: Card,
        locale: str,
    ) -> str:
        from ...messages.localization import Localization

        remedy = card.value
        if remedy == RemedyType.END_OF_LIMIT:
            return Localization.get(locale, "milebymile-reason-no-speed-limit")
        if remedy == RemedyType.ROLL:
            if race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                return Localization.get(locale, "milebymile-reason-has-right-of-way")
            if not race_state.has_problem(HazardType.STOP):
                return Localization.get(locale, "milebymile-reason-already-moving")
            problem = self._first_blocking_problem(race_state, locale)
            if problem:
                return problem
        if remedy == RemedyType.GASOLINE:
            return Localization.get(locale, "milebymile-reason-has-gas")
        if remedy == RemedyType.SPARE_TIRE:
            return Localization.get(locale, "milebymile-reason-tires-fine")
        if remedy == RemedyType.REPAIRS:
            return Localization.get(locale, "milebymile-reason-no-accident")
        return Localization.get(locale, "milebymile-reason-generic")

    def _first_blocking_problem(self, race_state: RaceState, locale: str) -> str | None:
        from ...messages.localization import Localization

        for problem in race_state.problems:
            if problem not in (HazardType.STOP, HazardType.SPEED_LIMIT):
                problem_name = self._get_localized_problem_name(problem, locale)
                return Localization.get(
                    locale,
                    "milebymile-reason-must-fix-first",
                    problem=problem_name,
                )
        return None

    def _get_localized_problem_name(self, problem: str, locale: str) -> str:
        """Get localized name for a problem/hazard type."""
        from ...messages.localization import Localization

        key_map = {
            HazardType.OUT_OF_GAS: "milebymile-card-out-of-gas",
            HazardType.FLAT_TIRE: "milebymile-card-flat-tire",
            HazardType.ACCIDENT: "milebymile-card-accident",
            HazardType.SPEED_LIMIT: "milebymile-card-speed-limit",
            HazardType.STOP: "milebymile-card-stop",
        }
        key = key_map.get(problem, "")
        return Localization.get(locale, key) if key else problem

    def _get_localized_safety_name(self, safety: str, locale: str) -> str:
        """Get localized name for a safety type."""
        from ...messages.localization import Localization

        key_map = {
            SafetyType.EXTRA_TANK: "milebymile-card-extra-tank",
            SafetyType.PUNCTURE_PROOF: "milebymile-card-puncture-proof",
            SafetyType.DRIVING_ACE: "milebymile-card-driving-ace",
            SafetyType.RIGHT_OF_WAY: "milebymile-card-right-of-way",
        }
        key = key_map.get(safety, "")
        return Localization.get(locale, key) if key else safety

    def _get_localized_safety_effect(self, safety: str, locale: str) -> str:
        """Get localized effect text for a safety card."""
        key_map = {
            SafetyType.EXTRA_TANK: "milebymile-safety-effect-extra-tank",
            SafetyType.PUNCTURE_PROOF: "milebymile-safety-effect-puncture-proof",
            SafetyType.DRIVING_ACE: "milebymile-safety-effect-driving-ace",
            SafetyType.RIGHT_OF_WAY: "milebymile-safety-effect-right-of-way",
        }
        key = key_map.get(safety, "")
        return Localization.get(locale, key) if key else safety

    def _get_localized_card_name(self, card: Card, locale: str) -> str:
        """Get localized name for a card."""
        from ...messages.localization import Localization

        if card.card_type == CardType.DISTANCE:
            return Localization.get(locale, "milebymile-card-miles", miles=card.value)

        key_map = {
            # Hazards
            HazardType.OUT_OF_GAS: "milebymile-card-out-of-gas",
            HazardType.FLAT_TIRE: "milebymile-card-flat-tire",
            HazardType.ACCIDENT: "milebymile-card-accident",
            HazardType.SPEED_LIMIT: "milebymile-card-speed-limit",
            HazardType.STOP: "milebymile-card-stop",
            # Remedies
            RemedyType.GASOLINE: "milebymile-card-gasoline",
            RemedyType.SPARE_TIRE: "milebymile-card-spare-tire",
            RemedyType.REPAIRS: "milebymile-card-repairs",
            RemedyType.END_OF_LIMIT: "milebymile-card-end-of-limit",
            RemedyType.ROLL: "milebymile-card-green-light",
            # Safeties
            SafetyType.EXTRA_TANK: "milebymile-card-extra-tank",
            SafetyType.PUNCTURE_PROOF: "milebymile-card-puncture-proof",
            SafetyType.DRIVING_ACE: "milebymile-card-driving-ace",
            SafetyType.RIGHT_OF_WAY: "milebymile-card-right-of-way",
            # Special
            "false_virtue": "milebymile-card-false-virtue",
        }
        key = key_map.get(card.value, "")
        return Localization.get(locale, key) if key else card.name

    def _can_play_distance(self, race_state: RaceState, card: Card) -> bool:
        """Check if team can play a distance card."""
        if not race_state.can_play_distance():
            return False

        distance = card.distance

        # Check speed limit
        if race_state.has_problem(HazardType.SPEED_LIMIT) and distance > 50:
            return False

        # Check perfect crossing
        if self.options.only_allow_perfect_crossing:
            if race_state.miles + distance > self.options.round_distance:
                return False

        return True

    def _can_play_hazard(self, player: MileByMilePlayer, card: Card) -> bool:
        """Check if hazard can be played on any opponent."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return False

        for target_idx, target_state in self.iter_teams():
            if target_idx == player.team_index:
                continue
            if self._can_play_hazard_on_team(card.value, target_state, attacker_state):
                return True
        return False

    def _can_play_hazard_on_team(self, hazard: str, target: RaceState, attacker: RaceState) -> bool:
        """Check if hazard can be played on a specific team."""
        # Check if target has blocking safety
        blocking_safety = HAZARD_TO_SAFETY.get(hazard)
        if blocking_safety and target.has_safety(blocking_safety):
            return False

        # Karma rule check
        if self.options.karma_rule:
            if not attacker.has_karma and target.has_karma:
                return False

        # Check for existing problems
        if hazard == HazardType.SPEED_LIMIT:
            # Speed limit just checks for duplicate
            return not target.has_problem(hazard)
        else:
            # Critical hazards: can't stack unless option enabled
            if self.options.allow_stacking_attacks:
                return not target.has_problem(hazard)
            else:
                return not target.has_any_problem()

    def _can_play_remedy(self, race_state: RaceState, card: Card) -> bool:
        """Check if remedy can be played."""
        remedy = card.value

        if remedy == RemedyType.END_OF_LIMIT:
            return race_state.has_problem(HazardType.SPEED_LIMIT)

        if remedy == RemedyType.ROLL:
            # Can't play if have Right of Way
            if race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                return False
            # Must have stop problem
            if not race_state.has_problem(HazardType.STOP):
                return False
            # Can't have other problems (except speed limit)
            for problem in race_state.problems:
                if problem not in (HazardType.STOP, HazardType.SPEED_LIMIT):
                    return False
            return True

        # Specific remedies
        remedy_to_hazard = {
            RemedyType.GASOLINE: HazardType.OUT_OF_GAS,
            RemedyType.SPARE_TIRE: HazardType.FLAT_TIRE,
            RemedyType.REPAIRS: HazardType.ACCIDENT,
        }
        hazard = remedy_to_hazard.get(remedy)
        return hazard and race_state.has_problem(hazard)

    def _get_valid_hazard_targets(self, player: MileByMilePlayer, hazard: str) -> list[int]:
        """Get list of team indices that can be targeted by a hazard."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return []

        targets = []
        for target_idx, target_state in self.iter_teams():
            if target_idx == player.team_index:
                continue
            if self._can_play_hazard_on_team(hazard, target_state, attacker_state):
                targets.append(target_idx)
        return targets

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show game status to player."""
        user = self.get_user(player)
        if not user:
            return

        from ...messages.localization import Localization

        locale = user.locale
        none_str = Localization.get(locale, "milebymile-none")

        for team_idx, race_state in self.iter_teams():
            name = self.get_team_name(team_idx)

            # Get score
            team = (
                self._team_manager.teams[team_idx]
                if team_idx < len(self._team_manager.teams)
                else None
            )
            score = team.total_score if team else 0

            if race_state.problems:
                problems_str = ", ".join(
                    self._get_localized_problem_name(p, locale) for p in race_state.problems
                )
            else:
                problems_str = none_str
            if race_state.safeties:
                safeties_str = ", ".join(
                    self._get_localized_safety_name(s, locale) for s in race_state.safeties
                )
            else:
                safeties_str = none_str

            user.speak_l(
                "milebymile-status",
                name=name,
                points=score,
                miles=race_state.miles,
                problems=problems_str,
                safeties=safeties_str,
            )

    def _action_check_status_detailed(self, player: Player, action_id: str) -> None:
        """Show detailed game status in a status box menu."""
        user = self.get_user(player)
        if not user:
            return

        from ...messages.localization import Localization

        locale = user.locale
        none_str = Localization.get(locale, "milebymile-none")
        lines = []

        for team_idx, race_state in self.iter_teams():
            name = self.get_team_name(team_idx)

            # Get score
            team = (
                self._team_manager.teams[team_idx]
                if team_idx < len(self._team_manager.teams)
                else None
            )
            score = team.total_score if team else 0

            # Format problems
            if race_state.problems:
                problems_str = ", ".join(
                    self._get_localized_problem_name(p, locale) for p in race_state.problems
                )
            else:
                problems_str = none_str

            # Format safeties
            if race_state.safeties:
                safeties_str = ", ".join(
                    self._get_localized_safety_name(s, locale) for s in race_state.safeties
                )
            else:
                safeties_str = none_str

            # Add team status line (one line per team)
            lines.append(
                f"{name}: {score} points, {race_state.miles} miles, Problems: {problems_str}, Safeties: {safeties_str}"
            )

        self.status_box(player, lines)

    def _action_dirty_trick(self, player: Player, action_id: str) -> None:
        """Handle dirty trick (Coup Fourré) attempt."""
        if not isinstance(player, MileByMilePlayer):
            return

        race_state = self.get_player_race_state(player)
        if not race_state or self.dirty_trick_window_team != player.team_index:
            return

        hazard = self.dirty_trick_window_hazard
        if not hazard:
            return

        # Find matching safety in hand
        blocking_safety = HAZARD_TO_SAFETY.get(hazard)
        if not blocking_safety:
            return

        safety_card = None
        card_index = -1
        for i, card in enumerate(player.hand):
            if card.card_type == CardType.SAFETY and card.value == blocking_safety:
                safety_card = card
                card_index = i
                break

        if not safety_card:
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-matching-safety")
            return

        # Play the dirty trick!
        self._play_safety(player, card_index, safety_card, is_dirty_trick=True)

        # Close the window
        self.dirty_trick_window_team = None
        self.dirty_trick_window_hazard = None
        self.dirty_trick_window_ticks = 0

    def _hazard_target_options(self, player: Player) -> list[str]:
        """Get list of valid hazard target names for menu input."""
        if not isinstance(player, MileByMilePlayer):
            return []

        # Get the pending action to find which card slot
        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return []

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return []

        if slot < 0 or slot >= len(player.hand):
            return []

        card = player.hand[slot]
        if card.card_type != CardType.HAZARD:
            return []

        target_indices = self._get_valid_hazard_targets(player, card.value)
        # Format like v10: "Name (X miles)" for individual, "Team N: members (X miles)" for teams
        options = []
        for team_idx in target_indices:
            race_state = self.race_states[team_idx]
            team = self._team_manager.teams[team_idx]
            if self.is_individual_mode():
                options.append(f"{team.members[0]} ({race_state.miles} miles)")
            else:
                members = ", ".join(team.members)
                options.append(f"Team {team_idx + 1}: {members} ({race_state.miles} miles)")
        return options

    def _bot_select_hazard_target(self, player: Player, options: list[str]) -> str | None:
        """Bot selects hazard target - picks team with most miles."""
        if not isinstance(player, MileByMilePlayer):
            return None

        action_id = self._pending_actions.get(player.id)
        if not action_id:
            return None

        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return None

        if slot < 0 or slot >= len(player.hand):
            return None

        card = player.hand[slot]
        if card.card_type != CardType.HAZARD:
            return None

        target_indices = self._get_valid_hazard_targets(player, card.value)
        if not target_indices:
            return None

        # Pick target with most miles
        best_idx = max(target_indices, key=lambda i: self.race_states[i].miles)
        race_state = self.race_states[best_idx]
        team = self._team_manager.teams[best_idx]
        # Return in same format as _hazard_target_options
        if self.is_individual_mode():
            return f"{team.members[0]} ({race_state.miles} miles)"
        else:
            members = ", ".join(team.members)
            return f"Team {best_idx + 1}: {members} ({race_state.miles} miles)"

    def _action_play_card(self, player: Player, *args) -> None:
        """Handle playing a card from hand.

        Can be called as:
        - _action_play_card(player, action_id) - no input
        - _action_play_card(player, input_value, action_id) - with menu input
        """
        if not isinstance(player, MileByMilePlayer):
            return

        # Check if it's this player's turn
        if self.current_player != player:
            return

        # Parse arguments - handler can receive (player, action_id) or (player, input_value, action_id)
        if len(args) == 1:
            action_id = args[0]
            input_value = None
        elif len(args) == 2:
            input_value, action_id = args
        else:
            return

        # Extract slot number from action_id (e.g., "card_slot_1" -> 0)
        try:
            slot = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]

        if self._can_play_card(player, card):
            self._play_card(player, slot, card, input_value)
        else:
            # Can't play - bots auto-discard, humans get a yes/no prompt
            if player.is_bot:
                self._discard_card(player, slot, card)
            else:
                user = self.get_user(player)
                if user:
                    reason = self._get_unplayable_reason(player, card, user.locale)
                    card_name = self._get_localized_card_name(card, user.locale)
                    user.speak_l("milebymile-cant-play", card=card_name, reason=reason)
                    self._show_discard_confirm(player, slot, user)

    def _action_junk_card(self, player: Player, action_id: str) -> None:
        """Handle discarding the currently selected card (shift+enter or backspace keybind)."""
        if not isinstance(player, MileByMilePlayer):
            return

        # Check if it's this player's turn
        if self.current_player != player:
            return

        # Get the selected menu item from context
        context = self.get_action_context(player)
        menu_item_id = context.menu_item_id

        if not menu_item_id or not menu_item_id.startswith("card_slot_"):
            user = self.get_user(player)
            if user:
                user.speak_l("milebymile-no-card-selected")
            return

        # Extract slot number from menu_item_id
        try:
            slot = int(menu_item_id.split("_")[-1]) - 1
        except ValueError:
            return

        if slot < 0 or slot >= len(player.hand):
            return

        card = player.hand[slot]

        # Check if discarding is allowed when card is playable
        if not self.options.always_allow_discarding:
            if self._can_play_card(player, card):
                user = self.get_user(player)
                if user:
                    user.speak_l("milebymile-cant-discard-playable")
                return

        self._discard_card(player, slot, card)

    def rebuild_player_menu(self, player, *, position: int | None = None) -> None:
        """Skip rebuilding if this player has a pending discard confirmation."""
        if player.id in self._pending_actions:
            return
        super().rebuild_player_menu(player, position=position)

    def _show_discard_confirm(self, player: MileByMilePlayer, slot: int, user) -> None:
        """Show a yes/no confirmation to discard the unplayable card."""
        self._pending_discard_slot[player.id] = slot
        self._pending_actions[player.id] = "discard_confirm"
        items = [
            MenuItem(text=Localization.get(user.locale, "confirm-yes"), id="yes"),
            MenuItem(text=Localization.get(user.locale, "confirm-no"), id="no"),
        ]
        user.show_menu(
            "discard_confirm",
            items,
            multiletter=False,
            escape_behavior=EscapeBehavior.SELECT_LAST,
        )

    def _handle_menu_event(self, player: "Player", event: dict) -> None:
        """Handle menu events, routing discard confirmation."""
        menu_id = event.get("menu_id")
        if menu_id == "discard_confirm":
            self._handle_discard_confirm(player, event)
        else:
            super()._handle_menu_event(player, event)

    def _handle_discard_confirm(self, player: "Player", event: dict) -> None:
        """Handle the discard confirmation menu response."""
        self._pending_actions.pop(player.id, None)
        slot = self._pending_discard_slot.pop(player.id, None)
        if not isinstance(player, MileByMilePlayer):
            self.rebuild_all_menus()
            return
        selection_id = event.get("selection_id", "")
        if not selection_id:
            selection = event.get("selection", 1) - 1
            selection_id = "yes" if selection == 0 else "no"
        if selection_id == "yes" and slot is not None and slot < len(player.hand):
            card = player.hand[slot]
            if not self.options.always_allow_discarding and self._can_play_card(player, card):
                user = self.get_user(player)
                if user:
                    user.speak_l("milebymile-cant-discard-playable")
                self.rebuild_all_menus()
                return
            self._discard_card(player, slot, card)
            return
        self.rebuild_all_menus()

    def _play_card(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        target_name: str | None = None,
    ) -> None:
        """Play a card from hand."""
        if card.card_type == CardType.DISTANCE:
            self._play_distance(player, slot, card)
        elif card.card_type == CardType.HAZARD:
            self._play_hazard(player, slot, card, target_name)
        elif card.card_type == CardType.REMEDY:
            self._play_remedy(player, slot, card)
        elif card.card_type == CardType.SAFETY:
            self._play_safety(player, slot, card, is_dirty_trick=False)
        elif card.card_type == CardType.SPECIAL:
            self._play_special(player, slot, card)

    def _play_distance(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a distance card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        distance = card.distance
        player.hand.pop(slot)
        race_state.miles += distance

        if distance == 200:
            race_state.used_200_mile = True

        # Play sounds
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311

        # Distance-specific sounds
        sound_variants = {25: 2, 50: 3, 75: 3, 100: 3, 200: 3}
        if distance in sound_variants:
            variant = random.randint(1, sound_variants[distance])  # nosec B311
            self.play_sound(f"game_milebymile/{distance}miles{variant}.ogg")

        # Announce
        if self.is_individual_mode():
            self.broadcast_l(
                "milebymile-plays-distance-individual",
                player=player.name,
                distance=distance,
                total=race_state.miles,
            )
        else:
            self.broadcast_l(
                "milebymile-plays-distance-team",
                player=player.name,
                distance=distance,
                total=race_state.miles,
            )

        self.discard_pile.append(card)

        # Check for race win
        if race_state.miles >= self.options.round_distance:
            if (
                race_state.miles == self.options.round_distance
                and not self.options.only_allow_perfect_crossing
            ):
                if self.is_individual_mode():
                    self.broadcast_l(
                        "milebymile-journey-complete-perfect-individual",
                        player=player.name,
                    )
                else:
                    self.broadcast_l(
                        "milebymile-journey-complete-perfect-team", team=player.team_index + 1
                    )
            else:
                if self.is_individual_mode():
                    self.broadcast_l("milebymile-journey-complete-individual", player=player.name)
                else:
                    self.broadcast_l("milebymile-journey-complete-team", team=player.team_index + 1)

            self.play_sound("game_milebymile/winround.ogg")
            self.race_winner_team_index = player.team_index

        self._end_turn()

    def _play_hazard(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        target_selection: str | None = None,
    ) -> None:
        """Play a hazard card on an opponent."""
        attacker_state = self.get_player_race_state(player)
        if not attacker_state:
            return

        target_indices = self._get_valid_hazard_targets(player, card.value)
        if not target_indices:
            self._notify_no_hazard_targets(player)
            return

        target_idx = self._resolve_hazard_target(target_indices, target_selection)
        if target_idx is None:
            return

        target_state = self.race_states[target_idx]
        target_team = self._team_manager.teams[target_idx]

        player.hand.pop(slot)

        attacker_shunned = self._resolve_karma_attack(
            player, attacker_state, target_state, target_team, target_idx, card
        )
        if attacker_shunned is None:
            return

        # Apply hazard
        target_state.battle_pile.append(card)
        target_state.add_problem(card.value)

        # All hazards except speed limit also add stop
        if card.value != HazardType.SPEED_LIMIT:
            if not target_state.has_safety(SafetyType.RIGHT_OF_WAY):
                target_state.add_problem(HazardType.STOP)

        self._announce_hazard_play(player, card, target_team, target_idx)

        # Announce karma loss (personalized)
        if attacker_shunned:
            self._announce_attacker_shunned(player, player.team_index)

        # Open dirty trick window
        self.dirty_trick_window_team = target_idx
        self.dirty_trick_window_hazard = card.value
        self.dirty_trick_window_ticks = 60  # 3 seconds at 20 ticks/sec

        # Schedule bot dirty trick check
        self._schedule_dirty_trick_bots(target_team)

        self._end_turn()

    def _notify_no_hazard_targets(self, player: MileByMilePlayer) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l("milebymile-no-valid-targets")

    def _resolve_hazard_target(
        self,
        target_indices: list[int],
        target_selection: str | None,
    ) -> int | None:
        if target_selection:
            if self.is_individual_mode():
                name = (
                    target_selection.split(" (")[0]
                    if " (" in target_selection
                    else target_selection
                )
                for idx in target_indices:
                    team = self._team_manager.teams[idx]
                    if team.members and team.members[0] == name:
                        return idx
            else:
                if target_selection.startswith("Team "):
                    try:
                        team_num = int(target_selection.split(":")[0].replace("Team ", ""))
                        for idx in target_indices:
                            if idx + 1 == team_num:
                                return idx
                    except (ValueError, IndexError):
                        return None
            return None
        if len(target_indices) == 1:
            return target_indices[0]
        return target_indices[0]

    def _resolve_karma_attack(
        self,
        player: MileByMilePlayer,
        attacker_state: RaceState,
        target_state: RaceState,
        target_team: Team,
        target_idx: int,
        card: Card,
    ) -> bool | None:
        attacker_shunned = False
        if self.options.karma_rule:
            if attacker_state.has_karma and target_state.has_karma:
                attacker_state.has_karma = False
                target_state.has_karma = False

                self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311
                self._announce_hazard_target(player, card, target_team, target_idx)
                self._announce_karma_clash(player, player.team_index, target_idx)

                self.discard_pile.append(card)
                self._end_turn()
                return None

            if attacker_state.has_karma and not target_state.has_karma:
                attacker_state.has_karma = False
                attacker_shunned = True
        return attacker_shunned

    def _announce_hazard_play(
        self,
        player: MileByMilePlayer,
        card: Card,
        target_team: Team,
        target_idx: int,
    ) -> None:
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311
        hazard_sounds = {
            HazardType.ACCIDENT: f"game_milebymile/crash{random.randint(1, 2)}.ogg",  # nosec B311
            HazardType.OUT_OF_GAS: "game_milebymile/outofgas.ogg",
            HazardType.FLAT_TIRE: "game_milebymile/flat.ogg",
            HazardType.STOP: "game_milebymile/stop.ogg",
            HazardType.SPEED_LIMIT: "game_milebymile/speedlimit.ogg",
        }
        if card.value in hazard_sounds:
            self.play_sound(hazard_sounds[card.value])
        self._announce_hazard_target(player, card, target_team, target_idx)

    def _announce_hazard_target(
        self,
        player: MileByMilePlayer,
        card: Card,
        target_team: Team,
        target_idx: int,
    ) -> None:
        if self.is_individual_mode():
            target_name = target_team.members[0]
            self._broadcast_card_message(
                "milebymile-plays-hazard-individual",
                card,
                player=player.name,
                target=target_name,
            )
        else:
            self._broadcast_card_message(
                "milebymile-plays-hazard-team",
                card,
                player=player.name,
                team=target_idx + 1,
            )

    def _schedule_dirty_trick_bots(self, target_team: Team) -> None:
        for member_name in target_team.members:
            member = self._get_player_by_name(member_name)
            if member and member.is_bot:
                BotHelper.jolt_bot(member, ticks=random.randint(12, 18))  # nosec B311

    def _play_remedy(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a remedy card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)
        race_state.battle_pile.append(card)

        remedy = card.value
        self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311

        if remedy == RemedyType.END_OF_LIMIT:
            race_state.remove_problem(HazardType.SPEED_LIMIT)
            self.play_sound("game_milebymile/speedlimitend.ogg")
        elif remedy == RemedyType.ROLL:
            race_state.remove_problem(HazardType.STOP)
            self.play_sound(f"game_milebymile/greenlight{random.randint(1, 3)}.ogg")  # nosec B311
        elif remedy == RemedyType.GASOLINE:
            race_state.remove_problem(HazardType.OUT_OF_GAS)
            self.play_sound("game_milebymile/gas.ogg")
        elif remedy == RemedyType.SPARE_TIRE:
            race_state.remove_problem(HazardType.FLAT_TIRE)
            self.play_sound("game_milebymile/sparetyre.ogg")
        elif remedy == RemedyType.REPAIRS:
            race_state.remove_problem(HazardType.ACCIDENT)
            self.play_sound(f"game_milebymile/repair{random.randint(1, 2)}.ogg")  # nosec B311

        self._broadcast_card_message("milebymile-plays-card", card, player=player.name)
        self.discard_pile.append(card)
        self._end_turn()

    def _play_safety(
        self,
        player: MileByMilePlayer,
        slot: int,
        card: Card,
        is_dirty_trick: bool = False,
    ) -> None:
        """Play a safety card."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)
        race_state.add_safety(card.value)

        if is_dirty_trick:
            race_state.dirty_trick_count += 1
            self._broadcast_safety_play_with_effect(
                player=player,
                card=card,
                is_dirty_trick=True,
            )
            self.play_sound("mention.ogg")

            # Remove the hazard that triggered this
            hazard = SAFETY_TO_HAZARD.get(card.value)
            if hazard:
                race_state.remove_problem(hazard)
            if card.value == SafetyType.RIGHT_OF_WAY:
                race_state.remove_problem(HazardType.SPEED_LIMIT)
                race_state.remove_problem(HazardType.STOP)

            # Clean up remaining stop if no other problems
            if len(race_state.problems) == 1 and HazardType.STOP in race_state.problems:
                race_state.remove_problem(HazardType.STOP)
        else:
            self._broadcast_safety_play_with_effect(
                player=player,
                card=card,
                is_dirty_trick=False,
            )
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311

            # Safety-specific sounds
            safety_sounds = {
                SafetyType.DRIVING_ACE: "game_milebymile/drivingace.ogg",
                SafetyType.EXTRA_TANK: f"game_milebymile/extratank{random.randint(1, 2)}.ogg",  # nosec B311
                SafetyType.PUNCTURE_PROOF: "game_milebymile/punctureproof.ogg",
                SafetyType.RIGHT_OF_WAY: "game_milebymile/rightofway.ogg",
            }
            if card.value in safety_sounds:
                self.play_sound(safety_sounds[card.value])

            # Remove matching problem
            hazard = SAFETY_TO_HAZARD.get(card.value)
            if hazard:
                race_state.remove_problem(hazard)
            if card.value == SafetyType.RIGHT_OF_WAY:
                race_state.remove_problem(HazardType.SPEED_LIMIT)
                race_state.remove_problem(HazardType.STOP)

        # Safety cards go to protections pile (never reshuffled)
        self.protections_pile.append(card)

        # Safety grants extra turn - draw replacement and continue
        new_card = self._draw_card(player)
        if new_card:
            player.hand.append(new_card)
            user = self.get_user(player)
            if user:
                card_name = self._get_localized_card_name(new_card, user.locale)
                user.speak_l("milebymile-you-drew", card=card_name, buffer="table")

        self._update_turn_actions(player)
        self.rebuild_player_menu(player)
        # Don't end turn - safety grants extra turn

        # Jolt bot to think about next play
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 40))  # nosec B311

    def _play_special(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Play a special card (False Virtue)."""
        race_state = self.get_player_race_state(player)
        if not race_state:
            return

        player.hand.pop(slot)

        if card.value == "false_virtue":
            race_state.has_karma = True
            self.play_sound(f"game_cards/play{random.randint(1, 4)}.ogg")  # nosec B311

            # Personalized messages like v10
            self._announce_false_virtue(player, player.team_index)

        self.protections_pile.append(card)
        self._end_turn()

    def _discard_card(self, player: MileByMilePlayer, slot: int, card: Card) -> None:
        """Discard a card."""
        player.hand.pop(slot)

        # Safety cards go to protections to prevent reshuffling
        if card.card_type == CardType.SAFETY:
            self.protections_pile.append(card)
        else:
            self.discard_pile.append(card)

        self.broadcast_l("milebymile-discards", player=player.name)
        self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")  # nosec B311
        self._end_turn()

    # ==========================================================================
    # Deck Management
    # ==========================================================================

    def _draw_card(self, player: MileByMilePlayer) -> Card | None:
        """Draw a card for a player."""
        if self.deck.is_empty():
            if not self.discard_pile or not self.options.reshuffle_discard_pile:
                return None
            # Reshuffle discard pile
            self.deck.add_all(self.discard_pile)
            self.discard_pile = []
            self.deck.shuffle()
            self.broadcast_l("milebymile-deck-reshuffled")
            self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")  # nosec B311

        if self.options.rig_game == "No Duplicates":
            return self.deck.draw_non_duplicate(player.hand)
        return self.deck.draw()

    def _deal_initial_hands(self) -> None:
        """Deal initial hands to all players."""
        active_players = self.get_active_players()
        for player in active_players:
            player.hand = []
            for _ in range(HAND_SIZE):
                card = self._draw_card(player)
                if card:
                    player.hand.append(card)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def prestart_validate(self) -> list[str]:
        """Validate game configuration before starting."""
        errors = super().prestart_validate()

        # Always (re)set up teams so validation uses current player list
        self._setup_teams()

        # Validate team mode for current player count
        team_mode_error = self._validate_team_mode(self.options.team_mode)
        if team_mode_error:
            errors.append(team_mode_error)

        # Check karma rule requirement: need at least 3 teams/cars
        if self.options.karma_rule:
            num_teams = len(self._team_manager.teams)
            if num_teams < 3:
                errors.append("milebymile-error-karma-needs-three-teams")

        return errors

    def on_start(self) -> None:
        """Called when the game starts."""
        # Always set up teams with current player list
        self._setup_teams()
        self.status = "playing"
        self.game_active = True
        self.current_race = 0

        # Initialize turn order
        active_players = self.get_active_players()
        self.set_turn_players(active_players)

        # Play music and ambience
        self.play_music("game_milebymile/music.ogg")
        self.play_ambience("game_milebymile/amloop.ogg")

        # Start first race
        self._start_race()

    def _start_race(self) -> None:
        """Start a new race."""
        self.current_race += 1
        self.race_winner_team_index = None

        # Reset race states for new race
        for race_state in self.race_states:
            race_state.reset()

        # Build and shuffle deck
        attack_mult = 2 if self.options.rig_game == "2x Attacks" else 1
        defense_mult = 2 if self.options.rig_game == "2x Defenses" else 1
        self.deck = Deck()
        self.deck.build_standard_deck(
            attack_multiplier=attack_mult,
            defense_multiplier=defense_mult,
            include_karma_cards=self.options.karma_rule,
        )
        self.deck.shuffle()

        self.discard_pile = []
        self.protections_pile = []

        # Deal hands
        self._deal_initial_hands()

        # Play shuffle sound (like Scopa)
        shuffle_sound = random.choice(["shuffle1.ogg", "shuffle2.ogg", "shuffle3.ogg"])  # nosec B311
        self.play_sound(f"game_cards/{shuffle_sound}")
        self.broadcast_l("milebymile-new-race")

        # Start first turn
        self.reset_turn_order()
        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        # Clean up any leftover discard confirmation state
        self._pending_discard_slot.clear()
        for pid in list(self._pending_actions):
            if self._pending_actions.get(pid) == "discard_confirm":
                del self._pending_actions[pid]

        player = self.current_player
        if not player or not isinstance(player, MileByMilePlayer):
            return

        # Draw a card at start of turn
        card = self._draw_card(player)
        if card:
            player.hand.append(card)
            self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")  # nosec B311
            user = self.get_user(player)
            if user:
                card_name = self._get_localized_card_name(card, user.locale)
                user.speak_l("milebymile-you-drew", card=card_name, buffer="table")

        # Announce turn
        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))  # nosec B311

        self._update_all_turn_actions()
        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        # Don't process turns during countdown
        if self._round_timer.is_active:
            return

        # Check for race end
        if self.race_winner_team_index is not None:
            self._end_race()
            return

        # Check for deck exhaustion (when reshuffling is disabled)
        if self.deck.is_empty() and not self.options.reshuffle_discard_pile:
            # No cards left to draw and can't reshuffle - check if all hands empty
            all_empty = all(len(p.hand) == 0 for p in self.get_active_players())
            if all_empty:
                self._end_race()
                return

        # Advance to next player
        BotHelper.jolt_bots(self, ticks=random.randint(15, 25))  # nosec B311
        self.advance_turn(announce=False)
        self._start_turn()

    def _end_race(self) -> None:
        """End the current race and calculate scores."""
        # Find winner (team index with most miles if no one reached target)
        winning_team_idx: int | None = self.race_winner_team_index
        if winning_team_idx is None:
            # Find team with most miles
            max_miles = -1
            for team_idx, race_state in self.iter_teams():
                if race_state.miles > max_miles:
                    max_miles = race_state.miles
                    winning_team_idx = team_idx

        self.broadcast_l("milebymile-race-complete")

        # Calculate and announce scores
        self._calculate_race_scores(winning_team_idx)

        # Check for game winner
        game_winner = self._check_game_winner()
        if game_winner is not None:
            self._end_game(game_winner)
        else:
            # Start next race after delay (silent countdown)
            self._round_timer.start()
            # Disable all actions during countdown
            self._update_all_turn_actions()
            self.rebuild_all_menus()

    def on_round_timer_ready(self) -> None:
        """Called when round timer expires - start the next race."""
        self._start_race()

    def _calculate_race_scores(self, winning_team_idx: int | None) -> None:
        """Calculate and announce race scores."""
        from ...messages.localization import Localization

        for team_idx, race_state in self.iter_teams():
            base_miles = min(race_state.miles, self.options.round_distance)
            score = base_miles
            # Store bonus keys and their parameters for localization
            bonus_parts: list[tuple[str, dict]] = []  # (message_key, params)

            is_winner = team_idx == winning_team_idx
            if is_winner and race_state.miles >= self.options.round_distance:
                # Trip complete bonus
                score += 400
                bonus_parts.append(("milebymile-from-trip", {"points": 400}))

                # Perfect crossing (only if not forced)
                if not self.options.only_allow_perfect_crossing:
                    if race_state.miles == self.options.round_distance:
                        score += 200
                        bonus_parts.append(("milebymile-from-perfect", {"points": 200}))

                # Safe trip (no 200s)
                if not race_state.used_200_mile:
                    score += 300
                    bonus_parts.append(("milebymile-from-safe", {"points": 300}))

                # Shut out
                if all(rs.miles == 0 for i, rs in self.iter_teams() if i != team_idx):
                    score += 500
                    bonus_parts.append(("milebymile-from-shutout", {"points": 500}))

            # Safety bonuses (all teams)
            safety_count = len(race_state.safeties)
            if safety_count > 0:
                safety_bonus = safety_count * 100
                score += safety_bonus
                bonus_parts.append(
                    (
                        "milebymile-from-safeties",
                        {"points": safety_bonus, "count": safety_count},
                    )
                )

            # All 4 safeties bonus
            if safety_count == 4:
                score += 300
                bonus_parts.append(("milebymile-from-all-safeties", {"points": 300}))

            # Dirty trick bonuses
            if race_state.dirty_trick_count > 0:
                dt_bonus = race_state.dirty_trick_count * 300
                score += dt_bonus
                bonus_parts.append(
                    (
                        "milebymile-from-dirty-tricks",
                        {"points": dt_bonus, "count": race_state.dirty_trick_count},
                    )
                )

            self.set_team_round_score(team_idx, score)
            self.add_team_score(team_idx, score)

            # Announce to each player in their locale
            name = self.get_team_name(team_idx)
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                locale = user.locale

                # Build localized bonus descriptions
                bonus_descriptions = [
                    Localization.get(locale, "milebymile-from-distance", miles=base_miles)
                ]
                for key, params in bonus_parts:
                    bonus_descriptions.append(Localization.get(locale, key, **params))

                # Format list with babel via Localization wrapper
                breakdown = Localization.format_list_and(locale, bonus_descriptions)
                user.speak_l(
                    "milebymile-earned-points",
                    name=name,
                    score=score,
                    breakdown=breakdown,
                )

        # Announce total scores
        self.broadcast_l("milebymile-total-scores")
        for team_idx in range(self.get_num_teams()):
            name = self.get_team_name(team_idx)
            self.broadcast_l(
                "milebymile-team-score", name=name, score=self.get_team_score(team_idx)
            )

    def _check_game_winner(self) -> int | None:
        """Check if any team has won the game. Returns team index or None."""
        for team_idx in range(self.get_num_teams()):
            if self.get_team_score(team_idx) >= self.options.winning_score:
                # Find team with highest score
                best_idx = team_idx
                for other_idx in range(self.get_num_teams()):
                    if self.get_team_score(other_idx) > self.get_team_score(best_idx):
                        best_idx = other_idx
                return best_idx
        return None

    def _end_game(self, winner_idx: int) -> None:
        """End the game with a winner."""
        self.play_sound("game_pig/win.ogg")

        winner_team = self._team_manager.teams[winner_idx]
        winner_score = self.get_team_score(winner_idx)

        if self.is_individual_mode():
            self.broadcast_l("milebymile-wins-individual", player=winner_team.members[0])
        else:
            members_str = ", ".join(winner_team.members)
            self.broadcast_l("milebymile-wins-team", team=winner_idx + 1, members=members_str)
        self.broadcast_l("milebymile-final-score", score=winner_score)

        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with MileByMile-specific data."""
        # Sort teams by score descending
        team_scores = [(i, self.get_team_score(i)) for i in range(self.get_num_teams())]
        sorted_teams = sorted(team_scores, key=lambda t: t[1], reverse=True)

        # Build final scores
        final_scores = {}
        for team_idx, score in sorted_teams:
            name = self.get_team_name(team_idx)
            final_scores[name] = score

        winner_idx, winner_score = sorted_teams[0] if sorted_teams else (0, 0)
        winner_name = self.get_team_name(winner_idx)

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
                "winner_name": winner_name,
                "winner_score": winner_score,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "target_score": self.options.round_distance,
                "team_mode": self.options.team_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for MileByMile game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            points_str = Localization.get(locale, "game-points", count=score)
            lines.append(f"{i}. {name}: {points_str}")

        return lines

    def _get_player_by_name(self, name: str) -> MileByMilePlayer | None:
        """Get a player by name."""
        for player in self.players:
            if player.name == name:
                return player
        return None

    # ==========================================================================
    # Karma Announcements (personalized per player like v10)
    # ==========================================================================

    def _announce_karma_clash(
        self,
        attacker: MileByMilePlayer,
        attacker_team_idx: int,
        target_team_idx: int,
    ) -> None:
        """Announce when both attacker and target lose karma (attack neutralized)."""
        if self.is_individual_mode():
            target_team = self._team_manager.teams[target_team_idx]
            target_name = target_team.members[0]
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == attacker:
                    user.speak_l("milebymile-karma-clash-you-target", buffer="table")
                elif p.name == target_name:
                    user.speak_l(
                        "milebymile-karma-clash-you-attacker",
                        attacker=attacker.name,
                        buffer="table",
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-others",
                        attacker=attacker.name,
                        target=target_name,
                        buffer="table",
                    )
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-clash-your-team", buffer="table")
                elif p.team_index == target_team_idx:
                    user.speak_l(
                        "milebymile-karma-clash-target-team",
                        team=attacker_team_idx + 1,
                        buffer="table",
                    )
                else:
                    user.speak_l(
                        "milebymile-karma-clash-other-teams",
                        attacker=attacker_team_idx + 1,
                        target=target_team_idx + 1,
                        buffer="table",
                    )

    def _announce_attacker_shunned(
        self, attacker: MileByMilePlayer, attacker_team_idx: int
    ) -> None:
        """Announce when attacker loses karma for attacking."""
        if self.is_individual_mode():
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == attacker:
                    user.speak_l("milebymile-karma-shunned-you", buffer="table")
                else:
                    user.speak_l(
                        "milebymile-karma-shunned-other",
                        player=attacker.name,
                        buffer="table",
                    )
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == attacker_team_idx:
                    user.speak_l("milebymile-karma-shunned-your-team", buffer="table")
                else:
                    user.speak_l(
                        "milebymile-karma-shunned-other-team",
                        team=attacker_team_idx + 1,
                        buffer="table",
                    )

    def _announce_false_virtue(self, player: MileByMilePlayer, team_idx: int) -> None:
        """Announce when a player plays False Virtue to regain karma."""
        if self.is_individual_mode():
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p == player:
                    user.speak_l("milebymile-false-virtue-you", buffer="table")
                else:
                    user.speak_l(
                        "milebymile-false-virtue-other",
                        player=player.name,
                        buffer="table",
                    )
        else:
            for p in self.players:
                user = self.get_user(p)
                if not user:
                    continue
                if p.team_index == team_idx:
                    user.speak_l("milebymile-false-virtue-your-team", buffer="table")
                else:
                    user.speak_l(
                        "milebymile-false-virtue-other-team",
                        team=team_idx + 1,
                        buffer="table",
                    )

    def _broadcast_card_message(self, message_key: str, card: Card, **kwargs) -> None:
        """Broadcast a message with a localized card name to all players."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            card_name = self._get_localized_card_name(card, user.locale)
            user.speak_l(message_key, card=card_name, buffer="table", **kwargs)

    def _broadcast_safety_play_with_effect(
        self,
        player: MileByMilePlayer,
        card: Card,
        *,
        is_dirty_trick: bool,
    ) -> None:
        """Broadcast a safety play with a short explanation of its effect."""
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue

            card_name = self._get_localized_card_name(card, user.locale)
            effect = self._get_localized_safety_effect(card.value, user.locale)

            if p == player:
                key = (
                    "milebymile-you-play-dirty-trick-with-effect"
                    if is_dirty_trick
                    else "milebymile-you-play-safety-with-effect"
                )
                user.speak_l(key, card=card_name, effect=effect, buffer="table")
            else:
                key = (
                    "milebymile-player-plays-dirty-trick-with-effect"
                    if is_dirty_trick
                    else "milebymile-player-plays-safety-with-effect"
                )
                user.speak_l(
                    key,
                    player=player.name,
                    card=card_name,
                    effect=effect,
                    buffer="table",
                )

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        # Handle round timer
        self._round_timer.on_tick()

        # Handle dirty trick window
        if self.dirty_trick_window_ticks > 0:
            self.dirty_trick_window_ticks -= 1
            if self.dirty_trick_window_ticks <= 0:
                self.dirty_trick_window_team = None
                self.dirty_trick_window_hazard = None

        BotHelper.on_tick(self)

    def bot_think(self, player: MileByMilePlayer) -> str | None:
        """Bot AI decision making."""
        # Don't act during between-race countdown
        if self._round_timer.is_active:
            return None

        # Check for dirty trick opportunity first
        if self.dirty_trick_window_team is not None:
            if player.team_index == self.dirty_trick_window_team:
                hazard = self.dirty_trick_window_hazard
                blocking_safety = HAZARD_TO_SAFETY.get(hazard) if hazard else None
                if blocking_safety:
                    for card in player.hand:
                        if card.card_type == CardType.SAFETY and card.value == blocking_safety:
                            return "dirty_trick"

        # Not our turn? Skip
        if self.current_player != player:
            return None

        # Choose best card to play
        return self._bot_choose_card(player)

    def _bot_choose_card(self, player: MileByMilePlayer) -> str | None:
        """Bot card selection logic."""
        if not player.hand:
            return None

        race_state = self.get_player_race_state(player)
        if not race_state:
            return None

        target_distance = self.options.round_distance
        distance_needed = target_distance - race_state.miles
        is_endgame = distance_needed <= 200

        # Score each card
        best_slot = 0
        best_priority = -1

        for i, card in enumerate(player.hand):
            priority = self._bot_score_card(player, card, race_state, distance_needed, is_endgame)
            if priority > best_priority:
                best_priority = priority
                best_slot = i

        return f"card_slot_{best_slot + 1}"

    def _bot_score_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        race_state: RaceState,
        distance_needed: int,
        is_endgame: bool,
    ) -> int:
        """Score a card for bot decision making."""
        if card.card_type == CardType.DISTANCE:
            return self._bot_score_distance_card(player, card, distance_needed, is_endgame)
        if card.card_type == CardType.REMEDY:
            return self._bot_score_remedy_card(player, card, race_state)
        if card.card_type == CardType.SAFETY:
            return self._bot_score_safety_card(card, race_state, distance_needed, is_endgame)
        if card.card_type == CardType.HAZARD:
            return self._bot_score_hazard_card(player, card, race_state)
        if card.card_type == CardType.SPECIAL:
            return self._bot_score_special_card(card, race_state)
        return 100

    def _bot_score_distance_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        distance_needed: int,
        is_endgame: bool,
    ) -> int:
        if not self._can_play_card(player, card):
            return 100
        distance = card.distance
        if is_endgame:
            if distance == distance_needed:
                return 5000
            if distance > distance_needed:
                if self.options.only_allow_perfect_crossing:
                    return 50
                return 4000
            return 1000 + distance
        return 1000 + distance

    def _bot_score_remedy_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        race_state: RaceState,
    ) -> int:
        if card.value == RemedyType.ROLL and race_state.has_problem(HazardType.STOP):
            if not race_state.has_safety(SafetyType.RIGHT_OF_WAY):
                return 3000
        if card.value == RemedyType.END_OF_LIMIT and race_state.has_problem(HazardType.SPEED_LIMIT):
            return 2800
        if self._can_play_card(player, card):
            return 2500
        return 150

    def _bot_score_safety_card(
        self,
        card: Card,
        race_state: RaceState,
        distance_needed: int,
        is_endgame: bool,
    ) -> int:
        if race_state.has_safety(card.value):
            return 50
        if is_endgame and distance_needed <= 100:
            return 1500
        return 2000

    def _bot_score_hazard_card(
        self,
        player: MileByMilePlayer,
        card: Card,
        race_state: RaceState,
    ) -> int:
        if not self._can_play_card(player, card):
            return 200
        if self.options.karma_rule and race_state.has_karma:
            has_playable_distance = any(
                c.card_type == CardType.DISTANCE and self._can_play_card(player, c)
                for c in player.hand
            )
            if has_playable_distance:
                return 50
        return 800

    def _bot_score_special_card(self, card: Card, race_state: RaceState) -> int:
        if card.value == "false_virtue" and not race_state.has_karma:
            return 1800
        return 50
