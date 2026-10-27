# IMPORT-EXPORT-UI-1 交付报告：导入/导出 UI 入口

- Task: `doc/tasks/IMPORT-EXPORT-UI-1.md`（team task-47）；Owner `route-research`；Reviewer `dsh`
- Branch: `task/IMPORT-EXPORT-UI-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/IMPORT-EXPORT-UI-1`
- Base: 卡面 `49c9e7f24`；按 Lead 指示基于当前 HEAD `558a48a76` 开分支，交付前 rebase 到 main `b874b2cf7`（READER-SELECTOR-UI-1 先落地；无冲突，仅 `Views/Pages.cs` 同文件不同区域自动合并）
- Delivery head: `__DELIVERY_HEAD__`（实现 + 证据提交；未改 Core 语义/协议/Host 契约/旧壳/packaging）
- 结论: **AC1–AC5 全部达成**——用户从书架/工作台真实导入文件、从阅读器真实导出 ZIP 并看到进度/历史/可取消/打开目录；真机截图 11 张 + 真实产物入库。

## 0. 结论

| AC | 判定 | 一句话 |
|---|---|---|
| AC1 导入 | **MET** | 书架/工作台「导入文件」「导入文件夹」→ 系统选择器 → 目标书/章/重复策略 → Host grant 链导入 → 进度/结果 + 刷新书架（真机：已导入 1 个文件，8 页→9 页） |
| AC2 导出 | **MET** | 阅读器「导出」→ 对当前书发 `StartExport`（Host grant）→ `GetExportSnapshot` 轮询进度 → 完成显示路径+sha256 → `GetExportHistory` → 可取消 → 「打开导出目录」（真机：exp-583026330d98，ZIP 7,070,562B sha `cb4d30db…`） |
| AC3 headless + 截图 | **MET** | 10 个 headless 用例精确覆盖命令参数与状态迁移（pending/running→completed、cancel、typed 拒绝、无翻译页、picker 取消）；真机截图 11 张（选择器/导入面板/结果/导出面板/完成/历史/打开目录/工作台入口） |
| AC4 回归 | **MET** | `test.ps1` **225/225 passed, 0 skipped**（coreclient 61 / host 55 / app 109，含本卡 10 例）；vitest **60 文件/567 用例**；pytest **3F/2772P/9S**（与基线同一组 3 失败，0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex sha256 pin；Handoff + Record Decision |

## 1. UI 结构（全部 `apps/desktop-avalonia/**`）

| 入口 | 文件 | 行为 |
|---|---|---|
| 书架「导入文件/导入文件夹」 | `Views/Pages.cs`（BookshelfPage header） | 点击即调系统选择器（Avalonia StorageProvider）→ 打开 ImportPanel（目标书 ComboBox / 目标章 ComboBox / 重复策略）→ 「开始导入」→ 进度条（不确定态，不伪造百分比）→ 结果文本 → 成功后刷新书架 |
| 工作台「导入文件/导入文件夹」 | `Views/ReaderWorkbenchPages.cs`（WorkbenchPage 左栏） | 同一 ImportPanel；完成后刷新 Host 书架快照 |
| 阅读器「导出」 | `Views/ReaderWorkbenchPages.cs`（ReaderPage toolbar） | 仅在有真实书库书时可见；打开 ExportPanel：当前书/章/可导出页数（来自 translated 投影）、最近导出历史、开始/取消/打开导出目录/关闭 |
| 系统选择器 seam | `Services/FilePickerGateway.cs` | `IFilePickerGateway`（PickFiles/PickFolder/PickExportTarget）+ Avalonia StorageProvider 实现；headless 用 fake 驱动同一流程 |
| 控制器 seam | `Services/IHostController.cs`、`HostController.cs`、`NullHostController.cs` | 导入走 Host grant 链（`RegisterImportSource`→`ImportPages`）；导出走 `HostGrantCoordinator.StartExportAsync`（host-control `RegisterExportTarget`→`StartExport`）；snapshot/history/cancel 为 Host 命令面；reveal 为 Host shell action。全部 typed outcome，不向 UI 抛异常 |
| 契约/文案 | `Services/ImportExportContracts.cs` | typed ImportOutcome / ExportStartInfo / ExportSnapshotInfo / ExportHistoryEntry；wire payload 用 `Utf8JsonWriter` 构造（App 禁用反射序列化）；状态中文文案、默认文件名清洗 |

## 2. AC1 导入（真机 + headless）

