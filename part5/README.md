# 第五部分：Agent 拆解

前四部分我们自底向上把"模型怎么炼成、Agent 怎么进化、靠什么技术支撑、有哪些主流框架"讲了一遍。这一部分换一种方式——**不再讲抽象概念，而是挑两个真实开源项目，把它们彻底拆开**，看看前面讲的那些东西在工业级代码里到底长什么样。

挑这两个项目，是因为它们恰好代表 Agent 世界的两个极端：

- **Open Notebook**（`lfnovo/open-notebook`）：一个**垂直应用型 Agent**。它解决一个具体问题——做一个隐私优先、可自托管的"NotebookLM 替代品"。它的形态是一套完整产品：前端 + 后端 + 数据库，AI 只是其中一层。拆它，能看清**一个落地的 AI 应用是如何把 RAG、记忆、工作流编排、多 Provider 抽象组织成产品**的。
- **Claude Code**（`anthropics/claude-code`）：一个**通用编码 Agent 的 Harness**。它不绑定某个具体任务，而是提供一套"模型 + 脚手架"，让 Agent 能在终端里读代码、改文件、跑命令。拆它，能看清第九章讲的 **Agent = Model + Harness** 这个公式在真实产品里是怎么落地的——引导、工具、权限、生命周期、记忆、编排、扩展，每一层都有对应实现。

两者放在一起对照，正好覆盖"应用层"和"基础设施层"两个视角：

| 维度 | Open Notebook | Claude Code |
|------|---------------|-------------|
| 定位 | 垂直应用（研究助手） | 通用编码 Agent 框架 |
| 形态 | 三层全栈产品 | CLI 引擎 + 多端 + SDK |
| AI 的位置 | 产品的一层 | 产品的核心 |
| 编排方式 | 预定义 LangGraph 工作流 | 开放式 Agent Loop + 子智能体 |
| 记忆 | SurrealDB + 向量检索（外部、领域数据） | CLAUDE.md + auto memory（外部、工程上下文） |
| 扩展性 | REST API + 自定义 Transformation | MCP / Skills / Hooks / Plugins / SDK |
| 自主程度 | 低（流程固定，人在环中） | 高（开放循环，可后台自治） |

> 拆解方法：对 Open Notebook，我们走"架构 → 数据与 AI 抽象 → 工作流 → 透镜回看"的路线；对 Claude Code，我们直接套用**第九章的 Harness 八层框架**（引导/感知/工具/权限/生命周期/记忆/编排/可观测），逐层对号入座。
>
> 本部分基于两个仓库的 README、`CLAUDE.md`、`pyproject.toml`、API 源码目录、官方文档与 plugins 目录整理（采集于 2026 年 6 月）。代码会持续演进，请以仓库最新版为准。

本部分包含两大章：

- **Open Notebook —— 垂直应用型 Agent 拆解**
- **Claude Code —— 通用编码 Agent Harness 拆解**
