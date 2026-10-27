---
task_id: PDF-EXPORT-UI-1
author: saber-ui-spec (DSH team)
recipient: DeepSeek Harness
base_commit: 2591ef028
delivery_head: 6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95
status: ready-for-integration
---

# Handoff：PDF-EXPORT-UI-1（导出面板 PDF 选项）

## 交付结果

实现提交 **`6deefdcc3ee1ab8b6d1c3b4b58e8960d728cab95`**（branch `task/PDF-EXPORT-UI-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1`；卡面 base `170878dc4`，按 DSH 指令从当前 HEAD `2591ef028` 建分支）；本 Handoff 与任务卡 pin 在后续文档提交记录。未改 Python Core / 协议 / Host 契约 / 旧壳；未 push / gc / prune；不伪造导出结果；**未触碰主工作树另一会话在途的 `ThemePack.cs` / `MainWindow.axaml*` 改动，也未 `git add -A`**（只按显式路径提交本卡文件）。

| AC | 结论 | 说明 |
|---|---|---|
| AC1 格式选择 | **MET** | 导出面板新增「导出格式」（ZIP 图片包 / PDF）+ PDF 内容模式（`searchable_dual_layer` / `image_only`）；经既有六字段 `format` + `format_options` 传 `library_start_export`，HostIssuer 早已支持该组合。 |
| AC2 结果展示 | **MET** | 完成态：`导出完成（PDF · searchable_dual_layer）：<真实路径> · sha256 <64hex> · 3 页`；ZIP 显示 `ZIP 图片包`；真实导出 sha256 与 UI 一致。 |
| AC3 测试 | **MET** | 6 项 headless（ZIP/PDF+两种模式参数、target 扩展名、完成态 PDF/ZIP 区分、失败/拒绝、payload 经 HostIssuer 校验）+ 真机截图 2 张（PDF 选项面板、真实 PDF 导出完成）。 |
| AC4 回归 | **MET** | test.ps1 **231/231**（61/55/115，0 skipped）；vitest **60/567**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增）。 |
| AC5 门禁 | **MET** | check.ps1 -TaskPath PASS；15 条 64-hex pin；本 Handoff 含 Record Decision。 |

## 面板结构

```
导出当前书
<书名> · <章名> · N 页可导出
支持 ZIP 图片包与 PDF（image_only / searchable_dual_layer）…（Host grant 说明）
导出格式      [ZIP 图片包（zip） ▾ | PDF（pdf）]
PDF 内容模式  [searchable_dual_layer（可搜索 CJK 文本层） ▾ | image_only（无损图片）]   ← 仅 PDF 显示
状态行        （可导出提示 / 完成 → 路径 + sha256 + N 页 + 格式 / 失败 typed code）
最近导出      <export_id> · <format> · 导出完成 · sha256 前缀
[开始导出] [取消导出] [打开导出目录] [关闭]
```

链路：`ExportPanel → IHostController.StartExportAsync(format, pdfContent) → ImportExportPayloads.StartExportRequest → HostGrantCoordinator → Core StartExport`；HostIssuer 对 `pdf + {"pdf_content":…}` 返回扩展名 `pdf`、对 `zip + {"compression":…}` 返回 `zip`。**无 Core/协议/Host 契约改动。**

## Record Decision

