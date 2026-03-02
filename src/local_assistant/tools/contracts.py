"""Tool contracts and result types."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


class ToolExecutionError(RuntimeError):
    """Raised when tool execution fails in a controlled way."""


@dataclass
class ToolIntent:
    name: str
    args: dict[str, object]


@dataclass
class ToolResult:
    ok: bool
    content: str | None = None
    error: str | None = None


@dataclass
class ToolSpec:
    name: str
    side_effectful: bool
    description: str
    executor: Callable[[dict[str, object]], ToolResult]
