# 基础 RAG（Naive RAG）与 三大件
在朋克音乐中，有我们熟悉的 “三大件”，即吉他、贝斯 和 鼓。在 Naive RAG 中，“三大件” 是 **数据准备与索引（Indexing）**、**检索（Retrieval）** 和 **生成（Generation）** 。 接下来，我将介绍一下这三大件。

## 数据准备与索引（Indexing）
所谓索引，就是把不同格式的文本提取出来，构建出机器可见可检索的过程。
在索引过程中，我们通常由以下几个步骤：

1. 解析： 把不同格式文件里的文本内容解析出来。
2. 切块（Chunking）：非常形象的步骤，把巨量的文字切成一小块。
3. 向量化（Embedding）：利用 Embedding 模型，将每个文本切块转化为一串高维数学向量。这个Embedding模型，可以包括cosine函数 、 内积 、甚至是 ANN。
4. 向量数据库（Vector DB）：存入专门的向量数据库。（Milvus, Pinecone, Chroma, PGVector）

切块的问题：
1. 语义碎片化（Semantic Fragmentation）：固定切块，丢失上下文。可以使用轻量级句向量模型、Embedding模型或者参数小的大语言模型来进行动态切块（Semantic Chunking）
2. 长尾依赖丢失（Long-range Dependency）：分块失去主语。父子块架构（Parent-Child / Cluster Retrieval）或大模型前置改写。分为小块和大块，切块前让 LLM 提取全局实体上下文，拼接到每个子块头部。本质为：分离检索空间和生成空间，只索引特征明显的 Child Chunk，加载出 Parent Chunk。Context Enrichment（上下文增强 / 引入上下文扩展）：当某个 Chunk 被检索命中后，系统根据它的唯一标识（如 chunk_id），自动向前（Forward）和向后（Backward）扩展获取相邻的 N 个 Chunk（例如提取当前块的前 1 块和后 1 块）
3. 如何设置块大小（Chunk Size）？多尺度并行索引（Multi-scale Indexing）。就是切分小中大三块。
4. 如何设置重叠度（Overlap）？动态自适应重叠（Dynamic Overlap）与句子边界锁定。重叠区的边界必须严格锁定在句号（.、。）或段落分界符，重叠大小根据当前段落的 Token 密度动态收缩。
5. 如何感知结构化信息？面包屑元数据注入（Breadcrumb Metadata Ingestion）。维护一个文档层级树。每个 Chunk 的元数据和文本头部都强制注入其所属的完整路径（例如：[系统架构 -> 高并发设计 -> 缓存击穿]）使孤立的 Chunk 重新获得文档树形拓扑结构的加权。
6. 如何解决级联效应（Cascading Updates）？基于文档指纹（Doc-Level Hash）与块级 ID 固定映射（Consistent Chunk IDing）。不使用自增 ID，而是对文档的稳定段落计算 MD5/SHA256 作为 Chunk ID。文档局部修改时，只更新 Hash 改变的块。本质就是git。
7. 如何处理时间敏感性？时间戳版本快照与滑动衰减（Temporal Decay）。增加指数衰减或者其他的什么衰减函数。
8. 极度不均匀的文本密度怎么办？基于 Token 密度的自适应权重分流（Density-based Chunking）。通过检测单位字符内的信息量（熵率或 Token 密集度），对信息密集的表格采取极小切块+属性展开，对稀疏的叙述采取大文本块。本质是香农熵（Information Entropy）。信息量大的文本块包含更多的正交特征维度，防止高密度的特征相互淹没（Feature Smearing）。


向量化的问题：
1. 一词多义与上下文湮灭。全推导上下文增强（Contextual Ingestion）或领域精调（Fine-tuning）。在向量化前，将整篇文章的摘要或关键词以 Invisible Prompt 的形式拼接到当前 Chunk 中再输入模型，或使用 Contrastive Learning（对比学习）在行业语料上进行微调。
2. 分布不均与“锥形效应”（Anisotropy / Cone Effect）？Whitening（白化旋转）或求残差（Embedding Normalization）。对模型输出的原始向量进行线性变换（如 PCA 白化），强行拉伸特征空间。
3. 泛化能力差？BGE-M3 混合表征 / 弱监督对比学习（SimCSE / PrompEemb）。引入混合检索（Dense 稠密向量 + Sparse 稀疏向量如 BM25/SPLADE），用 Sparse 捕捉行业硬匹配词，用 Dense 捕捉模糊语义。原理是双塔模型（Two-Tower Model）在未见域的失效可以通过稀疏表征（Sparse Embedding）来补救。Sparse Embedding 本质上是高维空间的词频/词权（如词袋模型扩展），它不依赖语义理解，能强行锚定行业黑话和独有实体。
4. 计算延迟怎么办？两阶段解耦、动态批处理（Dynamic Batching）与离线队列（Kafka + Celery）。使用异步离线，线上查询采用小模型（如 bge-small）。
5. 如何解决短查询与长文本的不对称匹配（Asymmetric Retrieval）问题？假设性文档生成（HyDE - Hypothetical Document Embeddings）或 Query 扩展。
6. 怎么解决对抗性攻击与噪音敏感（Prompt Injection / Noise）问题？向量裁剪（Truncation）、黑名单向量过滤（Blacklist Filtering）与语义显著性检验。什么是对抗性攻击？即在高位维存在的“恶性凸起”。通过在数据清洗阶段降低词频异常度，或在向量层引入 Layer Normalization，抑制极端异常激活值（Outliers）对整体特征方向的拉偏，保证系统的鲁棒性。

## 检索（Retrieval）
将用户的问题，用同一个 Embedding 模型转化为一个向量，通过一些数学公式（如余弦相似度），寻找和这个问题最匹配的前 K 个文本切块（Top-K）。



## 生成（Generation）
拼贴进LLM

## 主流向量数据库介绍
### Milvus
读写分离、存算分离、微服务化的计算架构。分为协调节点（Coordinator）、访问层（Proxy）、执行节点（Worker，包括 QueryNode、DataNode、IndexNode）。

数据持久化依赖对象存储（MinIO/S3），元数据依赖 etcd，消息存储依赖 Kafka/Pulsar。

数据在段（Segment）中流转。当 Segment 填满后会触发 IndexNode 异步构建索引。基于 HNSW（Hierarchical Navigable Small World） 和 IVF（Inverted File）构建的索引。

### Pinecone

### Qdrant

### Chroma