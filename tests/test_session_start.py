"""Subprocess-level checks for the self-contained SessionStart loader."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SCRIPT = ROOT / "skills" / "i-asked-for-a-button" / "scripts" / "session_start.py"
BODY = "\n# Test guidance\n\nPreserve this body: 按钮 café.\n\n"
FRONTMATTER = '---\nname: test-skill\ndescription: Test fixture.\nmetadata:\n  version: "0.5.0"\n---\n'


class SessionStartTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="session-start-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skill with spaces 按钮"
        self.script = self.skill / "scripts" / "session_start.py"
        self.script.parent.mkdir(parents=True)
        shutil.copyfile(SOURCE_SCRIPT, self.script)
        self.document = self.skill / "SKILL.md"
        self.document.write_text(FRONTMATTER + BODY, encoding="utf-8", newline="")
        self.cwd = self.root / "unrelated workspace"
        self.cwd.mkdir()

    def run_loader(self, payload: object = None, *, raw: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
        if raw is None:
            if payload is None:
                payload = {"hook_event_name": "SessionStart", "source": "startup"}
            raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        return subprocess.run(
            [sys.executable, str(self.script)],
            input=raw,
            capture_output=True,
            cwd=self.cwd,
            timeout=5,
            check=False,
        )

    def context(self, result: subprocess.CompletedProcess[bytes]) -> str:
        self.assertEqual(result.returncode, 0, result.stderr.decode("utf-8", errors="replace"))
        self.assertEqual(result.stderr, b"")
        output = json.loads(result.stdout.decode("utf-8"))
        self.assertEqual(set(output), {"hookSpecificOutput"})
        self.assertEqual(set(output["hookSpecificOutput"]), {"hookEventName", "additionalContext"})
        self.assertEqual(output["hookSpecificOutput"]["hookEventName"], "SessionStart")
        return output["hookSpecificOutput"]["additionalContext"]

    def assert_failed(self, result: subprocess.CompletedProcess[bytes], diagnostic: str) -> None:
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, b"")
        self.assertIn(diagnostic, result.stderr.decode("utf-8", errors="replace"))
        self.assertNotIn(b"Traceback", result.stderr)
        self.assertLess(len(result.stderr), 200)

    def test_each_source_emits_one_complete_body(self) -> None:
        for source in ("startup", "resume", "clear", "compact", "fork"):
            with self.subTest(source=source):
                context = self.context(self.run_loader({"hook_event_name": "SessionStart", "source": source}))
                self.assertIn("[I Asked for a Button / 0.5.0]", context)
                self.assertIn("$i-asked-for-a-button", context)
                self.assertIn("software development", context)
                self.assertTrue(context.endswith(BODY))
                self.assertEqual(context.count(BODY), 1)
                self.assertNotIn("metadata:", context)

    def test_extra_fields_cannot_select_another_skill(self) -> None:
        decoy = self.cwd / "SKILL.md"
        decoy.write_text("DO NOT LOAD THIS", encoding="utf-8")
        context = self.context(self.run_loader({
            "hook_event_name": "SessionStart", "source": "startup",
            "skill_path": str(decoy), "transcript_path": "missing-and-ignored", "other": "非 ASCII",
        }))
        self.assertTrue(context.endswith(BODY))
        self.assertNotIn("DO NOT LOAD THIS", context)

    def test_bundled_skill_works_from_an_unrelated_working_directory(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SOURCE_SCRIPT)],
            input=b'{"hook_event_name":"SessionStart","source":"startup"}',
            capture_output=True,
            cwd=self.cwd,
            timeout=5,
            check=False,
        )
        context = self.context(result)
        with (SOURCE_SCRIPT.parents[1] / "SKILL.md").open(encoding="utf-8-sig", newline="") as stream:
            document = stream.read()
        body = document.split("---", 2)[2]
        self.assertTrue(context.endswith(body))
        self.assertEqual(context.count(body), 1)
        self.assertIn(f"Resolve referenced files from: {SOURCE_SCRIPT.parents[1].as_posix()}", context)
        self.assertLessEqual(len(result.stdout), 8 * 1024)

    def test_utf8_bom_in_input_and_document_and_crlf_body(self) -> None:
        body = BODY.replace("\n", "\r\n")
        self.document.write_bytes(b"\xef\xbb\xbf" + (FRONTMATTER.replace("\n", "\r\n") + body).encode("utf-8"))
        context = self.context(self.run_loader(raw=b'\xef\xbb\xbf{"hook_event_name":"SessionStart","source":"compact"}'))
        self.assertTrue(context.endswith(body))

    def test_version_is_read_from_bundled_metadata(self) -> None:
        self.document.write_text(FRONTMATTER.replace('"0.5.0"', "'0.5.1-rc.1'") + BODY, encoding="utf-8")
        self.assertIn("/ 0.5.1-rc.1]", self.context(self.run_loader()))

    def test_invalid_event_shape_or_source_fails_before_reading_skill(self) -> None:
        self.document.unlink()
        for payload, diagnostic in (
            ([], "JSON object"),
            ({}, "hook_event_name"),
            ({"hook_event_name": "Stop", "source": "startup"}, "hook_event_name"),
            ({"hook_event_name": "SessionStart"}, "unsupported"),
            ({"hook_event_name": "SessionStart", "source": "unknown"}, "unsupported"),
            ({"hook_event_name": "SessionStart", "source": []}, "unsupported"),
        ):
            with self.subTest(payload=payload):
                self.assert_failed(self.run_loader(payload), diagnostic)

    def test_invalid_or_oversized_json_has_empty_stdout(self) -> None:
        for raw in (b"", b"{", b"{}{}", b"\xff", b'{"value":NaN}', b"[" * 2000):
            with self.subTest(raw=raw[:30]):
                self.assert_failed(self.run_loader(raw=raw), "valid UTF-8 JSON object")
        self.assert_failed(self.run_loader(raw=b" " * (64 * 1024 + 1)), "input limit")

    def test_missing_or_unreadable_skill_fails(self) -> None:
        self.document.unlink()
        self.assert_failed(self.run_loader(), "cannot read")
        self.document.mkdir()
        self.assert_failed(self.run_loader(), "cannot read")

    def test_bad_skill_frontmatter_or_body_fails(self) -> None:
        for document, diagnostic in (
            (BODY, "requires YAML frontmatter"),
            ("---\nmetadata:\n  version: 0.5.0\n", "not closed"),
            (FRONTMATTER, "body is empty"),
            (FRONTMATTER + " \n\t\r\n", "body is empty"),
            (FRONTMATTER.replace('  version: "0.5.0"\n', "" ) + BODY, "metadata.version"),
            (FRONTMATTER.replace('"0.5.0"', "latest") + BODY, "semantic version"),
            (FRONTMATTER.replace('  version: "0.5.0"', '  nested:\n    version: "0.5.0"') + BODY, "metadata.version"),
            (FRONTMATTER.replace('  version: "0.5.0"', '  version: "0.5.0"\n  version: "0.5.1"') + BODY, "exactly one"),
        ):
            with self.subTest(diagnostic=diagnostic, document=document[:50]):
                self.document.write_text(document, encoding="utf-8")
                self.assert_failed(self.run_loader(), diagnostic)

    def test_invalid_utf8_or_oversized_skill_fails(self) -> None:
        self.document.write_bytes(b"\xff")
        self.assert_failed(self.run_loader(), "must be UTF-8")
        self.document.write_bytes((FRONTMATTER + "x" * (8 * 1024)).encode("utf-8"))
        self.assert_failed(self.run_loader(), "package limit")

    def test_escaped_output_limit_fails_instead_of_truncating_body(self) -> None:
        self.document.write_text(FRONTMATTER + "\t" * 5000 + "body", encoding="utf-8")
        self.assert_failed(self.run_loader(), "output limit")


if __name__ == "__main__":
    unittest.main()
