"""
Humanity Cards Game Implementation for PlayPalace v11.

A party game where a judge reads a black card prompt and other players
submit white cards to fill in blanks. The judge picks the funniest submission.
"""

from dataclasses import dataclass, field
from datetime import datetime
import json
import random
from pathlib import Path

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import (
    IntOption,
    MenuOption,
    MultiSelectOption,
    multi_select_field,
    option_field,
)
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


# ==========================================================================
# Pack loading (cached globally)
# ==========================================================================

_humanity_packs: list[dict] | None = None


def load_humanity_packs() -> list[dict]:
    """Load card packs from JSON file. Results are cached."""
    global _humanity_packs
    if _humanity_packs is None:
        packs_path = Path(__file__).parent / "humanity_packs.json"
        with open(packs_path, "r", encoding="utf-8") as f:
            _humanity_packs = json.load(f)
    return _humanity_packs


def get_pack_names() -> list[str]:
    """Get list of all pack names."""
    return [pack["name"] for pack in load_humanity_packs()]


def get_pack_groups() -> dict[str, list[str]]:
    """Get preset groupings of packs for the options UI."""
    all_names = get_pack_names()

    # Define groups based on known pack prefixes/names
    base_set = []
    base_plus_expansions = []
    family_edition = []
    holiday_packs = []
    nostalgia_packs = []

    for name in all_names:
        lower = name.lower()
        if name == "CAH Base Set":
            base_set.append(name)
            base_plus_expansions.append(name)
        elif lower.startswith("cah:") and "expansion" in lower:
            base_plus_expansions.append(name)
        elif "family" in lower:
            family_edition.append(name)
        elif (
            "holiday" in lower
            or "christmas" in lower
            or "greeting" in lower
            or "seasons" in lower
            or "hanukkah" in lower
        ):
            holiday_packs.append(name)
        elif "nostalgia" in lower or "90s" in lower or "2000s" in lower:
            nostalgia_packs.append(name)

    # base_set group also includes base + official expansions
    if not base_set:
        # Fallback: first pack is base
        base_set = [all_names[0]] if all_names else []
    if not base_plus_expansions:
        base_plus_expansions = list(base_set)

    groups = {"All Packs": all_names}
    if base_set:
        groups["Base Set"] = base_set
    if base_plus_expansions:
        groups["Base + Expansions"] = base_plus_expansions
    if family_edition:
        groups["Family Edition"] = family_edition
    if holiday_packs:
        groups["Holiday Packs"] = holiday_packs
    if nostalgia_packs:
        groups["Nostalgia Packs"] = nostalgia_packs

    return groups


def _get_default_packs() -> list[str]:
    """Get default selected packs (Base Set group)."""
    groups = get_pack_groups()
    return list(groups.get("Base Set", get_pack_names()[:1]))


# ==========================================================================
# Card ID counter
# ==========================================================================

_next_card_id = 0


def _make_card_id() -> int:
    """Generate a unique card ID for this session."""
    global _next_card_id
    _next_card_id += 1
    return _next_card_id


# ==========================================================================
# Player and Options
# ==========================================================================


@dataclass
class HumanityCardsPlayer(Player):
    """Player state for Humanity Cards game."""

    score: int = 0
    hand: list[dict] = field(default_factory=list)  # {"text": str, "pack": str, "id": int}
    submitted_cards: list[str] | None = None  # Text of submitted cards (None = not submitted)
    selected_indices: list[int] = field(default_factory=list)  # Indices into hand


@dataclass
class HumanityCardsOptions(GameOptions):
    """Options for Humanity Cards game."""

    winning_score: int = option_field(
        IntOption(
            default=7,
            min_val=3,
            max_val=20,
            value_key="score",
            label="hc-set-winning-score",
            prompt="hc-enter-winning-score",
            change_msg="hc-option-changed-winning-score",
            description="hc-desc-winning-score",
        )
    )
    hand_size: int = option_field(
        IntOption(
            default=10,
            min_val=5,
            max_val=15,
            value_key="count",
            label="hc-set-hand-size",
            prompt="hc-enter-hand-size",
            change_msg="hc-option-changed-hand-size",
            description="hc-desc-hand-size",
        )
    )
    card_packs: list[str] = multi_select_field(
        MultiSelectOption(
            default=_get_default_packs(),
            choices=get_pack_names,
            label="hc-set-card-packs",
            change_msg="hc-option-changed-card-packs",
            min_selected=1,
            show_bulk_actions=True,
            groups=get_pack_groups,
            description="hc-desc-card-packs",
        )
    )
    czar_selection: str = option_field(
        MenuOption(
            default="Rotating",
            choices=["Rotating", "Random", "Most Recent Winner"],
            value_key="mode",
            label="hc-set-czar-selection",
            prompt="hc-select-czar-selection",
            change_msg="hc-option-changed-czar-selection",
            choice_labels={
                "Rotating": "hc-czar-rotating",
                "Random": "hc-czar-random",
                "Most Recent Winner": "hc-czar-winner",
            },
        )
    )
    num_judges: int = option_field(
        IntOption(
            default=1,
            min_val=1,
            max_val=3,
            value_key="count",
            label="hc-set-num-judges",
            prompt="hc-enter-num-judges",
            change_msg="hc-option-changed-num-judges",
        )
    )


