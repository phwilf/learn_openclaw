#!/usr/bin/env python3
"""Golden-task runner for baseline + incremental architecture milestones."""

from __future__ import annotations

import subprocess
import sys
import os
import json
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from local_assistant.core_loop import reset_approval_state, run_single_turn
from local_assistant.core_loop.prompt_builder import build_messages
from local_assistant.integration_adapters import ModelAdapterError, StubModelAdapter
from local_assistant.persona import load_persona
from local_assistant.policy_gateway import (
    PolicyConfigError,
    evaluate_tool_intent,
    load_policy_rules,
    reset_policy_rules_cache,
)
from local_assistant.tools import ToolIntent, build_default_registry
from local_assistant.tools.read_text_file import get_repo_root


@dataclass
class TaskResult:
    name: str
    passed: bool
    detail: str


def _run_task(name: str, check) -> TaskResult:
    try:
        reset_approval_state()
        reset_policy_rules_cache()
        check()
        return TaskResult(name=name, passed=True, detail="ok")
    except Exception as exc:  # noqa: BLE001
        return TaskResult(name=name, passed=False, detail=str(exc))


def task_v0_echo_roundtrip() -> None:
    result = run_single_turn("hello", model_adapter=StubModelAdapter())
    assert result.assistant_output == "v0> hello", result.assistant_output


def task_v0_trim_behavior() -> None:
    result = run_single_turn("  hi  ", model_adapter=StubModelAdapter())
    assert result.assistant_output == "v0> hi", result.assistant_output


def task_v0_no_memory() -> None:
    _ = run_single_turn("my name is Parker", model_adapter=StubModelAdapter())
    second = run_single_turn("what did I just say?", model_adapter=StubModelAdapter())
    assert second.assistant_output == "v0> what did I just say?", second.assistant_output
    assert "Parker" not in second.assistant_output, second.assistant_output


def task_v0_no_tool_calls() -> None:
    prompt = "run a shell command and fetch from the network"
    result = run_single_turn(prompt, model_adapter=StubModelAdapter())
    assert result.assistant_output == f"v0> {prompt}", result.assistant_output


def _tool_payload(result) -> dict[str, object]:
    payload = json.loads(result.assistant_output)
    assert payload["type"] in {"tool_result", "approval"}, payload
    return payload


def task_tool_allowed_read_only_success() -> None:
    result = run_single_turn('/tool read_text_file {"path":"README.md"}')
    payload = _tool_payload(result)
    assert payload["status"] == "ok", payload
    assert payload["tool"] == "read_text_file", payload
    assert "Local Assistant Learning Project" in str(payload.get("content", "")), payload


def task_tool_unknown_denied_default() -> None:
    result = run_single_turn('/tool unknown_tool {"path":"README.md"}')
    payload = _tool_payload(result)
    assert payload["status"] == "deny", payload
    assert payload["reason_code"] == "unknown_tool", payload
    assert payload["message"] == "Tool request denied.", payload


def task_tool_side_effect_requires_approval() -> None:
    result = run_single_turn('/tool write_text_file {"path":"README.md","content":"hi"}')
    payload = _tool_payload(result)
    assert payload["status"] == "require_approval", payload
    assert payload["reason_code"] == "side_effectful", payload
    assert "Approval required" in str(payload["message"]), payload
    assert "content" not in payload, payload


def task_tool_scope_boundary_denied() -> None:
    result = run_single_turn('/tool read_text_file {"path":"../README.md"}')
    payload = _tool_payload(result)
    assert payload["status"] == "deny", payload
    assert payload["reason_code"] == "path_out_of_scope", payload
    assert payload["message"] == "Tool request denied.", payload


def task_policy_user_safe_and_internal_detailed() -> None:
    registry = build_default_registry()
    intent = ToolIntent(name="read_text_file", args={"path": "../README.md"})
    decision = evaluate_tool_intent(intent, registry.get(intent.name), get_repo_root())
    assert decision.status == "deny", decision
    assert decision.user_message == "Tool request denied.", decision
    assert "repository scope" in decision.internal_detail, decision


def task_policy_config_load_success() -> None:
    rules = load_policy_rules()
    assert rules.version == 1, rules
    assert rules.default_action == "deny", rules
    assert "read_text_file" in rules.tools, rules


