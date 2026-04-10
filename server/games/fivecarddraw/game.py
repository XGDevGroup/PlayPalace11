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
from ...game_utils import poker_log
from ...game_utils.poker_state import order_after_button
from ...game_utils.poker_showdown import order_winners_by_button, format_showdown_lines
from ...game_utils.poker_payout import resolve_pots_with_payouts
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
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

RAISE_MODES = ["no_limit", "pot_limit", "double_pot"]
RAISE_MODE_LABELS = {
    "no_limit": "poker-raise-no-limit",
    "pot_limit": "poker-raise-pot-limit",
    "double_pot": "poker-raise-double-pot",
}


@dataclass
class FiveCardDrawPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    chips: int = 0
    folded: bool = False
    all_in: bool = False
    bet_this_round: int = 0
    to_discard: set[int] = field(default_factory=set)


@dataclass
class FiveCardDrawOptions(GameOptions):
    starting_chips: int = option_field(
        IntOption(
            default=20000,
            min_val=100,
            max_val=1000000,
            value_key="count",
            label="draw-set-starting-chips",
            prompt="draw-enter-starting-chips",
            change_msg="draw-option-changed-starting-chips",
        )
    )
    ante: int = option_field(
        IntOption(
            default=100,
            min_val=0,
            max_val=1000000,
            value_key="count",
            label="draw-set-ante",
            prompt="draw-enter-ante",
            change_msg="draw-option-changed-ante",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            label="draw-set-turn-timer",
            prompt="draw-select-turn-timer",
            change_msg="draw-option-changed-turn-timer",
        )
    )
    raise_mode: str = option_field(
        MenuOption(
            choices=RAISE_MODES,
            choice_labels=RAISE_MODE_LABELS,
            default="no_limit",
            label="draw-set-raise-mode",
            prompt="draw-select-raise-mode",
            change_msg="draw-option-changed-raise-mode",
        )
    )
    max_raises: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=10,
            value_key="count",
            label="draw-set-max-raises",
            prompt="draw-enter-max-raises",
            change_msg="draw-option-changed-max-raises",
        )
    )


