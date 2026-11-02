---
task_id: FEA-06-RESIDUAL-2
reviewer: DSH 独立子 agent（impl-r4 Reviewer；独立上下文，未参与实现）
reviewer_kind: subagent
author: DSH 与此前实现会话；本轮 R2R3 为 fresh Codex CLI 实施会话
base_commit: 669a4ae02bf8bf9d7dbdda01c4b2b9de71cb1431
reviewed_head: bb71e43db0063a99abe84973763656d97ae8186a
implementation_head: 17a26d552e27a57bafebe0bc77d008094d1a6775
evidence_head: c70d5c348172920847da6e1ab0d08ed9f219a80e
delivery_commit: 832103393（其后 69db595b9 / bb71e43db0063a99abe84973763656d97ae8186a 仅文档）
prior_review: doc/reviews/FEA-06-RESIDUAL-2-impl-r3.md
decision: approved
verdict: approved
p0: 0
p1: 0
p2: 3
provenance:
  agent: DSH independent subagent（workflow job workflow-1cbe60f57400429d）
  appointment: 用户本轮 impl-r4 独立复核指令；DSH checkpoint §149 按 D-9 派发（作者可派独立上下文子 agent 审查）
  implementation_participation: none
  mode: read_only_except_this_report
  date: 2026-11-03
  environment: Windows 10.0.26300 / PowerShell 7.6.8 / dotnet SDK 10.0.401 / net9.0 / Avalonia 11.3.22
  workspace: G:/CODEX/New Manga / main / common-directory .git
  head_moved_during_review: 69db595b9 -> bb71e43db0063a99abe84973763656d97ae8186a（相对起点仅追加 checkpoint §149；Task.delivery_head 已在起点 69db595b9 更新；apps/ 与 verification/ 字节无变化）
---

# Review：FEA-06-RESIDUAL-2 impl-r4

**approved：P0=0 / P1=0 / P2=3。R2R3-001…006 全部核实为 FIXED；172 图逐图签署 172 PASS / 0 REJECT / 0 NOT_RUN（仅指已交付文件）。B-5/D-1 原生 200% DPI、a11y、BLOCKED 格与 D-14 保持 NOT_RUN，不写达成。**

上一轮的 6 张 REJECT（danger pressed ×2、light 渐变 first/mid、误标 shell compact ×2）已被真实修复或按正确断点重命名；本轮独立复现了 r3 附录 C 的两个失败序列，均转为通过。NavRail 折叠/恢复、StatusBand 运行/错误、1024/1280/1600 宽度标签都由真实产品状态驱动，并由我独立像素复核。**172 PNG 与固定 head 副本重捕获逐字节一致（172/172），136/24/12/4 的旧→新分布与声明完全相符；light 渐变独立量测为纯背景横带 25114 像素 RGB 差>8（max14/15），差分呈平滑渐变而非 AA/容差抖动，肉眼可辨。** 机械门禁全通过（build 0/0、无过滤 1289/0/57、TokenGen/ThemeGen、check、pins、旧四 SHA、禁止范围、默认零写入、opt-in 仅本卡 visuals）。

仍不写整卡完成：3 个 P2 都在 DSH 自己的写域（STATUS/PLAN 数字滞后、Task reviewer 字段滞后、渐变工厂的旧初始令牌/注释），不影响实现与证据的批准；DSH 集成时应一并更新，并按 B-5/D-1 残余决定 Task 生命周期。本卡不得据此写 D-14、OUT、BLOCKED、原生 DPI 或 a11y 达成。

## 范围与依据

开始时 HEAD=69db595b9，工作树干净；审查中 DSH 提交 bb71e43db0063a99abe84973763656d97ae8186a（仅 checkpoint §149），按用户允许的“其后仅文档提交”固定 `reviewed_head=bb71e43db0063a99abe84973763656d97ae8186a`。`git diff 17a26d552 bb71e43db0063a99abe84973763656d97ae8186a -- apps/` 为空；`git diff --name-only 832103393 bb71e43db0063a99abe84973763656d97ae8186a` 仅 `doc/tasks/FEA-06-RESIDUAL-2.md` 与 `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md`。实现=17a26d552，证据=c70d5c348（172 PNG＋inventory＋日志＋处置＋audit），交付=832103393。

已读：r3 报告（450 行，含附录 A/C）、`r2r3-findings-disposition.md`、`impl-r3-rework-verification.log`、`r2r3-evidence-audit.md`、Handoff `FEA-06-RESIDUAL-2-r2r3-17a26d552.md`、Task、STATUS、REBASELINE_PLAN、checkpoint §146–§149、ADJ-2026-11-03-D14 与 D-14 卡；对照真实源码、测试、冻结设计 `fluent-v1/04-layout-responsive.md`、`10-component-inventory.md`、`02-motion.md`、`09-state-matrix.md`。

审查 diff：`git diff 9c6a2b474 17a26d552`（9 个文件：FluentShellSurface.axaml/.cs、FluentDecorativeMotion.cs、ReaderPageView.cs、ShelfPageView.cs、Controls.Fluent.axaml、两个 App.Tests 测试、r2r3-checkpoint）；证据提交 `c70d5c348`、交付 `832103393`、文档 `69db595b9/bb71e43db0063a99abe84973763656d97ae8186a`。禁止范围按 Task base 669a4ae02 比较。

Reviewer 未参与实现或返修；唯一仓库写入为本报告。临时构建/TRX/contact sheets/独立 probe/固定 head 捕获副本均在 `G:/CODEX/New Manga.workspace/agent-output/dsh/FEA-06-RESIDUAL-2/impl-r4-review/`，不作为唯一证据：关键计数、逐图 SHA、拒绝/缺失处置、失败与复现输出均内联。

**未审到**：原生 200% DPI、原生窗口 chrome、真实桌面触控、完整 Tab 遍历与原生 a11y（B-5/D-1，未运行）；双页/滚动、RegionBox 冲突、Console/Run 投影等 BLOCKED 格；旧 FEA-06 代码语义（只核四 PNG SHA）。headless 96 DPI 的截图不能替代原生验收。

## Architecture（executed）

分层与禁止范围通过：本轮只改 `Views/Fluent/**`、`DesignSystem/Styles/**`、`App.Tests/**`、本卡 `verification/**`；未改 Core/Host/IPC/schema/依赖/共享契约/用户数据、冻结设计、生成物、Current V2/组合根/FrontendSelector/FEA-07 seam、旧 `verification/FEA-06/**`。`git diff --exit-code 669a4ae02 bb71e43db0063a99abe84973763656d97ae8186a -- <禁止路径集合>` = 0。

真实状态链成立：StatusBand 的 `UpdateStatus` 由四个页 ViewModel 的 PropertyChanged 与 Navigate/SetViewportWidth 驱动，**运行态来自真实 Host `SaveGate` 未完成**（测试断言该 turn 未完成、页内“进度写回中…”与状态条“正在保存阅读进度…”），**错误态来自真实页图读取 `IOException`**（页内错误占位 + 状态条“页面读取失败（IOException），可重试；不会自动跳过”）。NavRail 折叠是真实 `IsVisible=false` 且不占位，状态在外壳字段中跨页保持（Workbench→Library 断言）。窗口宽度由 `FluentShell.SizeChanged → SetViewportWidth` 持续提供，`_viewportWidth` 只保留宿主窗口宽度、不再被 surface 的扣边框宽度覆盖。

生命周期解绑成立：`FluentDecorativeLoop` attach 时读取真实 `Window.IsActive`，DetachWindow 不再把解绑写成激活；粒子 `Play` 返回可幂等取消句柄，`Cancel` 使 generation 失效、解绑 Window 事件并同步移层；`ReaderPageView.ConfigureMotion` 在策略归零时同步取消。我以仓库外 probe 独立复现 r3 附录 C 的两个失败序列（现在均通过）及 4 个额外组合（见附录 C）。

**Architecture 结论：PASS。** 装饰生命周期此前的 PARTIAL 已收敛；唯一遗留是 `FluentUi.DecorativeShelfGradient` 的初始 Canvas 令牌/注释与 `Bind` 的 Overlay→Sunken 不一致（R2R4-003，P2，非执行路径缺陷）。

## Standards（executed）

按 AGENTS、Task 写域、协作协议 §4/§4.1、冻结设计约束核验：无越界写入、无新增依赖/字体/颜色/资产、无用户数据写入、无 push；build 0 warnings。未发现记录在案的硬性标准违规。Fowler baseline 仅 1 个判断项：possible Divergent Source of Truth（渐变工厂初始 `Nm.Color.Bg.Canvas` 与实际 `Bind(Overlay→Sunken)`，见 R2R4-003），不构成硬性违规。

治理指针：R2R3-006 的原矛盾（STATUS“无 READY 节点”对 PLAN“READY D-14”；旧 DAG 把 RESIDUAL-1 写 in_progress）已由 8203b3d28 消除；仍剩数字滞后（R2R4-001）与 Task reviewer 字段滞后（R2R4-002），均属 DSH 写域，集成时更新。

## Spec（executed）与 AC

| AC | 判定 | 依据 |
|---|---|---|
| AC-1：IN-1.1/1.2 三态降级/暂停/无泄漏/视觉签署 | **MET（headless/96DPI 冻结范围）** | 8s 循环仅改 Brush.Opacity；reduce/auto 系统关/category-off 静态且不建动画对象；失焦暂停、detach 停帧、相位保持；粒子 400ms、reduce 无层、失败/失焦/新翻页组合全过；渐变 full first/mid/reduce 双主题签署；独立 probe 6/6。原生 DPI/a11y 不在本 AC 声明内。 |
| AC-2：IN-2A 16+1 组解析后属性=令牌 | **PASS（限冻结组，未回退）** | 136 图同字节对应上轮 PASS；`expected-tokens.md` 与状态断言未削弱；D-14 特判保留；新增 danger pressed 读取实际 PART_Root/ContentPresenter 与 ≥4.5:1 断言。 |
| AC-3：IN-2B 像素格+独立签署 | **MET（本卡已列 IN 格；172/172 签署）** | pages8/components142/decor10/shell12，172 唯一 SHA；shell 的 1024/1280/1600、NavRail 折叠、StatusBand 运行/错误均真实。**TopBand 紧凑（200% DPI）仍按 B-5/D-1 NOT_RUN，不写达成**；双页/滚动、RegionBox 冲突等 BLOCKED 格不在本卡签署。 |
| AC-4：回归/生成器/治理/pins/旧 SHA/写域 | **机械门禁 PASS；当前指针 PARTIAL** | 1289/0/57、生成器、check、pins、旧四 SHA、禁止范围、默认零写入、副本 opt-in 均通过；STATUS/PLAN 数字与 Task reviewer 字段滞后（P2，DSH 集成时更新）。 |
| D-14 / OUT / BLOCKED / 原生 200% DPI / a11y | **未达成 / NOT_RUN** | `DesignSystem/Controls` 相对 base 零 diff；D-14 卡 `ready`、未实施；OUT/BLOCKED 维持 Task 原文；未运行原生 DPI/a11y，没有把 headless 96 DPI 写成原生验收。 |

