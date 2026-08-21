# Cairn 源码研究笔记

## 研究范围与证据规则

- 项目：<https://github.com/oritera/Cairn>
- 本地研究路径：`research/Cairn/`
- 固定研究提交：`8f702c5f3f9d3163948bd4089edc73980c9c9484`
- 版本：`cairn/pyproject.toml:1-34` 中声明的 `0.2.1`
- 许可证：GNU AGPLv3，见 `research/Cairn/LICENSE`
- 机械研究产物：`/private/tmp/cairn-research/`，其中的 feature registry 已通过验证

本文不复制 Cairn 的源码或 Prompt，只记录可由源码和测试重新验证的架构事实，并将它们映射到 Saligiare 的设计。

每条结论分为：

- **事实**：可以由文件和行号直接验证；
- **推断**：由多个事实组合得出的设计解释；
- **未知**：当前源码范围不能证明的内容。

## 一、全局模型：黑板上的状态空间搜索

### 1. 事实、意图和提示

Cairn 将一个问题表示为 Project，Project 中至少有三类图元素：

| 元素 | 含义 | 是否是事实结论 |
| --- | --- | --- |
| `Fact` | 已确认的客观发现 | 是，但描述内容仍由 Worker 提交 |
| `Intent` | 从已有 Fact 出发的一条待探索方向 | 否，是待执行的计划声明 |
| `Hint` | 人类或外部参与者注入的提示 | 否，属于辅助上下文 |

`Fact`、`Intent`、`Hint` 的 Pydantic 模型分别见 `cairn/src/cairn/server/models.py:13-36`。Intent 还保存 `from`、`to`、`creator`、`worker`、创建时间、心跳时间和结论时间，因此它同时表达因果边、认领状态和生命周期。

创建 Project 时，Server 由代码固定写入 `origin` 和 `goal` 两个 Fact，而不是让 Worker 生成它们，见 `cairn/src/cairn/server/routers/projects.py:77-121`。这是一个重要边界：模型可以探索从 origin 到 goal 的路径，但不能重写任务起点和终点。

### 2. 不是角色树，而是运行时任务图

README 将 Cairn 描述为“从 origin 到 goal 的状态空间搜索”，Worker 不拥有预定义的业务角色，任务根据当前图动态生成，见 `research/Cairn/README.md` 的 What is Cairn / How It Works 部分。

源码中实际固定的是三种**任务类型**，而不是三种领域专家：

```text
bootstrap：项目初始时先直接尝试解决
reason：读取全图，判断完成或生成新的 Intent
explore：认领一个 Intent，执行探索并产出一个 Fact
```

三种任务由调度器分别调用 `run_bootstrap_task`、`run_reason_task` 和 `run_explore_task`，见 `cairn/src/cairn/dispatcher/scheduler/loop.py:20-24` 以及 `:366-545`。

**推断**：Cairn 的“无固定角色”不是“没有结构”，而是把结构从静态 Agent 角色转移到共享图、任务契约和调度状态机。这样一个 Worker 可以在不同轮次承担不同探索方向。

## 二、入口到执行结果的完整链路

### 路径 A：CLI 到 Dispatcher

事实链如下：


1. `cairn` CLI 由 `pyproject.toml:25-28` 映射到 `cairn.cli:main`。
2. `cli.py:11-14` 创建 Click 命令组。
3. `serve` 命令在 `cli.py:16-39` 配置 SQLite 路径并启动 Uvicorn/FastAPI。
4. `dispatch` 命令在 `cli.py:42-67` 加载配置、创建 `DispatcherLoop`，然后运行持续循环或单轮调度。
5. `DispatcherLoop.__init__` 在 `scheduler/loop.py:43-66` 创建 `CairnClient`、容器/本地后端、线程池、任务状态和心跳相关缓存。
6. `DispatcherLoop.run` 在 `scheduler/loop.py:80-110` 每轮读取项目摘要、初始化检查点、取消非 active 任务、排队清理并派发任务。

```text
cairn serve / dispatch
    -> FastAPI Server + SQLite
    -> DispatcherLoop
    -> list_projects / get_project / export_project
    -> 选择 bootstrap、reason 或 explore
    -> Worker Driver
    -> 解析结构化 JSON
    -> CairnClient 写回协议
```

