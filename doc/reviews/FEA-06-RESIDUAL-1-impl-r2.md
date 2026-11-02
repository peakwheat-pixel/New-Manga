---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh session，独立上下文 Reviewer）
reviewer_kind: agent
author: ZCode CLI / DSH / Codex CLI 实现会话
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: eaf7b74d85cdb6c2d8961bf26db9b6d73abcaaf4
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 3
p2: 3
provenance:
  agent: Codex CLI
  session_id: 01a19d45-1e04-7151-95d7-924a18dcd941
  appointment: 本轮用户 fresh impl-r2 Prompt；checkpoint 第113节记录 DSH 派发
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-1 impl-r2

**changes_requested：P0=0 / P1=3 / P2=3。** 本轮 build、全量 test、check.ps1、verify_pins.ps1 全部 EXIT=0，全量为 **1213 passed / 0 failed / 57 skipped（总数1270）**。新增三项动画存在真实消费和判别性测试；但 Reader 淡出/分类、其他浮层、动态按钮颜色过渡及 Reader 点击空闲重置仍有可复现缺口，不能按测试总数签 AC 达成。

## 范围与依据

固定 base → reviewed_head，main，Git common directory=.git，工作路径 G:\CODEX\New Manga。第一次状态采集时 HEAD=e0d1d73c5，Task/checkpoint 有他人未提交修改；随后外部文档提交 eaf7b74d8 落地，本轮将其固定为 reviewed_head。已核对 e0d1d73c5→eaf7b74d8 仅修改 Task delivery_head 与 checkpoint 第113节（2文件，+6/-1），生产/测试与 e0d1d73c5 相同。未恢复、暂存或改写他人内容。固定后 HEAD 未变、源码与证据工作树无 diff。唯一持久交付为本报告；未 commit/push。

已读：AD-002 当前架构，STATUS/REBASELINE_PLAN 有效状态与 rolling checkpoint 当前段；Task 范围 v3、AC、实施记录、Canonical Evidence、D-7/D-8/D-10；impl-r1 全文及附录A；batch-a/b 与 impl-r1-animation 三份 Handoff；verification/FEA-06-RESIDUAL-1 的全部7个日志/矩阵/台账；fluent-v1 的 motion、accessibility、tokens/elevation、reader、settings、component inventory 相关章节。审查 base...head 的57文件变更及调用链，重点检查 51c5afb47、e327b64b5、3ea4af605、e25600431、033c8b4b9 的返修。

按项目 REVIEW 模板覆盖 Architecture 与 Verification；Standards/Spec 为同一独立 Reviewer 的视角。项目模板已取消强制双轴子代理，无子代理、无实现上下文继承。未将旧日志中间版本结果重写为当前结果。

## Architecture（executed）

未发现新增 UI 直接访问 SQLite/Core/模型、依赖、schema 或共享契约变更。禁止路径（冻结设计、Generated、Current V2 源码、Shell/FEA-07 seam、组合根、FrontendSelector）相对 base 零 diff；这仅证明写域保持，不证明所有共享样式运行效果均已验收。

033c8b4b9 的 IFluentMotionClock 是 internal 注入点；生产 FluentRenderClock 使用单调 Stopwatch 和 TopLevel.RequestAnimationFrame。插值/完成逻辑在生产 FluentFrameAnimation 中，手动时钟仅替换帧源。generation 使取消后的帧失效，detach 同步收敛终值；ConditionalWeakTable 的 feedback 实例没有外部静态强持有链。新增有限动画没有 DispatcherTimer/Task.Delay/后台轮询；回调走 UI 帧线程，未发现其持续计时泄漏。生产帧源测试实际使用 ForceRenderTimerTick 推进并验证隐藏时间不早于160ms，未以 Transitions 非空替代过程断言。

Appearance.Changed attach/detach 数量修复有效；已排队回调的失效保护仍缺失（R2-004）。Reader 原有 DispatcherTimer 的 detach Stop 保留，输入覆盖不足另见 R2-003。

## Standards（executed）

范围、只读、证据保全与 Host 边界按 AGENTS、协作协议和本 Task 核查。I-6 在拆分提交83fa1b186的7个完整类型声明/类体与 base 逐字节相同：FluentPageState、FluentViewModel、ShelfViewModel、WorkbenchViewModel、ReaderViewModel、SettingsGroupId、SettingsViewModel；后续功能另行审查。未削弱既有业务断言；PNG 用例按授权改为默认内存渲染/尺寸断言，opt-in 才写本卡目录。

全范围 git diff --check EXIT=2，仅旧 impl-r1 报告第408行新增 EOF 空行；本轮不改历史报告。未将此格式问题升级为产品 finding。

