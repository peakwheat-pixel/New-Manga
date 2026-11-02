---
task_id: FEA-06-RESIDUAL-1
reviewer: Codex CLI（fresh session，独立上下文实现复核）
reviewer_kind: agent
author: ZCode CLI / DSH
base_commit: 82529a3d5864a39f362e414b67bca774d743f862
reviewed_head: 9665e857350d6796b9745c0d3975417c7bf2f5d7
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 5
p2: 4
provenance:
  agent: Codex CLI
  session_id: 01a19d13-634e-7b02-9682-1f39c9c763b6
  appointment: doc/tasks/FEA-06-RESIDUAL-1.md 的 impl-r1 Appointment 与本轮用户派发
  implementation_participation: none
  subagents: none
  mode: read_only_review_except_this_report
  date: 2026-11-03
---

# Review：FEA-06-RESIDUAL-1 impl-r1

**changes_requested：P0=0 / P1=5 / P2=4。** 现有测试实跑 **1195 passed / 0 failed / 57 skipped（总数 1252）**，但独立行为探针复现了导航动画未触发、缓存页不遵守运行时 reduce、Reader 空闲计时未重置、Reader 导航绕过 dirty 确认、Esc 关闭下层浮层五类阻断问题。不能据测试总数判定 AC 已达成。

## 范围与依据

固定 base → reviewed_head；main，Git common directory 为本仓库 .git，未建 worktree、未 commit/push。起始工作树干净；唯一交付文件为本报告，未修改源码、Task 或原证据。未参与实现/返修，无实现会话上下文。身份来源是环境中的 CODEX_THREAD_ID / CODEX_SESSION_ID，上述两值相同。

已读取当前 AD-002、STATUS、REBASELINE_PLAN 的有效状态，Task 范围 v3/AC/实施记录、scope-r3、两份 Handoff、Batch A/B 验证日志、Task 引用的矩阵/AC 覆盖/子项台账/预复核快照及 rolling checkpoint 当前段落。设计依据为 fluent-v1 的 01 §2.3、02 §1–§3、03 §3–§4、10 §1–§3、07-page-reader 的工具条语义。按仓库 REVIEW 模板覆盖 Architecture 与 Verification；Standards/Spec 采用同一独立 Reviewer 的检查视角，遵从项目已取消强制双轴子 agent 的规则。

git log 82529a3d5864a39f362e414b67bca774d743f862..HEAD 自证用户列出的 83fa1b186、9337cbbe1、ce0bee67d、a315bee02、6edf24904、918e4a2e3 均在范围内；并审查其后至 4388e50bb 的生产/测试增补。4388e50bb → reviewed_head 仅文档提交。49 个变更文件，17 个生产源码文件；已检查生产 diff、受影响调用链及新增测试的断言和覆盖边界。交付范围未因后续文档提交缩小为早期 1178 用例快照。

### Architecture：边界保持；生命周期有 P2

- 未见 UI 绕过 Host 访问 Core/SQLite/模型的新增路径，未引入依赖或修改共享契约。I-6 在拆分提交 83fa1b186 的 7 个类型（两个 enum、共享基类、四 VM）逐个提取完整声明/类体，与 base **逐字节相同**，公开签名、事件接线及逻辑等价；后续功能增补单独审查。
- base → head 的旧 screens、整个冻结 fluent-v1、DesignSystem/Generated、Current V2、共享 Shell、组合根 App.axaml/App.axaml.cs/Program.cs、FrontendSelector 均零 diff。旧四 PNG 与 base 和 FEA-06 Task:221–224 的既有 SHA pin 同时相符。
- 高对比字典重复加载的实测 ReferenceEquals=false；Standard 恢复与 reduce 阴影保持测试通过。**未复现**“XamlLoader 共享缓存字典污染 Standard”的假设，不将假设列为 finding。
- 新 Appearance.Changed 订阅在宿主关闭后仍保留，见 R1-006。高对比实际表面边框、已显示焦点环更新分别有 R1-007/008。

## Standards（executed）

以 AGENTS、协作协议 §4/§6、本 Task 允许/禁止范围为依据。未发现 Core/契约/生成物/冻结设计/Current V2 源码越界。证据登记存在当前结论未刷新与日志格式缺口（R1-009）。DesignRulesTests 的 BoxShadow 放行与冻结设计要求相容，但逐行非锚定正则只证明该行含允许的 token 文本，不能代替解析 Setter 值；本次实际四条新增 Setter 均为合法 DynamicResource，未发现生产代码借此绕过。

## Spec（executed）

I-6、I-7 的实现路径及保护边界成立；I-4 仍为 PARTIAL，不能判 MET。I-5 的常量表数值正确，MotionResolver 的 auto/full/reduce、分类和旧值迁移纯逻辑测试通过，但实际 UI 消费不等于表测试：R1-001/002 复现了缺口。I-10/I-3 的关键行为分别受 R1-003/004/005 阻断。decorative 本体未实现是 Task D-8 的已披露缺口，Reviewer 不代替 DSH/用户批准范围减免。

## Findings

