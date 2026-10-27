---
id: READER-PROGRESS-1
title: 阅读进度保存接线
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: avalonia-spike
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/READER-PROGRESS-1
worktree: G:/CODEX/New Manga.workspace/worktrees/READER-PROGRESS-1
integration_commit: null
delivery_head: 10a0308c13a11c8be4f75967b48dbdb051116397
canonical_evidence_status: complete
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

- [x] **AC1 保存**：翻页/关闭阅读器时调用 Core 进度保存命令（参数/语义对齐旧壳），并在下次打开同一本书时恢复到上次页；失败不阻塞 UI（typed 错误 + 降级）。→ **MET**：`SaveReadingProgress`（`chapter_id`+`mode`+`page_id`，`scroll_offset_y`/`elapsed_seconds_delta` 仅在有效时发送）在翻页、离开阅读器页、关闭主窗/沉浸窗时触发；重开用 `GetReaderProjection(start_position=resume)` 恢复；失败映射 `NotReady`/`ReadOnly`/`Failed(code)`，UI 继续可用。证据：`verification/READER-PROGRESS-1/live-evidence.json`（真机 resume 命中）、`test/summary.json`（131/131）。
- [x] **AC2 边界**：多书独立进度；进度越界（页数变少）时钳制；只读模式/无 Core 时不写。→ **MET**：多书按 (book,chapter,mode) 独立 + 页数钳制（`ReaderBookData.FromProjection` + Core `_remap`）+ 只读 Host 直接 `HOST_READ_ONLY` 不发 Core 请求 + 无 Core `HOST_NOT_READY`。证据：`ReaderProgressTests`（18 项）、`HostReaderProgressIntegrationTests`（只读/未知页）、`live-evidence.json.assertions`。
- [x] **AC3 测试**：Avalonia.Headless 覆盖「打开→翻页→关闭→重开恢复」；真机用 BOOK-FIXTURE 数据根验证一次。→ **MET**：headless `ReaderProgressTests`；真机两会话（首启翻页→保存→关闭；重启→resume 到第 3 页且恢复过程零写入）。证据：`screens/01-bookshelf-session-a.png`、`screens/02-reader-restored-page.png`、`runtime-logs/wire-*.ndjson`、`runtime-logs/reading-progress-session-{a,b}.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线无新增失败。→ **MET**：test.ps1 **131/131 passed, 0 skipped**；vitest **60 files / 567 tests**；pytest **3F/2739P/9S**（与基线一致）。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/READER-PROGRESS-1.md` PASS；下方 11 条 Canonical Evidence pin；`doc/handoffs/READER-PROGRESS-1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/READER-PROGRESS-1/**`、workspace。

## 禁止范围

不改协议/Host 契约语义、不改 Python Core、不改旧壳、不 push、不 gc/prune。

## 实现摘要

