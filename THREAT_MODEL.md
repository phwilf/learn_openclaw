# Threat Model (Local-First Learning Assistant)

## Scope
Single-user, local-first assistant for learning architecture.
Not intended for multi-tenant production use.

## Assets to Protect
- API keys and credentials
- Local transcripts and memory state
- Filesystem contents accessible by tools
- System command execution capability

## Trust Boundaries
- User input -> model output
- Model output -> tool invocation
- Tool output -> persisted memory/logs
- Local repo -> public GitHub publication

## Primary Threats
1. Prompt injection causes unsafe tool use.
2. Secret leakage through logs, commits, or examples.
3. Over-permissive shell/file tools modify unintended data.
4. Memory persistence stores sensitive/private content.
5. Context compaction accidentally surfaces sensitive text.
6. External harness integration bypasses local policy checks.

## Baseline Mitigations
- Deny-by-default policy gateway for tool calls.
- Explicit approval requirement for side-effectful actions.
- Tool allowlist with constrained argument validation.
- Container boundary for risky tools, with explicit mount allowlist.
- Read-only filesystem defaults for tool execution unless explicitly required.
- Structured audit logs for policy decisions and side effects.
- Separate private runtime state from repo-tracked files.
- Pre-publish secret scanning and checklist enforcement.
- Adapter contract requiring policy + logging parity.

## Residual Risks (Accepted for Learning Phase)
- Single-machine compromise risk.
- Human error in manual publish review.
- Incomplete threat coverage until all modules are implemented.

## Security Review Triggers
Run a new review when:
- A new tool is added.
- Policy logic changes.
- Persistence format changes.
- External adapter is introduced or modified.
