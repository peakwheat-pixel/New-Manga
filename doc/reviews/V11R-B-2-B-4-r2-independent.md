# 独立审查报告 · 第二轮（V11R-B-2 Console / V11R-B-4 Studio·Batch）

**审查者**：reviewer（独立、只读，未参与实现；本轮唯一写操作是上一条归档文件）
**基准**：同上轮全部冻结文档；另按 Lead 指示以「main 已含这两支代码」为事实基线
**Pin**（以 git object 为准，未跟随分支 HEAD）：
- **B-2 Console** = `v11r/ui-shell` @ **`f3da3aaf3`**（`f3da3aaf3d9b4e263e4cd41a81affdadbcc0a4f6`，parent `16449bfa0`；B-2 的壳接线在更早的 `b4a75d724`，已在 pin 树内）
- **B-4 Batch** = `v11r/ui-studio` @ **`4cd9213c6`**（`4cd9213c60dc5d788312a0d8c0e1eba92ff8b27f`，parent `c452c28c8`）
- 两个 pin 均已是 `main` 祖先（已核实 `merge-base --is-ancestor` = YES）。

**基线漂移（审查期间）**：`main` 已前进到 `e070cc074`（DS「R-18 breakpoint token / 图标集 / Skeleton / 焦点环 / StatusCatalog」等 D-1 返修 + INT-1 计划落档）；两支工作树 HEAD 亦前进（shell `3c543856a`、studio `2fbb94b94`）。**本轮只审 pin**，DS 进展仅用于判断"上收时机"。另：`main` 工作区当前有 14 个 `verification/V11R-B-3/artifacts/*.png` 未提交改动 —— 证据仍在被重渲染改写（上轮 P3 未处置）。

**纪律**：未改动任何 worktree、未 commit/push、**未运行 build/test**（两条 pin 的 build/test log 均未由我重跑，只做代码↔日志↔证据一致性抽查）；不采信 Owner 自述，找反例。

---

## 一、结论

| 分支 | 结论 | 一句话理由 |
|---|---|---|
| **V11R-B-2 Console**（`f3da3aaf3`） | **PASS_WITH_ISSUES** | 9 分区真实/待接入划分诚实，凭据只显示状态、错误只渲染 typed code、危险确认阻断态零写、R-08 缺失幂等键零调用 —— 上轮 B-1 的"证据/裸值"病在 B-2 基本治好；但 **Run 轮询的"切回恢复/离开分区即停"两条声明都与代码不符**（离开控制台后轮询永久停、切回不恢复），且状态词表被复用来表达"是否接入/是否已保存"。 |
| **V11R-B-4 Studio·Batch**（`4cd9213c6`） | **FAIL（返修后重审）** | 动态列、七态符号（`·`）、门禁 Cancel 零执行、选择跨轮询保留都真实且有断言；但 **①每次投影轮询把整张矩阵重建约 26 次（`Rows.CollectionChanged→Rebuild`，24 行时每 750ms 造 ~6,240 个控件）并因此把矩阵滚动位置重置为 0（矩阵实际无法滚动）**；**②作用域=选中/当前页在无法物化时静默回落到"整章"并把 `*_selected` 命令发出去（静默扩大作用域）**；另有两处"证据里写实现没做的值"（`gate.json.impact_text` 写死、`drilldown.json.scroll_kept` 是 0==0 同义反复）与 2 条恒真断言。 |

---

## 二、V11R-B-2 问题清单

### P1
*无。*（本轮 Lead 点名的五条重点均未发现 P1，逐条结论见 §四）

### P2

| 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|
| `ViewModels/V2/Console/ConsoleViewModel.cs:488-502`（`LoadRunAsync` 内 :500 才 `StartRunPolling`）、`:459-468`、`:179-185`；壳侧 `ViewModels/V2/Shell/AppShellViewModel.cs:474-480`（`SwitchSpace(Console)` 只调 `InitializeAsync()`，`:1693` 有 `_initialized` 短路） | **"Run 轮询切回恢复"没有实现**：离开控制台 → `StopRunPolling()` → 回到控制台只执行 `InitializeAsync()`（已初始化则 no-op），**全仓只有 `LoadRunCommand→LoadRunAsync` 会重新 `StartRunPolling`**；连"刷新 Run"（`RefreshRunCommand`，`:168` → `RefreshRunAsync`）也不会重启轮询。用户切走再回来，Run 状态带永久冻结，直到重填 run_id 再点「读取 Run」。证据 `AC_COVERAGE AC2`「控制台切走时停止 Run 轮询，切回恢复」与 `NOT_WIRED.md #2`「离开分区/离开控制台立即停轮询」**两条都不成立**（"离开分区停"在代码里没有任何调用点） | SCREEN_SPECS §0「切换空间/模式不重置」精神；DESIGN_SYSTEM §7「ready 态持续投影」；AC2/证据可信度 | 增加 `OnActivated/OnDeactivated`（或复用 `SpaceChanged` + 分区分支）：进入 Console 且有 run_id 时 `StartRunPolling()`；切分区时按 NOT_WIRED 声明停/不停二选一并改文案；测试断言"切出→切回→轮询已恢复（`IsPolling` 或 timer 非空）" |
| `Views/V2/Console/ConsoleView.axaml:39,64`（`StatusBadge Status="{Binding Status}"`）、`ViewModels/V2/Console/ConsoleItems.cs:51`（`NmStatus.Status => IsWired ? Done : Blocked`）、`:264-266`（凭据 `StateStatus => IsConfigured ? Done : NotStarted`） | **状态词表被复用为非状态语义**：左索引把"该分区已接入"渲染成 `● 完成`、把"未接入"渲染成 `▲ 阻塞`；凭据把"未保存"渲染成 `○ 未开始`。DESIGN_SYSTEM §2.2 规定 `done=完成`、`blocked=阻塞`、`not_started=未开始`，§2.1 明确"状态不参与装饰、不得表达非状态含义"。截图 `01/07` 中 9 个分区全部带语义错误的绿点/橙三角（"临时端口未接入"读作"阻塞"会让用户以为需要他去解除） | DESIGN_SYSTEM §2.2/§2.1；§9.4「用颜色单独表达状态」的邻近风险 | 分区索引不要用状态 Badge：用中性 `Classes="meta"` 文案（"已接入/待接入"）或专用 `CapabilityBadge`；凭据用"已保存/未保存"文字 + 中性色（不用 Done/NotStarted 词表）；需要新增词表时先在 DECISION_LOG 登记 |

