# 1. 整体架构与技术栈

Open Notebook 是标准的**三层架构（Three-Tier）**，仓库根目录的 `CLAUDE.md` 里直接画了图，我们照着拆。

```
┌─────────────────────────────────────────────┐
│  前端  Frontend (Next.js 16 / React 19)       │  :3000
│  Zustand 状态 · TanStack Query · Shadcn/ui    │
└───────────────────────┬─────────────────────┘
                        │ HTTP REST
┌───────────────────────▼─────────────────────┐
│  后端  API (FastAPI)                          │  :5055
│  api/        —— HTTP 编排层（路由 + 服务）     │
│  open_notebook/ —— 领域核心层（模型/图/AI）    │
└───────────────────────┬─────────────────────┘
                        │ SurrealQL（异步驱动）
┌───────────────────────▼─────────────────────┐
│  数据库  SurrealDB                            │  :8000
│  记录 + 关系 + 向量嵌入，三合一                 │
└─────────────────────────────────────────────┘
```

## 1.1 三层各自干什么

**前端（`frontend/`）**：Next.js 16 + React 19 + TypeScript。状态管理用 Zustand，数据获取用 TanStack Query（React Query），UI 用 Shadcn/ui + Tailwind。它是一个纯展示层，所有数据都通过 REST 找后端要。值得注意的是它**内建多语言（i18n）**——任何前端改动都要同步翻译键。（早期版本 UI 是 Streamlit，仓库里 `pages/`、`app_home.py` 是其遗留，现已迁到 Next.js。）

**后端（`api/` + `open_notebook/`）**：Python 3.11+ 的 FastAPI。这一层是本章重点，它又分成两半：
- `api/`：HTTP 编排层。每个功能一个 `*_service.py`（业务逻辑）+ 一个 `routers/*.py`（HTTP 端点），schema 集中在 `api/models.py`。
- `open_notebook/`：领域核心层。领域模型（`domain/`）、AI 接入（`ai/`）、LangGraph 工作流（`graphs/`）、数据库操作（`database/`）都在这里。

**数据库（SurrealDB）**：一个把**文档、图、向量**三种能力合一的数据库。Open Notebook 用它同时存记录（Notebook/Source/Note/ChatSession/Credential）、存关系（source 属于哪个 notebook、note 关联哪个 source）、存向量嵌入（语义检索）。Schema 迁移在 API 启动时由 `AsyncMigrationManager` 自动跑。

## 1.2 一条请求是怎么流动的

以"用户上传一个 PDF 作为资料源"为例：

1. 前端把文件/URL 发到 `POST /sources`（`routers/sources.py`）。
2. 路由调 `sources_service.py`，后者触发 `open_notebook/graphs/source.py` 这条 LangGraph 工作流：**抽取内容 → 切块/嵌入 → 落库**。
3. 内容抽取交给 `content-core` 库（支持 50+ 文件类型、网页正文提取）；嵌入向量经 Esperanto 找对应 Provider 算出来。
4. 结果作为 Source 记录写进 SurrealDB，向量一起存好，供日后检索。

整条链路**全异步（async/await）**——数据库查询、图调用、外部 API 调用都是 await，FastAPI 借此高并发。这是 `CLAUDE.md` 里点名的"Async-First Design"。

## 1.3 技术栈速查表

| 层 | 选型 | 作用 |
|----|------|------|
| 前端 | Next.js 16 / React 19 / TypeScript / Zustand / TanStack Query / Shadcn/ui | 多端 UI、状态与数据获取 |
| 后端框架 | FastAPI 0.104+ / Uvicorn / Pydantic v2 / Loguru | HTTP 服务、校验、日志 |
| 工作流 | **LangGraph**（状态机）+ langgraph-checkpoint-sqlite | 编排 AI 多步流程、状态持久化 |
| AI 接入 | **Esperanto**（作者自研，统一 18+ Provider） | LLM / Embedding / STT / TTS 一套接口 |
| 数据库 | **SurrealDB**（异步驱动） | 记录 + 关系 + 向量，自动迁移 |
| 内容处理 | `content-core` | 文件/URL 内容抽取 |
| 提示词 | `ai-prompter`（Jinja2 模板） | 提示词模板化管理 |
| 异步任务 | `surreal-commands` | 后台任务队列（播客等重活） |
| 播客 | `podcast-creator` | 多人播客脚本 + 合成 |

这里有个很"作者风格"的细节：Esperanto、content-core、ai-prompter、podcast-creator、surreal-commands **全是同一作者（lfnovo）抽出来的独立库**。也就是说 Open Notebook 本体其实很"薄"——它是把一组**自研基础库编排起来的产品壳**。这是一种很值得学的工程姿势：把通用能力（多 Provider 抽象、内容抽取、任务队列）下沉成可复用库，应用层只负责编排。下一节我们就从这些抽象层开始拆。
