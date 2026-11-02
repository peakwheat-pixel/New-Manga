---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh session，独立上下文 Reviewer）
reviewer_kind: agent
author: ZCode CLI / DSH / Codex CLI 实现会话
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: 13a67e75f74b6fd881766552d5987e398f54aeda
implementation_head: fcf28bdfce642510c875b854f85497cccaa7b2b4
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 1
p2: 0
provenance:
  agent: Codex CLI
  session_id: 01a19d66-0415-7f61-bfd3-a8633e25fe44
  appointment: 用户 impl-r3 fresh-session Prompt；Task reviewer 与 checkpoint 第115节（job pwsh-95997fbd615d4902）
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-1 impl-r3

**changes_requested：P0=0 / P1=1 / P2=0。** R2-001/002/004/005/006 的指定反例已有有效修复；R2-003 的四类输入 deadline 重置也通过，但新增 press 唤醒破坏了“点击中部切换显隐”的反向分支：工具条隐藏后，同位置再次点击始终隐藏。full/reduce 两态均以真实 MouseDown/MouseUp、实际图片命中复现（R3-001）。

四条验收命令均 EXIT=0，无过滤全量为 **1233 passed / 0 failed / 57 skipped（总1290）**。测试通过不能证明未覆盖的反向交互或完整 AC 达成。本报告不批准 D-8 暂缓，也不将 I-4 未测格、B-1…B-7 或原生验收视为完成。

## 范围与依据

工作路径 G:\CODEX\New Manga，branch=main，Git common directory=.git，原 Task base 为上述82529a3d。首次读取时 HEAD=fcf28bdfc，Task/checkpoint 有他人未提交变更；其后外部文档提交13a67e75f落地。已核对 fcf28bdfc→13a67e75f **仅改 Task/checkpoint 两文件**，将后者固定为 reviewed_head；生产、测试和 verification 与 fcf28bdfc 一致。没有恢复、暂存或覆盖他人修改。

已读 AD-002 当前架构、STATUS/PLAN 当前 DAG、Task 范围v3/AC/禁止路径/Review Appointment/Canonical Evidence/D-8、rolling checkpoint 第113–115节；impl-r2 全文（R2-001…006 与附录复现）、impl-r2-rework Handoff 和完整验证日志；fluent-v1 的01 §2.3、02全文、03焦点/高对比、07 Reader、08设置、10组件/动效相关要求。审阅 eaf7b74d8→fcf28bdfc 全部23文件 diff，并核对 base→head 的66文件范围、受影响调用链及新增/修改测试。没有以 Handoff 自述代替源码和实际执行。

采用项目 REVIEW 模板；该模板依用户2026-09-18裁决取消 code-review 双子代理强制项，本轮无子代理。当前会话未参与该 Task 实现/返修。唯一持久交付为本文件；未 commit/push，未修改源码、Task 或既有证据。

## Architecture（executed）

新增 FluentVisibilityMotion 分离逻辑关闭与视觉退出，复用 FluentFrameAnimation 的单调时钟、有限帧插值和取消代次；detach 调用 Finish，取消后的旧帧不再更新。FluentMotionScope 是 Fluent 树内可继承配置，控件加入逻辑/模板树时取得当前 feedback；ConditionalWeakTable 不建立静态强持有控件链。没有新增循环计时器、后台动画任务或持久化路径；Reader 既有 DispatcherTimer 在 detach 停止并清 deadline。

Appearance.Changed 的后台回调在 UI 队列执行前复查订阅、attach generation、视觉挂载；detach/reattach 后旧代次失效。UI 同步分支在 UI 线程执行；UI 属性更新未迁移到工作线程。测试实际通过后台 SaveAsync（隔离临时根）触发 Changed，不只是直接调用处理器。

共享 FocusRing 的 Offset 默认0，只由 Fluent 根绑定现有 Nm.Focus.Ring.Offset=1；Current 默认几何保留。新增共享属性没有更改 Host/IPC/Schema/契约或依赖。禁止路径审计覆盖 Core、契约/冻结设计/生成物、Host/CoreClient/Presentation、Current V2、Shell/组合根/FrontendSelector；相对 Task base **零 diff**。

**Architecture 结论：** 在记录范围内未发现分层、数据保护、线程或生命周期新增阻断；输入事件组合存在产品行为回归，见 R3-001。事件订阅/代次与静态持有链检查不等于完成长时间原生内存 profiling（NOT_RUN）。

