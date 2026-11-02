---
id: FEA-06
title: Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）
kind: implementation
governance_version: 3
status: done
approval: scope_review_r3_approved_2026-11-02; impl_review_r2_approved_2026-11-02
suggested_owner: codex
owner: codex
reviewer: null
depends_on:
  - FEA-04
  - FEA-04b
  - FEA-05-WIRE-1
  - FEA-05-PORT-1
  - FEA-06-PREREQ-1
  - FEA-06-PREREQ-2
base_commit: 3c7f311d88b24bde462a61690e15d2c66f8c4683
branch: main
worktree: G:\CODEX\New Manga
integration_commit: b26840acdf682d69cf531bec3161d17bf90cf9f4
delivery_head: b26840acdf682d69cf531bec3161d17bf90cf9f4
canonical_evidence_status: complete
resource_closeout_status: complete（无 worktree；证据/过程文件全部登记；residual 转 FEA-06-RESIDUAL-1）
evidence_dir: verification/FEA-06
allowed_paths:
  - doc/tasks/FEA-06.md
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/**
  - apps/desktop-avalonia/src/NewManga.App/Controls/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-*.md
  - doc/handoffs/FEA-06-*.md
---

# FEA-06：Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）

## 来源与授权链

- **设计基线**：`doc/design/fluent-v1/`（**FROZEN v1.0.0**，2026-11-02，独立复核 r5 approved；FEA-04b done，集成 `112221b9a`）。本卡唯一设计输入，偏差走 v1.1 修订 + 重冻结（W-1）。
- **前置已交付**：`FEA-06-PREREQ-1`（外观持久化 Presentation 模型、`AppearanceSettings` schema、`motion.mode/categories` 解析、令牌生成器扩展）与 `FEA-06-PREREQ-2`（`AppearanceCoordinator` 唯一写者 + 兼容写、`FrontendSelector` 双壳激活、`FluentShell` 壳骨架、`--shell=legacy` 运维修回；集成 `92cac5ab1`，全量 1022/0/57）均 **done**。
- **数据/命令面**：FEA-05-WIRE-1（Core C078–C083）+ FEA-05-PORT-1（`IHostController` 7 Draft 方法、registry 17 additive）已 done。
- **架构**：AD-002（Windows/C# .NET 9 + Avalonia），产品四页唯一（书架/工作台/阅读器/设置），视觉**参考** Saber-Translator（非 1:1）。
- **Owner 指派（用户，2026-11-02）**：用户指示「四页 UI + 设计系统组件改造交给 codex」→ 本卡 implementation owner = **Codex**；DSH 保留范围冻结、Review Appointment、findings 处置、集成验证、证据收口与最终 push（W-10）。

## scope-r1 复核发现处置（2026-11-02，r1 = changes_requested / P0=2 / P1=7 / P2=11）

| r1 发现 | 处置 | 落点/证据 |
|---|---|---|
| **P0-1** C-03 外观持久化实现不存在（AC5/AC6 字段不可落） | 由 **PREREQ-1** 交付 Presentation 模型 + `AppearanceSettings` schema + `motion.mode` 三态/`motion.categories` 解析 + 迁移读取；**PREREQ-2** 交付唯一写者与兼容写 | `doc/tasks/FEA-06-PREREQ-1.md`、`FEA-06-PREREQ-2.md`（集成 `92cac5ab1`） |
| **P0-2** Fluent 激活/切换与 V2 并存未裁决、组合根不在写域 | 由 **PREREQ-2 W-1/W-2b** 交付：`FrontendSelector`（CLI > persisted > 缺省 V2；`builtin.fluent-dark`→V2 fallback）+ 组合根 `CreateShell` 双壳 + `--shell=legacy` 优先；本卡只实现 Fluent 壳内四页（W-5） | 同上；`App.axaml.cs` 组合根已冻结 |
| **P1-1** G-1/G-1b/G-1c 令牌生成缺口（`Nm.Focus.Ring.*`/`Corner.Fluent.*`/`Material.*`/`Elevation.*`） | **PREREQ-1** 生成器扩展（Focus/Corner/Elevation/Material + `NmKeys` registry）；**PREREQ-2** 追加 `Nm.Material.Acrylic.Base/Tint` 主题层键（不进 `Tokens.Global.axaml`） | 两生成器 `-- --check` up to date；`R14ContractTests` 67 allowed/59 required |
| **P1-2** AC2–AC5 未绑定 `09-state-matrix.md` 强制状态 | W-8 + 本版 AC2–AC5 逐页写死状态清单（取自 `09-state-matrix.md`） | 见 AC2–AC5 |
| **P1-3** Draft typed error 映射表未冻结 | W-2 + AC3 冻结映射表（17 码 → `CoreOperationException.Category` → UI 反馈面） | `doc/contracts/FEA-05_DRAFT_WIRE_CONTRACT.md:41-63` |
| **P1-4** P6 无 AC / 无组件拆解 | **AC6** 组件清单 AC（`10-component-inventory.md` 的 15–20 个新增/外观化组件逐项登记 + 状态/令牌/测试） | 见 AC6 + 任务拆解 P6 |
| **P1-5** 四页↔三空间↔左导航映射冲突 | W-6：顶栏空间 1/2/3（`04-layout-responsive.md:13`）；左导航随空间（书架空间=书架/回收站/导入，`05-page-shelf.md:21`）；四页与空间映射以设计为准，不新增第五页 | `04`、`05` |
| **P1-6** AC5 字段范围不清 | AC5 逐字引用 `08-page-settings.md:41-58` 冻结字段清单 | 见 AC5 |
| **P1-7** PLAN/STATUS 指针不一致 | 本版同步 STATUS/PLAN/ledger（DSH） | 本版提交 |
| **P2 系列**（写域、owner 记录、AC 细化、采证口径等） | 写域见 W-9；owner 见 W-10；采证见 AC9/W-11；AC 细化见下 | 本卡 |

## scope-r2 复核发现处置（2026-11-02，r2 = changes_requested / P0=1 / P1=1 / P2=10）

| r2 发现 | 处置 | 落点 |
|---|---|---|
| **P0** Fluent 壳依赖注入断裂（组合根只传 `(options, selection)`；写域内无合法注入通路） | **W-12**：DSH 单点预置注入（`App.axaml.cs` Fluent 分支传 `controller/appearance/themeManager`；`FluentShell.CreateRoot`/ctor 可选参数 + 只读属性；组合根测试断言实例同一）；不扩 FEA-06 写域 | 本版代码 + W-12 |
| **P1** AC2–AC5 状态清单与 `09-state-matrix.md` 不一致 | AC2–AC5 逐页改写为 09 本页列全行（含「—」说明）；W-8 落实 | AC2–AC5 |
| P2-1 AC5 漏 appearance/contrast | AC5 字段清单补全 | AC5 |
| P2-2 internal 映射与「保留旧 UI」张力 | AC3 补注「错误卡在位显示，保留旧 UI/上一帧，不清屏」 | AC3 |
| P2-3 W-6 缺阅读器/设置锚点 | W-6 补 `07:3`（ReaderOverlay）/`08:3`（ThemeStudio surface） | W-6 |
| P2-4 设置页其余分组承载口径 | 写入派发 brief（按 `08 §3` 分组在 Fluent 设置页内实现，数据语义沿用既有 surface） | 派发 brief |
| P2-5 depends_on 缺 FEA-04/FEA-05-WIRE-1 | 补入 depends_on | front matter |
| P2-6 资产边界未声明 | 禁止范围补「沿用 `NmIcon`，不新增资产/字体；确需新增停等 DSH」 | 禁止范围 |
| P2-7 「17 快捷键」口径 | AC1 改为「17 个既有冻结快捷键（全局 10 + 空间级 7）」 | AC1 |
| P2-8/P2-9/P2-10 令牌缺口/失败归因/交付顺序 | 写入派发 brief（缺口停等、单测失败先重跑归因、交付顺序） | 派发 brief |

## scope-r3 复核与释放（2026-11-02，r3 = approved / P0=0 / P1=0 / P2=3）

- r3 确认：r2-P0（Fluent 壳依赖注入）与 r2-P1（AC2–AC5 对齐 09 矩阵）**已闭环**，无新增 P0/P1；P2×3（卡 P3 旧口径、派发 brief 滞后、approval 字段）已在本版处置。
- **释放**：`status: ready`；`approval: scope_review_r3_approved_2026-11-02`；`base_commit = 3c7f311d8`（r3 被审 head）；owner=**Codex**（W-10），DSH 派发 brief：`G:\CODEX\New Manga.workspace\exchange\FEA-06-codex-brief.md`。
- 范围报告：`doc/reviews/FEA-06-scope-r1.md`（changes_requested）→ `-r2.md`（changes_requested）→ `-r3.md`（approved）。

## impl-r1 复核与处置（2026-11-02，r1 = changes_requested / P0=0 / P1=1 / P2=9）

- 复核报告：`doc/reviews/FEA-06-impl-r1.md`（独立上下文，被审 `b0388df9a`）；处置记录：`doc/reviews/FEA-06-impl-r1-adjudication.md`。
- **P1-1（返修）**：`Controls.Fluent.axaml:241` 悬空令牌 `Nm.Space.S1` → 改既有键（建议 `Nm.Space.2`）+ 登记表同步 + 令牌存在性守卫测试。
- **P2 处置**：P2-1 登记表页面归属（接线或改口径）、P2-2 09 细粒度缺口卡内补记、P2-3 响应式术语对齐、**P2-4 W-13 控制台空间映射**、P2-5 `[`/`]` 工作台翻页（可行则接线）、P2-7 Elevation 未消费登记 → 均交 Codex 返修；P2-6/P2-8/P2-9 接受并登记为 residual/技术债。
- 返修后：DSH 复核 → 集成验证 → 终态裁定。

## 任务拆解（按页 + 组件）

| 项 | 内容 | 设计输入 |
|---|---|---|
| P1 Shell | 顶条 `TopBand`/左导航 `NavRail`/状态条 `StatusBand`/命令条；17 全局快捷键（`ShellCommands` 既有）；三断点 1024/1280/1600；z-order；分栏折叠；空间 1/2/3 与四页映射（W-6/W-13） | `04-layout-responsive.md`、`03-accessibility.md` |
| P2 Shelf | `BookCard`/`BookRow`/`ChapterList`/`PageThumbStrip`；网格/列表、筛选、选择、右键、拖入、回收站入口；本页状态全量（见 AC2） | `05-page-shelf.md` |
| P3 Workbench | Region 列表/画布（`RegionBox`）/Inspector（`Drawer`）/FilmStrip（`StreamingThumb`）/批量栏（`BatchMatrix`）/`RunProjectionBar`；Draft 7 方法接入（OpenDraft/PatchDraft/PrepareCandidate/ApplyCandidates/GetDraft/ListDrafts/DiscardDraft）；`09-state-matrix.md` 工作台列 9 行全实现 | `06-page-workbench.md` |
| P4 Reader | `ReaderPage`/`ReaderProgressBar`；页导航/缩放/全屏/键盘滚轮→翻页、缩放/双击、方向 memento；进度保存接 `IReaderProgressSink`（FEA-04） | `07-page-reader.md` |
| P5 Settings | `SettingsGroup`/`SettingsField`；`08-page-settings.md:41-58` 字段逐字（frontendId/visualThemeId、motion.mode/categories、corners/material、layout.*、followSystemAccent、schemaVersion、Provider/网络/备份/关于）+ 保存/校验/错误态 | `08-page-settings.md`、C-03 §2.2 |
| P6 设计系统消费 | 15–20 个新增/外观化组件：`SurfaceCard`、`Drawer`、`Dialog`、`EmptyState`、`ErrorState`、`Toast/InfoBar`、`BookCard`、`BookRow`、`RegionBox`、`BatchMatrix`、`RunProjectionBar`、`SettingsGroup`、`SettingsField`、`PrimaryButton`、`SecondaryButton`、`DangerButton`、`SearchField`、`TabStrip`、`SegmentedControl`（以 `10-component-inventory.md` 为准，逐项登记）；令牌绑定 + 三态动效 + `09-state-matrix.md` | `01`、`02`、`09`、`10` |
| P7 证据与回归 | `verification/FEA-06/**`（每页 headless 状态测试日志 + 截图/渲染证据 + 组件登记表）；全量 sln；两生成器 `--check`；`check.ps1`/`verify_pins` | AC8/AC9 |

## 验收标准

- [ ] **AC1 Shell + 响应式**：`TopBand`/`NavRail`/`StatusBand` 使用 `Nm.*` 令牌；17 个既有快捷键可达，1024/1280/1600 断点与空间映射已实现。窄屏档为 `Narrow (<1024)`，`Medium (1024–1279)`，`Compact (1280–1599)`，`Full (≥1600)`；分栏折叠、UI memento、200% DPI 与原生桌面验收未覆盖。 <<PARTIAL: 基础导航、断点和键盘路径已实现；分栏折叠/状态恢复及原生 DPI 验收仍缺>>
- [ ] **AC2 Shelf**：实现书架网格/列表、搜索筛选、选择、拖入确认及加载/错误/只读等基础状态。回收站入口目前只有空面板；冻结 Host 端口不提供回收站恢复/删除操作，扫描进度也未细化到逐项。09 矩阵的错误态卡片尚缺控制台入口；空书架主按钮与 05 §3 的「导入文件/文件夹」不同，因当前 Host `ImportFilesAsync` 需先选章节，空态无可用目标，故保留可达的「新建作品」路径。 <<PARTIAL: 回收站操作端口、错误态控制台入口、逐项扫描进度及空态导入端口未提供；其余基础状态已实现>>
- [ ] **AC3 Workbench**：Region/Inspector/FilmStrip/批量视图、Draft 7 方法及 17 错误码到 UI 分类已接入。`pageBindingVersion` 缺失时新建 Draft 会 fail closed；Run 投影/控制端口未提供，BatchMatrix 未绑定数据。09 矩阵细粒度缺口：错误态卡片缺控制台入口；满态缺未保存圆点；冲突态缺「查看对照」动作。控制台空间已承载 Workbench「控制台」页签，空数据如实显示「当前没有运行中的任务」，完整 Run 投影/控制由 FEA-07/FEA-10 承接。 <<PARTIAL: 页面绑定与完整 Run 端口缺失，BatchMatrix 和 9 行状态矩阵未全实现；细粒度缺口已逐项登记>>
- [ ] **AC4 Reader**：页导航、缩放、方向 memento 和进度写回已接入。双页第二图、滚动模式、工具条自动隐藏和源不可用只读警示仍缺。 <<PARTIAL: 基础阅读与进度写回已实现，冻结设计要求的部分交互和状态尚未完成>>
- [ ] **AC5 Settings**：外观设置经唯一 `AppearanceCoordinator` 保存，Provider/网络/备份/关于分组已承载。现有冻结端口缺少网络超时/并发及备份目录/频率字段；完整错误/部分状态矩阵未覆盖。 <<PARTIAL: 外观与分组已落地，但受现有端口字段缺口及状态矩阵覆盖限制>>
- [ ] **AC6 设计系统组件**：组件登记表列出 20 项规范组件及令牌、页面和测试；样式复用 `Nm.*` 令牌。TabStrip、SegmentedControl、ChapterList 已接入对应页面；TabStrip `selected` 视觉样式与切换断言已覆盖；新增 Avalonia 令牌存在性守卫。部分组件尚未具备完整 normal/hover/pressed/disabled 状态，浮层开关状态也未全部实现。 <<PARTIAL: 组件清单、页面接线、TabStrip 选中视觉和令牌守卫完成，规范要求的全组件状态覆盖仍不足>>
- [ ] **AC7 可访问性与动效**：实现主要 Tab 顺序、A11y 名称、高对比和 reduce-motion 路径。焦点环与三类 motion 状态覆盖不完整，且没有原生桌面验证。 <<PARTIAL: 基础可访问性与动效路径已实现，焦点环/分类动效及原生验收未闭环>>
- [x] **AC8 回归**：全量 sln build/test、Fluent 页面测试、DesignSystem 组件测试及 TokenGen/ThemeGen `--check` 均通过；返修后全量 **1034 passed / 0 failed / 57 skipped**，相对返修前 1030/0/57 新增 4 passed。 <<MET>>
- [x] **AC9 证据**：提交 build/test/生成器/治理日志、四页 Headless PNG、组件登记表、UIUX 结果与 SHA-256 索引；Canonical Evidence 固定到实现 commit。 <<MET>>
- [x] **AC10 范围纪律**：实现提交及本轮返修路径均在允许范围；返修 scope audit 已记录。未改 Core/契约/schema/用户数据、冻结设计、生成物、组合根、selector 或 Current V2，未 push。 <<MET>>

## 禁止范围

- 不改 Core/契约（FEA-05 已冻结）；不改 schema；不改用户数据；不改 `doc/design/fluent-v1/**`（设计变更走 v1.1 + 重冻结）；不改生成物；不 push。
- 不实现设计基线之外的新交互（超出即范围变更）。
- 不改 Current V2 视觉与既有行为（C-02 V-05 判据②）。
- **资产边界（r2-P2-6）**：沿用 `NmIcon` 既有图标集合，不新增资产/字体；确需新增 → 停等 DSH 裁决（资产落点 `Assets/**` 不在写域，且需许可评估）。
- **双屏/拔屏（G-4）归 FEA-07**，不在本卡范围（`04-layout-responsive.md` §4 归 FEA-07）。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 设计基线版本 | 唯一输入 `fluent-v1.0.0`（FROZEN）；偏差须走 v1.1 修订 | FEA-04b Closeout |
| W-2 | Draft 命令面接入方式 | 经 `IHostController`（FEA-05-PORT-1）而非直接 CoreClient；typed error（`DraftError` code/category）映射到 UI 状态 | FEA-05-PORT-1 交付 |
| W-3 | 页面拆分 | 每页独立 View/ViewModel，Shell 只做导航与布局 | 设计 `04-layout-responsive.md` |
| W-4 | 视觉实现 | 用 `NewManga.DesignSystem` 令牌 + `NewManga.ThemeEngine`（既有），不新建第二套设计系统 | AC6/AC8 |
| W-5 | Fluent 激活/切换 | 前置 2 的双壳 selector（`frontendId`）；本卡只实现 Fluent 壳内四页 | FEA-06-scope-r1 P0-2 |
| W-6 | 四页↔三空间↔左导航映射 | 按设计基线执行：顶栏「空间 1/2/3」（`04:13`），左导航随空间（书架空间=书架/回收站/导入 `05:21`）；**阅读器=`ReaderOverlay` 浮层（`07:3`），设置不新增 `SpaceId`、由顶部命令条和左导航进入（`08:3`）**；四页与空间映射以设计为准，FEA-06 不新增第五页 | FEA-06-scope-r1 P1-5；design v1.0.0 FROZEN |
| W-7 | 令牌生成归属 | G-1/G-1b/G-1c 由前置 1 生成，本卡只消费 | r1 P1-1 |
| W-8 | 页面状态清单 | 以 `09-state-matrix.md` 为唯一状态清单，AC2–AC5 逐页覆盖 | r1 P1-2 |
| W-9 | 写域扩张（处置 r1 P2-2） | 在 `Views/**`/`ViewModels/**`/`Shell/**` 之外追加 `Controls/**`、`Styles/**`、`Services/**`（四页所需的页面数据/导航适配器与外观组件）；不含 `App.axaml`/组合根（PREREQ-2 已冻结） | r1 写域审查；实现可行性 |
| W-10 | Owner 与交付方式（用户 2026-11-02） | Owner = **Codex**；Codex 可在 main 直接实现并提交单一实现 commit（只含 allowed_paths 内文件），**不得 push**；DSH 负责 Review Appointment、独立实现复核、集成验证与最终 push | 用户 2026-11-02 指派 |
| W-11 | 证据口径（处置 r1 P2-6） | 每页 ≥1 headless 状态测试（`AvaloniaFact`）+ 至少 1 张 headless 渲染截图（PNG，落 `verification/FEA-06/`）+ 组件登记表（Markdown）；日志含命令与 exit | r1 采证口径 |
| W-12 | 组合根依赖注入预置（处置 **scope-r2 P0**） | Fluent 壳的依赖注入由 **DSH 单点预置**：`App.axaml.cs` 的 Fluent 分支传入 `controller/appearance/themeManager`，`FluentShell.CreateRoot`/ctor 扩为可选参数并暴露只读属性 `HostController`/`Appearance`/`ThemeManager`；不改 V2/legacy 分支与 selector 语义。Codex 只**消费**这些实例（不得新建第二个 `HostController` 或 `AppearanceCoordinator`）；`App.axaml.cs` 仍不在 FEA-06 写域 | scope-r2 §2.1 建议①；PREREQ-2 唯一写者/sidecar 单实例语义 |
| W-13 | 控制台空间映射（处置 **impl-r1 P2-4**，DSH 裁决 2026-11-02） | `SpaceId.Console` **不得映射 Settings**：控制台空间承载 Workbench 第三视图「控制台」（最小 Run 控制台面板：运行状态/错误入口；无数据时显示「当前没有运行中的任务」，不得造假数据；完整 Run 数据由 FEA-07/FEA-10 承接，登记 residual）。**Settings 改为非空间入口**：顶部命令条「设置」按钮 + 左导航项（`08-page-settings.md:3`）；Shell 测试同步。返修按 `doc/reviews/FEA-06-impl-r1-adjudication.md` | impl-r1 P2-4；design `04:13`/`06:12`/`06:21`/`08:3` |

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-06-session-handoff.md`（随交接文档提交）。
- Review：`doc/reviews/FEA-06-impl-r1.md` 已对 `b0388df9ae2bb087649b44cf25a0921b2116934e` 提出 changes_requested；DSH 处置见 `doc/reviews/FEA-06-impl-r1-adjudication.md`。本轮按处置返修，待 DSH 复核新 delivery head。
- 实际测试：见下表与 `verification/FEA-06/`；环境 Windows 11 / .NET 9 / Avalonia.Headless。
- 最终由 DSH 填写 `integration_commit`、完成资源核销与集成验证后决定终态；本次仅进入 `in_review`。

## 测试要求

| 场景/AC | 实际命令 | 环境 | 实际 | 证据 |
|---|---|---|---|---|
| AC6 / P2-R2-1 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~WorkbenchPage_UnselectedState_OffersReturnToShelf` | Windows 11 / .NET 9 / Avalonia.Headless | PASS：1 passed / 0 failed / 0 skipped；三 Tab 切换时 selected class 恰一项，选中背景/前景/边框/圆角与 `Nm.*` 资源一致 | `verification/FEA-06/impl-r2-fluent-tab-test.log` |
| AC1–AC7 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~Fluent` | Windows 11 / .NET 9 / Avalonia.Headless | PASS：23 passed / 0 failed / 0 skipped；含令牌守卫、W-13 与 P2-5 测试 | `verification/FEA-06/rework-page-tests.log` |
| AC6 | `dotnet test apps\desktop-avalonia\tests\NewManga.DesignSystem.Tests\NewManga.DesignSystem.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~FluentComponentsTests` | Windows 11 / .NET 9 | PASS：1 passed / 0 failed / 0 skipped | `verification/FEA-06/rework-design-system-tests.log` |
| AC8 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | Windows 11 / .NET 9 | PASS：0 warnings / 0 errors | `verification/FEA-06/impl-r2-build.log` |
| AC8 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | Windows 11 / .NET 9 | PASS：**1034 passed / 0 failed / 57 skipped**；与 impl-r1 返修结果相同，无退化；skip 因缺少 `NEWMANGA_CORECLIENT_SIDECAR_DIR` | `verification/FEA-06/impl-r2-full-test.log`、`skip-analysis.md` |
| AC8 | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | Windows 11 / .NET 9 | PASS：292 rows，冻结令牌生成物一致 | `verification/FEA-06/rework-token-gen.log` |
| AC8 | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | Windows 11 / .NET 9 | PASS：主题生成物与冻结输入一致 | `verification/FEA-06/rework-theme-gen.log` |
| AC8/AC9 | `pwsh -NoProfile -File tools\governance\check.ps1` | Windows PowerShell | PASS：3 项既有预算/ledger 提示；未增加治理错误 | `verification/FEA-06/impl-r2-check.log` |
| AC8/AC9 | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | Windows PowerShell | PASS：冻结契约 pins 15/15 | `verification/FEA-06/impl-r2-verify-pins.log` |
| AC9 | `python tools\governance\task_ledger.py --write` | Windows 11 / Python | PASS：ledger 已按 `in_review` 重建 | `verification/FEA-06/rework-task-ledger.log` |
| AC9 | Avalonia.Headless 每页渲染截图与页面状态测试 | Windows 11 / Avalonia.Headless（SIMULATED） | PASS：Shelf/Workbench/Reader/Settings 各 1 张；非原生验收；由全量测试重渲染 | `verification/FEA-06/screens/`、`rework-full-test.log` |
| AC9 | UIUX `finalize` | UIUX Engine 1.3.3 | PARTIAL（exit 11）：独立 Review、L4 设计 Review、持久流程图与 NATIVE_APP 验收待补 | `verification/FEA-06/uiux/finalize.log`、`task-result.json` |

## impl-r1 返修记录与 residual

- 已处置：P1-1 改用冻结令牌 `Nm.Space.2`，并增加 Fluent `DynamicResource Nm.*` Avalonia 解析守卫；P2-1 的 TabStrip、SegmentedControl、ChapterList 已接入 Workbench/Shelf；P2-3 断点文案统一为 Narrow `<1024`、Medium `1024–1279`；W-13 由 Workbench 控制台页签承载 Console 空间，Settings 从顶部命令条和左导航进入；P2-5 用现有 Workbench `Pages`/`SelectedPage` 接通 `[`/`]`，未增加 Host 端口。
- P2-2 residual（对应 09 矩阵）：Shelf 与 Workbench 错误卡缺控制台入口；Workbench 满态缺未保存圆点；冲突态缺「查看对照」动作。AC2/AC3 保持 `PARTIAL`。
- P2-6 residual：书架首次空态主按钮仍为「新建作品」，与 05 §3 的导入主按钮不同；当前 Host `ImportFilesAsync` 要求先选章节，空书架无导入目标。待 Host 提供可达的空态导入入口后再对齐。
- P2-7 residual：`Nm.Elevation.*` 当前未消费，使用 1px 边框替代阴影；后续样式 Task 补阴影。
- P2-8 技术债：四个 Fluent ViewModel 仍同居 `FluentPageViewModels.cs`，后续纯移动拆分，不改变行为。
- P2-9 residual：Settings 离开未保存更改的保存/丢弃/取消确认及 `Esc` 取消编辑尚未实现，留后续 UX Task。
- W-13 residual：Run 控制台仅呈现无任务状态和实际已有的工作台错误入口；完整 Run 数据/控制由 FEA-07/FEA-10 的 Host 端口承接，不构造模拟任务。
- PNG 采证测试仍直接写入 `verification/FEA-06/screens/`；异机渲染可能造成文件变更，后续可改为显式 opt-in。

## impl-r2 P2-R2-1 返修记录

- TabStrip 按钮原有 `selected` class 在页面/批量/控制台切换时已正确设置与清除；补充 `Button.fluent-secondary.selected` 令牌样式，显示 Accent.Muted 背景、Text.Primary 前景、Accent.Base 边框及 Fluent.Sm 圆角。
- 组件登记表 TabStrip 行改为列出实际令牌依赖和已实现的选中视觉状态。
- 扩展 `WorkbenchPage_UnselectedState_OffersReturnToShelf` headless 断言：检查三 Tab 在 Page/Batch/Console 切换时恰有一个 `selected`，且有效背景/前景/边框/圆角解析至列出的 `Nm.*` 令牌。该测试为扩展既有用例，未新增测试数量；全量仍为 1034/0/57。
- 初次定向构建因测试缺少 `CornerRadius` 命名空间引用而失败；补上 `using Avalonia` 后定向测试通过，首次失败日志保留为证据。

## impl-r2 复核与收口（2026-11-02，r2 = approved / P0=0 / P1=0 / P2=1）

- 复核报告：`doc/reviews/FEA-06-impl-r2.md`（独立上下文，被审返修 head `7cf305fe2`；**approved**）。确认：P1-1 闭合（`Nm.Space.S1`→`Nm.Space.2` + 守卫测试反证成立）、W-13 符合 DSH 裁决与设计（Console→Workbench 第三视图、Settings 非空间入口）、P2-1/2/3/5/6/7/8/9 全部落实、范围零越界、全量 1034/0/57。
- 唯一新 P2（P2-R2-1）：TabStrip `selected` class 视觉空操作 + 登记表半句失实 → **已由 Codex 修复**（`b26840acd`：`Button.fluent-secondary.selected` 令牌样式 + 登记表如实 + 测试扩展断言），DSH 复验全绿。
- **收口判定**：AC8–AC10 MET；AC1–AC7 为 PARTIAL —— 按 DSH 处置**接受并转 residual**（见 `doc/tasks/FEA-06-RESIDUAL-1.md`；依赖 FEA-07/09/10/11/12/13 端口逐项补齐，不阻塞 FEA-07）。integrated at `b26840acd`。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA06-AC1 | AC1 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml.cs` | `7cf305fe2534272dc75295c4644661ddb73221af` | `d9934017d33849c167867646d9737336cb957d23a77914459e83ec410d54c2d5` | CANONICAL |
| EV-FEA06-AC2 | AC2 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs` | `7cf305fe2534272dc75295c4644661ddb73221af` | `45e37d3fb38bfca7b030428b397193955afd1f06ace6e4cdecc559bdaa4115f8` | CANONICAL |
| EV-FEA06-AC3 | AC3 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs` | `7cf305fe2534272dc75295c4644661ddb73221af` | `7ed78e52fa1a1943bdbd58601b4eb12b25b5373f80eadfc1b9a388846eced74f` | CANONICAL |
| EV-FEA06-AC4 | AC4 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `2b5fc10a95e9f1fdbe20cc12e3f9f543a2400ada6d47ccbaf7925298f7026919` | CANONICAL |
| EV-FEA06-AC5 | AC5 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `bb55cd59872e288ffc3da676900a784e9153e138d676c2aa71d11befd75dd53f` | CANONICAL |
| EV-FEA06-AC6 | AC6 | `verification/FEA-06/component-registry.md` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `5dd20bf012c3863bca5700febd896357ec2fe136cc44fcd7ed2e131bcfe58324` | CANONICAL |
| EV-FEA06-AC7 | AC7 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `5c7fa89521418fbf518086e050f86f635f4e4f89bc498948fa32bc403bd1be72` | CANONICAL |
| EV-FEA06-AC8 | AC8 | `verification/FEA-06/full-test.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `be5fda55f2e55135bd5c81f902f9d2bf4b1d6aa10d78abc95b4451222890ad21` | CANONICAL |
| EV-FEA06-AC8-BUILD | AC8 | `verification/FEA-06/build.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `a7d6f89bb743f1bd40d46c185344c85d9c6fb2c5bea6940cccebaa38d632ffa0` | CANONICAL |
| EV-FEA06-AC6-TEST | AC6 | `verification/FEA-06/design-system-component-tests.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `5e3532f3b2af9efd01de8a75716f826c10d521a4797cb5ff568d708f52704838` | CANONICAL |
| EV-FEA06-AC1-7-TEST | AC1–AC7 | `verification/FEA-06/page-tests.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `1cd942044a0ab41326c9dedc9b9c6f3f1aa99e2f04059a92a14000b959a4439c` | CANONICAL |
| EV-FEA06-AC8-GENERATORS | AC8 | `verification/FEA-06/token-gen.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `0cc5e6bbc598c2ed50a3f5557a7fca2f027540d599c1be48f13504ca08ca3977` | CANONICAL |
| EV-FEA06-AC8-THEMEGEN | AC8 | `verification/FEA-06/theme-gen.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `ee2948527883acfe211eb47f881c63ba1f0511d7ca38d648902bc183a692651e` | CANONICAL |
| EV-FEA06-AC9-SKIPS | AC9 | `verification/FEA-06/skip-analysis.md` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `acaf68b7b12ed9347a97e6aad6193d2411c6bb47f80e63e3c483fb2dc91d692a` | CANONICAL |
| EV-FEA06-AC9-CHECK-PRE | AC9 | `verification/FEA-06/governance-check.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `1141042fda8bdff7f268927511cd243da838b1e13eab4aff08d60fbf5f0b982f` | CANONICAL |
| EV-FEA06-AC9-PINS-PRE | AC9 | `verification/FEA-06/verify-pins.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `cefc5376c8ea58cdd8297aa39674aff6aaaf31ac683dc446d16b2cbfb395a479` | CANONICAL |
| EV-FEA06-AC9-LEDGER | AC9 | `verification/FEA-06/task-ledger-in-review.log` | `-` | `0a62e1a2585f2fea8dc9a4049b361547d3d36fa5de4ebe392153a5c3e51a9f2f` | SOURCE_PIN |
| EV-FEA06-AC9-PINS | AC9 | `verification/FEA-06/verify-pins-in-review.log` | `-` | `4013203b711a94e9c158cb226b545711e609778384702f982d25aedeaffae9a5` | SOURCE_PIN |
| EV-FEA06-AC9-GOV-INREVIEW | AC9 | `verification/FEA-06/governance-in-review.log` | `-` | `dd09ac7e256b41fdd2907592b5438f7c08fe2cb2430e6f7488c7aa79c17faaf3` | SOURCE_PIN |
| EV-FEA06-AC9 | AC9 | `verification/FEA-06/evidence-index.md` | `-` | `6eaa01a72f824da88dc4621197a9028b794be811e8961fb0d544f89397477a09` | SOURCE_PIN |
| EV-FEA06-SCREEN-SHELF | AC9 | `verification/FEA-06/screens/shelf.png` | `7cf305fe2534272dc75295c4644661ddb73221af` | `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a` | CANONICAL |
| EV-FEA06-SCREEN-WORKBENCH | AC9 | `verification/FEA-06/screens/workbench.png` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` | CANONICAL |
| EV-FEA06-SCREEN-READER | AC9 | `verification/FEA-06/screens/reader.png` | `7cf305fe2534272dc75295c4644661ddb73221af` | `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2` | CANONICAL |
| EV-FEA06-SCREEN-SETTINGS | AC9 | `verification/FEA-06/screens/settings.png` | `7cf305fe2534272dc75295c4644661ddb73221af` | `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162` | CANONICAL |
| EV-FEA06-UIUX-COVERAGE | AC9 | `verification/FEA-06/uiux/coverage-matrix.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `a9d74fd319b806c823db7fb0ca19394f90a1258afa356fd264ad282ec37322c8` | CANONICAL |
| EV-FEA06-UIUX-GATES | AC9 | `verification/FEA-06/uiux/gate-results.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `dcdf1daf2139d78113cde29135d56531142fcbda942ffbdbdcc80aa6aa080b09` | CANONICAL |
| EV-FEA06-UIUX-REQUEST | AC9 | `verification/FEA-06/uiux/request.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `74c0edac9e66c700f9b8bd0289ccc7591aeeb323ac231749c66c80c219ea4c19` | CANONICAL |
| EV-FEA06-UIUX-TOOLLOGS | AC9 | `verification/FEA-06/uiux/tool-logs.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `8f32b1895125c37919ff9c83b8056d2e4974b101c9f6a1c916f84971ba7d971d` | CANONICAL |
| EV-FEA06-UIUX-MANIFEST | AC9 | `verification/FEA-06/uiux/evidence-manifest.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `dd1db40b8b1bef9318039d683f4aface7c3f80612a1708482e8f7637bbabeb4b` | CANONICAL |
| EV-FEA06-UIUX-FINALIZE | AC9 | `verification/FEA-06/uiux/finalize.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `bde655d84ede10046dae7df6c03e0b180b46e6cf6ce78b2274ad8e4ed43c1b88` | CANONICAL |
| EV-FEA06-UIUX-RESULT | AC9 | `verification/FEA-06/uiux/task-result.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `cebe22f92c522074343ec4303f176c42bfe4c3a3e003f4673fc0502b96fb267f` | CANONICAL |
| EV-FEA06-REVIEW-IMPL-R1 | Review | `doc/reviews/FEA-06-impl-r1.md` | `-` | `3791049f3347391e944cb7fda491217c528c1ca26c108e8903a719ec34a2e4b1` | SOURCE_PIN |
| EV-FEA06-ADJUDICATION | Review | `doc/reviews/FEA-06-impl-r1-adjudication.md` | `-` | `eaa5d24f70ec3159278833cf75354df588b7d839385cbbdfd25f591930549a9d` | SOURCE_PIN |
| EV-FEA06-REVIEW-IMPL-R2 | Review | `doc/reviews/FEA-06-impl-r2.md` | `-` | `f749682bd58ab392687f825588954dc3da98a2ffc5017a683918ae9dd38b6889` | SOURCE_PIN |
| EV-FEA06-INTEGRATION | AC8/Gate | `verification/FEA-06/integration-verification.log` | `-` | `2ad559ab8cbd8d8c8b9b95a7e94c8d351e23e2926a83efdb414fac3f6b3014e3` | CANONICAL |
| EV-FEA06-AC10 | AC10 | `verification/FEA-06/rework-scope-audit.md` | `7cf305fe2534272dc75295c4644661ddb73221af` | `4e0696c8944e99156d9b23268201aed9fd075f6347a821a4c9778f63dcb874d0` | CANONICAL |
| EV-FEA06-P1-1-STYLE | AC6 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `02a4a2cf851b82f39d16094a2a266214e3477877d4dbfb2143342175d3982c96` | CANONICAL |
| EV-FEA06-P1-1-GUARD | AC6 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentTokenResourceTests.cs` | `7cf305fe2534272dc75295c4644661ddb73221af` | `0549ab08c1f7a80583a6bafe877b0b14da6a08698e82696bd4e01c18ab3a372a` | CANONICAL |
| EV-FEA06-W13-SHELL-XAML | AC1 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml` | `7cf305fe2534272dc75295c4644661ddb73221af` | `9fdacf5af8e1ffc90adf66308c9a44f88ad788d834c34ab6946950512ddf10d8` | CANONICAL |
| EV-FEA06-W13-SHELL-TEST | AC1 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentShellTests.cs` | `7cf305fe2534272dc75295c4644661ddb73221af` | `f8cbb9eb1f26be141072716f2eaebd322356814175447ae8e4b335c8d2d368c8` | CANONICAL |
| EV-FEA06-REWORK-BUILD | AC8 | `verification/FEA-06/rework-build.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `56581789d10b76aa06ec29e9e05268de879691dd2bb562ba61cb5441cabb5c21` | CANONICAL |
| EV-FEA06-REWORK-FULL-TEST | AC8 | `verification/FEA-06/rework-full-test.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `63c707807a6e1da0dc02dfe6aa56579e3e95eb9ab443fcf7e954e929b782e23e` | CANONICAL |
| EV-FEA06-REWORK-PAGE-TEST | AC1–AC7 | `verification/FEA-06/rework-page-tests.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `3fb25d527c432dc53f68b50acbec4ce6245f31d51e72401b81136c47ff03ca27` | CANONICAL |
| EV-FEA06-REWORK-DS-TEST | AC6 | `verification/FEA-06/rework-design-system-tests.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `1ab974fb7cbec32ae2377830be759cd3d0a5f1b1760b027253d815347d6f5737` | CANONICAL |
| EV-FEA06-REWORK-TOKEN-GEN | AC8 | `verification/FEA-06/rework-token-gen.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `90b91fbde2c349ee51bb31fc0c68cf71ac63243f66dc19654a0f9b854df50753` | CANONICAL |
| EV-FEA06-REWORK-THEME-GEN | AC8 | `verification/FEA-06/rework-theme-gen.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `169b9fe70e730c0503ab12d4ee4a7f51684318d52aa23b2ab0ba3e1c10b024ee` | CANONICAL |
| EV-FEA06-REWORK-ATTEMPT1 | AC8 | `verification/FEA-06/rework-full-test-attempt1.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `1547e6984fa27208a2d87b2c99a1d8b0e091d2add8afbc4e307f129f2677be22` | CANONICAL |
| EV-FEA06-REWORK-LEDGER | AC9 | `verification/FEA-06/rework-task-ledger.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `15c220f917421357be14c9cdf9065c5c543f96f8740a52bfb13614a580fd5248` | CANONICAL |
| EV-FEA06-REWORK-GOV | AC9 | `verification/FEA-06/rework-governance-check.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `07ebd871931f4aed985f8afcb1e7aeb53ed476501940d334a6a021c61e9cc8a9` | CANONICAL |
| EV-FEA06-REWORK-PINS | AC9 | `verification/FEA-06/rework-verify-pins.log` | `7cf305fe2534272dc75295c4644661ddb73221af` | `d521d266606edec817ac419e0252fca4aeca39c1b06463bf87d1411e49929e05` | CANONICAL |
| EV-FEA06-AC10-BASE-SCOPE | AC10 | `verification/FEA-06/scope-audit.md` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `cec04b8135b13549f8c0114b43fe1259b00e5e335538cddccd6166cd8da90ea0` | CANONICAL |
| EV-FEA06-IMPL-R2-STYLE | AC6 | `apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/Controls.Fluent.axaml` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `02a4a2cf851b82f39d16094a2a266214e3477877d4dbfb2143342175d3982c96` | CANONICAL |
| EV-FEA06-IMPL-R2-FLUENT-TEST | AC6 | `verification/FEA-06/impl-r2-fluent-tab-test.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `a7b451dd0872d893fe0f961d311cbb4282869d653a54a5c3c4f1aafe707e8b53` | CANONICAL |
| EV-FEA06-IMPL-R2-FLUENT-ATTEMPT1 | AC6 | `verification/FEA-06/impl-r2-fluent-tab-test-attempt1.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `42932aabd87e116796678110570af9586933ee97e0235bdbf2ebb8e63d917ff8` | CANONICAL |
| EV-FEA06-IMPL-R2-BUILD | AC8 | `verification/FEA-06/impl-r2-build.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `30dc4310c5eb364b88678c5e65b69a0eecd8a65fa4ab8cee7e17beed2ea685cf` | CANONICAL |
| EV-FEA06-IMPL-R2-FULL-TEST | AC8 | `verification/FEA-06/impl-r2-full-test.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `cce2834512d194b979464f71a9e1dbbf7724d0ecaab736c6105d6da00012e61a` | CANONICAL |
| EV-FEA06-IMPL-R2-CHECK | AC8/AC9 | `verification/FEA-06/impl-r2-check.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `437e103611d48b529cbfe3047c81a6a9299318294e44d2bcb9a69a6c295ed2a5` | CANONICAL |
| EV-FEA06-IMPL-R2-PINS | AC8/AC9 | `verification/FEA-06/impl-r2-verify-pins.log` | `b26840acdf682d69cf531bec3161d17bf90cf9f4` | `fe89637581edf5203f39d2e6bda7a240b69724e5f88c877016f74a93c7743930` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 无 linked worktree；main checkout `G:\CODEX\New Manga` | NOT_APPLICABLE | 同一仓库 checkout | `b0388df9ae2bb087649b44cf25a0921b2116934e` | 直接在 main 实施；不创建/删除 worktree。 |
| verification artifacts | `verification/FEA-06/**` | PRESERVE_REFERENCED | 同路径 | `verification/FEA-06/evidence-index.md` | 证据被 Task 与 Handoff 引用；交 DSH 在集成窗口复核资源处置。 |
| task-env / user data | 未创建 / 未访问 | NOT_APPLICABLE | - | - | 未写产品数据或用户源文件；无独立环境需清理。 |

## Closeout Record

- **实施交付**：2026-11-02 / Codex（用户指派 owner）；首轮实现 `b0388df9a`；impl-r1 changes_requested → 返修 `7cf305fe2`；impl-r2 approved → P2-R2-1 小修 `b26840acd`；均未 push。
- **复核链**：scope-r1/r2/r3（r3 approved）→ impl-r1（changes_requested，P0=0/P1=1/P2=9）→ DSH adjudication → Codex 返修 → impl-r2（**approved**，P0=0/P1=0/P2=1）→ P2-R2-1 修复 → DSH 复验。
- **DSH 集成验证（2026-11-02）**：main 直接实现、无 worktree；集成 commit = delivery head **`b26840acd`**。build 0 警告/0 错误；全量 **1034 passed / 0 failed / 57 skipped**（基线 1022+12；57 skip 原因与基线一致）；TokenGen/ThemeGen `-- --check` up to date；`check.ps1` PASS（3 warnings）；`verify_pins` 15/15 → `verification/FEA-06/integration-verification.log`。
- **终态**：`status: done`；AC8–AC10 **MET**；**AC1–AC7 PARTIAL → residual 转 `FEA-06-RESIDUAL-1`**（依赖 FEA-07/09/10/11/12/13 端口逐项补齐；不阻塞 FEA-07）。canonical_evidence_status / resource_closeout_status 均 complete；证据表（含 review/集成验证行）经 `check.ps1` sha 校验。
- **残留登记**：P2-2（09 细粒度缺口）、P2-6（书架空态主按钮偏差）、P2-7（Elevation 未消费）、P2-8（四 VM 单文件技术债）、P2-9（设置未保存确认/Esc）、W-13 residual（完整 Run 控制台数据）、PNG 采证测试写仓库（异机 dirty）→ 全部登记到 `FEA-06-RESIDUAL-1` 或后续 Task。
- 删除、迁移、归档数量/字节数：0；未执行清理或数据迁移；未写产品数据/用户源文件。
- 关闭于 2026-11-02（DSH 集成；未 push）。
