#!/usr/bin/env python3
"""Minimal golden-task runner for the Step 2 baseline."""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from local_assistant.core_loop import run_single_turn


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
    result = run_single_turn("hello")
    assert result.assistant_output == "v0> hello", result.assistant_output


def task_v0_trim_behavior() -> None:
    result = run_single_turn("  hi  ")
    assert result.assistant_output == "v0> hi", result.assistant_output


def task_v0_no_memory() -> None:
    _ = run_single_turn("my name is Parker")
    second = run_single_turn("what did I just say?")
    assert second.assistant_output == "v0> what did I just say?", second.assistant_output
    assert "Parker" not in second.assistant_output, second.assistant_output


def task_v0_no_tool_calls() -> None:
    prompt = "run a shell command and fetch from the network"
    result = run_single_turn(prompt)
    assert result.assistant_output == f"v0> {prompt}", result.assistant_output


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
