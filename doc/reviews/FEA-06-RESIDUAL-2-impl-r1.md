---
task_id: FEA-06-RESIDUAL-2
reviewer: DSH 独立子 agent（独立上下文 Reviewer）
reviewer_kind: subagent
author: ZCode CLI（IN-1/IN-2A/IN-2B 实施；DSH 诊断收尾）
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: 854e5bb1b0602b3e48f6b4d4a514432a864c8504
implementation_head: 998d75bdb1e231d4ae2e2dd377b21452dd316cc9
decision: changes_requested
verdict: changes_requested
p0: 1
p1: 6
p2: 12
provenance:
  agent: DeepSeek Harness 独立子 agent（与实现会话无共享上下文）
  appointment: 用户本轮 FEA-06-RESIDUAL-2 impl Review 指令；Task scope-r3 approved
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  environment: Windows 11；pwsh 7；dotnet SDK；Avalonia 11.3.22；repo G:\CODEX\New Manga
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-2 impl-r1

**verdict = changes_requested（P0=1 / P1=6 / P2=12）。当前 head 不应进入 DSH 集成。**

四条门禁（build、无过滤全量、TokenGen/ThemeGen、check/pins）与旧 FEA-06 四 PNG SHA 均通过，全量 **1272 passed / 0 failed / 57 skipped**，禁止范围（Core/契约/生成物/冻结设计/Current/组合根/FrontendSelector/FEA-07 seam）零 diff；IN-1 的行为测试（12/12）与 IN-2A 的属性测试（14/14）也确实全绿，IN-2A 逐格期望值经抽查与样式锚点一致。但本卡的核心交付是**视觉证据 + 独立签署**，而当前视觉证据不能支撑 AC-1/AC-3：

1. **decor 两张 PNG 是无关占位**：`CaptureDecor()` 只渲染一个灰色 `Border`，与书架渐变/阅读器粒子无关；两张文件 SHA-256 完全相同（`96775212…`，791 B），IN-1.1 要求的 full 首/中 + reduce 三张、IN-1.2 的 full 中帧 + reduce 两张均不存在（R2-001，P0）。
2. **light/dark 主题没有真正切换**：只改 `Application.Current.RequestedThemeVariant`，设计令牌仍由默认 `System`（实际 dark）决定；16 对 light/dark 中 12 对、34 个文件中的 26 个字节完全相同；"light" 页面实际渲染为 dark（R2-002，P1）。
3. **IN-2B 清单远小于冻结范围**：34 张只覆盖 12 个组件状态 × 2 主题 + 4 页面 × 2 + 2 decor；IN-2A 众多状态、TopBand/NavRail/StatusBand、Empty/Error/Skeleton、ChapterList/PageThumbStrip、Dialog/Drawer、CommandPalette、AlertBanner 九值等均缺图；ReaderPage 图是"本章节暂无页面"空态（R2-003，P1）。
4. **`expected-tokens.md` 缺失**：测试文件自己声明期望值冻结在该文件，实际不存在；R3R-007 的"逐格锚点"与 D-11 的九值映射没有落盘证据（R2-004，P1）。
5. **派生控件样式修复不完整**：只修了 5 个 class，`Grid.fluent-settings-field`、`Border.fluent-streaming-thumb`、`Border.fluent-reader-page`、`ProgressBar.fluent-reader-progress`、`Border.fluent-settings-group`、`StackPanel.fluent-chapter-list`、`StackPanel.fluent-tab-strip` 仍不匹配派生控件；reader-progress 空白帧是旁证（R2-005，P1）。
6. **IN-2A 有状态格以默认值冒充状态断言、Slider 视觉未令牌化**：SurfaceCard 的 hover/selected/disabled、IconButton 的 checked 没有样式通道，测试只断言默认令牌不变；SearchField 只断言焦点时内边框不变、未断言焦点环；Slider 只断言 Foreground，实际 thumb 仍是默认蓝。这些应记 NOT_RUN/产品缺口，而不是"16+1 全组覆盖"（R2-006/R2-007，P1）。
7. 其余 P2 涉及 inventory 元数据、证据日志格式、`HasMotion` 文档与实现不一致、静态事件泄漏、暂停/不可见与粒子真实帧源证据、Canvas 布局写入、旧动画完成测试收窄、Handoff 缺失、D-14 未裁决和 R3R-001 指针未刷新。

测试数只证明已写入的断言通过，**不能据此判 AC 达成**；AC-1/AC-3 明确未 MET，AC-2 为 PARTIAL，AC-4 为 PARTIAL。Task 应保持 `in_progress`，不得写 D-14/OUT/BLOCKED 达成，不得 push。

## 范围与依据

仓库 `G:\CODEX\New Manga`，branch `main`；审查开始时工作树干净，`HEAD=854e5bb1b0602b3e48f6b4d4a514432a864c8504`（IN-2B 完成记录），实现 head 为 `998d75bdb`。`base_commit=669a4ae02`（RESIDUAL-1 集成/证据 head）。

已读（只读）：