# ==========================================================================
# Game
# ==========================================================================


@dataclass
@register_game
class HumanityCardsGame(Game):
    """
    Humanity Cards party game.

    Players take turns as the Card Czar. A black card prompt is read, and
    other players submit white cards to fill in the blanks. The Card Czar
    picks the funniest submission and that player scores a point.
    """

    players: list[HumanityCardsPlayer] = field(default_factory=list)
    options: HumanityCardsOptions = field(default_factory=HumanityCardsOptions)

    # Game state
    phase: str = "waiting"  # waiting, submitting, judging, round_end
    white_deck: list[dict] = field(default_factory=list)
    black_deck: list[dict] = field(default_factory=list)
    white_discard: list[dict] = field(default_factory=list)
    black_discard: list[dict] = field(default_factory=list)
    current_black_card: dict | None = None  # {"text": str, "pick": int, "pack": str}
    judge_indices: list[int] = field(default_factory=list)  # Indices into active players
    last_winner_index: int = -1  # For "Most Recent Winner" czar selection
    submissions: list[dict] = field(default_factory=list)  # [{"player_id": str, "cards": [str]}]
    submission_order: list[int] = field(default_factory=list)  # Shuffled indices into submissions
    round_end_ticks: int = 0  # Countdown ticks before next round starts

    @classmethod
    def get_name(cls) -> str:
        return "Cards Against Humanity"

    @classmethod
    def get_type(cls) -> str:
        return "humanitycards"

    @classmethod
    def get_category(cls) -> str:
        return "category-party-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 3

    @classmethod
    def get_max_players(cls) -> int:
        return 10

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> HumanityCardsPlayer:
        return HumanityCardsPlayer(id=player_id, name=name, is_bot=is_bot)

    # ==========================================================================
    # Deck management
    # ==========================================================================

    def _get_active_packs(self) -> list[str]:
        """Get the list of selected pack names."""
        return list(self.options.card_packs)

    def _build_decks(self) -> None:
        """Build white and black decks from selected packs."""
        packs = load_humanity_packs()
        active_pack_names = set(self._get_active_packs())

        self.white_deck = []
        self.black_deck = []
        self.white_discard = []
        self.black_discard = []

        for pack in packs:
            if pack["name"] not in active_pack_names:
                continue
            pack_name = pack["name"]

            for card in pack.get("white", []):
                text = card["text"].rstrip(".")
                self.white_deck.append(
                    {
                        "text": text,
                        "pack": pack_name,
                        "id": _make_card_id(),
                    }
                )

            for card in pack.get("black", []):
                text = card["text"]
                pick = text.count("_")
                if pick == 0:
                    pick = 1  # Cards with no blanks get 1 pick
                self.black_deck.append(
                    {
                        "text": text,
                        "pick": pick,
                        "pack": pack_name,
                    }
                )

        random.shuffle(self.white_deck)  # nosec B311
        random.shuffle(self.black_deck)  # nosec B311

    def _draw_white(self, count: int = 1) -> list[dict]:
        """Draw white cards from the deck, reshuffling discard if needed."""
        cards = []
        for _ in range(count):
            if not self.white_deck:
                if self.white_discard:
                    self.white_deck = list(self.white_discard)
                    self.white_discard = []
                    random.shuffle(self.white_deck)  # nosec B311
                    self.broadcast_l("hc-deck-reshuffled")
                else:
                    break  # No cards available
            if self.white_deck:
                cards.append(self.white_deck.pop())
        return cards

    def _draw_black(self) -> dict | None:
        """Draw a black card from the deck, reshuffling discard if needed."""
        if not self.black_deck:
            if self.black_discard:
                self.black_deck = list(self.black_discard)
                self.black_discard = []
                random.shuffle(self.black_deck)  # nosec B311
                self.broadcast_l("hc-black-deck-reshuffled")
            else:
                return None
        return self.black_deck.pop() if self.black_deck else None

    def _deal_to_hand_size(self, player: HumanityCardsPlayer) -> None:
        """Fill a player's hand up to the hand size."""
        needed = self.options.hand_size - len(player.hand)
        if needed > 0:
            cards = self._draw_white(needed)
            player.hand.extend(cards)

    def _fill_in_blanks(self, black_text: str, white_cards: list[str]) -> str:
        """Replace underscores in black card with white card texts."""
        result = black_text
        for card_text in white_cards:
            # Trim trailing period from white card for insertion
            insert = card_text.rstrip(".")
            if "_" in result:
                result = result.replace("_", insert, 1)
            else:
                result += f" {insert}"
        return result

    def _speech_friendly_black(self, text: str) -> str:
        """Replace underscores with 'blank' for screen reader speech."""
        return text.replace("_", "blank")

    # ==========================================================================
    # Judge management (supports multiple judges)
    # ==========================================================================

    def _is_judge(self, player: HumanityCardsPlayer) -> bool:
        """Check if a player is one of the current judges."""
        active = self.get_active_players()
        for idx in self.judge_indices:
            if idx < len(active) and active[idx].id == player.id:
                return True
        return False

    def _get_judges(self) -> list[HumanityCardsPlayer]:
        """Get all current judge players."""
        active = self.get_active_players()
        judges = []
        for idx in self.judge_indices:
            if idx < len(active):
                judges.append(active[idx])
        return judges

    def _get_non_judges(self) -> list[HumanityCardsPlayer]:
        """Get all non-judge active players."""
        judge_ids = {j.id for j in self._get_judges()}
        return [p for p in self.get_active_players() if p.id not in judge_ids]

    def _select_judges(self) -> None:
        """Select judge(s) for the current round based on czar_selection option."""
        active = self.get_active_players()
        num_judges = min(self.options.num_judges, len(active) - 1)  # At least 1 non-judge
        if num_judges < 1:
            num_judges = 1

        mode = self.options.czar_selection

        if mode == "Random":
            indices = list(range(len(active)))
            random.shuffle(indices)  # nosec B311
            self.judge_indices = indices[:num_judges]
        elif mode == "Most Recent Winner":
            if self.last_winner_index >= 0 and self.last_winner_index < len(active):
                self.judge_indices = [self.last_winner_index]
                # Fill additional judges rotating from winner
                if num_judges > 1:
                    for offset in range(1, len(active)):
                        if len(self.judge_indices) >= num_judges:
                            break
                        idx = (self.last_winner_index + offset) % len(active)
                        self.judge_indices.append(idx)
            else:
                # Fallback to rotating for first round
                self._select_judges_rotating(active, num_judges)
        else:
            # Rotating (default)
            self._select_judges_rotating(active, num_judges)

    def _select_judges_rotating(self, active: list[HumanityCardsPlayer], num_judges: int) -> None:
        """Rotating judge selection: advance from current position."""
        if not self.judge_indices:
            self.judge_indices = [0]
        else:
            # Advance the first judge index
            first = (self.judge_indices[0] + 1) % len(active)
            self.judge_indices = [first]

        # Fill additional judge slots
        while len(self.judge_indices) < num_judges:
            next_idx = (self.judge_indices[-1] + 1) % len(active)
            if next_idx in self.judge_indices:
                break
            self.judge_indices.append(next_idx)

    # ==========================================================================
    # Action set creation
    # ==========================================================================

    def create_turn_action_set(self, player: HumanityCardsPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Card toggle actions (0-14) — non-judges during submitting
        for i in range(15):
            action_set.add(
                Action(
                    id=f"toggle_card_{i}",
                    label=f"Card {i + 1}",
                    handler=f"_action_toggle_card_{i}",
                    is_enabled="_is_toggle_card_enabled",
                    is_hidden="_is_toggle_card_hidden",
                    get_label="_get_toggle_card_label",
                    get_sound="_get_toggle_card_sound",
                    show_in_actions_menu=False,
                )
            )

        # Judge prompt header (static, non-actionable) — shown at top of judge menu
        action_set.add(
            Action(
                id="judge_prompt_header",
                label="Choose the best card",
                handler="_action_noop",
                is_enabled="_is_judge_prompt_header_enabled",
                is_hidden="_is_judge_prompt_header_hidden",
                get_label="_get_judge_prompt_header_label",
                show_in_actions_menu=False,
            )
        )

        # Judge pick actions (0-19) — judges during judging, inline in menu
        for i in range(20):
            action_set.add(
                Action(
                    id=f"judge_pick_{i}",
                    label=f"Submission {i + 1}",
                    handler=f"_action_judge_pick_{i}",
                    is_enabled="_is_judge_pick_enabled",
                    is_hidden="_is_judge_pick_hidden",
                    get_label="_get_judge_pick_label",
                    show_in_actions_menu=False,
                )
            )

        # View submission (above submit for non-judges)
        action_set.add(
            Action(
                id="view_submission",
                label=Localization.get(locale, "hc-preview-submission"),
                handler="_action_view_submission",
                is_enabled="_is_view_submission_enabled",
                is_hidden="_is_view_submission_hidden",
                get_label="_get_view_submission_label",
                show_in_actions_menu=True,
            )
        )

        # Submit cards
        action_set.add(
            Action(
                id="submit_cards",
                label=Localization.get(locale, "hc-submit-cards", selected=0, required=1),
                handler="_action_submit_cards",
                is_enabled="_is_submit_enabled",
                is_hidden="_is_submit_hidden",
                get_label="_get_submit_label",
            )
        )

        # View black card
        action_set.add(
            Action(
                id="view_black_card",
                label=Localization.get(locale, "hc-view-black-card"),
                handler="_action_view_black_card",
                is_enabled="_is_view_enabled",
                is_hidden="_is_view_hidden",
                show_in_actions_menu=True,
            )
        )

        # View scores (always visible at bottom)
        action_set.add(
            Action(
                id="view_scores",
                label=Localization.get(locale, "hc-view-scores"),
                handler="_action_view_scores",
                is_enabled="_is_view_scores_enabled",
                is_hidden="_is_view_scores_hidden",
                show_in_actions_menu=True,
            )
        )

        # Whose judge (keybind-only, J key)
        action_set.add(
            Action(
                id="whose_judge",
                label=Localization.get(locale, "hc-whose-judge"),
                handler="_action_whose_judge",
                is_enabled="_is_view_scores_enabled",
                is_hidden="_is_whose_judge_hidden",
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Number keys 1-9, 0 for cards 1-10
        for i in range(10):
            key = str((i + 1) % 10)  # 1,2,3,...,9,0
            self.define_keybind(
                key,
                f"Toggle card {i + 1}",
                [f"toggle_card_{i}"],
                state=KeybindState.ACTIVE,
            )

        # Space to submit
        self.define_keybind(
            "space",
            "Submit cards",
            ["submit_cards"],
            state=KeybindState.ACTIVE,
        )

        # C to view black card
        self.define_keybind(
            "c",
            "View prompt",
            ["view_black_card"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # V to view/preview submission
        self.define_keybind(
            "v",
            "View submission",
            ["view_submission"],
            state=KeybindState.ACTIVE,
        )

        # S to view scores
        self.define_keybind(
            "s",
            "View scores",
            ["view_scores"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # J to announce judges
        self.define_keybind(
            "j",
            "Who is judging",
            ["whose_judge"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # is_enabled callbacks
    # ==========================================================================

    def _is_toggle_card_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "action-spectator"
        if hcp.submitted_cards is not None:
            return "hc-already-submitted"
        if self.phase != "submitting":
            return "action-not-playing"
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx >= len(hcp.hand):
            return "action-not-playing"
        return None

    def _is_toggle_card_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.phase != "submitting":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        if hcp.submitted_cards is not None:
            return Visibility.HIDDEN
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx >= len(hcp.hand):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_toggle_card_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx >= len(hcp.hand):
            return f"Card {idx + 1}"
        card = hcp.hand[idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if idx in hcp.selected_indices:
            return Localization.get(locale, "hc-card-selected", text=card["text"])
        return Localization.get(locale, "hc-card-not-selected", text=card["text"])

    def _get_toggle_card_sound(self, player: Player, action_id: str) -> str | None:
        hcp: HumanityCardsPlayer = player  # type: ignore
        idx = int(action_id.removeprefix("toggle_card_"))
        if idx in hcp.selected_indices:
            return "game_humanitycards/cardselect.ogg"
        return None

    def _is_submit_enabled(self, player: Player) -> str | tuple[str, dict] | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "action-spectator"
        if hcp.submitted_cards is not None:
            return "hc-already-submitted"
        if self.phase != "submitting":
            return "action-not-playing"
        required = self.current_black_card["pick"] if self.current_black_card else 1
        if len(hcp.selected_indices) != required:
            return ("hc-wrong-card-count", {"count": required})
        return None

    def _is_submit_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.phase != "submitting":
            return Visibility.HIDDEN
        if player.is_spectator:
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        if hcp.submitted_cards is not None:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_submit_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        required = self.current_black_card["pick"] if self.current_black_card else 1
        return Localization.get(
            locale,
            "hc-submit-cards",
            selected=len(hcp.selected_indices),
            required=required,
        )

    # ==========================================================================
    # Judge pick callbacks (inline submission selection)
    # ==========================================================================

    def _is_judge_pick_enabled(self, player: Player, action_id: str) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return "action-spectator"
        if self.phase != "judging":
            return "action-not-playing"
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx >= len(self.submission_order):
            return "action-not-playing"
        return None

    def _is_judge_pick_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.phase != "judging":
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return Visibility.HIDDEN
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx >= len(self.submission_order):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_judge_pick_label(self, player: Player, action_id: str) -> str:
        idx = int(action_id.removeprefix("judge_pick_"))
        if idx < len(self.submission_order):
            sub_idx = self.submission_order[idx]
            if sub_idx < len(self.submissions):
                sub = self.submissions[sub_idx]
                if self.current_black_card:
                    return self._fill_in_blanks(self.current_black_card["text"], sub["cards"])
                return ", ".join(sub["cards"])
        return f"Submission {idx + 1}"

    # ==========================================================================
    # Judge prompt header callbacks (static text)
    # ==========================================================================

    def _action_noop(self, player: Player, action_id: str) -> None:
        """No-op handler for static text actions."""
        pass

    def _is_judge_prompt_header_enabled(self, player: Player, action_id: str) -> str | None:
        return None

    def _is_judge_prompt_header_hidden(self, player: Player, action_id: str) -> Visibility:
        if self.status != "playing" or self.phase != "judging":
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_judge_prompt_header_label(self, player: Player, action_id: str) -> str:
        if self.current_black_card:
            prompt_text = self._speech_friendly_black(self.current_black_card["text"])
            return f"Choose the best card that matches: {prompt_text}"
        return "Choose the best card"

    def _get_submission_options(self, player: Player) -> list[str]:
        """Get submission options for judge's menu."""
        options = []
        for idx in self.submission_order:
            if idx < len(self.submissions):
                sub = self.submissions[idx]
                if self.current_black_card:
                    filled = self._fill_in_blanks(self.current_black_card["text"], sub["cards"])
                else:
                    filled = ", ".join(sub["cards"])
                options.append(filled)
        return options

    # ==========================================================================
    # View scores callbacks
    # ==========================================================================

    def _is_view_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_scores_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _action_view_scores(self, player: Player, action_id: str) -> None:
        """View the current scores."""
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        parts = [f"{p.name}: {p.score}" for p in sorted_players]  # type: ignore
        user.speak(". ".join(parts) + ".")

    # ==========================================================================
    # Whose judge / whose turn overrides
    # ==========================================================================

    def _is_whose_judge_hidden(self, player: Player) -> Visibility:
        # Keybind-only — always hidden from menu
        return Visibility.HIDDEN

    def _action_whose_judge(self, player: Player, action_id: str) -> None:
        """Announce who the current judge(s) are."""
        user = self.get_user(player)
        if not user:
            return
        judges = self._get_judges()
        if len(judges) == 1:
            user.speak_l("hc-judge-is", player=judges[0].name, count=1, others="")
        elif judges:
            others = ", ".join(j.name for j in judges[1:])
            user.speak_l("hc-judge-is", player=judges[0].name, count=len(judges), others=others)

    def _action_whose_turn(self, player: Player, action_id: str) -> None:
        """Override default whose_turn to show submission status."""
        user = self.get_user(player)
        if not user:
            return

        judges = self._get_judges()
        judge_names = ", ".join(j.name for j in judges)

        if self.phase == "submitting":
            # List who hasn't submitted
            waiting = [p.name for p in self._get_non_judges() if p.submitted_cards is None]
            if waiting:
                user.speak_l("hc-waiting-for", names=", ".join(waiting))
            else:
                user.speak_l("hc-all-submitted-waiting-judge", judge=judge_names)
        elif self.phase == "judging":
            user.speak_l("hc-all-submitted-waiting-judge", judge=judge_names)
        else:
            user.speak_l("game-no-turn")

    def _is_view_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or self.current_black_card is None:
            return Visibility.HIDDEN
        # Hide for judges during judging — prompt is shown in the header
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase == "judging" and self._is_judge(hcp):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_view_submission_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return "action-spectator"
        if self.phase != "submitting" and self.phase != "judging":
            return "action-not-playing"
        # During submitting: enabled if at least one card selected or already submitted
        if hcp.submitted_cards is None and not hcp.selected_indices:
            return "hc-select-cards-first"
        return None

    def _is_view_submission_hidden(self, player: Player) -> Visibility:
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.phase not in ("submitting", "judging"):
            return Visibility.HIDDEN
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self._is_judge(hcp):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _get_view_submission_label(self, player: Player, action_id: str) -> str:
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if hcp.submitted_cards is not None:
            return Localization.get(locale, "hc-view-submission")
        return Localization.get(locale, "hc-preview-submission")

    # ==========================================================================
    # Toggle card action handlers (0-14)
    # ==========================================================================

    def _toggle_card(self, player: Player, index: int) -> None:
        """Toggle card selection for submission."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase != "submitting" or hcp.submitted_cards is not None:
            return
        if self._is_judge(hcp):
            return
        if index >= len(hcp.hand):
            return

        required = self.current_black_card["pick"] if self.current_black_card else 1

        user = self.get_user(player)
        if index in hcp.selected_indices:
            hcp.selected_indices.remove(index)
            if user:
                user.play_sound("game_humanitycards/cardunselect.ogg")
        else:
            if len(hcp.selected_indices) >= required:
                # Deselect first to make room
                hcp.selected_indices.pop(0)
            hcp.selected_indices.append(index)
            if user:
                user.play_sound("game_humanitycards/cardselect.ogg")

        self.rebuild_player_menu(player)

    # Per-index toggle handlers
    def _action_toggle_card_0(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 0)

    def _action_toggle_card_1(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 1)

    def _action_toggle_card_2(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 2)

    def _action_toggle_card_3(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 3)

    def _action_toggle_card_4(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 4)

    def _action_toggle_card_5(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 5)

    def _action_toggle_card_6(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 6)

    def _action_toggle_card_7(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 7)

    def _action_toggle_card_8(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 8)

    def _action_toggle_card_9(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 9)

    def _action_toggle_card_10(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 10)

    def _action_toggle_card_11(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 11)

    def _action_toggle_card_12(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 12)

    def _action_toggle_card_13(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 13)

    def _action_toggle_card_14(self, player: Player, action_id: str) -> None:
        self._toggle_card(player, 14)

    # Per-index judge pick handlers
    def _action_judge_pick_0(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 0)

    def _action_judge_pick_1(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 1)

    def _action_judge_pick_2(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 2)

    def _action_judge_pick_3(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 3)

    def _action_judge_pick_4(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 4)

    def _action_judge_pick_5(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 5)

    def _action_judge_pick_6(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 6)

    def _action_judge_pick_7(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 7)

    def _action_judge_pick_8(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 8)

    def _action_judge_pick_9(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 9)

    def _action_judge_pick_10(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 10)

    def _action_judge_pick_11(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 11)

    def _action_judge_pick_12(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 12)

    def _action_judge_pick_13(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 13)

    def _action_judge_pick_14(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 14)

    def _action_judge_pick_15(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 15)

    def _action_judge_pick_16(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 16)

    def _action_judge_pick_17(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 17)

    def _action_judge_pick_18(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 18)

    def _action_judge_pick_19(self, player: Player, action_id: str) -> None:
        self._judge_pick(player, 19)

    # ==========================================================================
    # Submit / Judge action handlers
    # ==========================================================================

    def _action_submit_cards(self, player: Player, action_id: str) -> None:
        """Submit selected cards."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        if self.phase != "submitting" or hcp.submitted_cards is not None:
            return
        if self._is_judge(hcp):
            return

        required = self.current_black_card["pick"] if self.current_black_card else 1
        if len(hcp.selected_indices) != required:
            user = self.get_user(player)
            if user:
                user.speak_l("hc-wrong-card-count", count=required)
            return

        # Collect submitted card texts
        submitted_texts = []
        # Sort indices in selection order (the order they were picked)
        for idx in hcp.selected_indices:
            if idx < len(hcp.hand):
                card = hcp.hand[idx]
                submitted_texts.append(card["text"])

        hcp.submitted_cards = submitted_texts

        # Remove submitted cards from hand (highest index first to avoid shift)
        for idx in sorted(hcp.selected_indices, reverse=True):
            if idx < len(hcp.hand):
                removed = hcp.hand.pop(idx)
                self.white_discard.append(removed)

        hcp.selected_indices = []

        # Sound + announcement
        self.play_sound(f"game_humanitycards/submit{random.randint(1, 2)}.ogg")  # nosec B311
        user = self.get_user(player)
        if user:
            user.speak_l("hc-submitted")

        # Broadcast progress
        non_judges = self._get_non_judges()
        submitted_count = sum(1 for p in non_judges if p.submitted_cards is not None)
        total = len(non_judges)
        self.broadcast_l(
            "hc-submission-progress",
            submitted=submitted_count,
            total=total,
        )

        self.rebuild_all_menus()

        # Check if all have submitted
        if submitted_count >= total:
            self._start_judging()

    def _judge_pick(self, player: Player, pick_index: int) -> None:
        """Judge picks a submission by its display index."""
        if self.phase != "judging":
            return
        hcp: HumanityCardsPlayer = player  # type: ignore
        if not self._is_judge(hcp):
            return
        if pick_index >= len(self.submission_order):
            return
        actual_idx = self.submission_order[pick_index]
        if actual_idx >= len(self.submissions):
            return

        winning_sub = self.submissions[actual_idx]
        winner = self.get_player_by_id(winning_sub["player_id"])
        if not winner:
            return

        hc_winner: HumanityCardsPlayer = winner  # type: ignore

        # Award point
        hc_winner.score += 1
        active = self.get_active_players()
        self.last_winner_index = next((i for i, p in enumerate(active) if p.id == winner.id), -1)

        # Announce winner
        winning_text = self._fill_in_blanks(
            self.current_black_card["text"] if self.current_black_card else "",
            winning_sub["cards"],
        )

        # Play judge choice sound
        self.play_sound(
            f"game_humanitycards/judgechoice{random.randint(1, 3)}.ogg"  # nosec B311
        )

        self.broadcast_l(
            "hc-winner-announcement",
            player=winner.name,
            score=hc_winner.score,
        )

        # Announce winner's submission first
        self.broadcast_l(
            "hc-submission-reveal",
            player=winner.name,
            text=winning_text,
        )

        # Then announce other submissions
        self.broadcast_l("hc-all-submissions")
        for sub in self.submissions:
            if sub["player_id"] == winner.id:
                continue
            sub_player = self.get_player_by_id(sub["player_id"])
            if sub_player:
                filled = self._fill_in_blanks(
                    self.current_black_card["text"] if self.current_black_card else "",
                    sub["cards"],
                )
                self.broadcast_l(
                    "hc-submission-reveal",
                    player=sub_player.name,
                    text=filled,
                )

        # Play draw card sound as players receive new cards
        self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")  # nosec B311

        # Check win condition
        if hc_winner.score >= self.options.winning_score:
            self._end_game(hc_winner)
        else:
            # Transition to round_end with delay before next round
            self.phase = "round_end"
            self.round_end_ticks = 100  # ~5 seconds at 20 ticks/sec

            # Discard current black card
            if self.current_black_card:
                self.black_discard.append(self.current_black_card)
                self.current_black_card = None

            self.rebuild_all_menus()

    def _action_view_black_card(self, player: Player, action_id: str) -> None:
        """View the current black card prompt."""
        user = self.get_user(player)
        if not user or not self.current_black_card:
            return
        text = self._speech_friendly_black(self.current_black_card["text"])
        user.speak_l("hc-black-card", text=text)

    def _action_view_submission(self, player: Player, action_id: str) -> None:
        """View the player's submitted or in-progress submission."""
        hcp: HumanityCardsPlayer = player  # type: ignore
        user = self.get_user(player)
        if not user:
            return

        if hcp.submitted_cards is not None and self.current_black_card:
            filled = self._fill_in_blanks(self.current_black_card["text"], hcp.submitted_cards)
            user.speak_l("hc-your-submission", text=filled)
        elif hcp.selected_indices and self.current_black_card:
            # Preview current selection
            cards = [hcp.hand[i]["text"] for i in hcp.selected_indices if i < len(hcp.hand)]
            filled = self._fill_in_blanks(self.current_black_card["text"], cards)
            user.speak_l("hc-preview-submission-text", text=filled)
        else:
            user.speak_l("hc-select-cards-first")

    # ==========================================================================
    # Score overrides
    # ==========================================================================

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        parts = [f"{p.name}: {p.score}" for p in sorted_players]  # type: ignore
        user.speak(". ".join(parts) + ".")

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        sorted_players = sorted(
            self.get_active_players(),
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )
        lines = [
            f"{p.name}: {p.score} points"  # type: ignore
            for p in sorted_players
        ]
        self.status_box(player, lines)

    # ==========================================================================
    # Game lifecycle
    # ==========================================================================

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0
        self.judge_indices = []
        self.last_winner_index = -1

        # Build decks
        self._build_decks()

        active_players = self.get_active_players()

        # Check we have enough cards
        total_whites_needed = len(active_players) * self.options.hand_size
        if len(self.white_deck) < total_whites_needed:
            self.broadcast_l("hc-not-enough-cards")

        # Reset player state
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            hp.score = 0
            hp.hand = []
            hp.submitted_cards = None
            hp.selected_indices = []

        # Deal initial hands
        self.broadcast_l("hc-game-starting")
        self.broadcast_l("hc-dealing-cards", count=self.options.hand_size)
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            self._deal_to_hand_size(hp)

        # Play music
        self.play_music("game_3cardpoker/mus.ogg")

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1
        self.phase = "submitting"
        self.submissions = []
        self.submission_order = []

        # Play card shuffle sound at round start
        self.play_sound("game_3cardpoker/roundstart.ogg")

        active_players = self.get_active_players()

        # Reset player submission state
        for p in active_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            hp.submitted_cards = None
            hp.selected_indices = []
            # Refill hand
            self._deal_to_hand_size(hp)

        # Select judge(s)
        self._select_judges()

        # Draw black card
        self.current_black_card = self._draw_black()
        if not self.current_black_card:
            self.broadcast_l("hc-not-enough-cards")
            self.finish_game()
            return

        pick_count = self.current_black_card.get("pick", 1)

        # Announce round
        self.broadcast_l("hc-round-start", round=self.round)

        # Announce judge(s)
        judges = self._get_judges()
        if len(judges) == 1:
            self.broadcast_l("hc-judge-is", player=judges[0].name, count=1, others="")
        else:
            others = ", ".join(j.name for j in judges[1:])
            self.broadcast_l("hc-judge-is", player=judges[0].name, count=len(judges), others=others)

        # Announce black card
        black_text = self._speech_friendly_black(self.current_black_card["text"])
        self.broadcast_l("hc-black-card", text=black_text)
        if pick_count > 1:
            self.broadcast_l("hc-black-card-pick", count=pick_count)

        # Tell non-judges to select cards
        for p in self._get_non_judges():
            user = self.get_user(p)
            if user:
                user.speak_l("hc-select-cards", count=pick_count)

        # Jolt bots
        for p in active_players:
            if p.is_bot and not self._is_judge(p):
                BotHelper.jolt_bot(p, ticks=random.randint(20, 40))  # nosec B311

        self.rebuild_all_menus()

    def _start_judging(self) -> None:
        """Transition to judging phase."""
        self.phase = "judging"

        # Collect submissions
        self.submissions = []
        for p in self._get_non_judges():
            if p.submitted_cards is not None:
                self.submissions.append(
                    {
                        "player_id": p.id,
                        "cards": list(p.submitted_cards),
                    }
                )

        # Shuffle presentation order
        self.submission_order = list(range(len(self.submissions)))
        random.shuffle(self.submission_order)  # nosec B311

        self.play_sound("game_humanitycards/judging.ogg")
        self.broadcast_l("hc-judging-start")

        # Jolt judge bots
        for j in self._get_judges():
            if j.is_bot:
                BotHelper.jolt_bot(j, ticks=random.randint(30, 50))  # nosec B311

        self.rebuild_all_menus()

    def _end_game(self, winner: HumanityCardsPlayer) -> None:
        """End the game and announce the winner."""
        self.play_sound("game_humanitycards/win.ogg")
        self.broadcast_personal_l(
            winner,
            "hc-you-win",
            "hc-game-winner",
            score=winner.score,
        )
        self.finish_game()

    # ==========================================================================
    # Bot AI
    # ==========================================================================

    def bot_think(self, player: HumanityCardsPlayer) -> str | None:
        """Bot AI decision making."""
        if self.phase == "submitting" and not self._is_judge(player):
            if player.submitted_cards is not None:
                return None
            required = self.current_black_card["pick"] if self.current_black_card else 1

            # Select random cards if not enough selected
            if len(player.selected_indices) < required:
                available = [i for i in range(len(player.hand)) if i not in player.selected_indices]
                if available:
                    pick = random.choice(available)  # nosec B311
                    return f"toggle_card_{pick}"

            # Submit when we have enough
            if len(player.selected_indices) == required:
                return "submit_cards"

        return None

    def on_tick(self) -> None:
        """Called every tick."""
        super().on_tick()

        if not self.game_active:
            return

        # Round end delay before starting next round
        if self.phase == "round_end":
            self.round_end_ticks -= 1
            if self.round_end_ticks <= 0:
                self._start_round()
            return

        # Process bot actions
        if self.phase == "submitting":
            self._process_submission_bots()
        elif self.phase == "judging":
            self._process_judging_bots()

    def _process_submission_bots(self) -> None:
        """Process all bot actions during submission phase."""
        for player in self.players:
            if not player.is_bot or player.is_spectator:
                continue
            hcp: HumanityCardsPlayer = player  # type: ignore
            if self._is_judge(hcp) or hcp.submitted_cards is not None:
                continue

            BotHelper.process_bot_action(
                player,
                think_fn=lambda p=hcp: self.bot_think(p),
                execute_fn=lambda action_id, p=player: self.execute_action(p, action_id),
            )

    def _process_judging_bots(self) -> None:
        """Process judge bot actions during judging phase."""
        for judge in self._get_judges():
            if not judge.is_bot:
                continue

            if judge.bot_think_ticks > 0:
                judge.bot_think_ticks -= 1
                continue

            if judge.bot_pending_action:
                action_id = judge.bot_pending_action
                judge.bot_pending_action = None
                self.execute_action(judge, action_id)
                continue

            # Bot judge picks a random submission
            if self.submission_order:
                pick = random.randint(0, len(self.submission_order) - 1)  # nosec B311
                judge.bot_pending_action = f"judge_pick_{pick}"

    # ==========================================================================
    # Game result
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        """Build the game result."""
        active_players = self.get_active_players()
        sorted_players = sorted(
            active_players,
            key=lambda p: p.score,  # type: ignore
            reverse=True,
        )

        final_scores = {}
        for p in sorted_players:
            hp: HumanityCardsPlayer = p  # type: ignore
            final_scores[p.name] = hp.score

        winner = sorted_players[0] if sorted_players else None

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
                "winner_score": winner.score if winner else 0,  # type: ignore
                "final_scores": final_scores,
                "rounds_played": self.round,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen."""
        lines = [Localization.get(locale, "game-final-scores-header")]

        final_scores = result.custom_data.get("final_scores", {})
        for i, (name, score) in enumerate(final_scores.items(), 1):
            lines.append(f"{i}. {name}: {score}")

        return lines
