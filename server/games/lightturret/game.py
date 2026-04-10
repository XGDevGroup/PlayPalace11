"""
Light Turret Game Implementation for PlayPalace v11.

A resource management game where you shoot a turret to gain light and coins.
"""

from dataclasses import dataclass, field
from datetime import datetime
import random

from ..base import Game, Player
from ..registry import register_game
from ...game_utils.actions import Action, ActionSet, Visibility
from ...game_utils.bot_helper import BotHelper
from ...game_utils.game_result import GameResult, PlayerResult
from ...game_utils.options import IntOption, option_field, GameOptions
from ...messages.localization import Localization
from ...game_utils.game_status import GameStatus
from server.core.ui.keybinds import KeybindState


@dataclass
class LightTurretPlayer(Player):
    """Player state for Light Turret game."""

    power: int = 10  # Maximum light before elimination
    light: int = 0  # Current accumulated light
    coins: int = 0  # Currency for upgrades
    alive: bool = True  # Whether player is still in the game


@dataclass
class LightTurretOptions(GameOptions):
    """Options for Light Turret game."""

    starting_power: int = option_field(
        IntOption(
            default=10,
            min_val=5,
            max_val=30,
            value_key="power",
            label="lightturret-set-starting-power",
            prompt="lightturret-enter-starting-power",
            change_msg="lightturret-option-changed-power",
            description="lightturret-desc-starting-power",
        )
    )
    max_rounds: int = option_field(
        IntOption(
            default=50,
            min_val=10,
            max_val=200,
            value_key="rounds",
            label="lightturret-set-max-rounds",
            prompt="lightturret-enter-max-rounds",
            change_msg="lightturret-option-changed-rounds",
        )
    )


