---
id: FEA-07-RESIDUAL-2
title: FEA-07 收口（A03/ACK/Run gated + (SessionId,RegionId) 单写 owner + 崩溃注入 + 真实负载）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由用户 2026-11-08 残余收口指令（R4）与 ADJ §7.4 计划；**scope 未冻结，不得实施**；须先独立 scope review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-07
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-2.md
  - doc/reviews/FEA-07-RESIDUAL-2-*.md
  - doc/handoffs/FEA-07-RESIDUAL-2-*.md
  - verification/FEA-07-RESIDUAL-2/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-07-RESIDUAL-2：FEA-07 收口（占位）

## 拟做（待 scope review 冻结）
- **AC1 子项**：A03 真库 DB/current/pinned/Lock gated 用例、ACK 重连、真实 Run/Intent（`ChapterCreationTests`/`RunControllerTests`/`Fea11SourceIpcTests` 先例）。原生 IME → **NA**。
- **AC2 子项**：`(SessionId, RegionId)` 单写 owner + Host 生命周期（ADJ-2026-11-01 U-03 冻结语义；`WindowBroker` 目前仅角色登记）。真实双屏落位 → **NA**。
- **AC3**：跨进程崩溃注入 + 暂停期间保护状态变化。
- **AC4**：真实 App 初始化入口 + 坏包/scale 矩阵。
- **AC6**：真实规模合成负载 p95 + UI freeze 指标（最大 UI 线程调度间隔）。
- **NA**：原生 IME、AC5 双屏/拔屏/DPI 矩阵、真实双屏落位（原生交互未执行，NOT_RUN）。
