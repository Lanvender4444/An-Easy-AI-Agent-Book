# 3. 工具层 / 权限层 / 生命周期层

这三层是 Claude Code"动手能力"的核心：能用什么工具（工具层）、哪些动作要批准（权限层）、在动作前后插什么逻辑（生命周期层 / 感知层）。三者环环相扣。

## 3.1 工具层：内置工具 + MCP

**内置工具**是模型的"手"。Claude Code 自带一套覆盖编码全流程的工具（本书运行环境里也能看到它们的影子）：

- **文件**：`Read`、`Write`、`Edit`（精确字符串替换）。
- **检索**：`Glob`（按模式找文件）、`Grep`（基于 ripgrep 的内容搜索）。
- **执行**：`Bash`（跑 shell 命令，git 操作也走它）。
- **编排**：`Task`（派生子智能体，见 §4）、`TodoWrite`（任务清单跟踪）。
- **联网**：`WebFetch`、`WebSearch`。
- **其他**：`NotebookEdit`（Jupyter）等。

**MCP（Model Context Protocol）—— 工具层的开放扩展**。这是 Claude Code 工具层最重要的设计：通过 MCP 这个开放标准，Agent 能接入**外部数据源和工具**——读 Google Drive 的设计文档、更新 Jira 工单、从 Slack 拉数据、调你自研的内部工具。MCP 让工具层从"内置固定几样"变成"可无限挂载"。第三、四部分讲的各种外部能力，到了 Claude Code 这里都通过 MCP 统一接入。

> 工具层的设计哲学：**内置工具保证通用编码能力，MCP 保证可无限扩展到任意外部系统**。

## 3.2 权限层：allow / ask / deny

工具越强，越需要缰绳。Claude Code 的权限层在 `.claude/settings.json` 里配置，核心是第九章讲的 **allow / ask / deny 三态**：

- **allow**：自动放行（如只读的 `Read`、`Grep`）。
- **ask**：执行前必须问用户（如 `Bash` 跑某些命令、写文件）。
- **deny**：直接禁止（如碰某些敏感路径）。

配合**路径白名单 / 命令规则**做细粒度控制（比如允许 `npm test` 但拦 `rm -rf`）。这套权限模型是开放式 Agent Loop 能安全运行的前提——**模型可以自由决定下一步，但越界动作必须过权限这一关**。

此外还有 **Plan Mode（计划模式）**：让 Agent 先只读地探索、产出方案、等你批准了再动手改，进一步把"自主"关进"可审阅"的笼子。

## 3.3 生命周期层 + 感知层：Hooks（9 种事件）

**Hooks** 是 Claude Code 最强的可定制点——在特定时机插入你自己的 shell 命令/逻辑。它同时承担第九章的**生命周期层**（管会话内流转）和**感知层**（对动作做事后/事前核查）。Hook 配置在 `settings.json`，可用 `matcher` 匹配特定工具。一共 **9 种事件**：

| Hook 事件 | 触发时机 | 典型用途 |
|-----------|---------|---------|
| **PreToolUse** | 工具调用前 | 安全拦截、权限决策（可 allow/ask/deny）|
| **PostToolUse** | 工具调用后 | 自动格式化、跑 lint、校验改动 |
| **UserPromptSubmit** | 用户提交输入时 | 注入额外上下文、改写/校验输入 |
| **Notification** | 需要通知时 | 自定义提醒 |
| **Stop** | Agent 准备结束时 | 拦截退出、强制继续迭代 |
| **SubagentStop** | 子智能体结束时 | 收尾、汇总 |
| **PreCompact** | 上下文压缩前 | 控制压缩时机/内容 |
| **SessionStart** | 会话开始 | 自动注入项目上下文 |
| **SessionEnd** | 会话结束 | 清理、归档 |

Hook 通过结构化输出（如 `hookSpecificOutput`、`additionalContext`、`permissionDecision`、`decision`/`continue`/`stopReason`）和引擎通信——比如 PreToolUse 可以返回一个 `permissionDecision` 直接决定放行还是拦截，UserPromptSubmit 可以返回 `additionalContext` 往上下文里塞东西。

仓库 `plugins/` 里有几个**真实 Hook 案例**，特别适合理解这套机制：

- **`security-guidance`**：用 **PreToolUse** Hook 监控 9 种安全模式（命令注入、XSS、`eval`、危险 HTML、pickle 反序列化、`os.system` 等），编辑文件时预警。——这是"感知层/权限层"的事前核查。
- **`explanatory-output-style` / `learning-output-style`**：用 **SessionStart** Hook 在每次会话开始注入教学上下文。——这是"生命周期层 + 引导层"的自动注入。
- **`ralph-wiggum`**：用 **Stop** Hook 拦截退出，让 Claude 在同一任务上反复迭代直到完成。——这是"生命周期层"控制循环的极端玩法。

> 三层串起来看一次工具调用：模型决定调 `Edit` → **PreToolUse** Hook + 权限层一起判定（拦截危险？要不要问用户？）→ 真正执行 → **PostToolUse** Hook 自动 lint/格式化 → 结果塞回上下文。**这正是开放式 Agent Loop 里每一步动作的"安检流水线"。**

下一节看比单步动作更高层的东西：多智能体编排和整个扩展生态。
