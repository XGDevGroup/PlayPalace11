from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import random

from .base import Game, GameOptions, Player
from .registry import register_game
from ..game_utils.action_guard_mixin import ActionGuardMixin
from ..game_utils.actions import Action, ActionSet, MenuInput, Visibility
from ..game_utils.bot_helper import BotHelper
from ..game_utils.cards import Card, Deck, card_name
from ..game_utils.game_result import GameResult, PlayerResult
from ..messages.localization import Localization
from server.core.ui.keybinds import KeybindState


MODIFIER_RAISE_1 = "raise_1"
MODIFIER_RAISE_2 = "raise_2"
MODIFIER_RAISE_2_PLUS = "raise_2_plus"
MODIFIER_DRAW_2 = "draw_2"
MODIFIER_DRAW_3 = "draw_3"
MODIFIER_DRAW_4 = "draw_4"
MODIFIER_DRAW_5 = "draw_5"
MODIFIER_DRAW_6 = "draw_6"
MODIFIER_DRAW_7 = "draw_7"
MODIFIER_SCRAP = "scrap"
MODIFIER_RECYCLE = "recycle"
MODIFIER_SWAP_DRAW = "swap_draw"
MODIFIER_REDRAFT = "redraft"
MODIFIER_REDRAFT_PLUS = "redraft_plus"
MODIFIER_GUARD = "guard"
MODIFIER_GUARD_PLUS = "guard_plus"
MODIFIER_BREAK = "break_effect"
MODIFIER_BREAK_PLUS = "break_all"
MODIFIER_LOCKDOWN = "lockdown"
MODIFIER_PRECISION_DRAW = "precision_draw"
MODIFIER_PRECISION_DRAW_PLUS = "precision_draw_plus"
MODIFIER_PRIME_DRAW = "prime_draw"
MODIFIER_TARGET_17 = "target_17"
MODIFIER_TARGET_24 = "target_24"
MODIFIER_TARGET_27 = "target_27"
MODIFIER_SALVAGE = "salvage"
MODIFIER_AID_RIVAL = "aid_rival"

MODIFIER_POOL = (
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_DRAW_2,
    MODIFIER_DRAW_3,
    MODIFIER_DRAW_4,
    MODIFIER_DRAW_5,
    MODIFIER_DRAW_6,
    MODIFIER_DRAW_7,
    MODIFIER_SCRAP,
    MODIFIER_RECYCLE,
    MODIFIER_SWAP_DRAW,
    MODIFIER_REDRAFT,
    MODIFIER_REDRAFT_PLUS,
    MODIFIER_GUARD,
    MODIFIER_GUARD_PLUS,
    MODIFIER_BREAK,
    MODIFIER_BREAK_PLUS,
    MODIFIER_LOCKDOWN,
    MODIFIER_PRECISION_DRAW,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_PRIME_DRAW,
    MODIFIER_TARGET_17,
    MODIFIER_TARGET_24,
    MODIFIER_TARGET_27,
    MODIFIER_SALVAGE,
    MODIFIER_AID_RIVAL,
)

MODIFIER_LABELS = {
    MODIFIER_RAISE_1: "raise one",
    MODIFIER_RAISE_2: "raise two",
    MODIFIER_RAISE_2_PLUS: "withdraw and raise two",
    MODIFIER_DRAW_2: "draw 2",
    MODIFIER_DRAW_3: "draw 3",
    MODIFIER_DRAW_4: "draw 4",
    MODIFIER_DRAW_5: "draw 5",
    MODIFIER_DRAW_6: "draw 6",
    MODIFIER_DRAW_7: "draw 7",
    MODIFIER_SCRAP: "withdraw",
    MODIFIER_RECYCLE: "undraw",
    MODIFIER_SWAP_DRAW: "swap top cards",
    MODIFIER_REDRAFT: "change-up",
    MODIFIER_REDRAFT_PLUS: "change-up enhanced",
    MODIFIER_GUARD: "defend",
    MODIFIER_GUARD_PLUS: "defend enhanced",
    MODIFIER_BREAK: "delete",
    MODIFIER_BREAK_PLUS: "delete enhanced",
    MODIFIER_LOCKDOWN: "delete double enhanced",
    MODIFIER_PRECISION_DRAW: "best draw",
    MODIFIER_PRECISION_DRAW_PLUS: "best draw and raise five",
    MODIFIER_PRIME_DRAW: "best draw with change",
    MODIFIER_TARGET_17: "target 17",
    MODIFIER_TARGET_24: "target 24",
    MODIFIER_TARGET_27: "target 27",
    MODIFIER_SALVAGE: "embrace change",
    MODIFIER_AID_RIVAL: "trojan horse",
}
MODIFIER_HELP = [
    (MODIFIER_RAISE_1, "Raise one: increase opponent damage by 1 and gain 1 change card."),
    (MODIFIER_RAISE_2, "Raise two: increase opponent damage by 2 and gain 1 change card."),
    (
        MODIFIER_RAISE_2_PLUS,
        "Withdraw and raise two: increase opponent damage by 2, return opponent last drawn card to top of deck, and gain 1 change card.",
    ),
    (MODIFIER_DRAW_2, "Draw 2: draw a 2 from deck if available."),
    (MODIFIER_DRAW_3, "Draw 3: draw a 3 from deck if available."),
    (MODIFIER_DRAW_4, "Draw 4: draw a 4 from deck if available."),
    (MODIFIER_DRAW_5, "Draw 5: draw a 5 from deck if available."),
    (MODIFIER_DRAW_6, "Draw 6: draw a 6 from deck if available."),
    (MODIFIER_DRAW_7, "Draw 7: draw a 7 from deck if available."),
    (MODIFIER_SCRAP, "Withdraw: remove opponent last drawn card and place it on top of deck."),
    (MODIFIER_RECYCLE, "Undraw: return your last drawn card to top of deck."),
    (
        MODIFIER_SWAP_DRAW,
        "Swap top cards: exchange your last drawn card with your opponent's last drawn card.",
    ),
    (MODIFIER_REDRAFT, "Change-up: discard 2 change cards, then gain 3 change cards."),
    (MODIFIER_REDRAFT_PLUS, "Change-up enhanced: discard 1 change card, then gain 4 change cards."),
    (MODIFIER_GUARD, "Defend: reduce incoming damage by 1."),
    (MODIFIER_GUARD_PLUS, "Defend enhanced: reduce incoming damage by 2."),
    (MODIFIER_BREAK, "Delete: destroy opponent newest change card effect."),
    (MODIFIER_BREAK_PLUS, "Delete enhanced: destroy all opponent change card effects."),
    (
        MODIFIER_LOCKDOWN,
        "Delete double enhanced: clear opponent change card effects and lock opponent from playing change cards.",
    ),
    (MODIFIER_PRECISION_DRAW, "Best draw: draw the best available card for current target."),
    (
        MODIFIER_PRECISION_DRAW_PLUS,
        "Best draw and raise five: best draw plus increase opponent damage by 5.",
    ),
    (MODIFIER_PRIME_DRAW, "Best draw with change: best draw and gain 2 change cards."),
    (MODIFIER_TARGET_17, "Target 17: set round target to 17."),
    (MODIFIER_TARGET_24, "Target 24: set round target to 24."),
    (MODIFIER_TARGET_27, "Target 27: set round target to 27."),
    (
        MODIFIER_SALVAGE,
        "Embrace change: whenever any change card is played, gain 1 change card.",
    ),
    (MODIFIER_AID_RIVAL, "Trojan horse: opponent draws their best available card for current target."),
]
MODIFIER_HELP_MAP = {modifier_id: desc for modifier_id, desc in MODIFIER_HELP}

