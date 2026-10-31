# FEA-C07 应用端口清单（由代码生成）

状态：**GENERATED / 草案依据 / 未冻结**
生成日期：2026-11-01；生成时 HEAD：`e7e43543b`
生成方式：解析 `apps/desktop-avalonia/src/NewManga.App/Services/{IHostController.cs,RunContracts.cs}` 的 interface 块（成员名 + 返回类型）；**不是**手工枚举。

## 用途

C-07（应用端口与兼容面）要求「由代码生成的方法清单」，替换冻结文档中的「36」口径。本文件即该清单基线：

- **命令契约数**（冻结文档的 36/57 口径）与 **C# 端口方法数** 是两个不同计数，不得互相替代；
- 新增/删除端口方法时，同一 Task 内必须同步更新本清单；
- `IHostController` 继承的接口方法按下表分别列出，实现方必须全部满足。

## 统计

| 接口 | 成员数 |
|---|---|
| IReaderProgressSink | 1 |
| IHostController | 47 |
| IRunController | 6 |
| **合计** | **54** |

## IReaderProgressSink

| # | 方法 | 返回类型 |
|---|---|---|
| 1 | `SaveReadingProgressAsync` | `Task<ReaderProgressSaveResult>` |

## IHostController

| # | 方法 | 返回类型 |
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

## IRunController

| # | 方法 | 返回类型 |
|---|---|---|
| 1 | `StartRunAsync` | `Task<RunStartInfo?>` |
| 2 | `ControlRunAsync` | `Task<RunControlInfo?>` |
| 3 | `ResumeBlockedRunAsync` | `Task<RunControlInfo?>` |
| 4 | `GetRunSnapshotAsync` | `Task<RunSnapshotInfo?>` |
| 5 | `GetTaskProjectionAsync` | `Task<TaskProjectionInfo?>` |
| 6 | `RetryFailedTargetsAsync` | `Task<RunControlInfo?>` |

## 与 C-07 冻结面的关系

- 本清单是**基线**：冻结时以本文件 + 生成脚本为准；
- 「旧签名不变」的可验证基线 = 反复运行生成脚本得到同一集合；
- 能力握手与 request-scoped error（C-07 其余内容）不在本文件展开。
