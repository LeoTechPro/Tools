"""Reject vault maintenance destinations inside development and scratch trees."""

from pathlib import Path

BACKUP_ROOT = Path("/home/dev/backup")


def require_runtime_root(path: Path) -> None:
    forbidden = (
        Path("/home/dev/int"),
        Path("/int"),
        Path("/home/dev/tmp"),
        Path("/home/dev/backup"),
        Path("/tmp"),
        Path("/var/tmp"),
        Path("/run"),
    )
    if any(path.is_relative_to(root) for root in forbidden):
        raise ValueError(f"runtime_root_not_installed_state: {path}")


def require_archive_root(path: Path, runtime_root: Path) -> None:
    if not path.is_relative_to(BACKUP_ROOT):
        raise ValueError(f"archive_root_not_backup_storage: {path}")
    if path.is_relative_to(runtime_root) or runtime_root.is_relative_to(path):
        raise ValueError("runtime_and_archive_roots_overlap")
    if not path.is_dir() or path.stat().st_mode & 0o077:
        raise ValueError(f"private_archive_root_required: {path}")
