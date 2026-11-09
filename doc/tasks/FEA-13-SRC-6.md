---
id: FEA-13-SRC-6
title: SC-B01 ④ 源引用/授权元数据入包（包内加密段；Host staging 交接面）
kind: implementation
governance_version: 3
status: proposed
approval: **ZCode 独立裁决 2026-11-09（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）**：单列立项（「必须包含」项，非不做）；**不阻塞 FEA-15 正式验收**（验收登记为已知 limitation）；排在 `FEA-11-HOST-AUTH-3` 之后（同域 SourceAccessRegistry/Host 授权）
suggested_owner: zcode（Host/C# 主责域）
owner: null
reviewer: null
depends_on:
  - FEA-13-COV-2
  - FEA-11-HOST-AUTH-3
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-13-SRC-6
allowed_paths:
  - doc/tasks/FEA-13-SRC-6.md
  - doc/reviews/FEA-13-SRC-6-*.md
  - doc/handoffs/FEA-13-SRC-6-*.md
  - verification/FEA-13-SRC-6/**
out_of_scope:
  - **scope 未冻结，不得实施**；allowed_paths 待 scope review 后按实际写域补齐
  - 不实现跨机恢复（DPAPI CurrentUser：同机恢复有效，跨机须重授权）
  - 不改 C-06/C-09/C-17 契约字节与 18 pins（如需契约载体另走 UNFREEZE/errata）
  - 不实现数据根迁移（`FEA-13-MIGRATE-6` 单列 blocked）
---

# FEA-13-SRC-6：SC-B01 ④ 源引用/授权元数据入包（占位）

## 裁决依据（ZCode 2026-11-09）

- C-09 SC-B01 的「必须包含」项，SC-B07 强制增量 ④ 已预留；明确不做需走契约 errata（成本高于实现）。
- 产品价值：AD-003 引用模型下，若 SourceAccessRegistry 不随包恢复，重装/恢复后用户须对全部源重新授权，备份恢复承诺落空。
- 时序：排在 `FEA-11-HOST-AUTH-3`（UNFREEZE）之后——两者同域（SourceAccessRegistry/Host 授权），先落恢复语义再叠备份打包。
- **同机恢复有效；跨机恢复须重授权**（DPAPI CurrentUser 绑定，不得写成通用跨机恢复）。

## 预估范围（待 scope review 冻结）

| 项 | 预估 |
|---|---|
| Host staging 交接面 | `SourceAccessRegistry` 导出 → 交给 Core 打包加密段 |
| Core 侧 | `nmbak` 包内新增加密段（`extras/source-access/…`）+ manifest 记录 |
| 恢复反向 | 解包 → Host 导入（冲突/过期处置） |
| 契约 | 若需 C-06/C-09 载体 → 另走 UNFREEZE/errata（不得直接改冻结字节） |
| 证据 | L2 正/负 fixture + 加密段不可读断言 + 恢复后授权可用 |

## Acceptance Criteria

- 待 scope review 冻结（当前仅占位；不得实施）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（proposed 占位） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实数据 |

## Closeout Record

- 未开始（proposed）。
