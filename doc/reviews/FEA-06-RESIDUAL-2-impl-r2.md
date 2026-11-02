---
task_id: FEA-06-RESIDUAL-2
reviewer: DSH 独立子 agent（独立上下文 Reviewer；D-9 workflow job workflow-8eb284e7f674494c）
reviewer_kind: subagent
author: DSH main session（IN-1/IN-2A/IN-2B、R2 返修与最终 decor/Handoff；Codex/ZCode 额度窗口不可用期间按 D-7/D-9）
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: 5944f96527b0adee6964a8b1266ddfa00de4e0d6
implementation_head: dc1543005a048157423969cd4ee73522d84f8ec6
prior_review: doc/reviews/FEA-06-RESIDUAL-2-impl-r1.md（changes_requested；P0=1/P1=6/P2=12）
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 6
p2: 12
provenance:
  agent: DeepSeek Harness 独立子 agent（与实现/返修主会话无共享上下文）
  appointment: 用户本轮 FEA-06-RESIDUAL-2 impl-r2 Review 指令（D-9）
  implementation_participation: none
  subagents: none
  mode: read_only_except_this_report
  environment: Windows 11；pwsh 7；dotnet SDK（net9.0）；Avalonia 11.3.22；repo G:\CODEX\New Manga；branch main
  date: 2026-11-03
  reviewed_tree: implementation_head dc1543005；dc1543005..reviewed_head 仅 docs/checkpoint/ADJ/D-14 后续卡变更；D-14 ADJ 已由 5944f965 收录，工作区只剩本 Review 未跟踪
  head_moved_during_review: dc1543005 → 4a22168f1 → 195422c2f → 5944f965（均不改代码与证据；最后一并收录 D-14 ADJ 并释放 D-14-STATUS-COLOR-FIX）
---

# Review：FEA-06-RESIDUAL-2 impl-r2

**verdict = changes_requested（P0=0 / P1=6 / P2=12）。当前 head 不应进入 DSH 集成。**

上一轮 P0（decor 灰色占位）确已删除，本轮 `dc1543005` 用 `ManualFluentMotionClock` 驱动真实 `ShelfPageView`/`ReaderPageView` 装饰层，产出 5 张真实 decor 帧且 SHA 互不相同；`FluentResidual2DecorativeTests` 的行为断言（三态降级、400ms 移除、detach 停帧、生产时钟 shelf 采样）成立。机械门禁也全部通过：build 0/0、无过滤全量 **1274 passed / 0 failed / 57 skipped**、TokenGen 292 行/ThemeGen `--check`、`check.ps1` PASS(3)、`verify_pins` 15/15、旧 FEA-06 四 PNG SHA 不变、禁止范围 diff 全为 0。

但本卡的验收对象仍是**可信、可签署的视觉证据**；逐图检查后，本轮核心结论不能成立（实际目录为 pages 8 / components **21** / decor 5；brief/Handoff 的“components 19”与文件数不符）：

1. **页面 light/dark 仍不真实**：4 张 "light" 页面实际全是 dark；settings 的 light/dark 两张仅差 216 像素（0.023%），差异只是 `appearance.mode` 文本本身。测试只写入 `AppearanceCoordinator`，创建 shell 时没有传 `DesignSystemThemeManager`，也没有任何"令牌随主题变化"的断言。所谓"配对 SHA 全不同"来自页面淡入/重绘差异，不是主题切换（R2R2-001，P1）。
2. **IN-1.2 粒子帧看不到粒子**：粒子层以 `Insert(0, ...)` 放在不透明 `DsReaderPage` 之下（`FluentDecorativeMotion.cs:207`），mid/none 两图 69% 像素的差异是页面淡入（页面红均值 102 vs 123），没有任何金色粒子像素；shelf 渐变帧的整片背景只变化约 1 个 RGB 单位（1.7% 像素差 >8），且文件名仍写 light（R2R2-002，P1）。
3. **Slider thumb 仍是系统蓝**：`Controls.Custom.axaml:81-90` 新增的 `/template/ Thumb` 规则没有改变渲染；默认 thumb PNG 的 SHA `CA7A59C4…` 与 R2 返修前完全相同，测试仍只断言 `Foreground`/`Opacity`（R2R2-003，P1）。
4. **IconButton checked 像素是无效格**：视觉测试的 checked 用例没有 `fluent-icon` class（`:138-139`），而状态规则是 `Button.fluent-icon.checked`；两张 PNG 同为 714 B、同一 SHA `5684D773…`（R2R2-004，P1）。
5. **IN-2B 清单仍远小于冻结范围，且存在空白帧**：ReaderPage 仍是"本章节暂无页面"空态；ReaderProgressBar 仍是 295 B 空白帧；PageThumbStrip 433 B 空白帧；ChapterList 文本顶部被裁切；21 个组件格远少于 `10-component-inventory` + Task `:61-63` 的冻结清单（R2R2-005，P1）。
6. **expected-tokens 只有"形状"，没有锚点**：文件存在，但多个格子仍是"以样式令牌解析值为准"，没有 file:line 锚点、没有 D-11 四态↔StatusKind 映射，且写着"light/dark 由 AppearanceCoordinator 主题决定"这一与实测相反的前提（R2R2-006，P1）。

测试数只证明已写入的断言通过，**不能据此判 AC**。AC-1 与 AC-3 明确未 MET；AC-2 为 PARTIAL；AC-4 的机械门禁 PASS 但证据元数据/日志/Handoff 仍为 PARTIAL。Task 必须保持 `in_progress`；D-14/OUT/BLOCKED 不得写达成；不得 push。

## 范围与依据

仓库 `G:\CODEX\New Manga`，branch `main`。审查开始时 `HEAD=dc1543005`（实现与证据树）；审查期间 head 前进到 `4a22168f1`、`195422c2f`、`5944f965`，均只改 docs（checkpoint、D-14 ADJ、D-14 后续卡、Task D-14 文字）。本报告把 `reviewed_head` 固定为写报告时的 `5944f965`，代码/证据等价于 `dc1543005`。`base_commit=669a4ae02`（RESIDUAL-1 集成/证据 head）。`doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md` 是 Codex CLI 的 D-14 裁决，现已由 `5944f965` 收录，不属于本 Review 的交付；本 Reviewer 未修改它。

已读（只读）：

