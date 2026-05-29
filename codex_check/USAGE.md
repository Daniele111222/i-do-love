# Codex Session Sync 使用说明

## 这个工具做什么

`codex_check` 是一个 Codex Desktop 本地会话同步原型工具。它通过导出、导入 `.codex` 中的会话文件，让另一台设备尽量能在 Codex Desktop 原生会话列表中看到并继续历史会话。

第一版推荐用法是“本地导出包 + 同步盘目录”：

- 设备 A 生成导出包，并放入同步盘目录。
- 设备 B 从同步盘目录拉取并导入。
- 两台设备各自保持正常登录 Codex，不同步认证文件。

## 运行环境

工具是零依赖 Python CLI，只使用 Python 标准库。

推荐在 Windows 上使用包装脚本，这样不管你当前在哪个项目目录，都能运行到本仓库里的 `codex_check`：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --help
```

也可以在 `i-do-love` 仓库根目录中直接使用内置 Python：

```powershell
C:\Users\hyperchain\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m codex_check.sync_tool --help
```

如果系统已经安装 Python，并且当前目录就是 `i-do-love` 仓库根目录，也可以使用：

```powershell
python -m codex_check.sync_tool --help
```

以下示例默认使用 `run_sync.cmd`。这是当前推荐方式，因为它不依赖你所在的终端目录。

如果你在其他项目目录中运行，例如 `C:\Users\hyperchain\Desktop\personal_auth_h5`，必须优先使用 `run_sync.cmd`，否则 Python 可能找不到 `codex_check` 包。

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" doctor --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --sync-dir "D:\codex"
```

## 同步盘目录怎么填

`--sync-dir` 必须是真实存在或可创建的同步目录，不能把文档里的 `你的同步盘目录` 原样复制进去。

可用示例：

```powershell
C:\Users\你的用户名\OneDrive\codex-session-sync
D:\Syncthing\codex-session-sync
Z:\codex-session-sync
```

如果传入 `你的同步盘目录`、`<同步目录>` 这类占位文字，工具会直接报错，避免静默写到错误位置。

## 同步内容

会同步：

- `.codex/sessions/**/rollout-*.jsonl`
- 对应的 `.codex/session_index.jsonl` 条目
- 少量 thread 相关状态字段

不会同步：

- `auth.json`
- `installation_id`
- `cap_sid`
- `*.sqlite`
- `*.sqlite-wal`
- `*.sqlite-shm`
- `.sandbox-secrets`
- `cache`
- `plugins`
- `node_repl`
- 日志数据库

因此，两台设备需要各自已经正常登录 Codex。

## 命令总览

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" doctor --project "<项目路径>" --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" export --project "<项目路径>" --output-dir "<导出目录>"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" export --all --output-dir "<导出目录>"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "<导出包.zip>"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" push --project "<项目路径>" --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" push --all --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" pull --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" status --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" diff --sync-dir "C:\Users\你的用户名\OneDrive\codex-session-sync"
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" rollback
```

## 按项目导出

只导出某一个项目路径相关的会话：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" export --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --output-dir "D:\codex-session-sync\exports"
```

产出示例：

```text
D:\codex-session-sync\exports\codex-session-export-project-20260528-153000.zip
```

项目匹配规则：

- 读取 session JSONL 第一条 `session_meta.payload.cwd`。
- 与 `--project` 传入的路径做标准化比较。
- Windows 下大小写不敏感。
- 缺少 `cwd` 的 session 在项目导出中会被跳过。

## 导出全部会话

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" export --all --output-dir "D:\codex-session-sync\exports"
```

产出示例：

```text
D:\codex-session-sync\exports\codex-session-export-all-20260528-160000.zip
```

全量导出会尽量保留所有 session 文件，包括无法解析 `cwd` 的历史文件。

## 推送到同步盘目录

推荐把同步目录放在 OneDrive、Syncthing、坚果云、NAS 或移动硬盘中。下面的 `D:\codex-session-sync` 只是示例，请替换成你的真实同步目录。

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" push --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --sync-dir "D:\codex-session-sync"
```

如果使用 U 盘上的 `D:\codex`，推荐使用：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" push --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --sync-dir "D:\codex"
```

产出：

```text
D:\codex-session-sync\exports\codex-session-export-project-20260528-153000.zip
D:\codex-session-sync\latest-manifest.json
```

`latest-manifest.json` 会记录当前最新导出包的位置，另一台设备执行 `pull` 时会读取它。

## 从同步盘拉取

在另一台设备上，等同步盘完成同步后执行：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" diff --sync-dir "D:\codex-session-sync"
```

推荐先执行 `diff`，确认本机与同步盘之间有哪些差异：

