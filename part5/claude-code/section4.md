# 4. 编排层与扩展生态

到这一层，Agent 不再是"一个模型 + 一堆工具"，而是**多个智能体协作 + 一整套可插拔扩展**。这是 Claude Code 作为"平台"的部分。

## 4.1 编排层：子智能体、后台 Agent、Agent 团队

**子智能体（Subagents / Task 工具）**是 Claude Code 编排层的核心。官方对它的定位很精准：当一个side task会用"一堆你以后不会再看的搜索结果、日志、文件内容"淹没主对话时，就派一个子智能体去**在它自己的上下文窗口里**干这活，只把**结论**带回来。

每个子智能体的特征（对应第九章"编排层"）：

- **独立上下文窗口**：研究/探索不污染主对话——这是它最大的价值（"preserve context"）。
- **自定义 System Prompt**：聚焦某个领域（如"代码审查者""测试分析者"）。
- **受限工具集与独立权限**：可以只给它 `Read`/`Grep`，限制它能干什么（"enforce constraints"）。
- **可配置模型**：把简单任务路由到更快/更便宜的模型（"control costs"）。

定义方式：在 `.claude/agents/` 下放 Markdown 文件，用 frontmatter 写 `name` / `description` / `tools` / `model`。当某个任务匹配上某 subagent 的 `description`（描述里写"proactively"之类会鼓励自动委派），Claude 就把活派给它，它独立干完返回结果。

更大规模的编排：
- **Background Agents（agent-view）**：并行跑多个**完整会话**，在一块屏幕上监控——对应第九章编排层的"并行多智能体"。
- **Agent 团队**：会话之间能互相通信、移交工作——这就是第九章讲的 **Swarm / handoff** 模式。

> 对照 Open Notebook：它的"编排"是 LangGraph 写死的图（开发者定流程）；Claude Code 的编排是**模型动态决定派不派子智能体、派几个、怎么分工**（Agent 定流程）。一个是"流程驱动"，一个是"智能体驱动"。

## 4.2 扩展生态：Slash 命令 / Skills / Plugins / SDK

Claude Code 把"可扩展性"做成了一个分层生态。仓库的 `plugins/` 目录正好把这些机制都演示了一遍：

**Slash 命令（`/xxx`）**：把常用工作流封装成一条命令。如 `commit-commands` 插件提供 `/commit`、`/commit-push-pr`、`/clean_gone`；`code-review` 插件提供 `/code-review`。命令文件放 `commands/`。

**Skills（Agent 技能）**：把可复用的领域知识/工作流打包成 `SKILL.md`，**按需自动触发**。如 `frontend-design` 技能在做前端时自动注入"避免通用 AI 审美"的设计指导；`claude-opus-4-5-migration` 技能自动迁移模型字符串与 beta 头。Skills 放 `skills/`。

> Skills 在本书第二部分 Harness 一章出现过（9.3）。它和"命令"的区别：命令是用户**显式**调用，技能是 Agent 根据情境**隐式**触发。

**Plugins（插件）+ Marketplace（市场）**：把命令、子智能体、Skills、Hooks、MCP 服务器**打包成一个可分享的单元**。标准结构是：

```
plugin-name/
├── .claude-plugin/plugin.json   # 插件元数据
├── commands/                    # Slash 命令
├── agents/                      # 子智能体
├── skills/                      # 技能
├── hooks/                       # 事件钩子
├── .mcp.json                    # 外部工具(MCP)配置
└── README.md
```

用 `/plugin` 命令从市场安装。官方 `plugins/` 里的十几个插件就是活样本，按"它们用了哪种机制"归类：

- **纯命令型**：`commit-commands`。
- **多子智能体型**：`code-review`（5 个并行 Sonnet 子智能体分别查 CLAUDE.md 合规、bug、历史上下文、PR 历史、代码注释，再用置信度打分过滤误报）、`pr-review-toolkit`（comment/test/类型/简化等多个专精子智能体）、`feature-dev`（7 阶段功能开发，含 explorer/architect/reviewer）。
- **纯 Hook 型**：`security-guidance`（PreToolUse 安全预警）、`ralph-wiggum`（Stop 钩子做自循环）。
- **Skill 型**：`frontend-design`、`plugin-dev`（7 个专家技能教你写插件）。
- **开发套件型**：`agent-sdk-dev`（`/new-sdk-app` + SDK 校验子智能体）、`hookify`（用自然语言生成自定义 Hook）。

**Agent SDK**：给最硬核的需求。`Agent SDK` 让你**用 Claude Code 的工具与能力构建你自己的 Agent**，完全掌控编排、工具访问、权限。也就是说，Claude Code 既是成品工具，又是**造 Agent 的框架**——本书这套 Cowork 环境本身就是建立在 Claude Agent SDK 之上的。

## 4.3 可观测层

- **多 surface 可视化**：IDE 内联 diff、桌面 App 可视化 diff、Web 端长任务监控。
- **Background agents**：一屏监控多个并行会话的进度。
- **CLI 输出 + 无头模式**：`claude -p` 的输出可被管道/脚本消费，天然可观测、可集成进 CI。
- **`/bug` 反馈、使用数据**：产品级的反馈回路。

至此，第九章的 Harness 八层在 Claude Code 里全部对上了号。最后一节做个对照总结。
