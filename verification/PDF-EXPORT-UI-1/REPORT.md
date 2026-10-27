# PDF-EXPORT-UI-1 验证报告（导出面板 PDF 选项）

- Task：`doc/tasks/PDF-EXPORT-UI-1.md`（team task-52）
- Branch / worktree：`task/PDF-EXPORT-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1`
- Base：`2591ef028`（卡面记 `170878dc4`；按 DSH 指令以当前 HEAD 为准）
- 未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；不伪造导出结果。
- 主工作树中另一会话在途的 `ThemePack.cs` / `MainWindow.axaml*` 等改动**未触碰、未提交**；本卡只提交自己的文件。

## 1. 结论

| AC | 结论 | 证据 |
|---|---|---|
| AC1 格式选择 | **MET** | 导出面板新增「导出格式」下拉（ZIP 图片包 / PDF）；选 PDF 后出现「PDF 内容模式」（`searchable_dual_layer` 可搜索 CJK 文本层 / `image_only` 无损图片）；参数以 `format` + `format_options{"pdf_content":…}` 传给 `library_start_export`（Host 契约早已支持该组合，未改契约）。 |
| AC2 结果展示 | **MET** | 完成态来自 `GetExportSnapshot`：`导出完成（PDF · searchable_dual_layer）：<真实路径> · sha256 <64hex> · 3 页`；ZIP 显示 `ZIP 图片包` 并带 sha256/页数；真实 PDF 导出 sha256 与 UI 显示一致（`c0a97eb3…`）。 |
| AC3 测试 | **MET** | 6 项 headless（ZIP/PDF+两种模式参数、target 扩展名、完成态 PDF/ZIP 区分、失败/拒绝 typed 文本、payload 经 HostIssuer 校验）；真机截图 2 张（PDF 选项面板 + 真实 PDF 导出完成）。 |
| AC4 回归 | **MET** | `scripts/test.ps1` **231/231 passed, 0 skipped**（coreclient 61 / host 55 / app 115）；vitest **60 files / 567 tests**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增）。 |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；12 条 64-hex pin；Handoff 含 Record Decision。 |

## 2. 面板结构（阅读器「导出」弹层）

```
导出当前书
<书名> · <章名> · N 页可导出
支持 ZIP 图片包与 PDF（image_only / searchable_dual_layer）…（Host grant 说明）
导出格式      [ZIP 图片包（zip） ▾ | PDF（pdf）]
PDF 内容模式  [searchable_dual_layer（可搜索 CJK 文本层） ▾ | image_only（无损图片）]   ← 仅 PDF 显示
状态行        （可导出提示 / 导出完成 → 路径 + sha256 + N 页 + 格式 / 失败 typed code）
最近导出      <export_id> · <format> · 导出完成 · sha256 前缀
[开始导出] [取消导出] [打开导出目录] [关闭]
```

调用链：`ExportPanel → IHostController.StartExportAsync(format, pdfContent) → ImportExportPayloads.StartExportRequest(format, format_options) → HostGrantCoordinator → Core StartExport`；Host 侧 `HostIssuer.ValidateExportRequest` 对 `pdf + {"pdf_content": image_only|searchable_dual_layer}` 返回扩展名 `pdf`，对 `zip + {"compression": …}` 返回 `zip`——**未新增/修改 Host 命令或契约**。

## 3. Record Decision

| 项 | 决定 |
|---|---|
| 契约 | 完全复用既有 `library_start_export` 六字段：`format` ∈ `zip|pdf`，`format_options` 严格为 `{"compression":"standard"}`（ZIP）或 `{"pdf_content": …}`（PDF）；HostIssuer 已校验 PDF 组合，App 仅填充用户选择 |
| UI | 格式下拉默认 ZIP；选 PDF 才显示 PDF 内容模式（默认 `searchable_dual_layer`，CJK 文本层是 PDF 的核心价值）；完成态用 Core 返回的 `output.format` + 请求的 `pdf_content` + `total_pages` 渲染，ZIP/PDF 文案区分 |
| 目标文件 | 按所选格式生成 `…-<timestamp>.pdf` / `.zip`（`DefaultExportFileName(book, chapter, format)`），仍限定 Host 数据根 `exports/` |
| 提示一致性 | 切换格式后立即刷新就绪提示（真机截图时发现 ZIP 文案残留，已修复并重建复查） |
| 错误 | 失败快照显示 `导出失败（<error_code>）`；StartExport 被拒显示 `导出被拒绝…`；不可用不伪造完成 |
| 真机验证 | Debug 构建 + 隔离数据根（RELEASE-REPACK-3/data-root 副本，清理 catalog/derived 命名空间锁后重建）+ 冻结 sidecar；真实 PDF 20,728,075 字节、`%PDF-1.7`、3 个页面对象、含字体与文本操作符（可搜索层）、sha256 与 UI 一致；未写真实 `%APPDATA%` |

## 4. 实现摘要（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `Services/ImportExportContracts.cs` | `StartExportRequest` 增加 `pdfContent` → PDF 写 `pdf_content`；`DefaultExportFileName` 按格式扩展名；`SnapshotStatus` 显示格式+路径+sha256+页数；`FormatDisplay` 区分 ZIP/PDF 模式。 |
| `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs` | `StartExportAsync` 增加 `format`/`pdfContent` 并转发。 |
| `Views/ImportExportPanels.cs` | 导出格式下拉 + PDF 内容模式行（仅 PDF 显示）、目标扩展名、StartExport 传参、完成/失败状态格式化、格式切换刷新提示；标题/说明去掉“仅 ZIP”。 |
| `tests/NewManga.App.Tests/PdfExportUiTests.cs`（新，6 项） | ZIP/PDF 参数、两种 PDF 模式、book/chapter 页参数、target 扩展名、完成态 PDF/ZIP 区分、失败/拒绝、payload 经 HostIssuer 校验。 |
| `tests/NewManga.App.Tests/FakeHostController.cs` | `StartExportCalls` 记录 format/pdfContent。 |

