---
id: TASK-026
title: 独立集成审查与质量/性能验收
kind: verification
status: proposed
approval: pending_user_review
suggested_owner: DeepSeek Harness
owner: null
reviewer: null
depends_on: [TASK-020, TASK-021, TASK-022, TASK-023, TASK-025]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-026：独立集成审查与质量/性能验收

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D07 §97～106；D08 全文；G14/G15/G16/G17。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-PERF-001、AC-PERF-002、AC-PERF-003、AC-PERF-004、AC-PERF-005、AC-PERF-006、AC-CAP-001、AC-CAP-002、AC-CAP-003、AC-CAP-004、AC-MEM-001、AC-MEM-002、AC-MEM-003。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [ ] 针对固定集成head独立审查Spec/Architecture并执行覆盖表；真实命令、环境、Hash、截图记录所有结果。
- [ ] 运行容量/性能/DPI/多屏/数据安全/恢复/离线场景；报告原始测量与P50/P95，缺环境标BLOCKED。
- [ ] 从真实src/QML/Schema/测试更新11类架构地图并附路径/符号/commit；未实现部分继续To-Be。
- [ ] 发现Bug单独建修复Task和回归要求，不在只读Review范围内自行改生产代码。
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- tests/acceptance/**
- tests/benchmarks/**
- verification/**
- doc/11_ARCHITECTURE_MAPS.md
- doc/13_ACCEPTANCE_TRACEABILITY.md
- doc/reviews/**
- doc/tasks/TASK-026.md
- doc/handoffs/TASK-026-*.md
- verification/TASK-026/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/acceptance tests/benchmarks；获批固定Dataset A～E与全部适用AC。
- 独立复核核心数据安全：源Hash、人工保护、current/Pin、Stop/Crash/Migration/Secrets。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-020](TASK-020.md)、[TASK-021](TASK-021.md)、[TASK-022](TASK-022.md)、[TASK-023](TASK-023.md)、[TASK-025](TASK-025.md)。依赖必须已经集成 done 才可开始。

DeepSeek不可将自己编写的测试当成对自身实现的独立审查；相应部分换Codex/ZCode。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。

> **2026-09-19 ZCode 全权窗口条目**：本 Task 已纳入 [STATUS](../STATUS.md) 的窗口队列（W12+ 尾项），但**门槛未达成**：需 **TASK-022、TASK-025** 完成；且本 Task 为独立审查，**必须由非作者执行**（窗口内 ZCode 不可承担）。门槛满足前一律记 `BLOCKED（前置未达成）`，**不得跳过前置强行开工**；窗口内如需调整门槛，由 Codex 在 T1 后处理。
