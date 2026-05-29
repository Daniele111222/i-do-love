from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from codex_check.sync_tool import (
    UserFacingError,
    diff_sessions,
    export_sessions,
    import_sessions,
    load_config,
    rollback_last_import,
)


PROJECT = r"C:\Users\hyperchain\Desktop\AI学习\i-do-love"
OTHER_PROJECT = r"C:\Users\hyperchain\Desktop\other"


def write_session(codex_root: Path, thread_id: str, cwd: str, name: str, body: str = "hello") -> Path:
    # 构造最小可识别的 Codex session 文件：第一行必须包含 session_meta 和 cwd。
    session_path = (
        codex_root
        / "sessions"
        / "2026"
        / "05"
        / "28"
        / f"rollout-2026-05-28T15-00-00-{thread_id}.jsonl"
    )
    session_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        {
            "timestamp": "2026-05-28T07:00:00.000Z",
            "type": "session_meta",
            "payload": {
                "id": thread_id,
                "timestamp": "2026-05-28T07:00:00.000Z",
                "cwd": cwd,
                "thread_source": "user",
                "cli_version": "0.133.0",
            },
        },
        {
            "timestamp": "2026-05-28T07:00:01.000Z",
            "type": "response_item",
            "payload": {"type": "message", "role": "user", "content": body},
        },
    ]
    session_path.write_text("\n".join(json.dumps(line, ensure_ascii=False) for line in lines) + "\n", encoding="utf-8")
    append_index(codex_root, thread_id, name)
    return session_path


def append_index(codex_root: Path, thread_id: str, name: str) -> None:
    # Codex 侧边栏依赖 session_index.jsonl；测试里同步维护索引，模拟真实本地状态。
    index_path = codex_root / "session_index.jsonl"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "id": thread_id,
        "thread_name": name,
        "updated_at": "2026-05-28T07:00:01.0000000Z",
    }
    with index_path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


