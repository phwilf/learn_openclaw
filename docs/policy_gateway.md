# Policy Gateway

## Purpose
Enforce policy decisions before any tool executes.

## Step 4/P1 Implementation
- Policy evaluator: `src/local_assistant/policy_gateway/gateway.py`
- Policy config loader/validator: `src/local_assistant/policy_gateway/config.py`
- Default policy rules: `src/local_assistant/policy_gateway/policy_rules.json`
- Decision statuses: `allow`, `deny`, `require_approval`
- User-facing responses are safe summaries.
- Internal logs include detailed denial/decision context.
- Interactive approval flow is handled in `src/local_assistant/core_loop/loop.py`.

## Config-Driven Rules (v1)
- Unknown tool: `deny`
- Side-effectful tool: `require_approval`
- `read_text_file` path outside repo scope: `deny`
- `read_text_file` in repo scope: `allow`
- `write_text_file` requires explicit user approval and repo-scoped path.

## Safety Behavior
- Policy config is JSON.
- Missing/invalid policy config hard-fails (no soft fallback).
- Reason codes are config-driven; user-safe messages remain in code.
