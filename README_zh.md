<h1 align="center">I Asked for a Button</h1>

<p align="center"><a href="README.md">English</a> · <a href="#安装与维护">安装与维护</a> · <a href="#使用">使用</a> · <a href="skills/i-asked-for-a-button/SKILL.md">Skill 正文</a></p>

　　I Asked for a Button 是给 Codex 等编程助手使用的 Skill，用于减少软件开发、文案、文档和视觉交付中的多余表达与工作。

## 解决什么问题

　　内容写了很多，却没有分清读者真正需要什么。重复解释、套路表达和制作过程的说明挤占了有用信息。

　　连续修改容易偏离原意：只顾最新要求，丢失此前约定，或把已经删去的内容重新带回来。局部修补不断增加，文档、界面或图像却缺少整体判断。

　　执行任务也容易失去分寸：常规决定反复交回用户，简单工作附带无关工程，或已经获准实施却停在计划上。这个 Skill 根据读者、目标和上下文指导内容取舍、设计与工作量，把任务推进到相关验证和交付。

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

　　[致谢](SPONSORED_zh.md) · [贡献说明](CONTRIBUTING_zh.md) · [Apache License 2.0](LICENSE)
