"""Tool registry and default tool set."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import ToolIntent, ToolResult, ToolSpec
from .read_text_file import run_read_text_file
from .write_text_file import run_write_text_file


@dataclass
class ToolRegistry:
    specs: dict[str, ToolSpec]

    def get(self, name: str) -> ToolSpec | None:
        return self.specs.get(name)

    def execute(self, intent: ToolIntent) -> ToolResult:
        spec = self.get(intent.name)
        if spec is None:
            return ToolResult(ok=False, error="Unknown tool")
        return spec.executor(intent.args)


def build_default_registry() -> ToolRegistry:
    specs = {
        "read_text_file": ToolSpec(
            name="read_text_file",
            side_effectful=False,
            description="Read a UTF-8 text file within repository scope.",
            executor=run_read_text_file,
        ),
        "write_text_file": ToolSpec(
            name="write_text_file",
            side_effectful=True,
            description="Write UTF-8 text file contents within repository scope.",
            executor=run_write_text_file,
        ),
    }
    return ToolRegistry(specs=specs)