行号均对应 reviewed_head；下表的源码短名相对于 apps/desktop-avalonia/src，证据短名相对于 verification/FEA-06-RESIDUAL-1。**附录 A 是本轮实际运行的完整无文件写入探针及其输出**，其中反射只调用现有私有 ApplyMotion 入口，以隔离设置文件写入；导航、按钮点击、Esc、计时、资源与焦点检查使用实际控件。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 对应 AC | 处理状态/修订 commit |
|---|---|---|---|---|---|---|---|
| R1-001 | P1 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:619；同文件:616；NewManga.App/Views/Fluent/ReaderPageView.cs:205 | 一级页面只换 Content，未改变 Opacity；Reader 隐藏只改 IsVisible。给 Opacity 附加 Transition 不会产生淡入/淡出。180ms Tab、200/160ms 浮层及 90/150ms feedback 参数仅在表中，未接消费；使用的 CubicEaseOut 也不是冻结的 bezier。navigation=关但 feedback=开时 Reader 仍挂导航过渡，因为使用了全局 Enabled。I-5 的未完成范围远大于 D-8 decorative。 | 附录 A：NAV changes=0/opacity=1/hasTransition=True；HIDE full 时 opacityChanges=0 且立即 invisible；NAV_OFF_READER hasTransition=True。命令：rg -n -e NavigationTabMilliseconds -e NavigationOverlayInMilliseconds -e FeedbackPressedMilliseconds -e FeedbackBadgeMilliseconds apps/desktop-avalonia/src。 | 在冻结范围内真正消费时长/曲线并改变被动画的属性；Reader 使用 navigation 分类结果。补实际动画过程及 reduce/category-off 立即完成的断言，不能只检查 Transitions 非空。 | AC1/I-10；AC2/I-5 | open |
| R1-002 | P1 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:655、661 | 只遍历当前 visual descendants，且仅在 Shell 挂载或设置改变时重放。初次换到缓存页的按钮没有 120ms 过渡；在另一页切 reduce/feedback-off 后，先前缓存页仍保留 full 过渡。运行时 reduce 不能保证全页 0ms，Render 后新建按钮同样漏接。 | 附录 A：NEW_PAGE feedbackTransition=False；full Library → Workbench → reduce → Library 得 REDUCE_REVISIT shelfTransition=True。 | 用随控件/页面生命周期生效的 Fluent 局部样式或统一设置机制覆盖全部缓存页及动态控件；切 reduce 清理全部相关过渡。测试必须遍历切页/重建/分类切换组合。 | AC2/I-5 | open |
| R1-003 | P1 | NewManga.App/Views/Fluent/ReaderPageView.cs:200；NewManga.App/ViewModels/Fluent/ReaderViewModel.cs:48 | 可见时 PokeToolBars 只是再次设置 true，不产生 PropertyChanged，视图不重启倒计时。工具条按上次显示时刻隐藏，而非最后一次鼠标/键盘交互后 2s；持续交互仍会突然隐藏。既有测试直接调用 HideToolBarsAfterIdle，没有跑真实空闲窗口。 | 附录 A：POKE_ALREADY_VISIBLE notifications=0；真实 Dispatcher MainLoop 在 t=1500ms Poke，t=2270ms 已 VISIBLE=False（距交互仅约 770ms）。 | 每次交互独立重置空闲计时器（Stop/Start 或可重排的 deadline），不要依赖 bool 值变化；补真实计时/可控时钟测试及 detach 后停止。 | AC1/I-10；R3-003 | open |
| R1-004 | P1 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:215–228 | Reader 特判先返回，绕过其后的设置 dirty guard。真实路径：书架选章节 → 设置改值 → Ctrl+K → 阅读选中章节，可直接离开且没有保存/丢弃/取消确认，破坏导航保护。 | 附录 A 以真实命令按钮 RaiseEvent：ACTUAL_READ_COMMAND page=Reader; dirty=True; leave=False。也可直接以 dirty Settings 调 Navigate(Reader) 作最小回归测试。 | 将离开设置的检查放在所有目的地分支之前；挂起 Reader 请求及其加载动作，确认成功后再更新页面和 Reader 返回目标。 | AC3/I-3 | open |
| R1-005 | P1 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:450–474 | Settings dirty/确认浮层存在时再用 Ctrl+K 打开 shell 命令面板，Esc 优先处理设置页下层浮层，跳过最上层 shell 面板。继续 Esc 会重新打开下层离开确认，面板始终不关闭，焦点/返回路径错误。 | 附录 A：beforeEsc shell=True/leave=True → afterEsc shell=True/leave=False → afterSecondEsc shell=True/leave=True。 | 按当前实际顶层浮层处理 Esc，再处理页内确认和页面离开；关闭后返还正确触发焦点。补两层浮层、连续 Esc 与关闭后触发控件失效的测试。 | AC3/I-3；AC2/I-11 | open |
| R1-006 | P2 | NewManga.App/Views/Fluent/FluentShellSurface.axaml.cs:144、586 | 新增对长寿命 AppearanceCoordinator 的强事件订阅，没有对称解除。宿主关闭后 surface 仍被持有，后续 Changed/已排队 Dispatcher 回调可继续改已失效树，重复创建会累积监听。 | 附录 A 反射事件 invocation list，仅计 OnAppearanceChangedForMotion：beforeClose=1，afterClose=1。 | 增加 Fluent 自有的最终销毁/平衡 attach-detach 生命周期与回调失效保护；保留 FEA-07 缓存树切回可恢复语义，避免重复订阅。不得擅改共享生命周期 seam。 | AC2/I-5；架构/生命周期 | open |
| R1-007 | P2 | NewManga.App/Views/Fluent/ReaderPageView.cs:169–172 | 新侧边浮动条只绑定 CornerRadius/BoxShadow，没有边框。高对比覆盖清空 Elevation 后，该实际表面变成无阴影也无 1px 边框，不满足设计 03 §4；通用 card 测试未覆盖该条。 | 附录 A：HC_RAIL shadow=0; border=0,0,0,0; brushNull=True。 | 给实际 rail 接入高对比表面/边框资源，验证 High=1px 边框、Standard/reduce 阴影按原令牌恢复。 | AC4/I-8；R3-004 | open |
| R1-008 | P2 | NewManga.DesignSystem/Theming/DesignSystemThemeManager.cs:411；消费点 Theming/FocusRing.cs:178；tests/NewManga.DesignSystem.Tests/FocusRingHighContrastTests.cs:43–50 | 高对比 token 已改为 3px，但已显示的 ring.BorderThickness 有旧 local value，仅换设置且焦点保持时仍为 2px。现有测试先切到 other 再重聚焦，掩盖运行时不更新。设计未授权“必须重聚焦后才达成”。 | 附录 A：RING_BEFORE=2,2,2,2；RING_HIGH_WITHOUT_REFOCUS=2,2,2,2。 | 令 ring 的几何在资源变化时即时重算，或使用正确的动态资源绑定；保留焦点不动验证 2→3→2。Offset=1 的独立几何断言也仍需补充。 | AC2/I-11 | open |
| R1-009 | P2 | component-state-matrix.md:32、41–42；ac-coverage.md:8、11；batch-a-verification.log:1；batch-b-verification.log:1 | 当前矩阵仍把命令面板结果态、disabled 零触发写为未完成，结尾又称 hover/pressed 全不可复现，与本文件 EFFECTIVE 行及最新测试矛盾；“仅剩视觉/少数格子、I-11 均达成”也被本轮行为反例推翻。两 Batch 日志缺实际 shell/解释器头和逐条 skip 清单，预复核快照未给 build/test 的明确 EXIT，且快照自身是 1194/0/57，不能单独支撑 ac-coverage.md:11 的最新 1195。 | 对照当前 4388e50bb 命令面板测试、指针态测试与附录 A；本轮附录 B 明列总数/57 条 skip。未把这些陈旧文字等同于蓄意伪造，Task 的 AC 本体仍未勾选、状态仍 in_progress。 | DSH 处置 findings 后刷新当前台账/AC 标记，并追加符合协作协议 §6.12 的运行日志（shell/解释器、命令、EXIT、逐条 skip 与差值）；保留旧版本证据字节，不覆盖冻结历史。 | AC2/I-4/I-5/I-11；AC5 | open |

