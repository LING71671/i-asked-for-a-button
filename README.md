<p align="center"><img src="assets/logo.svg" alt="A black and white push button" width="128" height="128" /></p>

<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README_zh.md">中文</a> · <a href="#install-and-maintain">Install and maintain</a> · <a href="#use">Use</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill source</a></p>

I Asked for a Button is a Codex plugin for reducing unnecessary wording and work in software development, copy, documentation, and visual deliverables. Its Skill can also be installed on its own.

## Problems it addresses

Outputs can contain plenty of words while leaving the reader's actual needs unclear. Repetition, stock phrasing, defensive wording, and commentary about the work crowd out useful content.

Successive edits can drop earlier requirements or overlook the purpose of a change. Local fixes can also accumulate without a coherent view of the finished document, interface, or image.

An assistant may stop after finding a likely cause, leaving you to ask for the fix and its verification. When you've asked it to implement a change, the Skill directs it to take the next available step and check the result. If one part is blocked, it can still finish the independent parts.

## Install and maintain

### Install globally

```text
Install i-asked-for-a-button globally as a Codex plugin from https://github.com/LING71671/i-asked-for-a-button. Follow the repository's plugin installation instructions and check that the plugin is installed and enabled.
```

### Update

```text
Update the global i-asked-for-a-button installation from https://github.com/LING71671/i-asked-for-a-button. Identify whether it is installed as a plugin or a standalone Skill, follow the matching repository instructions, and check the result.
```

### Uninstall

```text
Uninstall the global i-asked-for-a-button installation. Follow https://github.com/LING71671/i-asked-for-a-button for the installed plugin or standalone Skill and check that it was removed.
```

<details>
<summary><strong>Manual installation and maintenance</strong></summary>

### Codex plugin

Use a Codex CLI that supports plugin commands:

```powershell
codex plugin marketplace add LING71671/i-asked-for-a-button
codex plugin add i-asked-for-a-button@i-asked-for-a-button
codex plugin list --marketplace i-asked-for-a-button --json
```

Restart Codex to refresh the installed plugin list under Customize > Plugins.

To update the plugin:

```powershell
codex plugin marketplace upgrade i-asked-for-a-button
codex plugin add i-asked-for-a-button@i-asked-for-a-button
```

To remove it:

```powershell
codex plugin remove i-asked-for-a-button@i-asked-for-a-button
```

### Standalone Skill

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

### Automatic loading for the standalone Skill

If your Codex CLI supports command hooks:

```powershell
python scripts/manage.py install --hooks --dry-run
python scripts/manage.py install --hooks
```

Run `/hooks` in a new Codex CLI session, review the command, and approve it through the CLI's normal trust process. The installer adds a `SessionStart` entry using the full path of the Python interpreter. If you move that interpreter, reinstall and review the updated hook.

Installing again without `--hooks` retains an existing hook.

### Update or remove the standalone Skill

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

When the Skill is loaded, describe the task in your own words. To select it explicitly, mention I Asked for a Button or use `$i-asked-for-a-button` for a standalone installation.

“Export ignores the folder I pick. Fix it.” The assistant can trace the selected folder from the file picker to the save operation, fix the issue, and try an export to see where the file lands.

## Acknowledgments

Thanks to the [LINUX DO community](https://linux.do/) for providing a platform to promote this project.

[Contributing](CONTRIBUTING.md) · [Apache License 2.0](LICENSE)
