## Why

The Linux intDBA CLI still discovers credentials from `dba/.env` and creates dumps and other scratch under the source checkout's `.tmp`. The canonical Linux checkout must contain source only.

## What Changes

- **BREAKING on Linux:** load DBA profiles from the protected user configuration directory, with an explicit absolute `DBA_ENV_FILE` override; do not fall back to checkout `.env`.
- Place sensitive Linux DBA scratch in private directories under system `/tmp` by default, with a safe explicit `DBA_TMP_ROOT` override. Preserve the existing Windows paths for compatibility.
- Move the existing 400-byte Linux profile file to the external private credential store after exact owner approval. Do not connect to or mutate a database as part of the move.

## Capabilities

### New Capabilities

- `dba-host-state-boundary`: Linux intDBA reads credentials and writes scratch outside the development source checkout.

### Modified Capabilities

None.

## Impact

`dba/lib/dba.py`, its focused tests and current DBA documentation. Operator invocations using the old implicit checkout file must use the external default or `DBA_ENV_FILE`; database targets and mutation gates remain unchanged.
