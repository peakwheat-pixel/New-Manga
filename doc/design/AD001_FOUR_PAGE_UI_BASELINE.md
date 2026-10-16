# AD-001 四页 UI/UX 设计基线（Bookshelf / Workbench / Reader / Settings）

状态：**UI-DESIGN-1 设计交付物（待独立 Review 与 Coordinator 集成）**。
Owner：ZCode。基线 commit：`c6f975d38842487c16491eea67a01cf134c337f8`（分支 `agent/zcode/UI-DESIGN-1` 起点）。

本文为新架构（React + TypeScript + Tauri/Rust + Python Core + SQLite，见 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)）的**四页 UI/UX 设计基线**，是 P12 / P14 / P15 / P17 实现 Task 的唯一 UI 前置。目标是：实现者在各自（另行冻结的）范围内**不需要再做设计决策**。

## 0. 事实优先级与引用约定（本文必读）

本文按 [UI-DESIGN-1 Task](../tasks/UI-DESIGN-1.md) 的事实优先级写作：

1. **CURRENT 架构权威**：[AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)（只读）。四页区域划分、"React/WebView 经显式 Tauri IPC 边界到达 Python Core；不直接访问数据库、任意文件系统路径或模型"、大图/tile/模型权重不得走普通 JSON/Base64 IPC，全部继承，本文不重复定义、不放松。
2. **REQUIREMENT 参考**（产品行为来源，不授予实现权限）：[01 功能架构](../01_FUNCTIONAL_ARCHITECTURE.md)、[04 用户流程](../04_USER_FLOW.md)、[07 非功能需求](../07_NON_FUNCTIONAL_REQUIREMENTS.md)、[08 验收标准](../08_ACCEPTANCE_CRITERIA.md)。
3. **冻结契约（UI 只能绑定其中已冻结的命令/事件）**：[M2-C1 类型化 IPC 契约](../contracts/M2-C1_TYPED_IPC_CONTRACT.md)（rev 2.3）、[M2-RC4 域命令](../contracts/M2-RC4_DOMAIN_COMMANDS.md)、[P09 导入契约](../contracts/P09_IMPORT_CONTRACT.md)、[P10 凭据配置契约](../contracts/P10_CREDENTIAL_CONFIG_CONTRACT.md)、[P11 长任务生命周期契约](../contracts/P11_LONG_TASK_LIFECYCLE_CONTRACT.md)。
4. **既有实现（只读事实）**：`apps/desktop/frontend/src/**` 当前是 M2 探针/验收壳与组件级素材（`App.tsx` 为 deny matrix + AC1 driver），**不是** AD-001 生产四页；其 client 层（`library/`、`settings/`、`region/`、`resourceChannel/`）证明了下述已冻结 wire 的真实调用形态，可复用其模式，不得假设其上层组件就是生产 UI。
5. **LEGACY（历史参考、非绑定）**：[05 UI 映射](../05_UI_MAPPING.md)、[ui-baseline](../ui-baseline.md)（QML 视觉基线）、`doc/design/ui-reference.html`、`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`、[UI_UX_GUI_DESIGN](../contracts/UI_UX_GUI_DESIGN.md)（Qoder 署名，作者已退出项目）。本文引用 LEGACY 处一律显式标注「历史参考、非绑定」，LEGACY **从不单独**作为任何要求的依据。

**标注约定**：
- `【依据】` = 引用 CURRENT 架构权威或 REQUIREMENT 文档的具体章节/AC；
- `【契约】` = 引用冻结契约的命令/事件/条款（可逐字检索，见 §6 绑定表与 AC8 自检）；
- `【自有取值】` = 本设计为新架构冻结的自有决策（含设计令牌、尺寸、快捷键等），非 REQUIREMENT 继承、非 LEGACY parity；
- `【GAP-Gxx】` = 该交互所需能力没有已冻结 wire，登记于 §7 Wire Gap List；实现 Task **不得**以 mock、私有路径或绕过 Tauri IPC 的方式消解。

尺寸单位除注明外均为 CSS 逻辑像素（DPI 处理见 §8.7）。

---

## 1. 导航 Shell（App Shell）

### 1.1 一级导航形态

**左侧固定导航 Rail**（垂直图标+文字入口），顺序固定：书架 → 工作台 → 阅读器 → 设置。

- 一级页面只有且仅有这四个【依据：04 §1.1；08 AC-NAV-002「一级页面只有四个」，作品详情/任务详情/标签管理等不得成为第五个一级 Route】。
- 软件启动默认进入**书架**；不自动跳回上次的工作台或阅读器【依据：04 §3；08 AC-NAV-001】。
- Rail 宽度 **64px**【自有取值；数值与 LEGACY QML 基线（[ui-baseline](../ui-baseline.md) §1 的 64px）一致属设计延续，非绑定】。入口为「图标 + 竖排短标签」，当前页高亮态由路由状态驱动。
- 工作台入口右上角挂 **NavBadge 运行指示**（小圆点/胶囊）：存在 `running` 状态 Run 时显示，无 Run 时隐藏【自有取值；数据依赖见 G15（Run 发现/列表 wire 未冻结）→ 实现期若无 wire 则隐藏，不得虚构状态】。
- 除四页切换外，其他业务内容遵循：**当前一级页面固定区域优先；不适合固定展示的内容使用居中悬浮窗**；不得为作品详情、章节详情、标签管理、任务详情、Provider 编辑等新建一级页面【依据：04 §1.2、§1.3；01 §1 总览图注】。
- 悬浮窗规则（模态背景不强制变暗、辅助工具 Non-modal、可调大小/最大化/拖出主窗口/双屏、编辑类不允许点击外部关闭、危险操作明确确认、无未保存修改时 `Esc` 关闭、有未保存修改弹「保存/放弃/取消」）【依据：04 §1.3；08 AC-WIN-002/003/005】。新架构下「拖出主窗口」由 Tauri 多 WebView 窗口实现，属实现 Task 范围；本基线只冻结交互语义。

### 1.2 四页切换语义（冻结）

**切换一级页面不销毁页面组件、不停止运行中的任务**——四页组件常驻挂载（keep-alive），切换仅改变可见性。

- 【依据：08 AC-NAV-003「工作台 → 设置 → 工作台，返回后 Book A / Chapter 12 上下文仍在；运行中的 Pipeline 不因离开页面停止」；04 §30（Run 生命周期与页面无关，长任务在 Python Core 内推进）】。
- 【契约佐证：M2-C1 §2 依赖方向——Run 调度与持久化全部在 Python Core；P11 §7.1「UI、bridge……MUST NOT 自行规划目标、推进 Run/Task/StepRun」——UI 卸载与否与 Run 无关；P11 §7.2「P13 提供基于权威 Run 的只读投影」】。因此「切换不停止任务」不是 UI 的主动义务而是架构事实；UI 侧对应要求是：**页面隐藏期间不清空已加载投影，返回时按 §6 绑定表事件/快照重新同步**（事件是失效提示，快照是真值【契约：M2-C1 §6.2】）。
- 页面级 UI 本地状态（选择、过滤、滚动位置、未保存输入）随组件常驻而保留；**React 不写持久化状态**（见 §9）。

### 1.3 最小窗口尺寸与伸缩行为（冻结）

- 最小窗口：**1024 × 680**；推荐默认：**1280 × 800**【自有取值，由工作台最小可用内容宽度推算：Rail 64 + PageList 240 + Inspector 320 + Viewer 最小 380 + 分隔线/边距 ≈ 1024；顶栏 48 + 工具栏 44 + TaskProgress 折叠条 44 + Viewer 最小高度 ≈ 680】。
- 伸缩行为：
  - 宽度增加时，优先扩展各页的**主内容区**（书架 BookGrid、工作台 Viewer、阅读器视口、设置内容面板）；固定宽度面板（BookDetailPanel 320、PageList 240、Inspector 320、设置分类导航 200、Rail 64）不随拉伸变化【自有取值】。各固定面板宽度允许用户在 240–420 区间拖动调节并记入**本地窗口布局状态（host 侧，非 Core 持久化）**【自有取值；不写 SQLite，见 §9.4】。
  - 高度增加时，扩展主内容区；TaskProgressPanel 展开态占底部固定高（约 220），折叠态 44。
  - 低于最小尺寸由窗口系统阻止（Tauri min-size），布局不提供 < 1024 的降级形态。
- 多显示器/双屏与 DPI 验证矩阵（100%/125%/150%/175%/200%）按 07 §8/§9 执行【依据】；窗口恢复时原显示器不存在则回到当前可用主屏【依据：07 §9】。

### 1.4 键盘与焦点（Shell 级）

- 四页切换快捷键：`Ctrl+1` 书架、`Ctrl+2` 工作台、`Ctrl+3` 阅读器、`Ctrl+4` 设置【自有取值】。
- Tab / Shift+Tab 在当前页内按 DOM 顺序移动焦点；焦点环规范见 §8.6。
- 启动后初始焦点：书架页首个可交互控件【自有取值】。
- 危险确认对话框内 `Enter` = 主确认、`Esc` = 取消【依据：04 §1.3 悬浮窗规则延伸】。