TABLE_EFFECT_MODIFIERS = {
    MODIFIER_RAISE_1,
    MODIFIER_RAISE_2,
    MODIFIER_RAISE_2_PLUS,
    MODIFIER_GUARD,
    MODIFIER_GUARD_PLUS,
    MODIFIER_LOCKDOWN,
    MODIFIER_PRECISION_DRAW_PLUS,
    MODIFIER_TARGET_17,
    MODIFIER_TARGET_24,
    MODIFIER_TARGET_27,
    MODIFIER_SALVAGE,
}

TARGET_VALUE_MODIFIERS = {
    MODIFIER_TARGET_17: 17,
    MODIFIER_TARGET_24: 24,
    MODIFIER_TARGET_27: 27,
}

TABLE_EFFECT_LIMIT = 5

SOUND_ROUND_START = "game_pig/roundstart.ogg"
SOUND_ROUND_DEAL = "game_cards/draw2.ogg"
SOUND_ROUND_RESOLVE = "game_cards/small_shuffle.ogg"
SOUND_TURN = "game_3cardpoker/turn.ogg"
SOUND_HIT = "game_cards/draw3.ogg"
SOUND_STAND = "game_blackjack/stand.ogg"
SOUND_OPPONENT_STAND = "game_pig/turn.ogg"
SOUND_CHANGE_MENU_OPEN = "menuclick.ogg"
SOUND_PLAY_CHANGE_CARD = "game_cards/play1.ogg"
SOUND_MOD_RAISE = "game_3cardpoker/bet.ogg"
SOUND_MOD_DEFEND = "game_blackjack/doubledown.ogg"
SOUND_MOD_DRAW = "game_cards/draw3.ogg"
SOUND_MOD_CONTROL = "game_cards/play3.ogg"
SOUND_TARGET_17 = "game_pig/roll.ogg"
SOUND_TARGET_24 = "game_cards/shuffle2.ogg"
SOUND_TARGET_27 = "game_cards/shuffle3.ogg"
SOUND_MOD_REFRESH = "game_cards/shuffle1.ogg"
SOUND_ROUND_WIN = "game_pig/win.ogg"
SOUND_ROUND_LOSE = "game_pig/lose.ogg"
SOUND_ROUND_DRAW = "game_crazyeights/draw.ogg"
SOUND_BUST = "game_blackjack/bust1.ogg"
SOUND_DAMAGE = "game_blackjack/bust2.ogg"
SOUND_ACTION_FAIL = "game_coup/challengefail.ogg"
SOUND_EFFECT_EXPIRE = "game_cards/discard2.ogg"
SOUND_CONTROL_SUCCESS = "game_cards/play2.ogg"
SOUND_GAIN_CHANGE_CARD = "game_cards/draw1.ogg"
SOUND_LOSE_CHANGE_CARD = "game_cards/discard1.ogg"
SOUND_BET_UP = "game_3cardpoker/winbet.ogg"
SOUND_BET_DOWN = "game_cards/discard3.ogg"
SOUND_NEAR_BUST = "game_crazyeights/fivesec.ogg"
SOUND_LOCKDOWN_APPLY = "game_crazyeights/discskip.ogg"
SOUND_LOCKDOWN_ACTIVE = "game_crazyeights/expired.ogg"
SOUND_LOCKDOWN_END = "game_crazyeights/pass.ogg"
SOUND_CLOSE_WIN = "game_blackjack/win1.ogg"
SOUND_CLOSE_LOSE = "game_uno/loseround.ogg"
SOUND_DOUBLE_BUST_DRAW = "game_blackjack/bust3.ogg"
SOUND_DAMAGE_HEAVY = "game_crazyeights/hitmark.ogg"
SOUND_GAME_WIN = "game_pig/wingame.ogg"
SOUND_GAME_NO_WIN = "game_crazyeights/pileempty.ogg"


@dataclass
class TwentyOneOptions(GameOptions):
    """Survival 21 defaults for Play Palace PvP."""

    starting_health: int = 10
    base_bet: int = 1
    starting_modifiers_per_round: int = 1
    draw_modifier_chance_percent: int = 35
    deck_count: int = 1
    next_round_wait_ticks: int = 30


@dataclass
class TwentyOnePlayer(Player):
    """Player state for Survival 21."""

    hand: list[Card] = field(default_factory=list)
    hp: int = 0
    modifiers: list[str] = field(default_factory=list)
    table_modifiers: list[str] = field(default_factory=list)
    stand_pending: bool = False
    last_drawn_card_id: int | None = None


