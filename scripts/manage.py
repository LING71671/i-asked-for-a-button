"""Install the skill globally by default, or into an explicit workspace."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import shlex
import stat
import subprocess
import sys
import tempfile
import tomllib

NAME = "i-asked-for-a-button"
ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(".agents") / "skills" / NAME
STATE = Path(".codex") / f"{NAME}-install.json"
HOOKS = Path(".codex") / "hooks.json"


@dataclass(frozen=True)
class Installation:
    root: Path
    global_scope: bool = False

    @property
    def skill(self) -> Path:
        return Path("skills") / NAME if self.global_scope else SKILL

    @property
    def state(self) -> Path:
        return Path(f"{NAME}-install.json") if self.global_scope else STATE

    @property
    def hooks(self) -> Path:
        return Path("hooks.json") if self.global_scope else HOOKS

    @property
    def config(self) -> Path:
        return Path("config.toml") if self.global_scope else Path(".codex/config.toml")


class InstallError(Exception):
    """An actionable installation conflict."""


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def safe_path(root: Path, relative: Path) -> Path:
    if relative.is_absolute() or ".." in relative.parts:
        raise InstallError("installation manifest contains an unsafe path")
    path = root / relative
    for ancestor in [path, *path.parents]:
        if ancestor == root:
            break
        if ancestor.exists() or ancestor.is_symlink():
            flags = ancestor.lstat().st_file_attributes if os.name == "nt" else 0
            if ancestor.is_symlink() or flags & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                raise InstallError(f"linked installation path: {ancestor}")
    if not path.resolve().is_relative_to(root):
        raise InstallError(f"path escapes installation root: {path}")
    return path


def parse_object(raw: bytes, label: str) -> dict:
    try:
        value = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, ValueError) as error:
        raise InstallError(f"invalid {label}: {error}") from error
    if not isinstance(value, dict):
        raise InstallError(f"{label} must be a JSON object")
    return value


def hook_groups(config: dict) -> list:
    hooks = config.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise InstallError("hooks.json: hooks must be an object")
    groups = hooks.setdefault("SessionStart", [])
    if not isinstance(groups, list):
        raise InstallError("hooks.json: SessionStart must be an array")
    return groups


def load_state(installation: Installation) -> dict | None:
    target = installation.root
    path = safe_path(target, installation.state)
    if not path.exists():
        return None
    state = parse_object(path.read_bytes(), "installation manifest")
    if state.get("format") != 1 or state.get("name") != NAME or not isinstance(state.get("files"), dict):
        raise InstallError("unrecognized installation manifest; no files were changed")
    for relative, checksum in state["files"].items():
        path = Path(relative)
        if not path.is_relative_to(installation.skill) or not isinstance(checksum, str):
            raise InstallError("installation manifest contains an unowned path")
        safe_path(target, path)
    return state


def verify_owned(installation: Installation, state: dict) -> None:
    target = installation.root
    for relative, checksum in state["files"].items():
        path = safe_path(target, Path(relative))
        if not path.is_file() or digest(path.read_bytes()) != checksum:
            raise InstallError(f"installed file was changed or removed: {path}; preserve or restore it before retrying")
    skill_path = safe_path(target, installation.skill)
    for path in skill_path.rglob("*"):
        safe_path(target, path.relative_to(target))
        if path.is_file() and path.relative_to(target).as_posix() not in state["files"]:
            if path.suffix == ".pyc" and path.parent.name == "__pycache__":
                continue
            raise InstallError(f"unowned file inside installed skill: {path}")
    if state.get("hook") is not None:
        hooks_path = safe_path(target, installation.hooks)
        if not hooks_path.is_file():
            raise InstallError("installed hook configuration was removed")
        groups = hook_groups(parse_object(hooks_path.read_bytes(), "hooks.json"))
        if groups.count(state["hook"]) != 1:
            raise InstallError("installed hook was changed or duplicated; no files were changed")


def make_hook(installation: Installation) -> dict:
    args = [str(Path(sys.executable).resolve()),
            str(installation.root / installation.skill / "scripts" / "session_start.py")]
    command = subprocess.list2cmdline(args) if os.name == "nt" else shlex.join(args)
    handler = {"type": "command", "command": command, "timeout": 3, "additionalContextLimit": 4000}
    if os.name == "nt":
        handler["commandWindows"] = command
    return {"matcher": "^(startup|resume|clear|compact|fork)$", "hooks": [handler]}


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def apply_writes(target: Path, writes: dict[Path, bytes | None]) -> None:
    originals = {}
    for relative in writes:
        path = safe_path(target, relative)
        originals[relative] = path.read_bytes() if path.exists() else None
    changed = []
    try:
        for relative, data in writes.items():
            path = safe_path(target, relative)
            changed.append(relative)
            if data is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, data)
    except OSError:
        for relative in reversed(changed):
            path = safe_path(target, relative)
            if originals[relative] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, originals[relative])
        raise


def verify_identical(installation: Installation, files: dict[Path, bytes]) -> None:
    """Adopt only a complete, unchanged manual copy of this source skill."""
    target = installation.root
    skill_path = safe_path(target, installation.skill)
    if not skill_path.is_dir():
        raise InstallError("--adopt requires an existing, identical skill without an installation manifest")
    for path in skill_path.rglob("*"):
        relative = path.relative_to(target)
        safe_path(target, relative)
        if path.is_file():
            if relative not in files:
                raise InstallError(f"cannot adopt an unowned file: {path}")
    for relative, data in files.items():
        path = safe_path(target, relative)
        if not path.is_file() or path.read_bytes() != data:
            raise InstallError(f"cannot adopt a different or incomplete skill: {path}")


def install(installation: Installation, hooks: bool, dry_run: bool, adopt: bool = False) -> dict:
    target = installation.root
    state = load_state(installation)
    if state is not None:
        if adopt:
            raise InstallError("--adopt requires a skill without an installation manifest")
        verify_owned(installation, state)
    source = ROOT / "skills" / NAME
    files = {}
    for path in sorted(source.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        safe_path(source, path.relative_to(source))
        if path.is_file():
            files[installation.skill / path.relative_to(source)] = path.read_bytes()
    if not files or not all((source / path).is_file() for path in
                            ("SKILL.md", "agents/openai.yaml", "scripts/session_start.py")):
        raise InstallError("source skill is incomplete")
    if state is None:
        if adopt:
            verify_identical(installation, files)
        elif safe_path(target, installation.skill).exists():
            raise InstallError(f"skill already exists without this installer's manifest: {target / installation.skill}; "
                               "use --adopt only for an identical manual installation")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    enabled = hooks or (state is not None and state.get("hook") is not None)
    writes: dict[Path, bytes | None] = dict(files)
    new_state = {"format": 1, "name": NAME, "version": version,
                 "files": {path.as_posix(): digest(data) for path, data in files.items()}, "hook": None}
    if state:
        for relative in state["files"]:
            if Path(relative) not in files:
                writes[Path(relative)] = None
    if enabled:
        toml_path = safe_path(target, installation.config)
        if toml_path.is_file():
            toml_config = tomllib.loads(toml_path.read_text(encoding="utf-8-sig"))
            if NAME in json.dumps(toml_config.get("hooks", {})):
                raise InstallError("inline TOML hooks already reference this skill; keep one hook source")
        hooks_path = safe_path(target, installation.hooks)
        raw = hooks_path.read_bytes() if hooks_path.exists() else None
        config = parse_object(raw, "hooks.json") if raw is not None else {}
        groups = hook_groups(config)
        previous_hook = state.get("hook") if state else None
        if previous_hook is not None:
            groups.remove(previous_hook)
        new_hook = make_hook(installation)
        if any(NAME in json.dumps(group) for group in groups):
            raise InstallError("another hook references this skill; remove the duplicate source before enabling")
        groups.append(new_hook)
        new_state["hook"] = new_hook
        new_state["hooks_before"] = state["hooks_before"] if previous_hook else (raw.decode("utf-8") if raw is not None else None)
        writes[installation.hooks] = json_bytes(config)
    writes[installation.state] = json_bytes(new_state)
    writes = {path: data for path, data in writes.items()
              if (safe_path(target, path).read_bytes() if safe_path(target, path).is_file() else None) != data}
    if not dry_run:
        apply_writes(target, writes)
    return {"action": "install", "version": version, "target": str(target), "hooks": enabled,
            "dry_run": dry_run, "changed": [path.as_posix() for path in writes],
            "next": "Review and trust this hook with /hooks in a new local Codex CLI session." if enabled else "Invoke $i-asked-for-a-button in Codex CLI."}


def uninstall(installation: Installation, dry_run: bool) -> dict:
    target = installation.root
    state = load_state(installation)
    if state is None:
        return {"action": "uninstall", "target": str(target), "changed": [], "dry_run": dry_run}
    verify_owned(installation, state)
    writes: dict[Path, bytes | None] = {Path(path): None for path in state["files"]}
    if state.get("hook") is not None:
        path = safe_path(target, installation.hooks)
        config = parse_object(path.read_bytes(), "hooks.json")
        hook_groups(config).remove(state["hook"])
        before = state["hooks_before"]
        baseline = parse_object(before.encode("utf-8"), "original hooks.json") if before is not None else {}
        normalized = json.loads(json.dumps(baseline))
        hook_groups(normalized)
        if config == normalized:
            writes[installation.hooks] = before.encode("utf-8") if before is not None else None
        else:
            writes[installation.hooks] = json_bytes(config)
    writes[installation.state] = None
    if not dry_run:
        apply_writes(target, writes)
        # Remove only now-empty directories; never recursively delete user content.
        directories = {safe_path(target, path).parent for path in writes}
        for path in list(directories):
            directories.update(parent for parent in path.parents if parent != target and parent.is_relative_to(target))
        for path in sorted(directories, key=lambda item: len(item.parts), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass
    return {"action": "uninstall", "target": str(target), "changed": [path.as_posix() for path in writes], "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    for action in ("install", "status", "uninstall"):
        command = commands.add_parser(action)
        command.add_argument("--target", type=Path,
                             help="Use an existing workspace instead of the global CODEX_HOME installation")
        if action != "status":
            command.add_argument("--dry-run", action="store_true")
        if action == "install":
            command.add_argument("--hooks", action="store_true", help="Add optional SessionStart context loading")
            command.add_argument("--adopt", action="store_true",
                                 help="Manage an identical manual installation that has no manifest")
    args = parser.parse_args()
    try:
        if args.target is not None:
            target = args.target.expanduser().resolve(strict=True)
            if not target.is_dir():
                raise InstallError("target must be an existing workspace directory")
            installation = Installation(target)
        else:
            target = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser().absolute()
            # Check before resolving: a linked CODEX_HOME must not redirect writes.
            for ancestor in (target, *target.parents):
                if ancestor.exists() or ancestor.is_symlink():
                    flags = ancestor.lstat().st_file_attributes if os.name == "nt" else 0
                    if ancestor.is_symlink() or flags & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0):
                        raise InstallError(f"linked global installation path: {ancestor}")
            target = target.resolve()
            if target.exists() and not target.is_dir():
                raise InstallError("CODEX_HOME must be a directory")
            installation = Installation(target, global_scope=True)
        if args.action == "install":
            result = install(installation, args.hooks, args.dry_run, args.adopt)
        elif args.action == "uninstall":
            result = uninstall(installation, args.dry_run)
        else:
            state = load_state(installation)
            if state is not None:
                verify_owned(installation, state)
            result = {"installed": state is not None, "version": state["version"] if state else None,
                      "hooks": state.get("hook") is not None if state else False, "target": str(target)}
        result["scope"] = "global" if installation.global_scope else "workspace"
        result["skill"] = str(target / installation.skill)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (InstallError, OSError, ValueError, KeyError) as error:
        print(f"{NAME}: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
