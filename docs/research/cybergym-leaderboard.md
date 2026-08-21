# CyberGym Leaderboard 研究矩阵

## 研究范围与快照

- 榜单：<https://www.cybergym.io/cybergym/>
- 代码仓库：<https://github.com/sunblaze-ucb/cybergym>
- 论文：<https://arxiv.org/abs/2506.02548>
- 数据集：<https://huggingface.co/datasets/sunblaze-ucb/cybergym>
- 本地读取日期：2026-08-21
- 快照说明：榜单会更新；本文记录的是该日期页面显示的 47 条记录，不代表永久排名。

页面明确说明：CyberGym Level 1 共 1,507 个实例，来自 188 个大型软件项目。Agent 获得漏洞描述和 pre-patch 未修复代码，需要生成可工作的 PoC；成功要求 PoC 在 pre-patch 版本触发目标漏洞，并在 post-patch 版本保持干净。`Success Rate` 是按实例统计的成功率；多 trial 时，一个实例任意一次成功就算成功。

榜单还使用两个标签：

- `dynamic`：Agent 在 sanitized vulnerable Docker image 或目标程序编译二进制上动态执行；
- `test-time mem.`：Agent 使用跨实例更新的测试时知识库或记忆。

这两个标签表示评测策略，不代表题目难度被降低。榜单同时警告：运行具有随机性，分数差异不一定代表有意义的能力差距。

## 一、完整公开榜单

下表按页面当前排名抄录。`公开入口`只表示榜单页面给了代码、文章、模型卡或团队页面链接，不等于源码、镜像和运行命令都公开。

