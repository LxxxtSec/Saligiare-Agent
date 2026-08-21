# CHYing-agent 源码研究笔记

## 研究范围

- 项目：<https://github.com/yhy0/CHYing-agent>
- 本地研究路径：`research/CHYing-agent/`
- 研究提交：`0d2ee81`（仓库当前浅克隆的 `main`）
- 许可证：MIT，见 `research/CHYing-agent/LICENSE`
- 本笔记用途：学习架构和工程取舍，不复制项目代码

本文区分三类内容：

```text
源码事实：可以由文件和函数直接验证
分析判断：根据调用关系得出的解释
Saligiare 建议：我们自己的设计决定
```

## 一、先看全局：它不是一个单循环 Agent

CHYing-agent 的核心不是“模型收到 Prompt 后不断调用 Shell”这一条简单循环，而是多层系统：

```text
命令行入口 main.py
    -> 任务/平台模式选择
    -> challenge_solver.solve_single_challenge()
    -> 目标解析、分类、工作目录和自动侦察
    -> PromptCompiler（首次任务）
    -> ClaudeOrchestrator（主会话）
       -> Task / AgentDefinition 调度子 Agent
          -> executor：命令、脚本、PoC
          -> browser：浏览器和页面交互
          -> reverse：Ghidra 和逆向分析
          -> c2：后渗透和 C2（配置可开关）
    -> 结构化结果、Flag 提取、数据库记录和 Writeup
    -> compact / 重试时的 ProgressCompiler 或 RetryHandoffCompiler
```

### 关键证据

- `main.py:268` 定义 CLI `main()`，支持 `--ctf`、`--target`、`--platform`、多目标和 Dashboard 模式。
- `main.py:126` 的 `run_targets()` 将 URL 转为虚拟 challenge，并调用 `solve_single_challenge()`。
- `chying_agent/challenge_solver.py:1231` 是单题任务的主要编排函数。
- `chying_agent/brain_agent/claude_advisor.py:40` 定义 `ClaudeOrchestrator`。
- `chying_agent/brain_agent/claude_advisor.py:227` 开始定义内建子 Agent。
- `chying_agent/claude_sdk/base.py:313` 定义所有 Claude SDK Agent 共用的 `BaseClaudeAgent`。

## 二、入口和任务生命周期

### 1. CLI 入口

`main.py` 先解析参数，再执行启动检查和数据库初始化，最后根据互斥参数选择运行模式：

```text
解析参数
    -> --skip-preflight 之外执行 run_preflight_checks()
    -> init_db()
    -> 判断只选择了一种模式
    -> asyncio.run(...) 启动对应 runner
```

`main.py` 的运行模式包括：

- 自动检测 `agent-work/ctf/` 的 CTF 模式；
- `-t/--target` 单目标或多 URL 模式；
- `--web/--pwn/--reverse/...` 多目标模式；
- `--platform` 平台爬取、启动场景、解题和提交；
- `--dashboard` Web Dashboard。

### 2. 单题任务

`solve_single_challenge()` 的主要阶段如下：

1. 设置 challenge context 和当前工作目录。
2. 规范化题目类别。
3. 创建或恢复题目工作目录。
4. 如果检测到历史执行记录，尝试先运行 `RetryHandoffCompiler`。
5. 创建数据库 `ExecutionContext`。
6. 对 URL 目标执行轻量 HTTP recon 和 httpx 指纹识别。
7. 组装文件信息、历史知识、重试历史和认证环境变量名。
8. 首次执行时运行 `PromptCompiler`，形成结构化上下文。
9. 创建 `ClaudeOrchestrator`，将最终上下文交给主会话。
10. 在任务超时、取消、用户中断或异常时写入结果和执行摘要。
11. 处理结构化输出、Flag、成功状态、数据库记录和后续 Writeup。

### 关键证据

