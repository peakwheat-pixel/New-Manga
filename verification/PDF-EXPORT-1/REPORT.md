# PDF-EXPORT-1 交付报告：PDF 导出验收 + Record Decision（未新增 composer，未改 Core 语义）

- Task: `doc/tasks/PDF-EXPORT-1.md`（team task-49）；Owner `baseline-scout`（DSH 委派）；base `170878dc4`
- 证据目录: `verification/PDF-EXPORT-1/`
- **结论（纠偏）**：HEAD 上 **PDF 导出早已实现且为 Qt-free**——`core_assembly.py` 注入 `QtFreePdfComposer`（`src/infrastructure/export/qt_free.py`，P16 + PDF-STREAM-FIX-1 + SEARCHABLE-PDF-CJK-1 累积产物）。本卡因此按 Lead 裁决执行「**验收 + Record Decision**」：不改 `src/**` 语义、不写 Pillow composer、不改 Host/UI；用真实数据根与真实 Core 导出链路补齐 AC3 产物证据，并记录"为什么现有资产是对的、为什么不要 Pillow save、UI 缺口归属"。
- 卡面前提"PDF 未覆盖"已在卡内更正为"已实现，补验收证据与 Record Decision"。

---

## 1. AC1 扩展点确认与方案（已实现，记录在案）

| 层 | 位置 | 说明 |
| --- | --- | --- |
| 端口 | `src/application/export/ports.py` | `PdfComposer.compose(images)`（image_only）与可选 `compose_searchable(images, regions)`（文本层） |
| 服务 | `src/application/export/service.py` | `ExportFormat.PDF`；`_build_payload` 的 pdf 分支按 `format_options.pdf_content` 选择 `compose` / `compose_searchable`；`PdfUnavailableError` 为 fail-closed 能力缺口 |
| 生产装配 | `src/bootstrap/core_assembly.py:1374` | `ExportService(..., pdf_composer=QtFreePdfComposer())` — **无 Qt**（Core-SLIM 后仍保持） |
| 合成器 | `src/infrastructure/export/qt_free.py` | `QtFreePdfComposer`：stdlib `zlib`/`struct` 手写多页 PDF；每页 `MediaBox [0 0 W H]`（72 dpi ⇒ 1 px = 1 pt，与旧 Qt composer 语义一致）；`image_only` 为无损 Flate RGB(+SMask)，`searchable_dual_layer` 嵌入 CJK 字体与 ToUnicode CMap；**仅 searchable 模式用 Pillow 取字形宽度**，无 PySide6/Qt 依赖 |
| 线缆 | `src/bootstrap/core_service.py` | `StartExport` 接受 `format="pdf"`、`format_options={"pdf_content": "image_only"|"searchable_dual_layer"}`；host-control `RegisterExportTarget` 铸 grant → `target_ref`；`export_history.export_type="pdf"` 落库 |

**为什么不用 Pillow `Image.save("PDF", save_all=True)`**：Pillow 的 PDF writer 只写 **JPEG 有损**图像，且无法产生文本层；现有 composer 是**无损 RGB + 可选 searchable 文本层**（CJK 已验证），换成 Pillow 属质量/能力退化。故保持现有资产，不新增冗余 composer（Lead 2026-10-27 裁决确认）。

## 2. AC2 导出支持 PDF（已支持，wire 实测）

真实请求（in-process 生产装配 + 真实 `CoreServiceServer`，Host 侧 grant 用 `HostIssuer.MintExportGrant` 同款 HMAC 配方本地铸造）：

```
StartExport {book_id, chapter_ids, ordered_page_ids=3 个有译文页,
             format: "pdf", format_options: {"pdf_content": "image_only"},
             stale_policy: "abort", target_ref: etref1.<grant>.<sig>}
→ 状态机: pending → running(0/3→3/3) → publishing → completed
→ ExportProgressChanged 事件 5 帧；`export_history` 行 export_type="pdf"、
  format_options={"pdf_content":"image_only"}、file_hash=<sha256>、status=completed
```

## 3. AC3 真实产物验证（BOOK-FIXTURE：8 页书、3 页有译文）

