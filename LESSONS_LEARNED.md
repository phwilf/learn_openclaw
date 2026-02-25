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
