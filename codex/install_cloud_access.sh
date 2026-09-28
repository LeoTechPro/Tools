#!/usr/bin/env bash
set -euo pipefail

SCRIPT_ROOT="/home/dev/int/tools/codex"
"$SCRIPT_ROOT/cloud_access.sh" ensure-dirs

cat <<'EOF'
Cloud access directories are prepared outside the source checkout.

Next steps:
  1. Run `/home/dev/int/tools/codex/cloud_access.sh config`
  2. Create remotes `gdrive` (drive) and `yadisk` (yandex)
  3. Install a reviewed user unit from `codex/systemd/` only if a new mount is needed.
EOF
