"""Meaningful source-release invariants; all fixtures are isolated from the project."""

from __future__ import annotations

import hashlib
import importlib.util
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/build_release.py"
SPEC = importlib.util.spec_from_file_location("build_release", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
release = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = release
SPEC.loader.exec_module(release)
TEMP_ROOT = Path(tempfile.gettempdir()) / "i-asked-for-a-button"


class ReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        TEMP_ROOT.mkdir(parents=True, exist_ok=True)
        self.sandbox = tempfile.TemporaryDirectory(prefix="release-test-", dir=TEMP_ROOT)
        self.addCleanup(self.sandbox.cleanup)
        self.root = Path(self.sandbox.name) / "source"
        self.root.mkdir()
        for relative in release.ROOT_FILES:
            self.write(relative, f"Release fixture: {relative}\n")
        self.write("VERSION", "0.5.0\n")
        self.write(
            release.SKILL_FILE,
            '---\nname: i-asked-for-a-button\ndescription: Test fixture.\nmetadata:\n  version: "0.5.0"\n---\n\nSkill body.\n',
        )
        self.write("scripts/build_release.py", "# Fixture script.\n")
        self.write("scripts/manage.py", "# Fixture installer.\n")
        self.write("skills/i-asked-for-a-button/scripts/session_start.py", "# Fixture loader.\n")
        self.write("skills/i-asked-for-a-button/agents/openai.yaml", 'interface:\n  display_name: "Fixture"\n')
        self.write("adapters/codex/hooks.example.json", '{"hooks": {}}\n')
        self.write("tests/test_fixture.py", "# Fixture test.\n")

    def write(self, relative: str | Path, contents: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8", newline="\n")
        return path

    def test_repeated_build_has_identical_bytes_and_checksum(self) -> None:
        first = release.build_release(self.root)
        first_bytes = first.archive.read_bytes()
        first_sums = first.checksums.read_bytes()
        for path in self.root.rglob("*"):
            if path.is_file() and "dist" not in path.relative_to(self.root).parts:
                os.utime(path, (1_700_000_000, 1_700_000_000))
        second = release.build_release(self.root, Path(self.sandbox.name) / "another-output")
        self.assertEqual(second.archive.read_bytes(), first_bytes)
        self.assertEqual(second.checksums.read_bytes(), first_sums)
        self.assertEqual(second.sha256, hashlib.sha256(first_bytes).hexdigest())
        self.assertEqual(first_sums.decode("ascii"), f"{second.sha256}  {second.archive.name}\n")
        with zipfile.ZipFile(second.archive) as archive:
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))
            for member in archive.infolist():
                self.assertTrue(member.filename.startswith("i-asked-for-a-button-0.5.0/"))
                self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(member.external_attr >> 16, stat.S_IFREG | 0o644)

    def test_private_credentials_cache_and_unlisted_inputs_are_excluded(self) -> None:
        excluded = (
            "private-reference/private.md",
            "source-archive/original.zip",
            "research/research.md",
            "unlisted-root-file.md",
            ".env",
            "dist/old.zip",
            "skills/__pycache__/cached.pyc",
            "skills/i-asked-for-a-button/SKILL.md.bak",
            "skills/i-asked-for-a-button/temp/draft.md",
            "adapters/.codex/auth.json",
            "adapters/auth.json",
            "adapters/credentials.json",
            "adapters/api_keys.json",
            "adapters/client_secret.json",
            "adapters/service-account.json",
            "adapters/passwords.txt",
            "adapters/.env.example",
            "adapters/private.key",
            "adapters/id_ed25519",
            "scripts/hidden.pfx",
            "scripts/backup.py~",
            "tests/private-reference/feedback.md",
            "tests/research/notes.md",
            "tests/dist/generated.json",
            "tests/unlisted.exe",
        )
        for relative in excluded:
            self.write(relative, "Must stay out of release.\n")
        result = release.build_release(self.root)
        with zipfile.ZipFile(result.archive) as archive:
            relative_members = {name.split("/", 1)[1] for name in archive.namelist()}
        self.assertTrue(set(excluded).isdisjoint(relative_members))
        self.assertIn("adapters/codex/hooks.example.json", relative_members)
        self.assertIn("scripts/build_release.py", relative_members)
        self.assertIn("tests/test_fixture.py", relative_members)

    def test_license_and_root_tests_are_included_without_assets_or_private_experiments(self) -> None:
        license_file = self.write("LICENSE", "Apache License\nVersion 2.0, January 2004\n")
        excluded = (
            "PROJECT_STATUS.md",
            "PROJECT_STATUS_zh.md",
            "VALIDATION.md",
            "VALIDATION_zh.md",
            "assets/logo.png",
            "assets/logo-v2.png",
            "assets/logo-old.png",
            "assets/logo.prompt.txt",
            "assets/candidates/logo.png",
            "tests/experiment/notes.md",
            "tests/experiment/results.json",
            "tests/experiment/index.html",
            "tests/experiment/test_private.py",
            "tests/experiment/screenshot.png",
            "tests/notes.md",
            "tests/results.json",
            "tests/index.html",
            "tests/fixture.py",
            "tests/screenshot.png",
            "skills/i-asked-for-a-button/example.html",
            "skills/i-asked-for-a-button/screenshot.png",
        )
        for relative in excluded:
            self.write(relative, "Private or unlisted fixture.\n")
        result = release.build_release(self.root)
        prefix = "i-asked-for-a-button-0.5.0/"
        with zipfile.ZipFile(result.archive) as archive:
            members = {name.removeprefix(prefix) for name in archive.namelist()}
            self.assertEqual(archive.read(prefix + "LICENSE"), license_file.read_bytes())
            self.assertIn("tests/test_fixture.py", members)
            self.assertTrue(set(excluded).isdisjoint(members))

    def test_version_mismatch_fails_before_creating_outputs(self) -> None:
        self.write("VERSION", "0.6.0\n")
        with self.assertRaisesRegex(release.ReleaseError, "Version mismatch"):
            release.build_release(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_missing_required_file_fails_before_creating_outputs(self) -> None:
        (self.root / "README_zh.md").unlink()
        with self.assertRaisesRegex(release.ReleaseError, "Missing required release file: README_zh.md"):
            release.build_release(self.root)
        self.assertFalse((self.root / "dist").exists())

    def test_empty_required_source_directory_fails(self) -> None:
        (self.root / "tests/test_fixture.py").unlink()
        self.write("tests/experiment/test_private.py", "# Nested experiments do not satisfy public tests.\n")
        with self.assertRaisesRegex(release.ReleaseError, "no distributable files: tests"):
            release.build_release(self.root)

    def test_missing_runtime_or_install_resource_fails_before_creating_outputs(self) -> None:
        for relative in (
            "scripts/manage.py",
            "skills/i-asked-for-a-button/scripts/session_start.py",
            "skills/i-asked-for-a-button/agents/openai.yaml",
            "adapters/codex/hooks.example.json",
        ):
            with self.subTest(missing=relative):
                path = self.root / relative
                original = path.read_bytes()
                path.unlink()
                try:
                    with self.assertRaises(release.ReleaseError) as caught:
                        release.build_release(self.root)
                    self.assertEqual(str(caught.exception), f"Missing required release file: {relative}")
                    self.assertFalse((self.root / "dist").exists())
                finally:
                    path.write_bytes(original)

    def test_missing_skill_metadata_version_fails(self) -> None:
        self.write(release.SKILL_FILE, "---\nname: fixture\ndescription: Fixture.\n---\nSkill.\n")
        with self.assertRaisesRegex(release.ReleaseError, "metadata.version"):
            release.build_release(self.root)

    def test_unsafe_version_cannot_escape_output_directory(self) -> None:
        self.write("VERSION", "../../elsewhere\n")
        with self.assertRaisesRegex(release.ReleaseError, "semantic version"):
            release.build_release(self.root)

    def test_symlink_to_outside_file_is_rejected(self) -> None:
        outside = Path(self.sandbox.name) / "outside.md"
        outside.write_text("Outside fixture.\n", encoding="utf-8")
        link = self.root / "adapters/linked.md"
        try:
            link.symlink_to(outside)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks are unavailable: {error}")
        with self.assertRaisesRegex(release.ReleaseError, "Symbolic links and junctions"):
            release.build_release(self.root)

    def test_symlink_to_outside_directory_is_rejected(self) -> None:
        outside = Path(self.sandbox.name) / "outside"
        outside.mkdir()
        (outside / "private.md").write_text("Outside fixture.\n", encoding="utf-8")
        link = self.root / "adapters/linked"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks are unavailable: {error}")
        with self.assertRaisesRegex(release.ReleaseError, "Symbolic links and junctions"):
            release.build_release(self.root)

    def test_cli_honors_output_directory(self) -> None:
        copied_script = self.write("scripts/build_release.py", SCRIPT.read_text(encoding="utf-8"))
        destination = Path(self.sandbox.name) / "output with spaces"
        process = subprocess.run(
            [sys.executable, str(copied_script), "--output-dir", str(destination)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertTrue((destination / "i-asked-for-a-button-0.5.0.zip").is_file())
        self.assertTrue((destination / "SHA256SUMS").is_file())
        self.assertFalse((self.root / "dist").exists())

    def test_cli_reports_missing_inputs_with_nonzero_exit(self) -> None:
        copied_script = self.write("scripts/build_release.py", SCRIPT.read_text(encoding="utf-8"))
        (self.root / "README.md").unlink()
        process = subprocess.run(
            [sys.executable, str(copied_script)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertNotEqual(process.returncode, 0)
        self.assertIn("Missing required release file: README.md", process.stderr)
        self.assertNotIn("Traceback", process.stderr)
        self.assertFalse((self.root / "dist").exists())


if __name__ == "__main__":
    unittest.main()
