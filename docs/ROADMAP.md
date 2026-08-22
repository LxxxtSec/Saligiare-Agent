# Saligiare 学习路线图

## 项目目的

Saligiare 是一个面向**授权本地 benchmark 环境**的安全 Agent 运行时。
项目的目标不是宣称一个 Agent 必然通过所有 benchmark，而是亲手构建、理解、评测并持续改进一个 Agent：它能在可复现环境中执行任务，同时让工具调用、权限和结果都可审计。

主要目标 benchmark 是 TSECBENCH Local。Cybench、InterCode-CTF、CyberGym、CyberSecEval 和 AgentDojo 是补充评测目标。
在 Agent Runtime 稳定后，项目增加两条高级源码审计专线：Linux Kernel 源码审计，以及 WebKit/WebCore/JavaScriptCore 源码审计。

这是一个学习优先的项目。你亲手输入实现代码；导师在每个阶段提供小步设计、代码骨架、测试要求、复盘问题和代码审查反馈。

## 当前进度

截至本路线图更新时，研究阶段已经完成，当前分支为 `docs/research-agent-architecture`，并已同步到远程仓库。已完成的研究成果如下：

| 状态 | 内容 | 主要产出 |
| --- | --- | --- |
| 已完成 | CHYing-agent 架构研究 | `docs/research/chying-agent.md` |
| 已完成 | Cairn 黑板/DAG/Dispatcher 研究 | `docs/research/cairn.md` |
| 已完成 | Whitzard、Sangfor、DoGNAVY、Velldepth、Atuin 研究 | `docs/research/*.md` |
| 已完成 | TCH 第二届比赛复盘 | `docs/research/tch-retrospective.md` |
| 已完成 | CyberGym 完整榜单快照和可复现性矩阵 | `docs/research/cybergym-leaderboard.md` |
| 已完成 | 参考 Agent 到 Saligiare 组件的汇总 | `docs/research/benchmark-matrix.md` |
| 已完成 | Phase 2：Task、Action、Observation、Result、Fake Runtime 和最小 Agent Loop | 32 个测试通过，已推送 |
| 已完成 | Phase 3：Tool Registry、Policy Guard、AuditLog 和 ToolRunner | 57 个测试通过，已推送 |
| 已完成 | Phase 4：隔离执行接口和 Sandbox | `FakeSandbox`、Docker 后端、非 root 最小镜像和真实 smoke test 已完成 |

研究分支可以作为学习资料保留。进入代码实现前，先将研究分支合并到 `main`，再从最新 `main` 创建小而聚焦的实现分支。不要在研究分支上混入 Phase 2 代码。

完整的能力边界、运行模式、授权约束和后续扩展顺序见
[`docs/能力蓝图.md`](能力蓝图.md)。能力蓝图将目标分为竞赛线、Real World CTF 与安全研究线、知识库线，避免把不同风险等级的工具混入同一个默认 Agent。

## 工作原则

1. 只在已授权的本地环境、benchmark 容器和故意存在漏洞的靶场中工作。
2. 在引入框架前，先实现最小且正确的组件。
3. 每项行为在被后续代码依赖前，都必须有测试。
4. 模型只能提出动作；确定性代码负责校验和授权。
5. benchmark 的特有细节必须放在适配器中，不能污染 Agent 核心。
6. 每次实验要保存模型、提示词、工具、限制、Trace 和结果，以便复现。
7. 每个小而聚焦的 Git commit 都必须让项目保持可运行。
8. 所有命令由你亲自输入，所有核心实现由你亲自手敲；导师只负责解释、给出不完整骨架、设计测试和审查 diff。
9. 任何需要真实目标、真实凭证或公共网络的操作，都必须先停在设计和 Fake Runtime 阶段，直到授权范围和隔离环境明确。

## 学习协作契约

### 你的职责

- 在终端亲自输入目录、文件、虚拟环境、测试和 Git 命令。
- 在编辑器中亲自输入核心 Python、测试和配置代码。
- 每次提交前运行测试、Ruff、`git diff --check` 和 `git status`。
- 用自己的话回答本阶段复盘问题，而不是只复制代码注释。
- 发现长期有价值的问题时，补充 `docs/问题记录.md`；低级拼写、路径和重复命令错误不强制记录。

### 导师的职责

- 先解释目录、文件和接口的责任，再给最小代码骨架。
- 不直接代写核心实现，不替你执行需要学习的命令，不跳过测试设计。
- 通过失败测试、边界问题和反例帮助你理解设计。
- 审查你提交的 diff，重点检查正确性、安全性、可测试性和可维护性。
- 只有在你确认理解并通过验收后，才进入下一个组件。

