---
task_id: GOV-DEBT-CLEANUP-2
author: dsh
recipient: Codex
base_commit: 75da8281b28c7c11f92518c63d4669b5cf3973e6
delivery_head: e63d9324766db0d381bad24b3fc60a58048430e1
status: ready_for_review
---

# Handoff：GOV-DEBT-CLEANUP-2

## 交付结果

按用户四项裁决与 Codex 两轮裁定，完成治理债的逐项事实核对与资源证据记录。
**没有执行任何重钉、删除、移动、合并或状态变更。**

提交链（base → delivery_head）：

| commit | 内容 |
|---|---|
| `9be9bab21` | 认领 Task（ready → in_progress）+ AC2 / AC3 / AC4 |
| `5b5c3e299` | AC5 / AC7 |
| `4e9bbe04b` | AC8 |
| `713c3aaaf` | AC6（7 个 DONE Task 的 Manifest） |
| `b2b32e05e` | AC1（102 行） |
| `e63d9324766` | AC9 治理输出原始记录 |

### 逐 AC 对照

| AC | 结果 | 证据 |
|---|---|---|
| AC1 102 条 SHA 逐行 | **完成**：78 `KEEP_HISTORIC_PIN` / 13 `BLOCKED_ORIGIN_UNVERIFIED` / 11 `BLOCKED_PRESERVE_DIRTY` | `verification/GOV-DEBT-CLEANUP-2/ac1-sha-rows.md` |
| AC2 29 个 Task 暂缓 | **完成**：29 项全部 `DEFERRED`，10 个未入库文件保持 untracked | `ac2-deferred-tasks.md` |
| AC3 Plan 预算裁决 | **完成**：记录批准值 7000/64，确认本 Task 未改 `check.ps1` | `ac3-budget-decision.md` |
| AC4 P02 AC3 23 条 pin | **完成**：18 `ON_FIXED_BRANCH_NOT_MAINLINE` / 5 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` | `ac4-p02-ac3-pins.md` |
| AC5 13 个 worktree | **完成**：13 项全部 `PRESERVE_UNKNOWN`，标注 2 个不可达 HEAD | `ac5-worktree-preserve-list.md` |
| AC6 7 个 DONE Manifest | **部分完成**：6 个已补表并消除对应错误；`P19-UI-FIX-1` 保留原状（见限制） | `ac6-manifest-backfill.md` |
| AC7 61 个 evidence_dir 文件 | **完成（分类层面）**：61 项全部保持候选分类，无一项登记进 Canonical Evidence | `ac7-evidence-dir-files.md` |
| AC8 未完成 AC | **完成**：373 项 / 69 个 Task，全部 `KEEP_OPEN` | `ac8-open-acs.md` |
| AC9 验证与交接 | **完成**：治理检查原始输出已保存 | `ac9-governance-output.txt` |

## 验证证据

| AC/场景 | 实际命令 | 环境与被测 commit | 结果 | 证据 |
|---|---|---|---|---|
| 全局治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | `e63d9324766` | **PASS (2 warnings)**，exit 0 | `ac9-governance-output.txt` |
| 本 Task 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/GOV-DEBT-CLEANUP-2.md` | `e63d9324766` | **PASS (2 warnings)**，exit 0 | 同上 |
| AC6 影响的 7 个 Task | 逐个 `-TaskPath` | `713c3aaaf` | 6 个各 −1 错误；`P19-UI-FIX-1` 保持 4 | `ac6-manifest-backfill.md` |
| 产品测试 / AC 探针 | **未运行** | — | N/A | 本 Task 明确排除 |

## 明确未做（按裁定与用户裁决）

- 未重钉任何 pin、未标记 `SUPERSEDED`、未编辑任何 Canonical Evidence 表。
- 未删除、移动、归档任何 worktree 或 evidence 文件；未 `git worktree prune`。
- 未合并 `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` 或任何分支。
- 未 `git add` 那 10 个未入库 Task 文件。
- 未修改任何 Task 的 `status`（认领本 Task 自身除外）、AC 或集成事实。
- 未修改 `tools/governance/check.ps1`、产品源码、测试或契约。
- 未复制或处置 `workspace.json`。

## 限制与已知债务

1. **`P19-UI-FIX-1` 的 Manifest 格式不兼容（AC6 未完成项）。**
   该 Task 已有 Codex 于 2026-10-17 生成的 `resource-manifest.json`（7 项，含 closeout 计数），
   正文以散文引用。我尝试转成表格：Manifest 错误消除但**新增 4 个「Resource 最终路径未验证」**
   （4 → 8），因为原文含花括号简写、`%APPDATA%` 变量，以及两个**实际已不存在**的路径
   （`p19-ui-fix-1-isolation-20261017`、`pyinstaller` cache）。为迁就检查器而改写会篡改
   一份准确的他方记录，故回退。**是否做格式转换、以及如何处理两个已不存在的资源，需 Codex 裁定。**

2. **AC7 只到分类层面。** 判定「唯一最终证据」需逐文件读内容并对照 AC 原文，本次未做，
   故 61 项全部停在候选状态，无一登记进 Canonical Evidence。

3. **AC6 新增表的 `sha256/manifest` 列是 Task 文件自身的 sha256**（真实 64-hex 可复核值），
   不是资源的完整性证明；资源状态记在 `reference/process check` 列。

4. **`BLOCKED_*` 与 `DEFERRED` 均不是 PASS。** 约束检查器错误行仍存在（191 行未清零），
   这是用户裁决 2/3 的直接结果，不是遗漏。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审）。
请针对固定 `delivery_head = e63d9324766db0d381bad24b3fc60a58048430e1` 独立复核，
重点核对：
- 102 行 SHA 分类是否与 `sha-mismatch-evidence-chain.md` 一致；
- 是否确实没有任何 pin、资源或 Task 状态被改动；
- `P19-UI-FIX-1` 的处理取舍是否合理（回退 vs 改写）。

Review 通过后交 Codex 核对范围、集成与 closeout。