### P3

| 位置 | 问题 | 建议 |
|---|---|---|
| `Views/V2/Console/ConsoleView.axaml:290-292` + `ConsoleItems.cs:269-319` | 凭据掩码正确（`PasswordChar="*"`、`SecretInput` 仅此一处绑定），但**反射断言只扫 2 个对象**（`V2ConsoleUiTests.cs:199-211`：`row` 与 `console`）——不扫其它行、`ProviderProfiles/NetworkProfiles/ExportHistory` 行、`Shell` VM、也不扫视觉树。当前无泄漏，但"所有 public string 不含 secret"的说法只对 2 个对象成立 | 递归扫整个 VM 对象图（含嵌套集合）＋渲染树 `TextBox.Text/TextBlock.Text/ToolTip`；把 secret 写进一个"陷阱属性"验证扫描能抓到（负向测试） |
| `ConsoleViewModel.cs:1120-1154` | 秘密只在 `catch (InvalidOperationException or SidecarException)` 与成功/typed 失败路径清空；若控制器抛其它异常（如 `ArgumentException`/`TimeoutException`）`finally` 里不清 | 把 `row.ClearSecretInput()` 移入 `finally` |
| `ConsoleViewModel.cs:1721-1741` / `:1778-1815` | 刷新后重建行集合，但 `SelectedProvider/SelectedNetwork` 仅在为 `null` 时重新选中（`:1737`,`:1804`）→ 保存/刷新后"当前 Provider"指向已脱离集合的旧行、无 `IsSelected` 高亮（功能仍可用因 id 未变） | 刷新时按 `ProfileId` 重映射选中项 |
| `ConsoleViewModel.cs:470-486` | 轮询间隔写死 1s（B-4 是可注入 750ms）；两处轮询（Console 1s、Batch 750ms）各自读同一 `IRunController` | 抽 `IRunProjectionPoller`（可注入间隔）供 Console/Batch 共用（见跨分支 §1） |
| `ConsoleViewModel.cs:92-93`（注释「未接入分区（①④⑤⑥⑦）」）、`:108-111`（`CapabilityText` 仍写"能力待接入"，而 CreateChapter 已真实） | 注释/文案陈旧（① 是真实分区） | 更新注释；`CapabilityText` 改为"走 Core CreateChapter"（与 B-1 D-11 一致） |
| `ConsoleViewModel.cs:546` / `:1831-1833` | 用户可见文本用 `Snapshot.LastError` / `StatusLine`。`IHostController.cs:32-41` 明确 `LastError` 是"code only, never a message/path/credential"，`HostViewSnapshot` 注释"Deliberately free of OS paths"，所以**当前合规**；但这条保证只靠文档，若 Host 侧回归塞入 message，Console 会把路径直接显示（诊断区已刻意不用 `ErrorMessage`，`D-10`） | 加 UI 侧防御：只接受 `^[A-Z0-9_]+$` 的 code，否则显示通用文案 + 记录到日志通道 |

---

## 三、V11R-B-4 问题清单

### P1

