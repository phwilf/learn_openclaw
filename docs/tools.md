# Tools Module

## Purpose
Provide a typed registry and execution path for assistant tools.

## Step 4 Implementation
- Tool contracts: `src/local_assistant/tools/contracts.py`
- Registry: `src/local_assistant/tools/registry.py`
- First safe tool: `read_text_file` in `src/local_assistant/tools/read_text_file.py`
- Side-effectful tool: `write_text_file` in `src/local_assistant/tools/write_text_file.py` (approval-gated)

## Current Rules
- Only registered tools can run.
- `read_text_file` is read-only and scoped to repository root.
- Unknown tools are denied by policy gateway.
- Side-effectful tools are gated with `require_approval`.

## Tool Intent Format
Use a structured command in user input:

```text
/tool <tool_name> <json-args>
```

Example:

```text
/tool read_text_file {"path":"README.md"}
```
