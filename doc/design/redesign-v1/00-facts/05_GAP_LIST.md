# 05 差异清单（Gap List）

> **文档性质**：L1 只读事实盘点。本文件只记录「文档与代码不一致」和「代码与 UI 不一致」的**事实**，不做设计决策。
>
> 三类定义：
> - **A 类**：文档（`doc/**`）或界面文案声称存在/可用，但代码里没有实现，或实现不足以支撑该声称。
> - **B 类**：代码（应用层或 Core/Tauri 命令面）已实现，但生产 UI 没有出口，用户实际上用不到。
> - **C 类**：只存在于 probe / AC1 / 测试通道的能力；生产 UI 不应依赖，也不应当成产品能力画进设计。
>
> 反向缺口（代码有、UI 文案却说没有）单独归入 A 类并标注「反向」。
>
> 所有条目附 `file:line`。计数见 §4。

---

## 1. A 类：文档声称存在但代码未实现

### A-01 术语表 / 不译表（**最高优先级缺口**）

| 项 | 内容 |
|---|---|
| 文档声称 | 书架负责「翻译约束维护：术语表 / 不译表」，工作台自动术语写入并持续供给翻译（`doc/01_FUNCTIONAL_ARCHITECTURE.md:46`, `62-65`, `75-77`, `114-115`）；`doc/03_DATA_MODEL.md` §12-§13 定义了 `TranslationConstraint` / `ConstraintRevision` 的完整模型 |
| 代码实际 | 只有 **domain 实体 + 合并规则 + 候选规则**：`domain/constraints/entities.py:32-120`（实体/枚举/归一化）、`candidates.py:19-120`（候选）、`merge.py:45-75`（作用域合并）；`application/translation/context/snapshot.py:27-70` + `step.py:107-131` 把它塞进翻译 payload。**没有持久化表**（`infrastructure/sqlite/schema.py` 内 grep `terminology` / `do_not_translate` = 无表；只有 `pipeline_defaults.constraint_snapshot_ref` 与 `pipeline_runs.constraint_snapshot_ref` 两个悬挂字段，`schema.py:297`, `409`），**没有仓储**（`src/ports/repositories/**` 无约束端口），**没有 Core 命令**（`src/bootstrap/core_service.py` 无 `constraint`/`terminology` 分支），**没有 UI**。 |
| 影响 | ① 翻译实际上永远拿不到任何术语约束（`constraint_snapshot_ref` 恒为 `None`，`core_assembly.py:566`, `1270`）；② 新设计若画「术语表编辑器」，等于承诺一个不存在的数据契约；③ `doc/01_FUNCTIONAL_ARCHITECTURE.md:75` 的「自动术语 → 写入约束表 → 供翻译」闭环在代码里断开（`term_extract` 只产出候选，无处落地）。 |
| 相关能力条目 | `01_CAPABILITY_INVENTORY.md` CAP-CONSTRAINT-01~05、CAP-TRANS-07 |

### A-02 翻译记忆（TM）

| 项 | 内容 |
|---|---|
| 文档声称 | `doc/03_DATA_MODEL.md:953-1023`（§14 TranslationMemory：目标/作用域/写入规则/匹配/字段） |
| 代码实际 | 应用层完整实现：`application/translation/knowledge/tm.py:22-294`（`TmScope`/`TmStatus`/`TranslationMemoryEntry`/`record_confirmed_translation`/`find_matches`/`set_disabled`/`record_usage`）。但 **`core_assembly.py` 中没有 `TranslationMemoryService`**（grep = NONE），**无表、无命令、无 UI**。 |
| 影响 | 已确认译文无法复用；新设计不能把 TM 当成设置项或列表来处理。 |

### A-03 约束历史（ConstraintRevision）

