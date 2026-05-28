from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from codex_check.sync_tool import export_sessions, import_sessions, rollback_last_import


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


if __name__ == "__main__":
    unittest.main()