## R2R3-001…006 逐条复核

| 原 finding | 本轮核验 | 证据 | 结论 |
|---|---|---|---|
| R2R3-001（P1）冻结 IN 格缺 NavRail 折叠、StatusBand 错误/运行态、宽度标签 | 代码：顶部 `NavRailToggle` 切换 `_navRailCollapsed`，`ApplyNavRailVisibility` 隐藏不占位、跨页保持；`UpdateStatus` 从当前页真实 State/Error 投影错误，Reader 的 Host SaveGate 未完成投影运行；宽度用宿主 viewport。像素：1024 `Medium · 1024–1279`、1280 `Compact · 1280–1599`、1600 `Full · ≥1600`；1024/1280/1600 三图 NavRail 均展开（rail 区 154341 像素的 200px 列块），collapsed-1280 图 rail 区变为页面背景、内容左移；running 状态条蓝色 (57,102,131)=#396683，error 红色 (161,67,45)=#A1432D（dark 分别 #86B0CB/#DB9487）。测试断言 band==GetResponsiveBand、断点文本包含 band、折叠跨页保持、状态文本/令牌颜色。 | 6 张 shell 状态图 + 6 张宽度图（双主题）；见附录 A 与 E | **FIXED**。TopBand 的 200% DPI 紧凑态仍属 B-5/D-1，不在本格。 |
| R2R3-002（P1）light 渐变全序列仅 0–4 色阶、不可辨 | 新实现只改既有令牌 `Bg.Overlay→Bg.Sunken`、Opacity 0–1、8s 周期不变。独立光栅：light first→mid 纯背景横带 (34,645,1000,60) max14、gt8=25114（整 crop max15、gt8=142193）；first→static max17、gt8=31699；**mid→static max3**（证明不是容差抖动）；strip 均值 first(250,249,247)→mid(244.5,242.4,239.6)。差分图为平滑斜向渐变场，文字/AA 区无差；并排/叠放目视可见白到暖灰的缓慢呼吸。dark first→mid 整 crop max23、strip gt8=10475；first→static crop max27。 | 6 张渐变图（双主题 first/mid/static）＋独立像素脚本输出；见附录 A/E | **FIXED**（以独立像素检查签署，不以 tolerance 单独关闭；可辨但克制）。 |
| R2R3-003（P2）danger pressed 前景/背景约 1.18:1 | 模板 `Button.fluent-danger:pressed /template/ Border#PART_Root` 改为 `Status.Failed`，与 pressed 公开 Background 同源；pressed Foreground=`Bg.App`。独立像素（真实按钮区域 191..328 × 150..188）：light 背景 (161,67,45)=#A1432D、文字 (250,249,247)=#FAF9F7，**5.9467:1**；dark 背景 (219,148,135)=#DB9487、文字 (20,21,24)=#141518，**7.4751:1**。测试读实际 PART_Root/ContentPresenter，断言令牌与 ≥4.5:1。 | 2 张原 REJECT 已改字节；见附录 A | **FIXED**。 |
| R2R3-004（P2）失焦→导航→返回错误 Resume | `OnTargetAttached` 读取真实 `_window.IsActive`；`DetachWindow` 不再清失焦；`Run` 检查 `_windowDeactivated`。测试 `ShelfGradient_InactiveNavigationReturn…` 与粒子版 `PageTurnParticles_InactiveNavigationAndNewTurn…` 通过。我的独立 probe 用 r3 完全相同序列：失焦→Workbench→Library→重新 Motion，`IsRunning=false`、PendingFrames=0、phase 保持；Activate 后恢复。 | 测试 + 附录 C probe 6/6（原 r3 实跑 FAIL 的两条均 PASS） | **FIXED**。 |
| R2R3-005（P2）粒子切 reduce 仅改后续时长、旧层残留 | `Play` 返回 `Cancel` 句柄；`Cancel` 幂等：标记 cancelled、`animation.Cancel()`、解绑 Window、同步移层；`ConfigureMotion` 在 `DecorativePageTurnMilliseconds<=0` 时同步取消；`DetachedFromVisualTree`、新翻页也释放句柄。测试覆盖播放中/暂停中 × reduce/auto 系统关/category-off 六格；我的 probe 另测暂停中 reduce、播放中 reduce、播放中 auto+系统关、播放中 category-off：切换瞬间 layer=null、排空后 PendingFrames=0、Activate 与新翻页均不复活。 | 6 个 theory 用例 + 附录 C probe 4 场景 | **FIXED**（未声称物理撤回平台已排队回调；generation 取消使其无操作且不再排队，诚实）。 |
| R2R3-006（P2）STATUS/PLAN 当前指针矛盾 | 8203b3d28 已把 STATUS“下一步”与 PLAN READY/进行中/DAG 统一为 READY=D-14、RESIDUAL-2 in_progress；两者不再互斥，旧 DAG 不再把 RESIDUAL-1 当下一节点。Task delivery_head 已由 DSH 更新为 832103393。仍余数字滞后，见 R2R4-001。 | STATUS:10、PLAN:36–39、Task:17 | **FIXED（矛盾）**；数字滞后另记 P2。 |

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R2R4-001 | P2 | `doc/STATUS.md:10`；`doc/REBASELINE_PLAN.md:37,39` | R2R3-006 的互斥已消除，但两处仍写 “R2R3 返修中 / 1281/0/57 / 164 PNG / 交付 445afc0ac”，落后于 R2R3 实际交付（1289/0/57、172 PNG、17a26d552/c70d5c348、impl-r4 复核中）。恢复入口不矛盾但会误导下一位读者。 | 对照 Task:17、Handoff、本报告 Verification 与 172 SHA | DSH 在其授权写域把 STATUS/PLAN 的进行中数字与审查轮次更新到实际交付；历史字节保留。 | open（DSH 集成时修） |
| R2R4-002 | P2 | `doc/tasks/FEA-06-RESIDUAL-2.md:10` | Task front matter `reviewer` 仍是 “…impl-r2 changes_requested …——R2R2 返修中”，与同文件 `delivery_head: 832103393（…impl-r4 复核中）` 不一致，未记录 impl-r3/impl-r4。 | Task:10 vs Task:17 | DSH 在 Task 写域补记 impl-r3/impl-r4 结论或改为指向最新 review；不覆盖历史条目。 | open（DSH 集成时修） |
| R2R4-003 | P2 | `NewManga.App/Controls/FluentUi.cs:164-188`（初始 `Nm.Color.Bg.Canvas` 与注释）vs `ShelfPageView.cs:132`（`Bind(Overlay→Sunken)`） | 工厂仍声明/初始化第一个停点为 `Bg.Canvas`，且注释称两个停点都通过 DynamicResource 绑定；实际生产路径由 `FluentTokenGradient.Bind` 覆盖为 `Overlay→Sunken`。当前渲染/测试正确，但形成两份真相：若 Bind 失败（`Application.Current` 为空）会静默保留未解析/不同令牌，未来重构易误改。 | 代码对照 + `ShelfGradient_BindsOnlyExistingBgTokens…` 断言实际停点 | 对齐工厂的初始颜色与注释到 `Overlay→Sunken`（或删除已不可解析的初始绑定），不改变视觉；可与本卡集成一并处理或登记小清理。 | open（低风险） |

在记录范围内未发现 P0/P1。三个 P2 都不阻断实现/证据批准；R2R4-001/002 是 DSH 自己的文档写域，R2R4-003 是不在执行路径的代码卫生。

## Verification（executed）

运行头：Windows 10.0.26300、pwsh 7.6.8、SDK 10.0.401/net9.0、Avalonia 11.3.22/headless Skia 96 DPI。全部命令在 `G:/CODEX/New Manga`（除明确标注的副本/probe）。

| 场景 | 实际命令或步骤 | 结果/EXIT | 判别证据 |
|---|---|---|---|
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | PASS / 0 | 0 warnings / 0 errors（EXIT=0）。 |
| 无过滤全量 | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --nologo --logger trx --results-directory <workspace>/impl-r4-review/results-normal` | PASS / 0 | **1289 passed / 0 failed / 57 skipped，总 1346**；相对 1281/0/57 = +8/0/0；逐程序集见附录 B；无 filter。 |
| 默认零仓库写入 | 上述运行前后 `git status --porcelain` | PASS | 前后均空；我的 checkout 未产生源码/证据 dirty。 |
| opt-in 独立重捕获 | 固定 head 副本（`core.longpaths=true` clone → checkout 17a26d552），build App.Tests 后 `$env:NEWMANGA_CAPTURE_RESIDUAL2_PNGS='1'` + inventory 记录的同 filter | PASS / build0、test0 | 1 passed/0 failed/0 skipped；副本 status-after 41 项**全部**在 `verification/FEA-06-RESIDUAL-2/visuals/`（24 M + 12 ?? + 4 D + inventory M），非 visuals 变更=0；**172/172 PNG 与原仓逐字节一致**，副本 inventory head=17a26d552。 |
| 第一次副本尝试 | 未设 longpaths 的 shared clone（验证脚本基础设施） | 不计 PASS（作废） | 长路径导致 checkout/index 残缺、测试因副本自身 status 断言失败；已删除该副本，未把它当产品失败或证据；随后按上述 longpaths 副本重做。 |
| TokenGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen -- --check` | PASS / 0 | 292 rows，byte-for-byte up to date。 |
| ThemeGen | `dotnet run --no-build --project apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen -- --check` | PASS / 0 | generated theme artifacts match frozen token source。 |
| governance | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS / 0 | 15 current documents；3 warnings（10 非终态 Task、STATUS/PLAN 体量预算 80%），非语义裁决。报告落盘后同命令复跑结果见文末补记。 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | PASS / 0 | 15/15。 |
| 旧四 PNG | `Get-ChildItem verification/FEA-06/screens -Filter *.png | Get-FileHash -Algorithm SHA256` | PASS | 四值完整见附录 D，与 669a4ae02 基线一致。 |
| 禁止范围 | `git diff --exit-code 669a4ae02 bb71e43db0063a99abe84973763656d97ae8186a -- <doc/design, doc/contracts, App/Shell, FrontendSelector.cs, DesignSystem/Generated, DesignSystem/Themes, verification/FEA-06, ApplicationCore, CoreClient, Host, App.axaml/.cs, MainWindow.axaml.cs>` | PASS / 0 | 零 diff。 |
| 独立生命周期 probe | 仓外 net9.0 xunit probe 引用固定 head 的 App.Tests 输出，反射复用既有 Create/CreateWithPages/Motion，执行 6 场景 | PASS / 0 | 6 passed/0 failed/0 skipped；原 r3 实跑 FAIL 的 InactiveNavigationReturn 与 ReduceWhilePaused 本次均 PASS；源码与输出见附录 C。 |
| 172 图独立签署 | 逐图 contact sheet 实看 + 重点图原尺寸/裁切/像素差；SHA 与 inventory/克隆捕获交叉核对 | PASS | 172 PASS / 0 REJECT / 0 NOT_RUN；附录 A。 |
| 原生 200% DPI / 原生 a11y / 桌面触控 | 未执行 | NOT_RUN | B-5/D-1；不用 headless 96 DPI 替代。 |
| BLOCKED 格（双页/滚动、RegionBox 冲突、Console/Run 投影、满态统计） | 未执行 | NOT_RUN | 维持 Task E 表，不写达成。 |

