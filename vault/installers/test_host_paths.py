import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

import host_paths
import runtime_vault_gc
import vault_sanitize


class HostPathPolicyTest(unittest.TestCase):
    def test_linux_planning_defaults_stay_outside_checkout(self):
        if os.name == "nt":
            self.skipTest("Linux host path policy")
        brain_root = Path("/home/dev/int/brain")
        expected = Path("/var/lib/intdata/brain-runtime-vault")
        self.assertEqual(runtime_vault_gc.canonical_runtime_root(brain_root), expected)
        self.assertEqual(vault_sanitize.canonical_runtime_root(brain_root), expected)

    def test_live_state_stays_outside_source_scratch_and_backups(self):
        for path in ("/home/dev/int/brain/.tmp", "/home/dev/tmp/vault", "/home/dev/backup/vault", "/int/.tmp/vault", "/var/tmp/vault"):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "runtime_root_not_installed_state"):
                host_paths.require_runtime_root(Path(path))
        host_paths.require_runtime_root(Path("/var/lib/intdata/brain-runtime-vault"))

    def test_archives_require_private_backup_storage(self):
        runtime = Path("/var/lib/intdata/brain-runtime-vault")
        with self.assertRaisesRegex(ValueError, "archive_root_not_backup_storage"):
            host_paths.require_archive_root(Path("/home/dev/tmp/vault"), runtime)
        with TemporaryDirectory() as directory:
            os.chmod(directory, 0o700)
            backup = Path(directory)
            with patch.object(host_paths, "BACKUP_ROOT", backup):
                host_paths.require_archive_root(backup, runtime)
                os.chmod(directory, 0o755)
                with self.assertRaisesRegex(ValueError, "private_archive_root_required"):
                    host_paths.require_archive_root(backup, runtime)


if __name__ == "__main__":
    unittest.main()