### I-4 与证据诚实性专项结论

- **I-4 不能判 MET**。声明测试只解析 Selector 文本；它保留为静态覆盖检查可以，但不能当有效属性/视觉达成证据。新增 PointerStates、StateEffective、DisabledAutomation 和 CommandPalette 测试确实比早期交付更强，相关格可按实际断言计入。
- 当前仍有 Slider、ToggleSwitch disabled、IconButton checked、Segmented hover/pressed、SearchField 聚焦、Tooltip/ContextMenu、Toast 多 severity、loading 等格未逐项验证；这些普通控件属性和命令不全部依赖原生硬件。需补能在 headless 验证的格，余项才登记 NOT_RUN。B-2/B-3 数据面格继续 BLOCKED；不得以占位态覆盖绑定验收。
- I-11 的四页各一场景与单层命令面板正常返焦通过，但隐藏控件测试只是两个独立 Button 的 Focus 返回值，未验证四页真实 Tab 遍历；触发控件被移除、多层浮层和保持焦点切高对比未被现有测试覆盖。不能由这些测试推出全 I-11 MET。
- Task D-8 只是待裁决的 decorative 暂缓建议。本 Review 不签发范围豁免；它也不能解释 navigation/feedback 的未消费问题。

## 验证

所有下列实跑均针对上述固定 head。为遵守“只写本报告”，没有重新 build/restore，没有运行 opt-in PNG 采证；复用已有 Debug/net9.0 二进制，独立核对 Portable PDB 的 **728 个文档校验记录，0 mismatch / 0 missing**（含多程序集重复源码记录，不是 728 个不同文件）。因此有当前源码对应证据，但**不是本轮 build PASS**。原生/DPI/B-5 与 opt-in 新 PNG 仍为 NOT_RUN/BLOCKED。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定范围 | git rev-parse HEAD；git log base..HEAD --oneline；git diff base...HEAD | main / reviewed_head | PASS | 用户列出的提交全部在祖先链；工作树初始为空 |
| I-6 | git show base:.../FluentPageViewModels.cs，对照 83fa1b186 的五文件，按每个完整类型括号提取并比较 | Python 3.14 / reviewed_head | PASS | 7 个类型声明/类体逐字节相同；四 VM 的新增功能不混入拆分结论 |
| 全量与 FEA-07 回归 | dotnet vstest 8 个现有测试 DLL，使用 NewManga.runsettings，无过滤 | PowerShell Core 7.6.8；dotnet SDK 10.0.401；VSTest 18.7.0；测试 runtime .NET 9.0.11 | PASS（现有断言） | 1252 总数=1195 passed+57 skipped，0 failed，EXIT=0；附录 B |
| 二进制来源 | 读取全部现有测试输出中 NewManga.*.pdb，SHA1/SHA256 对照当前源码 | PowerShell 内存 C# / reviewed_head | PASS | 728 matched，0 mismatch，0 missing；不对新 build 作结论 |
| I-7 默认路径 | 上述全量包含 FluentPages_RenderHeadlessPngEvidence；NEWMANGA_CAPTURE_FLUENT_PNGS 未设置；测试后 git status 与旧 SHA 核验 | reviewed_head | PASS | 四帧尺寸断言通过；仓库 tracked/untracked 状态未变；旧 PNG 4×pin 一致 |
| I-7 opt-in | 静态检查固定输出路径、无环境变量路径插值、无旧 screens 写入调用 | reviewed_head | PASS（路径检查）/NOT_RUN（实采） | 输出固定在本卡 png；本轮未生成 PNG，不能称 opt-in 实跑 PASS |
| 动效/导航/计时/焦点 | 附录 A 的 PowerShell + Add-Type 内存探针 | PowerShell 7.6.8 / .NET 10 宿主加载 net9.0 组件 / Avalonia 11.3.22 | FAIL（行为） | R1-001…008 的实际输出；探针命令本身 EXIT=0 表示执行完成，不表示 AC 通过 |
| 高对比缓存假设 | 重复 TryLoad HighContrastPalette；既有 HighContrastElevationFocusTests/FluentCurrentComparisonTests | 同上/现有测试 runtime | PASS（记录范围） | 两次字典对象不共享；Standard 恢复、reduce 阴影保持。测试未覆盖的边界不能扩大为 PASS |
| 生成器 | dotnet TokenGen.dll --check；dotnet ThemeGen.dll --check | SDK 10.0.401 / reviewed_head | PASS | 292 rows；两个 up-to-date；EXIT=0 |
| 治理 | pwsh -NoProfile -File tools/governance/check.ps1 | PowerShell 7.6.8 / reviewed_head | PASS | 3 warnings：9 非终态 Task、STATUS/PLAN 80% 预算；EXIT=0 |
| 契约 pins | pwsh -NoProfile -File tools/governance/verify_pins.ps1 | 同上 | PASS | 15/15；EXIT=0，范围是 14 契约+FEA01，不代表本 Task 七项证据已审 |
| 本 Task 7 项 pin | 对指定 commit 的 blob 与当前文件分别算 SHA256，再核对文本行尾归一的一致性 | Python 3.14 / reviewed_head | PASS（保全/来源） | 7/7 匹配当前工作树 SHA；其中 I7/BATCHB/PREREVIEW 的 blob SHA 因行尾不同不等于工作树 SHA，归一后内容一致。依协作协议 §4.4，不擅改 hash basis、不据此判 pin 损坏 |
| 冻结/禁止写域 | git diff base HEAD --name-only -- 对应路径；四旧 PNG Get-FileHash/对照旧 Task pin | reviewed_head | PASS | 附录 C；原证据与冻结设计未改 |
| build / 200% DPI / 原生 a11y / 新 opt-in PNG | 未执行 | 本轮只读约束；B-5 既有硬件限制 | NOT_RUN / BLOCKED | 不使用作者自检代替本轮实跑 |

