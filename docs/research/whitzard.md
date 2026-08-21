# Whitzard（白泽）研究笔记

## 研究范围

- 项目：<https://github.com/WhitzardAgent/Whitzard>
- 本地路径：`research/Whitzard/`
- 固定提交：`8b123fa90c62490b35f3cf2eb08eb0627c618095`
- 可验证公开内容：`README.md`、`README.zh-CN.md`
- 重要限制：该仓库的公开浅克隆只包含 README，没有 QitOS 源码、任务级 Prompt 或运行实现。因此本文把 README 声明标记为“公开设计声明”，不把它当成已验证的源码事实。

## 一、定位与评测结果

Whitzard 是面向真实世界漏洞复现的 Agent 系统，不是通用渗透工具集合。它针对 CyberGym Level 1：输入是漏洞描述、漏洞版本源码和 harness，输出是具体 PoC 输入；最终要求漏洞版本触发、修复版本 clean，见 `research/Whitzard/README.md:9-26`。

公开 README 报告：1,507 个任务中 1,374 个 fixed-clean PoC，91.2% 验证复现率；32 个超时、94 个已触发但未通过 fixed-clean、7 个不可恢复执行错误，见 `README.md:28-35`。这些是项目公开报告的结果，尚未由 Saligiare 独立复现实验。

第一条重要结论是：Whitzard 把“触发漏洞版本”与“通过修复版本差分验证”严格分开。它不把崩溃、Sanitizer 报告或模型自信当成成功。

## 二、运行时模型

### 1. QitOS + Whitzard 两层职责

README 声明 Whitzard 构建在 QitOS 之上：QitOS 提供执行内核、类型化工具契约、状态归约、上下文组装和事件追踪；Whitzard 增加 CyberGym 任务模型、证据纪律、候选输入溯源和验证策略，见 `README.md:45-49`。

这和 Cairn 的 Dispatcher/Worker 分离不同：

```text
QitOS：通用长程 Agent Runtime
    -> 类型化工具、状态归约、上下文、事件
Whitzard：CyberGym 领域层
    -> 任务状态、证据、候选输入、oracle 规则
```

QitOS 没有随本仓库公开，无法继续追踪其真实入口、状态类或工具实现。这是当前研究的明确未覆盖范围。

### 2. 单任务 Agent，而不是多任务共享记忆

公开设计称每个 CyberGym 任务使用一个 task-level Agent，并按阶段控制能力；显式保存计划、待解问题、证据、候选历史和 oracle 回执，见 `README.md:47-59`。

这不是跨任务 RAG：每个任务独立开始，长期状态只在当前任务内持续。这样可以避免一个项目泄漏另一个项目的 PoC、补丁或任务知识。

### 3. 阶段化调查循环

公开设计把过程拆成证据收集、候选构造和重新调查等模式；每个模式加载适合当前目标的工具，但沿用相同的决策状态，见 `README.md:71-77`。

可抽象为：

```text
source / harness 分析
    -> 根因与可达路径假设
    -> 候选输入构造
    -> vulnerable-side 动态观察
    -> 候选复盘
    -> 回到更早阶段修正假设
```

候选提交必须说明这次改变检验哪个假设，因此失败尝试不会只是日志，而会变成下一次实验的输入。

## 三、工具能力边界

公开工具表见 `README.md:51-59`：

| 工具组 | 公开工具 | 作用 | 结果地位 |
| --- | --- | --- | --- |
| 源码/输入 | `READ`、`GLOB`、`GREP`、`HexView`、`StructProbe` | 定位源码、查看字节、验证结构假设 | 诊断证据 |
| 工作区/执行 | `BASH`、`WRITE`、`EDIT` | 构造候选、局部执行 | 诊断证据 |
| 决策状态 | `NOTE`、`TODO_*`、`SWITCH` | 保留结论、问题和阶段切换 | 持久状态 |
| 可达性 fuzzing | `fuzz_witness` | 生成到达目标函数或 `file:line` 的 witness | 中间构造物，不是成功 |
| 动态诊断/验证 | `gdb_debug`、`submit_poc` | 观察运行时、提交候选给 benchmark oracle | `submit_poc` 才是评测入口 |

### `fuzz_witness` 的设计价值

`fuzz_witness` 让 Agent 指定断点或函数、提供 seed corpus，然后通过 staged libFuzzer + gdb 找到能够到达该位置的变异输入，见 `README.md:37-43`。

它刻意区分：

```text
到达代码位置 != 触发漏洞
触发漏洞版本 != fixed-clean
```

witness 可以继续作为更深断点的 seed，也可以被 HexView/StructProbe 检查和手工修改。只有 `submit_poc` 的最终 oracle 回执能让任务进入 solved。

这对 Saligiare 很重要：内核、WebKit 和 Android 任务中，我们也需要把“路径可达性”“Sanitizer 观察”“漏洞机制”和“修复前后差异”拆成不同证据等级。

## 四、状态与证据纪律

### 1. 证据是控制平面

README 明确说 source read、shell 输出、debugger stop、Sanitizer 和模型置信度都不是完成条件，只有 vulnerable-trigger + fixed-clean 的提交 oracle 才能关闭任务，见 `README.md:61-65`。

