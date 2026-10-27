---
id: BOOK-FIXTURE-1
title: 隔离数据根导入测试书（webtoon/Esc-H 复测前置）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: []
base_commit: c6934cba5
branch: task/BOOK-FIXTURE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/BOOK-FIXTURE-1
integration_commit: 377736213
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 一键建书**：脚本（`apps/desktop-avalonia/scripts/` 下）在隔离数据根（env 重定向）里创建 1 本书，页面取自 `test_assets/comic_golden_suite/日漫_JA/**`（只读引用，不复制进仓库）；可重复执行且幂等（重复运行不重复建书或给出明确跳过）。→ **MET**：`new-test-book.ps1` + `new_test_book.py`；book `14340ddad0ed472fbe687fe12340c5d8`、8 页；第二次运行 `status=existing`（同 book_id/页数）。 <<MET>>
- [x] **AC2 数据校验**：`list_books` 返回该书、页数 >0、可解析页面尺寸；证据 JSON 落 `verification/BOOK-FIXTURE-1/`。→ **MET**：冻结 core_service 协议复核 `ListBooks` page_count=8、`GetReaderProjection` 8 页均 1200×1660（可解析）、layout=webtoon_vertical；证据 `book-fixture.json`。 <<MET>>
- [x] **AC3 供复测**：输出「后续如何用该书跑 webtoon 工作集与 Esc/H」的一页说明（脚本参数/数据根/清理方法）。→ **PARTIAL**：`RETEST.md` 已交付（数据根/启动参数/清理/webtoon 工作集步骤 + app-level smoke PASS）；**沉浸 Esc/H 因产品缺口不可达**（阅读器页绑 fixture、`ReaderWindow` 全仓无调用点；已回报 Lead，建议 `READER-LIBRARY-WIRE-1`），非加书可解。 <<PARTIAL: 脚本+RETEST 说明+app smoke 已交付；沉浸 Esc/H 因产品缺口（阅读器未接书库、ReaderWindow 无实例化）不可达 → 转 READER-LIBRARY-WIRE-1>>
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；pytest 相对基线无新增失败；不污染真实 `%APPDATA%`。→ **MET**：test.ps1 102/102；pytest 3F/2739P/9S（0 新增）；真实 `%APPDATA%` 前后指纹一致（脚本断言）。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff。→ **MET**：pin 见下；`doc/handoffs/BOOK-FIXTURE-1-handoff.md`。 <<MET>>
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
| E-BF-REPORT | AC1–AC5 | `verification/BOOK-FIXTURE-1/REPORT.md` | `f0142fccd` | `9c9f879baf8d3233c38992c293c97df8e805a658f7e728387ce58817720d53cf` | CANONICAL |
| E-BF-RETEST | AC3 | `verification/BOOK-FIXTURE-1/RETEST.md` | `f0142fccd` | `e67dff71b79fe787dd2a613ce7d3980859be6eb91305d63945b9fa9cf7e7250c` | CANONICAL |
| E-BF-FIXTURE | AC1/AC2 | `verification/BOOK-FIXTURE-1/book-fixture.json` | `f0142fccd` | `4e809f8f227ee03461f68fbbb25b1a6e6300b9fc1f96abc7dac8f4c77745a879` | CANONICAL |
| E-BF-RERUN | AC1（幂等） | `verification/BOOK-FIXTURE-1/book-fixture-rerun.json` | `f0142fccd` | `bb5665ac36045829807564bc918eaa6f652e9631ebd493adb88b7d6a4095018e` | CANONICAL |
| E-BF-APPSMOKE | AC3/AC4 | `verification/BOOK-FIXTURE-1/app-smoke.json` | `f0142fccd` | `bcae98ddcab23e35138f73514d5b83025e69ef267582973a319b05117a920edb` | CANONICAL |
| E-BF-PYTEST | AC4 | `verification/BOOK-FIXTURE-1/pytest.log` | `f0142fccd` | `5acdf7e7f455f75367eafb0e438b46f1b556f6c0683ec0d88c039c729c57e816` | CANONICAL |
| E-BF-DOTNET | AC4 | `verification/BOOK-FIXTURE-1/scripts-test.log` | `f0142fccd` | `6aa2a76d5df7d7bf2d3b3d37fab0409f27a64b8aca9af8cb9f29011bbe1b664a` | CANONICAL |
| E-BF-HELPER | AC1 | `verification/BOOK-FIXTURE-1/new-test-book.helper.log` | `f0142fccd` | `89dadb79a1f4ed175254f623eaef61c390b71c2bc3ee18527d46bfbd32be3687` | CANONICAL |

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
## Review（DSH 集成复核，2026-10-27）— PASS（AC3 PARTIAL）

- 建书：book 14340ddad0ed472fbe687fe12340c5d8（8 页 1200×1660、webtoon_vertical、1 章），隔离根 8.1MB，二次运行 xisting 幂等。
- 校验：冻结 core_service 协议 2.3 复核 ListBooks/list_chapters/GetReaderProjection 全 PASS；发布件 --data-root smoke 命中隔离根、wire 2 次 ListBooks 含 book_id、exit 0、无残留。
- 真实 %APPDATA% 前后指纹一致（未污染）。
- 回归：DSH 复跑 scripts/test.ps1 **102/102**；pytest **3F/2739P/9S（0 新增）**。
- AC3 PARTIAL（接受）：脚本 + RETEST.md + smoke 已交付；沉浸 Esc/H 因**产品缺口**不可达（MainWindow.axaml.cs:66-72 阅读器绑 fixture；ReaderWorkbenchPages.cs:449-487 ReaderWindow 全仓无实例化）→ 已开 READER-LIBRARY-WIRE-1 承接。
- 集成：377736213；未 push。
