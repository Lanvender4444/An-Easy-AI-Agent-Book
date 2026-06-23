# Skills

一个 skill 就是一个含 SKILL.md 的文件夹（YAML 元数据 name+description + 指令正文，外加可选的 scripts/、references/、assets/），而它的运行机制正好是 harness「让上下文保持精简」的手段：启动时只加载每个 skill 的名字和描述（刚够判断何时该用），命中任务才把完整 SKILL.md 读进上下文，执行时才按需加载脚本或引用文件。

每个 skill 的发现成本中位数大约 80 token，所以装很多也不撑爆上下文。