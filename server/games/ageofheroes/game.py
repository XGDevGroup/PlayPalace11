"""
Age of Heroes Game Implementation for PlayPalace v11.

A civilization-building card game where tribes compete to build an empire of
five cities, complete their monument of culture, or be the last tribe standing.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, BoolOption, option_field
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState

from .cards import (
    Card,
    Deck,
    CardType,
    ResourceType,
    SpecialResourceType,
    EventType,
    MANDATORY_EVENTS,
    DISASTER_EVENTS,
    get_card_name,
    read_cards,
)
from .state import (
    Tribe,
    TribeState,
    WarState,
    TradeOffer,
    GamePhase,
    PlaySubPhase,
    ActionType,
    WarGoal,
    BuildingType,
    BUILDING_COSTS,
    TRIBE_SPECIAL_RESOURCE,
    DEFAULT_ARMY_SUPPLY,
    DEFAULT_CITY_SUPPLY,
    DEFAULT_FORTRESS_SUPPLY,
    DEFAULT_GENERAL_SUPPLY,
    DEFAULT_ROAD_SUPPLY,
    get_tribe_name,
    get_building_name,
    get_action_name,
    get_war_goal_name,
)
from .construction import (
    can_build,
    get_affordable_buildings,
    build,
    get_road_targets,
    build_road,
    execute_single_build,
    start_construction,
)
from .trading import (
    create_offer,
    cancel_offer,
    execute_trade,
    stop_trading,
    is_trading_complete,
    get_player_offers,
    get_matching_offers,
    can_accept_offer,
    announce_offer,
    check_and_execute_trades,
)
from .combat import (
    can_declare_war,
    get_valid_war_targets,
    get_valid_war_goals,
    declare_war,
    prepare_forces,
    resolve_battle_round,
    is_battle_over,
    get_battle_winner,
    apply_war_outcome,
    jolt_war_bots,
    resolve_war_round,
    execute_war_battle,
    finish_war_battle,
)
from . import bot as bot_ai
from . import events


# Hand size limit
MAX_HAND_SIZE = 5

# Trading timeout (30 seconds at ~20 ticks/second)
TRADING_TIMEOUT_TICKS = 600


@dataclass
class AgeOfHeroesPlayer(Player):
    """Player state for Age of Heroes."""

    hand: list[Card] = field(default_factory=list)
    tribe_state: TribeState | None = None

    # Setup phase
    dice_roll: int = 0  # Result of dice roll for turn order

    # Current turn state
    current_action: str | None = None  # ActionType being performed
    pending_discard: int = 0  # Cards that must be discarded

    # Trading state
    has_stopped_trading: bool = False  # Left the auction
    trading_ticks_waited: int = 0  # Ticks spent waiting for trades
    has_made_offers: bool = False  # Whether bot has made offers this phase
    pending_offer_card_index: int = -1  # Card selected to offer (-1 = none)

    # Construction state
    pending_road_targets: list[tuple[int, str]] = field(
        default_factory=list
    )  # Available neighbors for road
    declined_road_targets: list[int] = field(
        default_factory=list
    )  # Targets that declined during this construction action

    # War state
    pending_war_targets: list[tuple[int, "AgeOfHeroesPlayer"]] = field(
        default_factory=list
    )  # Available war targets
    pending_war_target_index: int = -1  # Selected war target (-1 = none)
    pending_war_goals: list[str] = field(
        default_factory=list
    )  # Available war goals for selected target
    pending_war_armies: int = 0  # Armies to commit
    pending_war_generals: int = 0  # Generals to commit
    pending_war_heroes_as_armies: int = 0  # Heroes to use as armies
    pending_war_heroes_as_generals: int = 0  # Heroes to use as generals

    # Disaster card state (Earthquake/Eruption targeting)
    pending_disaster_targets: list[tuple[int, "AgeOfHeroesPlayer"]] = field(
        default_factory=list
    )  # Available disaster targets
    pending_disaster_card_index: int = -1  # Index of disaster card being played (-1 = none)
    pending_disaster_type: str = ""  # Type of disaster (earthquake/eruption)


@dataclass
class AgeOfHeroesOptions(GameOptions):
    """Options for Age of Heroes game."""

    victory_cities: int = option_field(
        IntOption(
            default=5,
            min_val=3,
            max_val=7,
            value_key="cities",
            label="ageofheroes-set-victory-cities",
            prompt="ageofheroes-enter-victory-cities",
            change_msg="ageofheroes-option-changed-victory-cities",
        )
    )
    neighbor_roads_only: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="ageofheroes-toggle-neighbor-roads",
            change_msg="ageofheroes-option-changed-neighbor-roads",
        )
    )


@dataclass
@register_game
class AgeOfHeroesGame(Game):
    """
    Age of Heroes - A civilization-building card game.

    Players lead tribes competing to achieve victory through:
    - Building 5 cities (Empire of Five Cities)
    - Completing their monument with 5 special resources (Carriers of Great Culture)
    - Being the last tribe standing (The Most Persistent)
    """

    players: list[AgeOfHeroesPlayer] = field(default_factory=list)
    options: AgeOfHeroesOptions = field(default_factory=AgeOfHeroesOptions)

    # Game state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)

    # Phase tracking
    phase: str = GamePhase.SETUP
    sub_phase: str = ""
    current_day: int = 0  # Round counter
    day_start_turn_index: int = 0  # Who started the current day (for turn cycling)

    # Supply tracking (shared pool)
    army_supply: int = DEFAULT_ARMY_SUPPLY
    city_supply: int = DEFAULT_CITY_SUPPLY
    fortress_supply: int = DEFAULT_FORTRESS_SUPPLY
    general_supply: int = DEFAULT_GENERAL_SUPPLY
    road_supply: int = DEFAULT_ROAD_SUPPLY

    # Setup phase - track who has rolled
    setup_rolls: dict[str, int] = field(default_factory=dict)  # player_id -> dice total

    # War state
    war_state: WarState = field(default_factory=WarState)

    # Trading state
    trade_offers: list[TradeOffer] = field(default_factory=list)

    # Road building - pending request
    road_request_from: int = -1  # Player index requesting road
    road_request_to: int = -1  # Player index being asked

    @classmethod
    def get_name(cls) -> str:
        return "Age of Heroes"

    @classmethod
    def get_type(cls) -> str:
        return "ageofheroes"

    @classmethod
    def get_category(cls) -> str:
        return "category-uncategorized"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> AgeOfHeroesPlayer:
        """Create a new player with Age of Heroes-specific state."""
        return AgeOfHeroesPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Action Sets
    # ==========================================================================

    def create_turn_action_set(self, player: AgeOfHeroesPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        action_set = ActionSet(name="turn")

        # Setup phase - dice roll
        action_set.add(
            Action(
                id="roll_dice",
                label="Roll dice",
                handler="_action_roll_dice",
                is_enabled="_is_roll_dice_enabled",
                is_hidden="_is_roll_dice_hidden",
                get_label="_get_roll_dice_label",
            )
        )

        # War battle - roll dice for combat
        action_set.add(
            Action(
                id="war_roll_dice",
                label="Roll dice",
                handler="_action_war_roll_dice",
                is_enabled="_is_war_roll_enabled",
                is_hidden="_is_war_roll_hidden",
                get_label="_get_war_roll_label",
            )
        )

        # Continue button (used in various phases)
        action_set.add(
            Action(
                id="continue",
                label="Continue",
                handler="_action_continue",
                is_enabled="_is_continue_enabled",
                is_hidden="_is_continue_hidden",
                show_in_actions_menu=False,
            )
        )

        # Main play actions
        for action_type in ActionType:
            action_set.add(
                Action(
                    id=f"action_{action_type.value}",
                    label="",
                    handler="_action_select_main_action",
                    is_enabled="_is_main_action_enabled",
                    is_hidden="_is_main_action_hidden",
                    get_label="_get_main_action_label",
                    show_in_actions_menu=False,
                )
            )

        # Construction actions
        for building_type in BuildingType:
            action_set.add(
                Action(
                    id=f"build_{building_type.value}",
                    label="",
                    handler="_action_build_building",
                    is_enabled="_is_build_enabled",
                    is_hidden="_is_build_hidden",
                    get_label="_get_build_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="stop_building",
                label="Stop building",
                handler="_action_stop_building",
                is_enabled="_is_construction_menu_enabled",
                is_hidden="_is_construction_menu_hidden",
                get_label="_get_stop_building_label",
            )
        )

        # Road target selection actions (one per potential neighbor)
        for i in range(6):  # Max 6 players, so max 2 neighbors (left/right)
            action_set.add(
                Action(
                    id=f"road_target_{i}",
                    label="",
                    handler="_action_select_road_target",
                    is_enabled="_is_road_target_enabled",
                    is_hidden="_is_road_target_hidden",
                    get_label="_get_road_target_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="cancel_road",
                label="Cancel",
                handler="_action_cancel_road",
                is_enabled="_is_road_target_menu_enabled",
                is_hidden="_is_road_target_menu_hidden",
                get_label="_get_cancel_road_label",
            )
        )

        # Road permission actions (approve/deny)
        action_set.add(
            Action(
                id="approve_road",
                label="Approve",
                handler="_action_approve_road",
                is_enabled="_is_road_permission_enabled",
                is_hidden="_is_road_permission_hidden",
                get_label="_get_approve_road_label",
            )
        )
        action_set.add(
            Action(
                id="deny_road",
                label="Deny",
                handler="_action_deny_road",
                is_enabled="_is_road_permission_enabled",
                is_hidden="_is_road_permission_hidden",
                get_label="_get_deny_road_label",
            )
        )

        # War target selection actions (one per potential enemy)
        for i in range(6):  # Max 6 players
            action_set.add(
                Action(
                    id=f"war_target_{i}",
                    label="",
                    handler="_action_select_war_target",
                    is_enabled="_is_war_target_enabled",
                    is_hidden="_is_war_target_hidden",
                    get_label="_get_war_target_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="cancel_war_target",
                label="Cancel",
                handler="_action_cancel_war_target",
                is_enabled="_is_war_declare_menu_enabled",
                is_hidden="_is_cancel_war_target_hidden",
                get_label="_get_cancel_war_label",
            )
        )

        # War goal selection actions
        for goal in WarGoal:
            action_set.add(
                Action(
                    id=f"war_goal_{goal.value}",
                    label="",
                    handler="_action_select_war_goal",
                    is_enabled="_is_war_goal_enabled",
                    is_hidden="_is_war_goal_hidden",
                    get_label="_get_war_goal_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="cancel_war_goal",
                label="Cancel",
                handler="_action_cancel_war_goal",
                is_enabled="_is_war_declare_menu_enabled",
                is_hidden="_is_cancel_war_goal_hidden",
                get_label="_get_cancel_war_label",
            )
        )

        # War force selection actions (cycling buttons)
        action_set.add(
            Action(
                id="war_armies_cycle",
                label="",
                handler="_action_cycle_war_armies",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
                get_label="_get_war_armies_cycle_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="war_generals_cycle",
                label="",
                handler="_action_cycle_war_generals",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
                get_label="_get_war_generals_cycle_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="war_heroes_armies_cycle",
                label="",
                handler="_action_cycle_war_heroes_armies",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
                get_label="_get_war_heroes_armies_cycle_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="war_heroes_generals_cycle",
                label="",
                handler="_action_cycle_war_heroes_generals",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
                get_label="_get_war_heroes_generals_cycle_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="confirm_war_forces",
                label="",
                handler="_action_confirm_war_forces",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
                get_label="_get_confirm_war_forces_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="cancel_war_forces",
                label="Cancel",
                handler="_action_cancel_war_forces",
                is_enabled="_is_war_force_enabled",
                is_hidden="_is_war_force_hidden",
            )
        )

        # Trading actions
        action_set.add(
            Action(
                id="stop_trading",
                label="Stop Trading",
                handler="_action_stop_trading",
                is_enabled="_is_trading_enabled",
                is_hidden="_is_trading_hidden",
                get_label="_get_stop_trading_label",
            )
        )

        # Trade offer actions (one per potential card in hand)
        for i in range(10):  # Max potential hand size
            action_set.add(
                Action(
                    id=f"offer_card_{i}",
                    label="",
                    handler="_action_select_offer_card",
                    is_enabled="_is_offer_card_enabled",
                    is_hidden="_is_offer_card_hidden",
                    get_label="_get_offer_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Request selection actions (shown after selecting a card to offer)
        # Any card option
        action_set.add(
            Action(
                id="request_any",
                label="",
                handler="_action_select_request",
                is_enabled="_is_request_enabled",
                is_hidden="_is_request_menu_hidden",
                get_label="_get_request_label",
                show_in_actions_menu=False,
            )
        )

        # Standard resources (Iron, Wood, Grain, Stone, Gold)
        for i, resource in enumerate(ResourceType):
            action_set.add(
                Action(
                    id=f"request_resource_{i}",
                    label="",
                    handler="_action_select_request",
                    is_enabled="_is_request_enabled",
                    is_hidden="_is_request_menu_hidden",
                    get_label="_get_request_label",
                    show_in_actions_menu=False,
                )
            )

        # Own tribe's special resource
        action_set.add(
            Action(
                id="request_own_special",
                label="",
                handler="_action_select_request",
                is_enabled="_is_request_enabled",
                is_hidden="_is_request_menu_hidden",
                get_label="_get_request_label",
                show_in_actions_menu=False,
            )
        )

        # Event cards (Fortune, Olympics, Hero)
        for event in [EventType.FORTUNE, EventType.OLYMPICS, EventType.HERO]:
            action_set.add(
                Action(
                    id=f"request_event_{event.value}",
                    label="",
                    handler="_action_select_request",
                    is_enabled="_is_request_enabled",
                    is_hidden="_is_request_menu_hidden",
                    get_label="_get_request_label",
                    show_in_actions_menu=False,
                )
            )

        # Cancel offer selection
        action_set.add(
            Action(
                id="cancel_offer_selection",
                label="Cancel",
                handler="_action_cancel_offer_selection",
                is_enabled="_is_request_enabled",
                is_hidden="_is_request_menu_hidden",
                get_label="_get_cancel_offer_label",
            )
        )

        # Discard excess cards actions (one per potential card in hand)
        for i in range(10):  # Max potential hand size
            action_set.add(
                Action(
                    id=f"discard_card_{i}",
                    label="",
                    handler="_action_discard_card",
                    is_enabled="_is_discard_enabled",
                    is_hidden="_is_discard_card_hidden",
                    get_label="_get_discard_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Disaster card actions (Earthquake/Eruption) - one per potential card in hand
        for i in range(10):  # Max potential hand size
            action_set.add(
                Action(
                    id=f"play_earthquake_{i}",
                    label="",
                    handler="_action_play_disaster_card",
                    is_enabled="_is_disaster_card_enabled",
                    is_hidden="_is_disaster_card_hidden",
                    get_label="_get_disaster_card_label",
                    show_in_actions_menu=False,
                )
            )
            action_set.add(
                Action(
                    id=f"play_eruption_{i}",
                    label="",
                    handler="_action_play_disaster_card",
                    is_enabled="_is_disaster_card_enabled",
                    is_hidden="_is_disaster_card_hidden",
                    get_label="_get_disaster_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Disaster target selection actions (one per potential player)
        for i in range(6):  # Max 6 players
            action_set.add(
                Action(
                    id=f"disaster_target_{i}",
                    label="",
                    handler="_action_select_disaster_target",
                    is_enabled="_is_disaster_target_enabled",
                    is_hidden="_is_disaster_target_hidden",
                    get_label="_get_disaster_target_label",
                    show_in_actions_menu=False,
                )
            )
        action_set.add(
            Action(
                id="cancel_disaster",
                label="Cancel",
                handler="_action_cancel_disaster",
                is_enabled="_is_disaster_menu_enabled",
                is_hidden="_is_disaster_menu_hidden",
            )
        )

        # Status actions (keybind only)
        action_set.add(
            Action(
                id="check_status",
                label="Check status",
                handler="_action_check_status",
                is_enabled="_is_status_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_status_detailed",
                label="Detailed status",
                handler="_action_check_status_detailed",
                is_enabled="_is_status_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_hand",
                label="Check hand",
                handler="_action_check_hand",
                is_enabled="_is_status_enabled",
                is_hidden="_is_always_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Remove base class 's' and 'shift+s' keybinds before adding ours
        if "s" in self._keybinds:
            self._keybinds["s"] = []
        if "shift+s" in self._keybinds:
            self._keybinds["shift+s"] = []

        # Status keybinds
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
            "h",
            "Check hand",
            ["check_hand"],
            state=KeybindState.ACTIVE,
            include_spectators=False,
        )

    # ==========================================================================
    # Action Callbacks - Visibility/Enabled
    # ==========================================================================

    def _is_always_hidden(self, player: Player) -> Visibility:
        """Always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _is_status_enabled(self, player: Player) -> str | None:
        """Status is enabled once game starts."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        return None

    def _is_roll_dice_enabled(self, player: Player) -> str | None:
        """Roll dice is enabled in setup phase for players who haven't rolled."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.SETUP:
            return "ageofheroes-wrong-phase"
        if player.id in self.setup_rolls:
            return "ageofheroes-already-rolled"
        return None

    def _is_roll_dice_hidden(self, player: Player) -> Visibility:
        """Roll dice is visible only in setup phase."""
        if self.phase != GamePhase.SETUP:
            return Visibility.HIDDEN
        if player.id in self.setup_rolls:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_roll_dice_label(self, player: Player, action_id: str) -> str:
        """Get label for roll dice action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-roll-dice")

    def _is_war_roll_enabled(self, player: Player) -> str | None:
        """War roll is enabled during WAR_BATTLE subphase for participants who haven't rolled."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Not a valid player"
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.WAR_BATTLE:
            return "ageofheroes-wrong-phase"

        # Check if player is a combatant
        active_players = self.get_active_players()
        if player not in active_players:
            return "You are not in the game"
        player_index = active_players.index(player)
        war = self.war_state

        is_attacker = player_index == war.attacker_index
        is_defender = player_index == war.defender_index

        if not is_attacker and not is_defender:
            return "You are not involved in this war"

        # Check if player has already rolled
        if is_attacker and war.attacker_roll > 0:
            return "ageofheroes-already-rolled"
        if is_defender and war.defender_roll > 0:
            return "ageofheroes-already-rolled"

        return None

    def _is_war_roll_hidden(self, player: Player) -> Visibility:
        """War roll is visible only during WAR_BATTLE subphase for combatants."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.WAR_BATTLE:
            return Visibility.HIDDEN

        # Check if player is a combatant
        active_players = self.get_active_players()
        if player not in active_players:
            return Visibility.HIDDEN
        player_index = active_players.index(player)
        war = self.war_state

        is_attacker = player_index == war.attacker_index
        is_defender = player_index == war.defender_index

        if not is_attacker and not is_defender:
            return Visibility.HIDDEN

        # Hide if already rolled
        if is_attacker and war.attacker_roll > 0:
            return Visibility.HIDDEN
        if is_defender and war.defender_roll > 0:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_war_roll_label(self, player: Player, action_id: str) -> str:
        """Get label for war roll dice action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-war-roll-dice")

    def _is_continue_enabled(self, player: Player) -> str | None:
        """Continue is enabled at phase transitions."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        return None

    def _is_continue_hidden(self, player: Player) -> Visibility:
        """Continue is usually hidden."""
        return Visibility.HIDDEN

    def _is_main_action_enabled(self, player: Player, action_id: str = "") -> str | None:
        """Main actions are enabled during play phase action selection."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.SELECT_ACTION:
            return "ageofheroes-wrong-phase"
        if self.current_player != player:
            return "ageofheroes-not-your-turn"

        # Additional checks for specific actions
        if action_id == f"action_{ActionType.CONSTRUCTION}":
            if isinstance(player, AgeOfHeroesPlayer):
                from .construction import get_affordable_buildings

                affordable = get_affordable_buildings(self, player)
                if not affordable:
                    return "ageofheroes-no-resources"

        if action_id == f"action_{ActionType.WAR}":
            if isinstance(player, AgeOfHeroesPlayer):
                war_error = can_declare_war(self, player)
                if war_error:
                    return war_error

        return None

    def _is_main_action_hidden(self, player: Player) -> Visibility:
        """Main actions are visible during action selection."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.SELECT_ACTION:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_main_action_label(self, player: Player, action_id: str) -> str:
        """Get label for main action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        # Extract action type from action_id (e.g., "action_tax_collection" -> "tax_collection")
        action_type = action_id.replace("action_", "")
        return get_action_name(action_type, locale)

    def _is_trading_enabled(self, player: Player) -> str | None:
        """Trading is enabled during fair phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.FAIR:
            return "ageofheroes-wrong-phase"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if player.has_stopped_trading:
            return "ageofheroes-left-auction"
        return None

    def _is_trading_hidden(self, player: Player) -> Visibility:
        """Trading actions visible during fair phase."""
        if self.phase != GamePhase.FAIR:
            return Visibility.HIDDEN
        if isinstance(player, AgeOfHeroesPlayer):
            if player.has_stopped_trading:
                return Visibility.HIDDEN
            # Hide when in the middle of making an offer (showing request menu)
            if player.pending_offer_card_index >= 0:
                return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_stop_trading_label(self, player: Player, action_id: str) -> str:
        """Get label for stop trading action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-stop-trading")

    def _is_construction_menu_enabled(self, player: Player) -> str | None:
        """Construction menu actions enabled during construction phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.CONSTRUCTION:
            return "ageofheroes-wrong-phase"
        if self.current_player != player:
            return "ageofheroes-not-your-turn"
        return None

    def _is_construction_menu_hidden(self, player: Player) -> Visibility:
        """Construction menu visible during construction subphase."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.CONSTRUCTION:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_build_enabled(self, player: Player, action_id: str) -> str | None:
        """Building action enabled if player can afford it."""
        base_check = self._is_construction_menu_enabled(player)
        if base_check:
            return base_check

        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"

        # Extract building type from action_id
        building_type = action_id.replace("build_", "")

        # Check if player can build this
        from .construction import can_build

        if not can_build(self, player, building_type):
            return "ageofheroes-no-resources"

        return None

    def _is_build_hidden(self, player: Player, action_id: str) -> Visibility:
        """Building actions hidden outside construction subphase."""
        return self._is_construction_menu_hidden(player)

    def _get_build_label(self, player: Player, action_id: str) -> str:
        """Get label for build action with cost."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Extract building type from action_id
        building_type = action_id.replace("build_", "")
        building_name = get_building_name(building_type, locale)

        # Get cost string
        cost_key = f"ageofheroes-cost-{building_type}"
        cost_str = Localization.get(locale, cost_key)

        return f"{building_name} ({cost_str})"

    def _get_stop_building_label(self, player: Player, action_id: str) -> str:
        """Get label for stop building action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-construction-stop")

    def _is_road_target_menu_enabled(self, player: Player) -> str | None:
        """Road target menu actions enabled during road target selection."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.ROAD_TARGET:
            return "ageofheroes-wrong-phase"
        if self.current_player != player:
            return "ageofheroes-not-your-turn"
        return None

    def _is_road_target_menu_hidden(self, player: Player) -> Visibility:
        """Road target menu visible during road target subphase."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.ROAD_TARGET:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_road_target_enabled(self, player: Player, action_id: str) -> str | None:
        """Road target action enabled."""
        return self._is_road_target_menu_enabled(player)

    def _is_road_target_hidden(self, player: Player, action_id: str) -> Visibility:
        """Road target actions hidden outside road target subphase."""
        if self._is_road_target_menu_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN

        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN

        # Extract index from action_id
        try:
            target_index = int(action_id.replace("road_target_", ""))
        except ValueError:
            return Visibility.HIDDEN

        # Hide if index out of range
        if target_index >= len(player.pending_road_targets):
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_road_target_label(self, player: Player, action_id: str) -> str:
        """Get label for road target action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract index from action_id
        try:
            target_index = int(action_id.replace("road_target_", ""))
        except ValueError:
            return ""

        if target_index >= len(player.pending_road_targets):
            return ""

        neighbor_index, direction = player.pending_road_targets[target_index]
        active_players = self.get_active_players()
        if neighbor_index >= len(active_players):
            return ""

        neighbor = active_players[neighbor_index]
        if isinstance(neighbor, AgeOfHeroesPlayer) and neighbor.tribe_state:
            tribe_name = get_tribe_name(neighbor.tribe_state.tribe, locale)
            direction_str = Localization.get(locale, f"ageofheroes-direction-{direction}")
            return f"{neighbor.name} ({tribe_name}) - {direction_str}"

        return neighbor.name

    def _get_cancel_road_label(self, player: Player, action_id: str) -> str:
        """Get label for cancel road action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-cancel")

    def _is_road_permission_enabled(self, player: Player) -> str | None:
        """Road permission actions enabled during permission phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.ROAD_PERMISSION:
            return "ageofheroes-wrong-phase"

        # Only the target player can approve/deny
        active_players = self.get_active_players()
        try:
            player_index = active_players.index(player)
        except ValueError:
            return "ageofheroes-not-your-turn"

        if player_index != self.road_request_to:
            return "ageofheroes-not-your-turn"

        return None

    def _is_road_permission_hidden(self, player: Player) -> Visibility:
        """Road permission actions visible during permission phase."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.ROAD_PERMISSION:
            return Visibility.HIDDEN

        # Show to target player only
        active_players = self.get_active_players()
        try:
            player_index = active_players.index(player)
        except ValueError:
            return Visibility.HIDDEN

        if player_index != self.road_request_to:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_approve_road_label(self, player: Player, action_id: str) -> str:
        """Get label for approve road action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-approve")

    def _get_deny_road_label(self, player: Player, action_id: str) -> str:
        """Get label for deny road action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-deny")

    def _is_war_declare_menu_enabled(self, player: Player) -> str | None:
        """War declare menu actions enabled during war declaration phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return "ageofheroes-wrong-phase"
        if self.current_player != player:
            return "ageofheroes-not-your-turn"
        return None

    def _is_war_declare_menu_hidden(self, player: Player) -> Visibility:
        """War declare menu visible during war declare subphase."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_cancel_war_target_hidden(self, player: Player) -> Visibility:
        """Cancel war target visible only when selecting target."""
        if self._is_war_declare_menu_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        # Only show when selecting target (before goal selection)
        if player.pending_war_target_index >= 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_cancel_war_goal_hidden(self, player: Player) -> Visibility:
        """Cancel war goal visible only when selecting goal."""
        if self._is_war_declare_menu_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        # Only show when selecting goal (after target selected)
        if player.pending_war_target_index < 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_war_target_enabled(self, player: Player, action_id: str) -> str | None:
        """War target action enabled."""
        return self._is_war_declare_menu_enabled(player)

    def _is_war_target_hidden(self, player: Player, action_id: str) -> Visibility:
        """War target actions hidden outside war declare subphase or if not showing targets."""
        if self._is_war_declare_menu_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN

        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN

        # Hide if showing goal selection instead
        if player.pending_war_target_index >= 0:
            return Visibility.HIDDEN

        # Extract index from action_id
        try:
            target_index = int(action_id.replace("war_target_", ""))
        except ValueError:
            return Visibility.HIDDEN

        # Hide if index out of range
        if target_index >= len(player.pending_war_targets):
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_war_target_label(self, player: Player, action_id: str) -> str:
        """Get label for war target action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract index from action_id
        try:
            target_index = int(action_id.replace("war_target_", ""))
        except ValueError:
            return ""

        if target_index >= len(player.pending_war_targets):
            return ""

        enemy_index, enemy = player.pending_war_targets[target_index]
        if isinstance(enemy, AgeOfHeroesPlayer) and enemy.tribe_state:
            tribe_name = get_tribe_name(enemy.tribe_state.tribe, locale)
            return f"{enemy.name} ({tribe_name})"

        return enemy.name

    def _is_war_goal_enabled(self, player: Player, action_id: str) -> str | None:
        """War goal action enabled."""
        return self._is_war_declare_menu_enabled(player)

    def _is_war_goal_hidden(self, player: Player, action_id: str) -> Visibility:
        """War goal actions hidden outside war declare subphase or if not showing goals."""
        if self._is_war_declare_menu_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN

        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN

        # Hide if showing target selection instead
        if player.pending_war_target_index < 0:
            return Visibility.HIDDEN

        # Extract goal from action_id
        goal = action_id.replace("war_goal_", "")

        # Hide if not in available goals
        if goal not in player.pending_war_goals:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_war_goal_label(self, player: Player, action_id: str) -> str:
        """Get label for war goal action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Extract goal from action_id
        goal = action_id.replace("war_goal_", "")
        return get_war_goal_name(goal, locale)

    def _get_cancel_war_label(self, player: Player, action_id: str) -> str:
        """Get label for cancel war action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-cancel")

    def _is_war_force_enabled(self, player: Player) -> str | None:
        """War force selection actions enabled during force selection."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.PLAY:
            return "ageofheroes-wrong-phase"
        if self.sub_phase not in [
            PlaySubPhase.WAR_PREPARE_ATTACKER,
            PlaySubPhase.WAR_PREPARE_DEFENDER,
        ]:
            return "ageofheroes-wrong-phase"
        # Attacker makes selections during their turn, defender during attacker's turn
        if self.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER and self.current_player != player:
            return "ageofheroes-not-your-turn"
        if self.sub_phase == PlaySubPhase.WAR_PREPARE_DEFENDER:
            # Defender is the target of the war
            if not self.war_state or not isinstance(player, AgeOfHeroesPlayer):
                return "ageofheroes-not-your-turn"
            active_players = self.get_active_players()
            if self.war_state.defender_index >= len(active_players):
                return "ageofheroes-not-your-turn"
            if active_players[self.war_state.defender_index] != player:
                return "ageofheroes-not-your-turn"
        return None

    def _is_war_force_hidden(self, player: Player) -> Visibility:
        """War force selection visible during force selection."""
        if self.phase != GamePhase.PLAY:
            return Visibility.HIDDEN
        if self.sub_phase not in [
            PlaySubPhase.WAR_PREPARE_ATTACKER,
            PlaySubPhase.WAR_PREPARE_DEFENDER,
        ]:
            return Visibility.HIDDEN
        # Show to current player during attacker selection
        if self.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER and self.current_player != player:
            return Visibility.HIDDEN
        # Show to defender during defender selection
        if self.sub_phase == PlaySubPhase.WAR_PREPARE_DEFENDER:
            if not self.war_state or not isinstance(player, AgeOfHeroesPlayer):
                return Visibility.HIDDEN
            active_players = self.get_active_players()
            if self.war_state.defender_index >= len(active_players):
                return Visibility.HIDDEN
            if active_players[self.war_state.defender_index] != player:
                return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_war_armies_cycle_label(self, player: Player, action_id: str) -> str:
        """Get label for armies cycling action."""
        if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
            return "Armies: 0"
        return f"Armies: {player.pending_war_armies}"

    def _get_war_generals_cycle_label(self, player: Player, action_id: str) -> str:
        """Get label for generals cycling action."""
        if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
            return "Generals: 0"
        return f"Generals: {player.pending_war_generals}"

    def _get_war_heroes_armies_cycle_label(self, player: Player, action_id: str) -> str:
        """Get label for heroes as armies cycling action."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Hero Armies: 0"
        return f"Hero Armies: {player.pending_war_heroes_as_armies}"

    def _get_war_heroes_generals_cycle_label(self, player: Player, action_id: str) -> str:
        """Get label for heroes as generals cycling action."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Hero Generals: 0"
        return f"Hero Generals: {player.pending_war_heroes_as_generals}"

    def _get_confirm_war_forces_label(self, player: Player, action_id: str) -> str:
        """Get label for confirm forces action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if self.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER:
            return Localization.get(locale, "ageofheroes-war-attack")
        else:
            return Localization.get(locale, "ageofheroes-war-defend")

    def _is_offer_card_enabled(self, player: Player) -> str | None:
        """Offer card is enabled during fair phase if card can be offered."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.FAIR:
            return "ageofheroes-wrong-phase"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if player.has_stopped_trading:
            return "ageofheroes-left-auction"
        return None

    def _is_offer_card_hidden(self, player: Player, action_id: str) -> Visibility:
        """Offer card actions hidden if not in fair phase or card out of range."""
        if self.phase != GamePhase.FAIR:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if player.has_stopped_trading:
            return Visibility.HIDDEN

        # Hide card selection when a card is already selected (show request menu instead)
        if player.pending_offer_card_index >= 0:
            return Visibility.HIDDEN

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("offer_card_", ""))
        except ValueError:
            return Visibility.HIDDEN

        # Hide if card index out of range
        if card_index >= len(player.hand):
            return Visibility.HIDDEN

        # Check if card can be offered
        from .trading import can_offer_card

        error = can_offer_card(self, player, card_index)
        if error:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_offer_card_label(self, player: Player, action_id: str) -> str:
        """Get label for offer card action - just the card name."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("offer_card_", ""))
        except ValueError:
            return ""

        if card_index >= len(player.hand):
            return ""

        card = player.hand[card_index]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return get_card_name(card, locale)

    def _is_request_enabled(self, player: Player) -> str | None:
        """Request selection is enabled when a card is selected to offer."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if self.phase != GamePhase.FAIR:
            return "ageofheroes-wrong-phase"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if player.pending_offer_card_index < 0:
            return "No card selected"
        return None

    def _is_request_menu_hidden(self, player: Player, action_id: str) -> Visibility:
        """Request menu actions hidden if no card selected or not in fair phase."""
        if self.phase != GamePhase.FAIR:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN

        # Only show when a card is selected
        if player.pending_offer_card_index < 0:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_request_label(self, player: Player, action_id: str) -> str:
        """Get label for request action based on action_id."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Any card
        if action_id == "request_any":
            return Localization.get(locale, "ageofheroes-any-card")

        # Standard resources
        if action_id.startswith("request_resource_"):
            try:
                resource_index = int(action_id.replace("request_resource_", ""))
                resources = list(ResourceType)
                if resource_index < len(resources):
                    resource = resources[resource_index]
                    dummy_card = Card(id=-1, card_type=CardType.RESOURCE, subtype=resource)
                    return get_card_name(dummy_card, locale)
            except ValueError:
                pass
            return ""

        # Own tribe's special resource
        if action_id == "request_own_special":
            if isinstance(player, AgeOfHeroesPlayer) and player.tribe_state:
                special = player.tribe_state.get_special_resource()
                dummy_card = Card(id=-1, card_type=CardType.SPECIAL, subtype=special)
                return get_card_name(dummy_card, locale)
            return ""

        # Event cards
        if action_id.startswith("request_event_"):
            event_type = action_id.replace("request_event_", "")
            dummy_card = Card(id=-1, card_type=CardType.EVENT, subtype=event_type)
            return get_card_name(dummy_card, locale)

        return ""

    def _get_cancel_offer_label(self, player: Player, action_id: str) -> str:
        """Get label for cancel offer action."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "ageofheroes-cancel")

    def _is_discard_enabled(self, player: Player) -> str | None:
        """Discard is enabled when player has excess cards."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if player.pending_discard <= 0:
            return "No cards to discard"
        return None

    def _is_discard_card_hidden(self, player: Player, action_id: str) -> Visibility:
        """Discard card actions hidden if not in discard phase or card out of range."""
        if self.sub_phase != PlaySubPhase.DISCARD_EXCESS:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if player.pending_discard <= 0:
            return Visibility.HIDDEN

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("discard_card_", ""))
        except ValueError:
            return Visibility.HIDDEN

        # Hide if card index out of range
        if card_index >= len(player.hand):
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_discard_card_label(self, player: Player, action_id: str) -> str:
        """Get label for discard card action - just the card name."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("discard_card_", ""))
        except ValueError:
            return ""

        if card_index >= len(player.hand):
            return ""

        card = player.hand[card_index]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return get_card_name(card, locale)

    def _is_disaster_card_enabled(self, player: Player) -> str | None:
        """Disaster cards enabled during select action phase in round 2+."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if self.current_player != player:
            return "Not your turn"
        if self.sub_phase != PlaySubPhase.SELECT_ACTION:
            return "Wrong phase"
        if self.current_day <= 1:
            return "Disasters only playable from day 2 onward"
        return None

    def _is_disaster_card_hidden(self, player: Player, action_id: str) -> Visibility:
        """Disaster card actions hidden if not correct card or wrong phase."""
        if self.sub_phase != PlaySubPhase.SELECT_ACTION:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.current_day <= 1:
            return Visibility.HIDDEN

        # Extract disaster type and card index from action_id
        try:
            if action_id.startswith("play_earthquake_"):
                disaster_type = EventType.EARTHQUAKE
                card_index = int(action_id.replace("play_earthquake_", ""))
            elif action_id.startswith("play_eruption_"):
                disaster_type = EventType.ERUPTION
                card_index = int(action_id.replace("play_eruption_", ""))
            else:
                return Visibility.HIDDEN
        except ValueError:
            return Visibility.HIDDEN

        # Hide if card index out of range
        if card_index >= len(player.hand):
            return Visibility.HIDDEN

        # Hide if card at index is not the correct disaster type
        card = player.hand[card_index]
        if card.card_type != CardType.EVENT or card.subtype != disaster_type:
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_disaster_card_label(self, player: Player, action_id: str) -> str:
        """Get label for disaster card action - 'Play [card name]'."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract card index from action_id
        try:
            if action_id.startswith("play_earthquake_"):
                card_index = int(action_id.replace("play_earthquake_", ""))
            elif action_id.startswith("play_eruption_"):
                card_index = int(action_id.replace("play_eruption_", ""))
            else:
                return ""
        except ValueError:
            return ""

        if card_index >= len(player.hand):
            return ""

        card = player.hand[card_index]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        card_name = get_card_name(card, locale)
        play_text = Localization.get(locale, "ageofheroes-play")
        return f"{play_text} {card_name}"

    def _is_disaster_target_enabled(self, player: Player) -> str | None:
        """Disaster target selection enabled during disaster target phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if self.current_player != player:
            return "Not your turn"
        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return "Wrong phase"
        return None

    def _is_disaster_target_hidden(self, player: Player, action_id: str) -> Visibility:
        """Disaster target actions hidden if not in disaster target phase or out of range."""
        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN

        # Extract target index from action_id
        try:
            target_index = int(action_id.replace("disaster_target_", ""))
        except ValueError:
            return Visibility.HIDDEN

        # Hide if target index out of range
        if target_index >= len(player.pending_disaster_targets):
            return Visibility.HIDDEN

        return Visibility.VISIBLE

    def _get_disaster_target_label(self, player: Player, action_id: str) -> str:
        """Get label for disaster target action - target player name."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return ""

        # Extract target index from action_id
        try:
            target_index = int(action_id.replace("disaster_target_", ""))
        except ValueError:
            return ""

        if target_index >= len(player.pending_disaster_targets):
            return ""

        _, target = player.pending_disaster_targets[target_index]
        return target.name

    def _is_disaster_menu_enabled(self, player: Player) -> str | None:
        """Disaster menu actions enabled during disaster target phase."""
        if self.status != "playing":
            return "ageofheroes-game-not-started"
        if not isinstance(player, AgeOfHeroesPlayer):
            return "Invalid player"
        if self.current_player != player:
            return "Not your turn"
        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return "Wrong phase"
        return None

    def _is_disaster_menu_hidden(self, player: Player, action_id: str) -> Visibility:
        """Disaster menu actions hidden if not in disaster target phase."""
        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return Visibility.HIDDEN
        if not isinstance(player, AgeOfHeroesPlayer):
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_roll_dice(self, player: Player, action_id: str) -> None:
        """Handle dice roll for turn order in setup phase."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        # Roll two dice
        die1 = random.randint(1, 6)  # nosec B311
        die2 = random.randint(1, 6)  # nosec B311
        total = die1 + die2
        player.dice_roll = total
        self.setup_rolls[player.id] = total

        # Play dice sound
        self.play_sound("game_pig/dice.ogg")

        # Announce result
        user = self.get_user(player)
        if user:
            user.speak_l(
                "ageofheroes-dice-result", total=total, die1=die1, die2=die2, buffer="table"
            )

        # Announce to others
        for p in self.players:
            if p != player:
                other_user = self.get_user(p)
                if other_user:
                    other_user.speak_l(
                        "ageofheroes-dice-result-other",
                        player=player.name,
                        total=total,
                        buffer="table",
                    )

        # Check if all players have rolled
        if len(self.setup_rolls) == len(self.get_active_players()):
            self._resolve_setup_rolls()

        self.rebuild_all_menus()

    def _action_war_roll_dice(self, player: Player, action_id: str) -> None:
        """Handle dice roll for war battle."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        # Roll dice using combat system
        from .combat import player_roll_war_dice

        player_roll_war_dice(self, player)

        # Check if both players have rolled
        if self.war_state.is_both_rolled():
            resolve_war_round(self)

        self.rebuild_all_menus()

    def _resolve_setup_rolls(self) -> None:
        """Resolve setup dice rolls and determine turn order."""
        active_players = self.get_active_players()

        # Find highest roll
        max_roll = max(self.setup_rolls.values())
        winners = [p for p in active_players if self.setup_rolls.get(p.id, 0) == max_roll]

        if len(winners) > 1:
            # Tie - need to reroll
            self.broadcast_l("ageofheroes-dice-tie", total=max_roll)
            # Clear rolls for tied players
            for p in winners:
                del self.setup_rolls[p.id]
                p.dice_roll = 0
            # Jolt bots to reroll
            for p in winners:
                if p.is_bot:
                    BotHelper.jolt_bot(p, ticks=random.randint(20, 30))  # nosec B311
        else:
            # We have a winner - they go first
            first_player = winners[0]

            # Announce
            for p in self.players:
                user = self.get_user(p)
                if user:
                    if p == first_player:
                        user.speak_l("ageofheroes-first-player-you", total=max_roll, buffer="table")
                    else:
                        user.speak_l(
                            "ageofheroes-first-player",
                            player=first_player.name,
                            total=max_roll,
                            buffer="table",
                        )

            # Set turn order starting with winner
            self.set_turn_players(active_players)
            first_index = active_players.index(first_player)
            self.turn_index = first_index
            self.day_start_turn_index = first_index  # Track who starts each day

            # Deal initial hands (5 cards each)
            self._deal_initial_hands()

            # Move to prepare phase
            self._start_prepare_phase()

    def _action_continue(self, player: Player, action_id: str) -> None:
        """Handle continue button press."""
        # Used for phase transitions when player acknowledgment is needed
        pass

    def _action_select_main_action(self, player: Player, action_id: str) -> None:
        """Handle main action selection in play phase."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        # Extract action type from action_id
        action_type = action_id.replace("action_", "")
        player.current_action = action_type

        if action_type == ActionType.TAX_COLLECTION:
            self._perform_tax_collection(player)
        elif action_type == ActionType.CONSTRUCTION:
            start_construction(self, player)
        elif action_type == ActionType.WAR:
            self._start_war_declaration(player)
        elif action_type == ActionType.DO_NOTHING:
            self._perform_do_nothing(player)

    def _action_check_status(self, player: Player, action_id: str) -> None:
        """Show basic status for all players."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        for p in self.get_active_players():
            if not isinstance(p, AgeOfHeroesPlayer) or not p.tribe_state:
                continue

            ts = p.tribe_state
            tribe_name = get_tribe_name(ts.tribe, locale)
            user.speak_l(
                "ageofheroes-status",
                player=p.name,
                tribe=tribe_name,
                cities=ts.cities,
                armies=ts.get_available_armies(),
                monument=ts.monument_progress,
            )

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        """Show player's hand with grouped card counts."""
        user = self.get_user(player)
        if not user or not isinstance(player, AgeOfHeroesPlayer):
            return

        locale = user.locale

        if not player.hand:
            user.speak_l("ageofheroes-hand-empty")
            return

        # Group cards by type and subtype
        from collections import defaultdict

        card_counts: dict[tuple[str, str], int] = defaultdict(int)

        for card in player.hand:
            card_counts[(card.card_type, card.subtype)] += 1

        # Sort by card type, then subtype
        sorted_cards = sorted(card_counts.items(), key=lambda x: (x[0][0], x[0][1]))

        # Build the display string
        card_parts = []
        for (card_type, subtype), count in sorted_cards:
            dummy_card = Card(id=-1, card_type=card_type, subtype=subtype)
            card_name = get_card_name(dummy_card, locale)
            if count > 1:
                card_parts.append(f"{count} {card_name}")
            else:
                card_parts.append(card_name)

        hand_str = ", ".join(card_parts)
        user.speak_l("ageofheroes-hand-contents", cards=hand_str, count=len(player.hand))

    def _action_check_status_detailed(self, player: Player, action_id: str) -> None:
        """Show detailed status in a status box."""
        user = self.get_user(player)
        if not user:
            return

        locale = user.locale
        lines = []

        for p in self.get_active_players():
            if not isinstance(p, AgeOfHeroesPlayer) or not p.tribe_state:
                continue

            ts = p.tribe_state
            tribe_name = get_tribe_name(ts.tribe, locale)

            # Build road string
            road_parts = []
            if ts.road_left:
                road_parts.append(Localization.get(locale, "ageofheroes-status-road-left"))
            if ts.road_right:
                road_parts.append(Localization.get(locale, "ageofheroes-status-road-right"))
            road_str = (
                ", ".join(road_parts)
                if road_parts
                else Localization.get(locale, "ageofheroes-status-none")
            )

            # Build status line
            line = f"{p.name} ({tribe_name}): "
            line += f"{ts.cities} cities, "
            line += f"{ts.get_available_armies()} armies, "
            line += f"{ts.generals} generals, "
            line += f"{ts.fortresses} fortresses, "
            line += f"{ts.monument_progress}/5 monument, "
            line += f"Roads: {road_str}"

            if ts.earthquaked_armies > 0:
                line += f", {ts.earthquaked_armies} recovering"
            if ts.returning_armies > 0:
                line += f", {ts.returning_armies} returning"

            lines.append(line)

        self.status_box(player, lines)

    # ==========================================================================
    # Game Flow
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True

        # Assign tribes to players
        self._assign_tribes()

        # Build deck based on player count
        self.deck.build_standard_deck(len(self.get_active_players()))
        self.deck.shuffle()

        # Initialize supply based on player count
        self._initialize_supply()

        # Start setup phase
        self.phase = GamePhase.SETUP
        self.setup_rolls = {}

        # Tell players their tribes
        for player in self.get_active_players():
            if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
                continue

            user = self.get_user(player)
            if user:
                locale = user.locale
                tribe_name = get_tribe_name(player.tribe_state.tribe, locale)
                special = player.tribe_state.get_special_resource()
                special_name = get_card_name(
                    Card(id=-1, card_type=CardType.SPECIAL, subtype=special), locale
                )
                user.speak_l("ageofheroes-setup-start", tribe=tribe_name, special=special_name)

        # Play music
        self.play_music("game_ageofheroes/music.ogg")

        # Jolt bots to roll dice
        for p in self.get_active_players():
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(20, 40))  # nosec B311

        self.rebuild_all_menus()

    def _assign_tribes(self) -> None:
        """Assign tribes to players."""
        active_players = self.get_active_players()
        tribes = list(Tribe)[: len(active_players)]
        random.shuffle(tribes)

        for i, player in enumerate(active_players):
            if isinstance(player, AgeOfHeroesPlayer):
                player.tribe_state = TribeState(tribe=tribes[i])

    def _initialize_supply(self) -> None:
        """Initialize building supply based on player count."""
        # Standard supply works for 2-6 players
        self.army_supply = DEFAULT_ARMY_SUPPLY
        self.city_supply = DEFAULT_CITY_SUPPLY
        self.fortress_supply = DEFAULT_FORTRESS_SUPPLY
        self.general_supply = DEFAULT_GENERAL_SUPPLY
        self.road_supply = DEFAULT_ROAD_SUPPLY

    def _deal_initial_hands(self) -> None:
        """Deal initial hands to all players."""
        for player in self.get_active_players():
            if isinstance(player, AgeOfHeroesPlayer):
                player.hand = self._draw_cards(MAX_HAND_SIZE)
                # Tell player their cards
                user = self.get_user(player)
                if user:
                    cards_str = read_cards(player.hand, user.locale)
                    user.speak(f"Your cards: {cards_str}")

    def _draw_cards(self, count: int) -> list[Card]:
        """Draw cards from deck, reshuffling discard pile if needed."""
        drawn = []
        for _ in range(count):
            card = self._draw_one()
            if card:
                drawn.append(card)
        return drawn

    def _draw_one(self) -> Card | None:
        """Draw a single card, reshuffling discard pile if needed."""
        if self.deck.is_empty() and self.discard_pile:
            # Reshuffle discard pile into deck
            self.deck.add_all(self.discard_pile)
            self.discard_pile = []
            self.deck.shuffle()
            self.broadcast_l("ageofheroes-deck-reshuffled")
        return self.deck.draw_one()

    def _start_prepare_phase(self) -> None:
        """Start the preparation phase."""
        self.phase = GamePhase.PREPARE
        self.broadcast_l("ageofheroes-prepare-start")

        # Process mandatory events for all players
        self._process_prepare_phase()

    def _process_prepare_phase(self) -> None:
        """Process the preparation phase - play events and discard disasters."""
        # For simplicity, auto-process events in order
        # Population Growth -> apply immediately
        # Disasters -> discard
        for player in self.get_active_players():
            if not isinstance(player, AgeOfHeroesPlayer):
                continue

            events.process_player_events(self, player)

        # After all events processed, move to fair phase
        self._start_fair_phase()

    def _broadcast_discard(self, player: AgeOfHeroesPlayer, card: Card) -> None:
        """Broadcast card discard to other players."""
        for p in self.players:
            if p == player:
                continue
            user = self.get_user(p)
            if user:
                card_name = get_card_name(card, user.locale)
                user.speak_l("ageofheroes-discard-card", player=player.name, card=card_name)

    def _start_fair_phase(self) -> None:
        """Start the fair/trading phase."""
        self.phase = GamePhase.FAIR
        self.trade_offers = []

        # Reset trading state
        for player in self.get_active_players():
            if isinstance(player, AgeOfHeroesPlayer):
                player.has_stopped_trading = False
                player.trading_ticks_waited = 0
                player.has_made_offers = False
                player.pending_offer_card_index = -1

        # Players draw cards based on road network
        self._distribute_fair_cards()

        self.broadcast_l("ageofheroes-fair-start")
        self.broadcast_l("ageofheroes-auction-start")

        # Rebuild menus to show trading actions
        self.rebuild_all_menus()

        # Check if trading is already complete (all bots auto-stop)
        self._check_trading_complete()

    def _distribute_fair_cards(self) -> None:
        """Distribute cards based on road networks."""
        for player in self.get_active_players():
            if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
                continue

            # Count connected tribes via roads
            total_cards = self._count_road_network(player)

            # First card is always drawn (base card, not from roads)
            base_cards = 1
            road_cards = total_cards - 1  # Additional cards from road network

            # Draw all cards
            if total_cards > 0:
                drawn = self._draw_cards(total_cards)
                player.hand.extend(drawn)

                user = self.get_user(player)
                if user:
                    # Announce base card draw
                    user.speak_l("ageofheroes-fair-draw-base", count=base_cards)

                    # Announce additional road cards if any
                    if road_cards > 0:
                        user.speak_l("ageofheroes-fair-draw-roads", count=road_cards)

                # Announce to others
                for p in self.players:
                    if p != player:
                        other_user = self.get_user(p)
                        if other_user:
                            other_user.speak_l(
                                "ageofheroes-fair-draw-other",
                                player=player.name,
                                count=total_cards,
                            )

    def _count_road_network(self, player: AgeOfHeroesPlayer) -> int:
        """Count how many tribes are connected via road network."""
        if not player.tribe_state:
            return 1

        active_players = self.get_active_players()
        player_index = active_players.index(player)
        visited = {player_index}
        count = 1

        # Check left connections
        current = player_index
        while True:
            current_player = active_players[current]
            if not isinstance(current_player, AgeOfHeroesPlayer):
                break
            if not current_player.tribe_state:
                break
            if not current_player.tribe_state.road_left:
                break

            # Move to left neighbor (circular)
            left_index = (current - 1) % len(active_players)
            if left_index in visited:
                break
            visited.add(left_index)
            count += 1
            current = left_index

        # Check right connections
        current = player_index
        while True:
            current_player = active_players[current]
            if not isinstance(current_player, AgeOfHeroesPlayer):
                break
            if not current_player.tribe_state:
                break
            if not current_player.tribe_state.road_right:
                break

            # Move to right neighbor (circular)
            right_index = (current + 1) % len(active_players)
            if right_index in visited:
                break
            visited.add(right_index)
            count += 1
            current = right_index

        return count

    def _check_trading_complete(self) -> None:
        """Check if trading phase is complete and advance if so."""
        if self.phase != GamePhase.FAIR:
            return

        # Count active traders
        active_traders = 0
        for player in self.get_active_players():
            if isinstance(player, AgeOfHeroesPlayer):
                if not player.has_stopped_trading:
                    active_traders += 1

        # End trading if all stopped or only one remains
        if active_traders <= 1:
            self._start_play_phase()

    def _action_stop_trading(self, player: Player, action_id: str) -> None:
        """Handle stop trading action."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.phase != GamePhase.FAIR:
            return

        if player.has_stopped_trading:
            return

        # Mark player as stopped
        stop_trading(self, player)

        # Announce
        self.broadcast_personal_l(
            player, "ageofheroes-left-auction-you", "ageofheroes-left-auction"
        )

        # Check if trading is complete
        self._check_trading_complete()

    def _action_build_building(self, player: Player, action_id: str) -> None:
        """Handle building construction."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.CONSTRUCTION:
            return

        # Extract building type from action_id
        building_type = action_id.replace("build_", "")

        # Handle road building specially (needs neighbor selection)
        if building_type == BuildingType.ROAD:
            targets = get_road_targets(self, player)
            if not targets:
                user = self.get_user(player)
                if user:
                    user.speak_l("ageofheroes-road-no-target")
                self.sub_phase = PlaySubPhase.SELECT_ACTION
                self.rebuild_all_menus()
                return

            # Show road target selection menu
            player.pending_road_targets = targets
            self.sub_phase = PlaySubPhase.ROAD_TARGET
            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-road-select-neighbor")
            self.rebuild_all_menus()
            return

        # Build the selected building using shared logic
        success = execute_single_build(self, player, building_type, auto_road=False)

        if not success:
            # Build failed or victory occurred
            if player.tribe_state:  # Only end if not victory
                self.sub_phase = PlaySubPhase.SELECT_ACTION
                self.rebuild_all_menus()
                self._end_action(player)
            return

        # Check if player can still build more things
        from .construction import get_affordable_buildings

        available = get_affordable_buildings(self, player)

        if available:
            # Stay in construction mode - player can build more
            self.rebuild_all_menus()
            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-construction-menu")
        else:
            # No more buildings available - end action
            self.sub_phase = PlaySubPhase.SELECT_ACTION
            self.rebuild_all_menus()
            self._end_action(player)

    def _action_stop_building(self, player: Player, action_id: str) -> None:
        """Handle canceling construction."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.CONSTRUCTION:
            return

        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-construction-stopped")

        # Return to action selection and end turn
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()
        self._end_action(player)

    def _action_select_road_target(self, player: Player, action_id: str) -> None:
        """Handle road target selection - requests permission from neighbor."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.ROAD_TARGET:
            return

        # Extract index from action_id
        try:
            target_index_in_list = int(action_id.replace("road_target_", ""))
        except ValueError:
            return

        if target_index_in_list >= len(player.pending_road_targets):
            return

        target_index, direction = player.pending_road_targets[target_index_in_list]

        # Store the road request (builder and target)
        active_players = self.get_active_players()
        builder_index = active_players.index(player)
        self.road_request_from = builder_index
        self.road_request_to = target_index

        # Enter permission phase
        self.sub_phase = PlaySubPhase.ROAD_PERMISSION

        # Notify players
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-road-request-sent")

        if target_index < len(active_players):
            target_player = active_players[target_index]
            target_user = self.get_user(target_player)
            if target_user:
                target_user.speak_l("ageofheroes-road-request-received", requester=player.name)

        self.rebuild_all_menus()

    def _action_cancel_road(self, player: Player, action_id: str) -> None:
        """Handle canceling road target selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.ROAD_TARGET:
            return

        # Clear pending targets
        player.pending_road_targets = []

        # Return to construction menu
        self.sub_phase = PlaySubPhase.CONSTRUCTION
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-construction-menu")
        self.rebuild_all_menus()

    def _action_approve_road(self, player: Player, action_id: str) -> None:
        """Handle approving road request."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.ROAD_PERMISSION:
            return

        active_players = self.get_active_players()

        # Verify this player is the target
        player_index = active_players.index(player)
        if player_index != self.road_request_to:
            return

        # Get builder
        if self.road_request_from < 0 or self.road_request_from >= len(active_players):
            return
        builder = active_players[self.road_request_from]
        if not isinstance(builder, AgeOfHeroesPlayer) or not builder.tribe_state:
            return

        # Determine direction
        direction = None
        for target_index, target_direction in builder.pending_road_targets:
            if target_index == player_index:
                direction = target_direction
                break

        if not direction:
            return

        # Spend resources and build road
        from .construction import spend_resources, build_road, get_affordable_buildings

        spend_resources(builder, BUILDING_COSTS[BuildingType.ROAD], self.discard_pile)
        self.road_supply -= 1
        build_road(self, builder, player_index, direction)

        # Clear pending targets, declined targets, and request
        builder.pending_road_targets = []
        builder.declined_road_targets = []
        self.road_request_from = -1
        self.road_request_to = -1

        # Return to SELECT_ACTION subphase
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()

        # If builder is a bot, resume construction
        if builder.is_bot:
            from .construction import get_affordable_buildings

            available = get_affordable_buildings(self, builder)
            if available:
                # Continue building
                bot_ai.bot_perform_construction(self, builder)
            else:
                # No more resources to build
                self._end_action(builder)
        else:
            # For human players, check if they can still build
            available = get_affordable_buildings(self, builder)
            if available:
                # Show construction menu again
                self.sub_phase = PlaySubPhase.CONSTRUCTION
                self.rebuild_all_menus()
                builder_user = self.get_user(builder)
                if builder_user:
                    builder_user.speak_l("ageofheroes-construction-menu")
            else:
                # No more buildings available - end action
                self._end_action(builder)

    def _action_deny_road(self, player: Player, action_id: str) -> None:
        """Handle denying road request."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.ROAD_PERMISSION:
            return

        active_players = self.get_active_players()

        # Verify this player is the target
        player_index = active_players.index(player)
        if player_index != self.road_request_to:
            return

        # Get builder
        if self.road_request_from < 0 or self.road_request_from >= len(active_players):
            return
        builder = active_players[self.road_request_from]

        # Notify
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-road-request-denied-you")
        builder_user = self.get_user(builder)
        if builder_user:
            builder_user.speak_l("ageofheroes-road-request-denied", denier=player.name)

        # Track that this target declined so bot won't ask them again during this construction action
        if isinstance(builder, AgeOfHeroesPlayer):
            builder.declined_road_targets.append(player_index)
            builder.pending_road_targets = []
        self.road_request_from = -1
        self.road_request_to = -1

        # Return to SELECT_ACTION subphase
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()

        # If builder is a bot, resume construction (or end action)
        if builder.is_bot and isinstance(builder, AgeOfHeroesPlayer):
            from .construction import get_affordable_buildings

            available = get_affordable_buildings(self, builder)
            if available:
                # Continue building
                bot_ai.bot_perform_construction(self, builder)
            else:
                # No more resources to build
                self._end_action(builder)
        else:
            # For human players, return to construction menu
            available = (
                get_affordable_buildings(self, builder)
                if isinstance(builder, AgeOfHeroesPlayer)
                else []
            )
            if available:
                self.sub_phase = PlaySubPhase.CONSTRUCTION
                self.rebuild_all_menus()
                if builder_user:
                    builder_user.speak_l("ageofheroes-construction-menu")
            else:
                # No more resources
                if isinstance(builder, AgeOfHeroesPlayer):
                    self._end_action(builder)

    def _action_select_war_target(self, player: Player, action_id: str) -> None:
        """Handle war target selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return

        # Extract index from action_id
        try:
            target_index_in_list = int(action_id.replace("war_target_", ""))
        except ValueError:
            return

        if target_index_in_list >= len(player.pending_war_targets):
            return

        enemy_index, enemy = player.pending_war_targets[target_index_in_list]

        # Store selected target
        player.pending_war_target_index = enemy_index

        # Get valid goals for this target
        player.pending_war_goals = get_valid_war_goals(self, player, enemy)

        if not player.pending_war_goals:
            # No valid goals - shouldn't happen
            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-war-no-valid-goal")
            player.pending_war_target_index = -1
            player.pending_war_targets = []
            self.sub_phase = PlaySubPhase.SELECT_ACTION
            self.rebuild_all_menus()
            return

        # Show goal selection menu
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-war-select-goal")
        self.rebuild_all_menus()

    def _action_select_war_goal(self, player: Player, action_id: str) -> None:
        """Handle war goal selection and initiate war."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return

        if player.pending_war_target_index < 0:
            return

        # Extract goal from action_id
        goal = action_id.replace("war_goal_", "")

        if goal not in player.pending_war_goals:
            return

        # Get the target
        active_players = self.get_active_players()
        if player.pending_war_target_index >= len(active_players):
            return

        defender = active_players[player.pending_war_target_index]
        if not isinstance(defender, AgeOfHeroesPlayer):
            return

        # Store target index before clearing
        target_index = player.pending_war_target_index

        # Clear pending war state
        player.pending_war_targets = []
        player.pending_war_target_index = -1
        player.pending_war_goals = []

        # Declare war
        if not declare_war(self, player, target_index, goal):
            # Failed to declare war
            self.sub_phase = PlaySubPhase.SELECT_ACTION
            self.rebuild_all_menus()
            return

        # Initialize attacker's force selection with defaults (all available)
        if player.tribe_state:
            player.pending_war_armies = player.tribe_state.get_available_armies()
            player.pending_war_generals = player.tribe_state.get_available_generals()
            # Count hero cards
            hero_count = sum(
                1
                for card in player.hand
                if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
            )
            # Default: use heroes as armies
            player.pending_war_heroes_as_armies = hero_count
            player.pending_war_heroes_as_generals = 0

        # Enter attacker force selection phase
        self.sub_phase = PlaySubPhase.WAR_PREPARE_ATTACKER
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-war-prepare-attack")
        self.rebuild_all_menus()

    def _action_cancel_war_target(self, player: Player, action_id: str) -> None:
        """Handle canceling war target selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return

        # Only cancel if showing target selection
        if player.pending_war_target_index >= 0:
            return

        # Clear pending war state
        player.pending_war_targets = []
        player.pending_war_target_index = -1
        player.pending_war_goals = []

        # Return to action selection
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()

    def _action_cancel_war_goal(self, player: Player, action_id: str) -> None:
        """Handle canceling war goal selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.WAR_DECLARE:
            return

        # Only cancel if showing goal selection
        if player.pending_war_target_index < 0:
            return

        # Return to target selection
        player.pending_war_target_index = -1
        player.pending_war_goals = []

        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-war-select-target")
        self.rebuild_all_menus()

    def _action_cycle_war_armies(self, player: Player, action_id: str) -> None:
        """Cycle number of armies to commit (wraps around)."""
        if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
            return

        max_armies = player.tribe_state.get_available_armies()

        # Cycle: increment and wrap around to 0 if exceeds max
        player.pending_war_armies += 1
        if player.pending_war_armies > max_armies:
            player.pending_war_armies = 0

        self.rebuild_all_menus()

    def _action_cycle_war_generals(self, player: Player, action_id: str) -> None:
        """Cycle number of generals to commit (wraps around)."""
        if not isinstance(player, AgeOfHeroesPlayer) or not player.tribe_state:
            return

        max_generals = player.tribe_state.get_available_generals()

        # Cycle: increment and wrap around to 0 if exceeds max
        player.pending_war_generals += 1
        if player.pending_war_generals > max_generals:
            player.pending_war_generals = 0

        self.rebuild_all_menus()

    def _action_cycle_war_heroes_armies(self, player: Player, action_id: str) -> None:
        """Cycle number of heroes to use as armies (wraps around)."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        max_heroes = sum(
            1
            for card in player.hand
            if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
        )

        # Can't exceed total heroes minus those used as generals
        max_as_armies = max_heroes - player.pending_war_heroes_as_generals

        # Cycle: increment and wrap around to 0 if exceeds max
        player.pending_war_heroes_as_armies += 1
        if player.pending_war_heroes_as_armies > max_as_armies:
            player.pending_war_heroes_as_armies = 0

        self.rebuild_all_menus()

    def _action_cycle_war_heroes_generals(self, player: Player, action_id: str) -> None:
        """Cycle number of heroes to use as generals (wraps around)."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        max_heroes = sum(
            1
            for card in player.hand
            if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
        )

        # Can't exceed total heroes minus those used as armies
        max_as_generals = max_heroes - player.pending_war_heroes_as_armies

        # Cycle: increment and wrap around to 0 if exceeds max
        player.pending_war_heroes_as_generals += 1
        if player.pending_war_heroes_as_generals > max_as_generals:
            player.pending_war_heroes_as_generals = 0

        self.rebuild_all_menus()

    def _action_confirm_war_forces(self, player: Player, action_id: str) -> None:
        """Confirm force selection and proceed with war."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER:
            # Attacker has selected forces, prepare them
            prepare_forces(
                self,
                player,
                player.pending_war_armies,
                player.pending_war_generals,
                player.pending_war_heroes_as_armies,
                player.pending_war_heroes_as_generals,
            )

            # Reset attacker's pending values
            player.pending_war_armies = 0
            player.pending_war_generals = 0
            player.pending_war_heroes_as_armies = 0
            player.pending_war_heroes_as_generals = 0

            # Get defender
            active_players = self.get_active_players()
            if self.war_state.defender_index >= len(active_players):
                self.war_state.reset()
                self.sub_phase = PlaySubPhase.SELECT_ACTION
                self.rebuild_all_menus()
                self._end_action(player)
                return

            defender = active_players[self.war_state.defender_index]

            if isinstance(defender, AgeOfHeroesPlayer):
                if defender.is_bot:
                    # Bot defender auto-selects
                    def_armies, def_generals, def_heroes, def_hero_generals = (
                        bot_ai.bot_select_armies(self, defender, is_attacking=False)
                    )
                    prepare_forces(
                        self, defender, def_armies, def_generals, def_heroes, def_hero_generals
                    )

                    # Proceed to battle
                    execute_war_battle(self)
                else:
                    # Human defender needs to select forces
                    # Initialize defender's force selection with defaults
                    if defender.tribe_state:
                        defender.pending_war_armies = defender.tribe_state.get_available_armies()
                        defender.pending_war_generals = (
                            defender.tribe_state.get_available_generals()
                        )
                        # Count hero cards
                        hero_count = sum(
                            1
                            for card in defender.hand
                            if card.card_type == CardType.EVENT and card.subtype == EventType.HERO
                        )
                        # Default: use heroes as generals for defense
                        defender.pending_war_heroes_as_armies = 0
                        defender.pending_war_heroes_as_generals = hero_count

                    self.sub_phase = PlaySubPhase.WAR_PREPARE_DEFENDER
                    user = self.get_user(defender)
                    if user:
                        attacker_name = (
                            player.name if isinstance(player, AgeOfHeroesPlayer) else "Unknown"
                        )
                        user.speak_l("ageofheroes-war-prepare-defense", attacker=attacker_name)
                    self.rebuild_all_menus()
            else:
                # No valid defender
                self.war_state.reset()
                self.sub_phase = PlaySubPhase.SELECT_ACTION
                self.rebuild_all_menus()
                self._end_action(player)

        elif self.sub_phase == PlaySubPhase.WAR_PREPARE_DEFENDER:
            # Defender has selected forces, prepare them
            prepare_forces(
                self,
                player,
                player.pending_war_armies,
                player.pending_war_generals,
                player.pending_war_heroes_as_armies,
                player.pending_war_heroes_as_generals,
            )

            # Reset defender's pending values
            player.pending_war_armies = 0
            player.pending_war_generals = 0
            player.pending_war_heroes_as_armies = 0
            player.pending_war_heroes_as_generals = 0

            # Proceed to battle
            execute_war_battle(self)

    def _action_cancel_war_forces(self, player: Player, action_id: str) -> None:
        """Cancel force selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase == PlaySubPhase.WAR_PREPARE_ATTACKER:
            # Attacker cancels - return to action selection
            player.pending_war_armies = 0
            player.pending_war_generals = 0
            player.pending_war_heroes_as_armies = 0
            player.pending_war_heroes_as_generals = 0
            self.war_state.reset()
            self.sub_phase = PlaySubPhase.SELECT_ACTION
            self.rebuild_all_menus()
        elif self.sub_phase == PlaySubPhase.WAR_PREPARE_DEFENDER:
            # Defender can't cancel - they must respond
            # Reset to 0 forces (surrender)
            player.pending_war_armies = 0
            player.pending_war_generals = 0
            player.pending_war_heroes_as_armies = 0
            player.pending_war_heroes_as_generals = 0
            self.rebuild_all_menus()

    def _action_select_offer_card(self, player: Player, action_id: str) -> None:
        """Handle card selection for trade offer - first step."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.phase != GamePhase.FAIR:
            return

        if player.has_stopped_trading:
            return

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("offer_card_", ""))
        except ValueError:
            return

        if card_index >= len(player.hand):
            return

        # Set the pending offer card
        player.pending_offer_card_index = card_index

        # Tell the player to select what they want
        user = self.get_user(player)
        if user:
            card = player.hand[card_index]
            card_name = get_card_name(card, user.locale)
            user.speak_l("ageofheroes-select-request", card=card_name)

        self.rebuild_all_menus()

    def _action_select_request(self, player: Player, action_id: str) -> None:
        """Handle request selection for trade offer - second step."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.phase != GamePhase.FAIR:
            return

        if player.pending_offer_card_index < 0:
            return

        card_index = player.pending_offer_card_index
        if card_index >= len(player.hand):
            player.pending_offer_card_index = -1
            self.rebuild_all_menus()
            return

        card = player.hand[card_index]

        # Determine what was requested based on action_id
        wanted_type: str | None = None
        wanted_subtype: str | None = None

        if action_id == "request_any":
            # Any card - leave both as None
            pass
        elif action_id.startswith("request_resource_"):
            # Standard resource
            try:
                resource_index = int(action_id.replace("request_resource_", ""))
                resources = list(ResourceType)
                if resource_index < len(resources):
                    wanted_type = CardType.RESOURCE
                    wanted_subtype = resources[resource_index]
            except ValueError:
                player.pending_offer_card_index = -1
                self.rebuild_all_menus()
                return
        elif action_id == "request_own_special":
            # Own tribe's special resource
            if player.tribe_state:
                wanted_type = CardType.SPECIAL
                wanted_subtype = player.tribe_state.get_special_resource()
        elif action_id.startswith("request_event_"):
            # Event card (Fortune, Olympics, Hero)
            event_type = action_id.replace("request_event_", "")
            wanted_type = CardType.EVENT
            wanted_subtype = event_type
        else:
            player.pending_offer_card_index = -1
            self.rebuild_all_menus()
            return

        # Create the offer
        offer = create_offer(
            self,
            player,
            card_index,
            wanted_type=wanted_type,
            wanted_subtype=wanted_subtype,
        )

        if offer:
            announce_offer(self, player, card, wanted_subtype)

            # Check for matching trades immediately
            check_and_execute_trades(self)

        # Clear the pending offer
        player.pending_offer_card_index = -1
        self.rebuild_all_menus()

    def _action_cancel_offer_selection(self, player: Player, action_id: str) -> None:
        """Cancel the pending offer selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        player.pending_offer_card_index = -1
        self.rebuild_all_menus()

    def _action_discard_card(self, player: Player, action_id: str) -> None:
        """Handle discard card action - remove selected card from hand."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.DISCARD_EXCESS:
            return

        if player.pending_discard <= 0:
            return

        # Extract card index from action_id
        try:
            card_index = int(action_id.replace("discard_card_", ""))
        except ValueError:
            return

        if card_index >= len(player.hand):
            return

        # Remove the card
        card = player.hand.pop(card_index)
        self.discard_pile.append(card)
        player.pending_discard -= 1

        # Announce
        user = self.get_user(player)
        if user:
            card_name = get_card_name(card, user.locale)
            user.speak_l("ageofheroes-discard-card-you", card=card_name)
        self._broadcast_discard(player, card)

        # Check if more discards needed
        if player.pending_discard > 0:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "ageofheroes-discard-more",
                    count=player.pending_discard,
                )
            self.rebuild_all_menus()
        else:
            # Done discarding, end turn
            self._end_turn()

    def _action_play_disaster_card(self, player: Player, action_id: str) -> None:
        """Handle playing a disaster card (Earthquake/Eruption) - show target selection."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.SELECT_ACTION:
            return

        if self.current_player != player:
            return

        if self.current_day <= 1:
            return

        # Extract disaster type and card index from action_id
        try:
            if action_id.startswith("play_earthquake_"):
                disaster_type = EventType.EARTHQUAKE
                card_index = int(action_id.replace("play_earthquake_", ""))
            elif action_id.startswith("play_eruption_"):
                disaster_type = EventType.ERUPTION
                card_index = int(action_id.replace("play_eruption_", ""))
            else:
                return
        except ValueError:
            return

        if card_index >= len(player.hand):
            return

        # Verify card is correct type
        card = player.hand[card_index]
        if card.card_type != CardType.EVENT or card.subtype != disaster_type:
            return

        # Get valid targets (all other active players)
        active_players = self.get_active_players()
        targets = []
        for i, p in enumerate(active_players):
            if p != player and isinstance(p, AgeOfHeroesPlayer) and p.tribe_state:
                targets.append((i, p))

        if not targets:
            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-no-targets")
            return

        # For bots, auto-select best target and execute
        if player.is_bot:
            bot_ai.bot_play_disaster_on_target(self, player, disaster_type)
            return

        # For humans, store disaster state and enter target selection phase
        player.pending_disaster_targets = targets
        player.pending_disaster_card_index = card_index
        player.pending_disaster_type = disaster_type
        self.sub_phase = PlaySubPhase.DISASTER_TARGET

        user = self.get_user(player)
        if user:
            card_name = get_card_name(card, user.locale)
            user.speak_l("ageofheroes-select-disaster-target", card=card_name)

        self.rebuild_all_menus()

    def _action_select_disaster_target(self, player: Player, action_id: str) -> None:
        """Handle selecting a target for disaster card."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return

        if self.current_player != player:
            return

        # Extract target index from action_id
        try:
            target_list_index = int(action_id.replace("disaster_target_", ""))
        except ValueError:
            return

        if target_list_index >= len(player.pending_disaster_targets):
            return

        target_player_index, target = player.pending_disaster_targets[target_list_index]

        # Verify card still exists
        card_index = player.pending_disaster_card_index
        if card_index < 0 or card_index >= len(player.hand):
            return

        card = player.hand[card_index]
        disaster_type = player.pending_disaster_type

        # Apply the disaster effect
        from .events import apply_earthquake_effect, apply_eruption_effect

        if disaster_type == EventType.EARTHQUAKE:
            # Remove card and apply effect
            player.hand.pop(card_index)
            self.discard_pile.append(card)
            apply_earthquake_effect(self, player, target)
        elif disaster_type == EventType.ERUPTION:
            # Remove card and apply effect
            player.hand.pop(card_index)
            self.discard_pile.append(card)
            apply_eruption_effect(self, player, target)

        # Clear disaster state
        player.pending_disaster_targets = []
        player.pending_disaster_card_index = -1
        player.pending_disaster_type = ""

        # Return to action selection
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()

    def _action_cancel_disaster(self, player: Player, action_id: str) -> None:
        """Handle canceling disaster card play."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        if self.sub_phase != PlaySubPhase.DISASTER_TARGET:
            return

        if self.current_player != player:
            return

        # Clear disaster state
        player.pending_disaster_targets = []
        player.pending_disaster_card_index = -1
        player.pending_disaster_type = ""

        # Return to action selection
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.rebuild_all_menus()

    def _start_play_phase(self) -> None:
        """Start the main play phase."""
        self.phase = GamePhase.PLAY
        self.current_day += 1
        self.broadcast_l("ageofheroes-play-start")
        self.broadcast_l("ageofheroes-day", day=self.current_day)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not isinstance(player, AgeOfHeroesPlayer):
            return

        # Skip eliminated players
        if player.is_spectator or (player.tribe_state and player.tribe_state.is_eliminated()):
            # Skip this player's turn and advance to next
            self.advance_turn(announce=False)
            self._start_turn()
            return

        # Process end-of-turn effects from previous turn
        if player.tribe_state:
            armies_back, generals_back, recovered = player.tribe_state.process_end_of_turn()
            if armies_back > 0 or generals_back > 0:
                self.broadcast_personal_l(
                    player, "ageofheroes-army-returned-you", "ageofheroes-army-returned"
                )
            if recovered > 0:
                self.broadcast_personal_l(
                    player, "ageofheroes-army-recover-you", "ageofheroes-army-recover"
                )

        # Draw a card
        self.sub_phase = PlaySubPhase.DRAW_CARD
        drawn = self._draw_one()
        if drawn:
            player.hand.append(drawn)
            user = self.get_user(player)
            if user:
                card_name = get_card_name(drawn, user.locale)
                user.speak_l("ageofheroes-draw-card-you", card=card_name)

            # Announce to others
            for p in self.players:
                if p != player:
                    other_user = self.get_user(p)
                    if other_user:
                        other_user.speak_l("ageofheroes-draw-card", player=player.name)

            # Check for immediate event triggers (Hunger/Barbarians)
            events.check_drawn_card_event(self, player, drawn)

        # Move to action selection
        self.sub_phase = PlaySubPhase.SELECT_ACTION
        self.announce_turn()

        # Tell player their options
        user = self.get_user(player)
        if user:
            user.speak_l("ageofheroes-your-action")

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))  # nosec B311

        self.rebuild_all_menus()

    def _collect_special_resources(self, player: AgeOfHeroesPlayer) -> None:
        """Auto-collect special resources for monument building."""
        if not player.tribe_state:
            return

        tribe_special = player.tribe_state.get_special_resource()
        cards_to_remove = []

        for i, card in enumerate(player.hand):
            if card.card_type == CardType.SPECIAL and card.subtype == tribe_special:
                if player.tribe_state.monument_progress < 5:
                    player.tribe_state.monument_progress += 1
                    cards_to_remove.append(i)

        # Remove collected cards
        for i in reversed(cards_to_remove):
            removed = player.hand.pop(i)
            self.discard_pile.append(removed)

        # Announce if progress was made
        if cards_to_remove:
            percent = player.tribe_state.monument_progress * 20
            self.broadcast_personal_l(
                player,
                "ageofheroes-monument-progress-you",
                "ageofheroes-monument-progress",
                percent=percent,
                count=player.tribe_state.monument_progress,
            )

            # Check for monument victory
            if player.tribe_state.monument_progress >= 5:
                self._declare_victory(player, "monument")

    def _perform_tax_collection(self, player: AgeOfHeroesPlayer) -> None:
        """Perform tax collection action."""
        if not player.tribe_state:
            return

        cities = player.tribe_state.cities
        if cities == 0:
            # No cities - exchange a card
            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-tax-no-city")
            # For now, auto-exchange first card
            if player.hand:
                discarded = player.hand.pop(0)
                self.discard_pile.append(discarded)
                drawn = self._draw_one()
                if drawn:
                    player.hand.append(drawn)
                self.broadcast_personal_l(
                    player,
                    "ageofheroes-tax-no-city-done-you",
                    "ageofheroes-tax-no-city-done",
                )
        else:
            # Draw cards equal to cities
            drawn = self._draw_cards(cities)
            player.hand.extend(drawn)
            self.broadcast_personal_l(
                player,
                "ageofheroes-tax-collection-you",
                "ageofheroes-tax-collection",
                cities=cities,
                cards=len(drawn),
            )

        self._end_action(player)

    def _start_war_declaration(self, player: AgeOfHeroesPlayer) -> None:
        """Start war declaration."""
        if not player.tribe_state:
            self._end_action(player)
            return

        # Check if player can declare war
        war_error = can_declare_war(self, player)
        if war_error:
            user = self.get_user(player)
            if user:
                user.speak_l(war_error)
            # Don't end action - return to action selection
            return

        # For bots, auto-select target and execute war
        if player.is_bot:
            bot_ai.bot_perform_war(self, player)
        else:
            # Show war menu for human players
            # Get valid targets
            targets = get_valid_war_targets(self, player)
            if not targets:
                user = self.get_user(player)
                if user:
                    user.speak_l("ageofheroes-war-no-targets")
                return

            # Store targets and enter war declaration subphase
            player.pending_war_targets = targets
            player.pending_war_target_index = -1
            player.pending_war_goals = []
            self.sub_phase = PlaySubPhase.WAR_DECLARE

            user = self.get_user(player)
            if user:
                user.speak_l("ageofheroes-war-select-target")
            self.rebuild_all_menus()

    def _perform_do_nothing(self, player: AgeOfHeroesPlayer) -> None:
        """Perform do nothing action."""
        self.broadcast_personal_l(player, "ageofheroes-do-nothing-you", "ageofheroes-do-nothing")
        self._end_action(player)

    def _end_action(self, player: AgeOfHeroesPlayer) -> None:
        """End the current action and check for hand overflow."""
        player.current_action = None
        # Clear declined road targets when action ends
        player.declined_road_targets = []

        # Check hand size
        if len(player.hand) > MAX_HAND_SIZE:
            self.sub_phase = PlaySubPhase.DISCARD_EXCESS
            player.pending_discard = len(player.hand) - MAX_HAND_SIZE
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "ageofheroes-discard-excess",
                    max=MAX_HAND_SIZE,
                    count=player.pending_discard,
                )
            # For bots, auto-discard
            if player.is_bot:
                bot_ai.bot_execute_discard_excess(self, player)
            else:
                # Rebuild menus to show discard options
                self.rebuild_all_menus()
            return

        self._end_turn()

    def _end_turn(self) -> None:
        """End the current turn and advance to next player."""
        player = self.current_player
        if isinstance(player, AgeOfHeroesPlayer):
            # Collect special resources for monument (after action, before next turn)
            self._collect_special_resources(player)

        # Check victory conditions
        winner = self._check_victory()
        if winner:
            return

        # Check if day is over (all players had a turn)
        active_players = self.get_active_players()
        next_index = (self.turn_index + 1) % len(active_players)

        # Day is over when we cycle back to the player who started the day
        if next_index == self.day_start_turn_index:
            # Start new day
            self._start_new_day()
        else:
            # Continue to next player
            self.advance_turn(announce=False)
            self._start_turn()

    def _start_new_day(self) -> None:
        """Start a new day (round)."""
        # Set turn index to the day start player (maintains consistent turn order)
        self.turn_index = self.day_start_turn_index
        # Return to prepare phase for new events
        self._start_prepare_phase()

    def _check_victory(self) -> AgeOfHeroesPlayer | None:
        """Check for victory conditions."""
        active_players = [
            p
            for p in self.get_active_players()
            if isinstance(p, AgeOfHeroesPlayer)
            and p.tribe_state
            and not p.tribe_state.is_eliminated()
        ]

        # Last standing
        if len(active_players) == 1:
            self._declare_victory(active_players[0], "last_standing")
            return active_players[0]

        # Check cities and monument for each player
        for player in active_players:
            if not player.tribe_state:
                continue

            # 5 Cities
            if player.tribe_state.cities >= self.options.victory_cities:
                self._declare_victory(player, "cities")
                return player

            # Monument complete
            if player.tribe_state.monument_progress >= 5:
                self._declare_victory(player, "monument")
                return player

        return None

    def _declare_victory(self, player: AgeOfHeroesPlayer, victory_type: str) -> None:
        """Declare a victory."""
        self.phase = GamePhase.GAME_OVER
        self.play_sound("game_pig/win.ogg")

        if victory_type == "cities":
            self.broadcast_personal_l(
                player, "ageofheroes-victory-cities-you", "ageofheroes-victory-cities"
            )
        elif victory_type == "monument":
            self.broadcast_personal_l(
                player, "ageofheroes-victory-monument-you", "ageofheroes-victory-monument"
            )
        elif victory_type == "last_standing":
            self.broadcast_personal_l(
                player,
                "ageofheroes-victory-last-standing-you",
                "ageofheroes-victory-last-standing",
            )

        self.broadcast_l("ageofheroes-game-over")
        self.finish_game()

    def _check_elimination(self, player: AgeOfHeroesPlayer) -> None:
        """Check if a player has been eliminated."""
        if not player.tribe_state:
            return

        if player.tribe_state.is_eliminated() and len(player.hand) == 0:
            player.is_spectator = True
            self.broadcast_personal_l(
                player, "ageofheroes-eliminated-you", "ageofheroes-eliminated"
            )

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()
        if not self.game_active:
            return

        if self.phase == GamePhase.SETUP:
            self._tick_setup_bots()
            return

        if self.phase == GamePhase.FAIR:
            self._tick_fair_bots()
            return

        if self.phase == GamePhase.PLAY:
            if self.sub_phase == PlaySubPhase.ROAD_PERMISSION:
                self._tick_road_permission_bots()
                return
            if self.sub_phase == PlaySubPhase.WAR_BATTLE:
                self._tick_war_battle_bots()
                return

        # Normal turn-based bot handling
        BotHelper.on_tick(self)

    def _tick_setup_bots(self) -> None:
        """Handle bot actions during setup rolls."""
        for player in self.get_active_players():
            if not player.is_bot or player.id in self.setup_rolls:
                continue
            BotHelper.process_bot_action(
                bot=player,
                think_fn=lambda p=player: self.bot_think(p),
                execute_fn=lambda action_id, p=player: self.execute_action(p, action_id),
            )

    def _tick_fair_bots(self) -> None:
        """Handle bot trading during the fair phase."""
        for player in self.get_active_players():
            if not isinstance(player, AgeOfHeroesPlayer):
                continue
            if not player.is_bot or player.has_stopped_trading:
                continue
            if player.bot_think_ticks > 0:
                player.bot_think_ticks -= 1
                continue
            bot_ai.bot_do_trading(self, player)

    def _tick_road_permission_bots(self) -> None:
        """Handle bot response to road permission requests."""
        active_players = self.get_active_players()
        if self.road_request_to >= len(active_players):
            return
        target = active_players[self.road_request_to]
        if target.is_bot and not target.is_spectator:
            BotHelper.process_bot_action(
                bot=target,
                think_fn=lambda: self.bot_think(target),
                execute_fn=lambda action_id: self.execute_action(target, action_id),
            )

    def _tick_war_battle_bots(self) -> None:
        """Handle bot rolls during war battles."""
        active_players = self.get_active_players()
        war = self.war_state

        if war.attacker_index < len(active_players):
            attacker = active_players[war.attacker_index]
            if attacker.is_bot and not attacker.is_spectator and war.attacker_roll == 0:
                BotHelper.process_bot_action(
                    bot=attacker,
                    think_fn=lambda: self.bot_think(attacker),
                    execute_fn=lambda action_id: self.execute_action(attacker, action_id),
                )

        if war.defender_index < len(active_players):
            defender = active_players[war.defender_index]
            if defender.is_bot and not defender.is_spectator and war.defender_roll == 0:
                BotHelper.process_bot_action(
                    bot=defender,
                    think_fn=lambda: self.bot_think(defender),
                    execute_fn=lambda action_id: self.execute_action(defender, action_id),
                )

    def bot_think(self, player: Player) -> str | None:
        """Bot AI decision making."""
        if not isinstance(player, AgeOfHeroesPlayer):
            return None

        # Delegate to bot AI module
        return bot_ai.bot_think(self, player)

    # ==========================================================================
    # Game Result
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        """Build the game result."""
        active_players = self.get_active_players()

        # Find winner
        winner = None
        for p in active_players:
            if isinstance(p, AgeOfHeroesPlayer) and p.tribe_state:
                if (
                    p.tribe_state.cities >= self.options.victory_cities
                    or p.tribe_state.monument_progress >= 5
                ):
                    winner = p
                    break

        # If no winner by cities/monument, last standing
        non_eliminated = [
            p
            for p in active_players
            if isinstance(p, AgeOfHeroesPlayer)
            and p.tribe_state
            and not p.tribe_state.is_eliminated()
        ]
        if not winner and len(non_eliminated) == 1:
            winner = non_eliminated[0]

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "days_played": self.current_day,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        lines = [Localization.get(locale, "ageofheroes-game-over")]

        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(f"Winner: {winner_name}")

        days = result.custom_data.get("days_played", 0)
        lines.append(f"Days: {days}")

        return lines