### 每个实操单元的固定节奏

```text
目标说明
  -> 目录/文件职责
  -> 你亲手创建文件
  -> 你亲手写失败测试
  -> 你亲手写最小实现
  -> 运行测试和 lint
  -> 解释失败路径和安全边界
  -> 形成小 commit 并推送
```

导师可以提供命令和代码片段，但这些内容是教学材料，不代表已经替你完成；你应在本地逐行输入，并能够解释每一行的作用。

## 目标架构

```text
Benchmark 适配器 -> Task -> Agent Runtime -> Policy Guard -> Sandbox Tools
                       |        |                |              |
                       |        |                |              +-> 工具结果
                       |        |                +-> 审计 Trace
                       |        +-> 模型 / 状态 / 规划器
                       +-> Evaluator -> 指标 / 报告
```

### 组件职责

| 组件 | 负责什么 | 不应负责什么 |
| --- | --- | --- |
| Benchmark 适配器 | 解析某一个 benchmark 的任务和结果协议 | Agent 推理逻辑 |
| Agent Runtime | 观察、决策、停止和状态记录 | 直接访问宿主机 |
| Model Adapter | 不同模型厂商的请求与响应转换 | 权限决策 |
| Tool Registry | 有类型的工具发现与调度 | 解析 benchmark 结果 |
| Policy Guard | Schema、权限、预算和命令规则 | 用自然语言完成任务 |
| Sandbox | 隔离执行命令和资源限制 | 模型提示词 |
| Evaluator | 可信的成功/失败判定 | 由模型控制的判定标准 |
| Trace Logger | 可复现的运行记录 | 密钥或原始凭证 |

## Benchmark 策略

| 层级 | 目标 | 能证明什么 | 进入条件 |
| --- | --- | --- | --- |
| 1 | 本地 Fake Environment | Agent Loop 和类型化工具调用正确 | 无 API Key 的单元测试通过 |
| 2 | TSECBENCH Local | 协议集成和授权任务执行 | 适配器能解析样例任务 |
| 3 | InterCode-CTF | 有状态终端交互和 Flag 提交 | 命令只在沙箱中运行 |
| 4 | Cybench | 更广泛的 CTF 任务处理 | Trace 和评测器稳定 |
| 5 | CyberGym | 源码审查、PoC/测试、补丁和回归验证 | 已有 Patch Task 协议 |
| 6 | CyberSecEval | 安全能力和滥用风险回归测试 | 基线运行可重复 |
| 7 | AgentDojo / InjecAgent | 间接提示注入和工具调用安全 | 已有策略和 Trace 测试 |
| 8 | Linux Kernel / WebKit 源码审计专线 | 大型 C/C++ 代码库中的漏洞线索、漏报分析和补丁验证 | 已有源码任务协议、构建和测试环境 |

不要将公开排行榜分数等同于可复现性。必须分别记录：

```text
公开分数 != 公开代码 != 可运行环境 != 可复现实验结果
```

## 学习参考项目的计划

以下项目用于收集设计证据，而不是直接复制代码：

| 参考资料 | 要回答的问题 | 产出文件 |
| --- | --- | --- |
| CHYing-agent | Prompt、工具调用、状态和停止条件如何组织？ | `docs/research/chying-agent.md` |
| Cairn | 长时间运行任务和工具编排如何组织？ | `docs/research/cairn.md` |
| Whitzard | CyberGym 漏洞复现中的证据、可达性见证和 fixed-clean 验证如何组织？ | `docs/research/whitzard.md` |
| Sangfor AI CyberGym 提交 | Agent Swarm 如何并行探索假设并收敛到单一最终 PoC？ | `docs/research/sangfor-cybergym.md` |
| DeepSec DoGNAVY | 多阶段漏洞复现、独立 Review、沙箱和 validator 隔离如何组织？ | `docs/research/deepsec-dognavy.md` |
| Alibaba Velldepth | 结构化 harness、多候选审查和 double-crash 问题如何影响 CyberGym？ | `docs/research/velldepth.md` |
| Tencent Xuanwu Atuin | 源码、二进制和 JavaScript bundle 的多 Agent 工作流如何迁移到 CyberGym？ | `docs/research/atuin.md` |
| TCH 比赛复盘 | 哪些任务拆分、工具反馈和失败恢复设计真正有效？ | `docs/research/tch-retrospective.md` |
| CyberGym Leaderboard 及其链接 Agent | 哪些能力声明有代码、论文和可复现运行器支撑？ | `docs/research/cybergym-leaderboard.md` |