**Verification 结论：机械门禁全 PASS；视觉 172/172 签署；生命周期组合由独立 probe 复核；AC-1/AC-3 在本卡 96 DPI 冻结范围成立，原生 DPI/a11y 与 BLOCKED 格保持 NOT_RUN。**

**报告落盘后补记（2026-11-03，HEAD=bb71e43db，本报告为唯一未提交文件）**：`check.ps1` 复跑 PASS（3 warnings，与上同）；`verify_pins.ps1` 15/15 PASS；`git status --short` 仅 `?? doc/reviews/FEA-06-RESIDUAL-2-impl-r4.md`，无源码/证据 dirty、未 push。

## 结论与复审 / 推荐下一步

**本 head 可交 DSH 集成。** R2R3-001…006 的修复有真实产品状态、真实像素、独立 probe 与固定 head 重捕获支撑；剩余 3 个 P2 都在 DSH 写域/代码卫生，不改变实现或证据判断。建议 DSH 接收本报告后：① 在集成验证处更新 STATUS/PLAN/Task reviewer 指针并保留历史字节；② 按 AC-1/AC-3 的 96 DPI 结论与 B-5/D-1 残余决定 done/closed_with_limitations；③ 保持 D-14-STATUS-COLOR-FIX 为后续 ready 卡，不写其达成；④ 可选地把 R2R4-003 与既有域外死代码清理一起登记。

复审须追加新 head 与 findings disposition，不覆盖本报告原字节；不得仅追加新的测试总数申请通过。下一工作为 **FEA-06-RESIDUAL-2 findings 处置与集成验证**，Agent=DSH；Recovery point：仓库 `G:/CODEX/New Manga`，main/同工作区，base 669a4ae02，实现 17a26d552，证据 c70d5c348，reviewed_head=bb71e43db0063a99abe84973763656d97ae8186a。

可直接转发给 DSH：

> 请接收 `doc/reviews/FEA-06-RESIDUAL-2-impl-r4.md`（approved，P0=0/P1=0/P2=3；reviewed_head=bb71e43db0063a99abe84973763656d97ae8186a；实现 17a26d552 / 证据 c70d5c348）。R2R3-001…006 已逐条核实为 FIXED；172 图 172 PASS 已逐图签署；build 0/0、无过滤 1289/0/57、TokenGen/ThemeGen、check、pins 15/15、旧四 SHA、禁止范围、默认零写入均通过；固定 head 副本重捕获 172/172 逐字节一致，opt-in 只写本卡 visuals；r3 附录 C 两个失败序列在独立 probe 中转 PASS。请在集成时更新 STATUS/PLAN 数字与 Task reviewer 字段（R2R4-001/002），可一并处理 R2R4-003；不要把原生 DPI/a11y、OUT/BLOCKED、D-14 写成达成。D-14-STATUS-COLOR-FIX 保持后续 ready 卡；按 AC 结论决定 done/closed_with_limitations，未 push 前保留本卡证据字节。

## 附录 A：172 PNG 逐图签署

签署人：DSH 独立子代理（impl-r4 Reviewer），2026-11-03。路径相对 `verification/FEA-06-RESIDUAL-2/visuals/`。每张均出现在带文件名标签的 contact sheet 中并已实际查看；136 个同字节项与旧 impl-r3 已签 PASS 的 SHA 相同（不是仅凭 SHA 推断：本轮 sheet 已实看，且以固定 head 重捕获复核），24 个改字节项/12 个新增项另行按原尺寸或裁切复核；SHA 取自本机 `Get-FileHash`/Python hashlib，与 inventory 结算一致。

PASS 只签署该文件所标场景的真实可见内容，不签署整组件全部状态、原生 DPI/a11y 或未交付的 B-5/D-1/BLOCKED 格。StreamingThumb lazy 是 Task 允许的懒加载骨架；AlertBanner 的“普通基底＋glyph/标签”按 D-11 映射签署；reduce 静态图只签真实对照，不替代 full 动效。

