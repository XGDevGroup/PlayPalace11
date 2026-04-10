from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, EditboxInput
from ...game_utils.poker_keybinds import setup_poker_keybinds
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, option_field
from ...game_utils.cards import Card, Deck, DeckFactory, read_cards, sort_cards, card_name
from ...game_utils.poker_betting import PokerBettingRound
from ...game_utils.poker_pot import PokerPotManager
from ...game_utils.poker_table import PokerTableState
from ...game_utils.poker_timer import PokerTurnTimer
from ...game_utils.poker_evaluator import best_hand, describe_hand, describe_partial_hand
from ...game_utils.poker_actions import compute_pot_limit_caps, clamp_total_to_cap
from ...game_utils.poker_showdown import order_winners_by_button, format_showdown_lines
from ...game_utils.poker_payout import resolve_pots_with_payouts
from ...game_utils import poker_log
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from .bot import bot_think
from ...game_utils.poker_state import order_after_button


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

BLIND_TIMER_CHOICES = ["5", "10", "15", "20", "30"]
BLIND_TIMER_LABELS = {
    "5": "poker-blind-timer-5",
    "10": "poker-blind-timer-10",
    "15": "poker-blind-timer-15",
    "20": "poker-blind-timer-20",
    "30": "poker-blind-timer-30",
}

RAISE_MODES = ["no_limit", "pot_limit", "double_pot"]
RAISE_MODE_LABELS = {
    "no_limit": "poker-raise-no-limit",
    "pot_limit": "poker-raise-pot-limit",
    "double_pot": "poker-raise-double-pot",
}


@dataclass
class HoldemPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    chips: int = 0
    folded: bool = False
    all_in: bool = False


@dataclass
class HoldemOptions(GameOptions):
    starting_chips: int = option_field(
        IntOption(
            default=20000,
            min_val=100,
            max_val=1000000,
            value_key="count",
            label="holdem-set-starting-chips",
            prompt="holdem-enter-starting-chips",
            change_msg="holdem-option-changed-starting-chips",
        )
    )
    big_blind: int = option_field(
        IntOption(
            default=200,
            min_val=1,
            max_val=1000000,
            value_key="count",
            label="holdem-set-big-blind",
            prompt="holdem-enter-big-blind",
            change_msg="holdem-option-changed-big-blind",
        )
    )
    ante: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=1000000,
            value_key="count",
            label="holdem-set-ante",
            prompt="holdem-enter-ante",
            change_msg="holdem-option-changed-ante",
        )
    )
    ante_start_level: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=20,
            value_key="count",
            label="holdem-set-ante-start",
            prompt="holdem-enter-ante-start",
            change_msg="holdem-option-changed-ante-start",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            label="holdem-set-turn-timer",
            prompt="holdem-select-turn-timer",
            change_msg="holdem-option-changed-turn-timer",
        )
    )
    blind_timer: str = option_field(
        MenuOption(
            choices=BLIND_TIMER_CHOICES,
            choice_labels=BLIND_TIMER_LABELS,
            default="20",
            label="holdem-set-blind-timer",
            prompt="holdem-select-blind-timer",
            change_msg="holdem-option-changed-blind-timer",
        )
    )
    raise_mode: str = option_field(
        MenuOption(
            choices=RAISE_MODES,
            choice_labels=RAISE_MODE_LABELS,
            default="no_limit",
            label="holdem-set-raise-mode",
            prompt="holdem-select-raise-mode",
            change_msg="holdem-option-changed-raise-mode",
        )
    )
    max_raises: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=10,
            value_key="count",
            label="holdem-set-max-raises",
            prompt="holdem-enter-max-raises",
            change_msg="holdem-option-changed-max-raises",
        )
    )


