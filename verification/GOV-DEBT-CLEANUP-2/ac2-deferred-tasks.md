# AC2 — 29 个非终态 Task 的逐项暂缓记录

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC2 · **性质**: 只读 adjudication

**事实来源**: `verification/P09-GOVERNANCE-DEBT-20261019/dangling-dag-facts.md`（只读引用，未复制或修改）。
**用户裁决**: 见 `user-decisions-20261019.md` 裁决 2 —— 「29 个非终态 Task 全部暂缓，保持原状态与原 AC 不动」。

**本文件的结论**: 29 项**全部**记为 `DEFERRED`。本 Task 未登记其中任何一项到 Plan，
未执行 `git add`，未改动任何 Task 的 `status` 或 AC。

| # | Task ID | 现有状态（未改） | STATUS 指涉 | Plan 指涉 | 文件已入库 | 依赖 | integration_commit | 未勾选/总 AC | 裁决 |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | `M2-SFX-ANNOTATE-R2` | `in_review` | no | no | yes | `M2-SFX-ANNOTATE-R1, M2-SFX-DATA-INFRA, M2-SFX-FINETUNE-PREFLIGHT` | `84f952b3（mer` | 0/6 | `DEFERRED` |
| 2 | `M2-SFX-SYNTH-BG-AUTO` | `in_review` | no | no | yes | `M2-SFX-DATA-INFRA` | `913ca3a9f9c9` | 0/6 | `DEFERRED` |
| 3 | `P02-NEW-TIME-X6-BUILD-CARGO` | `approved` | no | no | yes | `P02-NEW-TIME-X6, P02-NEW-TIME-X6-POSTRUN-REVIEW` | `20d554e5cb8a` | 1/7 | `DEFERRED` |
| 4 | `P02-NEW-TIME-X6-POSTRUN-REVIEW` | `approved` | no | no | yes | `P02-NEW-TIME-X6` | null | 0/5 | `DEFERRED` |
| 5 | `P02-NEW-TIME-X6` | `approved` | no | no | yes | `P02-NEW-TIME-BASELINE` | null | 0/7 | `DEFERRED` |
| 6 | `P02PRE-R0S2` | `blocked` | no | no | **no** | `P02PRE-R0, P02PRE-R0S1` | null | 4/4 | `DEFERRED` |
| 7 | `P02PRE-R0S4` | `blocked` | no | no | **no** | `P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02M7, P02M8, P02M9, P02M10, P02M11` | null | 0/8 | `DEFERRED` |
| 8 | `P02PRE-R0S5` | `blocked` | no | no | **no** | `P02PRE-R0, P02PRE-R0S1, P02PRE-R0S2, P02PRE-R0S3, P02PRE-R0S4, P02M7, P02M8, P02M9, P02M10, P02M11` | null | 0/7 | `DEFERRED` |
| 9 | `P02PRE-R0S6` | `blocked` | no | no | **no** | — | null | 0/7 | `DEFERRED` |
| 10 | `P02PRE-R1H-P2-1-EVIDENCE-CLOSURE` | `blocked` | no | no | **no** | — | null | 1/5 | `DEFERRED` |
| 11 | `P02PRE-R1H-R6-EXEC-A4` | `blocked` | no | no | **no** | `P02PRE-R1H-R6-A4` | null | 6/6 | `DEFERRED` |
| 12 | `P02PRE-R1H-R6-EXEC-A5` | `blocked` | no | no | **no** | `P02PRE-R1H-R6-EXEC-A4` | null | 5/8 | `DEFERRED` |
| 13 | `P02PRE-R1H-R6-EXEC-A6` | `in_progress` | no | no | **no** | `P02PRE-R1H-R6-EXEC-A5` | null | 0/8 | `DEFERRED` |
| 14 | `P02PRE-R1H-R6-ZCODE-H1` | `in_review` | no | no | **no** | `P02PRE-R1H-R6-EXEC-A6` | null | 0/0 | `DEFERRED` |
| 15 | `P02PRE-R1H` | `in_progress` | no | no | **no** | `P02PRE-R1G` | null | 6/7 | `DEFERRED` |
| 16 | `P15-CORE-1` | `blocked` | no | no | yes | `P15-C1, P10, P13-C1` | null | 6/6 | `DEFERRED` |
| 17 | `P19-AC3-1` | `in_review` | no | no | yes | `P15-HOST-2, P19-UI-FIX-2, FEAT-CREATE-4` | `7b1fcc45a926` | 3/7 | `DEFERRED` |
| 18 | `P19-UI-FIX-3` | `blocked` | no | no | yes | `P12, P19-UI-FIX-1` | null | 6/6 | `DEFERRED` |
| 19 | `P20-CLOSE-BOUND-HARDEN-2` | `in_review` | yes | no | yes | `P20-CLOSE-BOUND-HARDEN-1` | null | 1/7 | `DEFERRED` |
| 20 | `T3.2.1-REPAIR-10` | `ready` | no | no | yes | — | null | 5/5 | `DEFERRED` |
| 21 | `T3.2.1-REPAIR-11` | `changes_requested` | no | no | yes | — | null | 7/7 | `DEFERRED` |
| 22 | `T3.2.1-REPAIR-12` | `approved` | no | no | yes | — | null | 6/6 | `DEFERRED` |
| 23 | `T3.2.1-REPAIR-3` | `ready` | no | no | yes | — | null | 6/6 | `DEFERRED` |
| 24 | `T3.2.1-REPAIR-4` | `changes_requested` | no | no | yes | — | null | 7/7 | `DEFERRED` |
| 25 | `T3.2.1-REPAIR-5` | `changes_requested` | no | no | yes | — | null | 9/9 | `DEFERRED` |
| 26 | `T3.2.1-REPAIR-6` | `changes_requested` | no | no | yes | `T3.2.1-REPAIR-5` | null | 7/7 | `DEFERRED` |
| 27 | `T3.2.1-REPAIR-7` | `ready` | no | no | yes | `T3.2.1-REPAIR-6` | null | 8/8 | `DEFERRED` |
| 28 | `T3.2.1-REPAIR-8` | `approved` | no | no | yes | `T3.2.1-REPAIR-7` | null | 4/4 | `DEFERRED` |
| 29 | `T3.2.1-REPAIR-9` | `ready` | no | no | yes | — | null | 5/5 | `DEFERRED` |

## 未入库文件（保持 `UNREGISTERED_UNTRUSTED_SNAPSHOT`）

以下 10 个 Task 文件在当前分支**未受版本控制**。本 Task 未执行 `git add`：

- `P02PRE-R0S2`
- `P02PRE-R0S4`
- `P02PRE-R0S5`
- `P02PRE-R0S6`
- `P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`
- `P02PRE-R1H-R6-EXEC-A4`
- `P02PRE-R1H-R6-EXEC-A5`
- `P02PRE-R1H-R6-EXEC-A6`
- `P02PRE-R1H-R6-ZCODE-H1`
- `P02PRE-R1H`

## 边界

- 本文件不改变任何 Task 的 `status`、AC、依赖或集成事实。
- 「暂缓」不是「取消」，也不是「已完成」；这些 Task 仍存在于工作区与仓库，状态原样保留。
- 未登记进 Plan 是用户裁决的直接结果，不是遗漏。
- 若日后用户改变裁决，需另行释放 Task 执行，不在本 Task 范围内。
