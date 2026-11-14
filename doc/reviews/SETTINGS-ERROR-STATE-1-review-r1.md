# SETTINGS-ERROR-STATE-1 独立复核（r1）

- **verdict**：**ACCEPT_WITH_LIMITATIONS**
- **审查者身份与来源**：DSH 子 agent `review-settings-error`，由根 Agent `lead` 派发；独立上下文（未参与该 Task 的实现或返修），只读被审 head，唯一写入为本报告。
- **被审 head**：`90dc51ded3482bb42b3d32e46f826ff9b201453d`（提交信息 `test(settings): 补设置页加载失败态的判别测试，闭合条件 3 矩阵唯一无覆盖格`；单父）
- **基线**：`4188014999edbe730bbb72027df0c63ad846450e`（`HEAD^`，已核对）
- **复核时间 / 环境**：2026-11-15，Windows / pwsh，.NET SDK 10.0.401，测试目标 `net9.0`，Avalonia headless。
- **一句话结论**：实现确实早已存在；3 个测试真实，且经我独立判别实验证明能因回退变红；`src/**` 零 diff。扣分全部在文档同步（Gate/矩阵/卡面/ledger）与测试判别的边界，不在产品代码，也不在“该格是否有测试”这个核心结论上。

## 0. 关键事实（先给出可复核的数字）

| 事实 | 命令/来源 | 结果 |
|---|---|---|
| 改动面 | `git show --stat HEAD` | 10 个文件，+334 / −18；其中测试 2 个文件（+115 / +10），其余为 doc/verification |
| 零生产代码 | `git diff 418801499..HEAD --stat -- apps/desktop-avalonia/src` | **空**（0 字符）；`HEAD` 亦无 src 改动 |
| 定向基线 | `dotnet test … --filter "FullyQualifiedName~SettingsErrorStateTests"` | **3 passed / 0 failed / 0 skipped**（约 0.7 s） |
| AC3 实验 | 见 §3 | 回退 catch → **2 failed / 1 passed**；已还原；重跑 3 passed |
| 视图级实验（我加做） | 见 §3 | 只回退视图 banner → **1 failed / 2 passed**；已还原；重跑 3 passed |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | PASS（3 warnings，与 four-pieces.log 一致） |

实现存在性（base 与 head 同一份 src）：

- `SettingsViewModel.LoadAsync`（`apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/SettingsViewModel.cs:139-171`）：
  `State = Loading` → try 内依次调用 `ListProviderProfilesAsync`（`:154`）/`ListNetworkProfilesAsync`（`:156`）/`ListBackupsAsync`（`:158`）/`ListCredentialTargetsAsync`（`:159`）→ catch（`:166-170`）设 `State = FluentPageState.Error`（`:168`）与 `Error = $"设置读取失败（{ex.GetType().Name}），可以重试。"`（`:169`）。
- `SettingsPageView.RenderState`（`apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs:688-706`）：
  `State == Error` 时 `_stateHost.Child = FluentUi.Banner(StatusKind.Failed, "设置错误", _viewModel.Error, "重试", () => _ = _viewModel.LoadAsync())`（`:698-701`）。
  `FluentUi.Banner` 用的是 `NewManga.DesignSystem.Controls.AlertBanner`（`Controls/FluentUi.cs:10,143-160`；注意 V2 Shell 另有一个同名 `AlertBanner`，不是这里用的那个），其内部 action Button 的 `Content = ActionText`、`IsVisible = !IsNullOrWhiteSpace(ActionText)`、`Click → ActionInvoked`（`src/NewManga.DesignSystem/Controls/Feedback.cs:136,141,187-188`），所以我确认“重试”按钮是真实存在且已接线的 Button（不是纯文本）。

⇒ “实现早已存在、本卡只补测试”这一说法**属实**。

## 1. 逐 AC 判定

