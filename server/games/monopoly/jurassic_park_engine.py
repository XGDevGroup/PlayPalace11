"""Jurassic Park Monopoly engine: T. Rex, fences, property damage, and gate mechanics."""

from __future__ import annotations

import random  # nosec B311
from dataclasses import dataclass, field

from .jurassic_park_profile import JurassicParkProfile

BOARD_SIZE = 40


# ---------------------------------------------------------------------------
# Outcome payloads
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class TRexMoveOutcome:
    """Result of moving the T. Rex one step."""

    old_position: int
    new_position: int
    amber_roll: int
    passed_players: list[str] = field(default_factory=list)
    landed_on_players: list[str] = field(default_factory=list)
    fees_charged: dict[str, int] = field(default_factory=dict)
    property_damaged: str | None = None
    fence_destroyed: str | None = None
    blocked_by_set: str | None = None
    already_damaged: bool = False


@dataclass(frozen=True)
class GateOutcome:
    """Result of activating the Jurassic Park electronic gate."""

    sound: str  # "theme" or "roar"
    payout: int
    method: str  # "gate" or "amber_die"
    amber_roll: int | None = None


@dataclass(frozen=True)
class FenceBuildOutcome:
    """Result of building a fence on a Dino Paddock."""

    status: str  # "built", "error"
    space_id: str = ""
    cost: int = 0
    message_key: str = ""
    reason_code: str = ""


@dataclass(frozen=True)
class RepairOutcome:
    """Result of repairing a damaged property."""

    status: str  # "repaired", "error"
    space_id: str = ""
    cost: int = 0
    message_key: str = ""
    reason_code: str = ""


@dataclass(frozen=True)
class CompleteSetResult:
    """Result of checking/applying complete set immunity."""

    newly_completed: bool = False
    set_group: str = ""
    space_ids: tuple[str, ...] = ()
    auto_repaired: tuple[str, ...] = ()


# ---------------------------------------------------------------------------
# Engine state
# ---------------------------------------------------------------------------

@dataclass
class JurassicParkState:
    """Mutable game state for Jurassic Park mechanics."""

    trex_position: int = 20  # Starts on Free Parking
    damaged_space_ids: set[str] = field(default_factory=set)
    fenced_space_ids: set[str] = field(default_factory=set)
    fences_remaining: int = 24
    complete_set_groups: set[str] = field(default_factory=set)
    all_damaged_game_over: bool = False


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