**headless**（`tests/NewManga.App.Tests/ImportExportUiTests.cs`）：fake picker → 书架按钮 → ImportPanel → 开始导入；断言 Host 收到 `chapter_id` / `paths` / `duplicate_policy`，成功后才刷新书架、失败展示 typed code 且不刷新、picker 取消不打开面板、工作台同样入口、payload key 集合与 dispatcher 一致。

**真机**（Debug `NewManga.App.exe`，隔离 `--data-root` + `--sidecar-dir`（RELEASE-REPACK-2 models）+ `--parity` + 私有 `--log-dir`）：
- 书架 → 导入文件 → Windows 选择器（截图 08/09）→ ImportPanel（截图 10）→ 开始导入 → **已导入 1 个文件**、书架刷新 **8 页 → 9 页**（截图 11）。
- wire 证据：`host-control RegisterImportSource` + `ImportPages`（`evidence/real-run/core-service.ndjson`）。

## 3. AC2 导出（真机 + headless）

**headless**：ExportPanel 从 controller 取 translated 页 → 开始导出参数（book/chapter/page ids/target 在 Host exports 目录下）→ 脚本化 snapshot `running(1/2)` → `completed(2/2)` → 进度条 50%、取消按钮在 running 可用、完成后 reveal 可用、历史列出真实记录；取消用例：`CancelExport`→`cancelled` 且 reveal 禁用；无翻译页时 Start 禁用；StartExport 被拒绝时显示 typed 原因。

**真机**：
- 阅读器当前书（BOOK-FIXTURE，第 1 章，8 页，3 页 translated）→ 导出面板（截图 03，显示 3 页可导出 + 真实历史 exp-268d58e2d983/exp-827c4833b7cf）→ 开始导出 → **导出完成**，产物 `exports/BOOK-FIXTURE-1 日漫_JA 测试书-第 1 章-20261027-144637.zip`，**7,070,562 B / sha256 cb4d30db7c61f73169c74ca3a36b21e82df196333a44df36b001bb67696788c1**，历史新增 `exp-583026330d98 · zip · 导出完成`（截图 04）；「打开导出目录」→ **已打开导出目录**（截图 05）。
- 独立复算（`artifact-verify.json`）：ZIP 4 条目（3 页 + manifest.json），逐页条目字节 sha256 = manifest = 落库 translated revision。
- wire 证据：`RegisterExportTarget`（host-control）→ `StartExport` → `GetExportSnapshot`×N → `GetExportHistory`。
- 第二次导出（截图 06）同样完成（exp-0bf422817526，sha f5a7bf32…），证明可重复；**取消的真实点击未赶上 200ms 的导出窗口**，如实记录：取消状态迁移由 headless 用例确定性覆盖。

## 4. AC3 headless 覆盖（10 例）+ 真机截图

| 用例 | 覆盖 |
|---|---|
| Payloads_MatchTheImportExportCommandFaces | import file/folder key 集、start_export 六字段（无 target_ref，由 Host 追加）、export_id、默认文件名清洗 |
| Bookshelf_ImportFiles_CallsHostWithPickerPathsChapterAndRefreshes | 参数 + 仅成功刷新 |
| Bookshelf_ImportFolder_PassesTheFolderPathAndPolicy | folder path + import_as_new 策略 |
| Bookshelf_ImportTypedFailure_ShowsCodeAndDoesNotRefresh | typed 失败不刷新 |
| Bookshelf_ImportPickerCancel_LeavesFlowClosed | picker 取消 |
| Workbench_ImportFiles_OpensTheSameFlow | 工作台入口一致 |
| Reader_ExportFlow_StartPollCompleteHistoryReveal | 参数、running→completed、历史、reveal |
| Reader_ExportCancel_WhileRunning_MarksRecordCancelled | cancel 状态迁移 |
| Reader_ExportWithoutTranslatedPages_DisablesStart | 无输入态 |
| Reader_ExportStartRefused_ShowsTypedReason | StartExport 拒绝态 |

headless 证据 JSON：`evidence/headless/import-export-ui/*.json`（payload-contract / import-files / import-folder / export-flow / export-cancel / export-reveal）。

真机截图 11 张（`real-run.json` 内逐张 sha256 + shows）：书架导入入口、阅读器导出入口、导出面板、导出完成、已打开目录、第二次导出、工作台导入入口、系统选择器、选择器填入、导入面板、导入完成。

## 5. AC4 回归/证据