| AC | 判定 | 依据 | 备注 |
|---|---|---|---|
| **AC1** VM 级 | **PASS** | `SettingsErrorStateTests.cs:35-46`：注入抛异常的 Host，`LoadAsync` 后断言 `State == Error`、Error 含“设置读取失败”“可以重试”“InvalidOperationException”；实跑 3 passed；我的 catch 实验令其变红（Expected: Error / Actual: Loading，`:42`） | 断言来自实现原文，不是猜的 |
| **AC2** 视图级 | **PASS（有保留）** | `SettingsErrorStateTests.cs:53-83`：真实 `FluentShell.CreateRoot` → `Navigate(Settings)` → 在 `SettingsPageView` 的**视觉树**里找 TextBlock/“重试” Button；我加做的“只回退视图 banner”实验令该测试单独变红（`:72`），AC1/对照测试仍绿 ⇒ 确为视图级，不是只看 VM 字段 | 只证明“视觉树里有文本/按钮”，未证明实际绘制可见、未点击、未断言按钮 `IsVisible`；且测试在导航前已把 VM 置为 Error，未区分“页面显示中失败→响应式出现”与“构造时已 Error→初始渲染”（见 P3-4） |
| **AC3** 判别力 | **PASS** | 我独立复现：回退 catch → 2 failed / 1 passed；还原后 3 passed、`src` diff 0（见 §3） | 与 README §3、commit message 的声称一致 |
| **AC4** 矩阵改判 | **基本满足，有缺陷** | 矩阵 `:62` 该格 ❌→✅，§5 `:160-170` 改写，Gate §15 `:191-205` 同步 | 但 `文件:行` 写错；§15 仍有 62/12/“补那 1 格”残留；见 P2-2/P3-1 |
| **AC5** 零回归 | **未独立验证** | 卡面/README/four-pieces.log 声称 App.Tests `950/0/11/961`（本卡前 947/0/11/958）；git diff 只显示新增 3 个测试；skip 属性未变（新测试无 skip） | 按指示未跑全量（约 5 分钟）；入库证据只有摘要行，无原始 `dotnet test` 输出（P3-6） |
| **AC6** 零生产代码 | **PASS** | `git diff 418801499..HEAD -- apps/desktop-avalonia/src` = 空；`git status --short` 在实验还原后为空 | 生产代码确实零改动 |

## 2. Findings

### P2-1 `allowed_paths` 与实际改动不一致（形式越界）

- **位置**：`doc/tasks/SETTINGS-ERROR-STATE-1.md:22-31`（frontmatter `allowed_paths`）。
- **证据**：`git show --stat HEAD` 修改了 `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md`，但该路径不在 `allowed_paths`；卡面 AC4（`:61-62`）本身要求同步 Gate §15。
- **影响**：范围声明与实际交付不一致。若按 `allowed_paths` 做集成/越界校验，这一提交会被判越界；卡面“只改 X”的承诺不可用。
- **建议**：把该路径加入 `allowed_paths`（可注明“AC4 要求”），或在卡面登记 DSH 的显式范围扩展。属于文档级修正，不涉及代码。

### P2-2 Gate §15 / 矩阵同步不完整，留下自相矛盾的数字

