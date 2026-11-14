# FEA-C07 应用端口清单（由代码生成）

状态：**FROZEN / 冻结于 2026-11-01（[冻结记录](FEA-CONTRACT-FROZEN-C07.md)）**；**2026-11-10 UNFREEZE 链 v1.2→v1.8**（v1.2 PREQ 计划追加；v1.3 READ-1 / v1.4 FONT-1 / v1.5 LIB-1 实现落地统计；v1.6 成员表同步——P1–P15 并入正式成员表；v1.7 EDIT-1 P16–P20 落地（74/81）；v1.8 AI-1 P21–P25 落地（79/86，S5 计划全部落地）；载体见 [C07](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md)、[READ1](../reviews/CONTRACT-UNFREEZE-2026-11-10-READ1.md)、[FONT1](../reviews/CONTRACT-UNFREEZE-2026-11-10-FONT1.md)、[LIB1](../reviews/CONTRACT-UNFREEZE-2026-11-10-LIB1.md)、[EDIT1](../reviews/CONTRACT-UNFREEZE-2026-11-10-EDIT1.md)、[AI1](../reviews/CONTRACT-UNFREEZE-2026-11-10-AI1.md)）；**2026-11-14 UNFREEZE v1.9（RO-1 预授权）→ v1.10（4B 落地）**（`FEA-06-RESIDUAL-4A` 为 `IHostController.ListPageRegionTextsAsync` 做 additive 预授权，见 [RO1](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md)；`FEA-06-RESIDUAL-4B` 落地端口后**统计翻转为 80/87、正式成员表并入第 #80 行**、pin 重算为 v1.10，见 [C07-4B](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-4B.md)）（本文档是脚本输出的**人工整理版**：统计表加了非方法成员说明、表头补了参数口径；**正式成员表与脚本 stdout 一一对应**，「S5 计划追加」节属人工预冻结、不计入统计，实现卡落地时并入正式表并重算）
生成日期：2026-11-02；生成时 HEAD：`a740f855f`（FEA-05-PORT-1 追加 Draft 端口后重算）；v1.6 重跑：2026-11-10；v1.7 重跑：2026-11-10；v1.8 重跑：2026-11-10（`python tools/generate_api_inventory.py` 与 `--check` 均 EXIT 0）；v1.9 重跑：2026-11-14（同一命令，stdout 仍 `1/79/6 = 86`，`--check` EXIT 0；该轮新增的「RO-1 计划追加」不计入脚本统计）；v1.10 重跑：2026-11-14（`FEA-06-RESIDUAL-4B` 端口落地后同一命令，stdout `1/80/6 = 87`，正式成员表 80 + 4 与 stdout 逐行一致，`--check` EXIT 0）
生成方式：`python tools/generate_api_inventory.py`（解析 `apps/desktop-avalonia/src/NewManga.App/Services/{IHostController.cs,RunContracts.cs}` 的 interface 块，输出成员名 + 返回类型）；**不是**手工枚举。重跑同一命令应得到同一集合。

## 用途

C-07（应用端口与兼容面）要求「由代码生成的方法清单」，替换冻结文档中的「36」口径。本文件即该清单基线：

- **`IHostController` 方法数基线 36**（V11R §5 `:239`）与 **本清单 v1.0 实测 47**（含 11 个新增；当前实测 79，见统计）是两个不同口径；「命令契约数」（冻结文档的 57）是第三种计数——三者不得互相替代；
- 新增/删除端口方法时，同一 Task 内必须同步更新本清单；
- `IHostController` 继承的接口方法按下表分别列出，实现方必须全部满足。

## 统计

| 接口 | 成员数 |
|---|---|
| IReaderProgressSink | 1 |
| IHostController | 80 |
| IRunController | 6 |
| **合计** | **87**（另有 4 个非方法成员：`HostViewSnapshot Snapshot`、`event EventHandler? Changed`、`int StartRequests`、`string ExportDirectorySuggestion`，均属 `IHostController`） |