对每个参考项目都要基于文件路径或 URL 回答：

1. 运行时入口在哪里？
2. Agent Loop 在哪里？
3. 工具如何声明和校验？
4. 上下文或记忆如何保存并限制大小？
5. 一次运行由什么条件停止？
6. 不可信指令或命令由谁执行？
7. 有哪些安全控制和 Trace？
8. Saligiare 应该采用、拒绝或重新设计什么？

研究证据分级：

```text
源码与测试 > 官方技术报告 > 官方 README > 排行榜/宣传页面 > 二手文章
```

如果参考项目只公开 README 或技术报告，笔记必须明确标注“未检查源码”，不能把角色、权限和运行时细节写成已验证事实。

## 项目阶段

以下进度按每周投入 8-12 小时估算。只有取得列出的证据后才能进入下一阶段。一个阶段可以延长，但不可跳过验收门槛。

### 阶段总览

| 阶段 | 主题 | 当前状态 | 进入条件 | 退出证据 |
| --- | --- | --- | --- | --- |
| 0 | Python/Git/CI 基础 | 已完成 | 无 | 干净克隆可安装、测试和 lint |
| 1 | 参考 Agent 研究 | 已完成 | Phase 0 稳定 | 研究笔记和能力矩阵完成 |
| 2 | 核心协议与 Fake Runtime | 已完成 | 研究矩阵完成 | 32 个无网络测试通过，覆盖状态转换和停止条件 |
| 3 | 类型化工具与 Policy Guard | 已完成 | Phase 2 验收通过 | 57 个测试通过，策略拒绝和工具执行均留 AuditEvent |
| 4 | 隔离执行 | 已完成 | Phase 3 验收通过 | Fake Sandbox、Docker 后端和真实 smoke test 通过；`73 passed, 1 skipped` |
| 5 | 模型适配与 Prompt 纪律 | 下一步 | Fake Runtime 和 Sandbox 稳定 | Fake/真实适配器产生相同已校验 Action |
| 6 | TSECBENCH Local | 待开始 | 沙箱和适配器契约稳定 | 已授权样例任务端到端运行 |
| 7 | 普通 CTF Benchmark | 待开始 | TSECBENCH 基线稳定 | 可复现实验报告和成本记录 |
| 8 | CyberGym/代码漏洞任务 | 待开始 | Patch Task 协议完成 | pre/post patch evaluator 隔离运行 |
| 8A | Linux Kernel 专线 | 规划中 | 通用源码任务稳定 | 内核源码证据和专用 VM 验证 |
| 8B | WebKit 专线 | 规划中 | C++/源码任务和隔离稳定 | 固定提交版本回归验证 |
| 9 | Agent 安全评测 | 规划中 | 工具和 Trace 稳定 | 注入和混淆代理测试通过 |
| 10 | 评测平台与持续迭代 | 持续 | 至少一个真实适配器 | 新贡献者可复现实验 |

### Phase 0：可复现的工程基础（第 1 周）

**学习内容**

- Git commit、分支、远程仓库、rebase 和冲突处理。
- Python 虚拟环境、包、`pyproject.toml` 和类型注解。
- `pytest`、Ruff 和 GitHub Actions。
- 密钥管理，以及为什么 `.env` 绝不能提交。

**你亲手输入的文件**

```text
README.md
pyproject.toml
.gitignore
.env.example
src/saligiare/__init__.py
tests/test_smoke.py
.github/workflows/ci.yml
```

**测试和证据**

```bash
python -m pytest -q
python -m ruff check .
git clone <repository-url> /tmp/saligiare-check
```

新克隆的目录必须可以安装并通过同一套测试。

**建议提交信息**

```text
chore: bootstrap Saligiare project
```

**验收门槛**：能解释为什么使用 `src/` 目录布局、CI 和本地测试有什么区别、以及一台干净电脑如何重新创建项目。

### Phase 1：研究现有 Agent（第 2 周）

**学习内容**

- Prompt 包装器、工具调用助手与 Agent Runtime 的差别。
- 基于证据阅读仓库：入口、调用图、接口、配置和数据流。
- 许可证意识：阅读一个实现不代表可以将其复制进自己的项目。

**你亲手输入的文件**

```text
docs/research/chying-agent.md
docs/research/cairn.md
docs/research/whitzard.md
docs/research/sangfor-cybergym.md
docs/research/deepsec-dognavy.md
docs/research/velldepth.md
docs/research/atuin.md
docs/research/tch-retrospective.md
docs/research/cybergym-leaderboard.md
docs/research/benchmark-matrix.md
```

