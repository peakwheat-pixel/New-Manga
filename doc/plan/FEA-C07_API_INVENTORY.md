# FEA-C07 应用端口清单（由代码生成）

状态：**FROZEN / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C07.md)）**；**2026-11-10 UNFREEZE v1.2**（新增「S5 计划追加」节，代码统计不变，见 [UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)）（本文档是脚本输出的**人工整理版**：统计表加了非方法成员说明、表头补了参数口径；**正式成员表与脚本 stdout 一一对应**，「S5 计划追加」节属人工预冻结、不计入统计，实现卡落地时并入正式表并重算）
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
| IHostController | 65 |
| IRunController | 6 |
| **合计** | **72**（另有 4 个非方法成员：`HostViewSnapshot Snapshot`、`event EventHandler? Changed`、`int StartRequests`、`string ExportDirectorySuggestion`，均属 `IHostController`） |

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

## S5 计划追加（FEA-14-S5-PREQ-1，2026-11-10 UNFREEZE；**尚未实现**）

> 本节由 [UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md) 引入：为 FEA-14 S5 五切片**预冻结**命令面，避免每切片各走一次 UNFREEZE。**本节成员尚未存在于代码**，不计入上方统计（统计仍是代码实测 61）；各实现卡落地时按冻结记录 §3 重跑脚本、把这些行并入正式成员表并重算统计/pin。旧 54 个方法签名不变。

| # | 计划命令 | 计划返回类型 | 切片 | 语义摘要 |
|---|---|---|---|---|
| P1 | `ListFontAssetsAsync` | `Task<IReadOnlyList<FontAssetInfo>>` | FONT-1 | 列出用户字体库资产 |
| P2 | `ImportFontAssetAsync` | `Task<FontAssetInfo?>` | FONT-1 | 导入字体文件（复制+sha256；原文件不动；≤50MB/≤200；逐文件拒绝） |
| P3 | `DeleteFontAssetAsync` | `Task<bool>` | FONT-1 | 软删库内资产（不删原文件） |
| P4 | `RefreshFontAssetsAsync` | `Task<FontRefreshInfo>` | FONT-1 | 重扫 `fonts/` 并报告可用/失败 |
| P5 | `UpdateBookMetadataAsync` | `Task<bool>` | LIB-1 | 书元数据 patch（重名规范化唯一约束） |
| P6 | `ReorderChaptersAsync` | `Task<bool>` | LIB-1 | 章/卷/番外排序（自定义排序保位/数字排序重排） |
| P7 | `UpdateChapterMetadataAsync` | `Task<bool>` | LIB-1 | 章元数据/类型/编号 patch |
| P8 | `CreateChapterWithMetadataAsync` | `Task<ChapterSummary?>` | LIB-1 | 带 kind/编号创建（不改既有 `CreateChapterAsync`） |
| P9 | `GetReadingPreferencesAsync` | `Task<ReadingPreferencesInfo?>` | READ-1 | 按书阅读偏好读 |
| P10 | `SaveReadingPreferencesAsync` | `Task<bool>` | READ-1 | 按书阅读偏好写（单写者） |
| P11 | `ListBookmarksAsync` | `Task<IReadOnlyList<BookmarkInfo>>` | READ-1 | 书签列表 |
| P12 | `CreateBookmarkAsync` | `Task<BookmarkInfo?>` | READ-1 | 新建书签（双页 left/right/both） |
| P13 | `DeleteBookmarkAsync` | `Task<bool>` | READ-1 | 删书签（不影响漫画/进度/人工修改） |
| P14 | `GetBookReadingProgressAsync` | `Task<BookProgressInfo?>` | READ-1 | 整书总进度（按页面数） |
| P15 | `ResetReadingProgressAsync` | `Task<bool>` | READ-1 | 重置进度（需确认） |
| P16 | `ListIssueMarkersAsync` | `Task<IReadOnlyList<IssueMarkerInfo>>` | EDIT-1 | 问题标记列表（默认待处理） |
| P17 | `CreateIssueMarkerAsync` | `Task<IssueMarkerInfo?>` | EDIT-1 | 新建整页/位置标记 |
| P18 | `ResolveIssueMarkerAsync` | `Task<bool>` | EDIT-1 | 标记解决 |
| P19 | `ReopenIssueMarkerAsync` | `Task<bool>` | EDIT-1 | 标记重开 |
| P20 | `DeleteIssueMarkerAsync` | `Task<bool>` | EDIT-1 | 删除标记（不影响漫画/人工修改） |
| P21 | `ListPromptTemplatesAsync` | `Task<IReadOnlyList<PromptTemplateInfo>>` | AI-1 | 模板列表（内置只读+自建） |
| P22 | `SavePromptTemplateAsync` | `Task<PromptTemplateInfo?>` | AI-1 | 保存自建模板（内置不可覆盖） |
| P23 | `DeletePromptTemplateAsync` | `Task<PromptTemplateDeleteResult>` | AI-1 | 删除（须选替代；仍有引用不删） |
| P24 | `CopyBuiltinPromptTemplateAsync` | `Task<PromptTemplateInfo?>` | AI-1 | 复制内置为可编辑副本 |
| P25 | `GetPromptTemplateReferencesAsync` | `Task<IReadOnlyList<PromptTemplateReference>>` | AI-1 | 删除前引用清单 |

计划追加合计 **25** 条（FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5）；实现完成后 `IHostController` 目标 54+25=79，三接口合计 61+25=86（以各卡实测为准）。

## 与 C-07 冻结面的关系

- 本清单是**基线**：冻结时以本文件 + `tools/generate_api_inventory.py` 的输出为准；
- 「旧签名不变」的可验证基线 = 重跑 `python tools/generate_api_inventory.py` 并把 **stdout 全文**与上次输出 diff（成员名/返回类型都在 stdout 里）；`--check` 只比对三个**计数行**（快速冒烟，不验签名内容）；
- 能力握手与 request-scoped error（C-07 其余内容）不在本文件展开。
