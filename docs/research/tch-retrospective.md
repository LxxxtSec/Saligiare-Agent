# TCH 第二届智能渗透挑战赛复盘研究

## 研究范围与证据等级

本文研究的是 l3yx 发布的《国内最强 AI 渗透测试 Agent —— TCH·腾讯云黑客松第二届智能渗透挑战赛 唯一 AK 战队复盘》：

- 文章 URL：<https://l3yx.github.io/2026/04/21/%E5%9B%BD%E5%86%85%E6%9C%80%E5%BC%BA-AI-%E6%B8%97%E9%80%8F%E6%B5%8B%E8%AF%95-Agent-%E2%80%94%E2%80%94-TCH%C2%B7%E8%85%BE%E8%AE%AF%E4%BA%91%E9%BB%91%E5%AE%A2%E6%9D%BE%E7%AC%AC%E4%BA%8C%E5%B1%8A%E6%99%BA%E8%83%BD%E6%B8%97%E9%80%8F%E6%8C%91%E6%88%98%E8%B5%9B-%E5%94%AF%E4%B8%80-AK-%E6%88%98%E9%98%9F%E5%A4%8D%E7%9B%98/
- 原文链接：<https://mp.weixin.qq.com/s/DlpEH7bVr0xi0VawPJs3XA>
- 阅读日期：2026-08-21
- 证据类型：参赛者一手赛后复盘，属于二手公开材料中的高价值经验，但不是公开源码、测试或官方评分日志。

文章没有公开 Cairn 的完整实现，也没有公开动态计分表、每个赛区的题目清单和所有运行日志。因此，本文不会把未公开的调度细节、工具权限和评测器实现写成已验证事实。

## 一、比赛和结果

### 1. 赛制变化

作者描述的第一届比赛使用 `xbow-engineering/validation-benchmarks`，偏向 CTF Web 题。每天随机抽取一批题目，Agent 在赛段内自主答题，赛段结束后题目不重复使用，按难度和分数排名。

第二届改为官方命题、对参赛 Agent 黑盒，并将题目拆成四个赛区：

1. 现实世界 SRC 与通用漏洞挖掘；
2. 典型 CVE 与 AI 基础设施漏洞利用；
3. 多层内网渗透与权限维持；
4. 基础域渗透。

题目一次性放出，但需要在前一个赛区达到解题数量门槛后才能进入下一个赛区。动态计分规则使早期速度和稳定性非常重要：开局落后会显著降低后续追赶机会。

### 2. 公开成绩和可比性

文章给出的规模是第二届 610 支战队、1345 名选手；作者称自己使用 Bytex 战队个人参赛，最终唯一 AK（通过全部挑战），排名第四。作者还提到第一届队名 Antix，最终第四；本届另一位队友以 For Future 战队排名第七。

“唯一 AK”和“第四名”同时出现，说明榜单并非简单按通过题数排序，动态计分、解题时间、赛段门槛或早期得分都会影响最终排名。文章中的榜单以图片展示，本文没有把图片中的每一行名次和分数转录为结构化数据，避免手工误读。

## 二、真实比赛任务拆分

文章没有披露单道题的内部协议，但从四个赛区和作者的描述可以抽象出一条跨题型任务链：

```text
赛区解锁条件
  -> 目标与服务建模
  -> 源码/配置/运行时侦察
  -> 漏洞假设
  -> 可达性和利用验证
  -> Flag 或结果提交
  -> 平台评分和下一题调度
```

这与普通 CTF 的差异在于：

- 题目可能要求把 SRC 线索、CVE 知识、云基础设施和内网路径组合起来；
- 题目数量和赛区解锁构成外部状态机；
- Agent 需要在多个并行任务之间分配模型调用、容器和时间；
- 早期错误配置不仅影响单题，还可能影响整个比赛的排名。

对 Saligiare 的直接启发是：`Task` 不能只有题目描述，还要带 `stage`、`unlock_condition`、`submission_deadline`、`score_rule_id` 和任务级预算。赛区状态应由 Benchmark Adapter 或 Trusted Evaluator 管理，不能由模型自报“已解锁”。

## 三、工具反馈如何驱动下一步

