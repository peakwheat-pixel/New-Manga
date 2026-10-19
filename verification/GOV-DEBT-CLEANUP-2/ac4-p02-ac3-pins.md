# AC4 — P02 AC3 分支的 23 条 pin：只读状态记录

**Task**: GOV-DEBT-CLEANUP-2 · **AC**: AC4 · **性质**: 只读，不合并、不重钉

| 项 | 值 |
|---|---|
| 分支 | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` |
| 固定 head | `0af8980884e9d027042ef145cd966577d86b5bc5` |
| head 是否为当前 HEAD 祖先 | **no** |
| 分支上的证据文件 | 72 |
| 其中已在主分支入库 | 0 |
| Task pin 总数 | 23 |
| 在分支上存在 | 18 |
| 在分支上也不存在 | 5 |

## 状态结论（全部 23 条）

- **18 条在分支上存在**：状态 `ON_FIXED_BRANCH_NOT_MAINLINE`。
  只确认「该固定 head 有此路径」，**不视为主线 Canonical Evidence，不视为已集成，不重钉。**
- **5 条在分支上也不存在**：状态 `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED`。
  保留原引用与原 pin，不静默移除。

## 5 条缺失项（保留原引用）

| `doc/handoffs/P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION-R1.md` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.md` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-parent-integration-r1.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.meta.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |
| `verification/P02-NEW-TIME-BASELINE/codex-post-resolution-selftest-r1.fixture-inventory.json` | `MISSING_FROM_FIXED_BRANCH_SOURCE_UNRESOLVED` |

## 明确未做的事

- 未合并该分支，也未 cherry-pick 任何提交。
- 未把 pin 改指向 worktree 绝对路径。
- 未从 Task 中删除任何引用。
- 未把该分支上的任何文件称为「已集成」。
- 未修改 `P02-NEW-TIME-BASELINE-AC3-GIT-TOPLEVEL-RESOLUTION` 的 `integration_status`。