| 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|
| `Views/V2/Studio/Controls/StudioBatchControls.cs:65`（`_viewModel.Rows.CollectionChanged += (_,_) => Rebuild();`）＋ `:58-64`（`Projection` 变化也 `Rebuild`）＋ `:92-202`（`Rebuild` 全量清空/重建 header+rows+cells）；数据侧 `ViewModels/V2/Studio/StudioBatchViewModel.cs:658-675`（`Rows.Clear()` 后逐行 `Rows.Add(...)`）；轮询 `:339`（750ms）、`StudioBatchControls.cs:589-602` | **每次轮询把矩阵全量重建 ~N+2 次并因此丢失滚动位置**：`ApplyProjection` 先 `Clear()`（触发 1 次 Rebuild）再逐行 `Add`（每行触发 1 次 Rebuild，24 行 = 24 次），随后 `Raise(nameof(Projection))` 再 1 次 → 每 tick ≈ 26 次 `Rebuild`，每次创建 `24 rows × 10 cells` = 240 个 `Border+TextBlock` → **≈6,240 控件/750ms**；真实 240 页 Run（FUSION §1 的 240 页场景）为 241 次 × 2,400 控件。且 `Rebuild()` 清空 `_rowsHost` 并替换 ScrollViewer 内容 → **滚动偏移被重置为 0，矩阵实际无法保持滚动**（焦点也每次丢失）。**复现**：打开 Batch（24 行投影）→ 滚动矩阵到中部 → 等一个 poll（≤750ms）→ 回到顶部；同时 CPU/GC 抖动。**用户后果**：240 页批次矩阵无法浏览，且拖动/框选被高频重建打断 | SCREEN_SPECS §4「矩阵行=页…框选/Shift/双击下钻」；FUSION §2.2「切换保持 selection 与滚动位置」；DESIGN_SYSTEM §7（不得整块重刷） | 数据层改为一次性通知（`ProjectionChanged` 事件/批处理 `Reset` 后一次），或在 VM 内 `BeginUpdate/EndUpdate`；视图改为**增量 diff**（按 `(pageId,stage)` 复用 cell 控件）或对行做虚拟化；`Rebuild` 前后保存/恢复 `Scroll.Offset`；补测试：写入一次真实 `Scroll.Offset`（非 0）→ 一次 poll → 断言 offset 保持且 `CellControls` 实例引用未全部变化 |
| `ViewModels/V2/Studio/StudioBatchViewModel.cs:1228-1241`（`BuildActions` 仅按 `_dataSource.IsWired` 置 `IsEnabled`）、`:1095-1125`（`BuildScope` 在 `Selected` 但页集为空、或 `CurrentPage` 但无当前页时**回落到 chapter**）、`:1191-1225`（`ExecuteActionCoreAsync` 直接用 `_scope` 拼命令） | **作用域静默扩大**：当 `Scope=选中` 而共享 `SelectedPageIds` 变空（`ApplyProjection` 合并后选中页/阶段从投影消失、step_flow 列变化、行集变化都会触发；`SyncSelectionToSharedModel` `:923-934` 会把空集写回共享模型），批量动作按钮**仍然 enabled**，点下去得到 `translate_selected` + `{kind:"chapter", chapter_id:…}` —— 以"选中"命令语义对**整章**发起 Run；`Scope=当前页` 且 `CurrentPageId=null` 同理会落到整章。**复现**：选中 2 页 → 作用域切「选中」→ 让下一份投影不含这些页/阶段（或换 5 列投影）→ 点「翻译 · 选中 0 页」→ 观察 `StartRunRequests[0]` 的 Command=`translate_selected`、Scope.kind=`chapter` | FUSION §1 硬规则 1（共享选择/作用域）＋ §2.3 作用域后缀＋ §9.6「看不出作用域的操作」；SCREEN_SPECS §4「批量动作带作用域后缀」 | `BuildScope` 在 `Selected/CurrentPage` 无法物化时返回 `null`（拒绝执行并就地说明），**不得回落 chapter**；`BuildActions` 的 `IsEnabled` 纳入 `CanMaterializeScope`（`Selected⇒页集非空`、`CurrentPage⇒有当前页`）；补测试：作用域选中+空选择 → 动作禁用/零调用；修正后 B-3 遗留的 `SelectionSummary` 优先级一并处理 |

### P2

