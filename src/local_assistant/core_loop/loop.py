"""Minimal v0 core loop: one input -> one output, no memory or tools."""

from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass
class TurnResult:
    user_input: str
    assistant_output: str
    created_at_utc: str


def _v0_model_stub(user_input: str) -> str:
    """Deterministic placeholder for model behavior in v0."""
    return f"v0> {user_input.strip()}"


def run_single_turn(user_input: str) -> TurnResult:
    output = _v0_model_stub(user_input)
    return TurnResult(
        user_input=user_input,
        assistant_output=output,
        created_at_utc=datetime.now(UTC).isoformat(),
    )
