<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README_zh.md">中文</a> · <a href="#install-and-maintain">Install and maintain</a> · <a href="#use">Use</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill source</a></p>

I Asked for a Button is a Skill for Codex and other coding assistants that helps reduce unnecessary wording and work in software development, copy, documentation, and visual deliverables.

## What it covers

### Writing and successive edits

Select information for the reader and purpose, retaining needed instructions and the author's natural wording. Reduce repetition, formulaic slogans, unprompted rebuttals, and stock closing caveats. Headings and control labels name the actual purpose, action, and outcome.

Carry requirements through successive edits so removed content stays out of later replies and editing commentary. When asked for only text, code, or JSON, deliver that content directly.

### Interfaces and visual work

Use layout, labels, defaults, and control states to communicate actions. Place explanations according to the current task, keeping needed information on the page and optional detail in help where useful.

Visual guidance covers grid alignment, responsive layouts, open menus, relevant control states, and keyboard and touch interaction. The [color guidance](skills/i-asked-for-a-button/references/color.md) considers hierarchy, visibility, and reading comfort. Images and pages omit captions that merely restate production requirements.

### Execution and verification

Work within the authorized scope, make routine reversible decisions, and carry implementation through relevant checks and delivery. Discussion and review requests receive the requested analysis and findings.

Reuse existing work and choose investigations, dependencies, refactors, and tests for the actual task, reducing unnecessary work attached to small changes. Report actual changes, check results, and unresolved issues that affect use.

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

[Contributing](CONTRIBUTING.md) · [Apache License 2.0](LICENSE)