**研究方法**

1. 将参考项目克隆到被忽略的 `research/` 目录。
2. 阅读 README、许可证、顶层目录、应用入口和工具代码。
3. 第一轮阅读时，不执行不熟悉的安全项目。
4. 每条架构结论都引用文件路径或 URL。
5. 严格区分“观察到的事实”和“自己的设计决定”。

**验收门槛**：为每个 Agent 画出 `观察 -> 决策 -> 工具 -> 观察` 的循环，并写出停止条件和缺失的安全控制。当前已完成，下一步不再继续无边界扩展资料，而是把研究结论转成最小协议。

### Phase 2：领域协议和 Fake Runtime（第 3-4 周）

**学习内容**

- Pydantic 数据模型、可变/不可变字段、Schema 与输入校验。
- 使用 `typing.Protocol` 设计接口。
- 确定性的 Fake Model 与依赖注入。
- 状态机、最大步数预算、失败原因和单元测试设计。

**你亲手输入的文件**

```text
src/saligiare/core/task.py
src/saligiare/core/action.py
src/saligiare/core/observation.py
src/saligiare/core/result.py
src/saligiare/models/base.py
src/saligiare/models/fake.py
src/saligiare/agent/state.py
src/saligiare/agent/loop.py
tests/core/
tests/agent/
```

**最小行为**

- Task 具有稳定 ID、描述、允许的工具、超时、评测器 ID 和不含密钥的 metadata。
- Action 有类型化的工具名和参数。
- Fake Model 可以返回预先编排的动作。
- Agent Loop 在成功、达到最大步数、任务超时或策略拒绝时停止。
- 不需要网络或 API Key 也能测试每次状态转换。

**建议提交信息**

```text
feat: define core task and action protocols
feat: add deterministic fake model
feat: add bounded agent loop
test: cover agent stopping conditions
```

**验收门槛**：展示三个通过的测试：Fake Model 完成两次工具调用、触发最大步数、记录策略拒绝。

#### Phase 2 实操顺序

Phase 2 不一次创建全部目录。每个小单元都先写测试，再写实现；上一单元通过后才进入下一单元。

| 小单元 | 你亲手创建 | 先学什么 | 最小验收 |
| --- | --- | --- | --- |
| 2A Task | `core/task.py`、`tests/core/test_task.py` | Pydantic 字段、不可变任务边界、枚举和预算 | 合法任务可构造；缺少 ID、非法模式和超范围预算会失败 |
| 2B Action | `core/action.py`、`tests/core/test_action.py` | 工具名、参数模型、模型输出为何不可信 | 合法动作可解析；未知工具名和额外字段可控失败 |
| 2C Observation | `core/observation.py`、`tests/core/test_observation.py` | 工具结果和可信证据的区别、输出截断 | 观察能关联动作；过大摘要和非法状态会失败 |
| 2D Result | `core/result.py`、`tests/core/test_result.py` | 候选结果、评测回执和不确定性 | 模型不能伪造 accepted verdict |
| 2E Fake Model | `models/base.py`、`models/fake.py`、`tests/models/` | Protocol、依赖注入和确定性响应 | 同一输入得到可预测动作序列 |
| 2F Runtime State | `agent/state.py`、`tests/agent/test_state.py` | 状态转换、预算扣减和事件记录 | 每次转换可解释、可测试、可重放 |
| 2G Agent Loop | `agent/loop.py`、`tests/agent/test_loop.py` | 停止条件、失败恢复和最大步数 | 成功、拒绝、超时和最大步数全部停止 |

导师在每个小单元只提供：字段设计说明、一个不完整骨架、失败测试目标和复盘问题。你完成后再提交代码，导师进行审查。

### Phase 3：类型化工具和 Policy Guard（第 5-6 周）

**学习内容**

- 工具 Schema、结构化结果、允许列表、拒绝规则和能力边界。
- 为什么工具输出是不可信数据，而不是要执行的指令。
- 单工具超时、输出上限、工作目录限制和审计日志。

**你亲手输入的文件**

```text
src/saligiare/tools/base.py
src/saligiare/tools/registry.py
src/saligiare/tools/echo.py
src/saligiare/security/policy.py
src/saligiare/security/audit.py
tests/tools/
tests/security/
```

开始时只实现 `EchoTool` 和一个只读的合成制品工具。此阶段**不要**加入宿主机 Shell。

