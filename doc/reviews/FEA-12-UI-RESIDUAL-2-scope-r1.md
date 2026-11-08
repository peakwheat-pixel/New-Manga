# FEA-12-UI-RESIDUAL-2 scope review r1（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（session `402ec34a-ae7b-4651-88f5-a6c87e3d1171`；未参与实现） |
| 审查模式 | 只读（read/grep/glob + 只读 git；未运行测试、未改任何文件） |
| 被审 head | `54e5d69db`（main；工作树 clean；AHEAD=0） |
| 结论 | **`READY-TO-FREEZE`**（前提：`allowed_paths` 必须含 `FakeHostController.cs`，否则 AC-A 只能退化为「调用次数」弱断言） |
| 并行第二轮 | session `986a9e4c-38d1-43a5-806c-563349be04ce`（另一独立上下文只读子代理，同题、同被审 head `54e5d69db`）：**同为 `READY-TO-FREEZE`**，并独立发现第三缺陷 **A′**（`IsRecycleBinView` setter 不重发 `BookCountText`/`ListStatusText`）→ 见本文末「第二轮评审补充」；DSH 已裁决并入本卡（AC-R6）。两轮结论无冲突。 |
| 落盘说明 | 报告正文由上述独立子代理产出；DSH 仅落盘并追加「DSH 裁决」段，未改动其判定与证据。 |

## 任务来源（DSH 发起）

上一轮 handoff §26 判「可推进项耗尽」；本轮两个并行独立只读审计推翻该结论并给出 App-only 候选。DSH 亲自逐行复核后，判定命中 AUTORUN §2 判据 **(a) 用户可见价值且无需解冻契约**，故派本 scope review 定稿卡面。

## 结论

**`READY-TO-FREEZE`。**

## 缺陷复核（独立验证，未照抄 DSH 声称）

### 缺陷 A —— 成立（回收站内「恢复」成功后书架不刷新）

- `TrashViewModel.RestoreSelectedAsync`（`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs:545-599`）：成功/部分成功后只做 `Items.Remove` + `_selectionOrder`/`_loaded` 清理（`:572-579`），末尾 `RaiseStates()`（`:596`）不发任何「书架已变」信号；无 event、无回调、无 controller 重读。
- 唯一活动入口：`Views/V2/Library/RecycleBinView.axaml:120` 绑定 `Trash.RestoreCommand`（`TrashViewModel.cs:79/114`）。全仓 grep `RecycleRestoreCommand` 仅 2 处，均在 `LibraryViewModel.cs:104`、`:173` → 确认**死代码**（注意：`RecyclePurgeCommand` **是**活的，绑在 `RecycleBinView.axaml:124`，**不得**一并删除）。
- 书架不重读：`LibraryViewModel.CloseRecycleBin()`（`:886-895`）只切 `IsRecycleBinView` + `Trash.Exit()`；`InitializeAsync`（`:610-623`）被 `_initialized` 守卫，`AppShellViewModel.cs:705`/`:1312` 的二次调用均为空操作；`_allBooks` 仅在 `RefreshAsync`（`:628-654`）重建。对照：移入回收站 `:981`、撤销 `:1020` 均 `await RefreshAsync()`。
- 结论：恢复后返回书架仍见进入回收站前的快照，直到用户手动刷新/导入等其它路径。

### 缺陷 B —— 成立，且范围比 DSH 声称更宽

- `TrashViewModel.cs:216 IsEmpty` 无 cursor 条件、`:220 HasMore`、`:222 ShowList` 要求 `Items.Count > 0`；`RecycleBinView.axaml:84` 的列表容器内含「加载更多」（`:88-92` 受 `HasMore` 控制）⇒ Items 清空即整块隐藏。
- 两处删行都不清 `_nextCursor`（仅 `LoadAsync:516` 赋值、`ReloadAsync:396-406` 清）：恢复 `:572-579`、彻底删除 `RemoveDeletedRow:877-893` ⇒ 首页清空 + cursor 非空时显示「回收站是空的」（`RecycleBinView.axaml:57-62`）且「加载更多」消失。**该缺陷同样适用于彻底删除路径**，修 B 须一并覆盖。

## 关键核实（决定卡面）