## Standards（executed）

符合本 Task 写域和“源文件/旧证据保全、不 push”的边界；没有引入依赖或许可材料。原测试方法名相对 base 保留933个、相对eaf7b74d8保留996个，missing=0；这是名称保留审计，不等于断言语义等价。修改的旧 Reader 用例从仅检查 Transition 配置升级为中间 Opacity 与瞬时降级，未据此删除原侧栏/reduce语义；Workbench用例增加动态重建后的实际 hover 断言。

本次增量 git diff --check 报既有 impl-r2.md:392 EOF空行（EXIT=2），该历史报告保持原字节，不作为产品 finding。未发现需要另列的硬性标准违规或可操作 smell finding。

## Spec（executed）：逐 R2 核验

| 原 finding | 本轮结论 | 源码与实际证据 | 仍需区分的限制 |
|---|---|---|---|
| R2-001 | 原反例 FIXED | Reader 顶/底以 FluentVisibilityMotion 实际改 Opacity，160ms后才隐藏；R2001 测80/159/160ms及唤醒取消。Settings离开/普通确认、Shelf对话框/抽屉四路测100/199/200ms进入、80/159/160ms退出、scrim160ms；full→reduce、navigation关闭均即时收敛。Reader按 Navigation 而非全局 Enabled 降级；FluentMotionScope/FeedbackMotion消费 SplineEasing(.4,0,.2,1)。附录B生产帧源另见中间值。 | 仅消费点和记录场景通过，不据此将D-8本体、未覆盖反馈状态或原生视觉签为完成。 |
| R2-002 | 原反例 FIXED | 继承 Configuration 在新控件进入树时配置120ms BrushTransition与90ms pressed；shell输入兜底用同配置。R2002测试 Providers→hover/pressed→feedback关→Backup重建→缓存页回full→Providers再建；WorkbenchDraftEdit另测投影重建→reduce→重建→full→再重建。真实指针/键盘、30ms RGB中间值按冻结曲线计算，非仅检查Transitions非空。 | I-4其他状态格继续NOT_RUN；不是动态按钮原反例仍失败。 |
| R2-003 | deadline原反例 FIXED，交互整体仍 PARTIAL | R2003四路真实press/release/wheel/被shell消费Ctrl+K，于1500ms输入把deadline改为3500ms，2000/3499保持、3500隐藏；detach停止并清空。附录B真实主循环于约1500ms点击后2378ms仍显示。 | 新press tunnel先强制显现，再由中部handler切换，导致隐藏→显示失败（R3-001）；现有中心测试只覆盖显示→隐藏。 |
| R2-004 | 原反例 FIXED | OnAppearanceChangedForMotion捕获generation，Post执行复查；R2004后台真实Changed→detach→pump不替换Transitions，快速reattach应用当前值且订阅数为1；重复attach仍1，detach为0。 | 未进行原生长时泄漏profiler，不以此推断其他长期资源验收。 |
| R2-005 | 原证据口径问题 FIXED | AC/子项/矩阵/batch-b均追加“当前快照”明确取代旧口径；head=8b39b1398，当前1233/0/57，对照历史1213/0/57，差值App+16/DS+4。四命令/EXIT及57条完整名称与逐条fixture原因齐全；只读脚本实跑PASS，原字节13/13保留。 | D-8=PENDING_DISPOSITION、I-4普通可测缺口与原生NOT_RUN分列。Task旧Canonical Evidence仍是历史pin，DSH尚需登记当前证据；不把机械PASS理解为最新指针已完成或R3无反例。 |
| R2-006 | 原offset反例 FIXED | FocusRingOffsetTests四项实跑覆盖标准/高对比2→3→2、不重聚焦、四边gap=1、外宽高=控件+2*(stroke+offset)、滚动仅gap被裁剪时隐藏/恢复；Current offset=0几何对照。R2006另验Fluent继承1、Current树0、返回Fluent1。 | 原生200%DPI/像素和完整Tab遍历NOT_RUN；不据stroke测试或单次截图签全I-11。 |

## Findings

