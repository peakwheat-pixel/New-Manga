---
id: S4-CMD-BATCH-1
title: S4-A/B/C 命令接线（region 写 4 + reader 2）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_a2_extra
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/S4-CMD-BATCH-1
worktree: G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/S4-CMD-BATCH-1
allowed_paths:
  - doc/tasks/S4-CMD-BATCH-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/S4-CMD-BATCH-1/**
  - G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/**
  - G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1/**
---

# S4-CMD-BATCH-1：S4-A/B/C 命令接线（region 写 + reader 命令）

## 背景

S2 遗留 42 条 NS 中，S4-A/B/C 登记 10 条：region 写 4、reader 2、Run/Export 4（Run/Export 由 `RUN-EXPORT-E2E-1` 承接）。本任务做 **region 写 4 + reader 2 = 6 条**接线。

## Acceptance Criteria

- [ ] **AC1 清单**：从 S2 Handoff 与 parity 快照列出 S4-A/B/C 中 region 写与 reader 命令（预期 6 条），标注 Core 路由/参数/返回。
- [ ] **AC2 接线**：C# Host registry/dispatcher/domain service 实现；每条对冻结 sidecar **真实执行**断言（region 写需有效 target：用 BOOK-FIXTURE 数据根取真实 region/revision id）；不得把验证不了的标实现。
- [ ] **AC3 parity**：`extract-command-surface.py --check` 零漂移；快照相应命令 NOT_SUPPORTED→IMPLEMENTED；证据 `verification/S4-CMD-BATCH-1/**`。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 3F/2739P/9S 无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（region 写权限/只读门）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/S4-CMD-BATCH-1/**`、workspace。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 Host 契约语义/旧壳、不 push、不 gc/prune；与 `RUN-EXPORT-E2E-1` 并行时 registry 冲突以先落地者为准、后落地者 rebase。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