| 位置 | 问题 | 依据 | 建议修法 |
|---|---|---|---|
| `StudioBatchViewModel.cs:1002`（`StartRunAsync` → `Guid.NewGuid().ToString("N")`）、`:1047`（`RetryFailedTargetsAsync(_runId, Guid.NewGuid()…)`） | **R-08 明文禁止的"静默生成幂等键"**：契约 §5.2 R-08「缺失/空白幂等键一律本地 typed 拒绝（`INVALID_REQUEST`），**禁止静默生成**——否则无法区分"用户重试"与"重复提交"」。StartRun 每次点击生成新 GUID ⇒ 双击/重试对 Core 是两次不同提交（幂等保护失效）；RetryFailed 同。且与 B-2 同契约的处理**相反**（B-2 要求操作者手填，缺失零调用） | 契约 §5.2 R-08；`README §4.5` 亦未声明此偏差 | 二选一并写进契约：①Batch 提供幂等键输入（与 Console 一致）；或②由 Lead 在 DECISION_LOG 裁定"UI 生成的键语义=新意图"，并让 A-2 契约接受 —— 但在裁定前应改为"显式键 + 双击保护（进行中禁用）"，并补测试断言键的来源与复用行为 |
| `StudioBatchViewModel.cs:554-603`（`RefreshAsync` 只 `catch (OperationCanceledException)`）；`StudioBatchControls.cs:588`（`_timer.Tick += _ = viewModel.TickAsync()`）；`StudioWorkspaceView.axaml.cs:194-198,226`（`_ = SyncBatchAsync()`） | **错误路径不完备 + 未观察异常**：数据源/控制器抛 `InvalidOperationException`/`SidecarException`（同仓 `LibraryViewModel.cs:525` 按这两类捕获）时异常逸出 `RefreshAsync`；`TickAsync` 由 `DispatcherTimer` fire-and-forget，UI 线程上未处理异常可致崩溃；`ApplyMode` 里 `SyncBatchAsync` 同样 fire-and-forget | AC3「error 就地 + 可重试」 | `RefreshAsync` 捕获同上两类 → `State=Error/Partial` + `_errorText`（typed）+ 保留上次投影；timer tick 加 try/catch + 计数降级；`SyncBatchAsync` 包 try/catch |
| `Views/V2/Studio/Controls/StudioBatchControls.cs:589-602` + `StudioWorkspaceView.axaml.cs:79-99,218-229` | **"仅 Batch 可见时轮询"不成立**：Page/Batch 两个 workspace 都常驻 `content.Children`，只切 `IsVisible`（`:82-83`,`:222-223`），`IsVisible=false` 不会 `DetachedFromVisualTree` → 定时器在整个 Studio 空间（含 Page 模式编辑时）持续 750ms 轮询 2 次 IPC。README §2「仅 Batch 可见时轮询」为不实声明 | 资源/证据可信度 | 用 `IsVisibleChanged` 或 `Activate/Deactivate` 控制启停；证据改为"仅 Batch 模式轮询"并加测试 |
| `StudioBatchControls.cs:481-513`（Gate 确认卡：无 `Focus()`、无 Esc、Scrim 只覆盖 `matrixHost`） | **门禁确认不是模态**：卡内无默认焦点/焦点陷阱/`Esc=取消`（`CancelGate` 只能点按钮）；且 `GateModal` 挂在 `matrixHost`（`StudioBatchControls.cs:543-547`）→ 顶部 StageRail、CountChips、动作条、RunStrip 仍可点击（用户可在"未确认影响面"时点另一个动作/暂停 Run）。对比 B-2 用的是壳层 `ConfirmModal`（默认焦点=取消、Esc 关闭） | DESIGN_SYSTEM §6.2 `Modal`（默认焦点取消、Esc 关闭）、§8 浮层焦点规则；§9 反面清单 | 复用壳层 `ConfirmModal`（B-1 已有）或给 Gate 卡补：打开即聚焦「取消」、焦点陷阱、`Esc=CancelGate`、Scrim 覆盖整个 Batch workspace |
| `StudioBatchControls.cs:371-381`（RunStrip「停止」直接 `StopAsync()`，无确认）、`README §4.5` | **Stop Run 无二次确认**，与同一 Supervisor（ui-shell）在 B-2 的处理相反（B-2 D-4 明确把"停止 Run"纳入确认 Modal 并写影响面："进行中的步骤会终止，未完成页需重跑"）。同一产品两个空间对同一破坏性命令两种纪律 | DESIGN_SYSTEM §6.2「中断恢复」Modal；B-2 `DEVIATIONS D-4` | Batch 的停止也走确认（可复用 Gate 确认或壳层 ConfirmModal），文案沿用 B-2 的影响面措辞；补 cancel 零调用断言 |
| `StudioBatchControls.cs:107,150`（`FontSize = 10`）＋ `:23-24,122,246,362,427,561,640`（`CellSize=18`、`PageColumnWidth=62`、`HeaderHeight=30`、`Height=22/40/24`、`Width=360/560`）；`Views/V2/Studio/StudioTheme.axaml:335-416`（新增大量 `Padding="8,0|6,2|0,1…"`、`Height="20"`） | **AC4 在 B-4 继续不成立，且新增"不在刻度上"的字号**：`FontSize=10` 既不是 `{DynamicResource Nm.FontSize.*}`，也不在 DESIGN_SYSTEM §3 的六档（11/12/13/14/18/24）——矩阵表头/单元格符号低于最小 Meta 11px；几何/间距仍为裸值（上轮 B-3 同类）。B-4 无 conformance 扫描测试，只有 `build.log 0 warning`（与裸值无关） | 契约 §2.2 硬规则（XAML/C# 禁止裸字号/裸间距）、AC4；DESIGN_SYSTEM §3 | 字号改 `Nm.FontSize.Xs`；尺寸/间距迁 `Nm.Size/ Padding/Space` 或登记 §2.4 例外；补 Studio 专用 conformance 扫描（XAML+C#，排除 tests），覆盖 `FontSize =`、`new Thickness`、`Width/Height =` |
| `Views/V2/Studio/Controls/StudioBatchControls.cs:716-730`（`RefreshChrome`：`_emptyHost.IsVisible = !HasData`，`_startButton.IsEnabled = IsWired`）、`StudioBatchViewModel.cs:389-411` | **Error 态被当成 Empty 态**：投影读取失败时（`State=Error`，`ShowsError=true`）仍显示空态卡片，且主按钮是「开始处理」（`StartProcessingAsync` → `translate_all` StartRun）且 enabled —— 错误态的正确动作应是"重试读取"，当前交互可能让用户在读取失败时**发起新 Run** | AC3 六态（error 就地 + 可重试）；DESIGN_SYSTEM §6.5 `EmptyState`「一句话+一个主操作」不适用于 error | `RefreshChrome` 按 `State` 分支：Error → 标题/详情 + 「重试」按钮（`RefreshAsync`），隐藏/禁用「开始处理」；Partial 保留数据 + banner |
| 证据：`verification/V11R-B-4/gate.json`（`impact_text` 字段）＋ `V2StudioBatchTests.cs:298-310` | **证据字段写死、与实现不符**：`writer.WriteString("impact_text","门禁未清 · 作用域 · 仍然执行会产生不完整产物")` 是字面量，真实 `GateImpactText` = `门禁未清（失败 2 · 阻塞 1） · 作用域 · 选中 1 页 · 仍然执行会产生不完整产物`。与上轮 B-3 `modal_default_focus` 同类（Studio 两支连续出现） | 证据须由被测值写出（禁字面量） | 改为 `batch.GateImpactText` 并加断言（含 `GateWarning` 与 `ScopeSuffix` 片段） |
| 证据：`drilldown.json` `scroll_kept`；`V2StudioBatchTests.cs:380,399` | **`scroll_kept: true` 是 0==0 同义反复**：`scrollBefore` 在矩阵从未滚动时采集（`Offset`=0），下钻前后都断言相等；从未设置非 0 偏移，也未触发一次 poll（配合上面 P1，真实滚动会被 poll 重置） | 上轮 B-1 同类（手写状态再断言） | 渲染后设 `Matrix.Scroll.Offset = (0, 240)` → 下钻/切模式/一次 poll → 断言仍为 240 |
| `V2StudioBatchTests.cs:180`、`:400` | **两条恒真/占位断言**：`:180` `cell.State == Stale && cell.State is null` 不可能成立；`:400` `Assert.Contains("NOT_WIRED","NOT_WIRED")`（注释自称"placeholder assertion keeps evidence honest"）——这不是诚实，是无断言 | 测试质量/证据可信度 | 删除占位断言；`:180` 改为"投影不含 stale 时不存在 stale 单元格"的真实断言（`Assert.DoesNotContain(cells, c => c.State == StudioStateKind.Stale)` 前先确保数据可产生 stale 或改为断言状态映射表无 stale 来源） |
| `verification/V11R-B-4/design-system-usage.md`（7 行，6 处 `System.Object[]`） | **生成器缺陷未修且被复制传播**（上轮 B-3 同文件同缺陷）：README 宣称"40 token / 62 类"无法从证据审计 | 修生成器（`object[]` → `string.Join(",", list.Select(x=>x.ToString()))`）后重生成 B-3/B-4 两份 |
| `verification/V11R-B-3/artifacts/*.png`（本 commit 改写了 14 张 B-3 证据） | **跨任务证据改写**：B-4 commit 内重跑了 B-3 截图（queued `·` 修复后的再渲染），但没有更新 B-3 README/JSON、也没有独立 fix commit → B-3 的证据与描述脱节（`states.json` 仍是旧值语义），滚动证据链断裂 | 契约 §7「证据与 commit 对应」 | 把 B-3 证据重生成放进 B-3 返修 commit；B-4 commit 只含 B-4 证据 |

