---
id: READER-LIBRARY-WIRE-1
title: 阅读器接真实书库 + 沉浸窗口入口（Esc/H/F 可达）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [BOOK-FIXTURE-1]
base_commit: 377736213
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/READER-LIBRARY-WIRE-1
allowed_paths:
  - doc/tasks/READER-LIBRARY-WIRE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/READER-LIBRARY-WIRE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1/**
---

# READER-LIBRARY-WIRE-1：阅读器接真实书库 + 沉浸入口

## 背景（BOOK-FIXTURE-1 发现的真实产品缺口）

- `MainWindow.axaml.cs:66-72`：「阅读器」页绑定 `ReaderFixtureLocator.TypographyPaths()` 的固定 fixture，**不接 `ListBooks` 的真实书**。
- `ReaderWindow`（沉浸窗：Esc 退出 / H 隐藏 HUD / F 切 fit，`Views/ReaderWorkbenchPages.cs:449-487`）全仓**无任何 `new ReaderWindow(...)` 调用** → Esc/H/F 当前**用户不可达**。
- 因此真机核验第 3 项（webtoon 工作集）与第 5 项（沉浸 Esc/H）无法在产品内完成。

## Acceptance Criteria

- [ ] **AC1 书库接线**：阅读器页从 Core `ListBooks`/`list_chapters`/`GetReaderProjection`（经 Host/CoreClient）取真实 book/chapter/pages 渲染；空库时显示空态（保留现有提示）。
- [ ] **AC2 沉浸入口**：从阅读器页可打开沉浸窗（如双击页面/按钮/快捷键），沉浸窗按 Esc 退出、H 隐藏 HUD、F 切换 fit、方向键翻页，**均有自动化测试**（Avalonia.Headless 可断言 Window 创建/关闭与状态）。
- [ ] **AC3 真机验证**：用 BOOK-FIXTURE-1 的数据根打开书 → 进入沉浸 → Esc 退出、H 隐藏 UI 各一次，截图 + 日志证据。
- [ ] **AC4 webtoon**：真实 8 页（1200×1660 webtoon_vertical）可滚动阅读；测量进程工作集峰值（目标 ≤1.5GB）并记录。
- [ ] **AC5 回归**：`scripts/test.ps1` 全绿；旧壳 vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/READER-LIBRARY-WIRE-1/**`、workspace。

## 禁止范围

不改协议/Host 契约、不改 Python Core、不改旧壳、不 push、不 gc/prune、不删除 fixture 回退路径（保留可切换）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | headless UI + 真 sidecar | 无标签副本 | NOT_RUN | 待填 |
| AC3/AC4 | 真机 + BOOK-FIXTURE 数据根 | Win11 | NOT_RUN | 待填 |
| AC5 | 全量回归 + 治理 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/READER-LIBRARY-WIRE-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