数据根：`RELEASE-REPACK-2/data-roots/data-root-full-chain` 的私有副本（完成态 Run：3 页 translated + clean + mask 产物；8 页原图）。产物全部由真实 Core 代码路径生成，未手工构造/未篡改：

| # | 场景 | 页数 | 大小 | SHA-256（64-hex，入库于 `pdf-artifacts.json`） | 解析器校验 |
| --- | --- | --- | --- | --- | --- |
| 1 | wire `pdf_content=image_only`（3 个译文页，host grant + `handle_start_export`） | 3 | 8,696,282 B (8.29 MiB) | `975b87d40a30939df389c84bcbc2fc76adb544a72bbea46e0a6b5353888d2eae` | pymupdf：页尺寸 1200×1660 / 1200×1660 / 1200×726 pt，与 DB 逐页一致；文件头 `%PDF-1.7`、尾 `%%EOF`；每页 1 图像、非空白 ink 采样 3885/3575/1555 |
| 2 | wire `pdf_content=searchable_dual_layer`（同一 3 页） | 3 | 21,106,403 B | `e0f7fd4951f7ffa8b075ea77d2ca23d7222c66244e3ff3de2ae02f45f05f5e14` | pymupdf：页尺寸同上；**文本层字符数 277 / 204 / 120**（CJK 可搜索） |
| 3 | engine 级整书 8 页（3 页译文 + 5 页无文字页回落原图，`stale_policy=continue_existing`） | 8 | 26,755,308 B | `eae5a85866feac54…`（完整值在 `pdf-artifacts.json`） | pymupdf：8 页；1200×1660 ×7 + 1200×726 ×1，与 DB `pages.width/height` 逐页一致 |

- 独立复算：`pdf-artifacts.json` 的 `wire_image_only_3pages.committed_copy` 把 3 页 image_only 产物复制进 `verification/PDF-EXPORT-1/artifacts/BOOK-FIXTURE-1-3pages-image-only.pdf`，`committed_copy_matches=true`（复算 sha 与导出返回的 `file_hash` 相同）；另两份 20–26 MB 产物留在 task-env `out/`，以 sha256 + 路径引用（避免仓库膨胀）。
- 说明：产品语义下"可导出页"= 有 translated 渲染的页（UI 显示 3 页）；8 页整书导出走 engine 级 `continue_existing`（无文字页回落原图），二者均已验证。

## 4. AC4 回归

### 4.1 pytest（全量）

`python -m pytest tests -q` → **3 failed / 2772 passed / 9 skipped**（与卡面基线 `3F/2772P/9S` 完全一致；失败集合与基线同为 `test_detection_manga_real`×2（需真实模型环境）+ `test_workbench_viewmodel`×1，均为既有环境性失败，**0 新增**）。日志：`evidence/pytest-full.log`。
PDF 相关既有测试单跑：`tests/export`（`test_pdf_stream_integrity` / `test_searchable_cjk_font` / `test_searchable_font_cost` / `test_searchable_korean_e2e`）+ `tests/core/test_architecture.py`（Qt-free 断言）→ **29 passed**。

### 4.2 test.ps1（App/Host）

- **干净 HEAD worktree 对照：`TEST PASS (Debug): 225/225 passed, 0 skipped`**（exit 0）——证据 `evidence/dotnet-test-clean-head.log` + `evidence/dotnet-summary-clean-head.json`；运行于 `G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1-clean`（HEAD `10273c9ce`，`git status` 干净）。
- 说明（如实记录）：主工作树当时的 test.ps1 失败 40 项（`NewManga.App.Tests` 109 中 69 通过），原因是**并发 Agent 未提交的 UI 改动**（`apps/desktop-avalonia/src/**` 的 `MainWindow.axaml`/`Pages.cs`/`MainViewModels.cs`/`AppStyles.axaml`/`ThemePack.cs`/`TestAppBuilder.cs` 等 7 个改动 + 新增 `ThemeMacosTests.cs`），与本卡零交集（本卡 `src/**`/`tests/**` 零 diff）；失败日志保留在 `evidence/dotnet-test-worktree-dirty.log` 供核对。

