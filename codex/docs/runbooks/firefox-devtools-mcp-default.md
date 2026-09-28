# Firefox DevTools MCP Default Runtime

Canonical agent workflow: `firefox-devtools-testing` in the `intdata-runtime` plugin. Use it for local browser-proof, persistent authenticated Firefox profiles, screenshots, console/network evidence, privileged scripts, prefs, and extension diagnostics.

## Назначение

Этот runbook фиксирует browser-proof runtime для `/home/dev/int/*` на Linux и `D:/int/*` на Windows: dedicated `firefox-devtools-mcp@0.9.1` с persistent profile и launcher-ами из `tools/codex/bin/**`.

## Prerequisites

- `node` и `npx` доступны в `PATH`;
- установлен Firefox 100+;
- project overlay подключён native Codex/OpenClaw mechanism; repo scripts не синхронизируют Codex home;
- browser-proof не использует owner browser profile как default-path.

## Runtime layout

- Linux profiles: `${XDG_STATE_HOME:-$HOME/.local/state}/intdata-tools/firefox-mcp/profiles/<profile>/`
- Linux logs: `${XDG_STATE_HOME:-$HOME/.local/state}/intdata-tools/firefox-mcp/logs/<profile>/`
- Linux run meta: `${XDG_STATE_HOME:-$HOME/.local/state}/intdata-tools/firefox-mcp/run/<profile>.json`
- Windows: `D:/int/tools/.runtime/firefox-mcp/` с теми же подкаталогами.

## Wrapper contract

- generic launcher: `D:/int/tools/codex/bin/mcp-firefox-devtools.ps1`
- thin entrypoint for MCP client: `D:/int/tools/codex/bin/mcp-firefox-devtools.cmd`
- profile wrappers задают только controlled inputs: `ProfileKey`, `StartUrl`, `Viewport`, `Visible`
- default mode: headless
- persistent state живёт только в profile directory

## Как запускать

- generic dry-run:
  - `pwsh -File D:/int/tools/codex/bin/mcp-firefox-devtools.ps1 -ProfileKey firefox-default -StartUrl http://127.0.0.1:8080/ -DryRun`
- generic MCP entry:
  - `D:/int/tools/codex/bin/mcp-firefox-default.cmd`
- project overlays:
  - `/home/dev/int/tools/codex/projects/int/.mcp.json` на Linux
  - `/home/dev/int/tools/codex/projects/assess/.mcp.json` на Linux

## Логи и диагностика

- stderr launcher-а и upstream MCP сервера пишутся в Linux state root `firefox-mcp/logs/<profile>/stderr.log`
- активный launcher отмечается файлом в Linux state root `firefox-mcp/run/<profile>.json`
- повторный запуск того же profile-key поверх живого launcher-а запрещён

## Reset одного profile

1. Убедиться, что run-meta для profile отсутствует.
2. При необходимости закрыть активный MCP session.
3. После отдельного точного разрешения удалить только `${XDG_STATE_HOME:-$HOME/.local/state}/intdata-tools/firefox-mcp/profiles/<profile>/` на Linux.
4. Не трогать соседние role-профили и общие логи.

## Fallback в owner Chrome

Owner Chrome допустим только если Firefox runtime:

- не стартует;
- не покрывает нужный debug-case;
- или профиль повреждён и нужен срочный unblock.

В handoff обязательно фиксируются причина fallback и Firefox-артефакты, которых не хватило.