**验收门槛**：非法参数、未知工具、不被允许的工具、过大的输出和格式错误的模型动作都必须安全失败并写入 Trace。

### Phase 4：隔离的命令执行（第 7-8 周）

**学习内容**

- Docker 镜像、工作目录挂载、非 root 执行、网络隔离、CPU/内存/PID 限制和清理。
- 命令解析风险，以及为什么不能使用 `shell=True`。
- 为 Agent、工具、benchmark 目标、宿主机和凭证做威胁建模。

**你亲手输入的文件**

```text
docker/sandbox/Dockerfile
src/saligiare/sandbox/base.py
src/saligiare/sandbox/docker.py
src/saligiare/tools/terminal.py
docs/threat-model.md
tests/sandbox/
```

**默认策略要求**

```text
默认关闭网络
容器用户不是 root
不挂载宿主机 home 目录
只允许任务范围内的可写目录
有命令超时和输出上限
有资源限制和清理逻辑
记录完整审计 Trace
```

**验收门槛**：测试证明终端在沙箱中运行、超时能干净结束、不能写入任务工作区外的位置，并记录执行的命令。

### Phase 5：模型适配器和 Prompt 纪律（第 9-10 周）

**学习内容**

- 模型厂商适配器、结构化工具调用、重试、模型错误和速率限制。
- 系统指令、任务上下文、工具结果和提示词版本化。
- 上下文窗口、摘要，以及为什么隐藏思维链不是可信的安全控制。

**你亲手输入的文件**

```text
src/saligiare/models/openai_compatible.py
src/saligiare/prompts/system.md
src/saligiare/prompts/task.py
src/saligiare/agent/context.py
src/saligiare/config.py
tests/models/
```

只有当 Fake Model 的测试稳定后，才引入 OpenAI-compatible Adapter。API Key 只写入本地 `.env`；仓库只提交 `.env.example`。

**验收门槛**：一段保存的 Fake Provider 响应和一次已授权的真实调用，都能产生相同的已校验 `Action` 接口。模型错误不能导致无限重试。

### Phase 6：TSECBENCH Local 适配器（第 11-12 周）

**学习内容**

- 从官方文档了解 TSECBENCH 当前的本地部署、任务生命周期、结果协议、评测器和允许的环境边界。
- Adapter Pattern 和契约测试。

**你亲手输入的文件**

```text
src/saligiare/benchmarks/base.py
src/saligiare/benchmarks/tsecbench/adapter.py
src/saligiare/benchmarks/tsecbench/runner.py
src/saligiare/benchmarks/tsecbench/evaluator.py
tests/benchmarks/tsecbench/
docs/benchmarks/tsecbench.md
```

**验收门槛**：一个已文档化、已授权的本地任务能被加载，转换为通用 `Task`，经由沙箱运行，并转换回官方结果格式。记录准确命令、镜像/版本、模型、提示词版本和 Trace ID。

### Phase 7：CTF Benchmark 能力（第 13-15 周）

**学习内容**

- 终端任务规划、观察结果压缩、检查点、命令失败恢复和故意脆弱靶场中的 Flag 提交。
- 公平实验控制：固定模型、固定 Prompt、固定预算、固定任务切分，不泄露题解。

**你亲手输入的文件**

```text
src/saligiare/benchmarks/intercode/
src/saligiare/benchmarks/cybench/
src/saligiare/evaluation/metrics.py
src/saligiare/evaluation/report.py
docs/experiments/
```

**验收门槛**：发布可复现的小任务基线，包括成功、失败、排除项、成本、耗时、步数和安全策略拦截。

### Phase 8：CyberGym 与代码漏洞任务（第 16-18 周）

**学习内容**

- CWE 推理、仓库检查、测试构造、补丁生成和回归验证。
- 区分“发现可疑代码行”“证明可利用”和“证明补丁正确”。

**你亲手输入的文件**

```text
src/saligiare/core/patch_task.py
src/saligiare/benchmarks/cybergym/
src/saligiare/evaluation/patch_evaluator.py
tests/benchmarks/cybergym/
docs/benchmarks/cybergym.md
```

**验收门槛**：对一个已授权任务，Trace 中记录源码证据、benchmark 范围内的测试或 PoC、补丁和通过的回归评测。

### Phase 8A：Linux Kernel 源码审计专线（第 19-22 周）

这是一条建立在通用代码审计能力之上的高级专线，不在前期直接开始。目标是让 Agent 能在**授权的内核源码、专用测试镜像和离线分析环境**中发现漏洞线索、识别可能漏报的路径，并用测试或补丁验证判断。