@dataclass
@register_game
class TwentyOneGame(ActionGuardMixin, Game):
    """Survival 21 ruleset with tactical modifier cards."""

    players: list[TwentyOnePlayer] = field(default_factory=list)
    options: TwentyOneOptions = field(default_factory=TwentyOneOptions)
    deck: Deck | None = None
    phase: str = "lobby"  # lobby, turns, between_rounds, finished
    round_number: int = 0
    round_starter_index: int = 0
    next_round_wait_ticks: int = 0
    modifier_used_since_last_stand_resolution: bool = False

    @classmethod
    def get_name(cls) -> str:
        return "21 (Survival Rules)"

    @classmethod
    def get_name_key(cls) -> str:
        return "21"

    @classmethod
    def get_type(cls) -> str:
        return "twentyone"

    @classmethod
    def get_category(cls) -> str:
        return "category-card-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 2

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> TwentyOnePlayer:
        return TwentyOnePlayer(id=player_id, name=name, is_bot=is_bot)

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        error = self.guard_turn_action_enabled(player)
        if error:
            return error
        if self.phase != "turns":
            return "action-not-available"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        return self.turn_action_visibility(player, extra_condition=self.phase == "turns")

    def _is_play_modifier_enabled(self, player: Player) -> str | None:
        error = self._is_turn_action_enabled(player)
        if error:
            return error
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return "action-not-available"
        if self._modifiers_locked_for(p):
            return "action-not-available"
        if not self._playable_modifiers(p):
            return "action-not-available"
        return None

    def _is_play_modifier_hidden(self, player: Player) -> Visibility:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p or not self._playable_modifiers(p):
            return Visibility.HIDDEN
        if self._modifiers_locked_for(p):
            return Visibility.HIDDEN
        return self._is_turn_action_hidden(player)

    def _is_check_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if player.is_spectator:
            return "action-spectator"
        return None

    def _is_check_hidden(self, player: Player) -> Visibility:
        if self.status != "playing" or player.is_spectator:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def create_turn_action_set(self, player: TwentyOnePlayer) -> ActionSet:
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="hit",
                label=Localization.get(locale, "blackjack-hit"),
                handler="_action_hit",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="stand",
                label=Localization.get(locale, "blackjack-stand"),
                handler="_action_stand",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="play_modifier",
                label="Play Change Card",
                handler="_action_play_modifier",
                is_enabled="_is_play_modifier_enabled",
                is_hidden="_is_play_modifier_hidden",
                input_request=MenuInput(
                    prompt="twentyone-select-change-card",
                    options="_options_for_play_modifier",
                    bot_select="_bot_select_play_modifier",
                ),
            )
        )
        return action_set

    def create_standard_action_set(self, player: Player) -> ActionSet:
        action_set = super().create_standard_action_set(player)
        action_set.add(
            Action(
                id="check_21_status",
                label="Check 21 status",
                handler="_action_check_status",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="modifier_guide",
                label="Change Card Guide",
                handler="_action_modifier_guide",
                is_enabled="_is_check_enabled",
                is_hidden="_is_check_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_opponent_face_up",
                label="Read opponent face-up cards",
                handler="_action_read_opponent_face_up",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_hand",
                label="Read current hand",
                handler="_action_read_current_hand",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_bets",
                label="Read current bets",
                handler="_action_read_current_bets",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        action_set.add(
            Action(
                id="read_21_active_effects",
                label="Read active change-card effects",
                handler="_action_read_active_effects",
                is_enabled="_is_check_enabled",
                is_hidden="_is_always_hidden",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("1", "Hit", ["hit"], state=KeybindState.ACTIVE)
        self.define_keybind("2", "Stand", ["stand"], state=KeybindState.ACTIVE)
        self.define_keybind("3", "Play Change Card", ["play_modifier"], state=KeybindState.ACTIVE)
        self.define_keybind("4", "Check 21 status", ["check_21_status"], state=KeybindState.ACTIVE)
        self.define_keybind("m", "Change Card Guide", ["modifier_guide"], state=KeybindState.ACTIVE)
        self.define_keybind("o", "Read opponent face-up cards", ["read_21_opponent_face_up"], state=KeybindState.ACTIVE)
        self.define_keybind("r", "Read current hand", ["read_21_hand"], state=KeybindState.ACTIVE)
        self.define_keybind("b", "Read current bets", ["read_21_bets"], state=KeybindState.ACTIVE)
        self.define_keybind("e", "Read active effects", ["read_21_active_effects"], state=KeybindState.ACTIVE)

    def _options_for_play_modifier(self, player: Player) -> list[str]:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return []
        options: list[str] = []
        for display_index, modifier in enumerate(p.modifiers, start=1):
            label = MODIFIER_LABELS.get(modifier, modifier)
            description = MODIFIER_HELP_MAP.get(modifier, "")
            if description:
                options.append(f"{display_index}:{label} - {description}")
            else:
                options.append(f"{display_index}:{label}")
        return options

    def _bot_select_play_modifier(self, player: Player, options: list[str]) -> str | None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return None
        modifier = self._bot_choose_modifier_to_play(p)
        if not modifier:
            return None
        return self._option_for_modifier(options, modifier)

    @staticmethod
    def _option_for_modifier(options: list[str], modifier: str) -> str | None:
        label = MODIFIER_LABELS.get(modifier, modifier)
        for option in options:
            body = option.split(":", 1)[1] if ":" in option else option
            if body == label or body.startswith(f"{label} -"):
                return option
        return None

    @staticmethod
    def _parse_modifier_option(option_value: str) -> int | None:
        try:
            prefix = option_value.split(":", 1)[0]
            return int(prefix)
        except (ValueError, IndexError):
            return None

    def _request_action_input(self, action: Action, player: Player) -> None:
        super()._request_action_input(action, player)
        if action.id != "play_modifier":
            return
        if self._pending_actions.get(player.id) != action.id:
            return
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        self._play_sound_for_player(p, SOUND_CHANGE_MENU_OPEN, volume=65)

    def _action_hit(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        card = self._draw_card()
        if not card:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            self.broadcast("Deck is empty. You can still choose to stay.")
            self.rebuild_all_menus()
            return

        self.play_sound(SOUND_HIT, volume=80)
        self._clear_pending_stands()
        self._add_card_to_hand(
            p,
            card,
            announce_source=f"{p.name} draws",
            reveal_to_others=True,
        )
        p.stand_pending = False

        chance = max(0, min(100, self.options.draw_modifier_chance_percent))
        if random.randint(1, 100) <= chance:  # nosec B311
            self._give_random_modifiers(p, 1, announce=True)

        self.rebuild_all_menus()

    def _action_stand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        self._play_sound_for_player(p, SOUND_STAND)
        self._play_opponent_stand_sound(p)
        p.stand_pending = True
        self.broadcast(f"{p.name} chooses to stay.")

        if self._both_players_standing():
            self.play_sound(SOUND_ROUND_RESOLVE, volume=65)
            self._settle_round()
            return

        self._advance_turn_after_action()

    def _action_play_modifier(self, player: Player, selected: str, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return

        choice_number = self._parse_modifier_option(selected)
        if choice_number is None:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            return

        choice_index = choice_number - 1
        if choice_index < 0 or choice_index >= len(p.modifiers):
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            return

        modifier = p.modifiers.pop(choice_index)
        if not self._is_single_modifier_playable(p, modifier):
            p.modifiers.insert(choice_index, modifier)
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            return

        opponent = self._opponent_of(p)
        my_bet_before = self._current_bet(p)
        opp_bet_before = self._current_bet(opponent) if opponent else my_bet_before
        self._play_modifier_sound(modifier)
        self._clear_pending_stands()
        self.broadcast(f"{p.name} plays {MODIFIER_LABELS.get(modifier, modifier)}.")
        self._resolve_modifier(p, modifier)
        self.modifier_used_since_last_stand_resolution = True
        self._trigger_harvest_rewards()
        if opponent:
            self._play_bet_change_sounds(p, opponent, my_bet_before, opp_bet_before)
        self.rebuild_all_menus()

    def _action_check_status(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        target = self._current_target()
        bet = self._current_bet(p)
        hand_text = ", ".join(str(card.rank) for card in p.hand) if p.hand else "none"
        modifiers_text = ", ".join(MODIFIER_LABELS.get(t, t) for t in p.modifiers) if p.modifiers else "none"
        table_text = ", ".join(MODIFIER_LABELS.get(t, t) for t in p.table_modifiers) if p.table_modifiers else "none"
        user.speak(
            f"Target {target}. HP {p.hp}. Bet {bet}. Hand [{hand_text}] total {self._hand_total(p)}. "
            f"Change cards in hand: {modifiers_text}. Table effects: {table_text}.",
            "table",
        )
        user.speak("Press M for the full change card guide.", "table")
        opponent = self._opponent_of(p)
        if opponent:
            shown_cards = self._opponent_visible_cards(opponent)
            shown_text = ", ".join(str(card.rank) for card in shown_cards) if shown_cards else "none"
            shown_total = sum(card.rank for card in shown_cards)
            user.speak(
                f"{opponent.name}: HP {opponent.hp}, bet {self._current_bet(opponent)}, "
                f"shown cards [{shown_text}] shown total {shown_total}, hole card hidden.",
                "table",
            )

    def _action_modifier_guide(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        user.speak("Change Card guide.", "table")
        for modifier_id, description in MODIFIER_HELP:
            name = MODIFIER_LABELS.get(modifier_id, modifier_id)
            user.speak(f"{name}: {description}", "table")
        user.speak(
            "Table effect limit is five. Target change cards replace older target change cards.",
            "table",
        )

    def _action_read_opponent_face_up(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return
        opponent = self._opponent_of(p)
        if not opponent:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            user.speak("No opponent available.", "table")
            return

        shown_cards = self._opponent_visible_cards(opponent)
        shown_text = ", ".join(str(card.rank) for card in shown_cards) if shown_cards else "none"
        shown_total = sum(card.rank for card in shown_cards)
        user.speak(
            f"{opponent.name} face-up cards [{shown_text}] total {shown_total}. "
            "Hole card is hidden.",
            "table",
        )

    def _action_read_current_hand(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        hand_text = ", ".join(str(card.rank) for card in p.hand) if p.hand else "none"
        user.speak(f"Your hand [{hand_text}] total {self._hand_total(p)}.", "table")

    def _action_read_current_bets(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        my_bet = self._current_bet(p)
        opponent = self._opponent_of(p)
        if not opponent:
            self._play_sound_for_player(p, SOUND_ACTION_FAIL)
            user.speak(f"Current bet {my_bet}.", "table")
            return
        opponent_bet = self._current_bet(opponent)
        user.speak(
            f"Current bets. {p.name}: {my_bet}. {opponent.name}: {opponent_bet}.",
            "table",
        )

    def _action_read_active_effects(self, player: Player, action_id: str) -> None:
        p = player if isinstance(player, TwentyOnePlayer) else None
        if not p:
            return
        user = self.get_user(p)
        if not user:
            return

        my_effects = ", ".join(MODIFIER_LABELS.get(effect, effect) for effect in p.table_modifiers) if p.table_modifiers else "none"
        opponent = self._opponent_of(p)
        if not opponent:
            user.speak(f"Active effects. {p.name}: {my_effects}.", "table")
            return

        opponent_effects = ", ".join(
            MODIFIER_LABELS.get(effect, effect) for effect in opponent.table_modifiers
        ) if opponent.table_modifiers else "none"
        user.speak(
            f"Active effects. {p.name}: {my_effects}. {opponent.name}: {opponent_effects}.",
            "table",
        )

    def on_start(self) -> None:
        self.status = "playing"
        self.game_active = True
        self.phase = "turns"
        self.round_number = 0
        self.round_starter_index = 0
        self.next_round_wait_ticks = 0
        self.modifier_used_since_last_stand_resolution = False

        active = self.get_active_players()
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active])
        self._team_manager.reset_all_scores()

        for player in active:
            if not isinstance(player, TwentyOnePlayer):
                continue
            player.hp = max(1, self.options.starting_health)
            player.hand.clear()
            player.modifiers.clear()
            player.table_modifiers.clear()
            player.stand_pending = False
            player.last_drawn_card_id = None

        self._sync_hp_scores()
        self._start_round(rotate_starter=False)

    def on_tick(self) -> None:
        super().on_tick()
        if not self.game_active or self.status != "playing":
            return

        if self.phase == "between_rounds":
            if self.next_round_wait_ticks > 0:
                self.next_round_wait_ticks -= 1
            if self.next_round_wait_ticks <= 0:
                self._start_round(rotate_starter=True)
            return

        if self.phase == "turns":
            BotHelper.on_tick(self)

    def _start_round(self, *, rotate_starter: bool) -> None:
        alive = self._alive_players()
        if len(alive) <= 1:
            self._end_game(alive[0] if alive else None)
            return

        if rotate_starter:
            self.round_starter_index = (self.round_starter_index + 1) % len(alive)
        if self.round_starter_index >= len(alive):
            self.round_starter_index = 0

        self.phase = "turns"
        self.round_number += 1
        self.modifier_used_since_last_stand_resolution = False
        self.play_sound(SOUND_ROUND_START, volume=70)

        self._build_round_deck()

        for player in alive:
            player.hand.clear()
            player.table_modifiers.clear()
            player.stand_pending = False
            player.last_drawn_card_id = None
            self._give_random_modifiers(player, self.options.starting_modifiers_per_round, announce=False)

        for deal_round in range(2):
            for player in alive:
                card = self._draw_card()
                if card:
                    reveal = deal_round > 0
                    self._add_card_to_hand(player, card, announce_source=None, reveal_to_others=reveal)
        self.play_sound(SOUND_ROUND_DEAL, volume=60)

        self.set_turn_players(alive, reset_index=True)
        self.turn_index = self.round_starter_index

        self.broadcast(f"Round {self.round_number} begins. Target is {self._current_target()}.")
        for player in alive:
            shown = self._peek_last_drawn_card(player)
            if shown:
                self.broadcast(f"{player.name} shows {card_name(shown, 'en')} ({shown.rank}).")
            else:
                self.broadcast(f"{player.name} receives cards.")
            user = self.get_user(player)
            if user:
                if player.hand:
                    user.speak(f"Your hidden card is {card_name(player.hand[0], user.locale)} ({player.hand[0].rank}).", "table")
                if shown:
                    user.speak(f"Your shown card is {card_name(shown, user.locale)} ({shown.rank}).", "table")
                user.speak(f"Your total is {self._hand_total(player)}.", "table")
                modifiers_text = ", ".join(MODIFIER_LABELS.get(t, t) for t in player.modifiers) if player.modifiers else "none"
                user.speak(f"Your change cards: {modifiers_text}.", "table")

        current = self.current_player
        if current:
            self.announce_turn(turn_sound=SOUND_TURN)
            self._play_target_reminder_sound(current)
            if self._modifiers_locked_for(current):
                self._play_sound_for_player(current, SOUND_LOCKDOWN_ACTIVE, volume=65)
            if current.is_bot:
                BotHelper.jolt_bot(current, ticks=random.randint(8, 16))  # nosec B311
        self.rebuild_all_menus()

    def _advance_turn_after_action(self) -> None:
        if self.phase != "turns":
            return
        self.advance_turn(announce=False)
        current = self.current_player
        if current:
            self.announce_turn(turn_sound=SOUND_TURN)
            self._play_target_reminder_sound(current)
            if self._modifiers_locked_for(current):
                self._play_sound_for_player(current, SOUND_LOCKDOWN_ACTIVE, volume=65)
            if current.is_bot:
                BotHelper.jolt_bot(current, ticks=random.randint(8, 16))  # nosec B311
        self.rebuild_all_menus()

    def _settle_round(self) -> None:
        players = self._alive_players()
        if len(players) < 2:
            self._end_game(players[0] if players else None)
            return

        self.phase = "between_rounds"
        p1, p2 = players[0], players[1]
        target = self._current_target()
        total_1 = self._hand_total(p1)
        total_2 = self._hand_total(p2)
        bust_1 = total_1 > target
        bust_2 = total_2 > target

        self.broadcast(
            f"Round totals (target {target}): {p1.name} {total_1}, {p2.name} {total_2}."
        )

        outcome = self._resolve_round_outcome(total_1, total_2, target)

        if outcome == "p1_wins":
            self._apply_round_loss_damage(p2)
            self.broadcast(f"{p1.name} wins the round.")
        elif outcome == "p2_wins":
            self._apply_round_loss_damage(p1)
            self.broadcast(f"{p2.name} wins the round.")
        else:
            self._apply_round_loss_damage(p1)
            self._apply_round_loss_damage(p2)
            self.broadcast("Round is a draw. Both players take damage.")
        self._play_round_outcome_sounds(outcome, p1, p2, total_1, total_2, bust_1, bust_2)

        if bust_1 and bust_2:
            self.broadcast("Both players busted; closer to target decides the winner.")
            self._play_sound_for_player(p1, SOUND_BUST)
            self._play_sound_for_player(p2, SOUND_BUST)
        elif bust_1:
            self.broadcast(f"{p1.name} busted.")
            self._play_sound_for_player(p1, SOUND_BUST)
        elif bust_2:
            self.broadcast(f"{p2.name} busted.")
            self._play_sound_for_player(p2, SOUND_BUST)

        self._sync_hp_scores()
        survivors = self._alive_players()
        if len(survivors) <= 1:
            self._end_game(survivors[0] if survivors else None)
            return

        self.next_round_wait_ticks = max(0, self.options.next_round_wait_ticks)
        self.rebuild_all_menus()

    @staticmethod
    def _resolve_round_outcome(total_1: int, total_2: int, target: int) -> str:
        bust_1 = total_1 > target
        bust_2 = total_2 > target
        if bust_1 and not bust_2:
            return "p2_wins"
        if bust_2 and not bust_1:
            return "p1_wins"
        if bust_1 and bust_2:
            diff_1 = abs(total_1 - target)
            diff_2 = abs(total_2 - target)
            if diff_1 < diff_2:
                return "p1_wins"
            if diff_2 < diff_1:
                return "p2_wins"
            return "draw"
        if total_1 > total_2:
            return "p1_wins"
        if total_2 > total_1:
            return "p2_wins"
        return "draw"

    def _apply_round_loss_damage(self, loser: TwentyOnePlayer) -> None:
        damage = max(0, self._current_bet(loser))
        if damage <= 0:
            self.broadcast(f"{loser.name} loses the round but bet is 0.")
            return
        loser.hp = max(0, loser.hp - damage)
        if damage >= 5:
            self._play_sound_for_player(loser, SOUND_DAMAGE_HEAVY)
        else:
            self._play_sound_for_player(loser, SOUND_DAMAGE)
        self.broadcast(f"{loser.name} takes {damage} damage and now has {loser.hp} HP.")

    def _end_game(self, winner: TwentyOnePlayer | None) -> None:
        self.phase = "finished"
        if winner:
            self._play_sound_for_player(winner, SOUND_GAME_WIN, volume=80)
            self.broadcast(f"{winner.name} wins 21 with {winner.hp} HP remaining.")
        else:
            self.play_sound(SOUND_GAME_NO_WIN, volume=75)
            self.broadcast("21 ends with no winner.")
        self.finish_game()

    def _play_round_outcome_sounds(
        self,
        outcome: str,
        p1: TwentyOnePlayer,
        p2: TwentyOnePlayer,
        total_1: int,
        total_2: int,
        bust_1: bool,
        bust_2: bool,
    ) -> None:
        if outcome == "draw" and bust_1 and bust_2:
            self._play_sound_for_player(p1, SOUND_DOUBLE_BUST_DRAW)
            self._play_sound_for_player(p2, SOUND_DOUBLE_BUST_DRAW)
            return

        close_margin = abs(total_1 - total_2) <= 1 and not (bust_1 or bust_2)
        if outcome == "p1_wins":
            self._play_sound_for_player(p1, SOUND_CLOSE_WIN if close_margin else SOUND_ROUND_WIN)
            self._play_sound_for_player(p2, SOUND_CLOSE_LOSE if close_margin else SOUND_ROUND_LOSE)
            return
        if outcome == "p2_wins":
            self._play_sound_for_player(p2, SOUND_CLOSE_WIN if close_margin else SOUND_ROUND_WIN)
            self._play_sound_for_player(p1, SOUND_CLOSE_LOSE if close_margin else SOUND_ROUND_LOSE)
            return
        self._play_sound_for_player(p1, SOUND_ROUND_DRAW)
        self._play_sound_for_player(p2, SOUND_ROUND_DRAW)

    def _play_sound_for_player(self, player: TwentyOnePlayer, sound_name: str, *, volume: int = 100) -> None:
        user = self.get_user(player)
        if user:
            user.play_sound(sound_name, volume=volume)

    def _play_opponent_stand_sound(self, player: TwentyOnePlayer) -> None:
        for other in self._alive_players():
            if other.id != player.id:
                self._play_sound_for_player(other, SOUND_OPPONENT_STAND, volume=70)

    def _play_modifier_sound(self, modifier: str) -> None:
        if modifier in (MODIFIER_RAISE_1, MODIFIER_RAISE_2, MODIFIER_RAISE_2_PLUS):
            self.play_sound(SOUND_MOD_RAISE, volume=75)
            return
        if modifier in (MODIFIER_GUARD, MODIFIER_GUARD_PLUS):
            self.play_sound(SOUND_MOD_DEFEND, volume=75)
            return
        if modifier in (
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
            MODIFIER_PRECISION_DRAW,
            MODIFIER_PRECISION_DRAW_PLUS,
            MODIFIER_PRIME_DRAW,
        ):
            self.play_sound(SOUND_MOD_DRAW, volume=75)
            return
        if modifier in TARGET_VALUE_MODIFIERS:
            self._play_target_change_sound(modifier)
            return
        if modifier in (MODIFIER_REDRAFT, MODIFIER_REDRAFT_PLUS):
            self.play_sound(SOUND_MOD_REFRESH, volume=75)
            return
        if modifier in (
            MODIFIER_SCRAP,
            MODIFIER_RECYCLE,
            MODIFIER_SWAP_DRAW,
            MODIFIER_BREAK,
            MODIFIER_BREAK_PLUS,
            MODIFIER_LOCKDOWN,
            MODIFIER_AID_RIVAL,
        ):
            self.play_sound(SOUND_MOD_CONTROL, volume=75)
            return
        self.play_sound(SOUND_PLAY_CHANGE_CARD, volume=75)

    def _play_target_change_sound(self, modifier: str) -> None:
        if modifier == MODIFIER_TARGET_17:
            self.play_sound(SOUND_TARGET_17, volume=75)
            return
        if modifier == MODIFIER_TARGET_24:
            self.play_sound(SOUND_TARGET_24, volume=75)
            return
        if modifier == MODIFIER_TARGET_27:
            self.play_sound(SOUND_TARGET_27, volume=75)
            return
        self.play_sound(SOUND_TARGET_17, volume=75)

    def _play_target_reminder_sound(self, player: TwentyOnePlayer) -> None:
        target = self._current_target()
        if target == 21:
            return
        if target == 17:
            self._play_sound_for_player(player, SOUND_TARGET_17, volume=60)
            return
        if target == 24:
            self._play_sound_for_player(player, SOUND_TARGET_24, volume=60)
            return
        if target == 27:
            self._play_sound_for_player(player, SOUND_TARGET_27, volume=60)

    def _play_bet_change_sounds(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        my_bet_before: int,
        opp_bet_before: int,
    ) -> None:
        my_bet_after = self._current_bet(player)
        opp_bet_after = self._current_bet(opponent)

        if my_bet_after > my_bet_before:
            self._play_sound_for_player(player, SOUND_BET_UP, volume=70)
        elif my_bet_after < my_bet_before:
            self._play_sound_for_player(player, SOUND_BET_DOWN, volume=70)

        if opp_bet_after > opp_bet_before:
            self._play_sound_for_player(opponent, SOUND_BET_UP, volume=70)
        elif opp_bet_after < opp_bet_before:
            self._play_sound_for_player(opponent, SOUND_BET_DOWN, volume=70)

    def _play_near_bust_sounds(self, player: TwentyOnePlayer) -> None:
        total = self._hand_total(player)
        target = self._current_target()
        if total < target - 1 or total > target:
            return

        self._play_sound_for_player(player, SOUND_NEAR_BUST, volume=65)
        opponent = self._opponent_of(player)
        if opponent:
            self._play_sound_for_player(opponent, SOUND_NEAR_BUST, volume=55)

    def bot_think(self, player: TwentyOnePlayer) -> str | None:
        if self.phase != "turns" or self.current_player != player:
            return None

        opponent = self._opponent_of(player)
        if not opponent:
            return "stand"

        target = self._current_target()
        total = self._hand_total(player)
        estimated_opp_total = self._bot_estimate_opponent_total(player, opponent)

        if not self._modifiers_locked_for(player) and player.modifiers:
            if self._bot_choose_modifier_to_play(player):
                return "play_modifier"

        return self._bot_choose_hit_or_stand(opponent, total, estimated_opp_total, target)

    @staticmethod
    def _bot_choose_hit_or_stand(
        opponent: TwentyOnePlayer,
        total: int,
        opp_total: float,
        target: int,
    ) -> str:
        if total < target - 2:
            return "hit"
        if opponent.stand_pending and total < opp_total and total <= target:
            return "hit"
        return "stand"

    def _bot_choose_modifier_to_play(self, player: TwentyOnePlayer) -> str | None:
        playable = self._playable_modifiers(player)
        if not playable:
            return None

        opponent = self._opponent_of(player)
        if not opponent:
            return playable[0]

        target = self._current_target()
        total = self._hand_total(player)
        estimated_opp_total = self._bot_estimate_opponent_total(player, opponent)
        likely_losing = self._bot_is_likely_losing(player, opponent, total, estimated_opp_total, target)
        confident_winning = self._bot_is_confident_winning(player, opponent, total, estimated_opp_total, target)
        needs_new_cards = self._bot_needs_new_change_cards(player, playable, likely_losing, confident_winning)

        best_modifier: str | None = None
        best_score = 0.0
        for modifier in playable:
            score = self._bot_modifier_score(
                player,
                opponent,
                modifier,
                total,
                target,
                likely_losing=likely_losing,
                confident_winning=confident_winning,
                needs_new_cards=needs_new_cards,
            )
            if score > best_score:
                best_score = score
                best_modifier = modifier
        return best_modifier

    def _bot_estimate_opponent_total(self, player: TwentyOnePlayer, opponent: TwentyOnePlayer) -> float:
        visible_cards = self._opponent_visible_cards(opponent)
        visible_total = float(sum(card.rank for card in visible_cards))
        if not opponent.hand:
            return visible_total
        return visible_total + self._bot_expected_hidden_rank(player, opponent)

    def _bot_expected_hidden_rank(self, player: TwentyOnePlayer, opponent: TwentyOnePlayer) -> float:
        counts = {rank: max(0, self.options.deck_count) for rank in range(1, 12)}
        for card in player.hand:
            if counts.get(card.rank, 0) > 0:
                counts[card.rank] -= 1
        for card in self._opponent_visible_cards(opponent):
            if counts.get(card.rank, 0) > 0:
                counts[card.rank] -= 1

        remaining = sum(counts.values())
        if remaining <= 0:
            return 6.0
        weighted = sum(rank * count for rank, count in counts.items())
        return weighted / remaining

    def _bot_is_likely_losing(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        total: int,
        estimated_opp_total: float,
        target: int,
    ) -> bool:
        if total > target:
            return True
        if opponent.stand_pending and estimated_opp_total > total:
            return True
        if total + 1.0 < estimated_opp_total:
            return True
        return player.hp <= opponent.hp and total < target - 3

    @staticmethod
    def _bot_is_confident_winning(
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        total: int,
        estimated_opp_total: float,
        target: int,
    ) -> bool:
        if total > target:
            return False
        if opponent.stand_pending:
            return total >= estimated_opp_total
        if total >= target - 1 and total >= estimated_opp_total + 1:
            return True
        return player.hp > opponent.hp and total >= estimated_opp_total + 2

    def _bot_needs_new_change_cards(
        self,
        player: TwentyOnePlayer,
        playable: list[str],
        likely_losing: bool,
        confident_winning: bool,
    ) -> bool:
        non_redraft = [m for m in playable if m not in (MODIFIER_REDRAFT, MODIFIER_REDRAFT_PLUS)]
        if not non_redraft:
            return True
        if len(non_redraft) == 1 and likely_losing:
            return True
        if likely_losing and not any(
            self._bot_has_immediate_round_impact(player, m, confident_winning=confident_winning)
            for m in non_redraft
        ):
            return True
        return False

    def _bot_has_immediate_round_impact(
        self,
        player: TwentyOnePlayer,
        modifier: str,
        *,
        confident_winning: bool,
    ) -> bool:
        if modifier in (
            MODIFIER_PRECISION_DRAW,
            MODIFIER_PRECISION_DRAW_PLUS,
            MODIFIER_PRIME_DRAW,
            MODIFIER_DRAW_2,
            MODIFIER_DRAW_3,
            MODIFIER_DRAW_4,
            MODIFIER_DRAW_5,
            MODIFIER_DRAW_6,
            MODIFIER_DRAW_7,
            MODIFIER_GUARD,
            MODIFIER_GUARD_PLUS,
            MODIFIER_TARGET_24,
            MODIFIER_TARGET_27,
            MODIFIER_BREAK,
            MODIFIER_BREAK_PLUS,
            MODIFIER_SWAP_DRAW,
            MODIFIER_SCRAP,
            MODIFIER_RECYCLE,
        ):
            return True
        if modifier in (MODIFIER_RAISE_1, MODIFIER_RAISE_2, MODIFIER_RAISE_2_PLUS):
            return confident_winning
        return False

    def _bot_modifier_score(
        self,
        player: TwentyOnePlayer,
        opponent: TwentyOnePlayer,
        modifier: str,
        total: int,
        target: int,
        *,
        likely_losing: bool,
        confident_winning: bool,
        needs_new_cards: bool,
    ) -> float:
        gap = target - total
        opponent_last = self._peek_last_drawn_card(opponent)
        own_last = self._peek_last_drawn_card(player)

        if modifier == MODIFIER_REDRAFT:
            return 7.0 if needs_new_cards else -8.0
        if modifier == MODIFIER_REDRAFT_PLUS:
            return 8.0 if needs_new_cards else -8.0

        if modifier == MODIFIER_GUARD:
            return 9.0 if likely_losing else -3.0
        if modifier == MODIFIER_GUARD_PLUS:
            return 10.0 if likely_losing else -3.0

        if modifier == MODIFIER_RAISE_1:
            return 6.0 if confident_winning else -4.0
        if modifier == MODIFIER_RAISE_2:
            return 7.0 if confident_winning else -4.0
        if modifier == MODIFIER_RAISE_2_PLUS:
            return 8.0 if confident_winning else -4.0

        if modifier == MODIFIER_PRECISION_DRAW:
            return 8.0 if gap > 0 else -4.0
        if modifier == MODIFIER_PRECISION_DRAW_PLUS:
            if gap > 0:
                return 8.5
            return 6.0 if confident_winning else -3.0
        if modifier == MODIFIER_PRIME_DRAW:
            return 7.5 if gap > 0 else -4.0

        if modifier in (MODIFIER_DRAW_2, MODIFIER_DRAW_3, MODIFIER_DRAW_4, MODIFIER_DRAW_5, MODIFIER_DRAW_6, MODIFIER_DRAW_7):
            rank = int(modifier.split("_")[1])
            if gap <= 0:
                return -6.0
            if rank > gap:
                return -5.0
            closeness = 1.0 if rank == gap else 0.0
            return 6.0 + closeness

        if modifier == MODIFIER_TARGET_24:
            return 9.0 if total > target else -5.0
        if modifier == MODIFIER_TARGET_27:
            return 9.5 if total > target + 2 else -6.0
        if modifier == MODIFIER_TARGET_17:
            return 3.0 if confident_winning and total >= 17 else -6.0

        if modifier == MODIFIER_SCRAP:
            if opponent_last and likely_losing:
                return 6.0 + (opponent_last.rank / 20.0)
            return -2.0
        if modifier == MODIFIER_RECYCLE:
            if own_last and total > target:
                return 8.0
            return -3.0
        if modifier == MODIFIER_SWAP_DRAW:
            if own_last and opponent_last and opponent_last.rank > own_last.rank and likely_losing:
                return 7.0
            return -3.0

        if modifier == MODIFIER_BREAK:
            return 6.5 if likely_losing and opponent.table_modifiers else -2.0
        if modifier == MODIFIER_BREAK_PLUS:
            return 7.0 if likely_losing and opponent.table_modifiers else -2.0
        if modifier == MODIFIER_LOCKDOWN:
            if likely_losing and opponent.modifiers:
                return 7.5
            return 4.0 if confident_winning and opponent.modifiers else -2.0

        if modifier == MODIFIER_SALVAGE:
            return 2.0 if likely_losing else -2.0
        if modifier == MODIFIER_AID_RIVAL:
            return -20.0
        return -1.0

    def _resolve_modifier(self, player: TwentyOnePlayer, modifier: str) -> None:
        opponent = self._opponent_of(player)
        if not opponent:
            return

        if modifier == MODIFIER_RAISE_1:
            self._place_table_effect(player, modifier)
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier == MODIFIER_RAISE_2:
            self._place_table_effect(player, modifier)
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier == MODIFIER_RAISE_2_PLUS:
            self._place_table_effect(player, modifier)
            removed = self._extract_last_drawn_card(opponent)
            if removed:
                self._return_card_to_top_of_deck(removed)
                self.broadcast(f"{opponent.name}'s last face-up card is returned to top of deck.")
            self._give_random_modifiers(player, 1, announce=True)
            return

        if modifier in (MODIFIER_DRAW_2, MODIFIER_DRAW_3, MODIFIER_DRAW_4, MODIFIER_DRAW_5, MODIFIER_DRAW_6, MODIFIER_DRAW_7):
            rank = int(modifier.split("_")[1])
            card = self._draw_specific_rank(rank)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announce_source=f"{player.name} draws exact",
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast(f"No {rank} card available.")
            return

        if modifier == MODIFIER_SCRAP:
            removed = self._extract_last_drawn_card(opponent)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                self._return_card_to_top_of_deck(removed)
                self.broadcast(f"{opponent.name}'s last face-up card is returned to top of deck.")
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("No face-up card to remove.")
            return

        if modifier == MODIFIER_RECYCLE:
            removed = self._extract_last_drawn_card(player)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                self._return_card_to_top_of_deck(removed)
                self.broadcast(f"{player.name}'s last face-up card returns to top of deck.")
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("No face-up card to return.")
            return

        if modifier == MODIFIER_SWAP_DRAW:
            player_recent = self._peek_last_drawn_card(player)
            opponent_recent = self._peek_last_drawn_card(opponent)
            if not player_recent or not opponent_recent:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("Both players need a face-up card to exchange.")
                return

            first = self._extract_last_drawn_card(player)
            second = self._extract_last_drawn_card(opponent)
            if not first or not second:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("Exchange failed.")
                return

            player.hand.append(second)
            player.last_drawn_card_id = second.id
            opponent.hand.append(first)
            opponent.last_drawn_card_id = first.id
            player.stand_pending = False
            opponent.stand_pending = False
            self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
            self.broadcast("Exchange resolves: both players swap their most recent face-up cards.")
            return

        if modifier == MODIFIER_REDRAFT:
            self._discard_random_modifiers(player, 2, announce_sound=True)
            self._give_random_modifiers(player, 3, announce=True)
            return

        if modifier == MODIFIER_REDRAFT_PLUS:
            self._discard_random_modifiers(player, 1, announce_sound=True)
            self._give_random_modifiers(player, 4, announce=True)
            return

        if modifier in TABLE_EFFECT_MODIFIERS:
            self._place_table_effect(player, modifier)
            if modifier in TARGET_VALUE_MODIFIERS:
                self.broadcast(f"Target changes to {self._current_target()}.")
            return

        if modifier == MODIFIER_BREAK:
            removed = self._pop_last_table_effect(opponent)
            if removed:
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                if removed == MODIFIER_LOCKDOWN:
                    self.play_sound(SOUND_LOCKDOWN_END, volume=70)
                self.broadcast(f"{player.name} destroys {MODIFIER_LABELS.get(removed, removed)}.")
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("No table effect to destroy.")
            return

        if modifier == MODIFIER_BREAK_PLUS:
            if opponent.table_modifiers:
                count = len(opponent.table_modifiers)
                had_lockdown = MODIFIER_LOCKDOWN in opponent.table_modifiers
                opponent.table_modifiers.clear()
                self._play_sound_for_player(player, SOUND_CONTROL_SUCCESS)
                if had_lockdown:
                    self.play_sound(SOUND_LOCKDOWN_END, volume=70)
                self.broadcast(f"{player.name} destroys all opponent table effects ({count}).")
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("No table effects to destroy.")
            return

        if modifier == MODIFIER_LOCKDOWN:
            if opponent.table_modifiers:
                opponent.table_modifiers.clear()
                self.broadcast(f"{player.name} clears opponent table effects.")
            self._place_table_effect(player, modifier)
            self.play_sound(SOUND_LOCKDOWN_APPLY, volume=75)
            return

        if modifier == MODIFIER_PRECISION_DRAW:
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announce_source=f"{player.name} precision draws",
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("Precision Draw found no card.")
            return

        if modifier == MODIFIER_PRECISION_DRAW_PLUS:
            self._place_table_effect(player, modifier)
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announce_source=f"{player.name} precision draws",
                    reveal_to_others=True,
                )
                player.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("Precision Draw+ found no card.")
            return

        if modifier == MODIFIER_PRIME_DRAW:
            card = self._draw_best_possible_card(player)
            if card:
                self._add_card_to_hand(
                    player,
                    card,
                    announce_source=f"{player.name} prime draws",
                    reveal_to_others=True,
                )
                player.stand_pending = False
            self._give_random_modifiers(player, 2, announce=True)
            return

        if modifier in TARGET_VALUE_MODIFIERS:
            self._place_table_effect(player, modifier)
            self.broadcast(f"Target changes to {self._current_target()}.")
            return

        if modifier == MODIFIER_SALVAGE:
            self._place_table_effect(player, modifier)
            return

        if modifier == MODIFIER_AID_RIVAL:
            card = self._draw_best_possible_card(opponent)
            if card:
                self._add_card_to_hand(
                    opponent,
                    card,
                    announce_source=f"{opponent.name} draws from Aid Rival",
                    reveal_to_others=True,
                )
                opponent.stand_pending = False
            else:
                self._play_sound_for_player(player, SOUND_ACTION_FAIL)
                self.broadcast("Aid Rival found no card.")

    def _alive_players(self) -> list[TwentyOnePlayer]:
        return [
            p for p in self.get_active_players()
            if isinstance(p, TwentyOnePlayer) and p.hp > 0
        ]

    def _opponent_of(self, player: TwentyOnePlayer) -> TwentyOnePlayer | None:
        for other in self._alive_players():
            if other.id != player.id:
                return other
        return None

    def _both_players_standing(self) -> bool:
        players = self._alive_players()
        if len(players) < 2:
            return False
        return all(p.stand_pending for p in players)

    def _clear_pending_stands(self) -> None:
        players = self._alive_players()
        if not any(p.stand_pending for p in players):
            return
        for p in players:
            p.stand_pending = False

    def _hand_total(self, player: TwentyOnePlayer) -> int:
        return sum(card.rank for card in player.hand)

    @staticmethod
    def _opponent_visible_cards(player: TwentyOnePlayer) -> list[Card]:
        if len(player.hand) <= 1:
            return []
        return player.hand[1:]

    def _current_target(self) -> int:
        for player in self._alive_players():
            for modifier in reversed(player.table_modifiers):
                if modifier in TARGET_VALUE_MODIFIERS:
                    return TARGET_VALUE_MODIFIERS[modifier]
        return 21

    def _current_bet(self, player: TwentyOnePlayer) -> int:
        base = max(0, self.options.base_bet)
        opponent = self._opponent_of(player)
        if not opponent:
            return base

        increase = 0
        for modifier in opponent.table_modifiers:
            if modifier == MODIFIER_RAISE_1:
                increase += 1
            elif modifier == MODIFIER_RAISE_2:
                increase += 2
            elif modifier == MODIFIER_RAISE_2_PLUS:
                increase += 2
            elif modifier == MODIFIER_PRECISION_DRAW_PLUS:
                increase += 5

        reduction = 0
        for modifier in player.table_modifiers:
            if modifier == MODIFIER_GUARD:
                reduction += 1
            elif modifier == MODIFIER_GUARD_PLUS:
                reduction += 2

        return max(0, base + increase - reduction)

    def _modifiers_locked_for(self, player: TwentyOnePlayer) -> bool:
        opponent = self._opponent_of(player)
        if not opponent:
            return False
        return MODIFIER_LOCKDOWN in opponent.table_modifiers

    def _playable_modifiers(self, player: TwentyOnePlayer) -> list[str]:
        return [modifier for modifier in player.modifiers if self._is_single_modifier_playable(player, modifier)]

    def _is_single_modifier_playable(self, player: TwentyOnePlayer, modifier: str) -> bool:
        if self._modifiers_locked_for(player):
            return False
        if modifier not in MODIFIER_POOL:
            return False

        if modifier in TABLE_EFFECT_MODIFIERS:
            if modifier in TARGET_VALUE_MODIFIERS:
                return True
            return len(player.table_modifiers) < TABLE_EFFECT_LIMIT

        opponent = self._opponent_of(player)
        if not opponent:
            return False

        if modifier == MODIFIER_SCRAP:
            return self._peek_last_drawn_card(opponent) is not None
        if modifier == MODIFIER_RECYCLE:
            return self._peek_last_drawn_card(player) is not None
        if modifier == MODIFIER_SWAP_DRAW:
            return (
                self._peek_last_drawn_card(player) is not None
                and self._peek_last_drawn_card(opponent) is not None
            )
        if modifier == MODIFIER_BREAK:
            return bool(opponent.table_modifiers)
        if modifier == MODIFIER_BREAK_PLUS:
            return bool(opponent.table_modifiers)
        return True

    def _place_table_effect(self, player: TwentyOnePlayer, modifier: str) -> None:
        if modifier in TARGET_VALUE_MODIFIERS:
            for p in self._alive_players():
                p.table_modifiers = [t for t in p.table_modifiers if t not in TARGET_VALUE_MODIFIERS]

        player.table_modifiers.append(modifier)
        while len(player.table_modifiers) > TABLE_EFFECT_LIMIT:
            removed = player.table_modifiers.pop(0)
            self.play_sound(SOUND_EFFECT_EXPIRE, volume=70)
            if removed == MODIFIER_LOCKDOWN:
                self.play_sound(SOUND_LOCKDOWN_END, volume=70)
            self.broadcast(f"{player.name}'s {MODIFIER_LABELS.get(removed, removed)} expires.")

    @staticmethod
    def _pop_last_table_effect(player: TwentyOnePlayer) -> str | None:
        if not player.table_modifiers:
            return None
        return player.table_modifiers.pop()

    def _trigger_harvest_rewards(self) -> None:
        for player in self._alive_players():
            if MODIFIER_SALVAGE in player.table_modifiers:
                self._give_random_modifiers(player, 1, announce=True)

    def _build_round_deck(self) -> None:
        cards: list[Card] = []
        card_id = self.round_number * 1000
        deck_count = max(1, self.options.deck_count)
        for _ in range(deck_count):
            for rank in range(1, 12):
                cards.append(Card(id=card_id, rank=rank, suit=0))
                card_id += 1
        self.deck = Deck(cards=cards)
        self.deck.shuffle()

    def _draw_card(self) -> Card | None:
        if not self.deck:
            return None
        if self.deck.is_empty():
            return None
        return self.deck.draw_one()

    def _draw_specific_rank(self, rank: int) -> Card | None:
        if not self.deck:
            return None
        if self.deck.is_empty():
            return None

        for index, card in enumerate(self.deck.cards):
            if card.rank == rank:
                return self.deck.cards.pop(index)
        return None

    def _draw_best_possible_card(self, player: TwentyOnePlayer) -> Card | None:
        if not self.deck:
            return None
        if not self.deck or self.deck.is_empty():
            return None

        target = self._current_target()
        current = self._hand_total(player)
        best_index = -1
        best_value = -1
        fallback_index = 0
        fallback_value = 999
        for index, card in enumerate(self.deck.cards):
            value = card.rank
            projected = current + value
            if projected <= target and value > best_value:
                best_value = value
                best_index = index
            diff = abs(projected - target)
            if diff < fallback_value:
                fallback_value = diff
                fallback_index = index
        chosen_index = best_index if best_index >= 0 else fallback_index
        return self.deck.cards.pop(chosen_index)

    def _add_card_to_hand(
        self,
        player: TwentyOnePlayer,
        card: Card,
        *,
        announce_source: str | None,
        reveal_to_others: bool = True,
    ) -> None:
        player.hand.append(card)
        player.last_drawn_card_id = card.id if reveal_to_others else None
        if announce_source:
            if reveal_to_others:
                self.broadcast(f"{announce_source} {card_name(card, 'en')} ({card.rank}).")
            else:
                self._speak_private(player, f"You receive a hidden card ({card.rank}).")
                self.broadcast(f"{player.name} receives a hidden card.", exclude=player)
            self._play_near_bust_sounds(player)

    def _speak_private(self, player: TwentyOnePlayer, text: str) -> None:
        if hasattr(self, "record_transcript_event"):
            self.record_transcript_event(player, text, "table")
        user = self.get_user(player)
        if user:
            user.speak(text, "table")

    def _return_card_to_top_of_deck(self, card: Card) -> None:
        if not self.deck:
            self.deck = Deck(cards=[card])
            return
        self.deck.add_top([card])

    def _peek_last_drawn_card(self, player: TwentyOnePlayer) -> Card | None:
        if player.last_drawn_card_id is None:
            return None
        for card in player.hand:
            if card.id == player.last_drawn_card_id:
                return card
        return None

    def _extract_last_drawn_card(self, player: TwentyOnePlayer) -> Card | None:
        card = self._peek_last_drawn_card(player)
        if not card:
            return None
        for index, hand_card in enumerate(player.hand):
            if hand_card.id == card.id:
                removed = player.hand.pop(index)
                player.last_drawn_card_id = None
                return removed
        return None

    def _give_random_modifiers(self, player: TwentyOnePlayer, count: int, *, announce: bool) -> None:
        for _ in range(max(0, count)):
            modifier = random.choice(MODIFIER_POOL)  # nosec B311
            player.modifiers.append(modifier)
            if announce:
                self._play_sound_for_player(player, SOUND_GAIN_CHANGE_CARD, volume=70)
                self._speak_private(player, f"You gain change card {MODIFIER_LABELS.get(modifier, modifier)}.")
                self.broadcast(f"{player.name} gains a change card.", exclude=player)

    def _discard_random_modifiers(
        self,
        player: TwentyOnePlayer,
        count: int,
        *,
        announce_sound: bool = False,
    ) -> None:
        for _ in range(min(max(0, count), len(player.modifiers))):
            index = random.randrange(len(player.modifiers))  # nosec B311
            player.modifiers.pop(index)
            if announce_sound:
                self._play_sound_for_player(player, SOUND_LOSE_CHANGE_CARD, volume=70)

    def _sync_hp_scores(self) -> None:
        for team in self._team_manager.teams:
            team.total_score = 0
        for player in self.players:
            if not isinstance(player, TwentyOnePlayer) or player.is_spectator:
                continue
            team = self._team_manager.get_team(player.name)
            if team:
                team.total_score = player.hp

    def build_game_result(self) -> GameResult:
        players = [
            p for p in self.players
            if isinstance(p, TwentyOnePlayer) and not p.is_spectator
        ]
        winner = max(players, key=lambda p: p.hp, default=None)
        final_hp = {p.name: p.hp for p in players}

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
                for p in players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_hp": winner.hp if winner else 0,
                "final_hp": final_hp,
                "rounds_played": self.round_number,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_hp = result.custom_data.get("final_hp", {})
        sorted_hp = sorted(final_hp.items(), key=lambda item: item[1], reverse=True)
        for index, (name, hp) in enumerate(sorted_hp, 1):
            lines.append(f"{index}. {name}: {hp} HP")
        return lines
