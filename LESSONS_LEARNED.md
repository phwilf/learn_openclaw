# Lessons Learned

Capture short notes at each milestone so learning is shareable.

## Template

### Milestone: <name>
- Date:
- What changed:
- What worked:
- What failed / surprised me:
- Key tradeoff:
- Safety implications:
- What I would do differently next time:

## Entries

### Milestone: Step 1 - Learning Spec
- Date: 2026-02-25
- What changed: Defined architecture, milestones, evaluation harness, and public-by-default publishing standards.
- What worked: Converting goals into explicit gates clarified what "done" means.
- What failed / surprised me: Scope can sprawl quickly without strict module boundaries.
- Key tradeoff: Fast iteration vs. early safety/documentation constraints.
- Safety implications: Added explicit secret handling and publish checks from day one.
- What I would do differently next time: Start golden-task definitions earlier to reduce ambiguity in later steps.

### Milestone: Step 2 - Module Scaffold + v0 Core Loop
- Date: 2026-02-25
- What changed: Added module scaffolding under `src/local_assistant/` and a runnable single-turn core loop with no memory/tools.
- What worked: Keeping module boundaries explicit early made next-phase implementation targets clear.
- What failed / surprised me: Hook setup under restricted environments can require local cache path overrides or elevated install steps.
- Key tradeoff: Lightweight deterministic v0 behavior now vs. realistic model behavior later.
- Safety implications: Secret scanning is active before commits, reducing accidental leakage risk.
- What I would do differently next time: Add first golden tasks immediately alongside each phase to tighten feedback loops.

### Milestone: Step 2.1 - Commit Guardrails (gitleaks + pre-commit)
- Date: 2026-02-25
- What changed: Added a `pre-commit` hook that runs `gitleaks` before each commit.
- What worked: It blocks accidental secret commits early, before code reaches remote repos.
- What failed / surprised me: Hook setup can fail if local cache/hook paths are restricted by environment permissions.
- Key tradeoff: Slightly slower commits in exchange for much safer publishing hygiene.
- Safety implications: Strongly reduces risk of leaking API keys, tokens, and credentials.
- What I would do differently next time: Install these guardrails immediately after `git init`.
- Plain-language note: `pre-commit` is a gate that runs checks before a commit is accepted; `gitleaks` is one of those checks that looks for secrets in staged changes.
- Scope note: This is a general software engineering best practice for most repositories, not specific to building an OpenClaw-like assistant.

### Milestone: Step 2.2 - Baseline Golden Tasks
- Date: 2026-02-25
- What changed: Added a minimal golden-task runner with 5 baseline checks for current v0 behavior and secret-scan health.
- What worked: Small deterministic checks make future refactors safer without adding heavy test tooling.
- What failed / surprised me: Security checks can be the slowest part of a tiny suite but are still worth keeping in the baseline.
- Key tradeoff: Narrow baseline scope now vs. broader behavioral coverage later.
- Safety implications: Includes a required clean `gitleaks` run to keep publish-safety expectations testable.
- What I would do differently next time: Add pass/fail snapshots per commit once behavior starts changing quickly.
- Scope note: Golden-task harnessing is a general engineering reliability practice and not specific to OpenClaw-like assistant architecture.

### Milestone: Step 3a - Model Adapter Boundary
- Date: 2026-02-26
- What changed: Added a model adapter boundary (`stub` + `openai`), wired fallback handling in core loop, and extended golden tasks for config/failure behavior.
- What worked: Adapter/factory design made provider choice environment-driven and kept core loop unchanged at call site.
- What failed / surprised me: Live provider verification should remain opt-in to avoid blocking local deterministic runs.
- Key tradeoff: More configuration paths vs. better extensibility and safer failure handling.
- Safety implications: Missing/invalid provider config now degrades to a safe local fallback instead of crashing.
- What I would do differently next time: Add a provider-level retry policy once observability is richer.
- Scope note: Adapter boundaries and fallback tests are general architecture best practices, not OpenClaw-specific.

### Milestone: Step 3b - Persona Research and Design Notes
- Date: 2026-02-26
- What changed: Captured a persona-layer deep dive before implementation, including definitions, misconceptions, best practices, and initial evaluation ideas.
- What worked: Separating persona from memory and policy clarified module boundaries and reduced design ambiguity.
- What failed / surprised me: It's easy to overuse persona text as a safety mechanism; hard enforcement still needs separate policy controls.
- Key tradeoff: Rich persona instructions vs. keeping behavior contracts concise and testable.
- Safety implications: Persona improves communication consistency but does not replace policy gateways or tool approval checks.
- What I would do differently next time: Add persona regression tasks at the same time as the first implementation pass.
- Deep dive: See `docs/persona.md` for full notes and implementation guidance.

