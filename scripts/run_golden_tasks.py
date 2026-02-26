#!/usr/bin/env python3
"""Minimal golden-task runner for the Step 2 baseline."""

from __future__ import annotations

import subprocess
import sys
import os
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from local_assistant.core_loop import run_single_turn
from local_assistant.core_loop.prompt_builder import build_messages
from local_assistant.integration_adapters import ModelAdapterError, StubModelAdapter
from local_assistant.persona import load_persona


@dataclass
class TaskResult:
    name: str
    passed: bool
    detail: str


def _run_task(name: str, check) -> TaskResult:
    try:
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
