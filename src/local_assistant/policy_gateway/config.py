"""Policy rules loader and validator (JSON)."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import resources
from pathlib import Path


class PolicyConfigError(RuntimeError):
    """Raised when policy config is missing or invalid."""


@dataclass
class ToolPolicyRule:
    approval_required: bool
    requires_repo_scope: bool
    allow: bool
    reason_codes: dict[str, str]


@dataclass
class PolicyRules:
    version: int
    default_action: str
    default_reason_code: str
    unknown_tool_reason_code: str
    tools: dict[str, ToolPolicyRule]


_POLICY_RULES_CACHE: PolicyRules | None = None


def _default_policy_path() -> Path:
    return Path(resources.files("local_assistant.policy_gateway") / "policy_rules.json")


def _validate_reason_codes(value: object, *, tool_name: str) -> dict[str, str]:
    if not isinstance(value, dict):
        raise PolicyConfigError(f"Tool '{tool_name}' reason_codes must be an object")
    result: dict[str, str] = {}
    for key, raw in value.items():
        if not isinstance(key, str) or not key:
            raise PolicyConfigError(f"Tool '{tool_name}' has invalid reason code key")
        if not isinstance(raw, str) or not raw:
            raise PolicyConfigError(f"Tool '{tool_name}' reason code '{key}' must be a non-empty string")
        result[key] = raw
    return result


def _parse_rules(data: object) -> PolicyRules:
    if not isinstance(data, dict):
        raise PolicyConfigError("Policy config root must be an object")

    version = data.get("version")
    if not isinstance(version, int):
        raise PolicyConfigError("Policy config 'version' must be an integer")
    if version != 1:
        raise PolicyConfigError(f"Unsupported policy config version: {version}")

    default_action = data.get("default_action")
    if default_action not in {"deny", "allow"}:
        raise PolicyConfigError("Policy config 'default_action' must be 'deny' or 'allow'")

    default_reason_code = data.get("default_reason_code")
    if not isinstance(default_reason_code, str) or not default_reason_code:
        raise PolicyConfigError("Policy config 'default_reason_code' must be a non-empty string")

    unknown_tool_reason_code = data.get("unknown_tool_reason_code")
    if not isinstance(unknown_tool_reason_code, str) or not unknown_tool_reason_code:
        raise PolicyConfigError("Policy config 'unknown_tool_reason_code' must be a non-empty string")

    tools_raw = data.get("tools")
    if not isinstance(tools_raw, dict):
        raise PolicyConfigError("Policy config 'tools' must be an object")

    tools: dict[str, ToolPolicyRule] = {}
    for tool_name, raw in tools_raw.items():
        if not isinstance(tool_name, str) or not tool_name:
            raise PolicyConfigError("Tool names must be non-empty strings")
        if not isinstance(raw, dict):
            raise PolicyConfigError(f"Tool '{tool_name}' rule must be an object")

        approval_required = raw.get("approval_required")
        if not isinstance(approval_required, bool):
            raise PolicyConfigError(f"Tool '{tool_name}' approval_required must be boolean")

        requires_repo_scope = raw.get("requires_repo_scope")
        if not isinstance(requires_repo_scope, bool):
            raise PolicyConfigError(f"Tool '{tool_name}' requires_repo_scope must be boolean")

        allow = raw.get("allow")
        if not isinstance(allow, bool):
            raise PolicyConfigError(f"Tool '{tool_name}' allow must be boolean")

        reason_codes = _validate_reason_codes(raw.get("reason_codes"), tool_name=tool_name)

        tools[tool_name] = ToolPolicyRule(
            approval_required=approval_required,
            requires_repo_scope=requires_repo_scope,
            allow=allow,
            reason_codes=reason_codes,
        )

    return PolicyRules(
        version=version,
        default_action=default_action,
        default_reason_code=default_reason_code,
        unknown_tool_reason_code=unknown_tool_reason_code,
        tools=tools,
    )


def load_policy_rules(path: str | None = None) -> PolicyRules:
    path_value = path or os.getenv("POLICY_RULES_PATH")
    file_path = Path(path_value).resolve() if path_value else _default_policy_path()

    if not file_path.exists() or not file_path.is_file():
        raise PolicyConfigError(f"Policy config file not found: {file_path}")

    try:
        data = json.loads(file_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PolicyConfigError(f"Policy config contains invalid JSON: {exc}") from exc

    return _parse_rules(data)


def get_policy_rules() -> PolicyRules:
    global _POLICY_RULES_CACHE
    if _POLICY_RULES_CACHE is None:
        _POLICY_RULES_CACHE = load_policy_rules()
    return _POLICY_RULES_CACHE


def reset_policy_rules_cache() -> None:
    global _POLICY_RULES_CACHE
    _POLICY_RULES_CACHE = None
