"""Chameleon party game implementation for PlayPalace.

Players receive a secret word and one player is the Chameleon. Each player
gives a one-word clue, then everyone votes on who the Chameleon is. If the
Chameleon is caught, they get one chance to guess the word.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random
from typing import Any

from ..base import Game, Player, GameOptions
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, EditboxInput, MenuInput, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.game_status import GameStatus
from ...game_utils.options import IntOption, option_field
from ...messages.localization import Localization
from server.core.ui.keybinds import KeybindState


CHAMELEON_ROUNDS: list[dict[str, Any]] = [
    {"topic": "Desserts", "word": "Tiramisu", "hints": ["coffee", "cream", "italian", "layers"]},
    {"topic": "Animals", "word": "Penguin", "hints": ["bird", "ice", "black", "waddle"]},
    {"topic": "Movies", "word": "Pirates", "hints": ["ship", "ocean", "sword", "treasure"]},
    {"topic": "Sports", "word": "Basketball", "hints": ["hoop", "dribble", "court", "bounce"]},
    {"topic": "Music", "word": "Orchestra", "hints": ["violin", "conductor", "ensemble", "strings"]},
    {"topic": "Weather", "word": "Thunderstorm", "hints": ["lightning", "rain", "cloud", "rumble"]},
    {"topic": "Food", "word": "Sushi", "hints": ["rice", "fish", "roll", "wasabi"]},
    {"topic": "Transportation", "word": "Subway", "hints": ["train", "tunnel", "platform", "underground"]},
    {"topic": "Technology", "word": "Smartphone", "hints": ["screen", "apps", "battery", "camera"]},
    {"topic": "Clothing", "word": "Jacket", "hints": ["zipper", "warm", "coat", "sleeves"]},
    {"topic": "Plants", "word": "Sunflower", "hints": ["yellow", "seed", "petal", "tall"]},
    {"topic": "Buildings", "word": "Lighthouse", "hints": ["beacon", "coast", "tower", "guide"]},
    {"topic": "Games", "word": "Chess", "hints": ["board", "king", "move", "rook"]},
    {"topic": "Travel", "word": "Backpack", "hints": ["straps", "trip", "carry", "camp"]},
    {"topic": "Nature", "word": "Waterfall", "hints": ["river", "cliff", "spray", "cascade"]},
    {"topic": "Kitchen", "word": "Spatula", "hints": ["flip", "cooking", "pan", "tool"]},
]


def _trim_clue(text: str) -> str:
    pieces = text.strip().split()
    return pieces[0] if pieces else ""


def _random_sound(base_name: str, count: int) -> str:
    return f"game_chameleon/{base_name}{random.randint(1, count)}.ogg"  # nosec B311


@dataclass
class ChameleonPlayer(Player):
    """Player state for Chameleon."""

    score: int = 0
    clue: str = ""
    voted_for: str | None = None
    guessed_word: str | None = None
    is_chameleon_round: bool = False


@dataclass
class ChameleonOptions(GameOptions):
    """Options for Chameleon."""

    target_score: int = option_field(
        IntOption(
            default=5,
            min_val=3,
            max_val=20,
            value_key="score",
            label="game-set-target-score",
            prompt="game-enter-target-score",
            change_msg="game-option-changed-target",
            description="chameleon-desc-target-score",
        )
    )


@dataclass
@register_game
class ChameleonGame(Game):
    """Chameleon party game."""

    players: list[ChameleonPlayer] = field(default_factory=list)
    options: ChameleonOptions = field(default_factory=ChameleonOptions)

    phase: str = "waiting"  # waiting, clue, vote, guess, finished
    current_card: dict[str, Any] | None = None
    chameleon_id: str = ""
    clues: dict[str, str] = field(default_factory=dict)
    votes: dict[str, str] = field(default_factory=dict)
    guess_result: str = ""  # correct, wrong, or empty

    @classmethod
    def get_name(cls) -> str:
        return "Chameleon"

    @classmethod
    def get_type(cls) -> str:
        return "chameleon"

    @classmethod
    def get_category(cls) -> str:
        return "category-party-games"

    @classmethod
    def get_min_players(cls) -> int:
        return 3

    @classmethod
    def get_max_players(cls) -> int:
        return 8

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> ChameleonPlayer:
        return ChameleonPlayer(id=player_id, name=name, is_bot=is_bot)

    def setup_keybinds(self) -> None:
        super().setup_keybinds()
        self.define_keybind("c", "Give clue", ["give_clue"], state=KeybindState.ACTIVE)
        self.define_keybind("v", "Vote", ["vote"], state=KeybindState.ACTIVE)
        self.define_keybind("g", "Guess", ["guess_word"], state=KeybindState.ACTIVE)

    def on_start(self) -> None:
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0
        self.phase = "clue"
        self.play_sound("game_chameleon/shuffle.ogg")
        self.play_music("game_chameleon/music.ogg", looping=True)
        self.set_turn_players(self.get_active_players())
        for player in self.get_active_players():
            player.score = 0
            player.clue = ""
            player.voted_for = None
            player.guessed_word = None
            player.is_chameleon_round = False
        self._start_round()

    def on_tick(self) -> None:
        super().on_tick()
        BotHelper.on_tick(self)

    def _player_locale(self, player: Player) -> str:
        user = self.get_user(player)
        return user.locale if user else "en"

    def _current_round_card(self) -> dict[str, Any]:
        return dict(random.choice(CHAMELEON_ROUNDS))  # nosec B311

    def _focus_current_player_menu(self) -> None:
        current = self.current_player
        if current is None:
            return
        for player in self.players:
            if player.is_spectator:
                continue
            if player is current:
                self.rebuild_player_menu(player, position=1)
            else:
                self.rebuild_player_menu(player)

    def _private_round_info(self) -> None:
        if not self.current_card:
            return
        topic = self.current_card["topic"]
        word = self.current_card["word"]
        for player in self.get_active_players():
            user = self.get_user(player)
            if not user:
                continue
            user.speak_l("chameleon-topic-private", topic=topic)
            if player.id == self.chameleon_id:
                user.speak_l("chameleon-you-are-chameleon")
                user.speak_l("chameleon-you-see-topic")
            else:
                user.speak_l("chameleon-you-are-not-chameleon")
                user.speak_l("chameleon-secret-word", word=word)

    def _start_round(self) -> None:
        self.round += 1
        active = self.get_active_players()
        if len(active) < self.get_min_players():
            self.finish_game()
            return

        self.phase = "clue"
        self.current_card = self._current_round_card()
        self.chameleon_id = random.choice(active).id  # nosec B311
        self.clues.clear()
        self.votes.clear()
        self.guess_result = ""

        for player in active:
            player.clue = ""
            player.voted_for = None
            player.guessed_word = None
            player.is_chameleon_round = player.id == self.chameleon_id

        self.set_turn_players(active)
        self.reset_turn_order()

        self.play_sound("game_chameleon/roundstart.ogg")
        self.broadcast_l("chameleon-round-start", round=self.round)
        self._private_round_info()
        self.announce_turn()
        self._focus_current_player_menu()
        BotHelper.jolt_bots(self, ticks=random.randint(8, 15))  # nosec B311

    def _start_vote_phase(self) -> None:
        self.phase = "vote"
        self.set_turn_players(self.get_active_players())
        self.reset_turn_order()
        self.broadcast_l("chameleon-select-suspect")
        self.announce_turn()
        self._focus_current_player_menu()
        BotHelper.jolt_bots(self, ticks=random.randint(8, 15))  # nosec B311

    def _start_guess_phase(self) -> None:
        chameleon = self.get_player_by_id(self.chameleon_id)
        if not chameleon:
            self._resolve_round(caught=True, guess_correct=False)
            return

        self.phase = "guess"
        self.set_turn_players([chameleon])
        self.reset_turn_order()
        self.broadcast_l("chameleon-caught", player=chameleon.name)
        self.announce_turn()
        self._focus_current_player_menu()
        BotHelper.jolt_bot(chameleon, ticks=random.randint(8, 15))  # nosec B311

    def _active_vote_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for target_name in self.votes.values():
            counts[target_name] = counts.get(target_name, 0) + 1
        return counts

    def _top_vote_target(self) -> tuple[str | None, bool]:
        counts = self._active_vote_counts()
        if not counts:
            return None, False
        sorted_counts = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        top_target, top_count = sorted_counts[0]
        tied = len(sorted_counts) > 1 and sorted_counts[1][1] == top_count
        return top_target, tied

    def _resolve_round(self, caught: bool, guess_correct: bool) -> None:
        active = self.get_active_players()
        chameleon = self.get_player_by_id(self.chameleon_id)
        if not chameleon:
            self.finish_game()
            return

        if caught and guess_correct:
            chameleon.score += 3
            self.guess_result = "correct"
            self.broadcast_l("chameleon-guess-correct", player=chameleon.name)
            self.broadcast_l("chameleon-round-points", player=chameleon.name, points=3)
        elif caught:
            self.guess_result = "wrong"
            self.play_sound("game_chameleon/wrong_guess.ogg")
            for player in active:
                if player.id != chameleon.id:
                    player.score += 1
            self.broadcast_l("chameleon-guess-wrong", player=chameleon.name)
            for player in active:
                if player.id != chameleon.id:
                    self.broadcast_l("chameleon-round-points", player=player.name, points=1)
        else:
            chameleon.score += 2
            self.guess_result = ""
            self.broadcast_l("chameleon-not-caught")
            self.broadcast_l("chameleon-round-points", player=chameleon.name, points=2)

        self.broadcast_l("chameleon-scoreboard")
        for player in sorted(active, key=lambda item: (-item.score, item.name)):
            self.broadcast_l("chameleon-score-line", player=player.name, score=player.score)

        winner = self._get_winner()
        if winner:
            self.play_sound("game_chameleon/win.ogg")
            self.broadcast_l("chameleon-game-winner", player=winner.name, score=winner.score)
            self.finish_game()
            return

        self._start_round()

    def _get_winner(self) -> ChameleonPlayer | None:
        active = self.get_active_players()
        contenders = [player for player in active if player.score >= self.options.target_score]
        if not contenders:
            return None
        return sorted(contenders, key=lambda item: (-item.score, self.players.index(item)))[0]

    def _advance_after_action(self) -> None:
        if not self.turn_player_ids:
            return

        if self.turn_index >= len(self.turn_player_ids) - 1:
            if self.phase == "clue":
                self._start_vote_phase()
            elif self.phase == "vote":
                self.play_sound("game_chameleon/voted.ogg")
                top_target, tied = self._top_vote_target()
                chameleon = self.get_player_by_id(self.chameleon_id)
                if top_target is None or tied or chameleon is None or top_target != chameleon.name:
                    self._resolve_round(caught=False, guess_correct=False)
                else:
                    self.play_sound("game_chameleon/caught.ogg")
                    self._start_guess_phase()
            elif self.phase == "guess":
                chameleon = self.get_player_by_id(self.chameleon_id)
                guess_correct = bool(
                    chameleon
                    and self.current_card
                    and chameleon.guessed_word
                    and chameleon.guessed_word.casefold() == self.current_card["word"].casefold()
                )
                self._resolve_round(caught=True, guess_correct=guess_correct)
            return

        self.advance_turn(announce=False)
        self.announce_turn()
        self._focus_current_player_menu()

    def create_turn_action_set(self, player: ChameleonPlayer) -> ActionSet:
        action_set = ActionSet(name="turn")
        locale = self._player_locale(player)

        action_set.add(
            Action(
                id="give_clue",
                label=Localization.get(locale, "chameleon-your-turn-clue"),
                handler="_action_give_clue",
                is_enabled="_is_give_clue_enabled",
                is_hidden="_is_give_clue_hidden",
                input_request=EditboxInput(
                    prompt="chameleon-enter-clue",
                    bot_input="_bot_input_clue",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="vote",
                label=Localization.get(locale, "chameleon-your-turn-vote"),
                handler="_action_vote",
                is_enabled="_is_vote_enabled",
                is_hidden="_is_vote_hidden",
                input_request=MenuInput(
                    prompt="chameleon-select-suspect",
                    options="_vote_options",
                    bot_select="_bot_select_vote",
                ),
                show_in_actions_menu=False,
            )
        )
        action_set.add(
            Action(
                id="guess_word",
                label=Localization.get(locale, "chameleon-your-turn-guess"),
                handler="_action_guess_word",
                is_enabled="_is_guess_enabled",
                is_hidden="_is_guess_hidden",
                input_request=EditboxInput(
                    prompt="chameleon-enter-guess",
                    bot_input="_bot_input_guess",
                ),
                show_in_actions_menu=False,
            )
        )

        return action_set

    def _is_give_clue_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "clue":
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_give_clue_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.phase == "clue" and self.current_player == player else Visibility.HIDDEN

    def _is_vote_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "vote":
            return "action-not-available"
        if self.current_player != player:
            return "action-not-your-turn"
        return None

    def _is_vote_hidden(self, player: Player) -> Visibility:
        return Visibility.VISIBLE if self.phase == "vote" and self.current_player == player else Visibility.HIDDEN

    def _is_guess_enabled(self, player: Player) -> str | None:
        if self.status != "playing":
            return "action-not-playing"
        if self.phase != "guess":
            return "action-not-available"
        if self.current_player != player or player.id != self.chameleon_id:
            return "action-not-your-turn"
        return None

    def _is_guess_hidden(self, player: Player) -> Visibility:
        return (
            Visibility.VISIBLE
            if self.phase == "guess" and self.current_player == player and player.id == self.chameleon_id
            else Visibility.HIDDEN
        )

    def _vote_options(self, player: Player) -> list[str]:
        return [candidate.name for candidate in self.get_active_players() if candidate.id != player.id]

    def _bot_select_vote(self, player: Player, options: list[str]) -> str:
        if not options:
            return ""
        return random.choice(options)  # nosec B311

    def _bot_input_clue(self, player: Player) -> str:
        if not self.current_card:
            return "hmm"
        hints = list(self.current_card.get("hints", []))
        if not hints:
            hints = [self.current_card["topic"].split()[0].lower()]
        return random.choice(hints)  # nosec B311

    def _bot_input_guess(self, player: Player) -> str:
        if not self.current_card:
            return ""
        if random.random() < 0.45:  # nosec B311
            return self.current_card["word"]
        hints = list(self.current_card.get("hints", []))
        if hints:
            return random.choice(hints)  # nosec B311
        return self.current_card["topic"]

    def bot_think(self, player: Player) -> str | None:
        if self.phase == "clue" and self.current_player == player:
            return "give_clue"
        if self.phase == "vote" and self.current_player == player:
            return "vote"
        if self.phase == "guess" and self.current_player == player and player.id == self.chameleon_id:
            return "guess_word"
        return None

    def _action_give_clue(self, player: Player, clue: str, action_id: str) -> None:
        if self.phase != "clue" or self.current_player != player:
            return
        clue_word = _trim_clue(clue)
        if not clue_word:
            user = self.get_user(player)
            if user:
                user.speak_l("chameleon-invalid-clue")
            return

        ch_player = player if isinstance(player, ChameleonPlayer) else None
        if ch_player:
            ch_player.clue = clue_word
        self.play_sound(_random_sound("draw", 4))
        self.clues[player.id] = clue_word
        self.broadcast_l("chameleon-clue-given", player=player.name, clue=clue_word)
        self._advance_after_action()

    def _action_vote(self, player: Player, target_name: str, action_id: str) -> None:
        if self.phase != "vote" or self.current_player != player:
            return
        valid_targets = set(self._vote_options(player))
        if target_name not in valid_targets:
            user = self.get_user(player)
            if user:
                user.speak_l("chameleon-invalid-vote")
            return

        ch_player = player if isinstance(player, ChameleonPlayer) else None
        if ch_player:
            ch_player.voted_for = target_name
        self.play_sound(_random_sound("play", 4))
        self.votes[player.id] = target_name
        self.broadcast_l("chameleon-vote-recorded", player=player.name)
        self.broadcast_l("chameleon-vote-reveal", player=player.name, target=target_name)
        self._advance_after_action()

    def _action_guess_word(self, player: Player, guess: str, action_id: str) -> None:
        if self.phase != "guess" or self.current_player != player or player.id != self.chameleon_id:
            return
        guess_word = guess.strip()
        if not guess_word:
            user = self.get_user(player)
            if user:
                user.speak_l("chameleon-invalid-guess")
            return

        ch_player = player if isinstance(player, ChameleonPlayer) else None
        if ch_player:
            ch_player.guessed_word = guess_word
        correct_word = self.current_card["word"] if self.current_card else ""
        if guess_word.casefold() != correct_word.casefold():
            self.play_sound(_random_sound("discard", 3))
        self._resolve_round(caught=True, guess_correct=guess_word.casefold() == correct_word.casefold())

    def _is_check_scores_enabled(self, player: Player) -> str | None:
        if self.status == "waiting":
            return "action-not-playing"
        return None

    def _is_check_scores_detailed_enabled(self, player: Player) -> str | None:
        return self._is_check_scores_enabled(player)

    def _action_check_scores(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "chameleon-scores-header")]
        for entry in sorted(self.get_active_players(), key=lambda item: (-item.score, item.name)):
            lines.append(Localization.get(user.locale, "chameleon-score-line", player=entry.name, score=entry.score))
        user.speak("\n".join(lines))

    def _action_check_scores_detailed(self, player: Player, action_id: str) -> None:
        user = self.get_user(player)
        if not user:
            return
        lines = [Localization.get(user.locale, "chameleon-scores-header")]
        lines.append(Localization.get(user.locale, "chameleon-round-start", round=self.round))
        if self.current_card:
            lines.append(
                Localization.get(
                    user.locale,
                    "chameleon-final-word",
                    word=self.current_card["word"],
                    topic=self.current_card["topic"],
                )
            )
        for entry in sorted(self.get_active_players(), key=lambda item: (-item.score, item.name)):
            lines.append(Localization.get(user.locale, "chameleon-score-line", player=entry.name, score=entry.score))
        self.status_box(player, lines)

    def build_game_result(self) -> GameResult:
        active = self.get_active_players()
        winner = self._get_winner()
        final_scores = {player.name: player.score for player in active}
        chameleon = self.get_player_by_id(self.chameleon_id)
        return GameResult(
            game_type=self.get_type(),
            timestamp=datetime.now().isoformat(),
            duration_ticks=self.sound_scheduler_tick,
            player_results=[
                PlayerResult(
                    player_id=player.id,
                    player_name=player.name,
                    is_bot=player.is_bot,
                    is_virtual_bot=getattr(player, "is_virtual_bot", False),
                )
                for player in sorted(active, key=lambda item: (-item.score, item.name))
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_score": winner.score if winner else 0,
                "final_scores": final_scores,
                "rounds_played": self.round,
                "topic": self.current_card["topic"] if self.current_card else "",
                "word": self.current_card["word"] if self.current_card else "",
                "chameleon_name": chameleon.name if chameleon else "",
                "caught": self.guess_result in {"correct", "wrong"},
                "guess_correct": self.guess_result == "correct",
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        lines = [Localization.get(locale, "game-final-scores")]
        final_scores = result.custom_data.get("final_scores", {})
        sorted_scores = sorted(final_scores.items(), key=lambda item: (-item[1], item[0]))
        for name, score in sorted_scores:
            lines.append(Localization.get(locale, "chameleon-score-line", player=name, score=score))
        if result.custom_data.get("caught"):
            if result.custom_data.get("guess_correct"):
                lines.append(
                    Localization.get(locale, "chameleon-guess-correct", player=result.custom_data.get("chameleon_name", ""))
                )
            else:
                lines.append(
                    Localization.get(locale, "chameleon-guess-wrong", player=result.custom_data.get("chameleon_name", ""))
                )
        else:
            lines.append(Localization.get(locale, "chameleon-not-caught"))
        lines.append(
            Localization.get(
                locale,
                "chameleon-final-word",
                word=result.custom_data.get("word", ""),
                topic=result.custom_data.get("topic", ""),
            )
        )
        winner_name = result.custom_data.get("winner_name")
        if winner_name:
            lines.append(
                Localization.get(
                    locale,
                    "chameleon-game-winner",
                    player=winner_name,
                    score=result.custom_data.get("winner_score", 0),
                )
            )
        return lines

    def get_rankings_for_rating(self, result: GameResult) -> list[list[str]]:
        final_scores = result.custom_data.get("final_scores", {})
        if not final_scores:
            return super().get_rankings_for_rating(result)
        ordered = sorted(
            self.get_active_players(),
            key=lambda player: (-final_scores.get(player.name, 0), player.name),
        )
        rankings: list[list[str]] = []
        last_score: int | None = None
        current_group: list[str] = []
        for player in ordered:
            score = final_scores.get(player.name, 0)
            if last_score is None or score == last_score:
                current_group.append(player.id)
            else:
                rankings.append(current_group)
                current_group = [player.id]
            last_score = score
        if current_group:
            rankings.append(current_group)
        return rankings
