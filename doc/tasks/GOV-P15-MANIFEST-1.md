---
id: GOV-P15-MANIFEST-1
title: 恢复 P15 缺失的 Resource Manifest
kind: governance
governance_version: 3
status: approved
approval: codex_r20_followup_not_yet_released
suggested_owner: codex
owner: codex
reviewer: Antigravity
depends_on: [GOV-SOURCE-RECORDS-1]
base_commit: 3539d8d75
branch: null
worktree: null
integration_commit: null
delivery_head: 2f9d549d5
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-P15-MANIFEST-1
---

# GOV-P15-MANIFEST-1：恢复 P15 缺失的 Resource Manifest

## 来源与目标

检查器对 `P15` 报 `Resource manifest 不存在：verification/P15/resource-manifest.json`。

Codex r20 §2.2 裁定：

> **P15 的已有 Resource Manifest 行明确记录真实 worktree 为 `PRESERVE_REFERENCED`，
> 且 `resource-manifest.json` 被引用为 closeout 清单。因而资源并非不适用；
> 把引用改为 `NOT_APPLICABLE` 会与既有事实矛盾。** 单独恢复。

## Acceptance Criteria

- [x] **AC1 核实被引用的内容**：从 `P15` 的 Resource Manifest 表与 Closeout Record 中 <<MET>>
  提取该 manifest 本应包含的全部字段（至少：worktree 路径、disposition、
  destination、以及 closeout 清单指向的其它资源）。
  **不得凭空发明字段**——只恢复能从既有记录推出的内容。
- [x] **AC2 核实 worktree 实际状态**：检查 <<MET>>
  `G:\CODEX\New Manga.workspace\worktrees\P15*` 是否存在、是否 clean、
  HEAD 是什么。若已不存在，如实记录为「原 worktree 已清理」，
  **不得伪造路径存在性**。
- [x] **AC3 重建 manifest**：在 `verification/P15/resource-manifest.json` 写入恢复的清单， <<MET>>
  格式须与其它 Task 的同类 manifest 一致（先读一个已有的作参照）。
  内容必须与 AC1/AC2 的核实结果一致，**每个 disposition 都有依据**。
- [x] **AC4 交付与 Review**：生成 Handoff；由 Antigravity 对固定 delivery head 独立 Review。 <<MET>>
  Review 必须核对：**重建的每一个字段都能在既有记录中找到依据**，
  且没有为了让检查器变绿而填 `NOT_APPLICABLE`。

## 允许修改范围

- `verification/P15/resource-manifest.json`（新建）。
- `verification/GOV-P15-MANIFEST-1/`。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不改 `P15.md` 的任何字段（含 `status`、AC、Closeout Record）。
- 不把资源改成 `NOT_APPLICABLE` 来消错。
- 不伪造 worktree 路径的存在性。
- 不改其它 Task 的 manifest。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
```

## Canonical Evidence

交付时登记恢复依据、worktree 实际状态核实、manifest 内容、Handoff、Review。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| P15M-RESTORED | AC3 | `verification/P15/resource-manifest.json` | `68e696306` | `2a8be70bc89152dba1b98d723c43458d2b725754ef6c3a302e4b30cec7c5a02e` | `CANONICAL` |
| P15M-WRITEUP | AC1–AC4 | `verification/GOV-P15-MANIFEST-1/ac1-ac4-manifest-restoration.md` | `237c43862` | `934b747842ff1c15dab1aeef2105bc1a7339077caf998225ccd9b11e9cb21788` | `CANONICAL` |
| P15M-HANDOFF | AC5 | `doc/handoffs/GOV-P15-MANIFEST-1-237c43862.md` | `6eec515a5` | `81e37cd1808cfde9c08eea88d98273b1d9f9ce78b7550502be84ada09e564d31` | `CANONICAL` |
| P15M-REVIEW-R1 | AC4 | `doc/reviews/GOV-P15-MANIFEST-1-6eec515a5-antigravity-r1.md` | `bfbb7b1a9` | `24850b219c19e1a4518e5c804a983694d2b3905c3b4e9e5be2cf7a7a2baac923` | `CANONICAL` |
| P15M-REVIEW-R2 | AC4 | `doc/reviews/GOV-P15-MANIFEST-1-2f9d549d5-antigravity-r2.md` | `bfbb7b1a9` | `3ab530f3beff5a8b65a7fc506368999f0958b11366df84b2483c2154192ac90c` | `CANONICAL` |
| P15M-REVIEW-R3 | AC5 | `doc/reviews/GOV-P15-MANIFEST-1-2f9d549d5-antigravity-r3.md` | `68e696306` | `192f8198b9cc53ba55a8da1674a34161465c8549471d04c0fb7ceb85d3eed758` | `CANONICAL` |

## Resource Manifest

本 Task 自身不处置资源；但须在 closeout 中说明它为何不改变 `P15` 的既有资源结论。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-P15-MANIFEST-1.md` | 只重建一个 JSON 文件 |
| evidence_dir | `verification/GOV-P15-MANIFEST-1/` | `PRESERVE_REFERENCED` | `verification/GOV-P15-MANIFEST-1/` | `934b747842ff1c15dab1aeef2105bc1a7339077caf998225ccd9b11e9cb21788` | 1 份证据 |

