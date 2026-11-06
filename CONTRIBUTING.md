# Contributing

[中文](CONTRIBUTING_zh.md)

For a problem report, include the request, the relevant output or action, and the expected result. Add the client and version for loading issues. Use a short, anonymized example; leave out private screenshots, credentials, and complete chats.

## Change the guidance

Edit the [Skill source](skills/i-asked-for-a-button/SKILL.md) for behavior changes and its references for supporting detail. Keep the English and Chinese usage documents in sync.

Retry the reported case. When a rule restricts behavior, also check a case that still needs it—for example, a requested thorough review after reducing unnecessary checks. Describe what changed and the result in the pull request.

## Check scripts

Requires Python 3.11 or newer. From the repository root:

```powershell
python -m unittest discover -s tests -v
```

Test installer changes in a temporary project. For hook changes, use a supported Codex CLI, approve the hook through its normal trust process, and confirm that the Skill text reaches a new session. Include the CLI version and result in the pull request.

## Build the source package

```powershell
python scripts/build_release.py
```

The builder writes a versioned ZIP and `SHA256SUMS` to `dist/`.

Contributions are distributed under the project's [Apache License 2.0](LICENSE).