**学习内容**

- C 语言内存模型、指针、并发、整数溢出和生命周期。
- Linux Kernel 的系统调用、驱动、网络子系统、VFS、内存管理和权限边界。
- Kconfig、Makefile、编译数据库、交叉编译和最小测试镜像。
- 静态分析、调用图、数据流、锁分析和 Sanitizer 的证据边界。
- KASAN、KCSAN、UBSAN、syzkaller 等工具的职责和限制。
- 如何区分“可疑代码”“可触达路径”“可验证缺陷”和“已修复漏洞”。

**你亲手输入的文件**

```text
src/saligiare/core/source_task.py
src/saligiare/analysis/callgraph.py
src/saligiare/analysis/dataflow.py
src/saligiare/benchmarks/kernel/adapter.py
src/saligiare/benchmarks/kernel/evaluator.py
tests/analysis/
tests/benchmarks/kernel/
docs/benchmarks/kernel-audit.md
docs/research/kernel-tools.md
```

**建议的任务形态**

```text
源码版本和配置
    -> 静态证据收集
    -> 调用路径和数据流假设
    -> 最小化测试或验证程序
    -> 缺陷分类和置信度
    -> 补丁候选
    -> 编译、测试和回归验证
```

**安全边界**

- 只分析明确授权的源码版本和离线镜像。
- 不连接生产内核、真实设备或不属于你的系统。
- 运行内核测试时使用专用虚拟机或容器，禁止访问宿主机敏感目录。
- Agent 的结论必须引用源码位置、调用路径和测试证据，不能只输出“看起来有漏洞”。

**验收门槛**：完成一个可复现的内核源码审计任务，Trace 中包含源码版本、配置、分析命令、证据位置、测试结果、补丁候选和已知不确定性。不能把静态分析告警直接当成漏洞。

### Phase 8B：WebKit 源码审计专线（第 23-26 周）

WebKit 不是普通的 Web 漏洞题。它包含大型 C++ 代码库、JavaScriptCore、WebCore、渲染流程、进程间通信和沙箱边界，因此需要在内核专线之后学习。

**学习内容**

- C++ 对象生命周期、智能指针、引用计数、类型转换和异常安全。
- WebKit 的 WebCore、JavaScriptCore、网络进程、Web 进程和 GPU 进程边界。
- IPC 消息、序列化/反序列化、权限检查和跨进程信任边界。
- 构建系统、编译数据库、单元测试、布局测试和回归测试。
- Clang 静态分析、CodeQL、AddressSanitizer、UndefinedBehaviorSanitizer 和模糊测试。
- 如何在复杂调用链中追踪输入、状态变化和生命周期风险。

**你亲手输入的文件**

```text
src/saligiare/analysis/cpp_lifetime.py
src/saligiare/analysis/ipc_boundary.py
src/saligiare/benchmarks/webkit/adapter.py
src/saligiare/benchmarks/webkit/evaluator.py
tests/benchmarks/webkit/
docs/benchmarks/webkit-audit.md
docs/research/webkit-architecture.md
```

**建议的任务形态**

```text
固定 WebKit 提交版本
    -> 构建和测试环境检查
    -> 输入来源和跨进程路径追踪
    -> 生命周期 / IPC / 边界假设
    -> 最小测试或回归用例
    -> 修复候选和回归验证
```

**安全边界**

- 优先使用公开源码、离线构建和专用测试夹具。
- 不对真实浏览器用户、生产服务或第三方网站进行测试。
- 浏览器测试进程必须在隔离环境中运行，并限制文件、网络和进程权限。
- 任何输入样本都要标记来源和授权范围，避免把不可信页面内容当成 Agent 指令。

**验收门槛**：完成一个固定 WebKit 版本的源码审计任务，能够展示从输入来源到代码位置的证据链，并通过编译、测试或回归用例验证结论。

### Phase 9：Agent 安全评测（第 27-28 周）

**学习内容**

- 间接提示注入、Confused Deputy、工具输出投毒、数据泄露、授权边界和最小权限。
- 防御评测：误报、漏报、工具可用性影响和绕过尝试。

**你亲手输入的文件**

```text
src/saligiare/security/trust.py
src/saligiare/security/approval.py
src/saligiare/benchmarks/agentdojo/
tests/security/injection/
docs/security/agent-safety.md
```

**验收门槛**：AgentDojo 或等价的已授权测试夹具证明，不可信内容不能改变策略、访问密钥或触发未经批准的能力；同时报告安全性和任务可用性的结果。

### Phase 10：评测平台与独立迭代（持续进行）

