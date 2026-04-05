"""Deterministic voice-style command parsing for Monopoly voice banking."""

from __future__ import annotations

from dataclasses import dataclass
import re


VOICE_PREFIX = "voice:"


@dataclass(frozen=True)
class VoiceParseResult:
    """Result of parsing a voice-style command payload."""

    intent: str = ""
    error: str = ""
    amount: int = 0
    target_name: str = ""
    payload: str = ""

    @property
    def ok(self) -> bool:
        """Return True when parse produced a valid intent."""
        return bool(self.intent) and not self.error


_TRANSFER_PATTERN = re.compile(
    r"^transfer\s+(?P<amount>\d+)\s+to\s+(?P<target>.+)$",
    re.IGNORECASE,
)


def parse_voice_command(text: str) -> VoiceParseResult:
    """Parse one raw message using strict `voice:` prefix contract."""
    raw = str(text)
    if not raw.startswith(VOICE_PREFIX):
        return VoiceParseResult(error="missing_prefix", payload=raw)

    payload = raw[len(VOICE_PREFIX) :].strip()
    if not payload:
        return VoiceParseResult(error="empty_command", payload=payload)

    lowered = payload.lower()
    if lowered in {"balance", "check balance"}:
        return VoiceParseResult(intent="check_balance", payload=payload)
    if lowered in {"ledger", "show ledger", "history"}:
        return VoiceParseResult(intent="show_recent_ledger", payload=payload)
    if lowered in {"repeat", "again"}:
        return VoiceParseResult(intent="repeat_last_bank_result", payload=payload)
    if lowered == "confirm transfer":
        return VoiceParseResult(intent="confirm_transfer", payload=payload)

    transfer_match = _TRANSFER_PATTERN.match(payload)
    if transfer_match:
        amount_text = transfer_match.group("amount")
        target_name = transfer_match.group("target").strip()
        try:
            amount = int(amount_text)
        except ValueError:
            return VoiceParseResult(error="invalid_amount", payload=payload)
        if amount <= 0:
            return VoiceParseResult(error="invalid_amount", payload=payload)
        if not target_name:
            return VoiceParseResult(error="missing_target", payload=payload)
        return VoiceParseResult(
            intent="transfer_amount_to_player",
            amount=amount,
            target_name=target_name,
            payload=payload,
        )

    return VoiceParseResult(error="unknown_command", payload=payload)
