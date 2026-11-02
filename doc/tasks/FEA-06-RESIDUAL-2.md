---
id: FEA-06-RESIDUAL-2
title: Fluent 视觉残项补做（D-8 decorative + I-4 视觉格）
kind: implementation
governance_version: 3
status: closed_with_limitations
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
| EV-RES2-INTEGRATION | AC1–AC4 | `verification/FEA-06-RESIDUAL-2/integration-verification.log` | `d1df8035a` | `92a7c8573d3570ae88209bc535c7de403ae35aa2e0a75e9a3e9b9b11f10bac9c` | CANONICAL |
| EV-RES2-IMPLR4 | AC1–AC4 | `doc/reviews/FEA-06-RESIDUAL-2-impl-r4.md` | `d1df8035a` | `9aa51c68ecec8507cf30be08a215ef1096444594a24084293bc3a20c325c2f33` | CANONICAL |
| EV-RES2-HANDOFF | AC1–AC4 | `doc/handoffs/FEA-06-RESIDUAL-2-r2r3-17a26d552.md` | `832103393` | `65455671ac931b2d6dedbfa0d4ac7ee8fc11a7b57ff90a869910a4b814ec6455` | CANONICAL |
| EV-RES2-INVENTORY | AC3 | `verification/FEA-06-RESIDUAL-2/visuals/visual-inventory.md` | `c70d5c348` | `e76b2f5fed7a80fc5f52ce2e28dd35b656e8a931f3884781f006098cfbffed74` | CANONICAL |

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
