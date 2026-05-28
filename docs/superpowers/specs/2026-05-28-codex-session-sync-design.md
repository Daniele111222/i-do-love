# Codex 跨设备原生会话同步工具设计

**日期:** 2026-05-28
**目标:** 在多台设备之间同步 Codex Desktop 本地会话，使另一台设备尽量能在原生会话列表中识别并继续历史会话。
**方案:** 本地导出包 + 同步盘目录。第一版不做 Git 同步，不同步认证文件，不直接同步 SQLite 状态数据库。

## 背景

当前 Codex Desktop 的会话记录主要存储在本地 `.codex` 目录中。已观察到的关键文件包括：

- `.codex/sessions/**/rollout-*.jsonl`
- `.codex/session_index.jsonl`
- `.codex/.codex-global-state.json`

用户希望实现跨设备的“原生会话同步”，即设备 B 不只是能阅读设备 A 的历史记录，而是尽量能在 Codex Desktop 的会话列表中看到同一批 thread，并继续使用。

## 目标

第一版目标：

- 支持导出某一个项目的 Codex 会话。
- 支持导出全部 Codex 会话。
- 支持从导出包导入到另一台设备。
- 支持通过同步盘目录进行 push/pull。
- 尽量让导入后的会话被 Codex Desktop 原生识别。
- 导入前自动备份，支持回滚。
- 默认不覆盖目标设备已有但内容不同的会话。

非目标：

- 不同步 `auth.json`。
- 不同步 `installation_id`。
- 不同步 `*.sqlite`、`*.sqlite-wal`、`*.sqlite-shm`。
- 不同步 `.sandbox-secrets`、缓存、插件、日志数据库。
- 不保证兼容未来所有 Codex 内部存储格式变化。
- 第一版不做多人协作合并。

## 工具形态

工具设计为独立 CLI，暂定名称：

```bash
codex-session-sync
```

第一版优先支持 Windows，默认 Codex 根目录为：

```text
%USERPROFILE%\.codex
```

后续可扩展 macOS/Linux。

## 核心命令

```bash
codex-session-sync export --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love"
codex-session-sync export --all
codex-session-sync import <export.zip>
codex-session-sync push --project "C:\Users\hyperchain\Desktop\AI学习\i-do-love" --sync-dir <dir>
codex-session-sync push --all --sync-dir <dir>
codex-session-sync pull --sync-dir <dir>
codex-session-sync status --sync-dir <dir>
codex-session-sync rollback
```

## 同步内容

包含：

- `.codex/sessions/**/rollout-*.jsonl`
- `.codex/session_index.jsonl` 中对应 thread id 的条目
- `.codex/.codex-global-state.json` 中 thread 相关的低风险字段补丁

默认排除：

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
- `logs_*`
- 临时文件和运行时缓存

## 导出包结构

导出结果为 zip：

```text
codex-session-export.zip
├── manifest.json
├── sessions/
│   └── 2026/05/28/rollout-...jsonl
├── session_index.jsonl
└── global_state_patch.json
```

## manifest.json

`manifest.json` 用于描述导出包内容和校验信息。

建议字段：

```json
{
  "schema_version": 1,
  "export_mode": "project",
  "source_device": "DESKTOP-A",
  "exported_at": "2026-05-28T15:30:00+08:00",
  "codex_root": "C:\\Users\\hyperchain\\.codex",
  "project_cwd": "C:\\Users\\hyperchain\\Desktop\\AI学习\\i-do-love",
  "threads": [
    {
      "id": "019e6d54-2083-79f0-b1ad-afa92d6df592",
      "thread_name": "导出会话记录同步设备",
      "cwd": "C:\\Users\\hyperchain\\Desktop\\AI学习\\i-do-love",
      "updated_at": "2026-05-28T06:47:02.1199512Z",
      "session_file": "sessions/2026/05/28/rollout-2026-05-28T14-44-55-019e6d54-2083-79f0-b1ad-afa92d6df592.jsonl",
      "sha256": "<hash>",
      "size_bytes": 12345
    }
  ],
  "excluded": [
    "auth.json",
    "installation_id",
    "*.sqlite",
    "*.sqlite-wal",
    "*.sqlite-shm",
    ".sandbox-secrets",
    "cache",
    "plugins"
  ]
}
```

## 项目过滤规则

项目模式通过 session JSONL 的第一条 `session_meta.payload.cwd` 判断所属项目。

规则：

- Windows 路径比较大小写不敏感。
- 比较前标准化路径分隔符。
- 去除尾部分隔符。
- `--project` 只匹配标准化后完全一致的 `cwd`。
- 如果 session 文件缺少 `session_meta` 或 `cwd`：
  - `export --project` 默认跳过。
  - `export --all` 默认保留。

## 导入流程

导入前：

- 检查导出包是否包含 `manifest.json`。
- 校验 manifest schema version。
- 校验每个 session 文件 hash。
- 提示用户关闭 Codex Desktop。
- 创建备份目录：

```text
.codex/session-sync-backups/<timestamp>/
```

备份内容：

- 当前 `.codex/sessions`
- 当前 `.codex/session_index.jsonl`
- 当前 `.codex/.codex-global-state.json`

导入时：

- 按 thread id 检测目标设备是否已有会话。
- 目标不存在：复制 session 文件并合并索引。
- 目标存在且 hash 相同：跳过。
- 目标存在但 hash 不同：默认标记 conflict，不覆盖。
- 合并 `session_index.jsonl` 时按 `id` 去重。
- 同 id 索引条目保留 `updated_at` 更新的一条。
- `.codex-global-state.json` 只合并白名单字段。

