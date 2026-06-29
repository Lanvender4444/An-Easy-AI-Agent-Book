# Claude Code —— 通用编码 Agent Harness 拆解

> 仓库：`anthropics/claude-code` · 分发：`@anthropic-ai/claude-code`（npm）/ 原生安装器 · 文档：code.claude.com/docs
> 一句话：活在终端里的 agentic coding 工具——读你的代码库、改文件、跑命令、处理 git，全用自然语言驱动。

## 先说一个容易踩的坑：仓库 ≠ 引擎

打开 `anthropics/claude-code` 这个仓库，你会发现**它没有 CLI 的核心源码**。仓库里主要是：`README`、`plugins/`（官方示例插件）、`.devcontainer/`、GitHub Action、问题追踪、变更日志。真正的引擎是**编译分发的二进制**（通过 `curl https://claude.ai/install.sh`、Homebrew、WinGet 或已废弃的 npm 安装），核心逻辑闭源、混淆。

所以"拆 Claude Code"不是去读它的源码，而是**拆它的架构与机制**——而这恰恰是检验第九章 **Agent = Model + Harness** 框架的最佳标本。我们拆的是：它把"模型"和"脚手架"如何组织成一个能在真实工程里干活的 Agent。

本章的素材来自：仓库 README 与 `plugins/`、官方文档（overview / hooks / sub-agents / settings / memory / mcp / skills），以及第九章已经建立的概念框架。

## Model + Harness：Claude Code 的两半

- **Model**：底层是 Claude 系列模型（Opus / Sonnet / Haiku 可切换）。模型负责"想"。
- **Harness**：围绕模型的一整套脚手架，负责"让模型能安全、可控、可扩展地在你的代码库里行动"。

Claude Code 的厉害之处全在 Harness。它还有一个关键特性——**同一个引擎，多个 surface**：终端 CLI、VS Code / JetBrains 插件、桌面 App、Web、iOS、Slack、GitHub Action 共用同一套引擎，所以你的 `CLAUDE.md`、settings、MCP 配置在哪都通用。

## 本章拆解路线：套用第九章 Harness 八层

第九章把 Harness 拆成八层，我们就**逐层对号入座**，看 Claude Code 每层怎么实现：

| Harness 层 | Claude Code 的实现 | 本章位置 |
|-----------|-------------------|---------|
| 引导层 | System Prompt、CLAUDE.md（分层）、output styles | §2 |
| 记忆层 | CLAUDE.md + auto memory（跨会话学习） | §2 |
| 工具层 | 内置工具（Read/Edit/Bash/Glob/Grep/Task…）+ MCP | §3 |
| 权限层 | settings.json 的 allow/ask/deny + 路径/命令规则 | §3 |
| 生命周期层 | Hooks（9 种事件）、/compact、/clear、resume | §3 |
| 感知层 | Hooks 的校验/拦截、权限决策 | §3 |
| 编排层 | 子智能体（Task / sub-agents）、后台 Agent、Agent 团队 | §4 |
| 可观测层 | 多 surface、background agents 监控、CLI 输出 | §4 |
| 扩展层（额外） | Slash 命令、Skills、Plugins/Marketplace、Agent SDK | §4 |
| 对照与借鉴 | 与 Open Notebook 的对比、可迁移经验 | §5 |

> 注：本章描述的是 2026 年 6 月采集时的形态。Claude Code 迭代极快。
