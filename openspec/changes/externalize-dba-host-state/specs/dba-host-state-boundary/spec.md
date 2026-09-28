## Purpose

Keep the Linux DBA operator tool usable while its credentials and generated files live outside the development source checkout.

## ADDED Requirements

### Requirement: Linux DBA credentials are external
On Linux, intDBA MUST load profile values from a private user configuration file outside the managed source checkout, or from a caller-supplied absolute external path. It MUST NOT implicitly load `dba/.env` from the checkout. Missing profiles MUST fail before a database command executes.

#### Scenario: Operator uses the external default
- **WHEN** an operator runs a profile command without `DBA_ENV_FILE`
- **THEN** intDBA reads the private XDG user credentials file
- **AND** it does not inspect a checkout `.env`

#### Scenario: Explicit path targets source
- **WHEN** an operator supplies a relative `DBA_ENV_FILE` or one inside the managed checkout
- **THEN** intDBA refuses that path before reading credentials

### Requirement: Linux DBA scratch is external
On Linux, intDBA MUST create dumps and temporary work in private mode-`0700` directories under a safe external temporary root and MUST NOT create a `.tmp` directory in the checkout. A group/world-writable root without sticky bit MUST be refused.

#### Scenario: Tool creates a dump workdir
- **WHEN** intDBA creates a temporary dump directory on Linux
- **THEN** the directory is under `/tmp` or an explicit absolute safe external `DBA_TMP_ROOT`
- **AND** its mode is `0700` even when the process umask is `0002`
