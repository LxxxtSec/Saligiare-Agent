# DeepSec DoGNAVY CyberGym 研究笔记

## 来源与可达性

- 文章：<https://deepsec.darknavy.net/blog/cybergym/>
- 抓取日期：2026-08-21
- 初始 HTML 返回页面部署恢复提示；公开前端资源中内嵌了完整技术报告文本，本笔记依据该公开报告整理。
- 报告标题：`DoGNAVY CyberGym Technical Report`
- 报告日期：2026-07-29

## 一、公开结果

报告称 DoGNAVY 在 CyberGym Level 1 的 1,507 个任务中：

- 1,369 个通过 server-side differential validation，90.84%；
- 1,453 个在 vulnerable build 触发崩溃，96.42%；
- 其中 79 个 patched build 也崩溃，因此未通过 fixed-clean；
- 54 个没有提交候选 PoC。

报告同时披露约 39.28B tokens、524,049 次 LLM 请求、22,648.43 USD 估算成本和 2,195.89 小时 trace activity span。

这些数字是公开技术报告的声明，不是 Saligiare 的复现结果。

## 二、系统工作流

DoGNAVY 将漏洞复现拆成显式阶段，阶段内的 Agent 选择分析策略、形成假设和选择工具；新证据出现后，可以在源码分析、输入构造、运行时测试之间移动，或回到已经被新证据否定的假设。

报告还明确设置独立 review Agent，检查候选是否：

- 到达预期代码路径；
- 匹配题目描述的漏洞；
- 可重复复现；
- 不是 assertion failure、环境异常或相邻漏洞。

抽象流程：

```text
漏洞描述
  -> 入口与调用链重建
  -> 解析/状态/数据约束
  -> 候选输入构造
  -> vulnerable-side 动态反馈
  -> 独立 review
  -> controlled submission
  -> validator 双版本执行
```

## 三、静态与动态闭环

DoGNAVY 用静态分析提出漏洞路径和输入约束，再用 coverage、错误位置、crash 类型和稳定性进行动态验证。每次结果都会更新下一次分析或输入。

报告强调：

```text
退出码、断言失败、无关崩溃和环境异常
    不等于目标漏洞已复现
```

这与 Whitzard 的 `fuzz_witness != solved`、Cairn 的 `Fact != trusted verdict` 完全一致，可以成为 Saligiare 的统一证据分层原则。

## 四、记忆与隔离

DoGNAVY 禁用跨任务记忆，每个任务从独立环境开始；任务内保留压缩路径、约束、失败尝试、运行时反馈和未解决假设。

它的任务状态不是无限聊天历史，而是用于下一轮实验的压缩研究状态。这样既防止跨任务泄漏，也保留长任务的因果链。

## 五、沙箱与验证边界

报告声明：

- 每个任务使用独立 sandbox；
- sandbox 参考 AgentDoG 的轨迹级安全诊断和干预思路；
- Agent 只能看到 vulnerable build；
- patched build 和 server-side validator 在独立环境；
- 两者之间只有受控 submission interface；
- Agent 不能访问 validator 地址、服务端凭据和 patched build；
- 网络只允许模型服务和任务准备所需资源；不提供 web search、web fetch 或 MCP。

这套设计同时防止 benchmark cheating 和现实网络越界，正好对应 Saligiare 能力蓝图中的“信息边界”和“执行边界”两类控制。

## 六、与 Saligiare 的映射

| DoGNAVY 设计 | Saligiare 设计 | 决策 |
| --- | --- | --- |
| 显式阶段 | `CapabilityPlan` / `TaskState` | **steal** |
| 可回退假设 | `HypothesisLedger` | **steal** |
| 独立 review Agent | `ReviewStage` + `Trusted Evaluator` | **steal** |
| vulnerable/validator 分离 | `Sandbox` + host-side evaluator | **steal** |
| 跨任务记忆关闭 | Task 隔离的 Knowledge Scope | **steal** |
| 轨迹级安全干预 | `TracePolicy` / `Approval` | **steal with redesign** |
| 39B token 规模 | 运行预算与成本指标 | **warning** |

DoGNAVY 的 `ReviewStage` 对 Saligiare 尤其重要：它可以在写入知识库前检查证据链完整性，防止“模型发现一个可疑点”直接变成“确认漏洞”。

## 七、对后续能力的影响

### 内核与 WebKit

DoGNAVY 的“调用链 + 输入约束 + 动态反馈”适用于内核系统调用、驱动入口、WebKit parser、JSC 字节码和 IPC 消息研究。但后端要分别使用 kernel VM、Android 模拟器或浏览器测试夹具，不能用一个通用 Shell 替代。

### Android App

静态入口、组件边界和动态行为可以共享同一套 Hypothesis Ledger；ADB、Frida、模拟器和网络代理仍需要独立能力白名单。

### 企业 SRC

DoGNAVY 的网络隔离原则可以迁移到 SRC，但 SRC 需要额外的目标 scope、速率限制和人工审批。不能因为有“controlled submission interface”就放宽真实企业系统的边界。

## 研究结论

DoGNAVY 提供的是一套完整的“假设—证据—复核—验证”方法：

```text
Agent 可以反复修改假设，
但不能修改任务范围、validator 规则和完成判定。
```

这应成为 Saligiare 支持 CVE、内核和 WebKit 的主线工作流。
