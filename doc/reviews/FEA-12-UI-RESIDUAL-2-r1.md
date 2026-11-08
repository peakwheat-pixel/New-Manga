# FEA-12-UI-RESIDUAL-2 Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（session `897f3928-3df7-4336-ad18-036b486ecc6a`；**未参与本卡实现**；DSH 派发） |
| 审查模式 | 只读审查 + 临时变异（工作树内破坏 → 跑测试 → 逐字节复原），未 commit/push，未改交付 |
| 被审 head | **`85356c22a`**（parent `b7c63bc50`；`main`） |
| diff 范围 | `git diff --name-status b7c63bc50 85356c22a` = 5 文件、+461/−8（numstat：LibraryViewModel 14/2、TrashViewModel 33/3、FakeHostController 33/3、TrashUiTests 342/0、V2ShellUiTests 39/0） |
| 收尾 | 开始/结束 `git status --short` 均为空；5 个被改文件 worktree blob 与 `HEAD:` blob 逐一相同（`7add89c56399`/`4750eba4bcc3`/`3c2bf0492d2c`/`3bdbbd29bae3`/`4323805e0d27`） |
| 落盘说明 | 报告正文由该独立子代理产出；DSH 落盘并在末尾追加「DSH findings 处置」段，未改动其判定与证据。 |

## 结论

**approved** —— **P0=0 / P1=0 / P2=1 / P3=5**；A/B/A′ 三条修复的行为与判别力均经独立复跑证实（7 组变异中 6 组 RED，逐字节复原 sha256 MATCH 后全部复绿），无阻断项；唯一 P2 是交付 head 未含 `verification/FEA-12-UI-RESIDUAL-2/**` 变异日志（需 DSH 集成时归档，本报告 §2 已独立补齐等价证据）。

## 0. 实跑命令与结果（本机真跑）

| 命令 | 结果 |
|---|---|
| `dotnet test ...NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~TrashUiTests\|FullyQualifiedName~V2ShellUiTests"` | **74 通过 / 0 失败 / 0 跳过**（EXIT 0；基线 1 次 + 每组变异复原后各 1 次，共 8 次全绿） |
| `dotnet test ...NewManga.App.Tests.csproj -c Release`（全量 App） | **通过 778 / 失败 0 / 跳过 7 / 总计 785**（EXIT 0，2m58s） |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`（全量 .NET） | **EXIT 0**；分项目 21+38+253+117+31+286+167+778 = **1691 通过 / 0 失败 / 96 跳过（总 1787）** |
| `verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，EXIT 0 |
| `check.ps1`（默认 + `-TaskPath doc/tasks/FEA-12-UI-RESIDUAL-2.md`） | `PASS (3 warnings)` ×2，EXIT 0 |
| `generate_api_inventory.py --check` | EXIT 0 |
| `git diff --check b7c63bc50 85356c22a` | 空 |

**复跑注意（reviewer 踩到并已纠正的坑）**：`Copy-Item` 复原会保留 pristine 旧 mtime，MSBuild 增量构建会跳过重编译、继续跑变异版二进制（首次复原后仍 3 RED）。所有「复绿」均在强制重编译（touch mtime）后取得，并以 worktree blob == HEAD blob 复核。

## 1. AC 逐条判定

### AC-R1 恢复成功后书架一致 —— **MET**
- 测试 `TrashUiTests.RestoreFromRecycleBin_ThroughTheRealCommands_ReputsTheBookOnTheShelf`（`TrashUiTests.cs:958`）。
- 真实入口链：`ShowRecycleBinCommand` → 选中 `book-0` → `Trash.RestoreCommand`（回收站「恢复」按钮绑定）→ `CloseRecycleBinCommand`。
- 关键断言：预置前 `DoesNotContain(AllBooks, book-0)`、`RefreshCalls==0`、`"3 / 3 作品"`（`:972-974`）；恢复后 `RefreshCalls==1 && Trash.Items.Count==1`（`:984-987`）；返回书架后 `Contains(Books, book-0)`、`Contains(AllBooks, book-0)`、`Books.Count==4`、`AllBooks.Count==4`、`"4 / 4 作品"`、文案不含「回收站」（`:992-997`）。
- 断言落在 **VM 集合/文案**而非帧数；fake 回填开关（默认关闭）+ 触发前预置快照使其不可能靠 fake 特性假绿。判别：M1 → RED。