| 项 | 内容 |
|---|---|
| 文档声称 | `doc/03_DATA_MODEL.md` §13（`ConstraintRevision` 不可变历史 + `is_pinned`） |
| 代码实际 | 实体在（`domain/constraints/entities.py:72-88`），注释明确「`UNIQUE(constraint_id, revision_no)` is enforced by callers」——**没有表、没有 caller**。 |
| 影响 | 属 A-01 的子项；单列是因为它涉及「历史不可变」这类会被设计误当既有能力的语义。 |

### A-04 自动备份（定时 / 启动时）

| 项 | 内容 |
|---|---|
| 文档/UI 声称 | `doc/03_DATA_MODEL.md` §34.3 的 `backup_type` 含 `automatic`；面板需要说明自动备份策略 |
| 代码实际 | 线上只暴露 `manual`：`core_service.py:1883-1895`（`backup_type != "manual"` → `INVALID_REQUEST`，注释「automatic backups have no scheduler consumer yet」）。`nmbak.py:56` 的枚举确实有 4 类，但只有 `pre_migration`（`migrator.py:86-93`）与 `pre_restore`（`nmbak.py:19-20`）会真正产生。 |
| 影响 | 现有 UI 已如实标注「自动备份未开放」（`BackupSettingsPanel.tsx:391`）——这是**正确做法**，新设计必须保持同等诚实。 |

### A-05 Revision 保留策略 / 按天数自动清理

| 项 | 内容 |
|---|---|
| 文档声称 | `doc/03_DATA_MODEL.md` §17.3（Revision 保留策略）、§45（数据清理策略：可安全清理 / 不自动清理） |
| 代码实际 | **无调度器、无消费点**。现有 UI 明确写「Revision 保留策略与自动清理未开放——当前没有调度器与存储消费点」（`CacheRevisionPanel.tsx:171`）。缓存清理只针对 `cache/` 前缀（`application/maintenance/cleanup.py:41`）。 |
| 影响 | 「清理」在代码里只有「缓存」一档；revision 永远不会被自动淘汰。新设计不要给出「按天保留」的承诺。 |

### A-06 回收站自动清理（按天数）

| 项 | 内容 |
|---|---|
| 文档/UI 声称 | 回收站面板通常需要「自动清理天数」 |
| 代码实际 | 无调度器。现有 UI 如实标注（`RecycleBinSettingsPanel.tsx:309`）。 |
| 影响 | 同上。 |

### A-07 MOBI 导入（**反向**：适配器已写、生产未接线）

| 项 | 内容 |
|---|---|
| 文档声称 | 「补充扩展能力：PDF/MOBI 导入解析」（`doc/01_FUNCTIONAL_ARCHITECTURE.md:166`） |
| 代码实际 | `MobiDocumentRaster` 已完整实现（`infrastructure/importing.py:283-388`，KF7 picture MOBI，DRM/文本文档/KF8 fail-closed），但**生产装配只注入 `PdfiumDocumentRaster()`**：`core_assembly.py:958`（`document_raster = PdfiumDocumentRaster()`），且 `MobiDocumentRaster` 在仓内**仅出现在自身定义处**（grep = 1 处）。`PdfiumDocumentRaster` 明确拒绝 MOBI（`infrastructure/importing.py:173-175`：`MOBI is not a PDFium capability and is deliberately ... UNSUPPORTED_FORMAT`）。 |
| 影响 | ① 用户导入 .mobi 会得到 `UNSUPPORTED_FORMAT`；② 这是「代码看起来有、实际不可用」的典型，设计侧若按「支持 MOBI」画入口会直接错。 |
| 相关能力条目 | CAP-IMP-09 |

### A-08 学习型图像修复路线（Manga LaMa / AOT-GAN / BrushNet·PowerPaint / FLUX Fill）