1. **Fake 现状**：`FakeHostController.RefreshBooksAsync`（`:68-83`）只 `RefreshCalls++` / `LifecycleLog.Add("refresh")`，**不动 `Snapshot`**；`RestoreFromTrashAsync`（`:1752-1765`）**不回填** `Snapshot.Books`，而 `MoveToTrashAsync`（`:1738-1747`）会移除 ⇒ 非对称。因此「恢复后书架出现该书」要么给 fake 加**可选、默认关闭**的回填（镜像 `:1738-1747`），要么测试内预置 `fake.Snapshot = fake.Snapshot with { Books = … }`（`Snapshot` 可写，`:24`，须在触发恢复前预置）。**只断言 `RefreshCalls` 不够**：空实现也能骗过计数。
2. **`ScriptedTrashPages` 足够**：`:1675` 队列 + `:1709-1725` 取值点，可脚本化 page1{entries, cursor:"c1"} → 断言 `HasMore==true`、`TrashListCursors` 第二帧为 `"c1"`；无需改 fake 分页。
3. **既有断言不会被新增一次 ListBooks 打破**：`StartupReadDedupTests:29/44/61` 的 `RefreshCalls` 精确值来自独立 fake 且不碰回收站；`TrashUiTests` 的恢复用例直接 `new TrashViewModel(…)`（`:26`）不经 Library，且 `:443`/`:842` 断的是 ListTrash 帧数；`V2ShellUiTests:566-611` 无 `RefreshCalls` 断言；`ImportExportUiTests:157-189` 用相对断言。**唯一雷区**：若改成 `CloseRecycleBin` 无条件刷新或顺手 `Trash.RefreshAsync()`，会撞 `TrashUiTests:842` 的 `ListTrash==2`。
4. **实现点建议**：用**可 await 的回调**——`TrashViewModel` 构造加第 4 个可选参 `Func<Task>? onBooksRestored = null`（生产唯一构造点 `LibraryViewModel.cs:70`；测试唯一直接构造点 `TrashUiTests.cs:26`；默认值保证不破编译），在 `SucceededIds.Count > 0` 时 `await _onBooksRestored()`（部分成功也刷、全失败不刷）。**不要用 `event`**：订阅方 async void → headless 断言竞态。脏标记 + `CloseRecycleBin` 刷新帧数更小但 `void` 方法只能 fire-and-forget，可测性更差，仅作备选。**不新增 `IHostController` 成员** ⇒ C-07 零变更。
5. **B 的最小修成立**：`IsEmpty => … && Items.Count == 0 && _nextCursor is null`、`ShowList => … && (Items.Count > 0 || HasMore)`；恢复（`:596`）与删除（`:890`）都已 `RaiseStates()`，而 `RaiseStates` 已含 `IsEmpty/HasMore/ShowList/ShowEmptyState`（`:969-970`）⇒ 无需改通知管线、**无需改 XAML**。与 `FEA-12-UI.md:132` AC1 不冲突而是**补齐**（AC1 明写「`nextCursor` 存在时出现『加载更多』」，现况在该边角违背 AC1）。但 AC1 已 `<<MET>>` 且有 pin 证据，**不得改写冻结 AC/证据**，新语义只能写进新卡新 AC。

## AC 建议（reviewer 原文）

1. **AC-A1（成功同步）**：恢复成功后 `RefreshBooksAsync` 恰 +1，被恢复书重回 `library.AllBooks`/`Books`，`Trash.Items` 不再含该书。
2. **AC-A2（部分/全失败边界）**：`SucceededIds>0 && FailedItems>0` → 刷新 1 次、逐项原因保留、文案含「已恢复 X 项」与「Y 项未恢复」；`SucceededIds==0` → `RefreshCalls` 不变且不称成功。
3. **AC-B1（首页清空 + 有下一页）**：page1 带 cursor，恢复/彻底删除清空全部行后 `IsEmpty==false`、`ShowEmptyState==false`、`ShowList==true`、`HasMore==true`，再 `LoadMoreAsync()` 以原 cursor 发第二帧。
4. **AC-B2（真空态不回归）**：`[0 条 + cursor==null]` → `IsEmpty/ShowEmptyState==true`、`ShowList==false`、`HasMore==false`；失败态与能力缺失态仍不显示空态。
5. **AC-C（门禁）**：相关测试套全通过；全量 .NET passed 不减；`git diff --name-only -- src/ doc/contracts` 为空；0 帧 `library_purge_trash`、0 帧批量彻底删除。

## allowed_paths（reviewer 建议，最小）

- `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs`
- `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`
- `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`
- `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`（仅恢复回填，默认关闭）
- 可选：`apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs`（窗口级断言）

（明确排除：`RecycleBinView.axaml`、`doc/contracts/**`、`IHostController`/C-07、Python Core、`doc/tasks/FEA-12-UI.md` 冻结证据）

## 风险（reviewer 原文，≤5）

