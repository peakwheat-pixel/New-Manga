# FEA-14 S5 共用 wire 契约包（PREQ AC2）

- Task：`FEA-14-S5-PREQ-1`；日期：2026-11-10；作者：DSH
- 性质：**命令面预冻结**（additive；尚未实现）。各切片实现卡只消费本清单，不得再扩 wire。
- 目标：五切片（FONT/LIB/READ/EDIT/AI）的 `IHostController` 增量**一次**列清，走**一次** C-07 UNFREEZE（`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`），避免五次。

## 1. 约束

1. 只 **additive**：不改/不删现有 54 个 `IHostController` 方法签名（C-07 旧签名不变）。
2. 实现卡落地时，按 `FEA-CONTRACT-FROZEN-C07.md:43` 在同一 Task 内重跑 `tools/generate_api_inventory.py`、更新清单统计与成员表、重算 pin；本清单先作为**计划追加节**挂在 inventory 文档，不改变代码实测统计（61）。
3. 未知请求/能力一律 typed 拒绝（不静默降级）；只读 Host（`WritesAllowed=false`）下写命令必须拒绝。
4. payload/DTO 命名沿用现有风格（`*Info` 读模型、`*Draft`/`*Patch`/`*Request` 写模型）；本清单锁**名称/返回类型/语义/Host command id/Core wire/minor/payload 键**（§8），实现卡可加可选键但不得改已有键名/语义。
5. 若实现中确需改名/改形，须回流本 PREQ 重新裁决（不得在实现卡内顺手变更）。

## 2. FONT（`FEA-14-FONT-1/2`）

| # | 命令 | 返回类型 | 语义 |
|---|---|---|---|
| 1 | `ListFontAssetsAsync` | `Task<IReadOnlyList<FontAssetInfo>>` | 列出用户字体库资产（家族/变体/格式/字节数/状态） |
| 2 | `ImportFontAssetAsync` | `Task<FontAssetInfo?>` | 导入字体文件（复制到数据根 `fonts/` + SHA-256；原文件不动；≤50MB/≤200 个；损坏逐文件 typed 拒绝） |
| 3 | `DeleteFontAssetAsync` | `Task<bool>` | 软删库内资产（引用检查由 FONT-2 UI 消费；不删原文件） |
| 4 | `RefreshFontAssetsAsync` | `Task<FontRefreshInfo>` | 重扫 `fonts/`，报告可用/失败数量与原因 |

域：`fonts`；不随包任何字体（用户导入 only）。

## 3. LIB（`FEA-14-LIB-1`，需 LIB-PREREQ 先裁形状）

| # | 命令 | 返回类型 | 语义 |
|---|---|---|---|
| 5 | `UpdateBookMetadataAsync` | `Task<bool>` | 书名/作者/简介/标签等元数据 patch（重名规范化唯一约束在 Core 事务内重验） |
| 6 | `ReorderChaptersAsync` | `Task<bool>` | 章/卷/番外排序（`orderedIds`；自定义排序保位，数字排序重排） |
| 7 | `UpdateChapterMetadataAsync` | `Task<bool>` | 章元数据/类型/编号 patch（`kind`/`customRank`/`number` 语义见 DDL v10 计划） |
| 8 | `CreateChapterWithMetadataAsync` | `Task<ChapterSummary?>` | 带 kind/编号创建（不改既有 `CreateChapterAsync` 签名） |

域：`library`；`Volume` 实体是否引入由 LIB-PREREQ 裁决；本清单不预先改变体语义。

## 4. READ（`FEA-14-READ-1/2`）

| # | 命令 | 返回类型 | 语义 |
|---|---|---|---|
| 9 | `GetReadingPreferencesAsync` | `Task<ReadingPreferencesInfo?>` | 按书阅读偏好读（模式/方向/缩放/双页/布局） |
| 10 | `SaveReadingPreferencesAsync` | `Task<bool>` | 按书阅读偏好写（单写者；旧数据默认回退全局设置） |
| 11 | `ListBookmarksAsync` | `Task<IReadOnlyList<BookmarkInfo>>` | 列出书签（所属内容项+页码+备注） |
| 12 | `CreateBookmarkAsync` | `Task<BookmarkInfo?>` | 新建书签（双页可 left/right/both） |
| 13 | `DeleteBookmarkAsync` | `Task<bool>` | 删书签（不影响漫画/进度/人工修改） |
| 14 | `GetBookReadingProgressAsync` | `Task<BookProgressInfo?>` | 整书总进度（按页面数；与章内进度分列） |
| 15 | `ResetReadingProgressAsync` | `Task<bool>` | 重置进度（需确认；不影响译文/人工修改） |

域：`reader`；跨内容连续序列（READ-2）依赖 LIB 阅读顺序，本清单先不预留序列命令。

