# Repository Guidelines

## Project Structure & Module Organization
This repository uses a Python `src/` layout.
- `src/local_assistant/`: core application modules (`core_loop`, `persona`, `memory`, `tools`, `policy_gateway`, `router`, etc.).
- `scripts/`: operational utilities (`run_golden_tasks.py`, `run_gitleaks.sh`, `install_hooks.sh`).
- `golden_tasks/`: baseline behavior docs and regression task definitions.
- `docs/`: architecture and security documentation.
- Root docs: `LEARNING_SPEC.md`, `THREAT_MODEL.md`, `PUBLISH_CHECKLIST.md`, `LESSONS_LEARNED.md`.

Keep new code inside `src/local_assistant/<module>/` and align additions with the module boundaries defined in `LEARNING_SPEC.md`.

## Build, Test, and Development Commands
- `PYTHONPATH=src python3 -m local_assistant.core_loop`: run the v0 single-turn assistant loop.
- `python3 scripts/run_golden_tasks.py`: run baseline regression tasks (behavior + security check).
- `./install_hooks.sh`: install pre-commit hook wiring for secret scanning.
- `./run_gitleaks.sh`: run manual secret scan using `.gitleaks.toml`.

Run golden tasks before opening a PR.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and clear, small functions.
- Use type hints and dataclasses where appropriate (current code follows this pattern).
- Prefer module/function names in `snake_case`; classes in `PascalCase`.
- Keep docstrings concise and behavior-focused.
- Optimize for concise, efficient, human-readable code by default; prefer the simplest implementation that preserves clarity.

No auto-formatter is enforced yet; keep style consistent with existing files.

## Testing Guidelines
The project currently uses a golden-task runner instead of a full test framework.
- Add new checks in `scripts/run_golden_tasks.py` as `task_<behavior_name>` functions.
- Keep tasks deterministic and local-only (no network dependency).
- Preserve baseline guarantees (e.g., no unintended memory/tool side effects in v0).

## Commit & Pull Request Guidelines
Recent commits use short, imperative subjects with optional milestone scope (example: `Step 2 baseline: scaffold modules, v0 loop, and commit guardrails`).
- Commit format: `<scope>: <what changed>` when helpful.
- PRs should include: purpose, key changes, test evidence (`python3 scripts/run_golden_tasks.py` output), and docs updates when architecture or safety behavior changes.
- Link related issues/tasks and include screenshots only if UI artifacts are introduced.

## Documentation Update Check (Required)
After any meaningful code or architecture change, always evaluate whether documentation updates are needed before finishing work.
- Update `LESSONS_LEARNED.md` for milestone-level learnings and tradeoffs.
- Update component deep dives in `docs/` (for example `docs/persona.md`, `docs/tools.md`) when behavior/design guidance changes.
- Update top-level docs (`README.md`, `LEARNING_SPEC.md`, `THREAT_MODEL.md`, `PUBLISH_CHECKLIST.md`) when setup, scope, risk, or release criteria change.
- If no doc updates are required, explicitly confirm that decision in the final summary.

## Security & Configuration Tips
- Never commit secrets; use `.env` locally and keep `.env.example` as placeholders only.
- Ensure `gitleaks` is installed before committing.
- Treat policy and safety behavior changes as high-risk; update `THREAT_MODEL.md` when relevant.