| 项 | 内容 |
|---|---|
| 文档声称 | 目标多级修复策略表把 4 条学习型路线列为「路线」并给了定位（`doc/01_FUNCTIONAL_ARCHITECTURE.md:236-252`） |
| 代码实际 | 4 条全部注册为 `implements=False`，注释直说「has no implementation in this build」（`infrastructure/providers/runtime.py:666-686`）；路由表明确「two routes are implemented today (Simple Fill, Edge Bleed); the learned routes ... are declared but unimplemented」（`application/translation/inpaint/route_catalog.py:13-19`）。即使依赖装齐也不会变成可运行（`ProviderNotImplemented`，`ports/providers/errors.py:88-96`）。 |
| 影响 | 修复路线选择器**只能诚实显示 2 条可用 + 4 条不可用**；不能把 4 条画成等价可选项。 |
| 相关能力条目 | CAP-INP-05 |

### A-09 文档的 Provider / 引擎矩阵与代码不符

| 项 | 内容 |
|---|---|
| 文档声称 | OCR 8 种引擎 + 混合回退；翻译「历史材料称 15 个」；检测 6 种后端 + aux + 大图切片（`doc/01_FUNCTIONAL_ARCHITECTURE.md:214-232`, `256-259`） |
| 文档自我限定 | 同文件 `212` 行明确：「本仓库未提供下表引用的旧源码路径；它们仅是历史材料中的迁移参考，当前不可核验，也不构成本仓库已实现能力」 |
| 代码实际 | 生产注册表只有 **7 个 provider id**：`openai-vision-detection`、`manga_ocr`、`paddleocr-korean`、`openai-vision-ocr`、`openai-compatible`(翻译)、`local-sakura`(翻译)、`inpaint-simple-fill`、`inpaint-edge-bleed` + 4 条未实现的学习型路线（`infrastructure/providers/runtime.py:73-79`, `544-686`）。检测后端只有 `manga`(默认)/`doctr`/`mock` 三选一（`core_assembly.py:1055-1130`），另有 SFX 并行检测（`core_assembly.py:1014-1030`）。**没有 baidu/caiyun/youdao/jina/cohere/gpt2api/openai 等具名 adapter**（grep `baidu`/`caiyun`/`youdao` in `src/` = 无）。 |
| 影响 | Provider 列表必须按注册表（7 个能力槽）画，不能按文档的 15+ 画。 |

### A-10 历史任务列表 / 任务队列查询

| 项 | 内容 |
|---|---|
| 文档声称 | 工作台必须有任务进度面板，显示「当前任务名称与作用范围」，并能持续跟踪（`doc/01_FUNCTIONAL_ARCHITECTURE.md:73`, `182-206`） |
| 代码实际 | **没有 `ListRuns` / `list_runs` 命令**（`core_service.py` grep = NONE）。`GetTaskProjection` 只接受已知 `run_id`（`core_service.py:3352-3355`）；Run 存在 DB 里（`schema.py:290-311`）但没有读面。现有 UI 明确占位：「暂不可用：Core 尚无 ListRuns 查询；仅能查看本次工作台明确启动的 Run」（`TaskProgressPanel.tsx:106-109`）。 |
| 影响 | **刷新/重开后任务面板即失忆**；而 `recover_running_runs` 恰恰会在启动时制造 `interrupted` Run（CAP-BOOT-04）——用户看得到「有个中断的任务」却没有任何入口去处理它。这是新设计必须先解决的能力前置条件。 |

### A-11 页面拖拽排序

| 项 | 内容 |
|---|---|
| 文档声称 | `doc/03_DATA_MODEL.md` §5.3（`sort_order` 是用户当前排序）、§44（页面列表批处理与右键菜单） |
| 代码实际 | `Page.reorder()` 存在（`domain/pages/entities.py:46-49`），但**全仓无调用方**（grep `.reorder(` 只有 `application/library/service.py:194` 的 `chapter.reorder`）；**没有 `LibraryService.reorder_pages`**，没有仓储方法，没有命令。章节排序有应用层实现（`library/service.py:185-202`）但无命令。 |
| 影响 | 现有 UI 已占位 `gap-g14-page-order`（`PageListPanel.tsx:127`）。页面顺序当前**只由导入时的 `source_order`/`sort_order` 决定**，用户无法改。 |
| 相关能力条目 | CAP-LIB-16 |

