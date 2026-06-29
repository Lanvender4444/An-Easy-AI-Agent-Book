# 3. LangGraph 工作流与异步任务

Open Notebook 的"智能"集中在 `open_notebook/graphs/` 下的几条 **LangGraph 工作流**。这是它和"开放式 Agent Loop"最不一样的地方——它**不让模型自由发挥**，而是把每个功能写成一张**确定的状态图**（StateGraph），节点之间的流转是写死的。这是垂直应用的典型取舍：**用可控性换自主性**。

## 3.1 四条核心工作流

仓库根 `CLAUDE.md` 点名了四条：

- **`source.py`（内容摄取）**：`抽取 → 嵌入 → 落库`。把用户给的文件/URL 经 content-core 抽成文本，切块、算向量，存成 Source 记录。这是"写入侧"流水线。
- **`chat.py`（对话）**：带消息历史的对话式 Agent。把选中的资料作为上下文，和用户多轮对话。
- **`ask.py`（检索 + 综合）**：`检索相关资料 → 喂给 LLM 综合`。这其实就是一条标准的 **RAG 问答链**：先在 SurrealDB 里做全文 + 向量检索，再让 LLM 基于命中的资料生成带引用的回答。
- **`transformation.py`（内容转换）**：对资料执行自定义"变换"——摘要、提取要点、改写等。这就是产品里"Content Transformations"功能的引擎。

每条工作流的写法是统一套路（`CLAUDE.md` 的 "Add a New LangGraph Workflow" 一节写得很清楚）：
1. 定义 `StateDict`（在节点间传递的状态）和若干节点函数；
2. 用 `.add_node()` / `.add_edge()` 把图搭起来；
3. 在 service 里 `graph.ainvoke({...}, config={...})` 异步调用；
4. 所有节点都通过 `provision_langchain_model()` 拿模型——也就是上一节的 ModelManager 智能选择在这里生效。

## 3.2 状态持久化：让长流程可恢复

对话、转换这类流程可能跑很久（`CLAUDE.md` 明说"可能要几分钟、且没有超时"）。LangGraph 的**状态持久化**在这里很关键：用的是 **SQLite checkpoint**（`langgraph-checkpoint-sqlite`，存在 `/data/sqlite-db/`）。每个节点执行完都落一次检查点，意味着流程中断后能从断点恢复，而不是从头再来。

> 这正是第九章"生命周期层"讲的**存档/恢复**在真实代码里的样子——只不过这里是 LangGraph 框架替你做了 checkpoint。

## 3.3 异步任务队列：重活不堵主线

有些活实在太重（典型是**播客生成**：要写多人脚本、逐句 TTS 合成、拼音频），不能让 HTTP 请求干等。Open Notebook 用作者自研的 **`surreal-commands`** 做后台任务队列（直接架在 SurrealDB 上）：

- `podcast_service.py` 只负责**提交任务**，提交完立刻返回，不等结果；
- 前端拿到一个 `command_id`，之后轮询 `GET /commands/{command_id}` 查状态；
- 实际生成由 `commands/` 下的命令（`podcast_commands.py`、`embedding_commands.py`、`source_commands.py`）在后台异步执行；
- 容错：TTS 失败时回落到静音音频，不让整个任务崩掉。

播客本身由 **`podcast-creator`** 库实现，支持 **1–4 个说话人**和自定义 Episode Profile / Speaker Profile（对比 NotebookLM 只能两人）。

## 3.4 把这套流程串起来看

一张图概括后端的运转：

```
用户操作
  │
  ├─ 摄取资料 → source 图（抽取→嵌入→落库）────────► SurrealDB（记录+向量）
  │
  ├─ 提问     → ask 图（检索→LLM 综合，带引用）──┐
  ├─ 对话     → chat 图（历史+资料上下文）──────┤──► provision_langchain_model() → Esperanto → Provider
  ├─ 转换     → transformation 图（摘要/提取）──┘
  │
  └─ 生成播客 → surreal-commands 队列（异步）──► podcast-creator → TTS → 音频文件
```

可以看到，Open Notebook 的"Agent 性"主要体现在 **ask/chat 两条 RAG 工作流**上，而 source/transformation/podcast 更像**确定性的数据管线**。它是一个**以 RAG 为核心、工作流编排为骨架、人在环中**的应用型 Agent。下一节用本书的概念框架把它再过一遍。
