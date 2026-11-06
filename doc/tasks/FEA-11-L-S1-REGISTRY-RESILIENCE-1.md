---
id: FEA-11-L-S1-REGISTRY-RESILIENCE-1
title: SourceAccessRegistry 根级韧性（file-root 缺失/替换不再使整库不可读；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-SCAN-2` L-S1（file-root 缺失/替换导致 `SOURCE_REGISTRY_UNAVAILABLE` 整库 typed fail-closed）与 `FEA-11-RUN-GRANT-2A` 卡 L-G16 邻域；须先独立 scope review（安全口径：单根不可用时不得放宽授权），由 DSH 裁决
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-RUN-GRANT-2
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md
  - doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md
  - doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md
  - verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**
out_of_scope:
  - 生产实现/Host 代码、契约/schema/依赖字节、真实用户数据、push —— 未冻结
---

# FEA-11-L-S1-REGISTRY-RESILIENCE-1：SourceAccessRegistry 根级韧性（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-SCAN-2` L-S1：file-root 缺失/替换 → `SourceAccessRegistry` 整体不可读 → 所有扫描/同步/授权 `SOURCE_REGISTRY_UNAVAILABLE`（fail-closed 正确但粒度过粗；单根故障使整库不可用）。
- 目标（草案）：在**不放宽授权**前提下，把 registry 的「单根不可用/被替换」与「整库不可读」区分开；单根故障按其自身 typed 状态处理（如该根下的 source 不可用），其余根不受影响；recovery 路径需明确（用户重新授权/重定位）。
- 关键约束：不得把缺失根当作「无授权」而静默放行；不得自动重建/猜测 identity；不得修改 Host 私有 registry 的持久化语义以外的契约/pins。

## 候选 Scope（待 scope review 冻结）

- In（草案）：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs`（读取容错/条目级错误）、`HostRuntime.cs`/`SourceScanScheduler.cs`（错误投影）、Host 测试；证据目录。
- Out（草案）：Core/Python、契约/UNFREEZE（除非 review 判必须）、UI/通知、扫描实现重写、真实用户数据、push。

## 依赖与下一步

- 依赖：`FEA-11-RUN-GRANT-2`（done，`018008989`）与本卡 scope review。
- **必须先做独立 scope review**（安全口径/最小写域/AC 草案/测试可行性），由 DSH 裁决后冻结释放。