### AC-R2 部分成功 / 全部失败边界 —— **MET**
- 测试 `RestoreFailureBoundary_OnlySuccessRefreshes_AndBothCountsStayHonest`（`:1007`）。
- 全失败：`RefreshCalls==0`（`:1034`）、行保留 2、逐项 `HasConflict`、`StatusMessage` 以「已恢复 0 项」开头且含「2 项未恢复」、通知无 `Done` 有 `Failed`。部分成功：`RefreshCalls==1`、剩 `book-0` 带冲突、文案同时含「已恢复 1 项」与「1 项未恢复」。
- 判别：M2 → 全失败分支 RED；M1 → 部分成功分支 RED。

### AC-R3 空态与分页诚实性 —— **MET**（附 P3-01）
- 测试 `EmptyStateIsHonestOnlyWhenThereIsNeitherRowNorCursor`（`:1161`）：0 行 + 无 cursor → `IsEmpty/ShowEmptyState==true`、`ShowList/HasMore==false`；READ 能力缺失 → `ShowCapabilityState==true`、`ShowList==false`、`ShowEmptyState==false`、`IsEmpty==false`；probe 失败 → 同上。
- cursor 诚实：T3/T4 清空首页后 `HasMore==true`，`LoadMoreAsync()` 以原 cursor 发第二帧，`TrashListCursors == [null, "cursor-opaque-1"]`（`:1104`、`:1150`）。
- 判别：M3、M4 各 2 RED；**M6a（处方变异）0 RED** → P3-01（`ShowList` 的能力/probe 短路子句在本 fake 下不可判别；`IsEmpty` 同一子句由 M6b 4 RED 判别）。

### AC-R4 两条删除路径同构覆盖 —— **MET**
- 恢复路径 `RestoreEmptyingTheFirstPage_KeepsTheListAndTheCursorHonest`（`:1078`）；彻底删除路径 `PermanentDeleteEmptyingTheFirstPage_KeepsTheListAndTheCursorHonest`（`:1116`，走 `BeginPermanentDeleteAsync` → `UnderstandIrrecoverable` → `ConfirmDeleteCommand`，并断 `DeletePermanently` 恰好 2 帧 `:1146`）。两条路径在 M3/M4 下各自 RED，确非「只修一条」。

### AC-R5 门禁与禁止面 —— **MET（门禁面）**；证据归档面见 P2-01
- 定向 74/0/0；全量 App 778 通过 / 0 失败 / 7 跳过（总 785）；全量 .NET 1691 通过 / 0 失败 / 96 跳过（总 1787）→「passed 只增不减」成立（+8 全为新增用例；其余项目零 diff）。
- pins 18/18；check PASS(3w)×2；API inventory EXIT 0；`git diff --name-only -- src/ doc/contracts doc/tasks/FEA-12-UI.md verification/FEA-12-UI` 空；`git diff --check` 空。
- 0 帧 `library_purge_trash` / 0 帧批量彻底删除：新增代码无此类调用，既有 `FullFlow_NeverEmitsPurgeOrBatchPermanentDeleteFrames`（`TrashUiTests.cs:424`）全量中仍绿。

### AC-R6 计数文案双向一致（A′）—— **MET**
- 测试 `BookCountText_FollowsTheRecycleBinView_BothWays`（`:1196`）：进入 → `"回收站"`（`:1207`）+ `PropertyChanged` 含 `BookCountText`/`ListStatusText`（`:1208-1209`）；返回（按钮路径）含通知（`:1218`）、值 == `$"{Books.Count} / {AllBooks.Count} 作品"` 且 `"4 / 4 作品"`、不含「回收站」。
- Esc 路径 `V2ShellUiTests.RecycleBin_BookCountText_FollowsTheEscPathBackToTheShelf`（`V2ShellUiTests.cs:622`）：`HandleKeyForTest(Key.Escape)` 走真实漏斗（`AppShellV2.axaml.cs:167` → `AppShellViewModel.HandleKey` → `SurfaceBack` → `Library.CloseRecycleBin`，`AppShellViewModel.cs:1221-1224`），文案先收「回收站」再收「4 / 4 作品」。
- 交错栅栏 `ReturningToTheShelfAfterAnInRecycleBinRefresh_NeverLeavesTheRecycleBinCopy`（`:1228`）：回收站内完成 refresh（`RefreshCalls==1`）时 bar 立即显示「回收站」，返回后必须重发并清掉残留。判别：M5 → 3 RED。

