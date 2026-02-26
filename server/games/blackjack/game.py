from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random
from collections.abc import Callable

from ..base import Game, GameOptions, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.cards import Card, Deck, DeckFactory, card_name, read_cards
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import BoolOption, IntOption, MenuOption, option_field
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState
from .bot import bot_think


TURN_TIMER_CHOICES = ["5", "10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "5": "poker-timer-5",
    "10": "poker-timer-10",
    "15": "poker-timer-15",
    "20": "poker-timer-20",
    "30": "poker-timer-30",
    "45": "poker-timer-45",
    "60": "poker-timer-60",
    "90": "poker-timer-90",
    "0": "poker-timer-unlimited",
}

RULES_PROFILE_CHOICES = ["vegas", "european", "friendly"]
RULES_PROFILE_LABELS = {
    "vegas": "blackjack-rules-profile-vegas",
    "european": "blackjack-rules-profile-european",
    "friendly": "blackjack-rules-profile-friendly",
}

BLACKJACK_PAYOUT_CHOICES = ["3_to_2", "6_to_5", "1_to_1"]
BLACKJACK_PAYOUT_LABELS = {
    "3_to_2": "blackjack-payout-3-to-2",
    "6_to_5": "blackjack-payout-6-to-5",
    "1_to_1": "blackjack-payout-1-to-1",
}

DOUBLE_DOWN_RULE_CHOICES = ["any_two", "9_to_11", "10_to_11"]
DOUBLE_DOWN_RULE_LABELS = {
    "any_two": "blackjack-double-rule-any-two",
    "9_to_11": "blackjack-double-rule-9-to-11",
    "10_to_11": "blackjack-double-rule-10-to-11",
}

SPLIT_RULE_CHOICES = ["same_value", "same_rank"]
SPLIT_RULE_LABELS = {
    "same_value": "blackjack-split-rule-same-value",
    "same_rank": "blackjack-split-rule-same-rank",
}

RULE_PROFILE_PRESETS: dict[str, dict[str, str | bool | int]] = {
    "vegas": {
        "dealer_hits_soft_17": True,
        "dealer_peeks_blackjack": True,
        "allow_insurance": True,
        "allow_late_surrender": True,
        "blackjack_payout": "3_to_2",
        "double_down_rule": "any_two",
        "allow_double_after_split": True,
        "split_rule": "same_rank",
        "max_split_hands": 2,
        "split_aces_one_card_only": True,
        "split_aces_count_as_blackjack": False,
    },
    "european": {
        "dealer_hits_soft_17": False,
        "dealer_peeks_blackjack": False,
        "allow_insurance": True,
        "allow_late_surrender": False,
        "blackjack_payout": "3_to_2",
        "double_down_rule": "9_to_11",
        "allow_double_after_split": False,
        "split_rule": "same_rank",
        "max_split_hands": 2,
        "split_aces_one_card_only": True,
        "split_aces_count_as_blackjack": False,
    },
    "friendly": {
        "dealer_hits_soft_17": False,
        "dealer_peeks_blackjack": True,
        "allow_insurance": True,
        "allow_late_surrender": True,
        "blackjack_payout": "3_to_2",
        "double_down_rule": "any_two",
        "allow_double_after_split": True,
        "split_rule": "same_value",
        "max_split_hands": 2,
        "split_aces_one_card_only": False,
        "split_aces_count_as_blackjack": True,
    },
}


@dataclass
class BlackjackPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    chips: int = 0
    bet: int = 0
    hand_done: bool = False
    stood: bool = False
    busted: bool = False
    has_blackjack: bool = False
    split_hand: list[Card] = field(default_factory=list)
    split_bet: int = 0
    split_hand_done: bool = True
    split_stood: bool = False
    split_busted: bool = False
    split_has_blackjack: bool = False
    active_hand_index: int = 0  # 0 = main, 1 = split
    doubled_main: bool = False
    doubled_split: bool = False
    surrendered_main: bool = False
    surrendered_split: bool = False
    main_from_split_aces: bool = False
    split_from_split_aces: bool = False
    insurance_bet: int = 0
    insurance_decision_done: bool = False
    took_even_money: bool = False


@dataclass
class BlackjackOptions(GameOptions):
    rules_profile: str = option_field(
        MenuOption(
            choices=RULES_PROFILE_CHOICES,
            choice_labels=RULES_PROFILE_LABELS,
            default="vegas",
            value_key="profile",
            label="blackjack-set-rules-profile",
            prompt="blackjack-select-rules-profile",
            change_msg="blackjack-option-changed-rules-profile",
        )
    )
    starting_chips: int = option_field(
        IntOption(
            default=500,
            min_val=50,
            max_val=1000000,
            value_key="count",
            label="blackjack-set-starting-chips",
            prompt="blackjack-enter-starting-chips",
            change_msg="blackjack-option-changed-starting-chips",
        )
    )
    base_bet: int = option_field(
        IntOption(
            default=10,
            min_val=1,
            max_val=100000,
            value_key="count",
            label="blackjack-set-base-bet",
            prompt="blackjack-enter-base-bet",
            change_msg="blackjack-option-changed-base-bet",
        )
    )
    table_min_bet: int = option_field(
        IntOption(
            default=5,
            min_val=1,
            max_val=100000,
            value_key="count",
            label="blackjack-set-table-min-bet",
            prompt="blackjack-enter-table-min-bet",
            change_msg="blackjack-option-changed-table-min-bet",
        )
    )
    table_max_bet: int = option_field(
        IntOption(
            default=100,
            min_val=1,
            max_val=100000,
            value_key="count",
            label="blackjack-set-table-max-bet",
            prompt="blackjack-enter-table-max-bet",
            change_msg="blackjack-option-changed-table-max-bet",
        )
    )
    deck_count: int = option_field(
        IntOption(
            default=4,
            min_val=1,
            max_val=8,
            value_key="count",
            label="blackjack-set-deck-count",
            prompt="blackjack-enter-deck-count",
            change_msg="blackjack-option-changed-deck-count",
        )
    )
    dealer_hits_soft_17: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-dealer-soft-17",
            change_msg="blackjack-option-changed-dealer-soft-17",
        )
    )
    dealer_peeks_blackjack: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-dealer-peek-blackjack",
            change_msg="blackjack-option-changed-dealer-peek-blackjack",
        )
    )
    players_cards_face_up: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-players-cards-face-up",
            change_msg="blackjack-option-changed-players-cards-face-up",
        )
    )
    allow_insurance: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-allow-insurance",
            change_msg="blackjack-option-changed-allow-insurance",
        )
    )
    allow_late_surrender: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-allow-late-surrender",
            change_msg="blackjack-option-changed-allow-late-surrender",
        )
    )
    blackjack_payout: str = option_field(
        MenuOption(
            choices=BLACKJACK_PAYOUT_CHOICES,
            choice_labels=BLACKJACK_PAYOUT_LABELS,
            default="3_to_2",
            value_key="mode",
            label="blackjack-set-blackjack-payout",
            prompt="blackjack-select-blackjack-payout",
            change_msg="blackjack-option-changed-blackjack-payout",
        )
    )
    double_down_rule: str = option_field(
        MenuOption(
            choices=DOUBLE_DOWN_RULE_CHOICES,
            choice_labels=DOUBLE_DOWN_RULE_LABELS,
            default="any_two",
            value_key="mode",
            label="blackjack-set-double-down-rule",
            prompt="blackjack-select-double-down-rule",
            change_msg="blackjack-option-changed-double-down-rule",
        )
    )
    allow_double_after_split: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-allow-double-after-split",
            change_msg="blackjack-option-changed-allow-double-after-split",
        )
    )
    split_rule: str = option_field(
        MenuOption(
            choices=SPLIT_RULE_CHOICES,
            choice_labels=SPLIT_RULE_LABELS,
            default="same_rank",
            value_key="mode",
            label="blackjack-set-split-rule",
            prompt="blackjack-select-split-rule",
            change_msg="blackjack-option-changed-split-rule",
        )
    )
    max_split_hands: int = option_field(
        IntOption(
            default=2,
            min_val=1,
            max_val=2,
            value_key="count",
            label="blackjack-set-max-split-hands",
            prompt="blackjack-enter-max-split-hands",
            change_msg="blackjack-option-changed-max-split-hands",
        )
    )
    split_aces_one_card_only: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="blackjack-set-split-aces-one-card",
            change_msg="blackjack-option-changed-split-aces-one-card",
        )
    )
    split_aces_count_as_blackjack: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="blackjack-set-split-aces-blackjack",
            change_msg="blackjack-option-changed-split-aces-blackjack",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            label="blackjack-set-turn-timer",
            prompt="blackjack-select-turn-timer",
            change_msg="blackjack-option-changed-turn-timer",
        )
    )