**学习内容**

- 实验注册表、回归套件、消融实验、可观测性和工程取舍。
- 如何撰写设计提案、选择架构，以及用证据而不是直觉拒绝一个改动。

**你亲手输入的文件**

```text
src/saligiare/experiments/
src/saligiare/evaluation/registry.py
docs/decisions/
docs/runbooks/
docs/learning-log.md
```

**验收门槛**：一个全新贡献者可以根据文档复现一次 benchmark 实验，并解释每个系统边界存在的原因。

## 每周节奏

| 日期 | 工作 | 必须产出 |
| --- | --- | --- |
| 第 1 天 | 阅读一个窄主题并绘制接口 | 一页设计笔记 |
| 第 2 天 | 编写失败测试 | 聚焦的测试提交 |
| 第 3 天 | 亲手输入最小实现 | 功能提交 |
| 第 4 天 | 审查失败路径和 Trace | 负向测试 / 修复提交 |
| 第 5 天 | 运行本阶段实验 | 实验记录 |
| 第 6 天 | 只重构有证据支持的部分 | 文档 / 清理提交 |
| 第 7 天 | 不看笔记解释设计 | 学习日志和下周 Issue |

## GitHub 与跨电脑工作流

### 一次性初始化仓库

```bash
git init -b main
git add docs/ROADMAP.md
git commit -m "docs: add Saligiare learning roadmap"
git remote add origin <github-repository-url>
git push -u origin main
```

若 GitHub 仓库创建时已包含文件，应先克隆该仓库，而不要在另一个目录运行 `git init`。

### 在任意电脑开始工作

```bash
git switch main
git pull --rebase origin main
git switch -c feat/<small-topic>
```

示例：`feat/task-protocol`、`feat/fake-model`、`docs/chying-analysis`。

如果上一台电脑停留在研究分支或某个功能分支，先确认远程状态，再决定是否继续：

```bash
git fetch origin
git branch -vv
git status --short --branch
```

不要直接在有未提交改动的目录切换分支。先完成提交、推送，或明确保存到 stash；不要用破坏性命令丢弃未理解的改动。

### 完成一个聚焦改动

```bash
python -m pytest -q
python -m ruff check .
git status
git add <specific-files>
git commit -m "feat: <small behavior>"
git push -u origin feat/<small-topic>
```

创建 Pull Request，等待 CI 完成，审查 diff 后再合并至 `main`。

### 学习型提交规则

每个实操单元都遵循以下顺序：

1. 导师先说明本单元目标、文件职责、失败路径和安全边界。
2. 你亲手执行目录/文件创建命令，并在编辑器中逐行输入代码。
3. 你先运行针对本单元的失败测试，再补充最小实现。
4. 你运行完整测试、Ruff 和 `git diff --check`。
5. 你用自己的话回答复盘问题，再创建一个小 commit。
6. 导师只审查你提交的 diff；未通过验收前不扩展到下一个组件。

核心实现、测试和 Git 命令不会由导师在后台替你完成。文档类修改可以由导师根据研究结果直接整理，但涉及学习目标的源码必须由你输入。

### 换电脑后恢复环境

```bash
git fetch origin
git switch main
git pull --rebase origin main
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest ruff
python -m pytest -q
```

PowerShell 激活命令为 `.venv\\Scripts\\Activate.ps1`。

### 防止工作丢失

- 换电脑前，不要让源码改动只停留在未提交的本地目录。
- 每个专注工作时段结束时都推送，即使只是创建 Draft PR。
- 密钥放在被 Git 忽略的 `.env`；每台电脑从 `.env.example` 重建。
- 在 pull、rebase、切换分支或结束工作前都运行 `git status`。
- 理解冲突两边的改动后再解决，不能盲目丢弃任意一边。
- 用 GitHub Issue 记录下一个小任务，每个可审查单元用一个 PR。

## 仓库基础目录

```text
Saligiare/
  .github/workflows/ci.yml
  benchmarks/                 # 锁定的外部说明/夹具，不放密钥
  docker/sandbox/
  docs/
    ROADMAP.md
    research/
    benchmarks/
    experiments/
    decisions/
  src/saligiare/
    agent/
    analysis/
    benchmarks/
    core/
    evaluation/
    models/
    sandbox/
    security/
    tools/
  docs/benchmarks/kernel-audit.md
  docs/benchmarks/webkit-audit.md
  tests/
  .env.example
  .gitignore
  pyproject.toml
  README.md
```

目录职责：

