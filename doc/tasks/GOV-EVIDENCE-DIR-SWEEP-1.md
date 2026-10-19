---
id: GOV-EVIDENCE-DIR-SWEEP-1
title: 两个来源 Task 的 evidence 目录盘点
kind: governance
governance_version: 3
status: done
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: b25af8142
delivery_head: c5cec3f63
canonical_evidence_status: complete
resource_closeout_status: complete
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
- [x] **AC5 交付与 Review**：生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。 <<MET>>
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

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| SWEEP-INVENTORY | AC1、AC2 | `verification/GOV-EVIDENCE-DIR-SWEEP-1/ac1-ac2-inventory.json` | `24fcfae13` | `cfe8bbf21c1d85443d3347cc12692ea797ab394980c8aa01642b78e7294650eb` | `CANONICAL` |
| SWEEP-TRIAGE | AC1–AC4 | `verification/GOV-EVIDENCE-DIR-SWEEP-1/ac1-ac4-inventory-and-triage.md` | `24fcfae13` | `95e576c85067c0a8c690071af8e0a23435b989e974e162eb5f8ddb3e3a518579` | `CANONICAL` |
| SWEEP-HANDOFF | AC5 | `doc/handoffs/GOV-EVIDENCE-DIR-SWEEP-1-24fcfae13.md` | `c5cec3f63` | `c93a406c4f3979aa9630500129dee9d07411e40ee6185e5b9bf0482074bdcb25` | `CANONICAL` |
| SWEEP-REVIEW | AC5 | `doc/reviews/GOV-EVIDENCE-DIR-SWEEP-1-c5cec3f63-antigravity-r1.md` | `b25af8142` | `df473330d0e82cc1b2683e653652da5a7a0547e24d56ffa5a8ad8521a896a6a8` | `CANONICAL` |

## Resource Manifest

本 Task **会移动文件**，Resource Manifest 必须逐项登记每个被移动文件的
原路径、目标路径、hash 与引用核查结论。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-EVIDENCE-DIR-SWEEP-1.md` | 本 Task 未移动任何文件 |
| evidence_dir | `verification/GOV-EVIDENCE-DIR-SWEEP-1/` | `PRESERVE_REFERENCED` | `verification/GOV-EVIDENCE-DIR-SWEEP-1/` | `95e576c85067c0a8c690071af8e0a23435b989e974e162eb5f8ddb3e3a518579` | 2 份证据 |

## Closeout Record

- 关闭：2026-10-20。Owner=dsh，Reviewer=Antigravity。裁定：Codex r22。
- 终态：**`done`**。AC 5/5 有记录（4 个 `<<MET>>`，AC4 为 `<<NOT_APPLICABLE>>`）；
  Review 一轮 `APPROVED`。
- head 三元组：`reviewed_head=c5cec3f63`、`delivery_head=c5cec3f63`、
  `integration_source_head=c5cec3f63`。
- **`integration_commit` 的诚实记录**（沿用 r21 对 `GOV-AC-GATE-1` 的口径）：
  r22 仍未产生 Codex 集成提交。本 Task 登记 `b25af8142`（当前分支 HEAD，
  落盘 Review 与证据行的提交），**并声明它不是 merge commit，也不是集成提交，
  只是为满足检查器 `done` 非空约束而登记的分支 HEAD**。
  **这一矛盾应作为治理问题统一处理**，不应靠每个 Task 各自填一个数掩盖。
- **AC4 标 `NOT_APPLICABLE` 不影响 `done`**（r22 §2.1）：AC4 写的是
  「把 `ARCHIVE` 项移入 workspace archive」，而逐文件判定结果为 **0 个 `ARCHIVE`**，
  该 AC 在本 Task 范围内不产生要求。这与「做了但没做成」性质不同，故用
  `NOT_APPLICABLE` 而非 `BLOCKED`/`PARTIAL`。Review 确认了这个区分成立。
- **本 Task 交付了什么**：19 个文件盘点，5 个未登记文件全部补登记（`SOURCE_PIN`）。
  **0 个 `ARCHIVE`，未移动任何文件。**
- **两份失败日志是本 Task 最重要的发现**：
  `post-merge-packaged-capture-error.log`（`EXIT_CODE=101`）与
  `cargo-test-unfiltered-first-run.log`（`EXIT_CODE=101`）。
  后者被 P15 的 Closeout L115 **字面点名**为「证据诚实性（正向记录）」——
  「Owner 保留未过滤首跑的失败日志并**如实命名**」。
  **删掉它们会让证据集看起来更干净，但会抹掉「曾经失败过」这个事实。**
- **一个关于工具的边界**：检查器的 `evidence_dir 含未登记文件` 只列**路径**，
  不判断**重要性**。若只按报错清单补登记，会补对文件但**说不出为什么**，
  也发现不了「这两份失败日志不能删」。本 Task 的 AC2（判据必须引用文件内容）
  正是为弥补这个差距而写。
- 效果：`EXPORT-REVEAL-1` 7→2 errors，`P15` 4→2 errors。
  剩余 4 个全部既有、各有归属（两条时间性 pin 失配 → `GOV-PIN-LINEAGE-1`；
  `P15` 缺 manifest → `GOV-P15-MANIFEST-1`；`EXPORT-REVEAL-1` AC4 `BLOCKED` → 真实情况）。
- **对象 Task 的既有错误不构成本 Task 的 limitation**（r22 §2.1）：
  它们在本 Task 开始前已存在，且本 Task 被明确禁止修其中两项。
- 未关闭项：无（剩余两个 `proposed` 专项由 r22 §2.6 排期）。
