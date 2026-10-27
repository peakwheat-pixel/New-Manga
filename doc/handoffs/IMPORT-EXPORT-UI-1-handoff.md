# IMPORT-EXPORT-UI-1 Handoff（导入/导出 UI 入口）

- Task: `doc/tasks/IMPORT-EXPORT-UI-1.md`（team task-47）
- Branch: `task/IMPORT-EXPORT-UI-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1`
- Base: 卡面 `49c9e7f24`；按 Lead 指示基于 HEAD `558a48a76` 开分支，交付前 rebase 到 main `b874b2cf7`（READER-SELECTOR-UI-1 先落地；无冲突）
- Delivery head: `5019eb01dab0d9b94c0a71cafb3b96c9bb9caba2`（实现 + 证据提交；未改 Core 语义/协议/Host 契约/旧壳/packaging）
- 未 push；未 gc/prune。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 导入 | **MET** | 书架/工作台「导入文件」「导入文件夹」→ 系统选择器 → 目标书/章/重复策略 → Host grant 链 → 结果文本 + 刷新书架；真机已导入 1 个文件（8 页→9 页）。`real-run.json`、`evidence/real-run/*.ndjson`、`evidence/headless/import-export-ui/import-*.json` |
| AC2 导出 | **MET** | 阅读器「导出」→ StartExport（Host `RegisterExportTarget`→`StartExport`）→ `GetExportSnapshot` 进度 → 完成显示路径+sha256 → `GetExportHistory` → 取消 →「打开导出目录」；真机 exp-583026330d98、ZIP 7,070,562B sha `cb4d30db…`。`real-run.json`、`artifact-verify.json`、`artifacts/` |
| AC3 headless+截图 | **MET** | 10 个 headless 用例（参数 key、running→completed、cancel、typed 拒绝、无翻译页、picker 取消、工作台入口）+ 真机 11 张截图（含系统选择器与导入/导出结果） |
| AC4 回归 | **MET** | `test.ps1` **225/225 passed, 0 skipped**（61/55/109）；vitest **60/567**；pytest **3F/2772P/9S**（基线同组 3 失败，0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；31 条 64-hex pin；本 Handoff + Record Decision（REPORT §6） |

## 2. 代码清单

| 路径 | 说明 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs`（新增） | typed import/export 模型 + wire payload（Utf8JsonWriter；App 禁用反射序列化）+ 中文状态文案/文件名清洗 |
| `apps/desktop-avalonia/src/NewManga.App/Services/FilePickerGateway.cs`（新增） | `IFilePickerGateway` seam + Avalonia StorageProvider 实现（打开文件多选/选择文件夹/另存为） |
| `Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs` | 导入走 Host grant 链（`RegisterImportSource`→`ImportPages`）；导出走 Host grant + StartExport；snapshot/history/cancel 命令面；translated 页发现（`GetReaderProjection` translated）；reveal shell action；全部 typed outcome |
| `Views/ImportExportPanels.cs`（新增） | ImportPanel（目标书/章/策略 + 不确定进度 + typed 结果）；ExportPanel（页数/开始/取消/打开目录/进度条/历史） |
| `Views/Pages.cs` | 书架 header 双入口 + overlay + 成功后刷新 |
| `Views/ReaderWorkbenchPages.cs` | 工作台左栏双入口；阅读器 toolbar「导出」+ 面板接线 |
| `Views/MainWindow.axaml.cs` | picker 注入（可选参数供 headless）+ 三页接线 |
| `tests/NewManga.App.Tests/ImportExportUiTests.cs`（新增） | 10 个 headless 用例（含 6 份证据 JSON 写入） |

## 3. 真机复现（关键）

```powershell
$env:NEWMANGA_DATA_ROOT='<task-env>/screenshot-root'   # RELEASE-REPACK-2 completed-run 的私有副本
apps/desktop-avalonia/src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe `
  --data-root=$env:NEWMANGA_DATA_ROOT `
  --sidecar-dir='<task-env>/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models/app/core-sidecar' `
  --parity --log-dir='<task-env>/app-logs'
# 书架 → 导入文件（系统选择器）→ 选择目标章 → 开始导入
# 阅读器 → 导出 → 开始导出 → 看到「导出完成 + sha256」→ 打开导出目录
```

- 真实产物：`screenshot-root/exports/BOOK-FIXTURE-1 日漫_JA 测试书-第 1 章-20261027-144637.zip`（7,070,562B / sha256 `cb4d30db7c61f73169c74ca3a36b21e82df196333a44df36b001bb67696788c1`，exp-583026330d98）。
- wire 帧：`RegisterImportSource`→`ImportPages`；`RegisterExportTarget`→`StartExport`→`GetExportSnapshot`→`GetExportHistory`（`evidence/real-run/core-service.ndjson`）。
- 独立复算：ZIP 4 条目（3 页 + manifest.json），逐页条目字节 sha256 = manifest = 落库 translated revision（`artifact-verify.json`）。

## 4. 关键决策与说明（完整见 REPORT §6）

1. **UI 不伪造**：进度为真实 snapshot 派生（不确定进度条或 completed/total）；结果文本来自 Host typed outcome，失败显示 code。
2. **继承既有安全边界**：导入 grant/源路径校验（GRANT-ISSUER-1）、导出目标限数据根 exports（EXPORT-E2E-CLOSE-1）；本卡零协议/Host 契约改动。
3. **选择器可测**：系统 picker 抽为 seam，headless fake 驱动同一流程。
4. **取消语义**：仅 pending/running/publishing 可取消；取消后不发产物。
5. **rebase 说明**：交付前 rebase 到 `b874b2cf7`（READER-SELECTOR-UI-1）；仅 `Views/Pages.cs` 同文件不同区域自动合并。真机截图取自 rebase 前同一实现的 Debug 构建（导入/导出代码 rebase 未变），final 全量回归在 rebase 后树上重跑（225/225）。
6. **真机首启备注**：第一次启动因参数引用方式错误使用了默认 log 目录（仅一条 host.log 失败记录）；修正后所有运行使用隔离 data root 与 `--log-dir`，真实 `%APPDATA%` 书库/凭据库未触碰（`real-run.json` safety 记录）。

## 5. 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/IMPORT-EXPORT-UI-1.md` → PASS（见 Task 卡收口）。
- Canonical Evidence：31 条 64-hex sha256 pin（23 条 CANONICAL + 8 条 SOURCE_PIN）；Resource Manifest 指向 task-env 与产物。

## 6. 遗留

1. **仅 ZIP 导出接入 UI**：PDF（需 Qt composer）/CBZ/text 未接入（Core 已支持，UI 需格式矩阵 Task）。
2. **真实取消点击未捕获**：3 页 ZIP 约 200ms 完成，人速点击赶不上 running 窗口；取消状态迁移由 headless 用例确定性覆盖，真机记录到两次成功导出。
3. **导入多选**：代码支持列表导入，真机只手工导入 1 个文件；多选/文件夹由 headless 覆盖。
4. **导出自定义路径**：默认 Host exports/ 确定性文件名；`PickExportTarget` seam 已实现但真机流程未使用（Host 白名单仍在）。
5. 大书/多章导出性能未测；translated 内容来自 identity EXPERIMENTAL 占位，不构成翻译质量验收。
6. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。
