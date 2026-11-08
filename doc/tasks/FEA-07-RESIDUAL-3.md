---
id: FEA-07-RESIDUAL-3
title: FEA-07 收口 B（AC1 A03/ACK gated + AC3 跨进程崩溃 + AC4 真实入口/矩阵/sink）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-07-RESIDUAL-2` scope review（§5 拆分）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-07-RESIDUAL-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-3
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-3.md
  - doc/reviews/FEA-07-RESIDUAL-3-*.md
  - doc/handoffs/FEA-07-RESIDUAL-3-*.md
  - verification/FEA-07-RESIDUAL-3/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-07-RESIDUAL-3：FEA-07 收口 B（gated/进程级）

## 拟做（由 scope review 定稿）
- **AC1**：gated 真库 A03（100 次切换前后 `regions.text_json`/`current_revision_id`/三锁列/manual/`region_revisions`/`region_candidates` 逐列相同；内嵌 Python 读库，不引入 `Microsoft.Data.Sqlite`）+ ACK 丢失/重连同 key 不双启动 + 真实 Run/Intent 链路；原生 IME → NA（已登记）。
- **AC3**：外部驱动 `crash-switch.ps1`（park→`Process.Kill(entireProcessTree:true)`→新进程 recover），断言 `RolledBack`/frontend=上一已提交/appearance 不被污染/二次恢复零变化；「暂停期保护状态」两条断言（切换零写保护列 + 恢复采用最新状态）。
- **AC4**：最小 `StartupDiagnostics` sink（`App/Services/StartupDiagnostics.cs` + `App.axaml.cs` ≤5 行）+ 真实进程启动矩阵（4 组参数）+ 9 类 warning fail-safe 单元矩阵；**不改** `tools/e2e/**`/`scripts/**`。
- 完成后与 R4a 合并登记 → `FEA-07` 翻 `done`（两卡都 MET 才行）。
