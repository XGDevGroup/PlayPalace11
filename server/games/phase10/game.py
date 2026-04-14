"""Phase 10 game implementation for PlayPalace v11."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import datetime

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.action_guard_mixin import ActionGuardMixin
from ...game_utils.bot_helper import BotHelper
from ...game_utils.cards import Card, Deck, DeckFactory
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState
from server.core.users.bot import Bot
from server.core.users.base import User

from .state import (
    Phase10Player,
    Phase10Options,
    TableGroup,
    PhaseRequirement,
    PHASES,
    P10_RANK_WILD,
    P10_RANK_SKIP,
    EVEN_PHASES,
    GROUP_RUN,
    GROUP_COLOR,
    P10_COLOR_NAMES,
)
from .evaluator import (
    is_wild,
    is_skip,
    p10_card_name,
    p10_cards_name,
    resolve_run_order,
    req_description,
    phase_description,
    score_hand,
    score_card,
    validate_group,
    can_hit_group,
    find_phase_assignment,
    active_phases,
    next_phase,
    starting_phase,
)
from .bot import bot_think

# ---------------------------------------------------------------------------
# Sounds
# ---------------------------------------------------------------------------

SOUND_MUSIC = "game_ninetynine/mus.ogg"
SOUND_SHUFFLE = ["game_cards/shuffle1.ogg", "game_cards/shuffle2.ogg", "game_cards/shuffle3.ogg"]
SOUND_DRAW = ["game_cards/draw1.ogg", "game_cards/draw2.ogg", "game_cards/draw3.ogg", "game_cards/draw4.ogg"]
SOUND_DISCARD = ["game_cards/discard1.ogg", "game_cards/discard2.ogg", "game_cards/discard3.ogg"]
SOUND_LAY_DOWN = ["game_cards/play1.ogg", "game_cards/play2.ogg", "game_cards/play3.ogg"]
SOUND_ROUND_START = "game_pig/roundstart.ogg"
SOUND_WIN_ROUND = "game_uno/winround.ogg"
SOUND_WIN_GAME = "game_uno/wingame.ogg"
SOUND_TURN = "game_pig/turn.ogg"


# ---------------------------------------------------------------------------
# Game
# ---------------------------------------------------------------------------


@register_game
@dataclass
class Phase10Game(Game, ActionGuardMixin):
    """Phase 10: complete all 10 phases before your opponents."""

    players: list[Phase10Player] = field(default_factory=list)
    options: Phase10Options = field(default_factory=Phase10Options)

    # Deck / pile
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)

    # Table groups from all players
    table_groups: list[TableGroup] = field(default_factory=list)

    # Turn-level flags (reset each turn)
    turn_has_drawn: bool = False

    # Lay-down mode state
    lay_down_active: bool = False
    lay_down_group_index: int = 0         # which requirement we're filling (0-based)
    lay_down_staged: list[list[int]] = field(default_factory=list)   # card IDs per confirmed group
    lay_down_current: list[int] = field(default_factory=list)        # card IDs selected for current group

    # Hit mode state
    hit_active: bool = False
    hit_card_id: int | None = None        # card selected as the hit card (None = choosing card)
    hit_wild_group_idx: int | None = None # set when choosing wild placement on a run

    # Skip discard state
    skip_discard_active: bool = False
    skip_pending_card_id: int | None = None

    # Discard confirmation state
    discard_pending_card_id: int | None = None

    # Round / game flow
    dealer_index: int = -1
    next_round_wait_ticks: int = 0
    intro_wait_ticks: int = 0

    # Skip targets already used this round (player IDs). Resets each time turns
    # wrap around — "round" per the official rules means once around the table.
    skip_targets_this_round: list[str] = field(default_factory=list)

    # Tiebreaker (only players in this set take turns)
    tiebreaker_mode: bool = False
    tiebreaker_player_ids: list[str] = field(default_factory=list)

    # Fixed-hands countdown
    fixed_hands_remaining: int = 10

    # Set when the game ends so build_game_result can include it
    game_winner_id: str | None = None

    # Turn timer
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)
    _timer_warning_played: bool = False
    _suppress_keybind_rebuild_player_ids: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        super().__post_init__()
        self._timer_warning_played = False
        self._suppress_keybind_rebuild_player_ids = set()

    # =========================================================================
    # Metadata
    # =========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "Phase 10"

    @classmethod
    def get_type(cls) -> str:
        return "phase10"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    # =========================================================================
    # Player management
    # =========================================================================

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> Phase10Player:
        return Phase10Player(id=player_id, name=name, is_bot=is_bot)

    def _get_p10_player(self, player: Player) -> Phase10Player | None:
        return player if isinstance(player, Phase10Player) else None

    def _require_current_player(self, player: Player) -> Phase10Player | None:
        p = self._get_p10_player(player)
        if not p or p.is_spectator:
            return None
        if self.current_player != p:
            return None
        return p

    def _sorted_hand_for_menu(self, p: Phase10Player) -> list:
        """Return the player's hand sorted for menu display.

        During lay-down, already-staged cards (committed to a previous group)
        are pushed to the bottom so the player sees available cards first.
        Sort order is controlled by p.hand_sort.
        """
        staged_ids = {cid for group in self.lay_down_staged for cid in group}
        staged = lambda c: c.id in staged_ids  # noqa: E731
        if p.hand_sort == "color":
            return sorted(p.hand, key=lambda c: (staged(c), c.suit, c.rank, c.id))
        if p.hand_sort == "number_desc":
            return sorted(p.hand, key=lambda c: (staged(c), -c.rank, c.suit, c.id))
        # "default" and "number_asc" both sort ascending by rank
        return sorted(p.hand, key=lambda c: (staged(c), c.rank, c.suit, c.id))

    def _card_action_id(self, p: Phase10Player, card) -> str | None:
        """Return the positional action ID for a card in the player's sorted hand."""
        sorted_hand = self._sorted_hand_for_menu(p)
        for i, c in enumerate(sorted_hand, 1):
            if c.id == card.id:
                return f"card_{i}"
        return None

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _active_players(self) -> list[Phase10Player]:
        return [p for p in self.players if isinstance(p, Phase10Player) and not p.is_spectator]

    # =========================================================================
    # Action sets
    # =========================================================================

    def create_turn_action_set(self, player: Phase10Player) -> ActionSet:
        action_set = ActionSet(name="turn")
        # Card items are dynamically injected by _sync_turn_actions.
        # We add placeholder-free fixed actions here so ordering is stable.
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        locale = self._player_locale(player)
        local_actions = [
            Action(
                id="read_hand",
                label=Localization.get(locale, "phase10-read-hand-action"),
                handler="_action_read_hand",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
            ),
            Action(
                id="read_discard",
                label=Localization.get(locale, "phase10-read-discard-action"),
                handler="_action_read_discard",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
                include_spectators=True,
            ),
            Action(
                id="read_table",
                label=Localization.get(locale, "phase10-read-table-action"),
                handler="_action_read_table",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_phase",
                label=Localization.get(locale, "phase10-check-phase-action"),
                handler="_action_check_phase",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
            ),
            Action(
                id="read_counts",
                label=Localization.get(locale, "phase10-read-counts-action"),
                handler="_action_read_counts",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
                include_spectators=True,
            ),
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "phase10-turn-timer-action"),
                handler="_action_check_turn_timer",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
                include_spectators=True,
            ),
            Action(
                id="sort_by_color",
                label=Localization.get(locale, "phase10-sort-by-color-action"),
                handler="_action_sort_by_color",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
            ),
            Action(
                id="sort_by_number",
                label=Localization.get(locale, "phase10-sort-by-number-action"),
                handler="_action_sort_by_number",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
            ),
            Action(
                id="discard",
                label=Localization.get(locale, "phase10-discard-action"),
                handler="_action_do_discard",
                is_enabled="_is_playing_enabled",
                is_hidden="_is_playing_hidden",
                get_label="_get_do_discard_label",
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
        # Draw
        self.define_keybind("space", "Draw from deck", ["draw_deck"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+d", "Draw from discard", ["draw_discard"], state=KeybindState.ACTIVE)
        # Phase / hit / skip actions
        self.define_keybind("n", "Lay down phase", ["lay_down_phase"], state=KeybindState.ACTIVE)
        self.define_keybind("enter", "Confirm group / select", ["confirm_group", "select_card_for_hit", "select_hit_group", "select_skip_target"], state=KeybindState.ACTIVE)
        self.define_keybind("f", "Confirm group", ["confirm_group"], state=KeybindState.ACTIVE)

        self.define_keybind("h", "Hit", ["hit"], state=KeybindState.ACTIVE)
        self.define_keybind("j", "Discard selected card", ["do_discard"], state=KeybindState.ACTIVE)
        # Info
        self.define_keybind("d", "Read top of discard", ["read_discard"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("c", "Read table groups", ["read_table"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("p", "Check phase status", ["check_phase"], state=KeybindState.ACTIVE)
        self.define_keybind("e", "Read card counts", ["read_counts"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], state=KeybindState.ACTIVE, include_spectators=True)
        self.define_keybind("shift+c", "Sort hand by color", ["sort_by_color"], state=KeybindState.ACTIVE)
        self.define_keybind("shift+h", "Sort hand by number", ["sort_by_number"], state=KeybindState.ACTIVE)

    # =========================================================================
    # Menu sync
    # =========================================================================

    def rebuild_player_menu(self, player: Player, **kwargs) -> None:
        self._sync_turn_actions(player)
        super().rebuild_player_menu(player, **kwargs)

    def update_player_menu(self, player: Player, selection_id: str | None = None, **kwargs) -> None:
        self._sync_turn_actions(player)
        super().update_player_menu(player, selection_id=selection_id, **kwargs)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
        super().rebuild_all_menus()

    def _suppress_keybind_rebuild(self, player: Player) -> None:
        """Call from read-only info actions to prevent the post-keybind menu rebuild."""
        context = self.get_action_context(player)
        if not context or not context.from_keybind:
            return
        self._suppress_keybind_rebuild_player_ids.add(player.id)

    def _should_rebuild_after_keybind(self, player: Player, executed_any: bool) -> bool:
        if player.id in self._suppress_keybind_rebuild_player_ids:
            self._suppress_keybind_rebuild_player_ids.discard(player.id)
            return False
        return super()._should_rebuild_after_keybind(player, executed_any)

    def _sync_turn_actions(self, player: Player) -> None:  # noqa: C901
        p = self._get_p10_player(player)
        if not p:
            return
        turn_set = self.get_action_set(p, "turn")
        if not turn_set:
            return

        # Remove all dynamic items
        turn_set.remove_by_prefix("card_")
        turn_set.remove_by_prefix("hit_group_")
        turn_set.remove_by_prefix("skip_target_")
        for action_id in [
            "draw_deck", "draw_discard",
            "lay_down_phase", "check_requirement", "confirm_group", "cancel_lay_down",
            "hit", "select_card_for_hit", "select_hit_group", "cancel_hit",
            "select_skip_target", "cancel_skip",
            "do_discard",
        ]:
            turn_set.remove(action_id)

        if self.status != "playing" or p.is_spectator:
            return

        is_current = self.current_player == p
        locale = self._player_locale(p)

        # ---- Hand cards: shown in most modes; hidden during skip/group/wild-placement selection ----
        current_in_group_select = is_current and self.hit_active and self.hit_card_id is not None
        current_in_skip_select = is_current and self.skip_discard_active
        current_in_wild_place = is_current and self.hit_wild_group_idx is not None
        if not current_in_skip_select and not current_in_group_select and not current_in_wild_place:
            sorted_hand = self._sorted_hand_for_menu(p)
            for i, card in enumerate(sorted_hand, 1):
                turn_set.add(Action(
                    id=f"card_{i}",
                    label="",
                    handler="_action_card_selected",
                    is_enabled="_is_card_enabled",
                    is_hidden="_is_card_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                ))

        if not is_current:
            return

        # ---- Mode-specific actions ----------------------------------------

        if self.skip_discard_active:
            for other in self._active_players():
                if other.id != p.id:
                    turn_set.add(Action(
                        id=f"skip_target_{other.id}",
                        label=Localization.get(locale, "phase10-skip-target-label",
                                               player=other.name, phase=other.current_phase),
                        handler="_action_select_skip_target",
                        is_enabled="_is_turn_action_enabled",
                        is_hidden="_is_turn_action_hidden",
                    ))
            turn_set.add(Action(
                id="cancel_skip",
                label=Localization.get(locale, "phase10-skip-cancel-action"),
                handler="_action_cancel_skip",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            return

        if self.hit_wild_group_idx is not None:
            # Choosing which end of a run to place a wild
            group = self.table_groups[self.hit_wild_group_idx]
            ordered = resolve_run_order(group.cards)
            low, high = ordered[0][1], ordered[-1][1]
            if low > 1:
                turn_set.add(Action(
                    id="hit_wild_low",
                    label=Localization.get(locale, "phase10-hit-wild-low", value=low - 1),
                    handler="_action_place_wild",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_turn_action_hidden",
                ))
            if high < 12:
                turn_set.add(Action(
                    id="hit_wild_high",
                    label=Localization.get(locale, "phase10-hit-wild-high", value=high + 1),
                    handler="_action_place_wild",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_turn_action_hidden",
                ))
            turn_set.add(Action(
                id="cancel_hit",
                label=Localization.get(locale, "phase10-hit-cancel-action"),
                handler="_action_cancel_hit",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            return

        if self.hit_active and self.hit_card_id is not None:
            # Choosing which group to hit onto
            for i, group in enumerate(self.table_groups):
                turn_set.add(Action(
                    id=f"hit_group_{i}",
                    label="",
                    handler="_action_select_hit_group",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_turn_action_hidden",
                    get_label="_get_hit_group_label",
                ))
            turn_set.add(Action(
                id="cancel_hit",
                label=Localization.get(locale, "phase10-hit-cancel-action"),
                handler="_action_cancel_hit",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            return

        if self.hit_active and self.hit_card_id is None:
            # Choosing which card to hit with (cards already shown above)
            turn_set.add(Action(
                id="cancel_hit",
                label=Localization.get(locale, "phase10-hit-cancel-action"),
                handler="_action_cancel_hit",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            return

        if self.lay_down_active:
            reqs = self._current_phase_reqs(p)
            total = len(reqs)
            current = self.lay_down_group_index + 1
            turn_set.add(Action(
                id="check_requirement",
                label=Localization.get(locale, "phase10-check-req-action"),
                handler="_action_check_requirement",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            turn_set.add(Action(
                id="confirm_group",
                label=Localization.get(
                    locale, "phase10-confirm-group-action",
                    current=current, total=total,
                ),
                handler="_action_confirm_lay_down_group",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            turn_set.add(Action(
                id="cancel_lay_down",
                label=Localization.get(locale, "phase10-cancel-lay-down-action"),
                handler="_action_cancel_lay_down",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            ))
            return

        # ---- Normal turn actions ------------------------------------------
        if not self.turn_has_drawn:
            # Draw from deck
            turn_set.add(Action(
                id="draw_deck",
                label=Localization.get(locale, "phase10-draw-deck-action"),
                handler="_action_draw_deck",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_keybind_only_hidden",
            ))
            # Draw from discard (if top is not a Skip and pile is non-empty)
            if self.discard_pile and not is_skip(self.discard_pile[-1]):
                top_name = p10_card_name(self.discard_pile[-1], locale)
                turn_set.add(Action(
                    id="draw_discard",
                    label=Localization.get(locale, "phase10-draw-discard-action", card=top_name),
                    handler="_action_draw_discard",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_keybind_only_hidden",
                ))
        else:
            # Lay down phase
            if not p.phase_laid_down:
                reqs = self._current_phase_reqs(p)
                desc = phase_description(p.current_phase, locale)
                turn_set.add(Action(
                    id="lay_down_phase",
                    label=Localization.get(locale, "phase10-lay-down-action", phase=p.current_phase),
                    handler="_action_start_lay_down",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_keybind_only_hidden",
                ))
            # Hit (only if own phase is down and groups exist)
            if p.phase_laid_down and self.table_groups:
                turn_set.add(Action(
                    id="hit",
                    label=Localization.get(locale, "phase10-hit-action"),
                    handler="_action_start_hit",
                    is_enabled="_is_turn_action_enabled",
                    is_hidden="_is_keybind_only_hidden",
                ))
            # Discard (Delete key; always present post-draw, hidden from actions menu)
            turn_set.add(Action(
                id="do_discard",
                label="",
                handler="_action_do_discard",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_keybind_only_hidden",
                get_label="_get_do_discard_label",
                show_in_actions_menu=False,
            ))

    # =========================================================================
    # Dynamic label helpers
    # =========================================================================

    def _get_card_label(self, player: Player, action_id: str) -> str:
        p = self._get_p10_player(player)
        locale = self._player_locale(player)
        if not p:
            return action_id
        index = int(action_id.split("_")[-1]) - 1
        sorted_hand = self._sorted_hand_for_menu(p)
        if index < 0 or index >= len(sorted_hand):
            return action_id
        card = sorted_hand[index]
        name = p10_card_name(card, locale)
        if self.lay_down_active:
            staged_ids = {cid for group in self.lay_down_staged for cid in group}
            if card.id in staged_ids:
                return Localization.get(locale, "phase10-card-label-staged", card=name)
            if card.id in self.lay_down_current:
                return Localization.get(locale, "phase10-card-label-selected", card=name)
        elif self.discard_pending_card_id == card.id:
            return Localization.get(locale, "phase10-card-label-selected", card=name)
        return name

    def _get_hit_group_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        idx = int(action_id.split("_")[-1])
        if idx >= len(self.table_groups):
            return action_id
        group = self.table_groups[idx]
        owner = self.get_player_by_id(group.owner_id)
        owner_name = owner.name if owner else "?"
        cards_str = self._format_group_summary(group.cards, group.requirement, locale)
        return Localization.get(
            locale, "phase10-table-group-entry",
            owner=owner_name,
            cards=cards_str,
        )

    def _get_do_discard_label(self, player: Player, action_id: str) -> str:
        p = self._get_p10_player(player)
        locale = self._player_locale(player)
        if p and self.discard_pending_card_id is not None:
            card = next((c for c in p.hand if c.id == self.discard_pending_card_id), None)
            if card:
                return Localization.get(locale, "phase10-discard-confirm-action",
                                        card=p10_card_name(card, locale))
        return Localization.get(locale, "phase10-discard-action")

    def _format_group_summary(self, cards: list[Card], req: PhaseRequirement, locale: str) -> str:
        """Brief summary of a group's current contents."""
        naturals = [c for c in cards if not is_wild(c)]
        if req.kind == GROUP_RUN:
            ordered = resolve_run_order(cards)
            low = ordered[0][1]
            high = ordered[-1][1]
            return Localization.get(locale, "phase10-group-summary-run", low=low, high=high)
        if req.kind == GROUP_COLOR:
            color_key = P10_COLOR_NAMES.get(naturals[0].suit, "") if naturals else ""
            color = Localization.get(locale, color_key) if color_key else "?"
            return Localization.get(locale, "phase10-group-summary-color",
                                    count=len(cards), color=color)
        # SET
        rank = naturals[0].rank if naturals else 0
        return Localization.get(locale, "phase10-group-summary-set", count=len(cards), rank=rank)

    # =========================================================================
    # Visibility / enabled helpers
    # =========================================================================

    def _is_playing_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_playing_hidden(self, player: Player) -> Visibility:
        return Visibility.HIDDEN

    def _is_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        p = self._get_p10_player(player)
        if not p or self.status != "playing":
            return "action-not-playing"
        if p.is_spectator:
            return "action-not-playing"
        if self.current_player == p:
            return None
        return "action-not-playing"

    def _is_card_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        return Visibility.VISIBLE

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        """Always enabled — these actions are only added when the mode is active."""
        return None

    def _is_keybind_only_hidden(self, player: Player) -> Visibility:
        """Actions accessible via keybind; hide from turn menu."""
        return Visibility.HIDDEN

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        """Always visible — these actions are only added when the mode is active."""
        return Visibility.VISIBLE

    # =========================================================================
    # Game flow
    # =========================================================================

    def on_start(self) -> None:
        self.status = "playing"
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.tiebreaker_mode = False
        self.tiebreaker_player_ids = []
        self.fixed_hands_remaining = 10

        active = self._active_players()
        sp = starting_phase(self.options.even_phases_only)
        for p in active:
            p.current_phase = sp
            p.phase_laid_down = False
            p.score = 0
            p.skipped = False

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])

        self.play_music(SOUND_MUSIC)
        self.intro_wait_ticks = 7 * 20

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active:
            return

        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return

        if self.next_round_wait_ticks > 0:
            self.next_round_wait_ticks -= 1
            if self.next_round_wait_ticks == 0:
                self._start_new_hand()
            return

        if self.timer.tick():
            self._handle_turn_timeout()
        self._maybe_play_timer_warning()
        BotHelper.on_tick(self)

    def bot_think(self, player: Phase10Player) -> str | None:
        return bot_think(self, player)

    def _start_new_hand(self) -> None:
        self.round += 1
        self.table_groups = []
        self.skip_targets_this_round = []

        # Deal
        self.deck, _ = DeckFactory.phase10_deck()
        self.discard_pile = []

        if self.tiebreaker_mode:
            active = [p for p in self._active_players() if p.id in self.tiebreaker_player_ids]
        else:
            active = self._active_players()

        for p in active:
            p.hand = []
            p.phase_laid_down = False
            p.skipped = False

        for _ in range(10):
            for p in active:
                card = self.deck.draw_one()
                if card:
                    p.hand.append(card)

        # Rotate dealer
        if self.turn_player_ids:
            self.dealer_index = (self.dealer_index + 1) % len(self.turn_player_ids)
        else:
            # First hand: seat human players before bots so humans go first.
            # Dealer is set to the last player so turn_index wraps to 0 (first human).
            active = sorted(active, key=lambda p: p.is_bot)
            self.dealer_index = len(active) - 1

        self.set_turn_players(active, reset_index=False)
        if self.turn_player_ids:
            # First player is left of dealer
            self.turn_index = (self.dealer_index + 1) % len(self.turn_player_ids)

        # Flip starting discard
        start_card = self.deck.draw_one()
        if start_card:
            self.discard_pile.append(start_card)

        self.play_sound(random.choice(SOUND_SHUFFLE))
        self.schedule_sound(random.choice(SOUND_DRAW), 10)

        self.broadcast_l("phase10-new-hand", round=self.round)

        if start_card:
            if is_skip(start_card):
                first = self.current_player
                first_name = first.name if first else "?"
                self.broadcast_l("phase10-start-discard-skip", player=first_name)
                # Auto-skip the first player
                if first:
                    p10_first = self._get_p10_player(first)
                    if p10_first:
                        p10_first.skipped = True
            else:
                for p in self._active_players():
                    user = self.get_user(p)
                    if user:
                        user.speak_l("phase10-start-discard",
                                     card=p10_card_name(start_card, self._player_locale(p)),
                                     buffer="table")

        self.play_sound(SOUND_ROUND_START)
        self.rebuild_all_menus()
        self._start_turn()

    def _start_turn(self) -> None:
        player = self.current_player
        p = self._get_p10_player(player) if player else None
        if not p:
            return

        # Reset turn flags
        self.turn_has_drawn = False
        self.lay_down_active = False
        self.lay_down_staged = []
        self.lay_down_current = []
        self.hit_active = False
        self.hit_card_id = None
        self.hit_wild_group_idx = None
        self.skip_discard_active = False
        self.skip_pending_card_id = None
        self.discard_pending_card_id = None
        self._timer_warning_played = False

        # Handle skip
        if p.skipped:
            p.skipped = False
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-your-turn-skipped", buffer="table")
            self._advance_turn()
            return

        self._start_turn_timer()
        self.broadcast_personal_l(p, "game-your-turn", "game-turn-start")

        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(25, 40))

        self.rebuild_player_menu(p, position=1)
        # Update other players' menus so they can see fresh card counts
        for other in self.players:
            if other.id != p.id:
                self.rebuild_player_menu(other)

    def _advance_turn(self) -> None:
        old_index = self.turn_index
        self.advance_turn(announce=False)
        new_index = self.turn_index
        # Detect wrap-around: when turn_index cycles back, a new round begins and
        # skip targets reset (official rule: once per round = once around the table).
        if (self.turn_direction >= 0 and new_index <= old_index) or \
           (self.turn_direction < 0 and new_index >= old_index):
            self.skip_targets_this_round = []
        self._start_turn()

    def _ensure_deck(self) -> None:
        """Reshuffle discard pile into deck if deck is empty."""
        if not self.deck.is_empty():
            return
        if len(self.discard_pile) <= 1:
            self.broadcast_l("phase10-deck-truly-empty")
            self._end_round(None)
            return
        top = self.discard_pile[-1]
        rest = self.discard_pile[:-1]
        self.discard_pile = [top]
        self.deck = Deck(cards=rest)
        self.deck.shuffle()
        self.broadcast_l("phase10-deck-reshuffled")

    # =========================================================================
    # Round end
    # =========================================================================

    def _end_round(self, winner: Phase10Player | None) -> None:  # noqa: C901
        self.game_active = False  # Pause ticking while computing state

        # Determine active players
        if self.tiebreaker_mode:
            active = [p for p in self._active_players() if p.id in self.tiebreaker_player_ids]
        else:
            active = self._active_players()

        # Announce who went out immediately — single clear message, rest follows
        if winner:
            self.broadcast_personal_l(winner, "phase10-you-go-out", "phase10-player-goes-out",
                                       round=self.round)
            self.play_sound(SOUND_WIN_ROUND)

        # Compute scores (state only, no announces yet)
        round_penalties: dict[str, int] = {}
        for p in active:
            penalty = 0 if p is winner else score_hand(p.hand)
            p.score += penalty
            round_penalties[p.id] = penalty

        # Clear hands now that scoring is done
        for p in active:
            p.hand = []

        # Advance phases (state only, no announces yet)
        even_only = self.options.even_phases_only
        phase_announces: list[tuple] = []
        for p in active:
            if self.options.fixed_hands:
                new_phase = next_phase(p.current_phase, even_only)
                p.current_phase = min(new_phase, 11)
                phase_announces.append((p, "phase10-you-fixed-hands-advance", "phase10-fixed-hands-advance",
                                        {"next": p.current_phase}))
            elif p.phase_laid_down:
                new_phase = next_phase(p.current_phase, even_only)
                p.current_phase = new_phase
                phase_announces.append((p, "phase10-you-advance", "phase10-player-advances",
                                        {"next": p.current_phase}))
            else:
                phase_announces.append((p, "phase10-you-stay", "phase10-player-stays",
                                        {"phase": p.current_phase}))

        # Update TeamManager scores (negate so higher = better internally)
        for p in active:
            penalty = round_penalties.get(p.id, 0)
            if penalty > 0:
                self._team_manager.add_to_team_score(p.name, -penalty)

        # Check whether the game ends this round before showing results.
        game_over = self._check_game_end(active)

        # Determine whether this is the final fixed-hands hand.
        fixed_hands_over = False
        if self.options.fixed_hands and not self.tiebreaker_mode:
            self.fixed_hands_remaining -= 1
            if self.fixed_hands_remaining <= 0:
                fixed_hands_over = True

        self.game_active = True

        # Show each player a status box with their personalised round summary.
        # Using a status box lets each player read at their own pace rather than
        # racing against a fixed stagger timer.
        for p in active:
            user = self.get_user(p)
            if not user:
                continue
            locale = user.locale
            lines: list[str] = [Localization.get(locale, "phase10-round-scoring-header")]

            # Score lines: personal pronoun for self, third person for others.
            for q in active:
                if q is winner:
                    if q is p:
                        lines.append(Localization.get(locale, "phase10-you-score-zero"))
                    else:
                        lines.append(Localization.get(locale, "phase10-player-scores-zero", player=q.name))
                else:
                    if q is p:
                        lines.append(Localization.get(locale, "phase10-you-score",
                                                       points=round_penalties[q.id], total=q.score))
                    else:
                        lines.append(Localization.get(locale, "phase10-player-scores",
                                                       player=q.name, points=round_penalties[q.id], total=q.score))

            # Phase advancement lines.
            for q, personal_id, others_id, kwargs in phase_announces:
                if q is p:
                    lines.append(Localization.get(locale, personal_id, **kwargs))
                else:
                    lines.append(Localization.get(locale, others_id, player=q.name, **kwargs))

            if fixed_hands_over:
                lines.append(Localization.get(locale, "phase10-fixed-hands-over"))

            self.status_box(p, lines)

        if game_over:
            return

        if fixed_hands_over:
            # Small delay so the status box is visible before winner resolution fires.
            self.schedule_event("resolve_winner", {}, delay_ticks=20)
            self.next_round_wait_ticks = 40
            return

        self.next_round_wait_ticks = 2 * 20  # 2 seconds before next round

    def _check_game_end(self, active: list[Phase10Player]) -> bool:  # noqa: C901
        """Check whether any player has completed the target phase. Returns True if game ended."""
        winning_phase = self.options.winning_phase
        even_only = self.options.even_phases_only

        # Clamp winning_phase to what's actually in play
        valid_phases = active_phases(even_only)
        if winning_phase not in valid_phases:
            winning_phase = valid_phases[-1]

        # Players who completed the winning phase this round
        # (current_phase has already been advanced, so check if > winning_phase OR == 11)
        completers = [p for p in active if p.current_phase > winning_phase]

        if not completers:
            return False

        if len(completers) == 1:
            winner = completers[0]
            self._declare_winner(winner, active)
            return True

        # Multiple completers: lowest score wins
        min_score = min(p.score for p in completers)
        top = [p for p in completers if p.score == min_score]

        if len(top) == 1:
            self._declare_winner(top[0], active)
            return True

        # Genuine tie: tiebreaker round
        tied_names = Localization.format_list_and("en", [p.name for p in top])
        self.broadcast_l("phase10-tiebreaker", players=tied_names, phase=winning_phase)
        for p in top:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-tiebreaker-you", phase=winning_phase, buffer="table")

        # Reset to the winning phase for tied players
        for p in top:
            p.current_phase = winning_phase
            p.phase_laid_down = False

        self.tiebreaker_mode = True
        self.tiebreaker_player_ids = [p.id for p in top]
        self.game_active = True
        self.next_round_wait_ticks = 4 * 20
        return True

    def on_game_event(self, event_type: str, data: dict) -> None:
        if event_type == "resolve_winner":
            active = self._active_players()
            self._resolve_winner(active)

    def _resolve_winner(self, active: list[Phase10Player]) -> None:
        """Resolve winner for fixed-hands mode (lowest score wins). Ties enter a tiebreaker hand."""
        min_score = min(p.score for p in active)
        winners = [p for p in active if p.score == min_score]
        if len(winners) == 1:
            self._declare_winner(winners[0], active)
            return
        # Genuine score tie: enter a tiebreaker hand using the same infrastructure
        # as _check_game_end. The fixed_hands countdown is suspended while tiebreaker_mode
        # is active (see _end_round) so this cannot loop with _resolve_winner.
        winning_phase = max(p.current_phase for p in winners)
        tied_names = Localization.format_list_and("en", [p.name for p in winners])
        self.broadcast_l("phase10-tiebreaker", players=tied_names, phase=winning_phase)
        for p in winners:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-tiebreaker-you", phase=winning_phase, buffer="table")
            p.current_phase = winning_phase
            p.phase_laid_down = False
        self.tiebreaker_mode = True
        self.tiebreaker_player_ids = [p.id for p in winners]
        self.game_active = True
        self.next_round_wait_ticks = 4 * 20

    def _declare_winner(self, winner: Phase10Player, active: list[Phase10Player]) -> None:
        self.play_sound(SOUND_WIN_GAME)
        self.broadcast_personal_l(winner, "phase10-you-win", "phase10-game-winner",
                                   score=winner.score)
        self.game_winner_id = winner.id
        self.finish_game()

    def build_game_result(self) -> GameResult:
        active = self._active_players()
        winner = next((p for p in active if p.id == self.game_winner_id), None)
        final_scores = {
            p.name: {"phase": p.current_phase, "score": p.score}
            for p in active
        }
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot,
                    is_virtual_bot=p.is_virtual_bot,
                )
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "final_scores": final_scores,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "phase10-score-header")]
        final_scores: dict = result.custom_data.get("final_scores", {})
        # Sort by score ascending (lower is better)
        sorted_entries = sorted(final_scores.items(), key=lambda kv: kv[1]["score"])
        for player_name, data in sorted_entries:
            lines.append(Localization.get(
                locale, "phase10-score-entry",
                player=player_name,
                phase=data["phase"],
                score=data["score"],
            ))
        return lines

    # =========================================================================
    # Draw actions
    # =========================================================================

    def _action_draw_deck(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return
        if self.turn_has_drawn:
            return
        self._ensure_deck()
        if not self.game_active:
            return
        card = self.deck.draw_one()
        if not card:
            return
        p.hand.append(card)
        self.turn_has_drawn = True
        locale = self._player_locale(p)
        card_name = p10_card_name(card, locale)
        self.play_sound(random.choice(SOUND_DRAW))
        self.broadcast_personal_l(p, "phase10-you-draw-deck", "phase10-player-draws-deck",
                                   card=card_name)
        self._start_turn_timer()
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(15, 25))
        selection_id = self._card_action_id(p, card)
        self.update_player_menu(p, selection_id=selection_id)
        for other in self.players:
            if other.id != p.id:
                self.rebuild_player_menu(other)

    def _action_draw_discard(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return
        if self.turn_has_drawn:
            return
        if not self.discard_pile:
            return
        top = self.discard_pile[-1]
        if is_skip(top):
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-cannot-draw-skip")
            return
        card = self.discard_pile.pop()
        p.hand.append(card)
        self.turn_has_drawn = True
        locale = self._player_locale(p)
        card_name = p10_card_name(card, locale)
        self.play_sound(random.choice(SOUND_DRAW))
        self.broadcast_personal_l(p, "phase10-you-draw-discard", "phase10-player-draws-discard",
                                   card=card_name)
        self._start_turn_timer()
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(15, 25))
        selection_id = self._card_action_id(p, card)
        self.update_player_menu(p, selection_id=selection_id)
        for other in self.players:
            if other.id != p.id:
                self.rebuild_player_menu(other)

    # =========================================================================
    # Card selection (dispatches based on current mode)
    # =========================================================================

    def _action_card_selected(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return

        index = int(action_id.split("_")[-1]) - 1
        sorted_hand = self._sorted_hand_for_menu(p)
        if index < 0 or index >= len(sorted_hand):
            return
        card = sorted_hand[index]

        if not self.turn_has_drawn and not self.lay_down_active and not self.hit_active:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-must-draw-first")
            return

        if self.lay_down_active:
            self._toggle_card_in_group(p, card)
        elif self.hit_active and self.hit_card_id is None:
            self._select_hit_card(p, card)
        elif self.hit_active and self.hit_card_id is not None:
            # Already chose a hit card; re-selecting switches to a different card
            self._select_hit_card(p, card)
        elif self.skip_discard_active:
            pass  # Ignore; player should pick a skip target
        else:
            user = self.get_user(p)
            if not p.phase_laid_down:
                # Can't hit until own phase is laid down — say so, don't mark for discard.
                if user:
                    user.speak_l("phase10-hit-no-phase", buffer="table")
                self.update_player_menu(p, selection_id=self._card_action_id(p, card))
            elif not self.table_groups:
                if user:
                    user.speak_l("phase10-hit-no-groups", buffer="table")
                self.update_player_menu(p, selection_id=self._card_action_id(p, card))
            else:
                # Phase is laid down and groups exist — always enter hit mode with this
                # card so the player can choose a group (even if no group accepts it).
                self.discard_pending_card_id = card.id
                self.hit_active = True
                self.hit_card_id = card.id
                locale = self._player_locale(p)
                if user:
                    user.speak_l("phase10-hit-choose-group",
                                 card=p10_card_name(card, locale), buffer="table")
                self.rebuild_player_menu(p, position=1)
                if p.is_bot:
                    BotHelper.jolt_bot(p, ticks=random.randint(5, 10))

    # =========================================================================
    # Lay-down mode
    # =========================================================================

    def _action_start_lay_down(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return
        if not self.turn_has_drawn:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-must-draw-first")
            return
        if p.phase_laid_down:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-already-laid-down")
            return

        self.lay_down_active = True
        self.lay_down_group_index = 0
        self.lay_down_staged = []
        self.lay_down_current = []

        reqs = self._current_phase_reqs(p)
        locale = self._player_locale(p)
        desc = phase_description(p.current_phase, locale)
        req = req_description(reqs[0], locale)
        user = self.get_user(p)
        if user:
            user.speak_l(
                "phase10-lay-down-start",
                phase=p.current_phase, description=desc,
                current=1, total=len(reqs), req=req,
                buffer="table",
            )
        self.rebuild_player_menu(p, position=1)

    def _toggle_card_in_group(self, p: Phase10Player, card: Card) -> None:
        locale = self._player_locale(p)
        card_name = p10_card_name(card, locale)
        reqs = self._current_phase_reqs(p)
        current_num = self.lay_down_group_index + 1

        # Build current selection label (after toggle)
        staged_ids = {cid for group in self.lay_down_staged for cid in group}
        if card.id in self.lay_down_current:
            self.lay_down_current.remove(card.id)
            msg_key = "phase10-lay-down-remove"
        elif card.id in staged_ids:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-lay-down-card-already-staged", card=card_name)
            self.update_player_menu(p, selection_id=self._card_action_id(p, card))
            return
        else:
            self.lay_down_current.append(card.id)
            msg_key = "phase10-lay-down-add"

        # Build current cards string
        selected_cards = [c for c in p.hand if c.id in self.lay_down_current]
        cards_str = p10_cards_name(selected_cards, locale) if selected_cards else ""
        user = self.get_user(p)
        if user:
            if selected_cards:
                user.speak_l(msg_key, card=card_name, current=current_num,
                              cards=cards_str, buffer="table")
            else:
                user.speak_l("phase10-lay-down-selection-empty", current=current_num, buffer="table")

        self.update_player_menu(p, selection_id=self._card_action_id(p, card))

    def _action_confirm_lay_down_group(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.lay_down_active:
            return

        reqs = self._current_phase_reqs(p)
        req = reqs[self.lay_down_group_index]
        locale = self._player_locale(p)
        user = self.get_user(p)

        # Gather selected cards
        selected = [c for c in p.hand if c.id in self.lay_down_current]

        # Also include already-staged cards (must not overlap)
        staged_ids: set[int] = set()
        for group_ids in self.lay_down_staged:
            staged_ids.update(group_ids)

        # Validate
        ok, err_key = validate_group(selected, req)
        if not ok:
            self.lay_down_current = []
            if user:
                if err_key == "phase10-err-need-cards":
                    user.speak_l(err_key, count=req.count, buffer="table")
                else:
                    user.speak_l(err_key, buffer="table")
            self.rebuild_player_menu(p, position=1)
            return

        # Confirm this group
        self.lay_down_staged.append(list(self.lay_down_current))
        current_num = self.lay_down_group_index + 1
        cards_str = p10_cards_name(selected, locale)
        if user:
            user.speak_l("phase10-lay-down-confirmed-group", current=current_num, cards=cards_str, buffer="table")

        self.lay_down_group_index += 1
        self.lay_down_current = []

        if self.lay_down_group_index >= len(reqs):
            # All groups confirmed — commit the phase
            self._commit_lay_down(p)
        else:
            # Prompt for next group
            next_req = reqs[self.lay_down_group_index]
            req_str = req_description(next_req, locale)
            next_num = self.lay_down_group_index + 1
            if user:
                user.speak_l(
                    "phase10-lay-down-next-group",
                    prev=current_num, current=next_num,
                    total=len(reqs), req=req_str,
                    buffer="table",
                )
            self.rebuild_player_menu(p, position=1)

    def _commit_lay_down(self, p: Phase10Player) -> None:
        """Remove staged cards from hand and add groups to the table."""
        all_staged_ids: set[int] = set()
        for group_ids in self.lay_down_staged:
            all_staged_ids.update(group_ids)

        reqs = self._current_phase_reqs(p)
        # Count existing groups for this player (for index offset)
        existing = sum(1 for g in self.table_groups if g.owner_id == p.id)
        new_groups: list[TableGroup] = []

        for group_idx, group_ids in enumerate(self.lay_down_staged):
            cards = [c for c in p.hand if c.id in group_ids]
            req = reqs[group_idx]
            tg = TableGroup(
                owner_id=p.id,
                group_index=existing + group_idx,
                requirement=req,
                cards=cards,
            )
            self.table_groups.append(tg)
            new_groups.append(tg)

        # Remove cards from hand
        p.hand = [c for c in p.hand if c.id not in all_staged_ids]
        p.phase_laid_down = True

        self.lay_down_active = False
        self.lay_down_staged = []
        self.lay_down_current = []
        self.lay_down_group_index = 0

        locale = self._player_locale(p)
        desc = phase_description(p.current_phase, locale)

        # Build per-group card detail strings for the announcement
        group_detail_parts: list[str] = []
        for tg in new_groups:
            group_detail_parts.append(self._format_group_summary(tg.cards, tg.requirement, locale))
        details = " and ".join(group_detail_parts)

        self.play_sound(random.choice(SOUND_LAY_DOWN))
        self.broadcast_personal_l(
            p,
            "phase10-lay-down-success",
            "phase10-player-lays-down",
            phase=p.current_phase,
            description=desc,
            details=details,
        )

        if len(p.hand) == 0:
            self._end_round(p)
            return

        self.rebuild_player_menu(p, position=1)
        for other in self.players:
            if other.id != p.id:
                self.rebuild_player_menu(other)

    def _action_cancel_lay_down(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.lay_down_active:
            return
        self.lay_down_active = False
        self.lay_down_staged = []
        self.lay_down_current = []
        self.lay_down_group_index = 0
        locale = self._player_locale(p)
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-lay-down-cancel", buffer="table")
        self.rebuild_player_menu(p, position=1)

    def _action_check_requirement(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.lay_down_active:
            return
        reqs = self._current_phase_reqs(p)
        if self.lay_down_group_index >= len(reqs):
            return
        req = reqs[self.lay_down_group_index]
        locale = self._player_locale(p)
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-check-req-result", req=req_description(req, locale))

    # =========================================================================
    # Hit mode
    # =========================================================================

    def _action_start_hit(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return
        if not self.turn_has_drawn:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-must-draw-first")
            return
        if not p.phase_laid_down:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-hit-no-phase")
            return
        if not self.table_groups:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-hit-no-groups")
            return

        self.hit_active = True
        self.hit_card_id = None
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-hit-mode-start", buffer="table")
        self.rebuild_player_menu(p, position=1)

    def _select_hit_card(self, p: Phase10Player, card: Card) -> None:
        self.hit_card_id = card.id
        locale = self._player_locale(p)
        card_name = p10_card_name(card, locale)
        user = self.get_user(p)
        if user:
            lines: list[str] = [Localization.get(locale, "phase10-hit-choose-group", card=card_name)]
            for group in self.table_groups:
                owner = self.get_player_by_id(group.owner_id)
                owner_name = owner.name if owner else "?"
                cards_str = self._format_group_summary(group.cards, group.requirement, locale)
                lines.append(Localization.get(locale, "phase10-table-group-entry",
                                              owner=owner_name, cards=cards_str))
            self.status_box(p, lines)
        self.rebuild_player_menu(p, position=1)

    def _action_select_hit_group(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.hit_active or self.hit_card_id is None:
            return

        group_idx = int(action_id.split("_")[-1])
        if group_idx >= len(self.table_groups):
            return

        card = next((c for c in p.hand if c.id == self.hit_card_id), None)
        if not card:
            self.hit_card_id = None
            self.hit_wild_group_idx = None
            return

        group = self.table_groups[group_idx]
        ok, reason_key = can_hit_group(group, card)
        locale = self._player_locale(p)
        user = self.get_user(p)

        if not ok:
            reason = Localization.get(locale, reason_key)
            if user:
                user.speak_l("phase10-hit-invalid", card=p10_card_name(card, locale),
                              reason=reason, buffer="table")
            self.hit_active = False
            self.hit_card_id = None
            self.hit_wild_group_idx = None
            self.rebuild_player_menu(p, position=1)
            return

        # Wild hitting a run: ask player which end to extend (if both ends open)
        if is_wild(card) and group.requirement.kind == GROUP_RUN:
            ordered = resolve_run_order(group.cards)
            low, high = ordered[0][1], ordered[-1][1]
            can_go_low = low > 1
            can_go_high = high < 12
            if can_go_low and can_go_high:
                self.hit_wild_group_idx = group_idx
                if user:
                    user.speak_l("phase10-hit-wild-choose", buffer="table")
                self.rebuild_player_menu(p, position=1)
                return
            # Only one end available — place automatically
            # (can_hit_group already blocks the all-full case)

        self._apply_hit(p, card, group_idx)

    def _apply_hit(self, p: Phase10Player, card: Card, group_idx: int) -> None:
        """Apply a hit and announce it."""
        group = self.table_groups[group_idx]
        locale = self._player_locale(p)
        group.cards.append(card)
        p.hand.remove(card)
        owner = self.get_player_by_id(group.owner_id)
        owner_name = owner.name if owner else "?"
        self.play_sound(random.choice(SOUND_DISCARD))
        self.broadcast_personal_l(p, "phase10-hit-success", "phase10-player-hits",
                                   target=owner_name,
                                   card=p10_card_name(card, locale))

        self.hit_active = False
        self.hit_card_id = None
        self.hit_wild_group_idx = None
        self.discard_pending_card_id = None

        if len(p.hand) == 0:
            self._end_round(p)
            return

        self.rebuild_player_menu(p, position=1)
        for other in self.players:
            if other.id != p.id:
                self.rebuild_player_menu(other)

    def _action_place_wild(self, player: Player, action_id: str) -> None:
        """Place a wild on the low or high end of a run."""
        p = self._require_current_player(player)
        if not p or self.hit_wild_group_idx is None or self.hit_card_id is None:
            return
        card = next((c for c in p.hand if c.id == self.hit_card_id), None)
        if not card:
            self.hit_wild_group_idx = None
            self.hit_card_id = None
            return
        self._apply_hit(p, card, self.hit_wild_group_idx)

    def _action_cancel_hit(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p:
            return
        self.hit_active = False
        self.hit_card_id = None
        self.hit_wild_group_idx = None
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-hit-cancelled", buffer="table")
        self.rebuild_player_menu(p, position=1)

    # =========================================================================
    # Discard (Delete key)
    # =========================================================================

    def _action_do_discard(self, player: Player, action_id: str) -> None:
        """Discard the pending card, or the currently focused hand card if none is pending."""
        p = self._require_current_player(player)
        if not p:
            return
        if not self.turn_has_drawn:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-must-draw-first")
            return
        card = None
        if self.discard_pending_card_id is not None:
            card = next((c for c in p.hand if c.id == self.discard_pending_card_id), None)
            self.discard_pending_card_id = None
        else:
            # Fall back to whichever card is focused in the menu right now.
            context = self.get_action_context(player)
            mid = context.menu_item_id if context else None
            if mid and mid.startswith("card_"):
                try:
                    idx = int(mid.split("_", 1)[1]) - 1
                    sorted_hand = self._sorted_hand_for_menu(p)
                    if 0 <= idx < len(sorted_hand):
                        card = sorted_hand[idx]
                except (ValueError, IndexError):
                    pass
        if card is None:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-no-card-selected")
            return
        # Cancel any in-progress hit mode so the discard goes through cleanly.
        self.hit_active = False
        self.hit_card_id = None
        self.hit_wild_group_idx = None
        if is_skip(card):
            self._start_skip_discard(p, card)
        else:
            self._do_discard(p, card)

    # =========================================================================
    # Discard
    # =========================================================================

    def _do_discard(self, p: Phase10Player, card: Card) -> None:
        """Discard a non-Skip card and end the turn."""
        p.hand.remove(card)
        self.discard_pile.append(card)
        locale = self._player_locale(p)
        self.play_sound(random.choice(SOUND_DISCARD))
        self.broadcast_personal_l(p, "phase10-you-discard", "phase10-player-discards",
                                   card=p10_card_name(card, locale))

        if len(p.hand) == 0:
            self._end_round(p)
            return

        self._advance_turn()

    # =========================================================================
    # Skip discard
    # =========================================================================

    def _start_skip_discard(self, p: Phase10Player, card: Card) -> None:
        # If all other players have already been skipped this hand, the skip
        # card cannot be used — discard it normally instead of entering the
        # target-selection flow (which would loop forever for bots).
        eligible = [
            other for other in self._active_players()
            if other.id != p.id and other.id not in self.skip_targets_this_round
        ]
        if not eligible:
            self._do_discard(p, card)
            return

        self.skip_discard_active = True
        self.skip_pending_card_id = card.id
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-skip-choose-target", buffer="table")
        self.rebuild_player_menu(p, position=1)

    def _action_select_skip_target(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.skip_discard_active:
            return

        target_id = action_id.split("_", 2)[-1]  # "skip_target_{player_id}"
        target = self._get_p10_player(self.get_player_by_id(target_id))
        if not target or target.id == p.id:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-skip-self")
            return

        if target.id in self.skip_targets_this_round:
            user = self.get_user(p)
            if user:
                user.speak_l("phase10-skip-already-used", player=target.name)
            return

        # Retrieve the skip card
        skip_card = next((c for c in p.hand if c.id == self.skip_pending_card_id), None)
        if not skip_card:
            self.skip_discard_active = False
            self.skip_pending_card_id = None
            return

        # Apply
        target.skipped = True
        self.skip_targets_this_round.append(target.id)
        p.hand.remove(skip_card)
        self.discard_pile.append(skip_card)

        locale = self._player_locale(p)
        self.play_sound(random.choice(SOUND_DISCARD))
        self.broadcast_personal_l(p, "phase10-skip-played", "phase10-player-skips",
                                   target=target.name)

        # Inform the target
        target_user = self.get_user(target)
        if target_user:
            target_user.speak_l("phase10-you-are-skipped", skipping_player=p.name, buffer="table")

        self.skip_discard_active = False
        self.skip_pending_card_id = None

        if len(p.hand) == 0:
            self._end_round(p)
            return

        self._advance_turn()

    def _action_cancel_skip(self, player: Player, action_id: str) -> None:
        p = self._require_current_player(player)
        if not p or not self.skip_discard_active:
            return
        self.skip_discard_active = False
        self.skip_pending_card_id = None
        user = self.get_user(p)
        if user:
            user.speak_l("phase10-skip-cancelled", buffer="table")
        self.rebuild_player_menu(p, position=1)

    # =========================================================================
    # Info / status actions
    # =========================================================================

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        self._suppress_keybind_rebuild(player)
        super()._action_whose_turn(player, action_id)

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        p = self._get_p10_player(player)
        if not p or p.is_spectator:
            return
        user = self.get_user(p)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        locale = user.locale
        cards_str = p10_cards_name(sorted(p.hand, key=lambda c: (c.rank, c.suit)), locale)
        user.speak_l("phase10-hand-contents", count=len(p.hand), cards=cards_str)

    def _action_read_discard(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        locale = user.locale
        if not self.discard_pile:
            user.speak_l("phase10-no-discard")
        else:
            card_name = p10_card_name(self.discard_pile[-1], locale)
            user.speak_l("phase10-top-discard", card=card_name)

    def _action_read_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        locale = user.locale
        if not self.table_groups:
            user.speak_l("phase10-no-table-groups")
            return
        lines: list[str] = [Localization.get(locale, "phase10-table-group-header")]
        for group in self.table_groups:
            owner = self.get_player_by_id(group.owner_id)
            owner_name = owner.name if owner else "?"
            cards_str = self._format_group_summary(group.cards, group.requirement, locale)
            lines.append(Localization.get(
                locale, "phase10-table-group-entry",
                owner=owner_name,
                cards=cards_str,
            ))
        self.status_box(player, lines)

    def _action_check_phase(self, player: Player, action_id: str) -> None:
        p = self._get_p10_player(player)
        if not p or p.is_spectator:
            return
        user = self.get_user(p)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        locale = user.locale
        if p.phase_laid_down:
            user.speak_l("phase10-your-phase-laid-down", phase=p.current_phase)
        else:
            desc = phase_description(p.current_phase, locale)
            user.speak_l("phase10-your-phase", phase=p.current_phase, description=desc)

    def _action_read_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        locale = user.locale
        lines: list[str] = []
        for p in self._active_players():
            lines.append(Localization.get(locale, "phase10-player-hand-count",
                                           player=p.name, count=len(p.hand)))
        lines.append(Localization.get(locale, "phase10-deck-count", count=len(self.deck.cards)))
        self.status_box(player, lines)

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self._suppress_keybind_rebuild(player)
        remaining = self.timer.seconds_remaining()
        if remaining > 0:
            user.speak_l("poker-timer-remaining", seconds=remaining)
        else:
            user.speak_l("poker-timer-unlimited")

    def _action_sort_by_color(self, player: Player, action_id: str) -> None:
        p = self._get_p10_player(player)
        user = self.get_user(player)
        if not p or not user:
            return
        p.hand_sort = "color"
        user.speak_l("phase10-sorted-by-color")
        self.rebuild_player_menu(player)

    def _action_sort_by_number(self, player: Player, action_id: str) -> None:
        p = self._get_p10_player(player)
        user = self.get_user(player)
        if not p or not user:
            return
        if p.hand_sort == "number_asc":
            p.hand_sort = "number_desc"
            user.speak_l("phase10-sorted-by-number-desc")
        else:
            p.hand_sort = "number_asc"
            user.speak_l("phase10-sorted-by-number-asc")
        self.rebuild_player_menu(player)

    # =========================================================================
    # Score display overrides
    # =========================================================================

    def _build_score_lines(self, locale: str) -> list[str]:
        lines = [Localization.get(locale, "phase10-score-header")]
        for p in sorted(self._active_players(), key=lambda x: x.score):
            lines.append(Localization.get(
                locale, "phase10-score-entry",
                player=p.name, phase=p.current_phase, score=p.score,
            ))
        return lines

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak("; ".join(self._build_score_lines(user.locale)))

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        self.status_box(player, self._build_score_lines(user.locale))

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        return self._is_playing_hidden(player)

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_hidden(self, player: Player) -> Visibility:
        return self._is_playing_hidden(player)

    # =========================================================================
    # Timer
    # =========================================================================

    def _timer_seconds(self) -> int:
        try:
            return int(self.options.turn_timer)
        except ValueError:
            return 0

    def _start_turn_timer(self) -> None:
        seconds = self._timer_seconds()
        if seconds <= 0:
            self.timer.clear()
            return
        self.timer.start(seconds)
        self._timer_warning_played = False

    def _maybe_play_timer_warning(self) -> None:
        if self._timer_seconds() < 20 or self._timer_warning_played:
            return
        if self.timer.seconds_remaining() == 5:
            self._timer_warning_played = True
            self.play_sound("game_crazyeights/fivesec.ogg")

    def _handle_turn_timeout(self) -> None:
        player = self.current_player
        p = self._get_p10_player(player) if player else None
        if not p:
            return
        action_id = bot_think(self, p)
        if action_id:
            self.execute_action(p, action_id)

    # =========================================================================
    # Phase helper
    # =========================================================================

    def _current_phase_reqs(self, p: Phase10Player) -> list[PhaseRequirement]:
        """Return the requirement list for the player's current phase."""
        idx = p.current_phase - 1
        if 0 <= idx < len(PHASES):
            return PHASES[idx]
        return []