---

## 2. 书架 Bookshelf

### 2.1 区域职责

作品（Book）、章节（Chapter）、页面（Page）数据的浏览与管理入口；翻译约束（术语表/不译表）的维护入口；从章节跳转工作台/阅读器的导航起点【依据：01 §1「书架/数据管理」（B1–B4）、§3 层级 1/5；04 §4】。书架中的章节可跳转到工作台或阅读器，但不构成上下级关系【依据：01 §1 总览图注】。

### 2.2 布局结构

```text
┌──────────┬──────────────────────────────────────┬──────────────────┐
│ Nav Rail │ BookshelfToolbar (高 48)              │ BookDetailPanel  │
│  64px    │ [新建作品][导入作品][搜索框][收藏][归档]│  320px（可调      │
│          │ [排序][网格/列表视图切换]              │  240–420）       │
│          ├──────────────────────────────────────┤ 资料 / 标签 / 进度 │
│          │ BookGrid（网格）或 BookList（列表）     │ 收藏 / 归档状态   │
│          │ 主内容区，随窗口伸缩                    │ ChapterList      │
│          │                                      │ [进入翻译][进入阅读]│
└──────────┴──────────────────────────────────────┴──────────────────┘
```

- BookDetailPanel 为**右侧固定面板**（非弹窗）【依据：08 AC-WIN-001「Bookshelf BookDetailPanel 至少为固定区域」】；未选中作品时显示「未选择作品」空状态。
- 网格/列表双视图常驻，`viewMode` 决定可见性，切换不销毁数据【自有取值；形态参考 LEGACY [ui-baseline](../ui-baseline.md) §2，非绑定】。

### 2.3 组件分解

| 组件 | 职责 | 输入 | 输出 |
|---|---|---|---|
| BookshelfToolbar | 汇聚书架全部全局操作：新建作品、导入作品、搜索、收藏/归档过滤、排序、视图切换 | 本地过滤/排序/视图状态（UI-local） | 触发 NewBookDialog、ImportDialog；过滤条件供 BookGrid/BookList 消费 |
| BookGrid / BookList | 作品集合展示（网格 cell 或列表行）；点击卡片选中作品 | BookSummary[]（`ListBooks` 结果）+ 本地过滤/排序 | 选中 book_id → BookDetailPanel |
| BookCard（Grid 内） | 单作品卡片：标题、原名、收藏星、归档徽标、页数摘要（`page_count` 为 null 时显示「—」，**不得渲染为 0**） | BookSummary | 选中/收藏切换（收藏切换 wire 见 G3） |
| BookDetailPanel | 作品详情：中文名、原名、作者、出版社、系列、源/目标语言、标签、收藏/归档状态、章节列表、阅读摘要 | 选中 book_id；`ListChapters` 结果 | 进入翻译/进入阅读跳转；新建章节输入行 |
| ChapterList | 章节列表：编号、标题、类型（paged/webtoon）、方向、页数摘要；行操作「进入翻译 / 进入阅读」 | `ListChapters`（chapter_id, title, chapter_number, sort_order）+ `ListChapterPages`（页数统计可由 pages 长度得出） | 选中 chapter_id；跳转动作 |
| NewBookDialog | 新建作品表单（标题、原名、默认类型 paged/webtoon、默认方向 RTL/LTR/Vertical、源/目标语言、标签）【依据：04 §5】 | 表单输入 | 提交创建（wire 见 G1）；成功后刷新列表并选中新作品 |
| ImportDialog | 选择本地图片/文件夹/PDF → 确认重复策略（skip / import_as_new）→ 展示逐源/逐页 ImportReport 结果 | chapter_id（从 ChapterList 或新建章节流程进入） | 提交 `ImportPages`（sources 由 host 签发，见 G6）；展示报告 |
| EmptyStateBookshelf | 空库引导（「还没有作品」+ 新建作品可用 + 导入作品入口） | — | — |

搜索、收藏/归档过滤、排序、视图切换全部为 **UI-local** 操作【契约：M2-C1 §5.2「Bookshelf search/filter/sort/view mode」明确列为前端本地状态，不成为 Core command】。

### 2.4 状态矩阵

| 状态 | 触发 | 表现 |
|---|---|---|
| loading | 首次进入书架、`ListBooks`/`ListChapters` 请求进行中 | 主内容区骨架占位（卡片网格骨架）；Toolbar 操作中仅「新建作品」可用 |
| empty | `ListBooks` 成功且返回空数组（空库）；或过滤条件无命中 | EmptyStateBookshelf（空库：标题「还没有作品」+ 新建入口；过滤无命中：提示清空过滤） |
| error | `ListBooks`/`ListChapters` 返回错误 envelope（含 Core 不可用 `CORE_UNAVAILABLE`） | 主内容区错误卡：展示 `ErrorEnvelope.code` 对应的本地化短文案 + 「重试」按钮；不暴露路径/stack【契约：M2-C1 §8 message 安全约束】 |
| disabled | 无选中作品时 BookDetailPanel 动作（进入翻译/进入阅读）禁用；导入入口在未选中章节时禁用；无 wire 支撑的操作（收藏切换、删除、标签管理、约束维护）在实现 Task 中一律以禁用态 + tooltip「等待能力接入」呈现，**不得**假装可用【GAP-G3/G2/G7/G8】 | 灰置 + tooltip 说明 |
| progress | `ImportPages` 同步执行期间（该命令为同步 request/response，返回最终 ImportReport） | ImportDialog 内确定性 busy 态（进度条不定态 + 「正在导入…」）；**无细分进度事件**【契约：M2-C1 §6.2 `ImportProgressChanged` 明确保留 UNKNOWN/PROPOSAL，P12-C1 不冻结】→ 细分进度见 G26 |

### 2.5 交互清单

1. 点击 BookCard → BookDetailPanel 加载该作品详情 + 章节列表（`ListChapters`）。
2. 搜索/过滤/排序/视图切换 → UI-local 即时生效【契约：M2-C1 §5.2】。
3. 新建作品 → NewBookDialog → 【GAP-G1：CreateBook wire 未冻结】。
4. 导入页面 → ImportDialog：选来源（host 文件选择【GAP-G6】）→ 选重复策略（默认 skip【依据：P09 §「重复项策略」默认 SKIP；契约：M2-C1 §5.6 `duplicate_policy` 缺省 "skip"】）→ 提交 `ImportPages` → 逐源/逐页结果表（imported / skipped_duplicate / rejected / pending；仅显示 basename，不显示路径【契约：M2-C1 §5.6 source_name/filename 仅 basename】）。
5. ChapterList 行操作「进入翻译」→ 关闭书架内详情浮层（若有）→ 切换工作台并携带 book_id + chapter_id【依据：04 §15.1】。
6. ChapterList 行操作「进入阅读」→ 切换阅读器并携带 book_id + chapter_id【依据：04 §33.1】。
7. 收藏/归档切换【GAP-G3】、编辑作品信息【GAP-G1 并入】、删除作品/章节【GAP-G2】、标签管理【GAP-G7】、术语表/不译表维护【GAP-G8】、页序拖拽（在书架章节页管理语境）【GAP-G14】。
8. 阅读摘要（最近阅读章节、当前进度、最后阅读时间、累计时长）显示【依据：04 §4.2/§36】→ 数据面【GAP-G5】；无 wire 前显示「—」占位，不得虚构数值。

### 2.6 键盘与焦点路径

- `↑/↓` 在 BookGrid 卡片间移动选择（列表同理）；`Enter` 打开选中作品详情面板。
- BookDetailPanel 内 `Tab` 顺序：资料区 → 章节列表 → 动作按钮（进入翻译 → 进入阅读）。
- ChapterList `↑/↓` 移动、`Enter` 进入翻译（主操作）；「进入阅读」经 `Tab` 到达后 `Enter`。
- `Ctrl+F` 聚焦搜索框【自有取值】；`Esc` 清空搜索/关闭对话框（无未保存修改时）【依据：04 §1.3】。

---

## 3. 工作台 Workbench

### 3.1 区域职责

翻译处理流水线（导入 → 检测 → OCR → 配色 → 术语 → 翻译 → 分割 → Mask → 修复 → 渲染 → 保存）的操作面、人工校对编辑器（Region/文本/样式）、固定任务进度面板【依据：01 §1「工作台/翻译处理」、§4；04 §15–§32】。工作台从书架进入时携带 book_id + chapter_id；直接点击一级导航进入时，若存在有效最近工作上下文则恢复之，否则显示空状态并用固定选择区/悬浮窗选择作品章节，**不得跳转到新的选择页面**【依据：04 §15.2】。

### 3.2 布局结构

