"""Core loop for one-turn handling with model adapter fallback."""

import json
import sys
from dataclasses import dataclass
from datetime import datetime, UTC

from local_assistant.integration_adapters import (
    ModelAdapter,
    ModelAdapterConfigError,
    ModelAdapterError,
    StubModelAdapter,
    build_model_adapter,
)


@dataclass
class TurnResult:
    user_input: str
    assistant_output: str
    created_at_utc: str
    model_provider: str
    model_name: str
    model_latency_ms: int
    model_error: str | None = None
    used_fallback: bool = False


def _log_model_event(
    *, provider: str, model: str, latency_ms: int, error: str | None, used_fallback: bool
) -> None:
    event = {
        "event": "model_call",
        "provider": provider,
        "model": model,
        "latency_ms": latency_ms,
        "used_fallback": used_fallback,
        "error": error,
    }
    print(json.dumps(event), file=sys.stderr)


def run_single_turn(user_input: str, model_adapter: ModelAdapter | None = None) -> TurnResult:
    adapter = model_adapter
    adapter_error: str | None = None
    used_fallback = False

    if adapter is None:
        try:
            adapter = build_model_adapter()
        except ModelAdapterConfigError as exc:
            adapter_error = str(exc)
            used_fallback = True
            adapter = StubModelAdapter()

    try:
        result = adapter.generate(user_input)
    except ModelAdapterError as exc:
        adapter_error = str(exc)
        used_fallback = True
        result = StubModelAdapter().generate(user_input)

    _log_model_event(
        provider=result.provider,
        model=result.model,
        latency_ms=result.latency_ms,
        error=adapter_error,
        used_fallback=used_fallback,
    )
    return TurnResult(
        user_input=user_input,
        assistant_output=result.text,
        created_at_utc=datetime.now(UTC).isoformat(),
        model_provider=result.provider,
        model_name=result.model,
        model_latency_ms=result.latency_ms,
        model_error=adapter_error,
        used_fallback=used_fallback,
    )