### A-12 导入逐页进度

| 项 | 内容 |
|---|---|
| 代码实际 | `ImportPages` 是**同步**返回最终结果（`core_service.py:2651-2656`），无 snapshot/事件。UI 占位 `gap-g26-import-progress`（`WorkbenchToolbar.tsx:84`）。 |
| 影响 | 大批量导入时没有任何进度反馈；设计不能假设有 `import_id`/进度事件。 |

### A-13 低清缩略图通道

| 项 | 内容 |
|---|---|
| 代码实际 | 只有原图/译图资源通道（`core_service.py:2364-2494`）；`artifact_type` 枚举里有 `thumbnail`（`schema.py:70`）但**无生产写入/读取路径**。UI 占位 `gap-g18-page-thumbnails`（`PageListPanel.tsx:128`）、`gap-g18-current-page-thumbnail`（`TaskProgressPanel.tsx:113`）。 |
| 影响 | 任何「缩略图网格/当前页小图」在实现上都是「加载原图」，会直接消耗 256 MiB/16 MiB/32 引用上限（见 `02_DATA_MODEL_AND_STATES.md` §18）。 |

### A-14（反向）插件系统「尚未实现」的 UI 文案与代码不一致

| 项 | 内容 |
|---|---|
| UI 声称 | 设置页分类 `plugins` 的未开放原因写作「插件系统尚未实现」，并给出「设计已冻结…实现后将在此管理已安装插件与权限」的整段说明（`SettingsPage.tsx:85-89`；nav 徽标逻辑 `SettingsPage.tsx:177-190`） |
| 代码实际 | 插件运行时**已实现并接线**：Core 4 条命令（`core_service.py:279-284`, `4033-4086`），Tauri 5 条命令（`main.rs:751-845`，含 `plugins_open_directory`），前端 `PluginSettingsPanel.tsx` 已调用 5 条（`settings/client.ts:137-141`），DB 两张表（`schema.py:563-593`），6 个 hook + 沙箱子进程（`infrastructure/plugins/service.py`）。 |
| 影响 | 真实能力被自己的文案掩盖。设计侧必须先修正「插件到底有没有」这个前提，否则会在错误基线上做信息架构。 |

---

## 2. B 类：代码已实现但 UI 无出口

> 判定口径：能力在 **application 层 / infrastructure 层**已实现（或有明确调用方），但**没有 Core 命令**、或**有 Core/Tauri 命令但前端零调用**，因此生产用户无法使用。
> 「影响」列只描述能力损失，不含设计方案。

### B-01 书架的整套「改」能力（`LibraryService`）

| 项 | 内容 |
|---|---|
| 代码已实现 | `application/library/service.py`：`update_book`(`:91-96`)、`set_favorite`(`:102-107`)、`set_archived`(`:108-117`)、`update_chapter`(`:174-179`)、`delete_chapter`(`:180-184`)、`reorder_chapters`(`:185-202`)、`create_tag`/`rename_tag`/`delete_tag`/`list_tags`/`add_tag_to_book`/`remove_tag_from_book`/`tags_of_book`(`:203-241`) |
| UI 无出口 | `core_service.py` 无任何对应分支（grep `update_book`/`update_chapter`/`reorder`/`tag` = NONE）；Tauri 无对应命令（`main.rs:1857-1920` 与 `settings_bridge.rs:917-1171` 均无）；前端只有占位：`BookCard.tsx:49`, `61`（收藏「等待能力接入 GAP-G3」）、`BookshelfToolbar.tsx:163-204`（筛选能点但无法改变收藏/归档状态） |
| 影响 | 书架当前只有「建 / 列 / 删」；作品元信息、收藏、归档、章节编辑与排序、标签**全部不可用**。`BookSummary` 里回传的 `is_favorite`/`is_archived` 是**只读**的。 |
| 相关能力条目 | CAP-LIB-10~15、CAP-LIB-18 |

### B-02 区域编辑的整套写入面（**产品核心承诺，缺口最大**）