```text
┌──────────┬────────────┬──────────────────────────┬────────────────┐
│ Nav Rail │ PageList-  │ Viewer（主内容区，随窗口伸缩）│ RegionInspector │
│  64px    │ Panel      │  页图（resource channel）    │  320px（可调    │
│          │ 240px      │  RegionOverlay 叠加         │  240–420）     │
│          │（可调       │  缩放/平移（UI-local）        │ 类型/译文/历史   │
│          │ 200–320）  │                            │                │
│          ├────────────┴──────────────────────────┴────────────────┤
│          │ WorkbenchToolbar (高 44)：批处理命令 / 缩放 / 模式          │
│          ├────────────────────────────────────────────────────────┤
│          │ TaskProgressPanel（底部固定；展开 ≈220 / 折叠 44）          │
└──────────┴────────────────────────────────────────────────────────┘
```

- PageListPanel、Viewer、RegionInspector、TaskProgressPanel 均为**固定区域**，不得全部实现成弹窗【依据：08 AC-WIN-001】。
- TaskProgressPanel 固定底部、可折叠为紧凑进度条，不作为独立页面或临时弹窗【依据：01 §4；04 §30.3；08 AC-PROGRESS-001】。
- 上下文携带：进入工作台时以 React 路由/会话状态携带 book_id + chapter_id（UI-local）。

### 3.3 组件分解

| 组件 | 职责 | 输入 | 输出 |
|---|---|---|---|
| WorkbenchContextPicker | 无有效上下文时的作品/章节选择（固定选择区或悬浮窗，不跳页）【依据：04 §15.2】 | `ListBooks`、`ListChapters` | 设定工作台 book/chapter 上下文 |
| WorkbenchToolbar | 批处理命令入口（翻译/重渲染/重修复/重 OCR 的全部/选择页/单页【依据：04 §11】）、Viewer 模式切换（`setViewerMode` 为 UI-local）、导入入口 | 当前 PageList 选择集 | 发起 `StartRun`（command + scope 由选择集派生）；打开 ImportDialog |
| PageListPanel | 页导航列表：页序、文件名、综合状态（未处理/处理中/已完成/失败/跳过/已锁定）、当前页高亮；单选/Ctrl 多选/Shift 连续多选，多选仅限当前章节【依据：04 §10、§52】 | `ListChapterPages`（page_id, source_filename, sort_order）+ `GetTaskProjection` 的 `rows`（状态/锁定/当前页联动） | 选择集 → WorkbenchToolbar 命令的 scope；选中 page_id → Viewer |
| ViewerPanel | 页图显示：经资源通道加载（§6 大媒体行）；缩放/平移/翻页为 UI-local | page_id → `ResolvePageResource`（resource_id, revision）→ host `issue_resource_url`（opaque URL）→ m2res 分块拉取 | 显示；scroll/zoom 状态 |
| RegionOverlay | 页面上的 Region 边界叠加绘制（含 letterbox 数学：页面尺寸只从投影取——`ListRegions` 的 `page_size`）【契约：M2-C1 §5.4 `page_size` 投影；rev 1.5 geometry 归一化通道】 | `ListRegions`（RegionListSummary + geometry + page_size） | 选中 region_id → RegionInspector |
| RegionInspector | 右侧检查器：Region 类型（六值）、sfx_policy 快照、origin、当前 revision_no；类型改标入口；译文编辑区；Revision 历史（摘要/current/pinned/source）；恢复入口 | `ListRegions`、`ListRegionRevisions` | `SetRegionType`（改标）、`RestoreRegionRevision`（恢复）、译文保存（【GAP-G9】） |
| RelabelContextMenu / RelabelConfirmDialog | 改标的右键菜单 + 确认；改标后 10 秒撤销窗口（撤销 = 恢复源 revision，不做「反向改标」）【契约：M2-RC4 §应用与 UI 约束 4】 | `SetRegionType` 结果（revision_no） | `RestoreRegionRevision`（undo 路径） |
| TaskProgressPanel | 固定进度面板（详见 3.5） | `GetTaskProjection` + 事件 | Run 控制动作（pause/stop/continue 等） |
| TaskDetailPopover | 任务详情（悬浮窗，非独立页面）：命令类型、Book/Chapter、页面范围、当前进度、当前 Step、Provider、Model、Device、错误、重试次数、运行时间【依据：04 §31】 | `GetTaskProjection` 的 tasks/steps 明细 | — |
| ExportDialog | 导出：选范围（章节/页）、格式 png/zip/cbz/pdf/text、格式选项、stale 策略、目标位置（host 签发 ExportTargetRef【GAP-G19】）、进度与历史 | `StartExport`/`CancelExport`/`GetExportSnapshot`/`GetExportHistory` | 导出任务提交/取消；历史列表 |
| EmptyStateWorkbench | 未选择作品/章节时的空状态 + 选择入口【依据：04 §15.2】 | — | — |

页选择、步进、范围选择、过滤、定位、模式切换、Inspector 文本编辑态、Region 选择等全部为 UI-local【契约：M2-C1 §5.2 明确列举】。

### 3.4 状态矩阵

| 状态 | 触发 | 表现 |
|---|---|---|
| loading | 进入章节时 `ListChapterPages`/`ListRegions`/首次 `GetTaskProjection` 进行中；Viewer 资源分块拉取中 | PageList 骨架行；Viewer 居中加载指示（含已拉取块数/总块数，`size` 可得时） |
| empty | 章节 `ListChapterPages` 返回空数组（未导入页面）→ 引导导入；`ListRegions` 空（无存活 Region，含 page 未命中 → `page_size: null`）→ Overlay 提示「本页暂无 Region」 | 空状态卡 + 主行动作（导入/开始翻译） |
| error | 命令返回错误 envelope；资源通道 `REF_*` 类型化拒绝；`rerender_page` 的 MISSING_REQUIRED_INPUT 等 | 就地错误条：code 本地化文案 + 可重试动作（`retryable=true` 时）【契约：M2-C1 §8；rerender_page 错误面见 M2-RC4】；Core 不可用时全区块降级为错误卡 |
| disabled | 无 Run 时 TaskProgressPanel 控制钮全禁用；`controls` 为 false 的动作禁用（矩阵见 3.5）；无 wire 的编辑动作（新建/删除 Region、保存译文、Lock、pin、拖拽排序、删除页）禁用 + tooltip「等待能力接入」【GAP-G9/G10/G11/G12/G13/G14】 | 灰置；禁用原因 tooltip |
| progress | Run 运行中：整体进度、页状态、Step 流向（TaskProgressPanel 缩略图缺口见 G18） | TaskProgressPanel 展开态全量信息；折叠态保留任务名/百分比/当前页/当前 Step/控制钮（按状态启用）【依据：04 §30.3 折叠态要求】 |

### 3.5 TaskProgressPanel（固定面板，冻结）

**展示**【依据：01 §4；04 §30.3；08 AC-PROGRESS-002，逐项覆盖】：

- 当前任务名（run_title）与处理范围；总体进度百分比（`overall_progress`）；
- 完整流程节点条（`step_flow`：type/label/state，当前 Step 高亮）；
- 当前页（`current_page_id` 对应页序/文件名；缩略图【GAP-G18】）；
- 统计：已完成 / 失败 / 跳过 / 等待 / 阻塞（`counts`）+ 阻塞原因列表（`blocked_reasons`）；
- 控制：暂停 / 停止 / 继续，按 `controls.{can_pause, can_stop, can_continue, can_restart, can_abandon, can_retry_failed}` 启用【契约：M2-C1 §6.1 TaskProjection DTO；controls 只提示可用性，Core 在命令边界重验】。

**控制动作 → wire 映射**（完整合法矩阵以契约为准，UI 不自行放宽）：

| UI 动作 | wire | 合法状态（摘） |
|---|---|---|
| 暂停 | `ControlRun(action=pause)` | Running【契约：M2-C1 §5.5 状态矩阵】 |
| 继续 | `ControlRun(action=continue)` | Paused；Interrupted（同 Run 恢复） |
| 停止 | `ControlRun(action=stop)` | Pending/Running/Paused/Blocked |
| 重启 | `ControlRun(action=restart)`（必带 idempotency_key） | Interrupted 无处置 |
| 放弃 | `ControlRun(action=abandon)` | Interrupted 无处置 |
| 重试失败页 | `RetryFailedTargets`（必带 idempotency_key） | CompletedWithFailures 且有失败页 |
| 解除阻塞 | `ResumeBlockedRun` | Blocked |