以下行号对应 reviewed_head。源码路径相对 apps/desktop-avalonia/。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 对应 AC | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|---|
| R3-001 | P1 | src/NewManga.App/Views/Fluent/ReaderPageView.cs:100、223、93、143；tests/NewManga.App.Tests/FluentR2ReworkTests.cs:401 | 新 PointerPressed tunnel无条件 NotifyInteraction(reveal=true)。隐藏状态在目标中部处理前被Poke为true，随后ToggleToolBars又设false，所以鼠标不移动的第二/第三次中部点击无法重新显示工具条；触摸中部唤回也落在同样事件顺序。违反I-10“点击中部切换显隐”。 | 附录A：载入FakeHost一页真实图片，固定同一坐标，每次onPage=True；Full和Reduce均click1=True→False，click2/3=False→False，Down/Up后均false。使用真实MouseDown/MouseUp，不是直接调用HandleReadingAreaTap；现有新增中心用例只断言第一次隐藏，因而1233通过未识别该反向分支。 | AC1 / I-10；设计07:23；R2-003返修的交互语义保持 | 将“续2s deadline”与“中部切换/普通输入唤醒”协调：中部按下根据事件开始前状态切换一次，释放只续时，其他控件按下/wheel/handled键仍唤醒并续时。补同坐标连续两次点击及已自动隐藏后的点击、full/reduce/navigation-off回归，验证双向显隐、2s和detach；不要用测试前Poke掩盖。 | open；8b39b1398引入，尚无返修 |

## 验证（executed）

环境：Microsoft Windows NT10.0.26300.0；PowerShell Core7.6.8，EXE=C:\Program Files\PowerShell\7\pwsh.exe；dotnet SDK10.0.401，目标net9.0，Avalonia11.3.22；VIRTUAL_ENV未设置（本轮未运行Python业务环境）。NEWMANGA_CORECLIENT_SIDECAR_DIR、NEWMANGA_CAPTURE_FLUENT_PNGS、NEWMANGA_EVIDENCE_SYNC均未设置。测试使用既有隔离临时根；内存探针只构造不存在临时路径的AppearanceStore，不保存、不写PNG/真实APPDATA。Add-Type运行于PowerShell .NET10宿主，不替代net9.0 VSTest。

所有验收均在固定13a67e75f生产/测试字节上执行；检查显示其与fcf28bdfc一致。首轮全量输出在工具展示中被截断，另一次同命令复跑用于补齐可持久化的原始计数/skip清单；不是新增通过项，不叠加两次计数。

| 场景 | 实际命令/步骤 | 结果 | 输出/EXIT |
|---|---|---|---|
| 构建 | dotnet build apps\desktop-avalonia\NewManga.sln --nologo | PASS | 0 warnings / 0 errors；BUILD_EXIT=0 |
| 全量，无过滤 | dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo | PASS（现有断言） | 1233/0/57，总1290；TEST_EXIT=0；逐程序集原始输出见附录C |
| 治理 | pwsh -NoProfile -File tools\governance\check.ps1 | PASS | CHECK_EXIT=0，3既有warnings：9非终态Task、STATUS/PLAN预算80% |
| 冻结契约pin | pwsh -NoProfile -File tools\governance\verify_pins.ps1 | PASS | PINS_EXIT=0，15/15 |
| TokenGen | dotnet apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen/bin/Debug/net9.0/NewManga.DesignSystem.TokenGen.dll --check | PASS | 292rows，byte-for-byte up-to-date；TOKENGEN_EXIT=0 |
| ThemeGen | dotnet apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen/bin/Debug/net9.0/NewManga.ThemeEngine.ThemeGen.dll --check | PASS | newmanga-default1.0.0，up-to-date；THEMEGEN_EXIT=0 |
| 当前证据/历史 | python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py | PASS | EVIDENCE_EXIT=0；raw13/13、57逐条原因、当前四表与历史前缀一致；另以Task原base直接比四PNG |
| R2行为回归 | 全量内FluentR2ReworkTests/FluentAnimationCompletionTests/FocusRingOffsetTests及既有Current对照 | PASS（记录场景） | 时长边界、颜色/缩放中间值、重建、分类、deadline、代次与焦点几何均通过；不声称未测分支通过 |
| 中部双向点击 | 附录A内存探针 | FAIL（产品行为） | full/reduce连续同位置真实点击均无法隐藏→显示；探针执行PROBE_EXIT=0 |
| 生产帧源 | 附录B内存探针输出 | PASS（记录场景） | 实际FluentRenderClock下对话框/抽屉/Reader出现中间Opacity并收敛；运行中reduce及navigation-off即时；PROBE_EXIT=0 |
| 原测试保留 | 比较base/eaf7b74d8的测试方法名与现文件，检查改动断言 | PASS（名称与所读断言） | 933/996均missing=0；R2比R1通过数+20，skip不增，不能据名称审计宣称全部测试语义等价 |
| 禁止范围 | base→head路径审计、reviewed bytes工作树对照 | PASS | 66变更文件，无禁止路径；git diff --quiet fcf28bdfc -- apps verification doc/design EXIT=0 |
| 旧Review/PNG | 原Review引入commit对照；Task原base四PNG原始blob逐字节比较 | PASS | 旧r1/r2零diff；SHA见附录D |
| 原生验收/采证 | 本轮未进行原生200%DPI、a11y、逐像素视觉/完整Tab遍历、PNG opt-in | NOT_RUN / BLOCKED | B-5硬件/书面waiver前置保持；其他普通headless可测缺口另见当前矩阵 |
| 增量空白检查 | git diff --check eaf7b74d8 fcf28bdfc | FAIL（历史文档格式） | EXIT=2；仅既有impl-r2.md:392 EOF空行，保持历史字节 |

