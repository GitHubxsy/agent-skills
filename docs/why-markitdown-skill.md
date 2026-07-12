# 为什么需要 MarkItDown Skill

## 制作背景

这个 Skill 最初是为建设知识库而制作的。知识来源格式多样，可能是 PDF、Word、PowerPoint、Excel、HTML、图片或音频；在进入知识库前，需要先把这些资料转换为统一、适合检索和大语言模型处理的文本。

Agent 因此需要先“读懂文件”，再进行清洗、切分、索引、问答或 RAG 入库。但不同格式有各自的解析方式，缺少统一入口。

如果每次都临时选择工具、安装依赖和编写转换代码，会带来三个问题：

- 相同任务被反复实现；
- 不同格式的输出结构不一致；
- 批量处理、安全边界和结果验证容易被忽略。

因此需要一个专门的 `markitdown` Skill，作为多来源知识统一摄取的入口。

## 这个新 Skill 解决什么问题

`markitdown` Skill 基于 Microsoft 的 [MarkItDown](https://github.com/microsoft/markitdown)，把多种文件和 URL 转换成适合大语言模型读取的 Markdown，并尽量保留标题、列表、表格和链接等结构。

它为 Agent 补充了库本身没有提供的任务流程：

- 自动判断何时应该使用 MarkItDown；
- 统一处理单个文件、多个文件和整个目录；
- 选择更安全的本地、流式或网络转换方式；
- 处理缺失依赖、插件、OCR 和云端解析；
- 检查转换结果是否为空或明显缺失内容。

## 为什么不能只用其他文档 Skill

Word、PowerPoint、Excel 和 PDF Skill 主要用于创建、编辑和高保真验证原始文件。它们适合“写文件”，但处理一批混合格式资料时成本较高，也缺少统一输出。

`markitdown` Skill 专注于“读文件”：把不同载体中的内容快速转成统一 Markdown，方便后续分析。两类 Skill 是互补关系：

> 读取和提取内容，使用 `markitdown`；创建或修改文件，使用格式专用 Skill。

## 核心价值

这个新 Skill 的价值不是增加另一种文档工具，而是为 Agent 建立一条统一、可重复的多格式内容摄取流程。它减少重复实现，让不同来源的资料更快进入总结、搜索、问答和知识库工作流，同时保留必要的安全与验证约束。

---

Skill 定义：[markitdown](../skills/markitdown/SKILL.md)