- 暂停/停止请求后 **≤ 200ms** 显示「正在暂停/正在停止」中间态，实际 Paused 以 `RunPaused` 事件 + 快照为准，不提前显示【依据：07 §54；08 AC-PAUSE-001；契约：P11 §4.3「UI 可显示正在暂停，不得提前显示 Paused」】。
- 批量任务 38 成功 2 失败 → 显示「已完成（有失败）」（completed_with_failures），不整体标失败【依据：04 §30.3；08 AC-PROGRESS-006】。
- 点击统计项（已完成/失败/跳过）→ PageList 筛选对应集合；点击「当前页」→ PageList 滚动定位并选中【依据：04 §30.3 页面统计交互；08 AC-PROGRESS-003/004/005】。筛选为 UI-local（`filterByStatus`）【契约：M2-C1 §5.2】。
- PageList 状态与 TaskProgressPanel 同源：同一 `GetTaskProjection` 的 `rows`，不得另查第二份状态【依据：08 AC-PROGRESS-007；契约：M2-C1 §5.5「PageList 不得另行查询或重算另一份状态」】。
- 刷新节流：普通百分比 ≤ 4 Hz（250ms 合并刷新）；TaskFailed / RunPaused / RunCompleted / CurrentPageStepChanged 四类事件即时处理【契约：M2-C1 §6.2 + P11 §7.3；依据：07 §6、08 AC-NFR-UI-002】。事件仅作失效提示，收到后重新查询 `GetTaskProjection`【契约：M2-C1 §6.2「Event 是提示与失效通知，不是状态真值」】。
- **Run 发起**：批处理命令统一经 `StartRun`（command ∈ PipelineCommand 枚举 18 值；scope 按选择集派生 book/chapter/page_selection/page/region；**必带调用方生成的 idempotency_key**）【契约：M2-C1 §5.5 + §5.1 PipelineCommand/PipelineScope】。UI 对用户重复点击以同键重放（超时/响应丢失场景），不做 UI 侧去重语义。

### 3.6 交互清单

1. 选择页/多选（Ctrl/Shift，仅当前章节）→ 工具栏批处理命令【依据：04 §10；UI-local】。
2. 批处理命令（全部翻译 / 全部翻译（跳过已翻译）/ 选择页翻译 / 单页翻译 / 全部·选择页·单页重新渲染 / 重新修复 / 重新 OCR / 单 Region 重全翻译）→ `StartRun`【依据：04 §11；契约：M2-C1 §5.1 命令枚举含 translate_all…rerender_region 全部 18 值】。
3. 页图加载：`ListChapterPages` 选中页 → `ResolvePageResource`（确定性资源键）→ host `issue_resource_url` → m2res 分块（≤16MiB/块）拉取渲染【契约：M2-C1 §5 `ResolvePageResource` 行（rev 1.7）；§10.1/§10.2 资源通道；RC-4 §3 preview 先例】。
4. Region 叠加与选中：`ListRegions`（geometry 归一化 + page_size letterbox）→ 点击选中 → Inspector【契约：M2-C1 §5.4】。
5. 类型改标：右键 Region → 菜单六值 → 确认对话框（说明 EV-8 语义：改标为 sfx 按当前全局配置重快照；非 sfx 强制 skip）→ `SetRegionType`（携带 expected_revision 乐观守卫）→ 结果条直接显示生效态（region_type/sfx_policy/revision_no，一次往返，无需二次查询）→ 10 秒撤销窗口（撤销经 `RestoreRegionRevision`）【契约：M2-C1 §5.4；M2-RC4 §应用与 UI 约束 4/5】。
6. Revision 历史：Inspector 常驻历史入口（`ListRegionRevisions` 摘要：origin/review_state/is_pinned/current）→ 显式确认恢复（确认文案必须说明恢复历史文字、类型、策略**及锁状态可能回退**）→ `RestoreRegionRevision`【契约：M2-RC4 §命令与 DTO restore 行 + §应用与 UI 约束 5】。
7. 本页重渲染：`rerender_page` → 成功后以 preview 资源刷新 Viewer（`loadPageImageUrl` 同型通道）；preview 失败（preview_error=PREVIEW_UNAVAILABLE）时已提交结果保留、明示「预览不可用，可重试」，**不伪报渲染失败**【契约：M2-RC4 §rerender_page 行】。
8. 保存人工译文（Inspector 文本区 + Dirty 确认 `resolveDirtyConfirm`）→【GAP-G9：SaveManualTranslation 未冻结】。
9. 新建/删除/移动/缩放/polygon/合并/拆分/reading_order 调整【依据：04 §18】→【GAP-G10/G11】。
10. Lock 设置/解除（Page/Region/Translation/Inpaint）【依据：04 §28；08 AC-LOCK-001..005】→【GAP-G12】。
11. Revision pin【依据：08 AC-REV-003】→【GAP-G13】。
12. 页序拖拽排序【依据：04 §10；AC-PAGE-001 sort_order 人工重排】→【GAP-G14】。
13. 导入页面（同书架 §2.5-4，入口重复于工具栏）。
14. 导出（ExportDialog，见 §6 导出行）。
15. 中断恢复：应用重启后存在 Interrupted Run 时，工作台进入即呈现处置选择（继续/重启/放弃），数据来源【GAP-G15：Run 发现/列表 wire 未冻结；04 §30.2 要求该体验】。
16. 双屏悬浮窗（辅助 Non-modal 窗口可在处理工作台时持续显示）【依据：04 §46】——形态自由，不冻结具体窗口。

### 3.7 键盘与焦点路径

- `↑/↓` PageList 移动；`Ctrl+Click`/`Shift+Click` 多选【依据：04 §10】；`Enter` 在 Viewer 打开选中页。
- Viewer：`+/-` 缩放、`0` 适配宽度、`空格` 按住临时平移（拖拽模式切换 `V` 平移 / `R` Region 选择模式）【自有取值】。
- RegionOverlay：`Tab` 在页内 Region 间按 reading_order 循环（方向 `Shift+Tab` 反向）；`Enter` 选中进 Inspector。
- Inspector：`Ctrl+Enter` 提交译文（有 Dirty 确认流程【依据：04 §45；UI-local `resolveDirtyConfirm`】）。
- TaskProgressPanel：`Ctrl+P` 暂停/继续切换、`Ctrl+.` 停止【自有取值；仅在 controls 允许时生效】。
- 导出/导入对话框内 `Esc` = 取消（无未保存修改时）【依据：04 §1.3】。

---

## 4. 阅读器 Reader

### 4.1 区域职责

阅读成果：Original / Translated 两模式查看分页漫画（RTL/LTR）与 Webtoon 条漫（垂直滚动），按模式独立保存阅读进度【依据：01 §1「阅读/成果查看」；04 §33–§36；08 AC-READ-001..005】。

### 4.2 布局结构

```text
┌──────────┬────────────────────────────────────────────────────┐
│ Nav Rail │ ReaderToolbar (高 48)：章节标题 · 模式切换 Original/  │
│  64px    │ Translated · 位置（x/y 或百分比） · resume/beginning │
│          ├────────────────────────────────────────────────────┤
│          │ 阅读视口（主内容区，随窗口伸缩）                       │
│          │  paged: 单页/横向页序列（RTL 或 LTR 方向语义）          │
│          │  webtoon_vertical: 宽度自适应、纵向滚动单逻辑 Page     │
└──────────┴────────────────────────────────────────────────────┘
```

阅读器进入：从书架章节「进入阅读」携带 book_id + chapter_id【依据：04 §33.1】；从工作台保存后「查看结果」进入【依据：04 §33.2】。阅读器空状态（无章节上下文）：「尚未选择阅读章节」+ 选择入口（固定选择区或悬浮窗，不跳页；与工作台 §3.1 同规则）【依据：04 §15.2 同语义延伸；空状态文案为自有取值】。

### 4.3 组件分解

| 组件 | 职责 | 输入 | 输出 |
|---|---|---|---|
| ReaderToolbar | 章节/模式/位置显示与控制；进入时的位置选择（从上次位置继续 / 从章节开头开始） | ReaderProjection（layout、saved_progress） | 模式切换（UI-local display mode）；触发 `GetReaderProjection`（start_position=resume/beginning） |
| PagedReaderView | 分页视口：按 `layout: rtl|ltr` 呈现方向语义；页间导航 UI-local | `ReaderProjection.pages`（page_id/order/width_px/height_px/original/translated 引用） | 当前 page_id；进度保存触发 |
| WebtoonReaderView | 垂直滚动视口：宽度自适应（以条漫宽度为基准，高度自然延伸）【依据：04 §9.2/§35】；一张长图 = 恰一个逻辑 Page，临时切片永不出现在阅读序列 | 同上（该章恰一页）；scroll_offset_y（源图像素坐标） | 滚动位置；节流保存触发 |
| ReaderPageImage | 页图加载：resource_ref（original/translated）→ host issue → m2res 分块拉取 | ReaderPageProjection 的 resource_ref | 渲染位图 |
| ReaderProgressSaver | 进度保存：位置变化节流（500–1000ms debounce）+ 退出/切章时即时保存；累计 elapsed_seconds_delta 由调用方计时，**不重发已接受区间** | 当前 (page_id, scroll_offset_y, 计时) | `SaveReadingProgress` |
| ReaderEmptyState | 无章节上下文空状态 | — | — |

翻页（nextPage/previousPage/jumpToPage）、显示模式切换为 UI-local【契约：M2-C1 §5.2「Reader nextPage, previousPage, jumpToPage, display mode」】。Original 与 Translated 是**独立进度键**，切换模式重新投影【契约：M2-C1 §6.3（book_id, chapter_id, mode) 独立保存】。

### 4.4 状态矩阵

