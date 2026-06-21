# 大预言模型的记忆

## 存储位置（Substrate）

外部检索式记忆（external / retrieval-based，把经验写入向量库、图谱或文件，用时检索）vs 内部参数化记忆（internal / parametric，把经验固化进模型权重或潜变量）。前者可解释、易扩展，后者紧凑、推理快但难更新。

## 认知类型（Function）

情景记忆（episodic，具体经历）、语义记忆（semantic，抽象事实/知识）、过程性记忆（procedural，技能/工作流）、工作记忆（working，当前上下文），以及多模态记忆（融合视觉、音频、空间）。

## 学习方式

纯提示（prompt-based / training-free）、监督微调（SFT）、强化学习（RL）。

## 评测重心

从早期长对话 QA（LoCoMo、LongMemEval），扩展到 Web/GUI 导航、具身与游戏、长时程办公等真实任务，并出现专门衡量「跨会话依赖」「动态环境遗忘」的新基准。

要把「记忆」当作智能体设计的**一等公民（first-class primitive）**！