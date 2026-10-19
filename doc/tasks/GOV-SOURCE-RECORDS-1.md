---
id: GOV-SOURCE-RECORDS-1
title: 两个来源 Task 的 AC 勾选记录维护
kind: governance
governance_version: 2
status: in_review
approval: codex_r19_requires_separate_maintenance_task
suggested_owner: dsh
owner: dsh
reviewer: Antigravity
depends_on: [GOV-EVIDENCE-UNIQUE-1]
base_commit: 32f95fdf9
branch: null（纯记录维护，主线直接执行）
worktree: null（不建 linked worktree）
integration_commit: null
delivery_head: d8ad739d2d99ac40fc96c3f2eed955eb59e516fa
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-SOURCE-RECORDS-1
allowed_paths:
  - doc/tasks/EXPORT-REVEAL-1.md
  - doc/tasks/P15.md
  - doc/tasks/GOV-SOURCE-RECORDS-1.md
  - verification/GOV-SOURCE-RECORDS-1/
  - doc/handoffs/GOV-SOURCE-RECORDS-1-*.md
  - doc/reviews/GOV-SOURCE-RECORDS-1-*.md
---

# GOV-SOURCE-RECORDS-1：两个来源 Task 的 AC 勾选记录维护

## 来源与目标

`GOV-EVIDENCE-UNIQUE-1` 在核对 13 个来源 Task 时发现一个**记录缺陷**：

| Task | AC 勾选 | status | 大小 |
|---|---|---|---:|
| `EXPORT-REVEAL-1` | **0 / 7** | `done` | 17305 B |
| `P15` | **0 / 6** | `done` | 15853 B |

其余 11 个来源 Task 的勾选数与 status 相符。

Codex r19 §2.5 裁定：该异常应**另立一个独立、有限的记录维护 Task**，
不改变两个 Task 的 `done` 资格，也不由 `GOV-EVIDENCE-UNIQUE-1` 代为补勾。

本 Task 即该维护 Task。

## 关键前提：这不是「AC 未满足」

在动手前必须先说清楚一件事——**读这两个 Task 的 Closeout Record 后可以确认，
它们的 AC 未勾选是表单遗漏，不是 AC 未达成。**

### `EXPORT-REVEAL-1` 的 Closeout Record 记载

- `canonical_evidence_status: complete`，**11 条 pin 逐个复算**；合入时全部匹配，
  closeout 时 5 条因 Git 行尾改写而失配（已记录机制）。
- 合并后由 Coordinator 亲自重跑：**source 88 passed / 0 failed / 1 ignored**、
  **frozen 打包 10 passed / 0 failed**。
- **未关闭项：AC4-③ = `BLOCKED`**（真实「成功导出 → reveal → 文件管理器打开」未跑通：
  fixture 无有效 book，且无头 Windows 无法取得 WebView2 句柄）。

即：AC1–AC3、AC5 有完成记录，**AC4 部分 `BLOCKED` 且如实保留**。

### `P15` 的 Closeout Record 记载

- `canonical_evidence_status: complete`，**8 条证据行**，BL-17 包含性逐条成立。
- **独立复核（不引用 Owner 日志）**：独立 Reviewer 工作树亲手复跑
  **前端 28 files / 274 tests passed**。
- **逐项验证**：范围零越界；只开放契约 §7 清单内 **4 个面**；
  **11 个禁用分区逐条**「可见 / 不可操作 / 有原因」。
- 更正了 1 处 pin（RV-P15-04：Owner 按 LF 算，提交 blob 为 CRLF）。
- 记录了 3 条 `P3` 级观察，均判为不要求返修。

即：AC1–AC6 均有完成与复核记录。

## 因此本 Task 要做的不是「验证 AC 是否满足」，而是

**把这个已经存在于 Closeout Record 中的事实，如实反映到 AC 勾选状态里。**

## Acceptance Criteria

- [ ] **AC1 逐 AC 溯源**：对两个 Task 的 13 个 AC，逐个从各自的 Closeout Record、
  Handoff、Review 与证据中找出「该 AC 是否达成」的**书面依据**，并记录依据位置
  （文件 + 行号或章节）。**不得仅凭 status 推定。**