| 路径 | 用途 | 当前阶段是否使用 |
| --- | --- | --- |
| `.github/workflows/` | CI 自动运行测试和 lint，保证另一台电脑或 PR 环境也能验证 | Phase 0 起 |
| `benchmarks/` | 受版本控制的任务样例、适配器夹具和公开协议；不放私有题目或密钥 | Phase 2 以后 |
| `docker/sandbox/` | 隔离执行环境的 Docker 构建文件和固定配置 | Phase 4 以后 |
| `docs/research/` | 参考 Agent、Benchmark 和技术报告的证据型研究笔记 | Phase 1 已使用 |
| `docs/benchmarks/` | Saligiare 自己的 benchmark 适配说明、版本和运行手册 | Phase 6 以后 |
| `docs/experiments/` | 每次实验的模型、Prompt、预算、Trace、结果和限制 | Phase 2 起逐步使用 |
| `docs/decisions/` | 重要架构决策及其证据、替代方案和后果 | Phase 2 起逐步使用 |
| `src/saligiare/core/` | 与具体模型、工具和 benchmark 无关的核心协议 | Phase 2 |
| `src/saligiare/agent/` | Runtime 状态、循环、停止和恢复逻辑 | Phase 2 |
| `src/saligiare/models/` | Fake Model 和未来的模型厂商适配器 | Phase 2/5 |
| `src/saligiare/tools/` | 有类型的工具注册、调用和结构化结果 | Phase 3 |
| `src/saligiare/security/` | Policy Guard、审批、审计和信任边界 | Phase 3/9 |
| `src/saligiare/sandbox/` | Docker、VM、模拟器等隔离执行后端 | Phase 4 |
| `src/saligiare/benchmarks/` | TSECBENCH、CyberGym、CTF 等外部协议适配器 | Phase 6 以后 |
| `src/saligiare/evaluation/` | 可信评测器、指标、报告和实验注册 | Phase 5/6 以后 |
| `src/saligiare/analysis/` | 内核、C/C++、WebKit 等源码分析能力 | Phase 8A/8B |
| `tests/` | 单元、集成、沙箱和安全回归测试 | 每个阶段 |
| `research/` | 被 `.gitignore` 忽略的外部仓库研究副本 | Phase 1 |

## 每次实验必须记录的内容

每次 benchmark 运行都必须在 `docs/experiments/` 或受版本控制的机器可读实验注册表中创建记录。至少包含：

```text
日期和 commit SHA
benchmark 与任务切分
benchmark 版本 / 容器镜像 digest
模型和提供商
提示词版本
可用工具和策略配置
时间、步数、Token 和成本预算
成功指标和结果
Trace 位置
失败、排除项和已知限制
```

不得提交 API Key、Cookie、目标凭证、私有题目材料，或包含密钥的原始 Trace。

## 问题与解决记录

长期有价值的设计疑问、环境阻塞、权限/依赖问题和解决证据统一记录在
[`docs/问题记录.md`](问题记录.md)。低级拼写、路径、重复执行和可以立即纠正的命令错误不强制记录；只有当它暴露出可复用的工程经验时才写入。

## 如何定义真实进展

排行榜声明不是成功定义。只有同时满足以下条件，一个里程碑才算完成：

1. 有已文档化的设计决策。
2. 测试覆盖成功和失败路径。
3. 有一个聚焦且已推送的 Git commit。
4. 有可复现命令或 CI Job。
5. 有用自己语言写成的学习日志解释。
6. 使用了已授权环境，并保留可审计 Trace。

## 下一次工作会话清单

1. 将 `docs/research-agent-architecture` 合并到 `main`，确认远程 `main` 包含全部研究文档。
2. 从最新 `main` 创建 `feat/phase2-task-protocol`。
3. 只完成 Phase 2A：`Task` 协议和对应测试，不提前创建真实 Shell、Docker 或模型 API。
4. 运行本单元测试、完整测试、Ruff 和 `git diff --check`。
5. 写一段学习记录：解释 `Task` 为什么拥有 scope、capability、budget 和 evaluator，而不是只保存自然语言题目。
6. 提交并推送一个小 commit，等待导师审查后再进入 2B `Action`。

## 与导师对话时的提交格式

每次课程结束后，提供：

```text
1. 相关文件树或 diff。
2. 测试 / lint 输出。
3. 如果失败，提供完整错误文本。
4. 对本节复盘问题的答案。
5. 一个你尚未确定的设计决策。
```

下一节将从正确性、安全性、可测试性、可维护性和 benchmark 相关性审查你的工作，确认通过后才引入下一个组件。
