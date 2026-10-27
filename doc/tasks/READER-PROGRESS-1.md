---
id: READER-PROGRESS-1
title: 阅读进度保存接线
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: avalonia-spike
owner: null
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/READER-PROGRESS-1
worktree: G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-PROGRESS-1
allowed_paths:
  - doc/tasks/READER-PROGRESS-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/READER-PROGRESS-1/**
  - G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1/**
  - G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1/**
---

# READER-PROGRESS-1：阅读进度保存接线

## 背景

READER-LIBRARY-WIRE-1 已把阅读器接真实书库，但 `SaveReadingProgress` 未接线（S4 NS 批 PLANNED）。用户翻页/退出后进度不保存。

## Acceptance Criteria

- [ ] **AC1 保存**：翻页/关闭阅读器时调用 Core 进度保存命令（参数/语义对齐旧壳），并在下次打开同一本书时恢复到上次页；失败不阻塞 UI（typed 错误 + 降级）。
- [ ] **AC2 边界**：多书独立进度；进度越界（页数变少）时钳制；只读模式/无 Core 时不写。
- [ ] **AC3 测试**：Avalonia.Headless 覆盖「打开→翻页→关闭→重开恢复」；真机用 BOOK-FIXTURE 数据根验证一次。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/READER-PROGRESS-1/**`、workspace。

## 禁止范围

不改协议/Host 契约语义、不改 Python Core、不改旧壳、不 push、不 gc/prune。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