## 2. 判别性变异实测

流程：pristine 副本 → 改工作树 → `dotnet test`（定向，不加 `--no-build`）→ 从 pristine 复制回 → `Get-FileHash` 比对 → touch mtime 强制重编译 → 复绿。复原指纹：`TrashViewModel.cs = B47532BC…AF3DF1`、`LibraryViewModel.cs = 98F4FBF2…E5C9BA`（每次 `MATCH=True`，`git status --short` 为空）。

| 变异 | 破坏点 | 目标用例 | 实测 RED | 复原 | 复绿 |
|---|---|---|---|---|---|
| **M1** A 修复 | `TrashViewModel.cs:625-628` 整块删除 `await _onBooksRestored()` | T1/T2(partial)/T7 | **失败 3 / 通过 71** | MATCH | 74/0/0 |
| **M2** A 边界 | 去掉 `result.SucceededIds.Count > 0 &&`，无条件 await | T2 全失败分支 | **失败 1 / 通过 73**（`RefreshCalls` 0→1） | MATCH | 74/0/0 |
| **M3** B(IsEmpty) | `IsEmpty` 去掉 `&& _nextCursor is null` | T3、T4 | **失败 2 / 通过 72** | MATCH | 74/0/0 |
| **M4** B(ShowList) | `ShowList` 改回 `Items.Count > 0` | T3、T4 | **失败 2 / 通过 72** | MATCH | 74/0/0 |
| **M5** A′ | setter 去掉两个 `nameof` | T6、T7、V2Shell Esc | **失败 3 / 通过 71** | MATCH | 74/0/0 |
| **M6a**（处方变异） | `ShowList` 去掉 `!_capabilityMissing` | T5/能力态 | **失败 0 / 通过 74 → 未被判别** | MATCH | 74/0/0 |
| **M6b**（等价更强） | `IsEmpty` 去掉 `!_capabilityMissing && !_probeFailed` | T5 + 3 既有能力态用例 | **失败 4 / 通过 70** | MATCH | 74/0/0 |

**M6a 未变红机理**（已读源码确认）：能力缺失态（`TrashViewModel.cs:479-484`）与 probe 失败态（`:455-469`）都在描画列表前 `return` ⇒ `Items.Count==0 && _nextCursor==null` ⇒ `(Items.Count > 0 || HasMore)` 恒 false，即使 `ShowList` 丢掉能力守卫仍为 false。唯一可暴露场景是「已加载行 + `ReloadAsync` 期间能力翻转为缺失」（`ReloadAsync:418-428` 不清 `Items`），仓内无测试走该路径 ⇒ 该子句只有结构性保护、无判别性保护（P3-01）。

## 3. 正确性与风险

- **回调时序**：`await _onBooksRestored()` 位于 `RestoreSelectedAsync` 末尾（`TrashViewModel.cs:622-628`），在 generation 守卫（`:581-584`）与「无写入失败早退」（`:586-592`）之后、`RaiseStates()`（`:618`）之后；部分成功刷新、全失败不刷新，与卡面口径 1 逐字一致。
- **上下文**：`ConfigureAwait(true)`（`:627`）保留 UI 上下文；`RefreshAsync` 的集合变更仍在 UI 线程，headless 与生产一致。
- **fire-and-forget 异常面**：`RestoreCommand` 为 `_ = RestoreSelectedAsync()`；`RefreshAsync` 只捕获 `InvalidOperationException`/`SidecarException`（`LibraryViewModel.cs:703`），其他异常成为未观察异常（不崩，但书架静默旧数据）。恢复调用原本即有同样暴露面 → 非新增风险（P3-05）。
- **重入**：`RefreshAsync` 无重入闸（`RefreshCommand` `:96` 也不看 `IsLoading`），回调略微放大并发窗口；与移入 `:993`、撤销 `:1032` 同构（P3-05 备注）。
- **短路顺序**：`IsEmpty`（`:232-233`）、`ShowList`（`:243-244`）前缀守卫原样保留；`RaiseStates`（`:992-1002`）已含四属性，两条路径（恢复 `:618`、`RemoveDeletedRow:920`）复用。
- **`_nextCursor` 生命周期零改**：仅 `EnterAsync:378`、`ReloadAsync:425`、`Exit:395`、`LoadAsync:538` 触碰，diff 未改。
- **装配完整性**：全仓 `new TrashViewModel` 仅 2 处 —— 生产 `LibraryViewModel.cs:73`（已注入 `() => RefreshAsync()`）与测试 `TrashUiTests.cs:26`（null）。无第二生产构造点。