### AC 当前判断（不修改 Task）

| AC | 结论与原因 |
|---|---|
| AC1 | PARTIAL：I-10双向中部切换失败；B-1/B-2/B-3/B-6/B-7继续按依赖BLOCKED，未造数据完成。 |
| AC2 | PARTIAL：记录的R2动效/重建/焦点反例已修；I-4剩余有效属性格及完整Tab遍历NOT_RUN，I-5 decorative本体仍D-8未裁决，B-5原生a11y仍BLOCKED。 |
| AC3 | 本轮IN范围已有三分支/保存失败/退出保护断言通过；完整AC仍有B-4数据面限制。 |
| AC4 | 默认PNG保护、既有拆分/阴影/Current对照证据和回归通过；本轮opt-in与原生视觉NOT_RUN。 |
| AC5 | 当前计数/表/日志及机械检查通过；新P1待处置，DSH当前证据登记和集成验证待完成，不能据检查器PASS关闭。 |

**Verification 结论：** 四验收、现有断言与保全检查通过；新增真实反向交互反例失败。1233通过不覆盖R3-001，不授权关闭全部AC。未把已登记NOT_RUN或D-8另计成新的重复finding，也未豁免它们。

## 结论与复审

固定head verdict=changes_requested；不得作为已批准实现交DSH集成。DSH处置R3-001并冻结返修范围后，由实现Owner修复、提供新固定commit/回归/Handoff，再Appointment fresh Reviewer。当前Reviewer不得参与此finding实现或返修；不释放下一节点、不关闭Task、不push。

推荐下一切片：Task=FEA-06-RESIDUAL-1，R3 findings处置；Agent=DSH，启动条件=接收本报告，无须重新取得实现授权即可先完成文档处置。恢复点=G:\CODEX\New Manga，main，同一worktree，base=82529a3d5864a39f362e414b67bca774d743f862，reviewed_head=13a67e75f74b6fd881766552d5987e398f54aeda，源码交付fcf28bdfc。允许写域、最终Owner与后续Review由DSH登记；建议ZCode负责Fluent输入返修。Core/契约/schema/依赖/生成物/冻结设计/Current V2/组合根/FEA-07 seam继续禁止，无需新增共享接口。

可直接转发给DSH：

> 在G:\CODEX\New Manga的main接收FEA-06-RESIDUAL-1 impl-r3报告doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md；base=82529a3d5864a39f362e414b67bca774d743f862，reviewed_head=13a67e75f74b6fd881766552d5987e398f54aeda（源码fcf28bdfc）。先核对HEAD/工作树，处置R3-001（P0=0/P1=1/P2=0），在Task/STATUS冻结Reader输入语义返修范围与Owner；建议派ZCode修改授权Fluent Reader视图及App测试，保护中部双向切换和所有输入deadline，禁止Core/契约/schema/依赖/生成物/冻结设计/Current/组合根/FEA-07 seam变更。交付固定commit、Handoff与追加verification，补真实同位置连续点击、自动隐藏后点击、full/reduce/navigation-off、2s/deadline/detach回归。复跑本报告附录A、四条验收命令、两生成器与只读证据检查，记录shell/命令/EXIT/单次计数/57条skip原因及旧PNG与历史字节保全；1233/0/57基线只增不减。保留I-4 NOT_RUN、D-8待裁决及B-1…B-7，更新当前证据pin但不覆盖历史报告。返修后Appointment独立上下文Reviewer，再由DSH集成验证；通过前不关闭Task、不释放新节点、不push。