导入后：

- 生成 `import-report.json`。
- 提示重启 Codex Desktop。
- 保留备份用于 rollback。

## 冲突策略

第一版默认冲突策略为 `skip`。

冲突场景：

- 同一个 thread id 在目标设备已经存在。
- session 文件 hash 不同。
- 两边 `updated_at` 无法判断明显先后。
- 目标设备对应 session 文件路径不同但 thread id 相同。

默认行为：

- 不覆盖目标文件。
- 将冲突写入 `import-report.json`。
- 保留源文件在导出包中。
- 后续版本可提供 `--overwrite` 或 `--keep-both`。

## global_state_patch.json

`.codex-global-state.json` 不整体同步，只生成补丁。

第一版允许合并的字段：

- `heartbeat-thread-permissions-by-id`
- `thread-workspace-root-hints`

只处理本次导入 thread id 对应的数据。

不合并：

- `auth`
- window bounds
- onboarding state
- installation state
- prompt history
- plugin state
- workspace ordering
- model cache
- 任何设备绑定字段

## 同步盘模式

同步盘目录由用户显式指定，例如：

```text
D:\Sync\codex-sessions
```

目录结构：

```text
codex-sessions/
├── latest-manifest.json
├── exports/
│   ├── codex-session-export-project-20260528-153000.zip
│   └── codex-session-export-all-20260528-160000.zip
└── reports/
```

`push` 行为：

- 执行 export。
- 将 zip 写入 `exports/`。
- 更新 `latest-manifest.json`。
- 保留历史包，后续可加清理策略。

`pull` 行为：

- 读取 `latest-manifest.json`。
- 找到最新导出包。
- 执行 import。
- 生成导入报告。

## 回滚设计

`rollback` 只恢复最近一次导入前备份。

恢复内容：

- `sessions`
- `session_index.jsonl`
- `.codex-global-state.json`

规则：

- rollback 前再次备份当前状态。
- 如果最近一次备份不完整，则拒绝回滚。
- rollback 不删除同步盘里的导出包。

## 安全原则

- 默认不覆盖。
- 默认不碰认证。
- 默认不碰 SQLite。
- 默认导入前备份。
- 默认保守合并 `.codex-global-state.json`。
- 所有写入使用临时文件 + 原子替换。
- 所有异常写入报告，不静默失败。

## 推荐技术实现

推荐使用 Python 实现 CLI。

原因：

- 标准库已包含 `json`、`zipfile`、`hashlib`、`pathlib`、`shutil`。
- 跨平台文件处理更方便。
- 后续可以用 `pyinstaller` 打包成单文件。
- 易于写单元测试和临时目录集成测试。

建议模块：

- `cli.py`：命令行入口。
- `codex_store.py`：定位和读取 `.codex`。
- `session_reader.py`：解析 JSONL session meta。
- `exporter.py`：生成导出包。
- `importer.py`：执行导入、合并、备份。
- `sync_dir.py`：同步盘 push/pull。
- `reports.py`：生成报告。
- `path_utils.py`：路径标准化。
- `tests/`：单元测试和集成测试。

## 测试计划

单元测试：

- 路径标准化。
- 项目会话过滤。
- JSONL session meta 解析。
- 损坏 JSONL 的容错。
- `session_index.jsonl` 去重合并。
- manifest hash 校验。
- global state 白名单补丁生成。
- conflict 检测。

集成测试：

- 构造临时 `.codex` 目录。
- 执行 `export --project`。
- 将导出包导入另一个临时 `.codex`。
- 验证 session 文件被复制。
- 验证 `session_index.jsonl` 被正确合并。
- 验证备份目录存在。
- 验证 rollback 恢复导入前状态。
- 验证排除文件没有进入 zip。

手工验收：

- 设备 A 关闭 Codex 后执行项目导出。
- 设备 B 关闭 Codex 后执行导入。
- 设备 B 重启 Codex Desktop。
- 确认会话列表出现导入 thread。
- 打开 thread，确认历史内容可见。
- 继续发送一条消息，确认会话可继续。
- 测试全量导出和导入。
- 测试冲突时不会覆盖目标设备已有会话。

## 风险

主要风险：

- Codex Desktop 内部存储格式可能变化。
- 仅同步 JSONL 和索引未必覆盖所有 UI 状态。
- `.codex-global-state.json` 中部分字段可能与设备绑定。
- Codex 正在运行时导入可能被覆盖或导致状态不一致。
- 同步盘并发写入可能产生旧包覆盖新包的问题。

第一版缓解：

- 要求导入前关闭 Codex。
- 使用 manifest hash 校验。
- 导入前备份。
- 默认不覆盖冲突。
- 不同步认证、SQLite 和设备绑定文件。
- 以报告形式暴露所有跳过和冲突。

## 后续扩展

第二阶段可以考虑：

- 路径映射，例如设备 A 和 B 项目路径不同。
- `--overwrite`、`--keep-both` 等冲突策略。
- 自动检测 Codex 是否正在运行。
- Windows 任务计划程序集成。
- 简单桌面 UI。
- Codex 插件或内嵌面板。
- 加密导出包。
- 增量同步。
- 多设备最新版本选择策略。

## 结论

第一版应优先验证最核心假设：同步 `sessions`、`session_index.jsonl` 和少量 thread 状态后，另一台设备的 Codex Desktop 是否能稳定识别并继续会话。

因此推荐先实现独立 CLI，而不是插件。CLI 可以快速验证数据边界、导入可靠性和冲突策略；等同步模型稳定后，再考虑插件化或图形界面。