@dataclass
class JurassicParkEngine:
    """Deterministic rule evaluator for Jurassic Park Monopoly mechanics.

    The engine manages T. Rex movement, property damage, fences, electronic
    gate resolution, and complete set immunity.  It does NOT manage player
    cash or turn flow directly; the main game class calls engine hooks and
    applies the returned outcome payloads to authoritative game state.
    """

    profile: JurassicParkProfile
    state: JurassicParkState = field(default_factory=JurassicParkState)

    # -- Board data loaded at game start --
    _property_space_ids: list[str] = field(default_factory=list)
    _space_subtype: dict[str, str] = field(default_factory=dict)
    _space_position: dict[str, int] = field(default_factory=dict)
    _position_space: dict[int, str] = field(default_factory=dict)
    _color_groups: dict[str, list[str]] = field(default_factory=dict)
    _fence_costs: dict[str, int] = field(default_factory=dict)
    _repair_costs: dict[str, int] = field(default_factory=dict)

    def init_from_board_data(self, board_data: dict) -> None:
        """Load board data from the jurassic_park.json structure."""
        self.state.trex_position = self.profile.trex_start_position
        self.state.fences_remaining = self.profile.total_fences

        economy = board_data.get("economy", {})
        properties = economy.get("properties", {})
        color_groups = economy.get("color_groups", {})

        self._color_groups = {k: list(v) for k, v in color_groups.items()}

        for space_id, prop in properties.items():
            self._property_space_ids.append(space_id)
            self._space_subtype[space_id] = prop.get("subtype", "")
            self._fence_costs[space_id] = prop.get("fence_cost", 0)
            self._repair_costs[space_id] = prop.get("repair_cost", 0)

        for space in board_data.get("board", {}).get("spaces", []):
            sid = space["space_id"]
            pos = space["position"]
            self._space_position[sid] = pos
            if space.get("kind") == "property":
                self._position_space[pos] = sid

    # -----------------------------------------------------------------
    # T. Rex movement
    # -----------------------------------------------------------------

    def move_trex(
        self,
        amber_roll: int,
        player_positions: dict[str, int],
        property_owners: dict[str, str],
        in_jail: dict[str, bool],
    ) -> TRexMoveOutcome:
        """Move the T. Rex by *amber_roll* spaces clockwise.

        Returns an outcome describing fees, damage, and fence destruction.
        The caller is responsible for applying cash changes.
        """
        old_pos = self.state.trex_position
        passed_players: list[str] = []
        landed_on_players: list[str] = []
        fees: dict[str, int] = {}

        # Move step by step to detect passing players
        for step in range(1, amber_roll + 1):
            check_pos = (old_pos + step) % BOARD_SIZE
            for pid, ppos in player_positions.items():
                if ppos == check_pos:
                    if step < amber_roll:
                        passed_players.append(pid)
                    else:
                        landed_on_players.append(pid)

        new_pos = (old_pos + amber_roll) % BOARD_SIZE
        self.state.trex_position = new_pos

        # Charge fees for players passed or landed on (not in jail)
        for pid in passed_players + landed_on_players:
            if self.profile.trex_no_fee_in_jail and in_jail.get(pid, False):
                continue
            fees[pid] = self.profile.trex_fee

        # Check property damage at landing position
        property_damaged = None
        fence_destroyed = None
        blocked_by_set = None
        already_damaged = False

        space_id = self._position_space.get(new_pos)
        if space_id and space_id in self._property_space_ids:
            result = self._apply_trex_landing(space_id, property_owners)
            property_damaged = result.get("damaged")
            fence_destroyed = result.get("fence_destroyed")
            blocked_by_set = result.get("blocked_by_set")
            already_damaged = result.get("already_damaged", False)

        # Check all-damaged game-over condition
        self._check_all_damaged()

        return TRexMoveOutcome(
            old_position=old_pos,
            new_position=new_pos,
            amber_roll=amber_roll,
            passed_players=passed_players,
            landed_on_players=landed_on_players,
            fees_charged=fees,
            property_damaged=property_damaged,
            fence_destroyed=fence_destroyed,
            blocked_by_set=blocked_by_set,
            already_damaged=already_damaged,
        )

    def _apply_trex_landing(
        self,
        space_id: str,
        property_owners: dict[str, str],
    ) -> dict[str, object]:
        """Apply T. Rex landing rules to a property space."""
        result: dict[str, object] = {}

        # Already damaged: nothing happens
        if space_id in self.state.damaged_space_ids:
            result["already_damaged"] = True
            return result

        # Part of a complete set: immune
        subtype = self._space_subtype.get(space_id, "")
        for group, members in self._color_groups.items():
            if space_id not in members:
                continue
            if group in self.state.complete_set_groups:
                result["blocked_by_set"] = group
                return result

        # Has a fence: fence destroyed, property survives
        if space_id in self.state.fenced_space_ids:
            self.state.fenced_space_ids.discard(space_id)
            # Fence is returned to bank supply
            self.state.fences_remaining = min(
                self.state.fences_remaining + 1,
                self.profile.total_fences,
            )
            result["fence_destroyed"] = space_id
            return result

        # No fence, not in complete set, not already damaged: damaged
        self.state.damaged_space_ids.add(space_id)
        result["damaged"] = space_id
        return result

    def _check_all_damaged(self) -> None:
        """Check if all properties are damaged (game-over condition)."""
        if not self._property_space_ids:
            return
        for sid in self._property_space_ids:
            if sid not in self.state.damaged_space_ids:
                # Check if this property is immune (complete set)
                immune = False
                for group, members in self._color_groups.items():
                    if sid in members and group in self.state.complete_set_groups:
                        immune = True
                        break
                if not immune:
                    return  # At least one damageable property is undamaged
        self.state.all_damaged_game_over = True

    # -----------------------------------------------------------------
    # Property damage & repair
    # -----------------------------------------------------------------

    def is_damaged(self, space_id: str) -> bool:
        """Return True if property is currently damaged."""
        return space_id in self.state.damaged_space_ids

    def repair_property(
        self,
        space_id: str,
        owner_id: str,
        property_owners: dict[str, str],
        player_cash: int,
    ) -> RepairOutcome:
        """Attempt to repair a damaged property.

        Returns outcome; caller applies cash change.
        """
        if space_id not in self.state.damaged_space_ids:
            return RepairOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-repair-not-damaged",
                reason_code="not_damaged",
            )

        if property_owners.get(space_id) != owner_id:
            return RepairOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-repair-not-owner",
                reason_code="not_owner",
            )

        cost = self._repair_costs.get(space_id, 0)
        if player_cash < cost:
            return RepairOutcome(
                status="error",
                space_id=space_id,
                cost=cost,
                message_key="monopoly-not-enough-cash",
                reason_code="insufficient_funds",
            )

        self.state.damaged_space_ids.discard(space_id)
        return RepairOutcome(status="repaired", space_id=space_id, cost=cost)

    def free_repair(self, space_id: str) -> None:
        """Repair a property for free (e.g., from completing a set)."""
        self.state.damaged_space_ids.discard(space_id)

    # -----------------------------------------------------------------
    # Fences
    # -----------------------------------------------------------------

    def has_fence(self, space_id: str) -> bool:
        """Return True if property has a fence."""
        return space_id in self.state.fenced_space_ids

    def build_fence(
        self,
        space_id: str,
        owner_id: str,
        property_owners: dict[str, str],
        player_cash: int,
    ) -> FenceBuildOutcome:
        """Attempt to build a fence on a Dino Paddock.

        Returns outcome; caller applies cash change.
        """
        # Must own the property
        if property_owners.get(space_id) != owner_id:
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-fence-not-owner",
                reason_code="not_owner",
            )

        # Must be a Dino Paddock
        subtype = self._space_subtype.get(space_id, "")
        if subtype != "dino_paddock":
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-fence-not-paddock",
                reason_code="not_dino_paddock",
            )

        # Must own at least one paddock in the same color set
        if self.profile.fences_require_full_set:
            pass  # Not used in JP, but kept for future editions
        else:
            # Just need to own the paddock itself (already checked above)
            pass

        # Already has a fence
        if space_id in self.state.fenced_space_ids:
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-fence-already-built",
                reason_code="already_fenced",
            )

        # Property is damaged - must repair first
        if space_id in self.state.damaged_space_ids:
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-fence-damaged",
                reason_code="property_damaged",
            )

        # No fences left in supply
        if self.state.fences_remaining <= 0:
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                message_key="monopoly-jp-fence-none-left",
                reason_code="no_supply",
            )

        cost = self._fence_costs.get(space_id, 0)
        if player_cash < cost:
            return FenceBuildOutcome(
                status="error",
                space_id=space_id,
                cost=cost,
                message_key="monopoly-not-enough-cash",
                reason_code="insufficient_funds",
            )

        self.state.fenced_space_ids.add(space_id)
        self.state.fences_remaining -= 1
        return FenceBuildOutcome(status="built", space_id=space_id, cost=cost)

    def sell_fence(self, space_id: str) -> int:
        """Sell a fence back to the bank for half cost. Returns refund amount."""
        if space_id not in self.state.fenced_space_ids:
            return 0
        cost = self._fence_costs.get(space_id, 0)
        refund = int(cost * self.profile.fence_sell_back_rate)
        self.state.fenced_space_ids.discard(space_id)
        self.state.fences_remaining = min(
            self.state.fences_remaining + 1,
            self.profile.total_fences,
        )
        return refund

    def get_buildable_paddocks(
        self,
        owner_id: str,
        property_owners: dict[str, str],
    ) -> list[str]:
        """Return space IDs where the player can build a fence."""
        result = []
        for sid in self._property_space_ids:
            if property_owners.get(sid) != owner_id:
                continue
            if self._space_subtype.get(sid) != "dino_paddock":
                continue
            if sid in self.state.fenced_space_ids:
                continue
            if sid in self.state.damaged_space_ids:
                continue
            result.append(sid)
        return result

    def get_repairable_properties(
        self,
        owner_id: str,
        property_owners: dict[str, str],
    ) -> list[str]:
        """Return space IDs of damaged properties the player can repair."""
        return [
            sid
            for sid in self.state.damaged_space_ids
            if property_owners.get(sid) == owner_id
        ]

    def get_sellable_fences(
        self,
        owner_id: str,
        property_owners: dict[str, str],
    ) -> list[str]:
        """Return space IDs where the player can sell a fence."""
        return [
            sid
            for sid in self.state.fenced_space_ids
            if property_owners.get(sid) == owner_id
        ]

    # -----------------------------------------------------------------
    # Electronic gate (GO resolution)
    # -----------------------------------------------------------------

    def resolve_gate(self, use_amber_die: bool = False) -> GateOutcome:
        """Resolve the electronic gate when a player passes or lands on GO.

        If *use_amber_die* is True, use the die-based fallback instead of
        random gate simulation.  Returns the payout and sound result.
        """
        if use_amber_die:
            roll = random.randint(1, 6)  # nosec B311
            if roll in self.profile.gate_amber_theme_range:
                return GateOutcome(
                    sound="theme",
                    payout=self.profile.gate_theme_payout,
                    method="amber_die",
                    amber_roll=roll,
                )
            return GateOutcome(
                sound="roar",
                payout=self.profile.gate_roar_payout,
                method="amber_die",
                amber_roll=roll,
            )

        # Simulate electronic gate: 50/50 chance
        if random.random() < 0.5:  # nosec B311
            return GateOutcome(
                sound="theme",
                payout=self.profile.gate_theme_payout,
                method="gate",
            )
        return GateOutcome(
            sound="roar",
            payout=self.profile.gate_roar_payout,
            method="gate",
        )

    # -----------------------------------------------------------------
    # Complete set tracking
    # -----------------------------------------------------------------

    def check_complete_sets(
        self,
        property_owners: dict[str, str],
    ) -> list[CompleteSetResult]:
        """Check all color groups for newly completed sets.

        When a set is newly completed, damaged properties in the set are
        auto-repaired for free.  Returns list of newly completed results.
        """
        results: list[CompleteSetResult] = []

        for group, members in self._color_groups.items():
            if group in self.state.complete_set_groups:
                continue  # Already tracked

            if not members:
                continue

            # Check if all members are owned by the same player or team
            owners = set()
            for sid in members:
                owner = property_owners.get(sid)
                if not owner:
                    break
                owners.add(owner)
            else:
                if len(owners) == 1:
                    # Newly completed set!
                    self.state.complete_set_groups.add(group)

                    # Auto-repair damaged properties in the set
                    auto_repaired: list[str] = []
                    if self.profile.complete_set_auto_repair:
                        for sid in members:
                            if sid in self.state.damaged_space_ids:
                                self.state.damaged_space_ids.discard(sid)
                                auto_repaired.append(sid)

                    results.append(
                        CompleteSetResult(
                            newly_completed=True,
                            set_group=group,
                            space_ids=tuple(members),
                            auto_repaired=tuple(auto_repaired),
                        )
                    )

        return results

    def untrack_complete_set(self, group: str) -> None:
        """Remove a group from complete set tracking (e.g., after a trade)."""
        self.state.complete_set_groups.discard(group)

    def is_set_complete(self, group: str) -> bool:
        """Return True if the given color group is a completed set."""
        return group in self.state.complete_set_groups

    # -----------------------------------------------------------------
    # Rent calculation helpers
    # -----------------------------------------------------------------

    def get_effective_rent(
        self,
        space_id: str,
        base_rent: int,
        fenced_rent: int,
    ) -> int:
        """Return effective rent considering damage and fence status.

        Returns 0 if the property is damaged.
        Returns fenced_rent if the property has a fence.
        Returns base_rent otherwise.
        """
        if space_id in self.state.damaged_space_ids:
            return 0
        if space_id in self.state.fenced_space_ids and fenced_rent > 0:
            return fenced_rent
        return base_rent

    # -----------------------------------------------------------------
    # State summary (for park status action)
    # -----------------------------------------------------------------

    def get_park_summary(
        self,
        property_owners: dict[str, str],
        player_names: dict[str, str],
    ) -> dict[str, object]:
        """Build a summary dict for the read-park-state action."""
        return {
            "trex_position": self.state.trex_position,
            "damaged_count": len(self.state.damaged_space_ids),
            "damaged_space_ids": sorted(self.state.damaged_space_ids),
            "fenced_count": len(self.state.fenced_space_ids),
            "fenced_space_ids": sorted(self.state.fenced_space_ids),
            "fences_remaining": self.state.fences_remaining,
            "complete_sets": sorted(self.state.complete_set_groups),
            "all_damaged_game_over": self.state.all_damaged_game_over,
            "total_properties": len(self._property_space_ids),
        }