@dataclass
@register_game
class BlackjackGame(Game):
    players: list[BlackjackPlayer] = field(default_factory=list)
    options: BlackjackOptions = field(default_factory=BlackjackOptions)
    deck: Deck | None = None
    dealer_hand: list[Card] = field(default_factory=list)
    hand_number: int = 0
    phase: str = "lobby"
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    dealer_hole_revealed: bool = False
    next_hand_wait_ticks: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Blackjack"

    @classmethod
    def get_type(cls) -> str:
        return "blackjack"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 1

    @classmethod
    def get_max_players(cls) -> int:
        return 7

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> BlackjackPlayer:
        return BlackjackPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str]:
        errors = super().prestart_validate()
        self._resolve_rules_profile()
        if self.options.base_bet > self.options.starting_chips:
            errors.append("blackjack-error-bet-too-high")
        if self.options.table_min_bet > self.options.table_max_bet:
            errors.append("blackjack-error-table-limits-invalid")
        if self.options.base_bet < self.options.table_min_bet:
            errors.append("blackjack-error-bet-below-min")
        if self.options.base_bet > self.options.table_max_bet:
            errors.append("blackjack-error-bet-above-max")
        return errors

    def _handle_option_change(self, option_name: str, value: str) -> None:
        super()._handle_option_change(option_name, value)
        if option_name != "rules_profile":
            return
        self._apply_rules_profile(self.options.rules_profile)
        if hasattr(self.options, "update_options_labels"):
            self.options.update_options_labels(self)
        self.rebuild_all_menus()

    def _resolve_rules_profile(self) -> str:
        profile = self.options.rules_profile
        if profile not in RULE_PROFILE_PRESETS:
            profile = "vegas"
            self.options.rules_profile = profile
        return profile

    def _apply_rules_profile(self, profile: str) -> None:
        resolved = profile if profile in RULE_PROFILE_PRESETS else "vegas"
        preset = RULE_PROFILE_PRESETS[resolved]
        self.options.rules_profile = resolved
        self.options.dealer_hits_soft_17 = bool(preset["dealer_hits_soft_17"])
        self.options.dealer_peeks_blackjack = bool(preset["dealer_peeks_blackjack"])
        self.options.allow_insurance = bool(preset["allow_insurance"])
        self.options.allow_late_surrender = bool(preset["allow_late_surrender"])
        self.options.blackjack_payout = str(preset["blackjack_payout"])
        self.options.double_down_rule = str(preset["double_down_rule"])
        self.options.allow_double_after_split = bool(preset["allow_double_after_split"])
        self.options.split_rule = str(preset["split_rule"])
        self.options.max_split_hands = int(preset["max_split_hands"])
        self.options.split_aces_one_card_only = bool(preset["split_aces_one_card_only"])
        self.options.split_aces_count_as_blackjack = bool(preset["split_aces_count_as_blackjack"])

    # ======================================================================
    # Action availability
    # ======================================================================

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "players":
            return "blackjack-not-player-phase"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._current_hand_done(p):
            return "blackjack-hand-complete"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.phase != "players":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._current_hand_done(p):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_split_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._can_split(p):
            return "blackjack-cannot-split"
        return None

    def _is_double_down_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._can_double_down(p):
            return "blackjack-cannot-double-down"
        return None

    def _is_surrender_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._can_surrender(p):
            return "blackjack-cannot-surrender"
        return None

    def _is_insurance_turn_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "insurance":
            return "blackjack-not-insurance-phase"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._player_needs_insurance_decision(p):
            return "blackjack-insurance-closed"
        return None

    def _is_insurance_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.phase != "insurance":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._player_needs_insurance_decision(p):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_take_insurance_enabled(self, player: Player) -> str | None:
        error = self._is_insurance_turn_enabled(player)
        if error:
            return error
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._can_take_insurance(p):
            return "blackjack-cannot-insure"
        return None

    def _is_even_money_enabled(self, player: Player) -> str | None:
        error = self._is_insurance_turn_enabled(player)
        if error:
            return error
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or not self._can_take_even_money(p):
            return "blackjack-cannot-even-money"
        return None

    def _is_decline_insurance_enabled(self, player: Player) -> str | None:
        return self._is_insurance_turn_enabled(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    # ======================================================================
    # Action sets / keybinds
    # ======================================================================

    def create_turn_action_set(self, player: BlackjackPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="hit",
                label=Localization.get(locale, "blackjack-hit"),
                handler="_action_hit",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="stand",
                label=Localization.get(locale, "blackjack-stand"),
                handler="_action_stand",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="double_down",
                label=Localization.get(locale, "blackjack-double-down"),
                handler="_action_double_down",
                is_enabled="_is_double_down_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="split",
                label=Localization.get(locale, "blackjack-split"),
                handler="_action_split",
                is_enabled="_is_split_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="surrender",
                label=Localization.get(locale, "blackjack-surrender"),
                handler="_action_surrender",
                is_enabled="_is_surrender_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="take_insurance",
                label=Localization.get(locale, "blackjack-take-insurance"),
                handler="_action_take_insurance",
                is_enabled="_is_take_insurance_enabled",
                is_hidden="_is_insurance_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="even_money",
                label=Localization.get(locale, "blackjack-even-money"),
                handler="_action_even_money",
                is_enabled="_is_even_money_enabled",
                is_hidden="_is_insurance_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="decline_insurance",
                label=Localization.get(locale, "blackjack-decline-insurance"),
                handler="_action_decline_insurance",
                is_enabled="_is_decline_insurance_enabled",
                is_hidden="_is_insurance_action_hidden",
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        local_actions = [
            Action(
                id="read_hand",
                label=Localization.get(locale, "blackjack-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="read_dealer",
                label=Localization.get(locale, "blackjack-read-dealer"),
                handler="_action_read_dealer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="table_status",
                label=Localization.get(locale, "blackjack-table-status"),
                handler="_action_table_status",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="read_rules",
                label=Localization.get(locale, "blackjack-read-rules"),
                handler="_action_read_rules",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "poker-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
        ]

        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Hit", ["hit"], state=KeybindState.ACTIVE)
        self.define_keybind("x", "Stand", ["stand"], state=KeybindState.ACTIVE)
        self.define_keybind("d", "Double down", ["double_down"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Split", ["split"], state=KeybindState.ACTIVE)
        self.define_keybind("u", "Surrender", ["surrender"], state=KeybindState.ACTIVE)
        self.define_keybind("i", "Insurance", ["take_insurance"], state=KeybindState.ACTIVE)
        self.define_keybind("n", "Decline insurance", ["decline_insurance"], state=KeybindState.ACTIVE)
        self.define_keybind("m", "Even money", ["even_money"], state=KeybindState.ACTIVE)
        self.define_keybind("r", "Read hand", ["read_hand"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("c", "Read dealer", ["read_dealer"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("e", "Table status", ["table_status"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+r", "Read rules", ["read_rules"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], state=KeybindState.ACTIVE, include_spectators=True)

    # ======================================================================
    # Game flow
    # ======================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.phase = "players"
        self.hand_number = 0
        self.next_hand_wait_ticks = 0

        active = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])

        for player in active:
            if isinstance(player, BlackjackPlayer):
                player.chips = self.options.starting_chips

        self._sync_team_scores()
        self.play_music("game_blackjack/mus.ogg")
        self._start_new_hand()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        if self.next_hand_wait_ticks > 0:
            self.next_hand_wait_ticks -= 1
            if self.next_hand_wait_ticks == 0:
                self._start_new_hand()
            return

        if self.phase in {"players", "insurance"} and self.timer.tick():
            self._handle_turn_timeout()

        BotHelper.on_tick(self)

    def bot_think(self, player: BlackjackPlayer) -> str | None:
        return bot_think(self, player)

    def _start_new_hand(self) -> None:
        self.phase = "players"
        self.hand_number += 1
        self.timer.clear()

        total_competitors = [
            p
            for p in self.get_active_players()
            if isinstance(p, BlackjackPlayer)
        ]
        active_players = [
            p
            for p in self.get_active_players()
            if isinstance(p, BlackjackPlayer) and p.chips > 0
        ]
        if len(active_players) == 0:
            self._end_game(None)
            return
        # In multiplayer, game ends when one stack remains. In solo mode, keep dealing hands
        # until that single player busts out.
        if len(total_competitors) > 1 and len(active_players) <= 1:
            self._end_game(active_players[0] if active_players else None)
            return

        for player in active_players:
            player.hand = []
            player.bet = 0
            player.hand_done = False
            player.stood = False
            player.busted = False
            player.has_blackjack = False
            player.split_hand = []
            player.split_bet = 0
            player.split_hand_done = True
            player.split_stood = False
            player.split_busted = False
            player.split_has_blackjack = False
            player.active_hand_index = 0
            player.doubled_main = False
            player.doubled_split = False
            player.surrendered_main = False
            player.surrendered_split = False
            player.main_from_split_aces = False
            player.split_from_split_aces = False
            player.insurance_bet = 0
            player.insurance_decision_done = False
            player.took_even_money = False

        self.dealer_hand = []
        self.dealer_hole_revealed = False

        self.broadcast_l("blackjack-hand-start", hand=self.hand_number)
        self._ensure_deck(min_cards=len(active_players) * 6)
        self._post_bets(active_players)
        self._deal_initial_cards(active_players)

        if self._should_offer_insurance(active_players):
            self._start_insurance_phase(active_players)
            return

        dealer_blackjack = self.is_blackjack(self.dealer_hand)
        if dealer_blackjack and self.options.dealer_peeks_blackjack:
            self._reveal_dealer_hand()
            self.broadcast_l("blackjack-dealer-blackjack")
            self._settle_hand()
            return

        self._start_player_phase(active_players)

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, BlackjackPlayer):
            self._play_dealer_turn()
            return
        self._select_first_pending_hand(player)
        if self._current_hand_done(player):
            self._advance_to_next_player()
            return

        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")
        self._announce_player_total(player)

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 35))  # nosec B311

        self._start_turn_timer()
        self.rebuild_all_menus()
        self.rebuild_player_menu(player, position=1)

    def _start_player_phase(self, players: list[BlackjackPlayer]) -> None:
        self.phase = "players"
        action_order = [p for p in players if self._player_has_pending_hand(p)]
        self.set_turn_players(action_order, reset_index=True)
        if not self.turn_player_ids:
            self._settle_hand()
            return
        self._start_turn()

    def _should_offer_insurance(self, players: list[BlackjackPlayer]) -> bool:
        if not self.options.allow_insurance:
            return False
        if not self._dealer_upcard_is_ace():
            return False
        return any(self._can_take_insurance(player) or self._can_take_even_money(player) for player in players)

    def _start_insurance_phase(self, players: list[BlackjackPlayer]) -> None:
        self.phase = "insurance"
        self.timer.clear()
        self.broadcast_l("blackjack-insurance-offer")
        for player in players:
            player.insurance_decision_done = not self._player_needs_insurance_decision(player)

        action_order = [p for p in players if self._player_needs_insurance_decision(p)]
        self.set_turn_players(action_order, reset_index=True)
        if not self.turn_player_ids:
            self._finish_insurance_phase(players)
            return
        self._start_insurance_turn()

    def _start_insurance_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, BlackjackPlayer):
            self._finish_insurance_phase([p for p in self.get_active_players() if isinstance(p, BlackjackPlayer)])
            return

        if not self._player_needs_insurance_decision(player):
            self._advance_insurance_to_next_player()
            return

        if self._can_take_even_money(player):
            self.broadcast_personal_l(
                player,
                "blackjack-insurance-prompt-even-money",
                "blackjack-insurance-prompt-even-money-player",
            )
        elif self._can_take_insurance(player):
            self.broadcast_personal_l(
                player,
                "blackjack-insurance-prompt",
                "blackjack-insurance-prompt-player",
                amount=self._insurance_bet_amount(player),
            )

        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 35))  # nosec B311
        self._start_turn_timer()
        self.rebuild_all_menus()
        self.rebuild_player_menu(player, position=1)

    def _advance_insurance_to_next_player(self) -> None:
        if not self.turn_player_ids:
            self._finish_insurance_phase([p for p in self.get_active_players() if isinstance(p, BlackjackPlayer)])
            return

        for _ in range(len(self.turn_player_ids)):
            self.advance_turn(announce=False)
            nxt = self.current_player
            if not isinstance(nxt, BlackjackPlayer):
                continue
            if self._player_needs_insurance_decision(nxt):
                self._start_insurance_turn()
                return

        self._finish_insurance_phase([p for p in self.get_active_players() if isinstance(p, BlackjackPlayer)])

    def _finish_insurance_phase(self, players: list[BlackjackPlayer]) -> None:
        self.timer.clear()
        for player in players:
            if self._player_needs_insurance_decision(player):
                player.insurance_decision_done = True

        dealer_blackjack = self.is_blackjack(self.dealer_hand)
        if dealer_blackjack and self.options.dealer_peeks_blackjack:
            self._reveal_dealer_hand()
            self.broadcast_l("blackjack-dealer-blackjack")
            self._settle_hand()
            return

        self._start_player_phase(players)

    def _advance_to_next_player(self) -> None:
        current = self.current_player
        if isinstance(current, BlackjackPlayer) and self._switch_to_next_hand(current):
            self._start_turn()
            return

        if not self.turn_player_ids:
            self._play_dealer_turn()
            return

        for _ in range(len(self.turn_player_ids)):
            self.advance_turn(announce=False)
            nxt = self.current_player
            if not isinstance(nxt, BlackjackPlayer):
                continue
            self._select_first_pending_hand(nxt)
            if self._current_hand_done(nxt):
                continue
            self._start_turn()
            return

        self._play_dealer_turn()

    def _play_dealer_turn(self) -> None:
        self.phase = "dealer"
        self.timer.clear()
        self._reveal_dealer_hand()

        while True:
            total, is_soft = self.hand_value(self.dealer_hand)
            should_hit = total < 17
            if total == 17 and is_soft and self.options.dealer_hits_soft_17:
                should_hit = True

            if not should_hit:
                break

            card = self._draw_card()
            if not card:
                break
            self.dealer_hand.append(card)
            self.play_sound("game_cards/draw3.ogg")
            self._broadcast_l_with_locale_args(
                "blackjack-dealer-hits",
                lambda locale: {
                    "card": card_name(card, locale),
                    "cards": read_cards(self.dealer_hand, locale),
                    "total": self._total_text(locale, *self.hand_value(self.dealer_hand)),
                },
            )

        total, is_soft = self.hand_value(self.dealer_hand)
        if total > 21:
            self._broadcast_l_with_locale_args(
                "blackjack-dealer-bust",
                lambda locale: {"total": self._total_text(locale, total, is_soft)},
            )
        else:
            self._broadcast_l_with_locale_args(
                "blackjack-dealer-stands",
                lambda locale: {"total": self._total_text(locale, total, is_soft)},
            )
        self._settle_hand()

    # ======================================================================
    # Player actions
    # ======================================================================

    def _action_hit(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_turn_action_enabled(p):
            return
        if self._is_current_hand_locked_after_split_aces(p):
            return

        hand = self._current_hand(p)
        card = self._draw_card()
        if not card:
            return

        hand.append(card)
        self.play_sound("game_cards/draw3.ogg")
        self.broadcast_personal_l(
            p,
            "blackjack-you-hit",
            "blackjack-player-hits",
            card=card_name(card, self._player_locale(p)),
        )
        self._evaluate_current_hand_after_draw(p)

    def _action_stand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_turn_action_enabled(p):
            return

        self._set_current_hand_done(p, done=True, stood=True)
        self.broadcast_personal_l(p, "blackjack-you-stand", "blackjack-player-stands")
        self._advance_to_next_player()

    def _action_surrender(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_surrender_enabled(p):
            return

        bet = self._current_bet(p)
        if bet <= 0:
            return

        refund = bet // 2
        loss = bet - refund
        p.chips += refund
        self._set_current_surrendered(p, True)
        self._set_current_hand_done(p, done=True, stood=True)
        self._sync_team_scores()
        self.broadcast_personal_l(
            p,
            "blackjack-you-surrender",
            "blackjack-player-surrenders",
            amount=loss,
        )
        self._advance_to_next_player()

    def _action_double_down(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_double_down_enabled(p):
            return

        bet = self._current_bet(p)
        if bet <= 0:
            return

        p.chips -= bet
        self._set_current_bet(p, bet * 2)
        self._set_current_doubled(p, True)
        self._sync_team_scores()

        self.broadcast_personal_l(
            p,
            "blackjack-you-double-down",
            "blackjack-player-double-downs",
            amount=bet,
        )

        hand = self._current_hand(p)
        card = self._draw_card()
        if card:
            hand.append(card)
            self.play_sound("game_cards/draw3.ogg")
            self.broadcast_personal_l(
                p,
                "blackjack-you-hit",
                "blackjack-player-hits",
                card=card_name(card, self._player_locale(p)),
            )

        total, is_soft = self.hand_value(hand)
        if total > 21:
            self._set_current_hand_done(p, done=True, busted=True)
            self.broadcast_personal_l(
                p,
                "blackjack-you-bust",
                "blackjack-player-bust",
                total=self._total_text(self._player_locale(p), total, is_soft),
            )
        else:
            self._set_current_hand_done(p, done=True, stood=True)
            self.broadcast_personal_l(p, "blackjack-you-stand", "blackjack-player-stands")
        self._advance_to_next_player()

    def _action_split(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_split_enabled(p):
            return

        split_is_aces = p.hand[0].rank == 1 and p.hand[1].rank == 1
        split_card = p.hand.pop()
        p.split_hand = [split_card]
        p.split_bet = p.bet
        p.split_hand_done = False
        p.split_stood = False
        p.split_busted = False
        p.split_has_blackjack = False
        p.split_from_split_aces = split_is_aces

        p.chips -= p.bet
        p.active_hand_index = 0
        p.has_blackjack = False
        p.hand_done = False
        p.stood = False
        p.busted = False
        p.surrendered_main = False
        p.surrendered_split = False
        p.main_from_split_aces = split_is_aces

        main_draw = self._draw_card()
        if main_draw:
            p.hand.append(main_draw)
        split_draw = self._draw_card()
        if split_draw:
            p.split_hand.append(split_draw)

        self._sync_team_scores()
        self.broadcast_personal_l(
            p,
            "blackjack-you-split",
            "blackjack-player-splits",
            amount=p.bet,
        )

        if split_is_aces and self.options.split_aces_count_as_blackjack:
            main_total, _main_soft = self.hand_value(p.hand)
            split_total, _split_soft = self.hand_value(p.split_hand)
            p.has_blackjack = len(p.hand) == 2 and main_total == 21
            p.split_has_blackjack = len(p.split_hand) == 2 and split_total == 21

        if split_is_aces and self.options.split_aces_one_card_only:
            p.hand_done = True
            p.stood = True
            p.split_hand_done = True
            p.split_stood = True
            self.broadcast_personal_l(
                p,
                "blackjack-you-split-aces-auto-stand",
                "blackjack-player-splits-aces-auto-stand",
            )
            self._advance_to_next_player()
            return

        total, _is_soft = self.hand_value(p.hand)
        if total == 21:
            self._set_current_hand_done(p, done=True, stood=True)
            self.broadcast_personal_l(
                p,
                "blackjack-you-stand-auto",
                "blackjack-player-stands-auto",
            )
            self._advance_to_next_player()
            return

        self._announce_player_total(p)
        self._start_turn_timer()
        self.rebuild_all_menus()

    def _action_take_insurance(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_take_insurance_enabled(p):
            return

        amount = self._insurance_bet_amount(p)
        if amount <= 0 or p.chips < amount:
            return

        p.chips -= amount
        p.insurance_bet = amount
        p.insurance_decision_done = True
        self._sync_team_scores()
        self.broadcast_personal_l(
            p,
            "blackjack-you-take-insurance",
            "blackjack-player-takes-insurance",
            amount=amount,
        )
        self._advance_insurance_to_next_player()

    def _action_even_money(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_even_money_enabled(p):
            return

        p.took_even_money = True
        p.insurance_decision_done = True
        self.broadcast_personal_l(
            p,
            "blackjack-you-take-even-money",
            "blackjack-player-takes-even-money",
        )
        self._advance_insurance_to_next_player()

    def _action_decline_insurance(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        if not p or self._is_decline_insurance_enabled(p):
            return
        p.insurance_decision_done = True
        self.broadcast_personal_l(
            p,
            "blackjack-you-decline-insurance",
            "blackjack-player-declines-insurance",
        )
        self._advance_insurance_to_next_player()

    # ======================================================================
    # Status / read actions
    # ======================================================================

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, BlackjackPlayer) else None
        user = self.get_user(player)
        if not p or not user:
            return

        if p.split_bet > 0 and p.split_hand:
            total1, soft1 = self.hand_value(p.hand)
            total2, soft2 = self.hand_value(p.split_hand)
            user.speak_l(
                "blackjack-read-hand-response-split",
                hand1=read_cards(p.hand, user.locale),
                total1=self._total_text(user.locale, total1, soft1),
                hand2=read_cards(p.split_hand, user.locale),
                total2=self._total_text(user.locale, total2, soft2),
                active=p.active_hand_index + 1,
            )
            return

        total, is_soft = self.hand_value(p.hand)
        user.speak_l(
            "blackjack-read-hand-response",
            cards=read_cards(p.hand, user.locale),
            total=self._total_text(user.locale, total, is_soft),
        )

    def _action_read_dealer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        if not self.dealer_hand:
            user.speak_l("blackjack-no-dealer-cards")
            return

        if not self.dealer_hole_revealed:
            user.speak_l(
                "blackjack-read-dealer-up",
                card=card_name(self.dealer_hand[0], user.locale),
            )
            return

        total, is_soft = self.hand_value(self.dealer_hand)
        user.speak_l(
            "blackjack-read-dealer-full",
            cards=read_cards(self.dealer_hand, user.locale),
            total=self._total_text(user.locale, total, is_soft),
        )

    def _action_table_status(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        lines = [self._rules_readout_text(user.locale)]
        for p in self.get_active_players():
            if not isinstance(p, BlackjackPlayer):
                continue
            can_view_cards = self._can_view_player_cards(player, p)
            if can_view_cards and p.split_bet > 0 and p.hand and p.split_hand:
                total1, soft1 = self.hand_value(p.hand)
                total2, soft2 = self.hand_value(p.split_hand)
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-line-hands",
                        player=p.name,
                        chips=p.chips,
                        bet1=p.bet,
                        total1=self._total_text(user.locale, total1, soft1),
                        bet2=p.split_bet,
                        total2=self._total_text(user.locale, total2, soft2),
                    )
                )
            elif can_view_cards and self.phase == "players" and p.bet > 0 and p.hand:
                total, is_soft = self.hand_value(p.hand)
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-line-hand",
                        player=p.name,
                        chips=p.chips,
                        bet=p.bet,
                        total=self._total_text(user.locale, total, is_soft),
                    )
                )
            elif p.split_bet > 0:
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-line-bet",
                        player=p.name,
                        chips=p.chips,
                        bet=p.bet + p.split_bet,
                    )
                )
            elif p.bet > 0:
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-line-bet",
                        player=p.name,
                        chips=p.chips,
                        bet=p.bet,
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-line",
                        player=p.name,
                        chips=p.chips,
                    )
                )

        if self.dealer_hand:
            if self.dealer_hole_revealed:
                total, is_soft = self.hand_value(self.dealer_hand)
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-dealer",
                        cards=read_cards(self.dealer_hand, user.locale),
                        total=self._total_text(user.locale, total, is_soft),
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        user.locale,
                        "blackjack-status-dealer-up",
                        card=card_name(self.dealer_hand[0], user.locale),
                    )
                )

        user.speak(". ".join(lines) if lines else Localization.get(user.locale, "blackjack-no-active-players"))

    def _action_read_rules(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak(self._rules_readout_text(user.locale))

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("poker-timer-disabled")
        else:
            user.speak_l("poker-timer-remaining", seconds=remaining)

    # ======================================================================
    # Helpers
    # ======================================================================

    @staticmethod
    def card_blackjack_value(card: Card | None) -> int:
        if not card:
            return 0
        if card.rank == 1:
            return 11
        return min(card.rank, 10)

    @staticmethod
    def hand_value(cards: list[Card]) -> tuple[int, bool]:
        total = 0
        ace_count = 0
        for card in cards:
            if card.rank == 1:
                ace_count += 1
                total += 11
            else:
                total += min(card.rank, 10)

        while total > 21 and ace_count > 0:
            total -= 10
            ace_count -= 1

        return total, ace_count > 0

    def is_blackjack(self, cards: list[Card]) -> bool:
        if len(cards) != 2:
            return False
        total, _is_soft = self.hand_value(cards)
        return total == 21

    def _total_text(self, locale: str, total: int, is_soft: bool) -> str:
        if is_soft:
            return Localization.get(locale, "blackjack-total-soft", total=total)
        return Localization.get(locale, "blackjack-total-hard", total=total)

    def _bool_rule_text(self, locale: str, enabled: bool) -> str:
        return Localization.get(locale, "blackjack-rule-yes" if enabled else "blackjack-rule-no")

    def _rules_readout_text(self, locale: str) -> str:
        return Localization.get(
            locale,
            "blackjack-rules-readout",
            profile=Localization.get(locale, RULES_PROFILE_LABELS.get(self.options.rules_profile, "blackjack-rules-profile-vegas")),
            min_bet=self.options.table_min_bet,
            max_bet=self.options.table_max_bet,
            base_bet=self.options.base_bet,
            soft_17=self._bool_rule_text(locale, self.options.dealer_hits_soft_17),
            peek=self._bool_rule_text(locale, self.options.dealer_peeks_blackjack),
            insurance=self._bool_rule_text(locale, self.options.allow_insurance),
            surrender=self._bool_rule_text(locale, self.options.allow_late_surrender),
            payout=Localization.get(locale, BLACKJACK_PAYOUT_LABELS.get(self.options.blackjack_payout, "blackjack-payout-3-to-2")),
            double_rule=Localization.get(locale, DOUBLE_DOWN_RULE_LABELS.get(self.options.double_down_rule, "blackjack-double-rule-any-two")),
            das=self._bool_rule_text(locale, self.options.allow_double_after_split),
            split_rule=Localization.get(locale, SPLIT_RULE_LABELS.get(self.options.split_rule, "blackjack-split-rule-same-rank")),
            split_hands=self.options.max_split_hands,
            split_aces_one=self._bool_rule_text(locale, self.options.split_aces_one_card_only),
            split_aces_blackjack=self._bool_rule_text(locale, self.options.split_aces_count_as_blackjack),
            players_cards_face_up=self._bool_rule_text(locale, self.options.players_cards_face_up),
        )

    def _dealer_upcard_is_ace(self) -> bool:
        return bool(self.dealer_hand) and self.dealer_hand[0].rank == 1

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _broadcast_l_with_locale_args(
        self,
        message_id: str,
        args_for_locale: Callable[[str], dict[str, object]],
        *,
        buffer: str = "table",
        exclude: Player | None = None,
    ) -> None:
        """Broadcast with per-recipient localized kwargs."""
        for player in self.players:
            if player is exclude:
                continue
            locale = self._player_locale(player)
            kwargs = args_for_locale(locale)
            localized = Localization.get(locale, message_id, **kwargs)
            if hasattr(self, "record_transcript_event"):
                self.record_transcript_event(player, localized, buffer)
            user = self.get_user(player)
            if user:
                user.speak_l(message_id, buffer, **kwargs)

    def _broadcast_personal_l_with_locale_args(
        self,
        actor: BlackjackPlayer,
        personal_message_id: str,
        others_message_id: str,
        args_for_locale: Callable[[str], dict[str, object]],
        *,
        buffer: str = "table",
    ) -> None:
        """Personalized broadcast with per-recipient localized kwargs."""
        actor_locale = self._player_locale(actor)
        actor_kwargs = args_for_locale(actor_locale)
        actor_text = Localization.get(actor_locale, personal_message_id, **actor_kwargs)
        if hasattr(self, "record_transcript_event"):
            self.record_transcript_event(actor, actor_text, buffer)
        actor_user = self.get_user(actor)
        if actor_user:
            actor_user.speak_l(personal_message_id, buffer, **actor_kwargs)

        for player in self.players:
            if player is actor:
                continue
            locale = self._player_locale(player)
            kwargs = args_for_locale(locale)
            localized = Localization.get(
                locale, others_message_id, player=actor.name, **kwargs
            )
            if hasattr(self, "record_transcript_event"):
                self.record_transcript_event(player, localized, buffer)
            user = self.get_user(player)
            if user:
                user.speak_l(others_message_id, buffer, player=actor.name, **kwargs)

    def _can_view_player_cards(self, viewer: Player | None, target: BlackjackPlayer) -> bool:
        if self.options.players_cards_face_up:
            return True
        if not viewer:
            return False
        return viewer.id == target.id

    def _current_hand(self, player: BlackjackPlayer) -> list[Card]:
        return player.hand if player.active_hand_index == 0 else player.split_hand

    def _current_bet(self, player: BlackjackPlayer) -> int:
        return player.bet if player.active_hand_index == 0 else player.split_bet

    def _set_current_bet(self, player: BlackjackPlayer, amount: int) -> None:
        if player.active_hand_index == 0:
            player.bet = amount
        else:
            player.split_bet = amount

    def _current_hand_done(self, player: BlackjackPlayer) -> bool:
        return player.hand_done if player.active_hand_index == 0 else player.split_hand_done

    def _current_hand_surrendered(self, player: BlackjackPlayer) -> bool:
        return player.surrendered_main if player.active_hand_index == 0 else player.surrendered_split

    def _set_current_surrendered(self, player: BlackjackPlayer, surrendered: bool) -> None:
        if player.active_hand_index == 0:
            player.surrendered_main = surrendered
        else:
            player.surrendered_split = surrendered

    def _current_hand_from_split_aces(self, player: BlackjackPlayer) -> bool:
        return player.main_from_split_aces if player.active_hand_index == 0 else player.split_from_split_aces

    def _is_current_hand_locked_after_split_aces(self, player: BlackjackPlayer) -> bool:
        return self.options.split_aces_one_card_only and self._current_hand_from_split_aces(player)

    def _set_current_hand_done(
        self,
        player: BlackjackPlayer,
        *,
        done: bool,
        stood: bool | None = None,
        busted: bool | None = None,
        blackjack: bool | None = None,
    ) -> None:
        if player.active_hand_index == 0:
            player.hand_done = done
            if stood is not None:
                player.stood = stood
            if busted is not None:
                player.busted = busted
            if blackjack is not None:
                player.has_blackjack = blackjack
        else:
            player.split_hand_done = done
            if stood is not None:
                player.split_stood = stood
            if busted is not None:
                player.split_busted = busted
            if blackjack is not None:
                player.split_has_blackjack = blackjack

    def _set_current_doubled(self, player: BlackjackPlayer, doubled: bool) -> None:
        if player.active_hand_index == 0:
            player.doubled_main = doubled
        else:
            player.doubled_split = doubled

    def _insurance_bet_amount(self, player: BlackjackPlayer) -> int:
        return player.bet // 2

    def _can_take_insurance(self, player: BlackjackPlayer) -> bool:
        if not self.options.allow_insurance:
            return False
        if not self._dealer_upcard_is_ace():
            return False
        if player.bet <= 0 or player.has_blackjack:
            return False
        if player.insurance_decision_done:
            return False
        amount = self._insurance_bet_amount(player)
        if amount <= 0:
            return False
        return player.chips >= amount

    def _can_take_even_money(self, player: BlackjackPlayer) -> bool:
        if not self.options.allow_insurance:
            return False
        if not self._dealer_upcard_is_ace():
            return False
        if player.bet <= 0 or not player.has_blackjack:
            return False
        return not player.insurance_decision_done

    def _player_needs_insurance_decision(self, player: BlackjackPlayer) -> bool:
        if player.bet <= 0:
            return False
        if player.insurance_decision_done:
            return False
        return self._can_take_insurance(player) or self._can_take_even_money(player)

    def _player_has_pending_hand(self, player: BlackjackPlayer) -> bool:
        if player.bet > 0 and not player.hand_done:
            return True
        if player.split_bet > 0 and not player.split_hand_done:
            return True
        return False

    def _select_first_pending_hand(self, player: BlackjackPlayer) -> None:
        if player.bet > 0 and not player.hand_done:
            player.active_hand_index = 0
            return
        if player.split_bet > 0 and not player.split_hand_done:
            player.active_hand_index = 1

    def _switch_to_next_hand(self, player: BlackjackPlayer) -> bool:
        if player.active_hand_index == 0 and player.split_bet > 0 and not player.split_hand_done:
            player.active_hand_index = 1
            return True
        return False

    def _can_split(self, player: BlackjackPlayer) -> bool:
        if player.active_hand_index != 0:
            return False
        if self.options.max_split_hands <= 1:
            return False
        if player.split_bet > 0:
            return False
        if len(player.hand) != 2:
            return False
        if player.bet <= 0:
            return False
        if player.chips < player.bet:
            return False
        if self.options.split_rule == "same_rank":
            return player.hand[0].rank == player.hand[1].rank
        return self.card_blackjack_value(player.hand[0]) == self.card_blackjack_value(player.hand[1])

    def _can_double_down(self, player: BlackjackPlayer) -> bool:
        hand = self._current_hand(player)
        bet = self._current_bet(player)
        if len(hand) != 2:
            return False
        if player.active_hand_index == 1 and not self.options.allow_double_after_split:
            return False
        if self._is_current_hand_locked_after_split_aces(player):
            return False
        if bet <= 0:
            return False
        if player.chips < bet:
            return False
        total, _is_soft = self.hand_value(hand)
        if self.options.double_down_rule == "9_to_11":
            return total in (9, 10, 11)
        if self.options.double_down_rule == "10_to_11":
            return total in (10, 11)
        return True

    def _can_surrender(self, player: BlackjackPlayer) -> bool:
        if not self.options.allow_late_surrender:
            return False
        if player.active_hand_index != 0:
            return False
        if player.split_bet > 0:
            return False
        if len(player.hand) != 2:
            return False
        if player.has_blackjack:
            return False
        if player.surrendered_main:
            return False
        if player.bet <= 0:
            return False
        return not player.hand_done

    def _blackjack_total_payout(self, bet: int) -> int:
        if self.options.blackjack_payout == "6_to_5":
            return bet + ((bet * 6) // 5)
        if self.options.blackjack_payout == "1_to_1":
            return bet * 2
        return bet + ((bet * 3) // 2)

    def _ensure_deck(self, min_cards: int = 1) -> None:
        if self.deck and self.deck.size() >= min_cards:
            return
        self.deck, _ = DeckFactory.standard_deck(num_decks=self.options.deck_count)
        self.deck.shuffle()

    def _draw_card(self) -> Card | None:
        self._ensure_deck(min_cards=1)
        return self.deck.draw_one() if self.deck else None

    def _post_bets(self, players: list[BlackjackPlayer]) -> None:
        for player in players:
            if player.chips <= 0:
                player.bet = 0
                player.hand_done = True
                continue

            bet = min(player.chips, self.options.base_bet, self.options.table_max_bet)
            if player.chips >= self.options.table_min_bet and bet < self.options.table_min_bet:
                bet = self.options.table_min_bet
            if bet <= 0:
                player.bet = 0
                player.hand_done = True
                continue
            player.chips -= bet
            player.bet = bet
            self.broadcast_personal_l(
                player,
                "blackjack-you-bet",
                "blackjack-player-bets",
                amount=bet,
            )

        self._sync_team_scores()

    def _deal_initial_cards(self, players: list[BlackjackPlayer]) -> None:
        for _ in range(2):
            for player in players:
                card = self._draw_card()
                if card:
                    player.hand.append(card)
            dealer_card = self._draw_card()
            if dealer_card:
                self.dealer_hand.append(dealer_card)

        if self.dealer_hand:
            self._broadcast_l_with_locale_args(
                "blackjack-dealer-shows",
                lambda locale: {"card": card_name(self.dealer_hand[0], locale)},
            )

        for player in players:
            total, is_soft = self.hand_value(player.hand)
            if self.options.players_cards_face_up:
                self._broadcast_personal_l_with_locale_args(
                    player,
                    "blackjack-you-have",
                    "blackjack-player-has",
                    lambda locale: {
                        "cards": read_cards(player.hand, locale),
                        "total": self._total_text(locale, total, is_soft),
                    },
                )
            else:
                user = self.get_user(player)
                if user:
                    user.speak_l(
                        "blackjack-you-have",
                        cards=read_cards(player.hand, user.locale),
                        total=self._total_text(user.locale, total, is_soft),
                    )
            if self.is_blackjack(player.hand):
                player.has_blackjack = True
                player.hand_done = True
                player.stood = True
                self.broadcast_personal_l(player, "blackjack-you-blackjack", "blackjack-player-blackjack")

    def _reveal_dealer_hand(self) -> None:
        if self.dealer_hole_revealed:
            return
        self.dealer_hole_revealed = True

        if len(self.dealer_hand) >= 2:
            total, is_soft = self.hand_value(self.dealer_hand)
            self._broadcast_l_with_locale_args(
                "blackjack-dealer-reveals",
                lambda locale: {
                    "card": card_name(self.dealer_hand[1], locale),
                    "cards": read_cards(self.dealer_hand, locale),
                    "total": self._total_text(locale, total, is_soft),
                },
            )

    def _announce_player_total(self, player: BlackjackPlayer) -> None:
        total, is_soft = self.hand_value(self._current_hand(player))
        if player.split_bet > 0:
            if self.options.players_cards_face_up:
                self._broadcast_personal_l_with_locale_args(
                    player,
                    "blackjack-your-total-hand",
                    "blackjack-player-total-hand",
                    lambda locale: {
                        "hand": player.active_hand_index + 1,
                        "total": self._total_text(locale, total, is_soft),
                    },
                )
            else:
                user = self.get_user(player)
                if user:
                    user.speak_l(
                        "blackjack-your-total-hand",
                        hand=player.active_hand_index + 1,
                        total=self._total_text(user.locale, total, is_soft),
                    )
            return
        if self.options.players_cards_face_up:
            self._broadcast_personal_l_with_locale_args(
                player,
                "blackjack-your-total",
                "blackjack-player-total",
                lambda locale: {"total": self._total_text(locale, total, is_soft)},
            )
        else:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "blackjack-your-total",
                    total=self._total_text(user.locale, total, is_soft),
                )

    def _start_turn_timer(self) -> None:
        try:
            seconds = int(self.options.turn_timer)
        except ValueError:
            seconds = 0

        if seconds <= 0:
            self.timer.clear()
            return

        self.timer.start(seconds)

    def _handle_turn_timeout(self) -> None:
        current = self.current_player
        if not isinstance(current, BlackjackPlayer):
            return
        if self.phase == "insurance":
            action_id = bot_think(self, current) or "decline_insurance"
        else:
            action_id = bot_think(self, current) or "stand"
        self.execute_action(current, action_id)

    def _evaluate_current_hand_after_draw(self, player: BlackjackPlayer) -> None:
        hand = self._current_hand(player)
        total, is_soft = self.hand_value(hand)
        if total > 21:
            self._set_current_hand_done(player, done=True, busted=True)
            self.broadcast_personal_l(
                player,
                "blackjack-you-bust",
                "blackjack-player-bust",
                total=self._total_text(self._player_locale(player), total, is_soft),
            )
            self._advance_to_next_player()
            return

        if total == 21:
            self._set_current_hand_done(player, done=True, stood=True)
            self.broadcast_personal_l(
                player,
                "blackjack-you-stand-auto",
                "blackjack-player-stands-auto",
            )
            self._advance_to_next_player()
            return

        self._announce_player_total(player)
        self._start_turn_timer()
        self.rebuild_all_menus()

    def _settle_hand(self) -> None:
        self.phase = "settle"
        self.timer.clear()

        dealer_total, _dealer_soft = self.hand_value(self.dealer_hand)
        dealer_blackjack = self.is_blackjack(self.dealer_hand)
        dealer_bust = dealer_total > 21

        for player in self.get_active_players():
            if not isinstance(player, BlackjackPlayer):
                continue

            if player.insurance_bet > 0:
                if dealer_blackjack:
                    insurance_profit = player.insurance_bet * 2
                    player.chips += player.insurance_bet * 3
                    self.broadcast_personal_l(
                        player,
                        "blackjack-you-insurance-wins",
                        "blackjack-player-insurance-wins",
                        amount=insurance_profit,
                    )
                else:
                    self.broadcast_personal_l(
                        player,
                        "blackjack-you-insurance-loses",
                        "blackjack-player-insurance-loses",
                        amount=player.insurance_bet,
                    )

            hands: list[tuple[int, list[Card], int, bool, bool, bool]] = []
            if player.bet > 0:
                hands.append((0, player.hand, player.bet, player.busted, player.has_blackjack, player.surrendered_main))
            if player.split_bet > 0:
                hands.append(
                    (
                        1,
                        player.split_hand,
                        player.split_bet,
                        player.split_busted,
                        player.split_has_blackjack,
                        player.surrendered_split,
                    )
                )
            if not hands:
                continue

            for hand_index, cards, bet, busted, is_blackjack, surrendered in hands:
                if surrendered:
                    continue

                if hand_index == 0 and player.took_even_money:
                    player.chips += bet * 2
                    self._broadcast_settle_result(player, hand_index, "even_money", amount=bet)
                    continue

                if busted:
                    self._broadcast_settle_result(player, hand_index, "lose", amount=bet)
                    continue

                player_total, _player_soft = self.hand_value(cards)

                if is_blackjack and not dealer_blackjack:
                    payout = self._blackjack_total_payout(bet)
                    player.chips += payout
                    self._broadcast_settle_result(player, hand_index, "win", amount=payout - bet)
                elif dealer_blackjack and not is_blackjack:
                    self._broadcast_settle_result(player, hand_index, "lose", amount=bet)
                elif dealer_bust or player_total > dealer_total:
                    player.chips += bet * 2
                    self._broadcast_settle_result(player, hand_index, "win", amount=bet)
                elif player_total == dealer_total:
                    player.chips += bet
                    self._broadcast_settle_result(player, hand_index, "push")
                else:
                    self._broadcast_settle_result(player, hand_index, "lose", amount=bet)

            if player.chips == 0:
                self.broadcast_personal_l(
                    player,
                    "blackjack-you-broke",
                    "blackjack-player-broke",
                )

        self._sync_team_scores()

        remaining = [
            p
            for p in self.get_active_players()
            if isinstance(p, BlackjackPlayer) and p.chips > 0
        ]
        total_competitors = [
            p
            for p in self.get_active_players()
            if isinstance(p, BlackjackPlayer)
        ]
        if len(remaining) == 0:
            self._end_game(None)
            return
        if len(total_competitors) > 1 and len(remaining) <= 1:
            self._end_game(remaining[0] if remaining else None)
            return

        self.next_hand_wait_ticks = 40
        self.rebuild_all_menus()

    def _broadcast_settle_result(
        self,
        player: BlackjackPlayer,
        hand_index: int,
        result: str,
        amount: int | None = None,
    ) -> None:
        is_split = player.split_bet > 0
        if result == "even_money":
            self.broadcast_personal_l(
                player,
                "blackjack-you-even-money-win",
                "blackjack-player-even-money-win",
                amount=amount or 0,
            )
            return
        if result == "win":
            if is_split:
                self.broadcast_personal_l(
                    player,
                    "blackjack-you-win-hand",
                    "blackjack-player-wins-hand",
                    hand=hand_index + 1,
                    amount=amount or 0,
                )
            else:
                self.broadcast_personal_l(
                    player,
                    "blackjack-you-win",
                    "blackjack-player-wins",
                    amount=amount or 0,
                )
            return
        if result == "lose":
            if is_split:
                self.broadcast_personal_l(
                    player,
                    "blackjack-you-lose-hand",
                    "blackjack-player-loses-hand",
                    hand=hand_index + 1,
                    amount=amount or 0,
                )
            else:
                self.broadcast_personal_l(
                    player,
                    "blackjack-you-lose",
                    "blackjack-player-loses",
                    amount=amount or 0,
                )
            return
        if is_split:
            self.broadcast_personal_l(
                player,
                "blackjack-you-push-hand",
                "blackjack-player-push-hand",
                hand=hand_index + 1,
            )
        else:
            self.broadcast_personal_l(
                player,
                "blackjack-you-push",
                "blackjack-player-push",
            )

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for player in self.players:
            if not isinstance(player, BlackjackPlayer) or player.is_spectator:
                continue
            team = self._team_manager.get_team(player.name)
            if team:
                team.total_score = player.chips

    def _end_game(self, winner: BlackjackPlayer | None) -> None:
        self.phase = "finished"
        self.timer.clear()
        if winner:
            self.broadcast_personal_l(
                winner,
                "blackjack-you-win-game",
                "blackjack-player-wins-game",
                chips=winner.chips,
            )
        self.finish_game()

    # ======================================================================
    # Results
    # ======================================================================

    def build_game_result(self) -> GameResult:
        active = [p for p in self.get_active_players() if isinstance(p, BlackjackPlayer)]
        winner = max(active, key=lambda p: p.chips, default=None)
        final_chips = {p.name: p.chips for p in active}

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
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_chips": winner.chips if winner else 0,
                "final_chips": final_chips,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_chips = result.custom_data.get("final_chips", {})
        sorted_scores = sorted(final_chips.items(), key=lambda item: item[1], reverse=True)
        for index, (name, chips) in enumerate(sorted_scores, 1):
            lines.append(f"{index}. {name}: {chips} chips")
        return lines