### P3

| 位置 | 问题 | 建议 |
|---|---|---|
| `V2StudioBatchTests.cs:266`（`var startsBefore = view is not null ? vm.Batch.Selection : null;` 未使用） | 死变量 + 证据 `starts_before_gate` 实际取自 `requestCount` | 删除；证据字段改真实来源 |
| `V2StudioBatchTests.cs:473`（`Assert.True(Matrix.ColumnCount >= 5)` at 1280） | 弱断言（列数恒 10，与布局无关；不能证明 1280 不崩/不挤压） | 断言矩阵可视区/行高/无横向裁切，或至少 `Scroll.Viewport.Width > 0` |
| `StudioBatchViewModel.cs:1228-1241`（`GateWarningGlyph/Class => "✗"/"●"` 硬编码）＋ `StudioBatchControls.cs:279`（StageRail 里 `✗{Failed}` 硬编码）＋ `StudioRunDataSource`/`StudioStates` | 符号来源仍是 3 处（Studio 本地 `StudioStates`、Batch 硬编码、shell `NmStatusInfo`）；`main` 的 DS 已交付 `Controls/StatusCatalog` + `Nm.State.Symbol.*`（r1 时尚未交付） | INT-1 统一上收 DS `StatusCatalog`，删除三份本地表 |
| `StudioRunDataSource.cs:105-141`（`NotWiredRunDataSource`）+ `StudioBatchViewModel.cs:338`（`host as IRunController`） | 因 `IHostController : IRunController`，该降级分支在冻结接口下**不可达**；README §4.1「用于 Host 无 IRunController」的表述会误导（真正不可达的是"接口未继承"的假想宿主） | README 改为"接口恒在，保留 seam 以便 A-2 回退"，或删除 seam 并让 `IsWired` 恒真 |
| `StudioRunControllerDataSource.cs:99-104` | `counts.X ?? rows.Count(state)`：Core 未给计数时用行状态推导——可接受（数据源仍为 Core），但会掩盖"Core 未提供该计数" | 保留推导时在 tooltip/抽屉注明"计数由投影行推导" |
| `StudioWorkspaceView.axaml.cs:145-167`（`OnKeyDown` 始终把 **Page** VM 交给 `StudioKeyboard.Handle`）；`:140-141`；`StudioBatchControls.cs:67-74`（Enter 下钻只在 Matrix 或其子元素获焦时生效） | **Batch 键盘半残**：Batch 模式下 J/K/Esc 仍作用于 Page VM（Esc 会去收检查器/清选区而不是关 Gate/Drawer）；矩阵无方向键导航；`Esc` 不能关 Gate/Drawer；README AC5「矩阵单元格可聚焦、Enter 下钻」只在手动 `TryBeginFocus`+Matrix 子焦点成立，未见测试 | 引入 Batch 键盘映射（方向键/Enter/Esc→Gate/Drawer）并按 `Mode` 分派；shell 集成时由 `IWorkspaceView.TryHandleKey` 仲裁 |
| `StudioWorkspaceView.axaml.cs:298-311`（Gate/Drawer 之外的关闭路径） | Drawer 只能点「关闭」；Esc 无效（同上） | 同上 |
| `StudioBatchControls.cs:44-49`（ScrollViewer 双层滚动）+ `:100-118`（表头与行数据分属两个 Panel，横向滚动时表头不跟随） | 列多/窄窗时表头与单元格横向错位（1600 下不明显；1280/1024 会） | 表头放进同一 ScrollViewer 或用 `Grid` 共享列宽；补窄窗截图断言 |
| `StudioBatchControls.cs:104-109`（18px 列宽 + 完整 stage 标签 + FontSize 10） | 表头文字被裁成 3 字符（截图中 `det/ocr/col/ter/tra/seg/mas/inp/ren/rev`），可读性依赖 StageRail 与 tooltip | 用缩写表（`StudioStages.Abbreviation`）或 `TextTrimming` + 明确 tooltip；可在 DESIGN 裁定 |

---

## 四、已核实正确的关键点

