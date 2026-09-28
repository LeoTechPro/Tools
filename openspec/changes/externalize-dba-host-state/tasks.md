## 1. Source

- [x] 1.1 Centralize the Linux DBA credential and temporary-root selections, preserving Windows defaults and existing database gates.
- [x] 1.2 Update focused tests and current DBA documentation; validate the change.
- [x] 1.3 Publish the verified Tools source to `origin/dev`.

## 2. Host cutover

- [x] 2.1 With exact owner approval, move the existing private DBA profile file to the external credential path and verify bytes, owner, mode and source absence without a DB connection.
