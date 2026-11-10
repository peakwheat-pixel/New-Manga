---
id: FEA-15-PIN-EOL-GOV-1
title: 证据 pin 行尾与跨 checkout 可复现性治理
kind: governance
governance_version: 3
status: proposed
approval: pending_scope_review
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-15-ACCEPT-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-15-PIN-EOL-GOV-1
allowed_paths:
  - doc/tasks/FEA-15-PIN-EOL-GOV-1.md
  - doc/reviews/FEA-15-PIN-EOL-GOV-1-*.md
  - doc/handoffs/FEA-15-PIN-EOL-GOV-1-*.md
  - verification/FEA-15-PIN-EOL-GOV-1/**
out_of_scope:
  - proposed 未释放；未经单独冻结不得实施，不得修改 .gitattributes、检查语义、历史证据或冻结契约
---

# FEA-15-PIN-EOL-GOV-1：证据 pin 口径治理候选

来源：`doc/reviews/FEA-15-ACCEPT-1-r2.md` P3-A 与 ZCode 最终裁决。r2 时 30 条 pin 中 27 条工作区 hash 与 blob 不同；后续又登记资源清单，执行前必须重新盘点当前全集。r27 曾记录 187 条历史工作区口径 pin，不能据此推断当前全集。

按 `doc/09_COLLABORATION.md` §4.4，先冻结核验范围、建立影响全集和基线矩阵，再裁决口径、行尾规则、renormalize 与历史 pin 处置；未完成核验与单独授权前不得改 `.gitattributes` 或既有证据。Task 尚未释放。

## Acceptance Criteria

- [ ] **AC1**：范围、数据来源与跨 checkout 的口径矩阵经释放后核验。 <<PENDING>>
- [ ] **AC2**：受影响全集和历史差异形成可复核证据，未确认项如实登记。 <<PENDING>>
- [ ] **AC3**：口径与迁移方案经授权和独立 Review；仅在后续明确释放范围内执行。 <<PENDING>>

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task resources | 尚未创建 | NOT_APPLICABLE | — | — | proposed，尚未执行 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Closeout Record

- 2026-11-11：ZCode 裁决登记 proposed；未释放、未实施。
