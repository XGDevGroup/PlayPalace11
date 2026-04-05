"""Deterministic in-game banking simulator for Monopoly electronic banking."""

from __future__ import annotations

from dataclasses import dataclass, field


BANK_ACCOUNT_ID = "bank"


@dataclass(frozen=True)
class ElectronicBankingProfile:
    """Anchor-driven configuration for electronic banking economy rules."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str = "anchor-first"
    starting_balance: int = 1500
    pass_go_credit: int = 200
    allow_manual_transfers: bool = True
    overdraft_policy: str = "no_overdraft"
    provenance_notes: tuple[str, ...] = ()


@dataclass
class BankAccount:
    """Mutable account state for one player."""

    player_id: str
    card_id: str
    balance: int
    is_active: bool = True


@dataclass(frozen=True)
class BankTransaction:
    """Immutable transaction record for deterministic ledgers."""

    tx_id: str
    kind: str
    from_id: str
    to_id: str
    amount: int
    reason: str
    status: str
    failure_reason: str = ""


@dataclass
class BankingState:
    """Serializable simulator state for all electronic banking operations."""

    preset_id: str
    anchor_edition_id: str
    source_policy: str
    accounts: dict[str, BankAccount] = field(default_factory=dict)
    ledger: list[BankTransaction] = field(default_factory=list)
    next_tx_index: int = 1

    def snapshot(self) -> dict:
        """Return deterministic snapshot payload for tests/persistence checks."""
        account_rows = [
            {
                "player_id": player_id,
                "card_id": account.card_id,
                "balance": account.balance,
                "is_active": account.is_active,
            }
            for player_id, account in sorted(self.accounts.items())
        ]
        ledger_rows = [
            {
                "tx_id": tx.tx_id,
                "kind": tx.kind,
                "from_id": tx.from_id,
                "to_id": tx.to_id,
                "amount": tx.amount,
                "reason": tx.reason,
                "status": tx.status,
                "failure_reason": tx.failure_reason,
            }
            for tx in self.ledger
        ]
        return {
            "preset_id": self.preset_id,
            "anchor_edition_id": self.anchor_edition_id,
            "source_policy": self.source_policy,
            "next_tx_index": self.next_tx_index,
            "accounts": account_rows,
            "ledger": ledger_rows,
        }


def _next_tx_id(state: BankingState) -> str:
    tx_id = f"tx-{state.next_tx_index:05d}"
    state.next_tx_index += 1
    return tx_id


def _record_transaction(
    state: BankingState,
    *,
    kind: str,
    from_id: str,
    to_id: str,
    amount: int,
    reason: str,
    status: str,
    failure_reason: str = "",
) -> BankTransaction:
    tx = BankTransaction(
        tx_id=_next_tx_id(state),
        kind=kind,
        from_id=from_id,
        to_id=to_id,
        amount=max(0, amount),
        reason=reason,
        status=status,
        failure_reason=failure_reason,
    )
    state.ledger.append(tx)
    return tx


def init_accounts(player_ids: list[str], profile: ElectronicBankingProfile) -> BankingState:
    """Initialize deterministic account state for provided players."""
    normalized_player_ids: list[str] = []
    seen: set[str] = set()
    for player_id in player_ids:
        normalized = str(player_id).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        normalized_player_ids.append(normalized)

    state = BankingState(
        preset_id=profile.preset_id,
        anchor_edition_id=profile.anchor_edition_id,
        source_policy=profile.source_policy,
    )
    starting_balance = max(0, profile.starting_balance)
    for index, player_id in enumerate(normalized_player_ids, start=1):
        state.accounts[player_id] = BankAccount(
            player_id=player_id,
            card_id=f"card-{index:02d}",
            balance=starting_balance,
        )
    return state


def get_balance(state: BankingState, player_id: str) -> int:
    """Return current account balance for a player."""
    account = state.accounts.get(player_id)
    if not account or not account.is_active:
        return 0
    return account.balance


def can_pay(state: BankingState, player_id: str, amount: int) -> bool:
    """Return True if account has sufficient balance for amount."""
    if amount <= 0:
        return True
    return get_balance(state, player_id) >= amount


def credit(
    state: BankingState,
    player_id: str,
    amount: int,
    reason: str,
    *,
    from_id: str = BANK_ACCOUNT_ID,
) -> BankTransaction:
    """Credit money to one player account."""
    account = state.accounts.get(player_id)
    if account is None or not account.is_active:
        return _record_transaction(
            state,
            kind="credit",
            from_id=from_id,
            to_id=player_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="unknown_account",
        )
    if amount <= 0:
        return _record_transaction(
            state,
            kind="credit",
            from_id=from_id,
            to_id=player_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="invalid_amount",
        )

    account.balance += amount
    return _record_transaction(
        state,
        kind="credit",
        from_id=from_id,
        to_id=player_id,
        amount=amount,
        reason=reason,
        status="success",
    )


def debit(
    state: BankingState,
    player_id: str,
    amount: int,
    reason: str,
    *,
    to_id: str = BANK_ACCOUNT_ID,
) -> BankTransaction:
    """Debit money from one player account."""
    account = state.accounts.get(player_id)
    if account is None or not account.is_active:
        return _record_transaction(
            state,
            kind="debit",
            from_id=player_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="unknown_account",
        )
    if amount <= 0:
        return _record_transaction(
            state,
            kind="debit",
            from_id=player_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="invalid_amount",
        )
    if account.balance < amount:
        return _record_transaction(
            state,
            kind="debit",
            from_id=player_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="insufficient_funds",
        )

    account.balance -= amount
    return _record_transaction(
        state,
        kind="debit",
        from_id=player_id,
        to_id=to_id,
        amount=amount,
        reason=reason,
        status="success",
    )


def transfer(
    state: BankingState,
    from_id: str,
    to_id: str,
    amount: int,
    reason: str,
) -> BankTransaction:
    """Transfer money between two player accounts."""
    from_account = state.accounts.get(from_id)
    to_account = state.accounts.get(to_id)
    if from_account is None or to_account is None:
        return _record_transaction(
            state,
            kind="transfer",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="unknown_account",
        )
    if not from_account.is_active or not to_account.is_active:
        return _record_transaction(
            state,
            kind="transfer",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="inactive_account",
        )
    if from_id == to_id:
        return _record_transaction(
            state,
            kind="transfer",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="invalid_target",
        )
    if amount <= 0:
        return _record_transaction(
            state,
            kind="transfer",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="invalid_amount",
        )
    if from_account.balance < amount:
        return _record_transaction(
            state,
            kind="transfer",
            from_id=from_id,
            to_id=to_id,
            amount=amount,
            reason=reason,
            status="failed",
            failure_reason="insufficient_funds",
        )

    from_account.balance -= amount
    to_account.balance += amount
    return _record_transaction(
        state,
        kind="transfer",
        from_id=from_id,
        to_id=to_id,
        amount=amount,
        reason=reason,
        status="success",
    )