1. **AC-A 假绿**：fake 不改 Snapshot、restore 不回填 → 可选回填 + 预置 Snapshot 双管，断言落到 `Books` 内容而非仅帧数。
2. **顺手多刷一帧**：撞 `TrashUiTests:842`、`StartupReadDedupTests:29/44` → 只在 restore success 路径、只在 Library 侧刷。
3. **竞态**：`event` + async void 使恢复后断言不稳 → await 回调（构造注入）。
4. **语义漂移 vs 冻结证据**：改 `IsEmpty/ShowList` 触碰「空态」定义，易被写成「改 FEA-12-UI AC1」→ 新卡新 AC，`[0条,有cursor]` 行为显式定死，`FEA-12-UI.md` 与 pin 不动。
5. **只修恢复不修彻底删除**：`RemoveDeletedRow`（`:877-893`）同构缺陷会被漏掉 → AC-B1 明确两条路径都断言。

## UNFREEZE？

**不需要。** App-only、复用既有 `IHostController.RefreshBooksAsync`，C-07/wire/Python 全零变更，不触碰任何冻结契约。**但**：不得改写 `doc/tasks/FEA-12-UI.md` 的 AC1 与已 pin 证据；应以新 Task 卡 + 新证据在 `REBASELINE_PLAN`/`STATUS` 登记（Lead 治理动作，非实现者路径）。

## 不确定（reviewer 自陈）

- `FakeHostController.RestoreFromTrashAsync` 无条件回填是否打破既有用例：只读定位了恢复/撤销相关断言（`TrashUiTests:346-400`/`479-497` 未见书架计数断言），**未实跑** → 故建议默认关闭的开关而非无条件回填。
- 未实跑任何测试；全量基线数字需 Lead 实跑确认。
- 未通读 `LibraryUiTests.cs`（grep 显示其无 `RefreshCalls` 断言）。

---

## DSH 裁决（2026-11-08，裁决人=DSH）

依据：独立 scope review 上述判定 + DSH 本会话一手复核（`git blame`/ancestry、`RecycleBinView.axaml:120` 绑定、`CloseRecycleBin`、`_allBooks` 重建路径）+ 本轮 Lead 实跑全量门禁（pytest **3390/10**、.NET **1683/0/96**、pins 18/18、check PASS）确认基线。

| 争议点 | Review 建议 | **DSH 裁决** |
|---|---|---|
| 判据归属 | (a) 用户可见价值、App-only | **接受**：恢复的唯一目的即把作品放回书架；旧行为使用户判为「恢复没生效」。立项不触碰任何冻结契约。 |
| 缺陷 B 范围 | 恢复与彻底删除两条路径同构 | **接受**：AC-B1 必须两条路径各有判别断言；不得只修恢复。 |
| 实现方案 | 构造注入 `Func<Task>? onBooksRestored`，不用 event | **接受**：可 await、headless 可断言；`TrashViewModel` 两个构造点均不受影响；不新增 `IHostController` 成员。**避免** `CloseRecycleBin` 无条件刷新（帧数雷区）。 |
| Fake 支持 | 可选**默认关闭**的回填开关 + 预置 Snapshot 双管 | **接受**：默认关闭保证既有用例零扰动；新用例显式开启。 |
| 死代码 `RecycleRestoreCommand` | 确认死代码但 `RecyclePurgeCommand` 是活的 | **裁决：本卡不删死代码**（清死代码属治理清理，与缺陷修复不同域，避免扩大口）；登记 P3 于卡面，未来需要时另卡。 |
| 空态修复方式 | `IsEmpty` 加 `_nextCursor is null`；`ShowList` 加 `|| HasMore`；不改 XAML、不自动重载 | **接受**：最小且可判定；「加载更多」留在 `ShowList` 内即恢复可达。 |
| 冻结 AC/证据 | 不得改写 `FEA-12-UI.md` AC1 与 pin | **接受**：本卡只新增自己的 AC；`doc/tasks/FEA-12-UI.md` 字节零改动。 |
| allowed_paths | 4 个必要 + 1 可选 | **接受并定稿**（见卡面；5 个 App/测试文件 + 卡/评审/handoff/证据路径）。 |
| UNFREEZE | 不需要 | **接受**：0 pin。 |
| 行文口径 | — | **冻结**：不得写「回收站已完全修复 / UI L1–L10 全部关闭」；只写本卡两条缺陷的行为修复与保留 limitation（L1/L2/L3/L8 OUT 不变、L3 真机 NOT_RUN）。 |

---

