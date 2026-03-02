# Local Assistant Learning Project

Local-first, single-user project for learning assistant architecture end-to-end.

## Learning path (start here)
For the full roadmap, architecture goals, and milestone gates, read:
- [`LEARNING_SPEC.md`](./LEARNING_SPEC.md)

## Current milestone
Step 4 baseline is in place:
- Model adapter boundary with persona-aware prompt building
- Tool registry + policy gateway minimal safe execution path
- Secret-scanning hooks with `gitleaks`

## Project layout
- `src/local_assistant/core_loop/`: v0 orchestration loop and CLI
- `src/local_assistant/persona/`
- `src/local_assistant/memory/`
- `src/local_assistant/tools/`
- `src/local_assistant/policy_gateway/`
- `src/local_assistant/compaction/`
- `src/local_assistant/automation/`
- `src/local_assistant/router/`
- `src/local_assistant/integration_adapters/`
- `src/local_assistant/observability/`
- `src/local_assistant/evaluation/`

## Run v0 core loop
```bash
PYTHONPATH=src python3 -m local_assistant.core_loop
```

## Use a real model (OpenAI)
```bash
MODEL_PROVIDER=openai OPENAI_API_KEY=... PYTHONPATH=src python3 -m local_assistant.core_loop
```

## Persona profile
- Default profile: `src/local_assistant/persona/default.json`
- Optional override: set `PERSONA_PROFILE_PATH=/absolute/path/to/profile.json`

## Tool execution (Step 4)
- Tool request format: `/tool <tool_name> <json-args>`
- Current tool: `read_text_file` (repo-scoped, read-only)
- Side-effectful tool: `write_text_file` (requires interactive approval)
- Policy gateway status outcomes: `allow`, `deny`, `require_approval`
- Policy rules source: `src/local_assistant/policy_gateway/policy_rules.json`
- Optional override: `POLICY_RULES_PATH=/absolute/path/to/policy_rules.json`

Example:
```text
/tool read_text_file {"path":"README.md"}
```

## Security checks
```bash
./install_hooks.sh
./run_gitleaks.sh
```

## Golden tasks
```bash
python3 scripts/run_golden_tasks.py
```