### Milestone: Step 3c - Persona Layer Implementation
- Date: 2026-02-26
- What changed: Implemented a file-backed persona profile, prompt-builder boundary, and core-loop persona injection into model calls.
- What worked: Keeping persona in a dedicated module made the model adapter integration small and easy to reason about.
- What failed / surprised me: Persona and policy can still be conflated unless tests explicitly check only behavior-style contracts.
- Key tradeoff: Added configuration complexity (`PERSONA_PROFILE_PATH`) vs. better behavior portability and versioning.
- Safety implications: Persona remains communication guidance only; enforcement still belongs in policy/tool layers.
- What I would do differently next time: Add persona variants and compare them in eval runs before expanding policy/tool features.
- Deep dive: See `docs/persona.md` for implementation details.

### Milestone: Step 3d - Explicit Capability Shipping Rule
- Date: 2026-02-26
- What changed: Promoted `schema + execution path + eval` from an implicit practice to an explicit planning rule.
- What worked: This clarified that golden tasks are necessary but not always sufficient for every capability.
- What failed / surprised me: It is easy to treat “eval” as only one script, which can miss contract-level bugs.
- Key tradeoff: Slightly more process overhead vs. stronger reliability and explainability.
- Safety implications: Reduces risk of shipping partially defined features with unclear boundaries.
- What I would do differently next time: Define required eval types per milestone earlier (golden + targeted checks).

### Milestone: Step 3e - Isolation-First Tooling Plan Update
- Date: 2026-02-26
- What changed: Added an explicit container-isolation milestone for risky tools, including read-only defaults and mount allowlists.
- What worked: This made the safety plan more concrete before shell/network tool power expands.
- What failed / surprised me: It is easy to under-specify isolation details unless they are written as milestone gates.
- Key tradeoff: More implementation overhead vs. lower risk of filesystem/tool misuse.
- Safety implications: Improves blast-radius control for side-effectful tool execution.
- What I would do differently next time: Add isolation-focused eval tasks at the same time as the first risky tool implementation.

### Milestone: Step 4 - Tools + Policy Gateway (Minimal Safe Path)
- Date: 2026-02-27
- What changed: Added typed tool contracts/registry, implemented `read_text_file`, and enforced policy-first tool execution with `allow | deny | require_approval`.
- What worked: A narrow `/tool <name> <json-args>` format kept the execution path explicit and testable.
- What failed / surprised me: User-facing denial text must stay intentionally generic while logs carry richer policy detail.
- Key tradeoff: Minimal capability now vs. strict safety boundaries and auditable decisions.
- Safety implications: Unknown tools are denied by default, side-effectful tools are gated behind `require_approval`, and file reads are repo-scoped.
- What I would do differently next time: Add interactive approval UX and config-driven policy rules as the next incremental hardening steps.

### Milestone: Step 4 P1 - Interactive Approval Prompt
- Date: 2026-02-27
- What changed: Added pending approval state, natural-language approve/deny handling, and auto-cancel on unrelated input.
- What worked: Human-in-the-loop approval made side-effectful tool execution explicit while preserving policy-first architecture.
- What failed / surprised me: Approval parsing needs strict boundaries to avoid accidental confirmations.
- Key tradeoff: Additional interaction step vs. stronger control over side effects.
- Safety implications: Side-effectful actions now require explicit confirmation before execution and pending actions are canceled on context switch.
- What I would do differently next time: Add timeout/expiry and request IDs for more robust pending-approval management.

### Milestone: Step 4 P1b - Config-Driven Policy Rules
- Date: 2026-02-27
- What changed: Moved policy decisions from hardcoded branches to validated JSON rules with explicit schema.
- What worked: Behavior stayed stable while policy became auditable and editable without code changes.
- What failed / surprised me: Hard-fail config loading increases safety but makes malformed config immediately blocking.
- Key tradeoff: Stricter startup/runtime constraints vs. better policy integrity and traceability.
- Safety implications: Missing/invalid policy config now fails closed; reason codes are config-driven while user-safe messaging remains controlled in code.
- What I would do differently next time: Add lightweight tooling to validate policy files before runtime.
