# Saligiare 参考 Agent 能力组件矩阵

## 文档目的

前面的研究笔记分别分析了 CHYing-agent、Cairn、TCH 复盘、Whitzard、Sangfor AI、DeepSec DoGNAVY、Alibaba Velldepth、Tencent Xuanwu Atuin 和 CyberGym Leaderboard。本文件把它们放在同一张矩阵中，回答三个问题：

1. 哪些设计已经被公开源码、测试或技术报告支持；
2. 哪些做法只适合某一场比赛，不能直接变成 Saligiare 默认行为；
3. Phase 2 开始手写协议时，哪些概念必须先成为类型和测试。

证据等级仍然是：

```text
源码与测试 > 官方技术报告 > 官方 README > 榜单/宣传页面 > 二手文章
```

公开分数、公开代码、可运行环境和可复现实验始终分开记录。

## 一、参考项目总览

| 参考项目 | 主要场景 | 公开证据 | 主要抽象 | Saligiare 判断 |
| --- | --- | --- | --- | --- |
| CHYing-agent | CTF、渗透竞赛 | 有源码、Prompt 和会话/Trace 代码 | Orchestrator + 专家子 Agent + Prompt/Progress 编译 | 借鉴可观测性和上下文编译；拒绝默认高权限和工具黑名单式安全 |
| Cairn | 通用长任务、TCH 竞赛 | 有源码、测试和设计文档 | Fact/Intent/Hint 黑板 + DAG + Server/Dispatcher/Worker | 借鉴黑板、状态图、心跳、取消和 Mock Driver；补上 Policy Guard/Evaluator |
| TCH 复盘 | 真实 AI 渗透竞赛 | 参赛者一手文章，无完整源码 | 通用 Worker、Kali 环境、并发探索、Flag Skill | 借鉴通用 Worker 和成本复盘；拒绝“装满工具即默认可用” |
| Whitzard | CyberGym Level 1 | 公开仓库仅 README | 阶段工具、计划、证据、候选历史、`submit_poc` oracle | 借鉴唯一最终裁决和 fixed-clean；不能把 README 当实现证据 |
| Sangfor AI | CyberGym Level 1 | 公开仓库仅 README | Agent Swarm、多漏洞假设、探索/接受分离 | 借鉴候选并行和单一最终 PoC；补充假设合并与权限边界 |
| DeepSec DoGNAVY | CyberGym、开放式发现 | 官方技术报告/公开页面 | 多阶段复现、静态/动态闭环、独立 Review | 借鉴独立审查和 validator 隔离；保留任务级 sandbox |
| Alibaba Velldepth | CyberGym、潜在 zero-day | 官方 writeups | 结构化 harness、多候选、语义/运行时联合审查 | 借鉴 double-crash 分析和不确定性字段 |
| Tencent Xuanwu Atuin | CyberGym | 官方技术文章 | 源码、二进制、JavaScript bundle 多 Agent 流程 | 借鉴统一 campaign context；不把跨域知识自动变成权限 |
| CyberGym Leaderboard | Level 1 公开评测 | 官方榜单、论文、数据集 | 1,507 任务、pre/post-patch、动态执行、试次统计 | 作为 Benchmark Adapter 和 Evaluator 契约来源 |

## 二、按能力维度比较

### 1. 运行时拓扑

| 设计 | 代表项目 | 可迁移部分 | Saligiare 版本 |
| --- | --- | --- | --- |
| 单一 Orchestrator 调专家 Agent | CHYing-agent | 入口、上下文、停止和子任务关系清晰 | 作为早期 `Agent Runtime`，专家仅是可选执行策略 |
| Server/Dispatcher/Worker | Cairn、TCH | 长任务、并发、取消、心跳和资源调度 | `Runtime` 与 `Task State Store` 分离 |
| Agent Swarm | Sangfor | 多候选假设并行探索 | 只并行 `Hypothesis`，不让 Worker 直接写 verdict |
| 多阶段专门角色 | DoGNAVY、Atuin | 源码、构建、验证和 review 的职责差异 | 在高风险模式中做权限边界，而非只做 Prompt 角色 |
| 单 Worker 通用环境 | Whitzard、TCH | 快速适配未知题型 | 运行时提供灵活工具，但由 Policy Guard 动态裁剪 |