class SessionSyncTests(unittest.TestCase):
    def test_export_project_includes_only_matching_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            matching = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            other = "019e6d55-2083-79f0-b1ad-afa92d6df593"
            write_session(source, matching, PROJECT, "matching project")
            write_session(source, other, OTHER_PROJECT, "other project")

            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            with zipfile.ZipFile(export_path) as archive:
                names = set(archive.namelist())
                manifest = json.loads(archive.read("manifest.json"))
                exported_index = archive.read("session_index.jsonl").decode("utf-8")

            self.assertIn("manifest.json", names)
            self.assertIn("session_index.jsonl", names)
            self.assertEqual(manifest["export_mode"], "project")
            self.assertEqual([thread["id"] for thread in manifest["threads"]], [matching])
            self.assertIn(matching, exported_index)
            self.assertNotIn(other, exported_index)

    def test_import_copies_missing_session_and_merges_index(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            thread_id = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(source, thread_id, PROJECT, "import me")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            report = import_sessions(target, export_path)

            copied_files = list((target / "sessions").rglob("*.jsonl"))
            index_text = (target / "session_index.jsonl").read_text(encoding="utf-8")
            self.assertEqual(report["copied"], [thread_id])
            self.assertTrue(copied_files)
            self.assertIn(thread_id, copied_files[0].name)
            self.assertIn(thread_id, index_text)

    def test_import_skips_conflicting_existing_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            thread_id = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(source, thread_id, PROJECT, "from source", body="new")
            target_session = write_session(target, thread_id, PROJECT, "existing", body="old")
            before = target_session.read_text(encoding="utf-8")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            report = import_sessions(target, export_path)

            self.assertEqual(report["conflicted"], [thread_id])
            self.assertEqual(target_session.read_text(encoding="utf-8"), before)

    def test_import_dry_run_reports_changes_without_writing_files_or_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            thread_id = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(source, thread_id, PROJECT, "import me")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            report = import_sessions(target, export_path, dry_run=True)

            self.assertEqual(report["copied"], [thread_id])
            self.assertTrue(report["dry_run"])
            self.assertFalse((target / "sessions").exists())
            self.assertFalse((target / "session_index.jsonl").exists())
            self.assertFalse((target / "session-sync-backups").exists())

    def test_import_overwrite_conflict_replaces_existing_session(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            thread_id = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(source, thread_id, PROJECT, "from source", body="new")
            target_session = write_session(target, thread_id, PROJECT, "existing", body="old")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            report = import_sessions(target, export_path, conflict_policy="overwrite")

            self.assertEqual(report["overwritten"], [thread_id])
            self.assertIn("new", target_session.read_text(encoding="utf-8"))

    def test_import_keep_both_conflict_copies_session_with_new_thread_id(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            thread_id = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(source, thread_id, PROJECT, "from source", body="new")
            write_session(target, thread_id, PROJECT, "existing", body="old")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            report = import_sessions(target, export_path, conflict_policy="keep-both")

            self.assertEqual(report["kept_both_original"], [thread_id])
            self.assertEqual(len(report["copied_as"]), 1)
            new_thread_id = report["copied_as"][0]["new_id"]
            copied_files = list((target / "sessions").rglob(f"*{new_thread_id}.jsonl"))
            index_text = (target / "session_index.jsonl").read_text(encoding="utf-8")
            self.assertTrue(copied_files)
            self.assertIn(new_thread_id, copied_files[0].read_text(encoding="utf-8"))
            self.assertIn(new_thread_id, index_text)

    def test_import_rejects_zip_entries_outside_export_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            export_path = tmp_path / "bad.zip"
            with zipfile.ZipFile(export_path, "w") as archive:
                archive.writestr("manifest.json", json.dumps({"schema_version": 1, "threads": []}))
                archive.writestr("../evil.txt", "nope")

            with self.assertRaises(UserFacingError):
                import_sessions(tmp_path / ".codex", export_path)

    def test_diff_sessions_reports_local_remote_matching_and_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            sync_dir = tmp_path / "sync"
            matching = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            remote_only = "019e6d55-2083-79f0-b1ad-afa92d6df593"
            local_only = "019e6d56-2083-79f0-b1ad-afa92d6df594"
            conflicted = "019e6d57-2083-79f0-b1ad-afa92d6df595"
            write_session(source, matching, PROJECT, "matching", body="same")
            write_session(target, matching, PROJECT, "matching", body="same")
            write_session(source, remote_only, PROJECT, "remote only")
            write_session(target, local_only, PROJECT, "local only")
            write_session(source, conflicted, PROJECT, "remote conflict", body="remote")
            write_session(target, conflicted, PROJECT, "local conflict", body="local")
            from codex_check.sync_tool import push_sessions

            push_sessions(source, sync_dir, project=PROJECT)

            report = diff_sessions(target, sync_dir)

            self.assertEqual(report["matching"], [matching])
            self.assertEqual(report["remote_only"], [remote_only])
            self.assertEqual(report["local_only"], [local_only])
            self.assertEqual(report["conflicted"], [conflicted])

    def test_import_prunes_old_backups_after_successful_import(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            backup_root = target / "session-sync-backups"
            for name in ("20260101-000000-000000", "20260102-000000-000000"):
                old_backup = backup_root / name
                old_backup.mkdir(parents=True)
                (old_backup / "marker.txt").write_text(name, encoding="utf-8")
            write_session(source, "019e6d54-2083-79f0-b1ad-afa92d6df592", PROJECT, "imported")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)

            import_sessions(target, export_path, max_backups=2)

            backups = sorted(path.name for path in backup_root.iterdir() if path.is_dir())
            self.assertEqual(len(backups), 2)
            self.assertNotIn("20260101-000000-000000", backups)

    def test_rollback_restores_last_import_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            source = tmp_path / "source" / ".codex"
            target = tmp_path / "target" / ".codex"
            original = "019e6d55-2083-79f0-b1ad-afa92d6df593"
            imported = "019e6d54-2083-79f0-b1ad-afa92d6df592"
            write_session(target, original, PROJECT, "original")
            write_session(source, imported, PROJECT, "imported")
            export_path = export_sessions(source, tmp_path / "out", project=PROJECT)
            import_sessions(target, export_path)

            rollback_last_import(target)

            index_text = (target / "session_index.jsonl").read_text(encoding="utf-8")
            self.assertIn(original, index_text)
            self.assertNotIn(imported, index_text)
            self.assertFalse(list((target / "sessions").rglob(f"*{imported}.jsonl")))

    def test_cli_rejects_placeholder_sync_dir_with_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_root = Path(temp_dir) / ".codex"
            write_session(codex_root, "019e6d54-2083-79f0-b1ad-afa92d6df592", PROJECT, "matching")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_check.sync_tool",
                    "--codex-root",
                    str(codex_root),
                    "push",
                    "--project",
                    PROJECT,
                    "--sync-dir",
                    "你的同步盘目录",
                ],
                cwd=Path(__file__).resolve().parents[2],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("不是有效的同步盘目录", result.stderr)

    def test_cli_reports_when_project_has_no_matching_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            codex_root = Path(temp_dir) / ".codex"
            output_dir = Path(temp_dir) / "out"
            write_session(codex_root, "019e6d54-2083-79f0-b1ad-afa92d6df592", OTHER_PROJECT, "other")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_check.sync_tool",
                    "--codex-root",
                    str(codex_root),
                    "export",
                    "--project",
                    PROJECT,
                    "--output-dir",
                    str(output_dir),
                ],
                cwd=Path(__file__).resolve().parents[2],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("没有找到匹配项目路径的 Codex 会话", result.stderr)

    def test_cli_doctor_reports_matching_sessions_and_writable_sync_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            codex_root = tmp_path / ".codex"
            sync_dir = tmp_path / "sync"
            write_session(codex_root, "019e6d54-2083-79f0-b1ad-afa92d6df592", PROJECT, "matching")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_check.sync_tool",
                    "--codex-root",
                    str(codex_root),
                    "doctor",
                    "--project",
                    PROJECT,
                    "--sync-dir",
                    str(sync_dir),
                ],
                cwd=Path(__file__).resolve().parents[2],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertIn("匹配项目会话数: 1", result.stdout)
            self.assertIn("同步目录可写: 是", result.stdout)

    def test_cli_init_writes_config_inside_codex_check_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            codex_root = tmp_path / ".codex"
            sync_dir = tmp_path / "sync"
            config_path = tmp_path / "codex-sync.json"

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_check.sync_tool",
                    "--config",
                    str(config_path),
                    "init",
                    "--codex-root",
                    str(codex_root),
                    "--sync-dir",
                    str(sync_dir),
                    "--project",
                    PROJECT,
                    "--scope",
                    "project",
                    "--max-backups",
                    "7",
                ],
                cwd=Path(__file__).resolve().parents[2],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue(config_path.exists())
            config = load_config(config_path)
            self.assertEqual(config["codex_root"], str(codex_root))
            self.assertEqual(config["sync_dir"], str(sync_dir))
            self.assertEqual(config["project"], PROJECT)
            self.assertEqual(config["scope"], "project")
            self.assertEqual(config["max_backups"], 7)

    def test_cli_push_uses_config_defaults_for_short_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            tmp_path = Path(temp_dir)
            codex_root = tmp_path / ".codex"
            sync_dir = tmp_path / "sync"
            config_path = tmp_path / "codex-sync.json"
            write_session(codex_root, "019e6d54-2083-79f0-b1ad-afa92d6df592", PROJECT, "matching")
            config_path.write_text(
                json.dumps(
                    {
                        "codex_root": str(codex_root),
                        "sync_dir": str(sync_dir),
                        "project": PROJECT,
                        "scope": "project",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "codex_check.sync_tool",
                    "--config",
                    str(config_path),
                    "push",
                ],
                cwd=Path(__file__).resolve().parents[2],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0)
            self.assertTrue((sync_dir / "latest-manifest.json").exists())

    def test_package_module_entrypoint_delegates_to_cli(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "codex_check",
                "--help",
            ],
            cwd=Path(__file__).resolve().parents[2],
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0)
        self.assertIn("Codex Session Sync", result.stdout)


if __name__ == "__main__":
    unittest.main()
