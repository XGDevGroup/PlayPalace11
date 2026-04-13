"""Phase 10 state dataclasses, phase definitions, and constants."""

from __future__ import annotations

from dataclasses import dataclass, field

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Player
from ...game_utils.cards import Card
from ...game_utils.options import (
    GameOptions,
    IntOption,
    BoolOption,
    MenuOption,
    option_field,
)

# ---------------------------------------------------------------------------
# Card rank / suit constants
# ---------------------------------------------------------------------------

P10_RANK_WILD = 13
P10_RANK_SKIP = 14

P10_COLOR_RED = 1
P10_COLOR_BLUE = 2
P10_COLOR_GREEN = 3
P10_COLOR_YELLOW = 4

P10_COLOR_NAMES = {
    P10_COLOR_RED: "phase10-color-red",
    P10_COLOR_BLUE: "phase10-color-blue",
    P10_COLOR_GREEN: "phase10-color-green",
    P10_COLOR_YELLOW: "phase10-color-yellow",
}

# ---------------------------------------------------------------------------
# Group kind constants
# ---------------------------------------------------------------------------

GROUP_SET = "set"
GROUP_RUN = "run"
GROUP_COLOR = "color"

# ---------------------------------------------------------------------------
# Phase requirement / phase table
# ---------------------------------------------------------------------------


@dataclass
class PhaseRequirement(DataClassJSONMixin):
    """One group requirement within a phase (e.g. 'set of 3' or 'run of 4')."""

    kind: str   # GROUP_SET | GROUP_RUN | GROUP_COLOR
    count: int  # minimum card count


# 10 phases in order.  Index 0 = Phase 1 … Index 9 = Phase 10.
PHASES: list[list[PhaseRequirement]] = [
    [PhaseRequirement(GROUP_SET, 3), PhaseRequirement(GROUP_SET, 3)],    # 1
    [PhaseRequirement(GROUP_SET, 3), PhaseRequirement(GROUP_RUN, 4)],    # 2
    [PhaseRequirement(GROUP_SET, 4), PhaseRequirement(GROUP_RUN, 4)],    # 3
    [PhaseRequirement(GROUP_RUN, 7)],                                     # 4
    [PhaseRequirement(GROUP_RUN, 8)],                                     # 5
    [PhaseRequirement(GROUP_RUN, 9)],                                     # 6
    [PhaseRequirement(GROUP_SET, 4), PhaseRequirement(GROUP_SET, 4)],    # 7
    [PhaseRequirement(GROUP_COLOR, 7)],                                   # 8
    [PhaseRequirement(GROUP_SET, 5), PhaseRequirement(GROUP_SET, 2)],    # 9
    [PhaseRequirement(GROUP_SET, 4), PhaseRequirement(GROUP_SET, 3)],    # 10
]

# FTL keys for phase descriptions (indexed 1-10)
PHASE_DESC_KEYS: dict[int, str] = {i: f"phase10-phase-desc-{i}" for i in range(1, 11)}

# Even phases variant uses only these phase numbers
EVEN_PHASES = [2, 4, 6, 8, 10]

# ---------------------------------------------------------------------------
# Table group (a laid-down phase group on the table)
# ---------------------------------------------------------------------------


@dataclass
class TableGroup(DataClassJSONMixin):
    """A single group laid down on the table by a player.

    Attributes:
        owner_id: Player ID of the owner.
        group_index: 0-based index of this group among the owner's groups.
        requirement: The phase requirement this group satisfies.
        cards: Cards currently in this group (grows as hits are applied).
    """

    owner_id: str
    group_index: int
    requirement: PhaseRequirement
    cards: list[Card] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Player
# ---------------------------------------------------------------------------


@dataclass
class Phase10Player(Player):
    """Per-player state for Phase 10.

    Attributes:
        hand: Cards currently in hand.
        current_phase: The phase number this player is working on (1-10).
        phase_laid_down: True once the player has laid their phase down this hand.
        score: Accumulated penalty points across all hands.
        skipped: True if a Skip card has been played against this player and
                 their next turn should be forfeited.
    """

    hand: list[Card] = field(default_factory=list)
    current_phase: int = 1
    phase_laid_down: bool = False
    score: int = 0
    skipped: bool = False


# ---------------------------------------------------------------------------
# Options
# ---------------------------------------------------------------------------

TURN_TIMER_CHOICES = ["5", "10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "5": "phase10-timer-5",
    "10": "phase10-timer-10",
    "15": "phase10-timer-15",
    "20": "phase10-timer-20",
    "30": "phase10-timer-30",
    "45": "phase10-timer-45",
    "60": "phase10-timer-60",
    "90": "phase10-timer-90",
    "0": "phase10-timer-unlimited",
}


@dataclass
class Phase10Options(GameOptions):
    """Configurable options for Phase 10."""

    winning_phase: int = option_field(
        IntOption(
            default=10,
            min_val=1,
            max_val=10,
            value_key="phase",
            label="phase10-set-winning-phase",
            prompt="phase10-enter-winning-phase",
            change_msg="phase10-option-changed-winning-phase",
        )
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            default="0",
            label="phase10-set-turn-timer",
            prompt="phase10-select-turn-timer",
            change_msg="phase10-option-changed-turn-timer",
            choice_labels=TURN_TIMER_LABELS,
        )
    )
    even_phases_only: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="phase10-toggle-even-phases",
            change_msg="phase10-option-changed-even-phases",
        )
    )
    fixed_hands: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="phase10-toggle-fixed-hands",
            change_msg="phase10-option-changed-fixed-hands",
        )
    )