**Architecture 结论：** 分层、契约和持久化边界保持；新增事件生命周期与真实高对比消费仍有 P2，不能宣称所有 UI 非回归已证明。

**Verification 结论：** 现有回归 PASS；产品行为验证 FAIL。新增反例说明现有测试只验证配置或理想路径，未覆盖实际消费、缓存页、空闲重排与浮层叠加。

### AC 当前判定（供 DSH 处置，不修改 Task）

| AC | 本轮判定 | 原因 |
|---|---|---|
| AC1 | PARTIAL | I-10 的最后交互后 2s/真实淡出未达成；其余 Batch A 既有功能测试通过，外部数据面 B-1/B-2/B-3/B-6/B-7 保持 BLOCKED |
| AC2 | PARTIAL | I-4 多格未验证；I-5 实际消费/运行时 reduce 有 P1；I-11 叠层 Esc、高对比保持焦点有缺口；D-8/B-5 继续记录 |
| AC3 | PARTIAL | 三分支理想路径通过，但 Reader 目的地可绕过确认，多浮层 Esc 优先级错误 |
| AC4 | PARTIAL | I-6/I-7 静态及默认路径成立；I-8 Reader 高对比边框未达成，完整 Current 行为对照仍不足 |
| AC5 | PARTIAL | 1195/0/57、生成器、治理和旧 pin 保全可复现；日志格式/当前矩阵需修订，本轮没有新 build 或 opt-in PNG 证据 |

## 结论与复审

固定 head **不可交 DSH 作为已批准实现集成**。5 个 P1 open 足以要求返修；4 个 P2 可由 DSH 明确处置。不要把 decorative 暂缓建议、headless 限制或 1195 个通过测试用作上述可复现功能缺陷的豁免。

复审须给新固定 head、R1-001…009 disposition、受影响回归与附录 A 对照结果；旧 Review 保留。现有合法 BLOCKED 子项不应被迫造数据完成。修复范围或共享 seam 有变化，先由 DSH 冻结授权，Reviewer 不自行改代码/Task。

**推荐下一切片：FEA-06-RESIDUAL-1 findings 处置与返修范围确认；Agent：DSH。** Recovery point：G:\CODEX\New Manga，main，base=82529a3d5864a39f362e414b67bca774d743f862，head=9665e857350d6796b9745c0d3975417c7bf2f5d7。当前 Reviewer 不释放新 Task。DSH 先文档处置，再按原 Task 写域指定 ZCode 承担 Fluent UI 返修；Core/契约/生成物/冻结设计/Current V2/共享 FEA-07 seam 继续禁止。

可直接转发给 DSH：

> 在 G:\CODEX\New Manga 的 main 接收 FEA-06-RESIDUAL-1 impl-r1，固定 base 82529a3d5864a39f362e414b67bca774d743f862 / reviewed_head 9665e857350d6796b9745c0d3975417c7bf2f5d7。先核对工作树和 head，读取本报告，逐项处置 R1-001…009（P0=0/P1=5/P2=4），在 Task/STATUS 冻结返修范围与 Owner 后派 ZCode 修 Fluent 动效消费、Reader 计时、dirty 导航与浮层优先级；不改 Core/共享契约/生成物/冻结设计/Current V2/FEA-07 共享 seam。交付固定 commit、Handoff 和 verification，补 I-4 能 headless 断言的状态，保留真实 NOT_RUN/BLOCKED，明确 D-8 决定。用本报告附录 A 作判别性回归，跑现有 8 程序集、两生成器 --check、check.ps1/verify_pins、四旧 PNG SHA；日志带 shell/EXIT/逐条 skip。完成后重新 Appointment 独立上下文复审，再由 DSH 集成验证；不得据本报告提前关闭或 push。


## 附录 A：判别性探针（实际运行，完整可复制）

从仓库根目录，在新的 PowerShell 7 进程执行下列代码。使用已有测试输出；Add-Type 只在内存编译，不写源码/Task/PNG/证据文件，不调用 SaveAsync。/nowarn:1701 只用于此 .NET 10 PowerShell 宿主加载 net9.0 组件的引用版本提示，不改变产品构建。若需在 .NET 9 测试中固化这些断言，应由返修 Owner 另行提交测试。

