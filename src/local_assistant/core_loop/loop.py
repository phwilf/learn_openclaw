"""Core loop for one-turn handling with model and tool-policy flows."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime

from .prompt_builder import build_messages
from local_assistant.integration_adapters import (
    ModelAdapter,
    ModelAdapterConfigError,
    ModelAdapterError,
    StubModelAdapter,
    build_model_adapter,
)
from local_assistant.persona import load_persona
from local_assistant.policy_gateway import evaluate_tool_intent
from local_assistant.tools import ToolIntent, ToolRegistry, build_default_registry
from local_assistant.tools.read_text_file import get_repo_root


@dataclass
class TurnResult:
    user_input: str
    assistant_output: str
    created_at_utc: str
    model_provider: str
    model_name: str
    model_latency_ms: int
    persona_name: str
    persona_version: str
    model_error: str | None = None
    used_fallback: bool = False
    tool_name: str | None = None
    policy_status: str | None = None


@dataclass
class PendingApproval:
    intent: ToolIntent
    summary: str
    created_at_utc: str


class ToolIntentParseError(ValueError):
    """Raised when a /tool request is malformed."""


_PENDING_APPROVAL: PendingApproval | None = None
_APPROVE_PATTERNS = {
    "/approve",
    "approve",
    "approved",
    "yes",
    "go ahead",
    "do it",
    "proceed",
    "confirm",
}
_DENY_PATTERNS = {
    "/deny",
    "deny",
    "denied",
    "no",
    "cancel",
    "stop",
    "reject",
    "don\'t do it",
}


def reset_approval_state() -> None:
    global _PENDING_APPROVAL
    _PENDING_APPROVAL = None


def _log_event(event: dict[str, object]) -> None:
    print(json.dumps(event), file=sys.stderr)


def _normalize_for_approval(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^\w\s/']", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _classify_approval_input(user_input: str) -> str | None:
    normalized = _normalize_for_approval(user_input)
    if not normalized:
        return None
    if normalized in _APPROVE_PATTERNS:
        return "approve"
    if normalized in _DENY_PATTERNS:
        return "deny"
    if re.search(r"\b(approve|approved|proceed|confirm)\b", normalized):
        return "approve"
    if re.search(r"\b(deny|denied|reject|cancel|stop)\b", normalized):
        return "deny"
    if re.search(r"\byes\b", normalized) and len(normalized.split()) <= 5:
        return "approve"
    if re.search(r"\bno\b", normalized) and len(normalized.split()) <= 5:
        return "deny"
    return None


def _parse_tool_intent(user_input: str) -> ToolIntent | None:
    text = user_input.strip()
    if not text.startswith("/tool"):
        return None
    parts = text.split(maxsplit=2)
    if len(parts) < 2:
        raise ToolIntentParseError("Missing tool name. Expected: /tool <name> <json-args>")
    name = parts[1].strip()
    if not name:
        raise ToolIntentParseError("Missing tool name. Expected: /tool <name> <json-args>")
    raw_args = parts[2].strip() if len(parts) > 2 else "{}"
    try:
        parsed_args = json.loads(raw_args)
    except json.JSONDecodeError as exc:
        raise ToolIntentParseError("Invalid JSON args. Expected: /tool <name> <json-args>") from exc
    if not isinstance(parsed_args, dict):
        raise ToolIntentParseError("Tool args must be a JSON object")
    return ToolIntent(name=name, args=parsed_args)


def _tool_response(
    *, status: str, tool_name: str, message: str, reason_code: str, content: str | None = None
) -> str:
    payload = {
        "type": "tool_result",
        "tool": tool_name,
        "status": status,
        "reason_code": reason_code,
        "message": message,
    }
    if content is not None:
        payload["content"] = content
    return json.dumps(payload)


def _approval_response(*, status: str, message: str, tool_name: str | None = None) -> str:
    payload: dict[str, object] = {"type": "approval", "status": status, "message": message}
    if tool_name is not None:
        payload["tool"] = tool_name
    return json.dumps(payload)


def _tool_turn_result(
    *,
    user_input: str,
    assistant_output: str,
    persona_name: str,
    persona_version: str,
    tool_name: str,
    policy_status: str,
) -> TurnResult:
    return TurnResult(
        user_input=user_input,
        assistant_output=assistant_output,
        created_at_utc=datetime.now(UTC).isoformat(),
        model_provider="none",
        model_name="none",
        model_latency_ms=0,
        persona_name=persona_name,
        persona_version=persona_version,
        tool_name=tool_name,
        policy_status=policy_status,
    )


def _execute_tool_intent(
    *,
    user_input: str,
    persona_name: str,
    persona_version: str,
    intent: ToolIntent,
    registry: ToolRegistry,
    has_user_approval: bool,
) -> TurnResult:
    spec = registry.get(intent.name)
    decision = evaluate_tool_intent(intent, spec, get_repo_root(), has_user_approval=has_user_approval)

    _log_event(
        {
            "event": "policy_decision",
            "tool": intent.name,
            "status": decision.status,
            "reason_code": decision.reason_code,
            "internal_detail": decision.internal_detail,
            "persona_name": persona_name,
            "persona_version": persona_version,
        }
    )

    if decision.status == "require_approval":
        global _PENDING_APPROVAL
        summary = f"{intent.name} with args {json.dumps(intent.args, sort_keys=True)}"
        _PENDING_APPROVAL = PendingApproval(
            intent=intent,
            summary=summary,
            created_at_utc=datetime.now(UTC).isoformat(),
        )
        _log_event(
            {
                "event": "approval_requested",
                "tool": intent.name,
                "summary": summary,
                "persona_name": persona_name,
                "persona_version": persona_version,
            }
        )
        output = _tool_response(
            status="require_approval",
            tool_name=intent.name,
            message=f"Approval required before executing this action: {summary}. Reply with yes/approve or no/deny.",
            reason_code=decision.reason_code,
        )
        return _tool_turn_result(
            user_input=user_input,
            assistant_output=output,
            persona_name=persona_name,
            persona_version=persona_version,
            tool_name=intent.name,
            policy_status=decision.status,
        )

    if decision.status != "allow":
        output = _tool_response(
            status=decision.status,
            tool_name=intent.name,
            message=decision.user_message,
            reason_code=decision.reason_code,
        )
        return _tool_turn_result(
            user_input=user_input,
            assistant_output=output,
            persona_name=persona_name,
            persona_version=persona_version,
            tool_name=intent.name,
            policy_status=decision.status,
        )

    tool_result = registry.execute(intent)
    _log_event(
        {
            "event": "tool_execution",
            "tool": intent.name,
            "ok": tool_result.ok,
            "error": tool_result.error,
            "persona_name": persona_name,
            "persona_version": persona_version,
        }
    )

    if tool_result.ok:
        output = _tool_response(
            status="ok",
            tool_name=intent.name,
            message="Tool executed successfully.",
            reason_code="executed",
            content=tool_result.content,
        )
    else:
        output = _tool_response(
            status="error",
            tool_name=intent.name,
            message="Tool execution failed.",
            reason_code="execution_error",
        )
    return _tool_turn_result(
        user_input=user_input,
        assistant_output=output,
        persona_name=persona_name,
        persona_version=persona_version,
        tool_name=intent.name,
        policy_status="allow",
    )


def run_single_turn(user_input: str, model_adapter: ModelAdapter | None = None) -> TurnResult:
    global _PENDING_APPROVAL
    persona = load_persona()
    registry: ToolRegistry = build_default_registry()

    if user_input.strip().startswith("/tool"):
        approval_action = None
    else:
        approval_action = _classify_approval_input(user_input)
    if _PENDING_APPROVAL is not None and approval_action is not None:
        pending = _PENDING_APPROVAL
        if approval_action == "deny":
            _PENDING_APPROVAL = None
            _log_event(
                {
                    "event": "approval_denied",
                    "tool": pending.intent.name,
                    "persona_name": persona.name,
                    "persona_version": persona.version,
                }
            )
            output = _approval_response(
                status="denied", message="Approval denied. Pending action was canceled.", tool_name=pending.intent.name
            )
            return _tool_turn_result(
                user_input=user_input,
                assistant_output=output,
                persona_name=persona.name,
                persona_version=persona.version,
                tool_name=pending.intent.name,
                policy_status="approval_denied",
            )

        _PENDING_APPROVAL = None
        _log_event(
            {
                "event": "approval_approved",
                "tool": pending.intent.name,
                "persona_name": persona.name,
                "persona_version": persona.version,
            }
        )
        return _execute_tool_intent(
            user_input=user_input,
            persona_name=persona.name,
            persona_version=persona.version,
            intent=pending.intent,
            registry=registry,
            has_user_approval=True,
        )

    if _PENDING_APPROVAL is not None and approval_action is None:
        pending = _PENDING_APPROVAL
        _PENDING_APPROVAL = None
        cancellation_note = f"Pending approval for {pending.intent.name} was canceled due to new input."
        _log_event(
            {
                "event": "approval_cancelled_unrelated_input",
                "tool": pending.intent.name,
                "persona_name": persona.name,
                "persona_version": persona.version,
            }
        )
    else:
        cancellation_note = None

    if _PENDING_APPROVAL is None and approval_action is not None:
        output = _approval_response(
            status="no_pending",
            message="No pending approval request. Submit a side-effectful tool request first.",
        )
        return _tool_turn_result(
            user_input=user_input,
            assistant_output=output,
            persona_name=persona.name,
            persona_version=persona.version,
            tool_name="none",
            policy_status="no_pending_approval",
        )

    try:
        intent = _parse_tool_intent(user_input)
    except ToolIntentParseError as exc:
        output = _tool_response(
            status="invalid_request",
            tool_name="unknown",
            message="Invalid tool request.",
            reason_code="parse_error",
        )
        _log_event(
            {
                "event": "tool_intent_parse",
                "status": "error",
                "detail": str(exc),
                "persona_name": persona.name,
                "persona_version": persona.version,
            }
        )
        return _tool_turn_result(
            user_input=user_input,
            assistant_output=output,
            persona_name=persona.name,
            persona_version=persona.version,
            tool_name="unknown",
            policy_status="invalid_request",
        )

    if intent is not None:
        result = _execute_tool_intent(
            user_input=user_input,
            persona_name=persona.name,
            persona_version=persona.version,
            intent=intent,
            registry=registry,
            has_user_approval=False,
        )
        if cancellation_note:
            payload = json.loads(result.assistant_output)
            payload["notice"] = cancellation_note
            result.assistant_output = json.dumps(payload)
        return result

    messages = build_messages(persona, user_input)
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
        model_result = adapter.generate(user_input, messages=messages)
    except ModelAdapterError as exc:
        adapter_error = str(exc)
        used_fallback = True
        model_result = StubModelAdapter().generate(user_input, messages=messages)

    _log_event(
        {
            "event": "model_call",
            "provider": model_result.provider,
            "model": model_result.model,
            "latency_ms": model_result.latency_ms,
            "persona_name": persona.name,
            "persona_version": persona.version,
            "used_fallback": used_fallback,
            "error": adapter_error,
        }
    )
    assistant_output = model_result.text
    if cancellation_note:
        assistant_output = f"{cancellation_note}\n{assistant_output}"

    return TurnResult(
        user_input=user_input,
        assistant_output=assistant_output,
        created_at_utc=datetime.now(UTC).isoformat(),
        model_provider=model_result.provider,
        model_name=model_result.model,
        model_latency_ms=model_result.latency_ms,
        persona_name=persona.name,
        persona_version=persona.version,
        model_error=adapter_error,
        used_fallback=used_fallback,
    )
