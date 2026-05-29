from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


# 只允许同步明确和 thread 相关的状态字段，避免把认证、窗口状态、插件状态等机器绑定数据带到另一台设备。
THREAD_STATE_KEYS = ("heartbeat-thread-permissions-by-id", "thread-workspace-root-hints")
PLACEHOLDER_VALUES = {
    "你的同步盘目录",
    "<同步目录>",
    "同步目录",
    "your-sync-dir",
    "<sync-dir>",
}


class UserFacingError(RuntimeError):
    """需要直接展示给 CLI 用户的可理解错误。"""


@dataclass(frozen=True)
class SessionRecord:
    thread_id: str
    cwd: str | None
    session_file: Path
    archive_name: str
    sha256: str
    size_bytes: int
    thread_name: str | None = None
    updated_at: str | None = None


def export_sessions(codex_root: Path, output_dir: Path, project: str | None = None) -> Path:
    codex_root = codex_root.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index_entries = _read_index(codex_root / "session_index.jsonl")
    sessions = _collect_sessions(codex_root, index_entries, project)
    if project and not sessions:
        raise UserFacingError(
            "没有找到匹配项目路径的 Codex 会话。\n"
            f"项目路径: {project}\n"
            f"Codex 根目录: {codex_root}\n"
            "请确认该项目曾经在 Codex 中打开过，并且路径与 session_meta.payload.cwd 完全一致。"
        )
    if not project and not sessions:
        raise UserFacingError(
            "没有找到可导出的 Codex 会话。\n"
            f"Codex 根目录: {codex_root}\n"
            "请确认 sessions 目录存在且包含 rollout-*.jsonl 文件。"
        )
    mode = "project" if project else "all"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    export_path = output_dir / f"codex-session-export-{mode}-{timestamp}.zip"

    # manifest 是导入端的唯一可信目录：后续导入必须用它校验文件、判断模式和定位 thread。
    manifest = {
        "schema_version": 1,
        "export_mode": mode,
        "source_device": platform.node(),
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "codex_root": str(codex_root),
        "project_cwd": project,
        "threads": [
            {
                "id": session.thread_id,
                "thread_name": session.thread_name,
                "cwd": session.cwd,
                "updated_at": session.updated_at,
                "session_file": session.archive_name,
                "sha256": session.sha256,
                "size_bytes": session.size_bytes,
            }
            for session in sessions
        ],
        "excluded": [
            "auth.json",
            "installation_id",
            "*.sqlite",
            "*.sqlite-wal",
            "*.sqlite-shm",
            ".sandbox-secrets",
            "cache",
            "plugins",
        ],
    }

    exported_ids = {session.thread_id for session in sessions}
    exported_index = [entry for entry in index_entries.values() if entry.get("id") in exported_ids]
    state_patch = _build_global_state_patch(codex_root / ".codex-global-state.json", exported_ids)

    with zipfile.ZipFile(export_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        archive.writestr(
            "session_index.jsonl",
            "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in exported_index),
        )
        archive.writestr("global_state_patch.json", json.dumps(state_patch, ensure_ascii=False, indent=2))
        for session in sessions:
            archive.write(session.session_file, session.archive_name)

    return export_path


def import_sessions(codex_root: Path, export_path: Path) -> dict[str, Any]:
    codex_root.mkdir(parents=True, exist_ok=True)
    # 导入会改动 Codex 原生索引和 session 文件，先备份再写入，方便出现格式变化或误导入时回滚。
    backup_dir = _backup_codex_state(codex_root)
    report: dict[str, Any] = {
        "copied": [],
        "skipped": [],
        "conflicted": [],
        "failed": [],
        "backup_dir": str(backup_dir),
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        extract_dir = Path(temp_dir)
        with zipfile.ZipFile(export_path) as archive:
            archive.extractall(extract_dir)
        manifest = json.loads((extract_dir / "manifest.json").read_text(encoding="utf-8"))
        if manifest.get("schema_version") != 1:
            raise ValueError("Unsupported manifest schema_version")

        target_sessions = _session_records_by_thread(codex_root)
        for thread in manifest.get("threads", []):
            thread_id = thread["id"]
            source_rel = thread["session_file"]
            source_file = extract_dir / source_rel
            if not source_file.exists():
                report["failed"].append(thread_id)
                continue
            if _sha256(source_file) != thread["sha256"]:
                report["failed"].append(thread_id)
                continue

            existing = target_sessions.get(thread_id)
            if existing:
                # 同 id 不同内容时默认跳过，避免覆盖另一台设备上已经继续过的会话。
                if _sha256(existing) == thread["sha256"]:
                    report["skipped"].append(thread_id)
                else:
                    report["conflicted"].append(thread_id)
                continue

            target_file = codex_root / source_rel
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            report["copied"].append(thread_id)

        _merge_session_index(codex_root / "session_index.jsonl", extract_dir / "session_index.jsonl")
        _merge_global_state(codex_root / ".codex-global-state.json", extract_dir / "global_state_patch.json")

    report_path = codex_root / "session-sync-last-import-report.json"
    _atomic_write_text(report_path, json.dumps(report, ensure_ascii=False, indent=2))
    return report


def rollback_last_import(codex_root: Path) -> Path:
    backup_root = codex_root / "session-sync-backups"
    backups = sorted(path for path in backup_root.iterdir() if path.is_dir())
    if not backups:
        raise FileNotFoundError("No session sync backups found")
    backup = backups[-1]
    # 回滚前再备份当前状态，避免用户误触 rollback 后丢掉最新现场。
    current_backup = backup_root / f"pre-rollback-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    _copy_if_exists(codex_root / "sessions", current_backup / "sessions")
    _copy_if_exists(codex_root / "session_index.jsonl", current_backup / "session_index.jsonl")
    _copy_if_exists(codex_root / ".codex-global-state.json", current_backup / ".codex-global-state.json")

    for target in (codex_root / "sessions", codex_root / "session_index.jsonl", codex_root / ".codex-global-state.json"):
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()

    _copy_if_exists(backup / "sessions", codex_root / "sessions")
    _copy_if_exists(backup / "session_index.jsonl", codex_root / "session_index.jsonl")
    _copy_if_exists(backup / ".codex-global-state.json", codex_root / ".codex-global-state.json")
    return backup


def push_sessions(codex_root: Path, sync_dir: Path, project: str | None = None) -> Path:
    _validate_sync_dir(sync_dir)
    exports_dir = sync_dir / "exports"
    export_path = export_sessions(codex_root, exports_dir, project=project)
    sync_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(export_path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
    # 同步盘只保存相对路径，避免设备 A 的绝对路径泄漏到设备 B 的查找逻辑中。
    manifest["export_file"] = str(PurePosixPath("exports") / export_path.name)
    _atomic_write_text(sync_dir / "latest-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return export_path


def pull_sessions(codex_root: Path, sync_dir: Path) -> dict[str, Any]:
    _validate_sync_dir(sync_dir)
    latest = sync_dir / "latest-manifest.json"
    if not latest.exists():
        raise UserFacingError(
            "同步目录中没有 latest-manifest.json，无法 pull。\n"
            f"同步目录: {sync_dir}\n"
            "请先在另一台设备执行 push，或确认同步盘已经完成同步。"
        )
    manifest = json.loads(latest.read_text(encoding="utf-8"))
    export_file = sync_dir / manifest["export_file"]
    if not export_file.exists():
        raise UserFacingError(
            "latest-manifest.json 指向的导出包不存在。\n"
            f"导出包: {export_file}\n"
            "请确认同步盘中的 exports 目录已经同步完整。"
        )
    return import_sessions(codex_root, export_file)


def status(codex_root: Path, sync_dir: Path | None = None) -> dict[str, Any]:
    session_count = len(_session_records_by_thread(codex_root))
    result: dict[str, Any] = {"codex_root": str(codex_root), "local_sessions": session_count}
    if sync_dir:
        latest = sync_dir / "latest-manifest.json"
        result["sync_dir"] = str(sync_dir)
        result["has_latest_manifest"] = latest.exists()
        if latest.exists():
            manifest = json.loads(latest.read_text(encoding="utf-8"))
            result["latest_exported_at"] = manifest.get("exported_at")
            result["latest_threads"] = len(manifest.get("threads", []))
    return result


def doctor(codex_root: Path, project: str | None = None, sync_dir: Path | None = None) -> dict[str, Any]:
    index_entries = _read_index(codex_root / "session_index.jsonl")
    sessions = _collect_sessions(codex_root, index_entries, project)
    result: dict[str, Any] = {
        "codex_root": str(codex_root),
        "codex_root_exists": codex_root.exists(),
        "sessions_dir_exists": (codex_root / "sessions").exists(),
        "session_index_exists": (codex_root / "session_index.jsonl").exists(),
        "project": project,
        "matching_sessions": len(sessions),
    }
    if sync_dir is not None:
        result["sync_dir"] = str(sync_dir)
        result["sync_dir_writable"] = _is_writable_dir(sync_dir)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Synchronize Codex Desktop session files.")
    parser.add_argument("--codex-root", type=Path, default=Path.home() / ".codex")
    subparsers = parser.add_subparsers(dest="command", required=True)

    export_parser = subparsers.add_parser("export")
    export_group = export_parser.add_mutually_exclusive_group(required=True)
    export_group.add_argument("--project")
    export_group.add_argument("--all", action="store_true")
    export_parser.add_argument("--output-dir", type=Path, required=True)

    import_parser = subparsers.add_parser("import")
    import_parser.add_argument("export_zip", type=Path)

    push_parser = subparsers.add_parser("push")
    push_group = push_parser.add_mutually_exclusive_group(required=True)
    push_group.add_argument("--project")
    push_group.add_argument("--all", action="store_true")
    push_parser.add_argument("--sync-dir", type=Path, required=True)

    pull_parser = subparsers.add_parser("pull")
    pull_parser.add_argument("--sync-dir", type=Path, required=True)

    status_parser = subparsers.add_parser("status")
    status_parser.add_argument("--sync-dir", type=Path)

    doctor_parser = subparsers.add_parser("doctor")
    doctor_parser.add_argument("--project")
    doctor_parser.add_argument("--sync-dir", type=Path)

    subparsers.add_parser("rollback")

    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            path = export_sessions(args.codex_root, args.output_dir, project=args.project)
            print(f"导出成功: {path}")
        elif args.command == "import":
            report = import_sessions(args.codex_root, args.export_zip)
            print("导入完成:")
            print(json.dumps(report, ensure_ascii=False, indent=2))
        elif args.command == "push":
            path = push_sessions(args.codex_root, args.sync_dir, project=args.project)
            print(f"推送成功: {path}")
            print(f"同步清单: {args.sync_dir / 'latest-manifest.json'}")
        elif args.command == "pull":
            print(json.dumps(pull_sessions(args.codex_root, args.sync_dir), ensure_ascii=False, indent=2))
        elif args.command == "status":
            print(json.dumps(status(args.codex_root, args.sync_dir), ensure_ascii=False, indent=2))
        elif args.command == "doctor":
            _print_doctor_report(doctor(args.codex_root, args.project, args.sync_dir))
        elif args.command == "rollback":
            print(f"回滚完成，使用备份: {rollback_last_import(args.codex_root)}")
    except UserFacingError as error:
        print(f"错误: {error}", file=sys.stderr)
        return 2
    except Exception as error:  # noqa: BLE001 - CLI 入口需要兜底展示异常原因。
        print(f"未预期错误: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


def _collect_sessions(
    codex_root: Path, index_entries: dict[str, dict[str, Any]], project: str | None
) -> list[SessionRecord]:
    records: list[SessionRecord] = []
    sessions_root = codex_root / "sessions"
    if not sessions_root.exists():
        return records

    for session_file in sorted(sessions_root.rglob("rollout-*.jsonl")):
        meta = _read_session_meta(session_file)
        if not meta:
            # 项目导出必须知道 cwd；全量导出则尽量保留无法解析 meta 的历史文件。
            if project:
                continue
            thread_id = _thread_id_from_name(session_file)
            cwd = None
        else:
            thread_id = meta["id"]
            cwd = meta.get("cwd")
        if project and _normalize_path(cwd) != _normalize_path(project):
            continue
        index_entry = index_entries.get(thread_id, {})
        archive_name = Path("sessions") / session_file.relative_to(sessions_root)
        records.append(
            SessionRecord(
                thread_id=thread_id,
                cwd=cwd,
                session_file=session_file,
                archive_name=archive_name.as_posix(),
                sha256=_sha256(session_file),
                size_bytes=session_file.stat().st_size,
                thread_name=index_entry.get("thread_name"),
                updated_at=index_entry.get("updated_at"),
            )
        )
    return records


def _read_session_meta(session_file: Path) -> dict[str, Any] | None:
    with session_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                return None
            if item.get("type") == "session_meta":
                payload = item.get("payload", {})
                if payload.get("id"):
                    return payload
                return None
    return None


def _read_index(index_path: Path) -> dict[str, dict[str, Any]]:
    entries: dict[str, dict[str, Any]] = {}
    if not index_path.exists():
        return entries
    with index_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            thread_id = entry.get("id")
            if not thread_id:
                continue
            existing = entries.get(thread_id)
            # 索引文件可能出现重复 thread id，保留 updated_at 更新的一条。
            if not existing or _sort_time(entry.get("updated_at")) >= _sort_time(existing.get("updated_at")):
                entries[thread_id] = entry
    return entries


def _merge_session_index(target_path: Path, source_path: Path) -> None:
    merged = _read_index(target_path)
    for thread_id, entry in _read_index(source_path).items():
        existing = merged.get(thread_id)
        # 合并索引只增量更新，不删除目标设备已有但导出包中不存在的会话。
        if not existing or _sort_time(entry.get("updated_at")) >= _sort_time(existing.get("updated_at")):
            merged[thread_id] = entry
    target_path.parent.mkdir(parents=True, exist_ok=True)
    body = "".join(json.dumps(entry, ensure_ascii=False) + "\n" for entry in merged.values())
    _atomic_write_text(target_path, body)


def _backup_codex_state(codex_root: Path) -> Path:
    backup_dir = codex_root / "session-sync-backups" / datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    _copy_if_exists(codex_root / "sessions", backup_dir / "sessions")
    _copy_if_exists(codex_root / "session_index.jsonl", backup_dir / "session_index.jsonl")
    _copy_if_exists(codex_root / ".codex-global-state.json", backup_dir / ".codex-global-state.json")
    return backup_dir


def _copy_if_exists(source: Path, target: Path) -> None:
    if not source.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(source, target)
    else:
        shutil.copy2(source, target)


def _session_records_by_thread(codex_root: Path) -> dict[str, Path]:
    result: dict[str, Path] = {}
    sessions_root = codex_root / "sessions"
    if not sessions_root.exists():
        return result
    for session_file in sessions_root.rglob("rollout-*.jsonl"):
        meta = _read_session_meta(session_file)
        thread_id = meta["id"] if meta else _thread_id_from_name(session_file)
        result.setdefault(thread_id, session_file)
    return result


def _build_global_state_patch(global_state_path: Path, thread_ids: set[str]) -> dict[str, Any]:
    if not global_state_path.exists():
        return {}
    try:
        state = json.loads(global_state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    patch: dict[str, Any] = {}
    for key in THREAD_STATE_KEYS:
        value = state.get(key)
        if isinstance(value, dict):
            selected = {thread_id: value[thread_id] for thread_id in thread_ids if thread_id in value}
            if selected:
                patch[key] = selected
    return patch


def _merge_global_state(target_path: Path, patch_path: Path) -> None:
    if not patch_path.exists():
        return
    patch = json.loads(patch_path.read_text(encoding="utf-8"))
    if not patch:
        return
    if target_path.exists():
        try:
            state = json.loads(target_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {}
    else:
        state = {}
    for key in THREAD_STATE_KEYS:
        value = patch.get(key)
        if isinstance(value, dict):
            current = state.get(key)
            if not isinstance(current, dict):
                current = {}
            current.update(value)
            state[key] = current
    _atomic_write_text(target_path, json.dumps(state, ensure_ascii=False, indent=2))


def _validate_sync_dir(sync_dir: Path) -> None:
    raw_value = str(sync_dir).strip().strip('"')
    if raw_value in PLACEHOLDER_VALUES or "你的" in raw_value or "<" in raw_value or ">" in raw_value:
        raise UserFacingError(
            "不是有效的同步盘目录，你传入的看起来仍是文档里的占位文字。\n"
            f"收到的值: {sync_dir}\n"
            "请改成真实目录，例如 OneDrive/Syncthing/NAS 中两台设备都能访问的文件夹。"
        )


def _is_writable_dir(path: Path) -> bool:
    try:
        path.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=True, dir=path) as handle:
            handle.write("ok")
        return True
    except OSError:
        return False


def _print_doctor_report(report: dict[str, Any]) -> None:
    print("Codex Session Sync 诊断")
    print(f"Codex 根目录: {report['codex_root']}")
    print(f"Codex 根目录存在: {'是' if report['codex_root_exists'] else '否'}")
    print(f"sessions 目录存在: {'是' if report['sessions_dir_exists'] else '否'}")
    print(f"session_index.jsonl 存在: {'是' if report['session_index_exists'] else '否'}")
    if report.get("project"):
        print(f"项目路径: {report['project']}")
    print(f"匹配项目会话数: {report['matching_sessions']}")
    if "sync_dir" in report:
        print(f"同步目录: {report['sync_dir']}")
        print(f"同步目录可写: {'是' if report['sync_dir_writable'] else '否'}")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _normalize_path(path: str | None) -> str | None:
    if path is None:
        return None
    normalized = path.replace("/", "\\").rstrip("\\")
    return os.path.normcase(normalized)


def _thread_id_from_name(path: Path) -> str:
    stem = path.stem
    marker = "rollout-"
    if stem.startswith(marker):
        return stem.split("-")[-5] + "-" + "-".join(stem.split("-")[-4:])
    return stem


def _sort_time(value: str | None) -> str:
    return value or ""


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # 先写临时文件再替换目标文件，降低中途失败导致索引半写入的概率。
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent, newline="\n") as handle:
        handle.write(text)
        temp_name = handle.name
    os.replace(temp_name, path)


if __name__ == "__main__":
    raise SystemExit(main())