| file | 签署 | 理由 | SHA256 |
|---|---|---|---|
| `components--alert-banner--blocked--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（blocked）；同字节旧PASS＋本轮 sheet 实看 | `889624c7872462760cc7545756717001ea63349fd747c19b4b39b22bc77a5b24` |
| `components--alert-banner--blocked--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（blocked）；同字节旧PASS＋本轮 sheet 实看 | `5d540e07adc5dcda6252092cb9e7b01708fbb2079d4755bddc412378f623154a` |
| `components--alert-banner--done--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（done）；同字节旧PASS＋本轮 sheet 实看 | `7a4d26627e72ace2020ff5ea0e51adc970e4b03184e30a8acbd5fa1386c8474e` |
| `components--alert-banner--done--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（done）；同字节旧PASS＋本轮 sheet 实看 | `163a6a8d34bc3115045d0ca15df288d686880733d038319321a454bdef346cf8` |
| `components--alert-banner--failed--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（failed）；同字节旧PASS＋本轮 sheet 实看 | `4e795504d6985ae9096333d8fb4eef07d5619a75dc5c8456669ac7b0871da9b0` |
| `components--alert-banner--failed--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（failed）；同字节旧PASS＋本轮 sheet 实看 | `c0c0ff3836fba3fceb4f8a4bc58423f3d8fb0e77d10c94e7b53abbdf4376c719` |
| `components--alert-banner--locked--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（locked）；同字节旧PASS＋本轮 sheet 实看 | `dd5a7ffc3450eeeb9dbb85065152f8f1c5a3714caba00d585420077e5f71a78a` |
| `components--alert-banner--locked--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（locked）；同字节旧PASS＋本轮 sheet 实看 | `bc5b80643145d8192e36d9b3f1a81ad4d3db0c1212559f9aaaa0343b57e446e7` |
| `components--alert-banner--notstarted--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（notstarted）；同字节旧PASS＋本轮 sheet 实看 | `bbaa2d452fc25923a23d2ad06a4c4f75fbe5a04a8d650fb4cb51b267db021eef` |
| `components--alert-banner--notstarted--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（notstarted）；同字节旧PASS＋本轮 sheet 实看 | `e2154725e7c1eae2a64f9e84a8b8cba298bdaa5fe74cb08b04a793e1f1d61f3a` |
| `components--alert-banner--queued--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（queued）；同字节旧PASS＋本轮 sheet 实看 | `41f70aa437e62c3463760aab8ded163ee5bcc76b12f609c13370eebae3d6b0c5` |
| `components--alert-banner--queued--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（queued）；同字节旧PASS＋本轮 sheet 实看 | `0f10612d149089d0d9aed4ee66177f239f1fa9b67f704bd96f2b0381c42b53fb` |
| `components--alert-banner--running--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（running）；同字节旧PASS＋本轮 sheet 实看 | `99c5e3c53622e072898c86ea2aae0d2029d9d4e0b7fd8b83c35f0719f7356ce2` |
| `components--alert-banner--running--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（running）；同字节旧PASS＋本轮 sheet 实看 | `4b694feb9fd9888e13eec5e5fe60bc49b2c82469c5486bbb123d61db9e232e11` |
| `components--alert-banner--skipped--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（skipped）；同字节旧PASS＋本轮 sheet 实看 | `a0ffe5811f77b4772115d3455cc443e94f938f6cf57c4f7a3eae992b073da157` |
| `components--alert-banner--skipped--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（skipped）；同字节旧PASS＋本轮 sheet 实看 | `c8bb612c824489e5a896f5e3aa2138c32550a2f30df26f390fbdd43c689331e1` |
| `components--alert-banner--stale--full--dark.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（stale）；同字节旧PASS＋本轮 sheet 实看 | `c3bc9b631b8eb5b51282a81e0c7fcfebf274fda9bb3effaecb3a105b3145afca` |
| `components--alert-banner--stale--full--light.png` | PASS | 所标 StatusKind 的 glyph/标签可见，基底与九值映射一致；双主题真实（stale）；同字节旧PASS＋本轮 sheet 实看 | `a87e56fd424452afbec7746b1fb573ce28f317f00d5d075dc65c0fba8baeb64b` |
| `components--book-card--default--full--dark.png` | PASS | 书名卡可见；禁用格按 Opacity 降级，非空白占位；同字节旧PASS＋本轮 sheet 实看 | `2b49270515c35d9d25a4ed2af95627d95ec92ec6df94e2abdfa8f43fca7567b7` |
| `components--book-card--default--full--light.png` | PASS | 书名卡可见；禁用格按 Opacity 降级，非空白占位；同字节旧PASS＋本轮 sheet 实看 | `4155acd86a1b6a0fe18a8ca2adbd0eda43dc88665f52811e56531d94c23458d8` |
| `components--book-card--disabled--full--dark.png` | PASS | 书名卡可见；禁用格按 Opacity 降级，非空白占位；同字节旧PASS＋本轮 sheet 实看 | `a379dba17d8109c2da45f7bddf371ae47dd8bd9db5d3f7e22baa7169f88594bc` |
| `components--book-card--disabled--full--light.png` | PASS | 书名卡可见；禁用格按 Opacity 降级，非空白占位；同字节旧PASS＋本轮 sheet 实看 | `611bd5b99caf77161b02dabc5a81d92113e924141b54e036423060453286005e` |
| `components--book-row--default--full--dark.png` | PASS | 书名行可见；禁用格按 Opacity 降级；同字节旧PASS＋本轮 sheet 实看 | `d4be22a5228aa3f8930cd8e2ae25789cdcd843780146a68d1d5f61228a89afdf` |
| `components--book-row--default--full--light.png` | PASS | 书名行可见；禁用格按 Opacity 降级；同字节旧PASS＋本轮 sheet 实看 | `f3e1043e9fca4fe3bedc316a8b6d9e16a1d3e810e3456da80eaeec343df48324` |
| `components--book-row--disabled--full--dark.png` | PASS | 书名行可见；禁用格按 Opacity 降级；同字节旧PASS＋本轮 sheet 实看 | `661615cb6d3be9fd287c54c36ba03082bcc02d78a0c686110fc0369d9c9167e6` |
| `components--book-row--disabled--full--light.png` | PASS | 书名行可见；禁用格按 Opacity 降级；同字节旧PASS＋本轮 sheet 实看 | `17d95b8b06885f6bc4a6e676169a50885a30b011701f29bcad0a8e89c662f32c` |
| `components--chapter-list--default--full--dark.png` | PASS | 三章行完整可见，无旧顶部裁切；同字节旧PASS＋本轮 sheet 实看 | `54d5facd816f38d120a9fc5adcfcdd8a31b3258c182b8949a077dfefeaa33386` |
| `components--chapter-list--default--full--light.png` | PASS | 三章行完整可见，无旧顶部裁切；同字节旧PASS＋本轮 sheet 实看 | `f4bc1e72aa58d8bfb6f4045028e95badfc02bb6255f0535ade7252bdd32159d5` |
| `components--command-palette--empty--full--dark.png` | PASS | 真实搜索输入（`不存在的命令-zzz`）与零结果、关闭按钮可见；浅色主题面板＋深色 scrim 非暗主题伪造。本轮改字节，已复核 | `f02341d594f487b3f5096ca5b7ec025af56766e80dc755393680de28533427eb` |
| `components--command-palette--empty--full--light.png` | PASS | 真实搜索输入（`不存在的命令-zzz`）与零结果、关闭按钮可见；浅色主题面板＋深色 scrim 非暗主题伪造。本轮改字节，已复核 | `a43cba142d61fc4f45e96056b124a1e97854122c5d8ceb268959cadcafceb669` |
| `components--command-palette--result--full--dark.png` | PASS | 真实命令结果（书架/刷新书架/关闭）与搜索输入可见；浅色面板＋深色 scrim。本轮改字节，已复核 | `3fb1b7368fb3127acab2ab5793d48128e7d94b9f8aaf068119ae0281be65e954` |
| `components--command-palette--result--full--light.png` | PASS | 真实命令结果（书架/刷新书架/关闭）与搜索输入可见；浅色面板＋深色 scrim。本轮改字节，已复核 | `0c164442056950b2671e6ba4dcaee6da26a0a6b74efe65245739e3d1a47945df` |
| `components--context-menu--disabled-item--full--dark.png` | PASS | 实际菜单打开，禁用项灰化可辨；同字节旧PASS＋本轮 sheet 实看 | `8a58e962dd4219c04b2daaa5914999a34acf64f073b4039e970cab33ab8191bc` |
| `components--context-menu--disabled-item--full--light.png` | PASS | 实际菜单打开，禁用项灰化可辨；同字节旧PASS＋本轮 sheet 实看 | `66d6d2856d808299064b6c7e5986856f335185c2510d438607fbab9862ce49ac` |
| `components--danger-button--default--full--dark.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `6a41f040ec40ba869973b2cb31e89b16a71380e79693f2a06956b33bcd0281d2` |
| `components--danger-button--default--full--light.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `1d8455eaf665cdd6b7571a30a955bb5a67b886c80dc1ec1c9865e2ca780adcc7` |
| `components--danger-button--disabled--full--dark.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `860f0a294d694add33ba817e43cc852d2e8e823ccba920e3603cef19aab4d0ed` |
| `components--danger-button--disabled--full--light.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `9149c20ee24a91492f1add37dcc719686595390af0869a50973bc497ebedcf42` |
| `components--danger-button--hover--full--dark.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `be969a6bb952c675bda2e1172da9dfe5d50fac5fd55cef03e324495b24359d4a` |
| `components--danger-button--hover--full--light.png` | PASS | 所标组件/状态可见；同字节旧PASS＋本轮 sheet 实看 | `9dc59d68f89479997baecd320880b65cd967d841753286d0a4f1d71452a926df` |
| `components--danger-button--pressed--full--dark.png` | PASS | pressed 实际模板背景 Status.Failed、前景 Bg.App；独立像素对比 7.48:1（≥4.5:1）。本轮改字节 | `c9ed4f8e9f47cb250fd569df180730a98f198a3a78fd4e077c855cf46379d6a9` |
| `components--danger-button--pressed--full--light.png` | PASS | pressed 实际模板背景 Status.Failed、前景 Bg.App；独立像素对比 5.95:1（≥4.5:1）。本轮改字节 | `8d37c109c38e96fc73fa5f7d1ddd08c3de02c9631ea54fe19b27470a980bed35` |
| `components--dialog--closed--full--dark.png` | PASS | 开态内容可见/关态内容移除；只签开合；同字节旧PASS＋本轮 sheet 实看 | `8ac09c4e2df3f412b5a45695aadf0bddc7035b3faf45d4dd063405bc0e3de48a` |
| `components--dialog--closed--full--light.png` | PASS | 开态内容可见/关态内容移除；只签开合；同字节旧PASS＋本轮 sheet 实看 | `12417c1281d9511903ddfe5d90ec27972402b28cbfd53d27a81704e9d0128659` |
| `components--dialog--open--full--dark.png` | PASS | 开态内容可见/关态内容移除；只签开合；同字节旧PASS＋本轮 sheet 实看 | `658516ddfb910a804a2a1c903f79d86b637918c312e4ad0cefdefb7bba306651` |
| `components--dialog--open--full--light.png` | PASS | 开态内容可见/关态内容移除；只签开合；同字节旧PASS＋本轮 sheet 实看 | `d0802f517cce8b3ffb55e3a210536bcf1eee78dc8ce173c2a8b06987e6b41dfd` |
| `components--drawer--closed--full--dark.png` | PASS | 实际抽屉开合，内容可见/移除；同字节旧PASS＋本轮 sheet 实看 | `3a23880327ee14fa9bb2129e23db725f4a0fa7b602295ba53331d7fe92dd95e5` |
| `components--drawer--closed--full--light.png` | PASS | 实际抽屉开合，内容可见/移除；同字节旧PASS＋本轮 sheet 实看 | `87da9a58f004be601d18b043b2eddb80a881d96a35e9a295c0a2851855c9b08b` |
| `components--drawer--open--full--dark.png` | PASS | 实际抽屉开合，内容可见/移除；同字节旧PASS＋本轮 sheet 实看 | `89177c7a4d87f7c6d47ba499e2dd8def32ac4ad6d53793efa20a1d650b22b301` |
| `components--drawer--open--full--light.png` | PASS | 实际抽屉开合，内容可见/移除；同字节旧PASS＋本轮 sheet 实看 | `f2af162bb59466d6d3af98961b858c52c9966d80f32814f3ee1a0ac667abe2be` |
| `components--empty-state--default--full--dark.png` | PASS | 标题、提示与导入动作可见；同字节旧PASS＋本轮 sheet 实看 | `00ebe5a1fb4d8f0bcae9cad3b1a8a1ad705e828c67ba93649fa61eeabf94ca2c` |
| `components--empty-state--default--full--light.png` | PASS | 标题、提示与导入动作可见；同字节旧PASS＋本轮 sheet 实看 | `fc608c250bd153f58ba53625b92ec5aeefba30f188c89c6b451811b0b066d36a` |
| `components--error-state--retryable--full--dark.png` | PASS | 错误原因与有/无重试动作可见；同字节旧PASS＋本轮 sheet 实看 | `95e877efe79f19166792bef6df47f17f376e677aba7bccc1870d996447fd6275` |
| `components--error-state--retryable--full--light.png` | PASS | 错误原因与有/无重试动作可见；同字节旧PASS＋本轮 sheet 实看 | `d14df0c76fddc633c968a984575d190192e80840a876734bfbd8083e5984cf65` |
| `components--error-state--unrecoverable--full--dark.png` | PASS | 错误原因与有/无重试动作可见；同字节旧PASS＋本轮 sheet 实看 | `5433294d678ee91518da15555b8b3630d74a04e8d83475f1b50da405e9433af5` |
| `components--error-state--unrecoverable--full--light.png` | PASS | 错误原因与有/无重试动作可见；同字节旧PASS＋本轮 sheet 实看 | `403d1287e9e6e0e5fc7b7a634362bfab9bde3b624a6bd31f1fd69a46b7aba622` |
| `components--icon-button--checked--full--dark.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `92fd3d87c790490f7abef0ff92f0b47e0af790063bb71f01123d9df360a165a3` |
| `components--icon-button--checked--full--light.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `d009b3061519b65f92451ea1c08ba9c8f88fc8e00a56bf3e31204bbb5a4db589` |
| `components--icon-button--default--full--dark.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `a76694f35f67dc4fc002b0d0bf7f331f93fe77d86b8c5d5921a7cbb782e87cbe` |
| `components--icon-button--default--full--light.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `dbe9ead20b6ee7668251604d59e9eac257327fd84f1f64927b9331d027ff06b6` |
| `components--icon-button--hover--full--dark.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `36739cad328ce06cd45e1e060651668ceeff5b1b13d0154c9a51018034d554b2` |
| `components--icon-button--hover--full--light.png` | PASS | 真实 NmIcon；checked 金底/边框与 default/hover 可区分；同字节旧PASS＋本轮 sheet 实看 | `0ee78de15661439f7382201ba67dab8d7123a1803cb9451ce5665d338fd1e74c` |
| `components--page-thumb-strip--default--full--dark.png` | PASS | 两张真实 fixture 缩略页与页码可见；同字节旧PASS＋本轮 sheet 实看 | `c0a1b356140f095b360aa0e13525b2577cc506a432020068441f36b95fea6626` |
| `components--page-thumb-strip--default--full--light.png` | PASS | 两张真实 fixture 缩略页与页码可见；同字节旧PASS＋本轮 sheet 实看 | `232e323c050233cde9ef3a2be0cdeded6948a3e6812cd49c7062c6b23597db7b` |
| `components--primary-button--default--full--dark.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `11fa85f9e7a5f03e6a32b8ef79bd2f944556310d4a506e888c03db45f7de794e` |
| `components--primary-button--default--full--light.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `ccaf77f6cfc0095e4f14951805384f820a4895fba409900d0718ef165f112849` |
| `components--primary-button--disabled--full--dark.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `19096cdb5df881d61ad3ae2f43f8ff6ac34aadbed4e5e501bc0a163790e65c3d` |
| `components--primary-button--disabled--full--light.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `1ea6a98c677b17d93fb066256cac6a0894ac05bd0d2ef59b4ec527ab67f42834` |
| `components--primary-button--hover--full--dark.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `058ccb1d999c4e4f39f51328c51faaebbf7d0d10425e2493bb9569546405c27a` |
| `components--primary-button--hover--full--light.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `a221df936ec221b8a3e4abfc2c64ef1e4f0e0389fb52cdcadd5a7d5c0483e34f` |
| `components--primary-button--pressed--full--dark.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `7bd2d5cf594bcbe8527a3e59a3b7706b3b63b67ed2285de07f1550c0c1c2a955` |
| `components--primary-button--pressed--full--light.png` | PASS | 主题化按钮与所标交互态可见；同字节旧PASS＋本轮 sheet 实看 | `966913b84077ce64a6cd571bb7b158b78b3d0b859d7e4663355ec4d662301f01` |
| `components--reader-page--single--full--dark.png` | PASS | 真实 fixture 页图，非空章节占位；同字节旧PASS＋本轮 sheet 实看 | `bcc7af72ece3d9b5e125c63a71c403d5c33be00bbab7ceda1532bb4efab95182` |
| `components--reader-page--single--full--light.png` | PASS | 真实 fixture 页图，非空章节占位；同字节旧PASS＋本轮 sheet 实看 | `e3f00ce494d670cf1e68710b0fb1c7a82491ef1a401a23ecba369bc103cccd55` |
| `components--reader-progress--default--full--dark.png` | PASS | 实际 60% 进度填充可见；同字节旧PASS＋本轮 sheet 实看 | `58c8d0d619c7e0bd14466c858781cb6124ced8c676744020b9309b97f7bf690a` |
| `components--reader-progress--default--full--light.png` | PASS | 实际 60% 进度填充可见；同字节旧PASS＋本轮 sheet 实看 | `0beab56ff843af1299a11b62a6eecf27871645195cd620dab18f689d3a045a31` |
| `components--region-box--default--full--dark.png` | PASS | 区域边框与 hover 填充可见；同字节旧PASS＋本轮 sheet 实看 | `f3b894536c2572c74ec509e12d62a10c47cb8108c1f275ccf2af1e602d3e4426` |
| `components--region-box--default--full--light.png` | PASS | 区域边框与 hover 填充可见；同字节旧PASS＋本轮 sheet 实看 | `c9d3be1cc6e7142e8f8beb303619091a6644123948e672f920da4acd21bc0051` |
| `components--region-box--hover--full--dark.png` | PASS | 区域边框与 hover 填充可见；同字节旧PASS＋本轮 sheet 实看 | `f62a1758ab3074ac07b2434cbf4e9dce6f55640331522edb2e706b4554d6d42d` |
| `components--region-box--hover--full--light.png` | PASS | 区域边框与 hover 填充可见；同字节旧PASS＋本轮 sheet 实看 | `17f44ae5eb9b98aa30a1e446bdd0809522d3f376ecdf578addd59d3bf11ac600` |
| `components--search-field--default--full--dark.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `dbc55aaef36076c30c35a6bc0f18da5f79ce9299fa457ebfe5251836b0290bae` |
| `components--search-field--default--full--light.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `27a98ef1deb62665126467e998639b74f366c4f8d76ac89abce5ad383c05cc5d` |
| `components--search-field--focus--full--dark.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `ca1645c4d6675445eb86d444829d8419e5256471524f8e462fab4b20f143a747` |
| `components--search-field--focus--full--light.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `b9d104868ae380e64b973d609c369f0a7a1883c886f5583edb8633d2204c089c` |
| `components--search-field--value--full--dark.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `eff1c117102189d659c3c4d224d121ba36388b96ba74a8f5f4c1518f012acce1` |
| `components--search-field--value--full--light.png` | PASS | 输入/值/Tab 焦点外环与所标状态相符；同字节旧PASS＋本轮 sheet 实看 | `9357d1f26a74a6bd8b6cfda1f20f515ea1698208b56aa62690cd8104152d3267` |
| `components--secondary-button--default--full--dark.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `6225650c0f4293b861aa2eccc06c726ca717c977c935a68598443d2aa19f9220` |
| `components--secondary-button--default--full--light.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `e3bfe1fbe83bb94888ee20dd3818dd5bc8b6d80f85beb6aa945e1eab3b4c2a14` |
| `components--secondary-button--disabled--full--dark.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `36721b2c032c5db03e353bfdd3d3f44677c27b6cce80a6ac4620a8cac133c131` |
| `components--secondary-button--disabled--full--light.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `2884f66463b69191dcefff138ed22551c1957cdce4f79620ca6b02b3b6e4ae98` |
| `components--secondary-button--hover--full--dark.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `bb96910170e0fbdf3a921f6b58c89ce7b6da7fb79b0842da46b6763cf71b2615` |
| `components--secondary-button--hover--full--light.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `e57ed5263bca2e360471898acbf01495f5115fda904c3101a6dea021837e3a8f` |
| `components--secondary-button--pressed--full--dark.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `61222ad0c8aaf2811461c14e78bd344af3294bad1c3452f9066823699169e4ed` |
| `components--secondary-button--pressed--full--light.png` | PASS | 默认/hover/pressed/禁用态主题化可见；同字节旧PASS＋本轮 sheet 实看 | `b0be52d745db064b268341b035a824771300f4f6e039616fe66322818e43c516` |
| `components--segmented-control--hover--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `28a542455894ce62b044bab1e8aac9497c5ea143f9dc0eaa1571f7d6bfb14122` |
| `components--segmented-control--hover--full--light.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `465c95af1b22d85ebf8abc205b3109b524e48e79c8b8a851c5c6df7169f6f18b` |
| `components--segmented-control--pressed--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `a3943901f5d06267c9ce416b44a73f1eb2543c1bd39263c5393095f497fcde47` |
| `components--segmented-control--pressed--full--light.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `29ce0fbc6992550f8d840354daa1370e7d45fc735433aac023cda548284f1336` |
| `components--segmented-control--selected--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `e3009ea3f427ce92841d2c2288b8cc847dc1fab4ab44c2c2ac9c467608520500` |
| `components--segmented-control--selected--full--light.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `b0eb26a82c36024b2007657eeee301567c888526e077f24eb0f89e64f8f8794d` |
| `components--segmented-control--unselected--full--dark.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `5cb43a0b3307144d3fbb88636825b62638cb7462658cc9b70d8b017326ae7e40` |
| `components--segmented-control--unselected--full--light.png` | PASS | 目标项选中/未选中/hover/pressed 可见；同字节旧PASS＋本轮 sheet 实看 | `8488e5063a86e0fd17beeafa260569714e3491cfbf0b902152e45248da22676d` |
| `components--settings-field--disabled--full--dark.png` | PASS | 字段值及错误边框/禁用降级可见；同字节旧PASS＋本轮 sheet 实看 | `6860034d4c29c33658afcbc3752a3c187516d6dd411c167562eed1aea058ddc0` |
| `components--settings-field--disabled--full--light.png` | PASS | 字段值及错误边框/禁用降级可见；同字节旧PASS＋本轮 sheet 实看 | `0e5f8d1d74f77f6aecb4bfc5a6f372c81165953393ac537b5bf0ceb202f625d3` |
| `components--settings-field--error--full--dark.png` | PASS | 字段值及错误边框/禁用降级可见；同字节旧PASS＋本轮 sheet 实看 | `8bc7233b0d73cf6f53de6b975933f9215075ede8b1f7030a136af4f3a20dcb86` |
| `components--settings-field--error--full--light.png` | PASS | 字段值及错误边框/禁用降级可见；同字节旧PASS＋本轮 sheet 实看 | `d7550f543ac0d743f328a2f832b3b667bb1942e58d703864a16094ab3dabf19b` |
| `components--skeleton--bookcard--full--dark.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton bookcard）；同字节旧PASS＋本轮 sheet 实看 | `b4c23048c005e5586c44d05f505205fe395f0115de5f7ebc4e9f28ce3808c274` |
| `components--skeleton--bookcard--full--light.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton bookcard）；同字节旧PASS＋本轮 sheet 实看 | `851e1f1010efe1f3f8f0b47e4e1bb615a23120d5c8bca9d8e9fd06d11704a3d3` |
| `components--skeleton--panel--full--dark.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton panel）；同字节旧PASS＋本轮 sheet 实看 | `80b35caafbc126f921557f83f286d8181faf3ab4da629d3bdf28026605c10623` |
| `components--skeleton--panel--full--light.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton panel）；同字节旧PASS＋本轮 sheet 实看 | `51e7b0bae6c7e7a3d756ed912156ae74bc4f0d549b8145b75097cc3a2532f22c` |
| `components--skeleton--row--full--dark.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton row）；同字节旧PASS＋本轮 sheet 实看 | `c467ecc7edf60eb05436ff3b6ce28dced2b37ada5ed218177ac7542a3bbd22e3` |
| `components--skeleton--row--full--light.png` | PASS | 所标骨架形状可见，尺寸不同非同 SHA 占位（skeleton row）；同字节旧PASS＋本轮 sheet 实看 | `f0d55c31d58648991c094e2010dd09034075d7c5986d077652b846cb02c40deb` |
| `components--slider--default--full--dark.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `ce971a4da37eb85f49984872bd59047eae23a6b1ddfc6de7dace352492d97768` |
| `components--slider--default--full--light.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `a9c0e297603c3bcfb861df94a0e2abdd483bee21ed5de80f88968174e453ee4d` |
| `components--slider--disabled--full--dark.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `afc956e90e3da7f0ea600c29adf7bf3ca1b506a61f269d11d9dbfc48efe571ea` |
| `components--slider--disabled--full--light.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `be751e7678927cc6a76d8f135538293e418f1f497d3d7c2a5b4d266dfc295dbc` |
| `components--slider--hover--full--dark.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `006731cca2a8e34b29dd5c5742d6c19c4e5e210cc59174b862cb0837e1e6a037` |
| `components--slider--hover--full--light.png` | PASS | 真实 thumb/填充轨道，无系统蓝；同字节旧PASS＋本轮 sheet 实看 | `7632eb4ee7f4f58f7897dd72fc78986b68b7ae5d33472ed8b13d8bff176ed6e4` |
| `components--streaming-thumb--lazy--full--dark.png` | PASS | Task 允许的 lazy 骨架态可见，不作已加载图像签署；同字节旧PASS＋本轮 sheet 实看 | `70da80c565c842c894ff3ad7ca3d8be6ba6c903de1b0bf5f9b7146f02d0e5231` |
| `components--streaming-thumb--lazy--full--light.png` | PASS | Task 允许的 lazy 骨架态可见，不作已加载图像签署；同字节旧PASS＋本轮 sheet 实看 | `9fe5f380156f6c1efe36f680e43b27820ad8858a9f1a5ab1127a3cd0c9f79938` |
| `components--surface-card--default--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `a1b460f11e58a8d929ae23da500b4c5a0b81773b12fc590b722cd87de9df721a` |
| `components--surface-card--default--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `4749378885e3e70debe7fe35002fd1e3c9289e8963dd5a1e3c889a8be74b89e6` |
| `components--surface-card--disabled--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `165d3b8bdcab65efa970b623293d1fa78a602396ba2e60570d9f62fd2669200c` |
| `components--surface-card--disabled--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `ac7ae33a835b6de04820ee3424d4a0b3a18b273d25da71390368aa4c3fe39849` |
| `components--surface-card--hover--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `0015cb721aad1d66d06b48185a24ea331401e92df1804c573b843f0ea1178830` |
| `components--surface-card--hover--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `be6d587c1a2ba68e7d46e2d42e83fd953e37e527f9ba28f0762d4b8c5133f8c5` |
| `components--surface-card--selected--full--dark.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `4efa48c6452907a3a924900bdf81891da0c67e5f664a082ec071923d74d3bf36` |
| `components--surface-card--selected--full--light.png` | PASS | 表面/hover/选中边框/禁用态可见；同字节旧PASS＋本轮 sheet 实看 | `2039281e84b426718778c598d8a4d5dff5dee7a69c10e4fd78acdde9783051a7` |
| `components--tab-strip--hover--full--dark.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `623b8ea1a98828ec37d781355254ebfab850ed923783c579a40fc573739d3665` |
| `components--tab-strip--hover--full--light.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `658d18952dcbbea6904f41678644cd738d7419745ac8c2f658f6c5fb5a8ae21d` |
| `components--tab-strip--selected--full--dark.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `19f32c0ca252617b9f73971d3069ae7cd22b59551ca65aa7c34275d8552ad84e` |
| `components--tab-strip--selected--full--light.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `1490841169568214e09db6778d3e2a35c1fdf2534223768d444b661281637f7a` |
| `components--tab-strip--unselected--full--dark.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `f297bca8d40097d2d4745750baa7bf59fc59bccadbcf2185547838fca6b9febd` |
| `components--tab-strip--unselected--full--light.png` | PASS | 实际 Tab 选中/未选中/hover 可见；同字节旧PASS＋本轮 sheet 实看 | `f5925ef1b3727fb1b3e2c452630c8e19535d8c2845b02002163e42b9377f5820` |
| `components--toggle-switch--disabled--full--dark.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `7e34408cb5a2f821aace06faa7c44062dd6117b00dbf9159072d221f986f9f7b` |
| `components--toggle-switch--disabled--full--light.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `d68de31cc8842ba81d9e7fad06218af91878e9d85b79de09636acd9d4847dd68` |
| `components--toggle-switch--off--full--dark.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `0c2923ce72c87666b9118d66bf5055fd07a2ef9fd691f0e2df2967230651c721` |
| `components--toggle-switch--off--full--light.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `5c480ea9f571df916d0bdac7f24fee7d0f3ab57dbf50c872e77bea2d34938177` |
| `components--toggle-switch--on--full--dark.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `3f7443f2bd2d5bc4b56026a0e7de252ae45bf3510b2b8b58c0290ca63f56fe85` |
| `components--toggle-switch--on--full--light.png` | PASS | 开/关/禁用切换控件可见；同字节旧PASS＋本轮 sheet 实看 | `e170cbc574001e2be3156434f5260f3858522dc03cdeb2983cadea70be186668` |
| `components--tooltip--opened--full--dark.png` | PASS | 实际提示文本弹出可见；同字节旧PASS＋本轮 sheet 实看 | `0e289319b382638cb22078db49434dab763d5c8ef05b8220d4c34affc4bd262b` |
| `components--tooltip--opened--full--light.png` | PASS | 实际提示文本弹出可见；同字节旧PASS＋本轮 sheet 实看 | `ef8d97e3980922b0e47039f8af4037011ff2afcdaeb9851165028bb2e22ef5cd` |
| `decor--page-turn-particles--mid--full--dark.png` | PASS | dark full 200ms 中点：页面前景稀疏金色粒子可见、不遮内容。本轮改字节 | `60ef983fbc08f8f20dd5ccde540e1ee1cf5421786878979b4c49e5aca4551e7d` |
| `decor--page-turn-particles--mid--full--light.png` | PASS | light full 200ms 中点：页面前景稀疏金色粒子可见、不遮内容。本轮改字节 | `76af16f65b6cc8391085c94be470526dd6335632ecd33eb5aa29a6d90bcd0156` |
| `decor--page-turn-particles--none--reduce--dark.png` | PASS | dark reduce 无粒子层（真实对照）。本轮改字节 | `147d8e823c74bdfcb7e4657eb6d170bd91c70c9b3055c54ce318fbfca6f7bc15` |
| `decor--page-turn-particles--none--reduce--light.png` | PASS | light reduce 无粒子层（真实对照）。本轮改字节 | `70ca25c5f96fccf2388ba8f4867914215b05983c3c8d7da81683284af75258d7` |
| `decor--shelf-gradient--first--full--dark.png` | PASS | dark full 相位 first（first=0ms/mid=3000ms）；纯背景横带 10475 px 差>8、max12（整 crop max23）；差分为平滑渐变非 AA 抖动，肉眼可辨。本轮改字节 | `21cce1e1d2a0242eab3dab1de2e4ad55c06b749a344c77894bc973e2d37d13cc` |
| `decor--shelf-gradient--first--full--light.png` | PASS | light full 相位 first（first=0ms/mid=3000ms）；纯背景横带 25114 px 差>8、max14（整 crop max15）、mean7.47；差分为平滑渐变非 AA 抖动，肉眼可辨。本轮改字节 | `82110d66080079d45685eaeb4822cb832de5ae8953ac4dbf170e9faac26f3c0b` |
| `decor--shelf-gradient--mid--full--dark.png` | PASS | dark full 相位 mid（first=0ms/mid=3000ms）；纯背景横带 10475 px 差>8、max12（整 crop max23）；差分为平滑渐变非 AA 抖动，肉眼可辨。本轮改字节 | `e177a608a9b584750367b64690050f1de1020267fe8245eede77ac370c0db013` |
| `decor--shelf-gradient--mid--full--light.png` | PASS | light full 相位 mid（first=0ms/mid=3000ms）；纯背景横带 25114 px 差>8、max14（整 crop max15）、mean7.47；差分为平滑渐变非 AA 抖动，肉眼可辨。本轮改字节 | `f97267f34dff055666d4a8c05b929a63223dff160ec911053809d093c4b2f41e` |
| `decor--shelf-gradient--static--reduce--dark.png` | PASS | dark reduce 静态对照（无动画对象）；与 mid 实帧差 light max3/dark max5，符合 crest 静态。本轮改字节（tokens/floor） | `f034f7a4d703a484a90655bcb2e9eb45430e03dbf4c351cf9c3ea7d40e86806c` |
| `decor--shelf-gradient--static--reduce--light.png` | PASS | light reduce 静态对照（无动画对象）；与 mid 实帧差 light max3/dark max5，符合 crest 静态。本轮改字节（tokens/floor） | `845e4b631962087ef6c2b584759e7f696711b2d9416c17fa6acf6aeb26aed211` |
| `pages--reader--default--full--dark.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `b583c6c40127f0771011c5a58095bd5b995a3151a95d12013c23b0df2a630381` |
| `pages--reader--default--full--light.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `a86b165e8a6baa39d39a89438a5bd1573926748e138a3d2f9fc16f4dd7101d83` |
| `pages--settings--default--full--dark.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `76e680dafdbb7fc831de461b21e6d4541817a53e7f3955d2931d6e7ff77de190` |
| `pages--settings--default--full--light.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `f56b3e2b5b3d8bd8e3c602018bab5e8b27c8057543ac31a76bde3aa63a69b50a` |
| `pages--shelf--default--full--dark.png` | PASS | 真实双主题书架页；背景渐变随 002 改字节，书卡/统计可见；本轮 sheet 实看 | `75be3b1294b7f61b48e67c237428bf5f7f9d6d441e208e661814dbaac4824426` |
| `pages--shelf--default--full--light.png` | PASS | 真实双主题书架页；背景渐变随 002 改字节，书卡/统计可见；本轮 sheet 实看 | `d82d005aa2743fd02022fb68078c722b99fdc7bae2db5fb57f5de42ed0e5901a` |
| `pages--workbench--default--full--dark.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `47bd41ff7ee547758f7c2f26a211c8db4a77f3bf8d7affed62f764901d2902d3` |
| `pages--workbench--default--full--light.png` | PASS | 真实双主题页面；本轮改字节与旧图 diff 仅顶部导航按钮区域（bbox 13,4–348,31）；内容真实。本轮 sheet 实看 | `9a44fcc96f7f2709f00124f9ed5f98eeb5d31caa4793b5c0f85fbca1b9440b22` |
| `shell--nav-rail--collapsed-1280--full--dark.png` | PASS | 新增：点击顶部“导航”后 rail 隐藏不占位、内容左移，Workbench→Library 跨页保持折叠；状态条 Compact。dark | `10f78d37500a627d0eb3d47f53ddd329663e549746ac35746fc2647406888734` |
| `shell--nav-rail--collapsed-1280--full--light.png` | PASS | 新增：点击顶部“导航”后 rail 隐藏不占位、内容左移，Workbench→Library 跨页保持折叠；状态条 Compact。light | `c18af4d233c6af1a1bd077209b5f2163c800316e0e3891ef39dd75dbb055b5e4` |
| `shell--status-band--error-1280--full--dark.png` | PASS | 新增：真实页图读取 IOException（页内错误提示，状态条红色 `错误 · 页面读取失败（IOException）…`，实际 #A1432D/#DB9487）。dark | `d4fd91d3ea864f01f506ecd1aba63054204972a904800f950ff6345b756da8aa` |
| `shell--status-band--error-1280--full--light.png` | PASS | 新增：真实页图读取 IOException（页内错误提示，状态条红色 `错误 · 页面读取失败（IOException）…`，实际 #A1432D/#DB9487）。light | `81b253677264b7460de1ada972263a86ac70393f32446a4c94aa713a39f52932` |
| `shell--status-band--running-1280--full--dark.png` | PASS | 新增：真实 Host 保存 await（页内“进度写回中…”，状态条蓝色 `运行中 · 正在保存阅读进度…`，实际 #396683/#86B0CB）。dark | `5fbfd830ca67ce57878fd733a925e40c40779cdfed63ad205f4b2a5f43b931d7` |
| `shell--status-band--running-1280--full--light.png` | PASS | 新增：真实 Host 保存 await（页内“进度写回中…”，状态条蓝色 `运行中 · 正在保存阅读进度…`，实际 #396683/#86B0CB）。light | `9ee323e81ba1e8e89c9f22a9c05412f213d5cc37b86e066986170dd8a4ee6a29` |
| `shell--top-nav-status--compact-1280--full--dark.png` | PASS | 新增：实际 1280=Compact，NavRail 展开，状态条右侧 `Compact · 1280–1599` 与断点一致；dark 真实主题 | `f9d3ed353477b975da0ce5d6ebda2375782f6bcdf2dfb10bd7d2c469c1065ded` |
| `shell--top-nav-status--compact-1280--full--light.png` | PASS | 新增：实际 1280=Compact，NavRail 展开，状态条右侧 `Compact · 1280–1599` 与断点一致；light 真实主题 | `f0bcdfb7da48e91641c584928a8c0e97dbd206dc1fc06ec49e98817fc225f1ef` |
| `shell--top-nav-status--full-1600--full--dark.png` | PASS | 新增：实际 1600=Full，NavRail 展开，状态条右侧 `Full · ≥1600` 与断点一致；dark 真实主题 | `d21658e04e8f2d44e8c0c233bda16698ddab30b5fd663de24ed4fc62528e41df` |
| `shell--top-nav-status--full-1600--full--light.png` | PASS | 新增：实际 1600=Full，NavRail 展开，状态条右侧 `Full · ≥1600` 与断点一致；light 真实主题 | `2c8b52d03865d651e97f9ed7eba55d72a84f25fe3055081676cc9a535a9b431f` |
| `shell--top-nav-status--medium-1024--full--dark.png` | PASS | 新增：实际 1024=Medium，NavRail 展开，状态条右侧 `Medium · 1024–1279` 与断点一致；dark 真实主题 | `d6a24a680fa4ab59537ceaf43d5286f2b83a7118a01cae0b0ce1172cfa02a60e` |
| `shell--top-nav-status--medium-1024--full--light.png` | PASS | 新增：实际 1024=Medium，NavRail 展开，状态条右侧 `Medium · 1024–1279` 与断点一致；light 真实主题 | `d0914b0e52fe0fa9b691856cfc947b0487f2dfe5e9724ecde368e26fe407fe63` |

签署合计：172 PASS / 0 REJECT / 0 NOT_RUN；172/172 有签署。旧 158 PASS 中 136 个保持同字节，6 个旧 REJECT 全部改字节或移除（见附录 E），没有旧 REJECT 字节留在集合中。

## 附录 B：无过滤全量与 57 条 skip

| 程序集 | passed | failed | skipped | total |
|---|---|---|---|---|
| NewManga.Appearance.Tests.dll | 21 | 0 | 0 | 21 |
| NewManga.Presentation.Avalonia.Tests.dll | 38 | 0 | 0 | 38 |
| NewManga.Host.Tests.dll | 51 | 0 | 28 | 79 |
| NewManga.ApplicationCore.Tests.dll | 31 | 0 | 0 | 31 |
| NewManga.CoreClient.Tests.dll | 128 | 0 | 22 | 150 |
| NewManga.ThemeEngine.Tests.dll | 253 | 0 | 0 | 253 |
| NewManga.DesignSystem.Tests.dll | 114 | 0 | 0 | 114 |
| NewManga.App.Tests.dll | 653 | 0 | 7 | 660 |
| 合计 | **1289** | **0** | **57** | **1346** |

相对用户基线 1281/0/57 = +8/0/0（+8 即新增 2 个 fact + 6 个 theory 用例）；skip 不记为 passed。57 条均为同一真实原因（缺 sidecar fixture），逐条：

| # | 测试 | 程序集 | skip 原因 |
|---|---|---|---|
| 1 | `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 2 | `NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 3 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 4 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 5 | `NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 6 | `NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 7 | `NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason` | newmanga.app.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 8 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 9 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 10 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 11 | `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 12 | `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 13 | `NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 14 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 15 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 16 | `NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 17 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 18 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 19 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 20 | `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 21 | `NewManga.CoreClient.Tests.Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 22 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 23 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 24 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 25 | `NewManga.CoreClient.Tests.CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 26 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 27 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 28 | `NewManga.CoreClient.Tests.HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 29 | `NewManga.CoreClient.Tests.SidecarFailureTests.StartupTimeout_IsTyped_NotAHang` | newmanga.coreclient.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 30 | `NewManga.Host.Tests.CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 31 | `NewManga.Host.Tests.ExportE2ETests.Export_Cancel_LeavesNoArtifact` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 32 | `NewManga.Host.Tests.ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 33 | `NewManga.Host.Tests.ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 34 | `NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 35 | `NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 36 | `NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 37 | `NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 38 | `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 39 | `NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 40 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 41 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 42 | `NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 43 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 44 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 45 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 46 | `NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 47 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 48 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 49 | `NewManga.Host.Tests.HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 50 | `NewManga.Host.Tests.LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 51 | `NewManga.Host.Tests.RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 52 | `NewManga.Host.Tests.StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 53 | `NewManga.Host.Tests.StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 54 | `NewManga.Host.Tests.StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 55 | `NewManga.Host.Tests.WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 56 | `NewManga.Host.Tests.WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |
| 57 | `NewManga.Host.Tests.WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` | newmanga.host.tests | needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy) |