- `doc/tasks/FEA-06-RESIDUAL-2.md` 全文（范围 v3、IN-1.1/1.2、IN-2A、IN-2B、OUT、BLOCKED、证据形式、AC 表）。
- `doc/reviews/FEA-06-RESIDUAL-2-scope-r1.md`、`-scope-r2.md`、`-scope-r3.md`；`doc/reviews/FEA-06-RESIDUAL-1-impl-r4.md`。
- 冻结设计：`doc/design/fluent-v1/02-motion.md` §2.3/§3/§4（8s、400ms、失焦/不可见暂停、自动化全关）、`03-accessibility.md` §4（高对比/可读性）。
- 实现 diff：`d854d91b2`（IN-1）、`1d2df1d15`（IN-2A + `Controls.Fluent.axaml` 选择器修复 + coverage 测试）、`998d75bdb`（IN-2B）；以及 `854e5bb1b` 的完成记录。
- workspace：`FEA-06-RESIDUAL-2/impl-zcode-prompt.md`、`in2a-calibration-notes.md`、`in2b-capture-plan.md`、`wip-snapshot/`（与提交内容核对；无未提交产品改动）。
- 证据：`verification/FEA-06-RESIDUAL-2/impl-in1|in2a|in2b-verification.log`、`visuals/visual-inventory.md`、34 张 PNG（逐张检查；20 个唯一 SHA）。
- 代码支点：`FluentDecorativeMotion.cs`、`FluentUi.cs`、`ShelfPageView.cs`、`ReaderPageView.cs`、`MotionTimings.cs`、`MotionResolver.cs`、`Controls.Fluent.axaml`、`Controls.Custom.axaml`、`Controls.Status.axaml`、`Themes/Controls/TabItem.axaml`、`Inputs.axaml`、`NewManga.DesignSystem/Controls/FluentComponents.cs`；`FluentResidual2DecorativeTests.cs`、`FluentResidual2StateEffectiveTests.cs`、`FluentComponentStateCoverageTests.cs`、`FluentResidual2VisualEvidenceTests.cs`、`FluentAnimationCompletionTests.cs`。
- 治理：`doc/templates/REVIEW.md`、`tools/governance/check.ps1`、`verify_pins.ps1`（只读运行）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`。

未审/未执行：opt-in 像素再生成（为保持已提交证据字节未重跑，见 R2-018）、原生 200% DPI/触摸、原生 a11y、逐像素美学评分（B-5/D-1 无硬件）；未修改任何生产源码、Task、证据或冻结设计；未 commit/push。唯一持久交付为本文件。

## Architecture（executed）

**IN-1 实现方向成立。** `FluentDecorativeLoop` 只用 `IFluentMotionClock.RequestFrame`（生产为 `TopLevel.RequestAnimationFrame`），无 dispatcher timer/后台线程；`Configure` 在 `period<=0` 时 `StopRunning`，reduce/category-off 不产生帧请求；`DetachedFromVisualTree` 停帧并注销窗口事件；`ConfigureMotion` 从 `MotionTimings.Resolve` 取 8s/400ms（常量已进 `MotionTimings.cs:36-40`，非 UI 魔法数）；渐变仅改 `Brush.Opacity`，粒子层 `IsHitTestVisible=false` 且插入页面图之下；粒子用 `FluentFrameAnimation` 有限 400ms 并在完成/取代/detach 时移除。`MotionResolver` 已保证 reduce 或 `categories=off` 下 decorative=false（`:82-85`），三态语义在解析层成立。

但实现仍有 4 个边界：① 只挂 `Activated/Deactivated`，未处理 `IsVisible`/隐藏（`FluentDecorativeMotion.cs:11` 的注释声称 hidden 会暂停，但代码没有对应钩子）；② `FluentTokenGradient.Bind` 对 `Application.Current.ResourcesChanged` 的订阅从不解除（`:271-277`），不是帧回调泄漏，但会长期保留 layer/brush；③ 粒子 `UpdatePageTurnParticles` 每帧写 `Canvas.Left/Top`（`FluentUi.cs:256-257`），属于布局属性，与"不触发重排"的严格口径不符（页面宿主未被重排，但粒子层自身会 measure/arrange）；④ IN-1.2 没有生产时钟的首/中/尾采样，也没有对粒子覆盖后的可读性/对比度断言。IN-1 的资产/令牌约束成立：diff 未新增图片/字体/颜色/几何资产；渐变只用 `Nm.Color.Bg.Canvas`/`Bg.Sunken`，粒子填充 `Nm.Color.Accent.Muted`，8s/400ms 已进 `MotionTimings` 常量；高对比测试验证两个停点仍解析既有令牌。自动化全关沿用既有 `MotionCategories`/`Reduce`（`MotionResolver` 已使 reduce/category-off 的 decorative=false），没有新增 env 开关；但 Handoff 缺失，开关名未在交付物中点名（R2-017/R2-012），`auto+系统关` 也未在 decorative 测试中单独覆盖。

**IN-2A 的五个选择器修复产品方向正确，但只做了一半。** Avalonia 类型选择器匹配精确类型，派生类需要 `:is()` 或 class-only；`x:SetterTargetType` 在 11.3.22 的 XAML 编译器中被接受（build 0 warning/0 error，14/14 有效断言通过）。逐类核对：`fluent-surface-card`/`fluent-dialog`/`fluent-book-card`/`fluent-book-row`/`fluent-region-box` 没有其他控件复用，`fluent-book-row` 出现在 `FluentUi.Button(..., "fluent-book-row")` 是有意的 plain Button 用法；因此这五个改动没有发现误启用其他类样式或类冲突。coverage 测试同步改写后的字符串一一对应，**文本层面等价**，但它只做 `<Style Selector="...">` 的 grep，新增 `.fluent-region-box` 是扩覆盖而非等价替换，并且完全没有覆盖 7 个未修的派生控件选择器（R2-005）。

**IN-2B 的证据生成器设计不成立。** `CaptureDecor()` 与 IN-1 无关；主题切换只动 Avalonia 内建主题变体，不动 DesignSystem 令牌；`Assert.DoesNotContain(Path.Combine("verification","FEA-06","screens"), output)` 对固定 output 是恒真断言，不能证明写域；inventory 固定写 `frame=mid`，缺 `head`。这些是证据可信度问题，不是测试数量问题。

**禁止范围与分层：** `git diff --exit-code 669a4ae02..HEAD` 对 `doc/design`、`DesignSystem/Generated`、`verification/FEA-06`、`Presentation.Avalonia`、`ApplicationCore`、`CoreClient`、`Host`、`doc/contracts`、`App/Shell`、`App.axaml.cs`、`MainWindow.axaml.cs`、`FrontendSelector.cs`、`Themes/**` 全部 EXIT=0；三个实现 commit 的文件均在 `allowed_paths` 内。新增依赖只有 `FluentUi.cs` 对 `App.ViewModels.Fluent` 的 using（R2-015，P2），不是契约/安全风险。

**Architecture 结论：** 未发现新的数据/契约/线程/持久化阻断；阻断集中在"视觉证据不可信/不完整 + 派生样式修复不彻底 + IN-2A 状态覆盖口径"。

## Spec（executed）：AC 判定

| AC | 判定 | 依据（不以测试数代替） |
|---|---|---|
| AC-1（IN-1.1/1.2 三态降级/暂停/无泄漏/视觉签署） | **NOT MET** | 行为测试 12/12 通过（reduce/category-off 无帧、detach 停帧、400ms 移除、生产时钟 shelf 采样），但 IN-1.1 的 full 首/中 + reduce 三张与 IN-1.2 的 full 中帧 + reduce 两张不存在；decor PNG 是灰色 Border 占位（R2-001）。失焦暂停测试直接调用 `Pause()`、未验证 `Deactivated` 接线；不可见窗口未处理；粒子无生产帧源/可读性断言（R2-012）。 |
| AC-2（IN-2A 16+1 组逐格有效属性） | **PARTIAL** | 14/14 通过，逐格期望值经抽查与样式锚点一致（SurfaceCard/BookCard/BookRow/Button/Slider/Segmented/TabItem/SearchField/SettingsField/RegionBox/ContextMenu/Tooltip/AlertBanner）；但 `expected-tokens.md` 缺失（R2-004），SurfaceCard 的 hover/selected/disabled 与 IconButton 的 checked 无状态通道、只断言默认值，SearchField 只断言抑制（R2-006/R2-007）；Slider 只断言 Foreground，thumb 仍是默认蓝（R2-006）。 |
| AC-3（IN-2B 像素格 + 独立签署） | **NOT MET** | 34 张 vs 冻结清单缺口见 R2-003；light/dark 主题标注不实（R2-002）；ReaderPage 是空章节、ReaderProgressBar 空白、SurfaceCard disabled 与 default 同字节、Slider 默认蓝、decor 无关（R2-001/R2-005/R2-006）；签署结果 12 PASS / 22 REJECT（附录 B）。 |
| AC-4（证据/回归/禁止范围/生成器/check/pins/旧 SHA） | **PARTIAL** | build、全量 1272/0/57、TokenGen/ThemeGen --check、check.ps1、verify_pins、旧四 PNG SHA、禁止路径均 PASS；但 `impl-in1/2a/2b` 日志缺 head、shell/host、逐程序集、57 skip 原因与差值（R2-009），inventory 缺 head（R2-008），Handoff 缺失（R2-017）。 |
| OUT/BLOCKED/D-14 | 未写达成 | 未见把 OUT 项或 BLOCKED 数据端口写成达成；Task 保持 `in_progress`。D-14 仍为"待 DSH 裁决"，测试按卡面临时口径对 NotStarted 特判（R2-016）；D-11 的九值映射没有写入证据文件（R2-004）。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 对应 AC | 建议 | 状态 |
|---|---|---|---|---|---|---|---|
| R2-001 | **P0** | `apps/desktop-avalonia/tests/NewManga.App.Tests/FluentResidual2VisualEvidenceTests.cs:150-156`；`verification/FEA-06-RESIDUAL-2/visuals/decor--shelf-gradient--default--full--light.png`、`...reduce--light.png`；`impl-in2b-verification.log:4`；`visual-inventory.md:35-36` | `CaptureDecor()` 两次都只渲染 `new Border { Width=320, Height=180, Background=Brushes.Gray }`，没有 `ShelfPageView`、`FluentDecorativeLoop`、`ReaderPageView` 或粒子层；两个文件 SHA-256 同为 `967752128…409A`（791 B）。IN-1.1 要求 full 首/中 + reduce 三张、IN-1.2 要求 full 中帧 + reduce 两张；实际 0 张有效 decor。以"decor 2 张"作为 IN-1 视觉证据会让 AC-1 的像素/签署半部分虚假达成。 | 读 `CaptureDecor()` 两行；`Get-FileHash` 两文件相同；打开图片为纯灰矩形；inventory 第 35-36 行均写 `frame=mid` | AC-1、AC-3 | 删除这两行与 PNG，或改为真实捕获：书架页 full 首/中 + reduce（捕获时断言 loop 相位/画刷 opacity），阅读器在有真实双页 fixture 下 full 中帧 + reduce（full 断言粒子层存在、reduce 断言 null）；重生成后重签。不得用当前文件签署。 | open |
| R2-002 | **P1** | `FluentResidual2VisualEvidenceTests.cs:38-51`、`:92-148`；`visual-inventory.md:3-34` | 只切换 `Application.Current.RequestedThemeVariant`；设计令牌由 `DesignSystemThemeManager`/`AppearanceCoordinator` 管理，默认 `AppearanceMode.System` 在此环境为 dark。结果：12/16 个 light/dark 对完全相同（34 文件中 26 个在相同哈希组），例如 surface-card 4 文件同一哈希 `26D2…`，book-card/book-row/icon/primary/region/reader-progress、reader/workbench 页面 light==dark；只有 Slider/ToggleSwitch（Avalonia 内建主题）和部分页面内建控件有差异。"light" 页面实际是 dark，inventory 的 theme 列不实。 | `Get-FileHash` 分组：34 files / 20 unique；surface-card 4 个同哈希；reader/workbench light==dark；打开 `pages--shelf--light`、`pages--settings--light` 为 dark；slider/toggle 的差异证明只切换了内建主题 | AC-1、AC-3 | 用 `DesignSystemThemeManager.SetAppearance(AppearanceMode.Light/Dark)`（参考 `FluentResidual2DecorativeTests.ShelfGradient_BindsOnlyExistingBgTokens…`）在创建 shell/组件窗口前设置主题；捕获前断言一个令牌颜色随主题不同；按真实主题重命名/重生成/重签。 | open |
| R2-003 | **P1** | `FluentResidual2VisualEvidenceTests.cs:92-123`、`:125-141`、`:150-156`；`visual-inventory.md`（34 行）；Task `:61-63`、`:112-123` | 34 张只覆盖 4 页面×2 主题、12 个组件状态（9 个组件）默认/disabled×2、2 decor。缺：IN-2A 的 SurfaceCard hover/selected、BookCard selected、BookRow disabled、Secondary/Danger disabled、IconButton hover/checked、ToggleSwitch 其余、Slider hover/disabled、Segmented selected/unselected/hover/pressed、TabItem hover、SearchField focus、SettingsField error/disabled、RegionBox hover、ContextMenu disabled、Tooltip opened、AlertBanner 九值；IN-2B 的 TopBand/NavRail/StatusBand、StreamingThumb、EmptyState/ErrorState/Skeleton、ChapterList/PageThumbStrip、真实 ReaderPage、非空 ReaderProgressBar、Dialog 开/关、Drawer、CommandPalette 空/结果；IN-1.1/1.2 的 5 张。AC-3 无法 MET；`impl-in2b:4` 的"components 12×light/dark … 等"与 checkpoint §134 的"IN-2B 完成"均高估覆盖。 | inventory 34 行；测试 cases 列表只到 `ReaderProgressBar`；Task IN-2B 清单逐项比对；reader 页图为"本章节暂无页面" | AC-3 | 按冻结清单扩矩阵（或由 DSH 重冻结缩小范围，不能由实现者自行改 IN/OUT）；真实双页 fixture 捕获 ReaderPage，ReaderProgressBar 至少设 Value；重生成后 inventory 行数=文件数，逐图签署。 | open |
| R2-004 | **P1** | 缺失文件 `verification/FEA-06-RESIDUAL-2/expected-tokens.md`；`FluentResidual2StateEffectiveTests.cs:19-20` 引用；`impl-zcode-prompt.md:15`；Task `:57`；scope-r3 R3R-007 | 测试头声明"Expected values and their anchors are frozen per group in verification/FEA-06-RESIDUAL-2/expected-tokens.md"，但该文件不存在（`git ls-files`/`Test-Path` 均为空）。因此 16+1 组的逐格期望令牌与锚点没有独立证据；D-11 的"设计四态↔StatusKind 映射写入证据"同样没有落盘；Reviewer 只能从测试代码反推，无法核对"期望值非实现者自造"。 | `git ls-files verification/FEA-06-RESIDUAL-2/expected-tokens.md` 空；`Test-Path` false；测试头 `:19-20` 原文 | AC-2 | 新增该文件：每组/状态 → 期望令牌键值 → 锚点（样式文件:行、`StatusCatalog` 成员、矩阵 EFFECTIVE 行）；加入 AlertBanner 九值映射与 D-14 例外；Handoff 链接；重跑后复核。 | open |
| R2-005 | **P1** | `Controls.Fluent.axaml:181`、`:197`、`:217`、`:221`、`:231`、`:238`、`:243`（另 `:204`/`:210` BLOCKED）；`FluentComponents.cs:52-59`、`:71-74`、`:88-98`、`:100-120` | 本次只把 5 个选择器改为 class-only + `x:SetterTargetType`；其余派生控件仍用"精确类型 + class"：`StackPanel.fluent-chapter-list`（ChapterList : StackPanel）、`Border.fluent-streaming-thumb`（StreamingThumb : Border）、`Border.fluent-reader-page`（ReaderPage : Border）、`ProgressBar.fluent-reader-progress`（ReaderProgressBar : ProgressBar）、`Border.fluent-settings-group`（SettingsGroup : Border）、`Grid.fluent-settings-field`（SettingsField : Grid）、`StackPanel.fluent-tab-strip`（TabStrip : StackPanel）——全部不匹配派生控件。直接后果：SettingsField 的 ColumnSpacing/RowSpacing/Margin、ChapterList/TabStrip 的 Spacing、StreamingThumb/SettingsGroup 的卡片表面、ReaderProgressBar 的 Foreground/Background/Corner、ReaderPage 的背景均未应用；IN-2A 的 SettingsField 组只断言了子 TextBox，未触及字段样式；coverage 测试也未包含这 7 个类。 | 读 `FluentComponents.cs` 基类与构造器；读上述 `Styles` 行；Avalonia 11.3.22 类型选择器语义（`:is(Button)` 才是派生匹配，docs）；`components--reader-progress--*` 为 295 B 空白帧 | AC-2、AC-3 | 用同一 class-only + `x:SetterTargetType`（或 `:is(Type)`）修完 7 个选择器；coverage 测试加入这些类；为 SettingsField/ChapterList/TabStrip/StreamingThumb/ReaderProgressBar/SettingsGroup 增加有效属性断言（Spacing/Background 等）；`FluentDialog` 也补一条有效断言；重生成受影响像素。 | open |
| R2-006 | **P1** | `Styles/Controls.Custom.axaml:72-80`；`FluentResidual2StateEffectiveTests.cs:202-225`；`components--slider--default--full--dark.png` | Slider 只声明 Foreground（normal/hover/disabled），未覆盖模板 thumb/track；实际渲染 thumb 为 Avalonia 默认蓝色、填充为金色，与 token 化设计明显不符。测试只断言 Foreground 与 disabled Opacity，无法发现该视觉缺陷；IN-2A Slider 组与 IN-2B Slider 格均因此不合格。 | 打开 slider 两张 PNG（蓝 thumb、金线）；读 `Controls.Custom.axaml:72-80`；测试只 `Assert.Equal(...Foreground)` | AC-2、AC-3 | 在允许的 `Styles/**` 内为 SliderThumb/Slider 模板补令牌（或由 DSH 将该格转 OUT/后续卡）；断言 thumb/track 颜色；重生成。 | open |
| R2-007 | **P1** | `FluentResidual2StateEffectiveTests.cs:49-89`、`:155-181`、`:294-320`；`component-state-matrix.md:56`、`:67`、`:72`；`impl-in2a-verification.log:10` | `SurfaceCard` 的 hover/selected/disabled 均只重复断言默认令牌（disabled 仅 `IsEffectivelyEnabled=false`），样式表中没有 `.fluent-surface-card:pointerover`/`.selected`/`:disabled`；`IconButton` 的 checked 只加 class 后断言默认 Background，没有 checked 通道；`SearchField` focus 只断言内边框保持 idle，未断言焦点环。测试注释也承认"no style channel"。这些格在矩阵中是 NOT_RUN，不能作为 16+1 组的 PASS 计入 AC-2；日志"含 hover/pressed/selected/disabled/focus 等状态"高估。 | 读测试三处；`Select-String` 样式表无 surface-card 状态选择器、无 `.fluent-icon.checked`；矩阵 `:56`/`:67`/`:72` 为 NOT_RUN | AC-2 | 在 expected-tokens/AC 表中把无通道格标 NOT_RUN；或由 DSH 批准补状态样式（超出本卡现有范围）；SearchField 补焦点环几何断言或标 PARTIAL；不要以默认值断言计入覆盖。 | open |
| R2-008 | P2 | `visual-inventory.md:1-36`；`FluentResidual2VisualEvidenceTests.cs:80`；Task `:83` | inventory 缺 `head` 列；`frame` 对所有行硬写 `mid`（静态组件/disabled 页也写 mid）；`mode` 只有 full/reduce，没有 auto-系统关/category-关 对照；`theme` 列不实（R2-002）；`signed_by` 仍为"待独立 Reviewer"。逐图元数据不满足 Task 的 head/场景/mode/视口/帧位/主题/命令/EXIT 要求。 | 读 inventory 头与 34 行；测试 `:80` 固定写 `mid` | AC-1、AC-3、AC-4 | 在测试/生成器中加 head（实现 commit）、真实 frame/mode、生成时间；重生成 inventory；签署列由本 Review 的附录 B 结果回填（由 DSH 授权的证据维护者执行）。 | open |
| R2-009 | P2 | `impl-in1-verification.log:2-10`；`impl-in2a-verification.log:1-9`；`impl-in2b-verification.log:1-6`；Task `:128` | 日志缺 head hash、shell/host 头、逐程序集计数（IN-1 写"其余程序集见输出"）、57 skip 逐条原因、与基线的差值说明（IN-2A/2B 只有总数）；不符合 R2S-010 冻结格式。不能用这些日志单独证明 AC-4。 | 逐行读三份日志；`impl-in1:10` 的"其余程序集见输出"；无 `head=`/`host=` 字段 | AC-4 | 追加一份完整日志（head、shell/host、命令、逐程序集、EXIT、差值、57 skip 原因或指向既有归因文件），或引用 DSH 集成日志；旧日志保留字节。 | open |
| R2-010 | P2 | `MotionTimings.cs:88-96` | 注释改为"any transition or decorative loop may run"，但表达式只包含 navigation/feedback，未包含 `DecorativeShelfGradientMilliseconds`/`DecorativePageTurnMilliseconds`/`DecorativeEnabled`。当前 `HasMotion` 只被测试使用，无生产影响，但诊断语义错误，且与 IN-1 日志"HasMotion 不再计入 decorative"的说明相反。 | 读 `MotionTimings.cs:88-96`；`grep HasMotion` 仅测试使用 | AC-1（诊断/可复核性） | 要么把 decorative 纳入 `HasMotion`，要么把注释改回"transition only"；补一个 decorative-only profile 的断言。 | open |
| R2-011 | P2 | `FluentDecorativeMotion.cs:271-277`；`FluentUi.cs:172-180`；`FluentDecorativeMotion.cs:239-244` | `FluentTokenGradient.Bind` 对 `Application.Current.ResourcesChanged` 的 lambda 从不解除订阅；每个 ShelfPageView/每次新建 shell 都会留下对 layer/brush 的强引用。`DecorativeShelfGradient` 同时给 GradientStop 设 DynamicResource，而 `FluentTokenGradient` 注释说该绑定不会解析，二者矛盾/冗余。帧回调泄漏要求已满足，但静态事件生命周期泄漏仍存在。 | 读 `:271-277` 无 unsubscribe；读 `FluentUi.cs:172-180` 与 `FluentDecorativeMotion.cs:239-244` 的注释 | AC-1（无泄漏） | detach 时解除 `ResourcesChanged`（或弱订阅）；删除冗余 DynamicResource 或写清两层回退；加一个"detach 后 handler 不保留"的断言。 | open |
| R2-012 | P2 | `FluentResidual2DecorativeTests.cs:144-172`、`:199-240`、`:266-299`、`:335-365`；`FluentDecorativeMotion.cs:11`、`:126-158` | ① `ShelfGradient_WindowDeactivated` 直接调用 `Pause()`（`:158`），只通过 `window.Activate()` 验证了 Activated 接线，`Deactivated` 事件本身未被触发；② 代码只挂 Activated/Deactivated，未处理隐藏/`IsVisible`，与 `:11` 注释"deactivated or hidden window pauses"不符；③ 三态中的 `auto`+系统关未在 decorative 测试中单独覆盖（reduce/category-off 已覆盖）；④ IN-1.2 只有手动时钟边界，没有生产 `FluentRenderClock` 首/中/尾采样；⑤ 粒子层没有对比度/可读性断言（Task `:52`、`:129` 要求），高对比只测了渐变令牌。 | 读测试四处；读 `FluentDecorativeMotion.cs:126-158`（只有 Activated/Deactivated）；Task `:52`/`:129` | AC-1 | 增加 Deactivated 的 headless 触发或事件级测试；挂 `IsVisibleChanged`/窗口隐藏；给粒子加生产帧源 200ms 中帧断言与可读性/对比度断言（或记录 DSH 裁决的替代口径）。 | open |
| R2-013 | P2 | `FluentUi.cs:252-257` | 粒子每帧除 Opacity/TranslateTransform 外还写 `Canvas.SetLeft`/`SetTop`（布局属性），与 Task `:47`"不触发重排"的严格口径不符；`UpdatePageTurnParticles` 还用常量 `MotionTimings.DecorativePageTurnMilliseconds` 计算 `total`（`:252`），与传入的 `progress` 来源脱钩。 | 读 `:238-263`；`Canvas.SetLeft/Top` 在每帧循环内 | AC-1 | 改为只在创建时定位一次 + 仅 RenderTransform/Opacity；`total` 由参数或 profile 显式传入；加布局不变量断言（如 Canvas child Bounds 不变）。 | open |
| R2-014 | P2 | `FluentAnimationCompletionTests.cs:30-33` | 既有完成测试的 helper 默认从 `MotionCategories.All` 收窄为 `Navigation \| Feedback`，以避开 decorative 的待决帧；这使得既有回归测试不再覆盖"装饰循环不应计入过渡完成"的边界。日志只说"装饰循环自有帧源"，没有指出哪条断言会因 All 失败。 | `git show d854d91b2 -- .../FluentAnimationCompletionTests.cs`；新默认 `:33` | AC-1（回归） | 保留默认 All，在需要的用例显式关 decorative；或新增一条明确断言说明 decorative 帧由 `FluentDecorativeLoop` 独立管理；Handoff 记录理由。 | open |
| R2-015 | P2 | `FluentUi.cs:9`、`:252` | App/Controls 层新增 `using NewManga.App.ViewModels.Fluent` 仅为拿 `MotionTimings.DecorativePageTurnMilliseconds`；Controls→ViewModels 是反向依赖，且使 400ms 常量来源不直观。 | 读 `FluentUi.cs:9`；`grep "using NewManga.App.ViewModels" Controls/*.cs` 仅此一处 | AC-1（分层） | 把 duration 作为 `UpdatePageTurnParticles` 参数传入，或把常量放到中性层；避免 Controls 依赖 ViewModels。 | open |
| R2-016 | P2 | `Controls.Status.axaml:35-38`；`Status.cs:85`；`FluentResidual2StateEffectiveTests.cs:457-459`、`:488-491`；Task `:110` | D-14 仍无 DSH 裁决/登记文件：`StatusCatalog.ColorKey(NotStarted)` 返回 `Text.Disabled`，样式权威用 `Text.Secondary`；测试按卡面临时口径断言样式值并在交叉断言对 NotStarted 特判。处理是诚实的（有注释、未删交叉断言），但例外没有进入 expected-tokens/证据文件，后续容易被当成永久口径。 | 读 Status/StatusCatalog/测试三处；Task `:110` 仍写"待 DSH 裁决" | AC-2（治理） | DSH 记录 D-14 处置（后续卡改 catalog 或重冻结），在 expected-tokens 写明例外；测试保持显式特判并可追溯。 | open |
| R2-017 | P2 | 缺失 `doc/handoffs/FEA-06-RESIDUAL-2-impl.md`；`impl-zcode-prompt.md:37` 要求 | 实施交付要求 Handoff 记录 commit/计数/逐 IN/未完成/OUT/NOT_RUN/证据路径；实际没有该文件。没有任何地方把 IN-1/2A/2B 的边界、D-14 例外、视觉待签、证据命令集中起来，Reviewer 只能从日志与 checkpoint 拼。 | `git ls-files doc/handoffs/FEA-06-RESIDUAL-2-impl.md` 空；`Test-Path` false | AC-4 | 补 Handoff（不改旧证据字节），含逐 IN 状态、expected-tokens 链接、visual sign-off 状态、D-14、NOT_RUN/BLOCKED、命令/EXIT、下一 reviewer 指令。 | open |
| R2-018 | P2 | `FluentResidual2VisualEvidenceTests.cs:58-65`、`:96-97` | `Assert.DoesNotContain(Path.Combine("verification","FEA-06","screens"), output)` 中 `output` 固定为 `.../FEA-06-RESIDUAL-2/visuals`，该断言恒真，不能证明"禁止写 FEA-06"；测试还从 `verification/FEA-06/runtime` 读取 appearance store（当前不存在），若该文件存在会静默改变主题。 | 读 `:58-65`（output 固定）；`:96-97` 路径 | AC-3、AC-4 | 断言 output 精确等于预期路径，使用 workspace/temp 隔离 appearance store；捕获前后记录 `git status --porcelain` 并在测试内断言无 `verification/FEA-06/**` 写入。当前默认运行零写入已由本 Review 实跑确认。 | open |
| R2-019 | P2 | `doc/REBASELINE_PLAN.md:22`、`:39`；`doc/STATUS.md:10` | scope-r3 R3R-001 的三处活文本仍未刷新：PLAN `:22` 仍是 RESIDUAL-1 Batch B/1195 旧态，PLAN `:39` 仍写"下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）"，STATUS `:10` 仍写"下一步：无 READY 节点"，与同文件 `:7`/`:37` 矛盾。不是本实现 diff 引入，但 reviewed_head 仍处矛盾状态，影响冻结台账。 | 读三处现状；`git log` 显示仅在 `1f53336e8` 更新了少量行 | 治理 | DSH 在任何终态判定前刷新三处活文本或登记推迟理由/Owner/时点；不改历史快照。 | open |

## Verification（executed）

环境：Windows 11，PowerShell 7，`dotnet` SDK（net9.0 测试目标），Avalonia 11.3.22；仓库 `G:\CODEX\New Manga`，branch `main`；`NEWMANGA_CAPTURE_RESIDUAL2_PNGS` 未设置（默认运行）；`git status` 在开始时与全量测试后均为空。本 Review 未重跑 opt-in 捕获（避免改写已提交 PNG 字节），也未执行原生 DPI/a11y。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定 head/工作树 | `git rev-parse HEAD`；`git status --porcelain` | `854e5bb1b` | PASS（干净） | HEAD 与 `reviewed_head` 一致；实现 head `998d75bdb` |
| 构建 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | HEAD | PASS，`BUILD_EXIT=0` | 0 warnings / 0 errors |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | HEAD | PASS，`TEST_EXIT=0` | **1272 passed / 0 failed / 57 skipped**；逐程序集：Appearance 21、Presentation 38、Host 51/28、ThemeEngine 253、DesignSystem 111、ApplicationCore 31、CoreClient 128/22、App 639/7；合计 1272/57，总 1329；较任务基线 1245 +27，与 delivery 1272 持平 |
| 默认零仓库写入 | 全量测试后 `git status --porcelain` | HEAD | PASS | 工作树为空；未新增/改写 `verification/**` |
| TokenGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.DesignSystem\tools\NewManga.DesignSystem.TokenGen -- --check` | HEAD | PASS，`TOKENGEN_EXIT=0` | 292 rows，byte-for-byte up to date |
| ThemeGen | `dotnet run --project apps\desktop-avalonia\src\NewManga.ThemeEngine\tools\NewManga.ThemeEngine.ThemeGen -- --check` | HEAD | PASS，`THEMEGEN_EXIT=0` | byte-for-byte up to date |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | HEAD | PASS，`CHECK_EXIT=0` | 3 既有 warnings（9 非终态 Task、STATUS/PLAN 预算 80%）；不替代审查 |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | HEAD | PASS，`PINS_EXIT=0` | 15/15 |
| 旧 FEA-06 四 PNG SHA | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | HEAD | PASS | reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…e2df5`，与 Task `:128` 全值一致；零 diff |
| 禁止路径 | `git diff --exit-code 669a4ae02..HEAD -- <path>` 对 `doc/design`、`DesignSystem/Generated`、`verification/FEA-06`、`Presentation.Avalonia`、`ApplicationCore`、`CoreClient`、`Host`、`doc/contracts`、`App/Shell`、`App.axaml.cs`、`MainWindow.axaml.cs`、`FrontendSelector.cs`、`DesignSystem/Themes` | HEAD | PASS | 全部 EXIT=0；三个实现 commit 的文件均落在 Task `allowed_paths` |
| 实现 commit 写域 | `git show --name-only d854d91b2 1d2df1d15 998d75bdb` | 三个 commit | PASS | IN-1：FluentUi/MotionTimings/Views/Fluent/tests/log；IN-2A：Controls.Fluent.axaml/tests/log；IN-2B：visual test/log/visuals。无 Core/契约/生成物/冻结设计/组合根 |
| IN-2A 测试判别力 | 全量内 `FluentResidual2StateEffectiveTests` 14/14；逐条对照样式锚点 | HEAD | PARTIAL | 值匹配（见 Findings 表 R2-004/R2-006/R2-007），但 3+ 格无状态通道、expected-tokens 缺失 |
| IN-1 测试判别力 | 全量内 `FluentResidual2DecorativeTests` 12/12；读断言 | HEAD | PASS（行为） / FAIL（视觉） | 降级/停帧/400ms/生产时钟 shelf 通过；粒子无生产时钟，暂停/隐藏与像素证据缺口（R2-012/R2-001） |
| 视觉逐图检查 | 34 张 PNG 逐张看图；`Get-FileHash` 分组 | HEAD | **FAIL** | 34 files / 20 unique；12 PASS / 22 REJECT（附录 B）；R2-001/R2-002/R2-003/R2-005/R2-006 |
| 证据日志格式 | 读三份 log；Task `:128` 对照 | HEAD | FAIL（P2） | 缺 head/shell/host/逐程序集/57 skip 原因/差值（R2-009） |
| 57 skip 归因 | 全量日志 `[SKIP]` 计数；`verification/FEA-06/skip-analysis.md` | HEAD | PASS（计数）/ 部分 | 57 条，均为既有 sidecar fixture 自跳过（未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`）；与基线同数，未新增；逐条名称在完整日志，原因未逐条重开 |
| opt-in 像素再生成 | 未执行 | HEAD | NOT_RUN | 为避免改写已提交证据字节；写域与 inventory 由代码审阅判定（R2-018） |
| D-14 / OUT / BLOCKED | 读 Task、logs、代码 | HEAD | 未写达成 | Task 保持 in_progress；D-14 仍待裁决；无 OUT/BLOCKED 被写成 MET |
| 原生 DPI/a11y/桌面 | — | B-5/D-1 | NOT_RUN/BLOCKED | 无硬件；不伪造 |
| PLAN/STATUS 一致性 | 读 `:22`/`:39`/`:10` | HEAD | FAIL（P2） | R3R-001 未刷新（R2-019） |

**证据纪律说明**：上表命令均在本轮实际执行；build/test/generators/governance 之后 `git status` 仍净。未把 opt-in、原生视觉或 NOT_RUN 计 PASS。全量 1272/0/57 只说明现有断言通过，不等同 AC-1…AC-4 达成。

## 附录 A：关键 SHA 与统计（复现用）

```text
HEAD / reviewed_head = 854e5bb1b0602b3e48f6b4d4a514432a864c8504
implementation_head  = 998d75bdb1e231d4ae2e2dd377b21452dd316cc9
base_commit          = 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431

decor full   96775212D657D92DCF653D40320BAC2B0157B920D30D5A2BB94920BB364E409A
decor reduce 96775212D657D92DCF653D40320BAC2B0157B920D30D5A2BB94920BB364E409A
surface-card default light  26D2D0508ACA2A114B7A0720CE7B653A8BC387D507983B5785AF6ED0998ACBCC
surface-card disabled light 26D2D0508ACA2A114B7A0720CE7B653A8BC387D507983B5785AF6ED0998ACBCC
surface-card default dark / disabled dark 同 26D2…（4 文件同哈希）
reader-progress light/dark  635A270DAD5462357AF98AA2F24B487F0FFD3255D141B88DF8CD2C2D48426640
reader page light/dark      2E188B5A37100366204121FB69F5BFC1E4768965595FFE81F3FF382A0ECB48F6
slider light                CA7A59C449290351C091E0D70C372A94A910BFD10D9866D8AAF3BD7E3482A232
shelf light                 9AE3624EBE1FF3404B387603F853CFC990FBAAEC73EAF5832715830770ECE486
shelf dark                  A9A2A8418415BC6D731B7206ED5A5D32657815AC5B3E6FCB55622C52D0E16613

PNG: 34 files / 20 unique SHA-256; 12/16 light/dark pairs byte-identical;
     26/34 files belong to duplicate groups.
全量: 1272 passed / 0 failed / 57 skipped.
```

## 附录 B：34 张 PNG 逐图签署表

签署口径：PASS = 该文件能作为其 inventory 所声称格位（组件/状态/mode/theme）的视觉证据；REJECT = 主题不实、内容无关、空帧、状态无差异或明显样式缺失。REJECT 项不得用于 AC 判定；本表不修改 `visual-inventory.md` 原字节，由 DSH/授权证据维护者回填。未签署项本应为 NOT_RUN；本表已覆盖全部 34 项，无 NOT_RUN。

| # | file | 结论 | 一句理由 |
|---|---|---|---|
| 1 | `components--book-card--default--full--dark.png` | PASS | BookCard 默认表面/圆角/内容真实渲染；文本有子像素彩边但无布局错位。 |
| 2 | `components--book-card--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同，实际 dark）。 |
| 3 | `components--book-card--disabled--full--dark.png` | PASS | 禁用透明度可见，禁用态与默认态有差异。 |
| 4 | `components--book-card--disabled--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 5 | `components--book-row--default--full--dark.png` | PASS | BookRow 表面/边框/文本真实渲染。 |
| 6 | `components--book-row--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 7 | `components--icon-button--default--full--dark.png` | PASS | fluent-icon 按钮默认态渲染；内容为文本而非 NmIcon，仅供默认态。 |
| 8 | `components--icon-button--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 9 | `components--primary-button--default--full--dark.png` | PASS | 主按钮 accent 背景/前景/圆角可见。 |
| 10 | `components--primary-button--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 11 | `components--primary-button--disabled--full--dark.png` | PASS | 禁用背景/前景/Opacity 与默认态可区分。 |
| 12 | `components--primary-button--disabled--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 13 | `components--reader-progress--default--full--dark.png` | REJECT | 300×70 单色空白帧，ProgressBar/样式未渲染。 |
| 14 | `components--reader-progress--default--full--light.png` | REJECT | 同上且 theme=light 未生效；与 dark 版字节相同。 |
| 15 | `components--region-box--default--full--dark.png` | PASS | RegionBox 的 Accent 表面/边框/文本真实渲染。 |
| 16 | `components--region-box--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 17 | `components--slider--default--full--dark.png` | REJECT | thumb 为 Avalonia 默认蓝、填充/轨道未令牌化，明显样式不符。 |
| 18 | `components--slider--default--full--light.png` | REJECT | 同上，且 theme=light 未生效。 |
| 19 | `components--surface-card--default--full--dark.png` | PASS | SurfaceCard 容器默认表面/圆角可见（无内容）。 |
| 20 | `components--surface-card--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |
| 21 | `components--surface-card--disabled--full--dark.png` | REJECT | 与 default dark 完全同哈希，disabled 无视觉差异。 |
| 22 | `components--surface-card--disabled--full--light.png` | REJECT | 与 default 同哈希且 theme=light 未生效。 |
| 23 | `components--toggle-switch--disabled--full--dark.png` | PASS | ToggleSwitch 轨道/滑钮/Off 文本可见，disabled 态可辨。 |
| 24 | `components--toggle-switch--disabled--full--light.png` | REJECT | 近空白，light 变体下文本/轨道不可见。 |
| 25 | `decor--shelf-gradient--default--full--light.png` | REJECT | 纯灰矩形，非书架渐变/IN-1 装饰；与 reduce 同哈希。 |
| 26 | `decor--shelf-gradient--default--reduce--light.png` | REJECT | 同上，且与 full 同哈希，未体现 reduce 静态/降级。 |
| 27 | `pages--reader--default--full--dark.png` | REJECT | 显示"本章节暂无页面"，不是 ReaderPage 单页渲染；与 light 同哈希。 |
| 28 | `pages--reader--default--full--light.png` | REJECT | 空章节页且 theme=light 未生效（与 dark 版字节相同）。 |
| 29 | `pages--settings--default--full--dark.png` | PASS | 设置页真实渲染，字段/分组可见；数据面符合当前 fixture。 |
| 30 | `pages--settings--default--full--light.png` | REJECT | 实际为 dark，且搜索框/`corners.scale` 等值与 dark 版缺失不一致。 |
| 31 | `pages--shelf--default--full--dark.png` | PASS | 书架页真实渲染，卡片/工具栏/状态带可见。 |
| 32 | `pages--shelf--default--full--light.png` | REJECT | 实际为 dark；搜索框文本缺失，theme 元数据不实。 |
| 33 | `pages--workbench--default--full--dark.png` | PASS | 工作台页真实渲染；数据面为空，与 BLOCKED B-1/B-2 一致。 |
| 34 | `pages--workbench--default--full--light.png` | REJECT | theme=light 未生效（与 dark 版字节相同）。 |

**签署统计：12 PASS / 22 REJECT。** 关键失败面：全部 18 张 light 图（theme 不实）、decor 2 张（无关占位）、ReaderPage 2 张（空章节）、ReaderProgressBar 2 张（空白）、Slider 2 张（默认蓝）、SurfaceCard disabled 2 张（无状态差异）、ToggleSwitch light 1 张（不可见）、Settings light 1 张（布局/值缺失）。因此 AC-1 的像素 + 签署条件与 AC-3 均不能成立。

## 结论与复审

**verdict = changes_requested。** 本 head 的代码行为回归、门禁和禁止范围是干净的；IN-1 的 render-frame 结构、IN-2A 的五个选择器修复方向、IN-2B 的默认零写入都值得肯定。但本卡的验收对象是 Flutter 视觉残项，当前提交的"视觉证据"不满足可信、可复核、可签署的最低条件，且派生控件样式修复只覆盖了同类缺陷的一部分。不能批准进入集成，也不能把 AC-1/AC-3 写成 MET。

**必须在本 Review 后处置（再复审门槛）**：

1. R2-001（P0）：删除/替换假 decor 证据，补 IN-1.1 三张与 IN-1.2 两张真实捕获。
2. R2-002（P1）：用 DesignSystem 主题管理器真正切换 light/dark，重生成并重签。
3. R2-003（P1）：按冻结清单补齐 IN-2B（或由 DSH 明确重冻结缩减范围），ReaderPage 用真实页面 fixture。
4. R2-004（P1）：新增 `expected-tokens.md`（逐格令牌 + 锚点 + D-11 映射 + D-14 例外）。
5. R2-005/R2-006（P1）：修完剩余 7 个派生控件选择器；Slider thumb/track 令牌化并补断言。
6. R2-007（P1）：把无通道状态格改记 NOT_RUN/产品缺口，不得计入 16+1 全组 PASS。
7. R2-008/R2-009/R2-017（P2）：补 inventory 元数据、完整证据日志和 Handoff；R2-019 由 DSH 刷新 PLAN/STATUS 三处活文本。

复审要求：新 head 必须重新 Appointment 独立上下文 Reviewer；复审逐条核对 R2-001…R2-019 的处置、重新逐图签署（附录 B 的 PASS 图除外，REJECT 图必须重签），并确认 AC-1/AC-3 的像素与签署、AC-2 的 expected-tokens 锚点。不得以 1272/0/57 或"图存在"替代视觉签署；不得写 D-14/OUT/BLOCKED 达成；不得 push。

**推荐下一步**：Task=`FEA-06-RESIDUAL-2`，Agent=DSH（findings 处置/范围裁决）→ ZCode（返修）；启动条件=DSH 接收本报告并决定 R2-003 是扩容还是重冻结。Recovery point=`G:\CODEX\New Manga`、main、同一 worktree，base=`669a4ae02`，reviewed_head=`854e5bb1b`，implementation_head=`998d75bdb`。本 Reviewer 未参与实现或返修，唯一仓库交付为本文件；未修改生产源码/Task/证据/冻结设计，未 commit/push。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga` 的 main 接收 `doc/reviews/FEA-06-RESIDUAL-2-impl-r1.md`：**changes_requested，P0=1 / P1=6 / P2=12**。先核对 HEAD/工作树（`854e5bb1b`、干净）。按 R2-001 删除/替换 decor 假证据并补 IN-1.1/1.2 五张真实捕获；按 R2-002 用 DesignSystemThemeManager 真正切换 light/dark；按 R2-003 决定 IN-2B 是扩容还是重冻结（不得由实现者自行缩范围），补 ReaderPage 真实页面；按 R2-004 补 expected-tokens.md（逐格锚点 + D-11 映射 + D-14 例外）；按 R2-005/R2-006 修完剩余派生控件选择器与 Slider thumb/track；按 R2-007 把无通道状态格改 NOT_RUN。处置 R2-008/009/017 的 inventory/日志/Handoff，并由你刷新 R2-019 的 PLAN/STATUS 三处活文本。保持 D-14 待裁决、OUT/BLOCKED 不求达成、Task `in_progress`；不得据 1272/0/57 写 AC 达成，不得 push。返修后重新 Appointment 独立上下文 Reviewer，逐图重签并复核 R2-001…R2-019。