### 路径 B：Server 是协议真相源

FastAPI 应用注册 settings、projects、hints、intents、export 路由，见 `cairn/src/cairn/server/app.py:21-40`。Server 负责：

- Project、Fact、Intent、Hint 的持久化；
- Fact ID、Intent ID 和时间戳的分配；
- Fact 引用是否存在的校验；
- Intent 的 claim、heartbeat、release、conclude；
- Project 级 `reason` lease；
- Project 的 active/stopped/completed 状态。

例如，创建 Intent 时，Server 会先检查项目 active、来源 Fact 存在、来源不能包含 goal、creator/worker 关系合法，然后才插入数据库，见 `cairn/src/cairn/server/routers/intents.py:28-71`。结论接口会由 Server 创建新的 Fact，并把 Intent 的 `to` 设置为该 Fact，见 `intents.py:118-147`。

**推断**：Dispatcher 是“唯一协议写入者”，但 Server 才是最终一致性和状态转换的控制点。即使 Worker 或 Dispatcher 出现竞态，Server 仍能通过 403/409 和引用校验拒绝非法写入。

### 路径 C：调度器如何选择任务

`_try_dispatch_project` 的顺序见 `scheduler/loop.py:254-338`：

1. 项目必须 active，且不能有待清理容器；
2. 达到项目并发上限则跳过；
3. 初始项目优先走 bootstrap；没有 bootstrap 条件时走 reason；
4. 非初始项目在出现新 Fact、Hint 或 open Intent 清空等新态势时走 reason；
5. 有未认领 Intent 时选择最新 Intent 走 explore；
6. 没有图变化且已有 reason lease 时不重复派发。

Worker 选择在 `scheduler/loop.py:547-570` 之后继续完成：先按 task type、并发上限、不健康冷却和 rejected 冷却过滤，再按 priority、当前运行数和随机因素选择 Worker。

**值得学习的点**：Cairn 没有每轮都强制调用模型。它用事实数量、提示数量和 open Intent 数量的检查点抑制无变化的 reason 调用，减少空转和成本。

### 路径 D：Worker 结果如何落图

Dispatcher 不让 Worker 直接调用 Cairn API。研究设计文档明确写出，Worker 只接收 Prompt、在项目容器内执行 CLI、返回结构化 JSON，Dispatcher 再代为写回协议，见 `research/Cairn/docs/specs/dispatcher-design.md:7-14` 和 `:81-95`。

三类结果的处理逻辑：

- `reason`：解析为 `complete`、`intents`、`noop` 或 `rejected`；代码调用 `complete` 或逐个 `create_intent`，见 `tasks/reason.py:176-281`；
- `explore`：解析为一个 Fact 描述，再调用 `conclude`，见 `tasks/explore.py:142-232`；
- `bootstrap`：主阶段必须同时给出 Fact 和 complete，先 conclude 再 complete；见 `tasks/bootstrap.py:136-188`。

输出契约集中在 `dispatcher/contracts.py:62-170`：

- `accepted=false` 表示 Worker 拒绝任务；
- `accepted=true` 时必须有字典型 `data`；
- `reason` 限制 Intent 数量，并禁止同时返回 complete 和 intents；
- `explore` 只接受一个非空 `description`，不能把“我还要继续分析”当作事实；
- `bootstrap` 要求 `fact.description` 和 `complete.description` 都是非空字符串。

**关键结论**：Cairn 的可信边界不是模型输出 JSON 本身，而是“Dispatcher 解析 JSON + Server 验证引用和状态 + 评测/运行环境观察结果”。不过 Fact 的描述文本仍可能是模型的未经证明的叙述，Cairn 本身没有自动验证安全事实的机制。

## 三、任务与状态机

### 1. Bootstrap：先做一次直接尝试

初始 Project 只有 `origin`、`goal` 时，Dispatcher 创建一个保留的 bootstrap Intent，约定为 `description="bootstrap"`、`creator="dispatcher.bootstrap"`、`from=["origin"]`，见 `scheduler/loop.py:30-31`、`:340-364` 和 `:647-702`。