## 附录 C：独立生命周期 probe（未改源码）

目的：独立复现 r3 附录 C 的两个失败序列（失焦→导航→返回仍暂停；暂停中 reduce 清理），并补播放中 reduce、auto+系统关、category-off、失焦中新翻页四个组合。probe 引用固定 head 的真实 App.Tests 输出 DLL，复用既有 `Create`/`CreateWithPages`/`Motion` 测试装置，不改生产源码；首次缺 using 的编译错误已修，不计产品失败。

命令：`dotnet test <workspace>/impl-r4-review/probe/Probe.csproj --nologo --logger trx --results-directory <workspace>/impl-r4-review/probe/results`，EXIT=0：

```text
已通过! - 失败: 0，通过: 6，已跳过: 0，总计: 6 - Probe.dll (net9.0)
```

6 个场景：

| 场景 | 断言 | 结果 |
|---|---|---|
| `R2R4_004_InactiveNavigationReturn_StaysPaused` | 失焦→Workbench→Library→重新 Motion 后 IsRunning=false、PendingFrames=0、phase 保持；Activate 后恢复 | PASS |
| `R2R4_005_ReduceWhilePaused_RemovesLayerAndCannotBeRevived` | 播放 100ms→失焦→reduce：layer 立即 null；Activate+100ms PendingFrames=0 且 layer 仍 null | PASS |
| `R2R4_005_ReduceWhilePlaying_RemovesLayerAndStopsFrames` | 播放中 reduce：layer null、排空 0、Activate/新 turn 不复活 | PASS |
| `R2R4_005_AutoSystemOffWhilePlaying_RemovesLayerAndStopsFrames` | MotionResolver 系统 Reduce 下播放中切 Auto：layer null、0 帧、不复活 | PASS |
| `R2R4_005_CategoryOffWhilePlaying_RemovesLayerAndStopsFrames` | 播放中 category-off：layer null、0 帧、不复活 | PASS |
| `R2R4_004_NewTurnWhileInactive_StaysPausedUntilActivation` | 失焦中新翻页：layer 存在但 2000ms 后 0 帧、粒子 opacity 全 0；Activate 后才出现 >0.2 的粒子并在 400ms 内移除 | PASS |

