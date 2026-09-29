# Vault Installers / Sanitize

## `vault_sanitize.py`

Idempotent cleanup script that keeps Obsidian vault content in `/2brain` (or `D:\Yandex.Disk\2brain`) and moves operational artifacts into an explicitly selected installed state directory and installer paths in `int/tools`.

### Local

```powershell
python d:\int\tools\vault\installers\vault_sanitize.py --dry-run
python d:\int\tools\vault\installers\vault_sanitize.py --apply
python d:\int\tools\vault\installers\vault_sanitize.py --dry-run --runtime-root D:\int\.tmp\brain-runtime-vault
```

### VDS

The development checkout contains code only. The example destination below is
a planning candidate, not a provisioned or approved runtime. Check the actual
service owner, provision its private state directory outside the checkout, and
review the full move/delete plan before an individually authorized `--apply`.
Linux `--apply` requires `--runtime-root` and refuses source, scratch and
backup directories as live state.

```bash
python3 -B /home/dev/int/tools/vault/installers/vault_sanitize.py --vault-root /2brain --brain-root /home/dev/int/brain --tools-root /home/dev/int/tools --runtime-root /var/lib/intdata/brain-runtime-vault --dry-run
```

### Whitelist profile

```powershell
python d:\int\tools\vault\installers\vault_sanitize.py --profile strict --dry-run
python d:\int\tools\vault\installers\vault_sanitize.py --profile strict --apply
```

`--enforce-whitelist` is kept as a deprecated alias for `--profile strict`.

`--runtime-root` is optional for dry-run and Windows compatibility. Linux dry-run
defaults to the unprovisioned candidate `/var/lib/intdata/brain-runtime-vault`;
Linux `--apply` still requires an explicit external path. Historical defaults:
- Local: `D:\int\.tmp\brain-runtime-vault`
- Old VDS: `/int/.tmp/brain-runtime-vault` (removed)

Legacy path `/int/brain/runtime/vault` (when already on VDS) is supported only as explicit override and emits a deprecation warning.

## `runtime_vault_gc.py`

Archives and resets generated vault runtime artifacts only with explicit Linux
state and private backup paths. It never treats `/home/dev/tmp` as a backup.

```powershell
python d:\int\tools\vault\installers\runtime_vault_gc.py --dry-run
python d:\int\tools\vault\installers\runtime_vault_gc.py --apply
python d:\int\tools\vault\installers\runtime_vault_gc.py --dry-run --runtime-root D:\int\.tmp\brain-runtime-vault
```

VDS:

The backup destination must already exist with private mode `0700` under
`/home/dev/backup`. The example paths are candidates for review; no current
service is configured to use them by this README. If a legacy runtime exists
inside the checkout, Linux `--apply` stops and requires a separate, exact move
decision instead of recreating that directory.

```bash
python3 -B /home/dev/int/tools/vault/installers/runtime_vault_gc.py --brain-root /home/dev/int/brain --runtime-root /var/lib/intdata/brain-runtime-vault --archive-root /home/dev/backup/brain-runtime-vault --dry-run
```
