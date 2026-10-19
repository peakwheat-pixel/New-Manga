---
id: GOV-EVIDENCE-DIR-SWEEP-1
title: 两个来源 Task 的 evidence 目录盘点
kind: governance
governance_version: 3
status: in_progress
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-DIR-SWEEP-1
---

# GOV-EVIDENCE-DIR-SWEEP-1：两个来源 Task 的 evidence 目录盘点

## 来源与目标

检查器对 `EXPORT-REVEAL-1` 与 `P15` 报 `DONE evidence_dir 含未登记文件`。

Codex r20 §2.2 裁定：

> 对 `EXPORT-REVEAL-1` 与 `P15` 的目录做**只读清单和引用核对**。
> 能证明 AC、Review 或交付结论的有效证据应在对应 Task 的证据登记中**补列**；
> 仅属冗余尝试/过程日志且无现行引用的文件，确认原始路径、hash、引用和可恢复性后，
> 移入相应 Task 的 workspace archive。

## Acceptance Criteria

- [x] **AC1 只读清单**：列出两个 evidence_dir 的全部文件，逐项记录路径、大小、SHA-256、 <<MET>>
  是否已在 Canonical Evidence 表登记、是否被任何已入库文档引用。
- [x] **AC2 逐文件判定**：对每个未登记文件给出四分类之一—— <<MET>>
  `REGISTER`（能证明某 AC/Review/交付结论，应补列登记）、
  `ARCHIVE`（冗余尝试或过程日志，且无现行引用，可移入 workspace archive）、
  `PRESERVE_UNKNOWN`（无法判定归属、或仍可能被引用 → **保留**）、
  `DUPLICATE`（与已登记文件内容相同，需给出被重复者的 evidence_id）。
  **判据必须引用文件实际内容，不得只看文件名。**
- [x] **AC3 引用核查**：对每个 `ARCHIVE` 候选，确认**没有**任何已入库文档、 <<MET>>
  Task、Review、pin 或 Plan/STATUS 引用它。**有引用者一律 `PRESERVE_UNKNOWN`。**
- [x] **AC4 执行移动（仅 ARCHIVE 项）**：把 `ARCHIVE` 项移入 <<NOT_APPLICABLE: 逐文件判定结果为 0 个 ARCHIVE，无文件需移动>>
  `G:\CODEX\New Manga.workspacerchive\<task>\`，记录原路径、hash 与移动时间。
  **移动前必须 `git status` 确认该文件未入库且有备份。**
- [ ] **AC5 交付与 Review**：生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。
  Review 必须核对：**没有把有引用的文件移走**，且每个 `ARCHIVE` 判定都有内容依据。

## 允许修改范围

- 两个 Task 的 Canonical Evidence 表（仅补列 `REGISTER` 项）。
- `G:\CODEX\New Manga.workspacerchive\`（仅移入 `ARCHIVE` 项）。
- `verification/GOV-EVIDENCE-DIR-SWEEP-1/`。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不删除任何文件（只移动，且移到 workspace archive）。
- 不移走有引用的文件。
- 不改 Task 的 status、AC、Closeout Record。
- 不改 pin。
- 不按文件名判定——必须读内容。

## 测试与验证

```powershell
git -C "G:\CODEX\New Manga" status --porcelain
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/EXPORT-REVEAL-1.md
```

## Canonical Evidence

交付时登记目录清单、逐文件判定表、引用核查、移动记录、Handoff、Review。

## Resource Manifest

本 Task **会移动文件**，Resource Manifest 必须逐项登记每个被移动文件的
原路径、目标路径、hash 与引用核查结论。

## Closeout Record

- 状态：`proposed`。授权来源：Codex r20 §2.2。