Bootstrap 主阶段超时或输出不合规时，若 Driver 支持 session/conclude，会进入第二阶段总结。第二阶段只允许产出 Fact，不允许自报 complete；这一点在 `tasks/bootstrap.py:234-288` 和契约校验函数中体现。

**设计价值**：简单问题不必先花一轮 reason 拆解；但即使直接解决，也要通过保留 Intent 和 Fact 协议落图，避免产生一条不可审计的旁路。

### 2. Reason：对全图做一次判断

Reason 读取完整 graph YAML、合法 Fact ID 和 open Intent 列表，见 `tasks/reason.py:83-115`。它可以：

- 返回 `complete`，由代码调用 `/complete`；
- 返回一个或多个 Intent，由代码调用 `/intents`；
- 返回 no-op；
- 返回 rejected 或非法结果，任务作废。

Reason 本身不是“执行工具”的阶段，而是“决定下一步搜索方向”的阶段。它有 Project 级 lease，Server 路由 `projects.py:191-254` 保证同一 Project 同时只有一个 reason worker。

### 3. Explore：一次只执行一个 Intent

Explore 在派发前通过 `POST /projects/{project_id}/intents/{intent_id}/heartbeat` claim Intent，见 `scheduler/loop.py:488-545`。执行中由 `HeartbeatLease` 按 interval 维持 claim，任务完成时用 `conclude` 写入一个 Fact。

Explore 的 fallback 允许同一 session 进入 conclude 阶段，但只有项目仍 active、heartbeat 未丢失、任务未被取消且 Driver 支持 conclude 时才可进入，见 `tasks/explore.py:241-288`。

**推断**：这是一种“单 Intent、单结论”的窄接口。它降低了多 Worker 同时写一大片自由文本的并发复杂度，也让每条 Fact 都有明确的来源 Intent。

## 四、Worker 适配器与执行后端

### 1. Driver 抽象

`WorkerDriver` 把不同 CLI 的差异压缩成 `check_health`、`build_execute`、`build_conclude`、session 提取和响应文本提取，见 `dispatcher/workers/base.py:18-55`。注册表目前包含 Claude Code、Codex、Pi 和 Mock，见 `workers/registry.py:7-29`。

这说明 Cairn 的“多模型”主要是命令/会话适配，不是把模型推理逻辑写死在 Dispatcher 中。Mock Driver 让测试可以不依赖真实模型。

### 2. 容器模式

容器后端按 Project 创建或复用一个容器，容器命名、生命周期和清理见 `runtime/containers.py:19-72`、`:93-170`。Worker 进程通过 Docker exec 启动，命令前可加 timeout，见 `containers.py:175-195`；输出流、超时、退出码和 kill 由 `runtime/process.py:44-205` 处理。

配置模型允许指定镜像、网络模式、完成后 stop/remove 和额外 Linux capabilities，见 `dispatcher/config.py:153-158`。

### 3. Local 模式

Local 模式复用宿主机已经登录的 `claude`、`codex` 或 `pi` CLI，不注入 API Key；启动时只检查 CLI 是否存在和可运行，见 `scheduler/loop.py:118-189`。示例配置明确提醒：Local worker 以用户权限运行且没有沙箱，见 `dispatch.local.example.yaml:1-14`。

这对开发体验很方便，但不能成为 Saligiare 的默认执行后端。

## 五、持久化、并发和可恢复性

### 1. Claim 与 heartbeat

Intent claim、release 和 reason lease 都通过 Server API 进行。`HeartbeatLease` 在独立线程中定期发送 heartbeat；收到 403/409 立即失败，普通网络错误允许两倍 interval 的宽限期，失败后会 kill 关联进程，见 `runtime/heartbeat.py:23-123`。

**值得学习的点**：心跳不是单纯的“在线指标”，而是执行权租约。租约失效时终止进程，可以避免一个已经失去协议所有权的 Worker 继续写入或消耗资源。

### 2. Session 与文件快照

Dispatcher 会为 Prompt 中的大图快照在容器内写入临时 YAML 文件，只向 Worker 提供文件位置和“先读完整文件”的指令，见 `tasks/common.py:56-70`。这避免把不断增长的完整图直接复制到每条 Prompt 中。

