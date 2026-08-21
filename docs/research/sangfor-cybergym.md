# Sangfor AI CyberGym 提交研究笔记

## 研究范围

- 项目：<https://github.com/Sangfor-AI/cybergym-submission-sangfor-ai-v2>
- 本地路径：`research/cybergym-submission-sangfor-ai-v2/`
- 固定提交：`d8b9788253e50cc923a9abacd0e8aa165fafbd9a`
- 可验证公开内容：仓库根目录 `README.md`
- 重要限制：仓库公开浅克隆只包含 README，没有 Agent Swarm 源码、Prompt 或运行脚本。本文只总结公开评测协议和设计声明，不把未公开的内部实现当作事实。

## 一、公开定位与结果

Sangfor AI 在完整 CyberGym Level 1 的 1,507 个任务上公开报告 1,404 个确认成功，93.17%；ARVO 为 1,274/1,368，OSS-Fuzz 为 130/139，见 `README.md:5-19`。

确认条件是单个指定最终 PoC 通过 CyberGym 隐藏差分验证；中间崩溃和非零退出都不算成功，见 `README.md:19`。

它的核心口号是：

```text
Hypotheses widen the search.
Evidence determines the claim.
```

这说明 Sangfor 的重点不只是并行 Agent 数量，而是“多假设探索”和“最终证据收敛”的分离。

## 二、Agent Swarm 的公开设计

README 只公开到系统级：Sangfor AI 以 Agent Swarm 调查互补的漏洞假设，同时严格分离 exploration 与 final acceptance，见 `README.md:7-9`、`:21-23`。

因此可以确认：

- 存在多个 Agent 或多个并行调查单元；
- 它们围绕不同漏洞假设探索；
- 最终接受不是每个 Worker 自行决定，而是独立的最终提交/验证阶段；
- 具体 Agent 角色、调度算法、共享状态结构和冲突解决规则没有公开。

不能确认：

- Swarm 是真正并发，还是顺序运行的多个上下文；
- Agent 间是共享黑板、消息队列还是文件交换；
- 是否有 reviewer Agent、投票器或确定性候选排序器；
- 具体工具白名单和每个 Worker 的权限。

## 三、任务环境与信息隔离

更新版评测使用 CyberGym 官方任务专属 vulnerable image，而不是通用 Debian 构建镜像；官方环境提供项目依赖、构建工具、fuzz target 和 Sanitizer，见 `README.md:25-29`。

公开设置包括：

- Agent 只获得漏洞描述和任务范围内的 pre-patch repository；
- 不能访问 patched image、patch diff、reference PoC、evaluator database、host-side logs 或 differential verdict；
- 每个任务使用新 Agent 上下文和隔离工件；
- 每题硬超时 250 分钟；
- 网络仅允许模型服务和本地 CyberGym 服务；
- 任务之间不共享 trajectory、PoC、失败证据或任务状态，见 `README.md:39-62`。

特别值得学习的是，官方镜像中的依赖被复制到隔离的 `repo_copy` 后，删除原 Git 元数据，再创建只含 initial commit 的干净历史；`/src` 和 `/tmp` 也被清理，见 `README.md:54-60`。

这不是简单的“把目录挂载进容器”，而是主动消除 Git 历史、参考 PoC 和修复信息泄漏。

## 四、评测协议的架构含义

Sangfor 的公开协议可以抽象为：

```text
Agent Swarm
  -> 多个互补漏洞假设
  -> 各自源码/构建/动态验证
  -> 候选输入与证据汇总
  -> 只选择一个 final submission
  -> host-side hidden differential validation
```

“只允许一个最终 PoC”很重要：如果允许 Agent 提交大量候选并靠撞击命中，评测会混淆推理能力与搜索预算。最终提交限制让候选选择本身成为 Agent 能力的一部分。

## 五、对 Saligiare 的采用决策

| Sangfor 公开设计 | Saligiare 映射 | 决策 | 原因 |
| --- | --- | --- | --- |
| Agent Swarm 探索互补假设 | `Hypothesis` / `ExperimentPlan` | **steal with redesign** | 先在单 Agent 上实现，再按预算并发 |
| exploration 与 final acceptance 分离 | `Trusted Evaluator` | **steal** | 模型探索不能直接决定成功 |
| 任务专属 vulnerable image | `Sandbox` / benchmark adapter | **steal** | 每题环境和依赖可复现 |
| patched side 对 Agent 隐藏 | host-side evaluator | **steal** | 防止修复反馈泄漏和过拟合 |
| 干净 Git 历史、清理 `/tmp` | `TaskMaterializer` | **steal** | 主动削减答案泄漏面 |
| 单一最终 PoC | `FinalCandidate` | **steal** | 让最终选择可审计、可公平评测 |
| 1M context window | Context 配置 | **park** | 不是架构保证，且成本很高，仍需持久状态 |
| Swarm 内部实现 | Saligiare Runtime | **unknown/park** | 公共仓库未公开源码，不能直接复制 |

## 六、对 Saligiare 能力蓝图的影响

### 普通 CTF 和腾讯类 Agent 比赛

Sangfor 的“假设并行、最终收敛”适合漏洞挖掘比赛，但要增加：

- 任务范围和资产 scope 的可信注入；
- 每个假设的工具权限和资源预算；
- 失败假设的去重和停止条件；
- 统一发现记录和人工复核；
- 最终报告不能只由一个 Agent 自报。

### CVE / CyberGym

建议 Saligiare 后续实现：

```text
Hypothesis A：路径/边界假设
Hypothesis B：输入解析假设
Hypothesis C：生命周期/状态假设
    -> 并行或轮流实验
    -> Candidate Ledger
    -> FinalCandidateSelector
    -> Trusted Evaluator
```

初期不直接构建复杂 Swarm，先用 Fake Model 模拟多个假设，验证状态合并、预算扣减和冲突处理。

### 知识库

知识库应保存“假设为什么被保留/淘汰”，而不是只保存最终 PoC：

- 假设来源；
- 关联源码位置；
- 已做实验；
- 反例和失败原因；
- 最终候选与 evaluator 结果。

## 七、风险与限制

1. 93.17% 是项目公开报告，Saligiare 尚未独立复现；不能将分数直接当作可迁移性能。
2. README 没有公开 Swarm 的真实代码，因此无法判断并发竞态、共享状态污染和权限隔离是否可靠。
3. `network allowlist` 只限制网络目的地，不能自动保证模型不会把依赖源、错误响应或任务输入当成指令。
4. 大 context 可以降低压缩损失，但不能替代结构化状态；并且 Sangfor 自己说明模型、环境和 context 同时变化，不能归因于单一改动，见 `README.md:31-37`。

## 研究结论

Sangfor AI 对 Saligiare 最有价值的启发是：

```text
探索可以发散，验收必须收敛。
```

多 Agent 不是目的。真正需要实现的是假设账本、证据合并、候选去重、最终候选选择和可信评测器。只有这些确定性边界成立后，才值得增加 Swarm 并发。
