---
id: FEA-06
title: Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）
kind: implementation
governance_version: 3
status: in_review
approval: scope_review_r3_approved_2026-11-02
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
integration_commit: null
delivery_head: b0388df9ae2bb087649b44cf25a0921b2116934e
canonical_evidence_status: complete
resource_closeout_status: pending
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
| P1 Shell | 顶条 `TopBand`/左导航 `NavRail`/状态条 `StatusBand`/命令条；17 全局快捷键（`ShellCommands` 既有）；三断点 1024/1280/1600；z-order；分栏折叠；空间 1/2/3 与四页映射（W-6） | `04-layout-responsive.md`、`03-accessibility.md` |
| P2 Shelf | `BookCard`/`BookRow`/`ChapterList`/`PageThumbStrip`；网格/列表、筛选、选择、右键、拖入、回收站入口；本页状态全量（见 AC2） | `05-page-shelf.md` |
| P3 Workbench | Region 列表/画布（`RegionBox`）/Inspector（`Drawer`）/FilmStrip（`StreamingThumb`）/批量栏（`BatchMatrix`）/`RunProjectionBar`；Draft 7 方法接入（OpenDraft/PatchDraft/PrepareCandidate/ApplyCandidates/GetDraft/ListDrafts/DiscardDraft）；`09-state-matrix.md` 工作台列 9 行全实现 | `06-page-workbench.md` |
| P4 Reader | `ReaderPage`/`ReaderProgressBar`；页导航/缩放/全屏/键盘滚轮→翻页、缩放/双击、方向 memento；进度保存接 `IReaderProgressSink`（FEA-04） | `07-page-reader.md` |
| P5 Settings | `SettingsGroup`/`SettingsField`；`08-page-settings.md:41-58` 字段逐字（frontendId/visualThemeId、motion.mode/categories、corners/material、layout.*、followSystemAccent、schemaVersion、Provider/网络/备份/关于）+ 保存/校验/错误态 | `08-page-settings.md`、C-03 §2.2 |
| P6 设计系统消费 | 15–20 个新增/外观化组件：`SurfaceCard`、`Drawer`、`Dialog`、`EmptyState`、`ErrorState`、`Toast/InfoBar`、`BookCard`、`BookRow`、`RegionBox`、`BatchMatrix`、`RunProjectionBar`、`SettingsGroup`、`SettingsField`、`PrimaryButton`、`SecondaryButton`、`DangerButton`、`SearchField`、`TabStrip`、`SegmentedControl`（以 `10-component-inventory.md` 为准，逐项登记）；令牌绑定 + 三态动效 + `09-state-matrix.md` | `01`、`02`、`09`、`10` |
| P7 证据与回归 | `verification/FEA-06/**`（每页 headless 状态测试日志 + 截图/渲染证据 + 组件登记表）；全量 sln；两生成器 `--check`；`check.ps1`/`verify_pins` | AC8/AC9 |

## 验收标准