| 项 | 内容 |
|---|---|
| 代码已实现 | `application/editing/service.py`：`create_region`(`:262-290`，detect 步骤内部在用，`core_assembly.py:1196`)、`delete_region`(`:298-306`)、`save_geometry`(`:468-490`)、`merge_regions`(`:491-547`)、`split_region`(`:548-588`)、`reorder_regions`(`:589-609`)、`save_manual_translation`(`:697-706`)、`confirm_final`(`:707-725`)、`restore_revision_with_number`(`:734-785`，已上线)、`set_revision_pinned`(`:786-791`) |
| 线上命令面只有 5 条 | `set_region_type` / `list_regions` / `list_region_revisions` / `restore_region_revision` / `rerender_page`（`core_service.py:4164-4334`） |
| UI 无出口 | 6 处显式占位：`WorkbenchToolbar.tsx:80`（新建 Region）、`:81`（删除 Region）、`:82`（编辑几何/合并/拆分/顺序）、`RegionInspector.tsx:135`（保存人工译文，文本框 `disabled` 且 placeholder「等待译文保存能力接入」）、`:136`（区域锁定）、`:137`（固定修订） |
| 影响 | 「人工校对」是产品主承诺（`doc/01_FUNCTIONAL_ARCHITECTURE.md:72`, `177`），但当前新 UI **不能改任何文本、不能画框、不能锁、不能 pin**。另注：legacy QML 工作台曾通过 duck-typed port 调用 `save_manual_translation` 与 `create_region`（`src/ui/viewmodels/viewmodel.py:86-87`, `634`, `706`）——即这是**新架构的能力回退**，不是从来没做过。 |
| 相关能力条目 | CAP-REGION-06~15、CAP-INP-07、CAP-PAGE-08 |

### B-03 页面级回收站（TrashService 批次）

| 项 | 内容 |
|---|---|
| 代码已实现 | `application/maintenance/trash.py`：`soft_delete_pages`(`:119-166`)、`list_batches`(`:167-187`)、`restore_batch`(`:188-195`)、`purge_batch`(`:196-227`)、`retry_pending_purges`(`:228-255`)、`pending_purge_count`(`:256-262`)；已装配进 Core（`core_assembly.py:964-970`） |
| UI 无出口 | `core_service.py` grep `trash` = 仅注释；无命令、无前端 |
| 影响 | 书籍级回收站可用（CAP-LIB-08/06），但**页面级误删不可恢复**且不可见。 |

### B-04 诊断包导出

| 项 | 内容 |
|---|---|
| 代码已实现 | `application/maintenance/diagnostics.py:251-260`（`DiagnosticsService.export`）+ 脱敏（`_SENSITIVE_KEY`/`_BEARER`/`_OPENAI_STYLE`，`:32-50`）+ 有界错误日志（`:202-224`）；已装配（`core_assembly.py:674`, `1301-1316`） |
| UI 无出口 | `core_service.py` grep `diagnostic` = NONE；无 Tauri 命令 |
| 影响 | 用户遇到问题无法自助产出可提交的诊断包；`doc/03_DATA_MODEL.md` §34.5 的 Diagnostic Settings 无落点。 |

### B-05 `settings_resolve_overrides`（设置来源可见性）

| 项 | 内容 |
|---|---|
| 代码已实现 | Core handler `src/bootstrap/settings_commands.py:724`；Tauri 命令 `settings_bridge.rs:1161`；生产注册 `main.rs:1892` |
| UI 无出口 | 前端 `settings/client.ts` 未声明该命令（grep `settings_resolve_overrides` 全前端 = NONE） |
| 影响 | `AC-SET-001`「每个生效值要能显示来源（task/chapter/book/global）」在界面上无法呈现（`application/settings/models.py:46-60` 的 `source_label` 无处可用）。 |

### B-06 `settings_provider_run_snapshot_get`（Run 的 Provider 快照）

