---
id: FEA-06
title: Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）
kind: implementation
governance_version: 3
status: proposed
approval: pending_scope_review_r2（用户 2026-11-02 指派 Codex 实施）
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
base_commit: 5a47170096bb28c42d108756f522cf4250cab983
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
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

## 任务拆解（按页 + 组件）

| 项 | 内容 | 设计输入 |
|---|---|---|
| P1 Shell | 顶条 `TopBand`/左导航 `NavRail`/状态条 `StatusBand`/命令条；17 全局快捷键（`ShellCommands` 既有）；三断点 1024/1280/1600；z-order；分栏折叠；空间 1/2/3 与四页映射（W-6） | `04-layout-responsive.md`、`03-accessibility.md` |
| P2 Shelf | `BookCard`/`BookRow`/`ChapterList`/`PageThumbStrip`；网格/列表、筛选、选择、右键、拖入、回收站入口；本页状态全量（见 AC2） | `05-page-shelf.md` |
| P3 Workbench | Region 列表/画布（`RegionBox`）/Inspector（`Drawer`）/FilmStrip（`StreamingThumb`）/批量栏（`BatchMatrix`）/`RunProjectionBar`；Draft 7 方法接入（Open/Patch/Prepare/Apply/Status/Discard）；本页 8 态 | `06-page-workbench.md` |
| P4 Reader | `ReaderPage`/`ReaderProgressBar`；页导航/缩放/全屏/键盘滚轮→翻页、缩放/双击、方向 memento；进度保存接 `IReaderProgressSink`（FEA-04） | `07-page-reader.md` |
| P5 Settings | `SettingsGroup`/`SettingsField`；`08-page-settings.md:41-58` 字段逐字（frontendId/visualThemeId、motion.mode/categories、corners/material、layout.*、followSystemAccent、schemaVersion、Provider/网络/备份/关于）+ 保存/校验/错误态 | `08-page-settings.md`、C-03 §2.2 |
| P6 设计系统消费 | 15–20 个新增/外观化组件：`SurfaceCard`、`Drawer`、`Dialog`、`EmptyState`、`ErrorState`、`Toast/InfoBar`、`BookCard`、`BookRow`、`RegionBox`、`BatchMatrix`、`RunProjectionBar`、`SettingsGroup`、`SettingsField`、`PrimaryButton`、`SecondaryButton`、`DangerButton`、`SearchField`、`TabStrip`、`SegmentedControl`（以 `10-component-inventory.md` 为准，逐项登记）；令牌绑定 + 三态动效 + `09-state-matrix.md` | `01`、`02`、`09`、`10` |
| P7 证据与回归 | `verification/FEA-06/**`（每页 headless 状态测试日志 + 截图/渲染证据 + 组件登记表）；全量 sln；两生成器 `--check`；`check.ps1`/`verify_pins` | AC8/AC9 |

## 验收标准