- `doc/reviews/FEA-06-RESIDUAL-2-impl-r1.md` 全文（含附录 B 34 图签署：12 PASS / 22 REJECT）与 `doc/tasks/FEA-06-RESIDUAL-2.md`（scope v3、IN-1.1/1.2、IN-2A/2B、OUT/BLOCKED、证据形式、AC 表）。
- 提交链 `d854d91b2`（IN-1）、`1d2df1d15`（IN-2A + 派生选择器修复）、`998d75bdb→bfacfe09c→21e305249→9f5723cb0→7e21b4de8→dc1543005`（IN-2B/R2）。
- 冻结设计 `doc/design/fluent-v1/02-motion.md` §2.3/§4、`03-accessibility.md` §4、`10-component-inventory.md`。
- 代码/测试：`FluentResidual2VisualEvidenceTests.cs`、`FluentResidual2DecorativeTests.cs`、`FluentResidual2StateEffectiveTests.cs`、`FluentComponentStateCoverageTests.cs`；`FluentDecorativeMotion.cs`、`FluentUi.cs`、`ReaderPageView.cs`、`FluentShellSurface.axaml.cs`、`SettingsViewModel.cs`、`MotionTimings.cs`、`Controls.Fluent.axaml`、`Controls.Custom.axaml`。
- 证据：`verification/FEA-06-RESIDUAL-2/visuals/` 34 张 PNG 逐张查看、`visual-inventory.md`、`expected-tokens.md`；`impl-in1/in2a/in2b-verification.log`；`doc/handoffs/FEA-06-RESIDUAL-2-impl.md`；checkpoint §135–§143；`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`。
- 治理：`doc/templates/REVIEW.md`、`tools/governance/check.ps1`、`verify_pins.ps1`（只读运行）。

未审/未执行：opt-in PNG 再生成（为保持已提交证据字节，见 R2R2-014）、原生 200% DPI/触摸、原生 a11y、逐像素美学评分（B-5/D-1 无硬件）。未修改任何生产源码、Task、证据或冻结设计；未 commit/push；唯一持久交付为本文件。

## Architecture（executed）

**IN-1 的结构方向仍成立，但"视觉可见性"没有成立。** `FluentDecorativeLoop` 只用 `IFluentMotionClock.RequestFrame`，无 dispatcher timer/后台线程；`Configure` 在 `period<=0` 时 `StopRunning`；`DetachedFromVisualTree` 停帧；8s/400ms 已进 `MotionTimings`；粒子只改 `Opacity`/`RenderTransform`（`FluentUi.cs:238-263`），不新增图片/字体/颜色资产。但本轮没有改任何产品源码（`854e5bb1b..HEAD` 的产品变更只有两个 `Styles/*.axaml`），因此 r1 指出的 4 个边界原样保留：① 只有 `Activated/Deactivated`（`:136-137`、`:156-158`），与 `:11` "deactivated or hidden" 注释不符，`IsVisible` 未处理；② `FluentTokenGradient.Bind` 对 `Application.Current.ResourcesChanged` 的 lambda（`:272-277`）从不解除；③ 粒子每帧仍写 `Canvas.SetLeft/Top`（`:256-257`）；④ 没有粒子生产时钟采样与可读性断言。

**新增的 decor 帧确实来自产品层，但像素层面不能证明 IN-1.2。** `Decor_Frames_Are_Captured_Only_When_Opted_In` 用 Manual clock 推进；shelf 的 first/mid/static 与粒子 mid/none 均不同 SHA。问题在构图上：`FluentPageTurnDecor.Play` 明确 `area.Children.Insert(0, layer)`，放在 `DsReaderPage` 之下；该 page surface 通过 `.fluent-reader-page` 仍是 `Nm.Color.Bg.Sunken` 不透明背景，1×1 红图又被放大到整页，粒子被完全遮住。像素核对：mid 与 none 在页面区域的差异是整片红色亮度（mid 约 102 vs none 约 123），不是粒子；整图金色像素仅 1609 vs 1535（主要是工具栏/按钮），没有粒子层新增的金色点。shelf 三帧的整片背景均值 13.0/12.1/12.5 RGB，差异只有约 1 个色阶，眼睛几乎不可辨。这些帧是真实的，但不能支撑"full 中帧可见粒子"或"full 渐变可见"的签署。

**IN-2A 的选择器修复完成，状态通道只完成一半的"证据链"。** 9 个派生控件选择器（r1 列的 ChapterList/StreamingThumb/ReaderPage/ReaderProgressBar/SettingsGroup/SettingsField/TabStrip，加 r1 记作 BLOCKED 但现在一并修的 BatchMatrix/RunProjectionBar）均已改为 class-only + `x:SetterTargetType`，方向正确；`SurfaceCard` hover/selected/disabled 与 `Button.fluent-icon.checked` 也已有真实样式规则，`FluentResidual2StateEffectiveTests` 15/15 通过。但 Slider thumb 规则没有改变渲染（见 R2R2-003）；`FluentComponentStateCoverageTests` 的 `RequiredSelectors` 仍没有这 9 个类；SettingsField/TabStrip/StreamingThumb/ReaderProgressBar/ReaderPage/SettingsGroup 没有解析后属性断言，只有子 TextBox 或 Foreground 的弱断言。`SearchField` 仍只断言 focus 时内边框保持 idle，没有断言焦点环（`:312-338`），测试头注释（`:19-23`）也仍写着"SurfaceCard/IconButton 无状态通道"，与实际实现漂移。

**IN-2B 的证据生成器仍不成立为"主题证据生成器"。** 页面循环只 `appearance.SaveAsync(Mode=Light/Dark)` 后 `FluentShell.CreateRoot(selection, host, appearance)`，没有传 `themeManager`；`FluentShellSurface` 只把 `Appearance.Changed` 用于 motion（`:150`、`:680-695`），真正应用外观的是 `SettingsViewModel.ApplyToThemeManager`（`:345-360`）或 `ThemeManager.SetAppearance`（`FluentShellSurface.axaml.cs:650-654`）。settings 页自己的 `appearance.mode` 从 light 变 dark，而 UI 完全不变，这是最直接的复现证据。组件由 `Render()` 单独建 Window、设 `RequestedThemeVariant=Light`，但实际 palette 仍是 dark，故标注为 `current`；这不是"真实双主题"，只是诚实地把缺口标出来。

**禁止范围与分层：** `git diff --exit-code 669a4ae02..HEAD` 对 `doc/design`、`DesignSystem/Generated`、`verification/FEA-06`、`Presentation.Avalonia`、`ApplicationCore`、`CoreClient`、`Host`、`doc/contracts`、`App/Shell`、`App.axaml.cs`、`MainWindow.axaml.cs`、`FrontendSelector.cs`、`DesignSystem/Themes` 全部 EXIT=0；各实现 commit 的文件均落在 `allowed_paths`。新增依赖只有 `FluentUi.cs:9` 对 `App.ViewModels.Fluent` 的 using（R2R2-016，P2）。未见数据/契约/线程/持久化阻断；阻断集中在视觉证据真实性、IN-2B 覆盖与 R2-012/R2-011 的产品侧残留。

**Architecture 结论：** 分层与禁止范围干净；IN-1 的帧源结构、IN-2A 的 class-only 选择器方向、状态通道属性实现成立；不成立的是"light/dark 已真实切换"、"粒子 mid 帧可见"、"Slider thumb 已令牌化"这三条视觉/主题结论。

## Spec（executed）：AC 判定

