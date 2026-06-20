"""Classic Monopoly game implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from server.core.ui.keybinds import KeybindState

from ...game_utils.actions import Action, ActionSet, EditboxInput, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.game_status import GameStatus
from ...game_utils.options import BoolOption, GameOptions, IntOption, option_field
from ...messages.localization import Localization
from ..base import Game, Player
from ..registry import register_game
from .board import (
    CARD_TEXT,
    CHANCE_CARD_IDS,
    COMMUNITY_CHEST_CARD_IDS,
    DEFAULT_BOARD_ID,
    PASS_GO_CASH,
    STARTING_CASH,
    BoardDefinition,
    MonopolySpace,
    get_board,
)


BAIL_AMOUNT = 50
MIN_AUCTION_INCREMENT = 10
HOTEL_LEVEL = 5
JAIL_POSITION = 10
GO_POSITION = 0
JAIL_CARD_TRADE_VALUE = 50


@dataclass
class MonopolyPlayer(Player):
    """Player state for Monopoly."""

    position: int = GO_POSITION
    cash: int = STARTING_CASH
    bankrupt: bool = False
    in_jail: bool = False
    jail_turns: int = 0
    jail_free_cards: list[str] = field(default_factory=list)
    last_roll: list[int] = field(default_factory=list)


@dataclass
class MonopolyPropertyState:
    """Mutable state for a purchasable board space."""

    owner_id: str = ""
    mortgaged: bool = False
    houses: int = 0


@dataclass
class MonopolyDebt:
    """Debt waiting for the debtor to raise funds or declare bankruptcy."""

    debtor_id: str
    amount: int
    creditor_id: str = ""
    reason: str = ""
    feeds_pot: bool = False


@dataclass
class MonopolyAuction:
    """English auction state for an unowned property."""

    property_id: str
    highest_bidder_id: str = ""
    highest_bid: int = 0
    passed_player_ids: list[str] = field(default_factory=list)


@dataclass
class MonopolyTradeOffer:
    """A pending or in-progress trade between two players.

    Each side may bundle any number of properties, a cash amount, and a Get
    Out of Jail Free card. While a player composes an offer it lives in
    ``trade_draft_offers``; once sent it becomes the game's ``pending_trade``.
    """

    proposer_id: str = ""
    target_id: str = ""
    give_cash: int = 0
    receive_cash: int = 0
    give_property_ids: list[str] = field(default_factory=list)
    receive_property_ids: list[str] = field(default_factory=list)
    give_jail_card: bool = False
    receive_jail_card: bool = False
    summary: str = ""


@dataclass
class MonopolyOptions(GameOptions):
    """Configurable house rules for Monopoly.

    Every default reproduces the official Hasbro ruleset (Free Parking does
    nothing, $1500 starting cash). Turning an option on enables a popular
    house rule without affecting the faithful default experience.
    """

    starting_cash: int = option_field(
        IntOption(
            default=STARTING_CASH,
            min_val=500,
            max_val=10000,
            value_key="cash",
            label="monopoly-option-starting-cash",
            prompt="monopoly-option-enter-starting-cash",
            change_msg="monopoly-option-changed-starting-cash",
            description="monopoly-option-desc-starting-cash",
        )
    )
    free_parking_jackpot: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="monopoly-option-free-parking-jackpot",
            change_msg="monopoly-option-changed-free-parking-jackpot",
            description="monopoly-option-desc-free-parking-jackpot",
        )
    )
    free_parking_seed: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=2000,
            value_key="cash",
            label="monopoly-option-free-parking-seed",
            prompt="monopoly-option-enter-free-parking-seed",
            change_msg="monopoly-option-changed-free-parking-seed",
            description="monopoly-option-desc-free-parking-seed",
        ),
        visible_when=("free_parking_jackpot", lambda value: bool(value)),
    )


@dataclass
@register_game
class MonopolyGame(Game):
    """Classic Monopoly with a data-driven board profile."""

    # Menu options are encoded as "value|label" (see _encode_property_option and
    # the trade pickers); this opts into showing only the label half.
    _menu_options_encode_ids = True

    players: list[MonopolyPlayer] = field(default_factory=list)
    options: MonopolyOptions = field(default_factory=MonopolyOptions)

    board_id: str = DEFAULT_BOARD_ID
    property_states: dict[str, MonopolyPropertyState] = field(default_factory=dict)
    chance_deck: list[str] = field(default_factory=list)
    community_chest_deck: list[str] = field(default_factory=list)
    bank_houses: int = 32
    bank_hotels: int = 12
    free_parking_pot: int = 0

    phase: str = "await_roll"
    pending_purchase_property_id: str = ""
    pending_debt: MonopolyDebt | None = None
    auction: MonopolyAuction | None = None
    pending_trade: MonopolyTradeOffer | None = None
    trade_draft_offers: dict[str, MonopolyTradeOffer] = field(default_factory=dict)
    extra_roll_pending: bool = False
    doubles_count: int = 0
    winner_id: str = ""

    @classmethod
    def get_name(cls) -> str:
        return "Monopoly"

    @classmethod
    def get_type(cls) -> str:
        return "monopoly"

    @classmethod
    def get_category(cls) -> str:
        return "category-board-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    @property
    def board(self) -> BoardDefinition:
        return get_board(self.board_id)

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> MonopolyPlayer:
        return MonopolyPlayer(id=player_id, name=name, is_bot=is_bot)

    def rebuild_runtime_state(self) -> None:
        self._ensure_property_states()

    def on_start(self) -> None:
        """Start a classic Monopoly game."""

        self.status = GameStatus.PLAYING
        self.game_active = True
        self.phase = "await_roll"
        self.pending_purchase_property_id = ""
        self.pending_debt = None
        self.auction = None
        self.pending_trade = None
        self.trade_draft_offers.clear()
        self.extra_roll_pending = False
        self.doubles_count = 0
        self.winner_id = ""

        board = self.board
        self.property_states = {
            space.space_id: MonopolyPropertyState() for space in board.purchasable_spaces
        }
        self.chance_deck = list(CHANCE_CARD_IDS)
        self.community_chest_deck = list(COMMUNITY_CHEST_CARD_IDS)
        random.shuffle(self.chance_deck)
        random.shuffle(self.community_chest_deck)
        self.bank_houses = board.total_houses
        self.bank_hotels = board.total_hotels
        self.free_parking_pot = (
            self.options.free_parking_seed if self.options.free_parking_jackpot else 0
        )

        starting_cash = self.options.starting_cash
        for player in self.get_active_players():
            mp: MonopolyPlayer = player  # type: ignore[assignment]
            mp.position = GO_POSITION
            mp.cash = starting_cash
            mp.bankrupt = False
            mp.in_jail = False
            mp.jail_turns = 0
            mp.jail_free_cards.clear()
            mp.last_roll.clear()

        self.set_turn_players(self.get_active_players())
        self.broadcast_l("monopoly-started", board=board.name, cash=self._money(starting_cash))
        self._start_turn(rebuild_all=True)

    def create_turn_action_set(self, player: MonopolyPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="roll",
                label=Localization.get(locale, "monopoly-roll-dice"),
                handler="_action_roll",
                is_enabled="_is_roll_enabled",
                is_hidden="_is_roll_hidden",
            )
        )
        action_set.add(
            Action(
                id="buy_property",
                label=Localization.get(locale, "monopoly-buy-property"),
                handler="_action_buy_property",
                is_enabled="_is_buy_property_enabled",
                is_hidden="_is_buy_property_hidden",
            )
        )
        action_set.add(
            Action(
                id="auction_property",
                label=Localization.get(locale, "monopoly-auction-property"),
                handler="_action_auction_property",
                is_enabled="_is_auction_property_enabled",
                is_hidden="_is_buy_property_hidden",
            )
        )
        action_set.add(
            Action(
                id="pay_debt",
                label=Localization.get(locale, "monopoly-pay-debt"),
                handler="_action_pay_debt",
                is_enabled="_is_pay_debt_enabled",
                is_hidden="_is_pay_debt_hidden",
            )
        )
        action_set.add(
            Action(
                id="declare_bankruptcy",
                label=Localization.get(locale, "monopoly-declare-bankruptcy"),
                handler="_action_declare_bankruptcy",
                is_enabled="_is_declare_bankruptcy_enabled",
                is_hidden="_is_declare_bankruptcy_hidden",
            )
        )
        action_set.add(
            Action(
                id="offer_trade",
                label=Localization.get(locale, "monopoly-offer-trade"),
                handler="_action_offer_trade",
                is_enabled="_is_offer_trade_enabled",
                is_hidden="_is_offer_trade_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-trade-partner",
                    options="_trade_partner_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        # Interactive trade builder — these are only visible while the player
        # is composing an offer (see _is_trade_builder_hidden).
        action_set.add(
            Action(
                id="trade_give",
                label=Localization.get(locale, "monopoly-trade-give"),
                handler="_action_trade_toggle_give",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-trade-give",
                    options="_trade_give_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="trade_request",
                label=Localization.get(locale, "monopoly-trade-request"),
                handler="_action_trade_toggle_request",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-trade-request",
                    options="_trade_request_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="trade_cash",
                label=Localization.get(locale, "monopoly-trade-cash"),
                handler="_action_trade_set_cash",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
                input_request=EditboxInput(prompt="monopoly-enter-trade-cash", default="0"),
            )
        )
        action_set.add(
            Action(
                id="trade_jail",
                label=Localization.get(locale, "monopoly-trade-jail"),
                handler="_action_trade_toggle_jail",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_jail_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-trade-jail",
                    options="_trade_jail_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="trade_review",
                label=Localization.get(locale, "monopoly-trade-review"),
                handler="_action_trade_review",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
            )
        )
        action_set.add(
            Action(
                id="trade_send",
                label=Localization.get(locale, "monopoly-trade-send"),
                handler="_action_trade_send",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
            )
        )
        action_set.add(
            Action(
                id="trade_cancel",
                label=Localization.get(locale, "monopoly-trade-cancel"),
                handler="_action_trade_cancel",
                is_enabled="_is_trade_builder_enabled",
                is_hidden="_is_trade_builder_hidden",
            )
        )
        action_set.add(
            Action(
                id="accept_trade",
                label=Localization.get(locale, "monopoly-accept-trade"),
                handler="_action_accept_trade",
                is_enabled="_is_accept_trade_enabled",
                is_hidden="_is_pending_trade_hidden",
            )
        )
        action_set.add(
            Action(
                id="decline_trade",
                label=Localization.get(locale, "monopoly-decline-trade"),
                handler="_action_decline_trade",
                is_enabled="_is_decline_trade_enabled",
                is_hidden="_is_pending_trade_hidden",
            )
        )
        action_set.add(
            Action(
                id="auction_bid",
                label=Localization.get(locale, "monopoly-auction-bid"),
                handler="_action_auction_bid",
                is_enabled="_is_auction_bid_enabled",
                is_hidden="_is_auction_action_hidden",
                input_request=EditboxInput(
                    prompt="monopoly-enter-auction-bid",
                    default="",
                    bot_input="_bot_input_auction_bid",
                ),
            )
        )
        action_set.add(
            Action(
                id="auction_pass",
                label=Localization.get(locale, "monopoly-auction-pass"),
                handler="_action_auction_pass",
                is_enabled="_is_auction_pass_enabled",
                is_hidden="_is_auction_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="pay_bail",
                label=Localization.get(locale, "monopoly-pay-bail"),
                handler="_action_pay_bail",
                is_enabled="_is_pay_bail_enabled",
                is_hidden="_is_pay_bail_hidden",
            )
        )
        action_set.add(
            Action(
                id="use_jail_card",
                label=Localization.get(locale, "monopoly-use-jail-card"),
                handler="_action_use_jail_card",
                is_enabled="_is_use_jail_card_enabled",
                is_hidden="_is_pay_bail_hidden",
            )
        )
        action_set.add(
            Action(
                id="mortgage_property",
                label=Localization.get(locale, "monopoly-mortgage-property"),
                handler="_action_mortgage_property",
                is_enabled="_is_mortgage_property_enabled",
                is_hidden="_is_mortgage_property_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-mortgage",
                    options="_mortgage_property_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="unmortgage_property",
                label=Localization.get(locale, "monopoly-unmortgage-property"),
                handler="_action_unmortgage_property",
                is_enabled="_is_unmortgage_property_enabled",
                is_hidden="_is_unmortgage_property_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-unmortgage",
                    options="_unmortgage_property_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="build_house",
                label=Localization.get(locale, "monopoly-build-house"),
                handler="_action_build_house",
                is_enabled="_is_build_house_enabled",
                is_hidden="_is_build_house_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-build",
                    options="_build_property_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="sell_house",
                label=Localization.get(locale, "monopoly-sell-house"),
                handler="_action_sell_house",
                is_enabled="_is_sell_house_enabled",
                is_hidden="_is_sell_house_hidden",
                input_request=MenuInput(
                    prompt="monopoly-select-property-sell",
                    options="_sell_building_options",
                    bot_select="_bot_select_first_option",
                ),
            )
        )
        action_set.add(
            Action(
                id="end_turn",
                label=Localization.get(locale, "monopoly-end-turn"),
                handler="_action_end_turn",
                is_enabled="_is_end_turn_enabled",
                is_hidden="_is_end_turn_hidden",
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="check_assets",
                label=Localization.get(locale, "monopoly-check-assets"),
                handler="_action_check_assets",
                is_enabled="_is_check_assets_enabled",
                is_hidden="_is_check_assets_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_board",
                label=Localization.get(locale, "monopoly-check-board"),
                handler="_action_check_board",
                is_enabled="_is_check_assets_enabled",
                is_hidden="_is_check_assets_hidden",
            )
        )
        for action_id in ("check_board", "check_assets"):
            if action_id in action_set._order:
                action_set._order.remove(action_id)
                action_set._order.insert(0, action_id)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("r", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("space", "Roll dice", ["roll"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Buy property", ["buy_property"], state=KeybindState.ACTIVE)
        self.define_keybind("a", "Auction property", ["auction_property"], state=KeybindState.ACTIVE)
        self.define_keybind("e", "End turn", ["end_turn"], state=KeybindState.ACTIVE)
        self.define_keybind("ctrl+t", "Offer trade", ["offer_trade"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "Check assets", ["check_assets"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+c", "Check board", ["check_board"], state=KeybindState.ACTIVE)

    # ------------------------------------------------------------------
    # Action visibility and guards
    # ------------------------------------------------------------------

    def get_all_visible_actions(self, player: Player):
        """Focus the menu on the trade builder while an offer is being composed.

        When the player has an open trade draft, only the ``trade_*`` builder
        actions are shown; otherwise those builder actions stay hidden.
        """
        if self._should_hide_idle_turn_menu(player):
            return []
        visible = super().get_all_visible_actions(player)
        building = self._active_player(player).id in self.trade_draft_offers
        if building:
            return [rv for rv in visible if rv.action.id.startswith("trade_")]
        return [rv for rv in visible if not rv.action.id.startswith("trade_")]

    def rebuild_player_menu(self, player: Player, *, position: int | None = None) -> None:
        """Show no passive turn menu to idle players waiting for someone else."""
        if self._should_hide_idle_turn_menu(player):
            user = self.get_user(player)
            if user:
                user.remove_menu("turn_menu")
            return
        super().rebuild_player_menu(player, position=position)

    def _active_player(self, player: Player) -> MonopolyPlayer:
        return player  # type: ignore[return-value]

    def _is_playing(self) -> bool:
        return self.status == GameStatus.PLAYING and self.game_active

    def _should_hide_idle_turn_menu(self, player: Player) -> bool:
        if not self._is_playing() or player.is_spectator or player.is_bot:
            return False
        if self._is_current_turn_player(player):
            return False
        if self.pending_debt and self.pending_debt.debtor_id == player.id:
            return False
        if self.pending_trade and self.pending_trade.target_id == player.id:
            return False
        if self.auction and not self._is_bankrupt(player) and player.id in {p.id for p in self._auction_players()}:
            return False
        if self._active_player(player).id in self.trade_draft_offers:
            return False
        return True

    def _is_bankrupt(self, player: Player) -> bool:
        return bool(getattr(player, "bankrupt", False))

    def _is_action_menu_only_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_current_turn_player(self, player: Player) -> bool:
        return self.current_player == player and not self._is_bankrupt(player)

    def _can_manage_assets(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if player.is_spectator:
            return "action-not-available"
        if self._is_bankrupt(player):
            return "monopoly-player-bankrupt-disabled"
        if self.auction:
            return "monopoly-auction-active"
        if self.pending_trade:
            return "monopoly-trade-pending"
        if self.pending_purchase_property_id and player == self.current_player:
            return "monopoly-resolve-property-first"
        if self.pending_debt and self.pending_debt.debtor_id != player.id:
            return "monopoly-debt-pending"
        return None

    def _is_roll_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if self.phase != "await_roll":
            return "monopoly-roll-not-available"
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        return None

    def _is_roll_hidden(self, player: Player) -> Visibility:
        if self._is_playing() and self.phase == "await_roll" and self._is_current_turn_player(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_buy_property_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        if self.phase != "await_purchase" or not self.pending_purchase_property_id:
            return "monopoly-no-property-to-buy"
        space = self._space(self.pending_purchase_property_id)
        if self._active_player(player).cash < space.price:
            return "monopoly-not-enough-cash"
        return None

    def _is_auction_property_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        if self.phase != "await_purchase" or not self.pending_purchase_property_id:
            return "monopoly-no-property-to-auction"
        return None

    def _is_buy_property_hidden(self, player: Player) -> Visibility:
        if self.phase == "await_purchase" and self._is_current_turn_player(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_pay_debt_enabled(self, player: Player) -> str | None:
        if not self.pending_debt or self.pending_debt.debtor_id != player.id:
            return "monopoly-no-debt"
        if self._active_player(player).cash < self.pending_debt.amount:
            return "monopoly-not-enough-cash"
        return None

    def _is_pay_debt_hidden(self, player: Player) -> Visibility:
        if self.pending_debt and self.pending_debt.debtor_id == player.id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_declare_bankruptcy_enabled(self, player: Player) -> str | None:
        if not self.pending_debt or self.pending_debt.debtor_id != player.id:
            return "monopoly-no-debt"
        return None

    def _is_declare_bankruptcy_hidden(self, player: Player) -> Visibility:
        return self._is_pay_debt_hidden(player)

    def _is_auction_bid_enabled(self, player: Player) -> str | None:
        if not self.auction:
            return "monopoly-no-auction-active"
        if self._is_bankrupt(player) or player.id not in {p.id for p in self._auction_players()}:
            return "action-not-available"
        if player.id in self.auction.passed_player_ids:
            return "monopoly-auction-already-passed"
        if self._active_player(player).cash < self._minimum_auction_bid():
            return "monopoly-not-enough-cash"
        return None

    def _is_auction_pass_enabled(self, player: Player) -> str | None:
        if not self.auction:
            return "monopoly-no-auction-active"
        if self._is_bankrupt(player) or player.id not in {p.id for p in self._auction_players()}:
            return "action-not-available"
        if player.id in self.auction.passed_player_ids:
            return "monopoly-auction-already-passed"
        return None

    def _is_auction_action_hidden(self, player: Player) -> Visibility:
        if self.auction and not self._is_bankrupt(player) and not player.is_spectator:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_pay_bail_enabled(self, player: Player) -> str | None:
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        mp = self._active_player(player)
        if not mp.in_jail:
            return "monopoly-not-in-jail"
        if mp.cash < BAIL_AMOUNT:
            return "monopoly-not-enough-cash"
        return None

    def _is_pay_bail_hidden(self, player: Player) -> Visibility:
        mp = self._active_player(player)
        if self.phase == "await_roll" and self._is_current_turn_player(player) and mp.in_jail:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_use_jail_card_enabled(self, player: Player) -> str | None:
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        mp = self._active_player(player)
        if not mp.in_jail:
            return "monopoly-not-in-jail"
        if not mp.jail_free_cards:
            return "monopoly-no-jail-card"
        return None

    def _is_mortgage_property_enabled(self, player: Player) -> str | None:
        error = self._can_manage_assets(player)
        if error:
            return error
        if not self._mortgage_property_options(player):
            return "monopoly-no-mortgage-options"
        return None

    def _is_mortgage_property_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_mortgage_property_enabled(player) is None else Visibility.HIDDEN

    def _is_unmortgage_property_enabled(self, player: Player) -> str | None:
        error = self._can_manage_assets(player)
        if error:
            return error
        if not self._unmortgage_property_options(player):
            return "monopoly-no-unmortgage-options"
        return None

    def _is_unmortgage_property_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_unmortgage_property_enabled(player) is None else Visibility.HIDDEN

    def _is_build_house_enabled(self, player: Player) -> str | None:
        error = self._can_manage_assets(player)
        if error:
            return error
        if self.pending_debt:
            return "monopoly-debt-pending"
        if not self._build_property_options(player):
            return "monopoly-no-build-options"
        return None

    def _is_build_house_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_build_house_enabled(player) is None else Visibility.HIDDEN

    def _is_sell_house_enabled(self, player: Player) -> str | None:
        error = self._can_manage_assets(player)
        if error:
            return error
        if not self._sell_building_options(player):
            return "monopoly-no-sell-options"
        return None

    def _is_sell_house_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_sell_house_enabled(player) is None else Visibility.HIDDEN

    def _is_offer_trade_enabled(self, player: Player) -> str | None:
        error = self._can_manage_assets(player)
        if error:
            return error
        if self._active_player(player).id in self.trade_draft_offers:
            return "monopoly-trade-pending"
        if not self._trade_partner_options(player):
            return "monopoly-no-trade-options"
        return None

    def _is_offer_trade_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self._is_offer_trade_enabled(player) is None else Visibility.HIDDEN

    def _is_trade_builder_enabled(self, player: Player) -> str | None:
        if self._active_player(player).id not in self.trade_draft_offers:
            return "monopoly-no-trade-pending"
        return None

    def _is_trade_builder_hidden(self, player: Player) -> Visibility:
        building = self._active_player(player).id in self.trade_draft_offers
        return Visibility.VISIBLE if building else Visibility.HIDDEN

    def _is_trade_jail_hidden(self, player: Player) -> Visibility:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return Visibility.HIDDEN
        target = self._player_by_id(draft.target_id)
        if mp.jail_free_cards or (target and target.jail_free_cards):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_accept_trade_enabled(self, player: Player) -> str | None:
        if not self.pending_trade or self.pending_trade.target_id != player.id:
            return "monopoly-no-trade-pending"
        return self._validate_trade_offer(self.pending_trade)

    def _is_decline_trade_enabled(self, player: Player) -> str | None:
        if not self.pending_trade or self.pending_trade.target_id != player.id:
            return "monopoly-no-trade-pending"
        if self._is_bankrupt(player):
            return "monopoly-player-bankrupt-disabled"
        return None

    def _is_pending_trade_hidden(self, player: Player) -> Visibility:
        if self.pending_trade and self.pending_trade.target_id == player.id:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_end_turn_enabled(self, player: Player) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        if not self._is_current_turn_player(player):
            return "action-not-your-turn"
        if self.phase != "post_roll":
            return "monopoly-roll-first"
        return None

    def _is_end_turn_hidden(self, player: Player) -> Visibility:
        if self.phase == "post_roll" and self._is_current_turn_player(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_check_assets_enabled(self, player: Player) -> str | None:
        if not self._is_playing() and self.status != GameStatus.FINISHED:
            return "action-not-playing"
        return None

    def _is_check_assets_hidden(self, player: Player) -> Visibility:
        if self._is_check_assets_enabled(player) is None:
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ------------------------------------------------------------------
    # Turn flow
    # ------------------------------------------------------------------

    def _start_turn(self, *, rebuild_all: bool = False, previous_player: Player | None = None) -> None:
        player = self.current_player
        if not player:
            return
        mp = self._active_player(player)
        if mp.bankrupt:
            self.advance_turn(announce=False)
            self._start_turn(rebuild_all=True)
            return

        self.phase = "await_roll"
        self.pending_purchase_property_id = ""
        self.pending_debt = None
        self.auction = None
        self.extra_roll_pending = False
        self.broadcast_l("monopoly-turn", player=mp.name)
        if mp.in_jail:
            self.broadcast_l("monopoly-in-jail-turn", player=mp.name, turns=mp.jail_turns)

        BotHelper.jolt_bot(mp, ticks=random.randint(8, 18))
        if rebuild_all:
            self.rebuild_all_menus()
        elif previous_player and previous_player != mp:
            self.rebuild_player_menu(previous_player)
        # Always snap the active player's cursor to their primary action (Roll)
        # at the start of their turn so it never sticks on an always-visible
        # item such as "Check assets".
        self.rebuild_player_menu(mp, position=1)

    def _focus_active_player(self, player: MonopolyPlayer) -> None:
        """Snap a still-active player's cursor to their primary (first) action.

        After a rebuild the client keeps the cursor on the previously selected
        item by id, which makes it stick on an always-visible entry such as
        "Check assets". When this player still holds the turn, move their cursor
        back to the first action (Roll, Buy, Pay debt, ... for the phase).
        """
        if self.current_player == player and not self._active_player(player).bankrupt:
            self.rebuild_player_menu(self._active_player(player), position=1)

    def _action_roll(self, player: MonopolyPlayer, action_id: str) -> None:
        if player.in_jail:
            self._roll_from_jail(player)
            return

        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        total = die1 + die2
        player.last_roll = [die1, die2]
        is_double = die1 == die2
        self.extra_roll_pending = is_double
        if is_double:
            self.doubles_count += 1
        else:
            self.doubles_count = 0

        self.broadcast_l(
            "monopoly-roll-result",
            player=player.name,
            die1=die1,
            die2=die2,
            total=total,
        )

        if self.doubles_count >= 3:
            self.broadcast_l("monopoly-three-doubles-jail", player=player.name)
            self._send_to_jail(player)
            self.extra_roll_pending = False
            self._complete_roll_resolution(player)
            self.rebuild_all_menus()
            return

        self._move_steps(player, total)
        if self._resolve_landing(player, roll_total=total):
            self._complete_roll_resolution(player)
        self.rebuild_all_menus()
        self._focus_active_player(player)

    def _roll_from_jail(self, player: MonopolyPlayer) -> None:
        die1, die2 = random.randint(1, 6), random.randint(1, 6)
        total = die1 + die2
        player.last_roll = [die1, die2]
        self.extra_roll_pending = False

        if die1 == die2:
            player.in_jail = False
            player.jail_turns = 0
            self.broadcast_l(
                "monopoly-jail-roll-doubles",
                player=player.name,
                die1=die1,
                die2=die2,
            )
            self._move_steps(player, total)
            if self._resolve_landing(player, roll_total=total):
                self._complete_roll_resolution(player)
            self.rebuild_all_menus()
            self._focus_active_player(player)
            return

        player.jail_turns += 1
        self.broadcast_l(
            "monopoly-jail-roll-failed",
            player=player.name,
            die1=die1,
            die2=die2,
            attempts=player.jail_turns,
        )
        if player.jail_turns >= 3:
            if player.cash >= BAIL_AMOUNT:
                self._pay_bank(player, BAIL_AMOUNT, "bail")
                player.in_jail = False
                player.jail_turns = 0
                self._move_steps(player, total)
                if self._resolve_landing(player, roll_total=total):
                    self._complete_roll_resolution(player)
            else:
                self._set_debt(player, BAIL_AMOUNT, None, "bail")
        else:
            self._complete_roll_resolution(player)
        self.rebuild_all_menus()
        self._focus_active_player(player)

    def _action_end_turn(self, player: MonopolyPlayer, action_id: str) -> None:
        self.doubles_count = 0
        self.extra_roll_pending = False
        previous = player
        self.advance_turn(announce=False)
        self._start_turn(previous_player=previous)

    def _complete_roll_resolution(self, player: MonopolyPlayer) -> None:
        if not self._is_playing() or player.bankrupt:
            return
        if self.pending_purchase_property_id or self.pending_debt or self.auction:
            return
        if self.extra_roll_pending and not player.in_jail:
            self.phase = "await_roll"
            self.broadcast_l("monopoly-roll-again", player=player.name)
            BotHelper.jolt_bot(player, ticks=random.randint(8, 18))
        else:
            self._advance_after_turn_completion(player)

    def _advance_after_turn_completion(self, player: MonopolyPlayer) -> None:
        if not self._is_playing() or player.bankrupt or self.current_player != player:
            return
        self.doubles_count = 0
        self.extra_roll_pending = False
        previous = player
        self.advance_turn(announce=False)
        self._start_turn(rebuild_all=True, previous_player=previous)

    # ------------------------------------------------------------------
    # Space resolution and cards
    # ------------------------------------------------------------------

    def _resolve_landing(
        self,
        player: MonopolyPlayer,
        *,
        roll_total: int,
        railroad_rent_multiplier: int = 1,
        utility_rent_multiplier: int | None = None,
    ) -> bool:
        space = self._space_at(player.position)
        self.broadcast_l("monopoly-landed", player=player.name, space=space.name)

        if space.kind == "go":
            return True
        if space.kind == "free_parking":
            if self.options.free_parking_jackpot:
                payout = self.free_parking_pot
                self.free_parking_pot = self.options.free_parking_seed
                if payout > 0:
                    player.cash += payout
                    self.broadcast_l(
                        "monopoly-free-parking-jackpot",
                        player=player.name,
                        amount=self._money(payout),
                    )
                    return True
            self.broadcast_l("monopoly-free-parking", player=player.name)
            return True
        if space.kind == "jail":
            self.broadcast_l("monopoly-just-visiting", player=player.name)
            return True
        if space.kind == "go_to_jail":
            self._send_to_jail(player)
            self.extra_roll_pending = False
            return True
        if space.kind == "tax":
            return self._pay_bank(player, space.tax_amount, space.name)
        if space.kind == "chance":
            return self._draw_card(player, "chance", roll_total=roll_total)
        if space.kind == "community_chest":
            return self._draw_card(player, "community_chest", roll_total=roll_total)
        if space.is_purchasable:
            return self._resolve_property_landing(
                player,
                space,
                roll_total=roll_total,
                railroad_rent_multiplier=railroad_rent_multiplier,
                utility_rent_multiplier=utility_rent_multiplier,
            )
        return True

    def _resolve_property_landing(
        self,
        player: MonopolyPlayer,
        space: MonopolySpace,
        *,
        roll_total: int,
        railroad_rent_multiplier: int = 1,
        utility_rent_multiplier: int | None = None,
    ) -> bool:
        state = self.property_states[space.space_id]
        if not state.owner_id:
            self.pending_purchase_property_id = space.space_id
            self.phase = "await_purchase"
            self.broadcast_l(
                "monopoly-property-available",
                property=space.name,
                price=self._money(space.price),
            )
            return False

        if state.owner_id == player.id:
            self.broadcast_l("monopoly-landed-own-property", player=player.name, property=space.name)
            return True
        if state.mortgaged:
            self.broadcast_l("monopoly-mortgaged-no-rent", player=player.name, property=space.name)
            return True

        owner = self._player_by_id(state.owner_id)
        if not owner or owner.bankrupt:
            return True

        rent = self._calculate_rent(
            space,
            roll_total=roll_total,
            railroad_multiplier=railroad_rent_multiplier,
            utility_multiplier=utility_rent_multiplier,
        )
        return self._pay_player(player, owner, rent, f"rent for {space.name}")

    def _draw_card(self, player: MonopolyPlayer, deck_name: str, *, roll_total: int) -> bool:
        deck = self.chance_deck if deck_name == "chance" else self.community_chest_deck
        if not deck:
            deck.extend(CHANCE_CARD_IDS if deck_name == "chance" else COMMUNITY_CHEST_CARD_IDS)
            random.shuffle(deck)
        card_id = deck.pop(0)
        text = CARD_TEXT.get(card_id, card_id.replace("_", " "))
        self.broadcast_l("monopoly-card-drawn", player=player.name, deck=deck_name, text=text)

        keep_card = card_id.startswith("get_out_of_jail_free")
        if keep_card:
            player.jail_free_cards.append(card_id)
            return True

        deck.append(card_id)
        return self._apply_card(player, card_id, roll_total=roll_total)

    def _apply_card(self, player: MonopolyPlayer, card_id: str, *, roll_total: int) -> bool:
        if card_id == "advance_to_go":
            self._move_to(player, GO_POSITION, collect_go=True)
            return True
        if card_id == "advance_to_illinois_avenue":
            self._move_to(player, 24, collect_go=True)
            return self._resolve_landing(player, roll_total=roll_total)
        if card_id == "advance_to_st_charles_place":
            self._move_to(player, 11, collect_go=True)
            return self._resolve_landing(player, roll_total=roll_total)
        if card_id == "advance_to_nearest_utility":
            self._move_to_nearest(player, "utility")
            card_roll = random.randint(1, 6) + random.randint(1, 6)
            return self._resolve_landing(
                player,
                roll_total=card_roll,
                utility_rent_multiplier=10,
            )
        if card_id == "advance_to_nearest_railroad":
            self._move_to_nearest(player, "railroad")
            return self._resolve_landing(
                player,
                roll_total=roll_total,
                railroad_rent_multiplier=2,
            )
        if card_id == "go_back_three":
            player.position = (player.position - 3) % len(self.board.spaces)
            self.broadcast_l("monopoly-moved-to", player=player.name, space=self._space_at(player.position).name)
            return self._resolve_landing(player, roll_total=roll_total)
        if card_id == "go_to_jail":
            self._send_to_jail(player)
            self.extra_roll_pending = False
            return True
        if card_id == "take_trip_to_reading_railroad":
            self._move_to(player, 5, collect_go=True)
            return self._resolve_landing(player, roll_total=roll_total)
        if card_id == "take_walk_on_boardwalk":
            self._move_to(player, 39, collect_go=True)
            return self._resolve_landing(player, roll_total=roll_total)
        if card_id in {
            "bank_dividend_50",
            "sale_of_stock_collect_50",
            "holiday_fund_matures_100",
            "income_tax_refund_20",
            "life_insurance_matures_100",
            "consultancy_fee_collect_25",
            "beauty_contest_collect_10",
            "inherit_100",
            "building_loan_matures_150",
            "crossword_competition_100",
            "bank_error_collect_200",
        }:
            card_payouts = {
                "bank_dividend_50": 50,
                "sale_of_stock_collect_50": 50,
                "holiday_fund_matures_100": 100,
                "income_tax_refund_20": 20,
                "life_insurance_matures_100": 100,
                "consultancy_fee_collect_25": 25,
                "beauty_contest_collect_10": 10,
                "inherit_100": 100,
                "building_loan_matures_150": 150,
                "crossword_competition_100": 100,
                "bank_error_collect_200": 200,
            }
            card_reasons = {
                "bank_dividend_50": "bank dividend",
                "sale_of_stock_collect_50": "sale of stock",
                "holiday_fund_matures_100": "holiday fund",
                "income_tax_refund_20": "income tax refund",
                "life_insurance_matures_100": "life insurance",
                "consultancy_fee_collect_25": "consultancy fee",
                "beauty_contest_collect_10": "beauty contest prize",
                "inherit_100": "inheritance",
                "building_loan_matures_150": "building loan",
                "crossword_competition_100": "crossword competition",
                "bank_error_collect_200": "bank error",
            }
            self._credit(player, card_payouts[card_id], card_reasons[card_id])
            return True
        if card_id in {
            "doctor_fee_pay_50",
            "hospital_fees_pay_100",
            "school_fees_pay_50",
            "speeding_fine_15",
        }:
            card_fees = {
                "doctor_fee_pay_50": 50,
                "hospital_fees_pay_100": 100,
                "school_fees_pay_50": 50,
                "speeding_fine_15": 15,
            }
            card_reasons = {
                "doctor_fee_pay_50": "doctor's fee",
                "hospital_fees_pay_100": "hospital fees",
                "school_fees_pay_50": "school fees",
                "speeding_fine_15": "speeding fine",
            }
            return self._pay_bank(player, card_fees[card_id], card_reasons[card_id])
        if card_id == "general_repairs":
            amount = self._building_count(player, houses=True) * 25 + self._building_count(player, hotels=True) * 100
            return self._pay_bank(player, amount, "repairs")
        if card_id == "street_repairs":
            amount = self._building_count(player, houses=True) * 40 + self._building_count(player, hotels=True) * 115
            return self._pay_bank(player, amount, "street repairs")
        if card_id == "birthday_collect_10_each":
            for other in self._solvent_players():
                if other.id != player.id:
                    self._pay_player(other, player, 10, "birthday")
            return self.pending_debt is None
        if card_id == "chairman_pay_50_each":
            total = 50 * (len([p for p in self._solvent_players() if p.id != player.id]))
            if not self._pay_bank(player, total, "chairman payment", feeds_pot=False):
                return False
            for other in self._solvent_players():
                if other.id != player.id:
                    self._credit(other, 50, "chairman payment")
            return True
        return True

    # ------------------------------------------------------------------
    # Purchases and auctions
    # ------------------------------------------------------------------

    def _action_buy_property(self, player: MonopolyPlayer, action_id: str) -> None:
        space = self._space(self.pending_purchase_property_id)
        if player.cash < space.price:
            return
        player.cash -= space.price
        self.property_states[space.space_id].owner_id = player.id
        self.pending_purchase_property_id = ""
        self.broadcast_l(
            "monopoly-property-bought",
            player=player.name,
            property=space.name,
            price=self._money(space.price),
        )
        self._announce_completed_set(player, space)
        self._complete_roll_resolution(player)
        self.rebuild_all_menus()
        self._focus_active_player(player)

    def _action_auction_property(self, player: MonopolyPlayer, action_id: str) -> None:
        property_id = self.pending_purchase_property_id
        if not property_id:
            return
        self.pending_purchase_property_id = ""
        # Every solvent player bids in an auction, so drop any open trade
        # drafts to return their menus from the builder to normal play.
        self.trade_draft_offers.clear()
        self.auction = MonopolyAuction(property_id=property_id)
        self.phase = "auction"
        space = self._space(property_id)
        self.broadcast_l(
            "monopoly-auction-started",
            property=space.name,
            amount=self._money(self._minimum_auction_bid()),
        )
        BotHelper.jolt_bots(self, ticks=6, players=self._auction_players())
        self.rebuild_all_menus()

    def _action_auction_bid(self, player: MonopolyPlayer, amount_text: str, action_id: str) -> None:
        if not self.auction:
            return
        try:
            amount = int(amount_text.strip().replace("$", ""))
        except ValueError:
            user = self.get_user(player)
            if user:
                user.speak_l("monopoly-invalid-bid")
            return
        minimum = self._minimum_auction_bid()
        if amount < minimum or amount > player.cash:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "monopoly-bid-out-of-range",
                    minimum=self._money(minimum),
                    cash=self._money(player.cash),
                )
            return

        self.auction.highest_bidder_id = player.id
        self.auction.highest_bid = amount
        if player.id in self.auction.passed_player_ids:
            self.auction.passed_player_ids.remove(player.id)
        space = self._space(self.auction.property_id)
        self.broadcast_l(
            "monopoly-auction-bid-placed",
            player=player.name,
            amount=self._money(amount),
            property=space.name,
        )
        self._finalize_auction_if_ready()
        self.rebuild_all_menus()

    def _action_auction_pass(self, player: MonopolyPlayer, action_id: str) -> None:
        if not self.auction:
            return
        if player.id not in self.auction.passed_player_ids:
            self.auction.passed_player_ids.append(player.id)
        space = self._space(self.auction.property_id)
        self.broadcast_l("monopoly-auction-pass-event", player=player.name, property=space.name)
        self._finalize_auction_if_ready()
        self.rebuild_all_menus()

    def _finalize_auction_if_ready(self) -> None:
        if not self.auction:
            return
        players = self._auction_players()
        if not players:
            self.auction = None
            self._resume_after_auction()
            return
        if not self.auction.highest_bidder_id:
            if len(self.auction.passed_player_ids) >= len(players):
                space = self._space(self.auction.property_id)
                self.broadcast_l("monopoly-auction-no-bids", property=space.name)
                self.auction = None
                self._resume_after_auction()
            return

        remaining = [
            player
            for player in players
            if player.id != self.auction.highest_bidder_id
            and player.id not in self.auction.passed_player_ids
        ]
        if remaining:
            return

        winner = self._player_by_id(self.auction.highest_bidder_id)
        space = self._space(self.auction.property_id)
        amount = self.auction.highest_bid
        self.auction = None
        if winner and winner.cash >= amount:
            winner.cash -= amount
            self.property_states[space.space_id].owner_id = winner.id
            self.broadcast_l(
                "monopoly-auction-won",
                player=winner.name,
                property=space.name,
                amount=self._money(amount),
            )
            self._announce_completed_set(winner, space)
        self._resume_after_auction()

    def _resume_after_auction(self) -> None:
        current = self.current_player
        if current and not self._is_bankrupt(current):
            self._complete_roll_resolution(self._active_player(current))
        else:
            self.phase = "await_roll"

    # ------------------------------------------------------------------
    # Asset actions
    # ------------------------------------------------------------------

    def _action_mortgage_property(
        self, player: MonopolyPlayer, property_id: str, action_id: str
    ) -> None:
        property_id = self._decode_property_option(property_id)
        if property_id not in self.property_states:
            return
        space = self._space(property_id)
        state = self.property_states[property_id]
        if state.owner_id != player.id or state.mortgaged or not self._can_mortgage(space):
            return
        state.mortgaged = True
        player.cash += space.mortgage_value
        self.broadcast_l(
            "monopoly-property-mortgaged",
            player=player.name,
            property=space.name,
            amount=self._money(space.mortgage_value),
        )
        self._after_asset_change(player)

    def _action_unmortgage_property(
        self, player: MonopolyPlayer, property_id: str, action_id: str
    ) -> None:
        property_id = self._decode_property_option(property_id)
        if property_id not in self.property_states:
            return
        space = self._space(property_id)
        state = self.property_states[property_id]
        cost = self._unmortgage_cost(space)
        if state.owner_id != player.id or not state.mortgaged or player.cash < cost:
            return
        player.cash -= cost
        state.mortgaged = False
        self.broadcast_l(
            "monopoly-property-unmortgaged",
            player=player.name,
            property=space.name,
            amount=self._money(cost),
        )
        self._after_asset_change(player)

    def _action_build_house(self, player: MonopolyPlayer, property_id: str, action_id: str) -> None:
        property_id = self._decode_property_option(property_id)
        space = self._space(property_id)
        state = self.property_states[property_id]
        if not self._can_build_on(player, space):
            return
        if player.cash < space.house_cost:
            return
        if state.houses == 4:
            if self.bank_hotels <= 0:
                return
            self.bank_hotels -= 1
            self.bank_houses += 4
            label = "hotel"
        else:
            if self.bank_houses <= 0:
                return
            self.bank_houses -= 1
            label = "house"
        state.houses += 1
        player.cash -= space.house_cost
        self.broadcast_l(
            "monopoly-building-built",
            player=player.name,
            building=label,
            property=space.name,
            amount=self._money(space.house_cost),
            level=self._building_label(state.houses),
        )
        self._after_asset_change(player)

    def _action_sell_house(self, player: MonopolyPlayer, property_id: str, action_id: str) -> None:
        property_id = self._decode_property_option(property_id)
        space = self._space(property_id)
        state = self.property_states[property_id]
        if state.owner_id != player.id or state.houses <= 0 or not self._can_sell_from(space):
            return
        amount = space.house_cost // 2
        if state.houses == HOTEL_LEVEL:
            if self.bank_houses < 4:
                return
            self.bank_hotels += 1
            self.bank_houses -= 4
        else:
            self.bank_houses += 1
        state.houses -= 1
        player.cash += amount
        self.broadcast_l(
            "monopoly-building-sold",
            player=player.name,
            property=space.name,
            amount=self._money(amount),
            level=self._building_label(state.houses),
        )
        self._after_asset_change(player)

    def _after_asset_change(self, player: MonopolyPlayer) -> None:
        if self.pending_debt and self.pending_debt.debtor_id == player.id and player.cash >= self.pending_debt.amount:
            self.broadcast_l("monopoly-debt-can-pay", player=player.name)
        self.rebuild_all_menus()

    def _action_pay_debt(self, player: MonopolyPlayer, action_id: str) -> None:
        if not self.pending_debt or self.pending_debt.debtor_id != player.id:
            return
        debt = self.pending_debt
        if player.cash < debt.amount:
            return
        player.cash -= debt.amount
        creditor = self._player_by_id(debt.creditor_id) if debt.creditor_id else None
        if creditor:
            creditor.cash += debt.amount
            self.broadcast_l(
                "monopoly-paid-player",
                player=player.name,
                target=creditor.name,
                amount=self._money(debt.amount),
                reason=debt.reason,
            )
        else:
            if debt.feeds_pot:
                self._bank_income(debt.amount)
            self.broadcast_l(
                "monopoly-paid-bank",
                player=player.name,
                amount=self._money(debt.amount),
                reason=debt.reason,
            )
        self.pending_debt = None
        current = self._active_player(self.current_player) if self.current_player else player
        self._complete_roll_resolution(current)
        self.rebuild_all_menus()

    def _action_declare_bankruptcy(self, player: MonopolyPlayer, action_id: str) -> None:
        if not self.pending_debt or self.pending_debt.debtor_id != player.id:
            return
        creditor = self._player_by_id(self.pending_debt.creditor_id) if self.pending_debt.creditor_id else None
        self._bankrupt_player(player, creditor)
        if self.game_active and self.current_player and self.current_player != player:
            self._complete_roll_resolution(self._active_player(self.current_player))
        self.rebuild_all_menus()

    def _action_pay_bail(self, player: MonopolyPlayer, action_id: str) -> None:
        if player.cash < BAIL_AMOUNT or not player.in_jail:
            return
        self._pay_bank(player, BAIL_AMOUNT, "bail")
        player.in_jail = False
        player.jail_turns = 0
        self.broadcast_l("monopoly-bail-paid", player=player.name, amount=self._money(BAIL_AMOUNT))
        self.rebuild_all_menus()

    def _action_use_jail_card(self, player: MonopolyPlayer, action_id: str) -> None:
        if not player.in_jail or not player.jail_free_cards:
            return
        card_id = player.jail_free_cards.pop(0)
        if card_id.endswith("chance"):
            self.chance_deck.append(card_id)
        else:
            self.community_chest_deck.append(card_id)
        player.in_jail = False
        player.jail_turns = 0
        self.broadcast_l("monopoly-jail-card-used", player=player.name)
        self.rebuild_all_menus()

    # ------------------------------------------------------------------
    # Trades
    # ------------------------------------------------------------------

    def _action_offer_trade(
        self, player: MonopolyPlayer, selected_partner: str, action_id: str
    ) -> None:
        """Begin composing a trade by choosing a partner; opens the builder."""
        mp = self._active_player(player)
        if self.pending_trade or mp.id in self.trade_draft_offers:
            return
        target = self._trade_partner_from_option(mp, selected_partner)
        if not target:
            user = self.get_user(player)
            if user:
                user.speak_l("monopoly-trade-no-longer-valid")
            return
        self.trade_draft_offers[mp.id] = MonopolyTradeOffer(
            proposer_id=mp.id, target_id=target.id
        )
        user = self.get_user(player)
        if user:
            user.speak_l("monopoly-trade-building", target=target.name)
        self.rebuild_all_menus()

    def _action_trade_toggle_give(
        self, player: MonopolyPlayer, property_id: str, action_id: str
    ) -> None:
        self._toggle_trade_property(player, property_id, side="give")

    def _action_trade_toggle_request(
        self, player: MonopolyPlayer, property_id: str, action_id: str
    ) -> None:
        self._toggle_trade_property(player, property_id, side="receive")

    def _toggle_trade_property(
        self, player: MonopolyPlayer, property_id: str, *, side: str
    ) -> None:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return
        property_id = self._decode_property_option(property_id)
        if property_id not in self.property_states:
            return
        ids = draft.give_property_ids if side == "give" else draft.receive_property_ids
        if property_id in ids:
            ids.remove(property_id)
        else:
            owner_id = mp.id if side == "give" else draft.target_id
            space = self._space(property_id)
            state = self.property_states[property_id]
            if state.owner_id != owner_id or not self._can_trade_property(space):
                user = self.get_user(player)
                if user:
                    user.speak_l("monopoly-trade-no-longer-valid")
                return
            ids.append(property_id)
        self.rebuild_all_menus()

    def _action_trade_set_cash(
        self, player: MonopolyPlayer, amount_text: str, action_id: str
    ) -> None:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return
        amount = self._parse_trade_amount(amount_text)
        if amount is None:
            user = self.get_user(player)
            if user:
                user.speak_l("monopoly-invalid-trade-amount")
            return
        # Positive: the proposer pays the partner. Negative: the partner pays.
        if amount >= 0:
            draft.give_cash = amount
            draft.receive_cash = 0
        else:
            draft.give_cash = 0
            draft.receive_cash = abs(amount)
        self.rebuild_all_menus()

    def _action_trade_toggle_jail(
        self, player: MonopolyPlayer, selected: str, action_id: str
    ) -> None:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return
        side = selected.split("|", 1)[0]
        if side == "give":
            draft.give_jail_card = not draft.give_jail_card
        elif side == "receive":
            draft.receive_jail_card = not draft.receive_jail_card
        self.rebuild_all_menus()

    def _action_trade_review(self, player: MonopolyPlayer, action_id: str) -> None:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return
        user = self.get_user(player)
        if not user:
            return
        lines = [self._trade_summary(draft)]
        for label, ids in (
            ("You give", draft.give_property_ids),
            ("You receive", draft.receive_property_ids),
        ):
            for property_id in ids:
                lines.append(f"{label}: {self._property_detail_line(property_id)}")
        self.status_box(player, lines)

    def _action_trade_send(self, player: MonopolyPlayer, action_id: str) -> None:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return
        draft.summary = self._trade_summary(draft)
        error = self._validate_trade_offer(draft)
        if error:
            user = self.get_user(player)
            if user:
                user.speak_l(error)
            return
        self.trade_draft_offers.pop(mp.id, None)
        self._offer_trade(mp, draft)

    def _action_trade_cancel(self, player: MonopolyPlayer, action_id: str) -> None:
        mp = self._active_player(player)
        if self.trade_draft_offers.pop(mp.id, None) is not None:
            user = self.get_user(player)
            if user:
                user.speak_l("monopoly-trade-cancelled")
        self.rebuild_all_menus()

    def _offer_trade(self, player: MonopolyPlayer, offer: MonopolyTradeOffer) -> None:
        error = self._validate_trade_offer(offer)
        if error:
            user = self.get_user(player)
            if user:
                user.speak_l(error)
            return

        self.pending_trade = offer
        target = self._player_by_id(offer.target_id)
        self.broadcast_l(
            "monopoly-trade-offered",
            player=player.name,
            target=target.name if target else "Unknown",
            summary=offer.summary,
        )
        if target:
            BotHelper.jolt_bot(target, ticks=random.randint(4, 9))
        self.rebuild_all_menus()

    def _action_accept_trade(self, player: MonopolyPlayer, action_id: str) -> None:
        offer = self.pending_trade
        if not offer or offer.target_id != player.id:
            return
        error = self._validate_trade_offer(offer)
        if error:
            self.pending_trade = None
            user = self.get_user(player)
            if user:
                user.speak_l("monopoly-trade-no-longer-valid")
            self.rebuild_all_menus()
            return

        proposer = self._player_by_id(offer.proposer_id)
        target = self._player_by_id(offer.target_id)
        if not proposer or not target:
            self.pending_trade = None
            self.rebuild_all_menus()
            return

        proposer.cash = proposer.cash - offer.give_cash + offer.receive_cash
        target.cash = target.cash - offer.receive_cash + offer.give_cash

        transferred_spaces: list[tuple[MonopolyPlayer, MonopolySpace]] = []
        for property_id in offer.give_property_ids:
            space = self._space(property_id)
            self.property_states[space.space_id].owner_id = target.id
            transferred_spaces.append((target, space))
        for property_id in offer.receive_property_ids:
            space = self._space(property_id)
            self.property_states[space.space_id].owner_id = proposer.id
            transferred_spaces.append((proposer, space))

        if offer.give_jail_card and proposer.jail_free_cards:
            target.jail_free_cards.append(proposer.jail_free_cards.pop(0))
        if offer.receive_jail_card and target.jail_free_cards:
            proposer.jail_free_cards.append(target.jail_free_cards.pop(0))

        for property_id in offer.receive_property_ids:
            self._charge_trade_mortgage_interest(proposer, property_id)
        for property_id in offer.give_property_ids:
            self._charge_trade_mortgage_interest(target, property_id)

        self.pending_trade = None
        self.broadcast_l(
            "monopoly-trade-accepted",
            player=proposer.name,
            target=target.name,
            summary=offer.summary,
        )
        for owner, space in transferred_spaces:
            self._announce_completed_set(owner, space)
        self._announce_payable_pending_debt(proposer)
        self._announce_payable_pending_debt(target)
        self.rebuild_all_menus()

    def _action_decline_trade(self, player: MonopolyPlayer, action_id: str) -> None:
        offer = self.pending_trade
        if not offer or offer.target_id != player.id:
            return
        proposer = self._player_by_id(offer.proposer_id)
        self.pending_trade = None
        self.broadcast_l(
            "monopoly-trade-declined",
            player=proposer.name if proposer else "Unknown",
            target=player.name,
            summary=offer.summary,
        )
        self.rebuild_all_menus()

    # ------------------------------------------------------------------
    # Menu option helpers
    # ------------------------------------------------------------------

    def _mortgage_property_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        options = []
        for space in self._owned_spaces(mp):
            state = self.property_states[space.space_id]
            if not state.mortgaged and self._can_mortgage(space):
                options.append(self._encode_property_option(space, space.mortgage_value))
        return options

    def _unmortgage_property_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        options = []
        for space in self._owned_spaces(mp):
            state = self.property_states[space.space_id]
            cost = self._unmortgage_cost(space)
            if state.mortgaged and mp.cash >= cost:
                options.append(self._encode_property_option(space, cost))
        return options

    def _build_property_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        return [
            self._encode_property_option(space, space.house_cost)
            for space in self._owned_spaces(mp)
            if self._can_build_on(mp, space)
        ]

    def _sell_building_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        return [
            self._encode_property_option(space, space.house_cost // 2)
            for space in self._owned_spaces(mp)
            if self.property_states[space.space_id].houses > 0 and self._can_sell_from(space)
        ]

    def _can_offer_trade(self, proposer: MonopolyPlayer) -> bool:
        """Whether a player may start composing a trade right now."""
        if proposer.bankrupt or proposer.is_spectator or self.pending_trade:
            return False
        if self.auction or self.pending_purchase_property_id:
            return False
        if self.pending_debt and self.pending_debt.debtor_id != proposer.id:
            return False
        return True

    def _trade_partner_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        if not self._can_offer_trade(mp):
            return []
        return [
            f"{target.id}|{target.name}"
            for target in self._solvent_players()
            if target.id != mp.id and not target.is_spectator
        ]

    def _trade_partner_from_option(
        self, player: MonopolyPlayer, selected_partner: str
    ) -> MonopolyPlayer | None:
        target_id = selected_partner.split("|", 1)[0]
        target = self._player_by_id(target_id)
        if not target or target.id == player.id or target.bankrupt or target.is_spectator:
            return None
        return target

    def _trade_property_options(self, player: Player, *, side: str) -> list[str]:
        """Checklist options for one side of the trade draft (give/request)."""
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return []
        if side == "give":
            owner_id, selected = mp.id, draft.give_property_ids
        else:
            owner_id, selected = draft.target_id, draft.receive_property_ids
        owner = self._player_by_id(owner_id)
        if not owner:
            return []
        options = []
        for space in self._owned_spaces(owner):
            if not self._can_trade_property(space):
                continue
            mark = "* " if space.space_id in selected else ""
            options.append(f"{space.space_id}|{mark}{space.name}")
        return options

    def _trade_give_options(self, player: Player) -> list[str]:
        return self._trade_property_options(player, side="give")

    def _trade_request_options(self, player: Player) -> list[str]:
        return self._trade_property_options(player, side="receive")

    def _trade_jail_options(self, player: Player) -> list[str]:
        mp = self._active_player(player)
        draft = self.trade_draft_offers.get(mp.id)
        if not draft:
            return []
        target = self._player_by_id(draft.target_id)
        options = []
        if mp.jail_free_cards:
            mark = "* " if draft.give_jail_card else ""
            options.append(f"give|{mark}Include your Get Out of Jail Free card")
        if target and target.jail_free_cards:
            mark = "* " if draft.receive_jail_card else ""
            options.append(f"receive|{mark}Request {target.name}'s Get Out of Jail Free card")
        return options

    def _bot_select_first_option(self, player: Player, options: list[str]) -> str | None:
        return options[0] if options else None

    def _bot_input_auction_bid(self, player: MonopolyPlayer) -> str | None:
        if not self.auction:
            return None
        space = self._space(self.auction.property_id)
        minimum = self._minimum_auction_bid()
        max_bid = min(player.cash, max(space.price, space.mortgage_value * 2))
        if self._owns_group_candidate(player, space):
            max_bid = min(player.cash, space.price + 100)
        if minimum <= max_bid and player.cash - minimum >= 100:
            return str(minimum)
        return None

    # ------------------------------------------------------------------
    # Core economic helpers
    # ------------------------------------------------------------------

    def _ensure_property_states(self) -> None:
        for space in self.board.purchasable_spaces:
            self.property_states.setdefault(space.space_id, MonopolyPropertyState())

    def _money(self, amount: int) -> str:
        return f"${amount}"

    def _space(self, space_id: str) -> MonopolySpace:
        return self.board.get_space(space_id)

    def _space_at(self, index: int) -> MonopolySpace:
        return self.board.get_space_at(index)

    def _player_by_id(self, player_id: str) -> MonopolyPlayer | None:
        player = self.get_player_by_id(player_id)
        return player if player is None else self._active_player(player)

    def _solvent_players(self) -> list[MonopolyPlayer]:
        return [
            self._active_player(player)
            for player in self.get_active_players()
            if not self._active_player(player).bankrupt
        ]

    def _bank_income(self, amount: int) -> None:
        """Route money paid to the bank into the Free Parking pot when enabled.

        Implements the optional Free Parking jackpot house rule: taxes, fees,
        and bail collected by the bank accumulate in a pot that a player wins
        by landing on Free Parking. No-op under the official ruleset.
        """
        if amount > 0 and self.options.free_parking_jackpot:
            self.free_parking_pot += amount

    def _credit(self, player: MonopolyPlayer, amount: int, reason: str) -> None:
        if amount <= 0:
            return
        player.cash += amount
        self.broadcast_l(
            "monopoly-collected",
            player=player.name,
            amount=self._money(amount),
            reason=reason,
        )

    def _pay_bank(
        self, player: MonopolyPlayer, amount: int, reason: str, *, feeds_pot: bool = True
    ) -> bool:
        if amount <= 0:
            return True
        if player.cash >= amount:
            player.cash -= amount
            if feeds_pot:
                self._bank_income(amount)
            self.broadcast_l(
                "monopoly-paid-bank",
                player=player.name,
                amount=self._money(amount),
                reason=reason,
            )
            return True
        self._set_debt(player, amount, None, reason, feeds_pot=feeds_pot)
        return False

    def _pay_player(
        self, debtor: MonopolyPlayer, creditor: MonopolyPlayer, amount: int, reason: str
    ) -> bool:
        if amount <= 0 or debtor.id == creditor.id:
            return True
        if debtor.cash >= amount:
            debtor.cash -= amount
            creditor.cash += amount
            self.broadcast_l(
                "monopoly-paid-player",
                player=debtor.name,
                target=creditor.name,
                amount=self._money(amount),
                reason=reason,
            )
            return True
        self._set_debt(debtor, amount, creditor, reason)
        return False

    def _set_debt(
        self,
        debtor: MonopolyPlayer,
        amount: int,
        creditor: MonopolyPlayer | None,
        reason: str,
        *,
        feeds_pot: bool = False,
    ) -> None:
        self.pending_debt = MonopolyDebt(
            debtor_id=debtor.id,
            creditor_id=creditor.id if creditor else "",
            amount=amount,
            reason=reason,
            feeds_pot=feeds_pot and creditor is None,
        )
        self.phase = "await_debt"
        target = creditor.name if creditor else "the bank"
        self.broadcast_l(
            "monopoly-debt-created",
            player=debtor.name,
            amount=self._money(amount),
            target=target,
            reason=reason,
        )

    def _move_steps(self, player: MonopolyPlayer, steps: int) -> None:
        self._move_to(player, player.position + steps, collect_go=True)

    def _move_to(self, player: MonopolyPlayer, target_position: int, *, collect_go: bool) -> None:
        old_position = player.position
        board_size = len(self.board.spaces)
        wrapped_target = target_position % board_size
        if collect_go and target_position >= board_size and old_position != wrapped_target:
            self._credit(player, self.board.pass_go_cash, "passing GO")
            self.broadcast_l(
                "monopoly-pass-go",
                player=player.name,
                amount=self._money(self.board.pass_go_cash),
            )
        elif collect_go and wrapped_target < old_position and target_position != old_position:
            self._credit(player, self.board.pass_go_cash, "passing GO")
            self.broadcast_l(
                "monopoly-pass-go",
                player=player.name,
                amount=self._money(self.board.pass_go_cash),
            )
        player.position = wrapped_target
        self.broadcast_l("monopoly-moved-to", player=player.name, space=self._space_at(player.position).name)

    def _move_to_nearest(self, player: MonopolyPlayer, kind: str) -> None:
        board_size = len(self.board.spaces)
        for distance in range(1, board_size + 1):
            target = (player.position + distance) % board_size
            if self._space_at(target).kind == kind:
                self._move_to(player, player.position + distance, collect_go=True)
                return

    def _send_to_jail(self, player: MonopolyPlayer) -> None:
        player.position = JAIL_POSITION
        player.in_jail = True
        player.jail_turns = 0
        self.broadcast_l("monopoly-go-to-jail", player=player.name)

    def _calculate_rent(
        self,
        space: MonopolySpace,
        *,
        roll_total: int,
        railroad_multiplier: int = 1,
        utility_multiplier: int | None = None,
    ) -> int:
        state = self.property_states[space.space_id]
        owner_id = state.owner_id
        if space.kind == "street":
            rent = space.rents[state.houses]
            if state.houses == 0 and self._owns_complete_group(owner_id, space.color_group):
                rent *= 2
            return rent
        if space.kind == "railroad":
            owned_count = len(
                [
                    owned_space
                    for owned_space in self._owned_spaces_by_id(owner_id)
                    if owned_space.kind == "railroad"
                ]
            )
            index = max(0, min(owned_count, len(space.rents)) - 1)
            return space.rents[index] * railroad_multiplier
        if space.kind == "utility":
            multiplier = utility_multiplier
            if multiplier is None:
                owned_count = len(
                    [
                        owned_space
                        for owned_space in self._owned_spaces_by_id(owner_id)
                        if owned_space.kind == "utility"
                    ]
                )
                multiplier = 10 if owned_count >= 2 else 4
            return roll_total * multiplier
        return 0

    def _owns_complete_group(self, owner_id: str, color_group: str) -> bool:
        if not owner_id or not color_group:
            return False
        group_ids = self.board.color_group_space_ids.get(color_group, ())
        return all(self.property_states[space_id].owner_id == owner_id for space_id in group_ids)

    def _owns_group_candidate(self, player: MonopolyPlayer, space: MonopolySpace) -> bool:
        if not space.color_group:
            return False
        group_ids = self.board.color_group_space_ids.get(space.color_group, ())
        return all(
            space_id == space.space_id or self.property_states[space_id].owner_id == player.id
            for space_id in group_ids
        )

    def _owned_spaces(self, player: MonopolyPlayer) -> list[MonopolySpace]:
        return self._owned_spaces_by_id(player.id)

    def _owned_spaces_by_id(self, owner_id: str) -> list[MonopolySpace]:
        return [
            self._space(space_id)
            for space_id, state in self.property_states.items()
            if state.owner_id == owner_id
        ]

    def _building_count(
        self, player: MonopolyPlayer, *, houses: bool = False, hotels: bool = False
    ) -> int:
        count = 0
        for space in self._owned_spaces(player):
            level = self.property_states[space.space_id].houses
            if houses and 0 < level < HOTEL_LEVEL:
                count += level
            if hotels and level == HOTEL_LEVEL:
                count += 1
        return count

    def _can_mortgage(self, space: MonopolySpace) -> bool:
        if space.kind != "street":
            return True
        group_ids = self.board.color_group_space_ids.get(space.color_group, ())
        return all(self.property_states[space_id].houses == 0 for space_id in group_ids)

    def _unmortgage_cost(self, space: MonopolySpace) -> int:
        return space.mortgage_value + max(1, space.mortgage_value // 10)

    def _can_build_on(self, player: MonopolyPlayer, space: MonopolySpace) -> bool:
        if space.kind != "street" or space.house_cost <= 0 or player.cash < space.house_cost:
            return False
        state = self.property_states[space.space_id]
        if state.owner_id != player.id or state.mortgaged or state.houses >= HOTEL_LEVEL:
            return False
        group_ids = self.board.color_group_space_ids.get(space.color_group, ())
        if not group_ids or not all(self.property_states[space_id].owner_id == player.id for space_id in group_ids):
            return False
        if any(self.property_states[space_id].mortgaged for space_id in group_ids):
            return False
        levels = [self.property_states[space_id].houses for space_id in group_ids]
        if state.houses > min(levels):
            return False
        if state.houses == 4:
            return self.bank_hotels > 0
        return self.bank_houses > 0

    def _can_sell_from(self, space: MonopolySpace) -> bool:
        if space.kind != "street":
            return False
        state = self.property_states[space.space_id]
        group_ids = self.board.color_group_space_ids.get(space.color_group, ())
        levels = [self.property_states[space_id].houses for space_id in group_ids]
        if state.houses < max(levels):
            return False
        if state.houses == HOTEL_LEVEL:
            return self.bank_houses >= 4
        return True

    def _can_trade_property(self, space: MonopolySpace) -> bool:
        state = self.property_states[space.space_id]
        if state.houses > 0:
            return False
        if space.kind != "street":
            return True
        group_ids = self.board.color_group_space_ids.get(space.color_group, ())
        return all(self.property_states[space_id].houses == 0 for space_id in group_ids)

    def _trade_summary(self, offer: MonopolyTradeOffer) -> str:
        proposer = self._player_by_id(offer.proposer_id)
        target = self._player_by_id(offer.target_id)
        give = self._trade_side_label(
            cash=offer.give_cash,
            property_ids=offer.give_property_ids,
            jail_card=offer.give_jail_card,
        )
        receive = self._trade_side_label(
            cash=offer.receive_cash,
            property_ids=offer.receive_property_ids,
            jail_card=offer.receive_jail_card,
        )
        target_name = target.name if target else "Unknown"
        proposer_name = proposer.name if proposer else "Unknown"
        return f"{proposer_name} gives {give} to {target_name} for {receive}"

    def _trade_side_label(
        self, *, cash: int, property_ids: list[str], jail_card: bool
    ) -> str:
        parts: list[str] = []
        if cash:
            parts.append(self._money(cash))
        for property_id in property_ids:
            parts.append(self._space(property_id).name)
        if jail_card:
            parts.append("Get Out of Jail Free card")
        return " and ".join(parts) if parts else "nothing"

    def _property_detail_line(self, property_id: str) -> str:
        """A one-line summary of a property for the trade review screen."""
        space = self._space(property_id)
        state = self.property_states[property_id]
        bits = [space.name]
        if space.color_group:
            bits.append(space.color_group.replace("_", " "))
        if space.rents:
            bits.append(f"rent {self._money(min(space.rents))}-{self._money(max(space.rents))}")
        bits.append(f"mortgage {self._money(space.mortgage_value)}")
        if state.mortgaged:
            bits.append("currently mortgaged")
        if state.houses:
            bits.append(self._building_label(state.houses))
        return ", ".join(bits) + "."

    def _parse_trade_amount(self, amount_text: str) -> int | None:
        cleaned = amount_text.strip().replace("$", "").replace(",", "")
        if not cleaned:
            return None
        try:
            return int(cleaned)
        except ValueError:
            return None

    def _validate_trade_offer(self, offer: MonopolyTradeOffer) -> str | None:
        if not self._is_playing():
            return "action-not-playing"
        proposer = self._player_by_id(offer.proposer_id)
        target = self._player_by_id(offer.target_id)
        if not proposer or not target or proposer.id == target.id:
            return "action-not-available"
        if proposer.bankrupt or target.bankrupt or proposer.is_spectator or target.is_spectator:
            return "monopoly-player-bankrupt-disabled"
        if self.auction:
            return "monopoly-auction-active"
        if self.pending_purchase_property_id:
            return "monopoly-resolve-property-first"
        if self.pending_debt and self.pending_debt.debtor_id not in {proposer.id, target.id}:
            return "monopoly-debt-pending"
        if offer.give_cash < 0 or offer.receive_cash < 0:
            return "monopoly-trade-no-longer-valid"
        if not any(
            [
                offer.give_cash,
                offer.receive_cash,
                offer.give_property_ids,
                offer.receive_property_ids,
                offer.give_jail_card,
                offer.receive_jail_card,
            ]
        ):
            return "monopoly-trade-no-longer-valid"

        for property_id in offer.give_property_ids:
            if property_id not in self.property_states:
                return "monopoly-trade-no-longer-valid"
            space = self._space(property_id)
            state = self.property_states[property_id]
            if state.owner_id != proposer.id or not self._can_trade_property(space):
                return "monopoly-trade-no-longer-valid"
        for property_id in offer.receive_property_ids:
            if property_id not in self.property_states:
                return "monopoly-trade-no-longer-valid"
            space = self._space(property_id)
            state = self.property_states[property_id]
            if state.owner_id != target.id or not self._can_trade_property(space):
                return "monopoly-trade-no-longer-valid"
        if offer.give_jail_card and not proposer.jail_free_cards:
            return "monopoly-no-jail-card"
        if offer.receive_jail_card and not target.jail_free_cards:
            return "monopoly-no-jail-card"

        proposer_cash_after = proposer.cash - offer.give_cash + offer.receive_cash
        target_cash_after = target.cash - offer.receive_cash + offer.give_cash
        if proposer_cash_after < 0 or target_cash_after < 0:
            return "monopoly-not-enough-cash"
        proposer_interest = sum(
            self._trade_mortgage_interest(property_id)
            for property_id in offer.receive_property_ids
        )
        target_interest = sum(
            self._trade_mortgage_interest(property_id)
            for property_id in offer.give_property_ids
        )
        if proposer_cash_after < proposer_interest or target_cash_after < target_interest:
            return "monopoly-not-enough-cash"
        return None

    def _trade_mortgage_interest(self, property_id: str) -> int:
        if not property_id:
            return 0
        state = self.property_states[property_id]
        if not state.mortgaged:
            return 0
        return max(1, self._space(property_id).mortgage_value // 10)

    def _charge_trade_mortgage_interest(
        self, player: MonopolyPlayer, property_id: str
    ) -> None:
        interest = self._trade_mortgage_interest(property_id)
        if interest <= 0:
            return
        player.cash -= interest
        self.broadcast_l(
            "monopoly-mortgage-transfer-interest-paid",
            player=player.name,
            amount=self._money(interest),
        )

    def _announce_payable_pending_debt(self, player: MonopolyPlayer) -> None:
        if self.pending_debt and self.pending_debt.debtor_id == player.id and player.cash >= self.pending_debt.amount:
            self.broadcast_l("monopoly-debt-can-pay", player=player.name)

    def _building_label(self, houses: int) -> str:
        if houses == 0:
            return "no buildings"
        if houses == HOTEL_LEVEL:
            return "hotel"
        return f"{houses} house" if houses == 1 else f"{houses} houses"

    def _encode_property_option(self, space: MonopolySpace, amount: int) -> str:
        return f"{space.space_id}|{space.name} ({self._money(amount)})"

    def _decode_property_option(self, option: str) -> str:
        return option.split("|", 1)[0]

    def _auction_players(self) -> list[MonopolyPlayer]:
        return [player for player in self._solvent_players() if not player.is_spectator]

    def _minimum_auction_bid(self) -> int:
        if not self.auction or self.auction.highest_bid <= 0:
            return MIN_AUCTION_INCREMENT
        return self.auction.highest_bid + MIN_AUCTION_INCREMENT

    def _announce_completed_set(self, player: MonopolyPlayer, space: MonopolySpace) -> None:
        if space.kind == "street" and self._owns_complete_group(player.id, space.color_group):
            self.broadcast_l(
                "monopoly-completed-set",
                player=player.name,
                group=space.color_group.replace("_", " "),
            )
        elif space.kind in {"railroad", "utility"}:
            owned_count = len([owned for owned in self._owned_spaces(player) if owned.kind == space.kind])
            target = 4 if space.kind == "railroad" else 2
            if owned_count == target:
                self.broadcast_l("monopoly-completed-set", player=player.name, group=f"{space.kind}s")

    def _bankrupt_player(
        self, player: MonopolyPlayer, creditor: MonopolyPlayer | None
    ) -> None:
        self._liquidate_all_buildings(player)
        if creditor:
            creditor.cash += player.cash
            for space in self._owned_spaces(player):
                self.property_states[space.space_id].owner_id = creditor.id
            creditor.jail_free_cards.extend(player.jail_free_cards)
        else:
            for space in self._owned_spaces(player):
                self.property_states[space.space_id] = MonopolyPropertyState()

        player.cash = 0
        player.jail_free_cards.clear()
        player.bankrupt = True
        player.in_jail = False
        self.pending_debt = None
        self.pending_purchase_property_id = ""
        if self.pending_trade and player.id in {
            self.pending_trade.proposer_id,
            self.pending_trade.target_id,
        }:
            self.pending_trade = None
        if self.auction and player.id in {p.id for p in self._auction_players()}:
            self.auction.passed_player_ids.append(player.id)
        self.turn_player_ids = [player_id for player_id in self.turn_player_ids if player_id != player.id]
        creditor_name = creditor.name if creditor else "the bank"
        self.broadcast_l("monopoly-player-bankrupt", player=player.name, creditor=creditor_name)
        self._check_for_winner()

    def _liquidate_all_buildings(self, player: MonopolyPlayer) -> None:
        for space in self._owned_spaces(player):
            state = self.property_states[space.space_id]
            if state.houses == 0:
                continue
            if state.houses == HOTEL_LEVEL:
                self.bank_hotels += 1
                player.cash += (space.house_cost // 2) * 5
            else:
                self.bank_houses += state.houses
                player.cash += (space.house_cost // 2) * state.houses
            state.houses = 0

    def _check_for_winner(self) -> None:
        solvent = self._solvent_players()
        if len(solvent) == 1:
            winner = solvent[0]
            self.winner_id = winner.id
            self.broadcast_l(
                "monopoly-winner",
                player=winner.name,
                value=self._money(self._net_worth(winner)),
            )
            self.finish_game()

    def _net_worth(self, player: MonopolyPlayer) -> int:
        total = player.cash
        for space in self._owned_spaces(player):
            state = self.property_states[space.space_id]
            total += space.mortgage_value if state.mortgaged else space.price
            if space.kind == "street":
                if state.houses == HOTEL_LEVEL:
                    total += space.house_cost * 5
                else:
                    total += space.house_cost * state.houses
        return total

    # ------------------------------------------------------------------
    # Status actions, bots, and results
    # ------------------------------------------------------------------

    def _action_check_assets(self, player: MonopolyPlayer, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [
            f"{player.name}: {self._money(player.cash)} cash, "
            f"net worth {self._money(self._net_worth(player))}, "
            f"at {self._space_at(player.position).name}."
        ]
        if player.in_jail:
            lines.append(f"In jail, attempt {player.jail_turns + 1} of 3.")
        if player.jail_free_cards:
            lines.append(f"Get Out of Jail Free cards: {len(player.jail_free_cards)}.")
        owned = self._owned_spaces(player)
        if owned:
            for space in owned:
                state = self.property_states[space.space_id]
                markers = []
                if state.mortgaged:
                    markers.append("mortgaged")
                if state.houses:
                    markers.append(self._building_label(state.houses))
                suffix = f" ({', '.join(markers)})" if markers else ""
                lines.append(f"{space.name}{suffix}.")
        else:
            lines.append("No properties owned.")
        self.status_box(player, lines)

    def _action_check_board(self, player: MonopolyPlayer, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        unowned = [space for space in self.board.purchasable_spaces if not self.property_states[space.space_id].owner_id]
        lines = [
            f"Bank supply: {self.bank_houses} houses, {self.bank_hotels} hotels.",
            f"Unowned properties: {len(unowned)}.",
        ]
        if self.options.free_parking_jackpot:
            lines.append(f"Free Parking pot: {self._money(self.free_parking_pot)}.")
        for other in self._solvent_players():
            lines.append(
                f"{other.name}: {self._space_at(other.position).name}, "
                f"{self._money(other.cash)} cash, net worth {self._money(self._net_worth(other))}."
            )
        if self.pending_debt:
            debtor = self._player_by_id(self.pending_debt.debtor_id)
            target = self._player_by_id(self.pending_debt.creditor_id)
            lines.append(
                f"Pending debt: {debtor.name if debtor else 'Unknown'} owes "
                f"{self._money(self.pending_debt.amount)} to "
                f"{target.name if target else 'the bank'}."
            )
        if self.auction:
            space = self._space(self.auction.property_id)
            bidder = self._player_by_id(self.auction.highest_bidder_id)
            high = self._money(self.auction.highest_bid) if self.auction.highest_bid else "no bid"
            lines.append(f"Auction: {space.name}, high bid {high} by {bidder.name if bidder else 'nobody'}.")
        if self.pending_trade:
            lines.append(f"Pending trade: {self.pending_trade.summary}.")
        self.status_box(player, lines)

    def on_tick(self) -> None:
        super().on_tick()
        if self.status != GameStatus.PLAYING or not self.game_active:
            return
        if self.pending_trade:
            self._process_trade_bot()
        if self.auction:
            self._process_auction_bots()
        else:
            BotHelper.on_tick(self)

    def _process_trade_bot(self) -> None:
        if not self.pending_trade:
            return
        target = self._player_by_id(self.pending_trade.target_id)
        if not target or not target.is_bot:
            return
        BotHelper.process_bot_action(
            bot=target,
            think_fn=lambda target=target: self.bot_think(target),
            execute_fn=lambda action_id, target=target: self.execute_action(target, action_id),
        )

    def _process_auction_bots(self) -> None:
        for bot in self._auction_players():
            if not bot.is_bot or bot.id in (self.auction.passed_player_ids if self.auction else []):
                continue
            BotHelper.process_bot_action(
                bot=bot,
                think_fn=lambda bot=bot: self.bot_think(bot),
                execute_fn=lambda action_id, bot=bot: self.execute_action(bot, action_id),
            )

    def bot_think(self, player: MonopolyPlayer) -> str | None:
        if player.bankrupt:
            return None
        if self.pending_trade and self.pending_trade.target_id == player.id:
            if self._validate_trade_offer(self.pending_trade):
                return "decline_trade"
            return "accept_trade" if self._bot_should_accept_trade(player, self.pending_trade) else "decline_trade"
        if self.auction:
            if player.id == self.auction.highest_bidder_id:
                return None
            return "auction_bid" if self._bot_input_auction_bid(player) else "auction_pass"
        if self.pending_debt and self.pending_debt.debtor_id == player.id:
            if player.cash >= self.pending_debt.amount:
                return "pay_debt"
            if self._sell_building_options(player):
                return "sell_house"
            if self._mortgage_property_options(player):
                return "mortgage_property"
            return "declare_bankruptcy"
        if self.current_player != player:
            return None
        if self.phase == "await_roll":
            if player.in_jail:
                if player.jail_free_cards:
                    return "use_jail_card"
                if player.cash > 350:
                    return "pay_bail"
            return "roll"
        if self.phase == "await_purchase":
            if not self.pending_purchase_property_id:
                return None
            space = self._space(self.pending_purchase_property_id)
            if player.cash - space.price >= 200 or self._owns_group_candidate(player, space):
                return "buy_property"
            return "auction_property"
        if self.phase == "post_roll":
            if player.cash > 500 and self._build_property_options(player):
                return "build_house"
            return "end_turn"
        return None

    def _bot_should_accept_trade(
        self, target: MonopolyPlayer, offer: MonopolyTradeOffer
    ) -> bool:
        incoming = self._trade_side_value(
            owner=target,
            cash=offer.give_cash,
            property_ids=offer.give_property_ids,
            jail_card=offer.give_jail_card,
        )
        outgoing = self._trade_side_value(
            owner=target,
            cash=offer.receive_cash,
            property_ids=offer.receive_property_ids,
            jail_card=offer.receive_jail_card,
        )
        return incoming >= outgoing

    def _trade_side_value(
        self,
        *,
        owner: MonopolyPlayer,
        cash: int,
        property_ids: list[str],
        jail_card: bool,
    ) -> int:
        value = cash
        for property_id in property_ids:
            space = self._space(property_id)
            state = self.property_states[property_id]
            value += space.mortgage_value if state.mortgaged else space.price
            if self._owns_group_candidate(owner, space):
                value += 100
        if jail_card:
            value += JAIL_CARD_TRADE_VALUE
        return value

    def build_game_result(self) -> GameResult:
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda player: (
                not self._active_player(player).bankrupt,
                self._net_worth(self._active_player(player)),
            ),
            reverse=True,
        )
        winner = self._player_by_id(self.winner_id) if self.winner_id else None
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(player_id=p.id, player_name=p.name, is_bot=p.is_bot)
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "net_worth": {p.name: self._net_worth(self._active_player(p)) for p in self.players},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        net_worth = result.custom_data.get("net_worth", {})
        for index, player_result in enumerate(result.player_results, 1):
            amount = net_worth.get(player_result.player_name, 0)
            lines.append(f"{index}. {player_result.player_name}: {self._money(amount)}")
        return lines