**注意**：这不是完整的上下文压缩。图快照文件仍然可能很大，且 Worker 读取的内容来自 Server/项目数据，Saligiare 需要额外限制大小、字段和不可信指令传播。

### 3. 测试证据

测试用 Mock Worker 覆盖了：

- bootstrap 直接完成；
- reason -> explore -> reason -> complete 链路；
- 非法 JSON、非法 payload、Intent 数量上限；
- 本地进程超时和取消；
- Server API 的状态与迁移。

端到端 Mock 流程见 `cairn/tests/test_mock_end_to_end.py:292-351`；契约测试见 `cairn/tests/test_contracts_and_drivers.py:16-55`；本地执行和取消测试见 `cairn/tests/test_local_execution.py`。

## 六、安全审计：可以借鉴什么，不能误判什么

### 1. Worker 输出仍然是不可信数据

`contracts.py` 只验证结构、必需字段和数量，不验证 Fact 描述是否真实。比如一个 Worker 可以返回“已经拿到 root shell”的字符串，只要格式合法，Dispatcher 就可能把它写成 Fact。`reason` 返回 complete 时，`projects.py:257-300` 会直接把给定描述写入完成 Intent 并把项目置为 completed。

**对 Saligiare 的要求**：

- `Result` 中区分模型叙述、工具证据、评测器 verdict 和人工确认；
- 不能把模型描述直接转换为“漏洞已复现”“已获得权限”或“Flag 正确”；
- 每种 benchmark 必须有 Trusted Evaluator。

### 2. Claude Driver 使用高风险权限参数

Claude Code Driver 构造命令时加入 `--dangerously-skip-permissions`，见 `workers/adapters/claudecode.py:38-61`。这与 CHYing-agent 中的 `bypassPermissions` 有相同的学习价值和风险：它改善无人值守流程，但把安全责任推给外层环境和 Prompt。

**Saligiare 决策**：拒绝直接复制。我们的 Agent Runtime 必须通过类型化 Tool Registry 和默认拒绝的 Policy Guard 控制动作，模型不能因为“任务是安全研究”而自动获得宿主机权限。

### 3. 容器设置不等于完整沙箱

示例配置默认使用 `network_mode: "host"`，见 `dispatch.example.yaml:43-52`；代码还允许显式增加 Linux capabilities，见 `dispatcher/config.py:153-158`。当前研究没有证明镜像内部一定以非 root 运行、没有证明文件系统挂载策略，也没有证明宿主机 Docker socket 的最小权限。

这些属于**未知或部署依赖**，不能从“使用 Docker”推断为安全隔离。

### 4. Local 模式是明确的宿主机高权限模式

项目自己的配置说明已经承认 Local worker 没有沙箱并使用用户权限，见 `dispatch.local.example.yaml:11-14`。这可以作为个人学习和调试模式，但不适合作为 TSECBENCH、CVE 复现、内核或 WebKit exploit 验证的默认后端。

### 5. API 认证边界需要部署审查

在本次检查的 FastAPI `app.py:21-40` 和项目/Intent 路由中，没有看到统一认证依赖；配置中的 `server` 是可配置 URL。仅凭这些文件不能断言生产部署一定无认证，因为反向代理或网络边界可能承担认证，但 Server API 不能被默认视为可信内部网络。

**Saligiare 决策**：Server、Dispatcher、Evaluator 和 Worker 之间要有显式身份、任务级 token 或本地 Unix socket 边界；不能只依靠“端口没有暴露”。

### 6. 知识图并不等于知识库可信

Cairn 的 Fact 图非常适合作为研究过程的共享状态，但它没有为事实来源、证据文件、授权范围、版本哈希和置信度建立一等字段。Fact 描述可以是模型生成的自然语言。

**Saligiare 决策**：借鉴图结构，但把 `Evidence`、`Source`、`Confidence`、`AuthorizationScope` 和 `EvaluatorVerdict` 分开建模，不让知识库内容改变工具权限。

## 七、对 Saligiare 的采用决策

