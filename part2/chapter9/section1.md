# Agent = Model + Harness

## 三种控制 LLM 的方式

+ 提示词（Prompt）
+ 上下文（Context）
+ 运行环境（Harness）

## 提示词

Advanced RAG 里的**查询改写、HyDE、step-back**

## 上下文

上下文包括：

- 检索回来的文档(RAG)
- 调出来的记忆(Memory)
- 工具调用的返回结果(observation)
- 对话历史
- 系统提示



**RAG + Memory = Context 工程**

## 运行环境

模型之外的整个运行机制。

+ 工具/函数的实际执行
+ 控制流/循环
+ 状态管理
+ 错误处理与重试
+ 与环境/系统的接口
+ 解析与校验



## Agent = Model + Harness

**Agent = Model(会思考、会决策的大脑)** + **Harness(让大脑的决策能作用于真实世界的躯体与环境)**