- `challenge_solver.py:1231-1300`：上下文初始化、工作目录和重试准备。
- `challenge_solver.py:1310-1450`：执行记录、自动侦察和历史知识。
- `challenge_solver.py:1455-1530`：PromptCompiler 和类别修正。
- `challenge_solver.py:1535-1635`：Orchestrator 创建、会话轮转、分支探索和任务级 timeout。

## 三、主 Agent：Orchestrator

### 1. 初始化

`ClaudeOrchestrator` 继承 `BaseClaudeAgent`，使用：

- 持久会话模式：`persistent_session=True`；
- 最大轮数：默认 `MAX_TURNS=30`；
- Claude Code 工具预设：`use_claude_code_preset=True`；
- Hook：开启；
- SDK 沙箱：开启；
- 本地绑定：默认允许；
- 可选双模型轮换：`LLM_MODEL_ALT`；
- 项目配置源：`setting_sources=["project"]`。

证据：`chying_agent/brain_agent/claude_advisor.py:67-146`。

### 2. 工具控制

Orchestrator 的 `DISALLOWED_TOOLS` 禁用了 Web 搜索、WebFetch、用户问答、计划模式、Worktree、Cron 和 Notebook 等工具，理由主要是节省上下文并避免在比赛中直接搜到题解。

值得注意的是：

```python
def _get_allowed_tools(self) -> List[str]:
    return []
```

这不是严格的“只允许空工具列表”。在该项目的 Hook 语义中，空列表代表跳过白名单检查，实际控制主要依赖 `disallowed_tools` 和 SDK 权限模式。

证据：`claude_advisor.py:43-65`、`claude_advisor.py:151-160`。

### 3. 子 Agent 定义

`_get_agents()` 通过 Claude SDK `AgentDefinition` 定义专用子 Agent：

| 子 Agent | 主要职责 | 典型工具边界 |
| --- | --- | --- |
| `executor` | Kali/Docker 中执行命令、脚本、PoC 和批量测试 | Read、Glob、Grep、Write、Edit、`mcp__chying__exec`、记录发现 |
| `browser` | 页面导航、DOM 操作、网络请求和 Cookie/Session 观察 | Read、Chrome DevTools MCP、记录发现、WSS 工具 |
| `reverse` | 逆向、反编译、字符串、交叉引用和 Exploit 辅助 | Ghidra MCP、`mcp__chying__exec`、记录发现 |
| `c2` | Metasploit、tmux、后渗透、权限提升和横向移动 | 配置开关开启时提供执行和记录工具 |

每个子 Agent 有自己的：

- `description`：告诉主 Agent 何时委派；
- `prompt`：专用系统指令；
- `tools` 或 `disallowedTools`：工具边界；
- `maxTurns`：子任务轮数上限；
- `model="inherit"`：继承主 Agent 模型。

证据：`claude_advisor.py:227-370`，以及 `agents/executor_agent.py`、`agents/browser_agent.py`、`agents/reverse_agent.py`、`agents/c2_agent.py`。

## 四、MCP 可见性：这份代码最值得学习的设计

`agent-work/.mcp.json` 将外部 MCP 服务器标记为：

```json
{
  "chrome-devtools": {"visibility": "subagent:browser"},
  "ghidra-mcp": {"visibility": "subagent:reverse"}
}
```

这意味着主 Orchestrator 可以知道有 `browser` 和 `reverse` 子 Agent，但不直接看到 Chrome DevTools 或 Ghidra 的全部工具定义。

作用有两个：

1. 降低主 Agent 上下文中工具描述的数量；
2. 减少主 Agent 绕过委派、自己操作专用工具的倾向。

这是“工具可见性控制”，不是完整的安全授权系统。真正的权限仍需要在工具执行层再次验证。

### Saligiare 的学习结论

Saligiare 后期可以采用类似的能力分区：

```text
orchestrator
    -> source-audit（只读源码、调用图、静态分析）
    -> build-test（构建、测试、Sanitizer）
    -> terminal（受限命令执行）
    -> browser（只在浏览器测试夹具中）
```