@dataclass
@register_game
class HoldemGame(Game):
    players: list[HoldemPlayer] = field(default_factory=list)
    options: HoldemOptions = field(default_factory=HoldemOptions)
    deck: Deck | None = None
    community: list[Card] = field(default_factory=list)
    pot_manager: PokerPotManager = field(default_factory=PokerPotManager)
    betting: PokerBettingRound | None = None
    table_state: PokerTableState = field(default_factory=PokerTableState)
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    hand_number: int = 0
    phase: str = "lobby"
    action_log: list[tuple[str, dict]] = field(default_factory=list)
    blind_level: int = 0
    blind_timer_ticks: int = 0
    blinds_raise_next_hand: bool = False
    current_small_blind: int = 0
    current_big_blind: int = 0
    last_sb_pay: int = 0
    last_bb_pay: int = 0
    pending_showdown: bool = False
    pending_board_reveals: list[tuple[str, int]] = field(default_factory=list)
    pending_board_delay_ticks: int = 0
    pending_board_wait_ticks: int = 0
    last_showdown_winner_ids: set[str] = field(default_factory=set)

    @classmethod
    def get_name(cls) -> str:
        return "Texas Hold'em"

    @classmethod
    def get_type(cls) -> str:
        return "holdem"

    @classmethod
    def get_category(cls) -> str:
        return "category-poker"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 12

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> HoldemPlayer:
        return HoldemPlayer(id=player_id, name=name, is_bot=is_bot, chips=0)

    # ==========================================================================
    # Actions / keybinds
    # ==========================================================================
    def create_turn_action_set(self, player: HoldemPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="call",
                label=Localization.get(locale, "poker-call"),
                handler="_action_call",
                get_label="_get_call_label",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="fold",
                label=Localization.get(locale, "poker-fold"),
                handler="_action_fold",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="raise",
                label=Localization.get(locale, "poker-raise"),
                handler="_action_raise",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
                input_request=EditboxInput(
                    prompt="poker-enter-raise",
                    default="",
                    bot_input="_bot_input_raise",
                ),
            )
        )
        action_set.add(
            Action(
                id="all_in",
                label=Localization.get(locale, "poker-all-in"),
                handler="_action_all_in",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        local_actions = [
            Action(
                id="check_pot",
                label=Localization.get(locale, "poker-check-pot"),
                handler="_action_check_pot",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_bet",
                label=Localization.get(locale, "poker-check-bet"),
                handler="_action_check_bet",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_min_raise",
                label=Localization.get(locale, "poker-check-min-raise"),
                handler="_action_check_min_raise",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_hand_players",
                label=Localization.get(locale, "poker-check-hand-players"),
                handler="_action_check_hand_players",
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
            Action(
                id="speak_hand",
                label=Localization.get(locale, "poker-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="speak_table",
                label=Localization.get(locale, "poker-read-table"),
                handler="_action_read_table",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="speak_hand_value",
                label=Localization.get(locale, "poker-hand-value"),
                handler="_action_read_hand_value",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_button",
                label=Localization.get(locale, "poker-check-button"),
                handler="_action_check_button",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_position",
                label=Localization.get(locale, "poker-check-position"),
                handler="_action_check_position",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_blind_timer",
                label=Localization.get(locale, "poker-check-blind-timer"),
                handler="_action_check_blind_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
        ]
        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)
        for i in range(1, 8):
            action_set.add(
                Action(
                    id=f"speak_card_{i}",
                    label=Localization.get(locale, "poker-read-card", index=i),
                    handler="_action_read_card",
                    is_enabled="_is_check_enabled",
                    is_hidden="_is_always_hidden",
                )
            )
        action_set.add(
            Action(
                id="reveal_both",
                label=Localization.get(locale, "poker-reveal-both"),
                handler="_action_reveal_both",
                is_enabled="_is_reveal_enabled",
                is_hidden="_is_reveal_hidden",
            )
        )
        action_set.add(
            Action(
                id="reveal_first",
                label=Localization.get(locale, "poker-reveal-first"),
                handler="_action_reveal_first",
                is_enabled="_is_reveal_enabled",
                is_hidden="_is_reveal_hidden",
            )
        )
        action_set.add(
            Action(
                id="reveal_second",
                label=Localization.get(locale, "poker-reveal-second"),
                handler="_action_reveal_second",
                is_enabled="_is_reveal_enabled",
                is_hidden="_is_reveal_hidden",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        setup_poker_keybinds(
            self,
            check_dealer="check_button",
            dealer_label="Button",
            check_position="check_position",
            check_bet="check_bet",
            check_min_raise="check_min_raise",
            check_hand_players="check_hand_players",
            check_turn_timer="check_turn_timer",
            read_table="speak_table",
            check_blind_timer="check_blind_timer",
            reveal_both="reveal_both",
            reveal_first="reveal_first",
            reveal_second="reveal_second",
            read_cards_count=7,
        )

    # ==========================================================================
    # Game flow
    # ==========================================================================
    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        for player in self.players:
            player.chips = self.options.starting_chips
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.players])
        self._sync_team_scores()
        self.set_turn_players(self.get_active_players())
        self.play_music("game_3cardpoker/mus.ogg")
        self._reset_blind_timer()
        self._start_new_hand()

    def _reset_blind_timer(self) -> None:
        try:
            minutes = int(self.options.blind_timer)
        except ValueError:
            minutes = 0
        if minutes <= 0:
            self.blind_timer_ticks = 0
            return
        self.blind_timer_ticks = minutes * 60 * 20

    def _tick_blind_timer(self) -> None:
        if self.blind_timer_ticks <= 0:
            return
        self.blind_timer_ticks -= 1
        if self.blind_timer_ticks == 0:
            self.blinds_raise_next_hand = True
            self.broadcast_l("poker-blinds-raise-next-hand")

    def _advance_blind_level(self) -> None:
        if not self.blinds_raise_next_hand:
            return
        self.blind_level += 1
        self.blinds_raise_next_hand = False
        self._reset_blind_timer()

    def _current_blinds(self) -> tuple[int, int]:
        base_small = max(1, self.options.big_blind // 2)
        base_big = self.options.big_blind
        level = self.blind_level
        if level <= 0:
            return (base_small, base_big)
        multipliers = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 100]
        mult = multipliers[min(level, len(multipliers) - 1)]
        return (base_small * mult, base_big * mult)

    def _start_new_hand(self) -> None:
        self.hand_number += 1
        self.phase = "preflop"
        self.action_log = []
        self.pot_manager.reset()
        self.community = []
        self.pending_showdown = False
        self.pending_board_reveals = []
        self.pending_board_delay_ticks = 0
        self.pending_board_wait_ticks = 0
        self.deck, _ = DeckFactory.standard_deck()
        self.deck.shuffle()

        active = [p for p in self.get_active_players() if p.chips > 0]
        if len(active) <= 1:
            self._end_game(active[0] if active else None)
            return

        self.table_state.advance_button([p.id for p in active])
        for p in active:
            p.hand = []
            p.folded = False
            p.all_in = False

        self.play_sound("game_cards/small_shuffle.ogg")
        self._post_antes(active)
        self._post_blinds(active)
        self._deal_hole_cards(active)
        self._start_betting_round(preflop=True)

    def _queue_new_hand(self) -> None:
        self._next_hand_wait_ticks = 100

    def _post_antes(self, active: list[HoldemPlayer]) -> None:
        ante = self._current_ante()
        if ante <= 0:
            return
        self.play_sound("game_3cardpoker/bet.ogg")
        for p in active:
            pay = min(p.chips, ante)
            p.chips -= pay
            if p.chips == 0:
                p.all_in = True
            self.pot_manager.add_contribution(p.id, pay)
        self._sync_team_scores()
        self.broadcast_l("holdem-antes-posted", amount=ante)

    def _current_ante(self) -> int:
        if self.options.ante <= 0:
            return 0
        if self.options.ante_start_level <= 0:
            return self.options.ante
        return self.options.ante if self.blind_level >= self.options.ante_start_level else 0

    def _post_blinds(self, active: list[HoldemPlayer]) -> None:
        small, big = self._current_blinds()
        self.current_small_blind = small
        self.current_big_blind = big
        sb_idx, bb_idx = self.table_state.get_blind_indices([p.id for p in active])
        sb_player = active[sb_idx]
        bb_player = active[bb_idx]
        sb_pay = min(sb_player.chips, small)
        bb_pay = min(bb_player.chips, big)
        self.last_sb_pay = sb_pay
        self.last_bb_pay = bb_pay
        sb_player.chips -= sb_pay
        bb_player.chips -= bb_pay
        self.play_sound("game_3cardpoker/bet.ogg")
        if sb_player.chips == 0:
            sb_player.all_in = True
        if bb_player.chips == 0:
            bb_player.all_in = True
        self.pot_manager.add_contribution(sb_player.id, sb_pay)
        self.pot_manager.add_contribution(bb_player.id, bb_pay)
        self._sync_team_scores()
        self.broadcast_l("holdem-blinds-posted", sb=sb_pay, bb=bb_pay)

    def _deal_hole_cards(self, players: list[HoldemPlayer]) -> None:
        if not players:
            return
        if len(players) == 2:
            start_index = self.table_state.button_index % len(players)
        else:
            start_index = (self.table_state.button_index + 1) % len(players)
        order = players[start_index:] + players[:start_index]
        delay_ticks = 4
        for _ in range(2):
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks, volume=100)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks + 1, volume=100)
            for p in order:
                card = self.deck.draw_one() if self.deck else None
                if card:
                    p.hand.append(card)
            delay_ticks += 6
        for p in players:
            p.hand = sort_cards(p.hand)
            user = self.get_user(p)
            if user:
                user.speak_l("poker-dealt-cards", cards=read_cards(p.hand, user.locale))

    def _announce_board(self, stage: str) -> None:
        if stage == "flop":
            self.broadcast_l("poker-flop", cards=read_cards(self.community, "en"))
        elif stage == "turn":
            self.broadcast_l("poker-turn", card=card_name(self.community[-1], "en"))
        elif stage == "river":
            self.broadcast_l("poker-river", card=card_name(self.community[-1], "en"))

    def _deal_community(self, count: int) -> None:
        # Burn card (cosmetic)
        if self.deck and not self.deck.is_empty():
            self.deck.draw_one()
        for idx in range(count):
            card = self.deck.draw_one() if self.deck else None
            if card:
                self.community.append(card)
            if idx == 0:
                self.play_sound("game_cards/draw3.ogg", volume=100)
                self.schedule_sound("game_cards/draw3.ogg", delay_ticks=1, volume=100)
            else:
                self.schedule_sound("game_cards/draw3.ogg", delay_ticks=idx * 6, volume=100)
                self.schedule_sound("game_cards/draw3.ogg", delay_ticks=idx * 6 + 1, volume=100)

    def _start_all_in_showdown(self, delay_between_rounds: int = 0) -> None:
        if self.pending_showdown:
            return
        needed = 5 - len(self.community)
        if needed <= 0:
            self._showdown()
            return
        self.pending_showdown = True
        self.pending_board_delay_ticks = max(0, delay_between_rounds)
        self.pending_board_wait_ticks = 0
        reveal_counts: list[tuple[str, int]] = []
        if len(self.community) == 0:
            reveal_counts.append(("flop", 3))
            needed -= 3
        while needed > 0:
            stage = "turn" if len(reveal_counts) == 1 else "river"
            reveal_counts.append((stage, 1))
            needed -= 1
        self.pending_board_reveals = reveal_counts

    def _start_betting_round(self, preflop: bool) -> None:
        active_ids = [p.id for p in self.get_active_players() if p.chips > 0 and not p.folded]
        order = [p.id for p in self.get_active_players() if p.id in active_ids]
        self.betting = PokerBettingRound(order=order, max_raises=self.options.max_raises or None)
        if not order:
            self._start_all_in_showdown(delay_between_rounds=100)
            return
        if preflop:
            # Initialize with posted blinds
            sb_idx, bb_idx = self.table_state.get_blind_indices(order)
            sb_id = order[sb_idx] if order else None
            bb_id = order[bb_idx] if order else None
            initial = {}
            if sb_id:
                initial[sb_id] = self.last_sb_pay
            if bb_id:
                initial[bb_id] = self.last_bb_pay
            self.betting.reset(
                current_bet=self.last_bb_pay,
                last_raise_size=self.current_big_blind,
                initial_bets=initial,
            )
        else:
            self.betting.reset(last_raise_size=self.current_big_blind)
        # Preflop action starts left of big blind; heads-up special
        if preflop and len(order) == 2:
            start_index = self.table_state.get_blind_indices(order)[0]
        elif preflop:
            start_index = (self.table_state.get_blind_indices(order)[1] + 1) % len(order)
        else:
            start_index = (self.table_state.button_index + 1) % len(order)
        self._set_turn_by_index(start_index, order)
        # Betting round announcements removed (cards are announced instead)

    def _set_turn_by_index(self, start_index: int, order: list[str]) -> None:
        if not order:
            return
        idx = start_index % len(order)
        self.turn_player_ids = order
        self.turn_index = idx
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        if not player:
            return
        p = player if isinstance(player, HoldemPlayer) else None
        if not p or p.folded or p.all_in:
            self._advance_turn()
            return
        self.announce_turn(turn_sound="game_3cardpoker/turn.ogg")
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(30, 50))  # nosec B311
        self._start_turn_timer()
        self.rebuild_all_menus()

    def _advance_turn(self) -> None:
        if not self.betting:
            return
        active_ids = self._active_betting_ids()
        next_id = self.betting.next_player(
            self.current_player.id if self.current_player else None, active_ids
        )
        if next_id is None:
            return
        self.turn_index = self.turn_player_ids.index(next_id)
        self._start_turn()

    def _start_turn_timer(self) -> None:
        try:
            seconds = int(self.options.turn_timer)
        except ValueError:
            seconds = 0
        if seconds <= 0:
            self.timer.clear()
            return
        self.timer.start(seconds)

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return
        if getattr(self, "_next_hand_wait_ticks", 0) > 0:
            self._next_hand_wait_ticks -= 1
            if self._next_hand_wait_ticks == 0:
                self._start_new_hand()
            return
        if self.pending_showdown:
            if self.pending_board_wait_ticks > 0:
                self.pending_board_wait_ticks -= 1
                return
            if self.pending_board_reveals:
                stage, count = self.pending_board_reveals.pop(0)
                self._deal_community(count)
                self._announce_board(stage)
                if self.pending_board_reveals and self.pending_board_delay_ticks > 0:
                    self.pending_board_wait_ticks = self.pending_board_delay_ticks
                return
            self.pending_showdown = False
            self._showdown()
            return
        if self.timer.tick():
            self._handle_turn_timeout()
        self._tick_blind_timer()
        BotHelper.on_tick(self)

    def bot_think(self, player: HoldemPlayer) -> str | None:
        return bot_think(self, player)

    # ==========================================================================
    # Actions
    # ==========================================================================
    def _action_fold(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        p.folded = True
        self.pot_manager.mark_folded(p.id)
        poker_log.log_fold(self.action_log, p.name)
        self.broadcast_l("poker-player-folds", player=p.name)
        self._after_action()

    def _action_call(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        to_call = self.betting.amount_to_call(p.id)
        pay = min(p.chips, to_call)
        p.chips -= pay
        if p.chips == 0:
            p.all_in = True
        self.pot_manager.add_contribution(p.id, pay)
        self.betting.record_bet(p.id, pay, is_raise=False)
        if to_call == 0:
            poker_log.log_check(self.action_log, p.name)
            self.broadcast_l("poker-player-checks", player=p.name)
        else:
            self.play_sound("game_3cardpoker/bet.ogg")
            poker_log.log_call(self.action_log, p.name, pay)
            self.broadcast_l("poker-player-calls", player=p.name, amount=pay)
        if p.all_in and pay > 0:
            self.broadcast_l("poker-player-all-in", player=p.name, amount=pay)
        self._sync_team_scores()
        self._after_action()

    def _action_raise(self, player: Player, amount_str: str, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        try:
            amount = int(amount_str)
        except ValueError:
            return
        if amount <= 0:
            return
        if not self.betting.can_raise():
            self.broadcast_l("poker-raise-cap-reached")
            return
        to_call = self.betting.amount_to_call(p.id)
        min_raise = max(self.betting.last_raise_size, 1)
        if amount > p.chips:
            self.broadcast_personal_l(p, "poker-raise-too-large", "poker-raise-too-large")
            return
        if amount == p.chips:
            self._action_all_in(p, "all_in")
            return
        if amount < min_raise:
            self.broadcast_l("poker-raise-too-small", amount=min_raise)
            return
        total = to_call + amount
        # Apply raise mode limits
        caps = compute_pot_limit_caps(
            self.pot_manager.total_pot(), to_call, self.options.raise_mode
        )
        total = clamp_total_to_cap(total, caps)
        if total > p.chips:
            total = p.chips
        if total < to_call + min_raise:
            # Treat short stack as all-in (does not reopen betting)
            self._action_all_in(p, "all_in")
            return
        p.chips -= total
        if p.chips == 0:
            p.all_in = True
        self.play_sound("game_3cardpoker/bet.ogg")
        self.pot_manager.add_contribution(p.id, total)
        self.betting.record_bet(p.id, total, is_raise=True)
        poker_log.log_raise(self.action_log, p.name, total)
        self.broadcast_l("poker-player-raises", player=p.name, amount=total)
        if p.all_in:
            self.broadcast_l("poker-player-all-in", player=p.name, amount=total)
        self._sync_team_scores()
        self._after_action()

    def _bot_input_raise(self, player: Player) -> str:
        if not self.betting:
            return "1"
        to_call = self.betting.amount_to_call(player.id)
        min_raise = max(self.betting.last_raise_size, 1)
        amount = min_raise
        caps = compute_pot_limit_caps(
            self.pot_manager.total_pot(), to_call, self.options.raise_mode
        )
        total = clamp_total_to_cap(to_call + amount, caps)
        amount = max(min_raise, total - to_call)
        max_affordable = max(1, player.chips - to_call)
        amount = min(amount, max_affordable)
        return str(max(1, amount))

    def _action_all_in(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or not self.betting:
            return
        amount = p.chips
        if amount <= 0:
            return
        to_call = self.betting.amount_to_call(p.id)
        min_raise = max(self.betting.last_raise_size, 1)
        pay = clamp_total_to_cap(
            amount,
            compute_pot_limit_caps(self.pot_manager.total_pot(), to_call, self.options.raise_mode),
        )
        p.chips -= pay
        p.all_in = p.chips == 0
        self.play_sound("game_3cardpoker/bet.ogg")
        self.pot_manager.add_contribution(p.id, pay)
        raise_amount = pay - to_call
        is_raise = raise_amount >= min_raise and pay > to_call
        self.betting.record_bet(p.id, pay, is_raise=is_raise)
        if pay > to_call:
            poker_log.log_raise(self.action_log, p.name, pay)
            self.broadcast_l("poker-player-raises", player=p.name, amount=pay)
        elif to_call == 0:
            poker_log.log_check(self.action_log, p.name)
            self.broadcast_l("poker-player-checks", player=p.name)
        else:
            poker_log.log_call(self.action_log, p.name, pay)
            self.broadcast_l("poker-player-calls", player=p.name, amount=pay)
        if p.all_in:
            self.broadcast_l("poker-player-all-in", player=p.name, amount=pay)
        self._sync_team_scores()
        self._after_action()

    # ==========================================================================
    # Betting helpers
    # ==========================================================================
    def _after_action(self) -> None:
        if not self.betting:
            return
        active_ids = self._active_betting_ids()
        if len(active_ids) <= 1:
            self._award_uncontested(active_ids)
            return
        if active_ids and active_ids.issubset(self._all_in_ids()):
            # Reveal remaining community cards and go to showdown
            self._start_all_in_showdown(delay_between_rounds=100)
            return
        if self.betting.is_complete(active_ids, self._all_in_ids()):
            self._advance_phase()
            return
        self._advance_turn()

    def _advance_phase(self) -> None:
        if self.phase == "preflop":
            self.phase = "flop"
            self._deal_community(3)
            self._announce_board("flop")
        elif self.phase == "flop":
            self.phase = "turn"
            self._deal_community(1)
            self._announce_board("turn")
        elif self.phase == "turn":
            self.phase = "river"
            self._deal_community(1)
            self._announce_board("river")
        else:
            self._showdown()
            return
        self._start_betting_round(preflop=False)

    def _showdown(self) -> None:
        self.phase = "showdown"
        self.broadcast_l("poker-showdown")
        self._resolve_pots()
        self._announce_showdown_hands(skip_best=True)
        self._advance_blind_level()
        self._queue_new_hand()

    def _award_uncontested(self, active_ids: set[str]) -> None:
        winner = self.get_player_by_id(next(iter(active_ids))) if active_ids else None
        if not winner:
            return
        amount = self.pot_manager.total_pot()
        if isinstance(winner, HoldemPlayer):
            winner.chips += amount
        self.play_sound(
            random.choice(
                ["game_blackjack/win1.ogg", "game_blackjack/win2.ogg", "game_blackjack/win3.ogg"]
            )
        )  # nosec B311
        self.broadcast_l("poker-player-wins-pot", player=winner.name, amount=amount)
        self._sync_team_scores()
        self._advance_blind_level()
        self._queue_new_hand()

    def _resolve_pots(self) -> None:
        self.last_showdown_winner_ids.clear()
        active_ids = [p.id for p in self.get_active_players()]
        button_id = self.table_state.get_button_id(active_ids)
        pot_results = resolve_pots_with_payouts(
            self.pot_manager.get_pots(),
            lambda player_id: (
                player
                if isinstance((player := self.get_player_by_id(player_id)), HoldemPlayer)
                else None
            ),
            active_ids,
            button_id,
            lambda p: p.id,
            lambda p: best_hand(p.hand + self.community)[0],
            lambda winner, payout: setattr(winner, "chips", winner.chips + payout),
        )
        for pot_result in pot_results:
            self.last_showdown_winner_ids.update(w.id for w in pot_result.winners)
            desc = describe_hand(pot_result.best_score, "en")
            if len(pot_result.winners) == 1:
                winner = pot_result.winners[0]
                cards = read_cards(winner.hand, "en")
                if pot_result.pot_index == 0 or len(pot_result.eligible_player_ids) <= 1:
                    self.play_sound(
                        random.choice(
                            [
                                "game_blackjack/win1.ogg",
                                "game_blackjack/win2.ogg",
                                "game_blackjack/win3.ogg",
                            ]
                        )
                    )  # nosec B311
                    self.broadcast_l(
                        "poker-player-wins-pot-hand",
                        player=winner.name,
                        amount=pot_result.pot_amount,
                        cards=cards,
                        hand=desc,
                    )
                else:
                    self.play_sound(
                        random.choice(
                            [
                                "game_blackjack/win1.ogg",
                                "game_blackjack/win2.ogg",
                                "game_blackjack/win3.ogg",
                            ]
                        )
                    )  # nosec B311
                    self.broadcast_l(
                        "poker-player-wins-side-pot-hand",
                        player=winner.name,
                        amount=pot_result.pot_amount,
                        index=pot_result.pot_index,
                        cards=cards,
                        hand=desc,
                    )
            else:
                names = ", ".join(w.name for w in pot_result.winners)
                self.play_sound(
                    random.choice(
                        [
                            "game_blackjack/win1.ogg",
                            "game_blackjack/win2.ogg",
                            "game_blackjack/win3.ogg",
                        ]
                    )
                )  # nosec B311
                if pot_result.pot_index == 0:
                    self.broadcast_l(
                        "poker-players-split-pot",
                        players=names,
                        amount=pot_result.pot_amount,
                        hand=desc,
                    )
                else:
                    self.broadcast_l(
                        "poker-players-split-side-pot",
                        players=names,
                        amount=pot_result.pot_amount,
                        index=pot_result.pot_index,
                        hand=desc,
                    )
        self._sync_team_scores()

    def _announce_showdown_hands(self, skip_best: bool = False) -> None:
        active = [
            p for p in self.get_active_players() if isinstance(p, HoldemPlayer) and not p.folded
        ]
        if len(active) <= 1:
            return
        skip_ids: set[str] = set()
        if skip_best and self.last_showdown_winner_ids:
            skip_ids = set(self.last_showdown_winner_ids)
        active_ids = [p.id for p in active]
        lines = format_showdown_lines(
            active,
            active_ids,
            self.table_state.get_button_id(active_ids),
            lambda p: p.id,
            lambda p: (
                (
                    "poker-show-hand",
                    {
                        "player": p.name,
                        "cards": read_cards(p.hand, "en"),
                        "hand": describe_hand(best_hand(p.hand + self.community)[0], "en"),
                    },
                ),
                best_hand(p.hand + self.community)[0],
            ),
        )
        for player_id, (message_id, kwargs), _score in lines:
            if skip_ids and player_id in skip_ids:
                continue
            self.broadcast_l(message_id, **kwargs)

    def _order_winners_by_button(self, winners: list[HoldemPlayer]) -> list[HoldemPlayer]:
        if len(winners) <= 1:
            return winners
        active_ids = [p.id for p in self.get_active_players()]
        return order_winners_by_button(
            winners, active_ids, self.table_state.get_button_id(active_ids), lambda p: p.id
        )

    # ==========================================================================
    # Status actions
    # ==========================================================================
    def _action_check_pot(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        pots = self.pot_manager.get_pots()
        if not pots:
            user.speak_l("poker-pot-total", amount=0)
            return
        user.speak_l("poker-pot-total", amount=self.pot_manager.total_pot())
        if not self._all_in_ids():
            return
        user.speak_l("poker-pot-main", amount=pots[0].amount)
        for idx, pot in enumerate(pots[1:], start=1):
            user.speak_l("poker-pot-side", index=idx, amount=pot.amount)

    def _action_check_bet(self, player: Player, action_id: str) -> None:
        if not self.betting:
            return
        to_call = self.betting.amount_to_call(player.id)
        user = self.get_user(player)
        if user:
            user.speak_l("poker-to-call", amount=to_call)

    def _action_check_min_raise(self, player: Player, action_id: str) -> None:
        if not self.betting:
            return
        min_raise = max(self.betting.last_raise_size, 1)
        user = self.get_user(player)
        if user:
            user.speak_l("poker-min-raise", amount=min_raise)

    def _action_check_hand_players(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [
            p.name
            for p in self.get_active_players()
            if isinstance(p, HoldemPlayer) and not p.folded
        ]
        count = len(active)
        if count == 0:
            user.speak_l("poker-hand-players-none")
            return
        names = ", ".join(active)
        if count == 1:
            user.speak_l("poker-hand-players-one", names=names, count=count)
        else:
            user.speak_l("poker-hand-players", names=names, count=count)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, HoldemPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            user.speak(read_cards(p.hand, user.locale))

    def _action_read_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if user:
            user.speak(read_cards(self.community, user.locale))

    def _action_read_hand_value(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, HoldemPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            desc = describe_partial_hand(p.hand + self.community, user.locale)
            user.speak(desc)

    def _action_read_card(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, HoldemPlayer) else None
        if not p:
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        all_cards = p.hand + self.community
        if idx < 0 or idx >= len(all_cards):
            return
        user = self.get_user(player)
        if user:
            user.speak(card_name(all_cards[idx], user.locale))

    def _action_check_button(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0]
        button_id = self.table_state.get_button_id([p.id for p in active])
        button_player = self.get_player_by_id(button_id) if button_id else None
        if button_player:
            user.speak_l("poker-button-is", player=button_player.name)

    def _action_check_position(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0]
        if not active:
            return
        button_id = self.table_state.get_button_id([p.id for p in active])
        order = [p.id for p in active]
        if button_id and player.id in order:
            idx = (order.index(player.id) - order.index(button_id)) % len(order)
            if idx == 0:
                user.speak_l("poker-position-button")
            else:
                key = "poker-position-seat" if idx == 1 else "poker-position-seats"
                user.speak_l(key, position=idx)
        if len(order) >= 2:
            sb_idx, bb_idx = self.table_state.get_blind_indices(order)
            sb_player = self.get_player_by_id(order[sb_idx])
            bb_player = self.get_player_by_id(order[bb_idx])
            if sb_player and bb_player:
                user.speak_l("poker-blinds-players", sb=sb_player.name, bb=bb_player.name)

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("poker-timer-disabled")
        else:
            user.speak_l("poker-timer-remaining", seconds=remaining)

    def _action_check_blind_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.blinds_raise_next_hand:
            user.speak_l("poker-blinds-raise-next-hand")
            return
        if self.blind_timer_ticks <= 0:
            user.speak_l("poker-blind-timer-disabled")
            return
        remaining = (self.blind_timer_ticks + 19) // 20
        minutes = remaining // 60
        seconds = remaining % 60
        user.speak_l("poker-blind-timer-remaining-ms", minutes=minutes, seconds=seconds)

    def _action_reveal_both(self, player: Player, action_id: str) -> None:
        if self.phase != "showdown":
            return
        p = player if isinstance(player, HoldemPlayer) else None
        if not p or p.folded:
            return
        user = self.get_user(player)
        if user:
            user.speak_l("poker-your-hand", cards=read_cards(p.hand, user.locale))

    def _action_reveal_first(self, player: Player, action_id: str) -> None:
        if self.phase != "showdown":
            return
        p = player if isinstance(player, HoldemPlayer) else None
        if not p or p.folded:
            return
        user = self.get_user(player)
        if user and p.hand:
            user.speak(card_name(p.hand[0], user.locale))

    def _action_reveal_second(self, player: Player, action_id: str) -> None:
        if self.phase != "showdown":
            return
        p = player if isinstance(player, HoldemPlayer) else None
        if not p or p.folded:
            return
        user = self.get_user(player)
        if user and len(p.hand) > 1:
            user.speak(card_name(p.hand[1], user.locale))

    # ==========================================================================
    # Helpers
    # ==========================================================================
    def _active_betting_ids(self) -> set[str]:
        return {
            p.id
            for p in self.get_active_players()
            if isinstance(p, HoldemPlayer) and not p.folded and (p.chips > 0 or p.all_in)
        }

    def _all_in_ids(self) -> set[str]:
        return {p.id for p in self.get_active_players() if isinstance(p, HoldemPlayer) and p.all_in}

    def _require_active_player(self, player: Player) -> HoldemPlayer | None:
        if not isinstance(player, HoldemPlayer):
            return None
        if self.current_player != player:
            return None
        if player.folded:
            return None
        return player

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_reveal_enabled(self, player: Player) -> str | None:
        if self.phase != "showdown":
            return "poker-reveal-only-showdown"
        return None

    def _get_call_label(self, player: Player, action_id: str) -> str:
        if not self.betting:
            return Localization.get("en", "poker-call")
        to_call = self.betting.amount_to_call(player.id)
        key = "poker-check" if to_call == 0 else "poker-call"
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, key)

    def _is_reveal_hidden(self, player: Player) -> Visibility:
        if self.phase != "showdown":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _handle_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, HoldemPlayer):
            return
        self._action_fold(player, "fold")

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team:
                team.total_score = p.chips

    def build_game_result(self) -> GameResult:
        active = self.get_active_players()
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

    def _end_game(self, winner: HoldemPlayer | None) -> None:
        self.play_sound("game_pig/win.ogg")
        if winner:
            self.broadcast_l("poker-player-wins-game", player=winner.name)
        self.finish_game()

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_chips = result.custom_data.get("final_chips", {})
        sorted_scores = sorted(final_chips.items(), key=lambda item: item[1], reverse=True)
        for i, (name, chips) in enumerate(sorted_scores, 1):
            lines.append(f"{i}. {name}: {chips} chips")
        return lines
