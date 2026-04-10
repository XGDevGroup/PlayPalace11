"""Classic Draw / Block Dominos for PlayPalace v11."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from mashumaro.mixins.json import DataClassJSONMixin

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility, MenuInput
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, MenuOption, BoolOption, TeamModeOption, option_field
from ...game_utils.teams import TeamManager
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


DRAW_MODE_CHOICES = ["draw", "block"]
DRAW_MODE_LABELS = {
    "draw": "dominos-mode-draw",
    "block": "dominos-mode-block",
}

SET_CHOICES = ["double6", "double9"]
SET_LABELS = {
    "double6": "dominos-set-double6",
    "double9": "dominos-set-double9",
}

OPENING_RULE_CHOICES = [
    "highest_double",
    "highest_tile",
    "set_max_double",
    "random",
    "round_winner",
]
OPENING_RULE_LABELS = {
    "highest_double": "dominos-opening-highest-double",
    "highest_tile": "dominos-opening-highest-tile",
    "set_max_double": "dominos-opening-set-max-double",
    "random": "dominos-opening-random-player",
    "round_winner": "dominos-opening-round-winner",
}

BRANCH_ORDER = ["left", "right", "up", "down"]
PLAY_ACTION_PREFIX = "play_tile_"

SOUND_DRAW = "game_dominos/draw.ogg"
SOUND_KNOCK = "game_dominos/knock.ogg"
SOUND_BLOCKED = "game_dominos/blocked.ogg"
SOUND_VIEW_CHAIN = "game_dominos/viewchain.ogg"
SOUND_MUSIC = "game_dominos/mus.ogg"
SOUND_WIN_ROUND = "game_pig/win.ogg"
SOUND_WIN_GAME = "game_pig/wingame.ogg"
SOUND_PLAY = [
    "game_dominos/play1.ogg",
    "game_dominos/play2.ogg",
    "game_dominos/play3.ogg",
    "game_dominos/play4.ogg",
]
SOUND_SHUFFLE = [
    "game_dominos/shuffle1.ogg",
    "game_dominos/shuffle2.ogg",
]


@dataclass
class DominoTile(DataClassJSONMixin):
    id: int
    left: int
    right: int

    @property
    def is_double(self) -> bool:
        return self.left == self.right

    @property
    def pip_total(self) -> int:
        return self.left + self.right

    @property
    def high(self) -> int:
        return max(self.left, self.right)

    @property
    def low(self) -> int:
        return min(self.left, self.right)

    def matches(self, value: int) -> bool:
        return self.left == value or self.right == value

    def orient_for(self, inward: int) -> tuple[int, int]:
        if self.left == inward:
            return self.left, self.right
        if self.right == inward:
            return self.right, self.left
        raise ValueError(f"Tile {self.left}-{self.right} does not match {inward}")

    def display(self) -> str:
        return f"{self.left}-{self.right}"


@dataclass
class PlacedDomino(DataClassJSONMixin):
    tile: DominoTile
    branch: str
    inward: int
    outward: int

    def display(self) -> str:
        return f"{self.inward}-{self.outward}"


@dataclass
class DominosPlayer(Player):
    hand: list[DominoTile] = field(default_factory=list)


@dataclass
class DominosOptions(GameOptions):
    target_score: int = option_field(
        IntOption(
            default=100,
            min_val=20,
            max_val=500,
            value_key="score",
            label="dominos-set-target-score",
            prompt="dominos-enter-target-score",
            change_msg="dominos-option-changed-target-score",
            description="dominos-desc-target-score",
        )
    )
    draw_mode: str = option_field(
        MenuOption(
            choices=DRAW_MODE_CHOICES,
            default="draw",
            label="dominos-set-draw-mode",
            prompt="dominos-select-draw-mode",
            change_msg="dominos-option-changed-draw-mode",
            choice_labels=DRAW_MODE_LABELS,
            description="dominos-desc-draw-mode",
        )
    )
    domino_set: str = option_field(
        MenuOption(
            choices=SET_CHOICES,
            default="double6",
            value_key="domino_set",
            label="dominos-set-domino-set",
            prompt="dominos-select-domino-set",
            change_msg="dominos-option-changed-domino-set",
            choice_labels=SET_LABELS,
            description="dominos-desc-domino-set",
        )
    )
    spinner_enabled: bool = option_field(
        BoolOption(
            default=True,
            value_key="enabled",
            label="dominos-set-spinner",
            change_msg="dominos-option-changed-spinner",
            description="dominos-desc-spinner",
        )
    )
    opening_rule: str = option_field(
        MenuOption(
            choices=OPENING_RULE_CHOICES,
            default="highest_double",
            value_key="opening_rule",
            label="dominos-set-opening-rule",
            prompt="dominos-select-opening-rule",
            change_msg="dominos-option-changed-opening-rule",
            choice_labels=OPENING_RULE_LABELS,
            description="dominos-desc-opening-rule",
        )
    )
    team_mode: str = option_field(
        TeamModeOption(
            default="individual",
            value_key="mode",
            choices=lambda g, p: TeamManager.get_all_team_modes(2, 4),
            label="game-set-team-mode",
            prompt="game-select-team-mode",
            change_msg="game-option-changed-team",
        )
    )


def build_domino_set(max_pip: int) -> list[DominoTile]:
    tiles: list[DominoTile] = []
    tile_id = 0
    for left in range(max_pip + 1):
        for right in range(left, max_pip + 1):
            tiles.append(DominoTile(id=tile_id, left=left, right=right))
            tile_id += 1
    random.shuffle(tiles)
    return tiles


@register_game
@dataclass
class DominosGame(Game):
    players: list[DominosPlayer] = field(default_factory=list)
    options: DominosOptions = field(default_factory=DominosOptions)

    boneyard: list[DominoTile] = field(default_factory=list)
    center_tile: DominoTile | None = None
    branches: dict[str, list[PlacedDomino]] = field(
        default_factory=lambda: {branch: [] for branch in BRANCH_ORDER}
    )
    open_ends: dict[str, int] = field(default_factory=dict)
    spinner_active: bool = False
    consecutive_passes: int = 0
    previous_round_winner_id: str | None = None
    opening_player_id: str | None = None
    round_wait_ticks: int = 0

    @classmethod
    def get_name(cls) -> str:
        return "Dominos"

    @classmethod
    def get_type(cls) -> str:
        return "dominos"

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

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> DominosPlayer:
        return DominosPlayer(id=player_id, name=name, is_bot=is_bot)

    def prestart_validate(self) -> list[str] | list[tuple[str, dict]]:
        errors: list[str] = []
        team_error = self._validate_team_mode(self.options.team_mode)
        if team_error:
            errors.append(team_error)
        return errors

    def create_turn_action_set(self, player: DominosPlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"
        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="draw",
                label=Localization.get(locale, "dominos-draw"),
                handler="_action_draw",
                is_enabled="_is_draw_enabled",
                is_hidden="_is_draw_hidden",
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="knock",
                label=Localization.get(locale, "dominos-knock"),
                handler="_action_knock",
                is_enabled="_is_knock_enabled",
                is_hidden="_is_knock_hidden",
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
                id="view_chain",
                label=Localization.get(locale, "dominos-view-chain"),
                handler="_action_view_chain",
                is_enabled="_is_view_chain_enabled",
                is_hidden="_is_view_chain_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_ends",
                label=Localization.get(locale, "dominos-read-ends"),
                handler="_action_read_ends",
                is_enabled="_is_view_chain_enabled",
                is_hidden="_is_view_chain_hidden",
                include_spectators=True,
            )
        )
        action_set.add(
            Action(
                id="read_hand",
                label=Localization.get(locale, "dominos-read-hand"),
                handler="_action_read_hand",
                is_enabled="_is_read_hand_enabled",
                is_hidden="_is_read_hand_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_counts",
                label=Localization.get(locale, "dominos-read-counts"),
                handler="_action_read_counts",
                is_enabled="_is_read_counts_enabled",
                is_hidden="_is_read_counts_hidden",
                include_spectators=True,
            )
        )
        self._apply_standard_action_order(action_set, user)
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("space", "Draw", ["draw"], state=KeybindState.ACTIVE)
        self.define_keybind("p", "Knock", ["knock"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "v", "View chain", ["view_chain"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "c", "Read ends", ["read_ends"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind(
            "e", "Read counts", ["read_counts"], state=KeybindState.ACTIVE, include_spectators=True
        )
        self.define_keybind("w", "Read hand", ["read_hand"], state=KeybindState.ACTIVE)

    def rebuild_player_menu(self, player: Player) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().rebuild_player_menu(player)

    def update_player_menu(self, player: Player, selection_id: str | None = None) -> None:
        self._sync_turn_actions(player)
        self._sync_standard_actions(player)
        super().update_player_menu(player, selection_id=selection_id)

    def rebuild_all_menus(self) -> None:
        for player in self.players:
            self._sync_turn_actions(player)
            self._sync_standard_actions(player)
        super().rebuild_all_menus()

    def _sync_standard_actions(self, player: Player) -> None:
        standard_set = self.get_action_set(player, "standard")
        if not standard_set:
            return
        self._apply_standard_action_order(standard_set, self.get_user(player))

    def _apply_standard_action_order(self, action_set: ActionSet, user) -> None:
        custom_ids = ["view_chain", "read_ends", "read_hand", "read_counts"]
        action_set._order = [aid for aid in action_set._order if aid not in custom_ids] + [
            aid for aid in custom_ids if action_set.get_action(aid)
        ]
        if user and getattr(user, "client_type", "") == "web":
            target_order = [
                "read_ends",
                "read_hand",
                "view_chain",
                "read_counts",
                "check_scores",
                "whose_turn",
                "whos_at_table",
            ]
            new_order = [aid for aid in action_set._order if aid not in target_order]
            for aid in target_order:
                if action_set.get_action(aid):
                    new_order.append(aid)
            action_set._order = new_order

    def _is_whos_at_table_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web":
            return Visibility.VISIBLE
        return super()._is_whos_at_table_hidden(player)

    def _is_whose_turn_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_whose_turn_hidden(player)

    def _is_check_scores_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return super()._is_check_scores_hidden(player)

    def _is_draw_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        if self.options.draw_mode != "draw":
            return "dominos-draw-only-mode"
        dom_player = self._as_dominos_player(player)
        if not dom_player:
            return "action-not-available"
        if self._has_playable_move(dom_player):
            return "dominos-must-play"
        if not self.boneyard:
            return "dominos-boneyard-empty"
        return None

    def _is_draw_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or self.current_player != player:
            return Visibility.HIDDEN
        if self.options.draw_mode != "draw":
            return Visibility.HIDDEN
        if self._has_playable_move(self._as_dominos_player(player)):
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_knock_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        if self.current_player != player:
            return "action-not-your-turn"
        dom_player = self._as_dominos_player(player)
        if not dom_player:
            return "action-not-available"
        if self._has_playable_move(dom_player):
            return "dominos-must-play"
        if self.options.draw_mode == "draw" and self.boneyard:
            return "dominos-must-draw"
        return None

    def _is_knock_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator or self.current_player != player:
            return Visibility.HIDDEN
        dom_player = self._as_dominos_player(player)
        if dom_player is None or self._has_playable_move(dom_player):
            return Visibility.HIDDEN
        if self.options.draw_mode == "draw" and self.boneyard:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_view_chain_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_view_chain_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_hand_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_read_hand_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if (
            user
            and getattr(user, "client_type", "") == "web"
            and self.status == "playing"
            and not player.is_spectator
        ):
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_read_counts_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_read_counts_hidden(self, player: Player) -> Visibility:
        user = self.get_user(player)
        if user and getattr(user, "client_type", "") == "web" and self.status == "playing":
            return Visibility.VISIBLE
        return Visibility.HIDDEN

    def _is_play_tile_enabled(self, player: Player, *, action_id: str | None = None) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        dom_player = self._as_dominos_player(player)
        if not dom_player or not action_id:
            return "action-not-available"
        tile = self._parse_tile_action(dom_player, action_id)
        return None if tile else "action-not-available"

    def _is_play_tile_hidden(self, player: Player, *, action_id: str | None = None) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        dom_player = self._as_dominos_player(player)
        if not dom_player or not action_id:
            return Visibility.HIDDEN
        tile = self._parse_tile_action(dom_player, action_id)
        return Visibility.VISIBLE if tile else Visibility.HIDDEN

    def _get_play_tile_label(self, player: Player, action_id: str) -> str:
        dom_player = self._as_dominos_player(player)
        user = self.get_user(player)
        locale = user.locale if user else "en"
        if not dom_player:
            return action_id
        tile = self._parse_tile_action(dom_player, action_id)
        if tile is None:
            return action_id
        legal = self._legal_destinations(tile)
        if len(legal) == 1:
            return Localization.get(
                locale,
                "dominos-play-tile-at",
                tile=self._format_tile(tile),
                side=self._branch_name(legal[0], locale),
            )
        if legal:
            return Localization.get(
                locale,
                "dominos-play-tile-multi",
                tile=self._format_tile(tile),
                sides=self._join_branch_names(legal, locale),
            )
        return Localization.get(
            locale,
            "dominos-play-tile",
            tile=self._format_tile(tile),
        )

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self._sync_table_status()
        self.game_active = True
        self.round = 0
        self._setup_teams()
        self.set_turn_players(self.get_active_players())
        self.play_music(SOUND_MUSIC)
        self._start_round()

    def _setup_teams(self) -> None:
        active_players = self.get_active_players()
        self._team_manager.team_mode = self.options.team_mode
        self._team_manager.setup_teams([player.name for player in active_players])
        self.team_manager.reset_all_scores()

    def _start_round(self) -> None:
        self.round += 1
        self.round_wait_ticks = 0
        self.center_tile = None
        self.branches = {branch: [] for branch in BRANCH_ORDER}
        self.open_ends = {}
        self.spinner_active = False
        self.consecutive_passes = 0
        self.opening_player_id = None
        self.broadcast_l("game-round-start", buffer="table", round=self.round)
        self.play_sound(random.choice(SOUND_SHUFFLE))

        max_pip = 6 if self.options.domino_set == "double6" else 9
        self.boneyard = build_domino_set(max_pip)

        active_players = self.get_active_players()
        self.set_turn_players(active_players)
        for player in active_players:
            player.hand.clear()

        hand_size = self._get_hand_size()
        for _ in range(hand_size):
            for player in active_players:
                tile = self.boneyard.pop() if self.boneyard else None
                if tile:
                    player.hand.append(tile)

        opener, opening_tile = self._select_opening_play(active_players, max_pip)
        opener.hand.remove(opening_tile)
        self.opening_player_id = opener.id
        self._place_opening_tile(opening_tile)
        self._broadcast_opening_play(opener, opening_tile)

        opener_index = active_players.index(opener)
        self.turn_index = (opener_index + 1) % len(active_players)
        self._update_all_turn_actions()
        self.announce_turn()
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def _get_hand_size(self) -> int:
        player_count = len(self.get_active_players())
        if self.options.domino_set == "double6":
            return 7 if player_count == 2 else 5
        return 10 if player_count == 2 else 7

    def _select_opening_play(
        self, active_players: list[DominosPlayer], max_pip: int
    ) -> tuple[DominosPlayer, DominoTile]:
        rule = self.options.opening_rule
        if rule == "round_winner":
            opener = self.get_player_by_id(self.previous_round_winner_id or "")
            if isinstance(opener, DominosPlayer) and opener in active_players and opener.hand:
                return opener, self._best_tile(opener.hand)
            rule = "highest_double"

        if rule == "random":
            opener = random.choice(active_players)
            return opener, self._best_tile(opener.hand)

        if rule == "set_max_double":
            exact_double = next(
                (
                    (player, tile)
                    for player in active_players
                    for tile in player.hand
                    if tile.left == max_pip and tile.right == max_pip
                ),
                None,
            )
            if exact_double:
                return exact_double
            rule = "highest_double"

        if rule == "highest_double":
            best: tuple[DominosPlayer, DominoTile] | None = None
            for player in active_players:
                doubles = [tile for tile in player.hand if tile.is_double]
                if not doubles:
                    continue
                tile = max(doubles, key=self._opening_tile_key)
                if best is None or self._opening_tile_key(tile) > self._opening_tile_key(best[1]):
                    best = (player, tile)
            if best:
                return best
            rule = "highest_tile"

        best = max(
            ((player, tile) for player in active_players for tile in player.hand),
            key=lambda item: self._opening_tile_key(item[1]),
        )
        return best

    def _opening_tile_key(self, tile: DominoTile) -> tuple[int, int, int]:
        return (tile.pip_total, tile.high, tile.low)

    def _best_tile(self, tiles: list[DominoTile]) -> DominoTile:
        return max(tiles, key=self._opening_tile_key)

    def _place_opening_tile(self, tile: DominoTile) -> None:
        self.center_tile = tile
        if tile.is_double and self.options.spinner_enabled:
            self.spinner_active = True
            self.open_ends = {branch: tile.left for branch in BRANCH_ORDER}
        else:
            self.spinner_active = False
            self.open_ends = {"left": tile.left, "right": tile.right}

    def _broadcast_opening_play(self, opener: DominosPlayer, tile: DominoTile) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            if self.spinner_active:
                user.speak_l(
                    "dominos-opening-spinner",
                    buffer="table",
                    player=opener.name,
                    tile=self._format_tile(tile),
                )
            else:
                user.speak_l(
                    "dominos-opening-play",
                    buffer="table",
                    player=opener.name,
                    tile=self._format_tile(tile),
                )

    def _action_draw(self, player: Player, action_id: str) -> None:
        dom_player = self._as_dominos_player(player)
        user = self.get_user(player)
        if not dom_player or not user:
            return
        if self._is_draw_enabled(player) is not None:
            return

        drawn_tiles: list[DominoTile] = []
        playable_tile: DominoTile | None = None
        while self.boneyard:
            tile = self.boneyard.pop()
            dom_player.hand.append(tile)
            drawn_tiles.append(tile)
            if self._legal_destinations(tile):
                playable_tile = tile
                break

        self.play_sound(SOUND_DRAW)
        self._broadcast_draw(dom_player, drawn_tiles)

        if playable_tile is None:
            self._handle_knock(dom_player)
            return

        branch = self._legal_destinations(playable_tile)[0]
        self._execute_play(dom_player, playable_tile, branch, auto_played=True)

    def _action_knock(self, player: Player, action_id: str) -> None:
        dom_player = self._as_dominos_player(player)
        if not dom_player:
            return
        if self._is_knock_enabled(player) is not None:
            return
        self._handle_knock(dom_player)

    def _action_view_chain(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        user.play_sound(SOUND_VIEW_CHAIN)
        self.status_box(player, self._build_chain_lines(user.locale))

    def _action_read_ends(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        visible_branches = BRANCH_ORDER if self.spinner_active else ["left", "right"]
        parts = [
            Localization.get(
                locale,
                "dominos-end-info",
                side=self._branch_name(branch, locale),
                value=self.open_ends.get(branch, 0),
            )
            for branch in visible_branches
            if branch in self.open_ends
        ]
        if not parts:
            user.speak_l("dominos-chain-empty", buffer="table")
            return
        user.speak(", ".join(parts), buffer="table")

    def _action_read_hand(self, player: Player, action_id: str) -> None:
        dom_player = self._as_dominos_player(player)
        user = self.get_user(player)
        if not dom_player or not user:
            return
        for line in self._build_hand_lines(dom_player, user.locale):
            user.speak(line, "game")

    def _action_read_counts(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        locale = user.locale
        parts = []
        for other in self.turn_players:
            if other.is_spectator or other.id == player.id:
                continue
            if isinstance(other, DominosPlayer):
                parts.append(
                    Localization.get(
                        locale,
                        "dominos-player-count",
                        player=other.name,
                        count=len(other.hand),
                    )
                )
        text = ", ".join(parts) if parts else Localization.get(locale, "dominos-no-other-players")
        user.speak(text, buffer="table")

    def _action_play_tile(self, player: Player, *args) -> None:
        dom_player = self._as_dominos_player(player)
        if not dom_player:
            return
        if self.current_player != player:
            user = self.get_user(player)
            if user:
                user.speak_l("action-not-your-turn", buffer="table")
            return
        input_value: str | None = None
        action_id = ""
        if len(args) == 1:
            action_id = args[0]
        elif len(args) == 2:
            input_value, action_id = args
        tile = self._parse_tile_action(dom_player, action_id)
        if tile is None:
            return
        legal = self._legal_destinations(tile)
        if not legal:
            user = self.get_user(player)
            if user:
                user.speak_l(
                    "dominos-no-play-for-tile", buffer="table", tile=self._format_tile(tile)
                )
            return
        if input_value is not None:
            branch = self._branch_from_input(input_value, self._player_locale(player), legal)
            if branch is None:
                return
            self._execute_play(dom_player, tile, branch)
            return
        if len(legal) == 1:
            self._execute_play(dom_player, tile, legal[0])
            return
        if dom_player.is_bot:
            self._execute_play(dom_player, tile, legal[0])
            return
        user = self.get_user(player)
        if user:
            user.speak_l(
                "dominos-choose-side-keybind",
                buffer="table",
                sides=self._join_branch_names(legal, user.locale),
            )

    def _execute_play(
        self,
        player: DominosPlayer,
        tile: DominoTile,
        branch: str,
        *,
        auto_played: bool = False,
    ) -> None:
        if branch not in self._legal_destinations(tile):
            user = self.get_user(player)
            if user:
                user.speak_l("dominos-illegal-side", buffer="table")
            return

        open_value = self.open_ends[branch]
        inward, outward = tile.orient_for(open_value)
        player.hand.remove(tile)
        self.branches.setdefault(branch, []).append(
            PlacedDomino(tile=tile, branch=branch, inward=inward, outward=outward)
        )
        self.open_ends[branch] = outward
        self.consecutive_passes = 0
        self.play_sound(random.choice(SOUND_PLAY))
        self._broadcast_play(player, tile, branch, auto_played=auto_played)

        if not player.hand:
            self._finish_round_from_empty_hand(player)
            return

        self._advance_to_next_turn()

    def _handle_knock(self, player: DominosPlayer) -> None:
        self.consecutive_passes += 1
        self.play_sound(SOUND_KNOCK)
        self.broadcast_l("dominos-player-knocks", buffer="table", player=player.name)
        if self._is_round_blocked():
            self._finish_blocked_round()
            return
        self._advance_to_next_turn()

    def _advance_to_next_turn(self) -> None:
        self.advance_turn(announce=False)
        self._update_all_turn_actions()
        self.announce_turn()
        self.rebuild_all_menus()
        self._queue_bot_turn()

    def _finish_round_from_empty_hand(self, winner: DominosPlayer) -> None:
        points = self._opponent_pip_total(winner)
        self.team_manager.add_to_team_score(winner.name, points)
        self.previous_round_winner_id = winner.id
        self.broadcast_l("dominos-round-won", buffer="table", player=winner.name, points=points)
        self.play_sound(SOUND_WIN_ROUND)
        if self._check_match_winner():
            return
        self._schedule_next_round()

    def _finish_blocked_round(self) -> None:
        self.play_sound(SOUND_BLOCKED)
        team_totals = self._team_pip_totals()
        lowest_total = min(team_totals.values())
        winning_team_indexes = [
            team_idx for team_idx, total in team_totals.items() if total == lowest_total
        ]

        if len(winning_team_indexes) != 1:
            self.previous_round_winner_id = None
            self.broadcast_l("dominos-round-blocked-tie", buffer="table", pips=lowest_total)
            self._schedule_next_round()
            return

        winning_team_idx = winning_team_indexes[0]
        winning_team = self.team_manager.teams[winning_team_idx]
        points = sum(
            total for team_idx, total in team_totals.items() if team_idx != winning_team_idx
        )
        if winning_team.members:
            self.team_manager.add_to_team_score(winning_team.members[0], points)

        opening_player = next(
            (player for player in self.get_active_players() if player.name in winning_team.members),
            None,
        )
        self.previous_round_winner_id = opening_player.id if opening_player else None
        self._broadcast_blocked_round_winner(winning_team, lowest_total, points)
        self.play_sound(SOUND_WIN_ROUND)
        if self._check_match_winner():
            return
        self._schedule_next_round()

    def _check_match_winner(self) -> bool:
        leaders = self.team_manager.get_teams_at_or_above_score(self.options.target_score)
        if not leaders:
            return False

        top_score = max(team.total_score for team in leaders)
        top_teams = [team for team in leaders if team.total_score == top_score]
        if len(top_teams) != 1:
            self.broadcast_l("dominos-match-tied-continue", buffer="table", score=top_score)
            return False

        winner = top_teams[0]
        self.play_sound(SOUND_WIN_GAME)
        self._broadcast_match_winner(winner)
        self.finish_game()
        return True

    def _schedule_next_round(self) -> None:
        self.round_wait_ticks = 5 * 20
        for player in self.get_active_players():
            player.hand = []
        self.rebuild_all_menus()

    def _team_pip_totals(self) -> dict[int, int]:
        totals: dict[int, int] = {team.index: 0 for team in self.team_manager.teams}
        for player in self.get_active_players():
            team = self.team_manager.get_team(player.name)
            if not team:
                continue
            totals[team.index] += sum(tile.pip_total for tile in player.hand)
        return totals

    def _opponent_pip_total(self, winner: DominosPlayer) -> int:
        winner_team = self.team_manager.get_team(winner.name)
        total = 0
        for player in self.get_active_players():
            if winner_team and player.name in winner_team.members:
                continue
            total += sum(tile.pip_total for tile in player.hand)
        return total

    def _legal_destinations(self, tile: DominoTile) -> list[str]:
        legal: list[str] = []
        for branch in BRANCH_ORDER:
            open_value = self.open_ends.get(branch)
            if open_value is None:
                continue
            if tile.matches(open_value):
                legal.append(branch)
        return legal

    def _is_round_blocked(self) -> bool:
        active_players = self.get_active_players()
        if not active_players:
            return False
        if self.options.draw_mode == "draw" and self.boneyard:
            return False
        return not any(self._has_playable_move(player) for player in active_players)

    def _has_playable_move(self, player: DominosPlayer | None) -> bool:
        if player is None:
            return False
        return any(self._legal_destinations(tile) for tile in player.hand)

    def _parse_tile_action(self, player: DominosPlayer, action_id: str) -> DominoTile | None:
        if not action_id.startswith(PLAY_ACTION_PREFIX):
            return None
        tile_id_text = action_id.removeprefix(PLAY_ACTION_PREFIX)
        if not tile_id_text:
            return None
        try:
            tile_id = int(tile_id_text)
        except ValueError:
            return None
        return next((item for item in player.hand if item.id == tile_id), None)

    def _tile_action_id(self, tile: DominoTile) -> str:
        return f"{PLAY_ACTION_PREFIX}{tile.id}"

    def _sync_turn_actions(self, player: Player) -> None:
        dom_player = self._as_dominos_player(player)
        if dom_player is None:
            return
        action_sets = self.player_action_sets.get(player.id, [])
        turn_set = next(
            (action_set for action_set in action_sets if action_set.name == "turn"), None
        )
        if turn_set is None:
            return

        turn_set.remove_by_prefix(PLAY_ACTION_PREFIX)
        turn_set.remove("draw")
        turn_set.remove("knock")
        if self.status != "playing" or dom_player.is_spectator:
            return
        if self.round_wait_ticks > 0:
            return

        tile_ids: list[str] = []
        for tile in self._sorted_tiles(dom_player.hand):
            input_request = None
            if len(self._legal_destinations(tile)) > 1 and not dom_player.is_bot:
                input_request = MenuInput(
                    prompt="dominos-select-side",
                    options="_placement_options_for_tile",
                    bot_select="_bot_select_side_for_tile",
                )
            action_id = self._tile_action_id(tile)
            turn_set.add(
                Action(
                    id=action_id,
                    label="",
                    handler="_action_play_tile",
                    is_enabled="_is_play_tile_enabled",
                    is_hidden="_is_play_tile_hidden",
                    get_label="_get_play_tile_label",
                    input_request=input_request,
                    show_in_actions_menu=False,
                )
            )
            tile_ids.append(action_id)

        if self.current_player == dom_player:
            locale = self._player_locale(dom_player)
            turn_set.add(
                Action(
                    id="draw",
                    label=Localization.get(locale, "dominos-draw"),
                    handler="_action_draw",
                    is_enabled="_is_draw_enabled",
                    is_hidden="_is_draw_hidden",
                    show_in_actions_menu=False,
                )
            )
            turn_set.add(
                Action(
                    id="knock",
                    label=Localization.get(locale, "dominos-knock"),
                    handler="_action_knock",
                    is_enabled="_is_knock_enabled",
                    is_hidden="_is_knock_hidden",
                    show_in_actions_menu=False,
                )
            )

        utility_ids = ["draw", "knock"]
        turn_set._order = tile_ids + [
            action_id for action_id in utility_ids if turn_set.get_action(action_id)
        ]

    def _update_all_turn_actions(self) -> None:
        for player in self.get_active_players():
            self._sync_turn_actions(player)

    def _sorted_tiles(self, tiles: list[DominoTile]) -> list[DominoTile]:
        return sorted(tiles, key=lambda tile: (-tile.pip_total, -tile.high, -tile.low, tile.id))

    def _build_chain_lines(self, locale: str) -> list[str]:
        lines = [Localization.get(locale, "dominos-chain-header")]
        if self.center_tile is None:
            lines.append(Localization.get(locale, "dominos-chain-empty"))
            return lines

        lines.append(
            Localization.get(
                locale, "dominos-chain-center", tile=self._format_tile(self.center_tile)
            )
        )
        visible_branches = BRANCH_ORDER if self.spinner_active else ["left", "right"]
        for branch in visible_branches:
            placements = self.branches.get(branch, [])
            branch_tiles = ", ".join(placed.display() for placed in placements)
            if not branch_tiles:
                branch_tiles = Localization.get(locale, "dominos-branch-empty")
            lines.append(
                Localization.get(
                    locale,
                    "dominos-chain-branch",
                    side=self._branch_name(branch, locale),
                    tiles=branch_tiles,
                    open_end=self.open_ends.get(branch, 0),
                )
            )
        lines.append(Localization.get(locale, "dominos-boneyard-count", count=len(self.boneyard)))
        return lines

    def _build_hand_lines(self, player: DominosPlayer, locale: str) -> list[str]:
        lines = [Localization.get(locale, "dominos-hand-header")]
        for tile in self._sorted_tiles(player.hand):
            legal = self._legal_destinations(tile)
            if legal:
                sides = self._join_branch_names(legal, locale)
                lines.append(
                    Localization.get(
                        locale,
                        "dominos-hand-line-playable",
                        tile=self._format_tile(tile),
                        points=tile.pip_total,
                        sides=sides,
                    )
                )
            else:
                lines.append(
                    Localization.get(
                        locale,
                        "dominos-hand-line",
                        tile=self._format_tile(tile),
                        points=tile.pip_total,
                    )
                )
        lines.append(
            Localization.get(
                locale,
                "dominos-hand-total",
                pips=sum(tile.pip_total for tile in player.hand),
            )
        )
        return lines

    def _placement_options_for_tile(self, player: DominosPlayer) -> list[str]:
        action_id = self._pending_actions.get(player.id)
        tile = self._parse_tile_action(player, action_id or "")
        if tile is None:
            return []
        locale = self._player_locale(player)
        return [self._branch_name(branch, locale) for branch in self._legal_destinations(tile)]

    def _bot_select_side_for_tile(self, player: DominosPlayer, options: list[str]) -> str | None:
        return options[0] if options else None

    def _branch_from_input(self, input_value: str, locale: str, legal: list[str]) -> str | None:
        for branch in legal:
            if self._branch_name(branch, locale) == input_value:
                return branch
        return None

    def _broadcast_draw(self, player: DominosPlayer, drawn_tiles: list[DominoTile]) -> None:
        if not drawn_tiles:
            return
        self.broadcast_l(
            "dominos-player-draws",
            buffer="table",
            player=player.name,
            count=len(drawn_tiles),
        )
        user = self.get_user(player)
        if user:
            if len(drawn_tiles) == 1:
                user.speak_l(
                    "dominos-you-drew-single",
                    buffer="table",
                    tile=self._format_tile(drawn_tiles[0]),
                )
            else:
                user.speak_l(
                    "dominos-you-drew-many",
                    buffer="table",
                    count=len(drawn_tiles),
                )

    def _broadcast_play(
        self,
        player: DominosPlayer,
        tile: DominoTile,
        branch: str,
        *,
        auto_played: bool,
    ) -> None:
        for other in self.players:
            user = self.get_user(other)
            if not user:
                continue
            if other is player:
                user.speak_l(
                    "dominos-you-played-drawn" if auto_played else "dominos-you-played",
                    buffer="table",
                    tile=self._format_tile(tile),
                    side=self._branch_name(branch, user.locale),
                )
            else:
                user.speak_l(
                    "dominos-player-played",
                    buffer="table",
                    player=player.name,
                    tile=self._format_tile(tile),
                    side=self._branch_name(branch, user.locale),
                )

    def _broadcast_blocked_round_winner(self, winning_team, lowest_total: int, points: int) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            team_name = self.team_manager.get_team_name(winning_team, user.locale)
            user.speak_l(
                "dominos-round-blocked-winner",
                buffer="table",
                team=team_name,
                pips=lowest_total,
                points=points,
            )

    def _broadcast_match_winner(self, winning_team) -> None:
        for player in self.players:
            user = self.get_user(player)
            if not user:
                continue
            team_name = self.team_manager.get_team_name(winning_team, user.locale)
            user.speak_l(
                "dominos-match-winner",
                buffer="table",
                team=team_name,
                score=winning_team.total_score,
            )

    def _format_tile(self, tile: DominoTile) -> str:
        return tile.display()

    def _branch_name(self, branch: str, locale: str) -> str:
        return Localization.get(locale, f"dominos-side-{branch}")

    def _join_branch_names(self, branches: list[str], locale: str) -> str:
        return Localization.format_list_and(
            locale, [self._branch_name(branch, locale) for branch in branches]
        )

    def _as_dominos_player(self, player: Player | None) -> DominosPlayer | None:
        return player if isinstance(player, DominosPlayer) else None

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _queue_bot_turn(self) -> None:
        current = self.current_player
        if current and current.is_bot:
            BotHelper.jolt_bot(current, ticks=random.randint(12, 24))

    def on_tick(self) -> None:
        super().on_tick()
        self.process_scheduled_sounds()
        if self.round_wait_ticks > 0:
            self.round_wait_ticks -= 1
            if self.round_wait_ticks == 0:
                self._start_round()
            return
        if self.status == "playing" and self.current_player and self.current_player.is_bot:
            BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        dom_player = self._as_dominos_player(player)
        if not dom_player or self.current_player != dom_player or self.status != "playing":
            return
        for tile in self._sorted_tiles(dom_player.hand):
            legal = self._legal_destinations(tile)
            if legal:
                return self._tile_action_id(tile)
        if self.options.draw_mode == "draw" and self.boneyard:
            return "draw"
        return "knock"

    def build_game_result(self) -> GameResult:
        sorted_teams = self.team_manager.get_sorted_teams(by_score=True, descending=True)
        final_scores = {}
        team_rankings = []
        for team in sorted_teams:
            name = self.team_manager.get_team_name(team)
            final_scores[name] = team.total_score
            team_rankings.append(
                {
                    "index": team.index,
                    "members": team.members,
                    "score": team.total_score,
                    "name": name,
                }
            )

        winner = sorted_teams[0] if sorted_teams else None
        winner_ids = []
        if winner:
            active_players = self.get_active_players()
            name_to_id = {player.name: player.id for player in active_players}
            winner_ids = [name_to_id[name] for name in winner.members if name in name_to_id]

        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot and not player.replaced_human,
                )
                for player in self.get_active_players()
            ],
            custom_data={
                "winner_name": self.team_manager.get_team_name(winner) if winner else None,
                "winner_ids": winner_ids,
                "winner_score": winner.total_score if winner else 0,
                "final_scores": final_scores,
                "team_rankings": team_rankings,
                "rounds_played": self.round,
                "target_score": self.options.target_score,
                "team_mode": self.options.team_mode,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        team_rankings = result.custom_data.get("team_rankings", [])
        for index, team in enumerate(team_rankings, 1):
            members = team.get("members", [])
            if len(members) == 1:
                name = members[0]
            else:
                name = Localization.get(locale, "game-team-name", index=team.get("index", 0) + 1)
            points_str = Localization.get(locale, "game-points", count=team.get("score", 0))
            lines.append(
                Localization.get(
                    locale,
                    "dominos-line-format",
                    rank=index,
                    player=name,
                    points=points_str,
                )
            )
        return lines
