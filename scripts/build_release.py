#!/usr/bin/env python3
"""Build the local, reproducible source archive with Python 3.11 or newer."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import stat
import sys
import tempfile
import zipfile


PROJECT_NAME = "i-asked-for-a-button"
ROOT_FILES = (
    ".gitignore",
    "CONTRIBUTING.md",
    "CONTRIBUTING_zh.md",
    "LICENSE",
    "README.md",
    "README_zh.md",
    "VERSION",
)
SOURCE_DIRECTORIES = ("skills", "adapters", "scripts", "tests")
SKILL_FILE = Path("skills") / PROJECT_NAME / "SKILL.md"
REQUIRED_SOURCE_FILES = (
    SKILL_FILE,
    Path("scripts/build_release.py"),
    Path("scripts/manage.py"),
    Path("skills") / PROJECT_NAME / "scripts/session_start.py",
    Path("skills") / PROJECT_NAME / "agents/openai.yaml",
    Path("adapters/codex/hooks.example.json"),
)
SOURCE_SUFFIXES = frozenset({".md", ".py", ".json", ".toml", ".yaml", ".yml", ".txt"})
EXCLUDED_DIRECTORIES = frozenset(
    {
        "__pycache__",
        "private-reference",
        "source-archive",
        "research",
        "dist",
        "node_modules",
        "venv",
        "tmp",
        "temp",
    }
)
SENSITIVE_NAME = re.compile(
    r"(?:\.env(?:\..*)?|(?:auth|credentials?|secrets?|tokens?|passwords?|"
    r"api[_-]?keys?|client[_-]?secrets?|private[_-]?keys?|service[_-]?accounts?)(?:\..*)?|"
    r"id_(?:rsa|dsa|ecdsa|ed25519)(?:\..*)?)\Z",
    re.IGNORECASE,
)
SENSITIVE_SUFFIXES = frozenset({".pem", ".key", ".p12", ".pfx", ".kdbx"})
TEMP_SUFFIXES = ("~", ".bak", ".old", ".orig", ".rej", ".swp", ".swo", ".tmp", ".temp")
VERSION_PATTERN = re.compile(
    r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?\Z"
)
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


class ReleaseError(ValueError):
    """The source tree does not meet the local release requirements."""


@dataclass(frozen=True)
class ReleaseResult:
    archive: Path
    checksums: Path
    sha256: str
    file_count: int


def _reject_link(path: Path) -> None:
    """Reject symlinks and Windows junctions before descending or reading."""
    attributes = path.lstat()
    is_reparse = bool(
        getattr(attributes, "st_file_attributes", 0)
        & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    )
    if stat.S_ISLNK(attributes.st_mode) or is_reparse:
        raise ReleaseError(f"Symbolic links and junctions are not release inputs: {path}")


def _required_file(root: Path, relative: Path) -> Path:
    current = root
    for part in relative.parts:
        current = current / part
        if not current.exists() and not current.is_symlink():
            raise ReleaseError(f"Missing required release file: {relative.as_posix()}")
        _reject_link(current)
    if not current.is_file():
        raise ReleaseError(f"Required release input is not a file: {relative.as_posix()}")
    return current


def _skill_version(text: str) -> str:
    """Read the small, documented metadata.version scalar without a YAML dependency."""
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0] != "---":
        raise ReleaseError("SKILL.md must start with YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ReleaseError("SKILL.md frontmatter is not closed") from error
    in_metadata = False
    versions = []
    metadata_count = 0
    for line in lines[1:end]:
        if line == "metadata:":
            metadata_count += 1
            in_metadata = True
        elif line and not line[0].isspace() and not line.startswith("#"):
            in_metadata = False
        elif in_metadata:
            match = re.fullmatch(r"[ \t]+version:[ \t]+([^#]+?)[ \t]*(?:#.*)?", line)
            if match:
                value = match.group(1).strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                versions.append(value)
    if metadata_count != 1 or len(versions) != 1:
        raise ReleaseError("SKILL.md frontmatter must declare one indented metadata.version scalar")
    return versions[0]


def _read_version(root: Path) -> str:
    version = _required_file(root, Path("VERSION")).read_text(encoding="utf-8-sig").strip()
    if not VERSION_PATTERN.fullmatch(version):
        raise ReleaseError("VERSION must contain one semantic version, for example 0.5.0")
    declared = _skill_version(_required_file(root, SKILL_FILE).read_text(encoding="utf-8-sig"))
    if declared != version:
        raise ReleaseError(f"Version mismatch: VERSION is {version}, SKILL.md metadata.version is {declared}")
    return version


def _excluded(path: Path) -> bool:
    lowered = path.name.lower()
    return (
        lowered.startswith(".")
        or lowered in EXCLUDED_DIRECTORIES
        or bool(SENSITIVE_NAME.fullmatch(lowered))
        or path.suffix.lower() in SENSITIVE_SUFFIXES
        or lowered.endswith(TEMP_SUFFIXES)
    )


def _directory_files(root: Path, directory: Path) -> list[Path]:
    files = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if _excluded(path):
            continue
        _reject_link(path)
        if path.is_dir():
            files.extend(_directory_files(root, path))
        elif path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
            if not path.resolve().is_relative_to(root):
                raise ReleaseError(f"Release input resolves outside the project: {path}")
            files.append(path)
        elif not path.is_file():
            raise ReleaseError(f"Release input is not a regular file: {path}")
    return files


def _test_files(root: Path, directory: Path) -> list[Path]:
    """Include maintained root test modules, without descending into experiment folders."""
    files = []
    for path in sorted(directory.iterdir(), key=lambda item: item.name):
        if not (path.name.startswith("test_") and path.name.endswith(".py")) or _excluded(path):
            continue
        _reject_link(path)
        if not path.is_file():
            continue
        if not path.resolve().is_relative_to(root):
            raise ReleaseError(f"Release input resolves outside the project: {path}")
        files.append(path)
    return files


def collect_release_files(root: Path) -> list[Path]:
    """Collect public documents, runtime sources, and maintained root test modules."""
    files = [_required_file(root, Path(name)) for name in ROOT_FILES]
    for relative in REQUIRED_SOURCE_FILES:
        _required_file(root, relative)
    for name in SOURCE_DIRECTORIES:
        directory = root / name
        if not directory.exists():
            raise ReleaseError(f"Missing required release directory: {name}")
        _reject_link(directory)
        if not directory.is_dir():
            raise ReleaseError(f"Required release input is not a directory: {name}")
        members = _test_files(root, directory) if name == "tests" else _directory_files(root, directory)
        if not members:
            raise ReleaseError(f"Required release directory has no distributable files: {name}")
        files.extend(members)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def build_release(project_root: Path, output_dir: Path | None = None) -> ReleaseResult:
    root = Path(project_root).resolve(strict=True)
    version = _read_version(root)
    files = collect_release_files(root)
    # Read all inputs before creating outputs, so malformed/inaccessible inputs fail cleanly.
    inputs = [(path.relative_to(root).as_posix(), path.read_bytes()) for path in files]
    destination = Path(output_dir) if output_dir is not None else root / "dist"
    destination.mkdir(parents=True, exist_ok=True)
    _reject_link(destination)
    archive_name = f"{PROJECT_NAME}-{version}.zip"
    archive = destination / archive_name
    checksums = destination / "SHA256SUMS"
    with tempfile.TemporaryDirectory(prefix=".build-release-", dir=destination) as staging:
        staged_archive = Path(staging) / archive_name
        with zipfile.ZipFile(staged_archive, "w", compression=zipfile.ZIP_STORED) as bundle:
            for relative, contents in inputs:
                entry = zipfile.ZipInfo(f"{PROJECT_NAME}-{version}/{relative}", FIXED_ZIP_TIME)
                entry.create_system = 3
                entry.external_attr = (stat.S_IFREG | 0o644) << 16
                bundle.writestr(entry, contents)
        digest = hashlib.sha256(staged_archive.read_bytes()).hexdigest()
        staged_checksums = Path(staging) / "SHA256SUMS"
        staged_checksums.write_text(f"{digest}  {archive_name}\n", encoding="ascii", newline="\n")
        staged_archive.replace(archive)
        staged_checksums.replace(checksums)
    return ReleaseResult(archive, checksums, digest, len(inputs))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, help="Output directory (default: project-root/dist)")
    args = parser.parse_args(argv)
    try:
        result = build_release(Path(__file__).resolve().parents[1], args.output_dir)
    except (ReleaseError, OSError, UnicodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Built {result.archive} ({result.file_count} files)")
    print(f"SHA256 {result.sha256}")
    print(f"Checksums {result.checksums}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
