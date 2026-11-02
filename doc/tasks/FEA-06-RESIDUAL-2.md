---
id: FEA-06-RESIDUAL-2
title: Fluent 视觉残项补做（D-8 decorative + I-4 视觉格）
kind: implementation
governance_version: 3
status: ready
approval: scope_r1_change_requested_2026-11-03（D-9 独立子 agent，P0=0/P1=5/P2=6；按附录 A 重写为范围 v2，待 scope-r2 复核冻结）
suggested_owner: zcode
owner: zcode
reviewer: scope-r1 changes_requested（doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md，D-9 独立子 agent）；待 scope-r2 复核
depends_on:
  - FEA-06-RESIDUAL-1
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-2.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Styles/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Theming/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06-RESIDUAL-2/**
  - doc/handoffs/FEA-06-RESIDUAL-2-*.md
  - doc/reviews/FEA-06-RESIDUAL-2-*.md
---

# FEA-06-RESIDUAL-2：Fluent 视觉残项补做（范围 v2）

## 来源与基线
- 前序卡 `FEA-06-RESIDUAL-1` 已 `closed_with_limitations`（impl-r4 approved P0=0/P1=0/P2=1；集成 `669a4ae02`；无过滤全量 **1245/0/57**）；AC2 PARTIAL 的残项转本卡。
- 范围 v1 经独立 scope 复核 **changes_requested**（`doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md`，P0=0/P1=5/P2=6）；本 v2 按该报告附录 A 逐格重写，待 scope-r2 复核后冻结。
- 冻结设计 `doc/design/fluent-v1/`（FROZEN v1.0.0）：02-motion §1–§4、03-accessibility §3–§4、10-component-inventory §1–§3、07-page-reader、01-design-tokens §2.3。**不重冻结设计、不新增组件/颜色/资产**。

## 范围 v2（穷尽、互斥、可验证）

### A. IN-1（D-8 decorative，全部 IN，3 子项）

共同约束（每子项均适用）：仅用既有令牌（`Nm.Color.Bg.*`、`Nm.Material.*`、`Nm.Opacity.*`、`Nm.Elevation.*`）与既有 `NmIcon`；不新增图片/字体/新颜色/新几何资产；装饰层 `IsHitTestVisible=false`、不触发重排、不遮挡内容；`reduce` / `auto`+系统关 / `category=关` 三态等价降级；窗口失焦/不可见暂停；自动化可全关；detach 后停帧、无计时器/帧回调泄漏；真实播放用生产帧源采样首/中/尾，测试 clock 仅做边界断言。

| 子项 | 场景 | full/auto(系统开) | reduce / auto(系统关) / category-off | 断言 | 视觉证据 |
|---|---|---|---|---|---|
| IN-1.1 | 书架背景渐变 | 8s 循环 | 静态背景、**不创建动画对象** | 时长=8s、循环、只改 Brush/Opacity、不重排；内容区像素无位移 | 3 张（full 首/中、reduce）+ 真实帧源采样 |
| IN-1.2 | 阅读器翻页装饰粒子 | 400ms（翻页触发一次） | **不创建粒子层** | 400ms 内结束、不拦截命中、不遮挡页面图、可读性断言 | 2 张（full 中帧、reduce） |
| IN-1.3 | 空态插画漂浮 | 6s 循环 | 静态插画 | 6s 循环、仅 Transform/Opacity；标题/提示/主按钮可点；`NmIcon` 派生 | 2 张（full 中帧、reduce）+ 交互断言 |

视觉签署：独立上下文 Reviewer（非实现者）逐图签署；未签署 = NOT_RUN；不得以类/样式/动画对象存在计 PASS。

### B. IN-2A（headless 有效属性断言，17 组；PASS=解析后属性等于设计令牌）

SurfaceCard（hover/selected/disabled）、BookCard（disabled）、BookRow（disabled）、PrimaryButton（disabled）、SecondaryButton（disabled）、DangerButton（disabled）、IconButton（hover/checked）、ToggleSwitch（disabled）、Slider（normal/hover/disabled）、SegmentedControl（selected/unselected/hover/pressed）、TabStrip/TabItem（hover）、SearchField（focus）、SettingsField（error/disabled）、RegionBox（hover）、ContextMenu（disabled item）、Tooltip（opened）、AlertBanner（**按 DSH 裁定枚举**；若采用 `StatusKind` 九值则除 Blocked 外八值补齐）。

### C. IN-2B（像素 PNG + 视觉签署）

IN-2A 全部组 × 状态 + EmptyState/ErrorState/Skeleton + ChapterList/PageThumbStrip + ReaderPage/ReaderProgressBar（单页 only）+ Dialog/Drawer 开合 + CommandPalette 空/结果；每组件每状态 1 张，固定视口/主题；`reduce` 对照仅对 IN-1 三场景强制。像素格不得替代 A.2 的属性断言。

### D. OUT（不在本卡，写明理由）
- PrimaryButton `loading`、Dialog 危险/加载、CommandPalette `loading`：组件无变体或无异步数据源；新增状态属功能/组件变更，假 loading = 假数据。
- 任何需新增组件状态/设计资产的项：走 v1.1 重冻结。

### E. BLOCKED（逐项恢复条件）

| 格 | 阻塞 | 恢复条件 |
|---|---|---|
| BatchMatrix 七状态/吸顶表头、RunProjectionBar 投影态 | FEA-10（B-2） | Run/批量端口 done + 契约冻结 |
| ReaderPage 双页第二图/滚动模式 | FEA-09/11（B-3） | 阅读器数据面端口 done |
| RegionBox 冲突态 | FEA-10（B-7） | 冲突投影端口 done |
| 书架满态统计 | FEA-12（B-6） | 真实统计数据面 |
| Console 投影/9 行数据 | FEA-10/12（B-1/B-2） | 对应端口 done |
| 完整 Tab 遍历、原生 a11y、200% DPI、原生桌面/截图 | B-5/D-1 | 硬件可用或用户书面 waiver |

## 证据形式（R1-006 口径）
- 默认测试运行**零仓库写入**（`git status` 干净）；仅显式开关 `NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1` 写 `verification/FEA-06-RESIDUAL-2/visuals/**`；**禁止写 `verification/FEA-06/**`**。
- 逐图元数据：head、场景/组件/状态、mode（full/reduce/auto-关/category-关）、视口尺寸、帧位置（首/中/尾）、主题（light/dark）、生成命令与 EXIT。
- 旧 FEA-06 四 PNG SHA（对照基线）：reader `8533c263…`、settings `fd30b166…`、shelf `307f8f67…`、workbench `d5d878bb…`（完整值见 scope-r1 附录 A.6）。

## allowed_paths 说明
保留 v1 路径；IN 落点限定在 Fluent 类包装/覆盖（`Views/Fluent/**`、DesignSystem `Styles|Theming`、测试）。若某格无法在域内实现，移入 OUT 并在 Handoff 说明，不得擅自扩域或改共享控件/主题（需 DSH 登记扩域理由）。

## 验收（冻结后实施）
```
dotnet build apps\desktop-avalonia\NewManga.sln --nologo
dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo
# 视觉证据（opt-in，写本卡 visuals/**）：
$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1; dotnet test ... (同上)
pwsh -NoProfile -File tools\governance\check.ps1
pwsh -NoProfile -File tools\governance\verify_pins.ps1
```
基线 1245/0/57 只增不减；旧 PNG 4×SHA 不变；TokenGen/ThemeGen `--check`；不 push；不改 Current V2/生成物/冻结设计。

## 实现约束
- 不改 FEA-07 稳定窗口 seam、共享契约、Current V2、组合根、`FrontendSelector`、生成物、冻结设计字节。
- 视觉实现为 ZCode 主责；实施后由独立上下文 Reviewer 做视觉与实现复核（Reviewer 不参与实现）；DSH 负责范围冻结、findings 处置与集成验证。
