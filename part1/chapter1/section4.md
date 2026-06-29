架构的分化：Encoder-Decoder → GPT（Decoder-only）vs BERT（Encoder-only）

## Pre normalization 和 Post normalization

大部分都在用 Pre normalization，而不是传统的 Post normalization。

采用 pre-norm 能使整个模型的训练更稳定（如下图），并且可以让梯度直接回传到原始输入。



## LayerNorm 和 RMSNorm

初始版的 Transformer 使用 LayerNorm ，需要对均值和方差进行归一化。

目前使用 RMSNorm，不会减去均值或添加偏差项。



## 激活层

初始版的 Transformer 使用 ReLU 。

后续使用 GeLU 函数。

从2023年开始，很多模型都开始使用 Gated activations 的变体 SwiGLU（Swish-Gated Linear Unit）。


$$
\text{ReLU}(x) = \max(0, x) 

\\

% 精确形式
\text{GELU}(x) = x \Phi(x) = x \cdot \frac{1}{2} \left[ 1 + \text{erf}\left( \frac{x}{\sqrt{2}} \right) \right]
\\

% Tanh 近似形式
\text{GELU}(x) \approx 0.5x \left( 1 + \tanh\left( \sqrt{\frac{2}{\pi}} \left( x + 0.044715x^3 \right) \right) \right)

\\

% Swish 定义
\text{Swish}_\beta(x) = x \cdot \sigma(\beta x)

\\

% SwiGLU 定义 (\otimes 表示按元素相乘 Element-wise product)
\text{SwiGLU}(x) = \text{Swish}_1(xW + b) \otimes xV + c
$$


## Position Embeddings

+ 基础：Sine embeddings
+ Absolute embeddings
+ Rope embeddings