完整 probe 源（为不依赖仓外路径，内联；`using` 与构建顺序见上方命令）：

```csharp
using System.Reflection;
using System.Runtime.CompilerServices;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Headless.XUnit;
using Avalonia.Threading;
using NewManga.App.Services;
using NewManga.App.Tests;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using Xunit;

[assembly: AvaloniaTestApplication(typeof(TestAppBuilder))]

// Independent probe (impl-r4 reviewer). Read-only use of the built product/test assemblies:
// it reproduces the impl-r3 appendix C failure sequences plus extra policy-switch combinations,
// and asserts on the product objects through reflection. No production source is modified.
public class R2R4LifecycleProbe
{
    private static readonly BindingFlags All = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance | BindingFlags.Static;

    private static object? Get(object o, string n) => o.GetType().GetProperty(n, All)!.GetValue(o);
    private static object Call(object o, string n, params object[] args) =>
        o.GetType().GetMethod(n, All)!.Invoke(o, args)!;

    private static void Motion(FluentShellSurface s, MotionMode mode = MotionMode.Full,
        MotionCategories categories = MotionCategories.All) =>
        typeof(FluentResidual2DecorativeTests).GetMethod("Motion", All)!.Invoke(null, new object[] { s, mode, categories });

    private static (Window Window, FluentShellSurface Surface, object Clock) Create(string factory)
    {
        var t = (ITuple)typeof(FluentResidual2DecorativeTests).GetMethod(factory, All)!.Invoke(null, null)!;
        return ((Window)t[0]!, (FluentShellSurface)t[1]!, t[2]!);
    }

    private static void Advance(object clock, double ms) => Call(clock, "Advance", ms);
    private static int PendingFrames(object clock) => (int)Get(clock, "PendingFrames")!;
    private static void Deactivate(Window w) => typeof(WindowBase).GetMethod("HandleDeactivated", All)!.Invoke(w, null);
    private static object ReaderView(FluentShellSurface s) => Get(s, "ReaderView")!;
    private static object ReaderModel(FluentShellSurface s) => Get(s, "ReaderViewModel")!;
    private static Border? Layer(FluentShellSurface s) => (Border?)Get(ReaderView(s), "DecorativeParticleLayer");
    private static object Loop(FluentShellSurface s) => Get(Get(s, "ShelfView")!, "DecorativeLoop")!;
    private static bool Running(FluentShellSurface s) => (bool)Get(Loop(s), "IsRunning")!;
    private static double Phase(FluentShellSurface s) => (double)Call(Loop(s), "Phase")!;

    private sealed class SystemMotionOff : IMotionPreferenceSource
    {
        public MotionMode? Read() => MotionMode.Reduce;
    }

    private static void ApplySystemOffReduce(FluentShellSurface s, object clock)
    {
        var settings = new MotionResolver(new SystemMotionOff()).Resolve(AppearanceDefaults.Settings with
        {
            MotionMode = MotionMode.Auto,
            MotionCategories = MotionCategories.Decorative,
        }).Settings;
        Call(ReaderView(s), "ConfigureMotion", MotionTimings.Resolve(settings), clock);
    }

    private static void LoadReader(FluentShellSurface s)
    {
        ((Task)Call(ReaderView(s), "LoadAsync", "book-1", "chapter-key", CancellationToken.None)).GetAwaiter().GetResult();
    }

    // impl-r3 appendix C, first failing scenario: deactivate -> navigate away -> return must stay paused.
    [AvaloniaFact]
    public void R2R4_004_InactiveNavigationReturn_StaysPaused()
    {
        var (window, surface, clock) = Create("Create");
        try
        {
            Motion(surface);
            Assert.True(Running(surface));
            Advance(clock, 1000);
            var phase = Phase(surface);
            Deactivate(window);
            Assert.False(Running(surface));
            surface.Navigate(FluentPage.Workbench); Dispatcher.UIThread.RunJobs();
            surface.Navigate(FluentPage.Library); Dispatcher.UIThread.RunJobs();
            Motion(surface); // reconfigure while the real window stays inactive
            Advance(clock, 1000);
            Assert.False(Running(surface));
            Assert.Equal(0, PendingFrames(clock));
            Assert.Equal(phase, Phase(surface), 5);
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Assert.True(Running(surface));
            Assert.Equal(phase, Phase(surface), 5);
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }

    // impl-r3 appendix C, second failing scenario: reduce while paused must remove the layer and stop frames.
    [AvaloniaFact]
    public void R2R4_005_ReduceWhilePaused_RemovesLayerAndCannotBeRevived()
    {
        var (window, surface, clock) = Create("CreateWithPages");
        try
        {
            Motion(surface);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            LoadReader(surface);
            ((Task)Call(ReaderModel(surface), "NavigateAsync", 1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Assert.NotNull(Layer(surface));
            Deactivate(window);
            Advance(clock, 0);
            Motion(surface, MotionMode.Reduce);
            Assert.Null(Layer(surface));
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Assert.Equal(0, PendingFrames(clock));
            Assert.Null(Layer(surface));
            Advance(clock, 1000);
            Assert.Null(Layer(surface));
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }

    // reduce while the particles are actually playing (not paused).
    [AvaloniaFact]
    public void R2R4_005_ReduceWhilePlaying_RemovesLayerAndStopsFrames()
    {
        var (window, surface, clock) = Create("CreateWithPages");
        try
        {
            Motion(surface);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            LoadReader(surface);
            ((Task)Call(ReaderModel(surface), "NavigateAsync", 1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Assert.NotNull(Layer(surface));
            Motion(surface, MotionMode.Reduce);
            Assert.Null(Layer(surface));
            Advance(clock, 0);
            Assert.Equal(0, PendingFrames(clock));
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Advance(clock, 400);
            Assert.Null(Layer(surface));
            ((Task)Call(ReaderModel(surface), "NavigateAsync", -1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 400);
            Assert.Null(Layer(surface));
            Assert.Equal(0, PendingFrames(clock));
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }

    // auto + system reduce while playing, using the real MotionResolver path.
    [AvaloniaFact]
    public void R2R4_005_AutoSystemOffWhilePlaying_RemovesLayerAndStopsFrames()
    {
        var (window, surface, clock) = Create("CreateWithPages");
        try
        {
            Motion(surface);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            LoadReader(surface);
            ((Task)Call(ReaderModel(surface), "NavigateAsync", 1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Assert.NotNull(Layer(surface));
            ApplySystemOffReduce(surface, clock);
            Assert.Null(Layer(surface));
            Advance(clock, 0);
            Assert.Equal(0, PendingFrames(clock));
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Advance(clock, 1000);
            Assert.Null(Layer(surface));
            Assert.Equal(0, PendingFrames(clock));
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }

    // category-off while playing.
    [AvaloniaFact]
    public void R2R4_005_CategoryOffWhilePlaying_RemovesLayerAndStopsFrames()
    {
        var (window, surface, clock) = Create("CreateWithPages");
        try
        {
            Motion(surface);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            LoadReader(surface);
            ((Task)Call(ReaderModel(surface), "NavigateAsync", 1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Assert.NotNull(Layer(surface));
            Motion(surface, MotionMode.Full, MotionCategories.Navigation | MotionCategories.Feedback);
            Assert.Null(Layer(surface));
            Advance(clock, 0);
            Assert.Equal(0, PendingFrames(clock));
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Advance(clock, 1000);
            Assert.Null(Layer(surface));
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }

    // particles created after a page turn while the window is already inactive must stay paused,
    // then run from the start on activation.
    [AvaloniaFact]
    public void R2R4_004_NewTurnWhileInactive_StaysPausedUntilActivation()
    {
        var (window, surface, clock) = Create("CreateWithPages");
        try
        {
            Motion(surface);
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            LoadReader(surface);
            ((Task)Call(ReaderModel(surface), "NavigateAsync", 1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            Advance(clock, 100);
            Deactivate(window);
            surface.Navigate(FluentPage.Workbench); Dispatcher.UIThread.RunJobs();
            surface.Navigate(FluentPage.Reader); Dispatcher.UIThread.RunJobs();
            ((Task)Call(ReaderModel(surface), "NavigateAsync", -1, CancellationToken.None)).GetAwaiter().GetResult();
            Dispatcher.UIThread.RunJobs();
            var layer = Layer(surface);
            Assert.NotNull(layer);
            Advance(clock, 2000);
            Assert.Equal(0, PendingFrames(clock));
            var canvas = (Canvas)layer.Child!;
            Assert.All(canvas.Children, dot => Assert.Equal(0, dot.Opacity));
            window.Activate(); Dispatcher.UIThread.RunJobs();
            Advance(clock, 200);
            Assert.Contains(canvas.Children, dot => dot.Opacity > .2);
            Advance(clock, 400);
            Assert.Null(Layer(surface));
            Assert.Equal(0, PendingFrames(clock));
        }
        finally { window.Close(); Dispatcher.UIThread.RunJobs(); }
    }
}

```

