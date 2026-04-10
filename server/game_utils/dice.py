"""Dice utilities for dice-based games."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
import random
from typing import Sequence

from mashumaro.mixins.json import DataClassJSONMixin


@dataclass
class DiceSet(DataClassJSONMixin):
    """Set of dice with keep/lock mechanics.

    Supports rolling any number of dice, keeping or locking dice across rolls,
    and toggling keep status on unlocked dice.

    Typical flow:
        1) roll() rolls all dice.
        2) keep()/unkeep() marks dice for preservation.
        3) roll() again locks kept dice and rerolls others.
        4) reset() clears state for the next turn.

    Attributes:
        num_dice: Number of dice in the set.
        sides: Sides per die.
        values: Current die values.
        kept: Indices marked to keep.
        locked: Indices locked until reset.
    """

    num_dice: int = 5
    sides: int = 6
    values: list[int] = field(default_factory=list)
    kept: set[int] = field(default_factory=set)
    locked: set[int] = field(default_factory=set)

    def __post_init__(self):
        """Initialize empty values if needed."""
        if not self.values:
            self.values = []

    @property
    def has_rolled(self) -> bool:
        """Check if dice have been rolled."""
        return len(self.values) == self.num_dice

    @property
    def unlocked_count(self) -> int:
        """Count of dice that are not locked."""
        if not self.has_rolled:
            return self.num_dice
        return sum(1 for i in range(self.num_dice) if i not in self.locked)

    @property
    def kept_unlocked_count(self) -> int:
        """Count of kept dice that are not locked (will be locked on next roll)."""
        return sum(1 for i in self.kept if i not in self.locked)

    @property
    def all_decided(self) -> bool:
        """Check if all dice are either kept or locked."""
        if not self.has_rolled:
            return False
        return all(i in self.kept or i in self.locked for i in range(self.num_dice))

    def reset(self) -> None:
        """Reset all dice state for a new turn."""
        self.values = []
        self.kept = set()
        self.locked = set()

    def roll(self, lock_kept: bool = True, clear_kept: bool = True) -> list[int]:
        """
        Roll the dice.

        If dice haven't been rolled yet, rolls all dice.
        Otherwise, respects kept/locked dice and rerolls the rest.

        Args:
            lock_kept: If True, kept dice become locked before rolling.
                      Set False for games where you can unkeep after rolling.
            clear_kept: If True, clears kept list after rolling.
                       Set False to preserve kept state.

        Returns:
            List of all dice values after rolling.
        """
        if not self.has_rolled:
            # First roll - roll all dice
            self.values = [random.randint(1, self.sides) for _ in range(self.num_dice)]  # nosec B311
        else:
            if lock_kept:
                self.locked |= self.kept

            for i in range(self.num_dice):
                if i not in self.locked and i not in self.kept:
                    self.values[i] = random.randint(1, self.sides)  # nosec B311

            if clear_kept:
                self.kept = set(self.locked)

        return self.values

    def is_locked(self, index: int) -> bool:
        """Check if a die at index is locked."""
        return index in self.locked

    def is_kept(self, index: int) -> bool:
        """Check if a die at index is kept."""
        return index in self.kept

    def keep(self, index: int) -> bool:
        """
        Mark a die to keep.

        Returns:
            True if successful, False if die is locked.
        """
        if index in self.locked:
            return False
        self.kept.add(index)
        return True

    def unkeep(self, index: int) -> bool:
        """
        Unmark a die from being kept.

        Returns:
            True if successful, False if die is locked.
        """
        if index in self.locked:
            return False
        self.kept.discard(index)
        return True

    def toggle_keep(self, index: int) -> bool | None:
        """
        Toggle keep status of a die.

        Returns:
            True if now kept, False if now unkept, None if locked.
        """
        if index in self.locked:
            return None
        if index in self.kept:
            self.kept.discard(index)
            return False
        else:
            self.kept.add(index)
            return True

    def get_value(self, index: int) -> int | None:
        """Get the value of a specific die."""
        if not self.has_rolled or index >= len(self.values):
            return None
        return self.values[index]

    def get_status(self, index: int) -> str:
        """Get status string for a die: 'locked', 'kept', or ''."""
        if index in self.locked:
            return "locked"
        elif index in self.kept:
            return "kept"
        return ""

    def format_die(self, index: int, show_status: bool = True) -> str:
        """Format a single die for display."""
        if not self.has_rolled:
            return "-"

        value = str(self.values[index])
        if show_status:
            status = self.get_status(index)
            if status:
                return f"{value} ({status})"
        return value

    def format_all(self, show_status: bool = True, separator: str = ", ") -> str:
        """Format all dice for display."""
        if not self.has_rolled:
            return "-"
        parts = [self.format_die(i, show_status) for i in range(self.num_dice)]
        return separator.join(parts)

    def format_values_only(self, separator: str = ", ") -> str:
        """Format just the dice values without status."""
        if not self.has_rolled:
            return "-"
        return separator.join(str(v) for v in self.values)

    def count_value(self, value: int) -> int:
        """Count how many dice show a specific value."""
        if not self.has_rolled:
            return 0
        return sum(1 for v in self.values if v == value)

    def sum_values(self, exclude_value: int | None = None) -> int:
        """
        Sum all dice values.

        Args:
            exclude_value: If set, dice showing this value are counted as 0.
        """
        if not self.has_rolled:
            return 0
        total = 0
        for v in self.values:
            if exclude_value is not None and v == exclude_value:
                continue
            total += v
        return total

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return {
            "num_dice": self.num_dice,
            "sides": self.sides,
            "values": self.values,
            "kept": sorted(self.kept),
            "locked": sorted(self.locked),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DiceSet":
        """Deserialize from dictionary."""
        return cls(
            num_dice=data.get("num_dice", 5),
            sides=data.get("sides", 6),
            values=data.get("values", []),
            kept=set(data.get("kept", [])),
            locked=set(data.get("locked", [])),
        )


def roll_dice(num_dice: int = 1, sides: int = 6) -> list[int]:
    """Roll multiple dice and return their values."""
    return [random.randint(1, sides) for _ in range(num_dice)]  # nosec B311


def roll_die(sides: int = 6) -> int:
    """Roll a single die and return its value."""
    return random.randint(1, sides)  # nosec B311


def count_dice(dice: Iterable[int], *, sides: int = 6) -> dict[int, int]:
    """Count occurrences of each die value."""
    counts = {i: 0 for i in range(1, sides + 1)} if sides else {}
    for value in dice:
        if value in counts:
            counts[value] += 1
        else:
            counts[value] = counts.get(value, 0) + 1
    return counts


def _coerce_counts(
    dice_or_counts: Iterable[int] | Mapping[int, int], *, sides: int = 6
) -> dict[int, int]:
    if isinstance(dice_or_counts, Mapping):
        base = {i: dice_or_counts.get(i, 0) for i in range(1, sides + 1)} if sides else {}
        for key, value in dice_or_counts.items():
            if key not in base:
                base[key] = value
        return base
    if isinstance(dice_or_counts, Sequence):
        return count_dice(dice_or_counts, sides=sides)
    return count_dice(list(dice_or_counts), sides=sides)


def has_n_of_a_kind(
    dice_or_counts: Iterable[int] | Mapping[int, int],
    count: int,
    value: int | None = None,
    *,
    sides: int = 6,
) -> bool:
    """Return True if there are ``count`` or more of ``value`` (or any value)."""
    counts = _coerce_counts(dice_or_counts, sides=sides)
    if value is not None:
        return counts.get(value, 0) >= count
    return any(v >= count for v in counts.values())


def count_exact_matches(
    dice_or_counts: Iterable[int] | Mapping[int, int],
    exact: int,
    *,
    sides: int = 6,
) -> int:
    """Count how many distinct values appear exactly ``exact`` times."""
    counts = _coerce_counts(dice_or_counts, sides=sides)
    return sum(1 for v in counts.values() if v == exact)


def has_consecutive_run(
    dice_or_counts: Iterable[int] | Mapping[int, int],
    length: int,
    *,
    min_value: int = 1,
    max_value: int | None = None,
    require_unique: bool = False,
    sides: int = 6,
) -> bool:
    """Return True if there is a run of ``length`` consecutive values."""
    counts = _coerce_counts(dice_or_counts, sides=sides)
    if not max_value:
        max_value = max(counts.keys(), default=0)
    run = 0
    for value in range(min_value, max_value + 1):
        count = counts.get(value, 0)
        if count > 0 and (not require_unique or count == 1):
            run += 1
            if run >= length:
                return True
        else:
            run = 0
    return False


def has_full_house(
    dice_or_counts: Iterable[int] | Mapping[int, int],
    *,
    allow_five_kind: bool = False,
    sides: int = 6,
) -> bool:
    """Return True if counts contain a 3-of-a-kind and a pair (optionally 5-kind)."""
    counts = _coerce_counts(dice_or_counts, sides=sides)
    has_three = any(v == 3 for v in counts.values())
    has_two = any(v == 2 for v in counts.values())
    if has_three and has_two:
        return True
    if allow_five_kind and any(v == 5 for v in counts.values()):
        return True
    return False


__all__ = [
    "DiceSet",
    "roll_dice",
    "roll_die",
    "count_dice",
    "has_n_of_a_kind",
    "count_exact_matches",
    "has_consecutive_run",
    "has_full_house",
]
