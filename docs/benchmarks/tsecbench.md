# TSECBENCH Local 适配器（第一版）

当前实现的是 Saligiare 自己的本地夹具协议，不代表已经完整实现 TSECBENCH 官方线上或本地运行器。这样做的目的，是先固定适配器边界和端到端测试，再根据官方版本文档补充协议字段。

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

## 安全边界

- 只接受 Pydantic 严格 Schema；
- 任务的 capability 仍由 `PolicyGuard` 决定；
- 执行器由调用方注入，默认应使用 Fake 或 Docker Sandbox；
- 适配器不访问公共网络、不读取 Token、不执行任务 JSON 中的任意代码；
- 官方协议字段、镜像和评测器版本在确认前不写入核心 Agent。
