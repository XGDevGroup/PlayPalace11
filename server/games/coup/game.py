"""
Coup Game Implementation for PlayPalace v11.

A game of deduction and deception. Players start with two influences (character cards)
and two coins. The goal is to eliminate all other players' influences.

Actions:
- Income: Take 1 coin
- Foreign Aid: Take 2 coins (can be blocked by Duke)
- Coup: Pay 7 coins, choose player to lose influence (mandatory at 10+ coins)
- Duke: Take 3 coins
- Assassin: Pay 3 coins, choose player to lose influence (can be blocked by Contessa)
- Captain: Steal 2 coins from another player (can be blocked by Captain or Ambassador)
- Ambassador: Exchange cards with the deck
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState

from .cards import Deck, Card, Character
from .player import CoupPlayer, CoupOptions
from .bot import CoupBot


@dataclass
@register_game
class CoupGame(Game):
    """
    Coup game implementation.
    """

    players: list[CoupPlayer] = field(default_factory=list)
    options: CoupOptions = field(default_factory=CoupOptions)

    # Game State
    deck: Deck = field(default_factory=Deck)
    turn_phase: str = (
        "main"  # main, action_declared, waiting_block, resolving_challenge, exchanging
    )

    # State tracking for interrupts/challenges
    active_action: str | None = None
    active_target_id: str | None = None  # the original action target (never overwritten mid-phase)
    active_claimer_id: str | None = None
    original_claimer_id: str | None = None
    return_count: int = 0
    passed_players: set[str] = field(default_factory=set)
    player_claims: dict[str, set[str]] = field(default_factory=dict)
    _losing_player_id: str = ""  # player currently choosing which influence to lose
    _next_action_after_lose: str = "end_turn"  # what to do after influence loss resolves
    _steal_block_claimed_role: str | None = None  # "captain" or "ambassador" when blocking a steal

    # Audio sequence timing and state locking
    is_resolving: bool = False
    event_queue: list[tuple[int, str, dict]] = field(default_factory=list)

    # Static lengths for Coup audio files in ticks (20 ticks = 1 second)
    AUDIO_DURATIONS_TICKS = {
        "assassinate.ogg": 30,
        "block_contessa.ogg": 60,
        "block_duke.ogg": 58,
        "block_stealing.ogg": 20,
        "challenge.ogg": 44,
        "challengefail.ogg": 14,
        "challengesuccess.ogg": 41,
        "chardestroy1.ogg": 11,
        "chardestroy2.ogg": 17,
        "claim_ambassador.ogg": 10,
        "claim_assassin.ogg": 27,
        "claim_captain.ogg": 36,
        "claim_contessa.ogg": 16,
        "claim_duke.ogg": 31,
        "coup.ogg": 89,
        "exchange_complete.ogg": 10,
        "exchange_start.ogg": 110,
        "foreign_aid.ogg": 28,
        "income.ogg": 11,
        "steal.ogg": 59,
        "tax.ogg": 29,
    }

    # Timer state
    interrupt_timer_ticks: int = 0
    interrupt_duration_ticks: int = 0

    def get_audio_duration_ticks(self, filename: str) -> int:
        """Helper to get dynamic duration of audio file in ticks."""
        name = filename.split("/")[-1]
        return self.AUDIO_DURATIONS_TICKS.get(name, 0)

    def __post_init__(self):
        super().__post_init__()

    @classmethod
    def get_name(cls) -> str:
        return "Coup"

    @classmethod
    def get_type(cls) -> str:
        return "coup"

    @classmethod
    def get_category(cls) -> str:
        return "category-playaural"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 6

    @classmethod
    def get_supported_leaderboards(cls) -> list[str]:
        return ["wins", "rating", "games_played"]

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> CoupPlayer:
        """Create a new Coup player."""
        return CoupPlayer(id=player_id, name=name, is_bot=is_bot)

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self._sync_table_status()
        self.game_active = True
        self.round = 1

        # Initialize deck
        self.deck = Deck()
        self.deck.build_standard_deck()
        self.deck.shuffle()

        # Initial hands and coins
        active_players = self.get_active_players()
        self.player_claims.clear()

        for player in active_players:
            player.coins = 2
            player.influences = []
            player.is_dead = False
            self.player_claims[player.id] = set()
            for _ in range(2):
                card = self.deck.draw()
                if card:
                    player.influences.append(card)

        self.set_turn_players(active_players)

        # Play intro music
        self.play_music("game_coup/music.ogg")
        self.play_sound(f"game_cards/shuffle{random.randint(1, 3)}.ogg")

        # Jolt bots
        BotHelper.jolt_bots(self, ticks=random.randint(10, 20))

        # Broadcast initial hands privately
        for player in active_players:
            if not player.is_bot:
                self._action_check_hand(player, "check_hand")

        # Start first turn
        self.reset_turn_order()
        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player or not isinstance(player, CoupPlayer):
            return

        # Check for game winner
        alive = self.get_alive_players()
        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)
            return

        # Skip dead players
        if player.is_dead:
            self._end_turn()
            return

        # Announce turn
        self.announce_turn()

        self.turn_phase = "main"
        self.active_action = None
        self.active_target_id = None
        self.active_claimer_id = None
        self.original_claimer_id = None
        self.interrupt_timer_ticks = 0
        self.passed_players = set()
        self._steal_block_claimed_role = None

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(20, 50))

        self.rebuild_all_menus()

    def _end_turn(self) -> None:
        """End current player's turn."""
        self.advance_turn(announce=False)
        self._start_turn()

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        user = None
        if hasattr(self, "host_username") and self.host_username:
            player = self.get_player_by_name(self.host_username)
            if player:
                user = self.get_user(player)
        locale = user.locale if user else "en"

        # Information Keybinds
        self.define_keybind(
            "w",
            Localization.get(locale, "coup-action-check-wealth"),
            ["check_wealth"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )
        self.define_keybind(
            "h",
            Localization.get(locale, "coup-action-check-hand"),
            ["check_hand"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "l",
            Localization.get(locale, "coup-action-check-table"),
            ["check_table"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

        # Reaction Keybinds
        self.define_keybind(
            "c",
            Localization.get(locale, "coup-action-challenge"),
            ["challenge"],
            state=KeybindState.ACTIVE,
        )
        self.define_keybind(
            "v", Localization.get(locale, "coup-action-block"), ["block"], state=KeybindState.ACTIVE
        )
        self.define_keybind(
            "p", Localization.get(locale, "coup-action-pass"), ["pass"], state=KeybindState.ACTIVE
        )

    def create_turn_action_set(self, player: CoupPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")

        # Lose Influence Actions
        for i in range(4):
            action_set.add(
                Action(
                    id=f"lose_influence_{i}",
                    label=Localization.get(locale, "coup-action-lose-influence"),
                    handler="_action_lose_influence",
                    is_enabled="_is_lose_influence_enabled",
                    is_hidden="_is_lose_influence_hidden",
                    get_label="_get_lose_influence_label",
                    show_in_actions_menu=False,
                )
            )

        # Exchange Actions
        for i in range(4):
            action_set.add(
                Action(
                    id=f"return_card_{i}",
                    label=Localization.get(locale, "coup-action-return-card"),
                    handler="_action_return_card",
                    is_enabled="_is_return_card_enabled",
                    is_hidden="_is_return_card_hidden",
                    get_label="_get_return_card_label",
                    show_in_actions_menu=False,
                )
            )

        # Interrupt Window Actions
        action_set.add(
            Action(
                id="challenge",
                label=Localization.get(locale, "coup-action-challenge"),
                handler="_action_challenge",
                is_enabled="_is_challenge_enabled",
                is_hidden="_is_interrupt_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="block",
                label=Localization.get(locale, "coup-action-block"),
                handler="_action_block",
                is_enabled="_is_block_enabled",
                is_hidden="_is_block_hidden",
                get_label="_get_block_label",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="block_captain",
                label=Localization.get(locale, "coup-action-block-captain"),
                handler="_action_block",
                is_enabled="_is_block_steal_enabled",
                is_hidden="_is_block_steal_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="block_ambassador",
                label=Localization.get(locale, "coup-action-block-ambassador"),
                handler="_action_block",
                is_enabled="_is_block_steal_enabled",
                is_hidden="_is_block_steal_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="pass",
                label=Localization.get(locale, "coup-action-pass"),
                handler="_action_pass",
                is_enabled="_is_pass_enabled",
                is_hidden="_is_interrupt_hidden",
                show_in_actions_menu=False,
            )
        )

        # Basic Actions
        action_set.add(
            Action(
                id="income",
                label=Localization.get(locale, "coup-action-income"),
                handler="_action_income",
                is_enabled="_is_income_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="foreign_aid",
                label=Localization.get(locale, "coup-action-foreign-aid"),
                handler="_action_foreign_aid",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="coup",
                label=Localization.get(locale, "coup-action-coup"),
                handler="_action_coup",
                is_enabled="_is_coup_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )

        # Character Actions
        action_set.add(
            Action(
                id="tax",
                label=Localization.get(locale, "coup-action-tax"),
                handler="_action_tax",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="assassinate",
                label=Localization.get(locale, "coup-action-assassinate"),
                handler="_action_assassinate",
                is_enabled="_is_assassinate_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="steal",
                label=Localization.get(locale, "coup-action-steal"),
                handler="_action_steal",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                input_request=MenuInput(
                    prompt="coup-select-target",
                    options="_target_options",
                    bot_select="_bot_select_target",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="exchange",
                label=Localization.get(locale, "coup-action-exchange"),
                handler="_action_exchange",
                is_enabled="_is_action_enabled",
                is_hidden="_is_action_hidden",
                show_in_actions_menu=False,
            )
        )

        return action_set

    web_target_order = ["check_wealth", "check_hand", "check_table", "whose_turn", "whos_at_table"]

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)

        # Remove redundant global score checks that don't apply well to Coup
        if action_set.get_action("check_scores"):
            action_set.remove("check_scores")
        if action_set.get_action("check_scores_detailed"):
            action_set.remove("check_scores_detailed")

        user = self.get_user(player)
        locale = user.locale if user else "en"

        # Info Actions (accessible anytime)
        action_set.add(
            Action(
                id="check_wealth",
                label=Localization.get(locale, "coup-action-check-wealth"),
                handler="_action_check_wealth",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_info_hidden",
                show_in_actions_menu=True,
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="check_hand",
                label=Localization.get(locale, "coup-action-check-hand"),
                handler="_action_check_hand",
                is_enabled="_is_private_info_enabled",
                is_hidden="_is_private_info_hidden",
                show_in_actions_menu=True,
            )
        )
        action_set.add(
            Action(
                id="check_table",
                label=Localization.get(locale, "coup-action-check-table"),
                handler="_action_check_table",
                is_enabled="_is_public_info_enabled",
                is_hidden="_is_info_hidden",
                show_in_actions_menu=True,
                include_spectators=True,
            )
        )

        # WEB-SPECIFIC: Reorder for Web Clients
        if user and getattr(user, "client_type", "") == "web":
            final_order = []
            for aid in self.web_target_order:
                if action_set.get_action(aid):
                    final_order.append(aid)

            for aid in action_set._order:
                if aid not in self.web_target_order:
                    final_order.append(aid)

            action_set._order = final_order

        return action_set

    # ==========================================================================
    # Action Checks
    # ==========================================================================

    def _is_whos_at_table_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (always), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: "Player") -> Visibility:
        """Override: Visible for Web (Playing only), hidden otherwise."""
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            if self.status == "playing":
                return Visibility.VISIBLE
            return Visibility.HIDDEN
        return super()._is_whose_turn_hidden(player)

    def _is_info_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_private_info_hidden(self, player: Player) -> Visibility:
        if player.is_spectator:
            return Visibility.HIDDEN
        return self._is_info_hidden(player)

    def _is_public_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_private_info_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_lose_influence_hidden(self, player: Player, action_id: str | None = None) -> Visibility:
        if self.turn_phase != "losing_influence" or player.id != self._losing_player_id:
            return Visibility.HIDDEN
        if action_id:
            coup_player: CoupPlayer = player  # type: ignore
            try:
                idx = int(action_id.split("_")[-1])
            except ValueError:
                return Visibility.HIDDEN
            if idx < 0 or idx >= len(coup_player.live_influences):
                return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_lose_influence_enabled(
        self, player: Player, action_id: str | None = None
    ) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if self.turn_phase != "losing_influence" or player.id != self._losing_player_id:
            return "action-not-available"

        if not action_id:
            return None

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "action-not-available"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "action-not-available"

        return None

    def _get_lose_influence_label(self, player: Player, action_id: str) -> str:
        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "Lose Influence"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "Lose Influence"

        card = coup_player.live_influences[idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        return Localization.get(locale, f"coup-card-{card.character.value}")

    def _is_return_card_hidden(self, player: Player) -> Visibility:
        if self.turn_phase != "exchanging" or self.current_player != player:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_return_card_enabled(self, player: Player, action_id: str | None = None) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if self.turn_phase != "exchanging" or self.current_player != player:
            return "action-not-available"

        if not action_id:
            return None

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "action-not-available"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "action-not-available"

        return None

    def _get_return_card_label(self, player: Player, action_id: str) -> str:
        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return "Return Card"

        if idx < 0 or idx >= len(coup_player.live_influences):
            return "Return Card"

        card = coup_player.live_influences[idx]
        user = self.get_user(player)
        locale = user.locale if user else "en"
        card_name = Localization.get(locale, f"coup-card-{card.character.value}")
        return Localization.get(locale, "coup-return-card-format", card=card_name)

    def _is_interrupt_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or player.is_dead:
            return Visibility.HIDDEN
        if self.turn_phase not in ["action_declared", "waiting_block"]:
            return Visibility.HIDDEN

        # Original claimer/blocker cannot interrupt themselves
        if player.id == self.active_claimer_id:
            return Visibility.HIDDEN

        if player.id in getattr(self, "passed_players", set()):
            return Visibility.HIDDEN

        # In waiting_block (e.g. Duke blocking Foreign Aid), only Challenge or Pass makes sense, no second Block.
        # But this is just visibility, we handle specifics in is_enabled.
        return Visibility.VISIBLE

    def _is_challenge_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if player.id == self.active_claimer_id:
            return "action-not-available"

        if self.turn_phase == "action_declared":
            # Can we challenge this action?
            unchallengeable = ["income", "foreign_aid", "coup"]
            if self.active_action in unchallengeable:
                return "coup-cannot-challenge-action"
            return None
        elif self.turn_phase == "waiting_block":
            # Can challenge a block
            return None
        return "coup-no-active-claim"

    def _is_block_hidden(self, player: Player) -> Visibility:
        """Hide generic block during steal (use block_captain/block_ambassador instead)
        and during actions that cannot be blocked at all."""
        if self.active_action not in ("foreign_aid", "assassinate"):
            return Visibility.HIDDEN
        return self._is_interrupt_hidden(player)

    def _is_block_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if player.id == self.active_claimer_id:
            return "action-not-available"

        if self.turn_phase != "action_declared":
            return "coup-cannot-block-now"

        if self.active_action == "foreign_aid":
            return None  # Anyone can block with Duke

        if self.active_action == "assassinate":
            if player.id != self.active_target_id:
                return "coup-only-target-can-block"
            return None

        # Steal uses block_captain / block_ambassador instead
        return "coup-cannot-block-action"

    def _is_block_steal_hidden(self, player: Player) -> Visibility:
        """Only show block_captain/block_ambassador during steal interrupt window."""
        if self.active_action != "steal" or self.turn_phase != "action_declared":
            return Visibility.HIDDEN
        return self._is_interrupt_hidden(player)

    def _is_block_steal_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if player.id == self.active_claimer_id:
            return "action-not-available"
        if self.turn_phase != "action_declared":
            return "coup-cannot-block-now"
        if self.active_action != "steal":
            return "coup-cannot-block-action"
        if player.id != self.active_target_id:
            return "coup-only-target-can-block"
        return None

    def _get_block_label(self, player: Player, action_id: str) -> str:
        """Dynamic label showing which role the block claims."""
        user = self.get_user(player)
        locale = user.locale if user else "en"
        role_key = {
            "foreign_aid": "coup-card-duke",
            "assassinate": "coup-card-contessa",
        }.get(self.active_action or "")
        if role_key:
            role = Localization.get(locale, role_key)
            return Localization.get(locale, "coup-action-block-with", role=role)
        # Steal uses separate block_captain/block_ambassador actions
        return Localization.get(locale, "coup-action-block")

    def _is_pass_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if player.id == self.active_claimer_id or player.id in getattr(
            self, "passed_players", set()
        ):
            return "action-not-available"
        return None  # If the interrupt is visible, passing is enabled.

    def _is_action_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or player.is_dead:
            return Visibility.HIDDEN
        if self.current_player != player or self.turn_phase != "main":
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_action_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if self.status != "playing":
            return "action-not-playing"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if self.current_player != player or self.turn_phase != "main":
            return "action-not-your-turn"

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins >= self.options.mandatory_coup_threshold:
            return "coup-must-coup"

        return None

    def _is_income_enabled(self, player: Player) -> str | None:
        return self._is_action_enabled(player)

    def _is_coup_enabled(self, player: Player) -> str | None:
        if self.is_resolving:
            return "action-game-in-progress"
        if self.status != "playing":
            return "action-not-playing"
        if player.is_dead:
            return "coup-you-are-eliminated"
        if player.is_spectator:
            return "action-not-playing"
        if self.current_player != player or self.turn_phase != "main":
            return "action-not-your-turn"

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins < 7:
            return "coup-not-enough-coins"

        return None

    def _is_assassinate_enabled(self, player: Player) -> str | None:
        err = self._is_action_enabled(player)
        if err:
            return err

        coup_player: CoupPlayer = player  # type: ignore
        if coup_player.coins < 3:
            return "coup-not-enough-coins"

        return None

    def _target_options(self, player: Player) -> list[str]:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        options = []
        for p in self.get_alive_players():
            if p != player:
                options.append(
                    Localization.get(locale, "coup-wealth-line", player=p.name, coins=p.coins)
                )
        return options

    def _extract_target_name(self, target_str: str) -> str:
        """Helper to extract the base player name from the formatted option string."""
        # The string format is defined by "coup-wealth-line" which is "PlayerName: X coins"
        # We can extract the name by splitting on ':'
        if ":" in target_str:
            return target_str.split(":", 1)[0].strip()
        return target_str.strip()

    def _bot_select_target(self, player: Player, options: list[str]) -> str | None:
        if not options:
            return None

        # Bot evaluates based on raw names, so we need to map formatted options back to names
        # and then map the selected name back to the formatted option string
        option_map = {self._extract_target_name(opt): opt for opt in options}

        best_name = CoupBot.select_best_target(self, player, list(option_map.keys()))
        if best_name and best_name in option_map:
            return option_map[best_name]
        return random.choice(options)

    # ==========================================================================
    # Action Handlers
    # ==========================================================================

    def _action_check_wealth(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        lines = []
        for p in self.get_alive_players():
            # e.g., "Alice: 4 coins"
            lines.append(
                Localization.get(user.locale, "coup-wealth-line", player=p.name, coins=p.coins)
            )

        if not lines:
            lines.append(Localization.get(user.locale, "coup-no-alive-players"))

        combined = ", ".join(lines)
        user.speak(combined, buffer="table")

    def _action_check_hand(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        coup_player: CoupPlayer = player  # type: ignore

        if coup_player.is_dead:
            user.speak_l("coup-you-are-eliminated", buffer="table")
            return

        lines = []
        for card in coup_player.live_influences:
            card_name = Localization.get(user.locale, f"coup-card-{card.character.value}")
            lines.append(card_name)

        if not lines:
            cards_str = Localization.get(user.locale, "coup-no-cards")
        else:
            cards_str = ", ".join(lines)

        # Deliver a contextual message including their coins and cards
        user.speak_l("coup-hand-context", coins=coup_player.coins, cards=cards_str, buffer="table")

    def _action_check_table(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return

        lines = []
        for p in self.get_active_players():
            dead = p.dead_influences
            if dead:
                cards = [
                    Localization.get(user.locale, f"coup-card-{c.character.value}") for c in dead
                ]
                # e.g., "Alice lost: Duke, Captain"
                cards_str = ", ".join(cards)
                lines.append(
                    Localization.get(user.locale, "coup-table-line", player=p.name, cards=cards_str)
                )

        if not lines:
            lines.append(Localization.get(user.locale, "coup-table-empty"))

        combined = "; ".join(lines)
        user.speak(combined, buffer="table")

    def _action_income(self, player: Player, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        coup_player.coins += 1

        self.play_sound("game_coup/income.ogg")
        self.broadcast_l("coup-takes-income", player=player.name)

        self._end_turn()

    def _action_foreign_aid(self, player: Player, action_id: str) -> None:
        # Declare action, start interrupt timer
        self._declare_action(player.id, "foreign_aid")

    def _action_coup(self, player: Player, target_name: str, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        target = self.get_player_by_name(self._extract_target_name(target_name))

        if not target or target.is_dead:
            return

        self.is_resolving = True
        self.rebuild_all_menus()

        coup_player.coins -= 7
        self.play_sound("game_coup/coup.ogg")
        self.broadcast_l("coup-plays-coup", player=player.name, target=target.name)

        duration = self.get_audio_duration_ticks("coup.ogg")
        self.event_queue.append(
            (
                self.sound_scheduler_tick + duration,
                "prompt_lose_influence",
                {"target_id": target.id, "reason": "coup"},
            )
        )

    def _action_tax(self, player: Player, action_id: str) -> None:
        self._declare_action(player.id, "tax")

    def _action_assassinate(self, player: Player, target_name: str, action_id: str) -> None:
        coup_player: CoupPlayer = player  # type: ignore
        target = self.get_player_by_name(self._extract_target_name(target_name))

        if not target or target.is_dead:
            return

        coup_player.coins -= 3
        self._declare_action(player.id, "assassinate", target.id)

    def _action_steal(self, player: Player, target_name: str, action_id: str) -> None:
        target = self.get_player_by_name(self._extract_target_name(target_name))

        if not target or target.is_dead:
            return

        self._declare_action(player.id, "steal", target.id)

    def _action_exchange(self, player: Player, action_id: str) -> None:
        self._declare_action(player.id, "exchange")

    def _declare_action(self, player_id: str, action: str, target_id: str | None = None) -> None:
        """Starts the interrupt window for a challengeable/blockable action."""
        self.active_action = action
        self.active_claimer_id = player_id
        self.original_claimer_id = player_id
        self.active_target_id = target_id
        self.turn_phase = "action_declared"
        self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
        self.interrupt_duration_ticks = self.interrupt_timer_ticks
        self.passed_players = set()

        player = self.get_player_by_id(player_id)
        target = self.get_player_by_id(target_id) if target_id else None

        req_char = self._get_required_character_for_action(action)
        if req_char and player_id in self.player_claims:
            self.player_claims[player_id].add(req_char)

        # Play claim sound and broadcast
        if action == "tax":
            self.play_sound("game_coup/claim_duke.ogg")
            self.broadcast_l("coup-claims-tax", player=player.name)
        elif action == "foreign_aid":
            # no character claimed, just standard action. Sound plays on resolution.
            self.broadcast_l("coup-claims-foreign-aid", player=player.name)
        elif action == "assassinate":
            self.play_sound("game_coup/claim_assassin.ogg")
            self.broadcast_l(
                "coup-claims-assassinate", player=player.name, target=target.name if target else ""
            )
        elif action == "steal":
            self.play_sound("game_coup/claim_captain.ogg")
            self.broadcast_l(
                "coup-claims-steal", player=player.name, target=target.name if target else ""
            )
        elif action == "exchange":
            self.play_sound("game_coup/claim_ambassador.ogg")
            self.broadcast_l("coup-claims-exchange", player=player.name)

        self.broadcast_l("coup-waiting-for-reactions")
        self.rebuild_all_menus()
        # Jolt bots heavily so they don't react instantly
        BotHelper.jolt_bots(self, ticks=random.randint(40, 80))  # 2-4 seconds delay

    def _action_challenge(self, player: Player, action_id: str) -> None:
        # Resolve challenge
        if self.turn_phase not in ["action_declared", "waiting_block"]:
            return

        # Prevent race condition: if timer is already 0, someone else beat them to it
        if self.interrupt_timer_ticks <= 0:
            return

        self.interrupt_timer_ticks = 0
        self.is_resolving = True
        self.rebuild_all_menus()

        self.play_sound("game_coup/challenge.ogg")
        claimer = self.get_player_by_id(self.active_claimer_id)

        self.broadcast_l("coup-challenges", challenger=player.name, target=claimer.name)

        duration = self.get_audio_duration_ticks("challenge.ogg")
        self.event_queue.append(
            (
                self.sound_scheduler_tick + duration,
                "resolve_challenge",
                {"challenger_id": player.id},
            )
        )

    def _action_block(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "action_declared":
            return

        # Prevent race condition
        if self.interrupt_timer_ticks <= 0:
            return

        self.interrupt_timer_ticks = 0
        claimer = self.get_player_by_id(self.active_claimer_id)
        if not claimer:
            return

        # Depends on what is blocked
        if self.active_action == "foreign_aid":
            self.play_sound("game_coup/claim_duke.ogg")
            self.broadcast_l("coup-blocks-foreign-aid", blocker=player.name, target=claimer.name)
            if player.id in self.player_claims:
                self.player_claims[player.id].add("duke")
        elif self.active_action == "assassinate":
            self.play_sound("game_coup/claim_contessa.ogg")
            self.broadcast_l("coup-blocks-assassinate", blocker=player.name, target=claimer.name)
            if player.id in self.player_claims:
                self.player_claims[player.id].add("contessa")
        elif self.active_action == "steal":
            # action_id tells us which role: block_captain or block_ambassador
            if action_id == "block_captain":
                claimed_role = "captain"
                self.play_sound("game_coup/claim_captain.ogg")
                self.broadcast_l(
                    "coup-blocks-steal-captain", blocker=player.name, target=claimer.name
                )
            elif action_id == "block_ambassador":
                claimed_role = "ambassador"
                self.play_sound("game_coup/claim_ambassador.ogg")
                self.broadcast_l(
                    "coup-blocks-steal-ambassador", blocker=player.name, target=claimer.name
                )
            else:
                return  # Unknown block variant; ignore
            if player.id in self.player_claims:
                self.player_claims[player.id].add(claimed_role)
            self._steal_block_claimed_role = claimed_role
        else:
            return  # Unblockable action; should not reach here

        # Enter "waiting_block" phase where the BLOCK can be challenged
        self.turn_phase = "waiting_block"
        self.active_claimer_id = player.id  # Blocker is now claiming to have a role
        self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
        self.interrupt_duration_ticks = self.interrupt_timer_ticks
        self.passed_players = set()

        self.broadcast_l("coup-waiting-for-reactions")
        self.rebuild_all_menus()
        BotHelper.jolt_bots(self, ticks=random.randint(40, 80))

    def _action_pass(self, player: Player, action_id: str) -> None:
        if self.turn_phase not in ["action_declared", "waiting_block"]:
            return

        self.passed_players.add(player.id)

        user = self.get_user(player)
        if user and not player.is_bot:
            user.speak_l("coup-action-pass-confirmed", buffer="table")

        # Check if all other eligible players have passed
        alive = self.get_alive_players()
        eligible_count = 0
        for p in alive:
            if p.id != self.active_claimer_id:
                eligible_count += 1

        if len(self.passed_players) >= eligible_count:
            # Everyone passed, fast-forward timer
            self.interrupt_timer_ticks = 1

        # Rebuild all menus so everyone sees that this player passed/menu updates
        self.rebuild_all_menus()

    def _get_required_character_for_action(self, action: str) -> str:
        mapping = {
            "tax": "duke",
            "assassinate": "assassin",
            "steal": "captain",
            "exchange": "ambassador",
        }
        return mapping.get(action, "")

    def _get_required_character_for_block(self, action: str) -> str | list[str]:
        mapping = {
            "foreign_aid": "duke",
            "assassinate": "contessa",
            "steal": ["captain", "ambassador"],
        }
        return mapping.get(action, "")

    def _process_events(self) -> None:
        """Process queued game events."""
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
        if event_type == "resolve_income":
            player = self.get_player_by_id(data.get("player_id"))
            if player:
                player.coins += 1
                self.broadcast_l("coup-takes-income", player=player.name)
            self.is_resolving = False
            self._end_turn()

        elif event_type == "prompt_lose_influence":
            self.is_resolving = False
            self._prompt_lose_influence(data.get("target_id"), data.get("reason"))

        elif event_type == "start_interrupt_window":
            self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
            self.interrupt_duration_ticks = self.interrupt_timer_ticks
            self.is_resolving = False
            self.broadcast_l("coup-waiting-for-reactions")
            self.rebuild_all_menus()
            BotHelper.jolt_bots(self, ticks=random.randint(40, 80))  # 2-4 seconds delay

        elif event_type == "start_waiting_block":
            self.turn_phase = "waiting_block"
            self.active_claimer_id = data.get("blocker_id")
            self.interrupt_timer_ticks = self.options.timer_duration_seconds * 20
            self.interrupt_duration_ticks = self.interrupt_timer_ticks
            self.passed_players = set()
            self.is_resolving = False
            self.broadcast_l("coup-waiting-for-reactions")
            self.rebuild_all_menus()
            BotHelper.jolt_bots(self, ticks=random.randint(40, 80))

        elif event_type == "resolve_challenge":
            self._execute_challenge(data.get("challenger_id"))

        elif event_type == "post_challenge_lose_influence":
            self.is_resolving = False
            self._prompt_lose_influence(data.get("target_id"), data.get("reason"))

        elif event_type == "post_challenge_resolve_action":
            self._resolve_action()

        elif event_type == "post_challenge_end_turn":
            self.is_resolving = False
            self._end_turn()

        elif event_type == "post_block_success":
            self.is_resolving = False
            self._end_turn()

        elif event_type == "post_lose_influence":
            self.is_resolving = False
            self._post_lose_influence()

    def _execute_challenge(self, challenger_id: str) -> None:
        player = self.get_player_by_id(challenger_id)
        claimer = self.get_player_by_id(self.active_claimer_id)
        if not player or not claimer:
            self.is_resolving = False
            return

        required_char = self._get_required_character_for_action(self.active_action)
        if self.turn_phase == "waiting_block":
            # For steal blocks, use the specific role the blocker claimed
            if self.active_action == "steal" and self._steal_block_claimed_role:
                required_char = self._steal_block_claimed_role
            else:
                required_char = self._get_required_character_for_block(self.active_action)

        has_character = False
        revealed_char = None

        if isinstance(required_char, list):
            for rc in required_char:
                if claimer.has_influence(rc):
                    has_character = True
                    revealed_char = rc
                    break
        else:
            if claimer.has_influence(required_char):
                has_character = True
                revealed_char = required_char

        if has_character:
            # Challenge fails!
            self.play_sound("game_coup/challengesuccess.ogg")
            duration = self.get_audio_duration_ticks("challengesuccess.ogg")
            self._broadcast_card_message(
                "coup-challenge-failed", revealed_char, player=claimer.name
            )

            # Claimer replaces card
            for card in claimer.live_influences:
                if card.character == revealed_char:
                    self.deck.add(card)
                    self.deck.shuffle()
                    self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")
                    claimer.influences.remove(card)
                    new_card = self.deck.draw()
                    claimer.influences.append(new_card)
                    self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
                    if claimer.id in self.player_claims:
                        self.player_claims[claimer.id].clear()
                    if new_card and not claimer.is_bot:
                        user = self.get_user(claimer)
                        if user:
                            new_card_name = Localization.get(
                                user.locale, f"coup-card-{new_card.character.value}"
                            )
                            user.speak_l(
                                "coup-drew-replacement-card",
                                character=new_card_name,
                                buffer="table",
                            )
                    break

            if self.turn_phase == "action_declared":
                self._next_action_after_lose = "resolve_action"
            else:
                self._next_action_after_lose = "end_turn"
                self.broadcast_l("coup-bluff-wrong", challenger=player.name)
                self.broadcast_l("coup-block-successful", blocker=claimer.name)
                # We will just play the block success sound alongside the challenge success.
                # Technically we should maybe sequentialize this, but both are short.

            self.event_queue.append(
                (
                    self.sound_scheduler_tick + duration,
                    "post_challenge_lose_influence",
                    {"target_id": player.id, "reason": "failed_challenge"},
                )
            )

        else:
            # Challenge succeeds!
            self.play_sound("game_coup/challengefail.ogg")
            duration = self.get_audio_duration_ticks("challengefail.ogg")
            self.broadcast_l("coup-challenge-succeeded", player=claimer.name)

            if self.turn_phase == "action_declared":
                self._next_action_after_lose = "end_turn"
            elif self.turn_phase == "waiting_block":
                self._next_action_after_lose = "resolve_action"

            self.broadcast_l("coup-bluff-called", player=claimer.name)

            self.event_queue.append(
                (
                    self.sound_scheduler_tick + duration,
                    "post_challenge_lose_influence",
                    {"target_id": claimer.id, "reason": "lost_challenge"},
                )
            )

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()

        if not self.game_active:
            return

        self._process_events()

        if self.interrupt_timer_ticks > 0 and not self.is_resolving:
            self.interrupt_timer_ticks -= 1
            if self.interrupt_timer_ticks == 0:
                # Timer expired! Resolve current state
                if self.turn_phase == "action_declared":
                    # Nobody challenged or blocked, action resolves
                    self._resolve_action()
                elif self.turn_phase == "waiting_block":
                    # Nobody challenged the block, action fails
                    self.is_resolving = True
                    self.rebuild_all_menus()
                    blocker = self.get_player_by_id(self.active_claimer_id)
                    self.broadcast_l(
                        "coup-block-successful", blocker=blocker.name if blocker else "Someone"
                    )
                    sound_file = ""
                    if self.active_action == "foreign_aid":
                        sound_file = "block_duke.ogg"
                        self.play_sound(f"game_coup/{sound_file}")
                    elif self.active_action == "assassinate":
                        sound_file = "block_contessa.ogg"
                        self.play_sound(f"game_coup/{sound_file}")
                    elif self.active_action == "steal":
                        sound_file = "block_stealing.ogg"
                        self.play_sound(f"game_coup/{sound_file}")

                    duration = self.get_audio_duration_ticks(sound_file) if sound_file else 0
                    self.event_queue.append(
                        (self.sound_scheduler_tick + duration, "post_block_success", {})
                    )

        CoupBot.on_tick(self)

    def _resolve_action(self) -> None:
        """Resolves the active action after no challenges/blocks occur or they fail."""
        self.broadcast_l("coup-action-resolves")
        player = self.get_player_by_id(self.original_claimer_id)
        target = self.get_player_by_id(self.active_target_id)

        if not player:
            self._end_turn()
            return

        if self.active_action == "foreign_aid":
            player.coins += 2
            self.play_sound("game_coup/foreign_aid.ogg")
            self.broadcast_l("coup-takes-foreign-aid", player=player.name)
            self._end_turn()

        elif self.active_action == "tax":
            player.coins += 3
            self.play_sound("game_coup/tax.ogg")
            self.broadcast_l("coup-takes-tax", player=player.name)
            self._end_turn()

        elif self.active_action == "assassinate":
            self.is_resolving = True
            self.rebuild_all_menus()

            sound_file = "assassinate.ogg"
            self.play_sound(f"game_coup/{sound_file}")
            self.broadcast_l(
                "coup-assassinates", player=player.name, target=target.name if target else ""
            )

            duration = self.get_audio_duration_ticks(sound_file)
            self.event_queue.append(
                (
                    self.sound_scheduler_tick + duration,
                    "prompt_lose_influence",
                    {"target_id": target.id if target else "", "reason": "assassinated"},
                )
            )

        elif self.active_action == "steal":
            stolen = min(2, target.coins) if target else 0
            if target:
                target.coins -= stolen
            player.coins += stolen
            self.play_sound("game_coup/steal.ogg")
            self.broadcast_l(
                "coup-steals",
                player=player.name,
                target=target.name if target else "",
                amount=stolen,
            )
            self._end_turn()

        elif self.active_action == "exchange":
            self.play_sound("game_coup/exchange_start.ogg")
            self.broadcast_l("coup-exchanges", player=player.name)

            # Add 2 cards to hand, transition to exchange phase instantly
            card1 = self.deck.draw()
            card2 = self.deck.draw()
            if card1:
                player.influences.append(card1)
                self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")
            if card2:
                player.influences.append(card2)
                self.play_sound(f"game_cards/draw{random.randint(1, 4)}.ogg")

            if player.id in self.player_claims:
                self.player_claims[player.id].clear()

            self.turn_phase = "exchanging"
            self.interrupt_timer_ticks = 0
            self.rebuild_all_menus()

            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))

    def _action_return_card(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "exchanging" or self.current_player != player:
            return

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return

        if idx < 0 or idx >= len(coup_player.live_influences):
            return

        card = coup_player.live_influences[idx]
        self.deck.add(card)
        self.deck.shuffle()
        coup_player.influences.remove(card)
        self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")

        user = self.get_user(player)
        if user:
            card_name = Localization.get(user.locale, f"coup-card-{card.character.value}")
            user.speak_l("coup-returned-card", buffer="table", character=card_name)

        # Check if we are done exchanging
        # Target live is original live count (usually 2, sometimes 1)
        # We had live_count + 2 cards. We return 2.
        # So when len(live) == expected, we are done.
        # For now, just count if we've returned 2.
        # It's easier: if len(live) > (2 if alive else 1), keep returning
        # But wait, max normal live is 2. So we return until live == (original count).
        # We don't explicitly store original count.
        # But since we draw 2, we return 2.
        # We need to track how many we returned.
        # Let's just track it via the deck state, but simpler: Add a state variable.
        if getattr(self, "return_count", 0) == 0:
            self.return_count = 1
            self.rebuild_all_menus()
        else:
            self.return_count = 0
            self.play_sound("game_coup/exchange_complete.ogg")
            self.broadcast_l("coup-exchange-complete", player=player.name)
            self._end_turn()

    def _broadcast_card_message(
        self, message_key: str, character: str | Character, **kwargs
    ) -> None:
        """Broadcast a message with a localized card name to all players."""
        char_val = character.value if hasattr(character, "value") else character
        for p in self.players:  # Broadcast to everyone, including spectators
            user = self.get_user(p)
            if not user:
                continue
            card_name = Localization.get(user.locale, f"coup-card-{char_val}")
            user.speak_l(message_key, buffer="table", character=card_name, **kwargs)

    def _prompt_lose_influence(self, player_id: str, reason: str) -> None:
        """Prompts a player to choose which influence to lose."""
        player = self.get_player_by_id(player_id)
        if not player or player.is_dead:
            self._post_lose_influence()
            return

        live = player.live_influences
        if len(live) == 0:
            self._post_lose_influence()
            return
        elif len(live) == 1:
            # Only one left, auto-lose it
            self._losing_player_id = player.id
            self.play_sound(f"game_coup/chardestroy{random.randint(1, 2)}.ogg")
            self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")
            player.reveal_influence(0)
            self._broadcast_card_message(
                "coup-loses-influence", live[0].character, player=player.name
            )
            if player.is_dead:
                self.broadcast_l("coup-player-eliminated", player=player.name)
            self._post_lose_influence()
        else:
            # Need to pick — use _losing_player_id so active_target_id is never overwritten
            self._losing_player_id = player.id
            self.turn_phase = "losing_influence"
            self.rebuild_all_menus()

            if player.is_bot:
                BotHelper.jolt_bot(player, ticks=random.randint(10, 20))
            else:
                user = self.get_user(player)
                if user:
                    user.speak_l("coup-must-lose-influence", buffer="table")

    def _action_lose_influence(self, player: Player, action_id: str) -> None:
        if self.turn_phase != "losing_influence" or player.id != self._losing_player_id:
            return

        coup_player: CoupPlayer = player  # type: ignore
        try:
            idx = int(action_id.split("_")[-1])
        except ValueError:
            return

        if idx < 0 or idx >= len(coup_player.live_influences):
            return

        self.is_resolving = True
        self.rebuild_all_menus()

        sound_file = f"chardestroy{random.randint(1, 2)}.ogg"
        self.play_sound(f"game_coup/{sound_file}")
        self.play_sound(f"game_cards/discard{random.randint(1, 3)}.ogg")

        char = coup_player.live_influences[idx].character
        coup_player.reveal_influence(idx)
        self._broadcast_card_message("coup-loses-influence", char, player=player.name)
        if coup_player.is_dead:
            self.broadcast_l("coup-player-eliminated", player=player.name)

        duration = self.get_audio_duration_ticks(sound_file)
        self.event_queue.append((self.sound_scheduler_tick + duration, "post_lose_influence", {}))

    def _post_lose_influence(self) -> None:
        if self._losing_player_id and self._losing_player_id in self.player_claims:
            self.player_claims[self._losing_player_id].clear()
        self._losing_player_id = ""

        next_action = self._next_action_after_lose
        self._next_action_after_lose = "end_turn"

        if next_action == "end_turn":
            self._end_turn()
        elif next_action == "resolve_action":
            self._resolve_action()

    def _end_game(self, winner: CoupPlayer | None) -> None:
        """End the game."""
        self.play_sound("game_chaosbear/wingame.ogg")
        if winner:
            self.broadcast_l("game-winner", player=winner.name)
        self.finish_game()

    def build_game_result(self) -> GameResult:
        """Build the game result with Coup-specific data."""
        alive = self.get_alive_players()
        winner = alive[0] if alive else None

        active_players = self.get_active_players()
        # Sort players: winner first, then by coins
        sorted_players = sorted(
            active_players, key=lambda p: (not p.is_dead, p.coins), reverse=True
        )

        rankings = []
        for p in sorted_players:
            dead_cards = [c.character.value for c in p.dead_influences]
            if not p.is_dead:
                dead_cards.extend(
                    [c.character.value for c in p.live_influences]
                )  # show remaining too!

            rankings.append(
                {"name": p.name, "coins": p.coins, "cards": dead_cards, "is_winner": p == winner}
            )

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
                for p in active_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_ids": [winner.id] if winner else None,
                "winner_score": 1,
                "rankings": rankings,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for Coup."""
        lines = [Localization.get(locale, "game-final-scores")]
        rankings = result.custom_data.get("rankings", [])

        for i, data in enumerate(rankings, 1):
            name = data["name"]
            coins = data["coins"]
            cards = data["cards"]

            loc_cards = [Localization.get(locale, f"coup-card-{c}") for c in cards]
            cards_str = (
                ", ".join(loc_cards) if loc_cards else Localization.get(locale, "coup-no-cards")
            )

            if data.get("is_winner"):
                status = Localization.get(locale, "coup-end-winner")
            else:
                status = Localization.get(locale, "coup-end-eliminated")

            line = Localization.get(
                locale,
                "coup-end-line",
                rank=i,
                name=name,
                status=status,
                coins=coins,
                cards=cards_str,
            )
            lines.append(line)

        return lines

    def get_alive_players(self) -> list[CoupPlayer]:
        """Get all alive players."""
        return [
            p
            for p in self.players
            if not getattr(p, "is_spectator", False) and not getattr(p, "is_dead", False)
        ]