## Spec（executed）

R1 的设置导航和叠层 Esc 关键反例已消除；I-5/I-10 仍有真实行为反例，I-11 的 stroke 修复不代表 offset=1 已实现。I-4 的 Slider/ToggleSwitch disabled、checked/loading、Toast severity 等格仍缺有效属性证据；普通 headless 可验证格不能统一称“硬件视觉阻塞”。D-8 仍为待独立裁决建议，decorative 本体未实现，本 Review 不代签范围豁免。D-10 的三项由新实现完成了 shell exit/pressed/dirty badge 的消费，不代表所有浮层或 I-5 全部完成；原生视觉/DPI/a11y 仍 NOT_RUN/BLOCKED。

## Findings

源码路径均相对 apps/desktop-avalonia/src；证据路径相对 verification/FEA-06-RESIDUAL-1。行号对应 reviewed_head。附录A为原R1探针复跑，附录B为本轮新增内存探针；探针 EXIT=0 表示执行完成，行为是否满足 AC 由输出判断。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据命令＋输出摘要 | 对应 AC | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|---|
| R2-001 | P1 | NewManga.App/Views/Fluent/ReaderPageView.cs:217、237；FluentShellSurface.axaml.cs:696；SettingsPageView.cs:140、227 | R1-001 仍未整体闭环。Reader 顶/底条隐藏仅改 IsVisible，不改 Opacity；navigation 分类关闭仍用全局 resolution.Enabled，因 feedback 开启而保留导航过渡。设置离开/确认浮层直接开关，未接200/160ms消费；Shelf 抽屉/对话框同类路径也未统一。full 与 reduce 在这些实际浮层的显示过程相同。feedback hover 还用 CubicEaseOut（Shell:755），与冻结(.4,0,.2,1)不同。 | 附录A复跑：HIDE full visible=False/opacity=1/opacityChanges=0；NAV_OFF_READER hasTransition=True/reduceFlag=False。附录B：SETTINGS_OVERLAY_OPEN visible=True/opacity=1/transition=False；关闭同步 visible=False。rg -n 'Transition\|Motion' 对应视图可核对仅Shell独立接线。 | AC1/I-10；AC2/I-5；设计02 §2.1/2.2、10 §4 | 在全部实际浮层及Reader工具条消费冻结参数/曲线；Reader按navigation有效结果降级。增加过程、中间值、分类关闭及reduce瞬时断言，不能只验时长对象。 | open；033c8b4b9仅修复部分消费点 |
| R2-002 | P1 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:745、788；SettingsPageView.cs:91、292 | R1-002 的缓存页/命令面板修复有效，但页面内部重建控件仍漏接120ms颜色过渡。PreparePressedFeedback仅补缩放，不补BrushTransition；一次ApplyMotion/导航后看似恢复，后续分组/投影重建又丢失，导致同一设置下反馈不一致。 | 附录B：full下切Providers→DYNAMIC_PROVIDER transition=False/transform=False；真实Space按下后DYNAMIC_PRESSED transition=False/scale=0.98；切Backup→transition=False；手动重放ApplyMotion后True。 | AC2/I-5；R1-002 | 用Fluent局部的持续机制覆盖新建控件、模板和缓存树；颜色与pressed一致配置。测试覆盖“切组/Render重建→hover→分类切换→再次重建”，不要仅测试下一次Navigate后的结果。 | open |
| R2-003 | P1 | NewManga.App/Views/Fluent/ReaderPageView.cs:82–92、204 | R1-003仅修复PointerMoved和未被上层处理的KeyDown。PointerPressed/释放、滚轮以及被Shell截获的按键没有统一重置入口；鼠标停在工具条上持续点击，仍按上一次移动时刻隐藏。 | 附录B真实MainLoop：键盘t=1509ms后t=2260ms visible=True，t=3725ms False（键盘路径PASS）；移入真实单/双页按钮，t=1590ms MouseDown/Up，pressed=True，DoublePage False→True；t=2253ms工具条已False，仅距成功点击约663ms。初期被命令面板挡住的试跑已排除，最终命中链含ReaderPageView/真实Button。 | AC1/I-10、R3-003 | 在Reader范围统一观察有效用户交互，覆盖pointer press/wheel及handled键盘，保持点击中部切换显隐语义；以真实输入和可控deadline验证最后交互后2s，另验detach停止。 | open；WakeToolBars修复不完整 |
| R2-004 | P2 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:669 | R1-006取消订阅平衡，但后台Changed在attach时已Post的闭包未再次检查订阅/挂载代次。detach后仍ApplyMotion、遍历树和写共享ThemeManager，违反“detach后回调失效”的返修承诺；不是持续事件泄漏。 | 附录B：工作线程调用现有OnAppearanceChangedForMotion→移除Window.Content→RunJobs，DETACHED_QUEUED_CALLBACK replacedTransitions=True；附录A beforeClose=1/afterClose=0证明订阅数已修复。 | AC2/I-5；Architecture生命周期 | Post闭包执行时复查有效attach generation；detach使已排队旧回调失效，reattach应用当前值且只订阅一次。补后台事件→detach→pump与快速reattach测试。 | open |
| R2-005 | P2 | ac-coverage.md:8、11、29；item-status.md:12、31；component-state-matrix.md:32、42；batch-b-verification.log:123–128 | R1-009仅部分修复。当前AC表写“最新1197”，结尾1195；item-status仍1195及“I-11完成”；matrix结论仍把命令面板结果态、disabled零触发列为缺口，与已存在的有效断言相冲突。Batch B补记称skip明细但只有程序集计数，未逐条原因。新动画日志已提供1213/57逐条清单，不能使旧快照自动成为最新。 | Get-Content上述7份证据对照本轮1213/0/57与附录B；pre-review快照实际1194，不能直接支撑1197/1213。Task:18“全部返修”也不能代替残余反例处置。 | AC2/I-4/I-5/I-11；AC5 | 保留旧日志/历史Review；追加当前版本统一AC/子项/组件矩阵与准确head/命令/EXIT/57逐条原因，区分历史快照和最新证据。明确当前NOT_RUN及待裁决D-8，不将其记完成。 | open；新日志格式本身已改善 |
| R2-006 | P2 | NewManga.DesignSystem/Theming/FocusRing.cs:180–190；tests/NewManga.DesignSystem.Tests/FocusRingHighContrastTests.cs:41–64 | R1-008的2↔3px即时stroke已修复，但I-11要求offset=1仍未消费：环尺寸/位置仅加减stroke，内边缘贴着控件，offset实际为0；测试只断言BorderThickness。 | 附录B：RING_GEOMETRY inputWidth=360/ringWidth=364/stroke=2/gap=0。预期offset=1时外宽应366、内缘间距1；未重聚焦stroke探针独立通过。 | AC2/I-11；设计03 §3 | 在Fluent授权边界实现1px offset，并测试标准/高对比/滚动裁剪几何及Current对照。若需要超出既有共享FocusRing授权，由DSH先冻结范围。 | open |

