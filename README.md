# Local Assistant Learning Project

Local-first, single-user project for learning assistant architecture end-to-end.

## Learning path (start here)
For the full roadmap, architecture goals, and milestone gates, read:
- [`LEARNING_SPEC.md`](./LEARNING_SPEC.md)

## Current milestone
Step 2 scaffold is in place:
- Module folders under `src/local_assistant/`
- Minimal `v0 core loop` (single turn, no memory/tools)
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

## Security checks
```bash
./install_hooks.sh
./run_gitleaks.sh
```

## Golden tasks (Step 2)
```bash
python3 scripts/run_golden_tasks.py
```