## 附录 D：旧 FEA-06 四 PNG SHA

| 文件 | SHA256 |
|---|---|
| reader.png | `8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2` |
| settings.png | `fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162` |
| shelf.png | `307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a` |
| workbench.png | `d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5` |

本机实测与 Task 基线一致，`verification/FEA-06/**` 相对 base 零 diff。

## 附录 E：172 图与 136/24/12/4 的独立核对

本机 SHA 清单与 inventory 172 行一一对应，172 唯一 SHA；raster 尺寸/主题/模式/viewport/EXIT 全部一致；86 light + 86 dark，168 full + 4 reduce；capture head 全为 17a26d552。相对 445afc0ac：

- 同字节 **136**（全部旧 PASS）
- 同名改字节 **24**（其中 4 个是旧 REJECT 的改字节处置；另 2 个旧 REJECT 以移除处置）
- 新增 **12**：6 个 shell 状态（nav-rail collapsed / status-band running / error ×2 主题）+ 6 个宽度标签（medium-1024 / compact-1280 / full-1600 ×2 主题）
- 移除 **4**：旧误标 `shell--top-nav-status--compact--full--{dark,light}.png`（实为 Medium）与 `shell--top-nav-status--default--full--{dark,light}.png`（标签被宽度帧取代）

24 个改字节文件：