### R1 findings 处置核验

| R1 | 本轮结论 | 证据/限制 |
|---|---|---|
| R1-001 | PARTIAL | 新Shell退出160ms、pressed90ms/.98、dirty badge150ms/.9→1真实消费；16个新增测试验证159/160、89/90、149/150边界、reduce/分类、取消/重开/detach。生产退出帧源通过；Reader/其他浮层/hover曲线仍R2-001。页面与Tab已有属性变化，不再是纯Transitions配置；未据最终Opacity=1宣称完整视觉时序已验收。 |
| R1-002 | PARTIAL | 缓存页首次切入/在别页切reduce后返回清过渡通过；命令面板构建/搜索重建有重放。设置页内部动态按钮仍R2-002；新增pressed补接不等于颜色过渡补接。 |
| R1-003 | PARTIAL | 真实键盘重排通过；成功鼠标点击未重排见R2-003；原附录A直接Poke没有通知的结果不作为“真实键盘修复失败”的证据。 |
| R1-004 | FIXED（原导航绕过反例） | 实际命令面板“阅读选中章节”：page=Settings/dirty=True/leave=True。Reader目的地不再跳过确认；三分支/失败保护测试通过。OpenReader仍先安排LoadAsync，未把“加载也全部延后”当成已验证事实。 |
| R1-005 | FIXED（原双层反例） | shell=True/leave=True→第一次Esc shell=False/leave=True→第二次Esc shell=False/leave=False。新有限退出期间逻辑Esc不等待视觉完成的测试通过。 |
| R1-006 | PARTIAL | 1→0取消订阅通过，重复attach有bool守卫；已排队后台回调仍R2-004。 |
| R1-007 | FIXED | HC_RAIL shadow=0/border=1,1,1,1/brushNull=False；standard/reduce阴影既有有效属性测试通过。 |
| R1-008 | FIXED（原stroke反例） | 无重聚焦2→3→2通过；offset独立残项见R2-006，不能因此写全I-11 MET。 |
| R1-009 | PARTIAL | 新动画日志有完整shell/命令/EXIT/逐条57skip；旧日志在Git blob层保持原前缀，仅追加。当前矩阵/AC/台账仍R2-005。 |