```powershell
$ErrorActionPreference='Stop'
Write-Output ('SHELL='+$PSVersionTable.PSEdition+' '+$PSVersionTable.PSVersion+'; EXE='+(Get-Process -Id $PID).Path)
Write-Output ('HEAD='+(git rev-parse HEAD))
$reviewDllDir=(Resolve-Path 'apps/desktop-avalonia/tests/NewManga.App.Tests/bin/Debug/net9.0').Path
$env:PATH="$reviewDllDir/runtimes/win-x64/native;"+$env:PATH
[System.Runtime.Loader.AssemblyLoadContext]::Default.add_Resolving({param($context,$name) $candidate=Join-Path $reviewDllDir ($name.Name+'.dll'); if(Test-Path -LiteralPath $candidate){ return $context.LoadFromAssemblyPath($candidate) }; return $null })
[System.Runtime.Loader.AssemblyLoadContext]::Default.LoadFromAssemblyPath((Join-Path $reviewDllDir 'NewManga.App.Tests.dll')) | Out-Null
$reviewRefs=@(Get-ChildItem 'C:/Program Files/dotnet/packs/Microsoft.NETCore.App.Ref/10.0.*/ref/net10.0/*.dll' | ForEach-Object FullName)+@(Get-ChildItem "$reviewDllDir/*.dll" | Where-Object Name -NotLike 'System.*' | ForEach-Object FullName)
Add-Type -CompilerOptions '/nowarn:1701' -ReferencedAssemblies $reviewRefs -TypeDefinition @'
using System;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Threading;
using System.Diagnostics;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Threading;
using Avalonia.VisualTree;
using NewManga.App.Services;
using NewManga.App.Tests;
using NewManga.App.ViewModels.Fluent;
using NewManga.App.Views.Fluent;
using NewManga.Appearance;
using NewManga.DesignSystem.Theming;
public static class ReviewProbe {
 static void Pump(int ms=0){
  var watch=Stopwatch.StartNew();
  do{Thread.Sleep(10);Dispatcher.UIThread.RunJobs();}while(watch.ElapsedMilliseconds<ms);
 }
 static void Motion(FluentShellSurface s,MotionMode mode,MotionCategories cats=MotionCategories.All)=>
  typeof(FluentShellSurface).GetMethod("ApplyMotion",BindingFlags.NonPublic|BindingFlags.Instance)
   .Invoke(s,new object[]{AppearanceDefaults.Settings with {MotionMode=mode,MotionCategories=cats}});
 public static void Run(){
  TestAppBuilder.BuildAvaloniaApp().SetupWithoutStarting();
  using var theme=new DesignSystemThemeManager(Application.Current);theme.Initialize();
  // Only construct a store for a nonexistent temp path. No SaveAsync or file creation.
  var appearance=new AppearanceCoordinator(new AppearanceStore(
   Path.Combine(Path.GetTempPath(),"nm-review-nonexistent-"+Guid.NewGuid(),"presentation-settings.json")));
  var host=new FakeHostController(FakeHostController.ReadySnapshot("Review Book"));
  host.ChaptersByBook[host.Snapshot.Books.First().BookId]=new[]{
   new NewManga.CoreClient.ChapterSummary("chapter-review","chapter","1",0)};
  var s=new FluentShellSurface(null,FrontendSelector.Select(FrontendSelector.FluentFrontendId,null),host,appearance,theme);
  var w=new Window{Width=1280,Height=900,Content=s};w.Show();Pump();Motion(s,MotionMode.Full);
  var pageHost=s.FindControl<ContentControl>("FluentPageHost");
  int pageOpacityChanges=0;
  pageHost.PropertyChanged+=(_,e)=>{if(e.Property==Visual.OpacityProperty)pageOpacityChanges++;};
  var shelfButton=s.ShelfView.DetailPaneToggle;
  s.Navigate(FluentPage.Workbench);Pump(300);
  Console.WriteLine($"NAV changes={pageOpacityChanges}; opacity={pageHost.Opacity}; hasTransition={pageHost.Transitions!=null}");
  Console.WriteLine($"NEW_PAGE feedbackTransition={s.WorkbenchView.InspectorToggle.Transitions!=null}");
  Motion(s,MotionMode.Reduce);s.Navigate(FluentPage.Library);Pump();
  Console.WriteLine($"REDUCE_REVISIT shelfTransition={shelfButton.Transitions!=null}");
  Motion(s,MotionMode.Full);s.Navigate(FluentPage.Reader);Pump();
  var reader=s.ReaderView;int barOpacityChanges=0;
  reader.TopBar.PropertyChanged+=(_,e)=>{if(e.Property==Visual.OpacityProperty)barOpacityChanges++;};
  s.ReaderViewModel.HideToolBarsAfterIdle();Pump();
  Console.WriteLine($"HIDE full: visible={reader.TopBar.IsVisible}; opacity={reader.TopBar.Opacity}; opacityChanges={barOpacityChanges}; transition={reader.TopBar.Transitions!=null}");
  s.ReaderViewModel.PokeToolBars();Pump();
  int notifications=0;
  s.ReaderViewModel.PropertyChanged+=(_,e)=>{if(e.PropertyName=="AreToolBarsVisible")notifications++;};
  s.ReaderViewModel.PokeToolBars();
  Console.WriteLine($"POKE_ALREADY_VISIBLE notifications={notifications}");
  var start=DateTime.UtcNow;
  DispatcherTimer.RunOnce(()=>{
   Console.WriteLine("POKE_T="+(DateTime.UtcNow-start).TotalMilliseconds.ToString("0"));
   s.ReaderViewModel.PokeToolBars();
  },TimeSpan.FromMilliseconds(1500));
  using(var cancellation=new CancellationTokenSource(2250)){
   try{Dispatcher.UIThread.MainLoop(cancellation.Token);}catch(OperationCanceledException){}
  }
  Console.WriteLine("CHECK_T="+(DateTime.UtcNow-start).TotalMilliseconds.ToString("0")+"; VISIBLE="+reader.TopBar.IsVisible);
  Motion(s,MotionMode.Full,MotionCategories.Feedback);
  Console.WriteLine($"NAV_OFF_READER hasTransition={reader.TopBar.Transitions!=null}; reduceFlag={s.ReaderViewModel.AreToolBarsReducedMotion}");
  s.ShelfViewModel.SelectBookAsync(s.ShelfViewModel.Books.First()).GetAwaiter().GetResult();
  s.Navigate(FluentPage.Settings);Pump();
  s.SettingsViewModel.UpdateDraft(s.SettingsViewModel.Draft with {MaterialAcrylicStrength=0.123});Pump();
  s.HandleKeyForTest(Key.K,KeyModifiers.Control);Pump();
  var readCommand=s.GetVisualDescendants().OfType<Button>()
   .First(b=>b.Content?.ToString()?.StartsWith("阅读选中章节")==true);
  readCommand.RaiseEvent(new RoutedEventArgs(Button.ClickEvent));Pump();
  Console.WriteLine($"ACTUAL_READ_COMMAND page={s.CurrentPage}; dirty={s.SettingsViewModel.IsDirty}; leave={s.SettingsView.LeaveConfirmationVisible}");
  s.Navigate(FluentPage.Settings);s.Navigate(FluentPage.Library);Pump();
  var modal=s.FindControl<Border>("FluentModalHost");
  s.HandleKeyForTest(Key.K,KeyModifiers.Control);Pump();
  Console.WriteLine($"OVERLAYS beforeEsc shell={modal.IsVisible}; leave={s.SettingsView.LeaveConfirmationVisible}");
  s.HandleKeyForTest(Key.Escape,KeyModifiers.None);Pump();
  Console.WriteLine($"OVERLAYS afterEsc shell={modal.IsVisible}; leave={s.SettingsView.LeaveConfirmationVisible}");
  s.HandleKeyForTest(Key.Escape,KeyModifiers.None);Pump();
  Console.WriteLine($"OVERLAYS afterSecondEsc shell={modal.IsVisible}; leave={s.SettingsView.LeaveConfirmationVisible}");
  s.SettingsView.CancelLeave();s.SettingsViewModel.UpdateDraft(appearance.Settings);
  s.HandleKeyForTest(Key.Escape,KeyModifiers.None);s.Navigate(FluentPage.Reader);Pump();
  theme.SetContrast(ContrastMode.High);Pump();
  Console.WriteLine($"HC_RAIL shadow={reader.SideRail.BoxShadow.Count}; border={reader.SideRail.BorderThickness}; brushNull={reader.SideRail.BorderBrush==null}");
  theme.SetContrast(ContrastMode.Standard);Pump();
  var uri=DesignSystemResourceSource.Default.HighContrastPalette;
  DesignSystemThemeManager.TryLoad(uri,out var a);DesignSystemThemeManager.TryLoad(uri,out var b);
  Console.WriteLine($"HC_SHARED_DICTIONARY={ReferenceEquals(a,b)}");
  var input=new TextBox();
  var focusWindow=new Window{Width=400,Height=300,Content=new Border{Padding=new Thickness(20),Child=input}};
  focusWindow.Show();Pump();input.Focus(NavigationMethod.Tab);Pump();
  Border Ring()=>focusWindow.GetVisualDescendants().OfType<Border>()
   .First(x=>x.Classes.Contains("nm-focus-ring")&&x.IsVisible);
  Console.WriteLine("RING_BEFORE="+Ring().BorderThickness);
  theme.SetContrast(ContrastMode.High);Pump();
  Console.WriteLine("RING_HIGH_WITHOUT_REFOCUS="+Ring().BorderThickness);
  theme.SetContrast(ContrastMode.Standard);Pump();
  Console.WriteLine("RING_STANDARD_WITHOUT_REFOCUS="+Ring().BorderThickness);
  focusWindow.Close();
  var changedField=typeof(AppearanceCoordinator).GetField("Changed",BindingFlags.NonPublic|BindingFlags.Instance);
  int Subscribers()=>((Delegate)changedField.GetValue(appearance))?.GetInvocationList()
   .Count(d=>d.Method.Name=="OnAppearanceChangedForMotion")??0;
  Console.WriteLine($"SUBS beforeClose={Subscribers()}");w.Close();Pump();
  Console.WriteLine($"SUBS afterClose={Subscribers()}");
  Console.WriteLine("PROBE_COMPLETE");
 }
}

'@
try { [ReviewProbe]::Run() } catch { Write-Output $_.Exception.ToString(); exit 1 }
Write-Output 'EXIT=0'
```