@dataclass
@register_game
class FiveCardDrawGame(Game):
    players: list[FiveCardDrawPlayer] = field(default_factory=list)
    options: FiveCardDrawOptions = field(default_factory=FiveCardDrawOptions)
    deck: Deck | None = None
    discard_pile: list[Card] = field(default_factory=list)
    pot_manager: PokerPotManager = field(default_factory=PokerPotManager)
    betting: PokerBettingRound | None = None
    table_state: PokerTableState = field(default_factory=PokerTableState)
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    hand_number: int = 0
    phase: str = "lobby"
    current_bet_round: int = 0
    action_log: list[tuple[str, dict]] = field(default_factory=list)
    last_showdown_winner_ids: set[str] = field(default_factory=set)

    @classmethod
    def get_name(cls) -> str:
        return "Five Card Draw"

    @classmethod
    def get_type(cls) -> str:
        return "fivecarddraw"

    @classmethod
    def get_category(cls) -> str:
        return "category-poker"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 5

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> FiveCardDrawPlayer:
        return FiveCardDrawPlayer(id=player_id, name=name, is_bot=is_bot, chips=0)

    # ==========================================================================
    # Action availability
    # ==========================================================================
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

    def _is_always_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    # ==========================================================================
    # Action sets / keybinds
    # ==========================================================================
    def create_turn_action_set(self, player: FiveCardDrawPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        action_set.add(
            Action(
                id="call",
                label=Localization.get(locale, "poker-call"),
                handler="_action_call",
                is_enabled="_is_bet_action_enabled",
                is_hidden="_is_bet_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="fold",
                label=Localization.get(locale, "poker-fold"),
                handler="_action_fold",
                is_enabled="_is_bet_action_enabled",
                is_hidden="_is_bet_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="raise",
                label=Localization.get(locale, "poker-raise"),
                handler="_action_raise",
                is_enabled="_is_bet_action_enabled",
                is_hidden="_is_bet_action_hidden",
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
                is_enabled="_is_bet_action_enabled",
                is_hidden="_is_bet_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="draw_cards",
                label=Localization.get(locale, "draw-draw-cards"),
                handler="_action_draw_cards",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                get_label="_get_draw_label",
            )
        )
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"card_key_{i}",
                    label=f"Card key {i}",
                    handler="_action_card_key",
                    is_enabled="_is_discard_toggle_enabled",
                    is_hidden="_is_always_hidden",
                    get_label="_get_card_key_label",
                    show_in_actions_menu=True,
                )
            )
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"toggle_discard_{i}",
                    label=Localization.get(locale, "draw-toggle-discard", index=i),
                    handler="_action_toggle_discard",
                    is_enabled="_is_discard_toggle_enabled",
                    is_hidden="_is_discard_toggle_hidden",
                    get_label="_get_toggle_discard_label",
                    show_in_actions_menu=False,
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
                id="speak_hand_value",
                label=Localization.get(locale, "poker-hand-value"),
                handler="_action_read_hand_value",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            ),
            Action(
                id="check_dealer",
                label=Localization.get(locale, "poker-check-dealer"),
                handler="_action_check_dealer",
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
        ]
        for action in reversed(local_actions):
            action_set.add(action)
            if action.id in action_set._order:
                action_set._order.remove(action.id)
            action_set._order.insert(0, action.id)
        for i in range(1, 6):
            action_set.add(
                Action(
                    id=f"speak_card_{i}",
                    label=Localization.get(locale, "poker-read-card", index=i),
                    handler="_action_read_card",
                    is_enabled="_is_check_enabled",
                    is_hidden="_is_always_hidden",
                    show_in_actions_menu=False,
                )
            )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        setup_poker_keybinds(
            self,
            check_dealer="check_dealer",
            dealer_label="Dealer",
            check_position="check_position",
            check_bet="check_bet",
            check_min_raise="check_min_raise",
            check_hand_players="check_hand_players",
            check_turn_timer="check_turn_timer",
            draw_cards="draw_cards",
        )
        for i in range(1, 6):
            self.define_keybind(
                str(i),
                f"Card key {i}",
                [f"card_key_{i}"],
                state=KeybindState.ACTIVE,
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
        self._start_new_hand()

    def _start_new_hand(self) -> None:
        self.hand_number += 1
        self.phase = "deal"
        self.action_log = []
        self.current_bet_round = 0
        self.pot_manager.reset()
        self.discard_pile = []
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
            p.to_discard = set()
            p.bet_this_round = 0
            p.to_discard = set()

        self.play_sound("game_cards/small_shuffle.ogg")
        self._post_ante(active)
        self._deal_cards(active, 5)
        for p in active:
            user = self.get_user(p)
            if user:
                user.speak_l("draw-dealt-cards", cards=read_cards(p.hand, user.locale))
        self._start_betting_round(start_index=-1)

    def _post_ante(self, active: list[FiveCardDrawPlayer]) -> None:
        ante = self.options.ante
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
        self.broadcast_l("draw-antes-posted", amount=ante)

    def _deal_cards(self, players: list[FiveCardDrawPlayer], count: int) -> None:
        if not players:
            return
        start_index = (self.table_state.button_index + 1) % len(players)
        order = players[start_index:] + players[:start_index]
        delay_ticks = 4
        for _ in range(count):
            for p in order:
                card = self.deck.draw_one() if self.deck else None
                if card:
                    p.hand.append(card)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks, volume=100)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks + 1, volume=100)
            delay_ticks += 6
        for p in players:
            p.hand = sort_cards(p.hand)

    def _start_betting_round(self, start_index: int) -> None:
        self.current_bet_round += 1
        active_ids = [p.id for p in self.get_active_players() if p.chips > 0 and not p.folded]
        order = [p.id for p in self.get_active_players() if p.id in active_ids]
        self.betting = PokerBettingRound(order=order, max_raises=self.options.max_raises or None)
        self.betting.reset()
        if not order:
            self._showdown()
            return
        if start_index < 0:
            # default: left of button
            start_index = (self.table_state.button_index + 1) % len(order)
        self._set_turn_by_index(start_index, order)
        self._announce_betting_round()

    def _announce_betting_round(self) -> None:
        if self.current_bet_round == 1:
            self.broadcast_l("draw-betting-round-1")
        else:
            self.broadcast_l("draw-betting-round-2")

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
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p or p.folded or (p.all_in and self.phase != "draw"):
            self._advance_turn()
            return
        if self.phase == "draw" and p.is_bot and p.all_in:
            self.bot_think(p)
            self._action_draw_cards(p, "draw_cards")
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
        if self.timer.tick():
            self._handle_turn_timeout()
        BotHelper.on_tick(self)

    def bot_think(self, player: FiveCardDrawPlayer) -> str | None:
        return bot_think(self, player)

    # ==========================================================================
    # Action handlers
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
        to_call = self.betting.amount_to_call(p.id)
        total = to_call + amount
        if self.options.raise_mode != "no_limit":
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
        if isinstance(player, FiveCardDrawPlayer):
            if not self.betting:
                return "1"
            to_call = self.betting.amount_to_call(player.id)
            min_raise = max(self.betting.last_raise_size, 1)
            max_raise = max(0, player.chips - to_call)
            if max_raise < min_raise:
                return str(min_raise)
            desired = max(min_raise, min(100, player.chips // 3))
            amount = min(desired, max_raise)
            return str(amount)
        return "1"

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

    def _action_draw_cards(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or self.phase != "draw":
            return
        if not p.to_discard:
            self.broadcast_personal_l(p, "draw-you-stand-pat", "draw-player-stands-pat")
            self._advance_after_draw(p)
            return
        indices = sorted(p.to_discard)
        drawn_cards: list[Card] = []
        for idx in reversed(indices):
            if 0 <= idx < len(p.hand):
                self.discard_pile.append(p.hand.pop(idx))
        for _ in range(len(indices)):
            card = self.deck.draw_one() if self.deck else None
            if card:
                drawn_cards.append(card)
                p.hand.append(card)
        p.hand = sort_cards(p.hand)
        self._play_draw_sounds(len(indices))
        user = self.get_user(p)
        self.broadcast_l("draw-player-draws", exclude=p, player=p.name, count=len(indices))
        if user and drawn_cards:
            user.speak_l("draw-you-drew-cards", cards=read_cards(drawn_cards, user.locale))
        p.to_discard = set()
        self._advance_after_draw(p)

    def _action_toggle_discard(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or self.phase != "draw":
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        self._set_discard(p, idx, discard=idx not in p.to_discard)
        self.update_player_menu(p)
        self._announce_discard_status(p, idx)

    # ==========================================================================
    # Action helpers
    # ==========================================================================
    def _after_action(self) -> None:
        if not self.betting:
            return
        active_ids = self._active_betting_ids()
        if len(active_ids) <= 1:
            self._award_uncontested(active_ids)
            return
        if active_ids and active_ids.issubset(self._all_in_ids()):
            if self.current_bet_round == 1:
                self.phase = "draw"
                self._start_draw_phase()
            else:
                self._showdown()
            return
        if self.betting.is_complete(active_ids, self._all_in_ids()):
            if self.current_bet_round == 1:
                self.phase = "draw"
                self._start_draw_phase()
            else:
                self._showdown()
            return
        self._advance_turn()

    def _start_draw_phase(self) -> None:
        self.broadcast_l("draw-begin-draw")
        self.turn_player_ids = [p.id for p in self.get_active_players() if not p.folded]
        self.turn_index = 0
        self._start_turn()

    def _advance_after_draw(self, player: FiveCardDrawPlayer) -> None:
        if self.current_player != player:
            return
        self.advance_turn(announce=False)
        if self.current_player is None or (
            self.current_player and self.current_player.id == self.turn_player_ids[0]
        ):
            self.phase = "bet2"
            self._start_betting_round(start_index=0)
        else:
            self._start_turn()

    def _showdown(self) -> None:
        self.phase = "showdown"
        self.broadcast_l("poker-showdown")
        self._resolve_pots()
        self._announce_showdown_hands(skip_best=True)
        self._queue_new_hand()

    def _award_uncontested(self, active_ids: set[str]) -> None:
        winner = self.get_player_by_id(next(iter(active_ids))) if active_ids else None
        if not winner:
            return
        amount = self.pot_manager.total_pot()
        if isinstance(winner, FiveCardDrawPlayer):
            winner.chips += amount
        self.play_sound(
            random.choice(
                ["game_blackjack/win1.ogg", "game_blackjack/win2.ogg", "game_blackjack/win3.ogg"]
            )
        )  # nosec B311
        self.broadcast_l("poker-player-wins-pot", player=winner.name, amount=amount)
        self._sync_team_scores()
        self._queue_new_hand()

    def _resolve_pots(self) -> None:
        self.last_showdown_winner_ids.clear()
        active_ids = [p.id for p in self.get_active_players()]
        button_id = self.table_state.get_button_id(active_ids)
        pot_results = resolve_pots_with_payouts(
            self.pot_manager.get_pots(),
            lambda player_id: (
                player
                if isinstance((player := self.get_player_by_id(player_id)), FiveCardDrawPlayer)
                else None
            ),
            active_ids,
            button_id,
            lambda p: p.id,
            lambda p: best_hand(p.hand)[0],
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
            p
            for p in self.get_active_players()
            if isinstance(p, FiveCardDrawPlayer) and not p.folded
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
                        "hand": describe_hand(best_hand(p.hand)[0], "en"),
                    },
                ),
                best_hand(p.hand)[0],
            ),
        )
        for player_id, (message_id, kwargs), _score in lines:
            if skip_ids and player_id in skip_ids:
                continue
            self.broadcast_l(message_id, **kwargs)

    def _queue_new_hand(self) -> None:
        self._next_hand_wait_ticks = 100

    def _order_winners_by_button(
        self, winners: list[FiveCardDrawPlayer]
    ) -> list[FiveCardDrawPlayer]:
        if len(winners) <= 1:
            return winners
        active_ids = [p.id for p in self.get_active_players()]
        return order_winners_by_button(
            winners, active_ids, self.table_state.get_button_id(active_ids), lambda p: p.id
        )

    # ==========================================================================
    # Utility / status actions
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
        if pots:
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
            if isinstance(p, FiveCardDrawPlayer) and not p.folded
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
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            user.speak_l("poker-your-hand", cards=read_cards(p.hand, user.locale))

    def _action_read_hand_value(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        user = self.get_user(player)
        if user:
            desc = describe_partial_hand(p.hand, user.locale)
            user.speak(desc)

    def _action_read_card(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        user = self.get_user(player)
        if user:
            user.speak(card_name(p.hand[idx], user.locale))

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("poker-timer-disabled")
        else:
            user.speak_l("poker-timer-remaining", seconds=remaining)

    def _action_check_raise_mode(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak_l(RAISE_MODE_LABELS.get(self.options.raise_mode, "poker-raise-no-limit"))

    def _action_check_dealer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0 or p.all_in]
        dealer_id = self.table_state.get_button_id([p.id for p in active])
        dealer_player = self.get_player_by_id(dealer_id) if dealer_id else None
        if dealer_player:
            user.speak_l("poker-dealer-is", player=dealer_player.name)

    def _action_check_position(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        active = [p for p in self.get_active_players() if p.chips > 0 or p.all_in]
        if not active:
            return
        dealer_id = self.table_state.get_button_id([p.id for p in active])
        order = [p.id for p in active]
        if dealer_id and player.id in order:
            idx = (order.index(player.id) - order.index(dealer_id)) % len(order)
            if idx == 0:
                user.speak_l("poker-position-dealer")
            else:
                key = "poker-position-dealer-seat" if idx == 1 else "poker-position-dealer-seats"
                user.speak_l(key, position=idx)

    # ==========================================================================
    # Helpers
    # ==========================================================================
    def _active_betting_ids(self) -> set[str]:
        return {
            p.id
            for p in self.get_active_players()
            if isinstance(p, FiveCardDrawPlayer) and not p.folded and (p.chips > 0 or p.all_in)
        }

    def _all_in_ids(self) -> set[str]:
        return {
            p.id
            for p in self.get_active_players()
            if isinstance(p, FiveCardDrawPlayer) and p.all_in
        }

    def _require_active_player(self, player: Player) -> FiveCardDrawPlayer | None:
        if not isinstance(player, FiveCardDrawPlayer):
            return None
        if self.current_player != player:
            return None
        if player.folded:
            return None
        return player

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "draw-not-draw-phase"
        return self._is_turn_action_enabled(player)

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.phase != "draw":
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_bet_action_enabled(self, player: Player) -> str | None:
        if self.phase == "draw":
            return "draw-not-betting"
        return self._is_turn_action_enabled(player)

    def _is_bet_action_hidden(self, player: Player) -> Visibility:
        if self.phase == "draw":
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_discard_toggle_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "action-not-playing"
        return self._is_turn_action_enabled(player)

    def _is_discard_key_enabled(self, player: Player) -> str | None:
        if self.phase != "draw":
            return "action-not-playing"
        return self._is_turn_action_enabled(player)

    def _is_discard_toggle_hidden(self, player: Player) -> Visibility:
        if self.phase != "draw":
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _action_read_card(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        user = self.get_user(player)
        if user:
            user.speak(card_name(p.hand[idx], user.locale))

    def _get_toggle_discard_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return action_id
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return action_id
        if idx < 0 or idx >= len(p.hand):
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        name = card_name(p.hand[idx], locale)
        if idx in p.to_discard:
            return Localization.get(locale, "draw-card-discard", card=name)
        return Localization.get(locale, "draw-card-keep", card=name)

    def _get_card_key_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return action_id
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return action_id
        if idx < 0 or idx >= len(p.hand):
            return action_id
        user = self.get_user(player)
        locale = user.locale if user else "en"
        name = card_name(p.hand[idx], locale)
        if idx in p.to_discard:
            return Localization.get(locale, "draw-card-keep", card=name)
        return Localization.get(locale, "draw-card-discard", card=name)

    def _get_draw_label(self, player: Player, action_id: str) -> str:
        p = player if isinstance(player, FiveCardDrawPlayer) else None
        if not p:
            return Localization.get("en", "draw-draw-cards")
        count = len(p.to_discard)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, "draw-draw-cards-count", count=count)

    def _set_discard(self, player: FiveCardDrawPlayer, idx: int, discard: bool) -> None:
        if discard:
            max_discards = 4 if any(card.rank == 1 for card in player.hand) else 3
            if len(player.to_discard) >= max_discards and idx not in player.to_discard:
                self.broadcast_personal_l(
                    player,
                    "draw-you-discard-limit",
                    "draw-player-discard-limit",
                    count=max_discards,
                )
                return
            player.to_discard.add(idx)
        else:
            player.to_discard.discard(idx)

    def _announce_discard_status(self, player: FiveCardDrawPlayer, idx: int) -> None:
        user = self.get_user(player)
        if not user:
            return
        if idx < 0 or idx >= len(player.hand):
            return
        card = card_name(player.hand[idx], user.locale)
        if idx in player.to_discard:
            user.speak_l("draw-card-discarded", card=card)
        else:
            user.speak_l("draw-card-kept", card=card)

    def _action_card_key(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p or self.phase != "draw":
            return
        try:
            idx = int(action_id.split("_")[-1]) - 1
        except ValueError:
            return
        if idx < 0 or idx >= len(p.hand):
            return
        self._set_discard(p, idx, discard=idx not in p.to_discard)
        self.update_player_menu(p)
        self._announce_discard_status(p, idx)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _handle_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, FiveCardDrawPlayer):
            return
        if self.phase == "draw":
            self._action_draw_cards(player, "draw_cards")
            return
        self._action_fold(player, "fold")

    def _play_draw_sounds(self, count: int) -> None:
        delay_ticks = 0
        for _ in range(count):
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks, volume=100)
            self.schedule_sound("game_cards/draw3.ogg", delay_ticks + 1, volume=100)
            delay_ticks += 6

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

    def _end_game(self, winner: FiveCardDrawPlayer | None) -> None:
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
