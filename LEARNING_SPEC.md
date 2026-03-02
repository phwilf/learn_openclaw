# LEARNING_SPEC

## 1) Purpose
Build a local-first, single-user assistant from first principles to deeply understand:
- Memory
- Persona
- Tools
- Safety gateway
- Context compaction and automation
- Multi-agent orchestration

This project is for learning architecture and extension patterns, not for production deployment.

## 2) Learning Outcomes (Definition of Done)
By the end, I should be able to:
1. Explain each subsystem and why it exists.
2. Trace one request end-to-end across all modules.
3. Add a new tool safely (policy + tests + eval case).
4. Diagnose failures using logs and evaluation harnesses.
5. Extend the system with an external harness (Claude Code/Codex-style) without breaking core guarantees.

## 3) Scope
### In scope
- Local-first assistant with modular architecture.
- Plain-text, inspectable state (files/SQLite/config).
- Explicit policy enforcement before tool execution.
- Container isolation boundary for higher-risk tools.
- Memory + compaction + scheduled automation.
- Basic multi-agent routing.
- Integration layer for external harnesses (e.g., Claude Code/Codex-like runtime).
- Public-by-default project structure for safe GitHub publishing.

### Out of scope (for now)
- Multi-tenant hosting and cloud scale.
- Full enterprise auth/permissions stack.
- Production-grade hardening/SOC2-level controls.

## 4) Core Principles
1. Safety is architectural, not a post-hoc patch.
2. Every decision is inspectable (logs, policies, memory entries).
3. Module boundaries stay strict.
4. New capability must include an evaluation case.
5. Prefer simple, explicit mechanisms over hidden magic.
6. New capability ships only when `schema + execution path + eval` are all present.
7. Risky tool execution must cross an explicit isolation boundary.

## 5) System Modules (Target Mental Model)
- `core_loop`: Message handling and orchestration.
- `persona`: Instruction profile (`SOUL.md`-style behavior layer).
- `memory`: Short-term + persistent store (local file/SQLite).
- `tools`: Tool registry + execution adapters.
- `policy_gateway`: Allowlists, approval flows, risk checks.
- `compaction`: Summarization and context budget management.
- `automation`: Scheduled tasks/heartbeats.
- `router`: Multi-agent dispatch and handoff.
- `integration_adapters`: Bridge external harnesses (CloudCoder/Codex-style).
- `observability`: Structured logging, traces, run metadata.
- `evaluation`: Golden tasks + regression checks.

## 6) Build Phases
1. `v0 core loop`: single chat turn, no memory/tools.
2. Add persistence + replay: inspect token and state growth.
3. Add persona layer: behavior consistency checks.
4. Add tools + policy gateway: safe execution path.
5. Add container isolation boundary for risky tools (mount allowlist + read-only defaults).
6. Add compaction + memory quality checks.
7. Add automation scheduler with isolated run context.
8. Add multi-agent routing and handoff protocol.
9. Add external harness adapter(s) and verify extension safety.

## 7) Observability Requirements
At minimum, log:
- Input/output events
- Model calls (latency, token usage, failure mode)
- Tool invocation intents + results
- Policy decisions (allow/deny/require approval)
- Memory writes/reads and compaction operations
- Router decisions and agent handoffs
- Automation trigger/start/finish/failure

All logs should be local and readable for postmortems.

## 8) Evaluation Harness Requirements
Maintain a `golden_tasks` suite (10-20 tasks) covering:
- Basic Q&A behavior
- Memory recall across turns
- Persona consistency
- Tool execution success/failure paths
- Policy denial/approval flows
- Compaction correctness under long sessions
- Multi-agent routing correctness
- External harness adapter behavior

Rule: no major change ships without re-running the suite and recording results.
Note: golden tasks are one evaluation type; capability-level checks may also include unit/contract/smoke tests.

## 9) External Harness Extension Goal (Claude Code/Codex-style)
Goal: learn to build *on top of* existing harnesses, not only from scratch.

Design requirement:
- Add an adapter boundary where external runtimes can plug in.
- Preserve internal guarantees:
  - policy checks before side effects
  - consistent logging schema
  - shared memory contract
  - reproducible evaluation path

Practical checkpoints:
1. Define adapter interface (`invoke`, `tool_proxy`, `session_state`).
2. Implement one harness adapter.
3. Run golden tasks through both native and adapter-backed paths.
4. Document behavioral diffs and mitigation strategy.

## 10) Safety Baseline (Local Learning Mode)
- Default deny for risky tools.
- Explicit user approval for side-effectful actions.
- Sandboxed tool execution where possible.
- Containerized execution for higher-risk tools where practical.
- Read-only filesystem defaults with explicit writable mount allowlist.
- No silent execution of shell/network actions.
- Audit trail for every side effect.

## 11) Public Publishing Baseline
Goal: publish progress safely and clearly on GitHub with zero secret leakage.

Required controls:
- Use `.env` for local secrets and never commit it.
- Commit a `.env.example` with placeholder variable names only.
- Add `.gitignore` entries for secrets, local DB/state, logs, and transcripts.
- Add pre-commit secret scanning (e.g., `gitleaks`) before pushes.
- Keep sample data and fixtures fully synthetic/anonymized.
- Separate user-private state from repo-managed files by design.

Repository/documentation format:
- Keep architecture docs in `docs/` with one file per subsystem.
- Maintain a public `LESSONS_LEARNED.md` updated per milestone.
- Add a `THREAT_MODEL.md` documenting risks and mitigations.
- Add `PUBLISH_CHECKLIST.md` before every public release.

Release rule:
- No publish unless `PUBLISH_CHECKLIST.md` passes (secrets scan + redaction review + safe defaults review).

## 12) Non-Functional Learning Targets
- Understand tradeoffs between simplicity and control.
- Learn failure modes (prompt injection, tool misuse, memory drift).
- Build confidence extending capabilities without coupling everything together.

## 13) Milestone Checkpoints
Use these review gates:
1. Architecture gate: modules exist with clear boundaries.
2. Safety gate: policy gateway blocks unsafe paths by default.
3. Isolation gate: risky tools run through container boundary with constrained mounts.
4. Reliability gate: golden task pass rate does not regress.
5. Extensibility gate: external adapter works without bypassing controls.
6. Explainability gate: can narrate one full trace from input to side effect.
7. Publishability gate: repo passes publish checklist with no secret exposure.

---

If this spec stays true, success means: I can both build a foundational assistant and confidently extend existing harnesses into my own system architecture.