- `matching`：两边都有且内容一致。
- `remote_only`：同步盘有、本机没有，pull 后会新增。
- `local_only`：本机有、同步盘没有，不会被 pull 删除。
- `conflicted`：两边 thread id 相同但内容不同，需要选择冲突策略。

如果只是想预演导入结果，不写入任何文件，可以直接对 zip 使用 `--dry-run`：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "D:\codex-session-sync\exports\codex-session-export-project-20260528-153000.zip" --dry-run
```

确认无误后再执行：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" pull --sync-dir "D:\codex-session-sync"
```

导入产出：

```text
%USERPROFILE%\.codex\session-sync-backups\<timestamp>\
%USERPROFILE%\.codex\session-sync-last-import-report.json
```

导入前工具会备份当前设备已有的会话文件和索引。导入后建议重启 Codex Desktop，让侧边栏重新加载。

## 直接导入某个 zip

如果你手动复制了导出包，可以直接导入：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "D:\codex-session-sync\exports\codex-session-export-project-20260528-153000.zip"
```

## 查看状态

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" status --sync-dir "D:\codex-session-sync"
```

状态输出会包含：

- 本机 Codex 根目录
- 本机会话数量
- 同步目录
- 是否存在 `latest-manifest.json`
- 最新导出时间
- 最新导出包包含的 thread 数量

## 回滚最近一次导入

如果导入后 Codex 侧边栏异常，或导入结果不符合预期，可以回滚最近一次导入：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" rollback
```

回滚会恢复：

- `.codex/sessions`
- `.codex/session_index.jsonl`
- `.codex/.codex-global-state.json`

回滚前工具也会再次备份当前状态，避免误操作后无法找回当前现场。

## 推荐双设备流程

设备 A：

1. 关闭 Codex Desktop。
2. 执行 `push --project ... --sync-dir ...` 或 `push --all --sync-dir ...`。
3. 等同步盘完成同步。

设备 B：

1. 关闭 Codex Desktop。
2. 执行 `pull --sync-dir ...`。
3. 打开 Codex Desktop。
4. 检查会话列表中是否出现导入的 thread。
5. 打开会话并继续使用。

## 冲突处理

如果目标设备已经存在同一个 thread id：

- 内容完全一致：跳过，记录为 `skipped`。
- 内容不同：默认不覆盖，记录为 `conflicted`。

冲突结果会写入：

```text
%USERPROFILE%\.codex\session-sync-last-import-report.json
```

直接导入 zip 时可以显式选择冲突策略：

```powershell
# 默认策略：遇到冲突不覆盖
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "<导出包.zip>" --conflict skip

# 覆盖本机同 id 会话，适合确认同步盘版本更新时使用
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "<导出包.zip>" --conflict overwrite

# 保留本机会话，同时把同步盘冲突会话复制为新 thread id
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "<导出包.zip>" --conflict keep-both
```

建议先运行 `--dry-run` 查看报告，再选择 `overwrite` 或 `keep-both`。

导入前工具会校验 zip 内部路径，拒绝包含 `../` 或绝对路径的导出包，避免不可信 zip 写到 `.codex` 之外。

如需限制备份数量，可以在导入时增加：

```powershell
C:\Users\hyperchain\Desktop\AI学习\i-do-love\codex_check\run_sync.cmd --codex-root "%USERPROFILE%\.codex" import "<导出包.zip>" --max-backups 10
```

## 导出包内容

导出包是 zip，内部结构如下：

```text
codex-session-export.zip
├── manifest.json
├── sessions/
│   └── 2026/05/28/rollout-...jsonl
├── session_index.jsonl
└── global_state_patch.json
```

其中：

- `manifest.json`：导出清单，包含 thread id、项目路径、hash、文件大小等。
- `sessions/`：实际会话 JSONL 文件。
- `session_index.jsonl`：用于 Codex 侧边栏识别会话。
- `global_state_patch.json`：少量 thread 相关状态补丁。

## 注意事项

- 导入前建议关闭 Codex Desktop。
- 不要同步整个 `.codex` 目录。
- 不要同步认证和 SQLite 文件。
- 同步目录里可能包含敏感对话内容，请放在可信位置。
- 第一版是原型工具，目标是验证 Codex Desktop 是否能稳定识别导入会话。
- 如果 Codex 后续改变本地存储格式，这个工具可能需要调整。

## 验证测试

运行测试：

```powershell
python -m unittest discover -s codex_check\tests -v
```

当前测试覆盖：

- 项目过滤导出。
- 导入缺失 session 并合并索引。
- 同 id 不同内容冲突时默认跳过。
- rollback 恢复最近一次导入前状态。
