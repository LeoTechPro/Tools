## Context

See proposal.md. The CLI already centralizes profile parsing in `_load_tool_env`, but twelve call sites supply `TOOL_ROOT/.env`. `_tool_tmp_dir` uses `INT_ROOT/.tmp`. The Linux host has private `/home/dev/.config/intdata/credentials`; Windows users retain their historical local paths.

## Goals / Non-Goals

**Goal:** select private external Linux credential and scratch roots in one place without changing profile contents or database gates.

**Non-goals:** change Windows defaults, run a database command, or migrate the obsolete `/int/data` migration workflow.

## Decisions

- Use `${XDG_CONFIG_HOME:-~/.config}/intdata/credentials/dba.env` by default on Linux and support `DBA_ENV_FILE` for an absolute external override. Reject relative and checkout paths; a cwd-dependent fallback would recreate the violation.
- Use system `/tmp` by default on Linux and support an absolute external `DBA_TMP_ROOT`. `tempfile.mkdtemp` creates private mode-`0700` work directories; reject a group/world-writable root without sticky bit. Current `/home/dev/tmp` is group writable without sticky bit, so it is not a safe DBA scratch root. Preserve existing Windows `INT_ROOT/.tmp` behavior.
- Change all call sites to one selector. Move the existing private file, preserving its bytes and mode, only after an exact owner decision. Keep mutation target approval logic unchanged.

## Risks / Trade-offs

- Published source precedes the file move → profile commands fail closed until the approved move; complete the transfer promptly and verify without a DB connection.
- A manually supplied path can expose secrets if permissions are weak → keep the host file in the existing mode-`0700` credential directory with file mode `0600`; do not print values.
- Windows compatibility depends on the old default → leave its path selection unchanged and run the focused Windows-mock tests.

## Migration Plan

Publish the verified source to `origin/dev`; with exact owner approval, move `dba/.env` to the protected user credential path on the same filesystem and compare its SHA-256, mode and owner. Do not invoke a database during cutover. Update current operator documentation; a reverse move needs a separate exact approval.