文章没有逐条展示工具调用轨迹，但给出了一个很明确的设计取舍：Cairn 不为“信息收集 Agent”“Web 漏洞利用 Agent”“后渗透 Agent”分别设计固定角色，而是给最小调度单位 Claude Code 或 Codex 一个足够通用、装满工具的 Kali 环境，让 Worker 自己决定下一步。

这里的反馈闭环可以还原为：

```text
Worker 观察终端/文件/网络响应
  -> 在黑板或 DAG 上更新问题状态
  -> 继续调用通用环境中的命令和工具
  -> 生成 Flag 提交动作
  -> Server/评测器返回成功或失败
```

应区分三类反馈：

1. **环境观察**：命令输出、HTTP 响应、文件内容、扫描结果和错误信息。这些都可能是不可信数据，不能直接成为系统指令。
2. **协议状态**：任务是否完成、某个 Intent 是否被接受、是否获得新的子任务。这由 Cairn Server 或适配器决定。
3. **评测回执**：Flag 是否正确、漏洞是否命中、是否满足赛区门槛。这应来自平台或本地 Trusted Evaluator，而不是模型自评。

作者明确提到只有一个比赛专用 Skill，即 Flag 提交 Skill；没有通用漏洞利用 Skill、MCP 或传统 RAG 知识库。这说明“工具结果可见”与“工具结果可信”必须分开设计：通用 Worker 可以自由观察，但提交动作必须经过专用、类型化的协议入口。

## 四、失败恢复与人类反馈

文章提供了四个重要失败恢复信号：

- 比赛第一天存在配置失误和并发不足；
- 前两天策略较保守，第一天平均每个 Flag 约 52 元、约 660 万 tokens；
- 第三天提高并发后成本最高，但平均每个 Flag 约 284 元、约 4000 万 tokens，出现明显边际收益递减；
- 第四天没有新增 Flag，却消耗了较高成本；当晚作者彻底复盘日志并注入人工意图，第五天完成 AK。

这不是“模型多跑几轮就一定能恢复”的证据。更准确的工程结论是：

1. 运行时必须记录可比较的 Trace，包括任务、模型、并发度、提示词版本、工具调用、失败原因、耗时、tokens、成本和评测回执；
2. 需要把配置错误和题目失败分开记录，避免把全局调度问题误判成模型能力不足；
3. 并发度应是受预算约束的运行时参数，不应由 Worker 随意扩大；
4. 人工复盘可以修改下一轮的策略或提示词，但必须形成版本化的 `PolicyRevision`，不能直接篡改历史 Trace；
5. “没有 Flag”不等于“没有有效观察”。失败尝试、疑似根因和未完成路径都应保存到知识库，供后续实验分析。

## 五、并发和多 Agent 的实际取舍

作者反对按安全领域拆分的传统多 Agent 结构，理由不是 Agent 数量本身，而是固定分工和 Agent 之间低效的信息交换。他选择：

- 一个通用问题解决引擎；
- 多个同质或少量异质的 Agent Worker；
- 由 Cairn Server 和 Dispatcher 维护黑板、Intent、Fact 与 DAG 状态；
- 通过并发 Worker 扩大探索，而不是把“侦察、利用、后渗透”硬编码成角色。

这套方法适合探索空间大、题型变化快的竞赛，但有两个前提：

- Worker 的环境和工具必须足够通用；
- 状态写入、取消、心跳、预算和最终提交必须由确定性服务控制。

Saligiare 不应直接复制“给每个 Worker 一个高权限 Kali 容器”。更稳妥的迁移方式是分两层：

```text
通用探索 Worker
  -> 只提出带证据引用的 Action/Hypothesis
Policy Guard + Sandbox
  -> 决定哪些工具和资源真的可用
Trusted Evaluator
  -> 判断漏洞/Flag/补丁回归是否成立
```

在源码审计、内核和 WebKit 任务中，还应额外保留 `source-audit`、`build-test`、`exploit-validate` 的权限边界。通用 Worker 可以提出跨阶段计划，但不能因为探索结果自动获得宿主机、设备或内核 VM 权限。

## 六、资源预算和成本模型

文章给出的全程数据：连续比赛五天，使用 Claude Opus 和 GPT，消耗约 10.9 亿 tokens，成本约 7692 元人民币（包含每天赛后的总结复盘）。这不是一个可直接复现的成本基线，因为模型版本、上下文缓存、输入输出比例和比赛平台费用均未公开，但足以说明成本控制是核心系统能力。

