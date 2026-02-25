# Publish Checklist

Use this checklist before every public push/release.

## 1) Secrets Hygiene
- [ ] `.env` is not tracked by git.
- [ ] No API keys/tokens/passwords in code, docs, commits, or examples.
- [ ] `.env.example` only contains placeholders.
- [ ] Secret scan run and clean (example: `./scripts/run_gitleaks.sh`).

## 2) Data Safety
- [ ] No personal transcripts, memory snapshots, logs, or local DB files committed.
- [ ] All shared fixtures/examples are synthetic or anonymized.
- [ ] No internal/private filesystem paths in docs or code comments.

## 3) Safe Defaults
- [ ] Risky tools default to disabled or approval-required.
- [ ] Policy gateway deny-by-default behavior is documented.
- [ ] Side-effectful operations are logged with audit metadata.

## 4) Documentation Quality
- [ ] `LEARNING_SPEC.md` is current.
- [ ] `THREAT_MODEL.md` reflects current architecture.
- [ ] `LESSONS_LEARNED.md` includes latest milestone notes.
- [ ] Setup instructions run cleanly on a fresh machine.

## 5) Final Review
- [ ] `git status` reviewed for unexpected files.
- [ ] `git diff --staged` reviewed for accidental leaks.
- [ ] Publish rationale and change summary prepared.