| 门 | 结果 |
|---|---|
| `apps/desktop-avalonia/scripts/test.ps1` | **225/225 passed, 0 skipped**（coreclient 61 / host 55 / app 109；本卡新增 app 10 例；基线 main b874b2cf7 为 215/215，+10 全为本卡用例） |
| vitest（`apps/desktop/frontend`） | **60 files / 567 tests passed**（未改旧壳前端） |
| pytest（worktree） | **3F/2772P/9S**（失败集合 = 基线同组：detection real ×2 + workbench viewmodel ×1；本卡未改 Python） |
| 治理 | `check.ps1 -TaskPath` PASS（Task 卡收口） |

日志：`evidence/test-ps1.log`、`evidence/dotnet/{summary.json,dotnet-test-Debug.log,results-app.trx}`、`evidence/vitest.log`、`evidence/pytest.log`。

## 6. Record Decision

1. **verification-first UI**：所有导入/导出结果均来自 Host/Core 真实返回；UI 不伪造进度（只显示不确定进度条或真实 completed/total）、不伪造成功（失败显示 typed code）。
2. **继承既有边界**：导入 grant 由 HostIssuer 签发、源路径由 Host 校验（GRANT-ISSUER-1）；导出目标被 Host 限制在数据根 exports/（EXPORT-E2E-CLOSE-1）；本卡零协议/Host 契约改动。
3. **选择器可测**：系统 picker 抽成 `IFilePickerGateway` seam，生产用 Avalonia StorageProvider，headless 用 fake；避免 UI 直接依赖 OS 对话框。
4. **取消语义**：ExportPanel 只在 job 处于 pending/running/publishing 时允许「取消导出」；取消后不发产物（与 Core `before_publish` 检查一致）。
5. **真机环境**：Debug 构建 + 隔离 data root（RELEASE-REPACK-2 completed-run 副本）+ RELEASE-REPACK-2 models sidecar + `--parity`；真实 `%APPDATA%` 书库与凭据库未触碰（首次启动因参数引用方式写了一条默认 log 行，已在 real-run.json 记录；之后全部隔离）。
6. **rebase 说明**：实现分支 rebase 到 main `b874b2cf7`（READER-SELECTOR-UI-1 先落地）；冲突仅 `Views/Pages.cs` 同文件不同区域，自动合并成功；真机截图取自 rebase 前同一实现的 Debug 构建（导入/导出代码 rebase 未变），final 回归在 rebase 后树上重跑。

## 7. 遗留 / NOT_RUN

1. **PDF/CBZ/text 导出格式**未接入 UI：本卡 UI 只提供 ZIP 图片包（与 EXPORT-E2E-CLOSE-1 验证的格式一致）；PDF 依赖 Qt composer，需另开格式矩阵。
2. **真实取消点击未捕获**：3 页 ZIP 约 200ms 完成，人速点击赶不上 running 窗口；取消迁移已由 headless 确定性覆盖，真机只记录到两次完成。
3. **导入多选**：系统选择器支持多选（代码按列表导入），真机只手工导入 1 个文件；多选/文件夹由 headless 覆盖。
4. **导出目标自定义路径**：当前默认 Host exports/ 下的确定性文件名；`PickExportTarget` seam 已实现但未在真机截图流程中使用（Host 白名单限制仍在）。
5. 大书/多章导出性能未测；translated 内容来自 identity EXPERIMENTAL 占位，不构成翻译质量验收。
6. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。

## 8. 复跑方式

```powershell
# headless：10 个导入/导出 UI 用例（fake controller + fake picker，隔离 %APPDATA%）
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~ImportExportUiTests"

# 真机：Debug 构建 + 隔离数据根 + 新 sidecar（导入/导出都真实走 Host grant 链）
$env:NEWMANGA_DATA_ROOT='<task-env>/screenshot-root'   # RELEASE-REPACK-2 completed-run 的副本
apps/desktop-avalonia/src/NewManga.App/bin/Debug/net9.0/NewManga.App.exe `
  --data-root=$env:NEWMANGA_DATA_ROOT `
  --sidecar-dir='<task-env>/RELEASE-REPACK-2/out/NewManga-0.1.0-win-x64-models/app/core-sidecar' `
  --parity --log-dir='<task-env>/app-logs'

# 独立复算真实导出 ZIP
python verification/EXPORT-E2E-CLOSE-1/tools/verify_export_records.py --help   # 同型复算见本卡 artifact-verify.json
```