## 附录A：R3-001 完整复现探针

在仓库根目录的新PowerShell7进程执行。引用历史报告中已固定的程序集加载头；Add-Type只在内存编译，FakeHost一页图片，不保存设置/PNG。固定同一指针位置；每次打印目标仍命中PageSurface或其后代，排除遮挡/空点。两次点击之间等待300ms，让160ms退出完成；不插入MouseMove或Poke。进入下一mode前Poke仅用于重置该mode的初始显示状态。

```powershell
$ErrorActionPreference='Stop'
$reviewDoc=Get-Content -Raw doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md
$reviewPart=$reviewDoc.Substring($reviewDoc.IndexOf('## 附录 A：'))
$reviewBlock=[regex]::Match($reviewPart,'(?s)```powershell\r?\n(.*?)\r?\n```').Groups[1].Value
$reviewHeader=$reviewBlock.Substring(0,$reviewBlock.IndexOf('Add-Type'))
Invoke-Expression $reviewHeader
Add-Type -CompilerOptions '/nowarn:1701' -ReferencedAssemblies $reviewRefs -TypeDefinition @'
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Input;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Tests;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
public static class R3CenterProbe {
 static void Pump(int ms=0){var t=Stopwatch.StartNew();do{Thread.Sleep(2);AvaloniaHeadlessPlatform.ForceRenderTimerTick();Dispatcher.UIThread.RunJobs();}while(t.ElapsedMilliseconds<ms);}
 static void Motion(FluentShellSurface s,MotionMode m)=>typeof(FluentShellSurface).GetMethod("ApplyMotion",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(s,new object[]{AppearanceDefaults.Settings with {MotionMode=m}});
 public static void Run(){
 TestAppBuilder.BuildAvaloniaApp().SetupWithoutStarting();
 using var theme=new DesignSystemThemeManager(Application.Current);theme.Initialize();
 var host=new FakeHostController(FakeHostController.ReadySnapshot());
 var png=Convert.FromBase64String("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==");
 host.ReaderBooksByChapterId["chapter-key"]=new ReaderBookData("book-1","Sample","chapter-key","Chapter","fit-page",new[]{new ReaderPageData("page-1",0,1,1,_=>Task.FromResult<byte[]>(png))});
 var a=new AppearanceCoordinator(new AppearanceStore(Path.Combine(Path.GetTempPath(),"nm-r3-nonexistent-"+Guid.NewGuid(),"appearance.json")));
 var s=new FluentShellSurface(host:host,appearance:a,themeManager:theme);
 var w=new Window{Width=1280,Height=900,Content=s};w.Show();
 s.Navigate(FluentPage.Reader);s.ReaderView.LoadAsync("book-1","chapter-key").GetAwaiter().GetResult();s.ReaderViewModel.IsSideRailVisible=false;
 var page=s.ReaderView.PageSurface;page.Height=400;Pump(300);w.UpdateLayout();
 var p=page.TranslatePoint(new Point(page.Bounds.Width/2,page.Bounds.Height/2),w).Value;
 w.MouseMove(p,RawInputModifiers.None);
 foreach(var mode in new[]{MotionMode.Full,MotionMode.Reduce}){
 Motion(s,mode);s.ReaderViewModel.PokeToolBars();Pump(20);
 for(var i=1;i<=3;i++){
 var hit=w.InputHitTest(p) as Visual;
 var onPage=ReferenceEquals(hit,page)||(hit!=null&&hit.GetVisualAncestors().Contains(page));
 var before=s.ReaderViewModel.AreToolBarsVisible;
 w.MouseDown(p,MouseButton.Left,RawInputModifiers.None);
 var afterDown=s.ReaderViewModel.AreToolBarsVisible;
 w.MouseUp(p,MouseButton.Left,RawInputModifiers.None);
 Console.WriteLine("CENTER mode="+mode+" click="+i+" onPage="+onPage+" before="+before+" down="+afterDown+" up="+s.ReaderViewModel.AreToolBarsVisible);
 Pump(300);
 }
 }
 w.Close();Console.WriteLine("R3_CENTER_PROBE_COMPLETE");
 }
}
'@
[R3CenterProbe]::Run()
Write-Output 'PROBE_EXIT=0'
```

