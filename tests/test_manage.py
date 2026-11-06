"""Exercise global and workspace installation against isolated skill copies."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANAGER = PROJECT_ROOT / "scripts/manage.py"
NAME = "i-asked-for-a-button"
SKILL = Path(".agents/skills") / NAME
STATE = Path(".codex") / f"{NAME}-install.json"
HOOKS = Path(".codex/hooks.json")


class ManageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.sandbox = tempfile.TemporaryDirectory(prefix="button-manage-")
        self.addCleanup(self.sandbox.cleanup)
        self.base = Path(self.sandbox.name)
        self.target = self.base / "workspace with spaces 中文"
        self.target.mkdir()
        self.user_home = self.base / "isolated user"
        self.user_home.mkdir()
        self.codex_home = self.base / "custom codex home 中文"

    def run_manager(self, action: str, *arguments: str, success: bool = True, manager: Path = MANAGER,
                    global_scope: bool = False, codex_home: Path | None = None,
                    home_default: bool = False) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONUTF8"] = "1"
        environment["HOME"] = str(self.user_home)
        environment["USERPROFILE"] = str(self.user_home)
        environment["CODEX_HOME"] = str(codex_home or self.codex_home)
        if home_default:
            environment.pop("CODEX_HOME", None)
        target_arguments = [] if global_scope else ["--target", str(self.target)]
        process = subprocess.run(
            [sys.executable, str(manager), action, *target_arguments, *arguments],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=environment,
            timeout=15,
            check=False,
        )
        if success:
            self.assertEqual(process.returncode, 0, process.stderr)
            self.assertIsInstance(json.loads(process.stdout), dict)
        else:
            self.assertNotEqual(process.returncode, 0, process.stdout)
            self.assertNotIn("Traceback", process.stderr)
        return process

    def write(self, relative: Path, data: bytes) -> Path:
        path = self.target / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def snapshot(self, root: Path | None = None) -> dict[str, bytes | None]:
        root = root or self.target
        return {
            path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")
        }

    def read_json(self, relative: Path) -> dict:
        return json.loads((self.target / relative).read_text(encoding="utf-8-sig"))

    def test_dry_run_does_not_create_or_modify_files(self) -> None:
        original = b'{\r\n  "hooks": {"SessionStart": []}, "custom": true\r\n}\r\n'
        self.write(HOOKS, original)
        before = self.snapshot()
        for arguments in ((), ("--hooks",)):
            with self.subTest(arguments=arguments):
                response = json.loads(self.run_manager("install", "--dry-run", *arguments).stdout)
                self.assertTrue(response["dry_run"])
                self.assertTrue(response["changed"])
                self.assertEqual(self.snapshot(), before)

    def test_plain_install_is_idempotent_and_copies_complete_skill(self) -> None:
        first = json.loads(self.run_manager("install").stdout)
        self.assertFalse(first["hooks"])
        source = PROJECT_ROOT / "skills" / NAME
        for path in source.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                self.assertEqual((self.target / SKILL / path.relative_to(source)).read_bytes(), path.read_bytes())
        before = self.snapshot()
        second = json.loads(self.run_manager("install").stdout)
        self.assertEqual(second["changed"], [])
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.target / HOOKS).exists())

    def test_hook_install_is_idempotent_and_plain_reinstall_preserves_hooks(self) -> None:
        original = {"hooks": {"Stop": [{"hooks": [{"type": "command", "command": "echo other"}]}]}}
        self.write(HOOKS, json.dumps(original).encode("utf-8"))
        self.run_manager("install", "--hooks")
        before = self.snapshot()
        for arguments in (("--hooks",), ()):
            with self.subTest(arguments=arguments):
                response = json.loads(self.run_manager("install", *arguments).stdout)
                self.assertTrue(response["hooks"])
                self.assertEqual(response["changed"], [])
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.read_json(HOOKS)["hooks"]["Stop"], original["hooks"]["Stop"])

    def test_uninstall_restores_original_hook_bytes(self) -> None:
        original = b'{\r\n\t"custom": "preserve spacing",\r\n\t"hooks": { "SessionStart": [] }\r\n}\r\n'
        self.write(HOOKS, original)
        self.run_manager("install", "--hooks")
        self.run_manager("uninstall")
        self.assertEqual((self.target / HOOKS).read_bytes(), original)
        self.assertFalse((self.target / STATE).exists())
        self.assertFalse((self.target / SKILL).exists())

    def test_uninstall_restores_original_hook_utf8_bom(self) -> None:
        original = b'\xef\xbb\xbf{\r\n  "hooks": {}, "custom": true\r\n}\r\n'
        self.write(HOOKS, original)
        self.run_manager("install", "--hooks")
        self.run_manager("uninstall")
        self.assertEqual((self.target / HOOKS).read_bytes(), original)

    def test_uninstall_preserves_hooks_added_after_install(self) -> None:
        self.run_manager("install", "--hooks")
        config = self.read_json(HOOKS)
        foreign = {"matcher": "resume", "hooks": [{"type": "command", "command": "echo other"}]}
        config["hooks"]["SessionStart"].append(foreign)
        config["hooks"]["Stop"] = [{"hooks": [{"type": "command", "command": "echo stop"}]}]
        self.write(HOOKS, json.dumps(config).encode("utf-8"))
        self.run_manager("uninstall")
        remaining = self.read_json(HOOKS)
        self.assertEqual(remaining["hooks"]["SessionStart"], [foreign])
        self.assertEqual(remaining["hooks"]["Stop"], config["hooks"]["Stop"])
        self.assertFalse((self.target / STATE).exists())
        self.assertFalse((self.target / SKILL).exists())

    def test_unowned_skill_is_refused_without_changes(self) -> None:
        self.write(SKILL / "SKILL.md", b"An existing user-owned skill.\n")
        before = self.snapshot()
        self.run_manager("install", "--hooks", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_inline_toml_hooks_reject_duplicate_skill_and_allow_unrelated_hooks(self) -> None:
        toml_path = Path(".codex/config.toml")
        for command, allowed in (
            (f"python .agents/skills/{NAME}/scripts/session_start.py", False),
            ("echo unrelated-inline-hook", True),
        ):
            with self.subTest(command=command, allowed=allowed):
                contents = (
                    '[[hooks.SessionStart]]\nmatcher = "startup"\n'
                    '[[hooks.SessionStart.hooks]]\ntype = "command"\n'
                    f'command = "{command}"\n'
                ).encode("utf-8")
                self.write(toml_path, contents)
                before = self.snapshot()
                process = self.run_manager("install", "--hooks", success=allowed)
                if allowed:
                    self.assertTrue(json.loads(process.stdout)["hooks"])
                    self.assertEqual((self.target / toml_path).read_bytes(), contents)
                    self.run_manager("uninstall")
                    self.assertEqual(self.snapshot(), before)
                else:
                    self.assertIn("inline TOML hooks already reference this skill", process.stderr)
                    self.assertEqual(self.snapshot(), before)

    def test_missing_required_source_file_fails_without_target_writes(self) -> None:
        before = self.snapshot()
        for index, missing in enumerate(("SKILL.md", "agents/openai.yaml", "scripts/session_start.py")):
            with self.subTest(missing=missing):
                source = self.base / f"source-{index}"
                (source / "scripts").mkdir(parents=True)
                manager = source / "scripts/manage.py"
                shutil.copy2(MANAGER, manager)
                shutil.copy2(PROJECT_ROOT / "VERSION", source / "VERSION")
                shutil.copytree(
                    PROJECT_ROOT / "skills",
                    source / "skills",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
                (source / "skills" / NAME / missing).unlink()
                process = self.run_manager("install", "--hooks", success=False, manager=manager)
                self.assertIn("source skill is incomplete", process.stderr)
                self.assertEqual(self.snapshot(), before)

    def test_changed_installed_file_refuses_install_and_uninstall_atomically(self) -> None:
        self.run_manager("install", "--hooks")
        path = self.target / SKILL / "SKILL.md"
        path.write_bytes(path.read_bytes() + b"\nUser edit.\n")
        before = self.snapshot()
        for action in ("install", "uninstall"):
            with self.subTest(action=action):
                self.run_manager(action, success=False)
                self.assertEqual(self.snapshot(), before)

    def test_changed_installed_handler_refuses_install_and_uninstall_atomically(self) -> None:
        self.run_manager("install", "--hooks")
        config = self.read_json(HOOKS)
        config["hooks"]["SessionStart"][0]["hooks"][0]["command"] += " --user-edit"
        self.write(HOOKS, json.dumps(config).encode("utf-8"))
        before = self.snapshot()
        for action in ("install", "uninstall"):
            with self.subTest(action=action):
                self.run_manager(action, success=False)
                self.assertEqual(self.snapshot(), before)

    def test_unowned_file_inside_skill_prevents_uninstall(self) -> None:
        self.run_manager("install")
        self.write(SKILL / "user-notes.md", b"User-owned content.\n")
        before = self.snapshot()
        self.run_manager("uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_manifest_cannot_own_another_workspace_file(self) -> None:
        self.run_manager("install")
        victim = self.write(Path("user-document.md"), b"User-owned content.\n")
        state = self.read_json(STATE)
        state["files"]["user-document.md"] = hashlib.sha256(victim.read_bytes()).hexdigest()
        self.write(STATE, json.dumps(state).encode("utf-8"))
        before = self.snapshot()
        self.run_manager("uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_manifest_parent_traversal_is_refused(self) -> None:
        self.run_manager("install")
        victim_relative = Path(".agents/skills/neighbor.md")
        victim = self.write(victim_relative, b"Neighbor content.\n")
        state = self.read_json(STATE)
        state["files"][f"{SKILL.as_posix()}/../neighbor.md"] = hashlib.sha256(victim.read_bytes()).hexdigest()
        self.write(STATE, json.dumps(state).encode("utf-8"))
        before = self.snapshot()
        self.run_manager("uninstall", success=False)
        self.assertEqual(self.snapshot(), before)

    def test_hook_command_runs_from_unicode_path_with_spaces(self) -> None:
        self.run_manager("install", "--hooks")
        handler = self.read_json(HOOKS)["hooks"]["SessionStart"][0]["hooks"][0]
        command = handler.get("commandWindows", handler["command"]) if os.name == "nt" else shlex.split(handler["command"])
        process = subprocess.run(
            command,
            input=b'{"hook_event_name":"SessionStart","source":"startup"}',
            capture_output=True,
            timeout=15,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr.decode("utf-8", errors="replace"))
        context = json.loads(process.stdout)["hookSpecificOutput"]["additionalContext"]
        self.assertIn("I Asked for a Button", context)

    def test_symlinked_install_parent_cannot_write_outside_target(self) -> None:
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "marker.txt").write_bytes(b"Preserve outside content.\n")
        link = self.target / ".agents"
        try:
            link.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks are unavailable: {error}")
        before = self.snapshot(outside)
        self.run_manager("install", success=False)
        self.assertEqual(self.snapshot(outside), before)
        self.assertFalse((self.target / STATE).exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction behavior")
    def test_junctioned_hook_parent_cannot_write_outside_target(self) -> None:
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "marker.txt").write_bytes(b"Preserve outside content.\n")
        link = self.target / ".codex"
        process = subprocess.run(
            ["cmd.exe", "/c", "mklink", "/J", str(link), str(outside)],
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            self.skipTest("Windows junctions are unavailable")
        self.addCleanup(lambda: link.rmdir() if link.exists() else None)
        before = self.snapshot(outside)
        self.run_manager("install", "--hooks", success=False)
        self.assertEqual(self.snapshot(outside), before)
        self.assertFalse((self.target / SKILL).exists())

    def test_status_and_repeated_uninstall(self) -> None:
        self.assertFalse(json.loads(self.run_manager("status").stdout)["installed"])
        self.assertEqual(json.loads(self.run_manager("uninstall").stdout)["changed"], [])
        self.run_manager("install", "--hooks")
        status = json.loads(self.run_manager("status").stdout)
        self.assertTrue(status["installed"])
        self.assertTrue(status["hooks"])
        before = self.snapshot()
        self.assertTrue(json.loads(self.run_manager("uninstall", "--dry-run").stdout)["changed"])
        self.assertEqual(self.snapshot(), before)
        self.run_manager("uninstall")
        self.assertFalse(json.loads(self.run_manager("status").stdout)["installed"])
        self.assertEqual(json.loads(self.run_manager("uninstall").stdout)["changed"], [])
        self.assertEqual(self.snapshot(), {})

    def test_default_global_install_uses_home_and_does_not_create_it_for_read_only_operations(self) -> None:
        codex_home = self.user_home / ".codex"
        for action, arguments in (("status", ()), ("uninstall", ()), ("install", ("--dry-run",))):
            with self.subTest(action=action):
                response = json.loads(self.run_manager(action, *arguments, global_scope=True,
                                                       home_default=True).stdout)
                self.assertEqual(response["scope"], "global")
                self.assertEqual(Path(response["target"]), codex_home)
                self.assertFalse(codex_home.exists())
        first = json.loads(self.run_manager("install", global_scope=True, home_default=True).stdout)
        skill = codex_home / "skills" / NAME
        manifest = codex_home / f"{NAME}-install.json"
        self.assertEqual(Path(first["skill"]), skill)
        self.assertTrue(manifest.is_file())
        source = PROJECT_ROOT / "skills" / NAME
        for path in source.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                self.assertEqual((skill / path.relative_to(source)).read_bytes(), path.read_bytes())
        state = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertTrue(all(path.startswith(f"skills/{NAME}/") for path in state["files"]))
        self.assertEqual(json.loads(self.run_manager("install", global_scope=True,
                                                   home_default=True).stdout)["changed"], [])
        self.assertTrue(json.loads(self.run_manager("status", global_scope=True,
                                                  home_default=True).stdout)["installed"])
        self.assertEqual(self.snapshot(), {})
        self.run_manager("uninstall", global_scope=True, home_default=True)
        self.assertFalse(skill.exists())
        self.assertFalse(manifest.exists())

    def test_codex_home_global_hooks_preserve_configuration_and_existing_hooks(self) -> None:
        self.codex_home.mkdir()
        config = b'model = "user-model"\n[projects."preserved"]\ntrust_level = "trusted"\n'
        (self.codex_home / "config.toml").write_bytes(config)
        hooks_before = b'{\r\n "hooks": {"Stop": []}, "custom": true\r\n}\r\n'
        (self.codex_home / "hooks.json").write_bytes(hooks_before)
        before = self.snapshot(self.codex_home)
        response = json.loads(self.run_manager("install", "--hooks", global_scope=True).stdout)
        self.assertTrue(response["hooks"])
        self.assertEqual(Path(response["target"]), self.codex_home)
        self.assertFalse((self.user_home / ".codex").exists())
        self.assertEqual((self.codex_home / "config.toml").read_bytes(), config)
        hook_config = json.loads((self.codex_home / "hooks.json").read_text(encoding="utf-8"))
        handler = hook_config["hooks"]["SessionStart"][0]["hooks"][0]
        self.assertIn(str(self.codex_home / "skills" / NAME / "scripts/session_start.py"), handler["command"])
        self.assertEqual(hook_config["hooks"]["Stop"], [])
        self.assertIn("/hooks", response["next"])
        self.assertEqual(json.loads(self.run_manager("install", global_scope=True).stdout)["changed"], [])
        self.run_manager("uninstall", global_scope=True)
        self.assertEqual(self.snapshot(self.codex_home), before)

    def test_explicit_workspace_does_not_write_to_codex_home(self) -> None:
        self.run_manager("install", "--hooks")
        self.assertTrue((self.target / SKILL).is_dir())
        self.assertTrue((self.target / STATE).is_file())
        self.assertFalse(self.codex_home.exists())
        status = json.loads(self.run_manager("status").stdout)
        self.assertEqual(status["scope"], "workspace")
        self.assertEqual(Path(status["skill"]), self.target / SKILL)

    def test_global_reinstall_updates_owned_files_and_manifest_version(self) -> None:
        source = self.base / "source"
        (source / "scripts").mkdir(parents=True)
        manager = source / "scripts/manage.py"
        shutil.copy2(MANAGER, manager)
        (source / "VERSION").write_text("0.0.1\n", encoding="utf-8")
        shutil.copytree(PROJECT_ROOT / "skills", source / "skills",
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        self.run_manager("install", "--hooks", global_scope=True, manager=manager)
        source_skill = source / "skills" / NAME
        updated_skill = (source_skill / "SKILL.md").read_bytes() + b"\nUpdated source.\n"
        (source_skill / "SKILL.md").write_bytes(updated_skill)
        (source_skill / "references/color_zh.md").unlink()
        (source_skill / "references/extra.md").write_bytes(b"New supporting reference.\n")
        (source / "VERSION").write_text("0.0.2\n", encoding="utf-8")
        updated = json.loads(self.run_manager("install", global_scope=True, manager=manager).stdout)
        installed_skill = self.codex_home / "skills" / NAME
        self.assertEqual(updated["version"], "0.0.2")
        self.assertTrue(updated["hooks"])
        self.assertEqual((installed_skill / "SKILL.md").read_bytes(), updated_skill)
        self.assertEqual((installed_skill / "references/extra.md").read_bytes(), b"New supporting reference.\n")
        self.assertFalse((installed_skill / "references/color_zh.md").exists())
        self.assertEqual(json.loads(self.run_manager("status", global_scope=True, manager=manager).stdout)["version"], "0.0.2")
        self.run_manager("uninstall", global_scope=True, manager=manager)
        self.assertFalse(installed_skill.exists())

    def test_global_existing_hook_sources_are_not_duplicated_or_overwritten(self) -> None:
        for filename, content in (
            ("config.toml", f'[[hooks.SessionStart]]\ncommand = "python skills/{NAME}/scripts/session_start.py"\n'.encode("utf-8")),
            ("hooks.json", json.dumps({"hooks": {"SessionStart": [{"hooks": [{"command": NAME}]}]}}).encode("utf-8")),
        ):
            with self.subTest(filename=filename):
                codex_home = self.base / filename.replace(".", "-")
                codex_home.mkdir()
                (codex_home / filename).write_bytes(content)
                before = self.snapshot(codex_home)
                self.run_manager("install", "--hooks", global_scope=True,
                                 codex_home=codex_home, success=False)
                self.assertEqual(self.snapshot(codex_home), before)

    def test_adopt_identical_manual_global_installation_without_rewriting_skill(self) -> None:
        skill = self.codex_home / "skills" / NAME
        shutil.copytree(PROJECT_ROOT / "skills" / NAME, skill,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        before = self.snapshot(self.codex_home)
        self.run_manager("install", global_scope=True, success=False)
        self.assertEqual(self.snapshot(self.codex_home), before)
        dry_run = json.loads(self.run_manager("install", "--adopt", "--dry-run", global_scope=True).stdout)
        self.assertEqual(dry_run["changed"], [f"{NAME}-install.json"])
        self.assertEqual(self.snapshot(self.codex_home), before)
        adopted = json.loads(self.run_manager("install", "--adopt", global_scope=True).stdout)
        self.assertEqual(adopted["changed"], [f"{NAME}-install.json"])
        for relative, contents in before.items():
            path = self.codex_home / relative
            self.assertEqual(path.read_bytes() if path.is_file() else None, contents)
        self.assertEqual(json.loads(self.run_manager("install", global_scope=True).stdout)["changed"], [])
        before_repeat = self.snapshot(self.codex_home)
        self.run_manager("install", "--adopt", global_scope=True, success=False)
        self.assertEqual(self.snapshot(self.codex_home), before_repeat)
        self.run_manager("uninstall", global_scope=True)
        self.assertFalse(skill.exists())

    def test_adopt_refuses_different_incomplete_and_extra_files_without_changes(self) -> None:
        source = PROJECT_ROOT / "skills" / NAME
        for variant in ("different", "incomplete", "extra", "bytecode", "missing"):
            with self.subTest(variant=variant):
                codex_home = self.base / variant
                skill = codex_home / "skills" / NAME
                if variant != "missing":
                    shutil.copytree(source, skill, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
                if variant == "different":
                    (skill / "SKILL.md").write_bytes(b"A user-edited skill.\n")
                elif variant == "incomplete":
                    (skill / "references/color.md").unlink()
                elif variant == "extra":
                    (skill / "user-notes.md").write_bytes(b"Keep these notes.\n")
                elif variant == "bytecode":
                    (skill / "__pycache__").mkdir()
                    (skill / "__pycache__/user.pyc").write_bytes(b"User-owned bytecode.\n")
                before = self.snapshot(codex_home)
                self.run_manager("install", "--adopt", "--hooks", global_scope=True,
                                 codex_home=codex_home, success=False)
                self.assertEqual(self.snapshot(codex_home), before)

    def test_global_manifest_cannot_own_configuration_or_another_skill(self) -> None:
        self.run_manager("install", global_scope=True)
        manifest = self.codex_home / f"{NAME}-install.json"
        for relative in ("config.toml", "skills/other/SKILL.md"):
            with self.subTest(relative=relative):
                state = json.loads(manifest.read_text(encoding="utf-8"))
                state["files"][relative] = hashlib.sha256(b"User content.\n").hexdigest()
                manifest.write_text(json.dumps(state), encoding="utf-8")
                before = self.snapshot(self.codex_home)
                self.run_manager("uninstall", global_scope=True, success=False)
                self.assertEqual(self.snapshot(self.codex_home), before)
                state["files"].pop(relative)
                manifest.write_text(json.dumps(state), encoding="utf-8")

    def test_linked_codex_home_is_refused_before_resolving(self) -> None:
        outside = self.base / "outside global"
        outside.mkdir()
        (outside / "marker.txt").write_bytes(b"Preserve outside content.\n")
        try:
            self.codex_home.symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError) as error:
            self.skipTest(f"Symlinks are unavailable: {error}")
        before = self.snapshot(outside)
        self.run_manager("install", "--hooks", global_scope=True, success=False)
        self.assertEqual(self.snapshot(outside), before)


if __name__ == "__main__":
    unittest.main()
