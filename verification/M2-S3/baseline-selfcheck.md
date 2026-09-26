# M2-S3 基线自检记录（S3-AC1 基线部分）

- 日期：2026-09-26
- 执行者：ZCode（M2-S3 Owner）
- 阶段：开工前基线自检

## Git 基线事实（2026-09-26，开工时）

| 检查项 | 命令 | 结果 | 预期 | 判定 |
| --- | --- | --- | --- | --- |
| 工作区根 | `git rev-parse --show-toplevel` | `G:/CODEX/New Manga.worktrees/M2-S3-zcode` | M2-S3-zcode worktree | PASS |
| git-dir | `git rev-parse --git-dir` | `G:/CODEX/New Manga/.git/worktrees/M2-S3-zcode` | linked worktree | PASS |
| common dir | `git rev-parse --git-common-dir` | `G:/CODEX/New Manga/.git` | 共享 common directory | PASS |
| HEAD | `git rev-parse HEAD` | `90c3e45962733799d43e3aefacf4fea99f662a2c` | base = 90c3e459 | PASS |
| 分支 | `git branch --show-current` | `agent/zcode/M2-S3-tauri-asset-protocol-probe` | 指定任务分支 | PASS |
| 工作区状态 | `git status --short` | （空） | 干净 | PASS |
| M2-C1 Contract blob（1.1，M2-C2 修订后） | `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `fc35913801297ee1876ea395f9c5041a16226f20` | `fc35913801297ee1876ea395f9c5041a16226f20`（Task 依赖声明的固定 blob） | PASS |

HEAD 所在 commit 主题：`90c3e459 docs(M2-C2): close integrated typed IPC contract revision`（M2-C2 集成收尾提交）。

## Task 文件来源

主线 `a006acb9`（`docs(M2-S3): reassign probe owner to ZCode`；其前序 `9b2d40c2 docs(M2-S3): release Tauri asset protocol probe` 创建本 Task 与 `verification/M2-S3/release-90c3e459.md`）。base `90c3e459` 不含这两个治理 commit；Owner 按指令以 `git checkout a006acb9 -- doc/tasks/M2-S3.md` 仅带入本 Task 文件（release 记录保持只读，经 `git show 9b2d40c2` 阅读，不落入本分支）。

## 判定

全部检查 PASS，无 BLOCKED 项。工作区干净、base 一致、分支一致、Contract blob 与 Task 依赖声明一致。

## 后续动作

- `doc/tasks/M2-S3.md` 状态 ready → in_progress。
- 环境探测（Windows/WebView2、Rust/Cargo、Node、Tauri 版本）后开始实现 `experiments/M2-S3/**` 隔离探针。
