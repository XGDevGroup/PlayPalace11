"""Game lifecycle status enum."""

from enum import Enum


class GameStatus(str, Enum):
    """Game lifecycle status.

    Inherits from str so that ``GameStatus.PLAYING == "playing"`` is True,
    preserving backward compatibility with existing string comparisons.
    """

    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"
