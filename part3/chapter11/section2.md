# 高级 RAG（Advanced RAG）与 Modular RAG

## 高级 RAG 做了什么？
Naive RAG 的检索质量问题,可以精确拆成两个指标：
1. 召回率低（Recall）：该检索到的相关块没检索到。
2. 精确率低（Precision）：检索回来一堆不相关的块,稀释了上下文、引入噪声。

问题出在两个地方：
"理解"出了问题:query 和文档没有被好好表示/对齐。

"检索动作"太粗糙:单一向量 top-k 一刀切。

## 语义理解

### 语义嵌入（Embedding）
用专门训练的 Dense Embedding 模型。从字面匹配升级到意义匹配。

### 语义切块（Semantic Chunking）
语义切块按意义边界切，保证每个块是一个自洽的语义单元。

### 查询变换（Query Transformation）
#### Query 优化与改写（Query Rewriting）

#### 假设性文档生成（HyDE）
编造一个可能正确的答案。把传统的“问题-答案匹配”转变成了“答案-答案匹配”。

#### 退一步提问（Step-Back）
把具体问题抽象成更一般的问题,检索到更宏观的背景知识

#### 查询分解（Decomposition）
把复合问题拆成子问题

## 增强检索

### 混合检索（Hybrid Search）

在本章第一小节之时，难免会有疑问，既然可以通过 Embedding 模型来检索相关文章，那为什么可不可以用更符合我们直觉的 更加传统的 关键词匹配呢？

于是混合检索的核心思路就跃然纸上了：关键词检索（Sparse Retrieval / BM25） + 语义向量检索（Dense Retrieval / Vector），Best Match ！

传统的统计学检索，通过计算词频、逆文档频率，可以对那些 特定数字、专有名词、产品型号 进行精确打击！

那么问题来了，如何进行融合？最稳定的融合算法叫 RRF（Reciprocal Rank Fusion，倒数排名融合）。它通过检索中的排名（Rank）进行融合。（公式一会列出）

更重要的马上就来。利用 RRF这步顶多叫初筛，那有初筛就有细筛，细筛在哪呢？就是我们接下来要介绍的 **重排序（Re-Ranking）** 。*（重念chong2）*

### 重排序（Re-Ranking）
为啥非得细筛？省 Token？自然只是其中一个（最重要的）原因了。核心原因是 一个叫 迷失在中间（Lost in the Middle）的缺陷。过于冗杂的 Prompt 往往会忽视中间的致命问题的答案。

Re-Ranking 的核心技术是交叉编码器（Cross-Encoder）。对，又是 Transformer 模型里提到过的。这个模型把用户提问中的词和初筛后的词进行 Attention计算，完美平衡高精度和低延迟。根据 Re-Ranking 的得分，最终决定被留下的是哪个。

BGE-Reranker / BAAI/bge-reranker-quantbased。

### 小块检索、大块喂入

### 检索后处理（post-retrieval）：重排之外还有上下文压缩。

## 高级 RAG 部分总结
| 技术点 | 偏“语义理解” | 偏“增强检索” | 所处阶段 |
| :--- | :---: | :---: | :--- |
| **更好的 Embedding 模型** | ✅ | | 索引阶段 |
| **语义切块** | ✅ | | 索引阶段 |
| **查询改写 / 分解 / HyDE / Step-back** | ✅ | | 检索前 (Pre-retrieval) |
| **混合检索 (Dense + BM25)** | | ✅ | 检索中 (Retrieval) |
| **重排序 (Cross-Encoder)** | | ✅ | 检索后 (Post-retrieval) |
| **小块检索，大块喂入 (父子块)** | | ✅ | 索引 + 检索阶段 |
| **上下文压缩** | | ✅ | 检索后 (Post-retrieval) |

## Modular RAG —— 一种框架

对 RAG 范式的革命：把"用什么组件"和"组件怎么连"这两件事彻底解耦。

+ 上半部分 = Modules(积木库:你有哪些功能单元)
+ 下半部分 = Patterns(拼装图:这些单元怎么连成一条流水线)

### 上半部分 Modules

**内圈**：核心四架构
+ 检索（Retrieve）：从知识库取回相关内容
+ 读取（Read）：LLM 读上下文并产出答案
+ 重排（Re-rank）：对检索结果重新排序
+ 重写（Re-write）：对 query 做改写/分解

**外圈**：增强模块
+ 记忆（Memory）：历史对话、缓存、过往交互
+ 融合（Fusion）：提到过的 融合检索
+ 示范（Demonstrate）：few-shot
+ 预测（Predict）：先"生成"预测性的上下文，降噪和补缺
+ 路由（Routing）：判断这个问题走哪条路
+ 搜索（Search）：其他数据源（Web、SQL、API）的检索

### 下半部分 Patterns
积木的搭建过程。例如：

`检索（Retrieve） -> 读取（Read）` = `朴素 RAG （Naive RAG）`

`重写（Re-write） -> 检索（Retrieve）-> 重排（Re-rank） -> 读取（Read）` = `高级 RAG （Advanced RAG）`

`示范（Demonstrate） -> 搜索（Search） -> 预测（Predict）` = `DSP 范式`

`检索（Retrieve） -> 读取（Read）` （循环） = `迭代/递归检索`

## 其他变化

### 检索前


智能路由（Query Routing）：根据用户输入的意图，动态决定去哪里查数据。

### 检索中

父子块/块大小解耦（Parent-Child Retrieval）：上一节提到过。

多模态与排版感知（Layout-Aware）：

### 检索后

信息压缩与去噪（Context Compression）：小模型去噪音。

解决“迷失在中间”（Lost in the Middle）：

## 流程的变化
自我反思与评估机制（Self-RAG / Corrective RAG）：高级 RAG 会让另一个反思模块去检查，
1. 真的假的？是不是幻觉？
2. 检索出来的 Chunk 能回答问题吗？

高级 RAG 还可能进行多轮迭代。

```mermaid
graph TD
    Start([用户提出复杂问题]) --> QRe([Query 改写与多路拆解])
    QRe --> Route{智能路由识别}
    
    Route -- 需要外部知识 --> Retrieve[向量/标量混合检索]
    Route -- 结构化数据 --> SQL[查询数据库/API]
    
    Retrieve --> Rerank[二阶段重排与去噪 Rerank]
    SQL --> Rerank
    
    Rerank --> Eval1{评估1: 检索到的文档<br>是否足以回答问题?}
    
    Eval1 -- 不足/无关 --> RewriteQuery[变换检索策略/改写 Query]
    RewriteQuery --> Retrieve
    
    Eval1 -- 充足 --> Generate[LLM 结合上下文生成答案]
    
    Generate --> Eval2{评估2: 生成的答案<br>是否存在幻觉/依据不足?}
    
    Eval2 -- 存在幻觉 --> Generate
    Eval2 -- 安全可靠 --> PostProcess[最终应答后处理]
    
    PostProcess --> End([输出最终精准答案])