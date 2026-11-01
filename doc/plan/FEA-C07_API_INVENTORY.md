# FEA-C07 应用端口清单（由代码生成）

状态：**FROZEN / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C07.md)）**（本文档是脚本输出的**人工整理版**：统计表加了非方法成员说明、表头补了参数口径，成员行与脚本 stdout 一一对应）
生成日期：2026-11-02；生成时 HEAD：`a740f855f`（FEA-05-PORT-1 追加 Draft 端口后重算）
生成方式：`python tools/generate_api_inventory.py`（解析 `apps/desktop-avalonia/src/NewManga.App/Services/{IHostController.cs,RunContracts.cs}` 的 interface 块，输出成员名 + 返回类型）；**不是**手工枚举。重跑同一命令应得到同一集合。

## 用途

C-07（应用端口与兼容面）要求「由代码生成的方法清单」，替换冻结文档中的「36」口径。本文件即该清单基线：

- **`IHostController` 方法数基线 36**（V11R §5 `:239`）与 **本清单实测 47**（含 11 个新增）是两个不同口径；「命令契约数」（冻结文档的 57）是第三种计数——三者不得互相替代；
- 新增/删除端口方法时，同一 Task 内必须同步更新本清单；
- `IHostController` 继承的接口方法按下表分别列出，实现方必须全部满足。

## 统计

| 接口 | 成员数 |
|---|---|
| IReaderProgressSink | 1 |
| IHostController | 54 |
| IRunController | 6 |
| **合计** | **61**（另有 4 个非方法成员：`HostViewSnapshot Snapshot`、`event EventHandler? Changed`、`int StartRequests`、`string ExportDirectorySuggestion`，均属 `IHostController`） |

**变更类别**：`IHostController` 的 54 个中，**36 个为 V11R §5 `:239` 基线**（签名不得变），**18 个为 FEA 期间新增**（additive；冻结后同样只允许追加）。逐成员的新增/基线标注由实现 Task 在该行落地时补（本文档暂不逐行标）。

## IReaderProgressSink

| # | 方法 | 返回类型（参数以代码为权威，本文档不列） |
|---|---|---|
| 1 | `SaveReadingProgressAsync` | `Task<ReaderProgressSaveResult>` |

## IHostController

