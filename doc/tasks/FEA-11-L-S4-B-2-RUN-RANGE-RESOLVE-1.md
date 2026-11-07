---
id: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
title: Run 源范围解析恢复（L-S4-B-2：HostRuntime.RunSourceRange 仍按路径解析；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1` 的 limitation（Run 面未含：`HostRuntime.RunSourceRange.Resolve` 仍按路径 `ResolveRegistryEntry`，同路径 revoked 旧条目对 Run 预授权/冷源 on-demand 影响未测未修）；须先独立 scope review（是否与 L-S4-B-1 同 helper、是否需 C-16/C-17 判定），由 DSH 裁决
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md
  - doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1：Run 源范围解析恢复（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1` 的 limitation：扫描执行面已恢复；但 `HostRuntime.RunSourceRange.Resolve`（`HostRuntime.cs:1785` 一带）仍按路径 `ResolveRegistryEntry`，同路径 revoked 旧条目可能导致 Run 预授权/冷源 on-demand scan 不解析 → Run 源范围不可用（未测未修）。
- 目标（草案）：复用 L-S4-B-1 的「自身已核验 live `(registry_id, generation)`」解析原则，恢复 Run 面；保持 fail-closed（缺失/撤销/漂移/根替换 typed）、不自动重新授权/不重建 identity。
- 关键问题（scope review 必答）：Run 面是否可用同一 helper；是否触及 C-16 §2.4/§2.5 或 C-17 §5.3 语义（若需 → UNFREEZE）；与 B2/folder/L-S4-1 关系。

## 候选 Scope（待 scope review 冻结）

- In（草案）：`HostRuntime.cs`（RunSourceRange 解析）+ 必要 helper + 测试/证据。
- Out（草案）：扫描执行面（已 done）；自动重新授权/自动重建 identity；契约（除非 review 判必须）；B2/folder；真实用户数据；push。

## 依赖与下一步

- 依赖：`FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`（done）。
- **必须先做独立 scope review**（UNFREEZE 判定、最小写域、AC 草案、测试可行性），由 DSH 裁决后冻结释放。
