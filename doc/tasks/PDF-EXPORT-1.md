---
id: PDF-EXPORT-1
title: PDF 导出验收（Pillow/Qt-free 现状纠偏 + Record Decision）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: baseline-scout
owner: baseline-scout
reviewer: dsh
depends_on: []
base_commit: 170878dc4
branch: task/PDF-EXPORT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1
integration_commit: 10273c9ce
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/PDF-EXPORT-1
allowed_paths:
  - doc/tasks/PDF-EXPORT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/PDF-EXPORT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1-clean/**
---

# PDF-EXPORT-1：PDF 导出验收（现状纠偏 + Record Decision）

## 背景（已按实测更正）

本卡释放时的前提是"导出仅 ZIP、PDF 未覆盖、旧 Qt composer 已移除"。**实测 HEAD 现状不符**（Lead 2026-10-27 裁决确认）：

- PDF 导出**早已实现且 Qt-free**：`src/bootstrap/core_assembly.py:1374` 注入 `QtFreePdfComposer`（`src/infrastructure/export/qt_free.py`，P16 + PDF-STREAM-FIX-1 + SEARCHABLE-PDF-CJK-1 累积产物），`image_only` 为无损 Flate RGB、`searchable_dual_layer` 带 CJK 文本层，闭包无 PySide6/Qt。
- 因此本卡改为「**验收 + Record Decision**」：不新增 Pillow composer（Pillow `Image.save("PDF")` 仅有损 JPEG 且无文本层，属退化）、不改 `src/**` 语义、不改协议/Host 契约/旧壳；补齐真实产物验收证据，并记录"后续 Agent 勿重复造 composer"。
- **真实缺口另派**：产品 Avalonia 导出面板仍是"ZIP 图片包"（`Views/ImportExportPanels.cs`），PDF 在 UI 不可达 → Lead 已释放 `PDF-EXPORT-UI-1`（`apps/desktop-avalonia/**`），不占本卡。

## Acceptance Criteria（原样保留，状态按实测）

- [x] **AC1 方案**：导出格式扩展点已确认（`PdfComposer` 端口 / `ExportFormat.PDF` / `core_assembly` 注入 / `StartExport` wire）；合成器为 Qt-free 多页 PDF writer（每页 `MediaBox [0 0 W H]`，72 dpi ⇒ 1 px = 1 pt，页序即 scope 顺序），方案与"为何不用 Pillow save"记录于 REPORT §1/§6。 <<MET>>
- [x] **AC2 实现**：PDF 支持已存在并 wire 实测——`StartExport format="pdf"` + `format_options={pdf_content:image_only|searchable_dual_layer}` + host-control `RegisterExportTarget` grant；状态机 pending→running→publishing→completed，`export_history.export_type="pdf"` 落库（含 format_options/file_hash），与 ZIP 并存互不影响。 <<MET>>
- [x] **AC3 验证**：真实数据根（RELEASE-REPACK-2 完成态，8 页书 3 页有译文）经真实 Core 导出 3 份真实 PDF：3 页 image_only（8,696,282 B，sha256 `975b87d4…`，页尺寸 1200×1660/1200×1660/1200×726 与 DB 逐页一致、非空白、`%PDF-1.7`+`%%EOF`）；3 页 searchable（21,106,403 B，文本层 277/204/120 字符）；engine 级整书 8 页（3 译文+5 原图回落，尺寸逐页匹配）。SHA-256 入库、产物副本入库。 <<MET>>
- [x] **AC4 回归**：pytest **3F/2772P/9S**（与基线逐项一致，0 新增）；`tests/export` + `tests/core/test_architecture.py`（Qt-free 断言）29 passed；`scripts/test.ps1` 在**干净 HEAD worktree** **225/225 全绿**（主工作树当时失败 40 项系并发 Agent 未提交 UI 改动，已留证并说明）。 <<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin、commit 列留空；Handoff + Record Decision（两种 PDF 模式与文本层证据、为何不新增 composer、影响面/回退/遗留）见 REPORT §6/§7。 <<MET>>

## 允许修改范围

`src/**`（本卡未使用）、本卡、STATUS/PLAN/LEDGER、`verification/PDF-EXPORT-1/**`、workspace。

## 禁止范围

不引 Qt、不改协议/Host 契约/旧壳、不 push；不伪造 PDF 产物；不得把任何 API key/secret 写入仓库、日志或证据（本卡 grant 签名密钥为进程内临时生成，未落盘）。

## Record Decision（PDF 导出）

- **保留现有 Qt-free `QtFreePdfComposer` 作为唯一生产实现**；不新增 Pillow composer、不改 `PdfComposer` 端口、不改协议/Host 契约。
- 理由：现有实现 Qt-free 且已生产接线；`image_only` 无损 RGB（Pillow PDF save 仅有损 JPEG）；`searchable_dual_layer` 已有 CJK 文本层（实测 277/204/120 字符），Pillow 无法产生文本层；新增第二条路径会造成"两个 PDF 真相"且无契约收益。
- 两模式语义：`image_only`＝纯图像页（小体积、无文本层）；`searchable_dual_layer`＝图像 + 嵌入 CJK 字体文本层（可搜索/复制，体积约 2.4×）。
- 影响面：本卡 `src/**` **零改动**；页尺寸/页序/`export_history` 语义不变。回退开关：无需（未改代码）。
- 防重复：后续 `PDF-EXPORT-*` 需求先读 REPORT §1/§6，PDF 合成器已存在，勿再写 Pillow composer；可做工作仅在 UI 可达性（`PDF-EXPORT-UI-1`）、元数据、文本层质量等具体缺口。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-REPORT | AC1–AC5 | verification/PDF-EXPORT-1/REPORT.md | | b36e5c9ddc769dc55f9b57606f460b2dafd8ea984239a3b72cda77aed40f554a | CANONICAL |
| EV-PDF-ARTIFACTS | AC2/AC3 | verification/PDF-EXPORT-1/pdf-artifacts.json | | 8108d4a9b49780148d304114d2d315e5a01cba94a8feea12aa1bdd2e2a47bd0a | CANONICAL |
| EV-PDF-3PAGES | AC3 | verification/PDF-EXPORT-1/artifacts/BOOK-FIXTURE-1-3pages-image-only.pdf | | 975b87d40a30939df389c84bcbc2fc76adb544a72bbea46e0a6b5353888d2eae | CANONICAL |
| EV-PYTEST | AC4 | verification/PDF-EXPORT-1/evidence/pytest-full.log | | cb01dc4c2ae2f396884c29ea3e17861976adfa7caac766069b83bb973d469dbf | CANONICAL |
| EV-DOTNET-CLEAN | AC4 | verification/PDF-EXPORT-1/evidence/dotnet-test-clean-head.log | | aa6fefc2b50f8457ec68ce889a5a26720b2b7dd7e5f38c0d9d1245d9793b0c6e | CANONICAL |
| EV-DOTNET-CLEAN-SUMMARY | AC4 | verification/PDF-EXPORT-1/evidence/dotnet-summary-clean-head.json | | dc2e61d75624c603e4329968285a2780edd91ac1efe0d0dbc328cef838f6fc3b | CANONICAL |
| EV-DOTNET-DIRTY | AC4 | verification/PDF-EXPORT-1/evidence/dotnet-test-worktree-dirty.log | | a7d9b3569d1f9b2a002922e009cdad1bc657627c3f2b8d73c214c249854c99f6 | CANONICAL |
| EV-TOOL-REAL | AC3 | verification/PDF-EXPORT-1/tools/real_pdf_export.py | | dd1e90785817fb3de54fcf41660d698c834c5165e1b7d0120d4cea9bccd7847e | SOURCE_PIN |
| EV-TOOL-SUPPLEMENTARY | AC3 | verification/PDF-EXPORT-1/tools/supplementary_pdf.py | | 43b633683c1afe6b85554c6825bca860bfbbb338ded6adf831706756d19072dd | SOURCE_PIN |
| EV-TOOL-EVIDENCE | AC3/AC5 | verification/PDF-EXPORT-1/tools/build_evidence.py | | d3765577461d5f04b2c0e1b5808a51bfd0164a23b2094ce1e16e3423c4b900d3 | SOURCE_PIN |
| EV-TOOL-SANITY | AC1 | verification/PDF-EXPORT-1/tools/sanity_pdf.py | | 6041963c2a037e4a3b0fb98d3804e905956fffafafcda08f6267a20444e15938 | SOURCE_PIN |
| EV-RESOURCE-MANIFEST | AC5 | verification/PDF-EXPORT-1/resource-manifest.json | | 46d3bb0fdbaec74e9469e64df715c9e44cb1be1f55ccd35b808d23b675023361 | SOURCE_PIN |
| EV-CHECK-TASKPATH | AC5 | verification/PDF-EXPORT-1/check-taskpath.log | | 90c2f9388a647aa9ca64228262370862382582b10bac1f26d4b230fea38b4e9e | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-1 | verification/PDF-EXPORT-1/resource-manifest.json | 数据根副本/产物/日志保留引用（3 份外部 PDF 以 sha 引用）；`src/**`、`tests/**` 零改动；无删除/迁移/归档；RELEASE-REPACK-2 与 BOOK-FIXTURE 原件零修改 |

## 交付与运行记录

- Owner：`baseline-scout`（DSH 委派，team task-49）；结论为**验收纠偏**：PDF 早已实现，本卡补齐真实产物证据与 Record Decision，未改产品源码。
- 复验环境：真实数据根 = `RELEASE-REPACK-2/data-roots/data-root-full-chain` 私有副本；生产装配（`assemble_production_core`）+ 真实 `CoreServiceServer` + host-control grant（本地按 `HostIssuer.MintExportGrant` 同款 HMAC 配方铸造，密钥进程内临时生成）；pymupdf 1.28.2 独立解析。
- 复现脚本：`tools/real_pdf_export.py`（wire image_only）、`tools/supplementary_pdf.py`（engine 8 页 + wire searchable）、`tools/sanity_pdf.py`（composer 冒烟）、`tools/build_evidence.py`（证据聚合）。
- 回归：pytest 3F/2772P/9S（0 新增）；`tests/export`+`tests/core/test_architecture.py` 29 passed；干净 HEAD worktree `test.ps1` 225/225；主工作树失败 40 项经查为并发 Agent 未提交 UI 改动（与本卡零交集，日志留证）。
- 遗留：PDF 的 UI 可达性（导出面板仅 ZIP）→ `PDF-EXPORT-UI-1`（Lead 已另派，`apps/**`，不占本卡）。

## Closeout Record

- Closeout date / DSH：待关闭时填写；Owner 交付日期 2026-10-27。
- canonical_evidence_status：`complete`（12 行 sha256 pin，commit 列留空）。
- resource_closeout_status：`pending`（task-env 保留引用；关闭时复核 `resource-manifest.json`）。
- 删除、迁移、归档数量/字节数：本 Task 无删除/迁移/归档。
- 未关闭项及保留原因：UI 可达性属 `PDF-EXPORT-UI-1`；本卡不实施。
- 当前指针清理：关闭时由 DSH 更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS（验收纠偏）

- **结论：PDF 早已实现**（src/infrastructure/export/qt_free.py QtFreePdfComposer，core_assembly.py:1374 生产接线；扩展点 PdfComposer/ExportFormat.PDF/StartExport format=pdf+grant）；**未新增 Pillow composer**（正确——Pillow PDF 有损且无文本层）。
- image_only 3 页：**8,696,282B** sha256 975b87d4…8d2eae；pymupdf 逐页尺寸 1200×1660/1200×1660/1200×726 与 DB 一致；%PDF-1.7+%%EOF；xport_history.export_type=pdf。
- searchable_dual_layer 3 页：21,106,403B，**文本层 277/204/120 字符**（CJK 可搜索）。
- engine 级整书 8 页（3 译文+5 原图 fallback）：26,755,308B，8 页尺寸逐页匹配。
- 回归：pytest 3F/2772P/9S（逐项一致）；export+architecture 29 passed（Qt-free 断言）；**干净 worktree 10273c9ce 上 test.ps1 225/225**（主工作树 40 项失败系并发 Agent 未提交 UI 改动，与本卡零交集，日志留证）。
- 遗留：PDF 的 UI 可达性 → PDF-EXPORT-UI-1（已另派）。
- 集成：10273c9ce。
