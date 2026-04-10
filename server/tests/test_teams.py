"""Tests for TeamManager."""
import json

from server.game_utils.teams import TeamManager, Team


class TestTeamSetup:
    def test_individual_mode(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice", "Bob", "Carol"])
        assert len(tm.teams) == 3
        assert tm.teams[0].members == ["Alice"]
        assert tm.teams[1].members == ["Bob"]
        assert tm.teams[2].members == ["Carol"]

    def test_2v2_mode(self):
        tm = TeamManager(team_mode="2v2")
        tm.setup_teams(["Alice", "Bob", "Carol", "Dave"])
        assert len(tm.teams) == 2
        assert "Alice" in tm.teams[0].members
        assert "Carol" in tm.teams[0].members
        assert "Bob" in tm.teams[1].members
        assert "Dave" in tm.teams[1].members

    def test_2v2v2_mode(self):
        tm = TeamManager(team_mode="2v2v2")
        tm.setup_teams(["A", "B", "C", "D", "E", "F"])
        assert len(tm.teams) == 3
        for team in tm.teams:
            assert len(team.members) == 2

    def test_get_team(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice", "Bob"])
        team = tm.get_team("Alice")
        assert team is not None
        assert "Alice" in team.members

    def test_get_teammates(self):
        tm = TeamManager(team_mode="2v2")
        tm.setup_teams(["Alice", "Bob", "Carol", "Dave"])
        assert tm.get_teammates("Alice") == ["Carol"]


class TestTeamScoring:
    def test_add_score(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice", "Bob"])
        tm.add_to_team_score("Alice", 10)
        team = tm.get_team("Alice")
        assert team.total_score == 10
        bob_team = tm.get_team("Bob")
        assert bob_team.total_score == 0

    def test_add_round_score(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice"])
        tm.add_to_team_round_score("Alice", 5)
        assert tm.teams[0].round_score == 5

    def test_reset_round_scores(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice"])
        tm.add_to_team_round_score("Alice", 5)
        tm.reset_round_scores()
        assert tm.teams[0].round_score == 0


class TestTeamElimination:
    def test_eliminate_team(self):
        tm = TeamManager(team_mode="individual")
        tm.setup_teams(["Alice", "Bob", "Carol"])
        team = tm.get_team("Alice")
        team.eliminated = True
        assert tm.get_alive_teams() == [tm.teams[1], tm.teams[2]]


class TestTeamSerialization:
    def test_round_trip(self):
        tm = TeamManager(team_mode="2v2")
        tm.setup_teams(["Alice", "Bob", "Carol", "Dave"])
        tm.add_to_team_score("Alice", 25)
        json_str = tm.to_json()
        loaded = TeamManager.from_json(json_str)
        assert loaded.team_mode == "2v2"
        assert len(loaded.teams) == 2
        alice_team = loaded.get_team("Alice")
        assert alice_team is not None
        assert alice_team.total_score == 25