这比简单的 `solved=true` 严格得多：Agent 的状态机不由模型自报成功驱动，而由外部可信评测器决定。

### 2. 持久决策状态

Whitzard 公开描述的持久状态包括：

- 当前计划；
- 活跃问题；
- 任务清单；
- 实验回执；
- 绑定到源码位置的证据笔记；
- 候选输入历史；
- oracle 回执。

每轮用这些状态重建决策上下文，而不是无限追加聊天记录，见 `README.md:67-69`。

### 3. 先做根因计划，再构造字节

根因计划需要指定 sink、harness 路径、输入载体、门槛、漏洞机制和未决问题，见 `README.md:79-81`。这会把“试很多随机输入”改造成一组可证伪实验：下一次输入必须区分 carrier、selector、route、gate 或 mechanism 中至少一个具体失败原因，见 `README.md:83-87`。

## 五、实验隔离与泄漏控制

公开实验设置声明：

- 每题最多 4 小时；
- 使用任务专属 Docker 环境；
- vulnerable binary 只读挂载；
- 不向 Agent 提供 patched image、patch diff、reference PoC、grader 凭据或固定版反馈；
- `network_mode=none`，不提供搜索、浏览器或外部检索工具；
- 评测结束后由外部流程执行 fixed-clean 验证，见 `README.md:97-123`。

这些控制同时解决两种风险：

1. Agent 从 benchmark 外部获得答案；
2. Agent 越过任务容器影响真实网络。

公开声明还指出，Agent 只看到基础镜像和只读漏洞二进制，不看到完整漏洞镜像中的 `/tmp/poc` 或 Git 历史。这是数据泄漏边界，而不是仅靠 Prompt 要求“不许看答案”。

## 六、对 Saligiare 的采用决策

| Whitzard 设计 | Saligiare 映射 | 决策 | 原因 |
| --- | --- | --- | --- |
| oracle 是唯一完成裁决者 | `Trusted Evaluator` | **steal** | 适用于 TSECBENCH、CVE、内核和 WebKit |
| 显式计划、问题、证据、候选历史 | `EvidenceGraph` + `TraceStore` | **steal** | 让长任务可恢复、可解释 |
| 阶段化工具能力 | `CapabilityPlan` + `Policy Guard` | **steal** | 工具按阶段和任务模式收敛 |
| `fuzz_witness` 可达性见证 | `ReachabilityWitness` | **steal with redesign** | 必须与漏洞确认、修复差分分开 |
| 候选输入变更必须绑定假设 | `ExperimentReceipt` | **steal** | 失败输入也能指导下一步 |
| vulnerable-only Agent 环境 | Sandbox + host-side evaluator | **steal** | 防止 fixed-side 反馈泄漏 |
| `network_mode=none` | Sandbox 网络策略 | **steal as default** | CTF/CyberGym 默认关闭外网 |
| QitOS 黑盒能力 | Saligiare Runtime | **park** | 公开仓库没有源码，先学接口思想，不复制依赖 |
| 91.2% 公开分数 | 实验注册表 | **have as evidence, not guarantee** | 分数需记录模型、环境、版本和验证协议 |

## 七、对 Saligiare 能力蓝图的影响

### CyberGym / CVE 复现

Saligiare 的 `vuln_reproduce` 应至少有以下状态：

```text
Hypothesis
  -> ReachabilityWitness
  -> CandidateInput
  -> VulnerableObservation
  -> ReviewerAssessment
  -> TrustedEvaluatorVerdict
```

不能把 `ReachabilityWitness` 或崩溃日志直接写成 `Solved`。

### Linux 内核 / Android 内核

`fuzz_witness` 的思想可用于到达系统调用、驱动函数或特定分支，但执行权限要放在专用 Kernel VM/模拟器中；源码读取、构建和利用验证仍然拆成不同能力域。

### WebKit

WebKit 任务可以把 JavaScript 输入、IPC 消息或测试页面当成候选输入；需要记录“到达 WebCore/JSC 位置”和“触发目标生命周期错误”之间的证据差距。

### 知识库

把每次候选尝试存成结构化实验回执：输入摘要、修改关系、运行环境、观察、失败原因、后续问题和 oracle 结果。知识库只能辅助回忆，不能改变工具权限。

## 八、不能直接照搬的部分

1. 不能因为 `BASH`、`WRITE` 和 `EDIT` 被称为 controlled 就默认它们安全；Saligiare 必须由 Policy Guard 校验路径、命令、资源和网络。
2. 不能把公开 README 的分数当作源码可复现事实；QitOS 和任务级实现没有公开在当前浅克隆中。
3. 不能把 zero-day/漏洞发现结果直接发布为确认漏洞；必须有授权、复现证据、影响分析和人工审查。
4. 19.4B token 的公开资源消耗说明高分可能伴随极高成本，Saligiare 必须把预算作为 Task 字段和评测指标。

## 研究结论

Whitzard 最值得学习的不是某个具体 Prompt，而是三条纪律：

```text
可达性证据 != 漏洞证据
漏洞版本触发 != fixed-clean 成功
模型判断 != benchmark verdict
```

它把长期漏洞复现从“不断试输入”变成“围绕假设进行有区分度的实验”。这会成为 Saligiare `ExperimentReceipt`、`Evidence` 和 `TrustedEvaluator` 设计的重要来源。
