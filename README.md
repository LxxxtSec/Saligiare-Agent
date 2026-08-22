# Saligiare

Saligiare 是一个面向授权本地安全 benchmark 的可学习、可审计 Agent。

项目目标是逐步实现一个能够在隔离环境中完成安全任务的 Agent，并系统学习：

- Agent Loop
- 模型适配器
- Tool Calling
- 状态和上下文管理
- 沙箱与权限控制
- Benchmark 适配器
- 漏洞分析和补丁验证
- Agent 自身的 Prompt Injection 防御
- Linux Kernel 和 WebKit 源码审计

## 当前阶段

当前已完成 v0.1.0 本地可审计基线，详见 [`docs/V1.md`](docs/V1.md)。下一步进入 TSECBENCH Local 适配器开发。

## 环境要求

- Python 3.11、3.12 或 3.13
- Git
- 后续阶段需要 Docker

## 安装

创建虚拟环境：

```bash
python -m pip install -e "[.dev]"
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## 测试和源码检查

运行测试：

```bash
python -m pytest -q
```

运行代码检查：

```bash
python -m ruff check
```

## 项目结构

```text
src/saligiare/  # Saligiare 源码
tests/          # 自动化测试
docs/           # 路线图、研究笔记和问题记录
```

## 安全范围

本项目只用于：

- 你拥有或明确获准测试的系统；
- TSECBENCH、Cybench 等 benchmark 提供的授权环境；
- 本地 Docker 沙箱；
- 故意存在漏洞的训练靶场；
- 离线的 Linux Kernel、WebKit 和其他公开源码分析环境。

不得使用本项目攻击未授权的互联网目标、生产系统、第三方设备或真实用户数据。

## 文档

- [学习路线图](docs/ROADMAP.md)
- [v0.1.0 本地基线说明](docs/V1.md)
- [问题与解决记录](docs/问题记录.md)

## 开发方式

Saligiare 是一个学习型项目。核心代码由学习者亲手实现，每个阶段都需要：

1. 先理解设计；
2. 编写测试；
3. 实现最小功能；
4. 验证成功和失败路径；
5. 保存 Trace 和实验记录；
6. 提交 Git；
7. 复盘设计取舍。
