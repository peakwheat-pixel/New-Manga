# 未登记 DAG 的非终态 Task：逐项现状事实表

**依据**：`codex-debt-ruling.md` §2「DSH 为每项整理现状：Task 状态、当前
STATUS/Plan 是否引用、依赖是否满足、是否有用户授权的未完成目标、交付/集成事实」。
**本表只记录事实，不含任何处置结论**；处置由 Codex 裁定。

采集时点：HEAD `8812f0347`。计数来源：`tools/governance/check.ps1 -TaskPath` 逐文件实测。

**读表须知**：
- `tracked=no` 表示该 Task 文件在当前分支根本未入版本控制——它只存在于工作区或其它分支，
  因此「登记进 DAG」在它先被提交之前无从谈起。
- `in_plan=yes` 表示 Plan 文本里出现过该 ID，但检查器仍报未登记，说明出现位置不在
  当前 DAG 区（例如落在 `## 历史快照` 之后）。
- 依赖列写的是 Task 声明的 ID，未在此表内递归解析其状态。

| Task | 声明状态 | STATUS 引用 | Plan 出现 | 文件已入库 | 依赖 | integration_commit | AC 未勾选/总数 |
|---|---|---|---|---|---|---|---|
| M2-SFX-ANNOTATE-R2 | in_review | no | no | yes | `M2-SFX-ANNOTATE-R1, M2-SFX-DATA-INFRA, M2-SFX-FINETUNE-PREFLIGHT` | `84f952b3（mer` | 0/6 |
| M2-SFX-SYNTH-BG-AUTO | in_review | no | no | yes | `M2-SFX-DATA-INFRA` | `913ca3a9f9c9` | 0/6 |
| P02-NEW-TIME-X6-BUILD-CARGO | approved | no | no | yes | `P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW` | `20d554e5cb8a` | 1/7 |
| P02-NEW-TIME-X6-POSTRUN-REVIEW | approved | no | no | yes | `P02-NEW-TIME-X6` | null | 0/5 |
| P02-NEW-TIME-X6 | approved | no | no | yes | `P02-NEW-TIME-BASELINE` | null | 0/7 |
| P02PRE-R0S2 | blocked | no | no | **no** | `P02PRE-R0, P02PRE-R0S1` | null | 4/4 |
| P02PRE-R0S4 | blocked | no | no | **no** | `P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02M7, P02M8, P02M9, P02M10, P02M11` | null | 0/8 |
| P02PRE-R0S5 | blocked | no | no | **no** | `P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02PRE-R0S4, P02M7, P02M8, P02M9, P02M10, P02M11` | null | 0/7 |
| P02PRE-R0S6 | blocked | no | no | **no** | — | null | 0/7 |
| P02PRE-R1H-P2-1-EVIDENCE-CLOSURE | blocked | no | no | **no** | — | null | 1/5 |
| P02PRE-R1H-R6-EXEC-A4 | blocked | no | no | **no** | `P02PRE-R1H-R6-A4` | null | 6/6 |
| P02PRE-R1H-R6-EXEC-A5 | blocked | no | no | **no** | `P02PRE-R1H-R6-EXEC-A4` | null | 5/8 |
| P02PRE-R1H-R6-EXEC-A6 | in_progress | no | no | **no** | `P02PRE-R1H-R6-EXEC-A5` | null | 0/8 |
| P02PRE-R1H-R6-ZCODE-H1 | in_review | no | no | **no** | `P02PRE-R1H-R6-EXEC-A6` | null | 0/0 |
| P02PRE-R1H | in_progress | no | no | **no** | `P02PRE-R1G` | null | 6/7 |
| P15-CORE-1 | blocked | no | no | yes | `P15-C1, P10, P13-C1` | null | 6/6 |
| P19-AC3-1 | in_review | no | no | yes | `P15-HOST-2, P19-UI-FIX-2, FEAT-CREATE-4` | `7b1fcc45a926` | 3/7 |
| P19-UI-FIX-3 | blocked | no | no | yes | `P12, P19-UI-FIX-1` | null | 6/6 |
| P20-CLOSE-BOUND-HARDEN-2 | in_review | yes | no | yes | `P20-CLOSE-BOUND-HARDEN-1` | null | 1/7 |
| T3.2.1-REPAIR-10 | ready | no | no | yes | — | null | 5/5 |
| T3.2.1-REPAIR-11 | changes_requested | no | no | yes | — | null | 7/7 |
| T3.2.1-REPAIR-12 | approved | no | no | yes | — | null | 6/6 |
| T3.2.1-REPAIR-3 | ready | no | no | yes | — | null | 6/6 |
| T3.2.1-REPAIR-4 | changes_requested | no | no | yes | — | null | 7/7 |
| T3.2.1-REPAIR-5 | changes_requested | no | no | yes | — | null | 9/9 |
| T3.2.1-REPAIR-6 | changes_requested | no | no | yes | `T3.2.1-REPAIR-5` | null | 7/7 |
| T3.2.1-REPAIR-7 | ready | no | no | yes | `T3.2.1-REPAIR-6` | null | 8/8 |
| T3.2.1-REPAIR-8 | approved | no | no | yes | `T3.2.1-REPAIR-7` | null | 4/4 |
| T3.2.1-REPAIR-9 | ready | no | no | yes | — | null | 5/5 |

## 分组观察（仅归类，不裁定）

- **当前分支未入库的 Task 文件：10 个** — `P02PRE-R0S2`、`P02PRE-R0S4`、`P02PRE-R0S5`、`P02PRE-R0S6`、`P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`、`P02PRE-R1H-R6-EXEC-A4`、`P02PRE-R1H-R6-EXEC-A5`、`P02PRE-R1H-R6-EXEC-A6`、`P02PRE-R1H-R6-ZCODE-H1`、`P02PRE-R1H`
- **STATUS 与 Plan 都没有任何指涉：28 个**
- **仍有未勾选 AC：20 个**（最高 9 项未勾选）
- **无 integration_commit：25 个**
