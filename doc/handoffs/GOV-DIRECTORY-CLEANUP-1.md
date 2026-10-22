---
task_id: GOV-DIRECTORY-CLEANUP-1
author: dsh
recipient: zcode
base_commit: 9ae8aab0a05a447b6330a86efd12a8b2d0ff9a31
delivery_head: 40acf35b77b528c8b9aa0ad4608ba42074ba61a0
status: in_review
---

# Handoff：项目目录清理（执行完成，待独立审查）

Coordinator / Owner：dsh（epoch 10，lease `37230d7822a141fcae8f46acd7841890`）；Reviewer：**zcode**（独立，未参与本次清理执行）。
canonical 仓库 `G:/CODEX/New Manga`；branch `main`；交付 head `40acf35b77b528c8b9aa0ad4608ba42074ba61a0`。

## 1. 授权与范围

用户 2026-10-22 明确要求「负责本项目的目录清理，自动完成调查、分类、计划、执行和验收，减少人工参与」。
盘点范围：`G:/CODEX/New Manga`、`.task-envs`、`.workspace`、`.worktrees`、`P02-scratch-build-source`（五根，合计约 66 GB）。

## 2. 执行摘要

| 候选 | 判定依据 | 原始 | 归档 | 结果 |
|---|---|---:|---:|---|
| `G:/CODEX/P02-scratch-build-source` | 唯一 ref 经 `git cat-file -e` 验证在主仓库可达；工作树 tracked 干净、0 untracked；`.git` 170.9 MiB 为重复对象，`.tmp.driveupload` 125.6 MiB 为上传临时 | 401.3 MiB / 7,656 文件 | 327.1 MiB | **已删除** |
| `G:/CODEX/New Manga.worktrees/*`（40 个目录） | 逐目录检查：`.git` 为目录 0、为文件 0、40 个全无 ⇒ 不被 Git 管理，是 admin 元数据被 prune 后的残留 checkout | 708.3 MiB / 59,917 文件 | 356.2 MiB | **已删除 40/40** |

实际释放 1,109.6 MiB，归档占用 683.3 MiB，净释放 426.3 MiB。两项均为「先归档 → tar 清单与源文件数逐一相等 → 再删除」。

执行期障碍：删除 `.git` 对象遇只读属性导致 `PermissionError`，用 `attrib -R` 清除属性（只改属性）后完成，已在交付记录中如实记录。

## 3. 保留项（未执行）

- `task-envs` 47 个环境（24.6 GiB）：可能含模型/数据/唯一诊断产物，可重建性未逐项验证 → `PRESERVE_UNKNOWN`。
- `workspace/builds|temp|tasks|scratch`（约 12.3 GiB）：派生产物，但未取得「不含唯一结果」证据 → `PRESERVE_UNKNOWN`。
- `workspace/archive`、`datasets`、`models`、`test-materials`、`.git`：证据/恢复资产，保留。
- 主仓库 1,235 个 untracked 根：用户未提交内容，原样保留。

## 4. 验证

```
check.ps1            PASS (3 warnings)              EXIT 0
声明审计              0 errors / 1983 protected roots
git diff --check     EXIT 0
refs/heads           1 (main)
worktrees            1
refs/archive/*      21
tracked 工作区        干净
构建/冒烟验证         NOT_RUN（清理未触及构建产物与运行环境）
```

## 5. 恢复入口

- 归档：`G:/CODEX/New Manga.workspace/archive/directory-cleanup-20261022/`
- 恢复：`tar -xzf <archive> -C <parent>`
- `P02-scratch-build-source` 的全部 Git 历史同时存在于主仓库 `main`，可用 `git checkout` 重建。
- 收据：`verification/GOV-DIRECTORY-CLEANUP-1/execution-receipts.json`（含两个 tar 的 SHA-256 与文件数）。

## 6. 下一 Gate：zcode 独立审查（固定 `9ae8aab0a`）

重点：
1. **两项删除是否满足「已备份 + 可恢复 + 已授权 + 依据充分」**；`P02-scratch-build-source` 的 ref 可达性结论是否成立；`worktrees` 40 个目录「无 .git 即不被管理」的判定是否有反例（例如目录内是否藏有未提交的唯一内容）。
2. **归档完整性**：tar 清单 7,656 / 59,917 项与源文件数一致是否足以证明无遗漏；SHA-256 是否已在收据中固定。
3. **分类诚实性**：`cleanup-plan.json` 中 171 项的分类是否有「名字推定可删」的违规；`PRESERVE_UNKNOWN` 的使用是否恰当。
4. **保留边界**：`task-envs`、`workspace` 派生物、用户 untracked 内容是否真的未动。
5. **禁止项**：是否出现 `clean -fdx`、强制 worktree 删除、`reset --hard`、GC/prune、历史改写或越界跟随。
6. **证据一致性**：Task/Handoff/report/inventory/receipts 与真实文件系统状态是否一致（`P02-scratch-build-source` 不存在、`.worktrees` 仅剩 1 个既有 zip）。

approved 后由 dsh 集成复验并 done；不批准则按 findings 返修。

## 7. 可转发指令（下一节点）

「从 `G:/CODEX/New Manga` 当前 `main`（HEAD `9ae8aab0a`）读取 `doc/tasks/GOV-DIRECTORY-CLEANUP-1.md`、`doc/handoffs/GOV-DIRECTORY-CLEANUP-1.md` 与 `verification/GOV-DIRECTORY-CLEANUP-1/` 下六份证据，独立审查该 Task。重点核对两项删除（`P02-scratch-build-source`、`New Manga.worktrees` 40 个残留目录）的授权、依据与可恢复性，以及 171 项分类是否有『按名字推定可删』的违规。只读审查，不得修改除 Review 文件外的任何文件，不得执行删除/移动/清理命令。approved 后由 dsh 集成并 done。」
