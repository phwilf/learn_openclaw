"""Safe read-only file tool scoped to a repository root."""

from __future__ import annotations

import os
from pathlib import Path

from .contracts import ToolExecutionError, ToolResult

_MAX_BYTES = 20_000
_ALLOWED_EXTENSIONS = {".md", ".txt", ".py", ".json", ".yaml", ".yml", ".toml"}


def get_repo_root() -> Path:
    configured = os.getenv("ASSISTANT_REPO_ROOT", "").strip()
    return Path(configured).resolve() if configured else Path.cwd().resolve()


def _resolve_in_repo(rel_path: str, repo_root: Path) -> Path:
    candidate = (repo_root / rel_path).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError as exc:
        raise ToolExecutionError("Path is outside repository scope") from exc
    return candidate


def run_read_text_file(args: dict[str, object]) -> ToolResult:
    raw_path = str(args.get("path", "")).strip()
    if not raw_path:
        return ToolResult(ok=False, error="Missing required arg: path")

    repo_root = get_repo_root()
    try:
        path = _resolve_in_repo(raw_path, repo_root)
    except ToolExecutionError as exc:
        return ToolResult(ok=False, error=str(exc))

    if not path.exists() or not path.is_file():
        return ToolResult(ok=False, error="File not found")

    if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
        return ToolResult(ok=False, error="File extension is not allowed")

    if path.stat().st_size > _MAX_BYTES:
        return ToolResult(ok=False, error="File exceeds size limit")

    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ToolResult(ok=False, error="File is not valid UTF-8 text")

    return ToolResult(ok=True, content=content)