- [ ] **AC1 Shell + 响应式**：`TopBand`/`NavRail`/`StatusBand` 用令牌（`Nm.Size.TopBand`/`TreeWidth`/`StatusBandPage`、`Nm.Corner.Fluent.*`，无裸值）；17 个既有冻结快捷键可达（全局 10 + 空间级 7：Tab + J/K/[/]/Shift+[/]）；1024/1280/1600 三断点布局、折叠、z-order 与 `04-layout-responsive.md` 一致；空间 1/2/3 与四页映射符合 W-6。 `<<TODO>>`
- [ ] **AC2 Shelf**：网格/列表/筛选/选择/右键/拖入/回收站入口；**`09-state-matrix.md` 书架列全部行实现**（空〔首次空态+导入主按钮〕/ 空〔筛选后，保留筛选+清除筛选〕/ 载入〔6 封面骨架+「正在读取书架…」〕/ 错误〔错误卡+重试+控制台入口〕/ 满〔网格/列表+统计〕/ 部分〔扫描中进度条；已就绪项可用〕/ 只读〔顶部警示；导入/删除禁用〕/ 运行中〔扫描/导入进度，与部分同态不重复计数〕；冲突列「—」）；`BookCard`/`BookRow`/`ChapterList`/`PageThumbStrip` 令牌与状态符合 `10`。 `<<TODO>>`
- [ ] **AC3 Workbench**：Region 选择/`RegionBox` 四态/Inspector/FilmStrip/批量栏；**Draft 7 方法接入**（`IHostController`，W-2）；**错误映射表冻结**（17 码→Category→UI：validation=行内提示、not_found=刷新/清选、conflict=重读提示、unavailable=可重试横幅、internal=错误卡在位显示并保留旧 UI/上一帧、不清屏）；**`09-state-matrix.md` 工作台列全部 9 行实现**（空〔未选章节→跳书架；批量无 Run→「开始处理」〕/ 空〔批量筛选无结果→保留 chips+清空选择〕/ 载入〔画布/检查器骨架+「读取中」〕/ 错误〔错误卡+重试；画布保留上一帧〕/ 满〔画布+检查器+操作条；未保存圆点〕/ 部分〔未决确认模态 保存/丢弃/取消；flush 失败留旧 UI〕/ 冲突〔冲突条+查看对照；应用禁用；不自动合并〕/ 只读〔检查器禁用+转移入口〕/ 运行中〔Run 投影条+暂停/停止/重试；intent key 复用〕）。 `<<TODO>>`
- [ ] **AC4 Reader**：页导航/缩放/全屏/双击/键盘滚轮/方向 memento；进度保存接 `IReaderProgressSink`；**`09-state-matrix.md` 阅读器列全部行实现**（空〔「本章节暂无页面」+返回〕/ 载入〔上一页保留+进度环〕/ 错误〔错误占位+重试+返回〕/ 满〔正常阅读；条自动隐藏〕/ 部分〔缺页占位「页面未就绪」+可重试；其余页可翻〕/ 只读〔只读警示，源不可用〕/ 运行中〔进度写回中，不阻塞〕；筛选/冲突列「—」）；`ReaderPage`/`ReaderProgressBar` 令牌与 `07` 一致。 `<<TODO>>`
- [ ] **AC5 Settings**：`08-page-settings.md:41-58` 字段逐字渲染（含深/浅 `appearance`、对比度 `contrast`、`frontendId`/`visualThemeId`、`motion.mode`/`motion.categories`、`corners`/`material`、`layout.*`、`followSystemAccent`、`schemaVersion`、Provider/网络/备份/关于；C-03 §2.2 字段名一致）；保存/校验/错误态；**`09-state-matrix.md` 设置列全部行实现**（空〔防御空态+重试〕/ 空〔搜索无结果→「无匹配」+清空搜索〕/ 载入〔卡片骨架；分组列表先显示〕/ 错误〔顶部错误条+重试；保存失败保留输入〕/ 满〔全分组可编辑〕/ 部分〔字段禁用+原因 Tooltip；Fluent 材质在 Current 下〕/ 只读〔保存禁用；可浏览〕；冲突/运行中列「—」）；不越权写 `presentation-settings.json`（经 coordinator）。 `<<TODO>>`
- [ ] **AC6 设计系统组件**：15–20 个新增/外观化组件逐项登记（名称、令牌依赖、状态、尺寸、测试），至少覆盖 normal/hover/pressed/disabled 与浮层开/关；无裸值；不复制业务组件（复用 DesignSystem 既有）。 `<<TODO>>`
- [ ] **AC7 可访问性与动效**：Tab 顺序、A11y 名称、焦点环可见、高对比（`03-accessibility.md`）；`motion.mode=reduce` 降级、`motion.categories=off` 0ms、full 差异（`02-motion.md`）。 `<<TODO>>`
- [ ] **AC8 回归**：全量 sln 不退化（**基线 1022/0/57**）+ App.Tests 新增用例（每页 ≥1 状态测试 + 组件测试）；`TokenGen/ThemeGen -- --check` up to date。 `<<TODO>>`
- [ ] **AC9 证据**：`verification/FEA-06/**` 下 build/test/生成器/治理日志 + 每页 headless 渲染截图（PNG）+ 组件登记表；Canonical Evidence 逐项 commit+sha256。 `<<TODO>>`
- [ ] **AC10 范围纪律**：不改 Core/契约/schema/用户数据；不改 `doc/design/fluent-v1/**`（改动即 v1.1 重冻结）；不改生成物（`NmKeys.g.cs`/`Tokens.Global.axaml`/`TokenMap.md`/`*.nmtheme`）；不 push。 `<<TODO>>`

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

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC7 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests`（Avalonia.Headless；每页状态测试 + 组件测试 + Shell 断点） | .NET 9 / Avalonia.Headless | NOT_RUN | 待补 |
| AC6 | `dotnet test apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests`（新组件 + 令牌绑定） | .NET 9 | NOT_RUN | 待补 |
| AC8 | 全量 sln build/test（基线 **1022/0/57**）+ `TokenGen -- --check` + `ThemeGen -- --check` | 全量 + 生成管线 | NOT_RUN | 待补 |
| AC8/AC9 | `pwsh tools/governance/check.ps1` + `verify_pins.ps1` | 治理 | NOT_RUN | 待补 |
| AC9 | headless 渲染截图（PNG）+ 每页状态日志 | Avalonia.Headless | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）；资源处置在收口时登记。

## Closeout Record

- 待关闭时填写。