- CoreClient：`GetReaderProjection(start_position)`/`SaveReadingProgressAsync`/`ReadingProgressSnapshot`；跳过 Core 事件帧（`ReadingProgressChanged`）避免 `INVALID_RESPONSE`。
- Host：`SaveReadingProgressAsync` 写权限门 + 与页图读共用串行门。
- App：ReaderPage 进度 sink、翻页/滚动/离开/关闭 flush、elapsed 仅成功后重置、重复同位置合并、恢复期间抑制滚动写入；主窗/沉浸窗接线；恢复页钳制。
- 测试：App +18、Host +3（真 sidecar，BOOK-FIXTURE 副本）；脚本 `test.ps1 -EvidenceDirectory`、`start-book-fixture.ps1 -ExtraArgs`。
- 说明：worktree 实际从释放提交 `b50ab8fc5` 建立（含本任务卡与 AD-002 文档），任务卡冻结 base 仍记 `230164c5c`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| RP1-TEST-SUMMARY | AC4 | verification/READER-PROGRESS-1/test/summary.json | 10a0308c13a11c8be4f75967b48dbdb051116397 | 169341da73be2f8e1c6bc8e6bf09e5ab345b19533b8a9de8d19ab9c6d1a94e7e | CANONICAL |
| RP1-TEST-LOG | AC4 | verification/READER-PROGRESS-1/test/dotnet-test-Debug.log | 10a0308c13a11c8be4f75967b48dbdb051116397 | 3d1023d78058774a6cb4ee442823cb65c27076786a3ccdff180ef8771f3638f8 | CANONICAL |
| RP1-VITEST | AC4 | verification/READER-PROGRESS-1/test/vitest.log | 10a0308c13a11c8be4f75967b48dbdb051116397 | 7ef01bf912803e8f0f8f57f55259eb1589377f85372abc15e2a7cbe9047b03da | CANONICAL |
| RP1-PYTEST | AC4 | verification/READER-PROGRESS-1/test/pytest.log | 10a0308c13a11c8be4f75967b48dbdb051116397 | 75d513c1a821fc6f742ff897a266f81dba1d1b37ad23623704ec2d6b99d921c9 | CANONICAL |
| RP1-LIVE | AC1/AC2/AC3 | verification/READER-PROGRESS-1/live-evidence.json | 10a0308c13a11c8be4f75967b48dbdb051116397 | 177e701a4c51446d01d4d9c29a027c809f93339f91fc392b82957095387cdf84 | CANONICAL |
| RP1-SHOT-A | AC1/AC3 | verification/READER-PROGRESS-1/screens/01-bookshelf-session-a.png | 10a0308c13a11c8be4f75967b48dbdb051116397 | ddb52d02dd8d4e668db320a406d0ae8ee898486062e4dc0ab081ae73f4208b47 | CANONICAL |
| RP1-SHOT-B | AC1/AC3 | verification/READER-PROGRESS-1/screens/02-reader-restored-page.png | 10a0308c13a11c8be4f75967b48dbdb051116397 | 586a631362bd6fb88b1c6d592124e97db81b4bc2212206e0836afd9001ce99cb | CANONICAL |
| RP1-WIRE-B | AC1/AC3 | verification/READER-PROGRESS-1/runtime-logs/wire-session-b-only.ndjson | 10a0308c13a11c8be4f75967b48dbdb051116397 | 9c8caa1b86860e6ea6be748e81ef1edf6a070b10008aac751430156d3d5d934a | CANONICAL |
| RP1-HOSTLOG | AC1/AC3 | verification/READER-PROGRESS-1/runtime-logs/host.log | 10a0308c13a11c8be4f75967b48dbdb051116397 | fe0ab651ae7778d3c5564fe003c3c082a458dbcdf99faf29aec5a8b638fdf95f | CANONICAL |
| RP1-DB-B | AC1/AC2/AC3 | verification/READER-PROGRESS-1/runtime-logs/reading-progress-session-b.json | 10a0308c13a11c8be4f75967b48dbdb051116397 | ce17f67d52ff3e379b43ecbf4d01a093522f52692a939d3ac0be878fdca427a9 | CANONICAL |
| RP1-REPORT | AC5 | verification/READER-PROGRESS-1/REPORT.md | 10a0308c13a11c8be4f75967b48dbdb051116397 | 8ff7586d033453e1165fc64d5deaca15f649bdcd0786cfceee46824a0c917cf7 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/READER-PROGRESS-1 | `evidence/`（test/wire/screens/logs）+ `pkg/app`（29.4 MB 发布件，`core-sidecar` 为 junction）+ `isolated-data`（EXTERNAL，非 Git） | 2026-10-27 本卡收口时目录存在；`live-evidence.json` 引用其路径；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `10a0308c1`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（11 条 pin 指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用，未清理）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件）。
- 未关闭项及保留原因：真实 Core 多书/页数缩小未用真机复验（fixture 仅 1 书 1 章，headless+Core 单测覆盖）；`HostCommandRegistry` 的 `library_save_reading_progress` 分类仍为 NOT_SUPPORTED（探针 payload 错误，见 REPORT §5.3，需单独任务重分类）。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
