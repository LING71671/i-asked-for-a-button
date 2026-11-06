<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README.md">English</a> · <a href="#安装与维护">安装与维护</a> · <a href="#使用">使用</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill 正文</a></p>

　　I Asked for a Button 是给 Codex 等编程助手使用的 Skill，用于减少软件开发、文案、文档和视觉交付中的多余表达与工作。

## 覆盖范围

### 写作与多轮编辑

　　根据读者和用途取舍信息，保留操作所需的内容和作者自然的说法。减少重复解释、套路口号、无端否定和句尾兜底，标题与按钮名称说明实际用途和操作结果。

　　多轮修改持续保留要求，避免已删内容在后续回复或修改说明中重新出现。要求只给正文、代码或 JSON 时，直接交付相应内容。

### 界面与视觉交付

　　用布局、命名、默认值和控件状态表达操作，按当前任务决定哪些说明需要留在页面、哪些适合放入帮助。

　　视觉要求覆盖栅格对齐、响应式布局、展开菜单、相关控件状态，以及键盘和触屏操作。[配色指导](skills/i-asked-for-a-button/references/color_zh.md) 同时考虑层次、可见性和阅读舒适性。图片与页面省去复述制作要求的附加文字。

### 执行与验证

　　在已授权范围内推进工作，自行完成常规、可逆的决定，把实施任务做到相关验证和交付。讨论和审查按用户要求给出分析与发现。

　　沿用现有实现，按任务实际需要选择调查、依赖、重构和测试，减少小改动附带的大工程。汇报实际变化、验证结果和影响使用的未解决问题。

## 安装与维护

### 全局安装

```text
请从 https://github.com/LING71671/i-asked-for-a-button 全局安装 i-asked-for-a-button，按照仓库说明使用附带安装器，并检查安装结果。
```

### 更新

```text
请从 https://github.com/LING71671/i-asked-for-a-button 更新全局安装的 i-asked-for-a-button，按照仓库说明使用附带安装器，并检查更新结果。
```

### 卸载

```text
请按照 https://github.com/LING71671/i-asked-for-a-button 的说明，使用附带安装器卸载全局安装的 i-asked-for-a-button，并检查是否已移除。
```

<details>
<summary><strong>手动安装与维护</strong></summary>

### 手动安装

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

### 在 Codex CLI 中自动加载

　　如果 Codex CLI 支持命令 hooks：

```powershell
python scripts/manage.py install --hooks --dry-run
python scripts/manage.py install --hooks
```

　　在新的 Codex CLI 会话中运行 `/hooks`，查看命令，再通过 CLI 的正常信任流程确认。安装器加入一条 `SessionStart` 配置，使用 Python 解释器的完整路径。如果移动了解释器，需要重新安装并审核更新后的 hook。

　　再次安装时不加 `--hooks`，会保留已有 hook。

### 更新与卸载

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

　　在 Codex 中输入 `$i-asked-for-a-button`，接着写你的需求。

　　[贡献说明](CONTRIBUTING_zh.md) · [Apache License 2.0](LICENSE)