实际输出：

```text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
HEAD=13a67e75f74b6fd881766552d5987e398f54aeda
CENTER mode=Full click=1 onPage=True before=True down=False up=False
CENTER mode=Full click=2 onPage=True before=False down=False up=False
CENTER mode=Full click=3 onPage=True before=False down=False up=False
CENTER mode=Reduce click=1 onPage=True before=True down=False up=False
CENTER mode=Reduce click=2 onPage=True before=False down=False up=False
CENTER mode=Reduce click=3 onPage=True before=False down=False up=False
R3_CENTER_PROBE_COMPLETE
PROBE_EXIT=0
```

预期每态连续三次为 True→False→True→False；实际第二、三次均 False→False。R3-001的根因由PointerPressed路由顺序与上述源码位置交叉证明，探针EXIT=0只说明成功执行。

## 附录B：独立生产帧源补查

另一次内存探针使用同历史程序集加载头、真实FluentShellSurface/FakeHost/AppearanceCoordinator/DesignSystemThemeManager；未设置MotionClock，使用生产FluentRenderClock。Pump循环以Stopwatch、ForceRenderTimerTick、Dispatcher.UIThread.RunJobs推进UI，记录运行后Opacity，未写PNG或设置。

步骤：ShelfView.ShowNewBookDialog→采样→真实取消Click事件→采样；OpenRecycleDrawer进入中切reduce；Navigate(Reader)→HideToolBarsAfterIdle→采样→Full/Feedback-only关闭navigation；回full后聚焦“切换单页或双页”，MouseMove到按钮，Dispatcher.UIThread.MainLoop约1500ms，再真实MouseDown/Up，MainLoop约750ms检查（没有直接调用CheckIdleDeadline）。输出如下；MID是采样标签，实际UI渲染耗时会超过请求Pump时长，不据该采样倒推出精确160/200ms边界，精确边界由全量内手动帧源测试独立覆盖。

```text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
HEAD=13a67e75f74b6fd881766552d5987e398f54aeda
PROD_DIALOG_ENTER_0 visible=True opacity=0.00000 hit=True
PROD_DIALOG_ENTER_MID visible=True opacity=0.97553 hit=True
PROD_DIALOG_ENTER_END visible=True opacity=1.00000 hit=True
PROD_DIALOG_EXIT_0 visible=True opacity=1.00000 hit=False
PROD_DIALOG_EXIT_MID visible=True opacity=0.33435 hit=False
PROD_DIALOG_EXIT_END visible=False opacity=0.00000 hit=False
PROD_DRAWER_ENTER_MID visible=True opacity=0.96035 hit=True
REDUCE_DURING_ENTER visible=True opacity=1.00000 hit=True
REDUCE_DRAWER_EXIT visible=False opacity=0.00000 hit=False
PROD_READER_EXIT_MID visible=True opacity=0.30532 hit=False
PROD_READER_EXIT_END visible=False opacity=0.00000 hit=False
NAV_OFF_READER visible=False opacity=0.00000 hit=False
REAL_CLICK_AFTER_MS=2378 visible=True
R3_PROBE_COMPLETE
PROBE_EXIT=0
```

## 附录C：本轮验收日志与57条skip

下列为实际控制台关键输出；不是复用实施者的计数。第二次全量实际SKIP完整名称集合与返修日志57条原因精确相同（57/57，集合比较），再核对当前SidecarFixture.TryGetSidecarDirectory及App/Host包装attribute：环境变量为空时逐条reason一致。没有启用sidecar fixture，未声称这些场景通过。