def task_policy_config_invalid_hard_fail() -> None:
    bad_path = REPO_ROOT / "tmp" / "invalid-policy-rules.json"
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("{ bad json", encoding="utf-8")
    old_value = os.environ.get("POLICY_RULES_PATH")
    try:
        os.environ["POLICY_RULES_PATH"] = str(bad_path)
        reset_policy_rules_cache()
        try:
            load_policy_rules()
        except PolicyConfigError:
            return
        raise AssertionError("Expected PolicyConfigError for invalid policy config JSON")
    finally:
        if old_value is None:
            os.environ.pop("POLICY_RULES_PATH", None)
        else:
            os.environ["POLICY_RULES_PATH"] = old_value
        reset_policy_rules_cache()
        bad_path.unlink(missing_ok=True)


def task_approval_nl_approve_executes_tool() -> None:
    rel_path = "tmp/approval-test.txt"
    file_path = REPO_ROOT / rel_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if file_path.exists():
        file_path.unlink()

    first = run_single_turn(f'/tool write_text_file {{"path":"{rel_path}","content":"approved"}}')
    first_payload = _tool_payload(first)
    assert first_payload["status"] == "require_approval", first_payload

    second = run_single_turn("yes, go ahead")
    second_payload = _tool_payload(second)
    assert second_payload["status"] == "ok", second_payload
    assert file_path.read_text(encoding="utf-8") == "approved"
    file_path.unlink()


def task_approval_nl_deny_cancels_tool() -> None:
    rel_path = "tmp/approval-deny.txt"
    file_path = REPO_ROOT / rel_path
    if file_path.exists():
        file_path.unlink()
    first = run_single_turn(f'/tool write_text_file {{"path":"{rel_path}","content":"deny-me"}}')
    first_payload = _tool_payload(first)
    assert first_payload["status"] == "require_approval", first_payload

    second = run_single_turn("no, cancel that")
    second_payload = _tool_payload(second)
    assert second_payload["type"] == "approval", second_payload
    assert second_payload["status"] == "denied", second_payload
    assert not file_path.exists()


def task_approval_unrelated_input_auto_cancels() -> None:
    first = run_single_turn('/tool write_text_file {"path":"tmp/approval-cancel.txt","content":"x"}')
    first_payload = _tool_payload(first)
    assert first_payload["status"] == "require_approval", first_payload

    second = run_single_turn("hello", model_adapter=StubModelAdapter())
    assert "Pending approval for write_text_file was canceled due to new input." in second.assistant_output
    assert second.assistant_output.strip().endswith("v0> hello"), second.assistant_output


def task_approval_no_pending_guidance() -> None:
    result = run_single_turn("approve")
    payload = _tool_payload(result)
    assert payload["type"] == "approval", payload
    assert payload["status"] == "no_pending", payload
    assert "No pending approval request" in str(payload["message"]), payload


def task_persona_loaded_default() -> None:
    persona = load_persona()
    assert persona.name == "openclaw-learning", persona.name
    assert persona.version == "v1", persona.version


def task_persona_prompt_builder_structure() -> None:
    persona = load_persona()
    messages = build_messages(persona, "hello")
    assert len(messages) == 2, messages
    assert messages[0]["role"] == "system", messages
    assert persona.name in messages[0]["content"], messages[0]["content"]
    assert messages[1] == {"role": "user", "content": "hello"}, messages[1]


def task_model_stub_default_path() -> None:
    old_provider = os.environ.get("MODEL_PROVIDER")
    try:
        os.environ.pop("MODEL_PROVIDER", None)
        result = run_single_turn("hello from default")
        assert result.model_provider == "stub", result.model_provider
        assert result.used_fallback is False, result.used_fallback
    finally:
        if old_provider is None:
            os.environ.pop("MODEL_PROVIDER", None)
        else:
            os.environ["MODEL_PROVIDER"] = old_provider