| AC | 判定 | 依据（不以测试数代替） |
|---|---|---|
| AC-1（IN-1.1/1.2 三态降级/暂停/无泄漏/视觉签署） | **NOT MET** | 行为测试通过（reduce/category-off 无帧、detach 停帧、400ms 移除、生产时钟 shelf 采样）；但 IN-1.2 的 full mid 帧看不到粒子（层在不透明页面下），shelf 渐变三帧肉眼几乎相同且 theme 标错；`Deactivated` 未真正触发（测试直接 `Pause()`），`IsVisible` 未接；粒子无生产时钟与可读性断言。 |
| AC-2（IN-2A 16+1 组逐格有效属性） | **PARTIAL** | 15/15 状态测试通过，SurfaceCard hover/selected/disabled 与 IconButton checked 已有真实通道；但 `expected-tokens.md` 无 file:line 锚点、无 D-11 映射且有多处占位（R2R2-006）；Slider thumb 仍默认蓝（R2R2-003）；SearchField 焦点环、SettingsField/TabStrip 解析后属性未断言；`FluentComponentStateCoverageTests` 未覆盖这 9 个派生类。 |
| AC-3（IN-2B 像素格 + 独立签署） | **NOT MET** | 34 张（pages 8 / components 21 / decor 5）中 15 PASS / 19 REJECT；4 张 light 页面实际 dark；ReaderPage 是空章节；ReaderProgressBar/PageThumbStrip 空白；ChapterList 裁切；icon-button checked 与 default 同字节；Slider thumb 系统蓝；decor 粒子不可见；冻结清单的大量状态/组件仍缺。 |
| AC-4（证据/回归/禁止范围/生成器/check/pins/旧 SHA） | **PARTIAL** | build、1274/0/57、TokenGen/ThemeGen、check.ps1、verify_pins、旧四 PNG SHA、禁止范围均 PASS；但 inventory head 不是产出字节的 commit、frame 仍硬写 `mid`、表行损坏（R2R2-008）；日志仍是 1272/27 PNG 的旧值（R2R2-009）；Handoff 计数与主题声明不实（R2R2-013）；Task `delivery_head` 仍停在 `7e21b4de8`（R2R2-015）。 |
| OUT/BLOCKED/D-14 | 未写达成 | 未见把 OUT 项或 BLOCKED 数据端口写成达成；Task 保持 `in_progress`。D-14 已由 `5944f965` 收录 ADJ（A：catalog→Secondary）并释放后续卡 `D-14-STATUS-COLOR-FIX`（ready），Task `:110` 已改为"已裁决、本卡不写达成"；卡内测试仍对 NotStarted 特判，D-14 实现不在本卡（R2R2-018）。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 对应 AC | 建议 | 状态 |
|---|---|---|---|---|---|---|---|
| R2R2-001 | **P1** | `FluentResidual2VisualEvidenceTests.cs:39-56`、`:163-177`；`FluentShellSurface.axaml.cs:150`、`:650-654`；`SettingsViewModel.cs:345-360`；4 张 `pages--*--light.png` | 只保存 `AppearanceCoordinator` 的 Mode，不创建/传入 `DesignSystemThemeManager`，捕获前也不断言令牌颜色变化；4 张 light 页面实际全是 dark。当前目录只有 4 对 pages（8 张），组件已无 dark 对；因此 brief 的"16 对"与文件集不符，所谓"配对 SHA 全不同"也不能推出主题切换。`settings` 的 light/dark 只差 216 像素（0.023%），差异是 `appearance.mode` 文本；shelf/workbench 的较大差异是页面淡入/重绘，不是主题。因此 "16 对 SHA 全不同" 不能推出"主题已切换"，inventory/Handoff/checkpoint 的"真实 light/dark"声明不实。 | 逐图：`pages--settings--light` 显示 `appearance.mode=light` 但整页 dark；`pages--shelf--light`、`pages--workbench--light`、`pages--reader--light` 同样为 dark；像素 diff 216（settings）、35425（shelf）、88389（workbench）、15575（reader），仅 settings 的差异可用文本解释；测试 `:52-56` 未传 themeManager。 | AC-3、AC-2（主题元数据） | 用 `DesignSystemThemeManager.Initialize(light/dark)` + `CreateRoot(..., themeManager: manager)`；捕获前断言一个令牌（如 `Nm.Color.Bg.Canvas`）两主题不同；重生成/重命名/重签。组件若不做双主题，必须由 DSH 明确改为"固定 light/dark 之一"并写进证据，不能用 `current` 冒充。 | open |
| R2R2-002 | **P1** | `FluentDecorativeMotion.cs:207`；`ReaderPageView.cs:68`、`:173-176`；`FluentUi.cs:230`；`FluentResidual2DecorativeTests.cs:392-414`；`decor--page-turn-particles--*.png`、`decor--shelf-gradient--*.png` | 粒子层 `Insert(0)` 放在 `DsReaderPage` 之下，而 page surface 的背景是不透明 `Bg.Sunken`；mid 帧没有任何粒子，mid/none 的差异是页面淡入。shelf 渐变帧的背景均值只差约 1 个色阶，只有 1.7% 像素差 >8（且集中在卡片/阴影），肉眼无法分辨；五张 decor 还都被标成 light，实际是 dark。IN-1.2 的"full 中帧"视觉证据因此不成立；"粒子在页面图之下"的产品设计也值得 DSH 复核是否本来就不可见。 | 页面区域 mid 红均值 102/8/9 vs none 123/6/7；金色像素 1609 vs 1535（无粒子增量）；背景 patch 均值 13.0/12.1/12.5；decor footer 为 `builtin.current-v2`；测试只断言层存在/某个 dot opacity>0，不检查可见性。 | AC-1、AC-3 | 将粒子放到 page surface 之上但 `IsHitTestVisible=false`（或放在真正可见的边缘/前景层），并加像素级"粒子可见"断言与对比度断言；shelf 证据改裁切/增强到能辨别的区域，或改设计令牌使效果可见；theme 与 frontend 标注改成真实值。 | open |
| R2R2-003 | **P1** | `Controls.Custom.axaml:81-90`；`FluentResidual2StateEffectiveTests.cs:220-243`；`components--slider--default--full--current.png`、`components--slider--disabled--full--current.png` | 新增 `Slider /template/ Thumb` Background 规则后，默认 thumb 仍是 FluentTheme 系统蓝；默认 PNG 的 SHA `CA7A59C4…` 与 R2 前完全相同（737 B），说明规则未生效或该文件未随规则重生成。测试仍只断言 `Foreground` 与 disabled `Opacity`，没有任何 thumb/track 断言，无法发现该视觉缺陷。 | 打开 slider 两张 PNG（蓝 thumb、金线）；`Get-FileHash` 默认 `CA7A59C4…`；`git log -1 -- components--slider--default--full--current.png` 停在 `21e305249`（9f5723cb0 只改了 disabled 文件）；测试 `:231-240`。 | AC-2、AC-3 | 用 Avalonia 11.3.22 实际 Slider 模板确认可写属性（`Thumb` 的 Background 是否被模板消费），必要时改 `Themes/Controls/Slider.axaml` 或设置 `SliderThumb` 资源；补 thumb/track 解析后属性断言（或像素断言）；重生成并重签；若超出本卡范围，由 DSH 重冻结为 OUT。 | open |
| R2R2-004 | **P1** | `FluentResidual2VisualEvidenceTests.cs:138-139`；`Controls.Fluent.axaml:100`、`:378`；两张 `components--icon-button--*.png` | 视觉测试的 icon-button 用例是普通 `Button`，没有 `fluent-icon` class；规则是 `Button.fluent-icon.checked`，所以 checked 不会命中。default 与 checked 均为 714 B、同一 SHA `5684D773…`，checked 像素格没有任何状态差异；默认格也不是 IconButton 样式。 | `Get-FileHash` 两文件相同；测试 `:138` 无 `Classes={"fluent-icon"}`（r1 版本曾有，见 `git show 854e5bb1b:...`）；状态测试 `:91-108` 用 `fluent-icon` 并通过，说明属性通道存在，坏的是像素用例。 | AC-3 | 视觉用例补 `fluent-icon` + `NmIcon`（非文本占位），checked 用 `Classes={"fluent-icon","checked"}`；重生成后要求 default/checked SHA 不同；否则该格记 NOT_RUN，不得计入 R2-011 像素证据。 | open |
| R2R2-005 | **P1** | `FluentResidual2VisualEvidenceTests.cs:109-148`；`visual-inventory.md`；`pages--reader--*.png`；`components--reader-progress-*`、`components--page-thumb-strip-*`、`components--chapter-list-*` | IN-2B 清单仍远小于冻结范围：ReaderPage 仍用 `LoadAsync("book-0","chapter-0")`，画面是"本章节暂无页面"；ReaderProgressBar 没有 `Value`，295 B 空白；PageThumbStrip 没有 items，433 B 空白；ChapterList 只有单个 TextBlock，文字顶部被裁切；components 只覆盖 21 个格，缺 TopBand/NavRail/StatusBand、StreamingThumb、ErrorState/Skeleton、Dialog/Drawer 开合、CommandPalette 空/结果，以及 IN-2A 的 hover/focus/selected/pressed 等大量状态。 | 逐图：reader 显示空章节；reader-progress SHA `635A270D…`（r1 同一空白帧）；page-thumb 433 B；chapter-list 顶部裁切；测试 `:116`、`:144-146`；Task `:61-63`、`:112-123`。 | AC-3 | 用 `TwoPageHost`（decor 测试已有）生成真实 ReaderPage；ReaderProgressBar 设 `Value`/`Maximum`；PageThumbStrip 加真实 page item；ChapterList 用真实章节项并修正裁切；按冻结清单补齐，或由 DSH 重冻结缩减范围（实现者不得自行缩）；再逐图签署。 | open |
| R2R2-006 | **P1** | `verification/FEA-06-RESIDUAL-2/expected-tokens.md:3`、`:19`、`:25`、`:31-32`；Task `:59`、`:107` | 文件存在，但多个组仍是"以样式令牌解析值为准"（IconButton/SettingsField/EmptyState 等），没有 file:line 锚点，没有 D-11 的四态↔StatusKind 映射，D-11 证据仍只在 Task 文字里；第 3 行"当前 light/dark 由 AppearanceCoordinator 主题决定"与实测相反。Reviewer 无法独立核对"期望值非实现者自造"，AC-2 的逐格锚点条件未满足。 | 读 `expected-tokens.md` 全文；`Select-String` 无 `D-11`/`EFFECTIVE`/`matrix`/`*.axaml:` 锚点；同一文件的 settings 证据已证明 AppearanceCoordinator 不驱动主题。 | AC-2 | 每组/状态写"期望令牌键值 + 锚点（样式文件:行、`StatusCatalog` 成员、`component-state-matrix.md` 的 EFFECTIVE 行）"；加入 D-11 九值映射与 D-14 例外；修正主题前提；Handoff 链接该文件。 | open |
| R2R2-007 | P2 | `Controls.Fluent.axaml`（9 个派生选择器）；`FluentComponentStateCoverageTests.cs:17-34`；`FluentResidual2StateEffectiveTests.cs:284-309`、`:340-373` | R2-005 的**产品修复**已完成（9 个类选择器均 class-only + `x:SetterTargetType`），但覆盖测试的 `RequiredSelectors` 仍没有 ChapterList/StreamingThumb/BatchMatrix/RunProjectionBar/ReaderPage/ReaderProgressBar/SettingsGroup/SettingsField/TabStrip 这些类；SettingsField/TabStrip 也没有期望属性（ColumnSpacing/RowSpacing/Spacing）断言。r1 要求的"有效属性断言 + coverage 同步"没有做。 | 读 coverage 测试 15 个 selector 列表；`Select-String` 这些类在测试中 0 命中；SettingsField 测试只断言子 TextBox 的 failed border/opacity。 | AC-2（部分组） | 在 coverage 测试加入这些类；为 SettingsField/TabStrip/StreamingThumb/ReaderProgressBar/ReaderPage/SettingsGroup 增加解析后属性断言；或在 expected-tokens 明确记 NOT_RUN，不计入 PASS。 | open |
| R2R2-008 | P2 | `visual-inventory.md:1-35`；`FluentResidual2VisualEvidenceTests.cs:80-100`、`:97`；提交 `6b705b6a2`、`11224d56` | head 列填的是两个 docs commit：`6b705b6a2` 不含当前 pages 字节（`git diff --quiet` EXIT=1），`11224d56` 中 decor PNG 数为 0（decor 首次出现在 `dc1543005`）。所有静态行仍硬写 `frame=mid`；decor 行 command 写"同上"；第 31 行把 settings dark 与 decor first 两行拼在一行（28 个 `|`），Markdown 表损坏；theme 列对组件写 `current`。R2-008 的 head/frame/场景元数据要求未满足。 | 读 inventory 35 行；`git diff --quiet 6b705b6a2..HEAD -- pages--shelf--dark` EXIT=1；`git ls-tree 11224d56` decor 0；`git log -1` 显示 decor 首次 `dc1543005`；第 31 行 pipes=28。 | AC-3、AC-4 | 在产出字节的 commit 上重新生成 inventory：head=该 commit；每行真实 frame（静态格写 static/n-a）；decor 行写完整命令；修复合并行；theme 列写成实际值（light/dark 或 FIXED light），不要 `current` 语义不明。 | open |
| R2R2-009 | P2 | `impl-in1-verification.log:16-22`；`impl-in2a-verification.log:14-20`；`impl-in2b-verification.log:9-16` | 三份日志的 R2-009 补记都停在 head `5a2692c05`、**1272 / 27 PNG**；最终是 `dc1543005`/`5944f965`、**1274 / 34 PNG**；新增的 decor 与 IconButton 测试、R2-001 收尾都没有进日志。57 skip 仍只有"Host 28 + CoreClient 22 + App 7"的计数，没有逐条原因或指向既有归因文件；IN-1 日志还写"HasMotion 不再计入 decorative"，与 `MotionTimings.cs:88-96` 的注释/表达式矛盾。 | 逐行读三份 log；`head: 5a2692c05`；"1272 passed"；"27 PNG"；`MotionTimings.cs:88-96` 只含 navigation/feedback。 | AC-4 | 追加一份最终日志（head、shell/host、命令、逐程序集、EXIT、差值、57 skip 原因或指向既有归因文件），保留旧日志字节；或引用 DSH 集成日志并写清对应 head。 | open |
| R2R2-010 | P2 | `FluentDecorativeMotion.cs:272-277`；`Controls.Fluent.axaml:100`、`:378`；commit `7e21b4de8` | r1 的 R2-011 是 `ResourcesChanged` 静态订阅泄漏（lambda 从不解除），本轮代码未改，泄漏仍在；而 `7e21b4de8` 把 SurfaceCard/IconButton 状态通道标成"R2-011"，实际对应 r1 的 R2-007。findings 编号被偏移，后续处置容易把"泄漏"误记为"已修"。另外 `Button.fluent-icon.checked` 规则在 `:100` 与 `:378` 重复。 | 读 `:272-277` 无 unsubscribe；读 `:100`/`:378` 两条同规则；checkpoint §140 与 r1 findings 对照。 | AC-1（无泄漏）/治理 | detach 时解除 `ResourcesChanged`（或弱订阅）；删除重复规则；在 Handoff/checkpoint 明确 R2-011（泄漏）与 R2-007（状态通道）的映射，不要用同一编号承担两件事。 | open |
| R2R2-011 | P2 | `FluentDecorativeMotion.cs:11`、`:136-137`、`:156-158`；`FluentResidual2DecorativeTests.cs:144-172`、`:266-299`；`FluentUi.cs:252-257` | R2-012 未处置：代码只有 Activated/Deactivated，没有 `IsVisible`/窗口隐藏钩子，与 `:11` 注释不符；`ShelfGradient_WindowDeactivated` 直接调 `shelf.DecorativeLoop.Pause()`，并未触发 `Deactivated`；粒子没有生产 `FluentRenderClock` 首/中/尾采样，也没有可读性/对比度断言；粒子仍每帧写 `Canvas.SetLeft/Top`，`total` 用常量而非传入 progress。checkpoint §143 却写"R2-012 已完成"，与代码不符。 | 读测试 `:158`；`Select-String IsVisible` 在装饰文件 0 命中；`git diff 854e5bb1b..HEAD -- src` 只有两个 Styles 文件。 | AC-1 | 挂 `IsVisibleChanged`/窗口隐藏；用 headless 事件或 `Deactivated` 触发做真实接线测试；给粒子加生产时钟采样与对比度断言；把 Canvas 定位改为一次性 + RenderTransform；或由 DSH 明确登记为本卡外。 | open |
| R2R2-012 | P2 | `FluentResidual2StateEffectiveTests.cs:312-338`、`:19-23` | SearchField focus 仍只断言内边框保持 idle 并等于 `Line.Default`，没有断言 `:focus` 焦点环/外部 adorner；测试头注释仍称 SurfaceCard hover/selected/disabled 与 IconButton checked "no style channel"，与实现和测试体相反；测试名 `SurfaceCard_HoverSelectedDisabled_KeepTheFrozenContainerTokens` 也不再描述行为。 | 读 `:312-338`；读 `:19-23`；读 SurfaceCard 测试体 `:69-86`。 | AC-2 | 补焦点环断言（或明确 NOT_RUN）；更新注释/测试名；把状态通道的期望写入 expected-tokens。 | open |
| R2R2-013 | P2 | `doc/handoffs/FEA-06-RESIDUAL-2-impl.md:15`、`:20`；Task `:17` | Handoff 已存在（R2-017 的形式满足），但内容不准：写"components 19"，实际 21；写"pages 8（真实 light/dark）"，实测 4 张 light 均 dark；Task `delivery_head` 仍停 `7e21b4de8`/29 PNG，与 `dc1543005`/34 PNG 不符。Reviewer 不能把它当作可靠的交接证据。 | 实际文件数 34（pages 8 + components 21 + decor 5）；`git ls-files`/`Test-Path` 对 Handoff 为真；Task `:17` 原文。 | AC-4 | 修正计数与主题声明；把 Handoff 的"限制"写在最前；DSH 在最终状态更新 `delivery_head`（不得由 Reviewer 改 Task）。 | open |
| R2R2-014 | P2 | `FluentResidual2VisualEvidenceTests.cs:80-84`、`:41-50` | `Assert.DoesNotContain(Path.Combine("verification","FEA-06","screens"), output)` 中 `output` 固定为 `.../FEA-06-RESIDUAL-2/visuals`，断言恒真，不能证明"禁止写 FEA-06"；测试也没有在捕获前后检查 `git status`/`verification/FEA-06/**`。appearance store 已改为 temp 路径（好），但 R2-018 的写域证明仍未闭环。 | 读 `:80-84`；`output` 固定；R2-018 原文；本轮默认运行后 `git status` 无 `verification/**` 变更（我实跑确认），但这是运行结果而非测试断言。 | AC-3、AC-4 | 断言 output 精确等于预期路径，并在捕获前后用 `git status --porcelain -- verification/FEA-06` 断言为空；或删除这条恒真断言，改为真实写域检查。 | open |
| R2R2-015 | P2 | `doc/STATUS.md:10`；`doc/REBASELINE_PLAN.md:39`；Task `:17` | scope-r3 R3R-001 的三处活文本仍未刷新：STATUS `:10` 仍"下一步：无 READY 节点"；PLAN `:39` 仍"下一节点 FEA-06-RESIDUAL-1（in_progress…Batch B 待派）"；Task `delivery_head` 停在上一轮。不是本实现 diff 引入，但 reviewed_head 仍处矛盾状态，影响冻结台账。 | 读三处原文；`git diff 854e5bb1b..HEAD -- doc/STATUS.md doc/REBASELINE_PLAN.md` 为空。 | 治理 | DSH 在终态判定前刷新三处，或登记推迟理由/Owner/时点；不改历史快照。 | open |
| R2R2-016 | P2 | `MotionTimings.cs:88-96`；`FluentUi.cs:9`、`:252-257`；`FluentAnimationCompletionTests.cs:30-35` | r1 的四条 P2（R2-010/013/014/015）未处置且本轮无产品改动：① `HasMotion` 注释写"any transition or decorative loop"，表达式只含 navigation/feedback；② 粒子每帧写 `Canvas.SetLeft/Top`（`:256-257`）；③ `total` 用常量 `MotionTimings.DecorativePageTurnMilliseconds`（`:252`）而非传入 progress；④ Controls 反向依赖 `App.ViewModels.Fluent`（`:9`）；⑤ 既有完成测试默认分类收窄为 `Navigation | Feedback`，未说明 decorative 边界。 | 读上述行；`git diff 854e5bb1b..HEAD -- src` 只有 Styles 两个文件。 | AC-1（诊断/分层） | 按 r1 建议逐条修：HasMotion 纳入或改注释；粒子只写 RenderTransform/Opacity；duration 显式传参；常量移到中性层；完成测试保留 All 或新增显式断言。 | open |
| R2R2-017 | P2 | `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` §142、§143；`decor--shelf-gradient--*.png` footer | checkpoint §142 写"R2-001 P0 闭环"、§143 写"R2-001/011/012/017 均已由 DSH 完成"，但 R2-001 的粒子帧不可见、R2-011 泄漏未修、R2-012 未接 IsVisible/Deactivated；decor 帧 footer 是 `builtin.current-v2`（`FluentShellSurface` 未传 selection，`:99` 默认），不是本卡冻结的 `builtin.fluent`，宿主也是空书架（0 部作品），inventory 没有 frontend 列。 | 读 checkpoint §142–143；打开 decor 帧 footer；读 `FluentShellSurface.axaml.cs:99`；读 decor 测试 `:377` 的 `Create()`。 | 治理/AC-3 | 修正 checkpoint 的完成声明；decor 捕获传 `FrontendSelector.Select("builtin.fluent", null)` 并使用与 pages 一致的 host fixture；inventory 增 frontend 列；"P0 闭环"改为"占位已删，视觉证据待补"。 | open |
| R2R2-018 | P2 | Task `:110`（现为 D-14 已裁决文字）；`FluentResidual2StateEffectiveTests.cs:475-477`、`:483-497`；`doc/reviews/ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md`（5944f965 收录）；`doc/tasks/D-14-STATUS-COLOR-FIX.md`（ready） | D-14 的治理登记已闭环：ADJ（A：catalog→Secondary）已入库，后续卡 `D-14-STATUS-COLOR-FIX` 已释放，Task `:110` 已改为"已裁决、本卡不写达成"。但 D-14 本身未实现（`StatusCatalog.ColorKey(NotStarted)` 仍 Disabled），本卡测试仍对 NotStarted 特判，expected-tokens 保留例外；在后续卡集成前，AC-2 的九值交叉断言仍不是统一规则。 | 读 Task `:110`；读测试特判；读 ADJ/后续卡 front matter；`git diff --quiet 195422c2f..HEAD -- doc/STATUS.md` 仍 0（STATUS 未刷新）。 | AC-2（治理） | 本卡保持现状即可；后续卡 `D-14-STATUS-COLOR-FIX` 实现并集成后再移除特判；不得在 D-14 未实现前写达成。 | open（实现待后续卡） |

