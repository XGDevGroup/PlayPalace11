"""Deterministic cheaters-rule engine for Monopoly cheaters preset."""

from __future__ import annotations

from dataclasses import dataclass, field

from .cheaters_profile import CheatersProfile


@dataclass(frozen=True)
class CheaterOutcome:
    """Outcome payload returned by cheaters engine hooks."""

    status: str = "allow"
    cash_delta: int = 0
    message_key: str = ""
    reason_code: str = ""


@dataclass
class _PlayerTurnState:
    """Per-player per-turn engine state."""

    turn_index: int = -1
    strike_count: int = 0
    reward_claimed: bool = False


@dataclass
class CheatersEngine:
    """Deterministic rule evaluator for anchor-backed cheaters mechanics."""

    profile: CheatersProfile
    _state_by_player_id: dict[str, _PlayerTurnState] = field(default_factory=dict)

    def on_turn_start(self, player_id: str, turn_index: int) -> None:
        """Reset per-turn detector state for player."""
        self._state_by_player_id[player_id] = _PlayerTurnState(
            turn_index=turn_index,
            strike_count=0,
            reward_claimed=False,
        )

    def _state_for(self, player_id: str) -> _PlayerTurnState:
        if player_id not in self._state_by_player_id:
            self._state_by_player_id[player_id] = _PlayerTurnState()
        return self._state_by_player_id[player_id]

    def on_action_attempt(self, player_id: str, action_id: str, context: dict | None = None) -> CheaterOutcome:
        """Evaluate generic action attempt for optional rule paths."""
        _ = context
        if action_id == "claim_cheat_reward" and "reward_claim" in self.profile.enabled_rules:
            state = self._state_for(player_id)
            if state.reward_claimed:
                return CheaterOutcome(
                    status="block",
                    message_key="monopoly-cheaters-reward-unavailable",
                    reason_code="reward_already_claimed",
                )
            reward = max(0, self.profile.reward_amounts.get("reward_claim", 0))
            if reward > 0:
                state.reward_claimed = True
                return CheaterOutcome(
                    status="reward",
                    cash_delta=reward,
                    message_key="monopoly-cheaters-reward-granted",
                    reason_code="reward_claim",
                )
        return CheaterOutcome(status="allow")

    def on_payment_required(
        self,
        player_id: str,
        reason: str,
        amount: int,
        context: dict | None = None,
    ) -> CheaterOutcome:
        """Record payment-required checkpoints."""
        _ = (player_id, reason, amount, context)
        return CheaterOutcome(status="allow")

    def on_payment_result(
        self,
        player_id: str,
        paid: int,
        required: int,
        context: dict | None = None,
    ) -> CheaterOutcome:
        """Evaluate payment completion results for avoidance behavior."""
        _ = context
        if "payment_avoidance" not in self.profile.enabled_rules:
            return CheaterOutcome(status="allow")
        if required <= 0 or paid >= required:
            return CheaterOutcome(status="allow")

        state = self._state_for(player_id)
        state.strike_count += 1
        penalty_key = "payment_avoidance"
        reason_code = penalty_key
        if state.strike_count >= self.profile.escalation_threshold:
            penalty_key = "escalated_repeat_violation"
            reason_code = penalty_key
        penalty = max(0, self.profile.penalty_amounts.get(penalty_key, 0))
        return CheaterOutcome(
            status="penalty",
            cash_delta=-penalty,
            message_key="monopoly-cheaters-payment-avoidance-blocked",
            reason_code=reason_code,
        )

    def on_turn_end_attempt(self, player_id: str, context: dict | None = None) -> CheaterOutcome:
        """Evaluate end-turn cheating attempts."""
        if "early_end_turn" not in self.profile.enabled_rules:
            return CheaterOutcome(status="allow")

        turn_has_rolled = bool((context or {}).get("turn_has_rolled", False))
        if turn_has_rolled:
            return CheaterOutcome(status="allow")

        state = self._state_for(player_id)
        state.strike_count += 1
        penalty_key = "early_end_turn"
        reason_code = penalty_key
        if state.strike_count >= self.profile.escalation_threshold:
            penalty_key = "escalated_repeat_violation"
            reason_code = penalty_key

        penalty = max(0, self.profile.penalty_amounts.get(penalty_key, 0))
        return CheaterOutcome(
            status="penalty",
            cash_delta=-penalty,
            message_key="monopoly-cheaters-early-end-turn-blocked",
            reason_code=reason_code,
        )
