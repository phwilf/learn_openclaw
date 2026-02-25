#!/usr/bin/env bash
set -euo pipefail

if [ ! -d .git ]; then
  echo "This directory is not a git repository yet."
  echo "Run: git init"
  exit 1
fi

if command -v pre-commit >/dev/null 2>&1; then
  pre-commit install
  echo "Installed pre-commit hook via pre-commit."
  if ! command -v gitleaks >/dev/null 2>&1; then
    echo "Warning: gitleaks not found; commits will fail until it is installed."
  fi
  exit 0
fi

echo "pre-commit is not installed; installing direct git hook fallback."
mkdir -p .git/hooks
cat > .git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
"$(git rev-parse --show-toplevel)/scripts/run_gitleaks.sh"
EOF
chmod +x .git/hooks/pre-commit
echo "Installed .git/hooks/pre-commit fallback hook."
if ! command -v gitleaks >/dev/null 2>&1; then
  echo "Warning: gitleaks not found; commits will fail until it is installed."
fi
