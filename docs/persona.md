# Persona Layer Deep Dive

## What It Is
A persona layer is a stable instruction contract that defines how the assistant behaves:
- tone and communication style
- response defaults (concise vs detailed, clarification behavior)
- boundaries for transparency and uncertainty
- escalation style when requests are risky or ambiguous

It is behavior policy, not business logic.

## What It Is Not
- Not memory: memory stores facts/state across turns.
- Not a policy gateway: hard allow/deny checks belong in policy/tool controls.
- Not jailbreak-proof security: persona helps steer behavior but does not replace enforcement layers.

## Why It Matters
- Consistency: users get predictable behavior across sessions.
- Portability: behavior remains stable when model/provider changes.
- Evaluability: you can test persona traits with repeatable tasks.
- Product identity: assistant tone and interaction style become intentional, not accidental.

## Best Practices
1. Keep persona instructions high priority and separate from user content.
2. Keep persona concise and structured (identity, defaults, do/don't).
3. Separate persona concerns from safety/policy enforcement code.
4. Version persona changes and evaluate regressions before shipping.
5. Add small focused persona tests (tone, uncertainty handling, refusal style).

## Suggested Minimal Persona Spec (for implementation later)
- `name`: short persona label
- `style`: concise communication defaults
- `principles`: behavior priorities in order
- `constraints`: prohibited response patterns
- `escalation`: what to do when uncertain or blocked

## Current Implementation (Step 3b)
- Profile schema and loader: `src/local_assistant/persona/profile.py`
- Default profile: `src/local_assistant/persona/default.json`
- Prompt construction boundary: `src/local_assistant/core_loop/prompt_builder.py`
- Core loop integration: `src/local_assistant/core_loop/loop.py`
- Validation checks: `scripts/run_golden_tasks.py`

## Initial Persona Evaluation Ideas
- Tone consistency on short factual prompts.
- Uncertainty handling when the answer is unknown.
- Refusal style consistency for unsafe requests.
- Verbosity adherence (concise by default unless asked otherwise).