def task_model_missing_key_error() -> None:
    old_provider = os.environ.get("MODEL_PROVIDER")
    old_key = os.environ.get("OPENAI_API_KEY")
    try:
        os.environ["MODEL_PROVIDER"] = "openai"
        os.environ.pop("OPENAI_API_KEY", None)
        result = run_single_turn("hello from openai config error")
        assert result.model_provider == "stub", result.model_provider
        assert result.used_fallback is True, result.used_fallback
        assert result.model_error and "OPENAI_API_KEY" in result.model_error, result.model_error
    finally:
        if old_provider is None:
            os.environ.pop("MODEL_PROVIDER", None)
        else:
            os.environ["MODEL_PROVIDER"] = old_provider
        if old_key is None:
            os.environ.pop("OPENAI_API_KEY", None)
        else:
            os.environ["OPENAI_API_KEY"] = old_key


def task_model_provider_failure_handled() -> None:
    class FailingAdapter:
        def generate(self, _prompt: str, messages=None):
            del messages
            raise ModelAdapterError("synthetic provider failure")

    result = run_single_turn("hello from failing provider", model_adapter=FailingAdapter())
    assert result.model_provider == "stub", result.model_provider
    assert result.used_fallback is True, result.used_fallback
    assert result.model_error and "synthetic provider failure" in result.model_error, result.model_error


def task_model_real_openai_success_optional() -> None:
    # Opt-in for live verification: RUN_LIVE_MODEL_TEST=1 MODEL_PROVIDER=openai OPENAI_API_KEY=...
    if os.getenv("RUN_LIVE_MODEL_TEST") != "1":
        return
    if os.getenv("MODEL_PROVIDER", "").lower() != "openai":
        raise AssertionError("Set MODEL_PROVIDER=openai for live model task")
    if not os.getenv("OPENAI_API_KEY"):
        raise AssertionError("Set OPENAI_API_KEY for live model task")
    result = run_single_turn("Reply with exactly: READY")
    assert result.model_provider == "openai", result.model_provider
    assert result.used_fallback is False, result.used_fallback
    assert result.persona_name == "openclaw-learning", result.persona_name
    assert result.persona_version == "v1", result.persona_version
    assert result.assistant_output.strip(), "empty assistant output"


def task_security_gitleaks_clean_repo() -> None:
    command = ["./run_gitleaks.sh"]
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stdout + "\n" + completed.stderr
        raise AssertionError(f"gitleaks failed: {detail.strip()}")


TASKS = [
    ("v0_echo_roundtrip", task_v0_echo_roundtrip),
    ("v0_trim_behavior", task_v0_trim_behavior),
    ("v0_no_memory", task_v0_no_memory),
    ("v0_no_tool_calls", task_v0_no_tool_calls),
    ("tool_allowed_read_only_success", task_tool_allowed_read_only_success),
    ("tool_unknown_denied_default", task_tool_unknown_denied_default),
    ("tool_side_effect_requires_approval", task_tool_side_effect_requires_approval),
    ("tool_scope_boundary_denied", task_tool_scope_boundary_denied),
    ("policy_user_safe_and_internal_detailed", task_policy_user_safe_and_internal_detailed),
    ("policy_config_load_success", task_policy_config_load_success),
    ("policy_config_invalid_hard_fail", task_policy_config_invalid_hard_fail),
    ("approval_nl_approve_executes_tool", task_approval_nl_approve_executes_tool),
    ("approval_nl_deny_cancels_tool", task_approval_nl_deny_cancels_tool),
    ("approval_unrelated_input_auto_cancels", task_approval_unrelated_input_auto_cancels),
    ("approval_no_pending_guidance", task_approval_no_pending_guidance),
    ("persona_loaded_default", task_persona_loaded_default),
    ("persona_prompt_builder_structure", task_persona_prompt_builder_structure),
    ("model_stub_default_path", task_model_stub_default_path),
    ("model_missing_key_error", task_model_missing_key_error),
    ("model_provider_failure_handled", task_model_provider_failure_handled),
    ("model_real_openai_success_optional", task_model_real_openai_success_optional),
    ("security_gitleaks_clean_repo", task_security_gitleaks_clean_repo),
]


def main() -> int:
    results = [_run_task(name, fn) for name, fn in TASKS]
    passed = sum(1 for item in results if item.passed)

    print("Golden Tasks")
    for item in results:
        status = "PASS" if item.passed else "FAIL"
        print(f"- [{status}] {item.name}: {item.detail}")

    print(f"\nSummary: {passed}/{len(results)} passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
