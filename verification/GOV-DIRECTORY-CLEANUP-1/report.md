# GOV-DIRECTORY-CLEANUP-1 执行报告

执行者：dsh（Coordinator epoch 10，lease `37230d7822a141fcae8f46acd7841890`）
时间：2026-10-22；范围：`G:/CODEX/New Manga`、`.task-envs`、`.workspace`、`.worktrees`、`P02-scratch-build-source`
授权：用户在 2026-10-22 明确要求「负责本项目的目录清理，自动完成调查、分类、计划、执行和验收」。

## 1. 盘点结果

| 根 | 体积 | 说明 |
|---|---:|---|
| `G:/CODEX/New Manga` | 14,563.5 MiB | 主仓库；tracked 干净，1,235 个 untracked 根原样保留 |
| `G:/CODEX/New Manga.task-envs` | 24,618.1 MiB | 47 个 Task 隔离环境（Python venv/模型/OCR 数据） |
| `G:/CODEX/New Manga.workspace` | 26,037.9 MiB | 28 个分类目录（archive/builds/temp/tasks/…） |
| `G:/CODEX/New Manga.worktrees` | 722.7 MiB → 14.4 MiB | 40 个无 `.git` 的残留 checkout |
| `G:/CODEX/P02-scratch-build-source` | 401.3 MiB → 0 | 独立 Git 仓库副本，全部 ref 在主仓库可达 |

共 171 个直接子项，逐项写入 `inventory.json`。

## 2. 本轮执行（已归档后删除）

| 候选 | 依据 | 原始 | 归档（tar.gz） | 结果 |
|---|---|---:|---:|---|
| `G:/CODEX/P02-scratch-build-source` | 唯一 ref `refs/heads/main` 经 `git cat-file -e` 验证在主仓库中存在；工作树 tracked 干净、0 untracked；.git 170.9 MiB 为重复对象，`.tmp.driveupload` 125.6 MiB 为上传临时文件 | 401.3 MiB / 7,656 文件 | 327.1 MiB，tar 清单 7,656 项与源一致 | **DELETED** |
| `G:/CODEX/New Manga.worktrees/*`（40 个目录） | 逐目录检查：`.git` 为目录 0 个、为文件 0 个、**40 个均无** ⇒ 不被 Git 管理，是 admin 元数据被 prune 后的残留 checkout | 708.3 MiB / 59,917 文件 | 356.2 MiB，tar 清单 59,917 项与源一致 | **DELETED（40/40）** |

**实际释放**：1,109.6 MiB；**归档占用**：683.3 MiB；**净释放约 426 MiB**。
恢复入口：`G:/CODEX/New Manga.workspace/archive/directory-cleanup-20261022/`，`tar -xzf <archive> -C <parent>`；
`P02-scratch-build-source` 的全部 Git 历史同时存在于主仓库 `main`，可用 `git checkout <commit>` 重建。

## 3. 保留项与原因

- **源代码/证据/数据集/模型/测试物料**（`apps`、`src`、`doc`、`verification`、`datasets`、`models`、`test-materials`）：默认保留。
- **`.git`（1,197.9 MiB）**、`refs/archive/*`（21 条）、全 refs bundle：恢复资产，保留。
- **`workspace/archive`（4.28 GiB）**：本次及历史的恢复资产，保留。
- **`task-envs` 47 个环境（24.6 GiB）**：可能含模型/数据/唯一诊断产物，可重建性未逐项验证 → `PRESERVE_UNKNOWN`，留待下一轮按任务归属核对。
- **`workspace/builds`（6.0 GiB）、`temp`（3.1 GiB）、`tasks`（2.9 GiB）、`scratch`（335 MiB）**：派生产物，但未取得「不含唯一结果」的证据 → `PRESERVE_UNKNOWN`。
- **主仓库 1,235 个 untracked 根**：用户未提交内容，原样保留。

## 4. 验证

- 归档完整性：两个 tar 的清单条目数与源文件数逐一相等（7,656 / 59,917）。
- 删除后：`P02-scratch-build-source` 不存在；`.worktrees` 根保留、40 个子目录为 0 个（仅剩 1 个既有 zip 文件 15.1 MiB）。
- Git：`refs/heads` 仍仅 `main`、worktree 1、`refs/archive/*` 21、tracked 干净。
- 治理检查与声明审计结果见 `report-verification.txt`。

## 5. 未执行 / 需要裁决

本轮**未删除** `task-envs`（24.6 GiB）与 `workspace/builds|temp|tasks|scratch`（约 12.3 GiB）。原因：这些目录需要逐项确认「不含唯一产物」，属于需要具体裁决的范围。若批准，建议按「先归档、后删除、再复验」的同一流程分批执行。

## 6. 恢复与回滚

- 归档目录：`G:/CODEX/New Manga.workspace/archive/directory-cleanup-20261022/`
- 执行收据：`execution-receipts.json`（含两个 tar 的 SHA-256、文件数、结果）
- 回滚：解包归档到原父目录即可恢复；Git 仓库副本可用主仓库 commit 重建。
