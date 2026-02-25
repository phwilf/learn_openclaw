# Security Setup

This project uses `gitleaks` to scan staged changes for potential secrets before commit.

## Prerequisites
- A git repository initialized in this folder (`git init`)
- `gitleaks` installed
- Optional: `pre-commit` installed

## Install Hook
Run:

```bash
./scripts/install_hooks.sh
```

Behavior:
- If `pre-commit` is installed, it installs a standard `pre-commit` hook using `.pre-commit-config.yaml`.
- If `pre-commit` is not installed, it installs a direct `.git/hooks/pre-commit` fallback that runs `scripts/run_gitleaks.sh`.

## Run Scan Manually

```bash
./scripts/run_gitleaks.sh
```

## Config
- `.gitleaks.toml` contains local allowlist settings.
- Keep allowlists minimal and document any additions in commit messages.