### 2. 状态和记忆

| 状态类型 | 公开来源 | Saligiare 类型/存储 |
| --- | --- | --- |
| 会话、token、重试、进度 | CHYing-agent | `TraceEvent`、`RunSummary`、`BudgetUsage` |
| Fact、Intent、Hint、DAG | Cairn | `Observation`、`Hypothesis`、`TaskState`、引用关系 |
| 计划、问题、证据、候选历史 | Whitzard、Sangfor | `CapabilityPlan`、`Evidence`、`CandidateResult` |
| 跨实例测试时记忆 | CyberGym 榜单标签 | `KnowledgeStore`，必须可清空并带来源/版本 |
| 赛后人工意图 | TCH 复盘 | `PolicyRevision`，不可修改历史 Trace |

关键原则：Fact/Observation 是状态记录，不等于可信漏洞结论；只有 `Trusted Evaluator` 可以写最终 verdict。

### 3. 工具和反馈

| 设计 | 代表项目 | 学习点 | Saligiare 约束 |
| --- | --- | --- | --- |
| 专家 Agent 绑定 MCP 工具 | CHYing-agent | 工具可见性会改变模型行为 | Tool Registry 按任务 capability 生成视图 |
| 通用 CLI/容器环境 | Cairn、TCH | 灵活处理未知题型 | 命令执行仍需参数、目录、网络、时间和输出限制 |
| 阶段化工具 | Whitzard | 降低错误工具使用和上下文噪声 | 由计划/策略阶段编译白名单 |
| Flag/PoC 专用提交 | CHYing-agent、Whitzard、TCH | 最终提交是特殊协议，不是普通 Shell | `SubmitCandidateTool` 只提交候选，Evaluator 独立回执 |
| 执行反馈闭环 | CyberGym、DoGNAVY | PoC 需要运行、观察、修改循环 | Observation 必须标注来源，不能把输出当指令 |

### 4. 可信边界和隔离

| 风险点 | 研究中观察 | Saligiare 决策 |
| --- | --- | --- |
| 模型自报成功 | Cairn Fact 可以是未经验证的自然语言 | 结论必须来自 Evaluator |
| patched-side 泄漏 | CyberGym 顶级 Agent 明确隐藏 fixed side | Evaluator、patched build、reference PoC 与 Agent 隔离 |
| Local 宿主机执行 | Cairn 配置明确承认无沙箱 | 只作为显式开发模式，不能是默认后端 |
| `bypassPermissions` | CHYing-agent、Cairn 出现高权限执行开关 | 不复制；权限由确定性 Policy Guard 控制 |
| 网络/容器能力 | `network_mode: host`、Kali 全工具环境等 | 默认无公共网络、非 root、任务级目录和资源上限 |
| 知识库污染 | 外部页面、PoC、日志可能含提示注入 | Knowledge Store 不得授予工具权限 |

## 三、Saligiare 最终组件表

下表是从研究转为实现的最小组件边界。Phase 2 只实现前五项和 Fake Runtime；后续阶段再加入真实工具、沙箱和 benchmark 适配器。

