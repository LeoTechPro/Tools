#!/usr/bin/env python3
"""Check that Linux SQL recovery snapshots cannot land in source or scratch."""

import os
from pathlib import Path

from backup_snapshot import BackupError, _default_backup_base, _ensure_backup_base


def test_linux_backup_custody() -> None:
    if os.name == "nt":
        return
    assert _default_backup_base() == Path("/home/dev/backup").resolve()
    _ensure_backup_base(Path("/home/dev/backup/review-sql-fix"))
    for path in ("/home/dev/tmp", "/home/dev/int", "/int/.tmp"):
        try:
            _ensure_backup_base(Path(path))
        except BackupError:
            continue
        raise AssertionError(f"accepted non-backup path: {path}")


if __name__ == "__main__":
    test_linux_backup_custody()