## 5. EDIT（`FEA-14-EDIT-1/2/3`）

| # | 命令 | 返回类型 | 语义 |
|---|---|---|---|
| 16 | `ListIssueMarkersAsync` | `Task<IReadOnlyList<IssueMarkerInfo>>` | 列出问题标记（整页/位置；默认待处理，可看已解决） |
| 17 | `CreateIssueMarkerAsync` | `Task<IssueMarkerInfo?>` | 新建标记（含义/可选备注/位置） |
| 18 | `ResolveIssueMarkerAsync` | `Task<bool>` | 标记解决（批量解决由 UI 循环或后续批量命令；本清单先单条） |
| 19 | `ReopenIssueMarkerAsync` | `Task<bool>` | 重新打开 |
| 20 | `DeleteIssueMarkerAsync` | `Task<bool>` | 删除标记（不影响漫画与人工修改） |

域：`editing`；多选动作与受控样式重渲染（EDIT-3）复用既有 Draft 端口，不在此扩。

## 6. AI（`FEA-14-AI-1/2`）

| # | 命令 | 返回类型 | 语义 |
|---|---|---|---|
| 21 | `ListPromptTemplatesAsync` | `Task<IReadOnlyList<PromptTemplateInfo>>` | 列出模板（内置只读 + 自建） |
| 22 | `SavePromptTemplateAsync` | `Task<PromptTemplateInfo?>` | 保存/更新自建模板（内置模板不可覆盖） |
| 23 | `DeletePromptTemplateAsync` | `Task<PromptTemplateDeleteResult>` | 删除（必须带替代 id；未选/仍有引用则不删） |
| 24 | `CopyBuiltinPromptTemplateAsync` | `Task<PromptTemplateInfo?>` | 复制内置模板为可编辑副本 |
| 25 | `GetPromptTemplateReferencesAsync` | `Task<IReadOnlyList<PromptTemplateReference>>` | 删除前列出全部引用 |

域：`ai`；本清单不触发网络/AI 调用。

## 7. 统计与计数

| 接口 | 现有（代码实测） | 本包计划追加 | 实现完成后目标 |
|---|---:|---:|---:|
| `IReaderProgressSink` | 1 | 0 | 1 |
| `IHostController` | 54 | **25** | **79** |
| `IRunController` | 6 | 0 | 6 |
| **合计** | **61** | **25** | **86** |

计划追加明细：FONT 4（§2 编号 1–4）+ LIB 4（§3 编号 5–8）+ READ 7（§4 编号 9–15）+ EDIT 5（§5 编号 16–20）+ AI 5（§6 编号 21–25）= **25 条**。实现完成后以各卡落地时 `generate_api_inventory.py` 实测为准。

## 8. Per-command wire 映射（25 条；R-001 处置）

> **计划值声明（R2-004）**：minor=3、Core wire 名与 payload 键为**计划值**，尚未在真实 Core 协议上验证（NOT_RUN）。实现卡落地时必须用真实 `core_service` 验证并为每个命令回填实测 minor、通道（app/host-control）与 payload 值类型；若与计划不符，须在实现卡内记录差异并更新本表。本清单不被 C-07 pin 覆盖（pin 只覆盖 inventory 文档）。

约定：Host command id 为 Host 侧注册表键（`HostCommandRegistry`）；Core wire 为 Core 命令名；**minor 为计划值 `3`**（当前活跃 2.3 协议；settings 面 7、delete 面 10 的既有约定不适用于本包新增面；实现卡若需 Core 侧新 minor，须按 Core 协议流程并在卡内记录，不得静默改）。payload 为 JSON 键（snake_case）；请求/响应键形状为实现下限，实现卡可加**可选**键但不得改已有键名/语义。

