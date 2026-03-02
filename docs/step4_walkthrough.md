# Step 4 Walkthrough (Tools + Policy Gateway)

## Quick Context
Step 4 adds a minimal safe tool execution path:
- tool intent parsing
- policy decision before execution
- one safe read-only tool
- one side-effectful tool behind interactive approval
- structured tool result responses

## Read First (5 minutes)
1. `src/local_assistant/core_loop/loop.py`
2. `src/local_assistant/policy_gateway/gateway.py`
3. `src/local_assistant/policy_gateway/config.py`
4. `src/local_assistant/policy_gateway/policy_rules.json`
5. `src/local_assistant/tools/registry.py`
6. `src/local_assistant/tools/read_text_file.py`
7. `src/local_assistant/tools/write_text_file.py`
8. `scripts/run_golden_tasks.py` (Step 4 tasks)

## Core Flow
1. User sends a tool request in this format:
   - `/tool <tool_name> <json-args>`
2. Core loop parses request into `ToolIntent`.
3. Core loop looks up `ToolSpec` in registry.
4. Core loop calls policy gateway:
   - `allow` -> execute tool
   - `deny` -> return safe denial
   - `require_approval` -> return approval-required response
5. If approval is required, core loop stores pending action and asks for explicit confirmation.
6. On natural-language approve/deny input, pending action is executed or canceled.
7. Core loop returns structured JSON `tool_result` or `approval` payload.
8. Internal logs capture decision and execution details.

## Files and Why They Exist
- `src/local_assistant/tools/contracts.py`
  - Defines `ToolIntent`, `ToolSpec`, `ToolResult`.
  - Separates request, definition, and outcome contracts.

- `src/local_assistant/tools/registry.py`
  - Central place to register tools.
  - Step 4 tools:
    - `read_text_file` (safe read-only)
    - `write_text_file` (side-effectful, approval-gated)

- `src/local_assistant/tools/read_text_file.py`
  - Implements scoped file reading.
  - Safety checks:
    - repo boundary enforcement
    - extension allowlist
    - size cap
    - UTF-8 text only

- `src/local_assistant/tools/write_text_file.py`
  - Implements scoped file writes.
  - Executes only after explicit approval.

- `src/local_assistant/policy_gateway/gateway.py`
  - Evaluates tool intents using loaded policy config.
  - Enforces:
    - unknown tool -> deny
    - side-effectful tool -> require_approval
    - out-of-scope read path -> deny
    - in-scope `read_text_file` -> allow
  - Returns user-safe message + internal detail.

- `src/local_assistant/policy_gateway/config.py` and `policy_rules.json`
  - JSON policy schema + strict validation.
  - Missing/invalid config hard-fails.
  - Reason codes live in config; user-safe messaging lives in code.

- `src/local_assistant/core_loop/loop.py`
  - Enforces policy-first execution path.
  - Executes side-effectful tools only after interactive approval.
  - Keeps existing model/persona flow for non-tool input.

## Key Decisions
- Deny by default.
- User-facing denial messages are generic.
- Internal logs hold detailed policy reasons.
- Scope boundary is repository root.
- Side-effectful tools require explicit natural-language approval.
- Pending approvals auto-cancel on unrelated input and notify the user.

## How To Run
- Run all checks:
```bash
python3 scripts/run_golden_tasks.py
```

- Manual tool call:
```bash
PYTHONPATH=src python3 -m local_assistant.core_loop
# then paste:
/tool read_text_file {"path":"README.md"}
```

## Step 4 Golden Tasks To Focus On
- `tool_allowed_read_only_success`
- `tool_unknown_denied_default`
- `tool_side_effect_requires_approval`
- `tool_scope_boundary_denied`
- `policy_user_safe_and_internal_detailed`
- `approval_nl_approve_executes_tool`
- `approval_nl_deny_cancels_tool`
- `approval_unrelated_input_auto_cancels`
- `approval_no_pending_guidance`

## What’s Next
- Add timeout/expiry + request IDs for pending approvals.
