# 缺 Resource Manifest 的 7 个 Task：资源盘点

**依据**：`codex-debt-ruling.md` §7a「先盘点再裁定」。
这 7 个 Task 的 `status` 均为 `done`，但体内**完全没有** `Resource Manifest` 节，
因此历史上从未登记过任何资源。**本表只记录实测事实，不含 disposition**。

| Task | status | 声明 worktree | worktree 存在 | 已注册 | HEAD 已在当前分支历史 | dirty | untracked | task-env | agent-output | evidence 文件数 |
|---|---|---|---|---|---|---|---|---|---|---|
| FEAT-CREATE-1 | done | yes | yes | yes | **no** | 0 | 0 | no | no | 2 |
| FEAT-CREATE-2 | done | null | yes | yes | yes | 0 | 0 | no | no | 4 |
| FEAT-CREATE-3 | done | yes | yes | yes | yes | 1 | 1 | no | no | 8 |
| FEAT-CREATE-4 | done | yes | yes | yes | yes | 0 | 0 | no | no | 28 |
| FEAT-IMPORT-MULTI-1 | done | yes | yes | yes | yes | 50 | 50 | no | no | 85 |
| P19-UI-FIX-1 | done | yes | yes | yes | yes | 0 | 0 | no | no | 58 |
| P19-UI-FIX-2 | done | yes | yes | yes | yes | 0 | 0 | no | no | 37 |

## 分组观察（仅归类）

- worktree 仍存在：**7 / 7**
- **声明 `worktree: null` 但目录实际存在：1 个** — `FEAT-CREATE-2`
- **HEAD 不在当前分支历史中：1 个** — `FEAT-CREATE-1`
- worktree 有 dirty 内容：2 个 — `FEAT-CREATE-3`(1)、`FEAT-IMPORT-MULTI-1`(50)
- task-env 存在：0 个
- agent-output 存在：0 个

> 本表不构成删除、移动或登记授权。按 `WORKTREE_SAFETY_INVENTORY`，
> clean 不等于可删；disposition 由 Codex 依 §4.2 在适用窗口给出。
