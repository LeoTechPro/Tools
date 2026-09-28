# intDBA

`intDBA` — self-contained operator CLI для remote Postgres/Supabase профилей с этой Windows-машины без SSH на DB-host.

## Что умеет v1

- `doctor` — проверить native PostgreSQL CLI, TCP и SQL-доступ к профилю;
- `sql` — выполнить ad-hoc SQL;
- `file` — выполнить SQL-файл;
- `dump` / `restore` — выгрузить и залить dump;
- `clone` — перенести dump из одной БД в другую через локальную машину;
- `copy` — выгрузить query в CSV и залить в target table;
- `migrate status` — исторический flow `migration_manifest.lock`/`public.schema_migrations` для явно выбранного legacy data repo;
- `migrate data` — исторический incremental или bootstrap flow явно выбранного legacy data repo. Действующий Platform использует собственный native runner.
- `project-migrate punktb-legacy-assess` — перенести legacy PunktB assessment data между профилями через `psql` staging flow.
- `project-migrate punktb-prod-dev-refresh` — перезалить `assess.specialists`, `assess.clients`, `assess.diag_results` из `punkt_b_prod` в `intdata` dev со strict read-only source и dev-side `auth` bootstrap.
- `local-test run` — поднять temporary local Supabase runtime под owner-контролем для явно выбранного legacy data repo и опционально прогнать SQL smoke.
- `local-test stop` — остановить temporary local Supabase runtime без backup.

## Layout

