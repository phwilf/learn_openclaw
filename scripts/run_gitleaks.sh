#!/usr/bin/env bash
set -euo pipefail

if ! command -v gitleaks >/dev/null 2>&1; then
  echo "gitleaks is not installed."
  echo "Install it first, then retry. See scripts/install_hooks.sh for setup."
  exit 1
fi

CONFIG_FLAG=(--config .gitleaks.toml)

# Prefer the modern command shape when available.
if gitleaks help git >/dev/null 2>&1; then
  exec gitleaks git --staged --redact "${CONFIG_FLAG[@]}"
fi

# Fall back for older gitleaks versions.
if gitleaks help protect >/dev/null 2>&1; then
  exec gitleaks protect --staged --redact "${CONFIG_FLAG[@]}"
fi

echo "Could not find a compatible gitleaks command (expected 'git' or 'protect')."
exit 1
