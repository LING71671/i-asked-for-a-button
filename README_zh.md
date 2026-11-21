<p align="center"><img src="assets/logo.svg" alt="黑白按钮" width="128" height="128" /></p>

<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README.md">English</a> · <a href="#安装与维护">安装与维护</a> · <a href="#使用">使用</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill 正文</a></p>

　　I Asked for a Button 是一个 Codex 插件，用于减少软件开发、文案、文档和视觉交付中的多余表达与工作。内含的 Skill 也可以独立安装。

## 解决什么问题

　　内容写了很多，却没有分清读者真正需要什么。重复解释、套路表达、防御性表述和制作过程的说明挤占了有用信息。

　　连续修改容易丢失此前约定，也容易忽略修改背后的意图。局部修补不断增加，文档、界面或图像却缺少整体判断。

　　有时助手找到可能的原因就停下了，修复和验证都要再催一次。用户已经要求动手时，这个 Skill 会引导助手直接做能做的下一步，并验证结果。即使一处卡住，也可以先完成其他不受影响的部分。

## 安装与维护

### 全局安装

```text
请从 https://github.com/LING71671/i-asked-for-a-button 将 i-asked-for-a-button 作为 Codex 插件全局安装，按照仓库的插件安装说明操作，并检查插件已安装且启用。
```

### 更新

```text
请从 https://github.com/LING71671/i-asked-for-a-button 更新全局安装的 i-asked-for-a-button，识别当前是插件还是独立 Skill 安装，按照仓库中对应的说明操作，并检查更新结果。
```

### 卸载

```text
请按照 https://github.com/LING71671/i-asked-for-a-button 的说明，卸载当前全局安装的 i-asked-for-a-button 插件或独立 Skill，并检查是否已移除。
```

<details>
<summary><strong>手动安装与维护</strong></summary>

### Codex 插件

　　使用支持插件命令的 Codex CLI：

```powershell
codex plugin marketplace add LING71671/i-asked-for-a-button
codex plugin add i-asked-for-a-button@i-asked-for-a-button
codex plugin list --marketplace i-asked-for-a-button --json
```

　　重启 Codex 后，可在“自定义 → 插件”的已安装列表中查看。

　　更新插件：

```powershell
codex plugin marketplace upgrade i-asked-for-a-button
codex plugin add i-asked-for-a-button@i-asked-for-a-button
```

　　卸载插件：

```powershell
codex plugin remove i-asked-for-a-button@i-asked-for-a-button
```

### 独立 Skill

　　需要 Python 3.11 或更新版本。从源码目录运行：

```powershell
python scripts/manage.py install
```

　　默认安装到 `CODEX_HOME` 下的 `skills/i-asked-for-a-button/`；未设置 `CODEX_HOME` 时，使用 `~/.codex/skills/i-asked-for-a-button/`。加载方式和是否自动启用取决于客户端与当前任务。

　　如果只安装到某个已有项目的 `.agents/skills/i-asked-for-a-button/` 目录，添加 `--target`：

```powershell
python scripts/manage.py install --target "E:\MyProject"
```

　　更新、查看状态或卸载该项目中的安装时，也使用同一个 `--target`。

### 独立 Skill 在 Codex CLI 中自动加载

　　如果 Codex CLI 支持命令 hooks：

```powershell
python scripts/manage.py install --hooks --dry-run
python scripts/manage.py install --hooks
```

　　在新的 Codex CLI 会话中运行 `/hooks`，查看命令，再通过 CLI 的正常信任流程确认。安装器加入一条 `SessionStart` 配置，使用 Python 解释器的完整路径。如果移动了解释器，需要重新安装并审核更新后的 hook。

　　再次安装时不加 `--hooks`，会保留已有 hook。

### 独立 Skill 的更新与卸载

　　更新时，取得新版源码，再运行同一安装命令。可以先预览变更或查看当前安装状态：

```powershell
python scripts/manage.py install --dry-run
python scripts/manage.py status
```

　　如果安装文件被修改，或已有文件发生冲突，安装器会停止。先保留自己的修改，处理冲突后再重试。

　　卸载已安装的 Skill：

```powershell
python scripts/manage.py uninstall --dry-run
python scripts/manage.py uninstall
```

</details>

## 使用

　　Skill 加载后，照常描述任务就行。想明确指定它时，可以提到 I Asked for a Button。独立安装时，也可以用 `$i-asked-for-a-button` 调用。

　　比如直接说“导出没存到我选的文件夹，帮我修好”。助手可以沿着用户选的路径找到写文件的地方，修复后实际导出一次，看文件存到了哪里。

## 致谢

　　感谢 [LINUX DO 社区](https://linux.do/) 提供项目推广平台。

　　[贡献说明](CONTRIBUTING_zh.md) · [Apache License 2.0](LICENSE)