| 项 | 内容 |
|---|---|
| 代码已实现 | Core handler `settings_commands.py:710-723`；Tauri 命令 `settings_bridge.rs:1029-1039`；生产注册 `main.rs:1883` |
| UI 无出口 | 前端 grep = NONE |
| 影响 | 「这次 Run 到底用了哪个 Provider/模型」无法回答——直接削弱 `Run 快照可复现` 这个被 `schema.py:294-298` 冻结的设计承诺。 |

### B-07 `revoke_resource_refs`（批量撤销资源引用）

| 项 | 内容 |
|---|---|
| 代码已实现 | Tauri `main.rs:1390-1401` |
| UI 无出口 | 前端 grep = NONE（只有单条 `revoke_ref`，`resourceChannel/client.ts:69`） |
| 影响 | 关闭多图视图时只能靠 300s TTL 自然过期；期间占用「活跃引用 ≤32 / 单资源订阅 ≤16」配额（`application/resource_channel/dto.py:22`, `26`），大批量翻页可能撞限流。 |

### B-08 Provider 就绪状态 / 模型安装状态

| 项 | 内容 |
|---|---|
| 代码已实现 | `ProviderRegistry.status(provider_id)` / `statuses()` / `readiness_report()`（`infrastructure/providers/registry.py:178-260`）；`ProviderStatus` 含 state/detail；`ModelManager`/`ModelSpec`（`infrastructure/providers/models.py`）；依赖探针 `Requirement`（`infrastructure/providers/dependencies.py`） |
| UI 无出口 | 没有对应 Core 命令（`settings_provider_profiles_list` 只回配置，不回 readiness——`settings_commands.py:114`, `139-145`） |
| 影响 | 设置页能列出 Provider 却**说不清它为什么不能用**；用户只能等到跑任务时看 `PROVIDER_NOT_CONFIGURED`/`PROVIDER_DEPENDENCY_MISSING`（`ports/providers/errors.py:59-96`）。 |

### B-09 产物 revision 的读/写面（含 pin）

| 项 | 内容 |
|---|---|
| 代码已实现 | `media_artifacts` / `artifact_revisions` 完整表结构 + `current_revision_id` 不可清空约束（`schema.py:64-106`, `136-146`）；`is_pinned`、`integrity_status`、溯源字段齐备 |
| UI 无出口 | 无任何 Core 命令读/写 artifact revision（仅 `rerender_page` 会新建 translated revision 并在结果里回 `revision_no`，`core_service.py:2300-2311`） |
| 影响 | 「这页当前用的是哪一版译图」「这版是不是 pin 住不许清」在界面上不可见不可操作。 |

### B-10 页面级 `review_state` / `overall_status`（列在，但既不推进也不读出）

| 项 | 内容 |
|---|---|
| 代码已实现（存储层） | `pages.review_state`（3 值 CHECK）与 `pages.overall_status`（9 值 CHECK）（`schema.py:199-205`）；domain 字段（`domain/pages/entities.py:30-31`）；仓储读写（`infrastructure/sqlite/library.py:99`, `295`, `349`, `387-394`） |
| 事实：没有推进代码 | `src/**` 内**没有任何** `.overall_status =` / `.review_state =` 赋值（grep = NONE）——两列除默认值 `not_started`/`unreviewed` 外不会变化 |
| UI 无出口 | `list_chapter_pages` 的导航摘要行不含这两字段（`core_service.py:2339-2363` docstring：「Navigation summary rows only」）；任务投影的页状态由 Task 现算（`projection.py:327-345`），不读这两列 |
| 影响 | 「这页校对到哪一步」在数据层是**空语义**：既不是读面缺，而是生产上根本没有值。新设计若把它当既有状态模型会直接错。 |

### B-11 导入取消入口

| 项 | 内容 |
|---|---|
| 代码已实现 | Core 侧取消回调 `self._import_cancelled`（`core_service.py:956`, `976`, `2623`, `2672`, `2679`），取消后未处理文件标 `outcome:"pending"` 并回 `cancelled:true`（`core_service.py:2618-2640`, `2651-2656`） |
| UI 无出口 | Tauri `library_import_file` / `library_import_folder` 无 cancel 参数（`main.rs:1189-1240`）；前端无取消 UI |
| 影响 | 大批量导入无法中止；用户只能等它跑完。 |

