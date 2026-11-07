---
id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
title: 根级恢复/重授权入口（B：source_list_roots 可用性投影 + App 分流 + 撤销/重置；proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-L-S1-REGISTRY-RESILIENCE-1` scope review B 面（恢复路径今天不存在：`source_reset_registry`/`source_revoke_root` App 侧 0 调用；被替换根同路径重导入持续失败）；需 C-16 v1.5 UNFREEZE（零交互自动恢复只读枚举/可用性投影，1 pin）+ 独立 scope review；依赖 L-S4 A（done）
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md
  - doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-*.md
  - verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S1-B-RECOVERY-REAUTH-1：根级恢复/重授权入口（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-L-S1-REGISTRY-RESILIENCE-1` scope review B 面：A 卡修完「单根不可用不再整库不可读」，但**恢复路径今天不存在**——`source_reset_registry`/`source_revoke_root` 在 App 侧 0 调用（仅命令表/Host handler），被替换根同路径重导入会复用失效条目而持续失败；冷启动/周期枚举的自动恢复需 C-16 v1.5 只读枚举/可用性投影（1 pin）。
- 目标（草案）：①C-16 v1.5 UNFREEZE（若 B 需要可用性投影/自动恢复枚举）；②App 侧接线撤销/重置/重授权入口与分流提示；③被替换根的显式恢复流程（用户操作，不自动）；④与 L-S4 A 的刷新/触发衔接。
- 红线：不得自动重新授权/自动重建 identity；恢复必须用户显式；撤销后不得自动放行；不得扩大授权面。

## 候选 Scope（待 scope review 冻结）

- In（草案）：C-16 v1.5 契约（如需）+ Host `SourceAccessRegistry`/App `SourceImportModels` 分流 + 恢复入口接线 + 测试/证据。
- Out（草案）：自动恢复/自动重新授权；扫描实现重写；真实用户数据；push。

## 依赖与下一步

- 依赖：`FEA-11-L-S1-REGISTRY-RESILIENCE-1`（done）、`FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`（done）。
- **必须先做独立 scope review**（判定 C-16 v1.5 是否必须、最小写域、AC 草案、App 分流可行性），由 DSH 裁决后冻结释放。