**变更类别**：`IHostController` 的 80 个中，**36 个为 V11R §5 `:239` 基线**（签名不得变），**44 个为 FEA 期间新增**（冻结前 18 个，含 Draft 7；S5 落地 25 个 = READ-1 7 / FONT-1 4 / LIB-1 4 / EDIT-1 5 / AI-1 5；RO-1 落地 1 个 = `ListPageRegionTextsAsync`；均为 additive，冻结后同样只允许追加）。逐成员的新增/基线标注由实现 Task 在该行落地时补（本文档暂不逐行标）。

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
| 9 | `GetReadingPreferencesAsync` | `Task<ReadingPreferencesInfo?>` |
| 10 | `SaveReadingPreferencesAsync` | `Task<bool>` |
| 11 | `ListBookmarksAsync` | `Task<IReadOnlyList<BookmarkInfo>>` |
| 12 | `CreateBookmarkAsync` | `Task<string?>` |
| 13 | `DeleteBookmarkAsync` | `Task<bool>` |
| 14 | `GetBookReadingProgressAsync` | `Task<BookReadingProgressInfo?>` |
| 15 | `ResetReadingProgressAsync` | `Task<int>` |
| 16 | `ListFontAssetsAsync` | `Task<IReadOnlyList<FontAssetInfo>>` |
| 17 | `ImportFontAssetAsync` | `Task<FontAssetInfo?>` |
| 18 | `DeleteFontAssetAsync` | `Task<bool>` |
| 19 | `RefreshFontAssetsAsync` | `Task<FontRefreshInfo>` |
| 20 | `UpdateBookMetadataAsync` | `Task<bool>` |
| 21 | `ReorderChaptersAsync` | `Task<bool>` |
| 22 | `UpdateChapterMetadataAsync` | `Task<bool>` |
| 23 | `CreateChapterWithMetadataAsync` | `Task<ChapterSummary?>` |
| 24 | `ListIssueMarkersAsync` | `Task<IReadOnlyList<IssueMarkerInfo>>` |
| 25 | `CreateIssueMarkerAsync` | `Task<string?>` |
| 26 | `ResolveIssueMarkerAsync` | `Task<bool>` |
| 27 | `ReopenIssueMarkerAsync` | `Task<bool>` |
| 28 | `DeleteIssueMarkerAsync` | `Task<bool>` |
| 29 | `ListPromptTemplatesAsync` | `Task<IReadOnlyList<PromptTemplateInfo>>` |
| 30 | `SavePromptTemplateAsync` | `Task<PromptTemplateInfo?>` |
| 31 | `DeletePromptTemplateAsync` | `Task<PromptTemplateDeleteResult>` |
| 32 | `CopyBuiltinPromptTemplateAsync` | `Task<PromptTemplateInfo?>` |
| 33 | `GetPromptTemplateReferencesAsync` | `Task<IReadOnlyList<PromptTemplateReference>>` |
| 34 | `LoadPageRegionsAsync` | `Task<RegionPageProjection?>` |
| 35 | `LoadRegionRevisionsAsync` | `Task<RegionRevisionHistory?>` |
| 36 | `ReadPageImageAsync` | `Task<byte[]?>` |
| 37 | `SetRegionTypeAsync` | `Task<RegionOperationResult>` |
| 38 | `RestoreRegionRevisionAsync` | `Task<RegionOperationResult>` |
| 39 | `RerenderPageAsync` | `Task<PageRerenderOutcome>` |
| 40 | `ListCredentialTargetsAsync` | `Task<IReadOnlyList<CredentialTargetOption>>` |
| 41 | `PutCredentialAsync` | `Task<CredentialOperationResult>` |
| 42 | `ClearCredentialAsync` | `Task<CredentialOperationResult>` |
| 43 | `ListProviderProfilesAsync` | `Task<IReadOnlyList<ProviderProfileInfo>>` |
| 44 | `SaveProviderProfileAsync` | `Task<SettingsProfileResult>` |
| 45 | `DeleteProviderProfileAsync` | `Task<SettingsProfileResult>` |
| 46 | `ListNetworkProfilesAsync` | `Task<IReadOnlyList<NetworkProfileInfo>>` |
| 47 | `SaveNetworkProfileAsync` | `Task<SettingsProfileResult>` |
| 48 | `DeleteNetworkProfileAsync` | `Task<SettingsProfileResult>` |
| 49 | `SetNetworkDefaultAsync` | `Task<SettingsProfileResult>` |
| 50 | `TestNetworkProfileAsync` | `Task<NetworkTestInfo?>` |
| 51 | `ResolveNetworkProfileAsync` | `Task<NetworkResolveInfo?>` |
| 52 | `SetProviderBindingAsync` | `Task<SettingsProfileResult>` |
| 53 | `ClearProviderBindingAsync` | `Task<SettingsProfileResult>` |
| 54 | `ResolveProviderBindingAsync` | `Task<ProviderBindingResult?>` |
| 55 | `ImportFilesAsync` | `Task<ImportOutcome>` |
| 56 | `ImportFolderAsync` | `Task<ImportOutcome>` |
| 57 | `GetTranslatedPageIdsAsync` | `Task<IReadOnlyList<string>>` |
| 58 | `StartExportAsync` | `Task<ExportStartInfo?>` |
| 59 | `GetExportSnapshotAsync` | `Task<ExportSnapshotInfo?>` |
| 60 | `GetExportHistoryAsync` | `Task<IReadOnlyList<ExportHistoryEntry>>` |
| 61 | `CancelExportAsync` | `Task<ExportSnapshotInfo?>` |
| 62 | `RevealExportFolderAsync` | `Task<bool>` |
| 63 | `ListBackupsAsync` | `Task<IReadOnlyList<BackupPackageInfo>>` |
| 64 | `CreateBackupAsync` | `Task<BackupPackageInfo?>` |
| 65 | `DeleteBackupAsync` | `Task<bool>` |
| 66 | `RetryPendingCleanupsAsync` | `Task<CleanupOutcomeInfo?>` |
| 67 | `ListPluginsAsync` | `Task<PluginListInfo>` |
| 68 | `SetPluginsGlobalEnabledAsync` | `Task<bool?>` |
| 69 | `SetPluginEnabledAsync` | `Task<bool?>` |
| 70 | `GetCleanupPreviewAsync` | `Task<CleanupPreviewInfo>` |
| 71 | `RunCleanupAsync` | `Task<CleanupOutcomeInfo?>` |
| 72 | `OpenDraftAsync` | `Task<DraftLease?>` |
| 73 | `PatchDraftAsync` | `Task<Draft?>` |
| 74 | `PrepareCandidateAsync` | `Task<RegionCandidate?>` |
| 75 | `ApplyCandidatesAsync` | `Task<IReadOnlyDictionary<string, string>>` |
| 76 | `GetDraftAsync` | `Task<Draft?>` |
| 77 | `ListDraftsAsync` | `Task<IReadOnlyList<Draft>>` |
| 78 | `DiscardDraftAsync` | `Task` |
| 79 | `RestoreBackupAsync` | `Task<string?>` |
| 80 | `ListPageRegionTextsAsync` | `Task<RegionPageTextProjection?>` |
| — | `Snapshot`（属性） | `HostViewSnapshot` |
| — | `StartRequests`（属性） | `int` |
| — | `ExportDirectorySuggestion`（属性） | `string` |
| — | `Changed`（事件） | `EventHandler?` |

