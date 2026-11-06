---
id: FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
title: Core `refresh_source_location_auth` 死代码与撤销/重注册后的 location auth 刷新（proposed 占位）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：scope 尚未冻结，不得实施；来源 `FEA-11-SCAN-2` L-S4（`refresh_source_location_auth` 死代码：撤销/重注册后 Core location auth 不更新，只读切片无法恢复）；须先独立 scope review 判定最小修复与是否需要契约/UNFREEZE，由 DSH 裁决
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
evidence_dir: verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1.md
  - doc/reviews/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - doc/handoffs/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1-*.md
  - verification/FEA-11-L-S4-LOCATION-AUTH-REFRESH-1/**
out_of_scope:
  - 生产实现/契约/schema/依赖字节、真实用户数据、push —— 本卡为占位，未冻结
---

# FEA-11-L-S4-LOCATION-AUTH-REFRESH-1：location auth 刷新（proposed 占位）

> **状态：`proposed`；scope 未冻结，不得实施。**

## 来源与目标（草案）

- `FEA-11-SCAN-2` L-S4：`refresh_source_location_auth` 为死代码；撤销/重注册后 Core 的 `source_locations` auth 状态不更新，只读切片无法恢复（用户撤销后重授权仍被旧 auth 阻断）。
- 目标（草案）：明确该函数的预期语义与调用点（撤销/重注册/重新授权时刷新 location auth），修复死代码路径；保持授权 fail-closed 与既有不变量（不得把撤销变成自动放行）。
- 关键约束：先判定它是否属于 C-16/C-17 冻结面；若涉及 wire/错误码/能力需 UNFREEZE + 独立复核；若纯 Core 内部语义修复则零契约。

## 候选 Scope（待 scope review 冻结）

- In（草案）：`src/application/sources/**`（含 `refresh_source_location_auth` 所在模块）、`src/infrastructure/**` 必要处、测试；证据目录。
- Out（草案）：Host/Avalonia、契约/UNFREEZE（除非 review 判必须）、UI、扫描实现重写、真实用户数据、push。

## 依赖与下一步

- 依赖：`FEA-11-RUN-GRANT-2`（done）与本卡 scope review。
- **必须先做独立 scope review**（死代码事实、正确语义、最小写域、AC 草案、测试可行性），由 DSH 裁决后冻结释放。