可以从文中抽取以下指标：

| 指标 | 文章明确内容 | Saligiare 应记录的字段 |
| --- | --- | --- |
| 总 tokens | 约 10.9 亿 | `input_tokens`、`output_tokens`、`cached_tokens` |
| 总成本 | 约 7692 元 | `estimated_cost_cny`、价格表版本 |
| 运行时长 | 5 天连续比赛 | `started_at`、`ended_at`、`active_seconds` |
| 第一天 | 保守、并发低，约 52 元/Flag、660 万 tokens/Flag | `parallelism`、`flags`、`cost_per_success` |
| 第三天 | 并发最高、成本最高，约 284 元/Flag、4000 万 tokens/Flag | `queue_depth`、`retry_count`、`marginal_cost` |
| 第四天 | 无新增 Flag，但成本仍高 | `zero_success_spend`、失败类型分布 |

Phase 2 的 Fake Runtime 就应先实现这些计数器，而不是等接入真实模型后才补。运行时至少需要三种预算：

1. **单任务预算**：最大步数、最大工具执行时间、最大输出量；
2. **Worker 预算**：并发数、单 Worker tokens、单 Worker 费用和空闲超时；
3. **比赛预算**：全局 tokens、金额、赛段时间和人工复盘窗口。

当边际成本连续超过阈值或长期没有新证据时，调度器应降低并发、切换模型、压缩上下文或暂停任务，而不是盲目重试。

## 七、Flag、漏洞和报告的可信判定

文章只公开提到 Flag 提交 Skill，并没有公开 Server 端实现。因此 Saligiare 的设计必须明确补上可信边界：

- Worker 返回的 `solved=true` 只是候选结论；
- Flag 必须由比赛平台或本地 evaluator 校验；
- 漏洞线索必须关联最小复现步骤、输入、目标版本、日志或崩溃证据；
- 公开 CVE、1day 和 Nday 任务还要保存公告、补丁、版本哈希和 fixed-side 回归结果；
- 0day 或 SRC 任务必须带授权来源、目标范围和人工批准状态；
- 知识库应分别保存 `hypothesis`、`observation`、`evidence` 和 `evaluator_verdict`，不能将模型叙述直接升级为漏洞事实。

建议的结果结构如下：

```text
CandidateResult
  task_id
  hypothesis_id
  submission
  evidence_refs
  evaluator_verdict: accepted | rejected | inconclusive
  target_match: true | false | unknown
  fixed_clean: true | false | unknown
  trace_id
```

这套结构可以同时服务 TSECBENCH Flag、CyberGym PoC、CVE 复现、内核崩溃和 WebKit 回归测试。

## 八、哪些设计可以迁移到 Saligiare

### 应采用

| TCH/Cairn 经验 | Saligiare 设计落点 | 迁移理由 |
| --- | --- | --- |
| 用通用 Worker 代替大量固定角色 | `Agent Runtime` + 可配置 `CapabilityPlan` | 减少角色边界和信息转发损耗 |
| Server/Dispatcher 维护黑板和 DAG | `Task State Store`、事件日志和调度器 | 支持长任务、并发、取消和恢复 |
| 只保留比赛真正需要的专用提交能力 | 类型化 `Submit` Tool + Evaluator Adapter | 把最终裁决留在可信边界 |
| 运行日志驱动赛后复盘 | `Trace Store` + 成本/预算指标 | 能解释失败和边际收益递减 |
| 通过环境提供通用能力 | 受 Policy Guard 约束的工具注册表 | 保留灵活性，同时控制权限 |
| 失败尝试和人工意图版本化 | `Hypothesis`、`PolicyRevision`、知识库引用 | 支持学习而不篡改历史 |

### 应重新设计

| 文章中的做法 | Saligiare 的调整 |
| --- | --- |
| “装满工具的 Kali 容器” | Phase 4 先提供最小只读工具；按模式和任务动态生成白名单，不默认暴露全部工具 |
| Worker 可以自由完成任何事情 | 模型只能提出 Action，确定性 Policy Guard 决定是否执行 |
| 赛后由人类直接注入意图 | 通过版本化配置、提示词和策略变更进入下一次运行，并保留审批记录 |
| 反对所有固定阶段 | 竞赛探索可以保持开放；内核、Android、WebKit 和 SRC 必须保留源码、构建、验证的权限分层 |
| 仅以 Flag 作为竞赛结果 | 统一支持 Flag、漏洞证据、补丁回归、版本和授权状态 |

