---
id: FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1
title: roots 可用性投影实现（B2：source_list_roots roots_available；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `C16-V15-BATCH-scope-r1`（B2 无消费者：无 roots UI；导入复用/B1 诊断均不消费）、`FEA-11-L-S1-B-RECOVERY-REAUTH-1` B2 面；C-16 v1.5 已冻结字段 `roots_available[]`；须先独立 scope review（消费者/UI 立项、Host-only 实现面、AC），由 DSH 裁决
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-B-PREREQ-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1.md
  - doc/reviews/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1-*.md
  - doc/handoffs/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1-*.md
  - verification/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1：roots 可用性投影实现（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- C-16 v1.5 已冻结 `source_list_roots` 的 `roots_available: [bool]` additive 字段（scope review 推荐「只冻结字段、实现延后」）；当前无消费者：无 roots UI，导入复用与 B1 诊断均不消费可用性。
- 目标（草案）：Host-only 实现 `roots_available`（逐根只读探测：缺失/不可读/身份不符/探测异常 → false；每根至多一次、锁外、不缓存；文件级损坏仍整命令 `SOURCE_REGISTRY_UNAVAILABLE`）；不改变授权/恢复动作。
- 关键问题（scope review 必答）：消费者是否立项（roots UI/诊断）；探测边界（有界、锁外、不持全局锁做 FS I/O）；性能/证据。

## 候选 Scope（待 scope review 冻结）

- In（草案）：`SourceAccessRegistry`/`SourceReadCoordinator` 投影 + Host 测试。
- Out（草案）：自动重新授权/自动重建 identity；UI（除非同批立项）；契约（字段已冻结）；B2 以外；真实用户数据；push。

## 依赖与下一步

- 依赖：C-16 v1.5（done，`3a475b5b9`）。
- **必须先做独立 scope review**（消费者/UI 立项、探测边界、AC、allowed_paths），由 DSH 裁决后冻结释放。