### V11R-B-2（逐条对应 Lead 的关注点）
1. **凭据永不回显（结构正确）**：`ConsoleView.axaml:290-292` 仅一个 `PasswordChar="*"` 的瞬态输入框绑定 `SecretInput`；`CredentialTargetRowViewModel` 只暴露 Core 的 `credential_state`（`ConsoleItems.cs:259-266`）；保存后无论 Core 结果如何都 `ClearSecretInput()`（`ConsoleViewModel.cs:1130-1131`，catch 分支 `:1146`）；通知文案只含目标名（`:1136`,`:1141`）。测试断言：secret 确实经 seam 发送一次 → 输入清空 → **反射扫 `row`+`console` 的所有 public string 不含 secret**（`V2ConsoleUiTests.cs:190-211`）；截图 `01/02` 为掩码输入 + 「已保存/未保存」。
2. **错误不含路径/secret（注入真的生效）**：注入 `SettingsProfileResult(Failed,"INVALID_REQUEST", @"C:\Users\someone\secret-config.json sk-live-should-not-leak")` → 断言通知含 `INVALID_REQUEST` 且**不含 `C:\` 与 `sk-live`**（`V2ConsoleUiTests.cs:376-395`）；生产侧只用 typed 映射（`DescribeSettingsFailure`/`DescribeCredentialFailure`，`:1916-1940`），全文无 `result.Message` 渲染；诊断区刻意不渲染 `ErrorMessage`（`:1830-1833`，D-10）。该注入不是空转：`SettingsProfileResult` 的 message 确实被塞入且被丢弃。
3. **危险确认默认取消/影响面/阻断态零写**：删除 Provider（`ConsoleViewModel.cs:1061-1070`）、清除密钥（`:1156-1164`）、停止 Run（`:654-664`）、⑤清理缓存/⑥创建/删除备份（`:1661-1687`，`CanConfirm:false` + `BlockedReason` + 影响面）全部走壳层 `ConfirmRequest`；壳层 `ConfirmModal` 打开即 `CancelButton.Focus()`（B-1 `ConfirmModal.axaml.cs:55`，默认焦点=取消 ✓），Esc 取消（B-1 `AppShellViewModel.cs:591-600`）。测试断言：取消/Esc → `ProviderDeletes` 空（`:235-242`）、阻断确认点击后只出提示（`:320-324`）、缓存确认 `ConfirmCanConfirm=false` 且原因含"能力待接入"（`:303-309`）。
4. **9 分区无假开关**：XAML 里 `CheckBox` 仅出现在 ②Provider 表单（能力勾选/启用）与 ③网络表单（TLS/回退/确认关闭 TLS）——都是真实 draft（`:248-252,263,406-409`）；④设备/⑦插件只有 `AlertBanner`+前置条件，无任何 toggle；⑤⑥只有"（能力待接入）"按钮且确认被禁；`④⑦` 截图可核对。测试逐分区断言 `IsNotWiredSection` 与文案含"能力待接入"（`V2ConsoleUiTests.cs:112-127`）。
5. **①任务与队列用对 IRunController 且 R-08 缺失零调用**：`IHostController : IReaderProgressSink, IRunController, IAsyncDisposable`（`IHostController.cs:97`）→ `_controller.GetRunSnapshotAsync/GetTaskProjectionAsync/ControlRunAsync/ResumeBlockedRunAsync/RetryFailedTargetsAsync` 即经 `IRunController`（契约允许的宿主继承形式，位置正确）。R-08：`Restart` 缺键 → 本地拒 + `return`（`ConsoleViewModel.cs:648-652`），测试断言 `Assert.Empty(controller.ControlRunRequests)`（`:427-431`）；`RetryFailed` 缺键同样本地拒（`:742-746`）；Stop 确认后 `ControlRunAsync(runId, Stop, null)`（`:662`，R-08 允许非 Restart 传 null）。
6. **无 run_id 不伪造**：`LoadRunAsync` 空 id → 提示并返回（`:488-495`）；测试断言零 `RunSnapshotRequests`、无行、提示含 run_id（`:457-475`）。
7. **真实投影逐字段**：状态/命令/作用域/进度/计数/当前步骤/阻塞原因/step_flow/rows 全部来自 `TaskProjectionInfo`（`ApplyRun :549-606`），缺失计数渲染「—」（`DescribeCounts :626-637`）；截图 `07` 可见 `chapter: ch-0-1 / 50% / 总 2 · 完成 1 · 等待 1`。
8. **令牌纪律（XAML/C#）在本卡干净**：Console 两个新文件无裸色/字号/圆角/阴影/渐变（我自己正则扫描：0 命中）；C# 无 `new Thickness`/尺寸字面量；仅有 2 处 `Margin="0,2"`；conformance JSON 已含 `Views/V2/Console/ConsoleView.axaml`（23 文件/49 token）。

### V11R-B-4（逐条对应 Lead 的关注点）
1. **矩阵列真来自 `GetTaskProjection.step_flow`**：`RunControllerRunDataSource.Map` 直接取 `info.StepFlow`（`:48-55`）→ `StudioRunProjection.Stages` → `ApplyProjection` 用 `projection.Columns` 建 cell（`StudioBatchViewModel.cs:656-675`）；测试用两份**不同阶段集**投影断言 10 列/240 cells 与 5 列/30 cells，且断言 `Matrix.ColumnCount`（`V2StudioBatchTests.cs:118-140`）；`matrix.json` 的 `stage_columns_five_projection:5`、`column_keys` 由真实 `StageColumns` 写出 ✓ —— **动态列证据是真的**。
2. **七态符号一致，queued = `·`**：`StudioStateKind.cs:29` `Queued => "·"`；未知 Core 状态 → `null`（`:102-116`）→ 渲染 `–`/"无投影数据"（`StudioBatchCellViewModel.Glyph :72`、`StudioRunPageRow.StageState :35-41`）；`states.json.queued_glyph` 由代码写出（`V2StudioBatchTests.cs:195`）；测试断言 `·/✗/▲/●` 与 `FromProjectionStatus("bogus_status") is null`（`:173-196`）。
3. **门禁未清时批量动作真的零执行（含 Cancel 断言）**：`ExecuteActionAsync` 在 `HasGateWarning` 时只设 `_pendingGateAction` + 开卡并 `return false`（`StudioBatchViewModel.cs:1148-1169`）；测试在 execute 后 `Assert.Empty(StartRunRequests)`（`:281`），`CancelGate()` 后再次 `Assert.Empty`（`:285`），再次 execute 仍 re-open 且空（`:290-291`），确认后才 `Assert.Single` 且 Command/Scope 精确（`:292-296`）—— **Cancel 零执行有断言**（`gate.json` 未单独记录该字段，建议补）。
4. **投影合并保选择（VM 层）**：`ApplyProjection` 先按 `(PageId, StageType)` 快照旧选中，重建后回填（`StudioBatchViewModel.cs:649-686`）；`Poll_...` 测试在第二份投影后断言 `SelectedPageIds.Single()` 与对应 cell `IsSelected`（`V2StudioBatchTests.cs:326-334`）；`run-controls.json.selection_survived_poll` 有测试支撑。**（注意：控件层每次重建会丢滚动/焦点，见 P1-1）**
5. **双向下钻两侧都有真实接线**：Batch→Page：`RequestDrillToPage` 事件 → `StudioWorkspaceView.DrillToPageAsync`（`SelectPageAsync` + `HighlightPipelineStage` + `RequestMode(Page)`，`:200-205`）；Page→Batch：流水线步骤点击 `ActivatePipelineStage` → `PipelineStageActivated` → `Batch.HighlightStage(stage, CurrentPageId)` + `SyncBatchAsync` + `RequestMode(Batch)`（`:207-216`）；Page 的流水线带在 B-4 已改为**投影动态阶段**（`StudioPageViewModel.cs:1281-1302`，无投影时退回 10 标准阶段显示"无投影数据"）；测试断言两方向目标值与 filter 保持（`V2StudioBatchTests.cs:373-415`）。
6. **CountChips 诚实**：过期/待确认在投影中无口径 → `Count=null` → 显示「—」、`IsAvailable=false`，点击只给说明不筛选（`StudioBatchViewModel.cs:739-776`；测试 `:208-216`）；`selection.json.stale_chip_unavailable` 有断言。
7. **空态真实 StartRun**：无 Run → EmptyState +「开始处理」→ `StartProcessingAsync` → `translate_all` 真实 `StartRunAsync` 后读取投影（`StudioBatchControls.cs:636-655,716-730`；测试 `:418-457`，`empty-state.json` 的 command 取自真实请求）。
8. **宿主与数据源方向**：`StudioBatchViewModel` 只经 `IRunController`（`_controller ?? host as IRunController`，`:338`），无 DB/文件/进程直连（grep 0 命中）；405 行 `StartRunAsync` 走 `RunStartRequest(command, scope, null, key)` 契约形状。

---

## 五、UNVERIFIED（只读环境不可确认）与建议验证

| 项 | 原因 | 建议 |
|---|---|---|
| 两条 pin 的 build/test log 真实性 | 未重跑（禁写 bin/obj） | 集成机重跑：B-2 预期 App 200/5；B-4 预期 App 185/5、`--filter V2Studio` 29/29，并 diff 计数 |
| **B-4 矩阵滚动/重建（P1-1）的运行期表现** | 由代码路径确定（`Rows.CollectionChanged→Rebuild` + ScrollViewer 内容替换），但 headless 下 `Scroll.Offset` 是否必然归零需实测 | 加临时诊断测试：设非 0 offset → `RefreshAsync` → 打印 offset 与 `CellControls` 引用是否变；若保留则降级为纯性能 P2 |
| B-4 作用域回落（P1-2）是否被 Core 拒绝 | 取决于 Core 对 `translate_selected`+`chapter` scope 的校验（typed 拒绝 or 接受） | 用 A-2/侧车跑一次 `translate_selected`+`kind=chapter`，确认是 `INVALID_REQUEST` 还是真的执行；无论哪种都需要 UI 侧拒绝 |
| B-2 重入 Console 轮询 | 代码确定"不重启"，但 `DispatcherTimer` 是否被别处重启需运行确认 | 测试：加载 Run → Ctrl+1 → Ctrl+3 → 等 2.5s → 断言 `IsRunPollingEnabled` 与投影读取次数增长（当前预期 0 增长） |
| 凭据/路径泄漏的"其它路径" | 已核 `Put/Save/Delete/Clear/Run/Diagnostics/Inject` 六类；`HostViewSnapshot.LastError` 的 typed 保证属 core-bridge | 让 Host 侧用带路径的 message 回归一次，验证 UI 是否仍只显示 code |
| 真实 Core E2E / DPI 三档 / 240 页真实矩阵性能 | 双方 NOT RUN | INT-1 用真实 sidecar + 240 页章节跑：矩阵滚动/框选/轮询 CPU 与内存，DPI 100/150/200 |

---

## 六、跨分支发现（本轮新增/升级）

1. **R-08 在两支被相反执行（必须由 Lead 裁定，非实现者可自行统一）**：Console 要求操作者手填幂等键、缺失零调用（合规）；Batch 对 `StartRun`/`RetryFailed` 静默 `Guid.NewGuid()`（违反 R-08"禁止静默生成"）。同一用户在产品里会遇到"控制台要先填键、矩阵自动生成"，且矩阵的双击/重试**失去幂等保护**。建议：统一为"显式键 + 进行中禁用重入"，或由 Lead 在 DECISION_LOG 明确改写 R-08 并同步契约 §5.2 与 B-2/B-4 证据。
2. **Run 投影视图仍然两套（B-2 的"待订阅"承诺未兑现）**：B-2 用自有 `DispatcherTimer`(1s)+`ConsoleStatusText` 映射+一次性 `RunSnapshotInfo`；B-4 用可注入 `IRunDataSource`(750ms)+`StudioStates` 映射+`StudioRunProjection`。B-2 README/AC 说"B-4 共享 Run 视图合入后改为订阅"，B-4 已交付但 Console 未改 → **同一 Run 在两个空间显示状态文案/计数来源可能不同**。INT-1 必须先收敛成单一投影源（建议：B-4 的 `RunControllerRunDataSource` + 一个可注入 `RunProjectionPoller` 服务，Console/Batch 共用；停止/重试/恢复也走同一控制面）。
3. **Stop Run 纪律分裂**：Console 有影响面确认+可取消；Batch RunStrip 直接调 `StopAsync()`。必须在 INT-1 前统一（建议采用 B-2 D-4 的更保守口径）。
4. **B-4 pin 仍携带 B-3 的未修 P1/P2**：`StudioRegionOverlay.cs:105` 仍 `IsHitTestVisible=false`（画布 Region 鼠标选中/hover 不可用）、`StudioLeaveModal.cs:42` 仍透明错误文案、Modal 仍无焦点（该 pin 上三处均未变）→ B-3 返修必须在 B-4 之后 rebase 或一起修，否则"矩阵→Page 下钻后用户点不中 Region"的组合体验会直接暴露。
5. **键盘路由仍无仲裁**：B-4 的 Batch 键盘半残（P3 表）+ B-3 的 Tab 占用 + B-1 shell 的 TopLevel tunnel 全局 `Tab/Esc`（上轮 §5.3）→ 三方叠加后 `Esc/Tab/Enter/J/K` 的归属互斥。INT-1 的 `IWorkspaceView.TryHandleKey` 必须在切 MainWindow 默认入口**之前**落地，否则用户第一次进 Studio 就会发现 Esc 关错东西。
6. **DS 已前进，UI 两支未上收**：`main` 现已交付 `NewManga.DesignSystem.Controls.StatusCatalog/StatusKind/NmStatusSymbols`（含 `· ◐ ● ✗ ▲ ▨ – ○ ▮` 单一源）、`Nm.Size.Breakpoint.{Full,Compact,Narrow}`、`Nm.Icon.*`、`Nm.Size.Skeleton*`、`Nm.Border.Focus`、`Controls/Skeleton` 等（commit `468c9066d`/`e070cc074`）。这意味着上轮/B-4 的"DS 未交付所以本地实现"理由**已过期**；B-2 的 `NmStatusInfo`、B-3/B-4 的 `StudioStates`、B-4 的硬编码 `✗/●`、三套断点（1200/1400/1600/1280）、两处"loading 无骨架"都应在 INT-1 上收时一次清掉 —— 否则 L3 视觉一致性无法成立。
7. **证据管线仍是薄弱环节（跨两轮）**：`design-system-usage.md` 生成器缺陷在 B-3、B-4 连续重复；`gate.json` 写死 impact_text；`drilldown.json` 0==0；B-4 commit 改写 B-3 的 14 张证据 PNG；`main` 工作区仍有 B-3 证据未提交改动。建议 Lead 在 INT-1 前给证据生成器加一条 gate：**证据 JSON 中禁止字面量-backed 字段**（只能从被测对象读取），并在 CI 里比对证据目录与 pin 的一致性。

---

## 七、最终判断

### 是否可合入 main
- **V11R-B-2**：**可有条件合入**（无 P1）。合入前需：①修"轮询切回恢复/离开分区停"其中至少"切回恢复"并更正两处证据声明；②分区/凭据改用非状态词表（或 Lead 裁决允许）；③返修 commit 后重生成证据。当前 main 已含其代码但未接线默认入口，不构成产品风险。
- **V11R-B-4**：**当前不可视为可合入**（P1×2 + 2 处证据不实 + 恒真断言）。必须修 ①矩阵重建/滚动（去 `CollectionChanged→Rebuild` 风暴、保 offset、增量/虚拟化）；②`BuildScope` 不回落 chapter + 动作启用纳入作用域可物化；③门禁卡真模态（默认取消/Esc/覆盖整块/焦点）；④RunStrip Stop 确认（与 B-2 对齐）；⑤`FontSize=10` 与裸几何迁 token 或登记；⑥证据用真实值 + 删占位断言 + 修生成器。返修后**建议重新审查 pin**（例如 `v11r/ui-studio` 上新的 B-4-fix commit），并同时复核 B-3 P1 是否随返修关闭。
- **共同前提**：在 INT-1（`IWorkspaceView` + 单一 selection + 键盘仲裁 + Run 单一投影源 + MainWindow 切换）完成前，**不要切默认入口**；main 现有合并可保留为"未接线代码"。

### 是否达到 L3 里程碑：**否**
理由（比上轮更明确）：
1. B-4 有 2 个 P1（矩阵不可滚动/重建风暴、作用域静默扩大）与证据不实项，B-2 有功能声明不实项 → "独立审查通过"未满足。
2. L3 的两条硬要求（跨模式共享 selection 的**真实作用域**、Batch↔Page 上下文保留）当前只被"VM 层"证明：作用域存在回落缺陷、滚动/焦点在轮询下丢失、键盘无归属 → 尚未形成可验收的端到端证据。
3. INT-1 的四个前置（`IWorkspaceView` 缺失、双 selection、键盘仲裁、Run 投影双源）全部未做；DS 的 `StatusCatalog/breakpoint/icon/skeleton` 已就绪但 UI 未上收，视觉一致性无法在 L3 收敛。
4. 真实 Core E2E、240 页矩阵性能、DPI 三档仍未验证（两支均 NOT RUN）。

**建议下一步**：Lead 按上述 P1 派返修（B-4 优先，含 B-3 P1 合并修复），返修 pin 落地后再发起一次"B-2+B-4 复审 + INT-1 预演"；在 INT-1 预演通过前，维持"main 含代码、默认入口仍旧壳"的状态。**建议修复后重新审查的 pin**：B-2 = 返修 head（`v11r/ui-shell` 新 commit）；B-4 = `v11r/ui-studio` 新 B-4-fix head（要求同时包含 B-3 P1 修复与两份证据重生成）。