### B-12 按原设置「再导一次」

| 项 | 内容 |
|---|---|
| 代码已实现 | `ExportService.repeat(export_id, ...)`：从历史 scope 快照重建请求（`application/export/service.py:398-437`） |
| UI 无出口 | 无命令；前端 `workbench/client.ts` 只有 start/cancel/snapshot/history/reveal |
| 影响 | 导出历史只能看，不能复用配置。 |

### B-13 区域级重渲染

| 项 | 内容 |
|---|---|
| 代码已实现 | `RenderService.rerender_region(...)`（`application/rendering/service.py:292-422`） |
| UI 无出口 | 线上只有页级 `rerender_page`（`core_service.py:2136-2312`） |
| 影响 | 改一个区域也要整页重渲；对长条 Webtoon 页代价显著。 |

---

## 3. C 类：仅 probe / AC1 测试通道，生产 UI 不应依赖

> 判定依据：命令只在特定启动模式注册，或源码注释自述为验证/工具面。

| ID | 通道 | 证据 | 为什么不能当产品能力 |
|---|---|---|---|
| C-01 | `core.detect` | `core_service.py:21-37`（docstring：「Verification/tooling surface only -- the product UI detect path remains the pipeline」）, `3833-3927` | 它是**探针面**；产品检测走 Run 的 `detect` step。用它做 UI 会绕过 Run/Revision/冲突保护 |
| C-02 | probe 模式命令：`probe_config`、`probe_write_results`、`probe_exit`、`probe_issue_url` | 只在这个分支注册：`main.rs:1821-1834`；命令定义 `main.rs:1406-1455` | 生产构建里**物理不存在**（`main.rs:1811-1813` 注释） |
| C-03 | ac1 模式命令：`ac1_request`、`ac1_write_results`、`ac1_exit` | 只在这个分支注册：`main.rs:1835-1847`；定义 `main.rs:1456-1487`；前端驱动 `frontend/src/ac1/driver.ts:94`, `140-175` | 验收脚本专用；`acceptance_bridge.py` 还直接调 `state.core.editing.create_region`（`src/bootstrap/acceptance_bridge.py:311`）——**绕过了 Core 命令面**，不能作为能力存在的证据 |
| C-04 | `register_catalog` | `main.rs:1811-1813`（「exists in no mode」）；`App.tsx:129`, `366-371` 故意调用以验证被拒（场景 `D-01-register-catalog-denied`） | 任何模式都不注册；前端调用它只为断言"被拒绝" |
| C-05 | `App.tsx` 的 probe / ac1 runner 视图 | `App.tsx:75-90`（`appMode` = detecting/probe/ac1/production）、`App.tsx:332-420`（E-08/E-09/D-01/D-02/D-03 场景） | 这是**测试驱动界面**，不是产品界面；`view=console` 参数（`App.tsx:433-435`）只有测试用 |
| C-06 | `FpsRecorderPanel`（性能记录面板） | `frontend/src/perf/FpsRecorderPanel.tsx`；`perf/fpsRecorder.ts`（15.7 KB） | 性能测量工具，非用户能力 |
| C-07 | `devMockBridge` | `frontend/src/dev/devMockBridge.ts` | 开发桩；不带真实 Core |
| C-08 | `sfx_detect_probe` 独立入口 | `src/bootstrap/sfx_detect_probe.py:1-10`（「One-shot, non-interactive, NOT part of the frozen stdio command surface」） | 打包内独立 exe，命令面**零扩展**（同一 docstring 自述） |
| C-09 | `acceptance_bridge.py`（AC1 后端） | `src/bootstrap/acceptance_bridge.py`（26.6 KB）；`core_service.py` 的 AC1 注释（`3735-3738`：`AC1 (R-007)`） | 验收通道；可直接触达服务层，不代表生产可达性 |
| C-10 | `verification/**` 与 `tests/**` 脚本 | `verification/`（多任务 verify.ps1）、`tests/`（pytest 基线） | 测试绿不代表生产路径可达（`doc/10_CURRENT_STATE_AND_GAPS.md:177` 明确记录过这一教训） |

