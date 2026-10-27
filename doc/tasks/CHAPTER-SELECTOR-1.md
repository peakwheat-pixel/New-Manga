---
id: CHAPTER-SELECTOR-1
title: 多章选择器 + 多书入口
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: avalonia-spike
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/CHAPTER-SELECTOR-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1
integration_commit: 3904e88f7
delivery_head: 126d055183b6852259b8fd292ca1c408c5fdd1b6
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/CHAPTER-SELECTOR-1
allowed_paths:
  - doc/tasks/CHAPTER-SELECTOR-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/CHAPTER-SELECTOR-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CHAPTER-SELECTOR-1/**
---

# CHAPTER-SELECTOR-1：多章选择器 + 多书入口

> 交付状态：**ready-for-integration**（实现 `126d05518` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。

## 背景

READER-LIBRARY-WIRE-1 完成书库接线但固定第一本书第一章；多章/多书无法切换。

## Acceptance Criteria

- [x] **AC1 章节列表**：阅读器页提供章节列表（`list_chapters`），当前书/章可见，可切章并渲染对应页。→ **MET**：工具栏「书：… · 章：…」上下文 + `ChapterSelector` 下拉 + 上一章/下一章按钮（单章隐藏、边界禁用），`HostRuntime.ListChaptersAsync` 走真实 `list_chapters`；切章重新投影并更新页数/布局。真机：书 A 第 1 章 8 页 →「下一章」→ 第二章 4 页。证据：`verification/CHAPTER-SELECTOR-1/live-evidence.json`、`screens/02-*.png`、`screens/03-*.png`、`test/summary.json`（145/145）。
- [x] **AC2 多书入口**：书架多本书时从任一本进入都打开对应书（不再固定第一本）。→ **MET**：书卡双击与详情「进入阅读」均走 `OpenReaderForBookAsync(bookId)`；切书/切章前 flush 当前进度；任意 bookId/chapterId 走 `LoadReaderBookAsync`。真机：书架两本书，第二本 → 副本B 3 页。证据：`screens/01-*.png`、`screens/04-*.png`、`live-evidence.json`（两本书 + 各自 `list_chapters`/投影）。
- [x] **AC3 测试**：Headless 覆盖切章更新页数/投影、多书分别打开；真机用 BOOK-FIXTURE 数据根（可复制成两本）验证。→ **MET**：headless 12 项（`ReaderChapterSelectorTests`）+ Host 真 sidecar 2 项（`HostReaderChaptersIntegrationTests`：list_chapters 与投影一致、12 路并发读被串行化）；真机双书三章数据根（源 fixture 不动）。证据：`test/*`、`host/*.json`、`live-evidence.json`、`runtime-logs/`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 无新增失败。→ **MET**：test.ps1 **145/145 passed, 0 skipped**（coreclient 40 / host 42 / app 63；上卡 131 + 本轮 14）；vitest **60 files / 567 tests**；pytest **3F/2739P/9S**（与基线一致）。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CHAPTER-SELECTOR-1.md` PASS；下方 14 条 Canonical Evidence pin；`doc/handoffs/CHAPTER-SELECTOR-1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/CHAPTER-SELECTOR-1/**`、workspace。

## 禁止范围

不改协议/Host 契约语义、不改 Python Core、不改旧壳、不 push、不 gc/prune。

## 实现摘要

- Host：`ListChaptersAsync`/`GetReaderProjectionAsync` 统一走 `_readerIoGate`（避免与页图读并发串响应）。
- App：阅读器工具栏 Grid（两行上下文 + 章节下拉 + 上下章 + 沉浸），`ChapterSelectionRequested` → 主窗 `OpenReaderForBookAsync(bookId, chapterId)`；书架书卡双击/详情「进入阅读」→ 该书 `bookId`。
- 交互修复（真机发现）：只有落在页图/webtoon 栈上的按压才翻页（工具栏/下拉/滚动条不再误翻页）；工具栏按钮在黑色阅读器上用主题色保证可读；章节标签不再重复「第 N 章」前缀。
- 测试：App +12、Host +2；`FakeHostController` 支持多书/多章脚本。
- 说明：worktree 从 READER-PROGRESS-1 delivery head `10a0308c1` 建立；任务卡冻结 base 仍记 `230164c5c`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
| C1 | AC3 | verification/CHAPTER-SELECTOR-1/runtime-logs/chapter-selector-data.py | 126d05518 | 67902e4e1472a17b4bd24b9380e3fea2c5d4c8d43d55b02a9615c01732c96246 | CANONICAL |
| C2 | AC3 | verification/CHAPTER-SELECTOR-1/runtime-logs/core-service.stderr.log | 126d05518 | b349b8ca25b59fb9058a031070d77883b405b3e60d33062fca6e1b4ee94f0d21 | CANONICAL |
| C3 | AC3 | verification/CHAPTER-SELECTOR-1/runtime-logs/wire-host-bridge.ndjson | 126d05518 | ff61279f90a4cc9551f177f0146deed4e65768080c2b7a64ff52b798814b8846 | CANONICAL |
| C4 | AC3 | verification/CHAPTER-SELECTOR-1/test/results-app.trx | 126d05518 | 4f99cda00a2969c3573e043a04b3a5dee71150107b2010da9c38c16820c8448d | CANONICAL |
| C5 | AC3 | verification/CHAPTER-SELECTOR-1/test/results-coreclient.trx | 126d05518 | f94155d2e0a0792011dc9fef67871be5e7e24217d1a9246080291092f3dbbee1 | CANONICAL |
| C6 | AC3 | verification/CHAPTER-SELECTOR-1/test/results-host.trx | 126d05518 | 21f23b0539a501c3631da79e9c7c55ca06b2e31b45240000b2cb55aebe602376 | CANONICAL |
| C7 | AC3 | verification/CHAPTER-SELECTOR-1/test/test.ps1-final.log | 126d05518 | 0a393f2d1c9bac6f1a2d2622dc4cf4c0b6522aa2bf0b2369deea5f9eb6d67bbc | CANONICAL |
|---|---|---|---|---|---|
| CS1-TEST-SUMMARY | AC4 | verification/CHAPTER-SELECTOR-1/test/summary.json | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 499f582b1f63c71d1f250c01ae3b7ffccbe73514c001ba75f5a47411c72f8bd4 | CANONICAL |
| CS1-TEST-LOG | AC4 | verification/CHAPTER-SELECTOR-1/test/dotnet-test-Debug.log | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | e182d609fdfe99dc5ebe49767725862d05bfd040d02ee0c8795af74110761fc7 | CANONICAL |
| CS1-VITEST | AC4 | verification/CHAPTER-SELECTOR-1/test/vitest.log | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 44f2c23b5e50b8e5e9c07deb0584053f9b842a9e6a676a1b0ac0d3466691342d | CANONICAL |
| CS1-PYTEST | AC4 | verification/CHAPTER-SELECTOR-1/test/pytest.log | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | f4159c7ebbb0168c28b8d28f09f4875e1ff645d2d60151d818ccf2881ecf6870 | CANONICAL |
| CS1-LIVE | AC1/AC2/AC3 | verification/CHAPTER-SELECTOR-1/live-evidence.json | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | bf578e0146f759e92eeaeece48900f5b8c610b6bc61d4db04598668b3af7881d | CANONICAL |
| CS1-SHOT-BOOKSHELF | AC2/AC3 | verification/CHAPTER-SELECTOR-1/screens/01-bookshelf-two-books.png | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | e5e795835b6c10c16ab4040d33473dfaa7bcf994327eeb469ab58154bd3cc300 | CANONICAL |
| CS1-SHOT-SELECTOR | AC1/AC3 | verification/CHAPTER-SELECTOR-1/screens/02-reader-chapter-selector.png | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 40b49bfcbbc041632d269e320e02c2b025c324eae7670cd5c02d30fba68da1d7 | CANONICAL |
| CS1-SHOT-CH2 | AC1/AC3 | verification/CHAPTER-SELECTOR-1/screens/03-reader-chapter-2.png | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | b4cdff0959a473e05cfee04f2c47769ec5db90d9277537dee2d854253236b9af | CANONICAL |
| CS1-SHOT-BOOKB | AC2/AC3 | verification/CHAPTER-SELECTOR-1/screens/04-reader-book-b.png | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 8fc72c2d9303cfbf7b8947fbc8875d4458f26d22d023dba4eee1c584cf41bc62 | CANONICAL |
| CS1-WIRE | AC1/AC2/AC3 | verification/CHAPTER-SELECTOR-1/runtime-logs/wire-real-machine.ndjson | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 80ffe318484ec4589917b3de19a2255baf828a9c5e0113622bd1b1b7f7d0aa72 | CANONICAL |
| CS1-HOSTLOG | AC1/AC3 | verification/CHAPTER-SELECTOR-1/runtime-logs/host.log | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 28ffb217f543ad7cf719489fe6928cd2a466b419e05c8a27ec09fc3f45e6fd31 | CANONICAL |
| CS1-HOST-LIST | AC1/AC3 | verification/CHAPTER-SELECTOR-1/host/reader-chapters-list.json | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 633bd583b0f6cdee8dd8a97a24817c403c7b2bba7d9652512cc432ceb30f8a0d | CANONICAL |
| CS1-HOST-CONCURRENT | AC1/AC3 | verification/CHAPTER-SELECTOR-1/host/reader-chapters-concurrent.json | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 5d7eb0068de1e90b5c4b99cf6307b7701f5ffa88fcf2a62244d354b8bb642615 | CANONICAL |
| CS1-REPORT | AC5 | verification/CHAPTER-SELECTOR-1/REPORT.md | 126d055183b6852259b8fd292ca1c408c5fdd1b6 | 09b4a381e87b280685d242cd1cd7013796a38f6818b919066f5308ad00b4f704 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CHAPTER-SELECTOR-1 | `evidence/`（测试/wire/screens/host）+ `pkg/app`（29.4 MB 发布件，`core-sidecar` 为 junction）+ `isolated-data`（EXTERNAL 双书三章测试根，源 fixture 未改） | 2026-10-27 本卡收口时目录存在；`live-evidence.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `126d05518`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（14 条 pin 指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用，未清理）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；FX 数据根为 workspace 副本，源 BOOK-FIXTURE 未改动）。
- 未关闭项及保留原因：真机未重复「书卡双击」手势与 ComboBox 弹层展开（自动化无法稳定注入；同一代码路径由 headless 覆盖，真机用详情按钮/上下章按钮走同一 `OpenReaderRequested`/`ChapterSelectionRequested` 路径）；沉浸窗内不提供切章；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（含 3 个真实缺陷修复）

- AC1：阅读器工具栏「书/章」上下文 + 章节下拉（真实 list_chapters）+ 上一/下一章（单章隐藏、边界禁用）；切章重新投影。真机：书 A 第 1 章 8 页 →「下一章」→ 第二章 4 页（wire GetReaderProjection chapter_id 更替）。
- AC2：书卡双击/详情「进入阅读」打开**该** bookId（不再固定第一本第一章）；切书/切章前 flush 进度。真机：书架 2 本 → 第二本 3 页。
- AC3：headless 12 项（ReaderChapterSelectorTests）+ Host 真 sidecar 2 项；真机双书三章数据根（BOOK-FIXTURE 副本扩展，源 fixture 未改）；证据 erification/CHAPTER-SELECTOR-1/**。
- AC4：DSH 复跑 scripts/test.ps1 → 见执行记录（实现方报 **145/145**：40/42/63）；vitest 60/567；pytest 3F/2739P/9S。
- AC5：check.ps1 -TaskPath PASS；14 条 64-hex pin；Handoff。
- **真机额外修复 3 个真实缺陷**：① 工具栏/下拉/滚动条点击误翻页（改为仅页图/webtoon 栈按压翻页）；② 工具栏按钮在黑色 chrome 上不可读（主题化）；③ 章标签重复「第 N 章」前缀。
- 遗留（记录不阻塞）：① ComboBox 弹层/书卡双击真机注入未覆盖（独立 popup 自动化不稳定；同路径按钮入口已真机验证、headless 覆盖事件）；② 章节列表无分页/百章性能未测；③ 沉浸窗不切章；④ 需独立 Review。
- 集成：3904e88f7。
