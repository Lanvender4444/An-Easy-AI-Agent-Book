# ReAct 的基础

## ReAct 核心逻辑

本质上是一个 while 循环。



+ Thought（思考）：模型推理"我现在该做什么" 。

+ Action（行动）：模型输出一个工具调用。

+ Observation（观察）：工具真的被执行，结果返回给模型

把这三步追加到对话历史，然后重复，直到模型认为任务完成。THINK→ACT→OBSERVE→THINK…



## ReAct的范式(Â = A ∪ L)

### A 行动空间

Action Only Agent

A 通常是**工具调用**——搜索、查数据库、调 API、点击网页。

特点是：会改变周围的环境状态。

### L 语言空间

COT

自由形式的语言思考集合。

内部推理环境

### Â 增广空间

二者的集合

### 设计核心

从 A 到 L，意味着结论已经被说出。

终止条件：没有 工具调用

### 扩展状态机模型

ReAct 状态机是一个扩展有限状态机 $M $:
$$
M = (Q,\ \Sigma,\ C,\ \delta,\ q_0,\ F)
$$

- $Q = \{\text{THINK, ACT, OBSERVE, DONE}\} $ —— 有限控制状态
- $\Sigma = \{\text{think\_done, is\_tool\_call, is\_finish, obs\_ready}\} $ —— 触发转移的事件
- $C $ —— 扩展变量(上下文 scratchpad),转移时被更新
- $\delta: Q \times \Sigma \times C \to Q \times C $ —— 转移函数(同时改控制状态和上下文)
- $q_0 = \text{THINK} $ —— 初始状态
- $F = \{\text{DONE}\} $ —— 接受/吸收态

转移函数 $\delta $ 的几条核心规则:
$$
\begin{aligned}
\delta(\text{THINK},\ \text{think\_done},\ c) &= (\text{ACT},\ c\oplus\theta) \\
\delta(\text{ACT},\ \text{is\_tool\_call},\ c) &= (\text{OBSERVE},\ c\oplus a) \\
\delta(\text{ACT},\ \text{is\_finish},\ c) &= (\text{DONE},\ c\oplus a) \\
\delta(\text{OBSERVE},\ \text{obs\_ready},\ c) &= (\text{THINK},\ c\oplus o)
\end{aligned}
$$
注意每条转移都带 $c\oplus(\cdot) $——**控制状态在有限集合里跳转,上下文 $c $ 单调增长**。这一行同时表达了"有限控制流"和"无限数据流"两个面向。



## 结束的信号

+ 边际收益衰减
+ 无进展检测
+ 收敛轨迹分析



## ReAct 与 Plan-and-Execute

### 什么是 Plan-and-Execute

Plan-and-Execute，字面意思，由两部分组成：

+ Plan 计划
+ Execute 执行

而只循环 Execute 环节。Plan 只执行一次。

增加 Re-planner，可以重新定制 Plan。

Plan-and-Execute 具有 可解释性，全局性强，而 ReAct 有反馈及时性。

### 共同的缺点

+ 注意力衰减：所有的都塞进了一个上下文窗口；
+ 上下文爆炸：同上；
+ 死亡循环：什么时候停止？