## IRunController

| # | 方法 | 返回类型（参数以代码为权威，本文档不列） |
|---|---|---|
| 1 | `StartRunAsync` | `Task<RunStartInfo?>` |
| 2 | `ControlRunAsync` | `Task<RunControlInfo?>` |
| 3 | `ResumeBlockedRunAsync` | `Task<RunControlInfo?>` |
| 4 | `GetRunSnapshotAsync` | `Task<RunSnapshotInfo?>` |
| 5 | `GetTaskProjectionAsync` | `Task<TaskProjectionInfo?>` |
| 6 | `RetryFailedTargetsAsync` | `Task<RunControlInfo?>` |

## S5 计划追加（FEA-14-S5-PREQ-1，2026-11-10 UNFREEZE；**25/25 已全部落地**）

> 本节由 [UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md) 引入：为 FEA-14 S5 五切片**预冻结**命令面，避免每切片各走一次 UNFREEZE。**P1–P25 已随实现卡全部落地并并入上方正式成员表**（v1.3 READ-1 P9–P15、v1.4 FONT-1 P1–P4、v1.5/v1.6 LIB-1 P5–P8、v1.7 EDIT-1 P16–P20、v1.8 AI-1 P21–P25，签名以代码为准）。本节自此**无待实现行**，仅保留本节作历史口径；上限统计以正式成员表为准。旧 54 个方法签名不变。

