# 1. 总览：Model + Harness 与"开放式 Agent Loop"

## 1.1 它和 Open Notebook 最本质的不同

上一章的 Open Notebook 是**写死的 LangGraph 状态图**——开发者预先规定"先抽取、再嵌入、再落库"，模型只在节点里被调用。Claude Code 走的是另一条路：**开放式 Agent Loop**。

它的循环本质很简单，就是第二部分讲的 **ReAct** 的工业级放大版：

```
读取上下文（System Prompt + CLAUDE.md + 对话历史 + 工具结果）
        │
        ▼
   模型决定下一步：要么回复用户，要么调用一个工具
        │
        ▼
   执行工具（受权限层把关）→ 把结果塞回上下文
        │
        ▼
   回到第一步，直到任务完成 / 用户打断
```

关键差别：**下一步做什么，是模型在循环里自己决定的**，不是开发者写死的。这带来高自主性（能自己探索代码库、自己决定改哪些文件、自己跑测试再修），也带来风险（可能改错、跑危险命令）——于是 Harness 的大量设计都在"**给这份自主性套上缰绳**"：权限、钩子、子智能体隔离、计划模式。

## 1.2 仓库构成：薄壳 + 生态

既然引擎是二进制，仓库 `anthropics/claude-code` 留下的是**生态与协作的部分**：

- **`plugins/`**：十几个官方示例插件（下面 §4 详谈），是理解扩展机制的最佳活教材。
- **`.devcontainer/`**：容器化开发环境，方便在隔离环境里跑 Claude Code。
- **GitHub Action / `.github/`**：把 Claude Code 接进 CI——`@claude` 提及即可自动评审 PR、处理 issue。
- **README / CHANGELOG / 文档链接**：指向 `code.claude.com/docs`。
- **`/bug` 反馈、Discord**：社区与问题追踪。

换句话说，这个仓库本身就体现了 Claude Code 的产品哲学：**核心引擎闭源稳定，扩展层完全开放**（插件、Skills、MCP、Hooks、SDK 都是用户可写的）。

## 1.3 一个引擎，多个 surface

官方文档反复强调一句话：**"Each surface connects to the same underlying Claude Code engine."** 同一个引擎，接到不同入口：

- **终端 CLI**：全功能本体，也是最适合脚本化的形态（`claude -p "..."` 无头模式，可被 Unix 管道串起来）。
- **IDE 插件**：VS Code / Cursor / JetBrains，内联 diff、@-mention、计划审阅。
- **桌面 App / Web / iOS**：可视化 diff、并行多会话、云端长任务、手机接力。
- **CI 与团队**：GitHub Actions / GitLab CI、Slack 里 @Claude。

因为引擎统一，你的 `CLAUDE.md`、`settings.json`、MCP 服务器配置**在所有 surface 通用**。这是"把 Harness 做成平台"的体现——Harness 不只是某个 CLI 的内部实现，而是一套可跨端复用的标准。

下面几节，我们就钻进这套 Harness，逐层拆。