- [ ] **AC2 区分达成 / 部分 / 阻塞**：对每个 AC 给出三分类之一——
  `MET`（有明确完成与复核记录）、`PARTIAL`（部分达成，如 `EXPORT-REVEAL-1` AC4 的 ③ 为 BLOCKED）、
  `UNKNOWN`（记录不足）。**`BLOCKED` 项必须保持不勾选**，只加注说明。
- [ ] **AC3 补勾并加注**：依据 AC1/AC2 的结果，为 `MET` 的 AC 补勾；
  `PARTIAL`/`BLOCKED` 的保持未勾选并在该 AC 行末加注原因与依据位置。
  **不得改变任何 AC 的文字**，只改勾选状态与追加注记。
- [ ] **AC4 不改 status 与其它字段**：两个 Task 的 `status`、`integration_commit`、
  `delivery_head`、`canonical_evidence_status`、`resource_closeout_status`、
  Closeout Record 一律**不改动**。本 Task 只动 AC 行的勾选框与注记。
- [ ] **AC5 记录与 Review**：产出逐 AC 判定表（含依据位置）；生成 Handoff；
  由 Antigravity 对固定 delivery head 独立 Review。
  **Review 必须核对：补勾的每一项都能在 Closeout Record 中找到依据，没有一项是凭 status 推定的。**

## 允许修改范围

- `doc/tasks/EXPORT-REVEAL-1.md`：**仅** AC 行的 `- [ ]` → `- [x]` 与行末注记。
- `doc/tasks/P15.md`：同上。
- `verification/GOV-SOURCE-RECORDS-1/`：逐 AC 判定表。
- 本 Task 自身文件、Handoff、Review。

## 禁止事项

- 不改两个 Task 的任何其它字段、正文、Closeout Record。
- 不改任何证据文件、pin、Review。
- 不把 `BLOCKED` 的 AC 勾上。
- 不因「status 是 done」就推定 AC 达成。
- 不删除、不移动任何文件。

## 测试与验证

```powershell
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/EXPORT-REVEAL-1.md
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/P15.md
pwsh -NoProfile -File tools/governance/check.ps1
```

三个检查均须 PASS。

## Canonical Evidence

交付时登记逐 AC 判定表、两个 Task 的 diff、Handoff、Review、checker 输出。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| SRC-AC1 | AC1、AC2 | `verification/GOV-SOURCE-RECORDS-1/ac1-tracing.md` | `d8ad739d2` | `042ca14c2e5c0686844479904bc76dc40108e2818f425306a88308006329a9f4` | `CANONICAL` |
| SRC-AC2AC3 | AC2、AC3 | `verification/GOV-SOURCE-RECORDS-1/ac2-ac3-ticks-and-preexisting-errors.md` | `d8ad739d2` | `27caaffe934e24fd4791855313e7dcb45fe5fda314cbf79204bad53fafffa30a` | `CANONICAL` |
| SRC-HANDOFF | AC5 | `doc/handoffs/GOV-SOURCE-RECORDS-1-d8ad739d2.md` | `d8ad739d2` | `497a9752ca3ac208e0378baf480a464d94b6aef73ca7fbec5c414baf457a0d1e` | `CANONICAL` |

## Resource Manifest

本 Task 只改两个 Task 文件的 AC 行，不处置资源。交付时逐项登记并注明 `NOT_APPLICABLE`。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| task-env | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| dataset | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| artifact | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| temp | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| agent-output | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| exchange | — | `NOT_APPLICABLE` | — | `doc/tasks/GOV-SOURCE-RECORDS-1.md` | 本 Task 只改两个 Task 文件的 AC 行 |
| evidence_dir | `verification/GOV-SOURCE-RECORDS-1/` | `PRESERVE_REFERENCED` | `verification/GOV-SOURCE-RECORDS-1/` | `042ca14c2e5c0686844479904bc76dc40108e2818f425306a88308006329a9f4` | 2 份证据 |

## Closeout Record

- 状态：`in_progress`。由 DSH 直接执行（两个文件的行级改动，不建 worktree）。
- 授权来源：`verification/P09-GOVERNANCE-DEBT-20261019/codex-closeout-evunique-r19.md` §2.5。
