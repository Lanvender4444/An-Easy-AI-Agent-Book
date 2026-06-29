# Open Notebook —— 垂直应用型 Agent 拆解

> 仓库：`lfnovo/open-notebook` · 版本：v1.9.0（采集时） · License：MIT
> 一句话：开源、隐私优先、可自托管的 Google NotebookLM 替代品。

## 它到底是个什么东西

把一堆资料（PDF、网页、视频、音频、Office 文档）丢进去，它能帮你**提取内容、生成笔记、语义检索、基于资料和你对话、还能把资料做成多人播客**。和 NotebookLM 最大的不同是：数据全在你自己手里，AI Provider 你随便换（支持 18+ 家，也能用 Ollama 本地跑）。

从 Agent 的视角看，Open Notebook 是一个典型的**垂直应用型 Agent**——它不追求"通用自主"，而是把若干个**有明确输入输出的 AI 工作流**（摄取、问答、转换、播客）封装进一个产品里，人始终在环中（human-in-the-loop）。它的价值不在"多聪明"，而在**工程组织**：怎么把 RAG、记忆、多 Provider、异步任务这些零件拼成一个能跑、能自托管、能扩展的东西。

## 本章拆解路线

1. **整体架构与技术栈** —— 三层架构（Next.js 前端 / FastAPI 后端 + 核心库 / SurrealDB），数据怎么流。
2. **数据层与 AI 抽象层** —— SurrealDB 领域模型与仓储模式、Esperanto 多 Provider 抽象、加密凭据与 ModelManager。
3. **LangGraph 工作流与异步任务** —— source / chat / ask / transformation 四条工作流，状态持久化，surreal-commands 任务队列与播客生成。
4. **用 RAG / 记忆 / Harness 透镜回看** —— 把前面学的概念对号入座，提炼可借鉴的工程经验。

> 一句话总览（来自仓库根目录 `CLAUDE.md` 的架构图）：
> **前端(React/Next.js, :3000) → HTTP REST → 后端(FastAPI, :5055) → SurrealQL → 数据库(SurrealDB, :8000)**，
> 后端内部由 `api/`（HTTP 编排层）+ `open_notebook/`（领域核心层）两部分组成，AI 能力经 Esperanto 统一接入，重活（如播客）丢给 surreal-commands 异步队列。
