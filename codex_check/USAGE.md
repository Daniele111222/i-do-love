# Codex Session Sync - AI Notes

`codex_check` 是一个独立的 Codex Desktop 本地会话同步 CLI。只处理 `codex_check/` 目录内的工具代码和文档；不要把外层 `i-do-love` 项目当作同一个包来改。

## Scope

同步目标：

- `.codex/sessions/**/rollout-*.jsonl`
- `.codex/session_index.jsonl` 中对应 thread 条目
- `.codex/.codex-global-state.json` 中少量 thread 状态字段

绝不同步：

- `auth.json`
- `installation_id`
- `cap_sid`
- `*.sqlite`, `*.sqlite-wal`, `*.sqlite-shm`
- `.sandbox-secrets`
- `cache`, `plugins`, `node_repl`
- 日志数据库

两台设备必须各自已正常登录 Codex。

## Entry Points

```powershell
# module entry
C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m codex_check --help

# wrapper script
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --help

# editable install, from codex_check/
C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m pip install -e .
codex-sync --help
```

Packaging metadata is local to `codex_check/pyproject.toml`.

## Config

Default config path:

```text
codex_check/codex-sync.json
```

Initialize:

```powershell
codex-sync init --codex-root "%USERPROFILE%\.codex" --sync-dir "D:\codex-session-sync" --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --scope project --max-backups 10
```

Use custom config:

```powershell
codex-sync --config "D:\codex-session-sync\codex-sync.json" init --codex-root "%USERPROFILE%\.codex" --sync-dir "D:\codex-session-sync" --project "<项目路径>"
```

After config exists, preferred commands:

```powershell
codex-sync doctor
codex-sync push
codex-sync diff
codex-sync pull --dry-run
codex-sync pull
codex-sync status
codex-sync rollback
```

## Explicit Commands

```powershell
run_sync.cmd doctor --codex-root "%USERPROFILE%\.codex" --project "<项目路径>" --sync-dir "<同步目录>"
run_sync.cmd push --codex-root "%USERPROFILE%\.codex" --project "<项目路径>" --sync-dir "<同步目录>"
run_sync.cmd push --codex-root "%USERPROFILE%\.codex" --all --sync-dir "<同步目录>"
run_sync.cmd diff --codex-root "%USERPROFILE%\.codex" --sync-dir "<同步目录>"
run_sync.cmd pull --codex-root "%USERPROFILE%\.codex" --sync-dir "<同步目录>" --dry-run
run_sync.cmd pull --codex-root "%USERPROFILE%\.codex" --sync-dir "<同步目录>"
run_sync.cmd import --codex-root "%USERPROFILE%\.codex" "<导出包.zip>" --dry-run
run_sync.cmd rollback --codex-root "%USERPROFILE%\.codex"
```

`--sync-dir` must be a real directory path. Placeholder values such as `你的同步盘目录` and `<同步目录>` are rejected intentionally.

## Safe Workflow

1. Close Codex Desktop.
2. On source device: `push`.
3. Wait for sync drive to finish syncing.
4. On target device: `diff`.
5. Run `pull --dry-run`.
6. If report is acceptable, run `pull`.
7. Reopen Codex Desktop.
8. Use `rollback` if imported sessions are wrong.

`diff` reports:

- `matching`: same thread id and same content.
- `remote_only`: sync drive has it, local does not.
- `local_only`: local has it, sync drive does not.
- `conflicted`: same thread id, different content.

## Conflict Policy

Default behavior: conflicting thread id with different content is not overwritten.

```powershell
run_sync.cmd import "<导出包.zip>" --conflict skip
run_sync.cmd import "<导出包.zip>" --conflict overwrite
run_sync.cmd import "<导出包.zip>" --conflict keep-both
```

- `skip`: record as `conflicted`, preserve local file.
- `overwrite`: replace local session file.
- `keep-both`: copy remote session as a new thread id.

Always prefer `--dry-run` before `overwrite` or `keep-both`.

## Reliability Rules

- Import creates backup under `.codex/session-sync-backups/<timestamp>/`.
- Import writes `.codex/session-sync-last-import-report.json`.
- `--max-backups N` prunes old import backups.
- Zip import rejects unsafe paths such as `../...` and absolute paths.
- Export packages contain `manifest.json`, `sessions/`, `session_index.jsonl`, and `global_state_patch.json`.

## Tests

Run from repository root:

```powershell
C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover -s codex_check\tests -v
```

Current coverage includes project export filtering, import/index merge, conflict handling, dry-run, keep-both, overwrite, unsafe zip rejection, diff, backup pruning, config init, package entrypoint, and rollback.
