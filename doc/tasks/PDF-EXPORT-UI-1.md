---
id: PDF-EXPORT-UI-1
title: PDF 导出 UI 选项（导出面板格式选择）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 2591ef028
branch: task/PDF-EXPORT-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1
integration_commit: 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95
delivery_head: 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/PDF-EXPORT-UI-1
allowed_paths:
  - doc/tasks/PDF-EXPORT-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/PDF-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1/**
---

# PDF-EXPORT-UI-1：PDF 导出 UI 选项

> 交付状态：**ready-for-integration**（实现 `6deefdcc3` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> 说明：卡面 base 记 `170878dc4`；按 DSH 指令分支从当前 HEAD **`2591ef028`** 创建。
> 主工作树中另一会话在途的 `ThemePack.cs` / `MainWindow.axaml*` 等改动未触碰、未提交（只按显式路径提交本卡文件）。

## 背景

Core 已支持 PDF 导出（`QtFreePdfComposer`：`image_only` 无损 RGB / `searchable_dual_layer` CJK 文本层），但导出 UI 面板只有 ZIP 图片包，PDF 用户不可达。本卡只补 UI 入口，未重实现 composer。

## Acceptance Criteria

- [x] **AC1 格式选择**：导出面板新增格式选项（ZIP 图片包 / PDF；PDF 可选 image_only / searchable_dual_layer）→ 参数正确传给 `library_start_export`。→ **MET**：面板新增「导出格式」下拉 + PDF 内容模式下拉；payload 为既有六字段 `format` + `format_options`（PDF → `pdf_content`，ZIP → `compression`），HostIssuer 已支持该组合，未改契约。 <<MET>>
- [x] **AC2 结果展示**：导出完成显示真实文件路径 + sha256 + 页数/格式；PDF 与 ZIP 提示区分。→ **MET**：`导出完成（PDF · searchable_dual_layer）：<路径> · sha256 <64hex> · 3 页`；ZIP 显示 `ZIP 图片包`；真机 PDF sha256 与 UI 一致。 <<MET>>
- [x] **AC3 测试**：Headless 覆盖格式参数传递（ZIP/PDF 两种 + 模式）、完成态展示、错误提示；真机截图一次（导出面板含 PDF 选项）。→ **MET**：6 项 headless + 真机截图 2 张（PDF 选项面板、真实 PDF 导出完成）。 <<MET>>
- [x] **AC4 回归**：test.ps1 全绿（≥225）；vitest 60/567；pytest 无新增失败。→ **MET**：test.ps1 **231/231**（61/55/115，0 skipped）；vitest **60/567**；pytest **3F/2772P/9S**（同一组 3 失败，0 新增）。 <<MET>>
- [x] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff。→ **MET**：check PASS；15 条 pin；Handoff 含 Record Decision。 <<MET>>

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| 契约 | 复用既有 `library_start_export` 六字段；`format` ∈ zip/pdf；`format_options` 严格 `{"compression":"standard"}` 或 `{"pdf_content": image_only|searchable_dual_layer}`；不改 Host/Core |
| UI | 格式默认 ZIP；选 PDF 显示内容模式（默认 searchable_dual_layer，CJK 文本层是 PDF 核心价值）；目标扩展名随格式 |
| 完成态 | 用 Core 返回 `output.format` + 请求的 pdf_content + total_pages 渲染真实路径/sha256/页数；ZIP/PDF 文案区分；不伪造 |
| 错误 | `导出失败（<code>）` / `导出被拒绝…` 原样呈现 |
| 真机 | 隔离数据根（RELEASE-REPACK-3/data-root 副本，清 catalog/derived 命名空间锁后重建）+ 冻结 sidecar；真实导出 20,728,075 B、`%PDF-1.7`、3 页对象、含字体/文本操作符、sha256 与 UI 一致 |

## 实现摘要

- `Services/ImportExportContracts.cs`：`StartExportRequest(pdfContent)`、`DefaultExportFileName(format)`、`SnapshotStatus`（格式+路径+sha256+页数）、`FormatDisplay`。
- `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs`：`StartExportAsync(format, pdfContent)`。
- `Views/ImportExportPanels.cs`：格式/PDF 模式选择、目标扩展名、状态呈现、格式切换刷新提示。
- `tests/NewManga.App.Tests/PdfExportUiTests.cs`（新，6 项）+ `FakeHostController` 记录 format/pdfContent。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| PE-TEST-SUMMARY | AC4 | verification/PDF-EXPORT-UI-1/test/summary.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 7ea6123246ae36007f2661f40938e71246bdcc329ceb159dfe9458eeed5ba2b8 | CANONICAL |
| PE-TEST-LOG | AC4 | verification/PDF-EXPORT-UI-1/test/dotnet-test-Debug.log | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 4ced4d579e0091d087841c17a1a4e74ef5184de1b9e3eb1fce3ed70bfd599f19 | CANONICAL |
| PE-VITEST | AC4 | verification/PDF-EXPORT-UI-1/test/vitest.log | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | f1be60ecf0df6669450b2f7a6294e559dea6f1a6429792135f3b910e96508c72 | CANONICAL |
| PE-PYTEST | AC4 | verification/PDF-EXPORT-UI-1/test/pytest.log | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | afbb690fbeb04d0e80643df243063e9d83c242aed5e7fbc9bab3345301a165d9 | CANONICAL |
| PE-TEST-PS1-LOG | AC4 | verification/PDF-EXPORT-UI-1/test/test.ps1-final.log | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 59d2ddda76d74a059226ce51f2f0ff5d5a3ca4445a9c3fab565dfdedd3780f16 | CANONICAL |
| PE-PDF-PARAMS | AC1/AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/pdf-format-params.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 5bde7dd03abc3fa2cc342c5f782fb360f102970d6cd0cefc03d4d70b59eafe84 | CANONICAL |
| PE-ZIP-PDF | AC1/AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/zip-pdf-both.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 431cf9f08cb0dbd6b552ceb8d2359150239627ff6c24bcb611f0466c5f88c4e1 | CANONICAL |
| PE-COMPLETED-PDF | AC2/AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/completed-pdf.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 604c96070f4c25e48a682e2cd370b387971cda4e6c2c4a0798f76a9487132f01 | CANONICAL |
| PE-COMPLETED-ZIP | AC2/AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/completed-zip.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 706fe911bb9b5ae89b16f95c3c672a02fcac4c21238b83f28498e1799f3acb83 | CANONICAL |
| PE-ERRORS | AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/errors.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 720402cd7e40fccd71a1e7c7d8db38497bc7102f60887d9b6abe2037834598f0 | CANONICAL |
| PE-PAYLOAD-CONTRACT | AC3 | verification/PDF-EXPORT-UI-1/pdf-export-ui/payload-contract.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 2f274548be05410a587b39206b6c0b9c1fd31b3abfdd00f23153ca3610bb98b3 | CANONICAL |
| PE-REAL-OPTIONS | AC3 | verification/PDF-EXPORT-UI-1/real-app-pdf-options.png | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | e3286ea4107fd7c3eb187458b26348150154fdff6bc6a2caeb928408e60f3688 | CANONICAL |
| PE-REAL-COMPLETED | AC2/AC3 | verification/PDF-EXPORT-UI-1/real-app-pdf-completed.png | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | b8e34e7b1d82dafa868a9981f6d9e9576756e3721aae3aaafcb5f5da3ec5048e | CANONICAL |
| PE-REAL-META | AC2/AC3 | verification/PDF-EXPORT-UI-1/real-app-export-metadata.json | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 586333cc5329f6ccfa29cfe938c06831d7f766e0489011900ff58eb3323e787e | CANONICAL |
| PE-REPORT | AC5 | verification/PDF-EXPORT-UI-1/REPORT.md | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 8ea84295a48f12a673f700226b9e0a58c773d9d11139a7c18a851c6a748940df | CANONICAL |
| PE-TRX-APP | AC4 | verification/PDF-EXPORT-UI-1/test/results-app.trx | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 266010ec4be7efe394289b131a89678e71baf44bc9f727a7f74c56556e5027e9 | SOURCE_PIN |
| PE-TRX-CORECLIENT | AC4 | verification/PDF-EXPORT-UI-1/test/results-coreclient.trx | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 8d63b22980e5b99ad97893c00d78d2fff1781208837874c364099d1d6f645ac7 | SOURCE_PIN |
| PE-TRX-HOST | AC4 | verification/PDF-EXPORT-UI-1/test/results-host.trx | 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95 | 94f1fb6ffea406d5154b4d442d646c39cd9fc485e160dd533ae16469d94bb59e | SOURCE_PIN |
| PE-RESOURCE-MANIFEST | Closeout | verification/PDF-EXPORT-UI-1/resource-manifest.json | - | dbb4746f3050761265bbb6006d03b41a4e10b62e22af83789f6190402abd04b0 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-UI-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-UI-1 | verification/PDF-EXPORT-UI-1/resource-manifest.json | 2026-10-28 收口时存在；真实导出 PDF `exports/BOOK-FIXTURE-1 日漫_JA 测试书-第 1 章-20261027-161525.pdf`（20,728,075 B，sha256 `c0a97eb3…`）保留在此供复核，不入 Git；未移动/未删除；关闭时由 DSH 复核 |

## Closeout Record

- Closeout date / DSH：2026-10-28（DSH 独立复核 PASS；实现提交 `6deefdcc3` 已在 main 历史）。
- canonical_evidence_status：`complete`（15 条 CANONICAL + 4 条 SOURCE_PIN；worktree/blob 双 basis 校验通过）。
- resource_closeout_status：`complete`（task-env 与隔离数据根 `PRESERVE_REFERENCED`；真实 PDF 原件保留在 task-env，不入 Git）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 `%APPDATA%` 未触碰；主工作树他人改动未触碰）。
- 未关闭项及保留原因：`image_only` 未真机导出（参数由 headless 钉住，composer 两路径由 baseline-scout 验证）；未翻译章节沿用既有「没有可导出的翻译页」提示。均为已记录限制，不阻塞。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER。

## Review（DSH 独立复核，2026-10-28）— PASS

- 证据核对：15 条 CANONICAL pin 全部命中（worktree 或 `6deefdcc3` blob 双 basis 均校验通过）；补登 3 条 trx + 1 条 resource-manifest 为 SOURCE_PIN；`verification/PDF-EXPORT-UI-1/` 无未登记文件。
- 代码核对（main HEAD `4f1796f17`）：`Services/ImportExportContracts.cs`（`pdfContent`、`FormatDisplay`、`SnapshotStatus` 路径+sha256+页数）、`Views/ImportExportPanels.cs`（ZIP/PDF 格式选择、PDF 内容模式、扩展名与状态文案）、`IHostController`/`HostController`/`NullHostController`、`tests/NewManga.App.Tests/PdfExportUiTests.cs`（6 项）均在库。
- 集成：实现提交 `6deefdcc3` 已在 main 历史（`git merge-base --is-ancestor` = 0）。
- 回归：DSH 在 main HEAD `4f1796f17` 用隔离 evidence 目录复跑 `apps/desktop-avalonia/scripts/test.ps1` → **TEST PASS 249/249, 0 skipped**（coreclient 61 / host 56 / app 132）。首次与并发测试共用默认 evidence 目录时 `D4SecurityHarnessTests` 出现 1 例环境干扰（TileDigestMismatch 期望收到 NO_ERROR），隔离重跑该组 **6/6 PASS**，判定为并发污染而非回归。`extract-command-surface.py --check` 当前基线 PASS（66 命令）。
- 结论：AC1–AC5 全部 MET；实现已集成、证据齐备、无阻塞遗留；标 `done`，集成点 `6deefdcc3`。