| 组件 | 输入 | 输出 | 可信程度 | Phase |
| --- | --- | --- | --- | --- |
| `BenchmarkAdapter` | 外部任务定义、样例和评测协议 | 可信 `Task`、Evaluator 句柄 | 可信边界 | 5 |
| `Task` | `task_id`、mode、scope、budget、evaluator_id | 不可由模型修改的任务上下文 | 可信配置 | 2 |
| `CapabilityPlan` | 模型提出的目标、能力和禁止项 | Policy Guard 的候选计划 | 未批准前不可信 | 2-3 |
| `Action` | 工具名、参数、父状态引用 | 待策略检查的动作 | 不可信 | 2 |
| `ToolRegistry` | 已注册工具和 schema | 可供模型发现的工具视图 | 可信注册表 | 3 |
| `PolicyGuard` | Task、CapabilityPlan、Action、预算 | 允许/拒绝及原因 | 可信执行前门 | 3 |
| `Sandbox` | 已批准工具、镜像、资源限制 | 隔离的工具执行结果 | 受控执行边界 | 4 |
| `Observation` | 工具 stdout/stderr、文件、HTTP 或设备反馈 | 截断、脱敏、带来源的观察 | 不可信数据 | 2-4 |
| `Hypothesis` | Observation、源码线索、候选输入 | 待验证的漏洞或解题假设 | 未验证 | 2 |
| `Evidence` | 命令、输入、日志、版本、Trace 引用 | 可审计证据 | 需来源校验 | 2-5 |
| `TrustedEvaluator` | CandidateResult、独立环境和版本 | accepted/rejected/inconclusive | 最终裁决 | 5 |
| `TraceStore` | 每次状态、动作、预算、模型和回执 | 可复现运行轨迹 | 审计记录 | 2 起 |
| `KnowledgeStore` | 脱敏 Evidence、失败模式和研究笔记 | 可检索知识，不改权限 | 不可信辅助输入 | 6 |

## 四、五个核心协议的第一版字段

### `Task`

```text
task_id
mode
target
scope
source_version
allowed_capabilities
required_approval
budget
evaluator_id
metadata
```

`scope`、`allowed_capabilities`、`required_approval` 和 `evaluator_id` 只能由任务加载器注入。

### `Action`

```text
action_id
tool_name
arguments
parent_observation_ids
requested_capability
reason
```

`reason` 只用于解释和审计，不能代替策略判断。未知工具、额外字段和过大参数应在解析阶段失败。

### `Observation`

```text
observation_id
action_id
source
status
summary
raw_ref
truncated
created_at
```

原始输出应受大小和敏感数据策略限制；摘要不能被当成 evaluator verdict。

### `Result`

```text
task_id
status
candidate_refs
evaluator_verdict
evidence_refs
trace_id
budget_usage
```

模型只能产生候选结果，不能伪造 `evaluator_verdict`。

### `TraceEvent`

```text
run_id
sequence
event_type
actor
payload_ref
policy_decision
timestamp
```

Trace 要能重放状态转换，但不能保存 API Key、Cookie、真实用户数据或未脱敏凭证。

## 五、从研究进入实现的验收门槛

Phase 2 开始前必须能回答：

1. 为什么 `Observation` 不是 `Evidence`？
2. 为什么模型不能直接写 `Result.solved = true`？
3. 为什么 Task 的 capability 和 evaluator 不能由 Prompt 修改？
4. 为什么 Fake Model 比直接接入真实 API 更适合先验证 Agent Loop？
5. 为什么多 Worker 的第一版应该合并 Hypothesis，而不是合并最终答案？
6. 为什么步数、并发、tokens 和成本属于运行时状态，而不是日志备注？

### Phase 2 的第一组测试

- Fake Model 连续返回两个合法 Action，Runtime 得到两个 Observation 后停止成功；
- Fake Model 返回未知工具，Policy Guard 拒绝并写入 Trace；
- 达到最大步数时停止，不能无限重试；
- 两个 Worker 对同一目标提出互相冲突的 Hypothesis，状态合并保留两者及来源；
- Fake Evaluator 返回 rejected 时，Result 不能变成 accepted；
- 跨任务 KnowledgeStore 关闭时，第二个任务看不到第一个任务的记忆；
- 所有测试不需要网络、API Key、Docker 或真实安全工具。

## 结论

参考 Agent 的共同有效部分不是“某个固定 Prompt”，而是可观察状态、受控工具、并发/恢复、候选与结论分离，以及可信评测器。它们的竞赛优化差异很大：有的依赖通用 Kali，有的依赖阶段化工具，有的依赖测试时记忆，有的依赖独立 review。Saligiare 的学习顺序应先把这些差异压缩成最小、可测试的协议，再逐步加入高风险执行能力。

下一份实现任务是：你亲手创建 `src/saligiare/core/task.py`、`action.py`、`observation.py`、`result.py` 和对应测试；我负责逐文件解释设计、给出不完整代码骨架、设计测试和审查你的实现。