| 排名 | Agent/Model | 类型/策略 | 模型或基础系统 | 成功率 | 日期 | 公开入口 |
| ---: | --- | --- | --- | ---: | --- | --- |
| 1 | Sangfor AI AGENT | Agent, dynamic | DeepSeek-V4-Flash | 93.2% | 2026-08-08 | [仓库](https://github.com/Sangfor-AI/cybergym-submission-sangfor-ai-v2)；[官方说明](https://www.sangfor.com/news-and-press-release/sangfor-ai-ranked-4-on-cybergym-2026) |
| 2 | Whitzard（白泽） | Agent, dynamic | DeepSeek-V4-Flash | 91.2% | 2026-08-07 | [仓库](https://github.com/WhitzardAgent/Whitzard) |
| 3 | MDASH | Agent, dynamic | GPT-5.4、Claude Opus 4.6、Claude Sonnet 4.6 | 91.0% | 2026-06-17 | [Microsoft Security](https://www.microsoft.com/en-us/security/blog/2026/06/17/beyond-the-benchmark-advancing-security-at-ai-speed/)；[MAI Cyber](https://microsoft.ai/news/introducing-mai-cyber-1-flash-inside-mdash/) |
| 4 | Wiz Atlas | Agent, dynamic | GPT-5.5、Claude Opus 4.6 | 90.9% | 2026-07-27 | [Wiz 文章](https://www.wiz.io/blog/atlas-ai-vulnerability-researcher) |
| 5 | DoGNAVY | Agent, dynamic | GLM-5.2 | 90.8% | 2026-08-03 | [DeepSec 报告](https://deepsec.darknavy.net/blog/cybergym) |
| 6 | Crystalline | Agent, test-time memory | Claude Opus 4.6 | 89.6% | 2026-06-08 | [榜单来源入口](https://github.com/synchopate/cybergym-logos) |
| 7 | RedbudAI | Agent, dynamic + test-time memory | GLM-5.2 | 86.3% | 2026-08-10 | [清华 Redbud 文章](https://redbud.tsinghua.edu.cn/posts/cybergym.html) |
| 8 | GPT-5.5-Cyber | Model | OpenAI Agent | 85.6% | 2026-06-22 | [OpenAI](https://openai.com/index/daybreak-securing-the-world/) |
| 9 | Velldepth Agent | Agent | XekRung | 85.3% | 2026-08-03 | [Velldepth writeups](https://alibaba-velldepth.github.io/writeups/) |
| 10 | Xuanwu Atuin AI | Agent, dynamic | GLM-5.2 | 84.8% | 2026-07-22 | [GLM-5.2 文章](https://xlab.tencent.com/en/2026/07/17/xuanwu-atuin-cybergym-glm52/)；[GLM-5.1 文章](https://xlab.tencent.com/en/2026/07/02/xuanwu-atuin-cybergym/) |
| 11 | Claude Mythos Preview | Model | Anthropic Agent | 83.1% | 2026-04-07 | [System Card](https://www.anthropic.com/claude-mythos-preview-system-card) |
| 12 | GPT-5.5 | Model | OpenAI Agent | 81.8% | 2026-04-23 | [OpenAI](https://openai.com/index/introducing-gpt-5-5) |
| 13 | GPT-5.4 | Model | OpenAI Agent | 79.0% | 2026-04-23 | [OpenAI](https://openai.com/index/introducing-gpt-5-5) |
| 14 | DeepSeek-V4-Flash | Model | DeepSeek Agent | 76.7% | 2026-07-31 | [模型入口](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731) |
| 15 | MopMonk Agent | Agent | MiniMax M3 | 73.1% | 2026-06-28 | [仓库](https://github.com/MopMonkAI/MopMonkAgent) |
| 16 | JiuXuan（九玄） | Agent, dynamic | GLM-5.1 | 72.9% | 2026-08-03 | [仓库](https://github.com/as837430732/JiuXuan) |
| 17 | GLM-5.1 | Model | Claude Code | 68.7% | 2026-04-07 | [Z.ai](https://z.ai/blog/glm-5.1) |
| 18 | Claude Opus 4.6 | Model | Anthropic Agent | 66.6% | 2026-02-05 | [System Card](https://www.anthropic.com/claude-opus-4-6-system-card) |
| 19 | GPT-5.4 | Model | Codex CLI | 66.3% | 2026-04-07 | [Z.ai](https://z.ai/blog/glm-5.1) |
| 20 | Claude Sonnet 4.6 | Model | Anthropic Agent | 65.2% | 2026-02-17 | [System Card](https://www.anthropic.com/claude-sonnet-4-6-system-card) |
| 21 | SageAgent | Agent, dynamic | GPT-5 | 60.2% | 2026-02-09 | [OpenSage](https://www.opensage-agent.ai/) |
| 22 | Muse Spark 1.1 | Model | Meta Agent | 59.0% | 2026-07-09 | [评估报告](https://ai.meta.com/static-resource/muse-spark-1-1-evaluation-report) |
| 23 | DeepSeek-V4-Pro | Model | Claude Code | 57.7% | 2026-07-13 | [仓库](https://github.com/XDxAI/cybergym-deepseek-submission-2026) |
| 24 | Claude Opus 4.5 | Model | Anthropic Agent | 50.6% | 2026-02-05 | [System Card](https://www.anthropic.com/claude-opus-4-5-system-card) |
| 25 | Muse Spark | Model | Meta Agent | 43.5% | 2026-04-14 | [评估报告](https://ai.meta.com/static-resource/muse-spark-safety-and-preparedness-report) |
| 26 | GLM-5 | Model | Claude Code | 43.2% | 2026-02-12 | [Z.ai](https://z.ai/blog/glm-5) |
| 27 | Kimi K2.5 | Model | Kimi Agent | 41.3% | 2026-02-02 | [论文](https://arxiv.org/abs/2602.02276) |
| 28 | GPT-5 | Model | OpenHands | 39.4% | 2025-12-05 | CyberGym Team |
| 29 | Gemini 3.1 Pro | Model | Gemini CLI | 38.8% | 2026-04-07 | CyberGym Team |
| 30 | Claude Sonnet 4.5 | Model | Anthropic Agent | 28.9% | 2025-09-29 | [System Card](https://www.anthropic.com/claude-sonnet-4-5-system-card) |
| 31 | Claude Opus 4.1 | Model | Anthropic Agent | 25.0% | 2025-09-29 | CyberGym Team |
| 32 | GLM-4.7 | Model | Claude Code | 23.5% | 2026-02-12 | [Z.ai](https://z.ai/blog/glm-5) |
| 33 | Claude Sonnet 4 | Model | Anthropic Agent | 22.6% | 2025-09-29 | CyberGym Team |
| 34 | Claude Sonnet 4 | Model | OpenHands | 17.9% | 2025-05-23 | CyberGym Team |
| 35 | Claude Sonnet 3.7 | Model | Anthropic Agent | 14.5% | 2025-09-29 | CyberGym Team |
| 36 | Claude Sonnet 3.7 | Model | OpenHands | 11.9% | 2025-05-15 | CyberGym Team |
| 37 | GPT-4.1 | Model | OpenHands | 9.4% | 2025-05-15 | CyberGym Team |
| 38 | GPT-4.1 | Model | Cybench | 9.0% | 2025-05-15 | CyberGym Team |
| 39 | GPT-4.1 | Model | Codex CLI | 7.4% | 2025-05-15 | CyberGym Team |
| 40 | GPT-4.1 | Model | ENiGMA | 7.2% | 2025-05-15 | CyberGym Team |
| 41 | Gemini 2.5 Flash Preview | Model | OpenHands | 4.8% | 2025-05-15 | CyberGym Team |
| 42 | DeepSeek-V3 | Model | OpenHands | 3.6% | 2025-05-15 | CyberGym Team |
| 43 | o4-mini | Model | OpenHands | 2.5% | 2025-05-15 | CyberGym Team |
| 44 | R2E-Gym-32B | Model | OpenHands | 2.0% | 2025-05-15 | CyberGym Team |
| 45 | Qwen3-235B-A22B | Model | OpenHands | 1.9% | 2025-05-15 | CyberGym Team |
| 46 | OpenHands-LM-32B | Model | OpenHands | 1.7% | 2025-05-15 | CyberGym Team |
| 47 | SWE-Gym-32B | Model | OpenHands | 0.1% | 2025-05-15 | CyberGym Team |

## 二、公开程度和可复现性矩阵

榜单的 `Source` 是一个入口，不是完整复现实验的证明。按当前公开材料可以分成四档：

| 档位 | 证据条件 | 当前榜单例子 | 能否直接复现 |
| --- | --- | --- | --- |
| A：代码和运行线索 | 有公开仓库，至少能看到 README、配置或提交历史 | Sangfor、Whitzard、MopMonk、JiuXuan、XDxAI | 仍需检查依赖、模型服务、镜像和评测权限；不能仅凭仓库宣称可运行 |
| B：技术报告/源码片段 | 有技术报告或详细 writeup，但没有完整运行器 | DoGNAVY、Velldepth、Xuanwu Atuin、MDASH、Wiz Atlas、Redbud | 可学习架构和实验口径，通常不能一键复现 |
| C：官方模型/系统说明 | 有模型卡、官方博客或论文，但 Agent harness 不公开 | GPT-5.5-Cyber、Claude Mythos、DeepSeek-V4-Flash、Muse Spark | 可比较公开分数，不足以复现 Agent 行为 |
| D：历史基线记录 | 只有榜单中的历史实验名称和分数 | OpenHands、Cybench、ENiGMA 等旧记录 | 只能作为基线，必须额外寻找实验配置 |

### 已完成的深入研究

Saligiare 已经分别记录了榜单中几个高分 Agent 的公开证据：

- [Sangfor AI CyberGym](sangfor-cybergym.md)：公开 README，源码不完整；Agent Swarm、单一最终 PoC、patched-side 隔离。
- [Whitzard](whitzard.md)：公开仓库只有 README；阶段化工具、显式证据和唯一 `submit_poc` verdict。
- [DeepSec DoGNAVY](deepsec-dognavy.md)：公开技术报告；多阶段复现、独立 Review、validator 隔离。
- [Alibaba Velldepth](velldepth.md)：公开 writeups；多候选假设、double-crash 和潜在 zero-day 的严格区分。
- [Tencent Xuanwu Atuin](atuin.md)：公开技术文章；源码、二进制、JavaScript bundle 的多 Agent 工作流。

这五类文档的共同限制是：公开分数和架构说明不等于公开完整代码、镜像、模型访问和逐任务日志。

## 三、CyberGym 的评测边界

页面公开的核心流程是：

```text
漏洞描述 + pre-patch 代码
  -> Agent 浏览源码和运行环境
  -> 生成/修改 PoC
  -> 在 vulnerable side 执行并根据反馈迭代
  -> 外部验证 pre-patch 触发、post-patch 不触发
  -> 统计实例成功率
```

Agent 不应从以下信息推断自己已经成功：

- 模型生成的 `solved` 字段；
- 仅在 vulnerable side 发生的任意崩溃；
- 与目标漏洞无关的 sanitizer 报告；
- patched side 也能触发的 double-crash；
- 没有版本哈希、命令和日志的自然语言描述。

可信结论至少需要：

```text
target_match = PoC 触发了目标漏洞
fixed_clean = patched side 没有同一漏洞触发
evidence = 输入、命令、日志/崩溃栈、版本哈希
verdict = 外部 evaluator 的接受/拒绝/不确定回执
```

这正是 Saligiare 需要把 `Observation`、`Evidence` 和 `Evaluator Verdict` 分开的原因。

## 四、榜单页面给出的跨系统发现

### 1. 更高成功率不只来自模型名称

榜单同时展示 Model 和 Agent。比如相同或相近模型在不同 harness 下有明显差距：OpenAI、Anthropic 和 DeepSeek 都出现了多个不同 Agent/CLI 组合。不能把 Agent 分数直接当作模型裸能力，也不能把模型记录和 Agent 记录混在一张“模型排名”中比较。

### 2. 动态执行是重要能力，但会扩大隔离要求

高排名记录中多个 Agent 标记为 `dynamic`。这表示 Agent 可以在任务镜像或目标二进制上运行测试并使用反馈，通常比只读源码更接近真实漏洞复现。但动态执行会带来命令、文件、网络、资源和恶意样本隔离问题，Saligiare 应把它放在 `Sandbox` 和 `Policy Guard` 之后。

### 3. 测试时记忆必须单独评测

`test-time mem.` 可能让 Agent 从之前实例积累经验，但也会改变任务间独立性。Saligiare 的实验记录必须写明：

- 是否允许跨任务记忆；
- 记忆写入的时间点和来源；
- 记忆是否包含 evaluator 回执；
- 清空记忆后的独立基线；
- 记忆是否可能泄漏任务间的补丁或题解信息。

### 4. 步数存在收益上限

页面引用的分析显示，在最多 100 步的 OpenHands/Claude Sonnet 4 实验中，成功主要集中在 20-80 步，20-50 步附近达到峰值，接近一半运行在 80-100 步时仍未成功。对 Saligiare 来说，最大步数不是越大越好；应记录“新证据产生率”和“每步成本”，在长期无进展时停止或切换策略。

### 5. PoC 长度是重要难点

页面说明：0-10 字节的 ground-truth PoC 成功率最高；超过 100 字节时成功率约 10%，而这类实例占 65.7%。这意味着 Agent 需要专门的输入构造、变异、最小化和执行反馈工具，而不是只增强自然语言推理。

## 五、榜单统计的口径问题

CyberGym 页面顶部写出“34 zero-day vulnerabilities、18 incomplete patches”。同一页面的详细说明又写到：759 个 PoC 在 60 个项目触发崩溃，人工确认 17 个 incomplete patch；post-patch 仍崩溃的 35 个 PoC 去重后对应 10 个 unique zero-day。

这可能是不同时间、不同实验范围或“PoC 数量/漏洞数量/公开统计”口径造成的差异，但页面没有在当前文本中解释。Saligiare 不应把这些数字合并成一个未经限定的指标。知识库需要明确字段：

```text
raw_poc_count
crash_count
unique_vulnerability_count
incomplete_patch_count
latest_release_validated
measurement_scope
```

## 六、映射到 Saligiare 核心协议

| CyberGym 概念 | Saligiare 协议 | 设计要求 |
| --- | --- | --- |
| benchmark instance | `Task` | 固定任务 ID、目标版本、范围、预算和 evaluator |
| 漏洞描述 | `Task.metadata` / `Hypothesis` 初始输入 | 作为不可信输入，不能修改权限 |
| pre-patch repository | `Sandbox` 的只读/可构建制品 | 记录提交哈希和镜像摘要 |
| Agent 生成 PoC | `Action` 或 `CandidateResult` | 参数结构化、大小限制和审计 |
| 命令/编译/运行反馈 | `Observation` | 截断、脱敏并标记来源 |
| 崩溃栈、日志、输入 | `Evidence` | 关联 Trace、版本和复现命令 |
| patched-side 回归 | `Trusted Evaluator` | 与 Agent 隔离，不能被模型伪造 |
| success rate | `Benchmark Result` | 保存 trial、seed、模型和统计口径 |
| test-time memory | `Knowledge Store` | 版本化、可清空、记录跨任务边界 |
| dynamic execution | `CapabilityPlan` + `Sandbox` | 由策略编译工具和资源白名单 |

## 七、Saligiare 的实验设计

为了学习 Agent 原理，不应一开始追求榜单分数。建议按以下顺序建立可解释基线：

1. **无模型 Fake Runtime**：用预设 Action 模拟源码查看、PoC 构造、执行、失败和提交；验证状态机与评测边界。
2. **单 Worker、无记忆**：固定模型、固定最大步数和单任务容器，记录每次 Observation 与 Evidence。
3. **单 Worker、测试时记忆**：只允许写入脱敏的失败模式和工具使用统计，比较独立任务和有记忆任务。
4. **多 Worker 黑板**：让多个 Worker 提出候选 Hypothesis，由确定性合并逻辑去重和排序，不允许 Worker 直接写最终 verdict。
5. **动态执行**：加入受限编译/运行工具，验证网络、文件系统、资源和超时策略。
6. **真实本地 benchmark**：先接入可授权、可复现的少量任务，最后再扩大样本。

每个实验必须同时保存：

```text
benchmark_version
task_ids
model_and_harness
prompt_revision
memory_policy
trial_seed
max_steps
tool_policy
sandbox_image_digest
trace_path
evaluator_verdict
cost_and_duration
```

## 八、当前结论

CyberGym Leaderboard 能回答“哪些系统在公开 Level 1 评测上取得了什么分数”，但不能单独回答“哪个 Agent 可以被 Saligiare 直接复现或安全复用”。目前最值得迁移的不是某个 Prompt，而是以下工程边界：动态执行和源码推理需要同一条可审计 Trace；PoC 触发与 patched-side clean 必须由外部 evaluator 判定；记忆、并发、步数和成本都必须显式记录；公开分数、公开代码、可运行环境和可复现实验必须分栏管理。

下一步应把这份榜单矩阵与已有的 CHYing-agent、Cairn、Whitzard、Sangfor、DoGNAVY、Velldepth 和 Atuin 研究合并，形成 Saligiare 的最终能力组件表，然后进入 Phase 2 的 `Task`、`Action`、`Observation`、`Result` 和 Fake Runtime 手写实现。
