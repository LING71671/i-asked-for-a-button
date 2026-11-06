<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README_zh.md">中文</a> · <a href="#install-and-maintain">Install and maintain</a> · <a href="#use">Use</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill source</a></p>

I Asked for a Button is a Skill for Codex and other coding assistants that helps reduce unnecessary wording and work in software development, copy, documentation, and visual deliverables.

## Problems it addresses

Outputs can contain plenty of words while leaving the reader's actual needs unclear. Repetition, stock phrasing, defensive wording, and commentary about the work crowd out useful content.

Successive edits can drop earlier requirements or overlook the purpose of a change. Local fixes can also accumulate without a coherent view of the finished document, interface, or image.

Execution can lose proportion: routine decisions keep returning to the user, small tasks attract unrelated work, or authorized implementation stops at a plan. The Skill guides content, design, and effort by the audience, goal, and context, carrying the work through relevant verification and delivery.

## Install and maintain

### Install globally

```text
Install i-asked-for-a-button globally from https://github.com/LING71671/i-asked-for-a-button. Follow the repository instructions, use its bundled installer, and check the installation result.
```

### Update

```text
Update the global i-asked-for-a-button installation from https://github.com/LING71671/i-asked-for-a-button. Follow the repository instructions, use its bundled installer, and check the update result.
```

### Uninstall

```text
Uninstall the global i-asked-for-a-button Skill using the installer from https://github.com/LING71671/i-asked-for-a-button. Follow the repository instructions and check that it was removed.
```

<details>
<summary><strong>Manual installation and maintenance</strong></summary>

### Manual installation

Requires Python 3.11 or newer. From the source directory:

```powershell
python scripts/manage.py install
```

The default location is `skills/i-asked-for-a-button/` under `CODEX_HOME`. If `CODEX_HOME` is unset, it uses `~/.codex/skills/i-asked-for-a-button/`. Loading and automatic activation depend on the client and the task.

To install only for one existing project in its `.agents/skills/i-asked-for-a-button/` directory, add `--target`:

```powershell
python scripts/manage.py install --target "E:\MyProject"
```

Use the same `--target` when updating, checking status, or uninstalling that project's copy.

### Automatic loading in Codex CLI

If your Codex CLI supports command hooks:

```powershell
python scripts/manage.py install --hooks --dry-run
python scripts/manage.py install --hooks
```

Run `/hooks` in a new Codex CLI session, review the command, and approve it through the CLI's normal trust process. The installer adds a `SessionStart` entry using the full path of the Python interpreter. If you move that interpreter, reinstall and review the updated hook.

Installing again without `--hooks` retains an existing hook.

### Update or remove

To update, get the new source and run the install command again. Preview changes or inspect the current installation with:

```powershell
python scripts/manage.py install --dry-run
python scripts/manage.py status
```

The installer stops if installed files were edited or conflicting files already exist. Preserve your edits before resolving the conflict and retrying.

To remove the installed Skill:

```powershell
python scripts/manage.py uninstall --dry-run
python scripts/manage.py uninstall
```

</details>

## Use

In Codex, enter `$i-asked-for-a-button` followed by your request.

[Acknowledgments](SPONSORED.md) · [Contributing](CONTRIBUTING.md) · [Apache License 2.0](LICENSE)