| 状态 | 触发 | 表现 |
|---|---|---|
| loading | `GetReaderProjection` 进行中；页图分块拉取中 | 视口骨架/加载指示（块进度） |
| empty | 无章节上下文（空状态）；章内 pages 为空 | ReaderEmptyState + 选择入口 |
| error | 投影/资源/保存命令错误 envelope（含 EXPORT 类无关错误不在此列）；translated 引用为 null 时的处理见下 | 错误卡 + 重试；`SaveReadingProgress` 拒绝（页不在章内/非法偏移）时回读快照纠偏并提示 |
| disabled | translated 模式下某页 `translated.resource_ref = null`（该页无译图）：该页显示原文 + 「未翻译」角标，**不得以路径或伪造引用替代**【契约：M2-C1 §6.3「missing translated artifact 由 null 字段表示」】；stale 指示（rendered_from_revision_id ≠ current_source_revision_id）显示「译文可能过期」角标，契约不规定回退 UI【契约：M2-C1 §6.3「不指定 Reader fallback UI」】 | 角标 + tooltip |
| progress | 大图分块加载（Webtoon 长图） | 渐进显示（已拉取块先行渲染）；滚动位置恢复指示 |

### 4.5 交互清单

1. 进入章节（resume）→ 从保存位置继续；「从开头开始」→ beginning（不改写 saved_progress）【契约：M2-C1 §6.3 start_position 语义】。
2. 分页导航：方向键/点击翻页按 layout 方向语义（rtl：下一页在左）【依据：04 §34；契约：§6.3 layout 语义】。
3. Webtoon：纵向滚动、宽度自适应、不允许按固定页高缩放【依据：04 §35】；滚动位置定期保存（源图像素坐标，视图做显示坐标 ↔ 源坐标映射）【契约：M2-C1 §6.3 webtoon 坐标语义】。
4. 模式切换 Original/Translated：独立进度，切换后重新投影到各自保存位置。
5. 进度保存：节流 + 退出保存；收到 `ReadingProgressChanged` 事件（失效提示）→ 重新读取投影【契约：M2-C1 §6.2/§6.3】。
6. 返回书架选择下一章节（「继续下一章节」经书架，不设跨章自动续读）【依据：04 §2 主流程 END → LIB】。

### 4.6 键盘与焦点路径

- 分页：`←/→`（按 layout 反转语义：rtl 时 `→` = 上一页）、`PageUp/PageDown`、`Home/End` 首/末页【自有取值；方向语义依据 04 §34】。
- Webtoon：`↑/↓`/`PageUp/PageDown` 滚动、`Home/End` 顶/底。
- `O/T` 或 `Ctrl+T` 切换 Original/Translated【自有取值】。
- `Esc` 返回书架（阅读器无未保存表单概念；进度已节流保存）。

---

## 5. 设置 Settings

### 5.1 区域职责

全局配置管理：Provider、网络/代理、OCR、翻译、图片修复、排版样式、模型/GPU、任务/并发、缓存/Revision、回收站、备份/恢复、Plugin/Hooks 十二分区【依据：04 §38】。设置是一级页面；Core 是设置语义权威，Tauri 只转发，React 不解释业务值【契约：M2-C1 §5.3】。

### 5.2 布局结构

```text
┌──────────┬──────────────────┬──────────────────────────────────┐
│ Nav Rail │ SettingsCategoryNav│ SettingsContentPanel（主内容区）    │
│  64px    │ 200px 固定        │  左分类右内容；无子路由             │
│          │ 12 分类，顺序固定   │  分类间切换 = React 本地状态         │
└──────────┴──────────────────┴──────────────────────────────────┘
```

分类顺序固定：Provider、网络/代理、OCR、翻译、图片修复、排版样式、模型/GPU、任务/并发、缓存/Revision、回收站、备份/恢复、Plugin/Hooks【依据：04 §38；08 AC-DOC-003 四页一致；导航宽度为自有取值】。分类导航为固定区域【依据：08 AC-WIN-001「Settings 分类导航」】。

### 5.3 组件分解与数据面

| 组件 | 职责 | 数据面 |
|---|---|---|
| SettingsCategoryNav | 十二分类导航，选中态本地状态 | UI-local |
| SettingsContentPanel | 当前分类表单渲染 + 保存反馈 | `settings_get`（全量或单节）/ `settings_update_section`（整节 upsert，成功一次往返返回最新全量）【契约：M2-C1 §5.3】 |
| SfxPolicyControl | SFX 策略三值单选（skip 默认 / translate / manual）——**当前唯一有写入校验实例的节** | `settings_get`（sfx 节）+ `settings_update_section("sfx", {"policy": …})`；非法值 Core typed fail-closed 拒绝（INVALID_REQUEST/validation）【契约：M2-C1 §5.3 写入端校验 3】 |
| ProviderProfilePanel | Provider Profile 列表/新建/编辑（能力、endpoint/model、CredentialRef 状态、Network Profile 选择、连接测试、多 Profile 同 Provider）【依据：04 §39；P10 §5】 | 【GAP-G21：Profile CRUD/绑定 wire 未冻结】 |
| CredentialField | 凭据输入：只显示「已配置/缺失」+ 允许 masked hint，**永不回显明文**；提交后不可读回【契约：P10 §3.4/§9】 | 【GAP-G22：CredentialRef 专用操作 wire 未冻结】 |
| NetworkProfilePanel | Network Profile 管理（Direct/System/HTTP/HTTPS/SOCKS5）+ 分阶段连接测试（代理→DNS→TCP→TLS→HTTP→Provider Auth，未执行阶段明确标记，失败保留阶段；代理失败默认不静默直连）【依据：04 §41；P10 §6】 | 【GAP-G23：Network Profile/连接测试 wire 未冻结】 |
| OverrideSummaryPanel | 设置覆盖链（全局→作品→章节→当前任务）与有效值来源显示【依据：04 §42；P10 §5】 | 【GAP-G24：范围解析查询 wire 未冻结】 |
| RecycleBinPanel | 回收站管理（恢复/永久删除/自动清理策略）【依据：04 §43】 | 【GAP-G2：软删/回收站 wire 未冻结】 |

**Secret 边界（UI 侧冻结）**：任何设置界面不得把 Secret 写入/读自普通 settings DTO；错误与日志显示走脱敏类别文案（稳定错误类别 + 失败阶段 + 可采取动作，不含原始响应/认证头）；TLS 校验关闭必须经明确危险确认且状态可见【契约：P10 §4 全部 MUST/MUST NOT 条款对 UI 生效；依据：08 AC-SEC-002/004/005】。

### 5.4 状态矩阵

| 状态 | 触发 | 表现 |
|---|---|---|
| loading | `settings_get` 进行中 | 表单骨架 |
| empty | 某节未设置（返回 JSON null） | 该节显示「未设置」占位（null 与空对象可区分【契约：M2-C1 §5.3 frozen-None 通道】），提供默认值填充动作 |
| error | 读取/保存错误 envelope（INVALID_REQUEST=validation 时高亮对应字段；UNKNOWN=internal；CORE_UNAVAILABLE 通道失败） | 就地错误条 + code 本地化文案；保存失败时表单保持用户输入不丢失 |
| disabled | 无 wire 的分区（Provider/网络/覆盖/回收站/备份/Plugin 等全部控件）禁用 + tooltip「等待能力接入」，分类可见但内容为占位说明【GAP-G2/G21/G22/G23/G24】 | 灰置分区 |
| progress | 保存请求进行中（upsert 单次往返） | 保存按钮 busy 态（通常 <300ms，按 07 §4 即时反馈） |

### 5.5 交互清单

1. 切换分类（本地状态，无路由）。
2. 修改 SFX 策略 → 即时保存（三值单选）→ 成功反馈条显示生效值；失败显示 typed 错误。
3. 修改其他已开放节键 → 「保存」按钮整节提交（`settings_update_section` 整节替换语义，UI 需在提交前明示整节替换影响——以当前面板已知键合并后提交）。
4. Provider Profile 新建/编辑/启用、连接测试【GAP-G21/G23】。
5. 凭据新增/替换/清除（专用操作、无明文回显）【GAP-G22】。
6. 危险确认：关闭 TLS 校验、永久删除类动作【依据：04 §1.3；P10 §4】。

### 5.6 键盘与焦点路径

- `↑/↓` 分类导航移动；`Enter` 进入分类。
- 表单内标准 Tab 流；`Ctrl+S` 保存当前分类【自有取值】。
- 危险确认：`Enter` 不绑定主 destructive 按钮（须显式点击或 Tab 到达后确认），`Esc` 取消【自有取值；延伸 04 §1.3「危险操作必须通过明确按钮确认」】。

---

## 6. 契约绑定表

下表把**每个需要数据的 UI 元素**绑定到**已冻结**的命令/事件。引用格式：`文件 §章节 / 行号`（行号为基线 commit `c6f975d38` 时的实际行，仅供人读辅助；机器核验以名字逐字检索为准，见 `verification/UI-DESIGN-1/selfcheck.ps1`）。**命令名给 transport-neutral 契约名（PascalCase）或已冻结 wire 名（snake_case），与契约文本逐字一致**；各命令的产品 Tauri command 名（如既有 `library_list_books`、`settings_get`）以契约已裁决者为限，其余由实现 Task 按 §11 既有纪律冻结。

