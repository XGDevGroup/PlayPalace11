"""
Pusoy Dos Game Implementation for PlayPalace v11.

Filipino card game where players race to empty their hand by playing
increasingly powerful card combinations.  Supports elimination and
points game modes, configurable instant wins, card passing, and
penalty tiers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, BoolOption, option_field
from ...game_utils.cards import Card, Deck, DeckFactory, card_name, read_cards
from ...game_utils.turn_timer_mixin import TurnTimerMixin
from ...game_utils.poker_timer import PokerTurnTimer
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState

from .evaluator import Combo, evaluate_combo, detect_instant_win, sort_cards, card_value
from .bot import bot_think, bot_choose_give_cards

# =============================================================================
# Constants
# =============================================================================

TURN_TIMER_CHOICES = ["10", "15", "20", "30", "45", "60", "90", "0"]
TURN_TIMER_LABELS = {
    "10": "pusoydos-timer-10",
    "15": "pusoydos-timer-15",
    "20": "pusoydos-timer-20",
    "30": "pusoydos-timer-30",
    "45": "pusoydos-timer-45",
    "60": "pusoydos-timer-60",
    "90": "pusoydos-timer-90",
    "0": "pusoydos-timer-unlimited",
}

GAME_MODE_CHOICES = ["elimination", "losses", "points", "points_elimination"]
GAME_MODE_LABELS = {
    "elimination": "pusoydos-mode-elimination",
    "losses": "pusoydos-mode-losses",
    "points": "pusoydos-mode-points",
    "points_elimination": "pusoydos-mode-points-elimination",
}

CARD_PASSING_CHOICES = ["off", "simple", "full"]
CARD_PASSING_LABELS = {
    "off": "pusoydos-passing-off",
    "simple": "pusoydos-passing-simple",
    "full": "pusoydos-passing-full",
}

PENALTY_TIER_CHOICES = ["standard", "aggressive", "flat"]
PENALTY_TIER_LABELS = {
    "standard": "pusoydos-penalty-standard",
    "aggressive": "pusoydos-penalty-aggressive",
    "flat": "pusoydos-penalty-flat",
}

# Sounds
SOUND_MUSIC = "game_ninetynine/mus.ogg"
SOUND_PLAY_SINGLE = [
    "game_cards/discard1.ogg",
    "game_cards/discard2.ogg",
    "game_cards/discard3.ogg",
]
SOUND_PLAY_MULTI = [
    "game_cards/play1.ogg",
    "game_cards/play2.ogg",
    "game_cards/play3.ogg",
    "game_cards/play4.ogg",
]
SOUND_SHUFFLE = ["game_cards/shuffle1.ogg", "game_cards/shuffle2.ogg", "game_cards/shuffle3.ogg"]
SOUND_DEAL = [
    "game_cards/draw1.ogg",
    "game_cards/draw2.ogg",
    "game_cards/draw3.ogg",
    "game_cards/draw4.ogg",
]
SOUND_WIN_ROUND = "game_uno/winround.ogg"
SOUND_LOSE_ROUND = "game_uno/loseround.ogg"
SOUND_WIN_GAME = "game_uno/wingame.ogg"
SOUND_INSTANT_WIN = "game_coup/challengesuccess.ogg"
SOUND_YOUR_TURN = "turn.ogg"
SOUND_ELIMINATED = "game_uno/winround.ogg"


# =============================================================================
# Options
# =============================================================================


@dataclass
class PusoyDosOptions(GameOptions):
    game_mode: str = option_field(
        MenuOption(
            choices=GAME_MODE_CHOICES,
            choice_labels=GAME_MODE_LABELS,
            default="elimination",
            value_key="choice",
            label="pusoydos-set-game-mode",
            prompt="pusoydos-select-game-mode",
            change_msg="pusoydos-option-changed-game-mode",
            description="pusoydos-desc-game-mode",
        )
    )
    rounds_to_win: int = option_field(
        IntOption(
            default=2,
            min_val=1,
            max_val=10,
            value_key="count",
            label="pusoydos-set-rounds-to-win",
            prompt="pusoydos-enter-rounds-to-win",
            change_msg="pusoydos-option-changed-rounds-to-win",
            description="pusoydos-desc-rounds-to-win",
        ),
        visible_when=("game_mode", lambda v: v == "elimination"),
    )
    losses_to_lose: int = option_field(
        IntOption(
            default=3,
            min_val=1,
            max_val=10,
            value_key="count",
            label="pusoydos-set-losses-to-lose",
            prompt="pusoydos-enter-losses-to-lose",
            change_msg="pusoydos-option-changed-losses-to-lose",
            description="pusoydos-desc-losses-to-lose",
        ),
        visible_when=("game_mode", lambda v: v == "losses"),
    )
    target_score: int = option_field(
        IntOption(
            default=100,
            min_val=10,
            max_val=10000,
            value_key="score",
            label="pusoydos-set-target-score",
            prompt="pusoydos-enter-target-score",
            change_msg="pusoydos-option-changed-target-score",
            description="pusoydos-desc-target-score",
        ),
        visible_when=("game_mode", lambda v: v in ("points", "points_elimination")),
    )
    turn_timer: str = option_field(
        MenuOption(
            choices=TURN_TIMER_CHOICES,
            choice_labels=TURN_TIMER_LABELS,
            default="0",
            value_key="choice",
            label="pusoydos-set-turn-timer",
            prompt="pusoydos-select-turn-timer",
            change_msg="pusoydos-option-changed-turn-timer",
            description="pusoydos-desc-turn-timer",
        )
    )
    allow_2_in_straights: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="pusoydos-set-allow-2-in-straights",
            change_msg="pusoydos-option-changed-allow-2-in-straights",
            description="pusoydos-desc-allow-2-in-straights",
        )
    )
    instant_wins: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="pusoydos-set-instant-wins",
            change_msg="pusoydos-option-changed-instant-wins",
            description="pusoydos-desc-instant-wins",
        )
    )
    card_passing: str = option_field(
        MenuOption(
            choices=CARD_PASSING_CHOICES,
            choice_labels=CARD_PASSING_LABELS,
            default="off",
            value_key="choice",
            label="pusoydos-set-card-passing",
            prompt="pusoydos-select-card-passing",
            change_msg="pusoydos-option-changed-card-passing",
            description="pusoydos-desc-card-passing",
        )
    )
    penalty_tier: str = option_field(
        MenuOption(
            choices=PENALTY_TIER_CHOICES,
            choice_labels=PENALTY_TIER_LABELS,
            default="standard",
            value_key="choice",
            label="pusoydos-set-penalty-tier",
            prompt="pusoydos-select-penalty-tier",
            change_msg="pusoydos-option-changed-penalty-tier",
            description="pusoydos-desc-penalty-tier",
        ),
        visible_when=("game_mode", lambda v: v in ("points", "points_elimination")),
    )
    penalty_per_two: bool = option_field(
        BoolOption(
            default=False,
            value_key="enabled",
            label="pusoydos-set-penalty-per-two",
            change_msg="pusoydos-option-changed-penalty-per-two",
            description="pusoydos-desc-penalty-per-two",
        ),
        visible_when=("game_mode", lambda v: v in ("points", "points_elimination")),
    )


# =============================================================================
# Player
# =============================================================================


@dataclass
class PusoyDosPlayer(Player):
    hand: list[Card] = field(default_factory=list)
    selected_cards: set[int] = field(default_factory=set)
    passed_this_trick: bool = False
    # Scoring / tracking
    round_wins: int = 0
    round_losses: int = 0
    score: int = 0
    eliminated: bool = False
    # Confirm-to-pass timer (ticks remaining; 0 = not pending)
    pass_confirm_ticks: int = 0
    # Card passing state
    cards_to_give: int = 0
    give_to_id: str = ""
    giving_cards: bool = False


# =============================================================================
# Game
# =============================================================================


@dataclass
@register_game
class PusoyDosGame(Game, TurnTimerMixin):
    relevant_preferences = ["confirm_destructive_actions"]

    players: list[PusoyDosPlayer] = field(default_factory=list)
    options: PusoyDosOptions = field(default_factory=PusoyDosOptions)

    current_combo: Combo | None = None
    trick_winner_id: str | None = None
    trick_cards: list[Card] = field(default_factory=list)

    is_first_turn: bool = True
    hand_wait_ticks: int = 0
    round: int = 0

    timer: PokerTurnTimer = field(default_factory=PokerTurnTimer)

    # Phases: "playing", "instant_win_check", "card_passing", "between_rounds"
    phase: str = "playing"

    # Finishing order for the current round (player IDs in order they went out)
    finishing_order: list[str] = field(default_factory=list)

    # Previous round finishing order (for card passing)
    prev_finishing_order: list[str] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        self._timer_warning_played = False

    # ==========================================================================
    # Metadata
    # ==========================================================================

    @classmethod
    def get_name(cls) -> str:
        return "Pusoy Dos"

    @classmethod
    def get_type(cls) -> str:
        return "pusoydos"

    @classmethod
    def get_category(cls) -> str:
        return "category-playaural"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> PusoyDosPlayer:
        return PusoyDosPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list:
        errors = super().prestart_validate()
        active_count = len([p for p in self.players if not p.is_spectator])
        if self.options.card_passing == "full" and active_count not in (2, 4):
            errors.append("pusoydos-error-full-passing-players")
        return errors

    # ==========================================================================
    # Game start
    # ==========================================================================

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self.finishing_order = []
        self.prev_finishing_order = []

        for p in self._playing_players():
            p.round_wins = 0
            p.round_losses = 0
            p.score = 0
            p.eliminated = False

        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in self._playing_players()])

        self.play_music(SOUND_MUSIC)
        self._start_new_hand()

    # ==========================================================================
    # Round management
    # ==========================================================================

    def _playing_players(self) -> list[PusoyDosPlayer]:
        """Players still in the game (not eliminated, not spectators)."""
        return [
            p
            for p in self.players
            if isinstance(p, PusoyDosPlayer) and not p.is_spectator and not p.eliminated
        ]

    def _start_new_hand(self) -> None:
        self.round += 1
        self.is_first_turn = True
        self.current_combo = None
        self.trick_winner_id = None
        self.trick_cards = []
        self.finishing_order = []

        active = self._playing_players()
        self.broadcast_l("pusoydos-new-hand", round=self.round)

        # --- Deal cards based on player count ---
        n = len(active)
        deck, _ = DeckFactory.standard_deck()

        if n == 3:
            # Remove one middle 3 (3 of Spades) so 51 cards / 3 = 17 each
            deck.cards = [c for c in deck.cards if not (c.rank == 3 and c.suit == 4)]

        deck.shuffle()

        for p in active:
            p.hand = []
            p.selected_cards.clear()
            p.passed_this_trick = False
            p.pass_confirm_ticks = 0
            p.cards_to_give = 0
            p.give_to_id = ""
            p.giving_cards = False

        cards_per_player = len(deck.cards) // n
        for _ in range(cards_per_player):
            for p in active:
                card = deck.draw_one()
                if card:
                    p.hand.append(card)

        # Sort hands
        for p in active:
            p.hand = sort_cards(p.hand)

        self.schedule_sound(random.choice(SOUND_SHUFFLE), 10, volume=100)
        self.schedule_sound(random.choice(SOUND_DEAL), 20, volume=100)
        self.schedule_sound(random.choice(SOUND_DEAL), 25, volume=100)

        for p in active:
            user = self.get_user(p)
            if user:
                user.speak_l(
                    "pusoydos-dealt",
                    buffer="table",
                    count=len(p.hand),
                    cards=read_cards(p.hand, user.locale),
                )

        # Check instant wins (disabled if card passing is on)
        if self.options.instant_wins and self.options.card_passing == "off":
            win_found = self._check_instant_wins(active)
            if win_found:
                return

        # Card passing phase
        if self.options.card_passing != "off" and self.round > 1 and self.prev_finishing_order:
            self._start_card_passing(active)
            return

        self._begin_play(active)

    def _check_instant_wins(self, active: list[PusoyDosPlayer]) -> bool:
        """Check all players for instant win hands. Returns True if one was found."""
        for p in active:
            win_type = detect_instant_win(
                p.hand, allow_2_in_straights=self.options.allow_2_in_straights
            )
            if win_type:
                msg_key = {
                    "dragon": "pusoydos-instant-win-dragon",
                    "four_twos": "pusoydos-instant-win-four-twos",
                    "six_pairs": "pusoydos-instant-win-six-pairs",
                }.get(win_type, "pusoydos-instant-win-dragon")

                self.play_sound(SOUND_INSTANT_WIN)
                self.broadcast_l(msg_key, player=p.name)
                self._player_wins_round(p)
                self._end_round()
                return True
        return False

    def _start_card_passing(self, active: list[PusoyDosPlayer]) -> None:
        """Initiate the card passing phase based on previous round finishing order."""
        self.phase = "card_passing"
        self.broadcast_l("pusoydos-passing-phase")

        # Map finishing positions to current active players
        active_ids = {p.id for p in active}
        prev_order = [pid for pid in self.prev_finishing_order if pid in active_ids]

        if len(prev_order) < 2:
            self._begin_play(active)
            return

        # Determine exchanges
        if self.options.card_passing == "simple":
            # Only 1st and last swap 1 card
            self._setup_exchange(prev_order[0], prev_order[-1], 1)
        elif self.options.card_passing == "full":
            # 1st and last swap 2
            self._setup_exchange(prev_order[0], prev_order[-1], 2)
            # 2nd and 2nd-to-last swap 1 (if 4+ players)
            if len(prev_order) >= 4:
                self._setup_exchange(prev_order[1], prev_order[-2], 1)

        # Auto-give from losers (their highest cards)
        self._auto_give_loser_cards(active)

        # Check if winners need to choose (bots choose automatically)
        self._process_card_passing(active)

    def _setup_exchange(self, winner_id: str, loser_id: str, count: int) -> None:
        """Set up a card exchange between winner and loser."""
        winner = self._get_pusoy_player(winner_id)
        loser = self._get_pusoy_player(loser_id)
        if not winner or not loser:
            return

        # Loser gives their N highest cards automatically
        loser_highest = sort_cards(loser.hand)[-count:]

        # Move cards from loser to winner
        for card in loser_highest:
            loser.hand.remove(card)
            winner.hand.append(card)

        # Announce the automatic transfer
        self.broadcast_l("pusoydos-loser-gives", loser=loser.name, winner=winner.name, count=count)

        # Tell the winner what they received
        winner_user = self.get_user(winner)
        if winner_user:
            cards_str = read_cards(loser_highest, winner_user.locale)
            winner_user.speak_l(
                "pusoydos-received-cards", buffer="table", cards=cards_str, sender=loser.name
            )

        # Winner must give N cards back — set up the choice
        winner.cards_to_give = count
        winner.give_to_id = loser_id
        winner.giving_cards = True

    def _auto_give_loser_cards(self, active: list[PusoyDosPlayer]) -> None:
        """Notify players about the automatic loser card transfers."""
        pass  # The transfers already happened in _setup_exchange

    def _process_card_passing(self, active: list[PusoyDosPlayer]) -> None:
        """Check if all card passing decisions are made. If so, proceed."""
        for p in active:
            if p.giving_cards and p.cards_to_give > 0:
                if p.is_bot:
                    # Bot auto-selects worst cards to give
                    give_ids = bot_choose_give_cards(p.hand, p.cards_to_give)
                    self._complete_give(p, give_ids)
                else:
                    # Human needs to select — rebuild menus so they see the selection UI
                    self.rebuild_all_menus()
                    return

        # All done
        self.phase = "playing"
        for p in active:
            p.hand = sort_cards(p.hand)

        self.broadcast_l("pusoydos-cards-exchanged")
        self._begin_play(active)

    def _complete_give(self, giver: PusoyDosPlayer, card_ids: list[int]) -> None:
        """Transfer selected cards from giver to recipient."""
        recipient = self._get_pusoy_player(giver.give_to_id)
        if not recipient:
            return

        given_cards = [c for c in giver.hand if c.id in card_ids]
        for card in given_cards:
            giver.hand.remove(card)
            recipient.hand.append(card)

        # Broadcast the return
        self.broadcast_l(
            "pusoydos-winner-gives-back",
            winner=giver.name,
            loser=recipient.name,
            count=len(given_cards),
        )

        # Tell each player what was exchanged
        giver_user = self.get_user(giver)
        recipient_user = self.get_user(recipient)

        if giver_user:
            giver_user.speak_l(
                "pusoydos-passed-cards",
                buffer="table",
                cards=read_cards(given_cards, giver_user.locale),
                recipient=recipient.name,
            )
        if recipient_user:
            recipient_user.speak_l(
                "pusoydos-received-cards",
                buffer="table",
                cards=read_cards(given_cards, recipient_user.locale),
                sender=giver.name,
            )

        giver.cards_to_give = 0
        giver.give_to_id = ""
        giver.giving_cards = False

    def _begin_play(self, active: list[PusoyDosPlayer]) -> None:
        """Find the starting player and begin normal play."""
        self.phase = "playing"

        # Find 3 of Clubs holder
        start_player = None
        for p in active:
            if any(c.rank == 3 and c.suit == 2 for c in p.hand):
                start_player = p
                break

        if not start_player:
            # 3 of Clubs not in play — start with lowest card
            lowest_val = 999
            for p in active:
                if p.hand:
                    val = card_value(p.hand[0])
                    if val < lowest_val:
                        lowest_val = val
                        start_player = p

        self.set_turn_players(active)
        if start_player:
            idx = self.turn_player_ids.index(start_player.id)
            self.turn_index = idx
            if any(c.rank == 3 and c.suit == 2 for c in start_player.hand):
                self.broadcast_l("pusoydos-first-player", player=start_player.name)
            else:
                self.broadcast_l("pusoydos-first-player-lowest", player=start_player.name)

        self._start_turn()

    # ==========================================================================
    # Turn management
    # ==========================================================================

    def _start_turn(self) -> None:
        player = self.current_player
        if not player or not isinstance(player, PusoyDosPlayer):
            return

        # Reset any pending pass confirmation for all players
        for p in self._playing_players():
            p.pass_confirm_ticks = 0

        # Edge case: trick winner left the game
        active_ids = [p.id for p in self._playing_players() if not p.eliminated]
        if (
            self.trick_winner_id
            and self.trick_winner_id not in active_ids
            and self.current_combo is not None
        ):
            self.trick_winner_id = player.id

        if self.trick_winner_id == player.id:
            # I won the trick — start a new one
            if self.current_combo is not None:
                self.broadcast_l("pusoydos-trick-won", player=player.name)
            self.current_combo = None
            self.trick_cards = []
            self.trick_winner_id = None
            for p in self._playing_players():
                p.passed_this_trick = False

        elif player.passed_this_trick:
            # Skip players who passed this trick
            all_passed = all(
                p.passed_this_trick
                for p in self._playing_players()
                if p.id != self.trick_winner_id and p.id in self.turn_player_ids
            )
            if all_passed:
                winner = self.get_player_by_id(self.trick_winner_id)
                if winner and winner.id in self.turn_player_ids:
                    self.current_player = winner
                else:
                    # Trick winner left the hand; current player inherits
                    self.trick_winner_id = player.id
                self._start_turn()
                return

            self.advance_turn(announce=False)
            self._start_turn()
            return

        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(30, 50))

        self.start_turn_timer()
        self.rebuild_all_menus()

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if not self.game_active:
            return

        if self.hand_wait_ticks > 0:
            self.hand_wait_ticks -= 1
            if self.hand_wait_ticks == 0:
                self._start_new_hand()
            return

        # Tick down pass-confirm timers
        for p in self._playing_players():
            if p.pass_confirm_ticks > 0:
                p.pass_confirm_ticks -= 1

        self.on_tick_turn_timer()
        BotHelper.on_tick(self)

    def bot_think(self, player: PusoyDosPlayer) -> str | None:
        if self.hand_wait_ticks > 0:
            return None

        # Card passing — bot gives cards
        if self.phase == "card_passing" and player.giving_cards and player.cards_to_give > 0:
            give_ids = bot_choose_give_cards(player.hand, player.cards_to_give)
            self._complete_give(player, give_ids)
            self._process_card_passing(self._playing_players())
            return None

        if self.phase != "playing":
            return None

        ids = bot_think(self, player)
        if not ids:
            return "pass"

        player.selected_cards = set(ids)
        return "play_selected"

    def _on_turn_timeout(self) -> None:
        player = self.current_player
        if not isinstance(player, PusoyDosPlayer):
            return

        if not self.current_combo:
            # Must play — use bot logic to auto-play
            ids = bot_think(self, player)
            if ids:
                player.selected_cards = set(ids)
                self._action_play_selected(player, "play_selected")
                return

        self._action_pass(player, "pass")

    # ==========================================================================
    # Action sets
    # ==========================================================================

    def create_turn_action_set(self, player: PusoyDosPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")

        for card in player.hand:
            action_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        action_set.add(
            Action(
                id="play_selected",
                label="",
                handler="_action_play_selected",
                is_enabled="_is_play_selected_enabled",
                is_hidden="_is_turn_action_hidden",
                get_label="_get_play_selected_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "pusoydos-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_pass_hidden",
                show_in_actions_menu=False,
            )
        )

        # Card passing: give actions
        if player.giving_cards and player.cards_to_give > 0:
            action_set.add(
                Action(
                    id="confirm_give",
                    label="",
                    handler="_action_confirm_give",
                    is_enabled="_is_give_enabled",
                    is_hidden="_is_give_hidden",
                    get_label="_get_give_label",
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
                id="check_trick",
                label=Localization.get(locale, "pusoydos-check-trick"),
                handler="_action_check_trick",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "pusoydos-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_card_counts",
                label=Localization.get(locale, "pusoydos-read-card-counts"),
                handler="_action_read_card_counts",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_turn_timer",
                label=Localization.get(locale, "pusoydos-check-turn-timer"),
                handler="_action_check_turn_timer",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
                include_spectators=True,
            )
        )

        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind(
            "space", "pusoydos-key-play", ["play_selected"], state=KeybindState.ACTIVE
        )
        self.define_keybind("p", "pusoydos-key-pass", ["pass"], state=KeybindState.ACTIVE)
        self.define_keybind("c", "pusoydos-key-trick", ["check_trick"], include_spectators=True)
        self.define_keybind("h", "pusoydos-key-hand", ["read_hand"], include_spectators=False)
        self.define_keybind(
            "e", "pusoydos-key-counts", ["read_card_counts"], include_spectators=True
        )
        self.define_keybind(
            "shift+t", "pusoydos-key-timer", ["check_turn_timer"], include_spectators=True
        )

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
        if not isinstance(player, PusoyDosPlayer):
            return
        turn_set = self.get_action_set(player, "turn")
        if not turn_set:
            return

        turn_set.remove_by_prefix("toggle_select_")
        turn_set.remove("play_selected")
        turn_set.remove("pass")
        turn_set.remove("confirm_give")

        if self.status != "playing" or player.is_spectator or player.eliminated:
            return

        if self.hand_wait_ticks > 0:
            return

        # Card passing phase: show give selection
        if self.phase == "card_passing" and player.giving_cards and player.cards_to_give > 0:
            for card in player.hand:
                turn_set.add(
                    Action(
                        id=f"toggle_select_{card.id}",
                        label="",
                        handler="_action_toggle_select",
                        is_enabled="_is_card_toggle_enabled",
                        is_hidden="_is_card_toggle_hidden",
                        get_label="_get_card_label",
                        show_in_actions_menu=False,
                    )
                )
            turn_set.add(
                Action(
                    id="confirm_give",
                    label="",
                    handler="_action_confirm_give",
                    is_enabled="_is_give_enabled",
                    is_hidden="_is_give_hidden",
                    get_label="_get_give_label",
                    show_in_actions_menu=False,
                )
            )
            return

        if self.phase != "playing":
            return

        # Cards always visible for the player
        for card in player.hand:
            turn_set.add(
                Action(
                    id=f"toggle_select_{card.id}",
                    label="",
                    handler="_action_toggle_select",
                    is_enabled="_is_card_toggle_enabled",
                    is_hidden="_is_card_toggle_hidden",
                    get_label="_get_card_label",
                    show_in_actions_menu=False,
                )
            )

        if self.current_player == player:
            turn_set.add(
                Action(
                    id="play_selected",
                    label="",
                    handler="_action_play_selected",
                    is_enabled="_is_play_selected_enabled",
                    is_hidden="_is_turn_action_hidden",
                    get_label="_get_play_selected_label",
                    show_in_actions_menu=False,
                )
            )
            turn_set.add(
                Action(
                    id="pass",
                    label=Localization.get(self._player_locale(player), "pusoydos-pass"),
                    handler="_action_pass",
                    is_enabled="_is_pass_enabled",
                    is_hidden="_is_pass_hidden",
                    show_in_actions_menu=False,
                )
            )

    # ==========================================================================
    # Action handlers
    # ==========================================================================

    def _action_toggle_select(self, player: Player, action_id: str) -> None:
        p = self._require_pusoy_player(player)
        if not p:
            return
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return

        if card_id in p.selected_cards:
            p.selected_cards.remove(card_id)
        else:
            p.selected_cards.add(card_id)

        self.update_player_menu(p)

    def _action_play_selected(self, player: Player, action_id: str) -> None:
        p = self._require_active_turn_player(player)
        if not p:
            return

        if not p.selected_cards:
            self._send_error(p, "pusoydos-error-no-cards")
            return

        selected = [c for c in p.hand if c.id in p.selected_cards]
        combo = evaluate_combo(selected, allow_2_in_straights=self.options.allow_2_in_straights)

        if not combo:
            self._send_error(p, "pusoydos-error-invalid-combo")
            return

        # First turn: must include 3 of Clubs if held
        if self.is_first_turn:
            player_has_three = any(c.rank == 3 and c.suit == 2 for c in p.hand)
            has_three_in_play = any(c.rank == 3 and c.suit == 2 for c in selected)
            if player_has_three and not has_three_in_play:
                self._send_error(p, "pusoydos-error-first-turn-3c")
                return

        # Check against current trick
        if self.current_combo:
            if len(combo.cards) != len(self.current_combo.cards):
                self._send_error(
                    p, "pusoydos-error-wrong-length", count=len(self.current_combo.cards)
                )
                return
            if not combo.beats(self.current_combo):
                self._send_error(p, "pusoydos-error-lower-combo")
                return

        # Valid play
        for c in selected:
            p.hand.remove(c)
        p.selected_cards.clear()

        self.current_combo = combo
        self.trick_cards = selected
        self.trick_winner_id = p.id
        self.is_first_turn = False

        # Sound
        if len(selected) > 1:
            self.play_sound(random.choice(SOUND_PLAY_MULTI))
        else:
            self.play_sound(random.choice(SOUND_PLAY_SINGLE))

        self._broadcast_play(p, combo)

        if len(p.hand) == 1:
            self.broadcast_l("pusoydos-one-card", player=p.name)

        if len(p.hand) == 0:
            self._player_finishes(p)
            return

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_pass(self, player: Player, action_id: str) -> None:
        p = self._require_active_turn_player(player)
        if not p:
            return

        if not self.current_combo:
            self._send_error(p, "pusoydos-error-must-play")
            return

        # Confirm-to-pass: if the preference is enabled and not yet confirmed
        if not p.is_bot and p.pass_confirm_ticks == 0:
            user = self.get_user(p)
            if user:
                wants_confirm = user.preferences.get_effective(
                    "confirm_destructive_actions", game_type=self.get_type()
                )
                if wants_confirm:
                    p.pass_confirm_ticks = 200  # 10 seconds at 50ms/tick
                    user.speak_l("pusoydos-confirm-pass", buffer="table")
                    return

        p.pass_confirm_ticks = 0
        p.passed_this_trick = True
        self._broadcast_pass(p)
        p.selected_cards.clear()

        self.advance_turn(announce=False)
        self._start_turn()

    def _action_confirm_give(self, player: Player, action_id: str) -> None:
        """Confirm card selection during card passing phase."""
        p = self._require_pusoy_player(player)
        if not p or not p.giving_cards:
            return

        selected = [c for c in p.hand if c.id in p.selected_cards]
        if len(selected) != p.cards_to_give:
            recipient = self._get_pusoy_player(p.give_to_id)
            rname = recipient.name if recipient else "?"
            self._send_error(
                p, "pusoydos-select-cards-to-give", count=p.cards_to_give, recipient=rname
            )
            return

        self._complete_give(p, [c.id for c in selected])
        p.selected_cards.clear()
        self._process_card_passing(self._playing_players())

    def _action_check_trick(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        if not self.current_combo:
            user.speak_l("pusoydos-trick-empty", buffer="table")
            return

        trick_winner = self.get_player_by_id(self.trick_winner_id)
        winner_name = (
            trick_winner.name if trick_winner else Localization.get(user.locale, "unknown-player")
        )
        combo_name = Localization.get(user.locale, f"pusoydos-combo-{self.current_combo.type_name}")
        cards_str = read_cards(self.trick_cards, user.locale)
        user.speak_l(
            "pusoydos-trick-status",
            buffer="table",
            player=winner_name,
            combo=combo_name,
            cards=cards_str,
        )

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        if not isinstance(player, PusoyDosPlayer):
            return
        user = self.get_user(player)
        if user:
            user.speak_l(
                "pusoydos-your-hand", buffer="table", cards=read_cards(player.hand, user.locale)
            )

    def _action_read_card_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        parts = []
        for p in self._playing_players():
            if p.id in self.turn_player_ids:
                parts.append(f"{p.name} {len(p.hand)}")

        if parts:
            user.speak(", ".join(parts))

    def _action_check_turn_timer(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        remaining = self.timer.seconds_remaining()
        if remaining <= 0:
            user.speak_l("pusoydos-timer-disabled", buffer="table")
        else:
            user.speak_l("pusoydos-timer-remaining", buffer="table", seconds=remaining)

    # ==========================================================================
    # Round end logic
    # ==========================================================================

    def _player_finishes(self, player: PusoyDosPlayer) -> None:
        """A player emptied their hand — round ends immediately."""
        self.finishing_order.append(player.id)
        self._player_wins_round(player)

        # Rank remaining players: fewer cards = better, ties broken by lower highest card
        remaining = [
            p
            for p in self._playing_players()
            if p.id not in self.finishing_order and p.id in self.turn_player_ids
        ]
        remaining.sort(key=lambda p: (len(p.hand), max((card_value(c) for c in p.hand), default=0)))
        for p in remaining:
            self.finishing_order.append(p.id)

        self._end_round()

    def _player_wins_round(self, player: PusoyDosPlayer) -> None:
        """Record a round win for the player."""
        player.round_wins += 1
        self.play_sound(SOUND_WIN_ROUND)
        if self.options.game_mode in ("elimination", "points_elimination"):
            self.broadcast_l("pusoydos-round-winner", player=player.name)
        else:
            self.broadcast_l("pusoydos-player-goes-out", player=player.name)

    def _end_round(self) -> None:
        """Process end of round for either game mode."""
        self.prev_finishing_order = list(self.finishing_order)

        if self.options.game_mode == "points":
            self._end_round_points()
        elif self.options.game_mode == "losses":
            self._end_round_losses()
        elif self.options.game_mode == "points_elimination":
            self._end_round_points_elimination()
        else:
            self._end_round_elimination()

    def _end_round_points(self) -> None:
        """Points mode: calculate penalties and check for winner."""
        winner_id = self.finishing_order[0] if self.finishing_order else None
        winner = self._get_pusoy_player(winner_id) if winner_id else None

        entries = []
        total = 0
        for p in self._playing_players():
            if p.id == winner_id:
                continue
            penalty = self._calculate_penalty(p)
            if winner:
                winner.score += penalty
            total += penalty
            entries.append((p.name, penalty))

        if winner and entries:
            gained = sum(pts for _, pts in entries)
            breakdown = ", ".join(f"{pts} from {name}" for name, pts in entries)
            self.broadcast_l(
                "pusoydos-penalty-summary",
                player=winner.name,
                breakdown=breakdown,
                gained=gained,
                total=winner.score,
            )

        self._sync_team_scores()

        # Check for winner
        if winner and winner.score >= self.options.target_score:
            self.play_sound(SOUND_WIN_GAME)
            self.broadcast_l("pusoydos-points-winner", player=winner.name, score=winner.score)
            self.finish_game()
            return

        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _end_round_losses(self) -> None:
        """Losses mode: last-place player takes a loss. First to target losses loses the game."""
        if not self.finishing_order:
            self.hand_wait_ticks = 5 * 20
            self.rebuild_all_menus()
            return

        loser_id = self.finishing_order[-1]
        loser = self._get_pusoy_player(loser_id)
        if loser:
            loser.round_losses += 1
            self.play_sound(SOUND_LOSE_ROUND)
            self.broadcast_l("pusoydos-round-loser", player=loser.name, count=loser.round_losses)

            if loser.round_losses >= self.options.losses_to_lose:
                self.broadcast_l(
                    "pusoydos-losses-game-over", player=loser.name, count=loser.round_losses
                )
                self.finish_game()
                return

        self._sync_team_scores()
        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _end_round_points_elimination(self) -> None:
        """Points elimination: losers get points, reaching target eliminates you, last standing wins."""
        winner_id = self.finishing_order[0] if self.finishing_order else None

        for p in self._playing_players():
            if p.id == winner_id:
                continue
            penalty = self._calculate_penalty(p)
            p.score += penalty
            self.broadcast_l(
                "pusoydos-points-elim-penalty", player=p.name, points=penalty, total=p.score
            )

        # Check for newly eliminated players
        newly_eliminated = []
        for p in self._playing_players():
            if p.score >= self.options.target_score and not p.eliminated:
                p.eliminated = True
                newly_eliminated.append(p)

        for p in newly_eliminated:
            self.play_sound(SOUND_ELIMINATED)
            self.broadcast_l("pusoydos-points-elim-eliminated", player=p.name, score=p.score)

        remaining = self._playing_players()
        if newly_eliminated:
            self.broadcast_l("pusoydos-players-remaining", count=len(remaining))

        if len(remaining) <= 1:
            winner = remaining[0] if remaining else None
            if winner:
                self.play_sound(SOUND_WIN_GAME)
                self.broadcast_l("pusoydos-points-elim-winner", player=winner.name)
            self.finish_game()
            return

        self._sync_team_scores()
        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _end_round_elimination(self) -> None:
        """Elimination mode: check if any player reached required wins."""
        newly_eliminated = []
        for p in self._playing_players():
            if p.round_wins >= self.options.rounds_to_win and not p.eliminated:
                p.eliminated = True
                newly_eliminated.append(p)

        for p in newly_eliminated:
            self.play_sound(SOUND_ELIMINATED)
            self.broadcast_l("pusoydos-player-eliminated", player=p.name, count=p.round_wins)

        remaining = self._playing_players()
        if newly_eliminated:
            self.broadcast_l("pusoydos-players-remaining", count=len(remaining))

        if len(remaining) <= 1:
            # Game over — last player is the loser
            loser = remaining[0] if remaining else None
            if loser:
                self.play_sound(SOUND_LOSE_ROUND)
                self.broadcast_l("pusoydos-last-player", player=loser.name)
            self.finish_game()
            return

        self._sync_team_scores()
        self.hand_wait_ticks = 5 * 20
        self.rebuild_all_menus()

    def _calculate_penalty(self, player: PusoyDosPlayer) -> int:
        """Calculate point penalty for a player based on remaining cards."""
        cards_left = len(player.hand)
        if cards_left == 0:
            return 0

        # Base penalty
        base = cards_left

        # Tier multiplier
        tier = self.options.penalty_tier
        if tier == "flat":
            multiplier = 1
        elif tier == "aggressive":
            if cards_left >= 13:
                multiplier = 4
            elif cards_left >= 10:
                multiplier = 3
            elif cards_left >= 8:
                multiplier = 2
            else:
                multiplier = 1
        else:  # standard
            if cards_left >= 13:
                multiplier = 3
            elif cards_left >= 10:
                multiplier = 2
            else:
                multiplier = 1

        penalty = base * multiplier

        # Per-2 multiplier: double for each 2 remaining
        if self.options.penalty_per_two:
            twos_held = sum(1 for c in player.hand if c.rank == 2)
            for _ in range(twos_held):
                penalty *= 2

        return penalty

    # ==========================================================================
    # Helpers
    # ==========================================================================

    def _get_pusoy_player(self, player_id: str | None) -> PusoyDosPlayer | None:
        if not player_id:
            return None
        p = self.get_player_by_id(player_id)
        return p if isinstance(p, PusoyDosPlayer) else None

    def _require_pusoy_player(self, player: Player) -> PusoyDosPlayer | None:
        if not isinstance(player, PusoyDosPlayer):
            return None
        if player.is_spectator or player.eliminated:
            return None
        return player

    def _require_active_turn_player(self, player: Player) -> PusoyDosPlayer | None:
        p = self._require_pusoy_player(player)
        if not p:
            return None
        if self.current_player != p:
            return None
        return p

    def _send_error(self, player: PusoyDosPlayer, msg_key: str, **kwargs) -> None:
        user = self.get_user(player)
        if user:
            user.speak_l(msg_key, buffer="table", **kwargs)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _get_card_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, PusoyDosPlayer):
            return action_id
        try:
            card_id = int(action_id.split("_")[-1])
        except ValueError:
            return action_id
        card = next((c for c in player.hand if c.id == card_id), None)
        if not card:
            return action_id

        locale = self._player_locale(player)
        name = card_name(card, locale)
        if card_id in player.selected_cards:
            return Localization.get(locale, "pusoydos-card-selected", card=name)
        return Localization.get(locale, "pusoydos-card-unselected", card=name)

    def _get_play_selected_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, PusoyDosPlayer):
            return action_id

        locale = self._player_locale(player)

        if not player.selected_cards:
            return Localization.get(locale, "pusoydos-play-none")

        selected = [c for c in player.hand if c.id in player.selected_cards]
        combo = evaluate_combo(selected, allow_2_in_straights=self.options.allow_2_in_straights)

        if not combo:
            return Localization.get(locale, "pusoydos-play-invalid")

        combo_name = Localization.get(locale, f"pusoydos-combo-{combo.type_name}")
        return Localization.get(locale, "pusoydos-play-combo", combo=combo_name)

    def _get_give_label(self, player: Player, action_id: str) -> str:
        if not isinstance(player, PusoyDosPlayer):
            return action_id
        locale = self._player_locale(player)
        selected_count = len(player.selected_cards)
        needed = player.cards_to_give
        recipient = self._get_pusoy_player(player.give_to_id)
        rname = recipient.name if recipient else "?"
        return Localization.get(
            locale, "pusoydos-select-cards-to-give", count=needed, recipient=rname
        )

    def _is_give_enabled(self, player: Player) -> str | None:
        if not isinstance(player, PusoyDosPlayer):
            return "action-not-playing"
        if not player.giving_cards:
            return "action-not-playing"
        selected = len(player.selected_cards)
        if selected != player.cards_to_give:
            return "pusoydos-select-cards-to-give"
        return None

    def _is_give_hidden(self, player: Player) -> Visibility:
        if not isinstance(player, PusoyDosPlayer) or not player.giving_cards:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    # -- Action visibility helpers --

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.hand_wait_ticks > 0:
            return "action-wait"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_card_toggle_enabled(
        self, player: Player, *, action_id: str | None = None
    ) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.hand_wait_ticks > 0:
            return "action-wait"
        return None

    def _is_card_toggle_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        if self.hand_wait_ticks > 0:
            return Visibility.HIDDEN
        if not isinstance(player, PusoyDosPlayer):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_play_selected_enabled(self, player: Player) -> str | None:
        return self._is_turn_action_enabled(player)

    def _is_pass_enabled(self, player: Player) -> str | None:
        if not self.current_combo:
            return "pusoydos-error-must-play"
        return self._is_turn_action_enabled(player)

    def _is_pass_hidden(self, player: Player) -> Visibility:
        if not self.current_combo:
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return Visibility.HIDDEN

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if player.is_spectator:
            return "action-spectator"
        return self._is_check_enabled(player)

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_check_hidden(player)

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: "Player") -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE if self.status == "playing" else Visibility.HIDDEN
        return super()._is_check_scores_hidden(player)

    # ==========================================================================
    # Broadcasts
    # ==========================================================================

    def _broadcast_play(self, player: PusoyDosPlayer, combo: Combo) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            combo_name = Localization.get(user.locale, f"pusoydos-combo-{combo.type_name}")
            cards_str = read_cards(combo.cards, user.locale)

            if combo.type_name == "single":
                user.speak_l(
                    "pusoydos-player-plays-single",
                    buffer="table",
                    player=player.name,
                    card=cards_str,
                )
            else:
                user.speak_l(
                    "pusoydos-player-plays-combo",
                    buffer="table",
                    player=player.name,
                    combo=combo_name,
                    cards=cards_str,
                )

    def _broadcast_pass(self, player: PusoyDosPlayer) -> None:
        for p in self.players:
            user = self.get_user(p)
            if not user:
                continue
            user.speak_l("pusoydos-player-passes", buffer="table", player=player.name)

    # ==========================================================================
    # Score tracking
    # ==========================================================================

    def _is_check_scores_enabled(self, player: "Player") -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: "Player") -> str | None:
        return self._is_check_scores_enabled(player)

    def _action_check_scores(self, player: "Player", action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        parts = []
        if self.options.game_mode == "elimination":
            for p in self._playing_players():
                parts.append(f"{p.name}: {p.round_wins} wins")
            user.speak("; ".join(parts) if parts else "No scores yet.", buffer="table")
        elif self.options.game_mode == "losses":
            for p in self._playing_players():
                parts.append(f"{p.name}: {p.round_losses} losses")
            user.speak("; ".join(parts) if parts else "No scores yet.", buffer="table")
        elif self.options.game_mode == "points_elimination":
            players = sorted(self._playing_players(), key=lambda p: p.score)
            for p in players:
                parts.append(f"{p.name}: {p.score}")
            user.speak(". ".join(parts) + "." if parts else "No scores yet.", buffer="table")
        else:
            players = sorted(self._playing_players(), key=lambda p: -p.score)
            for p in players:
                parts.append(f"{p.name}: {p.score}")
            user.speak(". ".join(parts) + "." if parts else "No scores yet.", buffer="table")

    def _action_check_scores_detailed(self, player: "Player", action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = []
        if self.options.game_mode == "elimination":
            for p in self._playing_players():
                wins = p.round_wins
                label = "win" if wins == 1 else "wins"
                lines.append(f"{p.name}: {wins} {label}")
        elif self.options.game_mode == "losses":
            for p in self._playing_players():
                losses = p.round_losses
                label = "loss" if losses == 1 else "losses"
                lines.append(f"{p.name}: {losses} {label}")
        elif self.options.game_mode == "points_elimination":
            for p in sorted(self._playing_players(), key=lambda p: p.score):
                lines.append(f"{p.name}: {p.score} points")
        else:
            for p in sorted(self._playing_players(), key=lambda p: -p.score):
                lines.append(f"{p.name}: {p.score} points")
        self.status_box(player, lines if lines else ["No scores yet."])

    def _sync_team_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for p in self.players:
            team = self._team_manager.get_team(p.name)
            if team and isinstance(p, PusoyDosPlayer):
                if self.options.game_mode == "elimination":
                    team.total_score = p.round_wins
                elif self.options.game_mode == "losses":
                    team.total_score = p.round_losses
                else:
                    team.total_score = p.score

    # ==========================================================================
    # Game result
    # ==========================================================================

    def build_game_result(self) -> GameResult:
        active = [p for p in self.players if not p.is_spectator]

        if self.options.game_mode == "elimination":
            # In elimination, the last player is the loser
            # Sort: eliminated players by round_wins (desc), then remaining (loser) last
            sorted_players = sorted(active, key=lambda p: (not p.eliminated, -p.round_wins))
            winner = sorted_players[0] if sorted_players else None
        elif self.options.game_mode == "losses":
            # In losses, the player who hit the loss target is the loser
            # Sort: fewest losses first (best), most losses last (worst)
            sorted_players = sorted(active, key=lambda p: p.round_losses)
            winner = sorted_players[0] if sorted_players else None
        elif self.options.game_mode == "points_elimination":
            # Points elim: lowest score is best (last standing), eliminated sorted by score
            sorted_players = sorted(active, key=lambda p: (p.eliminated, p.score))
            winner = sorted_players[0] if sorted_players else None
        else:
            sorted_players = sorted(active, key=lambda p: -p.score)
            winner = sorted_players[0] if sorted_players else None

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
                "game_mode": self.options.game_mode,
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else [],
                "final_scores": {p.name: p.score for p in active},
                "final_wins": {p.name: p.round_wins for p in active},
                "final_losses": {p.name: p.round_losses for p in active},
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        mode = result.custom_data.get("game_mode", "elimination")

        if mode == "elimination":
            final_wins = result.custom_data.get("final_wins", {})
            sorted_players = sorted(final_wins.items(), key=lambda item: item[1], reverse=True)
            for i, (name, wins) in enumerate(sorted_players, 1):
                lines.append(
                    Localization.get(
                        locale, "pusoydos-line-format-wins", rank=i, player=name, wins=wins
                    )
                )
        elif mode == "losses":
            final_losses = result.custom_data.get("final_losses", {})
            sorted_players = sorted(final_losses.items(), key=lambda item: item[1])
            for i, (name, losses) in enumerate(sorted_players, 1):
                lines.append(
                    Localization.get(
                        locale, "pusoydos-line-format-losses", rank=i, player=name, losses=losses
                    )
                )
        elif mode == "points_elimination":
            final_scores = result.custom_data.get("final_scores", {})
            sorted_scores = sorted(final_scores.items(), key=lambda item: item[1])
            for i, (name, score) in enumerate(sorted_scores, 1):
                lines.append(
                    Localization.get(
                        locale, "pusoydos-line-format", rank=i, player=name, score=score
                    )
                )
        else:
            final_scores = result.custom_data.get("final_scores", {})
            sorted_scores = sorted(final_scores.items(), key=lambda item: item[1], reverse=True)
            for i, (name, score) in enumerate(sorted_scores, 1):
                lines.append(
                    Localization.get(
                        locale, "pusoydos-line-format", rank=i, player=name, score=score
                    )
                )
        return lines
