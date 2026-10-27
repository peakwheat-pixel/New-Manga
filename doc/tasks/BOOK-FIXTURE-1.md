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
base_commit: c6934cba5
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

- [x] **AC1 一键建书**：脚本（`apps/desktop-avalonia/scripts/` 下）在隔离数据根（env 重定向）里创建 1 本书，页面取自 `test_assets/comic_golden_suite/日漫_JA/**`（只读引用，不复制进仓库）；可重复执行且幂等（重复运行不重复建书或给出明确跳过）。→ **MET**：`new-test-book.ps1` + `new_test_book.py`；book `14340ddad0ed472fbe687fe12340c5d8`、8 页；第二次运行 `status=existing`（同 book_id/页数）。
- [x] **AC2 数据校验**：`list_books` 返回该书、页数 >0、可解析页面尺寸；证据 JSON 落 `verification/BOOK-FIXTURE-1/`。→ **MET**：冻结 core_service 协议复核 `ListBooks` page_count=8、`GetReaderProjection` 8 页均 1200×1660（可解析）、layout=webtoon_vertical；证据 `book-fixture.json`。
- [ ] **AC3 供复测**：输出「后续如何用该书跑 webtoon 工作集与 Esc/H」的一页说明（脚本参数/数据根/清理方法）。→ **PARTIAL**：`RETEST.md` 已交付（数据根/启动参数/清理/webtoon 工作集步骤 + app-level smoke PASS）；**沉浸 Esc/H 因产品缺口不可达**（阅读器页绑 fixture、`ReaderWindow` 全仓无调用点；已回报 Lead，建议 `READER-LIBRARY-WIRE-1`），非加书可解。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；不污染真实 `%APPDATA%`。→ **MET**：test.ps1 102/102；pytest 3F/2739P/9S（0 新增）；真实 `%APPDATA%` 前后指纹一致（脚本断言）。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff。→ **MET**：pin 见下；`doc/handoffs/BOOK-FIXTURE-1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/scripts/**`、本卡、STATUS/PLAN/LEDGER、`verification/BOOK-FIXTURE-1/**`、workspace（含隔离数据根）。

## 禁止范围

不改产品源码（除非发现必要缺陷，需先回报 DSH）；不改协议/Host 契约；不碰真实用户数据；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `pwsh -File apps/desktop-avalonia/scripts/new-test-book.ps1 -PageLimit 8` → 冻结 core_service 协议校验 | 隔离 env + 无标签 sidecar 副本 | **PASS**：建书 8 页；ListBooks/GetReaderProjection 通过；幂等重跑 existing | `book-fixture.json`、`book-fixture-rerun.json` |
| AC3 | `start-book-fixture.ps1 -NoLaunch` / App `--data-root` smoke | FINAL-VALIDATION-1 发布件 | **PARTIAL**：说明+app smoke PASS（窗口/exit0/无残留）；Esc/H 因产品缺口不可达 | `RETEST.md`、`app-smoke.json` |
| AC4 | `python -m pytest -q`；`scripts/test.ps1`；真实 %APPDATA% 指纹 | 全量 | **PASS**：pytest 3F/2739P/9S；test.ps1 102/102；%APPDATA% 未变 | `pytest.log`、`scripts-test.log`、`book-fixture*.json` |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1 | `isolated-data/`（8.1 MB：library.db + managed 8 页 + catalog/derived/_env） | 建书/复测引用；不触碰真实 %APPDATA%；关闭时按 workspace 裁决保留或清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