```text
SHELL=Core 7.6.8
EXE=C:\Program Files\PowerShell\7\pwsh.exe
OS=Microsoft Windows NT 10.0.26300.0
DOTNET_SDK=10.0.401; TARGET=net9.0
VIRTUAL_ENV_SET=False
HEAD=13a67e75f74b6fd881766552d5987e398f54aeda
NEWMANGA_CORECLIENT_SIDECAR_DIR_SET=False
NEWMANGA_CAPTURE_FLUENT_PNGS_SET=False
NEWMANGA_EVIDENCE_SYNC_SET=False
COMMAND: dotnet build apps\desktop-avalonia\NewManga.sln --nologo
已成功生成。
    0 个警告
    0 个错误
BUILD_EXIT=0
COMMAND: dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo
已通过! - 失败:     0，通过:    21，已跳过:     0，总计:    21，持续时间: 41 ms - NewManga.Appearance.Tests.dll (net9.0)
已通过! - 失败:     0，通过:    38，已跳过:     0，总计:    38，持续时间: 302 ms - NewManga.Presentation.Avalonia.Tests.dll (net9.0)
已通过! - 失败:     0，通过:    51，已跳过:    28，总计:    79，持续时间: 624 ms - NewManga.Host.Tests.dll (net9.0)
已通过! - 失败:     0，通过:   253，已跳过:     0，总计:   253，持续时间: 718 ms - NewManga.ThemeEngine.Tests.dll (net9.0)
已通过! - 失败:     0，通过:    97，已跳过:     0，总计:    97，持续时间: 1 s - NewManga.DesignSystem.Tests.dll (net9.0)
已通过! - 失败:     0，通过:    31，已跳过:     0，总计:    31，持续时间: 4 s - NewManga.ApplicationCore.Tests.dll (net9.0)
已通过! - 失败:     0，通过:   128，已跳过:    22，总计:   150，持续时间: 22 s - NewManga.CoreClient.Tests.dll (net9.0)
已通过! - 失败:     0，通过:   614，已跳过:     7，总计:   621，持续时间: 1 m 41 s - NewManga.App.Tests.dll (net9.0)
TEST_EXIT=0
TOTAL=1233 passed / 0 failed / 57 skipped (1290 total)
PREVIOUS=1213/0/57; DELTA=App+16, DesignSystem+4
COMMAND: pwsh -NoProfile -File tools\governance\check.ps1
Governance scope: 15 current documents; no historical directory scan.
Task: doc\tasks\FEA-06-RESIDUAL-1.md
WARN: 存在 9 个非终态 Task（见 TASK_LEDGER）；状态字段不能证明活性，不得据此批量关闭（r38）
WARN: doc/STATUS.md 已达到预算的 80%：3197 bytes / 29 lines
WARN: doc/REBASELINE_PLAN.md 已达到预算的 80%：5068 bytes / 64 lines
Governance check: PASS (3 warnings)
CHECK_EXIT=0
COMMAND: pwsh -NoProfile -File tools\governance\verify_pins.ps1
PIN AUDIT: PASS (all 15)
PINS_EXIT=0
COMMAND: dotnet apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen/bin/Debug/net9.0/NewManga.DesignSystem.TokenGen.dll --check
rows: 292
up to date: every generated artifact matches the frozen token source byte-for-byte
TOKENGEN_EXIT=0
COMMAND: dotnet apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen/bin/Debug/net9.0/NewManga.ThemeEngine.ThemeGen.dll --check
theme: newmanga-default 1.0.0 (light 35 colors, dark 35 colors)
up to date: generated theme artifacts match the frozen token source byte-for-byte
THEMEGEN_EXIT=0
COMMAND: python -X utf8 verification/FEA-06-RESIDUAL-1/verify-r2-evidence.py
RAW_BYTES_ASSERT=13/13；旧文件/前缀逐字节保留
SKIP_ASSERT=57/57；每条实际 SKIP 均有完整名称与逐条原因
CURRENT_AND_HISTORY_ASSERT=ac-coverage.md: PASS
CURRENT_AND_HISTORY_ASSERT=item-status.md: PASS
CURRENT_AND_HISTORY_ASSERT=component-state-matrix.md: PASS
CURRENT_AND_HISTORY_ASSERT=batch-b-verification.log: PASS
R2_005_ASSERT=PASS；EXIT=0
EVIDENCE_EXIT=0
```

每行原因S的原文为：reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)。S对应本轮实际空变量；不是统称“平台原因”。App=7、CoreClient=22、Host=28；原生/PNG opt-in等NOT_RUN不混入这57个xUnit skip。