- `components--command-palette--empty--full--dark.png`
- `components--command-palette--empty--full--light.png`
- `components--command-palette--result--full--dark.png`
- `components--command-palette--result--full--light.png`
- `components--danger-button--pressed--full--dark.png`
- `components--danger-button--pressed--full--light.png`
- `decor--page-turn-particles--mid--full--dark.png`
- `decor--page-turn-particles--mid--full--light.png`
- `decor--page-turn-particles--none--reduce--dark.png`
- `decor--page-turn-particles--none--reduce--light.png`
- `decor--shelf-gradient--first--full--dark.png`
- `decor--shelf-gradient--first--full--light.png`
- `decor--shelf-gradient--mid--full--dark.png`
- `decor--shelf-gradient--mid--full--light.png`
- `decor--shelf-gradient--static--reduce--dark.png`
- `decor--shelf-gradient--static--reduce--light.png`
- `pages--reader--default--full--dark.png`
- `pages--reader--default--full--light.png`
- `pages--settings--default--full--dark.png`
- `pages--settings--default--full--light.png`
- `pages--shelf--default--full--dark.png`
- `pages--shelf--default--full--light.png`
- `pages--workbench--default--full--dark.png`
- `pages--workbench--default--full--light.png`

12 个新增文件：

- `shell--nav-rail--collapsed-1280--full--dark.png`
- `shell--nav-rail--collapsed-1280--full--light.png`
- `shell--status-band--error-1280--full--dark.png`
- `shell--status-band--error-1280--full--light.png`
- `shell--status-band--running-1280--full--dark.png`
- `shell--status-band--running-1280--full--light.png`
- `shell--top-nav-status--compact-1280--full--dark.png`
- `shell--top-nav-status--compact-1280--full--light.png`
- `shell--top-nav-status--full-1600--full--dark.png`
- `shell--top-nav-status--full-1600--full--light.png`
- `shell--top-nav-status--medium-1024--full--dark.png`
- `shell--top-nav-status--medium-1024--full--light.png`

4 个移除文件：

- `shell--top-nav-status--compact--full--dark.png`
- `shell--top-nav-status--compact--full--light.png`
- `shell--top-nav-status--default--full--dark.png`
- `shell--top-nav-status--default--full--light.png`

旧 impl-r3 的 6 个 REJECT SHA（danger pressed 2、gradient first/mid light 2、shell compact 2）逐一核对：4 个以改字节处置、2 个以移除处置；**新集合中不存在任何旧 REJECT SHA**。固定 head（17a26d552）副本重捕获的 172 图与原仓逐字节相同，status 变更恰好 24 M + 12 ?? + 4 D + inventory M = 41，全部在 `verification/FEA-06-RESIDUAL-2/visuals/`；这同时独立复核了“opt-in 仅本卡 visuals”和“172 图可从该 head 复现”。
