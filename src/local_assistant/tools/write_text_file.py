"""Side-effectful file writer tool scoped to repository root."""

from __future__ import annotations

from pathlib import Path

from .contracts import ToolResult
from .read_text_file import get_repo_root

_MAX_BYTES = 20_000
_ALLOWED_EXTENSIONS = {".md", ".txt", ".json", ".yaml", ".yml", ".toml"}


def _resolve_in_repo(rel_path: str, repo_root: Path) -> Path | None:
    candidate = (repo_root / rel_path).resolve()
    try:
        candidate.relative_to(repo_root)
    except ValueError:
        return None
    return candidate


def run_write_text_file(args: dict[str, object]) -> ToolResult:
    raw_path = str(args.get("path", "")).strip()
    content = args.get("content")

    if not raw_path:
        return ToolResult(ok=False, error="Missing required arg: path")
    if not isinstance(content, str):
        return ToolResult(ok=False, error="Missing required arg: content")
    if len(content.encode("utf-8")) > _MAX_BYTES:
        return ToolResult(ok=False, error="Content exceeds size limit")

    repo_root = get_repo_root()
    path = _resolve_in_repo(raw_path, repo_root)
    if path is None:
        return ToolResult(ok=False, error="Path is outside repository scope")

    if path.suffix.lower() not in _ALLOWED_EXTENSIONS:
        return ToolResult(ok=False, error="File extension is not allowed")

    if not path.parent.exists() or not path.parent.is_dir():
        return ToolResult(ok=False, error="Parent directory does not exist")

    path.write_text(content, encoding="utf-8")
    return ToolResult(ok=True, content=f"Wrote {len(content)} chars to {path.relative_to(repo_root)}")
