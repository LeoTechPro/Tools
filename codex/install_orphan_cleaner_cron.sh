#!/usr/bin/env bash
set -euo pipefail

CLEANER_BIN="${CODEX_ORPHAN_CLEANER_BIN:-}"
if [[ ! "$CLEANER_BIN" =~ ^/usr/local/lib/intdata/[A-Za-z0-9._/-]+$ ]]; then
  echo "CODEX_ORPHAN_CLEANER_BIN must name an installed executable outside the checkout" >&2
  exit 2
fi
if ! CLEANER_BIN="$(realpath -e -- "$CLEANER_BIN" 2>/dev/null)" || [[ "$CLEANER_BIN" != /usr/local/lib/intdata/* || ! -x "$CLEANER_BIN" ]]; then
  echo "CODEX_ORPHAN_CLEANER_BIN must name an installed executable outside the checkout" >&2
  exit 2
fi
CANONICAL_CMD="*/5 * * * * $CLEANER_BIN >/dev/null 2>&1 # probe-agent-orphan-cleaner"
TMP_FILE="$(mktemp)"
trap 'rm -f "$TMP_FILE"' EXIT

(crontab -l 2>/dev/null || true) > "$TMP_FILE"

# Remove legacy and duplicate cleaner entries, keep unrelated crons untouched.
sed -i '/probe-agent-orphan-cleaner/d;/codex-agent-orphan-cleaner/d;/cleanup-agent-orphans\.sh/d;/cleanup_agent_orphans\.sh/d' "$TMP_FILE"

printf '%s\n' "$CANONICAL_CMD" >> "$TMP_FILE"
crontab "$TMP_FILE"

echo "installed canonical cleaner cron entry:"
crontab -l | rg 'probe-agent-orphan-cleaner|cleanup-agent-orphans\.sh|cleanup_agent_orphans\.sh' || true