但不能只因为 Agent 看不到工具，就认为它没有权限。真正执行动作的工具 Registry 和 Policy Guard 必须再次检查。

## 五、BaseClaudeAgent：通用运行时抽象

### 1. 统一入口

`BaseClaudeAgent` 把各类 Agent 的共同能力集中起来：

- 模型和 API 配置；
- Prompt 和工作目录；
- MCP Server 配置；
- allowed/disallowed tools；
- AgentDefinition；
- Hook；
- 持久会话和 session resume；
- 结构化输出；
- 预算、fallback model 和双模型轮换；
- 沙箱选项；
- 工具调用、Token、成本和子 Agent 映射的观测。

它要求子类实现 `_get_mcp_servers()`、`_get_allowed_tools()` 和 `_get_agent_type()`，并允许覆盖 `_get_agents()`、`_get_disallowed_tools()`、`_get_output_schema()`。

证据：`claude_sdk/base.py:313-583`。

### 2. Session 管理

Base 类维护 `thread_id -> session_id` 的 LRU 映射，并在会话恢复时使用 SDK 的 `resume`。这说明项目把“同一个题目的连续工作”与“新的题目”区分开，避免错误恢复到最近的其他任务。

证据：`claude_sdk/base.py:431-552`。

### 3. Options 构建

`_build_options()` 将以下内容组合成 SDK 配置：

```text
system_prompt
工具预设
允许/禁止工具
max_turns
cwd
hooks
permission_mode
resume session
MCP servers
子 Agent definitions
structured output schema
sandbox
```

证据：`claude_sdk/base.py:1870-2002`。

## 六、执行器和 MCP 工具

`mcp_tools.py` 中的 `exec_tool()` 会把 Agent 的命令交给全局配置管理器的 Executor；Executor 有 Local、Docker Native 和 Python Wrapper 等实现。

```text
MCP exec tool
    -> ConfigManager.executor
    -> ExecutorFactory
       -> DockerExecutor / LocalExecutor / DockerPythonExecutor
    -> stdout / stderr / exit code
```

证据：

- `claude_sdk/mcp_tools.py:504-635`；
- `executor/base.py`；
- `executor/docker_native.py`；
- `executor/local_executor.py`；
- `runtime/singleton.py:17-74`。

项目还将 `record_key_finding` 结果写入任务目录的 `findings.log`，对 source 字段做 allowlist 和长度限制；这是一种让后续 Agent 读取“指针型证据”而非整段大输出的设计。

证据：`claude_sdk/mcp_tools.py` 中 `_sanitize_source()` 和 `_append_key_finding_markdown()`。

## 七、PromptCompiler、ProgressCompiler 和 RetryHandoffCompiler

### PromptCompiler：任务前置编译

`PromptCompiler` 是一个无工具、`max_turns=1` 的轻量 Agent。它将原始题目描述、目标、侦察结果、历史知识和用户提示整理成结构化 XML 片段，供 Orchestrator 使用。

```text
原始任务资料
    -> PromptCompiler
    -> 结构化上下文和可能的类别修正
    -> 代码重新注入不可丢失的 metadata
    -> Orchestrator
```

关键点是：`_build_compiled_context()` 由代码重新拼装 challenge metadata，不完全信任 Compiler 的文本输出。

证据：`brain_agent/prompt_compiler.py:1-100`、`challenge_solver.py:1455-1530`。

### ProgressCompiler：上下文压缩后的接班简报

当 SDK/CLI 发生 compact 时，项目异步启动 `ProgressCompiler`，把工作目录中的进度文件和日志编译成 `compact_handoff.md`，由 recovery Hook 指示主 Agent 读取。

目标是防止：

```text
上下文变满
 -> Agent 自己写大量日志
 -> 日志膨胀
 -> compact 后重新读取又占满上下文
```

