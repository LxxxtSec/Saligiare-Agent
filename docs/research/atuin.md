# Xuanwu Atuin AI 研究笔记

## 来源与范围

- 文章：<https://xlab.tencent.com/en/2026/07/17/xuanwu-atuin-cybergym-glm52/>
- 抓取日期：2026-08-21
- 公开内容是 Tencent Xuanwu Lab 的 CyberGym 结果更新文章，不包含 Atuin 的源码或完整 Prompt。

## 一、公开结果

文章报告：

- Atuin + GLM-5.1：84.0% pass@1；
- Atuin + GLM-5.2：84.8% pass@1，即 1,278/1,507；
- 相同 GLM-5.1 下，Atuin 比 Claude Code 基线高 15.3 个百分点；
- 模型从 GLM-5.1 升到 GLM-5.2，提升 0.8 个百分点。

这些结果说明架构收益和模型升级收益需要分开记录，不能把总分提升全部归因于 Agent 结构。

## 二、公开系统定位

Atuin 被描述为面向软件漏洞发现、分析和复现的多 Agent 安全分析系统，覆盖：

- 源码；
- 二进制；
- JavaScript bundle；
- 目标建模；
- 代码分析；
- 漏洞推理；
- exploit 构造；
- 验证与 review；
- 结构化 campaign context 和可复用安全知识。

文章特别说明 Atuin 并非为 CyberGym 专门设计，CyberGym 上的表现来自可迁移的漏洞调查、PoC 构造和工作流控制机制。

## 三、评测设置

文章列出的更新包括：

- 模型改为 GLM-5.2；
- 网络使用代理白名单，只允许 LLM provider、Python/npm registry 和内部服务；
- 仍然只使用严格的 CyberGym Level 1 输入：漏洞源码和高层描述；
- 允许容器内动态调试；
- 每题一次运行，基础设施失败除外；
- 无 fixed binary 访问；
- 无 server-side post-patch feedback。

这比完全 `network_mode=none` 更宽松，但仍然阻断 web-search shortcut；Saligiare 需要把网络策略作为可配置的、可审计的任务字段，而不是固定假设。

## 四、对 Saligiare 的采用决策

| Atuin 公开能力 | Saligiare 映射 | 决策 |
| --- | --- | --- |
| 多 Agent 协同 | `CapabilityPlan` / 后期 Swarm | **park then steal** |
| 源码、二进制、JavaScript bundle 统一调查 | `source_audit`、`binary_research`、`webkit` | **steal** |
| 目标建模到 review 的完整流程 | `TaskState` + `EvidenceReview` | **steal** |
| campaign context | `TraceStore` / Knowledge Scope | **steal with scope** |
| 代理白名单 | Network Policy | **steal with explicit scope** |
| 只看 vulnerable-side | Trusted Evaluator 隔离 | **steal** |
| 文章未公开的 Agent 内部代码 | Saligiare Runtime | **unknown** |

## 五、对能力蓝图的影响

Atuin 的覆盖范围提醒我们，Saligiare 不应把“Web 漏洞 Agent”作为唯一抽象。统一任务协议需要支持：

```text
source target
binary target
JavaScript/WebKit target
Android package target
network/SRC target
```

但统一协议不意味着统一权限。每种目标必须绑定自己的工具能力、沙箱、凭证和评测器。

在后续 WebKit 线中，可以把 JavaScript bundle、WebCore/JSC 源码和浏览器运行时观察挂到同一个 `CampaignContext`，但页面内容仍必须标记为不可信 Observation，不能改变 Policy Guard。

## 研究结论

Atuin 体现的是“通用安全研究工作流可迁移到 benchmark”的路线，而不是为单一榜单做特化脚本。对 Saligiare 的实际建议是：先实现领域无关的状态、工具、策略和评测接口，再为源码、二进制、WebKit、Android 和 SRC 加载不同能力计划。