本轮实际输出（2026-11-03，EXIT=0 为探针成功执行；FAIL 项见 Findings）：

```text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
HEAD=9665e857350d6796b9745c0d3975417c7bf2f5d7
NAV changes=0; opacity=1; hasTransition=True
NEW_PAGE feedbackTransition=False
REDUCE_REVISIT shelfTransition=True
HIDE full: visible=False; opacity=1; opacityChanges=0; transition=True
POKE_ALREADY_VISIBLE notifications=0
POKE_T=1500
CHECK_T=2270; VISIBLE=False
NAV_OFF_READER hasTransition=True; reduceFlag=False
ACTUAL_READ_COMMAND page=Reader; dirty=True; leave=False
OVERLAYS beforeEsc shell=True; leave=True
OVERLAYS afterEsc shell=True; leave=False
OVERLAYS afterSecondEsc shell=True; leave=True
HC_RAIL shadow=0; border=0,0,0,0; brushNull=True
HC_SHARED_DICTIONARY=False
RING_BEFORE=2,2,2,2
RING_HIGH_WITHOUT_REFOCUS=2,2,2,2
RING_STANDARD_WITHOUT_REFOCUS=2,2,2,2
SUBS beforeClose=1
SUBS afterClose=1
PROBE_COMPLETE
EXIT=0
```

## 附录 B：全量命令、结果、二进制来源与逐项 skip

实际命令（本轮没有构建；生成器直接运行已有 DLL）：

