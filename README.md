# Agent Skills

面向 AI 编程助手和人工检视流程的可复用 Skills 集合。每个 Skill 会明确自己的平台依赖、输入、输出和操作边界。

## Skills

### explain-diff-for-human-review

将提交、分支、PR/MR、暂存区或工作区代码差异整理为自包含 HTML 报告，以最小有效视图帮助人类理解行为变化、系统形状、风险和验证证据。

- [查看 Skill 定义](skills/explain-diff-for-human-review/SKILL.md)
- 输出为自包含 HTML，无远程脚本、样式或运行时依赖
- 根据改动选择伪代码、调用树、组件树、文件树、流程图或 `diff` 视图
- 支持 GitHub、CodeHub、GitLab、Gitee 及其他代码托管平台
- 最终判断权保留给人工 reviewer

延伸阅读：[AI 写代码越快，我们越需要认真看代码](docs/ai-writes-code-humans-still-review.md)

### commit-mr

将当前任务的改动提交并推送到 CodeHub，创建或更新 MR，同时用简洁的 Review 地图和最小有效视图呈现行为变化、实现结构、风险与验证证据。

- [查看 Skill 定义](skills/commit-mr/SKILL.md)
- 明确调用后，自动整理任务改动、提交、推送并创建或更新 CodeHub MR
- 可按改动选择伪代码、调用树、组件树、文件树、流程图或契约差异
- 区分代码事实、声明意图、待确认推断和实际验证结果
- 使用本机 `ch` CLI 的实际帮助发现命令，不套用 GitHub CLI 语法
- 自动获取仓库 MR 模板，能回答的字段据实填写，无法确认的字段留空并追加到结构化描述之后
- 只暂存当前任务文件，不强推、不改写历史，也不混入无关改动

延伸阅读：[如何让 AI 写的 MR 更容易 Review](docs/make-ai-written-mrs-easier-to-review.md)

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
skills/commit-mr/SKILL.md
```

## 新增 Skill

1. 在 `skills/` 下创建与 Skill 名称一致的目录。
2. 添加包含 `name` 和 `description` frontmatter 的 `SKILL.md`。
3. 明确平台依赖、输入、输出、授权边界和校验流程。
4. 不提交报告、凭证、私钥或被检视项目的敏感内容。

## License

[Apache License 2.0](LICENSE)
