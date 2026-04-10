"""
LastCard — An Uno-style card game for PlayPalace v11.

Players take turns matching the top card by color or number.
Special cards (Skip, Reverse, Draw Two, Wild, Wild Draw Four) add strategic depth.
House rules include stacking, jump-in, Seven-O hand swaps, and a buzzer callout.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.cards import Card, Deck, DeckFactory, card_name
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, BoolOption, MenuOption, option_field
from ...game_utils.bot_helper import BotHelper
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState
from server.core.users.bot import Bot
from server.core.users.base import User
from .bot import bot_think, bot_react
from ...game_utils.turn_timer_mixin import TurnTimerMixin

# ============================================================================
# Constants
# ============================================================================

# LastCard uses a custom deck: 4 colors × (0-9, 1-9, Skip, Reverse, Draw Two) + 4 Wild + 4 Wild Draw Four = 108 cards
# We encode colors as suits: 1=Red, 2=Blue, 3=Green, 4=Yellow, 0=Wild (no color)
COLOR_RED = 1
COLOR_BLUE = 2
COLOR_GREEN = 3
COLOR_YELLOW = 4
COLOR_WILD = 0
COLOR_NAMES = {COLOR_RED: "Red", COLOR_BLUE: "Blue", COLOR_GREEN: "Green", COLOR_YELLOW: "Yellow"}

# Ranks: 0-9 are number cards, 10=Skip, 11=Reverse, 12=Draw Two, 13=Wild, 14=Wild Draw Four
RANK_SKIP = 10
RANK_REVERSE = 11
RANK_DRAW_TWO = 12
RANK_WILD = 13
RANK_WILD_DRAW_FOUR = 14

TURN_TIMER_CHOICES = ["5", "10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "5": "lastcard-timer-5",
    "10": "lastcard-timer-10",
    "15": "lastcard-timer-15",
    "20": "lastcard-timer-20",
    "30": "lastcard-timer-30",
    "45": "lastcard-timer-45",
    "60": "lastcard-timer-60",
    "90": "lastcard-timer-90",
    "0": "lastcard-timer-unlimited",
}

STACKING_CHOICES = ["off", "standard", "progressive"]
STACKING_LABELS = {
    "off": "lastcard-stacking-off",
    "standard": "lastcard-stacking-standard",
    "progressive": "lastcard-stacking-progressive",
}

SKIP_CARD_CHOICES = ["next", "all"]
SKIP_CARD_LABELS = {
    "next": "lastcard-skip-next",
    "all": "lastcard-skip-all",
}

REVERSE_2P_CHOICES = ["reverse", "skip"]
REVERSE_2P_LABELS = {
    "reverse": "lastcard-reverse-2p-reverse",
    "skip": "lastcard-reverse-2p-skip",
}

ZERO_RULE_CHOICES = ["none", "rotate_hands"]
ZERO_RULE_LABELS = {
    "none": "lastcard-zero-none",
    "rotate_hands": "lastcard-zero-rotate",
}

SEVEN_RULE_CHOICES = ["none", "swap_hand"]
SEVEN_RULE_LABELS = {
    "none": "lastcard-seven-none",
    "swap_hand": "lastcard-seven-swap",
}

SCORING_CHOICES = ["classic", "negative"]
SCORING_LABELS = {
    "classic": "lastcard-scoring-classic",
    "negative": "lastcard-scoring-negative",
}

# Sounds — all reused from existing assets
SOUND_DRAW = [
    "game_cards/draw1.ogg",
    "game_cards/draw2.ogg",
    "game_cards/draw3.ogg",
    "game_cards/draw4.ogg",
]
SOUND_PLAY = [
    "game_cards/play1.ogg",
    "game_cards/play2.ogg",
    "game_cards/play3.ogg",
    "game_cards/play4.ogg",
]
SOUND_SHUFFLE = ["game_cards/shuffle1.ogg", "game_cards/shuffle2.ogg", "game_cards/shuffle3.ogg"]
SOUND_RESHUFFLE = "game_cards/small_shuffle.ogg"
SOUND_MUSIC = "game_uno/music.ogg"
SOUND_BUZZER_PRESS = "game_uno/buzzerpress.ogg"
SOUND_BUZZER_CAUGHT = "game_uno/buzzerplay.ogg"
SOUND_UNO_CALL = "game_uno/uno.ogg"
SOUND_WILD = "game_uno/wild.ogg"
SOUND_WILD_DRAW_FOUR = "game_uno/wild4.ogg"
SOUND_SKIP = "game_uno/skip.ogg"
SOUND_REVERSE = "game_uno/reverse.ogg"
SOUND_HAND_CHANGE = "game_uno/handchange.ogg"
SOUND_INTERCEPT = [
    "game_uno/intercept1.ogg",
    "game_uno/intercept2.ogg",
    "game_uno/intercept3.ogg",
    "game_uno/intercept4.ogg",
]
SOUND_PLAYABLE = "game_uno/playable.ogg"
SOUND_WIN_ROUND = "game_uno/winround.ogg"
SOUND_WIN_GAME = "game_uno/wingame.ogg"
SOUND_LOSE_ROUND = "game_uno/loseround.ogg"
SOUND_CHALLENGE = "game_coup/challenge.ogg"
SOUND_CHALLENGE_SUCCESS = "game_coup/challengesuccess.ogg"
SOUND_CHALLENGE_FAIL = "game_coup/challengefail.ogg"
SOUND_PASS = "game_crazyeights/pass.ogg"
SOUND_EXPIRED = "game_crazyeights/expired.ogg"
SOUND_NEW_HAND = "game_crazyeights/newhand.ogg"
SOUND_COLOR_CHANGE = "game_crazyeights/morf.ogg"
SOUND_YOUR_TURN = "turn.ogg"
SOUND_FORCE_PLAY = "game_crazyeights/drawPlayable.ogg"
SOUND_PENALTY_DRAW = "game_farkle/farkle.ogg"

COLOR_SORT_ORDER = {COLOR_RED: 0, COLOR_BLUE: 1, COLOR_GREEN: 2, COLOR_YELLOW: 3, COLOR_WILD: 4}

# Point values for scoring
CARD_POINTS = {
    RANK_SKIP: 20,
    RANK_REVERSE: 20,
    RANK_DRAW_TWO: 20,
    RANK_WILD: 50,
    RANK_WILD_DRAW_FOUR: 50,
}


# ============================================================================
# Deck builder
# ============================================================================


def build_lastcard_deck() -> Deck:
    """Build a 108-card LastCard deck."""
    cards: list[Card] = []
    card_id = 0
    for color in (COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW):
        # One 0 per color
        cards.append(Card(id=card_id, rank=0, suit=color))
        card_id += 1
        # Two each of 1-9, Skip, Reverse, Draw Two
        for rank in list(range(1, 10)) + [RANK_SKIP, RANK_REVERSE, RANK_DRAW_TWO]:
            for _ in range(2):
                cards.append(Card(id=card_id, rank=rank, suit=color))
                card_id += 1

    # 4 Wild and 4 Wild Draw Four
    for _ in range(4):
        cards.append(Card(id=card_id, rank=RANK_WILD, suit=COLOR_WILD))
        card_id += 1
    for _ in range(4):
        cards.append(Card(id=card_id, rank=RANK_WILD_DRAW_FOUR, suit=COLOR_WILD))
        card_id += 1

    deck = Deck(cards=cards)
    deck.shuffle()
    return deck


# ============================================================================
# Options
# ============================================================================


@dataclass
class LastCardOptions(GameOptions):
    """Options for LastCard."""

    # Core
    winning_score: int = option_field(
        IntOption(
            default=500,
            min_val=50,
            max_val=10000,
            value_key="score",
            label="lastcard-set-winning-score",
            prompt="lastcard-enter-winning-score",
            change_msg="lastcard-option-changed-winning-score",
            description="lastcard-desc-winning-score",
        )
    )
    hand_size: int = option_field(
        IntOption(
            default=7,
            min_val=3,
            max_val=15,
            value_key="count",
            label="lastcard-set-hand-size",
            prompt="lastcard-enter-hand-size",
            change_msg="lastcard-option-changed-hand-size",
            description="lastcard-desc-hand-size",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            default="0",
            label="lastcard-set-turn-timer",
            prompt="lastcard-select-turn-timer",
            change_msg="lastcard-option-changed-turn-timer",
            choice_labels=TURN_TIMER_LABELS,
            description="lastcard-desc-turn-timer",
        )
    )

    # Draw rules
    draw_until_playable: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="lastcard-set-draw-until-playable",
            change_msg="lastcard-option-changed-draw-until-playable",
            description="lastcard-desc-draw-until-playable",
        )
    )
    draw_limit: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=20,
            value_key="count",
            label="lastcard-set-draw-limit",
            prompt="lastcard-enter-draw-limit",
            change_msg="lastcard-option-changed-draw-limit",
            description="lastcard-desc-draw-limit",
        )
    )

    # Stacking
    stacking: str = option_field(
        MenuOption(
            choices=STACKING_CHOICES,
            default="off",
            label="lastcard-set-stacking",
            prompt="lastcard-select-stacking",
            change_msg="lastcard-option-changed-stacking",
            choice_labels=STACKING_LABELS,
            description="lastcard-desc-stacking",
        )
    )

    # Special card rules
    skip_card_rule: str = option_field(
        MenuOption(
            choices=SKIP_CARD_CHOICES,
            default="next",
            label="lastcard-set-skip-rule",
            prompt="lastcard-select-skip-rule",
            change_msg="lastcard-option-changed-skip-rule",
            choice_labels=SKIP_CARD_LABELS,
            description="lastcard-desc-skip-card-rule",
        )
    )
    reverse_two_players: str = option_field(
        MenuOption(
            choices=REVERSE_2P_CHOICES,
            default="skip",
            label="lastcard-set-reverse-2p",
            prompt="lastcard-select-reverse-2p",
            change_msg="lastcard-option-changed-reverse-2p",
            choice_labels=REVERSE_2P_LABELS,
            description="lastcard-desc-reverse-two-players",
        )
    )
    zero_card_rule: str = option_field(
        MenuOption(
            choices=ZERO_RULE_CHOICES,
            default="none",
            label="lastcard-set-zero-rule",
            prompt="lastcard-select-zero-rule",
            change_msg="lastcard-option-changed-zero-rule",
            choice_labels=ZERO_RULE_LABELS,
            description="lastcard-desc-zero-card-rule",
        )
    )
    seven_card_rule: str = option_field(
        MenuOption(
            choices=SEVEN_RULE_CHOICES,
            default="none",
            label="lastcard-set-seven-rule",
            prompt="lastcard-select-seven-rule",
            change_msg="lastcard-option-changed-seven-rule",
            choice_labels=SEVEN_RULE_LABELS,
            description="lastcard-desc-seven-card-rule",
        )
    )

    # Gameplay variants
    jump_in: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="lastcard-set-jump-in",
            change_msg="lastcard-option-changed-jump-in",
            description="lastcard-desc-jump-in",
        )
    )
    force_play: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="lastcard-set-force-play",
            change_msg="lastcard-option-changed-force-play",
            description="lastcard-desc-force-play",
        )
    )
    last_card_callout: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lastcard-set-callout",
            change_msg="lastcard-option-changed-callout",
            description="lastcard-desc-last-card-callout",
        )
    )
    challenge_wild_draw_four: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lastcard-set-challenge-wd4",
            change_msg="lastcard-option-changed-challenge-wd4",
            description="lastcard-desc-challenge-wild-draw-four",
        )
    )
    allow_multiple_play: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="lastcard-set-multiple-play",
            change_msg="lastcard-option-changed-multiple-play",
            description="lastcard-desc-allow-multiple-play",
        )
    )

    # Scoring
    scoring_mode: str = option_field(
        MenuOption(
            choices=SCORING_CHOICES,
            default="classic",
            label="lastcard-set-scoring",
            prompt="lastcard-select-scoring",
            change_msg="lastcard-option-changed-scoring",
            choice_labels=SCORING_LABELS,
            description="lastcard-desc-scoring-mode",
        )
    )

    # Buzzer & timer
    buzzer_enabled: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="lastcard-set-buzzer",
            change_msg="lastcard-option-changed-buzzer",
            description="lastcard-desc-buzzer-enabled",
        )
    )
    interrupt_timer: int = option_field(
        IntOption(
            default=4,
            min_val=2,
            max_val=7,
            value_key="seconds",
            label="lastcard-set-interrupt-timer",
            prompt="lastcard-enter-interrupt-timer",
            change_msg="lastcard-option-changed-interrupt-timer",
            description="lastcard-desc-interrupt-timer",
        )
    )

    # Safety
    max_hand_size: int = option_field(
        IntOption(
            default=0,
            min_val=0,
            max_val=50,
            value_key="count",
            label="lastcard-set-max-hand",
            prompt="lastcard-enter-max-hand",
            change_msg="lastcard-option-changed-max-hand",
            description="lastcard-desc-max-hand-size",
        )
    )


# ============================================================================
# Player
# ============================================================================

HAND_SORT_MODES = ["color", "rank", "none"]
HAND_SORT_LABELS = {
    "color": "lastcard-sort-by-color",
    "rank": "lastcard-sort-by-rank",
    "none": "lastcard-sort-none",
}


@dataclass
class LastCardPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    score: int = 0
    called_last_card: bool = False
    draws_this_turn: int = 0
    hand_sort: str = "color"  # "color", "rank", "none"
    selected_cards: set[int] = field(default_factory=set)  # Card IDs selected for multi-play


# ============================================================================
# Game
# ============================================================================


@register_game
@dataclass
class LastCardGame(Game, TurnTimerMixin):
    """LastCard game implementation."""

    players: list[LastCardPlayer] = field(default_factory=list)
    options: LastCardOptions = field(default_factory=LastCardOptions)

    # Deck state
    deck: Deck = field(default_factory=Deck)
    discard_pile: list[Card] = field(default_factory=list)
    current_color: int = 0  # The active color (may differ from top card if Wild played)

    # Turn state
    turn_has_drawn: bool = False
    dealer_index: int = -1

    # Wild color selection
    awaiting_color_choice: bool = False
    color_wait_ticks: int = 0

    # Stacking state
    pending_draw_count: int = 0  # Accumulated +2/+4 cards to draw
    pending_draw_is_plus_four: bool = False  # True if the pending stack includes +4

    # Interrupt timer (Coup-style) for buzzer/challenge/jump-in
    interrupt_phase: str = ""  # "", "last_card_callout", "challenge_wd4", "jump_in_window"
    interrupt_timer_ticks: int = 0
    interrupt_target_id: str = ""  # Player being challenged / who played last card
    interrupt_wd4_player_id: str = ""  # Player who played Wild Draw Four
    interrupt_wd4_had_matching: bool = False  # Whether WD4 player had matching color

    # Seven-O swap state
    awaiting_swap_target: bool = False
    swap_player_id: str = ""

    # Wait ticks
    intro_wait_ticks: int = 0
    hand_wait_ticks: int = 0

    # Event queue for deferred actions
    event_queue: list[tuple[int, str, dict]] = field(default_factory=list)

    # Timer
    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)

    # Jump-in tracking
    jump_in_played: bool = False  # Set when a jump-in occurs to cancel normal turn advance

    # Deadlock detection
    consecutive_passes: int = 0  # Resets whenever a card is played or drawn

    def __post_init__(self):
        super().__post_init__()
        self._timer_warning_played = False

    # ==========================================================================
    # Metadata
    # ==========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "Last Card"

    @classmethod
    def get_type(cls) -> str:
        return "lastcard"

    @classmethod
    def get_category(cls) -> str:
        return "category-playaural"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> LastCardPlayer:
        return LastCardPlayer(id=player_id, name=name, is_bot=is_bot)

    def broadcast_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        if name in ("join.ogg", "leave.ogg", "join_spectator.ogg", "leave_spectator.ogg"):
            return
        super().broadcast_sound(name, volume, pan, pitch)

    def add_player(self, name: str, user: User) -> LastCardPlayer:
        player = super().add_player(name, user)
        self.play_sound("join.ogg")
        return player

    def add_spectator(self, name: str, user: User) -> Player:
        player = super().add_spectator(name, user)
        super().broadcast_sound("join_spectator.ogg")
        return player

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: LastCardPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        # Draw action
        action_set.add(
            Action(
                id="draw",
                label=Localization.get(locale, "lastcard-draw"),
                handler="_action_draw",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                show_in_actions_menu=False,
            )
        )

        # Pass action
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "lastcard-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
                show_in_actions_menu=False,
            )
        )

        # Color selection actions
        for color_id, color_key in [
            ("red", "lastcard-color-red"),
            ("blue", "lastcard-color-blue"),
            ("green", "lastcard-color-green"),
            ("yellow", "lastcard-color-yellow"),
        ]:
            action_set.add(
                Action(
                    id=f"color_{color_id}",
                    label=Localization.get(locale, color_key),
                    handler="_action_choose_color",
                    is_enabled="_is_color_choice_enabled",
                    is_hidden="_is_color_choice_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Buzzer action (always accessible during play, handled via interrupt)
        action_set.add(
            Action(
                id="buzzer",
                label=Localization.get(locale, "lastcard-buzzer"),
                handler="_action_buzzer",
                is_enabled="_is_buzzer_enabled",
                is_hidden="_is_buzzer_hidden",
                show_in_actions_menu=False,
            )
        )

        # Challenge WD4 action
        action_set.add(
            Action(
                id="challenge_wd4",
                label=Localization.get(locale, "lastcard-challenge"),
                handler="_action_challenge_wd4",
                is_enabled="_is_challenge_enabled",
                is_hidden="_is_challenge_hidden",
                show_in_actions_menu=False,
            )
        )

        # Accept draw (decline challenge)
        action_set.add(
            Action(
                id="accept_draw",
                label=Localization.get(locale, "lastcard-accept-draw"),
                handler="_action_accept_draw",
                is_enabled="_is_accept_draw_enabled",
                is_hidden="_is_accept_draw_hidden",
                show_in_actions_menu=False,
            )
        )

        # Jump-in action
        action_set.add(
            Action(
                id="jump_in",
                label=Localization.get(locale, "lastcard-jump-in"),
                handler="_action_jump_in",
                is_enabled="_is_jump_in_enabled",
                is_hidden="_is_jump_in_hidden",
                show_in_actions_menu=False,
            )
        )

        # Seven swap target selection
        for i in range(10):  # Max 10 players
            action_set.add(
                Action(
                    id=f"swap_target_{i}",
                    label="",
                    handler="_action_swap_target",
                    is_enabled="_is_swap_target_enabled",
                    is_hidden="_is_swap_target_hidden",
                    get_label="_get_swap_target_label",
                    show_in_actions_menu=False,
                )
            )

        # Sort hand (web-only, visible in turn menu for mobile users)
        action_set.add(
            Action(
                id="cycle_hand_sort_turn",
                label=Localization.get(locale, "lastcard-cycle-sort"),
                handler="_action_cycle_hand_sort",
                is_enabled="_is_check_enabled",
                is_hidden="_is_sort_turn_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "lastcard-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_top",
                label=Localization.get(locale, "lastcard-read-top"),
                handler="_action_read_top",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_counts",
                label=Localization.get(locale, "lastcard-read-counts"),
                handler="_action_read_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "lastcard-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_draw_penalty",
                label=Localization.get(locale, "lastcard-read-draw-penalty"),
                handler="_action_read_draw_penalty",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="cycle_hand_sort",
                label=Localization.get(locale, "lastcard-cycle-sort"),
                handler="_action_cycle_hand_sort",
                is_enabled="_is_check_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "read_top",
                "read_counts",
                "read_draw_penalty",
                "check_scores",
                "check_turn_timer",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        # Card play / draw / pass
        self.define_keybind("space", "Draw", ["draw"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Pass", ["pass"], state=KeybindState.ACTIVE)

        # Color selection
        self.define_keybind("1", "Red", ["color_red"], state=KeybindState.ACTIVE)
        self.define_keybind("2", "Blue", ["color_blue"], state=KeybindState.ACTIVE)
        self.define_keybind("3", "Green", ["color_green"], state=KeybindState.ACTIVE)
        self.define_keybind("4", "Yellow", ["color_yellow"], state=KeybindState.ACTIVE)

        # Buzzer
        self.define_keybind("b", "Buzzer", ["buzzer"], state=KeybindState.ACTIVE)

        # Challenge / Accept
        self.define_keybind("c", "Challenge", ["challenge_wd4"], state=KeybindState.ACTIVE)
        self.define_keybind("a", "Accept Draw", ["accept_draw"], state=KeybindState.ACTIVE)

        # Jump-in
        self.define_keybind("j", "Jump In", ["jump_in"], state=KeybindState.ACTIVE)

        # Confirm multi-play
        self.define_keybind("x", "Confirm play", ["play_selected"], state=KeybindState.ACTIVE)

        # Information
        self.define_keybind("w", "Read hand", ["read_hand"])
        self.define_keybind("r", "Read top card", ["read_top"], include_spectators=True)
        self.define_keybind("e", "Read counts", ["read_counts"], include_spectators=True)
        self.define_keybind("shift+t", "Turn timer", ["check_turn_timer"], include_spectators=True)
        self.define_keybind("d", "Draw penalty", ["read_draw_penalty"], include_spectators=True)
        self.define_keybind("o", "Cycle hand sort", ["cycle_hand_sort"])

    # ==========================================================================
    # Menu syncing
    # ==========================================================================

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_turn_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
        super().rebuild_all_menus()

    def _sync_turn_actions(self, player: Player) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return
        turn_set.remove_by_prefix("play_card_")
        turn_set.remove_by_prefix("toggle_card_")
        turn_set.remove("play_selected")
        turn_set.remove("draw")
        turn_set.remove("pass")

        if self.status != "playing" or player.is_spectator:
            return
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return

        multi = self.options.allow_multiple_play
        ordered_cards = self._sort_hand(player)

        if multi:
            # Toggle-and-confirm mode: cards are toggleable, play_selected confirms
            for card in ordered_cards:
                turn_set.add(
                    Action(
                        id=f"toggle_card_{card.id}",
                        label="",
                        handler="_action_toggle_card",
                        is_enabled="_is_toggle_card_enabled",
                        is_hidden="_is_toggle_card_hidden",
                        get_label="_get_toggle_card_label",
                        show_in_actions_menu=False,
                    )
                )
            if self.current_player == player:
                locale = self._player_locale(player)
                turn_set.add(
                    Action(
                        id="play_selected",
                        label="",
                        handler="_action_play_selected",
                        is_enabled="_is_play_selected_enabled",
                        is_hidden="_is_play_selected_hidden",
                        get_label="_get_play_selected_label",
                        show_in_actions_menu=False,
                    )
                )
        else:
            # Direct play mode: clicking a card plays it immediately
            for card in ordered_cards:
                turn_set.add(
                    Action(
                        id=f"play_card_{card.id}",
                        label="",
                        handler="_action_play_card",
                        is_enabled="_is_play_card_enabled",
                        is_hidden="_is_play_card_hidden",
                        get_label="_get_card_label",
                        show_in_actions_menu=False,
                    )
                )

        if self.current_player == player:
            locale = self._player_locale(player)
            turn_set.add(
                Action(
                    id="draw",
                    label=Localization.get(locale, "lastcard-draw"),
                    handler="_action_draw",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=False,
                )
            )
            turn_set.add(
                Action(
                    id="pass",
                    label=Localization.get(locale, "lastcard-pass"),
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    show_in_actions_menu=False,
                )
            )

        # Web-specific turn menu reordering:
        # [Reaction: buzzer, jump_in] → [Context: colors, challenge, accept,
        #  swap targets] → [Cards + confirm] → [Draw, Pass] → [Sort]
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            top = ["buzzer", "jump_in"]
            bottom = ["draw", "pass", "cycle_hand_sort_turn"]
            card_ids = [
                aid for aid in turn_set._order if aid.startswith(("play_card_", "toggle_card_"))
            ]
            card_group = card_ids + (
                ["play_selected"] if "play_selected" in turn_set._order else []
            )
            pinned = set(top) | set(bottom) | set(card_group)
            middle = [aid for aid in turn_set._order if aid not in pinned]
            turn_set._order = (
                [aid for aid in top if aid in turn_set._order]
                + middle
                + card_group
                + [aid for aid in bottom if aid in turn_set._order]
            )

    # ==========================================================================
    # Validation
    # ==========================================================================

    def prestart_validate(self) -> list[str | tuple[str, dict]]:
        errors = super().prestart_validate()
        active = [p for p in self.players if not p.is_spectator]
        total_cards_needed = self.options.hand_size * len(active) + 1  # +1 for start card
        if total_cards_needed > 108:
            errors.append(
                (
                    "lastcard-error-too-many-cards",
                    {"players": len(active), "hand_size": self.options.hand_size},
                )
            )
        max_hand = self.options.max_hand_size
        if max_hand > 0 and self.options.hand_size > max_hand:
            errors.append(
                (
                    "lastcard-error-hand-exceeds-max",
                    {"hand_size": self.options.hand_size, "max_hand": max_hand},
                )
            )
        return errors

    # ==========================================================================
    # Game flow
    # ==========================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        self._sync_table_status()
        self.play_music(SOUND_MUSIC)

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self.players])
        self._sync_team_scores()

        self.intro_wait_ticks = 3 * 20
        self.play_sound(random.choice(SOUND_SHUFFLE))

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return

        # Wait ticks
        if self.color_wait_ticks > 0:
            self.color_wait_ticks -= 1
            if self.color_wait_ticks == 0:
                self._post_play_advance()
            return
        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return
        if self.intro_wait_ticks > 0:
            self.intro_wait_ticks -= 1
            if self.intro_wait_ticks == 0:
                self._start_new_hand()
            return

        # Process event queue
        self._process_events()

        # Interrupt timer (for buzzer/challenge/jump-in)
        if self.interrupt_timer_ticks > 0:
            self.interrupt_timer_ticks -= 1
            if self.interrupt_timer_ticks == 0:
                self._resolve_interrupt()
            # Process bot reactions during interrupt
            self._process_bot_reactions()
            return

        # Turn timer
        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def _start_new_hand(self) -> None:
        self.round += 1
        self.turn_direction = 1
        self.turn_skip_count = 0
        self.awaiting_color_choice = False
        self.color_wait_ticks = 0
        self.turn_has_drawn = False
        self.pending_draw_count = 0
        self.pending_draw_is_plus_four = False
        self.interrupt_phase = ""
        self.interrupt_timer_ticks = 0
        self.awaiting_swap_target = False
        self.consecutive_passes = 0
        self.jump_in_played = False

        self.broadcast_l("lastcard-new-hand", round=self.round)
        self.play_sound(SOUND_NEW_HAND)

        # Build deck
        self.deck = build_lastcard_deck()
        self.discard_pile = []
        self.current_color = 0

        active_players = [p for p in self.players if not p.is_spectator]
        self.set_turn_players(active_players, reset_index=False)
        for p in active_players:
            p.hand = []
            p.called_last_card = False
            p.draws_this_turn = 0
            p.selected_cards.clear()

        # Deal cards
        hand_size = self.options.hand_size
        for _ in range(hand_size):
            for p in active_players:
                card = self.deck.draw_one()
                if card:
                    p.hand.append(card)

        # Rotate dealer
        if self.turn_player_ids:
            self.dealer_index = (self.dealer_index + 1) % len(self.turn_player_ids)
            self.turn_index = (self.dealer_index + 1) % len(self.turn_player_ids)
        else:
            self.dealer_index = -1
            self.turn_index = 0

        # First card (must be a number card)
        start_card = self._draw_start_card()
        if start_card:
            self.discard_pile.append(start_card)
            self.current_color = start_card.suit
            self._broadcast_start_card()
            self.broadcast_l("lastcard-dealt-cards", cards=hand_size)

        self._start_turn()

    def _draw_start_card(self) -> Card | None:
        """Draw a number card (0-9) to start the discard pile."""
        attempts = 0
        while attempts < 200:
            card = self.deck.draw_one()
            if not card:
                return None
            if card.rank <= 9 and card.suit != COLOR_WILD:
                return card
            self.deck.add([card])
            self.deck.shuffle()
            attempts += 1
        return self.deck.draw_one()

    def _start_turn(self) -> None:
        player = self.current_player
        if not isinstance(player, LastCardPlayer):
            return
        self.turn_has_drawn = False
        self.jump_in_played = False
        player.draws_this_turn = 0
        player.selected_cards.clear()

        # If there's a pending draw stack and player can't stack, force draw
        if self.pending_draw_count > 0 and not self._can_stack(player):
            self._force_draw_pending(player)
            return

        self.announce_turn()
        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 40))

        self.start_turn_timer()
        self._sync_turn_actions(player)
        self.rebuild_all_menus()

    def _advance_turn(self) -> None:
        self.advance_turn(announce=False)
        self._start_turn()

    def _on_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, LastCardPlayer):
            return
        self.play_sound(SOUND_EXPIRED)
        # Auto-play: draw if possible, else pass
        action_id = bot_think(self, player)
        if action_id:
            self.execute_action(player, action_id)

    def bot_think(self, player: LastCardPlayer) -> str | None:
        return bot_think(self, player)

    # ==========================================================================
    # Card play action
    # ==========================================================================

    def _action_play_card(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return
        if self.interrupt_phase:
            return

        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        card = next((c for c in p.hand if c.id == card_id), None)
        if not card:
            return
        if not self._is_card_playable(card, p):
            return

        self._do_play_card(p, card)

    # ==========================================================================
    # Multi-card play (toggle + confirm)
    # ==========================================================================

    def _action_toggle_card(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if player.is_spectator:
            return
        if self.current_player != player:
            return
        if self.awaiting_color_choice or self.awaiting_swap_target or self.interrupt_phase:
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return
        if not any(c.id == card_id for c in player.hand):
            return
        if card_id in player.selected_cards:
            player.selected_cards.remove(card_id)
        else:
            player.selected_cards.add(card_id)
        self.update_player_menu(player)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if self.awaiting_color_choice or self.awaiting_swap_target or self.interrupt_phase:
            return
        if not p.selected_cards:
            user = self.get_user(p)
            if user:
                user.speak_l("lastcard-multi-no-cards", buffer="table")
            return

        selected = [c for c in p.hand if c.id in p.selected_cards]
        if not selected:
            p.selected_cards.clear()
            return

        # Validate: all must have the same rank
        ranks = {c.rank for c in selected}
        if len(ranks) != 1:
            p.selected_cards.clear()
            user = self.get_user(p)
            if user:
                user.speak_l("lastcard-multi-same-rank", buffer="table")
            return
        rank = ranks.pop()

        # Wilds must be played one at a time (require color choice)
        if rank in (RANK_WILD, RANK_WILD_DRAW_FOUR) and len(selected) > 1:
            p.selected_cards.clear()
            user = self.get_user(p)
            if user:
                user.speak_l("lastcard-multi-no-wilds", buffer="table")
            return

        # At least one selected card must be playable (matching top card / active color)
        # Reorder so a playable card is first (it determines the "lead" for multi-play)
        playable_idx = None
        for i, card in enumerate(selected):
            if self._is_card_playable(card, p):
                playable_idx = i
                break
        if playable_idx is None:
            p.selected_cards.clear()
            user = self.get_user(p)
            if user:
                user.speak_l("lastcard-multi-not-playable", buffer="table")
            return
        if playable_idx > 0:
            selected.insert(0, selected.pop(playable_idx))

        # Single card: use normal play path
        if len(selected) == 1:
            p.selected_cards.clear()
            self._do_play_card(p, selected[0])
            return

        # Multi-card play
        self._do_play_multiple(p, selected)

    def _do_play_multiple(self, player: LastCardPlayer, cards: list[Card]) -> None:
        """Execute playing multiple cards of the same rank at once."""
        rank = cards[0].rank
        # Last card's color determines the new active color
        last_card = cards[-1]

        for card in cards:
            player.hand.remove(card)
            self.discard_pile.append(card)
        player.selected_cards.clear()
        self.turn_has_drawn = False
        player.draws_this_turn = 0
        player.called_last_card = False
        self.consecutive_passes = 0

        # Play sounds (staggered card sounds)
        for i, card in enumerate(cards):
            self.schedule_sound(random.choice(SOUND_PLAY), delay_ticks=i * 5)

        # Broadcast
        self._broadcast_multi_play(player, cards)

        # Set active color from last card
        self.current_color = last_card.suit

        # Check for win
        if len(player.hand) == 0:
            self._end_round(player)
            return

        # Last card callout
        if len(player.hand) == 1 and self.options.last_card_callout:
            self.play_sound(SOUND_UNO_CALL)
            self.interrupt_phase = "last_card_callout"
            self.interrupt_target_id = player.id
            self.interrupt_timer_ticks = self.options.interrupt_timer * 20
            self.interrupt_wd4_player_id = ""
            self.interrupt_wd4_had_matching = False
            BotHelper.jolt_bots(self, ticks=random.randint(10, 30))
            self.rebuild_all_menus()
            return

        # Apply stacked effects
        count = len(cards)

        if rank == RANK_SKIP:
            self.play_sound(SOUND_SKIP)
            if self.options.skip_card_rule == "all":
                # Skip all — current player plays again
                self._start_turn()
                return
            else:
                self.skip_next_players(count)

        elif rank == RANK_REVERSE:
            self.play_sound(SOUND_REVERSE)
            active_count = len(self.turn_player_ids)
            for _ in range(count):
                if active_count == 2 and self.options.reverse_two_players == "skip":
                    self.skip_next_players(1)
                else:
                    self.reverse_turn_direction()

        elif rank == RANK_DRAW_TWO:
            draw_total = 2 * count
            if self.options.stacking != "off":
                self.pending_draw_count += draw_total
                self.pending_draw_is_plus_four = False
            else:
                next_p = self._next_player()
                if next_p:
                    self._draw_for_player(next_p, draw_total)
                self.skip_next_players(1)
            # Stagger draw sounds
            for i in range(min(count, 3)):
                self.schedule_sound(random.choice(SOUND_DRAW), delay_ticks=count * 5 + i * 5)

        # Seven-O with multiple cards: apply once (swap/rotate applies to the last card)
        if rank == 7 and self.options.seven_card_rule == "swap_hand":
            cur = self.current_player
            if isinstance(cur, LastCardPlayer):
                active = [p for p in self.turn_players if not p.is_spectator and p.id != cur.id]
                if len(active) == 1:
                    self._do_swap_hands(cur, active[0])
                elif len(active) > 1:
                    self.awaiting_swap_target = True
                    self.swap_player_id = cur.id
                    if cur.is_bot:
                        BotHelper.jolt_bot(cur, ticks=random.randint(10, 20))
                    self.rebuild_all_menus()
                    return

        if rank == 0 and self.options.zero_card_rule == "rotate_hands":
            for _ in range(count):
                self._rotate_all_hands()

        # Jump-in window
        if self.options.jump_in and not self.jump_in_played:
            self.interrupt_phase = "jump_in_window"
            self.interrupt_timer_ticks = self.options.interrupt_timer * 20
            BotHelper.jolt_bots(self, ticks=random.randint(10, 30))
            self.rebuild_all_menus()
            return

        self._advance_turn()

    def _broadcast_multi_play(self, player: LastCardPlayer, cards: list[Card]) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            card_names = [self.format_card(c, user.locale) for c in cards]
            user.speak_l(
                "lastcard-player-plays-multi",
                buffer="table",
                player=player.name,
                count=len(cards),
                cards=", ".join(card_names),
            )

    def _do_play_card(self, player: LastCardPlayer, card: Card) -> None:
        """Execute playing a card (used by both normal play and jump-in)."""
        # Track whether player had matching color before playing WD4 (for challenge)
        had_matching_color = False
        if card.rank == RANK_WILD_DRAW_FOUR:
            had_matching_color = any(
                c.suit == self.current_color and c.id != card.id for c in player.hand
            )

        player.hand.remove(card)
        self.discard_pile.append(card)
        self.turn_has_drawn = False
        player.draws_this_turn = 0
        player.called_last_card = False
        self.consecutive_passes = 0

        self._play_card_sound(card)
        self._broadcast_play(player, card)

        # Handle wild cards — need color selection
        if card.rank in (RANK_WILD, RANK_WILD_DRAW_FOUR):
            if len(player.hand) == 0:
                # Player won with a wild — pick any color
                self.current_color = COLOR_RED
                self._check_last_card_and_advance(player, card, had_matching_color)
                return
            self.awaiting_color_choice = True
            self.interrupt_wd4_player_id = player.id
            self.interrupt_wd4_had_matching = had_matching_color
            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
            self.start_turn_timer()
            self.rebuild_all_menus()
            return

        # Non-wild card
        self.current_color = card.suit
        self._check_last_card_and_advance(player, card, had_matching_color)

    def _check_last_card_and_advance(
        self, player: LastCardPlayer, card: Card, had_matching_color: bool
    ) -> None:
        """After a card is played, check for last-card callout and apply effects."""
        if len(player.hand) == 0:
            self._end_round(player)
            return

        # Last card callout check
        if len(player.hand) == 1 and self.options.last_card_callout:
            self.play_sound(SOUND_UNO_CALL)
            self.interrupt_phase = "last_card_callout"
            self.interrupt_target_id = player.id
            self.interrupt_timer_ticks = self.options.interrupt_timer * 20
            self.interrupt_wd4_player_id = player.id if card.rank == RANK_WILD_DRAW_FOUR else ""
            self.interrupt_wd4_had_matching = had_matching_color
            BotHelper.jolt_bots(self, ticks=random.randint(10, 30))
            self.rebuild_all_menus()
            return

        # WD4 challenge window
        if card.rank == RANK_WILD_DRAW_FOUR and self.options.challenge_wild_draw_four:
            self._start_wd4_challenge(player, had_matching_color)
            return

        self._apply_card_effects_and_advance(card)

    def _start_wd4_challenge(self, player: LastCardPlayer, had_matching_color: bool) -> None:
        """Start the challenge window for a Wild Draw Four."""
        self.interrupt_phase = "challenge_wd4"
        self.interrupt_target_id = player.id
        self.interrupt_wd4_player_id = player.id
        self.interrupt_wd4_had_matching = had_matching_color
        self.interrupt_timer_ticks = self.options.interrupt_timer * 20

        next_p = self._next_player()
        if next_p:
            user = self.get_user(next_p)
            if user:
                user.speak_l("lastcard-can-challenge", buffer="table")

        BotHelper.jolt_bots(self, ticks=random.randint(20, 40))
        self.rebuild_all_menus()

    def _apply_card_effects_and_advance(self, card: Card) -> None:
        """Apply card effects (skip, reverse, draw, etc.) and advance turn."""
        active_count = len(self.turn_player_ids)

        if card.rank == RANK_SKIP:
            if self.options.skip_card_rule == "all":
                # Skip all — current player plays again
                self.play_sound(SOUND_SKIP)
                self.rebuild_all_menus()
                self._start_turn()
                return
            else:
                self.play_sound(SOUND_SKIP)
                self.skip_next_players(1)

        elif card.rank == RANK_REVERSE:
            self.play_sound(SOUND_REVERSE)
            if active_count == 2:
                if self.options.reverse_two_players == "skip":
                    self.skip_next_players(1)
                else:
                    self.reverse_turn_direction()
            else:
                self.reverse_turn_direction()

        elif card.rank == RANK_DRAW_TWO:
            if self.options.stacking != "off":
                self.pending_draw_count += 2
                self.pending_draw_is_plus_four = False
            else:
                next_p = self._next_player()
                if next_p:
                    self._draw_for_player(next_p, 2)
                self.skip_next_players(1)

        elif card.rank == RANK_WILD_DRAW_FOUR:
            if self.options.stacking == "progressive":
                self.pending_draw_count += 4
                self.pending_draw_is_plus_four = True
            elif self.options.stacking == "standard":
                # Standard stacking: +4 stacks on +4 only
                self.pending_draw_count += 4
                self.pending_draw_is_plus_four = True
            else:
                next_p = self._next_player()
                if next_p:
                    self._draw_for_player(next_p, 4)
                self.skip_next_players(1)

        # Seven-O rules
        if card.rank == 7 and self.options.seven_card_rule == "swap_hand":
            player = self.current_player
            if isinstance(player, LastCardPlayer):
                active = [p for p in self.turn_players if not p.is_spectator and p.id != player.id]
                if len(active) == 1:
                    # Auto-swap with the only other player
                    self._do_swap_hands(player, active[0])
                elif len(active) > 1:
                    self.awaiting_swap_target = True
                    self.swap_player_id = player.id
                    if player.is_bot:
                        BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
                    self.rebuild_all_menus()
                    return

        if card.rank == 0 and self.options.zero_card_rule == "rotate_hands":
            self._rotate_all_hands()

        # Jump-in window
        if self.options.jump_in and not self.jump_in_played:
            self.interrupt_phase = "jump_in_window"
            self.interrupt_timer_ticks = self.options.interrupt_timer * 20
            BotHelper.jolt_bots(self, ticks=random.randint(10, 30))
            self.rebuild_all_menus()
            return

        self._advance_turn()

    def _post_play_advance(self) -> None:
        """Called after color selection wait completes."""
        card = self.top_card
        if not card:
            self._advance_turn()
            return

        player = (
            self.get_player_by_id(self.interrupt_wd4_player_id)
            if self.interrupt_wd4_player_id
            else self.current_player
        )
        if not isinstance(player, LastCardPlayer):
            player = self.current_player
        if not isinstance(player, LastCardPlayer):
            self._advance_turn()
            return

        had_matching = self.interrupt_wd4_had_matching

        self._check_last_card_and_advance(player, card, had_matching)

    # ==========================================================================
    # Draw / Pass actions
    # ==========================================================================

    def _action_draw(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if not self._can_draw(p):
            return

        card = self._draw_card()
        if not card:
            return
        p.hand.append(card)
        p.draws_this_turn += 1
        self.turn_has_drawn = True
        p.called_last_card = False
        self.consecutive_passes = 0

        playable = self._is_card_playable(card, p)
        if playable:
            user = self.get_user(p)
            if user:
                user.play_sound(SOUND_FORCE_PLAY if self.options.force_play else SOUND_PLAYABLE)
            for other in self.players:
                if other.id != p.id:
                    other_user = self.get_user(other)
                    if other_user:
                        other_user.play_sound(random.choice(SOUND_DRAW))
        else:
            self.play_sound(random.choice(SOUND_DRAW))

        self._broadcast_draw(p, 1)

        # Draw until playable logic
        if self.options.draw_until_playable and not playable:
            draw_limit = self.options.draw_limit
            max_hand = self.options.max_hand_size
            if (draw_limit > 0 and p.draws_this_turn >= draw_limit) or (
                max_hand > 0 and len(p.hand) >= max_hand
            ):
                # Hit draw limit or max hand size, must pass
                self.turn_has_drawn = True
            else:
                # Keep drawing state - player can draw again or will auto-draw
                self.turn_has_drawn = False
            self.start_turn_timer()
            self.rebuild_all_menus()
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(10, 20))
            return

        # Force play: if drawn card is playable, must play it
        if self.options.force_play and playable:
            self.start_turn_timer()
            prefix = "toggle_card_" if self.options.allow_multiple_play else "play_card_"
            self.update_player_menu(p, selection_id=f"{prefix}{card.id}")
            if p.is_bot:
                BotHelper.jolt_bot(p, ticks=random.randint(10, 20))
            return

        self.start_turn_timer()
        if playable:
            prefix = "toggle_card_" if self.options.allow_multiple_play else "play_card_"
            selection_id = f"{prefix}{card.id}"
        else:
            selection_id = None
        self.update_player_menu(p, selection_id=selection_id)
        if p.is_bot:
            BotHelper.jolt_bot(p, ticks=random.randint(10, 20))

    def _action_pass(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if self._is_pass_enabled(p) is not None:
            return

        self.play_sound(SOUND_PASS)
        self._broadcast_pass(p)
        self.turn_has_drawn = False
        p.draws_this_turn = 0
        self.consecutive_passes += 1

        # Deadlock detection: if every active player passed without playing or drawing
        # and the deck is completely exhausted, the round is stuck
        is_deck_exhausted = self.deck.is_empty() and len(self.discard_pile) <= 1
        active_count = len(self.turn_player_ids)
        if self.consecutive_passes >= active_count and is_deck_exhausted:
            self._end_round_deadlock()
            return

        self._advance_turn()

    # ==========================================================================
    # Color choice (after Wild)
    # ==========================================================================

    def _action_choose_color(self, player: Player, action_id: str) -> None:
        p = self._require_active_player(player)
        if not p:
            return
        if not self.awaiting_color_choice:
            return
        color = self._color_from_action(action_id)
        if color is None:
            return
        self.current_color = color
        self.awaiting_color_choice = False
        self.play_sound(SOUND_COLOR_CHANGE)
        self._broadcast_color_chosen(color)

        self.timer.clear()
        self.color_wait_ticks = 15

    # ==========================================================================
    # Buzzer action
    # ==========================================================================

    def _action_buzzer(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if player.is_spectator:
            return
        if self.interrupt_phase != "last_card_callout":
            # Player can pre-emptively call last card on their own turn
            if self.current_player == player and len(player.hand) == 2:
                # About to play down to 1 — allow pre-buzzer
                player.called_last_card = True
                self.play_sound(SOUND_BUZZER_PRESS)
                user = self.get_user(player)
                if user:
                    user.speak_l("lastcard-you-called", buffer="table")
                return
            return

        if player.id == self.interrupt_target_id:
            # The player with 1 card is buzzing — they're safe!
            player.called_last_card = True
            self.play_sound(SOUND_BUZZER_PRESS)
            self.broadcast_l("lastcard-player-called", player=player.name)
            # Resolve immediately — they called in time
            self.interrupt_timer_ticks = 0
            self._resolve_interrupt()
            return
        else:
            # Another player is catching them!
            target = self.get_player_by_id(self.interrupt_target_id)
            if not isinstance(target, LastCardPlayer):
                return
            if target.called_last_card:
                # Already called — too late to catch
                user = self.get_user(player)
                if user:
                    user.speak_l("lastcard-already-called", buffer="table")
                return
            # Caught! Target draws penalty
            self.play_sound(SOUND_BUZZER_CAUGHT)
            self.broadcast_l("lastcard-caught", catcher=player.name, target=target.name)
            self._draw_for_player(target, 2)
            target.called_last_card = True  # Prevent double penalty
            self.interrupt_timer_ticks = 0
            self._resolve_interrupt()

    # ==========================================================================
    # Challenge WD4
    # ==========================================================================

    def _action_challenge_wd4(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if self.interrupt_phase != "challenge_wd4":
            return
        # Only the next player can challenge
        next_p = self._next_player()
        if not next_p or next_p.id != player.id:
            return

        self.play_sound(SOUND_CHALLENGE)
        self.broadcast_l("lastcard-challenges-wd4", player=player.name)

        wd4_player = self.get_player_by_id(self.interrupt_wd4_player_id)
        if not isinstance(wd4_player, LastCardPlayer):
            return

        if self.interrupt_wd4_had_matching:
            # Challenge succeeds! WD4 player had matching color
            self.play_sound(SOUND_CHALLENGE_SUCCESS)
            self.broadcast_l("lastcard-challenge-success", player=wd4_player.name)
            # WD4 player draws 4 instead
            self._draw_for_player(wd4_player, 4)
            self.pending_draw_count = 0
        else:
            # Challenge fails! Challenger draws 6 (4 + 2 penalty)
            self.play_sound(SOUND_CHALLENGE_FAIL)
            self.broadcast_l("lastcard-challenge-fail", player=player.name)
            self._draw_for_player(player, 6)
            self.skip_next_players(1)

        self.interrupt_phase = ""
        self.interrupt_timer_ticks = 0
        self._advance_turn()

    def _action_accept_draw(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if self.interrupt_phase != "challenge_wd4":
            return
        next_p = self._next_player()
        if not next_p or next_p.id != player.id:
            return

        # Accept the draw — next player draws 4
        self._draw_for_player(player, 4)
        self.skip_next_players(1)
        self.interrupt_phase = ""
        self.interrupt_timer_ticks = 0
        self._advance_turn()

    # ==========================================================================
    # Jump-in
    # ==========================================================================

    def _action_jump_in(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if player.is_spectator:
            return
        if not self.options.jump_in:
            return
        if self.interrupt_phase != "jump_in_window":
            return
        if self.current_player == player:
            return  # Can't jump in on your own turn

        top = self.top_card
        if not top:
            return

        # Must have exact match (same color AND same rank)
        matching = [c for c in player.hand if c.rank == top.rank and c.suit == top.suit]
        if not matching:
            user = self.get_user(player)
            if user:
                user.speak_l("lastcard-no-matching-card", buffer="table")
            return

        card = matching[0]
        self.play_sound(random.choice(SOUND_INTERCEPT))
        self.broadcast_l("lastcard-jumped-in", player=player.name)

        self.interrupt_phase = ""
        self.interrupt_timer_ticks = 0
        self.jump_in_played = True

        # Hijack the turn to this player
        for i, pid in enumerate(self.turn_player_ids):
            if pid == player.id:
                self.turn_index = i
                break

        self._do_play_card(player, card)

    # ==========================================================================
    # Seven swap target
    # ==========================================================================

    def _action_swap_target(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if not self.awaiting_swap_target:
            return
        if player.id != self.swap_player_id:
            return

        try:
            target_idx = int(action_id.split("_")[-1])
        except ValueError:
            return

        active = [p for p in self.turn_players if not p.is_spectator and p.id != player.id]
        if target_idx < 0 or target_idx >= len(active):
            return

        target = active[target_idx]
        if not isinstance(target, LastCardPlayer):
            return

        self._do_swap_hands(player, target)
        self.awaiting_swap_target = False
        self.swap_player_id = ""
        self._advance_turn()

    def _do_swap_hands(self, player1: LastCardPlayer, player2: LastCardPlayer) -> None:
        player1.hand, player2.hand = player2.hand, player1.hand
        self.play_sound(SOUND_HAND_CHANGE)
        self.broadcast_l("lastcard-swapped-hands", player1=player1.name, player2=player2.name)

    def _rotate_all_hands(self) -> None:
        """Rotate all hands in the current turn direction."""
        active = [
            p for p in self.turn_players if not p.is_spectator and isinstance(p, LastCardPlayer)
        ]
        if len(active) < 2:
            return
        hands = [p.hand for p in active]
        if self.turn_direction == 1:
            rotated = [hands[-1]] + hands[:-1]
        else:
            rotated = hands[1:] + [hands[0]]
        for p, h in zip(active, rotated):
            p.hand = h
        self.play_sound(SOUND_HAND_CHANGE)
        self.broadcast_l("lastcard-hands-rotated")

    # ==========================================================================
    # Interrupt timer resolution
    # ==========================================================================

    def _resolve_interrupt(self) -> None:
        """Called when the interrupt timer expires."""
        phase = self.interrupt_phase
        self.interrupt_phase = ""

        if phase == "last_card_callout":
            target = self.get_player_by_id(self.interrupt_target_id)
            if isinstance(target, LastCardPlayer) and not target.called_last_card:
                # Nobody caught them, and they didn't call — they're safe (timer expired)
                pass
            # Now check for WD4 challenge
            card = self.top_card
            if card and card.rank == RANK_WILD_DRAW_FOUR and self.options.challenge_wild_draw_four:
                self._start_wd4_challenge(
                    self.get_player_by_id(self.interrupt_wd4_player_id)
                    if self.interrupt_wd4_player_id
                    else target,
                    self.interrupt_wd4_had_matching,
                )
                return
            self._apply_card_effects_and_advance(card if card else Card(id=-1, rank=0, suit=0))

        elif phase == "challenge_wd4":
            # Nobody challenged — next player draws
            next_p = self._next_player()
            if next_p and isinstance(next_p, LastCardPlayer):
                self._draw_for_player(next_p, 4)
            self.skip_next_players(1)
            self._advance_turn()

        elif phase == "jump_in_window":
            # Nobody jumped in — normal advance
            self._advance_turn()

    def _process_bot_reactions(self) -> None:
        """Let bots react during interrupt windows."""
        for p in self.players:
            if not p.is_bot or p.is_spectator:
                continue
            if not isinstance(p, LastCardPlayer):
                continue
            if p.bot_think_ticks > 0:
                p.bot_think_ticks -= 1
                continue

            action = bot_react(self, p)
            if action:
                self.execute_action(p, action)
                return  # One bot action per tick

    # ==========================================================================
    # Stacking
    # ==========================================================================

    def _can_stack(self, player: LastCardPlayer) -> bool:
        """Check if player can stack on the current pending draw."""
        if self.pending_draw_count == 0:
            return False
        if self.options.stacking == "off":
            return False

        for card in player.hand:
            if self.options.stacking == "progressive":
                if card.rank in (RANK_DRAW_TWO, RANK_WILD_DRAW_FOUR):
                    return True
            else:  # standard
                if self.pending_draw_is_plus_four and card.rank == RANK_WILD_DRAW_FOUR:
                    return True
                if not self.pending_draw_is_plus_four and card.rank == RANK_DRAW_TWO:
                    return True
        return False

    def _force_draw_pending(self, player: LastCardPlayer) -> None:
        """Force a player to draw the accumulated stack."""
        count = self.pending_draw_count
        self._draw_for_player(player, count)
        self.broadcast_l("lastcard-forced-draw", player=player.name, count=count)
        self.play_sound(SOUND_PENALTY_DRAW)
        self.pending_draw_count = 0
        self.pending_draw_is_plus_four = False
        self.skip_next_players(1)
        self._advance_turn()

    # ==========================================================================
    # Information actions
    # ==========================================================================

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if player.is_spectator:
            return
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        if not player.hand:
            user.speak_l("lastcard-hand-empty", buffer="table")
            return
        sorted_hand = self._sort_hand(player)
        card_names = [self.format_card(c, locale) for c in sorted_hand]
        text = Localization.get(
            locale, "lastcard-your-hand", count=len(player.hand), cards=", ".join(card_names)
        )
        user.speak(text, buffer="table")

    def _action_read_top(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.speak(self.format_top_card(user.locale), buffer="table")

    def _action_read_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        parts = []
        for p in self.turn_players:
            if p.is_spectator:
                continue
            if isinstance(p, LastCardPlayer):
                parts.append(f"{p.name} {len(p.hand)}")
        deck_count = self.deck.size()
        if deck_count > 0:
            parts.append(Localization.get(locale, "lastcard-deck-count", count=deck_count))
        text = ", ".join(parts) if parts else Localization.get(locale, "lastcard-no-players")
        user.speak(text, buffer="table")

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("lastcard-timer-disabled", buffer="table")
        else:
            user.speak_l("lastcard-timer-remaining", buffer="table", seconds=remaining)

    def _action_read_draw_penalty(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        if self.pending_draw_count > 0:
            user.speak_l(
                "lastcard-draw-penalty-active", buffer="table", count=self.pending_draw_count
            )
        else:
            user.speak_l("lastcard-draw-penalty-none", buffer="table")

    def _action_cycle_hand_sort(self, player: Player, action_id: str) -> None:
        if not isinstance(player, LastCardPlayer):
            return
        if player.is_spectator:
            return
        user = self.get_user(player)
        if not user:
            return
        idx = HAND_SORT_MODES.index(player.hand_sort) if player.hand_sort in HAND_SORT_MODES else 0
        player.hand_sort = HAND_SORT_MODES[(idx + 1) % len(HAND_SORT_MODES)]
        label_key = HAND_SORT_LABELS.get(player.hand_sort, "lastcard-sort-by-color")
        mode_label = Localization.get(user.locale, label_key)
        user.speak_l("lastcard-sort-changed", buffer="table", mode=mode_label)
        self._sync_turn_actions(player)
        self.rebuild_player_menu(player)

    # ==========================================================================
    # Action state helpers
    # ==========================================================================

    def _require_active_player(self, player: Player) -> LastCardPlayer | None:
        if not isinstance(player, LastCardPlayer):
            return None
        if player.is_spectator:
            return None
        if self.current_player != player:
            return None
        return player

    def _is_turn_active(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return "action-wait"
        return None

    def _is_turn_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        if self.color_wait_ticks > 0 or self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_card_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return "action-not-available"
        if self.interrupt_phase:
            return "action-not-available"
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return "action-wait"
        return None

    def _is_play_card_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, LastCardPlayer):
            return Visibility.HIDDEN
        if not action_id:
            return Visibility.HIDDEN
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return Visibility.HIDDEN
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # -- Toggle card (multi-play) callbacks --

    def _is_toggle_card_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        # Cards are always "enabled" so they remain visible for reading hand,
        # but toggling is gated in the handler by current-player check
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return "action-wait"
        return None

    def _is_toggle_card_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0 or self.intro_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, LastCardPlayer):
            return Visibility.HIDDEN
        if not action_id:
            return Visibility.HIDDEN
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return Visibility.HIDDEN
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_toggle_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, LastCardPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return action_id
        locale = self._player_locale(player)
        name = self.format_card(card, locale)
        if card_id in player.selected_cards:
            return Localization.get(locale, "lastcard-card-selected", card=name)
        return name

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        return self._is_turn_active(player)

    def _is_play_selected_hidden(self, player: Player) -> Visibility:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return Visibility.HIDDEN
        return self._is_turn_hidden(player)

    def _get_play_selected_label(self, player: Player, action_id: str) -> str:
        locale = self._player_locale(player)
        if not isinstance(player, LastCardPlayer) or not player.selected_cards:
            return Localization.get(locale, "lastcard-play-none")
        selected = [c for c in player.hand if c.id in player.selected_cards]
        if not selected:
            return Localization.get(locale, "lastcard-play-none")
        count = len(selected)
        if count == 1:
            return Localization.get(
                locale, "lastcard-play-one", card=self.format_card(selected[0], locale)
            )
        ranks = {c.rank for c in selected}
        if len(ranks) != 1:
            return Localization.get(locale, "lastcard-play-invalid")
        return Localization.get(locale, "lastcard-play-multi", count=count)

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return "action-not-available"
        if self.interrupt_phase:
            return "action-not-available"
        err = self._is_turn_active(player)
        if err:
            return err
        if not isinstance(player, LastCardPlayer):
            return "action-not-available"
        if not self._can_draw(player):
            return "action-not-available"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.awaiting_color_choice or self.interrupt_phase:
            return Visibility.HIDDEN
        if self._is_turn_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, LastCardPlayer):
            return Visibility.HIDDEN
        if not self._can_draw(player):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_pass_enabled(self, player: Player) -> str | None:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return "action-not-available"
        if self.interrupt_phase:
            return "action-not-available"
        err = self._is_turn_active(player)
        if err:
            return err
        if not isinstance(player, LastCardPlayer):
            return "action-not-available"
        # Can only pass after drawing (or when can't draw)
        if (
            self.options.force_play
            and isinstance(player, LastCardPlayer)
            and self._has_playable_cards(player)
        ):
            return "action-not-available"
        if self.turn_has_drawn:
            return None
        if not self._can_draw(player):
            return None
        return "action-not-available"

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if self.awaiting_color_choice or self.interrupt_phase:
            return Visibility.HIDDEN
        if self._is_turn_hidden(player) == Visibility.HIDDEN:
            return Visibility.HIDDEN
        if not isinstance(player, LastCardPlayer):
            return Visibility.HIDDEN
        if self.turn_has_drawn:
            return Visibility.VISIBLE
        if not self._can_draw(player):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_color_choice_enabled(self, player: Player) -> str | None:
        if not self.awaiting_color_choice:
            return "action-not-available"
        return self._is_turn_active(player)

    def _is_color_choice_hidden(self, player: Player) -> Visibility:
        if not self.awaiting_color_choice:
            return Visibility.HIDDEN
        return self._is_turn_hidden(player)

    def _is_buzzer_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if not self.options.buzzer_enabled:
            return "action-not-available"
        return None

    def _is_buzzer_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if not self.options.buzzer_enabled:
            return Visibility.HIDDEN
        # Web clients: show buzzer button during last-card callout window,
        # or when current player has 2 cards (pre-buzz opportunity)
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.interrupt_phase == "last_card_callout":
                return Visibility.VISIBLE
            if (
                self.current_player == player
                and isinstance(player, LastCardPlayer)
                and len(player.hand) == 2
            ):
                return Visibility.VISIBLE
        return Visibility.HIDDEN  # Keybind-only for desktop

    def _is_challenge_enabled(self, player: Player) -> str | None:
        if self.interrupt_phase != "challenge_wd4":
            return "action-not-available"
        next_p = self._next_player()
        if not next_p or next_p.id != player.id:
            return "action-not-available"
        return None

    def _is_challenge_hidden(self, player: Player) -> Visibility:
        if self.interrupt_phase != "challenge_wd4":
            return Visibility.HIDDEN
        next_p = self._next_player()
        if not next_p or next_p.id != player.id:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_accept_draw_enabled(self, player: Player) -> str | None:
        return self._is_challenge_enabled(player)

    def _is_accept_draw_hidden(self, player: Player) -> Visibility:
        return self._is_challenge_hidden(player)

    def _is_jump_in_enabled(self, player: Player) -> str | None:
        if not self.options.jump_in:
            return "action-not-available"
        if self.interrupt_phase != "jump_in_window":
            return "action-not-available"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player == player:
            return "action-not-available"
        return None

    def _is_jump_in_hidden(self, player: Player) -> Visibility:
        if not self.options.jump_in:
            return Visibility.HIDDEN
        if self.interrupt_phase != "jump_in_window":
            return Visibility.HIDDEN
        if player.is_spectator or self.current_player == player:
            return Visibility.HIDDEN
        # Web clients: show jump-in button during the window
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN  # Keybind-only for desktop

    def _is_swap_target_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        if not self.awaiting_swap_target:
            return "action-not-available"
        if player.id != self.swap_player_id:
            return "action-not-available"
        return None

    def _is_swap_target_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if not self.awaiting_swap_target:
            return Visibility.HIDDEN
        if player.id != self.swap_player_id:
            return Visibility.HIDDEN
        if not action_id:
            return Visibility.HIDDEN
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return Visibility.HIDDEN
        active = [p for p in self.turn_players if not p.is_spectator and p.id != player.id]
        if idx < 0 or idx >= len(active):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_swap_target_label(self, player: Player, action_id: str) -> str:
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        active = [p for p in self.turn_players if not p.is_spectator and p.id != player.id]
        if 0 <= idx < len(active):
            return active[idx].name
        return action_id

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return Visibility.HIDDEN  # Keybind-only for desktop

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.HIDDEN  # Keybind-only

    def _is_sort_turn_hidden(self, player: Player) -> Visibility:
        """Sort hand button in turn menu: web-only."""
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    # ==========================================================================
    # Card helpers
    # ==========================================================================

    def _sort_hand(self, player: LastCardPlayer) -> list[Card]:
        """Sort a player's hand based on their sort preference."""
        if player.hand_sort == "rank":
            return sorted(
                player.hand, key=lambda c: (c.rank, COLOR_SORT_ORDER.get(c.suit, 5), c.id)
            )
        if player.hand_sort == "none":
            return list(player.hand)
        # Default: sort by color then rank
        return sorted(player.hand, key=lambda c: (COLOR_SORT_ORDER.get(c.suit, 5), c.rank, c.id))

    def _is_card_playable(self, card: Card, player: LastCardPlayer | None = None) -> bool:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return False

        # During stacking, only matching stack cards can be played
        if self.pending_draw_count > 0 and self.options.stacking != "off":
            if self.options.stacking == "progressive":
                return card.rank in (RANK_DRAW_TWO, RANK_WILD_DRAW_FOUR)
            else:  # standard
                if self.pending_draw_is_plus_four:
                    return card.rank == RANK_WILD_DRAW_FOUR
                else:
                    return card.rank == RANK_DRAW_TWO

        # Wild cards are always playable
        if card.rank in (RANK_WILD, RANK_WILD_DRAW_FOUR):
            return True

        top = self.top_card
        if not top:
            return True

        # Match color
        if card.suit == self.current_color:
            return True
        # Match rank (number or action)
        if card.rank == top.rank and top.suit != COLOR_WILD:
            return True

        return False

    def _has_playable_cards(self, player: LastCardPlayer) -> bool:
        return any(self._is_card_playable(card, player) for card in player.hand)

    def get_playable_indices(self, player: LastCardPlayer) -> list[int]:
        return [i for i, card in enumerate(player.hand) if self._is_card_playable(card, player)]

    @property
    def top_card(self) -> Card | None:
        return self.discard_pile[-1] if self.discard_pile else None

    def _draw_card(self) -> Card | None:
        if self.deck.is_empty():
            self._reshuffle_discard_into_deck()
        return self.deck.draw_one()

    def _reshuffle_discard_into_deck(self) -> None:
        if len(self.discard_pile) <= 1:
            return
        top = self.discard_pile[-1]
        rest = self.discard_pile[:-1]
        self.discard_pile = [top]
        self.deck.add(rest)
        self.deck.shuffle()
        self.play_sound(SOUND_RESHUFFLE)

    def _can_draw(self, player: LastCardPlayer) -> bool:
        if self.awaiting_color_choice or self.awaiting_swap_target:
            return False
        if self.interrupt_phase:
            return False
        # Max hand size: can't draw if already at cap
        max_hand = self.options.max_hand_size
        if max_hand > 0 and len(player.hand) >= max_hand:
            return False
        # Force play: can't draw if you have playable cards
        if self.options.force_play and self._has_playable_cards(player):
            return False
        # Draw until playable: can keep drawing
        if self.options.draw_until_playable:
            if self.turn_has_drawn:
                return False  # Already drew and found playable (or hit limit)
            draw_limit = self.options.draw_limit
            if draw_limit > 0 and player.draws_this_turn >= draw_limit:
                return False
            if self.deck.is_empty() and len(self.discard_pile) <= 1:
                return False
            return True
        # Normal: can draw once per turn if no playable cards
        if self.turn_has_drawn:
            return False
        if self._has_playable_cards(player):
            return False
        if self.deck.is_empty() and len(self.discard_pile) <= 1:
            return False
        return True

    def _draw_for_player(self, player: LastCardPlayer, count: int) -> None:
        actual = 0
        max_hand = self.options.max_hand_size
        for _ in range(count):
            if max_hand > 0 and len(player.hand) >= max_hand:
                break
            card = self._draw_card()
            if card:
                player.hand.append(card)
                actual += 1
            else:
                break
        if actual > 0:
            self._broadcast_draw(player, actual)
            for i in range(min(actual, 3)):
                self.schedule_sound(random.choice(SOUND_DRAW), delay_ticks=i * 5)

    def _next_player(self) -> LastCardPlayer | None:
        if not self.turn_player_ids:
            return None
        idx = (self.turn_index + self.turn_direction) % len(self.turn_player_ids)
        player_id = self.turn_player_ids[idx]
        p = self.get_player_by_id(player_id)
        return p if isinstance(p, LastCardPlayer) else None

    # ==========================================================================
    # Card formatting
    # ==========================================================================

    def _color_from_action(self, action_id: str) -> int | None:
        mapping = {
            "color_red": COLOR_RED,
            "color_blue": COLOR_BLUE,
            "color_green": COLOR_GREEN,
            "color_yellow": COLOR_YELLOW,
        }
        return mapping.get(action_id)

    def _color_name(self, color: int, locale: str) -> str:
        key = {
            COLOR_RED: "lastcard-color-red",
            COLOR_BLUE: "lastcard-color-blue",
            COLOR_GREEN: "lastcard-color-green",
            COLOR_YELLOW: "lastcard-color-yellow",
        }.get(color, "lastcard-color-red")
        return Localization.get(locale, key)

    def format_card(self, card: Card, locale: str) -> str:
        if card.rank == RANK_WILD:
            return Localization.get(locale, "lastcard-card-wild")
        if card.rank == RANK_WILD_DRAW_FOUR:
            return Localization.get(locale, "lastcard-card-wild-draw-four")
        color = self._color_name(card.suit, locale)
        if card.rank == RANK_SKIP:
            return Localization.get(locale, "lastcard-card-skip", color=color)
        if card.rank == RANK_REVERSE:
            return Localization.get(locale, "lastcard-card-reverse", color=color)
        if card.rank == RANK_DRAW_TWO:
            return Localization.get(locale, "lastcard-card-draw-two", color=color)
        return Localization.get(locale, "lastcard-card-number", color=color, number=card.rank)

    def format_top_card(self, locale: str) -> str:
        top = self.top_card
        if not top:
            return Localization.get(locale, "lastcard-no-top")
        text = self.format_card(top, locale)
        if top.rank in (RANK_WILD, RANK_WILD_DRAW_FOUR) and self.current_color:
            color = self._color_name(self.current_color, locale)
            text += f", {color}"
        return text

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, LastCardPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return action_id
        locale = self._player_locale(player)
        return self.format_card(card, locale)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    # ==========================================================================
    # Broadcast helpers
    # ==========================================================================

    def _broadcast_start_card(self) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(
                "lastcard-start-card", buffer="table", card=self.format_top_card(user.locale)
            )

    def _broadcast_color_chosen(self, color: int) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(
                "lastcard-color-chosen", buffer="table", color=self._color_name(color, user.locale)
            )

    def _broadcast_play(self, player: LastCardPlayer, card: Card) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(
                "lastcard-player-plays",
                buffer="table",
                player=player.name,
                card=self.format_card(card, user.locale),
            )

    def _broadcast_draw(self, player: LastCardPlayer, count: int) -> None:
        key = "lastcard-player-draws-one" if count == 1 else "lastcard-player-draws-many"
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l(key, buffer="table", player=player.name, count=count)

    def _broadcast_pass(self, player: LastCardPlayer) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l("lastcard-player-passes", buffer="table", player=player.name)

    # ==========================================================================
    # Sounds
    # ==========================================================================

    def _play_card_sound(self, card: Card) -> None:
        if card.rank == RANK_WILD:
            self.play_sound(SOUND_WILD)
        elif card.rank == RANK_WILD_DRAW_FOUR:
            self.play_sound(SOUND_WILD_DRAW_FOUR)
        elif card.rank == RANK_SKIP:
            self.play_sound(SOUND_SKIP)
        elif card.rank == RANK_REVERSE:
            self.play_sound(SOUND_REVERSE)
        elif card.rank == RANK_DRAW_TWO:
            # Play card sound + scheduled draw sounds
            self.play_sound(random.choice(SOUND_PLAY))
            self.schedule_sound(random.choice(SOUND_DRAW), delay_ticks=8)
            self.schedule_sound(random.choice(SOUND_DRAW), delay_ticks=14)
        else:
            self.play_sound(random.choice(SOUND_PLAY))

    # ==========================================================================
    # Scoring / end of hand
    # ==========================================================================

    def _end_round(self, winner: LastCardPlayer) -> None:
        active = [p for p in self.players if not p.is_spectator and isinstance(p, LastCardPlayer)]

        if self.options.scoring_mode == "classic":
            total = 0
            for p in active:
                if p.id == winner.id:
                    continue
                total += self._hand_points(p.hand)
            real_winner = self.get_player_by_id(winner.id)
            if isinstance(real_winner, LastCardPlayer):
                real_winner.score += total
            self.broadcast_l("lastcard-round-winner", player=winner.name, points=total)
        else:  # negative
            for p in active:
                pts = self._hand_points(p.hand)
                p.score += pts
            self.broadcast_l("lastcard-round-end-negative")

        # Play sounds
        for p in active:
            user = self.get_user(p)
            if not user:
                continue
            if p.id == winner.id:
                user.play_sound(SOUND_WIN_ROUND)
            else:
                user.play_sound(SOUND_LOSE_ROUND)

        self._sync_team_scores()

        # Clear hands between rounds so they're hidden from UI
        for p in active:
            p.hand = []

        # Check for game winner
        if self.options.scoring_mode == "classic":
            real_winner = self.get_player_by_id(winner.id)
            if (
                isinstance(real_winner, LastCardPlayer)
                and real_winner.score >= self.options.winning_score
            ):
                self._end_game(real_winner)
                return
        else:
            # Negative: game ends when any player exceeds winning_score
            over_limit = [p for p in active if p.score >= self.options.winning_score]
            if over_limit:
                actual_winner = min(active, key=lambda p: p.score)
                self._end_game(actual_winner)
                return

        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _end_round_deadlock(self) -> None:
        """End the round when all players are forced to pass (deck exhausted, no playable cards)."""
        active = [p for p in self.players if not p.is_spectator and isinstance(p, LastCardPlayer)]
        self.broadcast_l("lastcard-round-deadlock")

        # Score by hand points: lowest hand wins (fewest points held)
        if self.options.scoring_mode == "classic":
            # Classic: no winner, no points awarded
            pass
        else:
            # Negative: everyone scores their hand points as usual
            for p in active:
                pts = self._hand_points(p.hand)
                p.score += pts

        self.play_sound(SOUND_LOSE_ROUND)
        self._sync_team_scores()

        for p in active:
            p.hand = []

        # Check for game winner (negative mode only — classic can't end on a draw round)
        if self.options.scoring_mode != "classic":
            over_limit = [p for p in active if p.score >= self.options.winning_score]
            if over_limit:
                actual_winner = min(active, key=lambda p: p.score)
                self._end_game(actual_winner)
                return

        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _hand_points(self, hand: list[Card]) -> int:
        total = 0
        for card in hand:
            if card.rank in CARD_POINTS:
                total += CARD_POINTS[card.rank]
            else:
                total += card.rank if card.rank > 0 else 0
        return total

    def _end_game(self, winner: LastCardPlayer) -> None:
        self.play_sound(SOUND_WIN_GAME)
        self.broadcast_l("lastcard-game-winner", player=winner.name, score=winner.score)
        self.finish_game()

    def build_game_result(self) -> GameResult:
        active = [p for p in self.players if not p.is_spectator]
        if self.options.scoring_mode == "classic":
            winner = max(active, key=lambda p: p.score, default=None)
        else:
            winner = min(active, key=lambda p: p.score, default=None)
        final_scores = {p.name: p.score for p in active}
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=p.id,
                    player_name=p.name,
                    is_bot=p.is_bot and not p.replaced_human,
                )
                for p in active
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "winner_score": winner.score if winner else 0,
                "final_scores": final_scores,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        reverse = self.options.scoring_mode == "classic"
        sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=reverse)
        for i, (name, score) in enumerate(sorted_scores, 1):
            lines.append(
                Localization.get(locale, "lastcard-line-format", rank=i, player=name, score=score)
            )
        return lines

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team and isinstance(p, LastCardPlayer):
                team.total_score = p.score

    # ==========================================================================
    # Event queue
    # ==========================================================================

    def _process_events(self) -> None:
        if not self.event_queue:
            return
        current_queue = list(self.event_queue)
        self.event_queue = []
        current_tick = self.sound_scheduler_tick
        for tick, event_type, data in current_queue:
            if tick <= current_tick:
                self._handle_event(event_type, data)
            else:
                self.event_queue.append((tick, event_type, data))

    def _handle_event(self, event_type: str, data: dict) -> None:
        pass  # Reserved for future deferred events