## 4. 超范围与契约/pin

- **diff ⊆ allowed_paths**：5 文件全部落在卡面 allowed_paths；无卡外文件。
- **禁止面零 diff**：`src/**`（Python）、`doc/contracts/**`、`doc/tasks/FEA-12-UI.md`、`verification/FEA-12-UI/**`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`IHostController.cs`、`ITrashController*`、`TrashModels.cs`、所有 `*.axaml`/`*.axaml.cs`、`*.csproj`/依赖/schema 均零改动。
- **死代码未删**：`RecycleRestoreCommand` 仍在 `LibraryViewModel.cs:111`、`:180`（L-3 保留，符合 DSH 裁决）；`RecyclePurgeCommand` 未被触碰。
- **契约/pin**：`verify_pins.ps1` 18/18 PASS；pin 目标为 `doc/plan/FEA-C*` 契约文件，本卡零字节改动 ⇒ 机械不可见。`generate_api_inventory.py --check` EXIT 0（App-only，无 Host/IPC 面变化）。
- **行文红线**：diff 内无「完全修复/全部关闭/功能完备/完全实现」等字样；L-2/L-3 未被宣称关闭。

## 5. 测试质量与 flaky 风险

- **纯增量**：`TrashUiTests.cs` 342/0、`V2ShellUiTests.cs` 39/0 —— 既有用例与断言零删除、零放宽；`FakeHostController` 改动为等价重构 + 新增**默认 false** 的 `RestoreRepopulatesSnapshot`（`:1697`，仅 `:1776-1792` 显式开启时回填），既有用例零扰动（全量 770 旧用例全绿佐证）。
- **断言强度**：T1 断 `Books`/`AllBooks`/`BookCountText`；T3/T4 断 `TrashListCursors`；T4 断真实 `DeletePermanently` 帧数 2。无「只断 `RefreshCalls`」弱断言。
- **fake 开关纪律**：T1 显式 `RestoreRepopulatesSnapshot = true` 且触发恢复前预置快照（`:964-971`）；其余用例默认 false。
- **隔离**：每用例自建 fake/library；`TrashBook0/1` 为不可变 record；无共享静态可变状态。
- **flaky 观察**：8 次定向全绿各 11–12 s，无抖动。薄弱点：T2(a) 等待谓词 `Trash.HasStatus`（`:1032`）在「正在恢复 N 项…」阶段已为 true（`TrashViewModel.cs:575-576` 先通知再 await）⇒ 若 fake 改真异步会变竞态（P3-02）；T7 的 `DoesNotContain("回收站", ListStatusText)`（`:1252`）恒真（空断言）；T1 用绝对 `RefreshCalls==0`（`:973`）绑定「启动复用快照」策略（低风险假 RED）。

## 6. Findings

**P0：无。P1：无。**