1. **契约复用**：不新增命令字段。`format` ∈ `zip|pdf`；`format_options` 严格为 `{"compression":"standard"}`（ZIP）或 `{"pdf_content":"image_only"|"searchable_dual_layer"}`（PDF）。HostIssuer 校验为该精确组合，UI 只填充用户选择，因此不需要改 Host。
2. **默认与安全**：默认 ZIP 保持旧行为；PDF 默认 `searchable_dual_layer`（CJK 文本层是 PDF 的核心价值），可切 `image_only`；目标扩展名随格式（`.pdf`/`.zip`），仍限定 Host 数据根 `exports/`。
3. **完成态诚实性**：使用 Core 返回的 `output.format` + `output_path` + `sha256` + `total_pages` 渲染，PDF 额外标注请求的 content mode；不完成不显示 sha/路径；失败/拒绝显示 typed code（`EXPORT_INPUT_UNAVAILABLE`）。
4. **提示一致性**：真机截图时发现切换到 PDF 后仍残留“选择「ZIP 图片包」”提示，已修复（格式变化即刷新就绪提示）并重建复查。
5. **真机验证方法**：Debug 构建 + 隔离数据根（RELEASE-REPACK-3/data-root 副本；因 catalog/derived 命名空间绑定原路径，清理命名空间锁后由 Core 重建）+ `RELEASE-REPACK-3/sidecar-base/core-sidecar` 冻结 sidecar；真实导出产物 20,728,075 B、`%PDF-1.7`、3 个页面对象、含 `/Font` 与文本操作符（可搜索层），sha256 `c0a97eb3…` 与 UI 显示一致；未写真实 `%APPDATA%`。
6. **并发**：主工作树另有会话在改 `ThemePack.cs` / `MainWindow.axaml*`（mac 风主题）；本卡分支独立，未触碰这些文件；若其先集成，本卡 rebase 后需重跑 gate。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境 | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 ZIP | `SearchableDualLayer_IsForwarded_AndZipStaysZip` | Avalonia Headless 11.3.22 + FakeHostController | zip、pdf_content=null、`.zip`、无 PDF 模式行 | `pdf-export-ui/zip-pdf-both.json` |
| AC1 PDF image_only | `PdfFormat_SendsFormatAndPdfContent_AndPdfTargetExtension` | 同上 | pdf + image_only、`.pdf`、页/章参数精确 | `pdf-export-ui/pdf-format-params.json` |
| AC1 PDF searchable | 同上（第二段） | 同上 | pdf + searchable_dual_layer | `pdf-export-ui/zip-pdf-both.json` |
| AC2 PDF 完成 | `CompletedPdf_ShowsPathSha256PagesAndMode` | 同上 | 路径+sha256+`PDF · searchable_dual_layer`+`3 页` | `pdf-export-ui/completed-pdf.json` |
| AC2 ZIP 完成 | `CompletedZip_IsLabelledAsZipImagePack` | 同上 | `ZIP 图片包`、含 sha256/页数、无 `PDF ·` | `pdf-export-ui/completed-zip.json` |
| AC3 错误 | `FailedSnapshot_ShowsTypedError_AndRefusedStartIsExplicit` | 同上 | `导出失败（EXPORT_INPUT_UNAVAILABLE）`、`导出被拒绝` | `pdf-export-ui/errors.json` |
| AC3 契约 | `PayloadOptions_MatchTheHostIssuerPdfContract` | 无 UI | 六字段键集；HostIssuer 校验 pdf/zip→扩展名 | `pdf-export-ui/payload-contract.json` |
| AC3 真机 | 1400×900 Debug App + 隔离数据根 + 冻结 sidecar → 书架 → 进入阅读 → 导出 → 选 PDF | Windows 10.0.26300；真实 Host/Core | 面板含 PDF 选项；真实导出完成状态含路径+sha256+3 页 | `real-app-pdf-options.png`、`real-app-pdf-completed.png`、`real-app-export-metadata.json` |
| AC3 真实 PDF | 面板「开始导出」 | 真实 Host/Core | 20,728,075 B、`%PDF-1.7`、3 页、含字体/文本操作符、sha256 `c0a97eb3bac77ed538e72468034e3b80e3a989509aef0eea5bedde09b8fbb210`（=UI） | task-env `real-app-data-root/exports/`（原件不入 Git）；metadata 记录 |
| AC4 全量 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence` | Windows 10.0.26300 | **231/231**（61/55/115），0 skipped | `test/summary.json`、`test/dotnet-test-Debug.log`、`test/results-*.trx` |
| AC4 vitest / pytest | `npm test`（主仓）/ `PYTHONPATH=src python -m pytest -q`（worktree） | 旧壳/Python 未改 | 60/567；3F/2772P/9S（0 新增） | `test/vitest.log`、`test/pytest.log` |
| AC5 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/PDF-EXPORT-UI-1.md` | 本卡 + 文档提交 | PASS | 任务卡 pin |

## 接收方式

