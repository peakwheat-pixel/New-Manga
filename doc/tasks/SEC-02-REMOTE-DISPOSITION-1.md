---
id: SEC-02-REMOTE-DISPOSITION-1
title: 远端暴露面处置方案评估（不执行）
kind: design
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [SEC-01-REMOTE-VISIBILITY-1]
base_commit: de79702b96f99e663442da3a2158c88d98385962
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 1a3b3616b0496f4e61b2f6a08eef32de872a90f0
delivery_head: 1a3b3616b0496f4e61b2f6a08eef32de872a90f0
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SEC-02-REMOTE-DISPOSITION-1
allowed_paths:
  - verification/SEC-02-REMOTE-DISPOSITION-1/**
  - doc/tasks/SEC-02-REMOTE-DISPOSITION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# SEC-02-REMOTE-DISPOSITION-1：远端暴露面处置方案评估（不执行）

## 来源与目标

SEC-01 已确认 `AUDIT-11-INC-001` 的远端可见性：公开仓库 `https://github.com/peakwheat-pixel/New-Manga` 可匿名访问，`cc88d1ee`、`b1c1f5a5` 提交可见，`.tmp.driveupload` 历史树可枚举。本 Task 只做**处置方案评估**：列出可选处置（保持现状、删除含素材分支、force-push 改写历史、联系 GitHub 支持、仓库转私有/删除）、评估风险、可逆性、外部影响与证据保全要求，给出建议与需要显式授权的不可逆动作清单。**本 Task 不执行任何远端写操作。**

## Acceptance Criteria

- [x] **AC1**：列出至少 4 个处置选项与不行动选项，记录每个选项的机制、影响面、可逆性、证据保全、对本地/他人 clone/fork 的影响。 <<MET>>
- [x] **AC2**：给出风险矩阵与推荐方案（可明确“暂不执行、保持现状并继续监测”为推荐），并说明不可逆动作需何种授权与前置核验。 <<MET>>
- [x] **AC3**：记录未验证事实（第三方 clone/fork/缓存、平台缓存、法律/通知义务），不推断已知结论之外的事实。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁与资源 closeout 完成，Task 由 DSH 自动裁决并记录 limitation。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| SEC02-REPORT-1 | AC1-4 | `verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md` | `1a3b3616b0496f4e61b2f6a08eef32de872a90f0` | `F942957D325B183F14F9DC5E15E5DBE42E787BC26575C1B6C66C3D59877E6194` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 无 agent-output |
| artifact | verification/SEC-02-REMOTE-DISPOSITION-1 | PRESERVE_REFERENCED | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 评估报告保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 未读取素材 |
| exchange | - | NOT_APPLICABLE | doc | verification/SEC-02-REMOTE-DISPOSITION-1/REPORT.md | 无外部传输 |

## 允许修改范围

- `verification/SEC-02-REMOTE-DISPOSITION-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

任何远端写操作（push/删除分支/force-push/改写历史/建 issue 或 PR/联系平台）、产品源码、契约、依赖、用户数据、历史证据、素材内容下载或传播。

## 测试要求

设计/评估 Task，无产品测试；引用 SEC-01 证据并保存评估输出与门禁记录。
