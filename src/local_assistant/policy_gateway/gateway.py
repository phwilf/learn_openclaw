"""Config-driven policy gateway for tool intent decisions."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from local_assistant.tools import ToolIntent, ToolSpec

from .config import get_policy_rules


@dataclass
class PolicyDecision:
    status: str  # allow | deny | require_approval
    reason_code: str
    user_message: str
    internal_detail: str


def _is_path_in_repo(path_value: object, repo_root: Path) -> tuple[bool, str]:
    if not isinstance(path_value, str) or not path_value.strip():
        return False, "Missing required arg: path"
    candidate = (repo_root / path_value).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError:
        return False, "Path escapes repository scope"
    return True, "ok"


def _user_message_for_status(status: str) -> str:
    if status == "allow":
        return "Tool request allowed."
    if status == "require_approval":
        return "Approval required before executing this tool."
    return "Tool request denied."


def evaluate_tool_intent(
    intent: ToolIntent, spec: ToolSpec | None, repo_root: Path, has_user_approval: bool = False
) -> PolicyDecision:
    rules = get_policy_rules()

    if spec is None:
        return PolicyDecision(
            status="deny",
            reason_code=rules.unknown_tool_reason_code,
            user_message=_user_message_for_status("deny"),
            internal_detail=f"Unknown tool: {intent.name}",
        )

    tool_rule = rules.tools.get(intent.name)
    if tool_rule is None:
        return PolicyDecision(
            status="deny",
            reason_code=rules.default_reason_code,
            user_message=_user_message_for_status("deny"),
            internal_detail=f"No policy rule for tool: {intent.name}",
        )

    if tool_rule.approval_required and not has_user_approval:
        reason_code = tool_rule.reason_codes.get("require_approval", "side_effectful")
        return PolicyDecision(
            status="require_approval",
            reason_code=reason_code,
            user_message=_user_message_for_status("require_approval"),
            internal_detail=f"Tool '{intent.name}' requires user approval",
        )

    if tool_rule.requires_repo_scope:
        ok, detail = _is_path_in_repo(intent.args.get("path"), repo_root)
        if not ok:
            reason_code = tool_rule.reason_codes.get("deny_scope", "path_out_of_scope")
            return PolicyDecision(
                status="deny",
                reason_code=reason_code,
                user_message=_user_message_for_status("deny"),
                internal_detail=detail,
            )

    if tool_rule.allow:
        reason_code = tool_rule.reason_codes.get("allow", "allowed")
        return PolicyDecision(
            status="allow",
            reason_code=reason_code,
            user_message=_user_message_for_status("allow"),
            internal_detail=f"Tool '{intent.name}' allowed by policy rules",
        )

    status = rules.default_action
    reason_code = tool_rule.reason_codes.get("deny_default", rules.default_reason_code)
    return PolicyDecision(
        status=status,
        reason_code=reason_code,
        user_message=_user_message_for_status(status),
        internal_detail=f"Tool '{intent.name}' followed default action: {status}",
    )