| # | 命令 | Host command id | Core wire | minor | request keys | response keys |
|---|---|---|---|---|---|---|
| P1 | `ListFontAssetsAsync` | `fonts_list` | `ListFontAssets` | 3 | `{}` | `assets[{asset_id,family,subfamily,format,sha256,size_bytes,state}]` |
| P2 | `ImportFontAssetAsync` | `fonts_import` | `ImportFontAsset` | 3 | `source_path,license_note?` | `asset_id,family,subfamily,status` |
| P3 | `DeleteFontAssetAsync` | `fonts_delete` | `DeleteFontAsset` | 3 | `asset_id` | `deleted` |
| P4 | `RefreshFontAssetsAsync` | `fonts_refresh` | `RefreshFontAssets` | 3 | `{}` | `available,failed[{path,code}]` |
| P5 | `UpdateBookMetadataAsync` | `library_update_book` | `UpdateBookMetadata` | 3 | `book_id,patch{title?,author?,series_title?,description?,notes?,tags?}` | `updated` |
| P6 | `ReorderChaptersAsync` | `library_reorder_chapters` | `ReorderChapters` | 3 | `book_id,ordered_ids[]` | `updated` |
| P7 | `UpdateChapterMetadataAsync` | `library_update_chapter` | `UpdateChapterMetadata` | 3 | `chapter_id,patch{kind?,custom_rank?,number?,title?,subtitle?,notes?}` | `updated` |
| P8 | `CreateChapterWithMetadataAsync` | `library_create_chapter_meta` | `CreateChapterWithMetadata` | 3 | `book_id,title,kind?,number?,import_order?` | `chapter_id,title,kind,number` |
| P9 | `GetReadingPreferencesAsync` | `reader_get_prefs` | `GetReadingPreferences` | 3 | `book_id` | `mode,direction,zoom,double_page,layout` |
| P10 | `SaveReadingPreferencesAsync` | `reader_save_prefs` | `SaveReadingPreferences` | 3 | `book_id,prefs{mode?,direction?,zoom?,double_page?,layout?}` | `saved` |
| P11 | `ListBookmarksAsync` | `reader_list_bookmarks` | `ListBookmarks` | 3 | `book_id` | `bookmarks[{bookmark_id,chapter_id,page_id,side,note,created_at}]` |
| P12 | `CreateBookmarkAsync` | `reader_create_bookmark` | `CreateBookmark` | 3 | `book_id,chapter_id,page_id,side?,note?` | `bookmark_id` |
| P13 | `DeleteBookmarkAsync` | `reader_delete_bookmark` | `DeleteBookmark` | 3 | `bookmark_id` | `deleted` |
| P14 | `GetBookReadingProgressAsync` | `reader_book_progress` | `GetBookReadingProgress` | 3 | `book_id` | `read_pages,total_pages,percent,finished` |
| P15 | `ResetReadingProgressAsync` | `reader_reset_progress` | `ResetReadingProgress` | 3 | `book_id,confirm_token?` | `reset` |
| P16 | `ListIssueMarkersAsync` | `editing_list_issues` | `ListIssueMarkers` | 3 | `book_id,state?` | `markers[{marker_id,chapter_id,page_id,position?,kind,note,state,created_at,resolved_at?}]` |
| P17 | `CreateIssueMarkerAsync` | `editing_create_issue` | `CreateIssueMarker` | 3 | `book_id,chapter_id,page_id,position?,kind,note?` | `marker_id` |
| P18 | `ResolveIssueMarkerAsync` | `editing_resolve_issue` | `ResolveIssueMarker` | 3 | `marker_id` | `resolved` |
| P19 | `ReopenIssueMarkerAsync` | `editing_reopen_issue` | `ReopenIssueMarker` | 3 | `marker_id` | `reopened` |
| P20 | `DeleteIssueMarkerAsync` | `editing_delete_issue` | `DeleteIssueMarker` | 3 | `marker_id` | `deleted` |
| P21 | `ListPromptTemplatesAsync` | `ai_list_templates` | `ListPromptTemplates` | 3 | `{}` | `templates[{template_id,name,version,builtin}],builtin_count` |
| P22 | `SavePromptTemplateAsync` | `ai_save_template` | `SavePromptTemplate` | 3 | `template_id?,name,body` | `template_id,version` |
| P23 | `DeletePromptTemplateAsync` | `ai_delete_template` | `DeletePromptTemplate` | 3 | `template_id,replacement_id` | `deleted`（缺替代/仍有引用 → typed 拒绝） |
| P24 | `CopyBuiltinPromptTemplateAsync` | `ai_copy_template` | `CopyBuiltinPromptTemplate` | 3 | `builtin_id,name?` | `template_id` |
| P25 | `GetPromptTemplateReferencesAsync` | `ai_template_refs` | `GetPromptTemplateReferences` | 3 | `template_id` | `references[{kind,owner_id,label}]` |

**payload 纪律**：`source_path` 等 OS 路径不得由 UI 直接拼；Host grant chain 校验后传给 Core（沿用 import/export 既有纪律）。响应键为 UI 投影下限；错误一律 typed code（不静默降级）。

## 9. UNFREEZE 与交付

- UNFREEZE 载体：`doc/reviews/CONTRACT-UNFREEZE-2026-11-10-C07.md`（说明：inventory 文档新增「S5 计划追加」节，代码统计不变，pin 因文档字节变化而重算）。
- inventory 文档只加计划节，不改旧成员/统计；`python tools/generate_api_inventory.py --check` 仍以代码实测 61 为基线。
- 独立上下文复核：本清单 + UNFREEZE + 新 pin 由未参与本卡写作的独立子 agent 复核（r1），记录于 `doc/reviews/FEA-14-S5-PREQ-1-wire-review-r1.md`（或 UNFREEZE 记录末尾）。
- 门禁：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 在重筛 pin 后全绿；无产品代码/DDL diff。