证据：`claude_sdk/base.py:978-1015`、`brain_agent/progress_compiler.py`、`claude_sdk/hooks.py:201-220` 和 `1054-1074`。

### RetryHandoffCompiler：跨任务重试的接班报告

检测到历史执行摘要时，`solve_single_challenge()` 先生成 `retry_handoff.md`，然后清理已被报告吸收的膨胀日志，保留可复用证据。

证据：`challenge_solver.py:1270-1300`、`brain_agent/retry_handoff_compiler.py`。

## 八、持久化、观测和结果

项目同时使用多种状态载体：

| 状态 | 作用 |
| --- | --- |
| Claude SDK session | 继续同一模型会话 |
| 题目工作目录 | `progress.md`、`findings.log`、`hint.md`、PoC 和输出 |
| SQLite/SQLAlchemy | Challenge、Execution、Discovery、Writeup 和成本统计 |
| 日志和 Trace | 工具调用、子 Agent、错误、Token 和耗时 |
| Writeup | 任务完成后的复盘产物 |

`ExecutionContext` 在单题开始时建立执行记录，在退出时写入成功、失败、超时或取消结果。`observability.py` 和数据库模块还支持 Token、成本和 Dashboard 查询。

## 九、错误处理和停止条件

CHYing-agent 至少有这些停止/降级边界：

- CLI 参数互斥检查；
- preflight 检查失败；
- 单题任务级 timeout，默认来自 `SINGLE_TASK_TIMEOUT`；
- Orchestrator `max_turns`；
- 子 Agent `maxTurns`；
- 最大 session rotations；
- 目标不可达时快速失败；
- 进程内重试次数 `MAX_RETRIES`；
- 用户中断、取消和异常的结果记录。

注意：结构化输出中的 `success/solved` 只是 Agent 结果的一部分，最终仍由上层结果处理和 Flag/评测逻辑判断，不能把自然语言“成功”当成可信证据。

## 十、安全审查：哪些设计不能直接照搬

### 1. `bypassPermissions` 风险

`BaseClaudeAgent._build_options()` 设置：

```python
"permission_mode": "bypassPermissions"
```

这适合比赛无人值守和已知靶场，但意味着 SDK 层跳过交互式权限提示。对于 Saligiare，必须由外部 Policy Guard 在调用工具前做确定性授权，不能把“模型运行在授权比赛里”当成足够的权限控制。

### 2. 默认偏向黑名单

Orchestrator 返回空的 allowed list，主要使用 disallowed list。随着工具数量增长，黑名单很容易漏项。Saligiare 应默认采用：

```text
任务能力白名单
    -> 工具参数 Schema
    -> 资源和路径检查
    -> 运行时策略
    -> 沙箱执行
```

### 3. 容器并不自动等于安全

项目同时支持 Docker 和 Local Executor。若配置切换到 Local，工具可能直接在宿主机执行；即使使用 Docker，也要检查挂载、凭证透传、网络和容器权限。Saligiare 需要把执行后端能力明确标记为 `sandboxed` 或 `host`，并默认拒绝后者。

### 4. 认证环境变量透传

`DockerConfig` 支持通过 `DOCKER_PASSTHROUGH_ENV` 白名单将环境变量传入容器。这比全量透传好，但 Saligiare 仍应默认不透传任何密钥，并对每个任务声明允许的凭证能力。

### 5. 知识库中的危险内容

CHYing-agent 的知识目录包含大量漏洞、利用和安全技巧资料。知识检索结果应该被视为不可信参考数据，不能直接改变工具权限；Saligiare 必须把“知识”和“可执行能力”分离。

## 十一、可借鉴设计

以下设计值得吸收，但要改造成 Saligiare 的安全边界：