下表是“偷模式，不复制平台”的映射。当前 Saligiare 只有 Phase 0 基础和计划中的接口，因此 `gap` 表示路线中应实现但现在还没有。

| Cairn 能力/取舍 | Saligiare 当前对应面 | 决策 | 原因 |
| --- | --- | --- | --- |
| Fact/Intent/Hint 黑板图 | `docs/ROADMAP.md` 中的 `Task`、`Observation`、`Result` 计划 | **steal** | 用作可恢复的探索图，但增加证据和可信度字段 |
| Dispatcher 代 Worker 写协议 | 计划中的 Agent Runtime + Policy Guard | **steal** | 模型只提出动作，确定性代码校验和授权 |
| 三种动态任务：bootstrap/reason/explore | 尚无实现 | **steal** | 可作为 CTF 和源码审计的最小状态机，而不是固定专家角色 |
| Server 负责状态一致性 | 计划中的 `Trusted Evaluator` / Trace Store | **steal** | 把状态转换和结果判定从模型中移出 |
| Driver 适配 Claude/Codex/Pi/Mock | 计划中的 Model Adapter | **steal** | 复用适配器思想，不复制命令行参数和权限模式 |
| Mock Driver + 端到端测试 | `tests/` 目前只有 smoke test | **gap** | Phase 2 必须先建立确定性 Fake Model 和 Fake Runtime |
| Claim + heartbeat lease | 尚无实现 | **steal** | 适合长时间任务、跨电脑恢复和并发防重入 |
| 每项目一个容器 | 计划中的 Sandbox Backend | **park** | 作为一种后端，不把容器默认等同完整隔离 |
| Local 宿主机执行 | 尚无安全等价物 | **reject as default** | 只允许显式开发模式，不能作为 benchmark 默认后端 |
| `--dangerously-skip-permissions` | 计划中的 Policy Guard | **reject** | 与默认拒绝、能力白名单原则冲突 |
| 模型直接提交 Fact 描述 | 计划中的 Trusted Evaluator | **reject** | 事实文本必须与工具证据和评测 verdict 分离 |
| 全图 YAML 快照写入容器 | 计划中的 Trace/Context Store | **steal with redesign** | 借鉴快照引用，但限制大小、版本、字段和注入风险 |
| 预定义领域专家 Agent | 当前能力蓝图的多模式设计 | **park** | 先用能力计划和工具域分区，后期才添加内核/WebKit/Android 专家 |

## 八、与 Saligiare 能力蓝图的映射

### 竞赛和普通 CTF

Cairn 的 `bootstrap -> reason -> explore` 很适合普通 CTF：

```text
origin/附件
    -> bootstrap：快速侦察或直接尝试
    -> reason：根据已验证观察提出探索 Intent
    -> explore：一次执行一个具体方向
    -> Fact：端口、文件、协议、漏洞线索或 Flag 证据
    -> Trusted Evaluator：确认答案/Flag
```

Saligiare 不能照搬“任何合法 Fact 都能推进 goal”。CTF 的 Flag、任务范围和成功条件必须由 benchmark adapter 注入。

### CVE 复现和漏洞研究

可将 Intent 具体化为“验证假设”，而不是泛泛的自然语言任务：

```text
Fact：固定版本、补丁差异、输入来源
Intent：运行最小复现测试
Fact：崩溃栈/行为差异/版本哈希
Intent：在修复版本运行回归测试
Fact：修复前后对比
```

这能把“疑似漏洞”“已复现”“已证明可利用”拆成多个证据节点。利用验证仍必须在批准的 VM、模拟器或靶场后端执行。

### Linux/Android 内核和 WebKit

Cairn 的共享图适合表示大型源码研究的证据链，但“无固定角色”不能完全替代能力隔离。Saligiare 应使用：

```text
source-audit：只读源码、调用图、数据流
    -> build-test：编译、Sanitizer、回归
    -> exploit-validate：只在批准 VM/模拟器/浏览器夹具执行
```

每个 Agent 都可以向同一个 Evidence Graph 写入结果，但不同能力的 Tool Registry 和 Policy Guard 必须独立。

### Android App 和企业 SRC