## 第二轮评审补充（session `986a9e4c-38d1-43a5-806c-563349be04ce`，独立上下文只读）

同题、同被审 head `54e5d69db`，结论同为 **`READY-TO-FREEZE`**。其与第一轮的差异/增益（DSH 已逐条复核）：

### 增益 1：第三缺陷 A′（DSH 裁决并入本卡）

- **事实**：`LibraryViewModel.IsRecycleBinView` setter（`LibraryViewModel.cs:418-433`）只重发 `ShowGrid/ShowSideDetail/ShowOverlayDetail/ShowPageBulkBar/ShowBooksGrid`，**不重发** `BookCountText`/`ListStatusText`；而 `BookCountText`（`:598-600`）取值依赖 `IsRecycleBinView`，文案绑定在**常驻** library bar（`Views/V2/Library/LibraryView.axaml:17`）。
- **后果**：① 进入回收站时 bar 仍显示「N / M 作品」（应显示「回收站」）；② 本卡修复后刷新发生在回收站内（`RefreshAsync` 的 `finally` → `RaiseListStates()` 会重发 `BookCountText`，此时 `IsRecycleBinView==true` ⇒ 文案变「回收站」），返回书架后 setter 不再重发 ⇒ bar **停在「回收站」**。故若不修 A′，本卡 AC 中「`BookCountText` 与 Core 一致」不可 MET。
- **DSH 裁决**：**并入本卡**（新增 **AC-R6**）；修法=setter 的 `OnPropertyChanged` 补 `nameof(BookCountText)` 与 `nameof(ListStatusText)`（一行；`LibraryViewModel.cs` 已在 allowed_paths 内，无 XAML 改动）。既有测试对 `BookCountText` 零断言（`grep BookCountText tests/` 命中 0），回归风险低。

### 增益 2：更精确的方案否决项（DSH 采纳）

- `CloseRecycleBin` 是 **void 同步**方法且被 Esc 同步调用（`AppShellViewModel.cs:1221-1224`），在其中刷新只能 fire-and-forget → 不可确定性断言 ⇒ **否决**该方案。
- 改 `HostController.WriteTrashAsync` 会让「移入」「撤销」变 2 帧（它们已自行刷新）⇒ **否决**。
- 回调位置建议：`RestoreSelectedAsync` 末尾（`:598` 之后、generation 守卫与全失败早退之后）`await` 注入回调；仓内先例 `ImportDockViewModel` 的 `afterImport`（装配于 `LibraryViewModel.cs:78`）与之一致。

### 增益 3：测试假绿陷阱（DSH 采纳为 AC 约束）

- **只断言 `RefreshCalls` 或 `Snapshot.Books` 会在「改动前」也 GREEN**（fake 的 `RefreshBooksAsync` 不动 Snapshot、`RestoreFromTrashAsync` 不回填，见 `FakeHostController.cs:68-83`/`:1752-1765`）。⇒ AC 必须钉在 **VM 集合/文案**（`Books`/`AllBooks`/`BookCountText`）上；fake 侧的「恢复回填」只能是**默认关闭**的测试支持开关，且必须在**触发恢复之前**预置快照。

### 增益 4：`RefreshAsync` 自动选中的副作用（DSH 裁决接受并登记）

- `RefreshAsync` 在 `snapshot.State == Ready` 且选择为空时自动 `SelectBookAsync(Books[0])`（`:656-672`）⇒ 本卡修复后返回书架可能出现「首本被选中」的既有同构行为（与移入回收站 `:981`、撤销 `:1020` 一致）。
- **DSH 裁决**：**接受**（不为此新增 `RefreshAsync` 参数或改写选中语义，避免扩大口）；登记为本卡 limitation **L-2**，并在 AC 中明确「断言 `Books`/`AllBooks`/`BookCountText`，不断言选中态为 null」。若实现者能在不扩域前提下自然规避，允许但不要求。

### 增益 5：能力态回归栅栏（DSH 采纳）

- `ShowList` 改动必须保持**短路顺序**：能力缺失态（`_capabilityMissing`）与 probe 失败态仍不得显示列表容器/空态（`TrashUiTests:80-92`、`:899-909` 断言 `ShowList=false`）。⇒ 写入 AC-R3 的回归栅栏。

### 第二轮自陈的不确定（保留，不视为结论）

未跑测试；`ShowList=true` + 0 行的布局观感未做截图验证；`FEA04CurrentAdapterTests` 金标未实跑；Core `list_trash_entries` 游标在条目被恢复后的跳行竞态未核 SQL（B 不承诺该语义）；未通读 `doc/09_COLLABORATION.md`。

