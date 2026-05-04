#!/usr/bin/env bash
# audit_static_waits.sh — fail on static waits (sleep/delay)
# SYNC-MANAGED — do not edit in project repos. Edit in shared-docs/ and run sync-standards.sh
# See: shared-docs/docs/adr/ADR-013-multirepo-sync-strategy.md
#
# Usage: bash scripts/audit_static_waits.sh
# Exit code 0 = no violations. Non-zero = violations found.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

PATTERN='(Thread\.sleep\s*\(|time\.sleep\s*\(|Task\.Delay\s*\()'
ALLOW_PATH_REGEX='(/utils/|/extensions/|/error_handler\.py$)'

echo -e "${YELLOW}▶ Audit: static waits (Thread.sleep / time.sleep / Task.Delay)${NC}"

VIOLATIONS=0

while IFS= read -r match_line; do
  file="$(echo "$match_line" | cut -d: -f1)"
  line="$(echo "$match_line" | cut -d: -f2)"
  match="$(echo "$match_line" | cut -d: -f3-)"

  if [[ "$file" =~ $ALLOW_PATH_REGEX ]]; then
    continue
  fi

  VIOLATIONS=$((VIOLATIONS + 1))
  echo -e "${RED}❌ Static wait found${NC} → $file:$line → $match"
done < <(
  grep -rn --binary-files=without-match -E "$PATTERN" \
    "$REPO_ROOT" \
    --include="*.py" \
    --include="*.java" \
    --include="*.cs" \
    --include="*.ts" \
    --include="*.tsx" \
    --include="*.js" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    --exclude-dir=target \
    --exclude-dir=bin \
    --exclude-dir=obj \
    --exclude-dir=.venv \
    --exclude-dir=venv \
    --exclude-dir=venv-enhanced \
    --exclude-dir=.pytest_cache \
    --exclude-dir=__pycache__ \
    --exclude-dir=allure-results \
    --exclude-dir=allure-report \
    --exclude-dir=test-results \
    --exclude-dir=playwright-report \
    --exclude-dir=docs \
    --exclude-dir=documentation \
    2>/dev/null || true
)

echo ""
if [[ $VIOLATIONS -eq 0 ]]; then
  echo -e "${GREEN}✅ audit_static_waits.sh — 0 violations found.${NC}"
else
  echo -e "${RED}❌ audit_static_waits.sh — $VIOLATIONS violation(s) found. Remove static waits before merging.${NC}"
fi

exit $VIOLATIONS