Cairn 的项目级 scope 很适合作为 SRC 任务的起点，但必须扩展为：域名/IP/API 范围、速率、时间窗、禁止项、凭证级别和人工审批状态。网页、APK、错误响应和知识库内容都只能作为不可信 Observation，不能扩展 scope。

### 知识库

Cairn 的 Fact 图可以成为知识库的一种过程视图，但长期知识条目还需要：

- 来源 URL、源码提交或镜像 digest；
- 授权范围和脱敏状态；
- 复现命令与环境；
- 证据附件和 Trace ID；
- 修复版本与回归结果；
- 人工审查和置信度。

## 九、Saligiare 应吸收的接口草案

这不是让用户现在实现的代码，而是研究后的接口约束。后续 Phase 2/3 由用户亲手输入最小版本。

```text
Task
  task_id
  mode
  scope                 # 可信注入，不可由模型改写
  origin / goal         # 可信注入
  allowed_capabilities  # 可信注入
  evaluator_id          # 可信注入
  budget

EvidenceGraph
  facts                 # 事实描述 + 证据引用 + 来源 + 置信度
  intents               # 假设/探索方向 + 来源 fact ids
  observations          # 原始工具结果，默认不可信
  hints                 # 人工提示，需标记来源

Action
  tool_name
  typed_arguments
  intent_id

Result
  model_summary
  evidence_refs
  evaluator_verdict
  status                # success / rejected / timeout / failed
```

核心流程应保持：

```text
模型提出 Action
    -> Policy Guard 校验 Task scope、能力、参数和预算
    -> Sandbox 执行
    -> Observation 写入 Trace
    -> Evaluator 产生 verdict
    -> 代码决定是否写入 Evidence/Fact
```

这比直接让模型返回 `fact + complete` 多一层，但也是 Saligiare 支持 CVE、内核、WebKit 和 SRC 时避免自报成功的必要代价。

## 十、研究结论

### 应采用

1. 黑板式 Evidence Graph：让多个 Worker 通过共享状态协作，而不是互相传递不可审计的长文本。
2. Dispatcher/Runtime 作为唯一协议写入者：模型只返回结构化候选动作或结论。
3. 动态的 `bootstrap/reason/explore` 任务状态机：减少固定角色和无变化轮询。
4. Claim、heartbeat、取消和资源清理：支持长任务与跨电脑恢复。
5. Driver + Mock Driver：把模型供应商差异隔离，并在无 API Key 时做端到端测试。
6. 任务级并发上限和新态势检查点：控制成本和竞态。

### 不能直接采用

1. `--dangerously-skip-permissions` 或任何默认允许模型执行任意动作的模式。
2. Local 宿主机执行作为默认 benchmark 或漏洞验证后端。
3. `network_mode: host` 作为通用安全默认值。
4. 把结构合法的模型 Fact 当成漏洞、权限提升或 Flag 已验证。
5. 把 Cairn 的 AGPLv3 源码、Prompt 或实现直接复制到 Saligiare；只能学习并重新实现接口思想，并遵守许可证边界。

### 仍需进一步验证

- Worker 容器镜像的实际用户、挂载、文件系统和 Docker socket 权限；
- Server 部署时是否由反向代理提供认证；
- 大型图快照在长期任务中的大小上限和敏感数据脱敏策略；
- 多 Dispatcher 并发部署是否被明确禁止并由部署层保证；
- Cairn 的真实比赛配置与公开复盘中哪些参数对结果最关键。

## 复盘结论（本轮直接确认）

本轮不要求额外问答，基于已达成的能力蓝图，直接形成以下 Saligiare 决策：

1. Saligiare 借鉴 Cairn 的图搜索和 Dispatcher/Worker 分离，但增加 `Policy Guard`、`Sandbox` 和 `Trusted Evaluator`。
2. `Fact` 不再等于“模型说它是真的”，而必须区分 Observation、Evidence、Evaluator Verdict 和人工确认。
3. 内核、Android 内核和 WebKit 任务可以共享 Evidence Graph，但源码读取、构建测试和利用验证使用不同能力域与后端。
4. 下一份参考研究是 TCH 比赛复盘，用来验证 Cairn 的通用图搜索在真实竞赛中的任务拆分、失败恢复和资源取舍。
