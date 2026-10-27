---
id: BOOK-FIXTURE-1
title: 隔离数据根导入测试书（webtoon/Esc-H 复测前置）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: []
base_commit: 4deb9ef3e
branch: task/BOOK-FIXTURE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/BOOK-FIXTURE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/BOOK-FIXTURE-1
allowed_paths:
  - doc/tasks/BOOK-FIXTURE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/BOOK-FIXTURE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/BOOK-FIXTURE-1/**
---

# BOOK-FIXTURE-1：隔离数据根导入测试书（供 webtoon/Esc-H 复测）

## 背景

真机核验 AC3（webtoon 工作集）与 AC5（沉浸 Esc/H）无法验证，因隔离数据根没有书；沉浸窗口只在打开真实页面时创建（`ReaderWorkbenchPages.cs:455-487`）。

## Acceptance Criteria

- [ ] **AC1 一键建书**：脚本（`apps/desktop-avalonia/scripts/` 下）在隔离数据根（env 重定向）里创建 1 本书，页面取自 `test_assets/comic_golden_suite/日漫_JA/**`（只读引用，不复制进仓库）；可重复执行且幂等（重复运行不重复建书或给出明确跳过）。
- [ ] **AC2 数据校验**：`list_books` 返回该书、页数 >0、可解析页面尺寸；证据 JSON 落 `verification/BOOK-FIXTURE-1/`。
- [ ] **AC3 供复测**：输出「后续如何用该书跑 webtoon 工作集与 Esc/H」的一页说明（脚本参数/数据根/清理方法）。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；不污染真实 `%APPDATA%`。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/scripts/**`、本卡、STATUS/PLAN/LEDGER、`verification/BOOK-FIXTURE-1/**`、workspace（含隔离数据根）。

## 禁止范围

不改产品源码（除非发现必要缺陷，需先回报 DSH）；不改协议/Host 契约；不碰真实用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 运行脚本 → list_books 校验 | 隔离 env、无标签副本 | NOT_RUN | 待填 |
| AC3/AC4 | 说明 + 全量回归 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