- 分支/worktree：`task/PDF-EXPORT-UI-1` / `G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1`；delivery head `6deefdcc3`。
- 复现：`verification/PDF-EXPORT-UI-1/REPORT.md §7`。
- 前置：真机复现需桌面会话 + `RELEASE-REPACK-3` 冻结 sidecar + 隔离数据根副本；真实导出会写隔离数据根 `exports/`（不写真实 `%APPDATA%`）。
- 需要 DSH 做：独立 Review（Owner 不自审）→ 重跑 test.ps1（231/231；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）→ 集成 → closeout。
- 并发说明：主工作树在途主题改动（`ThemePack.cs`/`MainWindow.axaml*`）未触碰；若先集成，本卡 rebase 后重跑 gate。

## 下一任务建议（必填）

- Task ID / 标题：**无必须由我立即释放的实现任务**；可选后续（由 DSH 裁决）：
  1. `EXPORT-HISTORY-UI-1`：导出历史行显示格式/模式/可打开产物（当前仅近期 5 条文本行）；
  2. `PDF-EXPORT-UI-2`：PDF 元数据选项（标题/作者/页码）与体积提示（本次 3 页 20.7MB 偏大，可提示 image_only/压缩权衡）。
- 推荐 Agent / Reviewer：UI 后续 = saber-ui-spec；Reviewer = 未参与实现者（DSH 排班）。
- 推荐原因与前置依赖：PDF 入口已可用；体积/元数据属体验优化，需 Core 侧确认可暴露字段后再释放。
- Recovery point：仓库 `G:/CODEX/New Manga`；delivery head `6deefdcc3`；base `2591ef028`。
- 允许修改路径：`apps/desktop-avalonia/**`、新任务卡、STATUS/PLAN/LEDGER、`verification/<新任务>/**`。
- 禁止范围：不改 Core 语义/协议/Host 契约/旧壳；不触碰他人在途文件；不 push/gc/prune；不伪造导出结果。
- 交付物：后续实现 + headless 测试 + 真机截图（如涉及 UI）+ 证据 + Handoff。
- 验证命令与完成 Gate：test.ps1 全绿（≥231）、vitest 60/567、pytest 无新增失败、`check.ps1 -TaskPath` PASS、64-hex pin、独立 Review。
- 可直接转发给 Agent 的指令：

```text
作为独立 Reviewer（未参与实现），复核 PDF-EXPORT-UI-1（delivery 6deefdcc3，walkthrough 见 doc/handoffs/PDF-EXPORT-UI-1-handoff.md 与 verification/PDF-EXPORT-UI-1/REPORT.md）。
只读：不要修改代码。核对 AC1–AC5 与 15 条 pin（sha256 与文件一致）：
1) 面板格式选择：ZIP/PDF，PDF 有 image_only/searchable_dual_layer，PDF 模式行仅 PDF 显示；
2) payload：StartExport 六字段，format=pdf 时 format_options 恰为 {"pdf_content":...}，format=zip 时 {"compression":"standard"}，HostIssuer.ValidateExportRequest 接受两者；
3) 完成态：路径+sha256+页数+格式，PDF/ZIP 文案区分，失败显示 typed code；
4) 真实证据：real-app-pdf-options.png / real-app-pdf-completed.png / real-app-export-metadata.json 与 task-env 中真实 PDF（20,728,075 B、%PDF-1.7、3 页、有文本层、sha256 c0a97eb3…）一致；
5) 重跑 pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1（应 231/231；注意其它 Agent 的 NewManga.App 占用全局互斥体时 LegacyShellRealTests 会假失败）与 dotnet test --filter FullyQualifiedName~PdfExportUiTests（应 6/6）；
6) 确认未改 Core/协议/Host 契约/旧壳、未触碰主工作树 ThemePack.cs/MainWindow.axaml*、未 push。
给出 PASS / 有条件 PASS / 返修 结论与具体证据行。
```

## 风险与遗留

1. 真实 PDF 原件 20.7MB 保留在 task-env（`real-app-data-root/exports/`），不进入 Git；复核需按 REPORT §7 重跑或直接读该文件。
2. `image_only` 未做真机导出（headless 已钉参数；composer 两种模式由 baseline-scout 真机验证）。
3. 体积提示缺失：3 页 20.7MB（高分辨率双图层），后续可加 image_only/压缩提示。
4. 未翻译章节沿用既有「没有可导出的翻译页」提示，本卡不改变导出输入面。
5. 与主工作树在途主题改动并发，rebase 后需重跑 gate。
6. 需独立 Review（Owner 不得自审）。