**额外警告（C 类衍生）**：`core.detect` 与 `acceptance_bridge` 都能在测试里把能力"跑通"，从而让人误判某项能力已可用。判断生产可达性的唯一口径是：**命令是否在生产 `generate_handler!` / Core 分发表里 + 前端是否有真实调用点**（`01_CAPABILITY_INVENTORY.md` §0.3-§0.4）。

---

## 4. 计数与优先序（事实层，不含设计决策）

| 类别 | 条数 | 说明 |
|---|---|---|
| A 类（文档声称 / 代码未实现） | **14** | A-01~A-13 + A-14（反向：代码有、文案说没有） |
| B 类（代码已实现 / UI 无出口） | **13** | B-01~B-13 |
| C 类（仅 probe/AC1/测试） | **10** | C-01~C-10 |
| 合计 | **37** | — |

### 4.1 按「对产品承诺的伤害」排序（纯事实判断，非设计建议）

| 排名 | 条目 | 为什么伤害大 |
|---|---|---|
| 1 | B-02 区域写面 | 产品核心承诺「人工校对」在生产 UI 上完全不可用；且这是相对 legacy QML 的能力回退 |
| 2 | A-01 术语表/不译表 | 文档把「翻译约束」写成产品主流程的一环（自动术语→约束→翻译），代码里整条链路断开 |
| 3 | A-10 历史任务列表 | `recover_running_runs` 会制造 `interrupted` Run，但没有读面 → 用户看得到「有中断任务」却无处处理 |
| 4 | B-01 书架写面 | 书架只能增删不能改；收藏/归档回传了状态却无法改变 |
| 5 | A-14 插件文案与实现不一致 | 信息架构建立在错误前提上（"插件没有" vs "插件有 8 条能力"） |
| 6 | B-05 / B-06 设置来源与 Run 快照 | 直接削弱「设置分层可解释」与「Run 可复现」两个已冻结的设计承诺 |
| 7 | A-07 / A-08 / A-09 | 会诱导设计画出不存在的能力（MOBI、4 条修复路线、15 个 Provider） |

### 4.2 每条条目的「新设计必须先确认」的开放问题（供 Lead 裁决，不是建议）

1. A-01/A-02/A-03：术语表/TM 是「本轮不做（界面上明确无此能力）」还是「先补存储+命令再做界面」？
2. B-02：区域写面是「补 Core 命令再设计界面」还是「本轮界面必须显式标注不可用」？
3. A-10：历史任务列表是新 UI 的硬前置吗（否则任务面板在重开后无意义）？
4. A-14：插件分区的定位需要按「已实现」重写，还是按「暂不暴露」继续隐藏？
5. A-04/A-05/A-06：三处「自动策略未开放」需要统一口径（现有三处 UI 文案各自为政）。
6. A-09：Provider 能力矩阵以注册表 7 槽为准还是以文档 15+ 为准？

---

## 5. 本次盘点的边界

- 只读源码与文档，未修改任何生产文件。
- 未运行构建与测试；本文件不声称任何通过/失败。
- 未审计 `src/ui/**`（Legacy PySide6/QML）作为设计依据；仅在两处把它作为「能力曾经存在」的旁证（B-02、A-14 相关）。
- `doc/**` 的声称以 `doc/01_FUNCTIONAL_ARCHITECTURE.md`、`doc/03_DATA_MODEL.md`、`doc/10_CURRENT_STATE_AND_GAPS.md` 为主；其余文档未逐条比对。
- 无法确认的项已在文中标 `UNVERIFIED` 并说明查了哪里。