```powershell
$reviewBinaries = Get-ChildItem 'apps/desktop-avalonia/tests/*/bin/Debug/net9.0/NewManga.*.Tests.dll' |
    ForEach-Object { $_.FullName }
dotnet vstest $reviewBinaries --Settings:apps/desktop-avalonia/tests/NewManga.runsettings --logger:console`;verbosity=normal
Write-Output ('EXIT=' + $LASTEXITCODE)
dotnet apps/desktop-avalonia/src/NewManga.DesignSystem/tools/NewManga.DesignSystem.TokenGen/bin/Debug/net9.0/NewManga.DesignSystem.TokenGen.dll --check
Write-Output ('TOKENGEN_EXIT=' + $LASTEXITCODE)
dotnet apps/desktop-avalonia/src/NewManga.ThemeEngine/tools/NewManga.ThemeEngine.ThemeGen/bin/Debug/net9.0/NewManga.ThemeEngine.ThemeGen.dll --check
Write-Output ('THEMEGEN_EXIT=' + $LASTEXITCODE)
pwsh -NoProfile -File tools/governance/check.ps1
Write-Output ('CHECK_EXIT=' + $LASTEXITCODE)
pwsh -NoProfile -File tools/governance/verify_pins.ps1
Write-Output ('PINS_EXIT=' + $LASTEXITCODE)
```

本轮运行记录：

```text
SHELL=Core 7.6.8; EXE=C:\Program Files\PowerShell\7\pwsh.exe
DOTNET=C:\Program Files\dotnet\dotnet.exe; SDK=10.0.401
VSTest=18.7.0 (x64); test runtime=.NET 9.0.11
HEAD=9665e857350d6796b9745c0d3975417c7bf2f5d7
NEWMANGA_CAPTURE_FLUENT_PNGS=<unset>
NEWMANGA_EVIDENCE_SYNC=<unset>
8 test files; tests=1252; passed=1195; failed=0; skipped=57
Elapsed=2.1567 minutes; EXIT=0
TokenGen: rows=292; every generated artifact matches source byte-for-byte; TOKENGEN_EXIT=0
ThemeGen: newmanga-default 1.0.0 (light 35 colors, dark 35 colors); up-to-date; THEMEGEN_EXIT=0
Governance check: PASS (3 warnings); CHECK_EXIT=0
PIN AUDIT: PASS (all 15); PINS_EXIT=0
Portable PDB current-source checksum audit: MATCHED=728; MISMATCH=0; MISSING=0; EXIT=0
```

全量口径与旧数值差异：pre-I-7 安全基线为 1137 passed/57 skipped，额外排除 1 个 PNG 测试；恢复该测试后起点 1138；Batch A +33 →1171（含 PNG）；早期 1178 是中间交付，当前新增累计到 1195。当前 **1252=1195+57**，不能将 57 skip 计入通过。3 个 ModelsBuild 用例在真实 VSTest 进程内通过，不能因为另一个无仓库 AppContext 的反射进程找不到默认 fixture 就把它们误列为 skip。下列清单在设置 NEWMANGA_WORKSPACE_ROOT 为实际相邻 workspace 后，逐个读取 Fact.Skip 并与本轮跳过总数交叉核对。

每条的 **S** 原因均为实际返回的：

```text
reason: needs sidecar fixture - set NEWMANGA_CORECLIENT_SIDECAR_DIR or run apps/desktop-avalonia/scripts/test.ps1 (AC11 unlabelled copy)
```

| # | 跳过用例（程序集::类.方法） | 原因 |
|---|---|---|
| 1 | NewManga.App.Tests::CreateChapterHostIntegrationTests.HostController_CreateChapter_SucceedsThenMapsCoreFailures | S |
| 2 | NewManga.App.Tests::CreateChapterHostIntegrationTests.HostController_CreateChapter_WhenReadOnly_PublishesHostReadOnly | S |
| 3 | NewManga.App.Tests::RunControllerHostIntegrationTests.RunCommands_MapCoreErrors_AndReuseIdempotencyKeys | S |
| 4 | NewManga.App.Tests::RunControllerHostIntegrationTests.RunCommands_StartSuccessfulRun_ProjectRealPerPageState_AndReuseKey | S |
| 5 | NewManga.App.Tests::RunControllerHostIntegrationTests.RunCommands_WhenReadOnly_PublishHostReadOnly | S |
| 6 | NewManga.App.Tests::StartupSelfCheckUiTests.SelfCheckFailure_IsVisibleInTheSnapshot | S |
| 7 | NewManga.App.Tests::WritePolicyUiIntegrationTests.DefaultController_IsWritable_AndParityFalse_IsReadOnlyWithReason | S |
| 8 | NewManga.CoreClient.Tests::CoreServiceIntegrationTests.Ping_ReturnsReady_WithProtocol23 | S |
| 9 | NewManga.CoreClient.Tests::CoreServiceIntegrationTests.ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped | S |
| 10 | NewManga.CoreClient.Tests::CoreServiceIntegrationTests.RawUtf8Request_ReplicatesUnknownError | S |
| 11 | NewManga.CoreClient.Tests::CoreServiceIntegrationTests.WireFrames_AreSingleLineUtf8AndAsciiForEveryEscapedRequest | S |
| 12 | NewManga.CoreClient.Tests::HostBridgeIntegrationTests.Ping_IssueResolveRevoke_FullLifecycle | S |
| 13 | NewManga.CoreClient.Tests::HostBridgeIntegrationTests.TypedErrors_UnknownResource_AndCoreOwnedPathSmuggling | S |
| 14 | NewManga.CoreClient.Tests::HostBridgeIntegrationTests.WireFrames_AreSingleLineJson_AsciiOnly | S |
| 15 | NewManga.CoreClient.Tests::SidecarFailureTests.StartupTimeout_IsTyped_NotAHang | S |
| 16 | NewManga.CoreClient.Tests::CommandIntegrationTests.TwelveImplementedCommands_ExecuteAgainstFrozenSidecars | S |
| 17 | NewManga.CoreClient.Tests::CommandIntegrationTests.ChineseTitle_ThroughCommandDispatcher_RoundTripsWithoutMojibake | S |
| 18 | NewManga.CoreClient.Tests::CommandIntegrationTests.NotSupportedSurface_ReturnsTypedErrorsWithReasons | S |
| 19 | NewManga.CoreClient.Tests::CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce | S |
| 20 | NewManga.CoreClient.Tests::CommandWiringB1Tests.B1Commands_ExecuteAgainstFrozenCore | S |
| 21 | NewManga.CoreClient.Tests::CommandWiringB1Tests.B1Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | S |
| 22 | NewManga.CoreClient.Tests::CommandWiringB2Tests.B2Commands_ExecuteAgainstFrozenCore | S |
| 23 | NewManga.CoreClient.Tests::CommandWiringB2Tests.ListRegionRevisions_ExecutesAgainstRegionFixture | S |
| 24 | NewManga.CoreClient.Tests::CommandWiringB2Tests.B2Commands_RejectInvalidArgumentsBeforeAnyCoreFrame | S |
| 25 | NewManga.CoreClient.Tests::RunBindingFixTests.StartRun_InjectsDefaultBindings_WhenOverridesAbsentOrEmpty | S |
| 26 | NewManga.CoreClient.Tests::RunBindingFixTests.StartRun_KeepsExplicitUserBindings_AndOtherOverrides | S |
| 27 | NewManga.CoreClient.Tests::RunBindingFixTests.StartRun_DefaultDisabled_OmitsProviderBindings | S |
| 28 | NewManga.CoreClient.Tests::RunBindingFixTests.StartRun_InvalidOverrides_AreRejectedBeforeAnyCoreFrame | S |
| 29 | NewManga.CoreClient.Tests::S4RegionReaderCommandTests.RegionWriteFace_AndReaderProgressFace_ExecuteAgainstFrozenCore | S |
| 30 | NewManga.Host.Tests::CredentialPortTests.CredentialPutAndClear_AgainstFrozenSidecar_FullChain | S |
| 31 | NewManga.Host.Tests::ExportE2ETests.Export_Zip_Produces_RealArtifact_AndSnapshotHistory | S |
| 32 | NewManga.Host.Tests::ExportE2ETests.Export_Cancel_LeavesNoArtifact | S |
| 33 | NewManga.Host.Tests::ExportStalePolicyWireTests.BothPolicies_AreSentToTheCore_AsStartExportFrames | S |
| 34 | NewManga.Host.Tests::GrantIssuerTests.Import_IntoNewChapter_Executes_AndRegistersGrant | S |
| 35 | NewManga.Host.Tests::GrantIssuerTests.Export_GrantRegisters_ThenCoreFailsTyped_OnMissingTranslatedPages | S |
| 36 | NewManga.Host.Tests::GrantIssuerTests.ShellActions_RealOpener_OpensExplorer_WhenEnabled | S |
| 37 | NewManga.Host.Tests::GrantIssuerTests.ShellActions_Open_Whitelisted_Directories_And_Refuse_Outside_Paths | S |
| 38 | NewManga.Host.Tests::HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection | S |
| 39 | NewManga.Host.Tests::HostReaderChaptersIntegrationTests.ConcurrentChapterAndProjectionReads_AreSerialized | S |
| 40 | NewManga.Host.Tests::HostReaderProgressIntegrationTests.SaveReadingProgress_PersistsAcrossHostRestart_AndResumes | S |
| 41 | NewManga.Host.Tests::HostReaderProgressIntegrationTests.SaveReadingProgress_UnknownPage_IsTypedCoreRejection | S |
| 42 | NewManga.Host.Tests::HostReaderProgressIntegrationTests.SaveReadingProgress_ReadOnlyHost_IsTypedRefusal_NoCoreCall | S |
| 43 | NewManga.Host.Tests::HostRegionWorkbenchIntegrationTests.RegionReadWriteFace_ExecutesAgainstFrozenCore_AndProjectsOverlayGeometry | S |
| 44 | NewManga.Host.Tests::HostRegionWorkbenchIntegrationTests.RegionWrite_StaleExpectedRevision_IsTypedInputRevisionChanged | S |
| 45 | NewManga.Host.Tests::HostRegionWorkbenchIntegrationTests.RegionWrites_ReadOnlyHost_AreTypedRefusals_WithZeroCoreFrames | S |
| 46 | NewManga.Host.Tests::HostRegionWorkbenchIntegrationTests.RegionReads_SerializeOnTheCorePipe | S |
| 47 | NewManga.Host.Tests::HostRuntimeIntegrationTests.ReadOnlyUntilParity_Ready_WithBothSidecars_AndWriteBlocked | S |
| 48 | NewManga.Host.Tests::HostRuntimeIntegrationTests.ParityReached_ChineseRoundTrip_IsExact_ThroughHost | S |
| 49 | NewManga.Host.Tests::HostRuntimeIntegrationTests.SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars | S |
| 50 | NewManga.Host.Tests::LegacyShellRealTests.LegacyShellRunning_ForcesReadOnlyMode_AndBlocksWrites | S |
| 51 | NewManga.Host.Tests::RealTranslateProviderTests.RealOpenCodeProvider_HostConfiguration | S |
| 52 | NewManga.Host.Tests::StartupSelfCheckTests.RealHost_PassesCheapChecks_AndStaysWritable | S |
| 53 | NewManga.Host.Tests::StartupSelfCheckTests.MajorMismatch_DowngradesToReadOnly_AndRefusesWrites | S |
| 54 | NewManga.Host.Tests::StartupSelfCheckTests.MissingCapability_DowngradesToReadOnly_AndRefusesWrites | S |
| 55 | NewManga.Host.Tests::WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook | S |
| 56 | NewManga.Host.Tests::WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError | S |
| 57 | NewManga.Host.Tests::WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog | S |

清单计数：App=7，CoreClient=22，Host=28；合计 57。没有消除 skip，也没有由此宣称真实 sidecar/硬件场景已验收。

## 附录 C：旧证据 SHA 与只读保全

下列当前工作树 SHA-256 与 base blob 逐字节相同，并与 doc/tasks/FEA-06.md:221–224 原 pin 一致：

| PNG | SHA-256 |
|---|---|
| reader.png | 8533c263c79bd53cefa68a21d2aabe6501556fd62218ebf653b528c9cbec78b2 |
| settings.png | fd30b166e30aec7a43e4d82ecd1fefb14dffef3bebe2f5f952e41d45e324a162 |
| shelf.png | 307f8f6748522d1cdb3226135a3f733961744a3b2aa5d410f89aad3fde138b0a |
| workbench.png | d5d878bbba9e47e2b59d9dd03816a370688a7afebec6d6e00016f262a46e2df5 |

可复制的只读核对命令：

```powershell
git rev-parse HEAD
git log --oneline 82529a3d5864a39f362e414b67bca774d743f862..HEAD
git diff --name-only 82529a3d5864a39f362e414b67bca774d743f862 HEAD -- verification/FEA-06/screens doc/design/fluent-v1 apps/desktop-avalonia/src/NewManga.DesignSystem/Generated apps/desktop-avalonia/src/NewManga.App/Views/V2 apps/desktop-avalonia/src/NewManga.App/ViewModels/V2 apps/desktop-avalonia/src/NewManga.App/Shell apps/desktop-avalonia/src/NewManga.App/App.axaml apps/desktop-avalonia/src/NewManga.App/App.axaml.cs apps/desktop-avalonia/src/NewManga.App/Program.cs apps/desktop-avalonia/src/NewManga.App/Services/FrontendSelector.cs
Get-FileHash -Algorithm SHA256 verification/FEA-06/screens/*.png
git status --porcelain=v1 --untracked-files=all
```

运行前与全部检查后（写本报告之前）git status 均为空，HEAD 始终为 reviewed_head；预期最终唯一新增项为本 Review。未运行 opt-in，未改旧 pin、Task、STATUS、PLAN、设计、源码或测试，未 push。