「资源通道」行说明：页图/预览字节不经 JSON IPC，经 host 签发的 opaque URL + 分块拉取（既有实现 `apps/desktop/frontend/src/resourceChannel/client.ts`，Tauri 命令 `issue_resource_url` / `revoke_ref` 为既有实现事实，非契约文本引用对象），契约依据为 §10.1/§10.2 的 RULED 条款与 RC-4 §3 的 preview 先例。

| # | 页面 | UI 元素 / 交互 | 绑定命令 / 事件（已冻结） | 契约引用（文件 + 章节/行） |
|---|---|---|---|---|
| W1 | Shell/书架 | 作品列表（卡片/列表数据） | `ListBooks`（BookSummary.page_count: int\|null；null 渲染「—」） | M2-C1 §5 表 `ListBooks` 行（行 139；`1.2` 修订见 Revision history） |
| W2 | 书架/工作台 | 章节导航列表（编号/标题/排序） | `list_chapters` | M2-C1 §5 表冻结行（行 159；rev 1.8，§5 表 `ListChapters` 冻结行） |
| W3 | 书架/工作台 | 页导航列表（页序/文件名/排序） | `list_chapter_pages` | M2-C1 §5 表冻结行（行 160；rev 1.8） |
| W4 | 书架/工作台 | 导入页面（选来源+重复策略→报告） | `ImportPages`（ImportReport 逐源/逐页） | M2-C1 §5 表（行 143）+ §5.6（行 314–380）；来源范围/重复语义另见 P09 §首发范围/重复项策略（P09 行 5–11、29–31） |
| W5 | 工作台 | Viewer 页图（原图字节获取） | `ResolvePageResource`（wire `resolve_page_resource`）→ 资源通道 | M2-C1 §5 表（行 158；rev 1.7）；通道条款 §10.1（行 780–797）、§10.2（行 799–807）；RC-4 §应用与 UI 约束 3（preview 发布先例） |
| W6 | 工作台 | RegionOverlay 叠加 | `ListRegions`（wire `list_regions`；RegionListSummary + 可选 geometry + page_size） | M2-C1 §5 表（行 152）+ §5.4 读取面（行 261–279；rev 1.4/1.5） |
| W7 | 工作台 | 类型改标（含确认/撤销） | `SetRegionType`（wire `set_region_type`；expected_revision 乐观守卫；EV-8 policy 重快照） | M2-C1 §5 表（行 151）+ §5.4（行 254–260） |
| W8 | 工作台 | Revision 历史摘要 | `list_region_revisions` | M2-RC4 §命令与 DTO（行 9）；M2-C1 §5 表 `ListRegionRevisions` 行（行 156） |
| W9 | 工作台 | 恢复历史 Revision（改标撤销同路径） | `restore_region_revision`（expected_revision 必填；恢复含锁状态回退，确认文案必须说明） | M2-RC4 §命令与 DTO（行 10）+ §应用与 UI 约束 1/5（行 15、20）；M2-C1 §5 表（行 156） |
| W10 | 工作台 | 本页重渲染 + 预览 | `rerender_page`（preview resource 或 PREVIEW_UNAVAILABLE） | M2-RC4 §命令与 DTO（行 11）；M2-C1 §5 表 `RerenderPage` 行（行 161） |
| W11 | 工作台 | 批处理命令发起（18 值 PipelineCommand × 5 种 scope） | `StartRun`（必带 idempotency_key） | M2-C1 §5.5 表（行 176）+ §5.1 枚举（行 216–230）+ §5 表 `StartRun` 行（行 145） |
| W12 | 工作台 | 暂停/停止/继续/重启/放弃 | `ControlRun`（restart 必带 idempotency_key；合法状态矩阵） | M2-C1 §5.5 表（行 177）+ 状态矩阵（行 193–210）+ §5 表（行 148） |
| W13 | 工作台 | 解除阻塞恢复 | `ResumeBlockedRun` | M2-C1 §5.5 表（行 178）+ §5 表（行 149） |
| W14 | 工作台 | Run 快照（接受目标/状态） | `GetRunSnapshot` | M2-C1 §5.5 表（行 179）+ §5 表（行 146） |
| W15 | 工作台 | TaskProgressPanel / PageList 状态 / 任务详情（tasks/steps/Provider/Model/Device/错误/重试） | `GetTaskProjection`（TaskProjection DTO：counts/controls/rows/tasks/steps） | M2-C1 §5.5 表（行 180）+ §6.1（行 485–544）+ §5 表（行 147）；行为来源 P11 §7.2（行 202–206） |
| W16 | 工作台 | 失败页重试 | `RetryFailedTargets`（必带 idempotency_key） | M2-C1 §5.5 表（行 181）+ §5 表（行 150） |
| W17 | 工作台 | Run 重要状态即时刷新（4 类事件；节流 4Hz + 事件即时） | `TaskFailed`、`RunPaused`、`RunCompleted`、`CurrentPageStepChanged` | M2-C1 §6.2 事件表（行 556–559）；P11 §7.3（行 208–210） |
| W18 | 阅读器 | 章节阅读投影（布局/页序列/进度/初始位置） | `GetReaderProjection` | M2-C1 §5 表（行 162）+ §6.3（行 571–618） |
| W19 | 阅读器 | 阅读进度保存（独立模式键；Webtoon 源像素坐标；elapsed_seconds_delta 不重发） | `SaveReadingProgress` | M2-C1 §5 表（行 163）+ §6.3（行 620–621） |
| W20 | 阅读器 | 进度失效重查 | `ReadingProgressChanged` | M2-C1 §6.2 事件表（行 563） |
| W21 | 工作台 | 导出提交（格式/顺序/stale 策略/目标引用） | `StartExport`（ExportTargetRef 为 host 签发一次性写授权，WebView 不接触） | M2-C1 §5 表（行 165）+ §6.3 Export 段（行 623–691）+ §10.3（行 809–819） |
| W22 | 工作台 | 导出取消 | `CancelExport` | M2-C1 §5 表（行 166）+ §6.3（行 691） |
| W23 | 工作台 | 导出进度/终态查询 | `GetExportSnapshot` | M2-C1 §5 表（行 167）+ §6.3（行 657–668） |
| W24 | 工作台 | 导出历史（状态；输出路径仅 host 可见） | `GetExportHistory`（只供可信 Tauri host；host 不向 WebView 转发路径） | M2-C1 §5 表（行 168）+ §6.3（行 669–682、689） |
| W25 | 工作台 | 导出进度失效重查 | `ExportProgressChanged` | M2-C1 §6.2 事件表（行 562） |
| W26 | 设置 | 设置读取（全量/单节；null=未设置） | `settings_get` | M2-C1 §5.3（行 236–248；读取语义行 240） |
| W27 | 设置 | 设置保存（整节 upsert；sfx.policy 三值 fail-closed 校验） | `settings_update_section` | M2-C1 §5.3（行 241–247） |
| W28 | 全部页 | 错误呈现（code/category/retryable 分支，不按 message 文本分支） | §8 `ErrorEnvelope` 语义 | M2-C1 §8（行 721–745） |
| W29 | 全部页 | UI-local 交互边界（选择/过滤/排序/翻页/模式等不成为 Core command） | §5.2 UI-local actions 清单 | M2-C1 §5.2（行 234） |

**未列入本表且未列入 §7 缺口表的交互不存在**——实现 Task 不得为本表之外的交互发明数据来源，也不得以 §7 缺口交互为由扩围实现。

---

## 7. Wire Gap List

第 6 节无法映射到已冻结 wire 的交互**全部**登记如下。处置纪律：缺口只能由 Coordinator 规划契约/host Task 消解；设计与其实现 Task **不得**以 mock、私有路径、绕过 Tauri IPC 或「假装可用」的方式消解（对应控件一律按 §2.4/§3.4/§5.4 disabled 态呈现）。