@dataclass
@register_game
class LightTurretGame(Game):
    """
    Light Turret game.

    Players take turns shooting a turret to gain light and coins.
    If a player's light exceeds their power, they are eliminated.
    Players can buy upgrades to increase power, but there's a 25% chance
    the upgrade backfires and adds light instead.
    The player with the most light at the end wins.
    """

    players: list[LightTurretPlayer] = field(default_factory=list)
    options: LightTurretOptions = field(default_factory=LightTurretOptions)

    # Flag to delay finish_game until sounds complete
    _pending_finish: bool = field(default=False, repr=False)

    @classmethod
    def get_name(cls) -> str:
        return "Light Turret"

    @classmethod
    def get_type(cls) -> str:
        return "lightturret"

    @classmethod
    def get_category(cls) -> str:
        return "category-rb-play-center"

    @classmethod
    def get_min_players(cls) -> int:
        return 2

    @classmethod
    def get_max_players(cls) -> int:
        return 4

    def create_player(self, player_id: str, name: str, is_bot: bool = False) -> LightTurretPlayer:
        """Create a new player with Light Turret-specific state."""
        return LightTurretPlayer(id=player_id, name=name, is_bot=is_bot)

    def create_turn_action_set(self, player: LightTurretPlayer) -> ActionSet:
        """Create the turn action set for a player."""
        user = self.get_user(player)
        locale = user.locale if user else "en"

        action_set = ActionSet(name="turn")
        action_set.add(
            Action(
                id="shoot",
                label=Localization.get(locale, "lightturret-shoot"),
                handler="_action_shoot",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="upgrade",
                label=Localization.get(locale, "lightturret-upgrade"),
                handler="_action_upgrade",
                is_enabled="_is_turn_action_enabled",
                is_hidden="_is_turn_action_hidden",
            )
        )
        action_set.add(
            Action(
                id="check_stats",
                label=Localization.get(locale, "lightturret-check-stats"),
                handler="_action_check_stats",
                is_enabled="_is_check_stats_enabled",
                is_hidden="_is_check_stats_hidden",
            )
        )
        return action_set

    def setup_keybinds(self) -> None:
        """Define all keybinds for the game."""
        super().setup_keybinds()

        # Turn action keybinds
        self.define_keybind("space", "Shoot turret", ["shoot"], state=KeybindState.ACTIVE)
        self.define_keybind("u", "Buy upgrade", ["upgrade"], state=KeybindState.ACTIVE)
        self.define_keybind(
            "c",
            "Check stats",
            ["check_stats"],
            state=KeybindState.ACTIVE,
            include_spectators=True,
        )

    # ==========================================================================
    # Declarative Action Callbacks
    # ==========================================================================

    def _is_turn_action_enabled(self, player: Player) -> str | None:
        """Check if turn actions (shoot/upgrade) are enabled."""
        if self.status != "playing":
            return "action-not-playing"
        if self.current_player != player:
            return "action-not-your-turn"
        if player.is_spectator:
            return "action-spectator"
        lt_player: LightTurretPlayer = player  # type: ignore
        if not lt_player.alive:
            return "lightturret-you-are-eliminated"
        return None

    def _is_turn_action_hidden(self, player: Player) -> Visibility:
        """Check if turn actions are hidden."""
        if self.status != "playing":
            return Visibility.HIDDEN
        if self.current_player != player:
            return Visibility.HIDDEN
        lt_player: LightTurretPlayer = player  # type: ignore
        if not lt_player.alive:
            return Visibility.HIDDEN
        return Visibility.VISIBLE

    def _is_check_stats_enabled(self, player: Player) -> str | None:
        """Check if check stats action is enabled."""
        if self.status != "playing":
            return "action-not-playing"
        return None

    def _is_check_stats_hidden(self, player: Player) -> Visibility:
        """Check stats is always hidden (keybind only)."""
        return Visibility.HIDDEN

    def _action_shoot(self, player: Player, action_id: str) -> None:
        """Handle shooting the turret."""
        lt_player = player
        if not isinstance(lt_player, LightTurretPlayer) or not lt_player.alive:
            return

        # Play shoot sound
        shoot_sound = f"game_lightturret/shoot{random.randint(1, 3)}.ogg"  # nosec B311
        self.play_sound(shoot_sound)

        # Gain light and coins
        gain = random.randint(1, 4)  # nosec B311
        lt_player.light += gain
        lt_player.coins += gain * 2
        self._team_manager.add_to_team_score(player.name, gain)

        self.broadcast_l(
            "lightturret-shoot-result",
            player=player.name,
            gain=gain,
            light=lt_player.light,
        )
        self.broadcast_l(
            "lightturret-coins-gained",
            player=player.name,
            coins=gain * 2,
            total=lt_player.coins,
        )

        # Check for elimination - schedule explosion sound after delay
        if lt_player.light > lt_player.power:
            self.schedule_sound("game_lightturret/overpowered.ogg", delay_ticks=5)
            self._eliminate_player(lt_player)

        self.end_turn()

    def _action_upgrade(self, player: Player, action_id: str) -> None:
        """Handle buying an upgrade."""
        lt_player = player
        if not isinstance(lt_player, LightTurretPlayer) or not lt_player.alive:
            return

        # Check if player has enough coins
        if lt_player.coins < 10:
            user = self.get_user(player)
            if user:
                user.speak_l("lightturret-not-enough-coins", have=lt_player.coins, need=10)
            return

        # Deduct coins
        lt_player.coins -= 10
        self.play_sound("game_lightturret/upgrade.ogg")
        self.broadcast_l("lightturret-buys-upgrade", player=player.name)

        # 25% chance of accident
        if random.randint(0, 3) == 3:  # nosec B311
            # Accident - upgrade infuses with turret
            accident_light = random.randint(1, 5)  # nosec B311
            lt_player.light += accident_light
            self._team_manager.add_to_team_score(player.name, accident_light)
            # Schedule merge sound after delay (5 ticks = 250ms)
            self.schedule_sound("game_lightturret/upgrademerge.ogg", delay_ticks=5)
            self.broadcast_l("lightturret-upgrade-accident", light=lt_player.light)

            # Check for elimination - schedule explosion at same time as merge
            if lt_player.light > lt_player.power:
                self.schedule_sound("game_lightturret/overpowered.ogg", delay_ticks=5)
                self._eliminate_player(lt_player)
        else:
            # Normal upgrade
            power_gain = random.randint(2, 8)  # nosec B311
            lt_player.power += power_gain
            self.broadcast_l(
                "lightturret-power-gained",
                player=player.name,
                gain=power_gain,
                power=lt_player.power,
            )

        self.end_turn()

    def _action_check_stats(self, player: Player, action_id: str) -> None:
        """Show stats for all players."""
        user = self.get_user(player)
        if not user:
            return

        for p in self.players:
            if isinstance(p, LightTurretPlayer):
                if p.alive:
                    user.speak_l(
                        "lightturret-stats-alive",
                        player=p.name,
                        power=p.power,
                        light=p.light,
                        coins=p.coins,
                    )
                else:
                    user.speak_l("lightturret-stats-eliminated", player=p.name, light=p.light)

    def _eliminate_player(self, player: LightTurretPlayer) -> None:
        """Eliminate a player from the game. Sound is scheduled by caller."""
        self.broadcast_l("lightturret-eliminated", player=player.name)
        player.alive = False

    def on_start(self) -> None:
        """Called when the game starts."""
        self.status = GameStatus.PLAYING
        self.game_active = True
        self.round = 0

        # Initialize players with starting power
        active_players = self.get_active_players()
        for player in active_players:
            if isinstance(player, LightTurretPlayer):
                player.power = self.options.starting_power
                player.light = 0
                player.coins = 0
                player.alive = True

        # Initialize turn order
        self.set_turn_players(active_players)

        # Set up TeamManager for score tracking (light totals)
        self._team_manager.team_mode = "individual"
        self._team_manager.setup_teams([p.name for p in active_players])
        self._team_manager.reset_all_scores()

        # Play music and intro sound
        self.play_music("game_lightturret/music.ogg")
        self.play_sound("game_3cardpoker/roundstart.ogg")

        # Game intro
        self.broadcast_l("lightturret-intro", power=self.options.starting_power)

        # Start first round
        self._start_round()

    def _start_round(self) -> None:
        """Start a new round."""
        self.round += 1

        # Refresh turn order to only include alive players
        alive_players = [
            p for p in self.get_active_players() if isinstance(p, LightTurretPlayer) and p.alive
        ]
        self.set_turn_players(alive_players)

        self._start_turn()

    def _start_turn(self) -> None:
        """Start a player's turn."""
        player = self.current_player
        if not player:
            # No more alive players
            self._end_game()
            return

        # Skip eliminated players (shouldn't happen normally due to turn order filtering)
        if isinstance(player, LightTurretPlayer) and not player.alive:
            self._on_turn_end()
            return

        # Announce turn
        self.announce_turn()

        if player.is_bot:
            BotHelper.jolt_bot(player, ticks=random.randint(12, 20))  # nosec B311

        self.rebuild_all_menus()

    def on_tick(self) -> None:
        """Called every tick. Handle bot AI and scheduled sounds."""
        super().on_tick()

        # Check if we're waiting to finish after sounds complete
        if self._pending_finish and not self.scheduled_sounds:
            self._pending_finish = False
            self.game_active = False
            self.finish_game(show_end_screen=False)
            return

        # Don't process bots if game is finished or inactive
        if not self.game_active or self.status == "finished":
            return
        BotHelper.on_tick(self)

    def bot_think(self, player: Player) -> str | None:
        """Bot AI decision making."""
        if not isinstance(player, LightTurretPlayer) or not player.alive:
            return None

        # AI: buy upgrade if coins >= 10 and close to capacity
        if player.coins >= 10 and (player.power - player.light) <= 4:
            return "upgrade"
        else:
            return "shoot"

    def _on_turn_end(self) -> None:
        """Handle end of a player's turn."""
        # Check for game end conditions
        winner = self._check_for_winner()
        if winner is not None:
            self._end_game()
            return

        # Check if round is over
        if self.turn_index >= len(self.turn_players) - 1:
            self._start_round()
        else:
            self.advance_turn(announce=False)
            self._start_turn()

    def _check_for_winner(self) -> LightTurretPlayer | None:
        """Check if the game should end."""
        # Check max rounds
        if self.round >= self.options.max_rounds:
            return self._find_light_winner()

        # Check if ALL players are eliminated (game ends)
        # Exclude spectators from the count
        alive_count = sum(
            1
            for p in self.players
            if isinstance(p, LightTurretPlayer) and p.alive and not p.is_spectator
        )
        if alive_count == 0:
            return self._find_light_winner()

        return None

    def _find_light_winner(self) -> LightTurretPlayer | None:
        """Find the player with the most light."""
        max_light = 0
        winner = None
        for p in self.players:
            if isinstance(p, LightTurretPlayer) and not p.is_spectator and p.light > max_light:
                max_light = p.light
                winner = p
        return winner

    def _end_game(self) -> None:
        """End the game and announce results."""
        # Mark status as finished to disable turn actions, but keep game_active
        # True until sounds finish playing (so ticks continue)
        self.status = GameStatus.FINISHED

        self.broadcast_l("lightturret-game-over")

        # Find max light and count winners
        max_light = 0
        winners = []
        for p in self.players:
            if not isinstance(p, LightTurretPlayer) or p.is_spectator:
                continue
            # Announce each player's result
            if p.alive:
                self.broadcast_l("lightturret-final-alive", player=p.name, light=p.light)
            else:
                self.broadcast_l("lightturret-final-eliminated", player=p.name, light=p.light)

            if p.light > max_light:
                max_light = p.light
                winners = [p]
            elif p.light == max_light:
                winners.append(p)

        # Announce winner or tie
        if len(winners) > 1:
            self.broadcast_l("lightturret-tie", light=max_light)
        elif len(winners) == 1:
            self.play_sound("game_pig/win.ogg")
            self.broadcast_l("lightturret-winner", player=winners[0].name, light=max_light)

        # Update actions to reflect game ended state
        self.rebuild_all_menus()

        # Show final menu first (before potential destruction)
        result = self.build_game_result()
        self._show_end_screen(result)

        # Delay final cleanup if sounds are pending
        if self.scheduled_sounds:
            self._pending_finish = True
            # Keep game_active = True so ticks continue and sounds play
        else:
            self.game_active = False
            self.finish_game(show_end_screen=False)

    def build_game_result(self) -> GameResult:
        """Build the game result with LightTurret-specific data."""
        sorted_players = sorted(
            [p for p in self.players if isinstance(p, LightTurretPlayer) and not p.is_spectator],
            key=lambda p: p.light,
            reverse=True,
        )

        # Build final light values
        final_light = {}
        alive_status = {}
        for p in sorted_players:
            final_light[p.name] = p.light
            alive_status[p.name] = p.alive

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
                for p in sorted_players
            ],
            custom_data={
                "winner_name": winner.name if winner else None,
                "winner_light": winner.light if winner else 0,
                "final_light": final_light,
                "alive_status": alive_status,
                "rounds_played": self.round,
            },
        )

    def format_end_screen(self, result: GameResult, locale: str) -> list[str]:
        """Format the end screen for LightTurret game."""
        lines = [Localization.get(locale, "game-final-scores")]

        final_light = result.custom_data.get("final_light", {})
        alive_status = result.custom_data.get("alive_status", {})

        for i, (name, light) in enumerate(final_light.items(), 1):
            status = "" if alive_status.get(name, True) else " (eliminated)"
            lines.append(f"{i}. {name}: {light} light{status}")

        return lines

    def end_turn(self, jolt_min: int = 15, jolt_max: int = 25) -> None:
        """End the current player's turn."""
        BotHelper.jolt_bots(self, ticks=random.randint(jolt_min, jolt_max))  # nosec B311
        self._on_turn_end()
