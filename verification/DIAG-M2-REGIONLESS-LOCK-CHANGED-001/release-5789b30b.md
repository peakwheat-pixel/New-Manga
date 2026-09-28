# DIAG-M2-REGIONLESS-LOCK-CHANGED-001 Release Record

- **Decision:** 用户要求只在 React + TypeScript + Tauri + Python Core + SQLite 新架构推进，并授权本次 REBASELINE 全面检查、更新与下一任务分配。
- **Task / state:** [`DIAG-M2-REGIONLESS-LOCK-CHANGED-001`](../../doc/tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md), `ready / M2_REGIONLESS_LOCK_CHANGED_DIAGNOSTIC_RELEASED`。
- **Owner / Reviewer / Integrator:** DeepSeek Harness / Antigravity（非作者）/ Codex。
- **Dependency:** M2-AC1=`done`, integration=`f162193b5255f06bcbbfc0d1820f38cd81f89d32`。
- **Fixed base:** `5789b30b37dfbf79d9bca707b5fdaaa562ada707`。
- **Branch:** `agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001`。
- **Worktree:** `G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh`（冻结路径；待创建）。
- **Dispatch:** `AWAITING_EXTERNAL_DISPATCH`。

## Release Gate

| Required field | Frozen evidence |
|---|---|
| Base | `5789b30b37dfbf79d9bca707b5fdaaa562ada707` |
| Branch / worktree | 已固定于 Task frontmatter |
| Allowed / forbidden paths | 已固定于 Task 对应章节 |
| Acceptance Criteria | AC1–AC5 已冻结 |
| Verification commands | 复现、既有受影响测试、`diff --check` 已冻结 |

释放前主线为 `main@5789b30b37dfbf79d9bca707b5fdaaa562ada707`，无 Active Task。工作区已有与本次无关的 modified/untracked 文件，本次不覆盖、不清理、不纳入交付。此 Task 只授权诊断；产品修复、Legacy QML、Contract、Schema、依赖、打包及其他 Acceptance Backlog 工作均未释放。

## Forwardable Owner instruction

> 致 DeepSeek Harness：执行已释放的 [`DIAG-M2-REGIONLESS-LOCK-CHANGED-001`](../../doc/tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md)。仓库 `G:/CODEX/New Manga`，固定 base=`5789b30b37dfbf79d9bca707b5fdaaa562ada707`，branch=`agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001`，worktree=`G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh`。只在 Task 允许路径内，用临时 SQLite 与 production Pipeline seam 稳定复现 regionless `detect → backfill → ocr` 的 `LOCK_CHANGED`，记录 PlanUnit、StepRun、lock snapshot、catalog current 与最终错误，完成多 Region fan-out/终态计数/重启恢复的反事实分析及最小修复建议。按 Task 命令执行复现、既有受影响测试和范围检查，把 shell、解释器、HEAD、EXIT 与原始日志写入 `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/`，提交研究报告和 Handoff。不得修改 `src/**`、`apps/**`、`tests/**`、Contract、Schema、依赖、打包或 Legacy QML。固定 delivery head 后交 Antigravity 非作者 Review，再由 Codex 裁决后续修复 Task 与集成。
