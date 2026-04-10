"""
Reusable team management utility for team-based games.

Provides Team dataclass and TeamManager for handling team assignments,
scoring, and elimination (for inverse game modes).
"""

from collections import OrderedDict
from collections.abc import Mapping
from dataclasses import dataclass, field
from mashumaro.mixins.json import DataClassJSONMixin

from ..messages.localization import Localization


@dataclass
class Team(DataClassJSONMixin):
    """Team container for team-based games.

    Attributes:
        index: Team index (0-based).
        members: Player names on the team.
        round_score: Points earned this round.
        total_score: Total points across rounds.
        eliminated: True if eliminated (inverse modes).
    """

    index: int  # Team number (0-based)
    members: list[str] = field(default_factory=list)  # Player names
    round_score: int = 0  # Points earned this round
    total_score: int = 0  # Total points across rounds
    eliminated: bool = False  # For inverse mode


@dataclass
class TeamManager(DataClassJSONMixin):
    """Manage team assignments and scoring for games.

    Supports individual mode (teams of 1) and common team configurations
    like 2v2, 3v3, 2v2v2, etc.
    """

    teams: list[Team] = field(default_factory=list)
    team_mode: str = "individual"  # "individual", "2v2", "3v3", "2v2v2", etc.
    _player_to_team: dict[str, int] = field(default_factory=dict)

    def setup_teams(self, player_names: list[str]) -> None:
        """
        Create teams based on team_mode and assign players.

        Args:
            player_names: List of player names to assign to teams.
        """
        self.teams = []
        self._player_to_team = {}

        if self.team_mode == "individual":
            # Each player is their own team
            for i, name in enumerate(player_names):
                team = Team(index=i, members=[name])
                self.teams.append(team)
                self._player_to_team[name] = i
        else:
            # Parse team mode like "2v2", "3v3", "2v2v2"
            team_sizes = self._parse_team_mode(self.team_mode)
            num_teams = len(team_sizes)

            # Create empty teams
            team_members: list[list[str]] = [[] for _ in range(num_teams)]

            # Round-robin assignment: player 0 -> team 0, player 1 -> team 1, etc.
            for player_idx, name in enumerate(player_names):
                team_idx = player_idx % num_teams
                team_members[team_idx].append(name)
                self._player_to_team[name] = team_idx

            # Create team objects
            for team_idx, members in enumerate(team_members):
                team = Team(index=team_idx, members=members)
                self.teams.append(team)

    def _parse_team_mode(self, mode: str) -> list[int]:
        """
        Parse a team mode string into list of team sizes.

        Examples:
            "2v2" -> [2, 2]
            "3v3" -> [3, 3]
            "2v2v2" -> [2, 2, 2]
            "2v3" -> [2, 3]
        """
        if mode == "individual":
            return []
        parts = mode.lower().split("v")
        return [int(p) for p in parts if p.isdigit()]

    def get_team(self, player_name: str) -> Team | None:
        """Get the team a player belongs to."""
        team_idx = self._player_to_team.get(player_name)
        if team_idx is not None and team_idx < len(self.teams):
            return self.teams[team_idx]
        return None

    def get_team_index(self, player_name: str) -> int:
        """Get the team index for a player (0 if not found)."""
        return self._player_to_team.get(player_name, 0)

    def get_teammates(self, player_name: str) -> list[str]:
        """Get names of player's teammates (excluding self)."""
        team = self.get_team(player_name)
        if team:
            return [m for m in team.members if m != player_name]
        return []

    def get_team_members(self, player_name: str) -> list[str]:
        """Get names of all players on the same team (including self)."""
        team = self.get_team(player_name)
        if team:
            return list(team.members)
        return [player_name]

    def add_to_team_score(self, player_name: str, points: int) -> None:
        """Add points to a player's team total score."""
        team = self.get_team(player_name)
        if team:
            team.total_score += points

    def add_to_team_round_score(self, player_name: str, points: int) -> None:
        """Add points to a player's team round score."""
        team = self.get_team(player_name)
        if team:
            team.round_score += points

    def commit_round_scores(self) -> None:
        """Add all round scores to total scores and reset round scores."""
        for team in self.teams:
            team.total_score += team.round_score
            team.round_score = 0

    def reset_round_scores(self) -> None:
        """Reset all team round scores to 0."""
        for team in self.teams:
            team.round_score = 0

    def reset_all_scores(self) -> None:
        """Reset all team scores to 0."""
        for team in self.teams:
            team.round_score = 0
            team.total_score = 0
            team.eliminated = False

    def get_alive_teams(self) -> list[Team]:
        """Get non-eliminated teams (for inverse mode)."""
        return [t for t in self.teams if not t.eliminated]

    def eliminate_team(self, team: Team) -> None:
        """Mark a team as eliminated."""
        team.eliminated = True

    def eliminate_by_player(self, player_name: str) -> None:
        """Eliminate the team that contains the given player."""
        team = self.get_team(player_name)
        if team:
            team.eliminated = True

    def is_team_eliminated(self, player_name: str) -> bool:
        """Check if a player's team is eliminated."""
        team = self.get_team(player_name)
        return team.eliminated if team else False

    def get_teams_at_or_above_score(self, target: int) -> list[Team]:
        """Get all teams that have reached or exceeded the target score."""
        return [t for t in self.teams if t.total_score >= target]

    def get_leading_team(self) -> Team | None:
        """Get the team with the highest total score."""
        if not self.teams:
            return None
        return max(self.teams, key=lambda t: t.total_score)

    def get_team_name(self, team: Team, locale: str = "en") -> str:
        """
        Get a display name for a team.

        For individual mode, returns the player name.
        For team mode, returns "Team N" or lists members.
        """
        if self.team_mode == "individual" and team.members:
            return team.members[0]
        if len(team.members) == 1:
            return team.members[0]
        # For actual teams, could use localization
        return f"Team {team.index + 1}"

    def get_sorted_teams(self, by_score: bool = True, descending: bool = True) -> list[Team]:
        """
        Get teams sorted by score or index.

        Args:
            by_score: If True, sort by total_score. Otherwise by index.
            descending: If True, highest first.
        """
        key = (lambda t: t.total_score) if by_score else (lambda t: t.index)
        return sorted(self.teams, key=key, reverse=descending)

    @staticmethod
    def format_team_mode_for_display(mode: str, locale: str = "en") -> str:
        """
        Convert internal team mode format to user-friendly localized display format.

        Examples:
            "individual" -> "Individual" (en) / "Individual" (pt) / "个人" (zh)
            "2v2" -> "2 teams of 2" (en) / "2 equipes de 2" (pt) / "2 个 2 人团队" (zh)
            "3v3" -> "2 teams of 3"
            "2v2v2" -> "3 teams of 2"
            "2v2v2v2" -> "4 teams of 2"

        Args:
            mode: Internal team mode string.
            locale: Language code for localization (default: "en").

        Returns:
            User-friendly localized display string.
        """
        if mode == "individual":
            return Localization.get(locale, "game-team-mode-individual")

        # Parse the mode
        parts = mode.lower().split("v")
        team_sizes = [int(p) for p in parts if p.isdigit()]

        if not team_sizes:
            return mode  # Fallback

        # Check if all teams are the same size
        if len(set(team_sizes)) == 1:
            # Symmetric teams
            num_teams = len(team_sizes)
            team_size = team_sizes[0]
            return Localization.get(
                locale,
                "game-team-mode-x-teams-of-y",
                num_teams=num_teams,
                team_size=team_size,
            )
        else:
            # Asymmetric teams (future support)
            return "v".join(str(s) for s in team_sizes)

    @staticmethod
    def parse_display_to_team_mode(display: str) -> str:
        """
        Convert user-friendly display format to internal team mode format.

        Works with localized strings by extracting numbers from patterns like:
        - "Individual" / "个人" -> "individual"
        - "2 teams of 2" / "2 equipes de 2" / "2 个 2 人团队" -> "2v2"
        - "3 teams of 2" -> "2v2v2"
        - "4 teams of 2" -> "2v2v2v2"

        Args:
            display: User-friendly display string (possibly localized).

        Returns:
            Internal team mode string.
        """
        import re

        # Check for "Individual" in any language by checking if it's a known individual string
        # We'll check against the English version and also check if there are no digits
        if "individual" in display.lower() or not any(char.isdigit() for char in display):
            # If it looks like individual mode (no numbers), return individual
            # This handles "Individual", "个人", etc.
            return "individual"

        # Extract all numbers from the display string
        numbers = re.findall(r"\d+", display)

        if len(numbers) >= 2:
            # Format: "N teams of M" or localized equivalent
            num_teams = int(numbers[0])
            team_size = int(numbers[1])
            return "v".join([str(team_size)] * num_teams)

        # If it doesn't match expected patterns, assume it's already in internal format
        return display

    @staticmethod
    def get_team_modes_for_player_count_internal(num_players: int) -> list[str]:
        """
        Get valid team mode options for a given number of players.
        Returns internal format strings.

        Args:
            num_players: Number of players in the game.

        Returns:
            List of valid team mode strings in internal format.
        """
        modes = ["individual"]

        if num_players < 2:
            return modes

        # Generate symmetric team modes (2v2, 3v3, etc.)
        for team_size in range(2, num_players // 2 + 1):
            num_teams = num_players // team_size
            if num_teams >= 2 and num_teams * team_size == num_players:
                mode = "v".join([str(team_size)] * num_teams)
                modes.append(mode)

        # Could add asymmetric modes like "2v3" for 5 players
        # but keeping it simple for now

        return modes

    @staticmethod
    def get_team_modes_for_player_count(num_players: int, locale: str = "en") -> list[str]:
        """
        Get valid team mode options for a given number of players.
        Returns localized display strings.

        Args:
            num_players: Number of players in the game.
            locale: Language code for localization (default: "en").

        Returns:
            List of valid team mode strings in user-friendly localized format.
        """
        internal_modes = TeamManager.get_team_modes_for_player_count_internal(num_players)
        return [TeamManager.format_team_mode_for_display(mode, locale) for mode in internal_modes]

    @staticmethod
    def get_all_team_modes(min_players: int, max_players: int) -> list[str]:
        """
        Get all possible team mode options for a range of player counts.
        Returns internal format strings.

        Args:
            min_players: Minimum number of players.
            max_players: Maximum number of players.

        Returns:
            Sorted list of unique team mode strings in internal format.
        """
        all_modes = set()
        for count in range(min_players, max_players + 1):
            modes = TeamManager.get_team_modes_for_player_count_internal(count)
            all_modes.update(modes)

        # Sort: individual first, then by total players, then alphabetically
        def sort_key(mode: str) -> tuple:
            """Sort key for team modes (individual first, then size)."""
            if mode == "individual":
                return (0, 0, "")
            parts = mode.split("v")
            total = sum(int(p) for p in parts if p.isdigit())
            return (1, total, mode)

        return sorted(all_modes, key=sort_key)

    @staticmethod
    def get_all_team_modes_for_display(
        min_players: int, max_players: int, locale: str = "en"
    ) -> list[tuple[str, str]]:
        """
        Get all possible team mode options for a range of player counts.
        Returns (display_string, internal_value) tuples for UI.

        Args:
            min_players: Minimum number of players.
            max_players: Maximum number of players.
            locale: Language code for localization (default: "en").

        Returns:
            List of (display, value) tuples sorted by internal value.
        """
        internal_modes = TeamManager.get_all_team_modes(min_players, max_players)
        return [
            (TeamManager.format_team_mode_for_display(mode, locale), mode)
            for mode in internal_modes
        ]

    @staticmethod
    def is_valid_team_mode(team_mode: str, num_players: int) -> bool:
        """
        Check if a team mode is valid for the given number of players.

        Args:
            team_mode: Internal team mode string (e.g., "individual", "2v2").
            num_players: Number of players in the game.

        Returns:
            True if the team mode is valid for the player count, False otherwise.
        """
        valid_modes = TeamManager.get_team_modes_for_player_count_internal(num_players)
        return team_mode in valid_modes

    # ==========================================================================
    # Score Formatting
    # ==========================================================================

    def format_scores_brief(self, locale: str = "en") -> str:
        """
        Format scores as a brief single-line string for speaking.

        Returns something like: "Alice: 5. Bob: 3. Charlie: 1."
        """
        sorted_teams = self.get_sorted_teams(by_score=True, descending=True)
        parts = []
        for team in sorted_teams:
            name = self.get_team_name(team, locale)
            parts.append(f"{name}: {team.total_score}")
        return ". ".join(parts) + "."

    def format_scores_detailed(self, locale: str = "en") -> list[str]:
        """
        Format localized scores as a list of lines for a status box.

        Returns something like (English):
        ["Alice: 5 points", "Bob: 3 points", ...]

        The points label is localized via the "game-points" Fluent key.
        No header needed - screen readers speak list items directly.
        """
        sorted_teams = self.get_sorted_teams(by_score=True, descending=True)
        lines = []
        for team in sorted_teams:
            name = self.get_team_name(team, locale)
            points = Localization.get(locale, "game-points", count=team.total_score)
            lines.append(f"{name}: {points}")
        return lines


class TeamResultBuilder:
    """Helpers for summarizing and formatting team-based results."""

    @staticmethod
    def summarize(team_manager: TeamManager):
        """Return (sorted_teams, winner, ordered final_scores dict)."""
        sorted_teams = team_manager.get_sorted_teams(by_score=True, descending=True)
        winner = sorted_teams[0] if sorted_teams else None
        final_scores: OrderedDict[str, int] = OrderedDict()
        for team in sorted_teams:
            name = team_manager.get_team_name(team)
            final_scores[name] = team.total_score
        return sorted_teams, winner, final_scores

    @staticmethod
    def format_final_scores(locale: str, final_scores: Mapping[str, int]) -> list[str]:
        """Format localized final score lines."""
        lines = [Localization.get(locale, "game-final-scores")]
        for index, (name, score) in enumerate(final_scores.items(), 1):
            points = Localization.get(locale, "game-points", count=score)
            lines.append(f"{index}. {name}: {points}")
        return lines


__all__ = ["Team", "TeamManager", "TeamResultBuilder"]
