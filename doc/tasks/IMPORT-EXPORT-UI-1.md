---
id: IMPORT-EXPORT-UI-1
title: 导入/导出 UI 入口（选择器+进度+历史+取消）
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: route-research
reviewer: dsh
depends_on: []
base_commit: 49c9e7f24
branch: task/IMPORT-EXPORT-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1
integration_commit: null
delivery_head: __DELIVERY_HEAD__
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/IMPORT-EXPORT-UI-1
allowed_paths:
  - doc/tasks/IMPORT-EXPORT-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/IMPORT-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/IMPORT-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1/**
---

# IMPORT-EXPORT-UI-1：导入/导出 UI 入口

## 背景

命令面 66/0 已全实现；`library_import_file/folder`（Host grant 链）与 `StartExport`/`GetExportSnapshot`/`GetExportHistory`/`CancelExport`/`RevealExportFolder` 均已真跑验证（EXPORT-E2E-CLOSE-1），但用户没有 UI 入口。本卡补齐书架/工作台的导入入口与阅读器的导出流程，并用 headless + 真机截图证明命令参数与状态迁移。

分支基于 HEAD `558a48a76`（Lead 指示；卡面 base `49c9e7f24`），交付前 rebase 到 `b874b2cf7`（READER-SELECTOR-UI-1 先落地；无冲突）。Handoff：`doc/handoffs/IMPORT-EXPORT-UI-1-handoff.md`。

## Acceptance Criteria

- [x] **AC1 导入**：书架 header 与工作台左栏提供「导入文件」「导入文件夹」，经系统选择器（Avalonia StorageProvider）→ 目标书/章/重复策略 → Host grant 链（`RegisterImportSource`→`ImportPages`）→ 不确定进度 + typed 结果文本 → 成功后刷新书架。真机：已导入 1 个文件、书架 8 页→9 页。证据 `real-run.json`、`evidence/real-run/*.ndjson`、`evidence/headless/import-export-ui/import-*.json`。<<MET>>
- [x] **AC2 导出**：阅读器「导出」→ 对当前书构造 translated 页列表并 `StartExport`（Host `RegisterExportTarget` grant → StartExport）→ `GetExportSnapshot` 轮询进度条/状态 → 完成显示产物路径 + sha256 → `GetExportHistory` 列出真实历史 → 可「取消导出」（pending/running）→「打开导出目录」（Host shell action）。真机：exp-583026330d98、ZIP 7,070,562B、sha256 `cb4d30db…`、已打开导出目录。证据 `real-run.json`、`artifact-verify.json`、`artifacts/`、`evidence/headless/import-export-ui/export-*.json`。<<MET>>
- [x] **AC3 测试**：headless 10 例覆盖命令参数（import file/folder keys、start_export 六字段无 target_ref、export_id）与状态迁移（running→completed、cancel、typed 拒绝、无翻译页、picker 取消、工作台入口）；真机截图 11 张（书架导入入口/阅读器导出入口/导出面板/完成/打开目录/第二次导出/工作台入口/系统选择器/选择器填入/导入面板/导入完成）。<<MET>>
- [x] **AC4 回归**：`test.ps1` **225/225 passed, 0 skipped**（coreclient 61 / host 55 / app 109，含本卡 10 例）；vitest **60 files/567 tests**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增）。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex sha256 pin；Handoff + Record Decision（REPORT §6）。<<MET>>

## 实现摘要

| 文件 | 改动 |
|---|---|
| `Services/ImportExportContracts.cs`（新增） | typed ImportOutcome / ExportStartInfo / ExportSnapshotInfo / ExportHistoryEntry；`Utf8JsonWriter` 构造 wire payload（import file/folder、start_export 六字段、export_id、translated 投影）；状态中文文案、默认 ZIP 文件名清洗 |
| `Services/FilePickerGateway.cs`（新增） | `IFilePickerGateway` seam + Avalonia StorageProvider 实现（打开文件多选/选择文件夹/另存为）；headless fake 驱动同一流程 |
| `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs` | 导入（Host grant 链：`HostGrantCoordinator.ImportAsync`）、导出（`StartExportAsync` grant 链）、translated 页发现、snapshot/history/cancel 命令面、reveal shell action；全部 typed outcome，不向 UI 抛异常 |
| `Views/ImportExportPanels.cs`（新增） | `ImportPanel`：目标书/章/重复策略 + 文件选择结果 + 不确定进度 + typed 结果；`ExportPanel`：可导出页数 + 开始/取消/打开目录 + 进度条 + 历史列表（真实记录） |
| `Views/Pages.cs`（BookshelfPage） | header「导入文件/导入文件夹」+ ImportPanel overlay；成功后刷新书架 |
| `Views/ReaderWorkbenchPages.cs` | WorkbenchPage 左栏导入入口；ReaderPage toolbar「导出」+ ExportPanel（仅真实书库书可见） |
| `Views/MainWindow.axaml.cs` | 统一 picker 注入与三页接线（可选 picker 参数便于 headless） |
| `tests/NewManga.App.Tests/ImportExportUiTests.cs`（新增） | 10 个 headless 用例 + 6 份证据 JSON |

## 实际测试记录

| 套件 | 命令 | 结果 |
|---|---|---|
| 全量 .NET | `apps/desktop-avalonia/scripts/test.ps1` | **TEST PASS 225/225（61/55/109），0 skipped** |
| 导入/导出 UI（headless） | `dotnet test ...App.Tests --filter FullyQualifiedName~ImportExportUiTests` | **10/10 passed**；证据 JSON 6 份 |
| vitest | `apps/desktop/frontend: npx vitest run` | **60 files / 567 tests passed** |
| pytest | `python -m pytest -q` | **3F/2772P/9S**（基线同组失败，0 新增） |
| 真机 | Debug App exe（隔离 data root + REPACK-2 models sidecar + `--parity`） | 导入 1 文件（8→9 页）；导出 ZIP 7,070,562B sha cb4d30db…；打开导出目录成功；11 张截图 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1 | AC3/AC4 | verification/IMPORT-EXPORT-UI-1/REPORT.md | - | 6ab315ab8d15ed5b270c955a88c969a6ee55820112684eb24d3c46c0f6a40abd | CANONICAL |
| E2 | AC1/AC2/AC3 | verification/IMPORT-EXPORT-UI-1/real-run.json | - | ae2c6aa41003c18716a2c5cc047c0d18cc5813ace0a9dcc1dd5945d204318b78 | CANONICAL |
| E3 | AC2 | verification/IMPORT-EXPORT-UI-1/artifact-verify.json | - | f5260ba44fca6d9e569636268ceff9f768941dbcc0de8d50cdbfde0776b9d251 | CANONICAL |
| E4 | AC2 | verification/IMPORT-EXPORT-UI-1/artifacts/ui-export-exp-583026330d98.zip | - | cb4d30db7c61f73169c74ca3a36b21e82df196333a44df36b001bb67696788c1 | CANONICAL |
| E5 | AC1/AC2/AC3 | verification/IMPORT-EXPORT-UI-1/evidence/real-run/core-service.ndjson | - | 547e80253a4cb407773671d33d29762b0bee2d5678f9d0df57d24f650f322c6f | CANONICAL |
| E6 | AC1/AC2 | verification/IMPORT-EXPORT-UI-1/evidence/real-run/host-bridge.ndjson | - | 6aaf1aaa092db6a7c9d5841ed9ed63b6b2d48ef34ee22c4774a0d3453eafdaeb | CANONICAL |
| E7 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/real-run/host.log | - | eec16e6bc50f2fd622f8d1a79eb0cfd5ce1c01f5bed155e8523db4e620c0aa02 | CANONICAL |
| E8 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/test-ps1.log | - | f26b08ed63c4a3f541d74e145f6139c73acb64218efa7de3c17127b121613d53 | CANONICAL |
| E9 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/dotnet/summary.json | - | 1d2a16b67165c21030f69445ece1b2f403a6b6959ce5324d84ccd2dff56ee80d | CANONICAL |
| E10 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/dotnet/results-app.trx | - | ca05deea3c2eedc24325b9aee5bf36e415da4e9f08682b022e17fe1f651ad94d | CANONICAL |
| E11 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/dotnet/dotnet-test-Debug.log | - | 5a7c12d34d7487f9a98ece4ceaeb8fd9895fa0aad6d5c3b361182f9bff7163b5 | CANONICAL |
| E12 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/vitest.log | - | a38874e07b3c6fb6feb0d2b407db5d8bc600a722d93148a65e514fd9a1bc7588 | CANONICAL |
| E13 | AC4 | verification/IMPORT-EXPORT-UI-1/evidence/pytest.log | - | bd5a66acf40f811fd4b53f0c31d1c31f28c42c5fafd38c65f2732278ab5ae04d | CANONICAL |
| E14 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/export-cancel.json | - | 5439b1fc170ca6538aea3bbb7d7a10e217a212b10cc1019e47a08cfec73c4032 | CANONICAL |
| E15 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/export-flow.json | - | b1cbb92151d5e5f53831c1414189e774cd5d0a4dc1314a7354cd225c5914228d | CANONICAL |
| E16 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/export-reveal.json | - | 380479633728d51171a796d46f230c30175f456412e00c995b802167ed3a723f | CANONICAL |
| E17 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/import-files.json | - | ed43a9830da85785ad1f4b31d06f715e54a597854e5763e60081e323b4b91fe6 | CANONICAL |
| E18 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/import-folder.json | - | 5223bdb50839f91259dfb005e302319915a479aa2d32bcc425d4683a3fd08982 | CANONICAL |
| E19 | AC3 | IMPORT-EXPORT-UI-1/evidence/headless/import-export-ui/payload-contract.json | - | d34c1f5bd62207bdc895abc66df0218359099dc0a3f6e97b43b16cf97bc1fec6 | CANONICAL |
| E20 | AC3 | IMPORT-EXPORT-UI-1/screens/01-bookshelf-import-entries.png | - | 2827224aa6b9341b1d34a8665cd264520d0da3840bdb1bb7b7ae6d4bbd3ad929 | CANONICAL |
| E21 | AC3 | IMPORT-EXPORT-UI-1/screens/02-reader-export-entry.png | - | ba3f635fb1887404b979aebc235be12b8c2ba20a0990607da97c21f8820d904a | CANONICAL |
| E22 | AC3 | IMPORT-EXPORT-UI-1/screens/03-export-ready.png | - | 4c0765afca8c359ba0bce527c2eb6a7e9c423f3db524b829ccc58dc9e896a295 | CANONICAL |
| E23 | AC3 | IMPORT-EXPORT-UI-1/screens/04-export-completed.png | - | 8dbe4f7d98f763bffea71f3de84254f1efbfa9b22fd233dcb7fe988c7190c7a1 | CANONICAL |
| E24 | AC3 | IMPORT-EXPORT-UI-1/screens/05-export-revealed.png | - | 0a7d08721349e8aa76c46538741f0e7970613b6315882012f39d2f09e7d033b8 | CANONICAL |
| E25 | AC3 | IMPORT-EXPORT-UI-1/screens/06-export-second-run.png | - | 98638db807ae4ade6e7d05546fe54493b8b776cc93633d4a07517bf3ed9bcd18 | CANONICAL |
| E26 | AC3 | IMPORT-EXPORT-UI-1/screens/07-workbench-import-entry.png | - | b4689bdf87001f5c6df46fb2c63d02347570abae2e586dfbf06fe539c6ed215d | CANONICAL |
| E27 | AC3 | IMPORT-EXPORT-UI-1/screens/08-picker-dialog.png | - | f11c3ca25b86e01488e2f08db83e0becaab31a15221c1c98db8cc366c4786a52 | CANONICAL |
| E28 | AC3 | IMPORT-EXPORT-UI-1/screens/09-picker-filled.png | - | e764a78015d89fbf6b8b0c8e114212ceec5c5f3bdfae8369d826b1a250ba8440 | CANONICAL |
| E29 | AC3 | IMPORT-EXPORT-UI-1/screens/10-import-panel.png | - | f56036cf0716e153eb66339660e9e67bd02a1d238857d1b2812efe9aad14acfd | CANONICAL |
| E30 | AC3 | IMPORT-EXPORT-UI-1/screens/11-import-completed.png | - | 859a8aba8d9012c550f88b9b9201cdb40d8af6652f5af26e74d57f0033e48a89 | CANONICAL |
| E31 | AC2 | apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs | - | 0b9b72a14947ee97d8141aabc2092ba2eccfcf4257d201bff4175257e94da671 | SOURCE_PIN |
| E32 | AC1/AC2 | apps/desktop-avalonia/src/NewManga.App/Services/FilePickerGateway.cs | - | 3301eb6ef781cf88877102d03994ae8abd9bc790b46367376f5f15781284838b | SOURCE_PIN |
| E33 | AC1/AC2 | apps/desktop-avalonia/src/NewManga.App/Views/ImportExportPanels.cs | - | 96f155f0477f541da585f1a9f16d481c337079b2937fdfd0b85a6d0f31f34b8a | SOURCE_PIN |
| E34 | AC3 | apps/desktop-avalonia/tests/NewManga.App.Tests/ImportExportUiTests.cs | - | c7358c1646890e3e43c6e6fc305b414a8c01f2c33b5324a9cc6c6b329a4bd00d | SOURCE_PIN |
| E35 | AC1/AC2 | apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs | - | 1f18dd51ae307e379a880687b0febba0c1a9fba805ca1017d1a815825176aa87 | SOURCE_PIN |
| E36 | AC1 | apps/desktop-avalonia/src/NewManga.App/Views/Pages.cs | - | 4392b909f36ceaaf0babaa00917f0a9604219f5c4eef2052a630f9daeafddde8 | SOURCE_PIN |
| E37 | AC2 | apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs | - | 34c172415ed4dd887482b86c25594b6ab681f3228e1ee820ffadee36bf486877 | SOURCE_PIN |
| E38 | AC1/AC2 | apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs | - | 9ca4d691e17323c795b4e136d7f8ef97d92c5177effb13620fcbb9aaac15d13d | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/IMPORT-EXPORT-UI-1 | PRESERVE_REFERENCED | 原路径 | `screenshot-root`（REPACK-2 completed-run 私有副本）、`app-logs/`、`dotnet-evidence-final/`、`import-src/`、`screens/` | 保留真机运行现场与 dotnet 证据；交付后关闭 App、数据根保留只读。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2 | PRESERVE_REFERENCED | 原路径 | sidecar models core_service sha `c5531930…` | 真机 sidecar 只读消费；归属 RELEASE-REPACK-2。 |
| artifact | verification/IMPORT-EXPORT-UI-1/artifacts/ui-export-exp-583026330d98.zip | PRESERVE | 同路径 | sha256 `cb4d30db…` | 真机 UI 导出产物（7,070,562B），已独立复算。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（31 条 sha256 pin，含 8 条 SOURCE_PIN）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