## 九、哪些做法不适合长期安全 Agent

以下做法可以解释比赛成绩，但不应直接作为 Saligiare 的默认安全策略：

1. **高权限、全工具环境**：比赛题目有明确隔离边界，真实 SRC、内核和设备环境不能假设同样安全。
2. **不设置细粒度能力计划**：通用探索适合快速比赛，但源码读取、构建测试、利用验证和凭证访问必须分开授权。
3. **只依赖最终 Flag**：无法支持漏洞知识积累、误报分析、补丁回归和可审计报告。
4. **把人工经验直接写入运行环境**：会破坏实验可复现性，也难以判断性能提升来自哪项改动。
5. **只用昂贵模型和无限重试**：成本曲线显示并发增加可能导致严重的边际收益递减；长期系统必须有预算和停止条件。
6. **把“没有公开源码”当成已验证实现**：Cairn 的公开仓库和本文都应标记源码可见性，不能据此推断具体权限隔离、容器配置或 Server 一致性实现。

## 十、对 Saligiare 后续实现的具体要求

### Phase 2：Fake Runtime

- Fake Model 预先返回两个探索 Worker 的动作，并模拟不同观察结果；
- 记录 `task_id`、`worker_id`、`attempt_id`、`parent_fact_ids` 和 `budget_delta`；
- 测试成功、失败、无新证据、最大步数、超时和策略拒绝；
- 让多个 Worker 产生相互冲突的 Hypothesis，验证黑板合并不会把未经评测的 Fact 当结论。

### Phase 3：Tool Registry 和 Policy Guard

- 先实现 `EchoTool`、合成文件读取工具和受控 `SubmitCandidateTool`；
- 验证未知工具、未授权工具、超过输出上限和伪造 evaluator verdict 都会被拒绝；
- 对工具输出标注 `Observation`，禁止把输出内容当作下一条系统指令。

### Phase 4：Sandbox

- 为 CTF、源码审计、构建测试和利用验证定义不同的沙箱配置；
- 默认非 root、无公共网络、任务级工作目录、CPU/内存/PID/时间限制和清理；
- 任何 Local 宿主机模式都必须显式标记为开发调试模式，不能成为 benchmark 默认后端。

### Phase 5：TSECBENCH/CyberGym Adapter

- 将赛区或任务解锁条件建模为适配器状态；
- 将 Flag/PoC 提交和 evaluator 回执建模为可信事件；
- 记录模型、提示词、并发、成本、工具、环境镜像和提交结果，支持完整复跑；
- 用公开任务样例和 Fake Evaluator 做端到端测试，再接入真实授权本地 benchmark。

## 十一、待验证问题

以下问题不能从公开文章确认，应在 Cairn 源码、官方比赛资料或作者后续开源后复核：

- Cairn Server 的黑板、Intent、Fact 和 DAG 的确切数据模型与一致性约束；
- Dispatcher 如何实现 Worker 心跳、取消、重试、并发上限和僵尸任务清理；
- Kali 容器的用户身份、网络、挂载、能力和 Docker socket 权限；
- Flag 提交 Skill 的参数校验、重复提交和平台回执处理；
- 动态计分的完整公式、赛段门槛和时间因素；
- 文章中成本图和榜单图片的原始数据；
- 比赛期间是否存在人工可见性、人工审批或平台侧限流。

## 结论

TCH 复盘最有价值的不是“唯一 AK”这一结果，而是它展示了一个竞赛级安全 Agent 的系统性约束：目标状态由平台定义，Worker 需要足够通用，调度器负责并发和状态，提交入口负责最终裁决，运行日志决定能否在失败后改进。

Saligiare 可以借鉴 Cairn 的黑板/DAG 和通用 Worker 思路，但必须增加自己的 `Policy Guard`、任务级 `Sandbox`、结构化 `Evidence` 和 `Trusted Evaluator`。这样既能学习竞赛中的灵活探索，也能把同一套协议安全地扩展到 CVE、Linux/Android 内核、WebKit 和企业 SRC 的授权研究环境。