| # | 计划命令 | 计划返回类型 | 切片 | 语义摘要 |
|---|---|---|---|---|

计划追加合计 **25** 条（FONT 4 / LIB 4 / READ 7 / EDIT 5 / AI 5），**已全部落地**（20 → 25）；`IHostController` 74+5=**79**、三接口合计 **86**，与 PREQ 目标一致（以实测为准）。

## RO-1 计划追加（v1.9 预授权 → **v1.10 已落地 1/1**）

> 本节由 [UNFREEZE 载体](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-RO1.md) 引入，依据 [RO-1 重开裁决](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md) §3 R2 与卡 [FEA-06-RESIDUAL-4A](../tasks/FEA-06-RESIDUAL-4A.md)。与「S5 计划追加」同型：先只锁名称 / 返回类型 / 落地行号，实现卡落地后并入正式成员表。**RO-1 行已随 `FEA-06-RESIDUAL-4B` 落地，并入正式成员表第 #80 行**（[载体 C07-4B](../reviews/CONTRACT-UNFREEZE-2026-11-14-C07-4B.md)）；本节保留作历史口径，不再有未落地行。

| # | 计划命令 | 计划返回类型 | 落地卡 | 语义摘要 | 落地后行号 |
|---|---|---|---|---|---|
| RO-1 | `ListPageRegionTextsAsync` | `Task<RegionPageTextProjection?>` | `FEA-06-RESIDUAL-4B` | 逐 region 文本投影（Core `list_page_region_texts` 的 App 端口），供「查看对照」的 L1 基底文本 | `#80` |

计划追加合计 **1** 条（additive：无删除、无改名、旧 79 个方法签名零改动），**已落地 1/1**。落地口径留档：

- **v1.9（2026-11-14，预授权）**：统计保持 `IHostController 79` / 合计 `86` = 那时代码实测；正式成员表 79 + 4 = stdout 逐行一致。原因：`generate_api_inventory.py` 的计数由源码 interface 块解析（`generate_api_inventory.py:105-119`，源 `IHostController.cs`），端口未落地时提前写 80 会让成员表与 stdout 差一行、`--check`（子串判定，`:174`）必红。
- **v1.10（2026-11-14，落地）**：端口落地后同一命令 stdout 为 `1/80/6 = 87`，已并入正式成员表第 **80** 行、统计改 `80` / `87`、`--check` EXIT 0、pin 重算（见 [C-07 冻结记录](FEA-CONTRACT-FROZEN-C07.md) §3「实现注意」）。

`regionIds` 可选过滤沿用 wire 语义（非空、去重、必须属该页，否则 Core 回 `TARGET_NOT_FOUND`）；返回 `null` = 投影不可用，**不得**抛进 UI，也**不得**用空集合冒充「无可比对内容」。

## 与 C-07 冻结面的关系

- 本清单是**基线**：冻结时以本文件 + `tools/generate_api_inventory.py` 的输出为准；
- 「旧签名不变」的可验证基线 = 重跑 `python tools/generate_api_inventory.py` 并把 **stdout 全文**与上次输出 diff（成员名/返回类型都在 stdout 里）；`--check` 只比对三个**计数行**（快速冒烟，不验签名内容）。因此 v1.6 起**正式成员表必须保持与 stdout 逐行对应**（**v1.10 起为 80 个方法 + 4 个非方法成员**），计数一致不能替代逐行核对；
- 能力握手与 request-scoped error（C-07 其余内容）不在本文件展开。
- 「S5 计划追加」与「RO-1 计划追加」两节均为**人工预冻结名单**，不计入脚本统计；实现卡落地时须把对应行并入正式成员表、把统计改为实测值并重算 pin。**两节现均已全部落地**（S5 25/25 → v1.8；RO-1 1/1 → v1.10，落地行号 **#80**，见 [C-07 冻结记录](FEA-CONTRACT-FROZEN-C07.md) §3）。