- **P2-01（P2）交付 head 未含本卡证据目录**：`verification/FEA-12-UI-RESIDUAL-2/**` 不存在 ⇒ AC-R5/I-4 的变异日志不可机械复核。不阻断（本报告 §2 已独立产出等价判别证据；卡面要求实现者不自行 commit，证据归档属 DSH 集成动作）。**建议 DSH 集成时归档 §2 + 运行日志并重签 EV。**
- **P3-01（P3）AC-R3 的 `ShowList` 能力/probe 短路栅栏没有判别力**：删掉 `ShowList` 的 `!_capabilityMissing`（乃至 `!_probeFailed`）后定向 74 全绿（M6a 0 RED）；机理见 §2。建议补「先 EnterAsync 得 2 行 → 能力翻转为 READ 缺失 → `await RefreshAsync()` → 断 `ShowList==false && ShowCapabilityState==true`」用例；若不加，须在卡/证据注明该子句为结构性保护。
- **P3-02（P3）T2(a) 等待谓词不判别**：`TrashUiTests.cs:1032` 等 `HasStatus`，该值在「正在恢复…」阶段即为真；建议改等 `Items.All(row => row.HasConflict)` 或显式完成信号。
- **P3-03（P3）A′ 的 `ListStatusText` 通知在 UI 上无消费者**：`LibraryViewModel.cs:442` 重发；全仓 XAML 无 `ListStatusText` 绑定（`LibraryView.axaml:17` 只绑 `BookCountText`）。无害防御性通知，符合 AC-R6 明文要求；仅提示「bar 文案」只由 `BookCountText` 承载。
- **P3-04（P3）交付说明把 App.Tests「总计」写成「passed」**：实测 `通过 778 / 跳过 7 / 总计 785`；全量 .NET「1691 passed / 0 failed / 96 skipped」精确（总 1787）。纯文档精度，不影响「+8 不降」结论。
- **P3-05（P3）回调异常面与 `RefreshAsync` 无重入闸（既有结构，窗口略增）**：位置 `TrashViewModel.cs:625-628`；`LibraryViewModel.cs:640-715` catch 仅两类异常。与移入/撤销同构，本卡未新增异常类型/未改并发语义；可选另卡（try/catch + `_notify` 或重入旗标）。

## 7. 未核实 / 不确定（reviewer 自陈）

1. **全量 pytest 未跑**（本卡 `src/**` 零 diff；留给 DSH 集成门禁）。2. 真实 Core/IPC 端到端未跑（全部 `FakeHostController` 驱动）。3. `0 行 + 有 cursor` 的布局观感未截图（卡面禁止改 XAML，不属本卡 AC）。4. 交付者本地 FEA-09 是否复原只能保证本机复核收尾 `git status` 为空。5. 未跑写入型治理命令（`task_ledger.py`）以免越权。6. `FluentResidual2VisualEvidenceTests` 已知 flaky，本次全量 .NET 一次通过（EXIT 0），未隔离复跑。7. M6a 结论时效性依赖 fake 的能力探针行为。

---

## DSH findings 处置（2026-11-08，裁决人=DSH）

| Finding | 处置 |
|---|---|
| **P2-01**（证据目录缺失） | **已处置**：DSH 集成时建立 `verification/FEA-12-UI-RESIDUAL-2/`，归档本报告 §2 变异证据、reviewer 运行日志、DSH 集成门禁日志（pytest/.NET/check/pins/API）、`EV.md`、`RESOURCE-MANIFEST.json`；`EV.md` 逐项登记「commit 填该文件所在提交」。 |
| **P3-01**（`ShowList` 能力守卫无判别力） | **保留为 P3 并写入卡 limitation L-4**：该子句现有结构性保护（源码守卫原样保留，diff 已核）；本轮不加测试（避免为一非阻断测试缺口再走一轮实现+复审），登记为后续候选（下一轮若开 `2C-RESIDUAL-1` 可顺带补）。**不得**据此声称 AC-R3 的「回归栅栏」有变异级判别。 |
| **P3-02**（T2 等待谓词） | **保留为 P3**（L-4 同条登记）：当前确定性由 fake 同步语义保证；若 fake 改异步须同步收紧谓词。 |
| **P3-03**（`ListStatusText` 无 UI 消费者） | **接受并记录**：AC-R6 明文要求该通知，属防御性；「bar 文案」以 `BookCountText` 为准。 |
| **P3-04**（App.Tests 口径） | **已更正**：卡面与 EV 统一写「778 通过 / 7 跳过 / 总 785」；全量 .NET 写「1691 通过 / 0 失败 / 96 跳过 / 总 1787」。 |
| **P3-05**（回调异常面/重入） | **保留为 P3（L-5）**：与移入/撤销同构的既有结构，本卡未劣化；另卡可选。 |

**AC 判定维持**：AC-R1…AC-R6 全部 MET（AC-R3 的短路子句判别力缺口按 P3-01 如实降级表述，不写「回归栅栏已被变异钉住」）。
