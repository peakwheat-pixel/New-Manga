# 未兑现 worktree closeout 的逐项实测

**依据**：`codex-debt-ruling.md` §4「DSH 对每个真实 worktree/resource 逐项记录
source、精确 disposition、当前最终路径、integrity manifest/hash、引用/进程检查和结果」。
**本文件只记录实测事实，不含 disposition**；处置由 Codex 裁定。

判据来源 `doc/WORKTREE_SAFETY_INVENTORY.md`：clean 不等于可删；Task 归属、独有 commit、
未跟踪内容无法确认时一律 `UNKNOWN_DO_NOT_DELETE`；只允许普通 `git worktree remove`，
不用 `--force`、不 `prune`。

| Task | worktree 存在 | 已注册 | HEAD | 分支 | dirty(tracked) | untracked | HEAD 已在当前分支历史中 |
|---|---|---|---|---|---|---|---|
| EVENTS-FWD-1 | yes | yes | `5f1d9870ea87` | `EVENTS-FWD-1` | 0 | 0 | yes |
| EXPORT-IPC-1 | yes | yes | `fee223e36bfc` | `EXPORT-IPC-1` | 0 | 0 | yes |
| HOST-TTL-BOUNDARY-1 | yes | yes | `fdf974645f4d` | `HOST-TTL-BOUNDARY-1-grant-ttl` | 0 | 0 | yes |
| P12 | yes | yes | `98f3055f1ace` | `P12-bookshelf-ui` | 0 | 0 | yes |
| P14 | yes | yes | `41c320694273` | `P14` | 3 | 1 | **no** |
| P15 | yes | yes | `ee19898fcd32` | `P15` | 0 | 2 | yes |
| P15-C1 | yes | yes | `9c0200e88f36` | `P15-C1` | 0 | 0 | yes |
| P15-C1-FU1 | yes | yes | `9b0a24590585` | `P15-C1-FU1` | 0 | 0 | yes |
| P15-C1-FU2 | yes | yes | `0aa01eddcd75` | `P15-C1-FU2` | 0 | 0 | **no** |
| P15-HOST-1 | yes | yes | `f80678bbd231` | `P15-HOST-1` | 0 | 0 | yes |
| P19-BOOT-1 | yes | yes | `e4aff85bc87f` | `P19-BOOT-1` | 0 | 0 | yes |
| READER-IPC-1 | yes | yes | `6aadc70de76b` | `READER-IPC-1` | 0 | 1 | yes |
| RUN-IPC-1 | yes | yes | `de3caf93adf4` | `RUN-IPC-1` | 25 | 1 | yes |

## 分组观察（仅归类）

- worktree 仍存在：**13 / 13**
- 已不存在：0 个 — 无
- 现存中 worktree 状态 clean：9 个
- 现存中有 dirty 内容：4 个

> 即便某行显示 clean 且 HEAD 已在当前分支历史中，本节也不构成删除授权：需 Codex 依 §4.2
> 给出 disposition，且只有 approved integration closeout window 才可执行物理处置。