| # | 页面 | 交互 | 期望语义 | 当前缺口 | 建议后续动作 |
|---|---|---|---|---|---|
| G1 | 书架 | 新建作品 / 编辑作品信息 | 表单创建 Book（title、original_title?、默认类型/方向/语言）；编辑回写 | `CreateBook` 在 M2-C1 §5 表为 PROPOSAL，未冻结 wire；编辑无任何命令行 | 契约 Task：冻结 CreateBook（及编辑面），含校验与 BookSummary 返回 |
| G2 | 书架/设置 | 删除作品/章节/页 + 回收站（软删、恢复同批、永久删除、自动清理策略）【依据：04 §43】 | 软删除进回收站、保留 Managed Copy、可恢复/永久删除（不删用户源文件） | `DeleteBook`/`DeleteChapter` 为 PROPOSAL；回收站（RecycleBinEntry）无任何 wire | 契约 Task：冻结软删/回收站/永久删除面（含 P09 孤儿 GC 与 Managed Copy 语义） |
| G3 | 书架 | 收藏 / 归档切换 | 切换 BookSummary 收藏/归档状态并即时反映 | `SetBookFavorite`/`SetBookArchived` 为 PROPOSAL | 契约 Task：冻结两写命令 |
| G4 | 书架 | 新建 / 删除章节 | 章节标题/编号/类型/方向创建；删除走回收站 | `CreateChapter`/`DeleteChapter` 为 PROPOSAL | 契约 Task：冻结（与 G2 回收站联动） |
| G5 | 书架 | 作品详情阅读摘要（最近阅读章节/当前进度/最后阅读时间/累计时长）【依据：04 §4.2、§36】 | Book 级聚合阅读摘要 | `ListBooks` 的 BookSummary 无这些字段；`ReadingProgressSnapshot` 是单章 wire，无 book 级聚合查询 | 契约 Task：评估 BookSummary 扩容或新增 book 阅读摘要查询；此前 UI 显示「—」占位 |
| G6 | 书架/工作台 | 导入来源选择（文件/文件夹/PDF 选择器 → ImportSourceRef） | 用户显式选择来源 → host 签发只读引用 → `ImportPages` | `ImportSourceRef`/HostControl 已冻结，但 **HostControl 明确不得由 React/WebView 调用**（M2-C1 §5.7）；「选择来源并返回 ref」的产品 Tauri command 面未冻结 | host 侧 Task：冻结文件选择 + RegisterImportSource 的 WebView 可触发 Tauri command（P12 前置） |
| G7 | 书架 | 标签管理（新增/重命名/删除/挂接）【依据：04 §6；AC-LIB-002】 | 自由标签 CRUD 与 Book 关联 | 无任何 tag wire | 契约 Task：冻结标签面 |
| G8 | 书架 | 翻译约束维护（术语表/不译表）【依据：01 §1 B4】 | 作品级约束表人工维护 | 无任何约束表 wire | 契约 Task：冻结约束表面 |
| G9 | 工作台 | 保存人工译文（Inspector 文本区） | 保存 text，含 expected_revision 乐观守卫 | `SaveManualTranslation` 为 PROPOSAL（精确并发策略 UNKNOWN；§5.4 已给同型语义模式） | 契约 Task：冻结（按 §5.4 交叉指针语义） |
| G10 | 工作台 | 新建 / 删除 Region | 手工框选（矩形两点/polygon ≥3 点，归一化）创建；删除 | `CreateRegion`/`DeleteRegion` 为 PROPOSAL（几何校验规则已在 §9 冻结） | 契约 Task：冻结两命令（payload 形状 §5 表已具雏形） |
| G11 | 工作台 | Region 几何编辑（移动/缩放/polygon/合并/拆分/reading_order）【依据：04 §18】 | 几何写回产生新 revision | 无几何/顺序写命令冻结 | 契约 Task：冻结几何与顺序写面 |
| G12 | 工作台 | Lock 设置/解除（Page/Region/Translation/Inpaint）【依据：04 §28；AC-LOCK-001..005】 | 显式锁定/解锁，写入受 Core 守卫 | 无任何 lock 写命令冻结（RC-4 明确不新增 pin/lock 写） | 契约 Task：冻结 lock 写面 |
| G13 | 工作台 | Revision pin / 取消 pin【依据：AC-REV-003】 | 标记/解除 pinned revision | `SetRevisionPinned` 为 PROPOSAL；RC-4 明确不新增 | 未来契约修订 |
| G14 | 工作台/书架 | 页序拖拽重排（人工只改 sort_order，不改 source_order）【依据：04 §8、§10；P09 §记录与排序】 | 拖拽提交新 sort_order | 无 sort_order 写命令 | 契约 Task：冻结页序写面 |
| G15 | 工作台 | Run 发现 / 任务队列列表 / 中断恢复提示【依据：04 §30.2、§15.2】 | 启动后发现 Interrupted Run 并呈现继续/重启/放弃；恢复最近工作上下文 | `GetRunSnapshot` 需已知 run_id；无 ListRuns/活动 Run 查询 wire；NavBadge（§1.1）同源依赖 | 契约 Task：冻结 Run 列表/活动 Run 查询（含 interrupted 处置所需数据） |
| G16 | 全局 | Core 可用性指示（启动握手、Core 崩溃/重启提示）【依据：04 §3；07 §54 语境】 | UI 呈现 Core starting/ready/unavailable | `CoreAvailabilityChanged` 为 UNKNOWN/PROPOSAL（M2-C1 §6.2）；`core_ping` 为 M2 探针实现事实、非契约冻结面 | 契约 Task：冻结可用性事件或产品级可用性查询 |
| G17 | 全局 | Run/Export/Reading 事件到 WebView 的转发面 | 事件（Core JSONL stream 上的 §3 `Event<T>`）经 host 转发到 React | 事件 wire 已冻结，但 host→WebView 转发（Tauri event emit 等）未在任何契约冻结 | host 侧 Task：冻结事件转发面（P14 前置） |
| G18 | 工作台 | PageList 缩略图 / 当前页小缩略图【依据：04 §30.3「建议附小缩略图」】 | 列表行/进度面板低清缩略图 | 仅有 `resolve_page_resource` 原图通道（§10 大媒体约束：直接拉原图当缩略图不可接受） | 大媒体/缩略图契约 Task：低清预览或按需解码通道 |
| G19 | 工作台 | 导出目标位置选择（保存对话框 → ExportTargetRef） | 用户选目标 → host 签发一次性写引用 → `StartExport` | `ExportTargetRef`/HostControl 已冻结，但「选目标并返回 ref」的产品 Tauri command 面未冻结（同 G6 型） | host 侧 Task：冻结目标选择 command（P17 前置） |
| G20 | 工作台 | 导出后「打开所在文件夹」/历史状态展示【依据：04 §37；§10.3 明示需独立 host command】 | 按 export_id 触发 host 打开目录；状态/历史展示不含路径 | §10.3 要求的独立 host command 未冻结；`GetExportHistory` 路径仅 host 可见 | host 侧 Task：冻结 open-folder command（按不透明 export_id） |
| G21 | 设置 | Provider Profile CRUD / Capability 默认绑定 / Run Snapshot 查看【依据：04 §39–§40；P10 §5/§9】 | 多 Profile、能力绑定、绑定优先级解析展示、快照冻结查看 | P10 仅逻辑边界（§5/§9 消费分工），无 IPC wire | 契约 Task：冻结 Provider Profile 面（P15 前置） |
| G22 | 设置 | 凭据新增/替换/清除（CredentialRef exchange）【依据：P10 §3】 | 专用一次性凭据操作；只显示已配置/缺失；永不回显 | CredentialRef exchange 协议无 wire（普通 settings DTO 禁止承载） | 契约 Task：冻结凭据操作面（P10 §3 落地） |
| G23 | 设置 | Network Profile CRUD / 分阶段连接测试【依据：04 §41；P10 §6】 | 多 Profile、模式选择、Proxy→DNS→TCP→TLS→HTTP→Auth 分阶段测试 | P10 仅逻辑边界，无 wire | 契约 Task：冻结 Network Profile/测试面（P15 前置） |
| G24 | 设置 | 设置覆盖解析与来源显示（全局→作品→章节→任务）【依据：04 §42；P10 §5】 | 解析最终值 + 来源标注 | `settings_get` 仅全局 PipelineDefaults；无范围解析查询 wire | 契约 Task：冻结范围解析查询 |
| G25 | 设置 | 其余分区 schema（OCR/翻译/修复/排版/模型/并发/缓存/回收站策略/备份/Plugin 的键域） | 各分区可编辑的确定键集与值域 | `settings_update_section` 为透传设计（§5.3 不白名单化键集合），各分区键 schema 未冻结；仅 sfx.policy 有写入校验实例 | 逐分区契约 Task：冻结 section schema 后开放对应 UI |
| G26 | 书架/工作台 | 导入细分进度反馈 | 导入进行中的逐源/逐页进度 | `ImportProgressChanged` 明确保留 UNKNOWN/PROPOSAL（M2-C1 §6.2：P09 无持久 operation/snapshot wire，孤立事件不能成为导入真值） | 按 §6.2 原文：先由独立授权冻结可查询 Core snapshot，再决定是否加事件；此前 UI 仅同步 busy 态 |

---

## 8. 设计令牌（新架构自有取值）

**以下全部为本设计为新架构冻结的自有取值**（标注【自有取值】逐项生效）。与 LEGACY 的关系：QML 视觉基线（[ui-baseline](../ui-baseline.md) §4–§6 的色板/字号/间距）与 [05 UI 映射](../05_UI_MAPPING.md)、`M2-UI1 视觉契约`、`UI_UX_GUI_DESIGN` 仅作历史参考、**非绑定**——本文部分数值与其接近属设计延续的自由选择，不构成 parity 承诺；任何 LEGACY 值与本文冲突时以本文为准。

### 8.1 色彩

