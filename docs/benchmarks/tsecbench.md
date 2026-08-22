# TSECBENCH Local 适配器（第一版）

当前实现分成两层：一层是 Saligiare 自己的本地夹具协议，另一层是根据官方页面确认的 Python SDK Agent 侧协议模型。前者用于无网络单元测试，后者只定义接口和生命周期，不在测试中使用真实 Token、VPN 或远程靶场。

官方来源：<https://tsecbench.zc.tencent.com/benchmark/prepare/4?mode=local>

官方页面确认的 Agent 侧流程为：

```text
TSecBenchmark(base_url, token)
  -> VPN 预检
  -> list_challenges()
  -> start_challenge(unique_code)
  -> 使用 started.container_addr 解题
  -> submit_flag(unique_code, flag)
  -> close_challenge(unique_code)
```

SDK 负责 Agent 视角的流程，不负责创建 benchmark 任务或连接 VPN。`BENCHMARK_TOKEN`、`BENCHMARK_BASE_URL` 和 VPN 配置由平台在创建跑分任务后提供。

官方页面还明确：一个题目可以有多个 flag 和多个 `container_addr`；已完成题目应跳过；容器无论解题成功与否都应关闭。

## 本地夹具格式

```json
{
  "task": {
    "task_id": "tsecbench-local-001",
    "mode": "ctf_solve",
    "target": "local-fixture",
    "scope": ["local-fixture"],
    "allowed_capabilities": ["echo"],
    "required_approval": "none",
    "max_steps": 2,
    "timeout_seconds": 30,
    "evaluator_id": "tsecbench-local-v1"
  },
  "expected_observation_summaries": ["echo completed"],
  "candidate_refs": ["candidate://flag-001"],
  "evidence_refs": ["trace://observation-001"]
}
```

适配器只负责解析并校验这个 JSON，生成通用 `Task`；它不执行命令，也不判断漏洞是否成立。

## 运行链路

```text
Local JSON
  -> TsecbenchTaskAdapter
  -> Task
  -> AgentLoop
  -> PolicyGuard / Sandbox
  -> RuntimeState
  -> TsecbenchEvaluator
  -> Result
```

评测器使用确定性规则：Agent 必须正常停止，且观测摘要包含任务声明的所有期望摘要，才返回 `accepted`。这只是本地夹具的演示规则，不能替代官方评测器。

## 文件运行

适配器支持从 UTF-8 JSON 文件读取任务，Runner 可以把统一 `Result` 写入另一个 JSON 文件。输出文件只包含评测结果，不包含模型隐藏推理或凭证。

```python
result = runner.run_file(
    Path("case.json"),
    Path("result.json"),
    trace_id="trace-local-001",
)
```

输入和输出路径由宿主程序控制，模型只能产生 `Action`，不能修改 benchmark 文件或选择输出路径。

## 官方协议模型

`src/saligiare/benchmarks/tsecbench/official.py` 对官方 SDK 的主要数据类进行了严格建模：

- `Challenge`：题目描述、难度、分数、flag 进度、容器状态和地址；
- `StartResult`：启动后的题目唯一标识和 `IP:端口` 地址数组；
- `HintResult`：提示内容；
- `SubmitResult`：正确性、得分、累计分数和 flag 进度；
- `CloseResult`：容器是否成功关闭。

`TsecbenchOfficialRunner` 只编排生命周期，实际网络请求由注入的 `TsecbenchClient` 负责。这样可以用 Fake Client 测试生命周期，也可以在确认依赖和 VPN 环境后接入官方 `tsec-benchmark` SDK。

## 官方 SDK 包装器

`TsecbenchSdkClient` 将官方 SDK 返回的数据类转换为 Saligiare 的严格 Pydantic 模型。真实环境中，凭证只从本地环境变量读取：

```bash
export BENCHMARK_TOKEN='只在本机 shell 中设置，不要写入仓库'
export BENCHMARK_BASE_URL='平台发放的 Base URL'
python -m pip install tsec-benchmark
```

代码入口：

```python
from saligiare.benchmarks.tsecbench import create_sdk_client_from_environment

with create_sdk_client_from_environment() as client:
    challenges = client.list_challenges()
```

这个入口只创建 SDK 客户端，不会自动开始评测；真正运行前仍需要确认 VPN 已连接、Agent 已授权、评测范围正确，并由调用方显式执行 `TsecbenchOfficialRunner`。

## Challenge 到 Task

`TsecbenchTaskFactory` 在题目容器成功启动后，使用 `Challenge` 和 `StartResult` 创建通用 `Task`：

- `task_id` 使用 `tsecbench:<unique_code>`；
- `scope` 只包含官方返回的 `container_addr`；
- 默认审批级别为 `dedicated_vm`；
- 题目难度、等级和 flag 数量写入 metadata；
- challenge code 不匹配或地址为空时立即拒绝。

Factory 只做数据转换，不启动容器、不连接地址，也不授予模型新的 capability。真正可用的工具集合仍由调用方注入并经过 `PolicyGuard` 检查。

页面列出的错误包括 VPN 预检失败、任务/题目不存在、状态冲突、重复提交、资源不可用、服务端错误、参数校验错误和连接错误。第一版 Runner 不吞掉这些错误，由上层决定是否重试或停止，并把错误分类接入后续 Trace。

## 安全边界

- 只接受 Pydantic 严格 Schema；
- 任务的 capability 仍由 `PolicyGuard` 决定；
- 执行器由调用方注入，默认应使用 Fake 或 Docker Sandbox；
- 适配器不访问公共网络、不读取 Token、不执行任务 JSON 中的任意代码；
- 官方协议字段、镜像和评测器版本在确认前不写入核心 Agent。
