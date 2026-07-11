# Agent Skills

面向 AI 编程助手和人工检视流程的可复用 Skills 集合。每个 Skill 都保持平台无关，不绑定特定 Agent、代码托管平台或文档服务。

## Skills

### explain-diff-for-human-review

将提交、分支、PR/MR、暂存区或工作区代码差异整理为独立 HTML 报告，帮助人类检视修改意图、架构影响、风险、兼容性和验证证据。

- [查看 Skill 定义](skills/explain-diff-for-human-review/SKILL.md)
- 输出为自包含 HTML，无远程脚本、样式或运行时依赖
- 支持 GitHub、CodeHub、GitLab、Gitee 及其他代码托管平台
- 最终判断权保留给人工 reviewer

延伸阅读：[AI 写代码越快，我们越需要认真看代码](docs/ai-writes-code-humans-still-review.md)

## 目录规范

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── scripts/       # 可选：确定性执行脚本
    ├── references/    # 可选：按需加载的参考资料
    ├── assets/        # 可选：输出模板和静态资源
    └── reports/       # 可选：本地生成物，不提交
```

## 使用方式

将需要的 Skill 目录复制或链接到所使用 Agent 的 Skill 搜索路径。不同 Agent 的安装目录可能不同，以对应平台的 Skill 发现机制为准。

直接使用仓库路径的 Agent，可以指向：

```text
skills/explain-diff-for-human-review/SKILL.md
```

## 新增 Skill

1. 在 `skills/` 下创建与 Skill 名称一致的目录。
2. 添加包含 `name` 和 `description` frontmatter 的 `SKILL.md`。
3. 保持说明平台无关，并明确输入、输出和校验流程。
4. 不提交报告、凭证、私钥或被检视项目的敏感内容。

## License

[Apache License 2.0](LICENSE)