| 令牌 | 值 | 用途 |
|---|---|---|
| `color.bg.app` | `#f5f5f4` | 页面底色 |
| `color.bg.rail` | `#ececea` | 导航 Rail |
| `color.bg.toolbar` | `#f7f7f5` | 工具栏 |
| `color.surface.card` | `#ffffff` + 边框 `#d9d9d6` | 卡片/面板 |
| `color.accent` | `#4f6bed`；选中底 `#e8edff` | 主色：选中态/编号/焦点环基色 |
| `color.text.primary` | `#1f2328` | 主文字 |
| `color.text.secondary` | `#6b7280` | 次要文字 |
| `color.state.favorite` | `#e2a400` | 收藏星 |
| `color.state.archived` | `#f0b429` | 归档徽标 |
| `color.state.running` | `#4f6bed` | 处理中 |
| `color.state.completed` | `#2da44e` | 已完成 |
| `color.state.failed` | `#cf222e` | 失败 |
| `color.state.skipped` | `#8c959f` | 跳过/禁用文字 |
| `color.state.blocked` | `#9a6700` | 阻塞/警告 |
| `color.focus.ring` | `#4f6bed` | 焦点环（8.6） |

页状态色同时服务 TaskProgressPanel 统计、PageList 状态点与 BookGrid 徽标，保证跨页一致。深色模式**不在本基线范围**（未有任何 REQUIREMENT 来源；如引入属新需求决策）。

### 8.2 字体与字号

- 字体栈：`system-ui, "Segoe UI", "Microsoft YaHei UI", sans-serif`（跟随 Windows 系统字体；不指定自定义 family）【自有取值】。
- 字号：基础 13；次要 11；卡片标题 14（600 weight）；面板/空状态标题 18（600）；NavBadge/徽标 10；等宽（文件名/ID/hash 展示）`ui-monospace, Consolas, monospace` 12。
- 行高统一 1.5；数字统计用 `font-variant-numeric: tabular-nums` 防抖动。

### 8.3 间距与密度

- 基础网格 **4px**；常用档位 4 / 8 / 12 / 16 / 24。
- 密度：列表行高 32（PageList/ChapterList）；工具栏高 48（书架）/44（工作台）；面板内边距 12；卡片网格间距 8、单元 168×210（Grid）。
- TaskProgressPanel：展开高 ≈220、折叠 44。

### 8.4 圆角与描边

- 圆角：卡片/面板 6；按钮/输入 4；徽标/胶囊全圆；焦点环随元素圆角。
- 描边 1px `#d9d9d6`；分隔线 1px `#e8e8e4`。

### 8.5 交互态

- 即时反馈 ≤100ms、一级页切换 P95 ≤300ms、固定面板 P95 ≤200ms、无 >500ms 无反馈冻结、预计 >300ms 的操作配 Loading/Progress【依据：07 §4/§5】。
- 按压态 `#e8e8e4`；禁用态：不透明度 0.45 + `cursor: not-allowed` + tooltip。

### 8.6 焦点环

- 全部可交互元素键盘聚焦时显示 2px `color.focus.ring` 外环 + 2px 偏移；鼠标点击不显示持久环（focus-visible 语义）；对话框内焦点陷阱，`Tab` 不逃逸【自有取值】。

### 8.7 DPI 处理

- 布局全部使用 CSS 逻辑像素，不做物理像素换算；图像资源按设备像素比请求合适分辨率（大图通道本身与 DPI 无关）。
- 验证矩阵：Windows 100%/125%/150%/175%/200% 缩放下不得出现文本裁切、Footer 按钮不可见、悬浮窗超出屏幕、Inspector 无法滚动、TaskProgressPanel 控件重叠【依据：07 §8】；双屏不同 DPI/分辨率/缩放组合按 07 §9 验证。

---

## 9. 边界合规自证（逐条）

本设计及据其实现的 React 代码遵守以下边界（全部继承 [AD-001](../AD-001_TARGET_DESKTOP_ARCHITECTURE.md)「TARGET_INTENT and decision」表与「Migration constraints」第 4/6 项；契约 M2-C1 §2/§10）：

1. **不直接访问 SQLite**：React/WebView 无任何数据库句柄、SQL 或 ORM 依赖；一切数据经 §6 绑定表的冻结命令取得；SQLite 仅由 Python Core 权威写入【依据：AD-001 边界表；契约 M2-C1 §2】。本设计所有数据元素均映射到 W1–W29，无直连通道。
2. **不接触任意 OS 路径**：WebView 不接收用户源文件路径、Managed Copy 路径或导出路径——导入/导出路径仅存在于 host/Core 受信边界（`ImportSourceRef`/`ExportTargetRef`）；`GetExportHistory` 的 output_path 仅回到可信 host，host 不向 WebView 转发【契约：M2-C1 §10.2 绝对路径下发禁止、§10.3、§10.4】；文件选择一律经 host（G6/G19）。资源字节仅经 opaque URL（§10.2 不透明映射 ID）。
3. **不接触模型**：模型权重不经前端引用机制，加载是 Core 侧受控读取【契约：M2-C1 §10.1 T7】；UI 无任何模型文件概念。
4. **大图、tile、模型权重不走普通 JSON/Base64 IPC**：页图/预览全部经资源通道（opaque URL + 分块拉取，单资源上限 256MiB、T1–T7 阈值约束）【契约：M2-C1 §10 总则 + §10.1；RC-4 §3】；本设计无任何「图片字节进 JSON 命令」的元素。
5. **UI 不写持久化状态**：React 只呈现投影与发送意图；一切持久化（settings、进度、revision、lock、Run 状态）由 Python Core 经对应命令权威执行【契约：M2-C1 §1/§2；P11 §7.1】。面板宽度/窗口布局等纯 UI 偏好允许存 host 侧本地布局状态，不进 SQLite【自有取值，§1.3】。
6. **事件不作真值**：Run/Export/Reading 事件仅触发重新查询快照（§3.5/§4.5）；断线/重连后重查，不从事件重建状态【契约：M2-C1 §6.2/§7.2】。
7. **Secret 边界**：设置 UI 永不回显/持有明文凭据，错误与日志脱敏【契约：P10 §4；§5.3】。
8. **源文件保护**：导入只读、零回写；删除/永久删除不触及用户源文件（G2 消解时延续该约束）【依据：P09 §受控来源；04 §43.3】。
9. **不发明 wire**：§7 缺口全部交回 Coordinator；实现 Task 对缺口交互只做禁用态。

---

## 10. 非目标（不做清单）

本设计基线**明确不做**以下事项：

1. **不新增一级页面**：四页之外不设第五个一级 Route；详情/管理类内容固定区域或悬浮窗【依据：04 §1.1–1.2；AC-NAV-002】。
2. **不改四页区域划分**：书架/工作台/阅读器/设置的职责边界按 01/AD-001 冻结，本文仅在其内做布局设计。
3. **不新增产品功能**：G1–G26 是**既有 REQUIREMENT 的 wire 缺口登记**，不是新功能提案；本文不发明任何 01/04/07/08 之外的能力。
4. **不裁决任何产品发布门槛**：包括但不限于 P18 的 JA/KO 语言支持门槛（属用户裁决）；本文不设置质量 Gate、不宣称任何验收通过。
5. **不修改** AD-001、任何契约（`doc/contracts/**`）、Schema 或依赖清单（`requirements.txt`、`Cargo.toml`、`package.json`）。
6. **不写产品代码**：本 Task 只交付设计文档；`apps/**`、`src/**` 不在写入范围。
7. **不承诺 LEGACY parity**：QML 界面的像素级复刻不是要求；LEGACY 引用仅为历史参考（§0.5）。
8. **不裁决实现细节**：组件内部状态管理库、样式方案（CSS-in-JS/Tailwind 等）、Tauri 窗口 API 用法、事件转发机制实现选型，均留给各实现 Task 在其冻结范围内决定；本文只冻结用户可见结构与交互语义。
9. **不做深色模式、国际化框架、无障碍全量规范**（未见 REQUIREMENT 来源；焦点/键盘可达性按 §8.6 最小集冻结）。
10. **不处理 Webtoon 切片策略**：临时切片不成为 Page、不出现在页面列表与阅读序列【依据：04 §9.1；AC-WEBTOON-002】，切片机制属 Core/大媒体实现 Task。

---

## 附：AC 对照（供 Review）

| AC | 本文位置 | 自检证据 |
|---|---|---|
| AC1 四页覆盖 | §2–§5（每页含职责/布局/组件/状态矩阵/交互/键盘焦点） | `verification/UI-DESIGN-1/selfcheck-output.txt` (d) 逐项打勾 |
| AC2 导航 Shell | §1（切换不销毁/不停止任务，依据 08 AC-NAV-003 + P11 §7.1/7.2） | 同上 |
| AC3 契约绑定表 | §6（W1–W29，逐字可检索） | selfcheck (a) Select-String 日志 |
| AC4 wire 缺口表 | §7（G1–G26） | selfcheck (a) 反向核对 + 文档审查 |
| AC5 边界合规 | §9 九条自证 | selfcheck (c) + 文档审查 |
| AC6 设计令牌 | §8（自有取值声明 + LEGACY 关系） | 文档审查 |
| AC7 非目标 | §10 十条 | 文档审查 |
| AC8 自检可核验 | `verification/UI-DESIGN-1/` | `selfcheck-output.txt` 全量日志 |
| AC9 交付 | Handoff + 固定 commit | `doc/handoffs/UI-DESIGN-1-zcode.md` |

