---
id: FEA-06-RESIDUAL-2
title: Fluent 视觉残项补做（D-8 decorative + I-4 视觉格）
kind: implementation
governance_version: 3
status: done
approval: scope-r3_approved_2026-11-03（ZCode CLI 独立上下文；reviewed_head b201d4489；P0=0/P1=0/P2=7）；范围 v3 冻结，按 IN-1.1/IN-1.2/IN-2A/IN-2B 实施
suggested_owner: zcode
owner: zcode
reviewer: scope-r3 approved（ZCode CLI）；impl-r1 changes_requested（P0=1/P1=6/P2=12）；**impl-r2 changes_requested**（D-9 独立子 agent，P0=0/P1=6/P2=12；doc/reviews/FEA-06-RESIDUAL-2-impl-r2.md；逐图 15 PASS/19 REJECT）——R2R2 返修中
depends_on:
  - FEA-06-RESIDUAL-1
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
branch: main
worktree: G:\CODEX\New Manga
integration_commit: d1df8035a5ea61921bb01b84494de0fd59f805e7
delivery_head: 832103393（R2R3 交付：NavRail/StatusBand 态、可辨渐变、danger 对比、失焦生命周期、reduce 粒子清理；172 PNG；全量 1289/0/57；impl-r4 复核中）
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-06-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-2.md
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/**
  - apps/desktop-avalonia/src/NewManga.App/Controls/FluentUi.cs（DSH 扩域理由：IN-1.1/1.2 装饰层工厂与 IN-2A 控件构造落点；不新增产品能力）
  - apps/desktop-avalonia/src/NewManga.DesignSystem/Themes/Controls/**（DSH 扩域理由：TabItem hover/Button 基础态令牌层覆盖；仅样式令牌，不改控件行为）
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


视觉签署：独立上下文 Reviewer（非实现者）逐图签署；未签署 = NOT_RUN；不得以类/样式/动画对象存在计 PASS。

### B. IN-2A（headless 有效属性断言，按 R2R-002 收窄为 16 组 + AlertBanner 特殊组；PASS=解析后属性等于设计令牌；逐格期望令牌表由实施 Handoff 冻结并逐行核对）

SurfaceCard（hover/selected/disabled）、BookCard（disabled）、BookRow（disabled）、PrimaryButton（disabled）、SecondaryButton（disabled）、DangerButton（disabled）、IconButton（hover/checked）、ToggleSwitch（disabled）、Slider（normal/hover/disabled）、SegmentedControl（selected/unselected/hover/pressed）、TabStrip/TabItem（hover）、SearchField（focus）、SettingsField（error/disabled）、RegionBox（hover）、ContextMenu（disabled item）、Tooltip（opened）、AlertBanner（**DSH 裁决 D-11**：按既有 `StatusKind` 九值覆盖——Blocked 已有断言，补充 Done/Failed/Queued/Running/Stale/Skipped/NotStarted/Locked；设计四态与 StatusKind 的映射写入证据；不新增组件变体、不改 Feedback.cs）。

### C. IN-2B（像素 PNG + 视觉签署）

IN-2A 全部组 × 状态 + EmptyState/ErrorState/Skeleton + ChapterList/PageThumbStrip + ReaderPage/ReaderProgressBar（单页 only）+ Dialog/Drawer 开合 + CommandPalette 空/结果；每组件每状态 1 张，固定视口/主题；`reduce` 对照仅对 IN-1 三场景强制。像素格不得替代 A.2 的属性断言。

### D. OUT（不在本卡，写明理由）
- **IN-1.3 空态插画漂浮**：`EmptyState` 无图标槽且注释 *No illustrations*，`FluentUi.Empty` 在 App/Controls 域外、无既有插画资产/造型定义；新增槽位或资产属组件/设计变更 → OUT 至 v1.1 重冻结（R2R-002）。
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
- 冻结路径如上（含 2 项 DSH 登记扩域理由）；**分类冻结**：IN/OUT/BLOCKED 由本卡固定，实施中发现的不可行格必须报告 DSH 裁决，先停该格、不得自行改分类或扩域。

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

## 范围 v3 决议（scope-r2 处置，2026-11-03）

### DSH 裁决（Lead/Architect 权限内）
- **D-11（AlertBanner）**：按既有 `StatusKind` 九值覆盖，不新增组件变体、不改 `Feedback.cs`；设计四态↔StatusKind 映射写入实施证据。若 Reviewer 认为映射仍不可接受，可由 scope-r3 要求改为设计四态 OUT（不阻塞其他 IN）。
- **D-12（IN-1.3）**：空态插画漂浮 **OUT** 至 v1.1（`EmptyState` 无图标槽/无插画资产；新增槽位=组件变更）。
- **D-13（扩域）**：登记 `NewManga.App/Controls/FluentUi.cs`（装饰层工厂）与 `DesignSystem/Themes/Controls/**`（TabItem hover/Button 基础态令牌覆盖）两项，理由见 allowed_paths；不新增产品能力、不改控件行为。
- **D-14（已裁决 2026-11-03，Codex 裁决 A）**：`StatusCatalog.ColorKey(NotStarted)` 应改为 `Nm.Color.Text.Secondary`（Secondary 对比度≥4.5:1，Disabled 不足）；已释放后续卡 `D-14-STATUS-COLOR-FIX`（ready），本卡不扩域、不写达成。原记录：`StatusCatalog.ColorKey(StatusKind.NotStarted)` 返回 `Nm.Color.Text.Disabled`，而 `Controls.Status.axaml` 的 StatusGlyph.notstarted 使用 `Nm.Color.Text.Secondary`（注释要求 ≥4.5:1）。DSH 推荐：**改 StatusCatalog 对齐 Text.Secondary**（语义/可读性一致；属 DesignSystem/Controls，超出本卡 allowed_paths，需在后续卡或扩域中实施），本卡测试按样式权威断言并在交叉断言对 NotStarted 特判。
- **D-10/R4-001 权威链**：D-10 的 R1-001 三项动画已由 `033c8b4b9`交付并经 impl-r2/r3/r4 复核；R4-001 由 `current-evidence-index.md` + 集成日志处置；本卡不重复认领。

### 分类完整性（R2R-003 闭合）
| 矩阵/组件 | 分类 | 落点 |
|---|---|---|
| TopBand / NavRail / StatusBand 默认/紧凑/错误态 | IN | IN-2B 像素格（每态 1 张，固定视口/主题） |
| StreamingThumb | IN | IN-2B 像素格（懒加载态用静态占位，无假数据） |
| EmptyState / ErrorState / Skeleton | IN | IN-2B（含空/错误/骨架各 1 张） |
| ChapterList / PageThumbStrip | IN | IN-2B |
| ReaderPage / ReaderProgressBar（单页 only） | IN | IN-2B；双页/滚动 BLOCKED B-3 |
| Dialog / Drawer 开合 | IN | IN-2B（开/关各 1 张） |
| CommandPalette 空/结果 | IN | IN-2B；loading OUT |
| IN-2A 16 组 + AlertBanner | IN | 有效属性断言 |
| BatchMatrix/RunProjectionBar/RegionBox 冲突/满态/Console 投影 | BLOCKED | 见 E 表 |

### IN-2B 逐图清单与证据命令
- 清单：以上 IN 像素格 + IN-1.1/1.2（full 首/中/尾、reduce 对照）逐项列出文件名、组件、状态、mode、视口、主题、帧位置，形成 `visual-inventory.md` 并逐图签署。
- 证据命令（写入手册/Handoff）：`$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS=1; dotnet test ...`；默认零写入；旧 FEA-06 四 SHA 全值对照（reader `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2`、settings `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162`、shelf `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a`、workbench `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5`）。
- 证据日志格式（R2S-010）：shell/host、head、命令、逐程序集计数（含 1245/0/57 与 57 skip 原因）、EXIT、差值；禁止过滤运行冒充全量。
- IN-1 附加：高对比下装饰层仍仅用令牌且无对比度回退（03 §4）；对比度/可读性断言写入证据。

### 禁止范围与测试要求（R2S-011）
- 禁止：Core/契约/schema/用户数据/生成物 `DesignSystem/Generated/**`/冻结设计 `doc/design/**` 字节/组合根/`FrontendSelector`/Current V2；不改 FEA-07 seam；不 push；不写真实 `%APPDATA%`。
- 测试：新断言只增不减；全量无过滤 ≥1245/0/57；PNG 默认零写入；视觉格必须属性+像素双证据并独立签署；NOT_RUN 不得计 PASS。

### AC 表（本卡）
- [x] **AC-1（IN-1.1/1.2 三态降级/暂停/无泄漏/视觉签署）**：行为测试、真实帧与逐图签署通过（172 图 172 PASS）。 <<MET>>
- [x] **AC-2（IN-2A 16+1 组有效属性逐格）**：解析后属性=令牌断言通过（15/15）。 <<MET>>
- [x] **AC-3（IN-2B 像素格+独立签署）**：172 图 172 PASS/0 REJECT（impl-r4 独立签署）。 <<MET>>
- [x] **AC-4（证据/回归/禁止范围/生成器/check/pins/旧 SHA）**：integration log PASS。 <<MET>>
- BLOCKED：B 表项与 B-5/D-1 不写达成。
## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-RES2-INTEGRATION | AC1–AC4 | `verification/FEA-06-RESIDUAL-2/integration-verification.log` | `-` | `92a7c8573d3570ae88209bc535c7de403ae35aa2e0a75e9a3e9b9b11f10bac9c` | CANONICAL |
| EV-RES2-IMPLR4 | AC1–AC4 | `doc/reviews/FEA-06-RESIDUAL-2-impl-r4.md` | `d1df8035a` | `9aa51c68ecec8507cf30be08a215ef1096444594a24084293bc3a20c325c2f33` | CANONICAL |
| EV-RES2-HANDOFF | AC1–AC4 | `doc/handoffs/FEA-06-RESIDUAL-2-r2r3-17a26d552.md` | `832103393` | `65455671ac931b2d6dedbfa0d4ac7ee8fc11a7b57ff90a869910a4b814ec6455` | CANONICAL |
| EV-RES2-INVENTORY | AC3 | `verification/FEA-06-RESIDUAL-2/visuals/visual-inventory.md` | `c70d5c348` | `e76b2f5fed7a80fc5f52ce2e28dd35b656e8a931f3884781f006098cfbffed74` | CANONICAL |
| EV-FLIP-01 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/expected-tokens.md | - | 5ed92d0a6c564329675584d34d975e48e639ba6f1368d0c45b6777f2058da0a2 | CANONICAL |
| EV-FLIP-02 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/impl-in1-verification.log | - | 10fe72ef77e990fcd2159b1931b07d5fa1223645f15e3041f53b70343db353ae | CANONICAL |
| EV-FLIP-03 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/impl-in2a-verification.log | - | 2bc4295a39ec461100abbf8f93775b33b08ffe593ff9b5cad54208dc2dc121a2 | CANONICAL |
| EV-FLIP-04 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/impl-in2b-verification.log | - | 2c96aee5aab98f0676d98d0b7dbbfc381d1e245eebd66fe2647589a8231ccd75 | CANONICAL |
| EV-FLIP-05 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/impl-r2-rework-verification.log | - | 040593fcc1b008c08e82c225c375890c5dff41ecac047b24aa408af85526cedc | CANONICAL |
| EV-FLIP-06 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/impl-r3-rework-verification.log | - | 3f7bc9ab88aa1c9fb6a8881af2e0b934b608f093fcdf21a48b7fe3252ce9635e | CANONICAL |
| EV-FLIP-07 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r2-checkpoint.md | - | 016556da5b6ad14a6191ec65bb839142c75f5270971cd8dd7d92a783673600de | CANONICAL |
| EV-FLIP-08 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r2-findings-disposition.md | - | 36ae666c998c3d8ad1e0ece7f8a4b25efbbec2bed50cad10a705d40a6b3d7790 | CANONICAL |
| EV-FLIP-LIST-001 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r3-checkpoint.md | - | b0fcbce601109331dd9f5f4fd43e9f3aefba1e5b5e3f2adbfacc09c62cbf95b3 | CANONICAL |
| EV-FLIP-LIST-002 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r3-evidence-audit.md | - | 1c4a1782fc6c5edfa77bb6dc9a9fefb3dd563ae7cbead582c6b443d4d8b779f3 | CANONICAL |
| EV-FLIP-LIST-003 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r3-evidence-audit.py | - | b94b48811bbe2db817d724741c2e544ec0274d4edb7fc28e0ec56c06b0ced766 | CANONICAL |
| EV-FLIP-LIST-004 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/r2r3-findings-disposition.md | - | ea1218d9e2f663f4a704d16b67e20c4604be9ca5ba18e07b2b6aefacfab8093b | CANONICAL |
| EV-FLIP-LIST-005 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visual-qa.md | - | ec61e4d44ceb619a81924cbd1021cec6ee1372ddbb7269c3b7ae5bac044657f8 | CANONICAL |
| EV-FLIP-LIST-006 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--blocked--full--dark.png | - | 889624c7872462760cc7545756717001ea63349fd747c19b4b39b22bc77a5b24 | CANONICAL |
| EV-FLIP-LIST-007 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--blocked--full--light.png | - | 5d540e07adc5dcda6252092cb9e7b01708fbb2079d4755bddc412378f623154a | CANONICAL |
| EV-FLIP-LIST-008 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--done--full--dark.png | - | 7a4d26627e72ace2020ff5ea0e51adc970e4b03184e30a8acbd5fa1386c8474e | CANONICAL |
| EV-FLIP-LIST-009 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--done--full--light.png | - | 163a6a8d34bc3115045d0ca15df288d686880733d038319321a454bdef346cf8 | CANONICAL |
| EV-FLIP-LIST-010 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--failed--full--dark.png | - | 4e795504d6985ae9096333d8fb4eef07d5619a75dc5c8456669ac7b0871da9b0 | CANONICAL |
| EV-FLIP-LIST-011 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--failed--full--light.png | - | c0c0ff3836fba3fceb4f8a4bc58423f3d8fb0e77d10c94e7b53abbdf4376c719 | CANONICAL |
| EV-FLIP-LIST-012 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--locked--full--dark.png | - | dd5a7ffc3450eeeb9dbb85065152f8f1c5a3714caba00d585420077e5f71a78a | CANONICAL |
| EV-FLIP-LIST-013 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--locked--full--light.png | - | bc5b80643145d8192e36d9b3f1a81ad4d3db0c1212559f9aaaa0343b57e446e7 | CANONICAL |
| EV-FLIP-LIST-014 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--notstarted--full--dark.png | - | bbaa2d452fc25923a23d2ad06a4c4f75fbe5a04a8d650fb4cb51b267db021eef | CANONICAL |
| EV-FLIP-LIST-015 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--notstarted--full--light.png | - | e2154725e7c1eae2a64f9e84a8b8cba298bdaa5fe74cb08b04a793e1f1d61f3a | CANONICAL |
| EV-FLIP-LIST-016 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--queued--full--dark.png | - | 41f70aa437e62c3463760aab8ded163ee5bcc76b12f609c13370eebae3d6b0c5 | CANONICAL |
| EV-FLIP-LIST-017 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--queued--full--light.png | - | 0f10612d149089d0d9aed4ee66177f239f1fa9b67f704bd96f2b0381c42b53fb | CANONICAL |
| EV-FLIP-LIST-018 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--running--full--dark.png | - | 99c5e3c53622e072898c86ea2aae0d2029d9d4e0b7fd8b83c35f0719f7356ce2 | CANONICAL |
| EV-FLIP-LIST-019 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--running--full--light.png | - | 4b694feb9fd9888e13eec5e5fe60bc49b2c82469c5486bbb123d61db9e232e11 | CANONICAL |
| EV-FLIP-LIST-020 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--skipped--full--dark.png | - | a0ffe5811f77b4772115d3455cc443e94f938f6cf57c4f7a3eae992b073da157 | CANONICAL |
| EV-FLIP-LIST-021 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--skipped--full--light.png | - | c8bb612c824489e5a896f5e3aa2138c32550a2f30df26f390fbdd43c689331e1 | CANONICAL |
| EV-FLIP-LIST-022 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--stale--full--dark.png | - | c3bc9b631b8eb5b51282a81e0c7fcfebf274fda9bb3effaecb3a105b3145afca | CANONICAL |
| EV-FLIP-LIST-023 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--alert-banner--stale--full--light.png | - | a87e56fd424452afbec7746b1fb573ce28f317f00d5d075dc65c0fba8baeb64b | CANONICAL |
| EV-FLIP-LIST-024 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-card--default--full--dark.png | - | 2b49270515c35d9d25a4ed2af95627d95ec92ec6df94e2abdfa8f43fca7567b7 | CANONICAL |
| EV-FLIP-LIST-025 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-card--default--full--light.png | - | 4155acd86a1b6a0fe18a8ca2adbd0eda43dc88665f52811e56531d94c23458d8 | CANONICAL |
| EV-FLIP-LIST-026 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-card--disabled--full--dark.png | - | a379dba17d8109c2da45f7bddf371ae47dd8bd9db5d3f7e22baa7169f88594bc | CANONICAL |
| EV-FLIP-LIST-027 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-card--disabled--full--light.png | - | 611bd5b99caf77161b02dabc5a81d92113e924141b54e036423060453286005e | CANONICAL |
| EV-FLIP-LIST-028 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-row--default--full--dark.png | - | d4be22a5228aa3f8930cd8e2ae25789cdcd843780146a68d1d5f61228a89afdf | CANONICAL |
| EV-FLIP-LIST-029 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-row--default--full--light.png | - | f3e1043e9fca4fe3bedc316a8b6d9e16a1d3e810e3456da80eaeec343df48324 | CANONICAL |
| EV-FLIP-LIST-030 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-row--disabled--full--dark.png | - | 661615cb6d3be9fd287c54c36ba03082bcc02d78a0c686110fc0369d9c9167e6 | CANONICAL |
| EV-FLIP-LIST-031 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--book-row--disabled--full--light.png | - | 17d95b8b06885f6bc4a6e676169a50885a30b011701f29bcad0a8e89c662f32c | CANONICAL |
| EV-FLIP-LIST-032 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--chapter-list--default--full--dark.png | - | 54d5facd816f38d120a9fc5adcfcdd8a31b3258c182b8949a077dfefeaa33386 | CANONICAL |
| EV-FLIP-LIST-033 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--chapter-list--default--full--light.png | - | f4bc1e72aa58d8bfb6f4045028e95badfc02bb6255f0535ade7252bdd32159d5 | CANONICAL |
| EV-FLIP-LIST-034 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--command-palette--empty--full--dark.png | - | f02341d594f487b3f5096ca5b7ec025af56766e80dc755393680de28533427eb | CANONICAL |
| EV-FLIP-LIST-035 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--command-palette--empty--full--light.png | - | a43cba142d61fc4f45e96056b124a1e97854122c5d8ceb268959cadcafceb669 | CANONICAL |
| EV-FLIP-LIST-036 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--command-palette--result--full--dark.png | - | 3fb1b7368fb3127acab2ab5793d48128e7d94b9f8aaf068119ae0281be65e954 | CANONICAL |
| EV-FLIP-LIST-037 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--command-palette--result--full--light.png | - | 0c164442056950b2671e6ba4dcaee6da26a0a6b74efe65245739e3d1a47945df | CANONICAL |
| EV-FLIP-LIST-038 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--context-menu--disabled-item--full--dark.png | - | 8a58e962dd4219c04b2daaa5914999a34acf64f073b4039e970cab33ab8191bc | CANONICAL |
| EV-FLIP-LIST-039 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--context-menu--disabled-item--full--light.png | - | 66d6d2856d808299064b6c7e5986856f335185c2510d438607fbab9862ce49ac | CANONICAL |
| EV-FLIP-LIST-040 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--default--full--dark.png | - | 6a41f040ec40ba869973b2cb31e89b16a71380e79693f2a06956b33bcd0281d2 | CANONICAL |
| EV-FLIP-LIST-041 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--default--full--light.png | - | 1d8455eaf665cdd6b7571a30a955bb5a67b886c80dc1ec1c9865e2ca780adcc7 | CANONICAL |
| EV-FLIP-LIST-042 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--disabled--full--dark.png | - | 860f0a294d694add33ba817e43cc852d2e8e823ccba920e3603cef19aab4d0ed | CANONICAL |
| EV-FLIP-LIST-043 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--disabled--full--light.png | - | 9149c20ee24a91492f1add37dcc719686595390af0869a50973bc497ebedcf42 | CANONICAL |
| EV-FLIP-LIST-044 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--hover--full--dark.png | - | be969a6bb952c675bda2e1172da9dfe5d50fac5fd55cef03e324495b24359d4a | CANONICAL |
| EV-FLIP-LIST-045 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--hover--full--light.png | - | 9dc59d68f89479997baecd320880b65cd967d841753286d0a4f1d71452a926df | CANONICAL |
| EV-FLIP-LIST-046 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--pressed--full--dark.png | - | c9ed4f8e9f47cb250fd569df180730a98f198a3a78fd4e077c855cf46379d6a9 | CANONICAL |
| EV-FLIP-LIST-047 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--danger-button--pressed--full--light.png | - | 8d37c109c38e96fc73fa5f7d1ddd08c3de02c9631ea54fe19b27470a980bed35 | CANONICAL |
| EV-FLIP-LIST-048 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--dialog--closed--full--dark.png | - | 8ac09c4e2df3f412b5a45695aadf0bddc7035b3faf45d4dd063405bc0e3de48a | CANONICAL |
| EV-FLIP-LIST-049 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--dialog--closed--full--light.png | - | 12417c1281d9511903ddfe5d90ec27972402b28cbfd53d27a81704e9d0128659 | CANONICAL |
| EV-FLIP-LIST-050 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--dialog--open--full--dark.png | - | 658516ddfb910a804a2a1c903f79d86b637918c312e4ad0cefdefb7bba306651 | CANONICAL |
| EV-FLIP-LIST-051 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--dialog--open--full--light.png | - | d0802f517cce8b3ffb55e3a210536bcf1eee78dc8ce173c2a8b06987e6b41dfd | CANONICAL |
| EV-FLIP-LIST-052 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--drawer--closed--full--dark.png | - | 3a23880327ee14fa9bb2129e23db725f4a0fa7b602295ba53331d7fe92dd95e5 | CANONICAL |
| EV-FLIP-LIST-053 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--drawer--closed--full--light.png | - | 87da9a58f004be601d18b043b2eddb80a881d96a35e9a295c0a2851855c9b08b | CANONICAL |
| EV-FLIP-LIST-054 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--drawer--open--full--dark.png | - | 89177c7a4d87f7c6d47ba499e2dd8def32ac4ad6d53793efa20a1d650b22b301 | CANONICAL |
| EV-FLIP-LIST-055 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--drawer--open--full--light.png | - | f2af162bb59466d6d3af98961b858c52c9966d80f32814f3ee1a0ac667abe2be | CANONICAL |
| EV-FLIP-LIST-056 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--empty-state--default--full--dark.png | - | 00ebe5a1fb4d8f0bcae9cad3b1a8a1ad705e828c67ba93649fa61eeabf94ca2c | CANONICAL |
| EV-FLIP-LIST-057 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--empty-state--default--full--light.png | - | fc608c250bd153f58ba53625b92ec5aeefba30f188c89c6b451811b0b066d36a | CANONICAL |
| EV-FLIP-LIST-058 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--error-state--retryable--full--dark.png | - | 95e877efe79f19166792bef6df47f17f376e677aba7bccc1870d996447fd6275 | CANONICAL |
| EV-FLIP-LIST-059 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--error-state--retryable--full--light.png | - | d14df0c76fddc633c968a984575d190192e80840a876734bfbd8083e5984cf65 | CANONICAL |
| EV-FLIP-LIST-060 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--error-state--unrecoverable--full--dark.png | - | 5433294d678ee91518da15555b8b3630d74a04e8d83475f1b50da405e9433af5 | CANONICAL |
| EV-FLIP-LIST-061 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--error-state--unrecoverable--full--light.png | - | 403d1287e9e6e0e5fc7b7a634362bfab9bde3b624a6bd31f1fd69a46b7aba622 | CANONICAL |
| EV-FLIP-LIST-062 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--checked--full--dark.png | - | 92fd3d87c790490f7abef0ff92f0b47e0af790063bb71f01123d9df360a165a3 | CANONICAL |
| EV-FLIP-LIST-063 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--checked--full--light.png | - | d009b3061519b65f92451ea1c08ba9c8f88fc8e00a56bf3e31204bbb5a4db589 | CANONICAL |
| EV-FLIP-LIST-064 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--default--full--dark.png | - | a76694f35f67dc4fc002b0d0bf7f331f93fe77d86b8c5d5921a7cbb782e87cbe | CANONICAL |
| EV-FLIP-LIST-065 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--default--full--light.png | - | dbe9ead20b6ee7668251604d59e9eac257327fd84f1f64927b9331d027ff06b6 | CANONICAL |
| EV-FLIP-LIST-066 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--hover--full--dark.png | - | 36739cad328ce06cd45e1e060651668ceeff5b1b13d0154c9a51018034d554b2 | CANONICAL |
| EV-FLIP-LIST-067 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--icon-button--hover--full--light.png | - | 0ee78de15661439f7382201ba67dab8d7123a1803cb9451ce5665d338fd1e74c | CANONICAL |
| EV-FLIP-LIST-068 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--page-thumb-strip--default--full--dark.png | - | c0a1b356140f095b360aa0e13525b2577cc506a432020068441f36b95fea6626 | CANONICAL |
| EV-FLIP-LIST-069 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--page-thumb-strip--default--full--light.png | - | 232e323c050233cde9ef3a2be0cdeded6948a3e6812cd49c7062c6b23597db7b | CANONICAL |
| EV-FLIP-LIST-070 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--default--full--dark.png | - | 11fa85f9e7a5f03e6a32b8ef79bd2f944556310d4a506e888c03db45f7de794e | CANONICAL |
| EV-FLIP-LIST-071 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--default--full--light.png | - | ccaf77f6cfc0095e4f14951805384f820a4895fba409900d0718ef165f112849 | CANONICAL |
| EV-FLIP-LIST-072 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--disabled--full--dark.png | - | 19096cdb5df881d61ad3ae2f43f8ff6ac34aadbed4e5e501bc0a163790e65c3d | CANONICAL |
| EV-FLIP-LIST-073 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--disabled--full--light.png | - | 1ea6a98c677b17d93fb066256cac6a0894ac05bd0d2ef59b4ec527ab67f42834 | CANONICAL |
| EV-FLIP-LIST-074 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--hover--full--dark.png | - | 058ccb1d999c4e4f39f51328c51faaebbf7d0d10425e2493bb9569546405c27a | CANONICAL |
| EV-FLIP-LIST-075 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--hover--full--light.png | - | a221df936ec221b8a3e4abfc2c64ef1e4f0e0389fb52cdcadd5a7d5c0483e34f | CANONICAL |
| EV-FLIP-LIST-076 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--pressed--full--dark.png | - | 7bd2d5cf594bcbe8527a3e59a3b7706b3b63b67ed2285de07f1550c0c1c2a955 | CANONICAL |
| EV-FLIP-LIST-077 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--primary-button--pressed--full--light.png | - | 966913b84077ce64a6cd571bb7b158b78b3d0b859d7e4663355ec4d662301f01 | CANONICAL |
| EV-FLIP-LIST-078 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--reader-page--single--full--dark.png | - | bcc7af72ece3d9b5e125c63a71c403d5c33be00bbab7ceda1532bb4efab95182 | CANONICAL |
| EV-FLIP-LIST-079 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--reader-page--single--full--light.png | - | e3f00ce494d670cf1e68710b0fb1c7a82491ef1a401a23ecba369bc103cccd55 | CANONICAL |
| EV-FLIP-LIST-080 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--reader-progress--default--full--dark.png | - | 58c8d0d619c7e0bd14466c858781cb6124ced8c676744020b9309b97f7bf690a | CANONICAL |
| EV-FLIP-LIST-081 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--reader-progress--default--full--light.png | - | 0beab56ff843af1299a11b62a6eecf27871645195cd620dab18f689d3a045a31 | CANONICAL |
| EV-FLIP-LIST-082 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--region-box--default--full--dark.png | - | f3b894536c2572c74ec509e12d62a10c47cb8108c1f275ccf2af1e602d3e4426 | CANONICAL |
| EV-FLIP-LIST-083 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--region-box--default--full--light.png | - | c9d3be1cc6e7142e8f8beb303619091a6644123948e672f920da4acd21bc0051 | CANONICAL |
| EV-FLIP-LIST-084 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--region-box--hover--full--dark.png | - | f62a1758ab3074ac07b2434cbf4e9dce6f55640331522edb2e706b4554d6d42d | CANONICAL |
| EV-FLIP-LIST-085 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--region-box--hover--full--light.png | - | 17f44ae5eb9b98aa30a1e446bdd0809522d3f376ecdf578addd59d3bf11ac600 | CANONICAL |
| EV-FLIP-LIST-086 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--default--full--dark.png | - | dbc55aaef36076c30c35a6bc0f18da5f79ce9299fa457ebfe5251836b0290bae | CANONICAL |
| EV-FLIP-LIST-087 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--default--full--light.png | - | 27a98ef1deb62665126467e998639b74f366c4f8d76ac89abce5ad383c05cc5d | CANONICAL |
| EV-FLIP-LIST-088 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--focus--full--dark.png | - | ca1645c4d6675445eb86d444829d8419e5256471524f8e462fab4b20f143a747 | CANONICAL |
| EV-FLIP-LIST-089 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--focus--full--light.png | - | b9d104868ae380e64b973d609c369f0a7a1883c886f5583edb8633d2204c089c | CANONICAL |
| EV-FLIP-LIST-090 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--value--full--dark.png | - | eff1c117102189d659c3c4d224d121ba36388b96ba74a8f5f4c1518f012acce1 | CANONICAL |
| EV-FLIP-LIST-091 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--search-field--value--full--light.png | - | 9357d1f26a74a6bd8b6cfda1f20f515ea1698208b56aa62690cd8104152d3267 | CANONICAL |
| EV-FLIP-LIST-092 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--default--full--dark.png | - | 6225650c0f4293b861aa2eccc06c726ca717c977c935a68598443d2aa19f9220 | CANONICAL |
| EV-FLIP-LIST-093 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--default--full--light.png | - | e3bfe1fbe83bb94888ee20dd3818dd5bc8b6d80f85beb6aa945e1eab3b4c2a14 | CANONICAL |
| EV-FLIP-LIST-094 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--disabled--full--dark.png | - | 36721b2c032c5db03e353bfdd3d3f44677c27b6cce80a6ac4620a8cac133c131 | CANONICAL |
| EV-FLIP-LIST-095 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--disabled--full--light.png | - | 2884f66463b69191dcefff138ed22551c1957cdce4f79620ca6b02b3b6e4ae98 | CANONICAL |
| EV-FLIP-LIST-096 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--hover--full--dark.png | - | bb96910170e0fbdf3a921f6b58c89ce7b6da7fb79b0842da46b6763cf71b2615 | CANONICAL |
| EV-FLIP-LIST-097 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--hover--full--light.png | - | e57ed5263bca2e360471898acbf01495f5115fda904c3101a6dea021837e3a8f | CANONICAL |
| EV-FLIP-LIST-098 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--pressed--full--dark.png | - | 61222ad0c8aaf2811461c14e78bd344af3294bad1c3452f9066823699169e4ed | CANONICAL |
| EV-FLIP-LIST-099 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--secondary-button--pressed--full--light.png | - | b0be52d745db064b268341b035a824771300f4f6e039616fe66322818e43c516 | CANONICAL |
| EV-FLIP-LIST-100 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--hover--full--dark.png | - | 28a542455894ce62b044bab1e8aac9497c5ea143f9dc0eaa1571f7d6bfb14122 | CANONICAL |
| EV-FLIP-LIST-101 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--hover--full--light.png | - | 465c95af1b22d85ebf8abc205b3109b524e48e79c8b8a851c5c6df7169f6f18b | CANONICAL |
| EV-FLIP-LIST-102 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--pressed--full--dark.png | - | a3943901f5d06267c9ce416b44a73f1eb2543c1bd39263c5393095f497fcde47 | CANONICAL |
| EV-FLIP-LIST-103 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--pressed--full--light.png | - | 29ce0fbc6992550f8d840354daa1370e7d45fc735433aac023cda548284f1336 | CANONICAL |
| EV-FLIP-LIST-104 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--selected--full--dark.png | - | e3009ea3f427ce92841d2c2288b8cc847dc1fab4ab44c2c2ac9c467608520500 | CANONICAL |
| EV-FLIP-LIST-105 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--selected--full--light.png | - | b0eb26a82c36024b2007657eeee301567c888526e077f24eb0f89e64f8f8794d | CANONICAL |
| EV-FLIP-LIST-106 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--unselected--full--dark.png | - | 5cb43a0b3307144d3fbb88636825b62638cb7462658cc9b70d8b017326ae7e40 | CANONICAL |
| EV-FLIP-LIST-107 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--segmented-control--unselected--full--light.png | - | 8488e5063a86e0fd17beeafa260569714e3491cfbf0b902152e45248da22676d | CANONICAL |
| EV-FLIP-LIST-108 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--settings-field--disabled--full--dark.png | - | 6860034d4c29c33658afcbc3752a3c187516d6dd411c167562eed1aea058ddc0 | CANONICAL |
| EV-FLIP-LIST-109 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--settings-field--disabled--full--light.png | - | 0e5f8d1d74f77f6aecb4bfc5a6f372c81165953393ac537b5bf0ceb202f625d3 | CANONICAL |
| EV-FLIP-LIST-110 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--settings-field--error--full--dark.png | - | 8bc7233b0d73cf6f53de6b975933f9215075ede8b1f7030a136af4f3a20dcb86 | CANONICAL |
| EV-FLIP-LIST-111 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--settings-field--error--full--light.png | - | d7550f543ac0d743f328a2f832b3b667bb1942e58d703864a16094ab3dabf19b | CANONICAL |
| EV-FLIP-LIST-112 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--bookcard--full--dark.png | - | b4c23048c005e5586c44d05f505205fe395f0115de5f7ebc4e9f28ce3808c274 | CANONICAL |
| EV-FLIP-LIST-113 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--bookcard--full--light.png | - | 851e1f1010efe1f3f8f0b47e4e1bb615a23120d5c8bca9d8e9fd06d11704a3d3 | CANONICAL |
| EV-FLIP-LIST-114 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--panel--full--dark.png | - | 80b35caafbc126f921557f83f286d8181faf3ab4da629d3bdf28026605c10623 | CANONICAL |
| EV-FLIP-LIST-115 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--panel--full--light.png | - | 51e7b0bae6c7e7a3d756ed912156ae74bc4f0d549b8145b75097cc3a2532f22c | CANONICAL |
| EV-FLIP-LIST-116 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--row--full--dark.png | - | c467ecc7edf60eb05436ff3b6ce28dced2b37ada5ed218177ac7542a3bbd22e3 | CANONICAL |
| EV-FLIP-LIST-117 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--skeleton--row--full--light.png | - | f0d55c31d58648991c094e2010dd09034075d7c5986d077652b846cb02c40deb | CANONICAL |
| EV-FLIP-LIST-118 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--default--full--dark.png | - | ce971a4da37eb85f49984872bd59047eae23a6b1ddfc6de7dace352492d97768 | CANONICAL |
| EV-FLIP-LIST-119 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--default--full--light.png | - | a9c0e297603c3bcfb861df94a0e2abdd483bee21ed5de80f88968174e453ee4d | CANONICAL |
| EV-FLIP-LIST-120 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--disabled--full--dark.png | - | afc956e90e3da7f0ea600c29adf7bf3ca1b506a61f269d11d9dbfc48efe571ea | CANONICAL |
| EV-FLIP-LIST-121 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--disabled--full--light.png | - | be751e7678927cc6a76d8f135538293e418f1f497d3d7c2a5b4d266dfc295dbc | CANONICAL |
| EV-FLIP-LIST-122 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--hover--full--dark.png | - | 006731cca2a8e34b29dd5c5742d6c19c4e5e210cc59174b862cb0837e1e6a037 | CANONICAL |
| EV-FLIP-LIST-123 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--slider--hover--full--light.png | - | 7632eb4ee7f4f58f7897dd72fc78986b68b7ae5d33472ed8b13d8bff176ed6e4 | CANONICAL |
| EV-FLIP-LIST-124 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--streaming-thumb--lazy--full--dark.png | - | 70da80c565c842c894ff3ad7ca3d8be6ba6c903de1b0bf5f9b7146f02d0e5231 | CANONICAL |
| EV-FLIP-LIST-125 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--streaming-thumb--lazy--full--light.png | - | 9fe5f380156f6c1efe36f680e43b27820ad8858a9f1a5ab1127a3cd0c9f79938 | CANONICAL |
| EV-FLIP-LIST-126 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--default--full--dark.png | - | a1b460f11e58a8d929ae23da500b4c5a0b81773b12fc590b722cd87de9df721a | CANONICAL |
| EV-FLIP-LIST-127 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--default--full--light.png | - | 4749378885e3e70debe7fe35002fd1e3c9289e8963dd5a1e3c889a8be74b89e6 | CANONICAL |
| EV-FLIP-LIST-128 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--disabled--full--dark.png | - | 165d3b8bdcab65efa970b623293d1fa78a602396ba2e60570d9f62fd2669200c | CANONICAL |
| EV-FLIP-LIST-129 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--disabled--full--light.png | - | ac7ae33a835b6de04820ee3424d4a0b3a18b273d25da71390368aa4c3fe39849 | CANONICAL |
| EV-FLIP-LIST-130 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--hover--full--dark.png | - | 0015cb721aad1d66d06b48185a24ea331401e92df1804c573b843f0ea1178830 | CANONICAL |
| EV-FLIP-LIST-131 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--hover--full--light.png | - | be6d587c1a2ba68e7d46e2d42e83fd953e37e527f9ba28f0762d4b8c5133f8c5 | CANONICAL |
| EV-FLIP-LIST-132 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--selected--full--dark.png | - | 4efa48c6452907a3a924900bdf81891da0c67e5f664a082ec071923d74d3bf36 | CANONICAL |
| EV-FLIP-LIST-133 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--surface-card--selected--full--light.png | - | 2039281e84b426718778c598d8a4d5dff5dee7a69c10e4fd78acdde9783051a7 | CANONICAL |
| EV-FLIP-LIST-134 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--hover--full--dark.png | - | 623b8ea1a98828ec37d781355254ebfab850ed923783c579a40fc573739d3665 | CANONICAL |
| EV-FLIP-LIST-135 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--hover--full--light.png | - | 658d18952dcbbea6904f41678644cd738d7419745ac8c2f658f6c5fb5a8ae21d | CANONICAL |
| EV-FLIP-LIST-136 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--selected--full--dark.png | - | 19f32c0ca252617b9f73971d3069ae7cd22b59551ca65aa7c34275d8552ad84e | CANONICAL |
| EV-FLIP-LIST-137 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--selected--full--light.png | - | 1490841169568214e09db6778d3e2a35c1fdf2534223768d444b661281637f7a | CANONICAL |
| EV-FLIP-LIST-138 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--unselected--full--dark.png | - | f297bca8d40097d2d4745750baa7bf59fc59bccadbcf2185547838fca6b9febd | CANONICAL |
| EV-FLIP-LIST-139 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tab-strip--unselected--full--light.png | - | f5925ef1b3727fb1b3e2c452630c8e19535d8c2845b02002163e42b9377f5820 | CANONICAL |
| EV-FLIP-LIST-140 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--disabled--full--dark.png | - | 7e34408cb5a2f821aace06faa7c44062dd6117b00dbf9159072d221f986f9f7b | CANONICAL |
| EV-FLIP-LIST-141 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--disabled--full--light.png | - | d68de31cc8842ba81d9e7fad06218af91878e9d85b79de09636acd9d4847dd68 | CANONICAL |
| EV-FLIP-LIST-142 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--off--full--dark.png | - | 0c2923ce72c87666b9118d66bf5055fd07a2ef9fd691f0e2df2967230651c721 | CANONICAL |
| EV-FLIP-LIST-143 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--off--full--light.png | - | 5c480ea9f571df916d0bdac7f24fee7d0f3ab57dbf50c872e77bea2d34938177 | CANONICAL |
| EV-FLIP-LIST-144 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--on--full--dark.png | - | 3f7443f2bd2d5bc4b56026a0e7de252ae45bf3510b2b8b58c0290ca63f56fe85 | CANONICAL |
| EV-FLIP-LIST-145 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--toggle-switch--on--full--light.png | - | e170cbc574001e2be3156434f5260f3858522dc03cdeb2983cadea70be186668 | CANONICAL |
| EV-FLIP-LIST-146 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tooltip--opened--full--dark.png | - | 0e289319b382638cb22078db49434dab763d5c8ef05b8220d4c34affc4bd262b | CANONICAL |
| EV-FLIP-LIST-147 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/components--tooltip--opened--full--light.png | - | ef8d97e3980922b0e47039f8af4037011ff2afcdaeb9851165028bb2e22ef5cd | CANONICAL |
| EV-FLIP-LIST-148 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--page-turn-particles--mid--full--dark.png | - | 60ef983fbc08f8f20dd5ccde540e1ee1cf5421786878979b4c49e5aca4551e7d | CANONICAL |
| EV-FLIP-LIST-149 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--page-turn-particles--mid--full--light.png | - | 76af16f65b6cc8391085c94be470526dd6335632ecd33eb5aa29a6d90bcd0156 | CANONICAL |
| EV-FLIP-LIST-150 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--page-turn-particles--none--reduce--dark.png | - | 147d8e823c74bdfcb7e4657eb6d170bd91c70c9b3055c54ce318fbfca6f7bc15 | CANONICAL |
| EV-FLIP-LIST-151 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--page-turn-particles--none--reduce--light.png | - | 70ca25c5f96fccf2388ba8f4867914215b05983c3c8d7da81683284af75258d7 | CANONICAL |
| EV-FLIP-LIST-152 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--first--full--dark.png | - | 21cce1e1d2a0242eab3dab1de2e4ad55c06b749a344c77894bc973e2d37d13cc | CANONICAL |
| EV-FLIP-LIST-153 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--first--full--light.png | - | 82110d66080079d45685eaeb4822cb832de5ae8953ac4dbf170e9faac26f3c0b | CANONICAL |
| EV-FLIP-LIST-154 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--mid--full--dark.png | - | e177a608a9b584750367b64690050f1de1020267fe8245eede77ac370c0db013 | CANONICAL |
| EV-FLIP-LIST-155 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--mid--full--light.png | - | f97267f34dff055666d4a8c05b929a63223dff160ec911053809d093c4b2f41e | CANONICAL |
| EV-FLIP-LIST-156 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--static--reduce--dark.png | - | f034f7a4d703a484a90655bcb2e9eb45430e03dbf4c351cf9c3ea7d40e86806c | CANONICAL |
| EV-FLIP-LIST-157 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--static--reduce--light.png | - | 845e4b631962087ef6c2b584759e7f696711b2d9416c17fa6acf6aeb26aed211 | CANONICAL |
| EV-FLIP-LIST-158 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--reader--default--full--dark.png | - | b583c6c40127f0771011c5a58095bd5b995a3151a95d12013c23b0df2a630381 | CANONICAL |
| EV-FLIP-LIST-159 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--reader--default--full--light.png | - | a86b165e8a6baa39d39a89438a5bd1573926748e138a3d2f9fc16f4dd7101d83 | CANONICAL |
| EV-FLIP-LIST-160 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--settings--default--full--dark.png | - | 76e680dafdbb7fc831de461b21e6d4541817a53e7f3955d2931d6e7ff77de190 | CANONICAL |
| EV-FLIP-LIST-161 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--settings--default--full--light.png | - | f56b3e2b5b3d8bd8e3c602018bab5e8b27c8057543ac31a76bde3aa63a69b50a | CANONICAL |
| EV-FLIP-LIST-162 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--shelf--default--full--dark.png | - | 75be3b1294b7f61b48e67c237428bf5f7f9d6d441e208e661814dbaac4824426 | CANONICAL |
| EV-FLIP-LIST-163 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--shelf--default--full--light.png | - | d82d005aa2743fd02022fb68078c722b99fdc7bae2db5fb57f5de42ed0e5901a | CANONICAL |
| EV-FLIP-LIST-164 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--workbench--default--full--dark.png | - | 47bd41ff7ee547758f7c2f26a211c8db4a77f3bf8d7affed62f764901d2902d3 | CANONICAL |
| EV-FLIP-LIST-165 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/pages--workbench--default--full--light.png | - | 9a44fcc96f7f2709f00124f9ed5f98eeb5d31caa4793b5c0f85fbca1b9440b22 | CANONICAL |
| EV-FLIP-LIST-166 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--nav-rail--collapsed-1280--full--dark.png | - | 10f78d37500a627d0eb3d47f53ddd329663e549746ac35746fc2647406888734 | CANONICAL |
| EV-FLIP-LIST-167 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--nav-rail--collapsed-1280--full--light.png | - | c18af4d233c6af1a1bd077209b5f2163c800316e0e3891ef39dd75dbb055b5e4 | CANONICAL |
| EV-FLIP-LIST-168 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--status-band--error-1280--full--dark.png | - | d4fd91d3ea864f01f506ecd1aba63054204972a904800f950ff6345b756da8aa | CANONICAL |
| EV-FLIP-LIST-169 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--status-band--error-1280--full--light.png | - | 81b253677264b7460de1ada972263a86ac70393f32446a4c94aa713a39f52932 | CANONICAL |
| EV-FLIP-LIST-170 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--status-band--running-1280--full--dark.png | - | 5fbfd830ca67ce57878fd733a925e40c40779cdfed63ad205f4b2a5f43b931d7 | CANONICAL |
| EV-FLIP-LIST-171 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--status-band--running-1280--full--light.png | - | 9ee323e81ba1e8e89c9f22a9c05412f213d5cc37b86e066986170dd8a4ee6a29 | CANONICAL |
| EV-FLIP-LIST-172 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--compact-1280--full--dark.png | - | f9d3ed353477b975da0ce5d6ebda2375782f6bcdf2dfb10bd7d2c469c1065ded | CANONICAL |
| EV-FLIP-LIST-173 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--compact-1280--full--light.png | - | f0bcdfb7da48e91641c584928a8c0e97dbd206dc1fc06ec49e98817fc225f1ef | CANONICAL |
| EV-FLIP-LIST-174 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--full-1600--full--dark.png | - | d21658e04e8f2d44e8c0c233bda16698ddab30b5fd663de24ed4fc62528e41df | CANONICAL |
| EV-FLIP-LIST-175 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--full-1600--full--light.png | - | 2c8b52d03865d651e97f9ed7eba55d72a84f25fe3055081676cc9a535a9b431f | CANONICAL |
| EV-FLIP-LIST-176 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--medium-1024--full--dark.png | - | d6a24a680fa4ab59537ceaf43d5286f2b83a7118a01cae0b0ce1172cfa02a60e | CANONICAL |
| EV-FLIP-LIST-177 | done 翻转补齐（2026-11-08） | verification/FEA-06-RESIDUAL-2/visuals/shell--top-nav-status--medium-1024--full--light.png | - | d0914b0e52fe0fa9b691856cfc947b0487f2dfe5e9724ecde368e26fe407fe63 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | 无 linked worktree；main checkout `G:\CODEX\New Manga` | NOT_APPLICABLE | 同一仓库 checkout | `832103393` | `git worktree list` 仅 main；未创建/删除 worktree。 |
| verification artifacts | `verification/FEA-06-RESIDUAL-2/**` | PRESERVE_REFERENCED | `verification/FEA-06-RESIDUAL-2/visuals/visual-inventory.md` | `e76b2f5fed7a80fc5f52ce2e28dd35b656e8a931f3884781f006098cfbffed74` | 172 PNG + inventory + expected-tokens + 各日志被 Task/Review/Handoff/Closeout 引用；旧 `verification/FEA-06/**` 字节未动。 |
| task-env / dataset / model / test-material | 未创建 / 未使用 | NOT_APPLICABLE | - | - | 未创建 task-env；测试使用 FakeHost 内存 fixture，不接触用户数据。 |
| temp | 测试 `%TEMP%` 临时根 | NOT_APPLICABLE | - | - | 每次运行临时根并在测试内清理；未写真实 `%APPDATA%`。 |
| agent-output / exchange | `G:\CODEX\New Manga.workspace\FEA-06-RESIDUAL-2\`（prompt/结果日志） | PRESERVE_REFERENCED | `verification/FEA-06-RESIDUAL-2/integration-verification.log` | `92a7c8573d3570ae88209bc535c7de403ae35aa2e0a75e9a3e9b9b11f10bac9c` | prompt/结果日志保留在 workspace；集成日志入库并登记 SHA。 |
| user data | 未访问 | NOT_APPLICABLE | - | - | 未访问用户源文件/AppData/DB；旧四 PNG SHA 未变。 |

## Closeout Record

- **终态**：`closed_with_limitations`（DONE 不允许 PARTIAL AC；本卡 AC1–AC4 MET，限制/OUT/BLOCKED 另列）。关闭时间 2026-11-03；delivery `832103393`，integration evidence `d1df8035a`。
- **复核链**：scope-r1（changes_requested）→ scope-r2（changes_requested）→ scope-r3 **approved**（ZCode，P2=7）；impl-r1 **changes_requested**（P0=1/P1=6/P2=12）→ impl-r2 **changes_requested**（P0=0/P1=6/P2=12）→ impl-r3 **changes_requested**（P0=0/P1=2/P2=4）→ **impl-r4 approved**（P0=0/P1=0/P2=3；172 图 172 PASS/0 REJECT；D-9 独立子 agent，Codex 限额期间）。全部报告/证据提交在库，历史字节未覆盖。
- **集成验证**：`verification/FEA-06-RESIDUAL-2/integration-verification.log`：build 0/0、无过滤全量 **1289/0/57**、PNG 172/inventory 172/唯一 SHA 172、旧 FEA-06 四 PNG SHA 不变、TokenGen/ThemeGen up-to-date、check PASS(3)、pins 15/15、禁止范围 diff=0、工作树干净。
- **AC 结论**：AC1–AC4 MET（见上）。
- **限制/残项**：原生 200% DPI/a11y 矩阵 = **BLOCKED/D-1**（无硬件，不写达成）；OUT：PrimaryButton loading、Dialog 危险/加载、CommandPalette loading、新增组件状态（v1.1 重冻结）；R2R4 P2 卫生项已由 DSH 处理（指针/审阅字段）；D-14 NotStarted 令牌 = 已裁决 A，实施在后续卡 `D-14-STATUS-COLOR-FIX`（ready），本卡不写达成。
- **资源**：见 Resource Manifest；未 push；关闭时工作树干净（除关闭提交）。
- **后续建议**：按顺序实施 D-14-STATUS-COLOR-FIX；原生矩阵待硬件/waiver。

## Closeout 补充（DSH，2026-11-08：`closed_with_limitations` → `done` 翻转记录，append-only）

- **授权依据**：用户 2026-11-08 残余收口指令（R2）+ DSH 裁决（`doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md` §3/§7.5：新授权可翻转终态；**不改任何历史 Review/证据字节**）。
- **BLOCKED 表 before/after（逐格）**：
  | 格 | before | after |
  |---|---|---|
  | 1 BatchMatrix 七状态/吸顶 + RunProjectionBar | BLOCKED（FEA-10 端口） | **关闭**（`FEA-06-RESIDUAL-3` AC-1，`ddc29ecb3`） |
  | 2 ReaderPage 双页/滚动 | BLOCKED（FEA-09/11 数据面） | **关闭**（AC-3；两页连续口径，L-R3-1 全章长滚动 re-home） |
  | 3 RegionBox 冲突态「查看对照」 | BLOCKED（FEA-10 冲突投影） | **未关闭 → re-home `FEA-06-RESIDUAL-4`**（需 C-07 additive；0 pin 不允许） |
  | 4 书架满态统计 | BLOCKED（FEA-12 统计面） | **关闭（改口径）**：既有投影自洽聚合（AC-4）；原「FEA-12 统计面」表述作废（该项误归） |
  | 5 Console 投影/9 行 | BLOCKED（FEA-10/12） | **关闭**（AC-2） |
  | 6 完整 Tab 遍历 / 原生 a11y / 200% DPI / 原生截图 | BLOCKED（B-5/D-1） | Tab 遍历 + a11y 属性 **关闭**（AC-5）；原生 a11y/200% DPI/截图 **NA（原生交互未执行，NOT_RUN）** |
- **显式声明**：**本卡 `done` 不覆盖 BLOCKED 表** —— 格 3 与原生项仍未做（格 3 re-home 具名卡；原生项 `NOT_RUN`）。
- **连带 limitation**：L-R3-1（webtoon 全章长滚动）→ `FEA-06-RESIDUAL-5`；L-R3-2（DS `ReaderPage` peer 类型）、L-R3-3（DS `BatchMatrix` 不可滚）→ DS 回修卡；L-R3-4（R3-008/011/012）；L-R3-5（Avalonia discoverer 非稳定契约类型）；L-R3-6（`ImportExportPanels` 章节 off-by-one，re-home）；L-R3-7（interrupted+disposition dead-end）—— 均见 `verification/FEA-06-RESIDUAL-3/limitations.md`。
- **口径**：不宣称「全部关闭/完全实现/可发布」；`Technical Gate=NOT_SATISFIED` 不变。
