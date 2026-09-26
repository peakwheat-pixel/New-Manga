# M2-RC1 基线自检记录（RC1-AC1）

- 日期：2026-09-27
- 执行者：ZCode（M2-RC1 Owner）
- 阶段：开工前基线自检

## Git 基线事实（2026-09-27，开工时）

| 检查项 | 命令 | 结果 | 预期 | 判定 |
| --- | --- | --- | --- | --- |
| 工作区根 | `git rev-parse --show-toplevel` | `G:/CODEX/New Manga.worktrees/M2-RC1-zcode` | M2-RC1-zcode worktree | PASS |
| git-dir | `git rev-parse --git-dir` | `G:/CODEX/New Manga/.git/worktrees/M2-RC1-zcode` | linked worktree | PASS |
| common dir | `git rev-parse --git-common-dir` | `G:/CODEX/New Manga/.git` | 共享 common directory | PASS |
| HEAD | `git rev-parse HEAD` | `2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1` | base = 2dca20cd | PASS |
| 分支 | `git branch --show-current` | `agent/zcode/M2-RC1-large-media-resource-channel-runtime` | 指定任务分支 | PASS |
| 工作区状态 | `git status --short` | （空） | 干净 | PASS |
| Contract blob（1.1） | `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `fc35913801297ee1876ea395f9c5041a16226f20` | `fc35913801297ee1876ea395f9c5041a16226f20`（Task 固定 blob） | PASS |

HEAD 所在 commit 主题：`2dca20cd docs(M2-S3): record integration verification and close probe`（M2-S3 集成收尾）。

## 释放 commit 关系

释放 commit `fb87414a`（`docs(M2-RC1): register and release large-media runtime`）的父 commit 即 base `2dca20cd`——Task 文件与 `verification/M2-RC1/release-2dca20cd.md` 位于该治理 commit。Owner 按指令仅以 `git checkout fb87414a -- doc/tasks/M2-RC1.md` 取入 Task 文件（release 记录经 `git show` 只读），**不合并释放 commit**。

## 判定

全部检查 PASS，无 BLOCKED 项。工作区干净、base 一致、分支一致、Contract blob 与 Task 固定 blob 一致。