| # | 本轮实际跳过用例 | 逐条原因 |
|---|---|---|
| 1 | NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures | S |
| 2 | NewManga.App.Tests.CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly | S |
| 3 | NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys | S |
| 4 | NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey | S |
| 5 | NewManga.App.Tests.RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly | S |
| 6 | NewManga.App.Tests.StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot | S |
| 7 | NewManga.App.Tests.WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason | S |
| 8 | NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake | S |
| 9 | NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce | S |
| 10 | NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons | S |
| 11 | NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars | S |
| 12 | NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore | S |
| 13 | NewManga.CoreClient.Tests.Commands.CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | S |
| 14 | NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore | S |
| 15 | NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | S |
| 16 | NewManga.CoreClient.Tests.Commands.CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture | S |
| 17 | NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings | S |
| 18 | NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty | S |
| 19 | NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame | S |
| 20 | NewManga.CoreClient.Tests.Commands.RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides | S |
| 21 | NewManga.CoreClient.Tests.Commands.S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore | S |
| 22 | NewManga.CoreClient.Tests.CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped | S |
| 23 | NewManga.CoreClient.Tests.CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23 | S |
| 24 | NewManga.CoreClient.Tests.CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError | S |
| 25 | NewManga.CoreClient.Tests.CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest | S |
| 26 | NewManga.CoreClient.Tests.HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle | S |
| 27 | NewManga.CoreClient.Tests.HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling | S |
| 28 | NewManga.CoreClient.Tests.HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly | S |
| 29 | NewManga.CoreClient.Tests.SidecarFailureTests.StartupTimeout_IsTyped_NotAHang | S |
| 30 | NewManga.Host.Tests.CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain | S |
| 31 | NewManga.Host.Tests.ExportE2ETests.Export_Cancel_LeavesNoArtifact | S |
| 32 | NewManga.Host.Tests.ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory | S |
| 33 | NewManga.Host.Tests.ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames | S |
| 34 | NewManga.Host.Tests.GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages | S |
| 35 | NewManga.Host.Tests.GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant | S |
| 36 | NewManga.Host.Tests.GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths | S |
| 37 | NewManga.Host.Tests.GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled | S |
| 38 | NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized | S |
| 39 | NewManga.Host.Tests.HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection | S |
| 40 | NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes | S |
| 41 | NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall | S |
| 42 | NewManga.Host.Tests.HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection | S |
| 43 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry | S |
| 44 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe | S |
| 45 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged | S |
| 46 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames | S |
| 47 | NewManga.Host.Tests.HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost | S |
| 48 | NewManga.Host.Tests.HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked | S |
| 49 | NewManga.Host.Tests.HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars | S |
| 50 | NewManga.Host.Tests.LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites | S |
| 51 | NewManga.Host.Tests.RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration | S |
| 52 | NewManga.Host.Tests.StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites | S |
| 53 | NewManga.Host.Tests.StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites | S |
| 54 | NewManga.Host.Tests.StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable | S |
| 55 | NewManga.Host.Tests.WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook | S |
| 56 | NewManga.Host.Tests.WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError | S |
| 57 | NewManga.Host.Tests.WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog | S |

## 附录D：保护与交付

本Reviewer另用subprocess取得 Task base 的PNG原始blob，与当前文件逐字节比较；四项均相同，不仅比较返修manifest所声明的SHA。原历史Review相对其引入commit零diff；返修manifest的13项原文件/前缀字节检查PASS。

| PNG | SHA256（工作树=原Task base blob） |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

报告落盘前HEAD仍13a67e75f，工作树干净；当前生产/测试/verification/设计与fcf28bdfc零diff。未修改源码/Task/既有证据，未commit/push。

### 落盘后实际检查

在同一PowerShell Core7.6.8、无venv环境再次执行：check.ps1 PASS（上述3个既有warnings），FINAL_CHECK_EXIT=0；verify_pins.ps1 PASS（15/15），FINAL_PINS_EXIT=0。git status --short唯一项为 ?? doc/reviews/FEA-06-RESIDUAL-1-impl-r3.md；HEAD仍13a67e75f74b6fd881766552d5987e398f54aeda。git diff --quiet fcf28bdfc -- apps verification doc/design 的 FINAL_REVIEWED_BYTES_EXIT=0。报告PowerShell代码块Parser错误数=0，R3 findings表=1行，与front matter P0=0/P1=1/P2=0一致。此次追加只记录已执行结果，不改变被审内容或verdict。

