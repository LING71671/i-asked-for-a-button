#!/usr/bin/env python3
"""Send the bundled skill body to a Codex SessionStart hook (Python 3.11+)."""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys


MAX_INPUT_BYTES = 64 * 1024
MAX_SKILL_BYTES = 8 * 1024
MAX_OUTPUT_BYTES = 8 * 1024
SOURCES = frozenset({"startup", "resume", "clear", "compact", "fork"})
SCOPE = (
    "The complete $i-asked-for-a-button Skill is loaded below. Apply it without reloading. "
    "Scope: software development, copy, documentation, and visual deliverables; "
    "not standalone fiction writing or general conversation. "
    "Follow user requests, repository rules, safety, and authorization."
)


class LoaderError(Exception):
    """An expected input or package error suitable for a short diagnostic."""


def reject_json_constant(value: str) -> None:
    raise ValueError(f"invalid JSON constant: {value}")


def read_event() -> None:
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise LoaderError("event exceeds the 64 KiB input limit")
    try:
        event = json.loads(
            raw.decode("utf-8-sig"),
            parse_constant=reject_json_constant,
        )
    except (UnicodeDecodeError, ValueError, RecursionError) as exc:
        raise LoaderError("event must be a valid UTF-8 JSON object") from exc
    if not isinstance(event, dict):
        raise LoaderError("event must be a JSON object")
    if event.get("hook_event_name") != "SessionStart":
        raise LoaderError("hook_event_name must be SessionStart")
    source = event.get("source")
    if not isinstance(source, str) or source not in SOURCES:
        raise LoaderError("unsupported SessionStart source")


def read_version(frontmatter: list[str]) -> str:
    """Read the scalar metadata.version from the package's block YAML mapping."""
    metadata_blocks: list[list[str]] = []
    for index, line in enumerate(frontmatter):
        if re.fullmatch(r"metadata:[ \t]*(?:#.*)?", line):
            block: list[str] = []
            for child in frontmatter[index + 1 :]:
                if child.strip() and not child.startswith((" ", "#")):
                    break
                if child.strip() and not child.lstrip().startswith("#"):
                    block.append(child)
            metadata_blocks.append(block)
    if len(metadata_blocks) != 1 or not metadata_blocks[0]:
        raise LoaderError("SKILL.md requires a metadata.version block scalar")
    block = metadata_blocks[0]
    indentation = min(len(line) - len(line.lstrip(" ")) for line in block)
    values = []
    for line in block:
        match = re.fullmatch(r" {" + str(indentation) + r"}version:[ \t]*(.*)", line)
        if match:
            values.append(match.group(1).split(" #", 1)[0].strip())
    if len(values) != 1:
        raise LoaderError("SKILL.md requires exactly one metadata.version")
    version = values[0]
    if len(version) >= 2 and version[0] in {"'", '"'} and version[-1] == version[0]:
        version = version[1:-1]
    if not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", version):
        raise LoaderError("SKILL.md metadata.version must be a semantic version")
    return version


def read_skill() -> tuple[str, str]:
    skill_path = Path(__file__).resolve().parents[1] / "SKILL.md"
    try:
        with skill_path.open("rb") as stream:
            raw = stream.read(MAX_SKILL_BYTES + 1)
    except OSError as exc:
        raise LoaderError("cannot read the bundled SKILL.md") from exc
    if len(raw) > MAX_SKILL_BYTES:
        raise LoaderError("SKILL.md exceeds the 8 KiB package limit")
    try:
        document = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise LoaderError("SKILL.md must be UTF-8") from exc
    lines = document.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise LoaderError("SKILL.md requires YAML frontmatter")
    end = next(
        (index for index, line in enumerate(lines[1:], 1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if end is None:
        raise LoaderError("SKILL.md frontmatter is not closed")
    version = read_version([line.rstrip("\r\n") for line in lines[1:end]])
    body = "".join(lines[end + 1 :])
    if not body.strip():
        raise LoaderError("SKILL.md body is empty")
    return version, body


def main() -> int:
    try:
        read_event()
        version, body = read_skill()
        payload = {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": (
                    f"[I Asked for a Button / {version}]\n{SCOPE}\n"
                    f"Resolve referenced files from: {Path(__file__).resolve().parents[1].as_posix()}\n\n{body}"
                ),
            }
        }
        output = (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
        if len(output) > MAX_OUTPUT_BYTES:
            raise LoaderError("context exceeds the 8 KiB output limit; shorten SKILL.md")
    except LoaderError as exc:
        print(f"i-asked-for-a-button: {exc}", file=sys.stderr)
        return 1
    sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