### 4.3 无 Qt 闭包

- `tests/core/test_architecture.py` 的 `QT_FORBIDDEN = {"PySide6"}` + `M2-I2_QT_FREE_MODULES` 断言通过（29 passed 组内含）；`core_assembly.py` 的 PDF 合成器为 `QtFreePdfComposer`，`src/infrastructure/export/qt_free.py` 只 import stdlib + Pillow；本卡未新增任何依赖、未改 PROTOCOL/Host 契约。
- 生产装配路径确认：`grep -n "pdf_composer=" src/bootstrap/core_assembly.py` → `pdf_composer=QtFreePdfComposer()`；`git diff --stat -- src` 为空（本卡零源码改动）。

## 5. AC5 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PDF-EXPORT-1.md`：**PASS**（证据 `check-taskpath.log`）。
- Canonical Evidence：64-hex sha256 pin、commit 列留空；Resource Manifest 指向 `verification/PDF-EXPORT-1/resource-manifest.json`；真实 PDF 产物（8.29 MiB）随证据入库并在 `pdf-artifacts.json` 记录复算 sha。
- `src/**` 零改动（`git status --porcelain -- src` 为空）；未 push、未 gc/prune；未改协议/Host 契约/旧壳。

## 6. Record Decision（供后续 Agent 直接引用）

- **决定**：保留 `QtFreePdfComposer` 作为 PDF 导出的唯一生产实现；**不新增 Pillow composer、不改 `PdfComposer` 端口、不改协议/Host 契约**。
- **理由**：① 现有实现 Qt-free 且已在 `core_assembly` 生产接线（Core-SLIM 闭包无 PySide6）；② `image_only` 为**无损** Flate RGB，Pillow `Image.save("PDF")` 只有 JPEG 有损；③ `searchable_dual_layer` 已有 CJK 文本层（本卡实测 277/204/120 字符），Pillow 无法生成文本层；④ 新增第二条 composer 会造成"两个 PDF 真相"，且无测试/契约收益。
- **两种模式语义**（本卡实测背书）：`image_only`＝纯图像页，无文本层，体积小（3 页 8.3 MiB）；`searchable_dual_layer`＝图像 + 嵌入 CJK 字体文本层（可搜索/可复制），体积大（3 页 20.1 MiB），字体按"覆盖全部字符"选择（msyh/malgun…，见 SEARCHABLE-PDF-CJK-1）。
- **影响面**：本卡 `src/**` **零改动**；PDF 行为、页尺寸（1 px = 1 pt @72 dpi）、页序、`export_history` 语义均不变。回退开关：无需（未改代码）。
- **遗留（真实缺口，已由 Lead 另派）**：产品 Avalonia 导出面板仍只提供"ZIP 图片包"（`Views/ImportExportPanels.cs`：标题/参数），PDF 在用户界面不可达；该缺口属 `apps/desktop-avalonia/**`（Host/UI），已由 Lead 释放 **`PDF-EXPORT-UI-1`**，不在本卡范围。
- **后续 Agent 防重复**：看到 `PDF-EXPORT-*` 需求时，先读本报告 §1/§6——**PDF 合成器已存在，勿再造 Pillow composer**；新增工作应只落在 UI 可达性、元数据或文本层质量等具体缺口上。

## 7. Handoff 摘要

- 交付形态：`verification/PDF-EXPORT-1/**`（REPORT + `pdf-artifacts.json` + 8.29 MiB 真实 PDF 产物 + 校验脚本/日志）+ 本卡/PLAN/STATUS/LEDGER；`src/**` 零 diff（`git status` 可核）。
- 复现方式：`tools/real_pdf_export.py`（wire image_only）、`tools/supplementary_pdf.py`（engine 8 页 + wire searchable）、`tools/build_evidence.py`（证据聚合）；数据根来自 `RELEASE-REPACK-2/.../data-root-full-chain` 的私有副本。
- 真实限界：本机无 pypdf，使用 **pymupdf 1.28.2**（独立解析器）校验页数/尺寸/文本层 + 文件头/尾；已如实记录于 `pdf-artifacts.json`。
