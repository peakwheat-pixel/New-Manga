---
id: FEA-11-L-S4-B-AUTO-RECOVERY-1
title: 零交互自动恢复只读枚举（B：C-16 v1.5 批量载体；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` L-S4-1（缺触发器：无既有写路径介入时冷启动/周期枚举不会自动恢复）与 L-S1 scope review B2（roots 可用性投影）；需 C-16 v1.5 UNFREEZE（与 B2 同一批量载体，1 pin）+ 独立 scope review；依赖 L-S4-A done
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
  - FEA-11-L-S1-B-RECOVERY-REAUTH-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-AUTO-RECOVERY-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-AUTO-RECOVERY-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-AUTO-RECOVERY-1-*.md
  - verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S4-B-AUTO-RECOVERY-1：零交互自动恢复只读枚举（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` L-S4-1：A 修完「重注册/重授权原位刷新」，但**缺触发器**——无既有写路径（重导入/sync apply）介入时，冷启动/周期只读枚举不会自动恢复；零交互恢复需 C-16 v1.5 的只读枚举/可用性投影命令。
- `FEA-11-L-S1-B-RECOVERY-REAUTH-1` B2：`source_list_roots` 可用性投影/多根管理面——与 L-S4-B **同一 C-16 v1.5 批量载体**（避免两卡撞版本号；D-2 已裁决一次性分配）。
- 红线：不得自动重新授权/自动重建 identity；不得扩大授权面；只读枚举命令 fail-closed、零 DB 写；恢复仍需用户显式。

## 候选 Scope（待 scope review 冻结）

- In（草案）：C-16 v1.5（与 B2 同批）只读枚举/可用性投影命令 + 能力 + Core/Host 接线 + 测试/证据。
- Out（草案）：自动重新授权、自动重建 identity、扫描实现重写、UI 重写、真实用户数据、push。

## 依赖与下一步

- 依赖：L-S4-A done（`0ebb234bf`）、L-S1-B done（`80d2799de`）、B2 scope 评估。
- **必须先做独立 scope review**（与 B2 合并的 C-16 v1.5 载体范围、最小写域、AC 草案、UNFREEZE 判定），由 DSH 裁决后冻结释放。
