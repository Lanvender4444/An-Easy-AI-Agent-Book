# 早期 Prompt Engineering
Chain of Thought (思维链) —— 让模型一步步推理而不是直接给答案。

Few-shot (少样本提示) —— 给几个例子比抽象描述管用得多。

Role-playing (角色扮演) —— "你是一个资深的..."。

Temperature 调节 (温度系数) —— 控制输出的随机性。

System Prompts (系统提示词) —— 在全局层面为模型设定底层行为逻辑、安全边界和语气基调。

Self-Consistency (自一致性) —— 让模型对同一个问题生成多个推理路径，并通过投票选出最顶尖、最可靠的答案。

Tree of Thoughts (思维树/ToT) —— 允许模型在解决问题时进行多路径探索、前瞻预测和自主纠错，像人类下棋一样思考。

Retrieval-Augmented Generation (RAG/检索增强) 思想 —— 在提示词中注入外部知识库或实时搜索结果，彻底解决模型的“胡说八道（幻觉）”问题。（来自Context Engineering ）

Structured Output (结构化输出) —— 使用 “请用 JSON/Markdown 格式返回” 等指令，让原本不可控的文本变成可以直接被程序解析的结构化数据。

Generated Knowledge (生成知识提示) —— 让模型在回答前，先自主生成一段关于该主题的相关知识，再结合这些知识去解决复杂问题。

2023 年 3 月《Self-Refine: Iterative Refinement with Self-Feedback》：Self-Refine 模式：三步循环：生成（Draft） → 反思反馈（Critique） → 修正提高（Refine） 反思循环

Reflexion 架构：《Reflexion: Language Agents with Verbal Reinforcement Learning》，Reflection 到 Agent 引入了外部环境反馈和长期记忆（Episodic Memory）