| # | 方法 | 返回类型（参数以代码为权威，本文档不列） |
|---|---|---|
| 1 | `StartAsync` | `Task` |
| 2 | `RefreshBooksAsync` | `Task` |
| 3 | `TryChineseRoundTripAsync` | `Task<bool>` |
| 4 | `TryCreateBookAsync` | `Task<bool>` |
| 5 | `CreateChapterAsync` | `Task<ChapterSummary?>` |
| 6 | `LoadReaderBookAsync` | `Task<ReaderBookData?>` |
| 7 | `ListChaptersAsync` | `Task<IReadOnlyList<ChapterSummary>>` |
| 8 | `ListChapterPagesAsync` | `Task<IReadOnlyList<ChapterPageSummary>>` |
| 9 | `LoadPageRegionsAsync` | `Task<RegionPageProjection?>` |
| 10 | `LoadRegionRevisionsAsync` | `Task<RegionRevisionHistory?>` |
| 11 | `ReadPageImageAsync` | `Task<byte[]?>` |
| 12 | `SetRegionTypeAsync` | `Task<RegionOperationResult>` |
| 13 | `RestoreRegionRevisionAsync` | `Task<RegionOperationResult>` |
| 14 | `RerenderPageAsync` | `Task<PageRerenderOutcome>` |
| 15 | `ListCredentialTargetsAsync` | `Task<IReadOnlyList<CredentialTargetOption>>` |
| 16 | `PutCredentialAsync` | `Task<CredentialOperationResult>` |
| 17 | `ClearCredentialAsync` | `Task<CredentialOperationResult>` |
| 18 | `ListProviderProfilesAsync` | `Task<IReadOnlyList<ProviderProfileInfo>>` |
| 19 | `SaveProviderProfileAsync` | `Task<SettingsProfileResult>` |
| 20 | `DeleteProviderProfileAsync` | `Task<SettingsProfileResult>` |
| 21 | `ListNetworkProfilesAsync` | `Task<IReadOnlyList<NetworkProfileInfo>>` |
| 22 | `SaveNetworkProfileAsync` | `Task<SettingsProfileResult>` |
| 23 | `DeleteNetworkProfileAsync` | `Task<SettingsProfileResult>` |
| 24 | `SetNetworkDefaultAsync` | `Task<SettingsProfileResult>` |
| 25 | `TestNetworkProfileAsync` | `Task<NetworkTestInfo?>` |
| 26 | `ResolveNetworkProfileAsync` | `Task<NetworkResolveInfo?>` |
| 27 | `SetProviderBindingAsync` | `Task<SettingsProfileResult>` |
| 28 | `ClearProviderBindingAsync` | `Task<SettingsProfileResult>` |
| 29 | `ResolveProviderBindingAsync` | `Task<ProviderBindingResult?>` |
| 30 | `ImportFilesAsync` | `Task<ImportOutcome>` |
| 31 | `ImportFolderAsync` | `Task<ImportOutcome>` |
| 32 | `GetTranslatedPageIdsAsync` | `Task<IReadOnlyList<string>>` |
| 33 | `StartExportAsync` | `Task<ExportStartInfo?>` |
| 34 | `GetExportSnapshotAsync` | `Task<ExportSnapshotInfo?>` |
| 35 | `GetExportHistoryAsync` | `Task<IReadOnlyList<ExportHistoryEntry>>` |
| 36 | `CancelExportAsync` | `Task<ExportSnapshotInfo?>` |
| 37 | `RevealExportFolderAsync` | `Task<bool>` |
| 38 | `ListBackupsAsync` | `Task<IReadOnlyList<BackupPackageInfo>>` |
| 39 | `CreateBackupAsync` | `Task<BackupPackageInfo?>` |
| 40 | `DeleteBackupAsync` | `Task<bool>` |
| 41 | `RetryPendingCleanupsAsync` | `Task<CleanupOutcomeInfo?>` |
| 42 | `ListPluginsAsync` | `Task<PluginListInfo>` |
| 43 | `SetPluginsGlobalEnabledAsync` | `Task<bool?>` |
| 44 | `SetPluginEnabledAsync` | `Task<bool?>` |
| 45 | `GetCleanupPreviewAsync` | `Task<CleanupPreviewInfo>` |
| 46 | `RunCleanupAsync` | `Task<CleanupOutcomeInfo?>` |
| 47 | `RestoreBackupAsync` | `Task<string?>` |
| 48 | `OpenDraftAsync` | `Task<DraftLease?>` |
| 49 | `PatchDraftAsync` | `Task<Draft?>` |
| 50 | `PrepareCandidateAsync` | `Task<RegionCandidate?>` |
| 51 | `ApplyCandidatesAsync` | `Task<IReadOnlyDictionary<string, string>>` |
| 52 | `GetDraftAsync` | `Task<Draft?>` |
| 53 | `ListDraftsAsync` | `Task<IReadOnlyList<Draft>>` |
| 54 | `DiscardDraftAsync` | `Task` |

## IRunController

| # | 方法 | 返回类型（参数以代码为权威，本文档不列） |
|---|---|---|
| 1 | `StartRunAsync` | `Task<RunStartInfo?>` |
| 2 | `ControlRunAsync` | `Task<RunControlInfo?>` |
| 3 | `ResumeBlockedRunAsync` | `Task<RunControlInfo?>` |
| 4 | `GetRunSnapshotAsync` | `Task<RunSnapshotInfo?>` |
| 5 | `GetTaskProjectionAsync` | `Task<TaskProjectionInfo?>` |
| 6 | `RetryFailedTargetsAsync` | `Task<RunControlInfo?>` |

## 与 C-07 冻结面的关系

- 本清单是**基线**：冻结时以本文件 + `tools/generate_api_inventory.py` 的输出为准；
- 「旧签名不变」的可验证基线 = 重跑 `python tools/generate_api_inventory.py` 并把 **stdout 全文**与上次输出 diff（成员名/返回类型都在 stdout 里）；`--check` 只比对三个**计数行**（快速冒烟，不验签名内容）；
- 能力握手与 request-scoped error（C-07 其余内容）不在本文件展开。
