---
id: REALUSE-DATA-SAFETY-8
title: SAFETY-7 Review P2 收尾——证据文档修正与 CloseAsync 健壮性
kind: quality
governance_version: 3
status: ready
approval: follow_up_of_REALUSE-DATA-SAFETY-7_review_2026-11-01
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-7
base_commit: aaed145e9
branch: null
worktree: null
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

- [ ] **AC1 F-001/F-002/F-003 证据文档修正**：`ac2-eol-pin.md` 计数与表格覆盖 12 条 pin / 5 条变化；`ac1-negative-control.md` 改为 post-delivery 配方并附原始输出与 `exit_code=`；`ac1-fix-tests.txt` 补 filtered 段并记录 cwd。 <<PARTIAL: 待实现>>
- [ ] **AC2 F-004 异常捕获限定**：`CloseAsync` 等待在途保存时只捕获与 core 一致的已知类型，其余记录 `Debug`/通知，不得静默；新增或调整用例覆盖。 <<PARTIAL: 待实现>>
- [ ] **AC3 F-005 关闭期间保存门禁**：closing 期间禁止新保存启动（或循环等待 `_isSaving == false` 后再做 closing 保存），保证 closclose 时始终恰好一次权威重读；新增确定性用例。 <<PARTIAL: 待实现>>

## 禁止范围

- 不改冻结契约；不动用户数据；不 push；不改 SAFETY-6/7 的历史 Review 字节；不删除用户数据。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 文档核对 + 重新执行负向对照配方 | 只读/仓外副本 | NOT_RUN | 待补 |
| AC2 | `dotnet test --filter FullyQualifiedName~LibraryProgressRefreshTests` | net9.0 | NOT_RUN | 待补 |
| AC3 | 新增 closing 期间保存用例 | net9.0 | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

本 Task 尚未开 worktree；资源处置在实现完成后登记。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
