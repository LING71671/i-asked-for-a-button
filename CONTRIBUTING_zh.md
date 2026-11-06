# 贡献说明

[English](CONTRIBUTING.md)

　　报告问题时附上请求、相关输出或操作，以及预期结果。加载问题另附客户端和版本。使用简短、去除个人信息的例子，省去私人截图、凭据和完整聊天。

## 修改指导

　　行为修改写在 [Skill 正文](skills/i-asked-for-a-button/SKILL.md)，详细资料放在其参考文件中，中英文使用文档同步更新。

　　重试报告中的场景。规则限制某种行为时，再检查一个仍需保留该行为的场景，例如减少多余检查后，仍应完成用户要求的深入审查。在拉取请求中说明具体修改和结果。

## 检查脚本

　　需要 Python 3.11 或更新版本。在仓库根目录运行：

```powershell
python -m unittest discover -s tests -v
```

　　安装器修改在临时项目中测试。修改 hook 时，使用支持它的 Codex CLI，通过正常信任流程确认 hook，再检查 Skill 正文是否传入新会话。在拉取请求中注明 CLI 版本和结果。

## 构建源码包

```powershell
python scripts/build_release.py
```

　　构建器在 `dist/` 中生成带版本号的 ZIP 和 `SHA256SUMS`。

　　贡献内容按项目的 [Apache License 2.0](LICENSE) 分发。
