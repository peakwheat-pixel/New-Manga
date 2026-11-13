---
id: AUDIT14-V1-MANIFEST-1
title: 建立 V1 commitment manifest 并对齐 README/AD-003/STATUS 文档（AUDIT-14-CAND-001 P3）
kind: documentation
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT09-READER-EMPTY-RETRY-1]
base_commit: 338dc3f9a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 90301427380e67ec72cd253a721fe53214e43333
delivery_head: 90301427380e67ec72cd253a721fe53214e43333
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/AUDIT14-V1-MANIFEST-1
allowed_paths:
  - doc/design/V1_COMMITMENT_MANIFEST.md
  - README.md
  - doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md
  - doc/00_INDEX.md
  - doc/STATUS.md
  - verification/AUDIT14-V1-MANIFEST-1/**
  - doc/tasks/AUDIT14-V1-MANIFEST-1.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AUDIT14-V1-MANIFEST-1：建立 V1 commitment manifest 并对齐 README/AD-003/STATUS 文档（AUDIT-14-CAND-001 P3）

## 来源与目标

`AUDIT-14-CAND-001`（非产品 P3 文档优先级）：README、AD-003、STATUS 等存在可核对的文档漂移，且缺少可计数的 V1 commitment manifest；未证明由此直接造成运行故障（见 `audit/V1-FULL-AUDIT/reports/AUDIT-14-V1-INTEGRITY-2026-11-13.md`）。目标：建立带日期/版本的 V1 commitment manifest（列出 V1 交付项、状态指针与证据位置），并把 README、AD-003、STATUS、文档索引的指针对齐到当前事实；不改产品代码与冻结契约。

## Acceptance Criteria

- [x] **AC1**：核对 README、AD-003、STATUS、00_INDEX 当前指针与漂移点，记录基准（commit/日期）。 <<MET>>
- [x] **AC2**：新增 `doc/design/V1_COMMITMENT_MANIFEST.md`：V1 交付项清单、状态指针（STATUS/Task/证据）与明确的未完成/未验证项。 <<MET>>
- [x] **AC3**：对齐 README、AD-003、STATUS（预算内）、00_INDEX 的指针；不得把 BLOCKED/NOT_RUN 写成 PASS。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| AUDIT14-MANIFEST-1 | AC2 | `doc/design/V1_COMMITMENT_MANIFEST.md` | `90301427380e67ec72cd253a721fe53214e43333` | `85CB2A50C8A4607FA71277EF64F624048760BF470D58A541BB2DD56C39ECEF9A` | CANONICAL | BLOB |
| AUDIT14-README-1 | AC3 | `README.md` | `90301427380e67ec72cd253a721fe53214e43333` | `DFCC585EC180BEF693BB9B382399E9C840F0F2860134ABCB9FE11EDD7106FF54` | CANONICAL | BLOB |
| AUDIT14-INDEX-1 | AC3 | `doc/00_INDEX.md` | `90301427380e67ec72cd253a721fe53214e43333` | `F8A4BF05EBA6EB26923F41A6A1BCFAE1ED16EC34A4D3795454FBCA04455AECE6` | CANONICAL | BLOB |
| AUDIT14-AD003-1 | AC3 | `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md` | `90301427380e67ec72cd253a721fe53214e43333` | `FA67F0822F6F1BB8929358DEB1046B88A272EDF1589F25A6352F4531DAA32F5C` | CANONICAL | BLOB |
| AUDIT14-STATUS-1 | AC3 | `doc/STATUS.md` | `90301427380e67ec72cd253a721fe53214e43333` | `7C418A73D0CE97A13FCB0427E589FA496283E4B877F6355268BBCAE0451FD57E` | CANONICAL | BLOB |
| AUDIT14-EVIDENCE-1 | AC4 | `verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json` | `90301427380e67ec72cd253a721fe53214e43333` | `45D1F209531AC95CA84353EA8CEC9429FEDDB60863AF90AF359A98F5365D361C` | CANONICAL | BLOB |
| AUDIT14-ALIGN-LOG-1 | AC3 | `verification/AUDIT14-V1-MANIFEST-1/logs/manifest-alignment.log` | `90301427380e67ec72cd253a721fe53214e43333` | `7B6054EF8D4E556FBD4E9DF53FF767C9340AAE82F7832FE220CEA3102DF27B7F` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 无 agent-output |
| artifact | verification/AUDIT14-V1-MANIFEST-1 | PRESERVE_REFERENCED | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 对齐证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 无 |
| exchange | - | NOT_APPLICABLE | doc | verification/AUDIT14-V1-MANIFEST-1/evidence/manifest-alignment.json | 无外部传输 |

## 允许修改范围

- `doc/design/V1_COMMITMENT_MANIFEST.md`（新增）
- `README.md`、`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`、`doc/00_INDEX.md`、`doc/STATUS.md`（指针/预算内）
- `verification/AUDIT14-V1-MANIFEST-1/**`
- 本 Task 卡、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

产品源码、测试、契约字节、依赖、真实用户数据、远端、发布；不改写历史 Review/证据。

## 测试要求

纯文档 Task：链接/路径存在性与 STATUS 预算检查（`tools/governance/check.ps1`）；无产品测试。