- `dba.ps1` / `dba.cmd` — основные launchers;
- `lib/dba.py` — Python core;
- `.env.example` — bootstrap-шаблон профилей;
- Linux: `${XDG_CONFIG_HOME:-~/.config}/intdata/credentials/dba.env` — приватный файл профилей (`0600`), `DBA_ENV_FILE` задаёт явный абсолютный путь вне checkout;
- Linux: приватные каталоги `0700` в `/tmp/intdata-dba-*` — временные выгрузки и рабочие файлы; `DBA_TMP_ROOT` задаёт явный абсолютный внешний корень без групповой/общей записи либо со sticky bit;
- Windows сохраняет локальные `dba/.env` и `D:\int\.tmp\tools\dba\` до отдельной миграции.

## Требования

- Windows: PowerShell; Linux: запуск `python3 lib/dba.py`;
- `python` или `py` в `PATH` на Windows, `python3` на Linux;
- `psql`, `pg_dump`, `pg_restore` в `PATH` или в стандартном каталоге `C:\Program Files\PostgreSQL\<version>\bin`;
- сетевой доступ до нужных PostgreSQL endpoint'ов;
- для исторического `migrate *` требуется явно выбрать совместимый legacy repo через `--repo` или `DBA_DATA_REPO`; действующий Platform Backend находится в `/home/dev/int/platform` и использует `scripts/supabase-db-apply.sh`;
- для `migrate data --mode incremental`: `bash` из Git for Windows или иной совместимый `bash`.

## Профили

Формат переменных:

```env
DBA_PROFILE__INTDATA_DEV__PGHOST=api.intdata.pro
DBA_PROFILE__INTDATA_DEV__PGPORT=5432
DBA_PROFILE__INTDATA_DEV__PGDATABASE=intdatadb-dev
DBA_PROFILE__INTDATA_DEV__PGUSER=intdata_dev
DBA_PROFILE__INTDATA_DEV__PGPASSWORD=<secret>
DBA_PROFILE__INTDATA_DEV__PGSSLMODE=require
DBA_PROFILE__INTDATA_DEV__WRITE_CLASS=nonprod
```

CLI обращается к такому профилю как `intdata-dev`.

`WRITE_CLASS`:

- `nonprod` — достаточно `--approve-target <profile>`;
- `prod` — дополнительно требуется `--force-prod-write`.

## Guardrail entrypoints (Punkt-B)

Для безопасной модели доступа используйте Python wrappers из `D:\int\tools\dba\bin`:

- `pg-prod-ro.py` -> `punktb-prod-ro` (`db_readonly_prod`)
- `pg-legacy-ro.py` -> `punktb-legacy-ro` (`db_readonly_prod` on `punkt_b_legacy_prod`)
- `pg-dev-ro.py` -> `intdata-dev-ro` (`db_readonly_dev`)
- `pg-prod-migrate.py` -> `punktb-prod-migrator` (`db_migrator_prod`)
- `pg-dev-migrate.py` -> `intdata-dev-migrator` (`db_migrator_dev`)
- `pg-prod-admin.py` -> `punktb-prod-admin` (`agents`, breakglass)
- `pg-dev-admin.py` -> `intdata-dev-admin` (`agents`, breakglass)
- `pg-test-bootstrap.py` -> retired stop-signal; remote disposable test contour больше не поддерживается

На Linux из `/home/dev/int/tools/dba` (на Windows используйте `python` и путь `D:\int\tools\dba`):

```bash
python3 bin/pg-prod-ro.py --doctor
python3 bin/pg-dev-migrate.py --path /path/to/change.sql --write --confirm-target intdata
```

### Важно

- Supabase system roles (`authenticator`, `anon`, `authenticated`, `service_role`, `supabase_*`) в этой модели считаются immutable.
- Wrappers должны использовать только custom роли.
- Raw `psql` с ad-hoc DSN для agent workflow запрещен process-policy.
- Исторические инструкции для `/int/data` не являются действующим dev workflow. Для Platform Backend используйте его текущий native runner и отдельные DB gates.

## Local disposable Supabase runner

Исторический disposable workflow требует явно выбранный совместимый legacy repo; этот пример не подтверждает текущую Platform migration history:

```bash
pwsh -File D:\int\tools\dba\dba.ps1 local-test run --repo '<legacy-data-repo>' --confirm-owner-control I_ACKNOWLEDGE_LOCAL_ONLY
```

Основные свойства:

- нужен Docker;
- нужен Supabase CLI (`supabase`) или fallback через `npx supabase`;
- на Linux workspace создаётся вне checkout в приватном `/tmp/intdata-dba-local-supabase-*`; Windows сохраняет `D:\int\.tmp\tools\dba\`;
- после `supabase start` tool применяет owner scripts из явно переданного локального repo (`--repo`/`DBA_DATA_REPO`), затем `init/seed.sql`;
- SQL smoke можно передать через `--smoke-file`;
- по умолчанию runtime останавливается сам; для ручной диагностики используйте `--keep-running` и затем `local-test stop`.

## PunktB legacy assessment migrator

Core workflow lives in `dba`; project-specific PunktB launch parameters are thin wrappers.

Rehearsal against dev target:

```bash
python D:\int\tools\dba\lib\dba.py project-migrate punktb-legacy-assess --dry-run --source punktb-legacy-ro --target intdata-dev-migrator
```

Release apply target remains guarded:

```bash
python D:\int\tools\dba\lib\dba.py project-migrate punktb-legacy-assess --apply --source punktb-legacy-ro --target punktb-prod-migrator --approve-target punktb-prod-migrator --force-prod-write
```

Properties:

- source profile is executed read-only;
- target apply uses the existing `--approve-target` and `--force-prod-write` gates;
- dry-run stages target changes and rolls them back;
- clients are matched by normalized email, not numeric legacy ids;
- duplicate legacy client rows with the same normalized email merge into one target client;
- legacy `public.clients.results` JSONB array entries are staged into `assess.diag_results` with deterministic ids and `_import.legacy_punktb` metadata.

## PunktB prod -> intdata dev refresh

Dry-run against the approved dev admin target:

```bash
python D:\int\tools\dba\lib\dba.py project-migrate punktb-prod-dev-refresh --dry-run --source punktb-prod-ro --target intdata-dev-admin
```

Apply with full replace semantics in the approved dev scope:

```bash
python D:\int\tools\dba\lib\dba.py project-migrate punktb-prod-dev-refresh --apply --source punktb-prod-ro --target intdata-dev-admin --approve-target intdata-dev-admin
```

Properties:

- source export stays read-only and uses `psql \copy (SELECT row_to_json(...))`, not `pg_dump`;
- fallback source `punktb-prod-migrator` is allowed only when the session is still forced into `default_transaction_read_only=on`;
- target requires `intdata-dev-admin` (`agents` on `intdata`), because the workflow fully replaces the approved dev rows;
- target bootstraps only the required `auth.users` and `auth.identities` rows for imported emails and does not read prod auth tables.

## Safety

- Все mutating-команды требуют явный `--approve-target`.
- Для профилей класса `prod` обязателен `--force-prod-write`.
- `sql` и `file` по умолчанию запускаются в `default_transaction_read_only=on`.
- `local-test run` требует `--confirm-owner-control I_ACKNOWLEDGE_LOCAL_ONLY` и не имеет unattended default path.
- Типовые runtime-ошибки `psql/pg_dump/pg_restore`, `bash` и TCP-доступа переводятся в обычные `intDBA:` сообщения без Python traceback.
- Типовые runtime-ошибки `docker` и `supabase` для local runner тоже переводятся в обычные `intDBA:` сообщения.
- Секреты профиля передаются внешним PostgreSQL CLI через окружение процесса и не вшиваются в argv.
- Для `migrate data --mode incremental` `dba` сам добавляет найденный PostgreSQL `bin` в `PATH` дочернего `bash`, если глобальный `PATH` на машине ещё не обновлён.
- На Linux временные dump/CSV-файлы складываются в приватные каталоги `/tmp/intdata-dba-*`, а секреты читаются из защищённого внешнего файла; checkout `.env` не подхватывается.
