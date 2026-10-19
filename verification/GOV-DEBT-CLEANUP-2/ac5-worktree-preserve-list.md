# AC5 — 13 个 worktree 的只读保留清单

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC5 · **性质**: 只读，不删除/移动/prune

**事实来源**: `verification/P09-GOVERNANCE-DEBT-20261019/worktree-closeout-facts.md`。
**安全判据**: `doc/WORKTREE_SAFETY_INVENTORY.md` —— clean 不等于可删；
无法确认时一律 `UNKNOWN_DO_NOT_DELETE`；只允许普通 `git worktree remove`，不用 `--force`、不 `prune`。

**本文件的结论**: 13 项**全部**记为保留。本 Task 未删除、未移动、未 prune 任何 worktree。

| # | Task | worktree 存在 | 已注册 | HEAD | 分支 | dirty(tracked) | untracked | HEAD 已在当前分支历史 | disposition |
|---:|---|---|---|---|---|---|---|---|---|
| 1 | EVENTS-FWD-1 | yes | yes | `5f1d9870ea87` | `EVENTS-FWD-1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 2 | EXPORT-IPC-1 | yes | yes | `fee223e36bfc` | `EXPORT-IPC-1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 3 | HOST-TTL-BOUNDARY-1 | yes | yes | `fdf974645f4d` | `HOST-TTL-BOUNDARY-1-grant-ttl` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 4 | P12 | yes | yes | `98f3055f1ace` | `P12-bookshelf-ui` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 5 | P14 | yes | yes | `41c320694273` | `P14` | 3 | 1 | **no** | `PRESERVE_UNKNOWN`（不可达 HEAD） |
| 6 | P15 | yes | yes | `ee19898fcd32` | `P15` | 0 | 2 | yes | `PRESERVE_UNKNOWN` |
| 7 | P15-C1 | yes | yes | `9c0200e88f36` | `P15-C1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 8 | P15-C1-FU1 | yes | yes | `9b0a24590585` | `P15-C1-FU1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 9 | P15-C1-FU2 | yes | yes | `0aa01eddcd75` | `P15-C1-FU2` | 0 | 0 | **no** | `PRESERVE_UNKNOWN`（不可达 HEAD） |
| 10 | P15-HOST-1 | yes | yes | `f80678bbd231` | `P15-HOST-1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 11 | P19-BOOT-1 | yes | yes | `e4aff85bc87f` | `P19-BOOT-1` | 0 | 0 | yes | `PRESERVE_UNKNOWN` |
| 12 | READER-IPC-1 | yes | yes | `6aadc70de76b` | `READER-IPC-1` | 0 | 1 | yes | `PRESERVE_UNKNOWN` |
| 13 | RUN-IPC-1 | yes | yes | `de3caf93adf4` | `RUN-IPC-1` | 25 | 1 | yes | `PRESERVE_UNKNOWN` |

## 需要单独说明的两项

以下两项的 HEAD **不在当前分支历史中**，持有当前分支无法到达的提交。
按 Safety Inventory，它们**无论工作区多干净都不可被视为可移除**：

- `P14`（同时是 dirty 项之一）
- `P15-C1-FU2`

## 有 dirty 内容的项

- `P14`：tracked 3 / untracked 1
- `P15`：tracked 0 / untracked 2
- `READER-IPC-1`：tracked 0 / untracked 1
- `RUN-IPC-1`：tracked 25 / untracked 1

## 明确未做的事

- 未执行 `git worktree remove`（含普通形式）。
- 未执行 `git worktree prune`，未使用 `--force`。
- 未修改、暂存或清理任何 worktree 内的 dirty/untracked 内容。
- 未删除任何本地分支。

> 即便某项显示 clean 且 HEAD 已可达，本文件也不构成删除授权。disposition 的最终裁定
> 属 Codex，物理处置只能在 approved integration closeout window 内进行。