## 5. 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 产物 |
|---|---|---|---|---|
| AC1 ZIP 参数 | `SearchableDualLayer_IsForwarded_AndZipStaysZip` | Avalonia Headless 11.3.22 + FakeHostController | ZIP → format=zip、pdf_content=null、目标 `.zip`、PDF 模式行隐藏 | `pdf-export-ui/zip-pdf-both.json` |
| AC1 PDF+image_only | `PdfFormat_SendsFormatAndPdfContent_AndPdfTargetExtension` | 同上 | format=pdf、pdf_content=image_only、目标 `.pdf`、页面/章节参数精确 | `pdf-export-ui/pdf-format-params.json` |
| AC1 PDF+searchable | 同上（第二段） | 同上 | format=pdf、pdf_content=searchable_dual_layer | `pdf-export-ui/zip-pdf-both.json` |
| AC2 PDF 完成态 | `CompletedPdf_ShowsPathSha256PagesAndMode` | 同上 | 状态含路径、`sha256 <64hex>`、`PDF · searchable_dual_layer`、`3 页` | `pdf-export-ui/completed-pdf.json` |
| AC2 ZIP 完成态 | `CompletedZip_IsLabelledAsZipImagePack` | 同上 | `ZIP 图片包`、含 sha256/页数、不含 `PDF ·` | `pdf-export-ui/completed-zip.json` |
| AC3 错误 | `FailedSnapshot_ShowsTypedError_AndRefusedStartIsExplicit` | 同上 | `导出失败（EXPORT_INPUT_UNAVAILABLE）`、`导出被拒绝` | `pdf-export-ui/errors.json` |
| AC3 契约 | `PayloadOptions_MatchTheHostIssuerPdfContract` | 无 UI | 六字段键集；HostIssuer 校验 pdf/zip → 扩展名 pdf/zip | `pdf-export-ui/payload-contract.json` |
| AC3 真机截图 | 1400×900 Debug App + 隔离数据根 + 冻结 sidecar → 书架 → 进入阅读 → 导出 → 选 PDF | Windows 10.0.26300；真实 Host/Core | 面板含「导出格式 PDF」「PDF 内容模式 searchable_dual_layer」；真实导出完成显示路径+sha256+3 页 | `real-app-pdf-options.png`、`real-app-pdf-completed.png`、`real-app-export-metadata.json` |
| AC3 真实 PDF 导出 | 面板「开始导出」（PDF/searchable_dual_layer） | 真实 Host/Core | `exports/BOOK-FIXTURE-1 日漫_JA 测试书-第 1 章-20261027-161525.pdf` 20,728,075 B · `%PDF-1.7` · 3 page 对象 · 有字体/文本操作符 · sha256 `c0a97eb3bac77ed538e72468034e3b80e3a989509aef0eea5bedde09b8fbb210`（与 UI 一致） | `real-app-export-metadata.json`（PDF 原件保留在 task-env，不提交仓库） |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **231/231**（61/55/115），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60 files / 567 tests；3F/2772P/9S（0 新增） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PDF-EXPORT-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 6. 遗留 / 未关闭项（记录不阻塞）

1. **真机导出所用数据根**是 RELEASE-REPACK-3/data-root 的隔离副本（清 catalog/derived 命名空间锁后重建），仅在 task-env，未提交；PDF 原件（20.7MB）保留在 task-env 供复核，不进入 Git。
2. **translated 页依赖**：本次 BOOK-FIXTURE-1 有 3 页已翻译内容；未翻译章节会显示「没有可导出的翻译页」，符合既有行为。
3. **image_only 模式**未做真机导出（headless 已钉参数；composer 两条路径由 baseline-scout 真机验证），本卡只补 UI 入口。
4. **ZIP 旧行为**保持默认与文案；未改变 `.zip` 压缩选项。
5. **并发**：`route-research`/`core-admin-rca` 等在跑；主工作树另一会话的 `ThemePack.cs`/`MainWindow.axaml*` 在途改动未被本卡触碰或提交；如主工作树先集成，rebase 后重跑 gate。
6. 需独立 Review（Owner 不自审）。

## 7. 复现

```pwsh
# 1) 全量回归（231 项，含 6 项 PDF 导出 UI headless）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory G:\CODEX\New Manga.workspace\task-envs\PDF-EXPORT-UI-1\evidence

# 2) 只看 PDF 导出 UI 测试
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  -c Debug --filter "FullyQualifiedName~PdfExportUiTests"

# 3) 真机截图+真实导出（隔离数据根，不写真实 %APPDATA%）
$root='G:\CODEX\New Manga.workspace\task-envs\PDF-EXPORT-UI-1'
NewManga.App.exe --data-root=$root\real-app-data-root `
  --sidecar-dir='G:\CODEX\New Manga.workspace\task-envs\RELEASE-REPACK-3\sidecar-base\core-sidecar' `
  --parity --mutex-name=NewManga.PdfExportUi.Shot --width=1440 --height=920
# 书架 → BOOK-FIXTURE-1 → 进入阅读 → 导出 → 导出格式选 PDF → 开始导出
```