1. **Orchestrator + 专用子 Agent**：主 Agent 负责任务分解，专用 Agent 负责特定能力。
2. **MCP 可见性分区**：减少主上下文中的无关工具，并降低误调用。
3. **PromptCompiler**：先整理长上下文，再交给主 Agent。
4. **Progress/Retry Handoff**：把跨 compact 和跨 session 的工作压缩成接班报告。
5. **结构化结果和可信字段重注入**：代码保留不能由模型丢失的 metadata。
6. **任务目录 + findings.log**：保存可验证的关键发现，而不是只依赖会话文本。
7. **成本、Token、工具调用和执行时间观测**：使 benchmark 对比可解释。

## 十二、Saligiare 的重新设计

建议 Saligiare 采用下面的第一版抽象：

```text
Task
  -> CapabilityPlan
  -> Agent Runtime
     -> Typed Tool Registry
     -> Policy Guard（默认拒绝）
     -> Sandbox Backend
     -> Trace Store
  -> Trusted Evaluator
```

后期能力分区：

```text
orchestrator
├── terminal-researcher
├── browser-researcher
├── binary-researcher
├── source-auditor
├── build-test-agent
└── report-agent
```

内核和 WebKit 审计不能只加一个“代码审计 Prompt”，还需要：

- 固定源码提交和构建环境；
- 只读源码工具；
- 编译/测试工具的单独能力；
- 调用图、数据流和生命周期证据；
- Sanitizer/模糊测试结果；
- 可信补丁评估器；
- 不能访问生产目标的隔离环境。

## 十三、与 TSECBENCH / CyberGym 的映射

| CHYing-agent 设计 | Saligiare 目标 |
| --- | --- |
| challenge dict | 统一 `Task` 模型 |
| `solve_single_challenge()` | Benchmark Adapter + Agent Runtime |
| Orchestrator | 通用编排器 |
| executor/browser/reverse/c2 | 能力受限的子 Agent |
| MCP visibility | 工具可见性层，不替代授权层 |
| `progress.md` / `findings.log` | Trace 和可恢复状态 |
| Flag 提取/提交 | Trusted Evaluator 接口 |
| Docker/Local Executor | Sandbox Backend，默认只允许隔离后端 |
| PromptCompiler | 可选的输入规范化阶段 |
| CyberGym 补丁流程 | SourceAuditTask + PatchEvaluator |

TSECBENCH Local 首先要求我们实现协议和任务生命周期；Cybench/InterCode-CTF 验证终端交互；CyberGym 再验证源码和补丁；Linux Kernel/WebKit 专线则在此基础上增加大型 C/C++ 代码库的证据链。

## 十四、结论

CHYing-agent 最值得学习的不是某个 Prompt，而是它把安全任务拆成了多个边界：

```text
任务编排
能力专门化
工具可见性
会话恢复
进度压缩
执行隔离
观测和评测
```

同时，它的比赛优化取舍也提醒我们：

```text
无人值守效率 ≠ 默认安全
工具不可见 ≠ 工具无权限
Docker 配置存在 ≠ 已经完成沙箱
模型输出 solved=true ≠ 可信成功
公开排行榜分数 ≠ 可复现实验
```

Saligiare 将保留这些有价值的结构，但把权限、评测和证据链提升为一等组件。

## 复盘问题

请在阅读本文后用自己的话回答：

1. 为什么 CHYing-agent 要把 Chrome DevTools MCP 隐藏给 Orchestrator？这解决的是上下文问题、权限问题，还是两者都不完全解决？
2. `PromptCompiler` 和 `ProgressCompiler` 分别解决什么问题？为什么不能用一个无限膨胀的 `progress.md` 代替它们？
3. 为什么 Saligiare 不应直接复制 `bypassPermissions`？
4. 如果内核源码审计 Agent 需要运行编译和 Sanitizer，应该把“源码读取”和“构建执行”放在同一个子 Agent 里吗？为什么？
5. 在 TSECBENCH 适配器中，哪些字段必须由代码可信注入，不能由模型自行决定？
