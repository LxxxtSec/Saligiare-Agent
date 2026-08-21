# Saligiare 学习路线图

## 项目目的

Saligiare 是一个面向**授权本地 benchmark 环境**的安全 Agent 运行时。
项目的目标不是宣称一个 Agent 必然通过所有 benchmark，而是亲手构建、理解、评测并持续改进一个 Agent：它能在可复现环境中执行任务，同时让工具调用、权限和结果都可审计。

主要目标 benchmark 是 TSECBENCH Local。Cybench、InterCode-CTF、CyberGym、CyberSecEval 和 AgentDojo 是补充评测目标。

这是一个学习优先的项目。你亲手输入实现代码；导师在每个阶段提供小步设计、代码骨架、测试要求、复盘问题和代码审查反馈。

## 工作原则

1. 只在已授权的本地环境、benchmark 容器和故意存在漏洞的靶场中工作。
2. 在引入框架前，先实现最小且正确的组件。
3. 每项行为在被后续代码依赖前，都必须有测试。
4. 模型只能提出动作；确定性代码负责校验和授权。
5. benchmark 的特有细节必须放在适配器中，不能污染 Agent 核心。
6. 每次实验要保存模型、提示词、工具、限制、Trace 和结果，以便复现。
7. 每个小而聚焦的 Git commit 都必须让项目保持可运行。

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

## 项目阶段

以下进度按每周投入 8-12 小时估算。只有取得列出的证据后才能进入下一阶段。一个阶段可以延长，但不可跳过验收门槛。

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

**验收门槛**：为每个 Agent 画出 `观察 -> 决策 -> 工具 -> 观察` 的循环，并写出停止条件和缺失的安全控制。

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

### Phase 9：Agent 安全评测（第 19-20 周）

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
    benchmarks/
    core/
    evaluation/
    models/
    sandbox/
    security/
    tools/
  tests/
  .env.example
  .gitignore
  pyproject.toml
  README.md
```

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

## 如何定义真实进展

排行榜声明不是成功定义。只有同时满足以下条件，一个里程碑才算完成：

1. 有已文档化的设计决策。
2. 测试覆盖成功和失败路径。
3. 有一个聚焦且已推送的 Git commit。
4. 有可复现命令或 CI Job。
5. 有用自己语言写成的学习日志解释。
6. 使用了已授权环境，并保留可审计 Trace。

## 第一次工作会话清单

1. 在 GitHub 创建名为 `Saligiare` 的私有仓库。
2. 按 Phase 0 建立 Python 项目和 CI。
3. 使用 `docs: add Saligiare learning roadmap` 提交本路线图。
4. 验证新克隆目录能安装依赖并运行 smoke test。
5. 创建 GitHub Issue：`research: map CHYing-agent runtime`。
6. 从 Phase 1 开始，只写项目结构图，不执行安全代码。

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
