# 2. 数据层与 AI 抽象层

应用型 Agent 的"地基"是两件事：**数据怎么存取**、**AI Provider 怎么抽象**。这两层做好了，上面的工作流才能写得干净。

## 2.1 SurrealDB：用一个库搞定记录 / 关系 / 向量

传统 RAG 应用往往要拼三套存储：关系库存元数据、图库存关系、向量库存嵌入。Open Notebook 用 **SurrealDB 一个库全包**：

- **记录（Records）**：Notebook、Source、Note、ChatSession、Credential 等领域对象。
- **关系（Relationships）**：source→notebook、note→source 这类边，直接用 SurrealDB 的图能力表达，不用自己在关系库里维护连接表。
- **向量（Vector Embeddings）**：嵌入向量和记录存在一起，语义检索是数据库内建能力，不需要外挂 FAISS/Qdrant。

对应到代码，`open_notebook/domain/` 是领域模型 + **仓储模式（Repository Pattern）**：领域对象（Pydantic 模型）负责"是什么"，仓储函数负责"怎么读写 SurrealDB"，并处理事务（ACID）。检索函数（全文 + 向量）也在 domain 层。`open_notebook/database/` 管连接、迁移与异步操作。

**自动迁移**是个省心设计：迁移脚本是 `migrations/XXX_description.surql`（外加可选的 `_down.surql` 回滚），API 启动时 `AsyncMigrationManager` 比对版本号，发现有更新就自动执行。代价是——**必须先起数据库、再起 API、最后起前端**，顺序错了就报错。

> 用第三部分的话说：SurrealDB 在这里同时扮演了"记忆存储"的**向量存储**与**图存储**两种角色，是"扁平 + 分层 + 图"混合的存储底座。

## 2.2 Esperanto：多 Provider 的"万能插座"

支持 18+ 个 AI Provider，如果每家都写一套适配，应用层会被 if/else 淹没。Open Notebook 把这层抽成独立库 **Esperanto**，对外暴露统一接口，覆盖四类能力：

| 能力 | 代表 Provider |
|------|--------------|
| LLM | OpenAI / Anthropic / Google / Groq / Ollama / Mistral / DeepSeek / xAI / OpenRouter / Qwen … |
| Embedding | OpenAI / Google / Vertex / Ollama / Mistral / Voyage / Azure … |
| 语音转文字 STT | OpenAI / Groq / ElevenLabs |
| 文字转语音 TTS | OpenAI / Google / Vertex / ElevenLabs |

应用层只管"我要一个 LLM / 一个 embedding 模型"，具体是谁、走什么 endpoint，由 Esperanto 解决。这正是第二部分反复强调的**抽象边界**——把"会变的东西"（Provider）挡在一道接口后面。

## 2.3 凭据系统与 ModelManager：把"选模型"做成一等公民

光有统一接口还不够，真实产品要解决"用户的 key 存哪、用哪个模型、模型挂了怎么办"。Open Notebook 的做法是：

- **加密凭据（Credential）**：每个 Provider 一条**独立加密**的凭据记录（靠 `OPEN_NOTEBOOK_ENCRYPTION_KEY` 加密），模型记录再链接到凭据。用户在 UI 里"添加凭据 → 测试连接 → 发现模型 → 注册模型"，不用碰环境变量。
- **ModelManager（工厂 + 兜底）**：工厂模式创建模型实例，优先用凭据配置、缺失时回落到环境变量。
- **智能选择**：检测到超长上下文时，自动**偏向长上下文模型**。
- **按请求覆盖（Override）**：每次调用都能指定用哪个模型，互不影响。
- **失败兜底**：主模型挂了，回落到更便宜/更小的模型，保证流程不中断。

这套"凭据 + ModelManager"是应用型 Agent 很典型的一块——**它把"用哪个脑子"从硬编码变成了运行时可配置、可兜底的资源调度**。对比第九章 Harness 的"工具层/权限层"，这里相当于给"模型"这个最核心的资源也做了一层治理。

下一节看这些零件是怎么被 LangGraph 串成实际工作流的。
