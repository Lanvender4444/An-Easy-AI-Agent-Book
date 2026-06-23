# 子 Agent 间通讯

## Harness 父子 Agent

本质：**工具调用**



+ 开一块全新的 context (独立的消息历史、独立的 system prompt、独立的工具集)

+ 跑子 agent 自己的 agent loop 到结束 (它自己 think → tool call → observe → 循环)

+ 把子 agent 的最终一条 assistant 消息,作为 `tool_result` 塞回父 agent 的 context



并不会污染父 Agent 的空间。一次性且无状态。



## 框架式多 Agent

共享 State， reducer 合并。节点之间不直接对话,而是都对同一块 state 做增量更新。

子图：一个子 agent 可以是一张编译好的子图,作为父图的一个节点被调用。但父图和子图各有各的 state schema,所以跨边界要做 schema 映射(把父 state 的某些字段映射成子图的输入,再把子图输出映射回来)。

Command 对象：让一个节点同时做两件事——更新 state + 指定下一个跳转的节点。

Send API ：一个节点可以 spawn N 个 worker,每个 worker 拿到各自的、不同的 state 分片并发跑,这是 map-reduce 式并行的基础。



## 父与子 Agent 的信道

父 → 子（只在 spawn 时）

子 → 父（只在 return 时）



## 旁路：外部共享资源

设计原则：让 token 信道传"指针"，让外部存储传"数据"。

**文件系统**:父 agent 写一个文件,把路径传给子 agent;子 agent 把结果写到另一个文件,父 agent 再读回来。本质就是经典的"通过共享文件做 IPC",完全绕开 context window。Claude Code 这类 harness 里,文件系统就是天然的宽信道。

**Redis / KV 存储**:更适合需要并发协调、需要 TTL、需要多个子 agent 同时读写的场景。多个子 agent 往一个约定的 key 空间里读写,父 agent 轮询或在汇聚点读取。

**黑板架构(blackboard)**:更老的 AI 范式,多个 agent 围绕一块共享数据结构读写、各自在合适时机贡献结论。本质就是把 Redis/DB 抽象成一块"公共留言板"。