- **位置与证据**：
  - `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md:191` 仍写“`[AvaloniaFact]` 文件 **62 个**”，但 `git grep -l '\[AvaloniaFact\]'`：base `418801499` = 62，**HEAD = 63**（新增 `SettingsErrorStateTests.cs`）。
  - 同文 `:206` 仍写“只有 **12 格**被逐行核对断言”；矩阵 §3 新增的这一格明确标了【核对】，应为第 13 个。
  - 同文 `:208-209` 仍写“推进路径…/**补那 1 格**”，而 `:205` 已说“GUI 层的‘无覆盖’格已清零”——同一节内自相矛盾。
  - 矩阵 `:34`（§2）、`:88`（§4.1）仍是 `947/0/11/958`，`:190`（§7）仍写 12 格；而 §3/§5 已按本卡更新。矩阵头部 `:3` 仍称基线 `d86f185ca`，但 §3/§5 引用了 `d86f185ca` 之后才存在的测试。
- **影响**：Gate 结论区与矩阵内部数字/基线不一致；读者会以为“那 1 格还没补”、`[AvaloniaFact]` 文件数错、核对格数少 1。矩阵作为“快照”的基线声明也不再对 §3/§5 成立。
- **建议**：把 Gate `:191` 改 63、`:206` 改 13、删除或改写 `:208-209` 的“补那 1 格”；在矩阵标题或 §5 注明“§3/§5 于 `90dc51ded` 更新，§2/§4.1 为 `d86f185ca` 基线快照”；§7 的 12 格同步为 13（或明确统计口径）。

### P2-3 “真无覆盖 0 格 / 无覆盖格已清零”缺少“仅 13 类矩阵内”的限定

- **位置**：矩阵 §5.3 `:167`、§5.1 `:160-161`、§0 `:13-20`；Gate §15 `:204-205`。
- **证据**：
  - §0 的“不在本矩阵内”只列了其它测试项目、legacy shell、真机走查，**没有**列“回收站/命令面板/源恢复/沉浸 F11 等 AC1 之外的 GUI 流程”，§3 的 13 类流程中也没有这些行；这正是 `GATE3-COVERAGE-MATRIX` r2 R2-008、r3 R3-009 两次指出的限定缺失。
  - §5.1 自己仍保留 2 个 ⚠️ 格（书架只读 `[WritePolicySidecarFact]` → 本环境 NOT_RUN；设置快捷键仅有“非 Space 入口”一条）。
  - 因此“0 格”只在“13 类 × 4 页、以 ❌ 为口径”的范围内成立，不是“GUI 无缺口”。
- **影响**：读者可能把“GUI 层的‘无覆盖’缺口已清零”误读为 GUI 全覆盖；Gate 证据口径被夸大（虽然条件 3 仍判 NOT MET，这一点没有改变）。
- **建议**：在 §5.3 与 Gate `:205` 明确写“在 13 类矩阵内、按 ❌ 口径”；把 2 个 ⚠️ 格并列写在同一句；§0 增一句“GUI 仅覆盖 AC1 的 13 类，不含回收站/命令面板/源恢复/沉浸等”。

### P3-1 矩阵该格的 `文件:行` 写错

- **位置**：矩阵 `:62` 引用 `SettingsErrorStateTests.cs:44/:60`。
- **证据**：两个测试的方法声明在 `:35` 与 `:53`；`:44` 是 AC1 的第三条 assert，`:60` 是 AC2 的 `await shell.SettingsViewModel.LoadAsync();`。矩阵其它格（如 `FluentPageTests.cs:25`）使用的是方法声明行，口径不一致。
- **影响**：AC4 明确要求“带测试名 + 文件:行”，当前引用无法按行定位；属于可验证性缺陷。
- **建议**：改为 `:35/:53`（或属性行 `:34/:52`），并统一矩阵的“文件:行”口径。

### P3-2 `doc/TASK_LEDGER.md` 在 HEAD 上是过期生成物

- **位置**：`doc/TASK_LEDGER.md:9-16`。
- **证据**：提交内的 ledger 写 `task files 610 / tracked 609 / untracked 1 / non-terminal tracked 6`；我在 HEAD 只读运行生成器：`python tools/governance/task_ledger.py --diff` → `task files 610 (tracked 610, untracked drafts 0)`、`non-terminal 7 (tracked 7, untracked drafts 0)`。原因应是 ledger 在新 task 文件被 `git add` 之前生成，随后又把两者一起提交。
- **影响**：治理指标误报“1 个未跟踪草稿”；`check.ps1` 按文件扫描报 7 个非终态（PASS），不会发现这一自相矛盾。
- **建议**：重新 `python tools/governance/task_ledger.py --write` 后提交（或 amend），让 HEAD 自洽。

### P3-3 `SettingsLoadFailure` 只挂在 `ListProviderProfilesAsync`，测试与调用顺序耦合

- **位置**：`apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs:739-742`（抛异常）与 `:746-749`（注释）；`SettingsViewModel.cs:154-159`（四个 list 调用）。
- **证据**：只有 `ListProviderProfilesAsync` 真正抛；`LoadAsync` 当前**第一个**调用它，所以今天能稳定触发。若未来重排（例如先 `ListBackupsAsync`），fake 不会抛，AC1/AC2 会**假红**；注释写的是“the settings list calls throw”（复数），与实现不符。
- **影响**：这是“实现顺序巧合”而非“语义触发”。功能正常但重排调用顺序时，测试会错误地报红；反过来，若重排后仍保留 provider 调用，则不会漏测（不会假绿）。属于测试脆性与注释不准确。
- **建议**：让 fake 对四个设置列举调用统一抛（或提供一个“设置加载失败”的统一 seam）；注释改成实际行为；或在测试里断言 `ProviderProfileListCalls == 1` 以把“触发点”固定下来。

### P3-4 AC2 的“重试按钮”与对照测试判别力有边界

- **位置**：`SettingsErrorStateTests.cs:76-77`（按钮）、`:73`（“设置读取失败”）、`:90-114`（对照测试）；`SettingsPageView.cs:710`（`_notice` 也显示 Error）、`:117`（页面 ctor 自动 `_ = LoadAsync()`）；`Feedback.cs:187-188`。
- **证据/问题**：
  1. 按钮断言只查 `(button.Content as string) == "重试"`，未查 `IsVisible`/`IsEnabled`，也未点击。`AlertBanner.Apply()` 无论可见性都会设置 `Content`；若有人把按钮隐藏、或去掉 `ActionInvoked` 订阅（点击不再触发 `LoadAsync`），本测试仍绿。“用户可重试”没有被判别。
  2. “设置读取失败”这条断言也可能由工具栏 `_notice` 的文本满足（`SettingsPageView.cs:710` 在 Error 时把 Error 写入 `_notice`），因此 banner 的 **message** 并未被唯一钉住；“设置错误”标题是唯一能证明 banner 存在的断言。
  3. `HealthyLoad_DoesNotShowTheErrorBanner` 能防住“VM 永远 Error”“全新健康页也渲染错误 banner”，但**没有**覆盖 Error → Ready 的转换（例如“重试成功”后 banner 是否消失），也没有断言健康态是 `Ready`（只断言 `!= Error`）。
  4. 测试在 `Navigate` **之前**就 `await LoadAsync()` 把 VM 置为 Error，页面构造时的 `RenderState()` 因而就能画出 banner；这不能区分“页面已显示时失败 → 靠 `State/Error` 的 PropertyChanged 响应式渲染”与“构造时已 Error → 初始渲染”。真实 Host 是异步的（页面 ctor `:117` 的 fire-and-forget 才是主路径），若有人删掉 `PropertyChanged → RenderState` 订阅，本测试仍可能绿（初始渲染已经画过）。
- **影响**：AC2 的“错误态可见”成立，但“可重试/消息在 banner 上/成功后恢复/失败发生在页面已显示时能响应式出现”这几点没有被固定。
- **建议**：断言页面内存在 `AlertBanner`（或按 `AutomationProperties` 定位）且 `IsVisible`；点击“重试”后断言 `ProviderProfileListCalls` 增加或成功后 banner 消失；补一个“失败→修好→重试→Ready 且无 banner”的测试；再加一个“先导航到设置页、再让加载失败”的变体，以固定响应式路径。若认为超出本卡范围，至少在 README 的“边界”里写明。

### P3-5 卡面没有登记两次探针失败，且“交付与运行记录”仍写“尚无”

- **位置**：`doc/tasks/SETTINGS-ERROR-STATE-1.md:83`（AC3 行）、`:95-100`（交付与运行记录）。
- **证据**：卡面 AC3 只写了成功的“2 failed / 1 passed”和“已还原”，**没有**写“第一次 PowerShell `.Replace` 字符串被插值、探针未生效”和“第二次删掉 `ex` 引用导致 CS0168 编译失败”。这两次失败只出现在 `verification/SETTINGS-ERROR-STATE-1/README.md` §4 与 commit message。README §4 写得完整且自我批评（明确说“若就此收工会是假结论”），**没有淡化**。另外，卡面同一文件里已经有 3 passed / 950 的结果表，而 `:99` 仍写“实际测试：尚无”，自相矛盾。
- **影响**：只读卡面的读者会错过“探针没生效却被当成已验证”的风险教训；卡面作为 canonical task record 不完整。
- **建议**：在 AC3 行或“交付与运行记录”里登记两次失败与“第三次才得到真实结果”，并把“实际测试”改为“已跑，见 README/日志”；无需改写 README 的诚实表述。

### P3-6 AC5 的全量数字没有原始输出入库

- **位置**：`verification/SETTINGS-ERROR-STATE-1/four-pieces.log:15-16`、`verification/SETTINGS-ERROR-STATE-1/README.md` §3。
- **证据**：入库的是摘要行（“950 passed / 0 failed / 11 skipped / 961 total”），不是 `dotnet test` 原始尾部输出/退出码。我按指示未跑全量（约 5 分钟）；作为旁证，`dotnet test --list-tests` 只列出 957 个（因部分 sidecar skip 未出现在发现列表中，**不能**据此反证 961）。
- **影响**：AC5 的“零回归”无法从入库证据独立复核；只能靠命令可复现。与项目此前“实测输出而非源码推断”的证据纪律相比偏弱。
- **建议**：附原始 `dotnet test` 尾部（含 passed/failed/skipped/total 与 `EXIT`），或明确写“可复现命令、未存原始日志”。

## 3. 判别力实验记录（我亲自做的两次）

### 实验 A（AC3，按要求）

- **改了什么**：把 `SettingsViewModel.LoadAsync` 的 catch 由
  `State = FluentPageState.Error;` + `Error = $"设置读取失败（{ex.GetType().Name}），可以重试。";`
  改为 `Status = "PROBE swallowed " + ex.GetType().Name;`（保留 `ex` 引用，避免 CS0168；`State` 停在函数开头的 `Loading`）。
- **命令**：`cd apps/desktop-avalonia; dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Debug --filter "FullyQualifiedName~SettingsErrorStateTests" --nologo`
- **结果**：**失败 2 / 通过 1 / 总计 3**。
  - `LoadFailure_PutsTheViewModelInErrorState_WithRetryableMessage`：`Expected: Error / Actual: Loading`（`:42`）。
  - `LoadFailure_ShowsTheErrorBannerWithRetryAction`：`Assert.Contains() Failure`（`:72`，视觉树里没有“设置错误”）。
  - `HealthyLoad_DoesNotShowTheErrorBanner`：通过（它不依赖失败态）。
- **还原**：`git checkout -- apps/desktop-avalonia/src/NewManga.App/ViewModels/Fluent/SettingsViewModel.cs`；`git status --short` **空**；`git diff -- apps/desktop-avalonia/src` 为 0 字符；重跑同命令 → **3 passed**。

### 实验 B（我加做，验证 AC2 真是视图级）

- **改了什么**：只改视图，不动 VM——把 `SettingsPageView.RenderState` 的 Error 分支
  `_stateHost.Child = FluentUi.Banner(StatusKind.Failed, "设置错误", _viewModel.Error, "重试", …)` 换成 `_stateHost.Child = FluentUi.Text("PROBE no banner");`。
- **结果**：**失败 1 / 通过 2**；只有 `LoadFailure_ShowsTheErrorBannerWithRetryAction` 在 `:72` 变红，AC1 与对照测试仍绿 ⇒ AC2 确实在判别“视图是否渲染 banner”，不是只看 VM 字段。
- **还原**：`git checkout -- apps/desktop-avalonia/src/NewManga.App/Views/Fluent/SettingsPageView.cs`；`git status --short` **空**；`git diff -- apps/desktop-avalonia/src` 为 0；重跑 → **3 passed**。

**还原声明**：两次实验后 `git status --short` 均为空，`git diff 418801499..HEAD --stat -- apps/desktop-avalonia/src` 仍为空；后续只写出了本报告（`doc/reviews/SETTINGS-ERROR-STATE-1-review-r1.md`，未跟踪），没有其它写入。

## 4. 我没有验证的面

- **没有跑全量 App.Tests**（按交办要求；AC5 的 950/0/11/961 未独立复核，只有摘要级证据）。
- 没有逐格重审矩阵另外 12 个【核对】格与【摘要】格；只抽查了 `FluentPageTests.cs` 的行号约定，以及本卡两个测试。
- 没有审 Host/Core 的 111 个 skip（本卡不涉及）。
- 没有做像素级验证：headless 下只验证视觉树中的 `TextBlock`/`Button`，不能证明实际绘制可见、对比度、布局或焦点。
- 没有点击“重试”验证真实重载（只读了接线代码）；因此“成功重试后 banner 消失”未验证。
- 没有验证 `--list-tests` 957 与全量 961 的差异原因（不作为结论）。
- 没有跑其它测试项目（Host/CoreClient）或整个 solution。

## 5. 对交办问题的直接回答

1. **“实现早已存在”属实吗？** 属实。`SettingsViewModel.LoadAsync` `:139-171` 的 catch（`:166-170`）与 `SettingsPageView.RenderState` `:688-706`（错误分支 `:698-701`）在 base 与 head 是同一份 src（src diff 为空）。
2. **3 个测试测到宣称的东西了吗？** AC1：是；AC2：是**真实视图树**（`FluentShell` + `SettingsPageView` 的视觉后代），不是 VM 字段——我用实验 B 单独回退视图即变红；AC3：是。保留意见见 P3-4（按钮只查存在、消息可能来自 `_notice`、未测重试成功）。
3. **矩阵 ❌→✅ 有测试依据吗？** 有。测试真实存在且通过；我独立令其因回退变红（2 failed / 1 passed）。不是“为了矩阵好看”。
4. **零生产代码改动？** 是。`git diff 418801499..HEAD -- apps/desktop-avalonia/src` 为空；`FakeHostController` 在 tests 下，不算生产代码。
5. **`SettingsLoadFailure` 只挂在 `ListProviderProfilesAsync`，能稳定触发吗？** 当前能稳定触发，因为 `LoadAsync` 第一句就调用它；但这是**调用顺序耦合**，不是“语义触发”。重排四个 list 调用会产生假红。注释写复数“list calls”也不准确。见 P3-3。
6. **对照测试能防住“错误 banner 永远显示”吗？** 能防住“全新健康页也渲染错误 banner”和“VM 永远 Error”；但防不住“Error→Ready 后 banner 残留”（重试成功场景），也没有断言健康态是 `Ready`。见 P3-4。
7. **断言文案是读出来的还是猜的？** 是读出来的：`"设置错误"`/`"重试"` 来自 `SettingsPageView.cs:700`，`"设置读取失败"`/`"可以重试"` 来自 `SettingsViewModel.cs:169`。实现改文案测试会变红；README §5 已承认这是有意的耦合。
8. **矩阵 §5“真无覆盖 0 格”只基于这 1 格吗？有没有把其它仍无覆盖的格算成 0？** 该结论就是“唯一 ❌ 格被补上”的直接补集：HEAD 的 §3 除图例外确实没有第二个 ❌；但仍有 2 个 ⚠️ 格（书架只读 NOT_RUN、设置快捷键单入口），且矩阵 §0 不覆盖回收站/命令面板/源恢复/沉浸等 GUI 流程。因此“0 格”只在“13 类 × 4 页、按 ❌ 口径”内成立；当前 §5.3 与 Gate `:205` 缺这个限定（P2-3）。
9. **卡面完整登记了两次探针失败吗？有无淡化？** 卡面（`doc/tasks/SETTINGS-ERROR-STATE-1.md`）**没有**登记；`verification/…/README.md` §4 与 commit message 有，且写得完整、自我批评，**没有淡化**。卡面 `:99` 的“实际测试：尚无”还与该文件已有的结果表矛盾（P3-5）。
10. **能否进入集成？矩阵该格改判成立吗？**
    - **可以进入集成**：测试真实、判别力经我复现，生产代码零改动；没有 P0/P1。
    - 但建议在 Gate 文档被引用前先修 **P2-1/P2-2/P2-3**（allowed_paths 补登记、Gate §15 的 63/13/“补那 1 格”、0 格的 13 类限定），并顺手修 P3-1（文件:行）与 P3-2（ledger 重新生成）。若集成门禁要求 P2 全清，则先返修一轮再进；这不影响“该格应判 ✅”。
    - **矩阵该格 ❌→✅ 成立**；成立的是“设置页加载失败态有可判别测试覆盖”，不成立的是把它外推成“GUI 层无任何覆盖缺口”。

## 6. 建议的下一步（供 DSH 处置）

1. 修 P2-2：Gate §15 的 `62→63`、`12→13`、删“补那 1 格”；矩阵标题/§5 标注 §3/§5 的更新 commit（`90dc51ded`），§2/§4.1 标注为 `d86f185ca` 基线快照。
2. 修 P2-3：给“真无覆盖 0 格”和“GUI 层无覆盖缺口已清零”加“在 13 类矩阵内”限定，并保留 2 个 ⚠️ 格的说明。
3. 修 P2-1：把 `doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` 加入 `allowed_paths`（或登记授权）。
4. 修 P3-1/P3-2/P3-5：`文件:行` 改 `:35/:53`；ledger 重新 `--write`；卡面补两次探针失败与“实际测试”状态。
5. 可选但推荐：补一条“失败→修好→点击重试→Ready 且无 banner”的测试，把“重试可恢复”从代码接线变成测试证据；这会让矩阵该格的 ✅ 更硬。
