"""
Command-line interface for AI agents to simulate and watch games.

All operations are parameter-based with no interactive input required.

Usage examples:
    # Simulate a Light Turret game with 2 bots
    python -m server.cli simulate lightturret --bots 2

    # Simulate with specific bot names
    python -m server.cli simulate lightturret --bots Alice,Bob,Charlie

    # Set game options
    python -m server.cli simulate lightturret --bots 3 -o starting_power=15 -o max_rounds=30

    # Output as JSON for machine parsing
    python -m server.cli simulate lightturret --bots 2 --json

    # Test serialization (save/restore after each tick)
    python -m server.cli simulate threes --bots 2 --test-serialization

    # List available games
    python -m server.cli list-games

    # Show game options
    python -m server.cli show-options lightturret
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from getpass import getpass
from io import StringIO
from pathlib import Path
from typing import Any

import pyperclip

# Allow running as standalone script (uv run cli.py)
_MODULE_DIR = Path(__file__).parent
if __name__ == "__main__":
    sys.path.insert(0, str(_MODULE_DIR.parent))

# Initialize localization before importing games
from server.messages.localization import Localization  # noqa: E402

Localization.init(_MODULE_DIR / "locales")

from server.games.registry import GameRegistry, get_game_class  # noqa: E402
from server.games.base import Game, BOT_NAMES  # noqa: E402
from server.core.users.base import User, MenuItem, TrustLevel, generate_uuid  # noqa: E402
from server.core.users.bot import Bot  # noqa: E402
from server.core.ui.keybinds import KeybindState  # noqa: E402
from server.persistence.database import Database  # noqa: E402
from server.auth.auth import AuthManager  # noqa: E402


@dataclass
class SpectatorUser(User):
    """
    A spectator user that captures all game output.
    Used for CLI simulation to watch games play out.
    """

    _username: str = ""
    _locale: str = "en"
    _uuid: str = field(default_factory=generate_uuid)
    _messages: list = field(default_factory=list)
    _menus: dict = field(default_factory=dict)  # menu_id -> items
    _sounds: list = field(default_factory=list)  # {tick, sound}
    _json_mode: bool = False
    _quiet: bool = False
    _tick: int = 0

    @property
    def username(self) -> str:
        return self._username

    @property
    def locale(self) -> str:
        return self._locale

    @property
    def uuid(self) -> str:
        return self._uuid

    def _log(self, text: str) -> None:
        """Log a message."""
        # Skip messages about the spectator
        if "__spectator__" in text:
            return
        self._messages.append(text)
        if not self._quiet and not self._json_mode:
            print(f"  {text}")

    def speak(self, text: str, buffer: str = "misc") -> None:
        self._log(text)

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        self._sounds.append({"tick": self._tick, "sound": name})

    def play_music(self, name: str, looping: bool = True) -> None:
        pass  # Ignore music

    def stop_music(self) -> None:
        pass

    def play_ambience(self, loop: str, intro: str = "", outro: str = "") -> None:
        pass  # Ignore ambience

    def stop_ambience(self) -> None:
        pass

    def show_menu(self, menu_id: str, items: list, **kwargs) -> None:
        # Extract text from MenuItem objects
        item_texts = []
        for item in items:
            if hasattr(item, "text"):
                item_texts.append(item.text)
            elif isinstance(item, dict):
                item_texts.append(item.get("text", str(item)))
            else:
                item_texts.append(str(item))
        self._menus[menu_id] = item_texts

    def update_menu(
        self,
        menu_id: str,
        items: list,
        position: int | None = None,
        selection_id: str | None = None,
    ) -> None:
        self.show_menu(menu_id, items)

    def remove_menu(self, menu_id: str) -> None:
        self._menus.pop(menu_id, None)

    def show_editbox(self, input_id: str, prompt: str, default_value: str = "", **kwargs) -> None:
        pass

    def remove_editbox(self, input_id: str) -> None:
        pass

    def clear_ui(self) -> None:
        self._menus.clear()


class CapturingBot(Bot):
    """
    A bot that captures menus, speech, and sound events for CLI inspection.
    Used instead of plain Bot when the CLI needs to report what players see.
    """

    def __init__(self, name: str, locale: str = "en"):
        super().__init__(name, locale=locale)
        self.captured_menus: list[dict] = []  # {tick, menu_id, items}
        self.captured_speech: list[str] = []
        self.captured_sounds: list[dict] = []  # {tick, sound, volume, pan, pitch}
        self._tick: int = 0

    def speak(self, text: str, buffer: str = "misc") -> None:
        self.captured_speech.append(text)

    def play_sound(self, name: str, volume: int = 100, pan: int = 0, pitch: int = 100) -> None:
        self.captured_sounds.append(
            {"tick": self._tick, "sound": name, "volume": volume, "pan": pan, "pitch": pitch}
        )

    def show_menu(self, menu_id: str, items: list, **kwargs) -> None:
        item_texts = []
        for item in items:
            if hasattr(item, "text"):
                item_texts.append(item.text)
            elif isinstance(item, dict):
                item_texts.append(item.get("text", str(item)))
            else:
                item_texts.append(str(item))
        self.captured_menus.append(
            {"tick": self._tick, "menu_id": menu_id, "items": item_texts}
        )

    def update_menu(
        self,
        menu_id: str,
        items: list,
        position: int | None = None,
        selection_id: str | None = None,
        play_selection_sound: bool = False,
    ) -> None:
        self.show_menu(menu_id, items)


class GameSimulator:
    """Runs a game simulation with bots and a spectator."""

    def __init__(
        self,
        game_type: str,
        bot_names: list[str],
        options: dict[str, Any],
        json_mode: bool = False,
        quiet: bool = False,
        max_ticks: int = 10000000,
        test_serialization: bool = False,
        locale: str = "en",
        validate_keybinds: bool = False,
    ):
        self.game_type = game_type
        self.bot_names = bot_names
        self.options = options
        self.json_mode = json_mode
        self.quiet = quiet
        self.max_ticks = max_ticks
        self.test_serialization = test_serialization
        self.locale = locale
        self.validate_keybinds = validate_keybinds

        self.game: Game | None = None
        self.spectator: SpectatorUser | None = None
        self.game_class: type | None = None
        self.capturing_bots: dict[str, CapturingBot] = {}  # name -> CapturingBot

    def setup(self) -> bool:
        """Set up the game. Returns True on success."""
        # Get game class
        self.game_class = get_game_class(self.game_type)
        if not self.game_class:
            if not self.json_mode:
                print(f"Error: Unknown game type '{self.game_type}'")
                print("Use 'list-games' to see available games.")
            return False

        # Check player count
        min_players = self.game_class.get_min_players()
        max_players = self.game_class.get_max_players()

        if len(self.bot_names) < min_players:
            if not self.json_mode:
                print(f"Error: {self.game_type} requires at least {min_players} players")
            return False

        if len(self.bot_names) > max_players:
            if not self.json_mode:
                print(f"Error: {self.game_type} allows at most {max_players} players")
            return False

        # Create game instance
        self.game = self.game_class()

        # Apply options
        if hasattr(self.game, "options"):
            for key, value in self.options.items():
                if hasattr(self.game.options, key):
                    # Convert value to appropriate type
                    # Note: Check bool before int because bool is a subclass of int
                    current = getattr(self.game.options, key)
                    if isinstance(current, bool):
                        value = value.lower() in ("true", "1", "yes")
                    elif isinstance(current, int):
                        value = int(value)
                    elif isinstance(current, float):
                        value = float(value)
                    setattr(self.game.options, key, value)
                elif not self.json_mode:
                    print(f"Warning: Unknown option '{key}' for {self.game_type}")

        # Create spectator to watch the game
        self.spectator = SpectatorUser(
            _username="__spectator__",
            _locale=self.locale,
            _json_mode=self.json_mode,
            _quiet=self.quiet,
        )

        # Set up host
        self.game.host = self.bot_names[0]

        # Add bot players using CapturingBot for menu/sound inspection
        for name in self.bot_names:
            bot_user = CapturingBot(name, locale=self.locale)
            self.capturing_bots[name] = bot_user
            player = self.game.create_player(bot_user.uuid, name, is_bot=True)
            self.game.players.append(player)
            self.game.attach_user(player.id, bot_user)
            self.game.setup_player_actions(player)

        # Add spectator as a player to receive broadcasts
        spectator_player = self.game.create_player(
            self.spectator.uuid, "__spectator__", is_bot=False
        )
        spectator_player.is_spectator = True
        self.game.players.append(spectator_player)
        self.game.attach_user(spectator_player.id, self.spectator)
        self.game.setup_player_actions(spectator_player)

        return True

    def _save_and_restore(self, tick: int) -> None:
        """Save game to JSON and restore it, testing serialization."""
        if not self.game or not self.game_class:
            return

        # Save non-serialized runtime state
        saved_users = dict(self.game._users)
        saved_table = self.game._table
        saved_keybinds = dict(self.game._keybinds)
        saved_pending_actions = dict(self.game._pending_actions)
        saved_transient_display_state = dict(self.game._transient_display_state)
        saved_actions_menu_open = set(self.game._actions_menu_open)
        saved_turn_index = self.game.turn_index

        # Serialize to JSON
        try:
            game_json = self.game.to_json()
        except Exception as e:
            raise RuntimeError(f"Serialization failed at tick {tick}: {e}")

        # Deserialize back
        try:
            self.game = self.game_class.from_json(game_json)
        except Exception as e:
            raise RuntimeError(f"Deserialization failed at tick {tick}: {e}")

        # Restore non-serialized runtime state
        self.game._users = saved_users
        self.game._table = saved_table
        self.game._keybinds = saved_keybinds
        self.game._pending_actions = saved_pending_actions
        self.game._transient_display_state = saved_transient_display_state
        self.game._actions_menu_open = saved_actions_menu_open

        # Restore turn_index before rebuild
        self.game.turn_index = saved_turn_index
        self.game.rebuild_runtime_state()

    def run(self) -> dict[str, Any]:
        """Run the simulation to completion. Returns results dict."""
        if not self.game or not self.spectator:
            return {"error": "Game not set up"}

        if not self.json_mode and not self.quiet:
            mode_str = " [testing serialization]" if self.test_serialization else ""
            print(f"\n=== {self.game.get_name()} ({len(self.bot_names)} bots){mode_str} ===\n")

        # Validate before starting
        errors = self.game.prestart_validate()
        if errors:
            for err in errors:
                if isinstance(err, tuple):
                    key, kwargs = err
                    msg = Localization.get("en", key, **kwargs)
                else:
                    msg = Localization.get("en", err)
                print(f"Error: {msg}")
            return {"error": "prestart validation failed", "messages": [str(e) for e in errors]}

        # Start the game
        self.game.setup_keybinds()
        self.game.on_start()

        # Run game loop
        tick = 0
        serialization_error = None
        while self.game.game_active and tick < self.max_ticks:
            # Update tick counters for event logging
            self.spectator._tick = tick
            for bot in self.capturing_bots.values():
                bot._tick = tick

            self.game.on_tick()
            tick += 1

            # Test serialization after each tick if enabled
            if self.test_serialization:
                try:
                    self._save_and_restore(tick)
                except RuntimeError as e:
                    serialization_error = str(e)
                    if not self.json_mode:
                        print(f"\nError: {serialization_error}")
                    break

        # Check for timeout
        timed_out = tick >= self.max_ticks
        if timed_out and not self.json_mode:
            print(f"\nWarning: Game timed out after {self.max_ticks} ticks")

        # Build results - filter out spectator references
        filtered_messages = [m for m in self.spectator._messages if "__spectator__" not in m]
        filtered_menu = [
            item
            for item in self.spectator._menus.get("game_over", [])
            if "__spectator__" not in item
        ]

        results: dict[str, Any] = {
            "game_type": self.game_type,
            "game_name": self.game.get_name(),
            "ticks": tick,
            "rounds": self.game.round,
            "timed_out": timed_out,
            "locale": self.locale,
            "messages": filtered_messages,
            "final_menu": filtered_menu,
        }

        # Add serialization test results
        if self.test_serialization:
            results["serialization_tested"] = True
            if serialization_error:
                results["serialization_error"] = serialization_error
            else:
                results["serialization_passed"] = True

        # Per-player menu captures
        player_menus: dict[str, list[dict]] = {}
        player_sounds: dict[str, list[dict]] = {}
        for name, bot in self.capturing_bots.items():
            if bot.captured_menus:
                player_menus[name] = bot.captured_menus
            if bot.captured_sounds:
                player_sounds[name] = bot.captured_sounds
        results["player_menus"] = player_menus
        results["player_sounds"] = player_sounds

        # Sound summary
        spectator_sound_count = len(self.spectator._sounds)
        total_player_sounds = sum(len(s) for s in player_sounds.values())
        results["sound_events"] = {
            "spectator": spectator_sound_count,
            "players": total_player_sounds,
            "total": spectator_sound_count + total_player_sounds,
        }

        # Keybind validation
        if self.validate_keybinds:
            results["keybind_validation"] = self._validate_keybinds()

        return results

    def _validate_keybinds(self) -> dict[str, Any]:
        """Validate keybinds: check action IDs exist and fire smoke tests."""
        if not self.game:
            return {"error": "no game"}

        issues: list[str] = []
        keybind_summary: list[dict] = []

        # Collect all action IDs across all players
        all_action_ids: set[str] = set()
        for player in self.game.players:
            if player.is_spectator:
                continue
            for action_set in self.game.player_action_sets.get(player.id, []):
                for aid in action_set._order:
                    all_action_ids.add(aid)

        # Static validation: check every keybind references real action IDs
        for key, keybinds in self.game._keybinds.items():
            for keybind in keybinds:
                entry = {
                    "key": key,
                    "name": keybind.name,
                    "actions": keybind.actions,
                    "state": keybind.state.name,
                }
                keybind_summary.append(entry)

                for action_id in keybind.actions:
                    if action_id not in all_action_ids:
                        issues.append(
                            f"Keybind '{key}' ({keybind.name}): "
                            f"action '{action_id}' not found in any action set"
                        )

        # Smoke test: fire each keybind against the first non-spectator player
        smoke_results: list[dict] = []
        test_player = None
        for p in self.game.players:
            if not p.is_spectator:
                test_player = p
                break

        if test_player:
            for key, keybinds in self.game._keybinds.items():
                # Build synthetic event
                event = {"type": "keybind", "key": key}
                if key.startswith("ctrl+"):
                    event["control"] = True
                    event["key"] = key.removeprefix("ctrl+")
                if key.startswith("shift+"):
                    event["shift"] = True
                    event["key"] = key.removeprefix("shift+")
                if key.startswith("alt+"):
                    event["alt"] = True
                    event["key"] = key.removeprefix("alt+")

                try:
                    self.game.handle_event(test_player, event)
                    smoke_results.append({"key": key, "status": "ok"})
                except Exception as e:
                    smoke_results.append({"key": key, "status": "error", "error": str(e)})
                    issues.append(f"Keybind '{key}' smoke test crashed: {e}")

        return {
            "keybinds": keybind_summary,
            "issues": issues,
            "smoke_tests": smoke_results,
            "passed": len(issues) == 0,
        }


def cmd_list_games(args):
    """List all available games."""
    games = GameRegistry.get_all()

    if args.json:
        output = []
        for game_class in games:
            output.append(
                {
                    "type": game_class.get_type(),
                    "name": game_class.get_name(),
                    "category": game_class.get_category(),
                    "min_players": game_class.get_min_players(),
                    "max_players": game_class.get_max_players(),
                }
            )
        print(json.dumps(output, indent=2))
    else:
        print("Available games:\n")
        for game_class in games:
            print(f"  {game_class.get_type()}")
            print(f"    Name: {game_class.get_name()}")
            print(f"    Category: {game_class.get_category()}")
            print(f"    Players: {game_class.get_min_players()}-{game_class.get_max_players()}")
            print()


def cmd_show_options(args):
    """Show options for a specific game."""
    game_class = get_game_class(args.game_type)
    if not game_class:
        print(f"Error: Unknown game type '{args.game_type}'")
        sys.exit(1)

    # Create instance to inspect options
    game = game_class()

    if not hasattr(game, "options"):
        if args.json:
            print(json.dumps({"options": []}))
        else:
            print(f"{args.game_type} has no configurable options.")
        return

    options_obj = game.options
    options_list = []

    # Inspect the options dataclass
    from server.game_utils.options import get_option_meta

    for field_name in options_obj.__dataclass_fields__:
        current_value = getattr(options_obj, field_name)

        option_data = {
            "name": field_name,
            "type": type(current_value).__name__,
            "default": current_value,
        }

        # Try to get metadata from option_field
        meta = get_option_meta(options_obj, field_name)
        if meta:
            if hasattr(meta, "min_val"):
                option_data["min"] = meta.min_val
            if hasattr(meta, "max_val"):
                option_data["max"] = meta.max_val
            if hasattr(meta, "label"):
                option_data["label"] = meta.label

        options_list.append(option_data)

    if args.json:
        print(json.dumps({"game_type": args.game_type, "options": options_list}, indent=2))
    else:
        print(f"Options for {args.game_type}:\n")
        for opt in options_list:
            print(f"  {opt['name']} ({opt['type']})")
            print(f"    Default: {opt['default']}")
            if "min" in opt:
                print(f"    Range: {opt['min']} - {opt['max']}")
            print()


def cmd_simulate(args):
    """Simulate a game with bots."""
    if args.clip:
        capture = StringIO()
        original_stdout = sys.stdout
        sys.stdout = _TeeWriter(original_stdout, capture)
        try:
            _run_simulate(args)
        finally:
            sys.stdout = original_stdout
        output = capture.getvalue()
        if output:
            pyperclip.copy(output)
            print("(Output copied to clipboard.)")
    else:
        _run_simulate(args)


class _TeeWriter:
    """Write to two streams simultaneously."""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


def _run_simulate(args):
    """Core simulate logic."""
    # Parse bot names
    if args.bots.isdigit():
        num_bots = int(args.bots)
        bot_names = BOT_NAMES[:num_bots]
    else:
        bot_names = [name.strip() for name in args.bots.split(",")]

    # Parse options
    options = {}
    if args.option:
        for opt in args.option:
            if "=" in opt:
                key, value = opt.split("=", 1)
                options[key.strip()] = value.strip()

    # Create and run simulator
    simulator = GameSimulator(
        game_type=args.game_type,
        bot_names=bot_names,
        options=options,
        json_mode=args.json,
        quiet=args.quiet,
        max_ticks=args.max_ticks,
        test_serialization=args.test_serialization,
        locale=args.locale,
        validate_keybinds=args.validate_keybinds,
    )

    if not simulator.setup():
        sys.exit(1)

    results = simulator.run()

    if results.get("error"):
        if args.json:
            print(json.dumps(results, indent=2))
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2))
    elif not args.quiet:
        print(f"\n=== Finished: {results['ticks']} ticks, {results['rounds']} rounds ===")
        if results.get("locale") != "en":
            print(f"Locale: {results['locale']}")
        if results.get("final_menu"):
            print("\nFinal standings:")
            for line in results["final_menu"]:
                if line and not line.lower().startswith("leave"):
                    print(f"  {line}")

        # Player menu summary
        player_menus = results.get("player_menus", {})
        if player_menus:
            print("\nPlayer menus captured:")
            for name, menus in player_menus.items():
                # Group by menu_id and show the last snapshot of each
                latest: dict[str, list[str]] = {}
                for m in menus:
                    latest[m["menu_id"]] = m["items"]
                for menu_id, items in latest.items():
                    print(f"  {name} [{menu_id}]: {', '.join(items[:8])}")
                    if len(items) > 8:
                        print(f"    ... and {len(items) - 8} more items")

        # Sound summary
        sound_info = results.get("sound_events", {})
        total_sounds = sound_info.get("total", 0)
        if total_sounds == 0:
            print("\nWarning: 0 sound events fired. Silence is a bug.")
        else:
            print(f"\nSound events: {total_sounds} total ({sound_info.get('spectator', 0)} broadcast, {sound_info.get('players', 0)} per-player)")

        # Keybind validation
        kb = results.get("keybind_validation")
        if kb:
            if kb["passed"]:
                print(f"\nKeybind validation: passed ({len(kb['keybinds'])} keybinds, {len(kb['smoke_tests'])} smoke tests)")
            else:
                print(f"\nKeybind validation: FAILED")
                for issue in kb["issues"]:
                    print(f"  - {issue}")


def _prompt_for_password() -> str:
    """Interactively prompt for a password twice."""
    while True:
        pw = getpass("New owner password: ")
        confirm = getpass("Confirm password: ")
        if pw != confirm:
            print("Passwords do not match. Try again.")
            continue
        if not pw:
            print("Password cannot be empty.")
            continue
        return pw


def _resolve_bootstrap_password(args: argparse.Namespace) -> str:
    """Resolve password from CLI arguments."""
    if args.password is not None:
        return args.password
    if args.password_file:
        path = Path(args.password_file)
        return path.read_text(encoding="utf-8").rstrip("\r\n")
    if args.password_stdin:
        data = sys.stdin.read()
        return data.rstrip("\r\n")
    return _prompt_for_password()


def bootstrap_owner(
    *,
    db_path: str,
    username: str,
    password: str,
    locale: str = "en",
    force: bool = False,
    quiet: bool = False,
) -> str:
    """
    Create or update the initial server owner account.

    Returns a short status string describing the action performed.
    Raises RuntimeError if the operation is not permitted.
    """
    if not password:
        raise RuntimeError("Password cannot be empty.")

    database = Database(db_path)
    database.connect()

    try:
        auth = AuthManager(database)
        user_count = database.get_user_count()
        password_hash = auth.hash_password(password)

        if user_count > 0 and not force:
            raise RuntimeError(
                "Database already contains users. Use --force if you intend to replace or update an existing account."
            )

        if database.user_exists(username):
            if not force:
                raise RuntimeError(
                    f"User '{username}' already exists. Use --force to elevate/update the account."
                )
            database.update_user_password(username, password_hash)
            database.update_user_trust_level(username, TrustLevel.SERVER_OWNER)
            database.approve_user(username)
            action = "Updated"
        else:
            database.create_user(
                username=username,
                password_hash=password_hash,
                locale=locale,
                trust_level=TrustLevel.SERVER_OWNER,
                approved=True,
            )
            action = "Created"

        if not quiet:
            print(f"{action} server owner '{username}' in {db_path}.")
        return action
    finally:
        database.close()


def cmd_bootstrap_owner(args: argparse.Namespace) -> None:
    """Handle the bootstrap-owner CLI command."""
    try:
        password = _resolve_bootstrap_password(args)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Error reading password: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        bootstrap_owner(
            db_path=args.db_path,
            username=args.username,
            password=password,
            locale=args.locale,
            force=args.force,
            quiet=args.quiet,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="PlayPalace CLI for AI agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list-games command
    list_parser = subparsers.add_parser("list-games", help="List available games")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # show-options command
    options_parser = subparsers.add_parser("show-options", help="Show options for a game")
    options_parser.add_argument("game_type", help="Game type (e.g., lightturret, pig)")
    options_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # simulate command
    sim_parser = subparsers.add_parser("simulate", help="Simulate a game with bots")
    sim_parser.add_argument("game_type", help="Game type (e.g., lightturret, pig)")
    sim_parser.add_argument(
        "--bots",
        "-b",
        required=True,
        help="Number of bots (e.g., 3) or comma-separated names (e.g., Alice,Bob)",
    )
    sim_parser.add_argument(
        "--option",
        "-o",
        action="append",
        help="Set game option (e.g., -o starting_power=15)",
    )
    sim_parser.add_argument("--json", action="store_true", help="Output as JSON")
    sim_parser.add_argument("--quiet", "-q", action="store_true", help="Suppress game output")
    sim_parser.add_argument(
        "--max-ticks",
        type=int,
        default=10000000,
        help="Maximum ticks before timeout (default: 10000000)",
    )
    sim_parser.add_argument(
        "--test-serialization",
        "-s",
        action="store_true",
        help="Save and restore game state after each tick to test serialization",
    )
    sim_parser.add_argument(
        "--locale",
        "-l",
        default="en",
        help="Locale for output (e.g., fr, es). Non-English exposes hardcoded strings.",
    )
    sim_parser.add_argument(
        "--validate-keybinds",
        "-k",
        action="store_true",
        help="Validate keybind action IDs and run smoke tests after game",
    )
    sim_parser.add_argument(
        "--clip",
        action="store_true",
        help="Copy all output to clipboard on completion",
    )

    # bootstrap-owner command
    bootstrap_parser = subparsers.add_parser(
        "bootstrap-owner",
        help="Create or update the initial server owner account",
    )
    bootstrap_parser.add_argument(
        "--username",
        required=True,
        help="Username for the server owner account",
    )
    bootstrap_parser.add_argument(
        "--password",
        help="Password for the server owner (use with caution; prefer --password-file or interactive prompt)",
    )
    bootstrap_parser.add_argument(
        "--password-file",
        help="File containing the password (first line used)",
    )
    bootstrap_parser.add_argument(
        "--password-stdin",
        action="store_true",
        help="Read password from stdin (useful for automation)",
    )
    bootstrap_parser.add_argument(
        "--db-path",
        default="playpalace.db",
        help="Path to the server database (default resolves to var/server/playpalace.db)",
    )
    bootstrap_parser.add_argument(
        "--locale",
        default="en",
        help="Locale to assign to the owner account (default: en)",
    )
    bootstrap_parser.add_argument(
        "--force",
        action="store_true",
        help="Allow operation when users already exist or when replacing an account",
    )
    bootstrap_parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress success output (useful for CI)",
    )

    args = parser.parse_args()

    if args.command == "list-games":
        cmd_list_games(args)
    elif args.command == "show-options":
        cmd_show_options(args)
    elif args.command == "simulate":
        cmd_simulate(args)
    elif args.command == "bootstrap-owner":
        cmd_bootstrap_owner(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