- [ ] **AC1 Shell + 响应式**：`TopBand`/`NavRail`/`StatusBand` 使用 `Nm.*` 令牌；17 个既有快捷键可达，1024/1280/1600 断点与空间映射已实现。分栏折叠、UI memento、200% DPI 与原生桌面验收未覆盖。 <<PARTIAL: 基础导航、断点与键盘路径已实现；折叠/状态恢复及原生 DPI 验收仍缺>>
- [ ] **AC2 Shelf**：实现书架网格/列表、搜索筛选、选择、拖入确认及加载/错误/只读等基础状态。回收站入口目前只有空面板；冻结 Host 端口不提供回收站恢复/删除操作，扫描进度也未细化到逐项。 <<PARTIAL: Host 无回收站操作端口，入口和完整状态矩阵尚未闭环>>
- [ ] **AC3 Workbench**：Region/Inspector/FilmStrip/批量基础视图、Draft 7 方法及 17 错误码到 UI 分类已接入。缺少 `pageBindingVersion` 时新建 Draft 会 fail closed；Run 投影/控制端口未提供，BatchMatrix 未绑定数据，工作台 9 行状态矩阵未全实现。 <<PARTIAL: Draft 与错误映射已接入，但页面绑定和 Run 端口缺失，完整状态矩阵未完成>>
- [ ] **AC4 Reader**：页导航、缩放、方向 memento 和进度写回已接入。双页第二图、滚动模式、工具条自动隐藏和源不可用只读警示仍缺。 <<PARTIAL: 基础阅读与进度写回已实现，冻结设计要求的部分交互和状态尚未完成>>
- [ ] **AC5 Settings**：外观设置经唯一 `AppearanceCoordinator` 保存，Provider/网络/备份/关于分组已承载。现有冻结端口缺少网络超时/并发及备份目录/频率字段；完整错误/部分状态矩阵未覆盖。 <<PARTIAL: 外观与分组已落地，但受现有端口字段缺口及状态矩阵覆盖限制>>
- [ ] **AC6 设计系统组件**：组件登记表列出 20 项规范组件及令牌、页面和测试；样式复用 `Nm.*` 令牌。部分组件尚未具备完整 normal/hover/pressed/disabled 状态，浮层开关状态也未全部实现。 <<PARTIAL: 组件清单与基础样式完成，规范要求的全组件状态覆盖仍不足>>
- [ ] **AC7 可访问性与动效**：实现主要 Tab 顺序、A11y 名称、高对比和 reduce-motion 路径。焦点环与三类 motion 状态覆盖不完整，且没有原生桌面验证。 <<PARTIAL: 基础可访问性与动效路径已实现，焦点环/分类动效及原生验收未闭环>>
- [x] **AC8 回归**：全量 sln build/test、Fluent 页面测试、DesignSystem 组件测试及 TokenGen/ThemeGen `--check` 均通过；全量 **1030 passed / 0 failed / 57 skipped**，相对基线 1022/0/57 新增 8 passed。 <<MET>>
- [x] **AC9 证据**：提交 build/test/生成器/治理日志、四页 Headless PNG、组件登记表、UIUX 结果与 SHA-256 索引；Canonical Evidence 固定到实现 commit。 <<MET>>
- [x] **AC10 范围纪律**：实现提交 37 个路径均在允许范围；scope audit 已提交。未改 Core/契约/schema/用户数据、冻结设计、生成物、组合根、selector 或 Current V2，未 push。 <<MET>>

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
| W-6 | 四页↔三空间↔左导航映射 | 按设计基线执行：顶栏「空间 1/2/3」（`04:13`），左导航随空间（书架空间=书架/回收站/导入 `05:21`）；**阅读器=`ReaderOverlay` 浮层（`07:3`），设置=ThemeStudio surface 承载外观组（`08:3`），两者不新增 SpaceId**；四页与空间映射以设计为准，FEA-06 不新增第五页 | FEA-06-scope-r1 P1-5；design v1.0.0 FROZEN |
| W-7 | 令牌生成归属 | G-1/G-1b/G-1c 由前置 1 生成，本卡只消费 | r1 P1-1 |
| W-8 | 页面状态清单 | 以 `09-state-matrix.md` 为唯一状态清单，AC2–AC5 逐页覆盖 | r1 P1-2 |
| W-9 | 写域扩张（处置 r1 P2-2） | 在 `Views/**`/`ViewModels/**`/`Shell/**` 之外追加 `Controls/**`、`Styles/**`、`Services/**`（四页所需的页面数据/导航适配器与外观组件）；不含 `App.axaml`/组合根（PREREQ-2 已冻结） | r1 写域审查；实现可行性 |
| W-10 | Owner 与交付方式（用户 2026-11-02） | Owner = **Codex**；Codex 可在 main 直接实现并提交单一实现 commit（只含 allowed_paths 内文件），**不得 push**；DSH 负责 Review Appointment、独立实现复核、集成验证与最终 push | 用户 2026-11-02 指派 |
| W-11 | 证据口径（处置 r1 P2-6） | 每页 ≥1 headless 状态测试（`AvaloniaFact`）+ 至少 1 张 headless 渲染截图（PNG，落 `verification/FEA-06/`）+ 组件登记表（Markdown）；日志含命令与 exit | r1 采证口径 |
| W-12 | 组合根依赖注入预置（处置 **scope-r2 P0**） | Fluent 壳的依赖注入由 **DSH 单点预置**：`App.axaml.cs` 的 Fluent 分支传入 `controller/appearance/themeManager`，`FluentShell.CreateRoot`/ctor 扩为可选参数并暴露只读属性 `HostController`/`Appearance`/`ThemeManager`；不改 V2/legacy 分支与 selector 语义。Codex 只**消费**这些实例（不得新建第二个 `HostController` 或 `AppearanceCoordinator`）；`App.axaml.cs` 仍不在 FEA-06 写域 | scope-r2 §2.1 建议①；PREREQ-2 唯一写者/sidecar 单实例语义 |
| W-13 | 控制台空间映射（处置 **impl-r1 P2-4**，DSH 裁决 2026-11-02） | `SpaceId.Console` **不得映射 Settings**：控制台空间承载 Workbench 第三视图「控制台」（最小 Run 控制台面板：运行状态/错误入口；无数据时显示「当前没有运行中的任务」，不得造假数据；完整 Run 数据由 FEA-07/FEA-10 承接，登记 residual）。**Settings 改为非空间入口**：顶部命令条「设置」按钮 + 左导航项（`08-page-settings.md:3`）；Shell 测试同步。返修按 `doc/reviews/FEA-06-impl-r1-adjudication.md` | impl-r1 P2-4；design `04:13`/`06:12`/`06:21`/`08:3` |

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-06-session-handoff.md`（随交接文档提交）。
- Review：待 DSH Appointment；实现 head `b0388df9ae2bb087649b44cf25a0921b2116934e` 尚无独立审查。
- 实际测试：见下表与 `verification/FEA-06/`；环境 Windows 11 / .NET 9 / Avalonia.Headless。
- 最终由 DSH 填写 `integration_commit`、完成资源核销与集成验证后决定终态；本次仅进入 `in_review`。

## 测试要求

| 场景/AC | 实际命令 | 环境 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC7 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests\NewManga.App.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~Fluent` | Windows 11 / .NET 9 / Avalonia.Headless | PASS：19 passed / 0 failed / 0 skipped | `verification/FEA-06/page-tests.log` |
| AC6 | `dotnet test apps\desktop-avalonia\tests\NewManga.DesignSystem.Tests\NewManga.DesignSystem.Tests.csproj --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --filter FullyQualifiedName~Fluent` | Windows 11 / .NET 9 | PASS：1 passed / 0 failed / 0 skipped | `verification/FEA-06/design-system-component-tests.log` |
| AC8 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | Windows 11 / .NET 9 | PASS：0 warnings / 0 errors | `verification/FEA-06/build.log` |
| AC8 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings` | Windows 11 / .NET 9 | PASS：1030 passed / 0 failed / 57 skipped；skip 因缺少 `NEWMANGA_CORECLIENT_SIDECAR_DIR` | `verification/FEA-06/full-test.log`、`skip-analysis.md` |
| AC8 | TokenGen `-- --check`；ThemeGen `-- --check` | Windows 11 / .NET 9 | PASS：均与生成物一致 | `verification/FEA-06/token-gen.log`、`theme-gen.log` |
| AC8/AC9 | `pwsh -NoProfile -File tools\governance\check.ps1`；`pwsh -NoProfile -File tools\governance\verify_pins.ps1` | Windows PowerShell | PASS：最终 in_review 检查通过（含治理提示）；冻结 pins 15/15 | `verification/FEA-06/governance-in-review.log`、`verify-pins-in-review.log` |
| AC9 | `python tools\governance\task_ledger.py --write` | Windows 11 / Python | PASS：ledger 已按 `in_review` 重建 | `verification/FEA-06/task-ledger-in-review.log` |
| AC9 | Avalonia.Headless 每页渲染截图与页面状态测试 | Windows 11 / Avalonia.Headless（SIMULATED） | PASS：Shelf/Workbench/Reader/Settings 各 1 张；非原生验收 | `verification/FEA-06/screens/`、`page-tests.log` |
| AC9 | UIUX `finalize` | UIUX Engine 1.3.3 | PARTIAL（exit 11）：独立 Review、L4 设计 Review、持久流程图与 NATIVE_APP 验收待补 | `verification/FEA-06/uiux/finalize.log`、`task-result.json` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-FEA06-AC1 | AC1 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/FluentShell.axaml.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `bdff9485eec7c81298cce2b4ee8d2e063e0a75d5ea6033314af31ef5bb37e095` | CANONICAL |
| EV-FEA06-AC2 | AC2 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `3bcb3af9d6045f175cae8fb439ff6d365ba9de05fc3bf08b52dcdaab6990e78e` | CANONICAL |
| EV-FEA06-AC3 | AC3 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/WorkbenchPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `48615c1a33803ab9efcc7a2c8c93bed47b8d489991d70b068e9a7dedafeda029` | CANONICAL |
| EV-FEA06-AC4 | AC4 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ReaderPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `2b5fc10a95e9f1fdbe20cc12e3f9f543a2400ada6d47ccbaf7925298f7026919` | CANONICAL |
| EV-FEA06-AC5 | AC5 | `apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `bb55cd59872e288ffc3da676900a784e9153e138d676c2aa71d11befd75dd53f` | CANONICAL |
| EV-FEA06-AC6 | AC6 | `verification/FEA-06/component-registry.md` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `a629145df96cdca76ca3703e8852d865810cc5077959115ae2854b02c267fff4` | CANONICAL |
| EV-FEA06-AC7 | AC7 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentPageTests.cs` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `43e26c38b63d602efbd3ba76b06a1f9596a28c24f96f2ac790d7ee531c4ba921` | CANONICAL |
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
| EV-FEA06-AC9 | AC9 | `verification/FEA-06/evidence-index.md` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `f43f0b44384c037948e63c9ee3c01da5a205d3a4cbeeea16d44219c43ced6317` | CANONICAL |
| EV-FEA06-SCREEN-SHELF | AC9 | `verification/FEA-06/screens/shelf.png` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `018af624d300e053b7276b702f7908e00426d432808eec810a6c8a4797f72c3f` | CANONICAL |
| EV-FEA06-SCREEN-WORKBENCH | AC9 | `verification/FEA-06/screens/workbench.png` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `4ea215345178215fb9e677dc71e0cae10bd2cad7251165752ae7cfb259d6ab41` | CANONICAL |
| EV-FEA06-SCREEN-READER | AC9 | `verification/FEA-06/screens/reader.png` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `26e7a47a240cce5698396dd06ec9c4eac7e53ce1e7dbf69c1ce9a1f773f08374` | CANONICAL |
| EV-FEA06-SCREEN-SETTINGS | AC9 | `verification/FEA-06/screens/settings.png` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `73ab84ad2807534ef39b186c74bea144bcf8e92f057d54ecc61b584c52b282cd` | CANONICAL |
| EV-FEA06-UIUX-COVERAGE | AC9 | `verification/FEA-06/uiux/coverage-matrix.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `a9d74fd319b806c823db7fb0ca19394f90a1258afa356fd264ad282ec37322c8` | CANONICAL |
| EV-FEA06-UIUX-GATES | AC9 | `verification/FEA-06/uiux/gate-results.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `dcdf1daf2139d78113cde29135d56531142fcbda942ffbdbdcc80aa6aa080b09` | CANONICAL |
| EV-FEA06-UIUX-REQUEST | AC9 | `verification/FEA-06/uiux/request.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `74c0edac9e66c700f9b8bd0289ccc7591aeeb323ac231749c66c80c219ea4c19` | CANONICAL |
| EV-FEA06-UIUX-TOOLLOGS | AC9 | `verification/FEA-06/uiux/tool-logs.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `8f32b1895125c37919ff9c83b8056d2e4974b101c9f6a1c916f84971ba7d971d` | CANONICAL |
| EV-FEA06-UIUX-MANIFEST | AC9 | `verification/FEA-06/uiux/evidence-manifest.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `dd1db40b8b1bef9318039d683f4aface7c3f80612a1708482e8f7637bbabeb4b` | CANONICAL |
| EV-FEA06-UIUX-FINALIZE | AC9 | `verification/FEA-06/uiux/finalize.log` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `bde655d84ede10046dae7df6c03e0b180b46e6cf6ce78b2274ad8e4ed43c1b88` | CANONICAL |
| EV-FEA06-UIUX-RESULT | AC9 | `verification/FEA-06/uiux/task-result.json` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `cebe22f92c522074343ec4303f176c42bfe4c3a3e003f4673fc0502b96fb267f` | CANONICAL |
| EV-FEA06-AC10 | AC10 | `verification/FEA-06/scope-audit.md` | `b0388df9ae2bb087649b44cf25a0921b2116934e` | `cec04b8135b13549f8c0114b43fe1259b00e5e335538cddccd6166cd8da90ea0` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 无 linked worktree；main checkout `G:\CODEX\New Manga` | NOT_APPLICABLE | 同一仓库 checkout | `b0388df9ae2bb087649b44cf25a0921b2116934e` | 直接在 main 实施；不创建/删除 worktree。 |
| verification artifacts | `verification/FEA-06/**` | PRESERVE_REFERENCED | 同路径 | `verification/FEA-06/evidence-index.md` | 证据被 Task 与 Handoff 引用；交 DSH 在集成窗口复核资源处置。 |
| task-env / user data | 未创建 / 未访问 | NOT_APPLICABLE | - | - | 未写产品数据或用户源文件；无独立环境需清理。 |

## Closeout Record

- 实施交付：2026-11-02 / Codex；DSH 集成与 Task closeout 尚未执行。
- canonical_evidence_status：`complete`；resource_closeout_status：`pending`（由 DSH 在 approved 集成窗口核销）。
- 删除、迁移、归档数量/字节数：0；未执行清理或数据迁移。
- 未关闭项：`AC1–AC7` 有明确部分完成项，保留待 Review/后续裁决；Review 与集成尚未完成。
- 当前指针：STATUS 与 Plan 已更新到 `in_review`；rolling checkpoint 无需切换；当前 Task 仍由 STATUS 指向。
