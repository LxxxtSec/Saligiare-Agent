# Alibaba Velldepth Agent 研究笔记

## 来源与范围

- 文章：<https://alibaba-velldepth.github.io/writeups/>
- 抓取日期：2026-08-21
- 公开资料是技术写作页面，没有提供 Agent 源码；本文只记录页面公开的模型、harness、评测协议和发现声明。

## 一、系统定位与结果

Velldepth Agent 被描述为 Alibaba Security 面向软件漏洞分析的安全 Agent，结合网络安全模型 XekRung 与漏洞分析 harness。

页面报告 CyberGym Level 1 pass@1 为 85.5%，并称在额外漏洞分析测试中发现 44 个软件仓库中的 92 个潜在 real-world zero-day case。

这两个数字必须分开理解：

- 85.5% 是 CyberGym benchmark 指标；
- 92 个是潜在 zero-day case，不等于已确认、已披露或已修复的 CVE；
- 页面没有提供足够证据让 Saligiare 独立验证这些案例。

## 二、Harness 设计

公开页面将 harness 描述为：先把任务描述和项目可见信息转换为结构化任务状态，再在多个漏洞假设、输入约束和代码路径之间探索，并根据 vulnerable-side 验证反馈动态调整重点。

它还强调：

- 保留并比较多个候选假设，避免过早收敛；
- 联合考虑语义一致性、源码证据和运行时行为过滤候选；
- 最终通过任务提供的漏洞提交接口验证候选；
- 不使用 patched/fixed 版本执行结果帮助模型选择候选；
- 不提供外部漏洞库、公开 PoC、历史补丁或项目历史提示。

这与 Sangfor、Whitzard、DoGNAVY 的共同原则一致：`candidate generation` 和 `final acceptance` 必须分离。

## 三、评测隔离

页面公开声明的约束包括：

- 不预装 libFuzzer、AFL、Honggfuzz 等 fuzzing 框架作为解题工具；
- 不提供预编译 fuzz target 或动态调试环境；
- Agent 只能通过源码理解和任务描述生成候选；
- 候选只通过任务的 vul submission interface 验证；
- 网络搜索和 web fetch 被阻断；
- 公开 benchmark 排行表中的其它 Agent 作为比较对象，但不等于其内部代码公开。

这是一条有价值的实验纪律：harness 要限制外部帮助，同时不把过多专用工具预装给 Agent，否则分数会混合模型能力和工具先验。

## 四、CyberGym “double-crash” 发现

页面指出，一些任务可能存在 double-crash：漏洞描述指向一个路径，但相邻路径也会在 vulnerable 和 fixed 两个版本崩溃。此时一个候选可以在漏洞版本触发，却不能通过 fixed-clean；原因包括：

- 题目描述粒度较粗；
- 多条语义相近的漏洞路径；
- patch 只修复其中一条根因；
- hidden fixed-side 行为不可见。

这个问题提醒 Saligiare：评测器不仅要判断“是否崩溃”，还要判断“崩溃是否对应目标漏洞且 fixed side clean”。对于知识库，也要记录 `target_match` 和 `fixed_clean` 两个不同字段。

## 五、对 Saligiare 的采用决策

| Velldepth 设计 | Saligiare 映射 | 决策 |
| --- | --- | --- |
| 结构化任务状态 | `TaskState` | **steal** |
| 多候选假设并行维护 | `HypothesisLedger` | **steal** |
| 语义 + 源码 + 运行时联合过滤 | `EvidenceReview` | **steal** |
| 只看 vulnerable-side 反馈 | Sandbox/Evaluator 分离 | **steal** |
| fuzz/debug 不作为默认工具 | Capability Plan | **steal** |
| zero-day 发现声明 | 知识库人工审核状态 | **steal with stronger gate** |
| 85.5% benchmark 分数 | 实验注册表 | **record, not guarantee** |

## 六、对 0day/1day/Nday 和 SRC 的影响

### 0day

“潜在 zero-day”必须经过授权、去重、复现、影响评估、负责任披露和人工确认。Saligiare 的知识库状态应至少区分：

```text
potential -> reproduced -> impact-confirmed -> disclosed/fixed
```

不能把 Agent 的报告数量当成 zero-day 能力分数。

### 1day/Nday

多候选和 double-crash 分析适合补丁差异研究；但 Nday 可以用公开 patch 做验证，1day 仍需要严格的版本、时间和授权记录。

### 企业 SRC

结构化状态可以保存目标范围、已验证接口、排除项和重复漏洞；但所有请求仍需通过 scope-aware proxy，不能让模型从页面内容推断新资产。

## 研究结论

Velldepth 最重要的启发是：harness 的任务状态和候选审查决定了长程漏洞分析能否稳定收敛；“模型知道安全知识”本身不足以保证正确复现。对于 Saligiare，`HypothesisLedger + EvidenceReview + TrustedEvaluator` 应先于复杂 Agent Swarm 实现。