## Verification（executed）

环境：Windows 11，PowerShell 7，`dotnet` SDK（net9.0），Avalonia 11.3.22；仓库 `G:\CODEX\New Manga`，branch `main`；`NEWMANGA_CAPTURE_RESIDUAL2_PNGS` 未设置（默认运行）；本轮所有命令后 `git status` 仅剩本 Review 未跟踪，无 `verification/**` 改写。未重跑 opt-in 捕获（保护已提交 PNG 字节）；未执行原生 DPI/a11y。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定 head/工作树 | `git rev-parse HEAD`；`git status --porcelain` | reviewed_head `5944f965`；实现/证据树 `dc1543005` | PASS（代码/证据树干净；仅本 Review 未跟踪） | head 与 `reviewed_head` 一致；`dc1543005..HEAD` 仅 docs/ADJ/D-14 后续卡 |
| 构建 | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | HEAD | PASS，`BUILD_EXIT=0` | 0 warnings / 0 errors |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo` | HEAD | PASS，`TEST_EXIT=0` | **1274 passed / 0 failed / 57 skipped**；逐程序集：Appearance 21、Presentation 38、Host 51/28、ThemeEngine 253、DesignSystem 112、ApplicationCore 31、CoreClient 128/22、App 640/7；总 1331；较基线 1245 +29，较 r1 1272 +2（新增 IconButton 状态测试 + decor 捕获测试） |
| 默认零仓库写入 | 全量/定向测试后 `git status --porcelain` | HEAD | PASS | 无 `verification/**` 变更；仅本 Review 未跟踪；未新增/改写 PNG |
| 定向测试 | `dotnet test ...\NewManga.DesignSystem.Tests.csproj --no-build ...`；`...NewManga.App.Tests.csproj --filter FullyQualifiedName~FluentResidual2` | HEAD | PASS | DesignSystem 112/112；App FluentResidual2 14/14 |
| TokenGen | `dotnet run --project ...\NewManga.DesignSystem.TokenGen -- --check` | HEAD | PASS，`TOKENGEN_EXIT=0` | 292 rows，byte-for-byte up to date |
| ThemeGen | `dotnet run --project ...\NewManga.ThemeEngine.ThemeGen -- --check` | HEAD | PASS，`THEMEGEN_EXIT=0` | byte-for-byte up to date |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | HEAD | PASS，`CHECK_EXIT=0` | 3 既有 warnings（9 非终态 Task、STATUS/PLAN 80% 预算）；不替代审查 |
| 冻结 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | HEAD | PASS，`PINS_EXIT=0` | 15/15 |
| 旧 FEA-06 四 PNG SHA | `Get-FileHash verification\FEA-06\screens\*.png -Algorithm SHA256` | HEAD | PASS | reader `8533C263…78B2`、settings `FD30B166…A162`、shelf `307F8F67…8B0A`、workbench `D5D878BB…E2DF5`，与 Task `:128` 全值一致；零 diff |
| 禁止路径 | `git diff --exit-code 669a4ae02..HEAD -- <path>`（见正文路径列表） | HEAD | PASS | 全部 EXIT=0；实现 commit 文件均落在 `allowed_paths` |
| 实现 diff 写域 | `git show --name-only d854d91b2 1d2df1d15 998d75bdb 21e305249 9f5723cb0 7e21b4de8 dc1543005` | 提交链 | PASS | 产品源码只改 Styles + 测试/doc/verification；无 Core/契约/生成物/冻结设计/组合根 |
| 视觉逐图检查 | 34 张 PNG 逐张看图；`Get-FileHash`/像素 diff | HEAD | **FAIL** | 34 files / 33 unique SHA；pages 1 PASS/7 REJECT、components 14/7、decor 0/5；15 PASS / 19 REJECT（附录 B） |
| 主题真实切换 | 像素 diff + 代码读 | HEAD | **FAIL** | settings light/dark 仅 216 像素差（mode 文本）；4 张 light 全 dark；测试未传 themeManager |
| IN-1.2 粒子可见性 | 像素 diff + `FluentDecorativeMotion.cs:207` | HEAD | **FAIL** | mid 无粒子；mid/none 差异为页面淡入（红均值 102 vs 123） |
| IN-2B 清单完整性 | Task `:61-63`、`:112-123` 对照 inventory | HEAD | **FAIL** | ReaderPage 空章节、progress/thumb 空白、大量状态/组件缺 |
| inventory 元数据 | 读 35 行；`git diff`/`git ls-tree` 验证 head | HEAD | **FAIL** | head 为 docs commit；decor 行合并；frame=mid；command"同上" |
| 证据日志格式 | 读三份 log | HEAD | **FAIL（P2）** | 1272/27 PNG、head 5a2692c05；最终 1274/34；57 skip 无逐条原因 |
| expected-tokens 锚点 | 读全文 + `Select-String` | HEAD | **FAIL（P1）** | 无 file:line/D-11/EFFECTIVE；多处"以样式为准"；主题前提不实 |
| Handoff | 读 `doc/handoffs/FEA-06-RESIDUAL-2-impl.md` | HEAD | PARTIAL | 文件存在；components 19≠21、light/dark 声明不实、Task delivery_head 旧 |
| 57 skip 归因 | 逐程序集 summary 的 skip 计数 + 全量日志 `[SKIP]` 名称 | HEAD | PASS（计数）/ 部分 | 57 条，均为既有 sidecar fixture 自跳过（未设 `NEWMANGA_CORECLIENT_SIDECAR_DIR`，与 r1 同一归因）；与基线同数；本轮未逐条重开原因文件 |
| opt-in 像素再生成 | 未执行 | HEAD | NOT_RUN | 为避免改写已提交证据字节；写域由代码审阅判定（R2R2-014） |
| 原生 DPI/a11y/桌面 | — | B-5/D-1 | NOT_RUN/BLOCKED | 无硬件；不伪造 |
| D-14 / OUT / BLOCKED | 读 Task/logs/代码/ADJ | HEAD | 未写达成 | Task 保持 in_progress；D-14 已入库 ADJ+后续卡，但实现未做；无 OUT/BLOCKED 被写成 MET |

**证据纪律说明**：上表命令均在本轮实际执行；build/test/generators/governance 之后 `git status` 仍无本卡证据改写。未把 opt-in、原生视觉或 NOT_RUN 计 PASS。全量 1274/0/57 只说明现有断言通过，不等同 AC-1…AC-4 达成。

## 附录 A：关键 SHA 与统计（复现用）

```text
HEAD / reviewed_head = 5944f96527b0adee6964a8b1266ddfa00de4e0d6
implementation_head  = dc1543005a048157423969cd4ee73522d84f8ec6
base_commit          = 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431

PNG: 34 files / 33 unique SHA-256（唯一重复：icon-button default == checked）
pages 8 (4 对) / components 21 / decor 5

settings light vs dark: changed>8 = 216 px (0.023%)  ← 仅 appearance.mode 文本
shelf light vs dark:     changed>8 = 35425 px (3.85%) ← 淡入/重绘，非主题
workbench light vs dark: changed>8 = 88389 px (9.60%)
reader light vs dark:    changed>8 = 15575 px (1.69%)

slider default SHA = CA7A59C449290351C091E0D70C372A94A910BFD10D9866D8AAF3BD7E3482A232
  == R2 返修前同一文件（9f5723cb0 只改 disabled；thumb 仍系统蓝）
icon default SHA  = 5684D773D1AD16C51392C664D67255919834A496752F493DBEE59A69248E0C97
icon checked SHA  = 5684D773D1AD16C51392C664D67255919834A496752F493DBEE59A69248E0C97

decor shelf background patch mean: first 13.0/14.3/16.6; mid 12.1/13.0/15.0; static 12.5/13.5/15.5
decor particles page patch mean: mid 102/8/9; none 123/6/7（页面淡入，不是粒子）
gold pixels mid/none = 1609/1535（差值仅工具栏范围，无粒子增量）
full: 1274 passed / 0 failed / 57 skipped（Appearance 21、Presentation 38、Host 51/28、ThemeEngine 253、DesignSystem 112、ApplicationCore 31、CoreClient 128/22、App 640/7）
```

## 附录 B：34 张 PNG 逐图签署表

签署口径：PASS = 该文件能作为其 inventory 声称格位（组件/状态/mode/theme/帧位）的视觉证据；REJECT = 主题不实、内容无关/空帧、状态无差异、效果不可见或明显样式缺失。REJECT 项不得用于 AC 判定。本表不修改 `visual-inventory.md` 原字节；`signed_by` 由 DSH/授权证据维护者回填。未签署项本应为 NOT_RUN；本表覆盖全部 34 项。

| # | file | 结论 | 一句理由 |
|---|---|---|---|
| 1 | `pages--shelf--default--full--light.png` | REJECT | theme=light 不实：实际为 dark；settings 同批证明 AppearanceCoordinator 未应用主题。 |
| 2 | `pages--shelf--default--full--dark.png` | REJECT | 虽为 dark，但内容整体处于淡入/半透明态，工具条文字不可读，非稳定页面帧。 |
| 3 | `pages--workbench--default--full--light.png` | REJECT | theme=light 不实，实际 dark。 |
| 4 | `pages--workbench--default--full--dark.png` | REJECT | 内容暗淡，运行/检查器文字对比度不足，非稳定 dark 帧。 |
| 5 | `pages--reader--default--full--light.png` | REJECT | 实际 dark，且为"本章节暂无页面"空态，不是 ReaderPage。 |
| 6 | `pages--reader--default--full--dark.png` | REJECT | 空章节空态，不是 ReaderPage；主题也不足为证。 |
| 7 | `pages--settings--default--full--light.png` | REJECT | 实际 dark；`appearance.mode=light` 只是文本，不是主题。 |
| 8 | `pages--settings--default--full--dark.png` | PASS | 暗色设置页真实渲染（导航/字段/分组可见）；浮层"外观"/重置按钮叠放痕迹另行记录。 |
| 9 | `components--surface-card--default--full--current.png` | PASS | SurfaceCard 默认表面/圆角真实渲染。 |
| 10 | `components--surface-card--disabled--full--current.png` | PASS | disabled Opacity 与 default 可区分。 |
| 11 | `components--surface-card--selected--full--current.png` | PASS | selected 的 Accent 边框 + Elevation.2 可见。 |
| 12 | `components--book-card--default--full--current.png` | PASS | BookCard 表面/文本真实渲染。 |
| 13 | `components--book-card--disabled--full--current.png` | PASS | disabled 与 default 可区分。 |
| 14 | `components--book-row--default--full--current.png` | PASS | BookRow 表面/边框/文本真实渲染。 |
| 15 | `components--book-row--disabled--full--current.png` | PASS | disabled 与 default 可区分。 |
| 16 | `components--primary-button--default--full--current.png` | PASS | 主按钮 accent 背景/前景/圆角可见。 |
| 17 | `components--primary-button--disabled--full--current.png` | PASS | disabled 背景/前景/Opacity 可区分。 |
| 18 | `components--secondary-button--default--full--current.png` | PASS | 次按钮描边/文本可见。 |
| 19 | `components--danger-button--default--full--current.png` | PASS | Danger 红描边/文字可见。 |
| 20 | `components--icon-button--default--full--current.png` | REJECT | 用例未加 `fluent-icon` class，只是普通 Button 文本，不是 IconButton。 |
| 21 | `components--icon-button--checked--full--current.png` | REJECT | 与 default 同 SHA（714 B）；checked 规则因缺 `fluent-icon` 未命中，状态无差异。 |
| 22 | `components--toggle-switch--disabled--full--current.png` | PASS | 轨道/滑钮/Off 可见（disabled 对比度低属预期，但可辨）。 |
| 23 | `components--slider--default--full--current.png` | REJECT | thumb 仍是 FluentTheme 系统蓝，未令牌化；与 R2 前同 SHA。 |
| 24 | `components--slider--disabled--full--current.png` | REJECT | thumb/track 未证明走 Accent/Text.Disabled；仅整体 Opacity，不足以作为令牌状态证据。 |
| 25 | `components--region-box--default--full--current.png` | PASS | RegionBox 的 Accent 表面/边框/文本可见。 |
| 26 | `components--reader-progress--default--full--current.png` | REJECT | 295 B 空白帧；ProgressBar 无 Value/进度，未渲染。 |
| 27 | `components--chapter-list--default--full--current.png` | REJECT | 仅一个 TextBlock，文字顶部被裁切，无列表结构/间距可审。 |
| 28 | `components--page-thumb-strip--default--full--current.png` | REJECT | 433 B 空白帧，无缩略图/条目。 |
| 29 | `components--empty-state--default--full--current.png` | PASS | 文本空态"暂无内容"渲染；插画属 OUT，不计缺口。 |
| 30 | `decor--shelf-gradient--first--full--light.png` | REJECT | theme=light 不实（footer `builtin.current-v2`，实际 dark）；渐变仅约 1 RGB 阶、肉眼不可辨，不能作为 8s 渐变证据。 |
| 31 | `decor--shelf-gradient--mid--full--light.png` | REJECT | 同上；与 first/static 的可见差异不足；theme/frontend 标注不实。 |
| 32 | `decor--shelf-gradient--static--reduce--light.png` | REJECT | 同上；静帧不能证明 reduce，且 theme 标错。 |
| 33 | `decor--page-turn-particles--mid--full--light.png` | REJECT | 画面无粒子（层在不可见页面下）；mid/none 差异是页面淡入；theme 标错。 |
| 34 | `decor--page-turn-particles--none--reduce--light.png` | REJECT | 同上；无粒子可证明"reduce 不创建层"，theme 标错。 |

**签署统计：15 PASS / 19 REJECT。** 关键失败面：全部 4 张 light 页面（主题不实）、shelf/workbench dark（淡入/低对比）、ReaderPage 2 张（空章节）、ReaderProgressBar（空白）、PageThumbStrip（空白）、ChapterList（裁切）、IconButton 2 张（缺 class/同字节）、Slider 2 张（系统蓝 thumb）、decor 5 张（theme 不实；粒子不可见；渐变不可辨）。因此 AC-1 的像素/签署条件与 AC-3 均不能成立。

## 结论与复审

**verdict = changes_requested。** 本 head 的机械门禁、禁止范围、回归与 IN-1/IN-2A 的核心行为是干净的；P0 占位假证据已删除，decor 帧确实来自产品层，SurfaceCard/IconButton 的状态通道与 9 个派生选择器也确有进展。但本卡的验收对象是 Fluent 视觉残项，当前提交仍把"dark 页面"命名为 light、把"不可见粒子"当作 IN-1.2 的 full mid 证据、把"系统蓝 thumb"留在 Slider、把"无差异 checked"当作 IconButton checked，并且 IN-2B 清单与 inventory/日志/Handoff 的元数据不能支撑独立复核。不能批准进入集成，也不能把 AC-1/AC-3 写成 MET。

**必须在本 Review 后处置（再复审门槛）**：

1. R2R2-001（P1）：用 `DesignSystemThemeManager` 真正应用 light/dark，捕获前断言令牌颜色随主题变化；重生成 4 对页面并重签。组件若要保留单主题，必须由 DSH 明确固定为 light 或 dark，不能用 `current`。
2. R2R2-002（P1）：让粒子层在产品中真实可见（前景/边缘，非不透明页面下），补像素/对比度断言；shelf 渐变证据改到可辨别的裁切或设计允许的对比度；修正 theme/frontend 标注。
3. R2R2-003（P1）：修到 Slider thumb 真正走令牌（或由 DSH 转 OUT），补 thumb/track 断言；重生成。
4. R2R2-004（P1）：icon-button 视觉用例补 `fluent-icon` + NmIcon，checked 与 default 必须不同 SHA；否则记 NOT_RUN。
5. R2R2-005（P1）：按冻结清单补 IN-2B（或由 DSH 重冻结缩减），ReaderPage 用真实双页 fixture、ProgressBar 设 Value、PageThumbStrip 有 items、ChapterList 不裁切。
6. R2R2-006/R2R2-007（P1/P2）：expected-tokens 补 file:line 锚点、D-11 映射；coverage/有效属性断言补齐。
7. R2R2-008/R2R2-009/R2R2-013/R2R2-014/R2R2-015（P2）：inventory head/frame/表行、最终日志（1274/34）、Handoff 计数、R2-018 写域断言、PLAN/STATUS/Task 指针。
8. R2R2-010/R2R2-011/R2R2-012/R2R2-016/R2R2-017/R2R2-018（P2）：解除 ResourcesChanged 泄漏、IsVisible/Deactivated 真实接线、搜索焦点环、HasMotion/Canvas/常量/分层、checkpoint 过度声明、D-14 处置。D-14 已由 `5944f965` 收录 ADJ 并释放后续卡；本卡不写达成，后续卡实现后再移除特判。

复审要求：新 head 必须重新 Appointment 独立上下文 Reviewer；R2R2-001…018 逐条核对；34 张图中所有 REJECT（尤其 4 张 light、Slider、IconButton、ReaderPage、ReaderProgressBar、PageThumbStrip、ChapterList、5 张 decor）必须重生成并重签；不得以 1274/0/57 或"图存在"替代视觉签署；不得写 D-14/OUT/BLOCKED 达成；不得 push。Task 保持 `in_progress`。

**推荐下一步**：Task=`FEA-06-RESIDUAL-2`，Agent=DSH（findings 处置/范围裁决/证据维护）；若继续返修，可由 DSH 在独立上下文派发实现（不得与本 Review 同一会话自审）。Recovery point=`G:\CODEX\New Manga`、main、同一 worktree，base=`669a4ae02`，reviewed_head=`5944f965`，implementation_head=`dc1543005`。本 Reviewer 未参与实现或返修，唯一仓库交付为本文件；未修改生产源码/Task/证据/冻结设计，未 commit/push。

可直接转发给 DSH：

> 在 `G:\CODEX\New Manga` 接收 `doc/reviews/FEA-06-RESIDUAL-2-impl-r2.md`：**changes_requested，P0=0 / P1=6 / P2=12**。门禁全 PASS（build 0/0、1274/0/57、TokenGen/ThemeGen、check/pins、旧四 SHA、禁止范围零 diff），但视觉证据仍不成立：4 张 light 页面实为 dark（settings 对仅差 216 像素，差异是 mode 文本），ReaderPage 仍空章节，ReaderProgressBar/PageThumbStrip 空白，IconButton checked 与 default 同 SHA（缺 `fluent-icon`），Slider thumb 仍系统蓝，decor 粒子被不透明页面遮住不可见，34 图签署 15 PASS/19 REJECT。按 R2R2-001…018 处置；D-14 已由 `5944f965` 收录 ADJ 并释放后续卡，本卡不写达成；Task 保持 `in_progress`；不得 push。返修后重新 Appointment 独立 Reviewer，逐图重签。
