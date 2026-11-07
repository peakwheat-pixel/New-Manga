---
id: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
title: 扫描执行面恢复（L-S4-B-1：reattest 后 tick 仍被同路径 revoked 旧条目 fail-closed 拦住；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-L-S4-B-AUTO-RECOVERY-1` 的 L-S4-B-1（枚举 target 恢复成立，但 `ResolveRegistryEntry` 对同路径 revoked 旧条目 exact-match fail-closed 使 tick 为 typed error）；须先独立 scope review（是否需 C-17/C-16 语义修订、是否 Host-only），由 DSH 裁决
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-B-AUTO-RECOVERY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1：扫描执行面恢复（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-L-S4-B-AUTO-RECOVERY-1` 的 **L-S4-B-1**：B1 显式重授权 → reattest → 枚举 target 恢复成立；但 Host 扫描执行仍被既有 `ResolveRegistryEntry` 对「同路径 revoked 旧条目」的 exact-match fail-closed 拦住（tick `last_result=error`，gated IPC 已如实记录）。
- 目标（草案）：设计并实现「显式重授权 + reattest 之后，扫描执行面也能恢复」——重新解析 registry 条目时接受新 live 条目（同路径 + 新 identity + `CreatedAt > RevokedAt`）而仍拒绝真正的 identity 漂移；不得自动重新授权/自动重建 identity。
- 关键问题（scope review 必答）：该解析是否属于 C-17 §5.3 fail-closed 冻结语义（若是 → 需 C-17 UNFREEZE）；是否可 Host-only 在 reattest 成功后更新 scheduler 的 registry 视图；与 B2 roots 管理、L-S4-1 的关系。

## 候选 Scope（待 scope review 冻结）

- In（草案）：Host `ResolveRegistryEntry`/扫描执行解析 + reattest 成功后的视图更新 + 测试/证据。
- Out（草案）：自动重新授权/自动重建 identity；契约（除非 review 判必须）；folder（L-S4-2）；真实用户数据；push。

## 依赖与下一步

- 依赖：`FEA-11-L-S4-B-AUTO-RECOVERY-1`（done）。
- **必须先做独立 scope review**（C-17 语义/UNFREEZE 判定、最小写域、AC 草案、测试可行性），由 DSH 裁决后冻结释放。
