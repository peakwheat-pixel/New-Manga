---
id: REALUSE-DATA-SAFETY-8
title: SAFETY-7 Review P2 收尾——证据文档修正与 CloseAsync 健壮性
kind: quality
governance_version: 3
status: in_progress
approval: follow_up_of_REALUSE-DATA-SAFETY-7_review_2026-11-01
suggested_owner: dsh
owner: dsh-lead
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-7
base_commit: bb7cbda1d
branch: task/REALUSE-DATA-SAFETY-8
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-8
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-8
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-8.md
  - doc/tasks/REALUSE-DATA-SAFETY-7.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-8-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-8-*.md
  - apps/desktop-avalonia/src/**
  - apps/desktop-avalonia/tests/**
  - verification/REALUSE-DATA-SAFETY-8/**
  - verification/REALUSE-DATA-SAFETY-7/**
---

# REALUSE-DATA-SAFETY-8：SAFETY-7 Review 的 5 条 P2

## 来源

[REALUSE-DATA-SAFETY-7 独立 Review](../reviews/REALUSE-DATA-SAFETY-7-review.md)（`approved`，P0/P1=0，P2×5 open）在集成后保留的 5 条 P2。本 Task 承接，不重复 SAFETY-7 的范围。

## 逐条说明

1. **F-001 证据文档计数不实**：`ac2-eol-pin.md` 与 SAFETY-7 任务卡写「11 条 pin / 2 条更新 / 9 条不变」，实际 SAFETY-6 共 12 条 pin、5 条值变化（3 代码 + 2 证据）；对照表漏列 4 条代码 pin。
2. **F-002 负向对照配方不可复现**：`ac1-negative-control.md` 的步骤是「提交前工作树」配方，在交付 head 上逐字执行是空操作；缺原始输出与 `exit_code=`。
3. **F-003 日志缺 filtered 段与 cwd**：任务卡把 filtered 6/6 归到 `ac1-fix-tests.txt`，但日志只有 build + 全量两段；相对路径命令在仓库根执行会 `MSB1009`。
4. **F-004 `catch (Exception)` 静默吞异常**：`ReaderOverlayViewModel.CloseAsync` 等待在途保存时捕获所有异常且不记录，同类回归将不可见。
5. **F-005 残留窄竞态**：CloseAsync 等待窗口内若再触发翻页保存，closing 权威重读仍可能被 `_isSaving` 短路（不再 NRE，影响为一次「镜像而非权威重读」）。

## 验收标准

- [x] **AC1 F-001/F-002/F-003 证据文档修正**：`ac2-eol-pin.md` 计数与表格覆盖 12 条 pin / 5 条变化；`ac1-negative-control.md` 改为 post-delivery 配方并附原始输出与 `exit_code=`；`ac1-fix-tests.txt` 补 filtered 段并记录 cwd。 <<MET>>
- [x] **AC2 F-004 异常捕获限定**：`CloseAsync` 等待在途保存时只捕获与 core 一致的已知类型，其余记录 `Debug` 并设置可见状态，不得静默；保存路径自身不再抛出未观察异常。 <<MET>>
- [x] **AC3 F-005 关闭期间保存门禁**：closing 期间禁止新保存启动（`_isClosing` 门禁 + 循环等待），保证 closing 时恰好一次权威重读；新增确定性用例。 <<MET>>

## 禁止范围

- 不改冻结契约；不动用户数据；不 push；不改 SAFETY-6/7 的历史 Review 字节；不删除用户数据。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 配方 | base 文件覆盖 + filtered 测试 + 恢复 | SAFETY-7 worktree | **1 failed / 0 passed，EXIT=1**（修复前）；恢复后 clean | `ac1-doc-fix.md` |
| AC1 日志 | 构建 + filtered + 全量，记录 cwd | net9.0 | 三段均含 cwd/输出/EXIT | `ac1-fix-tests.txt` |
| AC2 | `dotnet build` + filtered | net9.0 | **0 警告 / 0 错误**；7/7 | `ac1-fix-tests.txt` |
| AC3 | 全量 + 新增 closing 门禁用例 | net9.0 | **396 通过 / 0 失败 / 7 跳过（403）**，EXIT=0 | `ac1-fix-tests.txt` |

## Canonical Evidence

证据 pin 采用 **blob（LF）基准**（`git cat-file blob` → SHA-256）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC2-READER-VM | AC2/AC3 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ReaderOverlayViewModel.cs` | `60056d353` | `f71eed262580207963ee6e2518638230ebf1045c9285c48af300174da73664eb` | CANONICAL |
| E-AC3-TEST | AC3 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LibraryProgressRefreshTests.cs` | `60056d353` | `b1862e36386128ed5cb65ba8ac64b2c849ffece0c9c139d69556b3c82e0aecd2` | CANONICAL |
| E-AC1-PIN-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` | `60056d353` | `4b7676cf8980cf97caa5039cf822b9a3295887abdd979e7d005bb7cca97196f6` | CANONICAL |
| E-AC1-NEG | AC1 | `verification/REALUSE-DATA-SAFETY-7/ac1-negative-control.md` | `60056d353` | `ad1a0fc4027984c8d653f57ebff12ab2385e2656a230df72d6f86e670982e4b2` | CANONICAL |
| E-AC1-DOC | AC1 | `verification/REALUSE-DATA-SAFETY-8/ac1-doc-fix.md` | `60056d353` | `42d5a986cd6cefb62791b93d6b288dcfab621ccd658b8c461f2fa6c5b9df6ec8` | CANONICAL |
| E-AC2-DOC | AC2 | `verification/REALUSE-DATA-SAFETY-8/ac2-catch-scope.md` | `60056d353` | `a90521d543b1f574f8929bce6820cbea414675defe395d2728bb42088edd94d0` | CANONICAL |
| E-AC3-DOC | AC3 | `verification/REALUSE-DATA-SAFETY-8/ac3-closing-gate.md` | `60056d353` | `6bc65d82fef2016d54c00e975f7c1c380ce06c0289021e759903d47f9825ec01` | CANONICAL |
| E-TEST-LOG | AC1/AC2/AC3 | `verification/REALUSE-DATA-SAFETY-8/ac1-fix-tests.txt` | `60056d353` | `713a8e0ac880cabf9f1d70d654ba90b13845df0efbec0a7ee8b8b42230278e06` | CANONICAL |
| E-EVIDENCE-INDEX | AC1/AC2/AC3 | `verification/REALUSE-DATA-SAFETY-8/README.md` | `60056d353` | `2df34f829fd6f345e9995dc8b0981f51bdc0fd20547f5c579733576cae40860d` | CANONICAL |
| E-RESOURCE-MANIFEST | Resource | `verification/REALUSE-DATA-SAFETY-8/resource-manifest.json` | `923f1d5db` | `3fef751eae39c0596ec8b7b8fe032829f661ff83ee6f52b66c537d411b4e3f55` | CANONICAL |

## Resource Manifest

资源收口记录：`verification/REALUSE-DATA-SAFETY-8/resource-manifest.json`（schema_version 1）。

- worktree：PRESERVE_REFERENCED（分支 `task/REALUSE-DATA-SAFETY-8`）
- 负向对照临时日志 `tmp/safety8-negctl.log`：DELETE_SAFE，已删除（`closeout_counts.deleted=1`）
- 用户数据：本 Task 零写操作

## Closeout Record

- Closeout date / DSH：待关闭时填写。