## Closeout Record

- 关闭：2026-10-20。Owner=dsh，Reviewer=Antigravity。裁定：Codex r23。
- 终态：**`approved`**（不是 `done`）。AC 4/4 全部 `<<MET>>`；Review 三轮，r3 `APPROVED`。
- **为什么不设 `done`**（r23 §1 与 §3）：`integration_commit` 必须为 `null`，
  直到真实发生 Codex 集成与集成后验证。r23 明确：
  > `integration_commit` 只表示 Codex 集成完成点，**不是「最新提交」、Review 落盘提交
  > 或方便 checker 通过的占位字段**。
  前三轮（`GOV-AC-GATE-1`、`GOV-EVIDENCE-DIR-SWEEP-1`）都遇到过这个矛盾，
  当时登记了分支 HEAD 并在 Closeout 中声明「非集成提交」。**本 Task 不再这样做**：
  按 r23 的口径如实设 `null`，把 Task 停在 `approved`。
- head 三元组：`reviewed_head=2f9d549d5`（r3 Review 固定对象）、
  `delivery_head=2f9d549d5`（最后一次实质交付，**不是** `68e696306` 或 `e66927a31`
  这两个仅落盘 Review / 补 pin 的提交）、`integration_source_head=2f9d549d5`。
- **本 Task 做了什么**：P15 的 Resource Manifest 行引用了一个**不存在**的文件。
  从 P15 自己的记录 + 现场核验重建了它，含 4 个资源。
- **最重要的错误与纠正**：初版只写 1 个 resource（worktree），理由是
  「P15 的记录从未声称 junction，抄同类 Task 就是伪造来源」。r1 Review 实测发现
  三个 junction **全部存在且指向主仓库**，并指出：
  > **物理真实性高于原始文本缺失。混淆了「凭空捏造不存在的虚假资源」与
  > 「对现实物理挂载资源的诚实盘点」。**
  这个纠正已写进 manifest 的 `notes`：
  > The distinction that first version got wrong: fabricating provenance means
  > inventing resources that do not exist. It does not mean declining to observe
  > ones that do. **Physical truth outranks textual silence.**
- **这份 manifest 是重建的，不是原件**：原件从未入库，无从比对。文件已用
  `restored_by` / `restoration_basis` 标注来历。r23 §2.1 判定这不构成 limitation
  ——**已披露的事实不是未完成项**。
- **第二个错误**：改 manifest 后忘了同步 `P15M-RESTORED` 的 sha256 与 `delivery_head`，
  r2 抓到并已修。这是本会话同类错误的第 4、5 次（「改 A 忘了 B 指向 A」）。
- 效果：`P15` 的 `Resource manifest 不存在` **已消除**，只剩 1 个既有错误
  （`SettingsPage.test.tsx` pin 时间性失配，归属 `GOV-PIN-LINEAGE-1`）。
- **`GOV-PIN-LINEAGE-1` 不应吸收 pin 门禁**（r23 §6）：`check.ps1` **已经**校验
  「commit 中存在该路径」与「磁盘 SHA-256 匹配」。六次失误不是缺校验器，
  是交付方没跑它。该 Task 主体仍是历史 pin lineage，不要因这六次而扩张范围。
- 未关闭项：**Codex 集成与集成后验证**。完成后设 `integration_commit` 真实值并转 `done`。
