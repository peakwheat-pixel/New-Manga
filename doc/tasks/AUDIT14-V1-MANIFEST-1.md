---
id: AUDIT14-V1-MANIFEST-1
title: 建立 V1 commitment manifest 并对齐 README/AD-003/STATUS 文档（AUDIT-14-CAND-001 P3）
kind: documentation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [AUDIT09-READER-EMPTY-RETRY-1]
base_commit: 338dc3f9a
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1**：核对 README、AD-003、STATUS、00_INDEX 当前指针与漂移点，记录基准（commit/日期）。
- [ ] **AC2**：新增 `doc/design/V1_COMMITMENT_MANIFEST.md`：V1 交付项清单、状态指针（STATUS/Task/证据）与明确的未完成/未验证项。
- [ ] **AC3**：对齐 README、AD-003、STATUS（预算内）、00_INDEX 的指针；不得把 BLOCKED/NOT_RUN 写成 PASS。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `doc/design/V1_COMMITMENT_MANIFEST.md`（新增）
- `README.md`、`doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md`、`doc/00_INDEX.md`、`doc/STATUS.md`（指针/预算内）
- `verification/AUDIT14-V1-MANIFEST-1/**`
- 本 Task 卡、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

产品源码、测试、契约字节、依赖、真实用户数据、远端、发布；不改写历史 Review/证据。

## 测试要求

纯文档 Task：链接/路径存在性与 STATUS 预算检查（`tools/governance/check.ps1`）；无产品测试。