## 验证

所有实跑在固定 reviewed_head 的生产/测试字节上执行。构建仅产生通常的ignored构建产物；未写源码/Task/旧证据。探针Add-Type在内存编译、AppearanceStore使用不存在的临时路径且不调用SaveAsync；未写真实APPDATA。NEWMANGA_CAPTURE_FLUENT_PNGS、NEWMANGA_EVIDENCE_SYNC、NEWMANGA_CORECLIENT_SIDECAR_DIR均未设置。

环境：Windows NT 10.0.26300.0；PowerShell Core 7.6.8，EXE=C:\Program Files\PowerShell\7\pwsh.exe；dotnet SDK10.0.401，测试目标net9.0，Avalonia11.3.22。内存探针是PowerShell .NET10宿主加载本轮build产出的net9.0组件；不代替net9.0 VSTest全量。

| 场景 | 实际命令/步骤 | 结果 | 输出摘要/EXIT |
|---|---|---|---|
| 构建 | dotnet build apps\desktop-avalonia\NewManga.sln --nologo | PASS | 0 warnings / 0 errors；BUILD_EXIT=0 |
| 全量，无过滤 | dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings --nologo | PASS（现有断言） | 8程序集，1270=1213+0+57；App约1m41s；TEST_EXIT=0 |
| 治理 | pwsh -NoProfile -File tools\governance\check.ps1 | PASS | CHECK_EXIT=0；3既有warning：9非终态Task、STATUS/PLAN预算80% |
| 冻结契约pin | pwsh -NoProfile -File tools\governance\verify_pins.ps1 | PASS | PINS_EXIT=0；15/15，不代表本Task全AC通过 |
| TokenGen | dotnet apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen/bin/Debug/net9.0/NewManga.DesignSystem.TokenGen.dll --check | PASS | 292rows，byte-for-byte up-to-date；EXIT=0 |
| ThemeGen | dotnet apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen/bin/Debug/net9.0/NewManga.ThemeEngine.ThemeGen.dll --check | PASS | newmanga-default1.0.0，up-to-date；EXIT=0 |
| 真实行为 | 附录A原命令复跑＋附录B内存探针 | FAIL（行为） | 两探针执行EXIT=0；反例R2-001…004/006 |
| I-6等价 | git show base:FluentPageViewModels.cs，与83fa1b186的五文件按平衡括号提取完整类型比较 | PASS | TYPES=7/7，全部EXACT，EXIT=0 |
| 测试保留/FEA-07 | 检查测试diff＋本轮全量包含PresentationWindow/InputRouting/HostComposition/FrontendHostCoordinator/SettingsDraftSync | PASS（已有断言） | 基线1137（排除PNG）→1138（恢复PNG）→1195（R1）→1197（前批返修）→1213（+16）；skip仍57，未删用例充数 |
| 本Task证据pin | 逐行读取Task Canonical Evidence，按commit取blob及工作树SHA256比较 | PASS（来源/保全） | 7/7工作树SHA匹配；I7/BATCHB/PREREVIEW的blob仅因CRLF/LF不同，归一内容一致；不擅自更改hash basis |
| 历史证据 | 比较9665e8573与reviewed_head三个旧log blob | PASS | batch-a/b、pre-review原blob均为当前blob完整字节前缀；旧Review未变 |
| 禁止路径/旧PNG | git diff --name-only base reviewed_head -- 禁止路径；Get-FileHash SHA256 verification/FEA-06/screens/*.png | PASS | 零路径diff，四PNG与base及既有pin一致；见附录D |
| I-7默认 | 全量包含FluentPages_RenderHeadlessPngEvidence；采证变量未设置；运行后git status | PASS | 默认渲染/尺寸断言通过，未写仓库PNG |
| I-7 opt-in/原生矩阵 | 未运行新PNG采证；未运行原生200%DPI/a11y/真机视觉 | NOT_RUN / BLOCKED | 本轮唯一交付约束；B-5原硬件前置保持，不以headless属性证据替代 |
| 空白检查 | git diff --check base reviewed_head | FAIL（已有文档格式） | EXIT=2；仅impl-r1.md:408 EOF空行，本轮保持原字节 |

### 逐程序集计数

| 程序集 | passed | failed | skipped | total |
|---|---:|---:|---:|---:|
| Appearance | 21 | 0 | 0 | 21 |
| Presentation.Avalonia | 38 | 0 | 0 | 38 |
| Host | 51 | 0 | 28 | 79 |
| ThemeEngine | 253 | 0 | 0 | 253 |
| DesignSystem | 93 | 0 | 0 | 93 |
| ApplicationCore | 31 | 0 | 0 | 31 |
| CoreClient | 128 | 0 | 22 | 150 |
| App | 598 | 0 | 7 | 605 |
| 合计 | 1213 | 0 | 57 | 1270 |

### AC当前判定（不修改Task）

| AC | 判定 | 原因 |
|---|---|---|
| AC1 | PARTIAL | I-10淡出/分类和最后点击后2s未达成；其他既有功能回归通过；B-1/2/3/6/7继续按依赖BLOCKED |
| AC2 | PARTIAL | I-5真实消费/动态控件有P1；I-4剩余有效属性格未验证；offset=1缺失；D-8未裁决、B-5仍BLOCKED |
| AC3 | IN范围既有断言PASS，完整AC仍有B-4限制 | 导航保护/原双层Esc反例修复，三分支及保存失败保护测试通过；B-4数据面不在本轮伪造完成 |
| AC4 | IN范围既有断言PASS，opt-in本轮NOT_RUN | I-6等价、默认PNG保护、rail高对比及standard/reduce阴影通过；不宣称新原生视觉验收 |
| AC5 | PARTIAL | 四必跑命令/生成器/保护证据通过；最新台账口径仍不一致，原生/opt-in限制分列 |

**Architecture结论：** 分层/契约/持久化与新有限动画帧源在审查范围内保持；detach后的排队回调尚需修复。
**Verification结论：** 构建和现有回归PASS，关键实际行为FAIL。不能交DSH作为已批准实现集成，也不能由1213个通过推导AC全达成。

## 结论与复审

固定head verdict=changes_requested。DSH处置R2-001…006，返修后提供新head与受影响行为/回归证据，再派fresh独立复核；本会话不得参与这些finding的实现或返修。D-8和B-5须按真实授权/依赖处置，Reviewer不释放新节点、不代裁决范围、不关闭Task。

推荐下一切片：FEA-06-RESIDUAL-1 impl-r2 findings处置，Agent=DSH；启动条件=接收本报告。Recovery point：G:\CODEX\New Manga、main、同一worktree，base=82529a3d5864a39f362e414b67bca774d743f862，reviewed_head=eaf7b74d85cdb6c2d8961bf26db9b6d73abcaaf4。DSH先记录处置和冻结返修范围，再指定ZCode承担Fluent UI返修；不授予本Reviewer实现权限。现Task写域继续适用，Core/契约/schema/生成物/冻结设计/Current V2/组合根/FEA-07 seam禁止变更，任何共享FocusRing范围变化先由DSH明确。

可直接转发给DSH：

> 在 G:\CODEX\New Manga 的 main 接收 FEA-06-RESIDUAL-1 impl-r2，base 82529a3d5864a39f362e414b67bca774d743f862，reviewed_head eaf7b74d85cdb6c2d8961bf26db9b6d73abcaaf4；先核对当前HEAD/工作树，读取 doc/reviews/FEA-06-RESIDUAL-1-impl-r2.md。逐项处置R2-001…006（P0=0/P1=3/P2=3），明确D-8及I-4未验证格，冻结返修写域后分配ZCode。交付新固定commit、Handoff及追加verification日志/当前矩阵，不覆盖旧证据。复跑报告附录行为探针、build、全量test、两生成器、check.ps1、verify_pins.ps1和旧PNG SHA；记录每条EXIT、57skip逐条原因及计数差值，不能将NOT_RUN/BLOCKED计PASS。返修后由DSH派fresh Reviewer，Review和集成验证通过前不关闭本Task、不释放后续实现节点；不得push。

## 附录A：原R1附录A复跑

本轮实际从磁盘读原报告的完整powershell代码块并在新PowerShell进程内执行（不重写旧报告）：

~~~powershell
$reviewDoc=Get-Content -Raw doc/reviews/FEA-06-RESIDUAL-1-impl-r1.md
$reviewPart=$reviewDoc.Substring($reviewDoc.IndexOf('## 附录 A：'))
$reviewBlock=[regex]::Match($reviewPart,'(?s)```powershell\r?\n(.*?)\r?\n```').Groups[1].Value
Invoke-Expression $reviewBlock
~~~

~~~text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
HEAD=eaf7b74d85cdb6c2d8961bf26db9b6d73abcaaf4
NAV changes=4; opacity=0.5739320083417825; hasTransition=True
NEW_PAGE feedbackTransition=True
REDUCE_REVISIT shelfTransition=False
HIDE full: visible=False; opacity=1; opacityChanges=0; transition=True
POKE_ALREADY_VISIBLE notifications=0
POKE_T=1502
CHECK_T=2254; VISIBLE=False
NAV_OFF_READER hasTransition=True; reduceFlag=False
ACTUAL_READ_COMMAND page=Settings; dirty=True; leave=True
OVERLAYS beforeEsc shell=True; leave=True
OVERLAYS afterEsc shell=False; leave=True
OVERLAYS afterSecondEsc shell=False; leave=False
HC_RAIL shadow=0; border=1,1,1,1; brushNull=False
HC_SHARED_DICTIONARY=False
RING_BEFORE=2,2,2,2
RING_HIGH_WITHOUT_REFOCUS=3,3,3,3
RING_STANDARD_WITHOUT_REFOCUS=2,2,2,2
SUBS beforeClose=1
SUBS afterClose=0
PROBE_COMPLETE
EXIT=0
~~~

这里的Poke仍是直接VM调用，不代表真实键盘路径；以附录B真实输入补足。NAV opacity的单次采样不能单独证明240ms时序达标。

## 附录B：新增内存探针（完整可复制）

在仓库根目录的新PowerShell7进程执行；只在内存编译，使用本轮build二进制，不调用设置保存、不写证据PNG。Clock边界另由全量内FluentAnimationCompletionTests覆盖。鼠标试跑已先关闭上层命令面板，且输出命中链、pressed和业务布尔值，排除了“空点被挡”的假反例。

~~~powershell
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
using System.Diagnostics;
using Avalonia;
using Avalonia.Animation;
using Avalonia.Controls;
using Avalonia.Headless;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Tests;
using NewManga.App.Services;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
public static class R2Probe {
 static void Pump(int ms=0){var t=Stopwatch.StartNew();do{Thread.Sleep(5);AvaloniaHeadlessPlatform.ForceRenderTimerTick();Dispatcher.UIThread.RunJobs();}while(t.ElapsedMilliseconds<ms);}
 static void Loop(int ms){using var c=new CancellationTokenSource(ms);try{Dispatcher.UIThread.MainLoop(c.Token);}catch(OperationCanceledException){}}
 static void Motion(FluentShellSurface s,MotionMode m=MotionMode.Full,MotionCategories c=MotionCategories.All)=>
 typeof(FluentShellSurface).GetMethod("ApplyMotion",BindingFlags.Instance|BindingFlags.NonPublic).Invoke(s,new object[]{AppearanceDefaults.Settings with {MotionMode=m,MotionCategories=c}});
 static Button Named(Control c,string name)=>c.GetVisualDescendants().OfType<Button>().First(b=>Avalonia.Automation.AutomationProperties.GetName(b)==name);
 public static void Run(){
 TestAppBuilder.BuildAvaloniaApp().SetupWithoutStarting();
 using var theme=new DesignSystemThemeManager(Application.Current);theme.Initialize();
 var a=new AppearanceCoordinator(new AppearanceStore(Path.Combine(Path.GetTempPath(),"nm-r2-nonexistent-"+Guid.NewGuid(),"appearance.json")));
 var s=new FluentShellSurface(host:new FakeHostController(FakeHostController.ReadySnapshot()),appearance:a,themeManager:theme);
 var w=new Window{Width=1280,Height=900,Content=s};w.Show();Pump();Motion(s);
 s.Navigate(FluentPage.Settings);Pump();
 s.SettingsViewModel.SelectedGroup=SettingsGroupId.Providers;Pump();
 var b=Named(s.SettingsView,"添加 Provider Profile");
 Console.WriteLine("DYNAMIC_PROVIDER transition="+(b.Transitions!=null)+"; transform="+(b.RenderTransform!=null));
 b.Focus();w.KeyPressQwerty(PhysicalKey.Space,RawInputModifiers.None);Pump(95);
 Console.WriteLine("DYNAMIC_PRESSED transition="+(b.Transitions!=null)+"; scale="+((Avalonia.Media.ScaleTransform)b.RenderTransform).ScaleX);
 s.FindControl<Button>("CommandPaletteButton").Focus();w.KeyReleaseQwerty(PhysicalKey.Space,RawInputModifiers.None);
 s.SettingsViewModel.SelectedGroup=SettingsGroupId.Backup;Pump();
 Console.WriteLine("DYNAMIC_BACKUP transition="+(Named(s.SettingsView,"创建手动备份").Transitions!=null));
 Motion(s);Console.WriteLine("AFTER_REPLAY transition="+(Named(s.SettingsView,"创建手动备份").Transitions!=null));
 s.HandleKeyForTest(Key.Escape,KeyModifiers.None);Pump(250);s.Navigate(FluentPage.Reader);Pump();Motion(s);
 var reader=s.ReaderView;
 reader.Focus();w.KeyPressQwerty(PhysicalKey.A,RawInputModifiers.None);w.KeyReleaseQwerty(PhysicalKey.A,RawInputModifiers.None);
 var t=Stopwatch.StartNew();
 DispatcherTimer.RunOnce(()=>{w.KeyPressQwerty(PhysicalKey.A,RawInputModifiers.None);w.KeyReleaseQwerty(PhysicalKey.A,RawInputModifiers.None);Console.WriteLine("REAL_KEY_T="+t.ElapsedMilliseconds);},TimeSpan.FromMilliseconds(1500));
 Loop(2250);Console.WriteLine("REAL_KEY_CHECK_T="+t.ElapsedMilliseconds+"; visible="+reader.TopBar.IsVisible);
 Loop(1450);Console.WriteLine("REAL_KEY_FINAL_T="+t.ElapsedMilliseconds+"; visible="+reader.TopBar.IsVisible);
 // Clicking a visible toolbar button should also reset the real deadline, without a MouseMove.
 reader.Focus();w.KeyPressQwerty(PhysicalKey.A,RawInputModifiers.None);w.KeyReleaseQwerty(PhysicalKey.A,RawInputModifiers.None);Pump();
 var zoom=Named(reader,"切换单页或双页");
 var p=zoom.TranslatePoint(new Point(zoom.Bounds.Width/2,zoom.Bounds.Height/2),w).Value;w.MouseMove(p,RawInputModifiers.None);
 Console.WriteLine("CLICK_TARGET bounds="+zoom.Bounds+"; point="+p+"; visible="+zoom.IsEffectivelyVisible+"; hit="+w.InputHitTest(p)?.GetType().Name+"; ancestors="+string.Join("/",(w.InputHitTest(p) as Visual).GetVisualAncestors().OfType<Control>().Select(c=>c.GetType().Name+":"+c.Name+":"+string.Join(",",c.Classes))));t.Restart();
 DispatcherTimer.RunOnce(()=>{var before=s.ReaderViewModel.DoublePage;w.MouseDown(p,MouseButton.Left,RawInputModifiers.None);var pressed=zoom.IsPressed;w.MouseUp(p,MouseButton.Left,RawInputModifiers.None);Console.WriteLine("REAL_CLICK_T="+t.ElapsedMilliseconds+"; pressed="+pressed+"; toggleBefore="+before+"; toggleAfter="+s.ReaderViewModel.DoublePage);},TimeSpan.FromMilliseconds(1500));
 Loop(2250);Console.WriteLine("REAL_CLICK_CHECK_T="+t.ElapsedMilliseconds+"; visible="+reader.TopBar.IsVisible);
 // All non-shell overlays still use immediate visibility changes.
 s.Navigate(FluentPage.Settings);Pump();Motion(s);
 var settingsScrim=(Border)typeof(SettingsPageView).GetField("_scrim",BindingFlags.Instance|BindingFlags.NonPublic).GetValue(s.SettingsView);
 s.SettingsViewModel.UpdateDraft(s.SettingsViewModel.Draft with{MaterialAcrylicStrength=.123});
 s.Navigate(FluentPage.Library);Pump();
 Console.WriteLine("SETTINGS_OVERLAY_OPEN visible="+settingsScrim.IsVisible+"; opacity="+settingsScrim.Opacity+"; transition="+(settingsScrim.Transitions!=null));
 s.SettingsView.CancelLeave();
 Console.WriteLine("SETTINGS_OVERLAY_CLOSE visible="+settingsScrim.IsVisible+"; opacity="+settingsScrim.Opacity);
 s.SettingsViewModel.UpdateDraft(a.Settings);
 // Appearance queued callback is scheduled while attached, then surface is removed before dispatch.
 var method=typeof(FluentShellSurface).GetMethod("OnAppearanceChangedForMotion",BindingFlags.Instance|BindingFlags.NonPublic);
 var pageHost=s.FindControl<ContentControl>("FluentPageHost");
 var transitionsBefore=pageHost.Transitions;
 var worker=new Thread(()=>method.Invoke(s,new object[]{a,EventArgs.Empty}));worker.Start();worker.Join();
 w.Content=null;Dispatcher.UIThread.RunJobs();
 Console.WriteLine("DETACHED_QUEUED_CALLBACK replacedTransitions="+(!ReferenceEquals(transitionsBefore,pageHost.Transitions)));
 w.Content=s;Pump();w.Content=null;Pump();w.Close();
 var input=new TextBox();
 var fw=new Window{Width=400,Height=300,Content=new Border{Padding=new Thickness(20),Child=input}};
 fw.Show();Pump();input.Focus(NavigationMethod.Tab);Pump();
 var ring=fw.GetVisualDescendants().OfType<Border>().First(x=>x.Classes.Contains("nm-focus-ring")&&x.IsVisible);
 var ip=input.TranslatePoint(default,fw).Value;var rp=ring.TranslatePoint(default,fw).Value;
 Console.WriteLine("RING_GEOMETRY inputWidth="+input.Bounds.Width+"; ringWidth="+ring.Bounds.Width+"; stroke="+ring.BorderThickness.Left+"; gap="+(ip.X-rp.X-ring.BorderThickness.Left));
 fw.Close();Console.WriteLine("R2_PROBE_COMPLETE");
 }
}
'@
try { [R2Probe]::Run() } catch { Write-Output $_.Exception.ToString(); exit 1 }
Write-Output 'EXIT=0'

~~~

本轮最终探针输出（初期无命中/遮挡的试跑不作为finding证据）：

~~~text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
HEAD=eaf7b74d85cdb6c2d8961bf26db9b6d73abcaaf4
DYNAMIC_PROVIDER transition=False; transform=False
DYNAMIC_PRESSED transition=False; scale=0.98
DYNAMIC_BACKUP transition=False
AFTER_REPLAY transition=True
REAL_KEY_T=1509
REAL_KEY_CHECK_T=2260; visible=True
REAL_KEY_FINAL_T=3725; visible=False
CLICK_TARGET bounds=99, 0, 92, 35; point=361, 69.5; visible=True; hit=TextBlock
命中祖先链包含Button(fluent-secondary)/StackPanel(fluent-reader-bar)/ReaderPageView/FluentPageHost
REAL_CLICK_T=1590; pressed=True; toggleBefore=False; toggleAfter=True
REAL_CLICK_CHECK_T=2253; visible=False
SETTINGS_OVERLAY_OPEN visible=True; opacity=1; transition=False
SETTINGS_OVERLAY_CLOSE visible=False; opacity=1
DETACHED_QUEUED_CALLBACK replacedTransitions=True
RING_GEOMETRY inputWidth=360; ringWidth=364; stroke=2; gap=0
R2_PROBE_COMPLETE
EXIT=0
~~~

## 附录C：本轮57条skip及原因

本轮标准dotnet test控制台逐条列出以下57个SKIP，名称与最新动画日志交叉核对，App=7、CoreClient=22、Host=28。每条原因S均为：

~~~text
reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)
~~~

本轮该环境变量为空；原因由SidecarFixture.TryGetSidecarDirectory及其App/Host Fact包装器给出。未配置fixture，未消除skip，也未把这些真实sidecar场景计为通过。清单按完整名称记录；不是仅凭总数反推skip。

| # | 跳过用例 | 原因 |
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
| 43 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe | S |
| 44 | NewManga.Host.Tests.HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry | S |
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

## 附录D：旧PNG及最终保全

~~~powershell
git rev-parse HEAD
git diff --name-only 82529a3d5864a39f362e414b67bca774d743f862 eaf7b74d8 -- verification/FEA-06/screens doc/design/fluent-v1 apps/desktop-avalonia/src/NewManga.DesignSystem/Generated apps/desktop-avalonia/src/NewManga.App/Views/V2 apps/desktop-avalonia/src/NewManga.App/ViewModels/V2 apps/desktop-avalonia/src/NewManga.App/Shell apps/desktop-avalonia/src/NewManga.App/App.axaml apps/desktop-avalonia/src/NewManga.App/App.axaml.cs apps/desktop-avalonia/src/NewManga.App/Program.cs apps/desktop-avalonia/src/NewManga.App/Services/FrontendSelector.cs
Get-FileHash -Algorithm SHA256 verification/FEA-06/screens/*.png
git diff --name-only eaf7b74d8 -- apps verification doc/design
git status --short
~~~

| PNG | SHA256（本轮工作树=base blob=原pin） |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

最终实测状态：HEAD仍为reviewed_head，apps/verification/doc/design无工作树diff，git status唯一新增项为本报告。落盘后再次运行check.ps1和verify_pins.ps1，分别PASS（3既有warnings）/15项PASS，EXIT均为0；四PNG SHA仍一致。报告内3个PowerShell代码块的Parser检查均0错误，findings表为6行，与front matter计数一致。原始Task/checkpoint修改由外部文档commit落地，本Reviewer未写这些文件。没有源码返修、证据覆盖或push。


