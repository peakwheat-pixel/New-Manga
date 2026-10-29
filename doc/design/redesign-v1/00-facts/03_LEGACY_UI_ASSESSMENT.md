# 03 旧前端现状盘点：界面清单 / 覆盖缺口 / 缺陷识别（LEGACY，仅作问题输入）

> **文档性质**：只读盘点结论（AS-IS 事实 + 问题识别）。**不是设计依据**，也不提供任何设计提案。
> 旧 UI 的布局、导航结构、配色、组件、交互流程在新设计里**一律不得沿用**；本文的价值只在于回答三件事：
> ① 旧前端到底覆盖了哪些业务能力；② 旧界面到底坏在哪（"要解决什么"）；③ 哪些交互假设必须被替换。
>
> **证据基准**：`G:\CODEX\New Manga`，branch `main`，HEAD `65d9efa191c6867243bf67aced54fd89308838b7`（2026-10-25 00:59:28 +0800）。
> 所有 `file:line` 均相对仓库根目录，行号取自该 commit 的工作区文件（工作区有他人未提交改动：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/TASK_LEDGER.md` 及 `audit/`、`doc/tasks/*` 未跟踪文件，本文未触碰）。
>
> **核对口径**：
> - 后端能力面以 `apps/desktop/src-tauri/src/main.rs` 的 `PRODUCTION_COMMANDS`（66 条，`main.rs:70-165`）为准；WebView 可见面另有 probe 4 条（`main.rs:170-175`）、AC1 3 条（`main.rs:186`），ACL 合计 73 条（`apps/desktop/src-tauri/capabilities/m2rc1-commands.json:4` 自述 + `:8-90` 逐条列出）。
> - 历史 UI/流程文档（`doc/05_UI_MAPPING.md`、`doc/04_USER_FLOW.md`）**标注为 LEGACY**，仅用于"曾经承诺过什么能力"的功能面核对，不视为当前实现事实。
> - 能力 ID 为本文自建的临时命名空间（见 §A.0），用于把"界面"与"能力"对齐；**最终编号需与 `01_CAPABILITY_INVENTORY.md` 对齐**（本文写作时该文件尚未产出）。
> - 无法确认的一律写 `UNVERIFIED`，不做推测。

---

## 统计摘要

| 指标 | 数值 |
|---|---|
| 产品界面表面（一级页面 / 固定面板 / 工具栏 / 对话框 / 遮罩） | 45（§A.1–A.5） |
| 非产品表面（遗留 Console / 探测视图 / FPS / dev mock / AC1） | 5（§A.6） |
| 后端生产命令（Tauri `PRODUCTION_COMMANDS`） | 66 |
| 有产品 UI 出口的命令 | 62 |
| 完全无前端引用（连 `client.ts` 里都没有） | 3（`revoke_resource_refs`、`settings_provider_run_snapshot_get`、`settings_resolve_overrides`） |
| 只有 probe/测试出口、无产品出口 | 1（`revoke_ref`） |
| 仅以 DisabledFeature / 禁用控件/"未开放"文案存在的缺口占位 | 12 处 `DisabledFeature` + 4 处手写禁用块 |
| **缺陷条目** | **67**（**P0 21 / P1 34 / P2 12**） |
| 前端源码规模 | 126 文件 / 31,704 行（其中测试 45 文件 / 11,791 行；非测试 81 文件 / 19,913 行） |

---

# A. 现有界面清单

## A.0 入口判定与能力 ID 命名空间

**产品真正渲染的产品界面只有 `AppShell` 一条路径。** `App.tsx` 是一个"测试运行器 + 产品宿主"的混合体：

- `apps/desktop/frontend/src/App.tsx:154-421`：启动即按顺序探测 `ac1_request` → `probe_config`，命中则进入 AC1/probe 证据模式；都被拒（= 生产模式）才走 `runInteractiveDenyMatrix` 并 `setAppMode("production")`（`App.tsx:113-152`）。
- `App.tsx:433-455`：`appMode === "detecting"` 时渲染一行 `M2-RC2 resource channel runtime` 文本 + 探测日志。
- `App.tsx:459-525`：`appMode` 为 `probe`/`ac1`，**或 URL 带 `?view=console`** 时渲染遗留 Console（含 `Console`/`Workbench` 两个 nav 按钮、`LibraryPanel`、`SettingsPanel`）。注意：生产模式下只要 URL 带 `?view=console` 也会进这一支（判断在 `App.tsx:459`，早于 `App.tsx:528` 的 `AppShell` 返回）。
- `App.tsx:527-528`：`return <AppShell invoke={safeInvoke} />`——**唯一产品入口**。

**能力 ID 命名空间（临时）**

| 前缀 | 覆盖面 |
|---|---|
| `CAP-BOOT-*` | 启动、Core 生命周期/健康 |
| `CAP-LIB-*` | 作品(Book)、章节(Chapter) 的读/建/收藏/归档/删除 |
| `CAP-IMP-*` | 页面导入（文件/文件夹/重复策略/导入报告） |
| `CAP-PAGE-*` | 页面列表、页序、页状态、页面锁 |
| `CAP-READ-*` | 阅读投影、阅读进度、阅读模式/方向 |
| `CAP-RUN-*` | 任务队列 Run：启动/暂停/停止/继续/重启/放弃/重试失败/解除阻塞 |
| `CAP-REG-*` | Region 读、改类型(retype)、几何、新建/删除、锁 |
| `CAP-REV-*` | Region 修订历史、恢复、pin |
| `CAP-SFX-*` | 拟声词策略（全局设置 + region 快照 + 疑似标记） |
| `CAP-EXP-*` | 导出（格式/进度/历史/打开文件夹） |
| `CAP-SET-*` | 设置分区（ocr/translate/inpaint/typeset/model_gpu/tasks/sfx…） |
| `CAP-PRV-*` | Provider Profile、能力绑定、凭据、网络代理 |
| `CAP-PLG-*` | 插件运行时 |
| `CAP-BAK-*` / `CAP-CLN-*` | 备份 .nmbak / 缓存与 revision 清理 |
| `CAP-RB-*` | 回收站 |
| `CAP-GL-*` / `CAP-TM-*` / `CAP-TAG-*` | 术语表/翻译约束、翻译记忆、标签 |
| `CAP-DEV-*` | 非产品表面（probe/console/AC1/dev mock/FPS） |

## A.1 一级页面（4 个，常驻内存）

| # | 界面 | 文件:行 | 承载能力 | 用户可见入口路径 |
|---|---|---|---|---|
| 1 | 应用外壳 / 左侧 64px 图标导航栏 | `shell/AppShell.tsx:146-440`（rail `:162-314`） | `CAP-LIB-*`,`CAP-RUN-*`,`CAP-READ-*`,`CAP-SET-*`（页面容器） | 应用启动默认页 |
| 2 | 书架页 BookshelfPage | `bookshelf/BookshelfPage.tsx:203-448` | `CAP-LIB-BOOK-LIST`,`CAP-LIB-CHAPTER-LIST`,`CAP-IMP-*`,`CAP-LIB-FAV`,`CAP-LIB-ARCH`,`CAP-RB-*`,`CAP-READ-*`,`CAP-RUN-*`（跳转） | rail「书架」/ `Ctrl+1`（`AppShell.tsx:113-115`）/ 启动默认 |
| 3 | 工作台页 WorkbenchPage | `workbench/WorkbenchPage.tsx:1179-1357` | `CAP-RUN-*`,`CAP-REG-*`,`CAP-REV-*`,`CAP-SFX-*`,`CAP-PAGE-*`,`CAP-EXP-*`,`CAP-IMP-*` | rail「工作台」/ `Ctrl+2` / 书架章节行「翻译」按钮（`ChapterList.tsx:148-165` → `AppShell.tsx:132-135`） |
| 4 | 阅读器页 ReaderPage | `reader/ReaderPage.tsx:343-497` | `CAP-READ-*`（投影/进度/模式） | rail「阅读器」/ `Ctrl+3` / 书架章节行「阅读」（`ChapterList.tsx:166-182`） |
| 5 | 设置页 SettingsPage | `settings/SettingsPage.tsx:113-333` | `CAP-SET-*`,`CAP-PRV-*`,`CAP-PLG-*`,`CAP-BAK-*`,`CAP-CLN-*`,`CAP-RB-*` | rail「设置」/ `Ctrl+4` |

四个页面容器**始终挂载**，仅用 `display: none` 切换（`AppShell.tsx:376-436`）；`AppShell.test.tsx:64-70` 把"keep-alive 不卸载"写成了硬断言。

## A.2 书架子界面

| # | 界面 | 文件:行 | 承载能力 | 入口路径 |
|---|---|---|---|---|
| 6 | 书架上工具栏（新建/导入/回收站/搜索/收藏筛选/归档筛选/排序/网格列表切换） | `bookshelf/BookshelfToolbar.tsx:34-277` | `CAP-LIB-CREATE`,`CAP-IMP-*`,`CAP-RB-*`,`CAP-LIB-FILTER`,`CAP-LIB-SORT` | 书架顶部 |
| 7 | 书卡（网格） | `bookshelf/BookCard.tsx:10-154`；容器 `BookGrid.tsx:11-33` | `CAP-LIB-BOOK-LIST`（收藏/归档只读徽标） | 书架主区 |
| 8 | 书行（列表） | `bookshelf/BookList.tsx:10-133` | 同上 | 书架主区（列表视图） |
| 9 | 作品详情面板（固定 320px：元信息/阅读摘要占位/导入/删除(禁用)/标签(禁用)/翻译约束(禁用)/章节列表） | `bookshelf/BookDetailPanel.tsx:16-300` | `CAP-LIB-BOOK-DETAIL`,`CAP-IMP-*`,`CAP-LIB-DELETE`(禁用),`CAP-TAG-*`(禁用),`CAP-GL-*`(禁用),`CAP-LIB-CHAPTER-LIST` | 书架右侧常驻 |
| 10 | 章节列表 + 行内动作（导入/翻译/阅读） | `bookshelf/ChapterList.tsx:14-189` | `CAP-LIB-CHAPTER-LIST`,`CAP-IMP-*`,`CAP-RUN-*`(跳转),`CAP-READ-*`(跳转) | 详情面板内 |
| 11 | 空态（空书架 / 筛选无结果） | `bookshelf/EmptyStateBookshelf.tsx:10-132` | `CAP-IMP-*`,`CAP-LIB-CREATE` | 书架主区 |
| 12 | 新建作品/新建章节对话框 | `bookshelf/CreateTitleDialog.tsx:29-157` | `CAP-LIB-CREATE`,`CAP-LIB-CHAPTER-CREATE` | 工具栏「+ 新建作品」/ 详情面板「+ 新建章节」 |
| 13 | 导入页面对话框（目标作品/章节选择、重复策略、文件/文件夹选择器、忙碌态、错误、聚合导入报告） | `bookshelf/ImportDialog.tsx:19-594` | `CAP-IMP-FILE`,`CAP-IMP-FOLDER`,`CAP-IMP-DUP-POLICY`,`CAP-IMP-REPORT` | 工具栏「导入作品」/ 详情面板「导入页面」/ 章节行「导入」/ 工作台工具栏「导入页面」 |
| 14 | 回收站（以模态遮罩嵌入书架） | `bookshelf/BookshelfPage.tsx:405-445` → `recycleBin/RecycleBinPage.tsx:45-507` | `CAP-RB-LIST`,`CAP-RB-PERM-DELETE` | 工具栏「🗑️ 回收站」 |
| 15 | 永久删除二次确认对话框（目标作品清单 + "我理解不可恢复" 勾选 + 确认按钮） | `recycleBin/PermanentDeleteConfirmDialog.tsx:11-289`（遮罩 `:41-55`，勾选 `:195-219`，`zIndex:2000` 见 `:53`） | `CAP-RB-PERM-DELETE` | 回收站「永久删除」 |

## A.3 工作台子界面（五区）

区域声明见 `workbench/WorkbenchPage.tsx:1-19`，实际渲染 `:1211-1281`。

| # | 界面 | 文件:行 | 承载能力 | 入口路径 |
|---|---|---|---|---|
| 16 | 工作台工具栏（上下文串、Region 计数、19 项批处理命令下拉 + 「启动」、导入、导出选择页、查看模式、5 个禁用功能） | `workbench/WorkbenchToolbar.tsx:41-87` | `CAP-RUN-START`(19 命令族),`CAP-IMP-*`,`CAP-EXP-*`,`CAP-PAGE-LOCK`(禁用),`CAP-REG-CREATE`(禁用),`CAP-REG-GEOMETRY`(禁用),`CAP-RUN-DISCOVERY`(禁用),`CAP-IMP-PROGRESS`(禁用) | 工作台底部栏 |
| 17 | 页面列表面板（书→章→页三级下钻 + "按页面 ID 定位"输入 + 状态筛选 + 2 个禁用功能） | `workbench/PageListPanel.tsx:69-253` | `CAP-LIB-BOOK-LIST`,`CAP-LIB-CHAPTER-LIST`,`CAP-PAGE-LIST`,`CAP-PAGE-SELECT`(多选),`CAP-RUN-STATUS-FILTER`,`CAP-PAGE-ORDER`(禁用),`CAP-PAGE-THUMB`(禁用) | 工作台左列 |
| 18 | 页面查看器（缩放/平移/适配、页图、"本页暂无 Region"、Region 覆盖层、右键改标菜单、E4 反馈条含撤销/重渲染） | `workbench/ViewerPanel.tsx:64-353` | `CAP-PAGE-IMAGE`,`CAP-REG-SELECT`,`CAP-REG-RETYPE`,`CAP-SFX-SUSPECT`,`CAP-REV-UNDO`(10s),`CAP-REG-RERENDER-PAGE` | 工作台中央 |
| 19 | Region 覆盖层（SVG 框 + 多边形环 + 类型/警告 pill；可点、可右键、可 Tab） | `region/RegionOverlay.tsx:79-237` | `CAP-REG-SELECT`,`CAP-REG-RETYPE`(入口),`CAP-SFX-SUSPECT`(显示) | 查看器内部 |
| 20 | 右键改标菜单（标记 sfx / 改回 speech / 标记疑似拟声词） | `workbench/RelabelContextMenu.tsx:37-133` | `CAP-REG-RETYPE`,`CAP-SFX-SUSPECT` | 查看器内 Region 上右键 |
| 21 | 改回对白确认对话框 | `workbench/RelabelConfirmDialog.tsx:32-128` | `CAP-REG-RETYPE`（反向、破坏性） | 右键菜单 / Inspector 按钮 |
| 22 | Region Inspector（原始字段 dl、策略说明整段、禁用的人工译文 textarea、3 个禁用功能、改标按钮、疑似标记、修订历史列表、恢复确认对话框） | `workbench/RegionInspector.tsx:54-323` | `CAP-REG-DETAIL`,`CAP-REG-RETYPE`,`CAP-SFX-SUSPECT`,`CAP-REV-HISTORY`,`CAP-REV-RESTORE`,`CAP-TR-MANUAL-SAVE`(禁用),`CAP-REG-LOCK`(禁用),`CAP-REV-PIN`(禁用) | 工作台右列 |
| 23 | 任务进度面板（折叠/展开、7 个运行控制、状态计数筛选、步骤流、任务详情 `<details>` 弹层、1 个禁用功能） | `workbench/TaskProgressPanel.tsx:28-163` | `CAP-RUN-SNAPSHOT`,`CAP-RUN-PROJECTION`,`CAP-RUN-PAUSE/STOP/CONTINUE/RESTART/ABANDON`,`CAP-RUN-RESUME-BLOCKED`,`CAP-RUN-RETRY-FAILED`,`CAP-RUN-LOCATE-PAGE`,`CAP-RUN-DISCOVERY`(禁用),`CAP-PAGE-THUMB`(禁用) | 工作台底部固定区 |
| 24 | 导出对话框（格式/选项/过期策略/当前进度/导出历史/打开文件夹/取消） | `workbench/ExportDialog.tsx:25-114` | `CAP-EXP-FORMAT`,`CAP-EXP-STALE-POLICY`,`CAP-EXP-SNAPSHOT`,`CAP-EXP-HISTORY`,`CAP-EXP-REVEAL`,`CAP-EXP-CANCEL` | 工具栏「导出选择页」 |
| 25 | 工作台错误条 | `workbench/WorkbenchError.tsx:3-24` | 通用错误呈现 | 各面板内联 |
| 26 | 禁用功能占位（禁用按钮 + 常显原因小字） | `workbench/DisabledFeature.tsx:1-22` | `CAP-DEV-GAP` | 工具栏/页面列表/进度面板/Inspector 共 12 处 |

## A.4 阅读器子界面

| # | 界面 | 文件:行 | 承载能力 | 入口路径 |
|---|---|---|---|---|
| 27 | 阅读器工具栏（返回、章节标题、保存中、翻页/百分比、继续/从头开始、原文/译文切换） | `reader/ReaderToolbar.tsx:21-269` | `CAP-READ-PROGRESS`,`CAP-READ-MODE`,`CAP-READ-START-POS` | 阅读器顶部 |
| 28 | 分页阅读视图（左右各 25% 透明点击区 + 单页图） | `reader/PagedReaderView.tsx:15-156` | `CAP-READ-PAGED`,`CAP-READ-NAV` | 阅读器主区（rtl/ltr） |
| 29 | 长条阅读视图（单页 prop、按 `width/height_px` 换算滚动偏移） | `reader/WebtoonReaderView.tsx:15-108` | `CAP-READ-WEBTOON` | 阅读器主区（`webtoon_vertical`） |
| 30 | 页图组件（缺失译文/译文过期徽标、加载骨架、错误+重试） | `reader/ReaderPageImage.tsx:26-250` | `CAP-READ-IMAGE`,`CAP-TR-STALE-BADGE`,`CAP-TR-MISSING-BADGE` | 上述两视图内部 |
| 31 | 阅读空态 / 加载 / 错误 | `reader/ReaderEmptyState.tsx:9-75`；`ReaderPage.tsx:390-468` | `CAP-READ-EMPTY` | 阅读器主区 |

## A.5 设置页（12 个分区）

分类顺序与开关状态：`settings/SettingsPage.tsx:40-74`（12 个分区当前 `open: true`，`DISABLED_SECTION_TEST_IDS` 已空，`SettingsPage.tsx:76-80`）。

| # | 分区 | 面板文件:行 | 承载能力 |
|---|---|---|---|
| 32 | Provider（Profile 列表 + 内联表单 + 能力绑定 + 凭据） | `settings/ProviderProfilePanel.tsx`（列表 `:222-275`，表单 `:281-390+`）、`settings/CapabilityBindingPanel.tsx:54-92`、`settings/CredentialField.tsx:16-130` | `CAP-PRV-PROFILE-CRUD`,`CAP-PRV-BINDING`,`CAP-PRV-CREDENTIAL` |
| 33 | 网络/代理（Profile CRUD + 测试 + 默认 + resolve） | `settings/NetworkProfilePanel.tsx`（表单 `:477-560+`） | `CAP-PRV-NETWORK` |
| 34 | OCR（脚本/方向） | `settings/OcrSettingsPanel.tsx`；schema `settings/sections.ts:99-133` | `CAP-SET-OCR` |
| 35 | 翻译（SFX 策略 + 上下文页数/Token 预算） | `settings/SfxPolicyControl.tsx`、`settings/TranslationParamsPanel.tsx`；schema `sections.ts:153-202` | `CAP-SFX-POLICY-SET`,`CAP-SET-TRANSLATE` |
| 36 | 图片修复（质量/背景复杂度） | `settings/InpaintSettingsPanel.tsx`；schema `sections.ts:219-244` | `CAP-SET-INPAINT` |
| 37 | 排版样式 + "阅读方向不是全局设置"说明卡 | `settings/TypesetSettingsPanel.tsx`；说明卡 `SettingsPage.tsx:275-295` | `CAP-SET-TYPESET` |
| 38 | 模型/GPU | `settings/ModelGpuSettingsPanel.tsx` | `CAP-SET-MODEL-GPU` |
| 39 | 任务/并发 | `settings/TasksSettingsPanel.tsx` | `CAP-SET-TASKS` |
| 40 | 缓存/Revision 清理（预览/运行/重试 pending） | `settings/CacheRevisionPanel.tsx:91-127` | `CAP-CLN-*` |
| 41 | 回收站（列表 + 分批清空） | `settings/RecycleBinSettingsPanel.tsx:67-90+` | `CAP-RB-*`（与 A.2#14 重复实现） |
| 42 | 备份/恢复（.nmbak 创建/列出/恢复/删除） | `settings/BackupSettingsPanel.tsx:29-32,140-250` | `CAP-BAK-*` |
| 43 | 插件/Hooks（发现、全局开关、逐插件开关、审计、打开目录） | `settings/PluginSettingsPanel.tsx:32-39,136-211` | `CAP-PLG-*` |
| 44 | 设置分区通用外壳（卡片/加载骨架/错误条/未设置态/保存/dirty 文案/持久化值） | `settings/SectionPanelFrame.tsx:19-201`、`settings/useSettingsSection.ts:43-114`、`settings/SettingsErrorBar.tsx:15-73` | 全部 `CAP-SET-*` 的公共生命周期 |
| 45 | 设置分区禁用占位组件 | `settings/DisabledSection.tsx:13-107` | `CAP-DEV-GAP` |

## A.6 非产品表面（不计入产品界面，但同样发布在包里）

| # | 表面 | 文件:行 | 说明 |
|---|---|---|---|
| 46a | 遗留 Console 视图（`nav-console`/`nav-workbench`、`M2-RC2 resource channel runtime`、`LibraryPanel`、`SettingsPanel`） | `App.tsx:459-525`；`library/LibraryPanel.tsx:42-155`；`settings/SettingsPanel.tsx:100-235` | 生产模式下 `?view=console` 仍可达（`App.tsx:433-435,459`）；两个面板是 **GitHub 暗色板**，与主应用亮色主题完全不同 |
| 46b | 探测日志/deny 矩阵视图 | `App.tsx:437-457`（detecting）、`App.tsx:113-152` | 启动瞬间会渲染 `M2-RC2 resource channel runtime` 与 deny 结果 |
| 46c | FPS 采样浮层（`z-index: 9999`） | `perf/FpsRecorderPanel.tsx:200`；开关 `main.tsx:16-26`、`perf/fpsRecorder.ts` | 需 build flag / `?m2_fps=1` / localStorage 才启用 |
| 46d | 浏览器预览 IPC 垫片 | `dev/devMockBridge.ts:1-40+`；装配 `main.tsx:11-14` | 仅 `import.meta.env.DEV` |
| 46e | AC1 验收驱动 | `ac1/driver.ts`、`App.tsx:167-184` | 仅 `M2AC1_TEST_MODE=1` |

---

# B. 覆盖缺口：后端有命令、UI 没有出口 / 只有占位

## B.1 完全无前端引用（Tauri 已注册 + ACL 已允许，但 WebView 从不调用）

| 命令 | 证据 | 影响 |
|---|---|---|
| `revoke_resource_refs` | 命令注册 `apps/desktop/src-tauri/src/main.rs:73`；ACL `capabilities/m2rc1-commands.json:11`；前端全仓 grep 无引用（唯一吊销调用是 `resourceChannel/client.ts:68-70` 的 `revoke_ref`） | 批量回收资源引用凭据的能力未被使用；单条 `revoke_ref` 也只在 probe 脚本里调用（`App.tsx:274`），**产品运行期从不主动吊销** → 只能靠 Core 侧 TTL 过期 |
| `settings_provider_run_snapshot_get` | `main.rs:113`；`capabilities/m2rc1-commands.json:39` | 无法查看"某个 Run 实际用了哪套 Provider/模型快照"——而设置页反复强调"进行中的任务使用冻结快照"（`SectionPanelFrame.tsx:10-11`），用户却看不到该快照 |
| `settings_resolve_overrides` | `main.rs:122`；`capabilities/m2rc1-commands.json:48` | 无法查看"当前生效的覆盖链解析结果"；`CapabilityBindingPanel` 只能显示绑定表（`CapabilityBindingPanel.tsx:54`），无法显示最终解析值 |

## B.2 只有 probe / 测试出口

| 命令 | 证据 | 说明 |
|---|---|---|
| `revoke_ref` | `main.rs:72`；唯一调用点 `App.tsx:274`（probe 证据场景 E-04） | 产品代码路径从不吊销引用 |

## B.3 只有 DisabledFeature / 禁用控件 / "未开放"文案的缺口（12 + 4 处）

| 缺口 | UI 占位证据 | 对应 LEGACY 承诺 |
|---|---|---|
| 收藏切换（`is_favorite` 只读） | `bookshelf/BookCard.tsx:49,61`（`title="收藏（等待能力接入 GAP-G3）"`） | `doc/05_UI_MAPPING.md:393` |
| 删除作品（软删除入口） | `bookshelf/BookDetailPanel.tsx:191-208`（`disabled`，GAP-G2） | `doc/05_UI_MAPPING.md:396` |
| 标签管理 | `BookDetailPanel.tsx:213-231`（GAP-G7） | `doc/05_UI_MAPPING.md:395`；`doc/04_USER_FLOW.md:241` |
| 翻译约束/术语表 | `BookDetailPanel.tsx:232-250`（GAP-G8） | `doc/05_UI_MAPPING.md:528-575`；`doc/04_USER_FLOW.md:723` |
| 阅读摘要（最近阅读/累计时长） | `BookDetailPanel.tsx:147-167`（两行 `—` + GAP-G5 提示） | `doc/05_UI_MAPPING.md:412-413` |
| 人工译文编辑 | `workbench/RegionInspector.tsx:131-134`（`disabled` textarea）+ `:135`（GAP-G9，明确写"Ctrl+Enter 提交保持禁用"） | `doc/05_UI_MAPPING.md:886-913` |
| Region 锁定 | `RegionInspector.tsx:136`（GAP-G12） | `doc/05_UI_MAPPING.md:1031` |
| Revision pin | `RegionInspector.tsx:137`（GAP-G13） | `doc/05_UI_MAPPING.md` §29 后续 |
| 新建/删除 Region | `WorkbenchToolbar.tsx:80-81`（GAP-G10） | `doc/05_UI_MAPPING.md:855-856` |
| Region 几何编辑（移动/缩放/合并/拆分/reading_order） | `WorkbenchToolbar.tsx:82`（GAP-G11） | `doc/05_UI_MAPPING.md:857-862` |
| Core 可用性查询/事件 | `WorkbenchToolbar.tsx:83`（GAP-G16） | — |
| 逐页导入进度 | `WorkbenchToolbar.tsx:84`（GAP-G26） | — |
| 拖动调整页序 | `PageListPanel.tsx:127`（GAP-G14） | `doc/05_UI_MAPPING.md` §11 |
| 页面缩略图 | `PageListPanel.tsx:128`、`TaskProgressPanel.tsx:113`（GAP-G18） | `doc/05_UI_MAPPING.md:696-734` |
| 已有任务与中断 Run 发现（ListRuns） | `TaskProgressPanel.tsx:106-110`（GAP-G15："仅能查看本次工作台明确启动的 Run"） | — |
| 页面锁 | `TaskProjection.rows[].is_locked` 只读展示（`PageListPanel.tsx:227`），无写入 | `doc/05_UI_MAPPING.md:497,510` |

## B.4 命令有出口但能力被削掉一半（口径型缺口）

| 能力 | 实际限制 | 证据 |
|---|---|---|
| 导出 | 只能导出"当前选中的页"，`pageIds.length === 0` 时按钮禁用；无法整章/整本导出（请求体本身支持 `book_id`+`chapter_ids`） | `ExportDialog.tsx:56,60-63`；`WorkbenchToolbar.tsx:73`；请求类型 `workbench/client.ts:35-42` |
| 阅读方向/排版 | 阅读方向由投影给出，设置页只有"请去书架或章节属性里改"的说明文字；而书架**没有**该属性编辑入口 | `SettingsPage.tsx:275-295`；`ChapterList.tsx`（无属性编辑）；`chapter` 投影无方向字段 `library/types.ts:53-58` |
| Webtoon 阅读 | 只渲染 `projection.pages[0]` 单页（见 C-64） | `ReaderPage.tsx:475`；`WebtoonReaderView.tsx:15-22,97-104` |
| 回收站 | 只有"永久删除"，没有恢复/还原出口；Tauri 生产命令面也没有 restore 命令 | `RecycleBinPage.tsx:255-274`；`main.rs:70-165`（无 restore）；Core 侧是否有 restore 命令 **UNVERIFIED**（需 `01_CAPABILITY_INVENTORY.md` 核对） |
| 章节属性 | 只有标题；`chapter_number` 只读、无类型/方向/排序/备注编辑 | `library/client.ts:164-176`（`createChapter(bookId,title)`）；`doc/05_UI_MAPPING.md:431-456` 承诺 7 个字段 |
| 作品属性 | 只能新建（只有 title），无重命名/编辑 | `library/client.ts:152-162`；`doc/05_UI_MAPPING.md:392` 承诺"编辑作品" |
| 单 Region 重全翻译 | 命令存在（`retranslate_region_full`，`WorkbenchToolbar.tsx:21`），但只能从"19 项下拉框"里选，且必须先手选 Region | `WorkbenchToolbar.tsx:5-24,45-49`；`WorkbenchPage.tsx:324-326` |
| 翻译记忆（TM） | 无任何 UI | `doc/05_UI_MAPPING.md:575`、`doc/04_USER_FLOW.md:761` 承诺 |
| 页面右键菜单 | LEGACY 有完整单选/多选/章节级菜单；React 版**没有任何页面级右键菜单**，页面多选只在工作台页面列表里通过 ctrl/shift 存在 | `doc/05_UI_MAPPING.md:488-522`；`PageListPanel.tsx:200-232` |
| Region Inspector 分区 | LEGACY 承诺 7 个折叠分区（基本/OCR/翻译/样式/修复/Lock/Revision）；React 版只有 1 个原始字段区 + 历史列表 | `doc/05_UI_MAPPING.md:820-834`；`RegionInspector.tsx:94-273` |

---

# C. 缺陷识别（9 类，67 条）

**严重度口径**：P0 = 阻断主流程 / 造成错误理解或数据不可控；P1 = 显著拖慢专业工作流或造成误操作；P2 = 一致性、观感、可维护性。
**层归属**：`设计层` = 交互模型/信息结构本身错了，新设计必须换模型；`实现层` = 模型可留、实现要重写。
**分布**：P0 21 / P1 34 / P2 12。

## C.1 信息架构（10 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| IA-01 | 全局导航只有 4 个平级页面，无法表达"作品 → 章节 → 页面 → Region"四层工作深度；当前位置只能靠面板内列表的底色推断，没有面包屑/标题区 | `AppShell.tsx:162-314`；`WorkbenchPage.tsx:1211-1281`；`ChapterList.tsx:105-115` | 用户在大书里失去方位感，只能靠滚动列表找自己刚才在哪 | P0 | 设计层 |
| IA-02 | 工作台把"书/章/页"三级塞进同一 240px 单列滚动面板，三级列表上下相邻、同款 tile 样式 | `PageListPanel.tsx:107-124,140-250` | 三级列表视觉同权，误点概率高；深列表需要连续滚动 | P0 | 设计层 |
| IA-03 | 页面导航的正式入口之一是"按页面 ID 定位"文本框（手输内部 ID） | `PageListPanel.tsx:129-139` | 把内部标识当成用户路径；真实用户没有任何已知 page_id | P0 | 设计层 |
| IA-04 | 三级并列的"选中当前"语义不一致：书/章 tile 无选中样式之外的指示，页 tile 同时有"当前页"和"多选"两套状态 | `PageListPanel.tsx:147,172,214-223` | 用户分不清"我在哪一页"和"我选了哪几页" | P1 | 设计层 |
| IA-05 | 设置页有**两套并存实现**：亮色 12 分区 `SettingsPage`，与遗留 Console 里的暗色单分区 `SettingsPanel`（同一份 SFX 设置） | `App.tsx:519-520`；`SettingsPanel.tsx:100-235`；`SettingsPage.tsx:40-74` | 同一设置两处入口、两套外观、两套错误文案 | P1 | 实现层（含历史债） |
| IA-06 | 回收站同样双实现（书架模态 + 设置分区），一个有逐项选择、一个只有分批清空 | `BookshelfPage.tsx:405-445`；`RecycleBinSettingsPanel.tsx:67-90` | 用户在两处看到不同的回收站能力 | P1 | 实现层 |
| IA-07 | 书列表在书架与工作台各自独立拉取，没有共享状态、没有"列表变更"事件；工作台导入后书架不会刷新 | `BookshelfPage.tsx:58-81`；`WorkbenchPage.tsx:509-532`；`events.ts:53-74`（事件面只有 7 个，无 library 变更事件） | 跨页数据不一致，用户看到"过期书架" | P1 | 实现层（事件面缺口） |
| IA-08 | 隐藏的遗留 Console 视图在生产模式仍可通过 `?view=console` 打开（含 `Console`/`Workbench` 两个 nav 按钮 + 暗色面板） | `App.tsx:433-435,459-525` | 用户/支持人员可能误入第二套 UI，形成两个产品 | P2 | 实现层 |
| IA-09 | 章节行没有"当前章节"概念，只有三个动作按钮；无法表达"我正在这一章工作" | `ChapterList.tsx:66-186` | 从章节列表进入工作台后，回来找不到刚才是哪章 | P1 | 设计层 |
| IA-10 | 右侧详情面板固定 320px 且无选中时也占位；应用最小宽度 1024 时书架正文只剩约 640px | `tokens.ts:71-75`；`AppShell.tsx:153`；`BookDetailPanel.tsx:26-56,61-75` | 小屏/高分屏缩放下书架可用宽度被永久吃掉 1/3 | P1 | 设计层 |

## C.2 视觉一致性（9 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| VC-01 | 项目**没有任何样式表层**：0 个 `.css`/`.scss` 文件、无 `:root`、无 CSS 变量定义；全部视觉靠 710 处内联 `style={{…}}` | 全仓 `*.css` 计数 0；`style={{` 出现 710 次（非测试 tsx） | 无法做主题/暗色/密度切换；任何全局视觉调整都是散弹式改代码 | P0 | 实现层 |
| VC-02 | 令牌双轨且断裂：`tokens.ts` 一套；`RegionOverlay`/`RegionInspector`/`RelabelConfirmDialog` 用 `var(--st-warn, #fbbf24)` 一类**从未定义**的变量 → 永远走暗色 fallback，落在亮色 `#f5f5f4` 背景上 | `RegionOverlay.tsx:42-48`；`RegionInspector.tsx:228,299`；`RelabelConfirmDialog.tsx:22`；全仓无 `setProperty`/`:root` | 区域框、警告 pill、错误文字使用暗色主题色值，亮色界面上对比与语义都不对 | P0 | 实现层 |
| VC-03 | 硬编码颜色 280 处（绕过 tokens）；`tokens.ts` 之外还散落 `#c62828`、`#ffb300`、`#ff6b6b`、`#fef2f2`、`#fff1f0` 等一次性色值 | 计数 280；例：`RecycleBinPage.tsx:265-267,306,344`；`ImportDialog.tsx:415`；`SettingsErrorBar.tsx:34` | 同一种"危险/警告"至少有 6 种红/黄，语义无法学习 | P1 | 实现层 |
| VC-04 | 暗色孤岛：`LibraryPanel` 与 `SettingsPanel` 使用 GitHub 暗色板（`#161b22`/`#0d1117`/`#e6edf3`），与主应用亮色（`#f5f5f4`/`#1f2328`）并存于同一构建 | `LibraryPanel.tsx:48-54`；`SettingsPanel.tsx:100-110`；`tokens.ts:8,22` | 同一应用两套视觉语言 | P1 | 实现层 |
| VC-05 | 图标体系三分裂：emoji（📚🛠️📖⚙️🗑️📄📁⌛⚠️🔒，共 25 处）+ 文本符号（★☆⊞☰✕−＋）+ 自绘 SVG | `AppShell.tsx:218,249,281,311`；`BookshelfToolbar.tsx:105,156,253,272`；`RegionOverlay.tsx:93-235` | 图标风格、尺寸基线、可访问文本全都不一致 | P1 | 设计层 |
| VC-06 | 字号体系失控：15 种 `font-size` 字面量（10/11/12/13/14/15/16/18/20/24/30/32/36/40/48），而 tokens 只定义 6 档 | 计数 15 档；`tokens.ts:48-55`；`RegionInspector.tsx:78-97,123-129,242` | 层级读不出来，10px 正文化 | P1 | 实现层 |
| VC-07 | 按钮没有主次：导出对话框的「取消」与「选择位置并导出」共用同一个 `buttonStyle` | `ExportDialog.tsx:23,108,109` | 破坏性/提交动作无视觉权重，误点风险 | P2 | 实现层 |
| VC-08 | 中英混排未本地化：`Inspector`、`no region selected`、`Page N`、`Next page`、`status` 枚举原文直接进界面 | `RegionInspector.tsx:88,91`；`PagedReaderView.tsx:110,152`；`ReaderPageImage.tsx:238`；`TaskProgressPanel.tsx:116,124,135,144,147` | 中文界面里插入英文机器词，专业用户需二次翻译 | P1 | 实现层 |
| VC-09 | 应用名/窗口标题仍是测试代号：`index.html` 标题 `M2-RC1 resource channel runtime`、窗口标题同值、`document.title` 在运行期被改写为 `M2RC1|interactive|deny=…` | `index.html:4`；`tauri.conf.json:11`；`App.tsx:99,144-146` | 任务栏/标题栏显示证据字符串，用户会认为装错了软件 | P2 | 实现层 |

## C.3 信息密度（6 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| ID-01 | 工作台工具栏 44px 高、`overflowX: auto`，里面塞了 19 项批处理命令下拉 + 开始按钮 + 导入 + 导出 + 视图模式 + 5 个带解释小字的禁用功能 | `WorkbenchToolbar.tsx:56-84` | 1024 宽下必须横向滚动才能看全最常用操作；禁用说明把工具栏变成变更日志 | P0 | 设计层 |
| ID-02 | Region Inspector 直接把内部字段名当标签：`region_id` / `region_type` / `sfx_policy` / `origin` / `revision_no`，值也是原始枚举 | `RegionInspector.tsx:95-120` | 产品最核心的"选中一个文字块后能做什么"被实现成调试面板 | P0 | 设计层 |
| ID-03 | 任务进度面板固定 220px，即使"没有本次会话中已知的 Run"也占满底部 | `TaskProgressPanel.tsx:78,105` | 工作台画布永久损失 220px 高度 | P1 | 实现层 |
| ID-04 | 10–11px 文字成片：策略说明整段 10px、修订历史整行 10px、反馈条 11px | `RegionInspector.tsx:123-129,233-272`；`ViewerPanel.tsx:288` | 专业用户长时间阅读，10px 中文几乎不可读 | P1 | 实现层 |
| ID-05 | 章节行每行 3 个按钮 × N 行 + 页码 + 页数，行高 32px | `ChapterList.tsx:66-186`（按钮 `:130-183`） | 列表噪声大，主操作（进入）被稀释 | P1 | 设计层 |
| ID-06 | 工作台右列 320px 同时承载 Inspector + 修订历史列表 + 恢复确认；一个受控列承载三种不同粒度信息 | `WorkbenchPage.tsx:1263-1280`；`RegionInspector.tsx:232-273` | 修历史一展开就把 Inspector 顶出视口 | P2 | 设计层 |

## C.4 交互效率（9 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| IE-01 | 19 个批处理命令只能"下拉框选一个 + 点启动"，命令名全是同构长中文（翻译/重渲染/重修复/重新OCR × 全章/选择页/当前页/Region），无分组、无快捷键、无最近使用 | `WorkbenchToolbar.tsx:5-24,63-71` | 每次批处理都是一次"读 19 条下拉项"的认知开销 | P0 | 设计层 |
| IE-02 | 模态遮罩堆叠：书架可同时叠加 回收站(1500) → 永久删除确认(2000)，创建/导入/导出各占 1000 | `BookshelfPage.tsx:405-445`；`PermanentDeleteConfirmDialog.tsx:53`；`CreateTitleDialog.tsx:72`；`ImportDialog.tsx:141`；`ExportDialog.tsx:68` | 深层操作被遮住上下文；Esc/点击外部行为在各层不一致 | P0 | 设计层 |
| IE-03 | 页面列表的方向键处理在"移动焦点"的同时**真正切页**（触发 resolve + 全量取图） | `PageListPanel.tsx:200-210` → `WorkbenchPage.tsx:828-868`、`614-651` | 用方向键扫一眼页面列表就等于把每页都下载一遍 | P0 | 实现层 |
| IE-04 | 书架的章节页数是 N+1 次 IPC 算出来的（每章一次 `list_chapter_pages` 只为了 `length`） | `BookshelfPage.tsx:93-102` | 50 章的书写入 51 次调用，选中作品后明显卡顿 | P1 | 实现层 |
| IE-05 | 切设置分区会卸载面板 → 每次重进都重新 `settings_get`，重新出现骨架屏 | `SettingsPage.tsx:240-326`（条件渲染）；`useSettingsSection.ts:78-80` | 12 个分区来回对比配置时反复等待 | P1 | 实现层 |
| IE-06 | 导出强绑定"先选页"，无法对整章/整本发起；`ExportDialog` 的 `pageIds` 为空即禁用 | `ExportDialog.tsx:56`；`WorkbenchToolbar.tsx:73`；`workbench/client.ts:35-42` | 交付一个章节要逐页勾选 | P1 | 设计层 |
| IE-07 | 没有全局命令面板；命令分散在四个页面各自的按钮/下拉里，快捷键只有 `Ctrl+1..4` | `AppShell.tsx:110-130` | 熟练用户无法摆脱鼠标 | P1 | 设计层 |
| IE-08 | 撤销只有"改标后 10 秒内、当前页、无新操作"这一种；其它写操作不可撤销 | `WorkbenchPage.tsx:985,1008`；`ViewerPanel.tsx:306-324` | 误操作代价高，用户倾向于不敢操作 | P1 | 设计层 |
| IE-09 | 导入必须先有章节；空书架时导入弹窗直接给出"暂无章节"的不可用态，而"新建章节"在其父面板里（用户被引导去关弹窗） | `ImportDialog.tsx:265-282`；`BookDetailPanel.tsx:267-285` | 首次使用路径断裂 | P2 | 设计层 |

## C.5 状态与反馈（8 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| ST-01 | 全局每 2 秒一次 `core_ping`，无退避、无可见性判断，四页常驻时也照跑；结果只体现为一条横幅 | `AppShell.tsx:68-90` | 空转 IPC；横幅是唯一的健康信号，且只有三种文案 | P0 | 实现层 |
| ST-02 | Run 快照 250ms 轮询 + 导出快照 250ms 轮询；且进度只对"本 Session 亲手启动的 Run"可见 | `WorkbenchPage.tsx:478-488`；`TaskProgressPanel.tsx:106-110` | 每秒 8 次 IPC；关掉工作台或重开应用就丢失全部运行可见性 | P0 | 设计层 |
| ST-03 | 失败信息统一降格为"错误代码：X"：至少 8 处直接把内部 code 当正文 | `bookshelf/error.ts:180-186`；`WorkbenchError.tsx:20`；`PageListPanel.tsx:162,186,240`；`ReaderPage.tsx:439`；`ReaderPageImage.tsx:213`；`bookshelf/BookshelfPage.tsx:304` | 用户拿到 `PAGE_NAV_UNAVAILABLE` 而不是"接下来该做什么" | P0 | 设计层 |
| ST-04 | E4 反馈条 36px 高 + `nowrap` + `ellipsis`：长错误（如"改标失败：REGION_CHANNEL_UNAVAILABLE（region 未变更；冲突后可刷新再操作）"）会被截断且无展开 | `ViewerPanel.tsx:288-303`（`height:36`、`whiteSpace:"nowrap"`、`overflow:"hidden"`、`textOverflow:"ellipsis"`） | 关键失败原因读不到全句 | P1 | 实现层 |
| ST-05 | 设置保存后没有明确的"已保存"确认态，只有 `dirty-state` 文案 + "当前持久化值"一行 | `SectionPanelFrame.tsx:173-196`；`useSettingsSection.ts:82-100` | 用户不确定是否真的写入 | P1 | 实现层 |
| ST-06 | 阅读进度保存失败被静默吞掉（`catch {}`），界面只可能短暂显示"保存中…" | `ReaderPage.tsx:172-173`；`ReaderToolbar.tsx:94-105` | 进度丢失无任何告知 | P1 | 实现层 |
| ST-07 | 纯 UI 状态会静默丢失：切页时 `setSuspects(new Set())` 清空"疑似拟声词"人工标记 | `WorkbenchPage.tsx:857` | 用户的人工标注无声消失 | P1 | 实现层 |
| ST-08 | 任务进度只存在于工作台底部面板；其它页面、任务栏、标题栏都没有任何进度指示 | `TaskProgressPanel.tsx:63-163` | 切到书架/阅读器后无法得知长任务是否还在跑 | P2 | 设计层 |

## C.6 错误恢复（6 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| ER-01 | **导入过程中无法取消**：`busy` 时关闭按钮 `disabled`、Esc 处理被 `!busy` 拦下，文案还要求"处理期间请勿关闭窗口" | `ImportDialog.tsx:59`（`if (e.key === "Escape" && !busy)`）、`:168`（`disabled={busy}`）、`:384-388` | 大文件夹导入卡住时，用户只能杀进程 | P0 | 设计层 |
| ER-02 | 导入报告只有 4 个聚合计数，逐文件失败原因被明确隐藏（"已隐藏原始错误详情"） | `ImportDialog.tsx:429`（注释）、`:559-562`（文案） | 用户知道"3 个失败"，但不知道是哪个文件、为什么 | P1 | 设计层 |
| ER-03 | revision 冲突只能"刷新再操作"，没有对比、没有重试策略选择 | `WorkbenchPage.tsx:991-998` | 冲突即人工重来 | P1 | 设计层 |
| ER-04 | 回收站没有恢复入口；Tauri 生产命令面也没有恢复命令 | `RecycleBinPage.tsx:255-274`；`main.rs:70-165` | "回收站"实际是"待永久删除队列"，与用户心智不符 | P1 | 设计层 |
| ER-05 | 未知错误码把内部 code 拼进中文句子 | `bookshelf/error.ts:184`（`系统报告代码：${code}`） | 用户面对 `UNKNOWN_ERROR` 无从下手 | P2 | 实现层 |
| ER-06 | 全区域错误替换：`CORE_UNAVAILABLE` 时把整个工作台内容替换成一张错误卡，用户无法继续查看已加载的数据 | `WorkbenchPage.tsx:1195-1206` | 单点故障造成整页不可用 | P2 | 实现层 |

## C.7 键盘与鼠标（7 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| KB-01 | 四页常驻 + 各页 `window` 级 keydown 无"当前可见"判断：阅读器一旦加载过章节，方向键/PageUp/PageDown/Home/End 在书架、工作台、设置页也会被 `preventDefault` | `AppShell.tsx:376-436`（keep-alive）；`ReaderPage.tsx:246-336`（`:302-330` 拦截并 preventDefault） | 其它页面的方向键滚动和 Home/End 失效 | P0 | 实现层 |
| KB-02 | `Ctrl+F` 被书架工具栏全局抢注；在其它页面按下只会尝试聚焦一个 `display:none` 里的输入框 | `BookshelfToolbar.tsx:23-32`；`AppShell.tsx:381`（隐藏容器） | 跨页快捷键静默失效 | P0 | 实现层 |
| KB-03 | 焦点可见性被系统性关闭：10 处 `outline: "none"` 且没有 `:focus-visible` 替代（内联样式无法写伪类） | `AppShell.tsx:215,246,278,308`；`BookshelfToolbar.tsx:136,219`；`BookCard.tsx:40`；`BookList.tsx:72`；`PagedReaderView.tsx:108,150` | 键盘用户看不到焦点在哪 | P0 | 实现层 |
| KB-04 | 右键菜单是改标主入口，但无键盘等价路径、无 `role="menu"`、Esc 只在 stage 获得焦点时才生效 | `RelabelContextMenu.tsx:64-80`；`ViewerPanel.tsx:161-166` | 纯键盘用户无法完成改标 | P1 | 设计层 |
| KB-05 | SVG Region 帧自行拦 Tab 并造焦点环（`preventDefault` + 手算索引） | `RegionOverlay.tsx:138-148` | 焦点顺序被自定义逻辑覆盖，与浏览器/读屏预期不符 | P1 | 实现层 |
| KB-06 | 多选能力极不均衡：只有工作台页面列表支持 ctrl/shift；书架与章节列表完全没有批量选择 | `WorkbenchPage.tsx:870-888`（多选实现）；`BookCard.tsx:21-26`（单击即选）；`ChapterList.tsx:148-182` | 批量操作只能逐条点 | P1 | 设计层 |
| KB-07 | 6 个对话框都没有焦点陷阱/初始焦点/焦点归还（`role="dialog"` 有，键盘闭环没有） | `CreateTitleDialog.tsx:63-93`；`ImportDialog.tsx:128-159`；`ExportDialog.tsx:68-110`；`RelabelConfirmDialog.tsx:40-53`；`PermanentDeleteConfirmDialog.tsx:41-71`；`RegionInspector.tsx:276-288` | Tab 会跑出模态；关闭后焦点落回 body | P2 | 实现层 |

## C.8 可访问性（6 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| A11Y-01 | 导航用 emoji 作为唯一图形语义（📚🛠️📖⚙️），文本标签 10px，语义靠 `title` 提示 | `AppShell.tsx:196-219`（`title="书架 (Ctrl+1)"` + `<span>📚</span>`） | 读屏/触控/高分屏下图标语义不稳定；emoji 渲染随系统字体变化 | P0 | 设计层 |
| A11Y-02 | 选中态只写 `data-active` / `data-selected`，没有 `aria-current` / `aria-selected` | `AppShell.tsx:198,229,261,291`；`BookCard.tsx:19`；`BookList.tsx:52` | 辅助技术无法得知当前位置/当前选中 | P1 | 实现层 |
| A11Y-03 | 页图 alt 是英文占位（`page` / `Page N`），不表达页码语义 | `ViewerPanel.tsx:215`；`ReaderPageImage.tsx:238` | 读屏用户无法获得页语义 | P1 | 实现层 |
| A11Y-04 | 禁用控件的唯一解释放在 `title` 里（悬停才可见、键盘不可达），且部分是"禁用按钮 + 常显小字"混用 | `BookDetailPanel.tsx:195,217,236`；`DisabledFeature.tsx:13,19`；`TaskProgressPanel.tsx:53` | 键盘用户永远看不到"为什么不能用" | P1 | 设计层 |
| A11Y-05 | 没有 `prefers-reduced-motion` / `prefers-color-scheme` 支持，所有过渡硬编码；`tokens.ts` 无 motion/theme 维度 | `AppShell.tsx:214,245,277,307`；`tokens.ts:5-80` 全文 | 前庭敏感用户与暗色偏好用户无法适配 | P2 | 实现层 |
| A11Y-06 | 文档语言声明为英文（`<html lang="en">`），界面正文为中文 | `index.html:2` | 读屏发音语言错配 | P2 | 实现层 |

## C.9 长任务与高 DPI（6 条）

| ID | 现象 | 证据 | 用户影响 | 严重度 | 层 |
|---|---|---|---|---|---|
| LP-01 | 阅读无图片缓存/预取：每次翻页都"issue → 逐 16MiB chunk 全量拉取 → createObjectURL"，上一页立即 revoke | `ReaderPageImage.tsx:49-105`；`resourceChannel/client.ts:81-101` | 每次翻页都重下一整张原图，翻页延迟明显 | P0 | 实现层 |
| LP-02 | Webtoon 长条阅读只渲染 `pages[0]` 一页，滚动进度按单页高度算 | `ReaderPage.tsx:471-481`（`page={projection.pages[0]}`）；`WebtoonReaderView.tsx:15-22,85-105`；`ReaderPage.tsx:236-243` | 长条模式对多页章节实质不可用（只看到第 1 页） | P0 | 实现层（也含设计层：模式定义不完整） |
| LP-03 | Region 覆盖层尺寸只在挂载时用 callback ref 测一次，没有 `ResizeObserver`；窗口/面板缩放后 SVG 尺寸与页图不匹配 | `ViewerPanel.tsx:120-130`；`RegionOverlay.tsx:93-98` | 缩放窗口或拖动分栏后，Region 框整体错位 | P0 | 实现层 |
| LP-04 | 无缩略图通道，列表只能显示文件名；页面列表/任务详情用纯文本标识页面 | `PageListPanel.tsx:128`（GAP-G18）、`:227`；`TaskProgressPanel.tsx:113` | 漫画工作流里"看图认页"不可用 | P1 | 设计层（受能力缺口约束） |
| LP-05 | 全部列表无虚拟化：书、章、页、修订历史全量渲染 DOM | `BookGrid.tsx:23`；`PageListPanel.tsx:212`；`RegionInspector.tsx:235`；`RecycleBinPage.tsx:438` | 数百页章节时首屏与滚动抖动 | P1 | 实现层 |
| LP-06 | 高 DPI 零处理：无 `devicePixelRatio`/`image-rendering`/缩放因子相关代码；窗口 1180×860 硬编码且无最小尺寸配置，最小尺寸只靠 CSS `minWidth/minHeight` | `tauri.conf.json:9-14`（无 `minWidth`/`minHeight`/`theme`/`zoomHotkeysEnabled`）；`AppShell.tsx:153-154`；`tokens.ts:71-72` | 200% 缩放下最小宽高把内容压到不可用；原生窗口可被拖到小于界面的尺寸 | P2 | 实现层 |

---

# D. 不可沿用的交互假设清单（新设计必须替换）

每条给出"旧假设 → 为什么必须换掉 → 证据"。

| # | 旧假设 | 为什么必须替换 | 证据 |
|---|---|---|---|
| D-01 | **四个平级一级页面 + 常驻 keep-alive 就是全局 IA** | 产品是"作品→章节→页面→Region"四层深度工作，平级四页无法表达层级，也无法表达"我在这本书这一章这一页"；keep-alive 还让所有页面的全局副作用（键盘/轮询）互相污染 | `AppShell.tsx:11,162-314,376-436`；`AppShell.test.tsx:64-70` |
| D-02 | **页面级跳转（setActivePage）即导航** | 跳转不携带可恢复的上下文（`workbenchContext` 只存 `bookId/chapterId`，且用 null 表示"无"），也没有 URL/历史/返回栈；Esc 只能"返回书架" | `AppShell.tsx:18-34,132-144`；`ReaderPage.tsx:253-256` |
| D-03 | **线性模态向导（一次一个弹窗、堆叠遮罩）** | 导入/导出/改标/恢复/删除全部是模态，最多三层叠加（1000/1500/2000），且深层模态让用户失去对作品的浏览上下文 | `CreateTitleDialog.tsx:72`；`ImportDialog.tsx:141`；`ExportDialog.tsx:68`；`BookshelfPage.tsx:415`；`PermanentDeleteConfirmDialog.tsx:53` |
| D-04 | **用"内部 ID 输入框"做导航** | "按页面 ID 定位"把实现细节变成用户路径；专业软件不应要求用户知道 `page_id` | `PageListPanel.tsx:129-139` |
| D-05 | **用原始字段名/原始枚举做详情面板** | `region_id/region_type/sfx_policy/origin/revision_no` + 英文枚举原文，是把数据层直接贴到产品上 | `RegionInspector.tsx:95-120`；`TaskProgressPanel.tsx:116-147` |
| D-06 | **19 项同构命令挤在一个 `<select>` 里** | 命令的选择成本随命令数线性上升；批处理需要"目标域 × 步骤 × 范围"的结构，而不是一维长列表 | `WorkbenchToolbar.tsx:5-24,63-71` |
| D-07 | **进度只在一个页面内的一个固定面板里** | 长任务是产品常态（翻译/OCR/修复/导出），进度必须跨页面、跨上下文可见；当前"只显示本 Session 启动的 Run"更使可见性不可靠 | `TaskProgressPanel.tsx:63-163,106-110`；`WorkbenchPage.tsx:478-488` |
| D-08 | **错误只以"错误代码"或一次性反馈条出现** | 8+ 处把内部 code 当正文；反馈条还会 ellipsis 截断；没有"错误中心/可追溯的失败清单" | `bookshelf/error.ts:180-186`；`PageListPanel.tsx:162,186,240`；`ViewerPanel.tsx:288-303` |
| D-09 | **无全局命令面板 / 无统一快捷键层** | 快捷键分散在 4 个组件、作用域不统一（window vs 元素），且互相抢注（Ctrl+F、方向键） | `AppShell.tsx:110-130`；`BookshelfToolbar.tsx:23-32`；`ReaderPage.tsx:246-336`；`TaskProgressPanel.tsx:67-76`；`ViewerPanel.tsx:161-180` |
| D-10 | **无多选批处理（书架/章节）** | 只有页面列表有 ctrl/shift 多选；批量导出/批量删除/批量改标无从下手 | `BookCard.tsx:21-26`；`ChapterList.tsx:148-182`；`WorkbenchPage.tsx:870-888` |
| D-11 | **无并排对照（原文/译文、两页、两修订）** | 阅读器是"整页切换原文或译文"（二选一），修订历史是纯文本列表，没有并排 diff；翻译校对的本质工作因此无法进行 | `ReaderToolbar.tsx:220-265`；`RegionInspector.tsx:232-272`；`ReaderPage.tsx:210-218` |
| D-12 | **"卡片 + 固定右栏"作为唯一详情形态** | 320px 固定栏 + 单选卡片，无法承载 Region 级的多分区信息，也无法在宽屏上做真正的分栏工作台 | `BookDetailPanel.tsx:61-75`；`WorkbenchPage.tsx:1263-1280` |
| D-13 | **所有视觉靠内联样式 + 单一 `tokens` 常量** | 0 个 CSS 文件、710 处内联样式、无 CSS 变量 → 无法做主题/暗色/密度/高 DPI 适配，任何视觉系统都无法落地 | 全仓 `.css` = 0；`style={{` = 710；`tokens.ts:5-80` |
| D-14 | **`title` 属性作为解释与提示的唯一载体** | 禁用原因、"清空搜索(Esc)"、收藏缺口说明全在 `title` 里：悬停才可见、键盘不可达、触控不可用 | `BookCard.tsx:49,61`；`BookDetailPanel.tsx:195,217,236`；`BookshelfToolbar.tsx:93,143`；`DisabledFeature.tsx:13` |
| D-15 | **写操作默认可"静默丢失"** | 疑似标记切页即清、阅读进度保存失败静默、撤销只有 10 秒单点；缺少"待提交/未保存"的状态模型 | `WorkbenchPage.tsx:857,985`；`ReaderPage.tsx:172-173` |
| D-16 | **一次只处理一个 Region，且改标只有两个值** | 改标只支持 speech↔sfx，其它四种类型（narration/title/note/other）无入口、无批量改标 | `region/types.ts:14-21`；`relabelMachine`（`canRetype` 见 `RelabelContextMenu.tsx:47-48`）；`WorkbenchToolbar.tsx:80-82` |
| D-17 | **导入是"同步阻塞 + 不可取消 + 只有聚合结果"的模态** | 大目录导入既不能取消也不能看进度，失败不可定位 | `ImportDialog.tsx:59,168,384-388,429,559-562` |
| D-18 | **运行状态靠前端轮询（250ms/2s）维持** | 8 IPC/s 的轮询是前端代替事件通道；事件面只有 7 个事件且都是"失效提示" | `WorkbenchPage.tsx:478-488`；`AppShell.tsx:68-90`；`events.ts:53-74` |
| D-19 | **"未开放"作为一等 UI 元素** | 12 处 `DisabledFeature` 把工程缺口、wire 未冻结、GAP 编号直接渲染在生产界面（含 `GAP-G7` 这类编号） | `DisabledFeature.tsx:19`；`WorkbenchToolbar.tsx:80-84`；`BookDetailPanel.tsx:230,249`；`RegionInspector.tsx:135-137` |
| D-20 | **调试/证据表面与产品表面同包共存** | `?view=console` 遗留暗色 UI、deny 矩阵日志、FPS 浮层、`document.title` 证据串都在同一构建里 | `App.tsx:99,433-435,459-525`；`perf/FpsRecorderPanel.tsx:200`；`main.tsx:16-26` |

---

## 附：本次盘点未覆盖 / 需下游补的事项

| 事项 | 状态 | 建议归属 |
|---|---|---|
| Core 侧是否存在书籍恢复（undelete）命令 | `UNVERIFIED` | `task-1` / `01_CAPABILITY_INVENTORY.md` |
| `settings_provider_run_snapshot_get`、`settings_resolve_overrides` 是"预留"还是"遗漏接入" | `UNVERIFIED`（代码里无调用，也无注释说明） | 需 Lead 与 Core 契约核对 |
| Webtoon 长条模式的 Core 投影是否本就按"单页长图"建模 | `UNVERIFIED`（`ReaderPageProjection` 有 `height_px`，暗示长图可能是一页） | 需与 `task-1` 的 Page/Chapter 模型核对 |
| 真实设备上的高 DPI 行为 | `UNVERIFIED`（无 `devicePixelRatio` 代码，未在实机采样） | 需 e2e 或人工验证 |
| 主题候选 F（`doc/design/tokens-cand-f.json`）是否为既定方向 | 事实存在且被 AC6 引用为比对基准，但**未接入运行时**（`e2e/p02-new-time/ac6-contrast.mjs:362`） | 由 Lead 裁决，本文不主张 |
