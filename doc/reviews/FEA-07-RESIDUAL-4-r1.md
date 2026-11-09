---
task_id: FEA-07-RESIDUAL-4
reviewer: DSH 主会话 session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发的独立上下文只读子代理（subagent，review r1）
reviewer_kind: subagent
author: dsh
base_commit: 77a7459ab
reviewed_head: 908ad9aa0
decision: approved
---

# Review：FEA-07-RESIDUAL-4（实现 Review r1）

## 0. 审查者来源与独立性

- 本报告由 DSH 主会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5` 派发的**独立上下文只读子代理**完成；该子代理未参与 `FEA-07-RESIDUAL-4` 的实现、返修或证据生成，也未持有其实现会话上下文。
- 审查全程只读；未修改生产源码、测试源码、任务卡、契约、pins、`verification/**` 既有字节；未 commit / push。唯一写入文件为本报告。
- 审查期间只运行了：3 个新增测试、6 文件 + 新增测试定向 filter、2 个既有失败用例、harness `-Verify` / `-SelfTest`、`check.ps1` / `verify_pins`。所有测试均使用隔离 `--log-dir`（或只读真实 AppData 行数），真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 前后均为 **14544** 行，未删除/修改真实用户目录文件。

## 1. 被审 head 与范围

| 项 | 值 |
|---|---|
| 被审 head | `908ad9aa0`（文档/状态提交：AC1–6 `<<MET>>`、EV、Handoff、PLAN/STATUS 指针） |
| 实现提交 | `86d65d1a9`（测试隔离 + 证据） |
| base / 冻结 | base `77a7459ab`；冻结提交 `5ca20036c`；scope review base `a49311cbe`（已核实 `a49311cbe` 是 `77a7459ab` 的祖先） |
| 审查 diff | `5ca20036c..86d65d1a9`（16 文件，+1377/−11） |
| 范围卡 | `doc/tasks/FEA-07-RESIDUAL-4.md`；scope review `doc/reviews/FEA-07-RESIDUAL-4-scope-r1.md` |
| 证据 | `verification/FEA-07-RESIDUAL-4/` |

**diff 形状**：6 个既有测试文件共 11 行构造参数改动（`new AppOptions()` → `LegacyUiTestOptions.Isolated()`），新增 `LegacyWindowIsolationTests.cs`（201 行），新增 `verification/FEA-07-RESIDUAL-4/**`（README/DEFECTS/evidence/logs/tools）。逐文件 diff 确认：

- `CredentialUiTests.cs` 1 处、`F11HotkeyTests.cs` 1 处、`LegacyAppearanceSyncTests.cs` 1 处、`ImportExportUiTests.cs` 3 处、`RegionWorkbenchUiTests.cs` 1 处、`ThemeRetirementR4Tests.cs` 4 处（2 处 `MainWindow` + 2 处 `AppShellV2.CreateRoot`）；全部只改构造参数，**未改任何断言**。
- `out_of_scope` 零 diff：`apps/desktop-avalonia/src/**`、`NewManga.sln`、`doc/plan/**`、`doc/contracts/**`、`tools/governance/**`、`src/**`（Python）、`tests/**`（Python）、`NewManga.Host.Tests/**`、`NewManga.Presentation.Avalonia.Tests/**` 均为空 diff；`git status` 审查前后 clean（本报告除外）。
- `allowed_paths` 覆盖：`git diff --name-only 5ca20036c..86d65d1a9` 的 16 条路径全部落在卡面 `allowed_paths` 内。

## 2. Verdict

**`approved`**（P0 = 0 / P1 = 0 / **P2 = 3** / P3 = 4），**附条件**：

1. P2-01（守卫覆盖）必须在关账前处置：扩守卫，或收窄卡面/README 的守卫表述并登记 follow-up；
2. P2-02（base 计数）与 P2-03（证据索引引用不存在文件）修正文档；
3. 以上为文档/回归保护层问题，不改变「当前 16 个既有 `MainWindow.Show()` 站点全部隔离、真实 AppData delta=0」的实测结论；若 DSH 将 AC-R4-1 的守卫子句视为阻塞，则应转为 `changes_requested`。

关键实测：6 文件 + 新增测试定向 filter **46 passed / 0 failed**，真实 `window-material.log` **14544 → 14544（delta=0）**；3 个新增测试 **3/3 pass**；harness `-Verify` 对已提交 baseline 复跑 **EXIT 0 / delta=0**；`-SelfTest` 检出追加行并返回 **EXIT 0**；`check.ps1`（默认 + `-TaskPath`）**PASS**；pins **18/18 PASS**；EV 9 个 sha256 **9/9 一致**。

## 3. Findings

| ID | 级别 | 文件:行 | 问题 | 依据 | 建议 |
|---|---|---|---|---|---|
| P2-01 | P2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/LegacyWindowIsolationTests.cs:22-30,36-49,51-58`；卡 `doc/tasks/FEA-07-RESIDUAL-4.md:58`；`verification/FEA-07-RESIDUAL-4/README.md:12` | 源扫描守卫只覆盖**硬编码的 6 个文件**，且只匹配 `new MainWindow(... new AppOptions())` 这一字面形态；不扫描 `.Show()`，不覆盖变量 options、`AppOptions.Parse(Array.Empty<string>())`、`AppOptionsStore.Current` 或**新增测试文件**。卡面「出现默认 `AppOptions` + `Show()` 即 RED」不成立。 | 用同一条正则对样例行实测：`new MainWindow(c, new AppOptions())`=True；`var o=new AppOptions(); new MainWindow(c,o)`=False；`new MainWindow(c, AppOptions.Parse(Array.Empty<string>()))`=False；`new MainWindow(c, AppOptionsStore.Current)`=False；注释中的同一文本=True（误报）。仓库现有同类写法：`V2ShellUiTests.cs:854` 用 `AppOptions.Parse(Array.Empty<string>())`，`AppOptions.cs:363` 定义 `AppOptionsStore.Current`；6 文件外仍有 15 处 `new MainWindow(..., new AppOptions())`（`ReaderChapterSelectorTests.cs:167,197,228,245,267,287,309,324`；`ReaderLibraryTests.cs:123,144,160`；`ReaderProgressTests.cs:104,112,278,295`），当前均未 `Show()`，但未来加 `Show()` 或新文件加默认构造会静默绕过守卫。 | 把守卫扩为扫描 `NewManga.App.Tests/**/*.cs` 的全部 `new MainWindow(` 调用，要求 options 实参为 `LegacyUiTestOptions.Isolated()` 或其他显式 `--log-dir` 表达式；至少覆盖变量/`Parse([])`/`Current` 三种别名。若暂不扩，删掉卡面「出现...即 RED」的绝对表述，并另立回归保护 follow-up。 |
| P2-02 | P2 | `doc/handoffs/FEA-07-RESIDUAL-4-86d65d1a9.md:47`；`verification/FEA-07-RESIDUAL-4/DEFECTS.md:27`；卡 `doc/tasks/FEA-07-RESIDUAL-4.md:62` | 「改动前后同 836/2/11/849」「改动前后计数完全相同（836/2/11/849）」与同句「新增 3 个测试通过」算术矛盾：新增 3 个测试后为 849，则 base 应为 **833/2/11/846**（全量 **1796/2/107**），交付为 **836/2/11/849**（全量 **1799/2/107**）。此外「base 上 `git stash` 复跑」没有对应日志/工件入库。 | `full-solution.log` 8 个项目合计 1799/2/107；App.Tests 836/2/11/849；`LegacyWindowIsolationTests` 新增 3 个测试（`:32,61,73`）；846+3=849、833+3=836。R3 证据 `verification/FEA-07-RESIDUAL-3/README.md:123` 为 831/0/11/842，V2-F11 `5108c6640` 增加测试并引入 2 个既有失败，与 base 833/2/11/846 自洽。**「2 个既有失败」结论本身成立**：`git diff a49311cbe..86d65d1a9` 对 `V2ConformanceTests.cs`、`FluentPageTests.cs`、`ImmersiveReaderWindow.cs`、`FluentShell.axaml.cs`、`FluentShellSurface.axaml.cs` 为空；`5108c6640` 是 base 祖先；我在 HEAD 复跑两例均以相同消息失败（`ImmersiveReaderWindow.cs:23 Background = Brushes.Black`；`FluentPageTests.cs:132 Expected 17 / Actual 18`）。 | 将 base 计数改为 833/2/11/846（全量 1796/2/107），或明确写「base 对照未含新增 3 测试」；如保留「base 复跑」说法，补一份可核验的 base 运行日志（不要求进真实 AppData）。 |
| P2-03 | P2 | `verification/FEA-07-RESIDUAL-4/README.md:26,28`；`verification/FEA-07-RESIDUAL-4/DEFECTS.md:15` | README「证据文件」表引用 `logs/app-tests-full.log` 与 `logs/pins.log`；DEFECTS 也把 `app-tests-full.log` 列为判别证据，但这两个文件在树内和 `git log --all` 历史中均不存在。 | EV 表 9 个 CANONICAL 文件全部存在且 sha256 9/9 一致；`full-solution.log` 已包含 App.Tests 结果，`governance.log` 已包含 pins 输出；`Test-Path` 与 `git log --all --` 对两个缺失文件均为空。 | 删除这两个引用，或改为指向 `full-solution.log` / `governance.log`；若确实需要独立 App.Tests 日志与 pins 日志，补入库并加入 EV 表。 |
| P3-01 | P3 | `verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1:154-181`；`logs/appdata-isolation-selftest.log:1`；卡 `:60` | `-SelfTest` 只证明「追加 1 行会被比较器检出」，随后以 **EXIT 0** 结束；日志中的「EXIT 1 by design」不是实际退出码。AC-R4-3 的「delta=1/exit 1」中，exit 1 只由 `-Verify` 分支代码检查支持，未被实际执行。 | 实跑 `-SelfTest`：输出 `SELFTEST KILL` + `SELFTEST OK`，EXIT=0；`-Verify` 的 `delta≠0 → exit 1` 分支未在真实 delta 上运行（红线禁止写真实 AppData）。 | 把日志改为「Verify would exit 1」；或增加隔离子进程 self-test：对临时根运行 `-Verify`，断言子进程 exit 1（不触碰真实 AppData）。 |
| P3-02 | P3 | `LegacyWindowIsolationTests.cs:36-49` | 守卫按整文件文本匹配：注释里出现 `new MainWindow(controller, new AppOptions())` 会误报 RED；6 个文件中「构造但从不 `Show()`」的默认 `MainWindow` 也会误报（当前无此情况）。 | 正则样例行：注释文本=True；守卫无「是否真正 `Show()`」的判别。 | 只匹配代码中的构造调用（剔除注释），或在断言失败消息中明确这是保守守卫、允许显式白名单。 |
| P3-03 | P3 | `LegacyWindowIsolationTests.cs:156-176` | `LegacyUiTestOptions.Isolated()` 只注入 `--data-root` 与 `--log-dir`，未隔离 `--theme-home`；名字「Isolated」不覆盖 `%APPDATA%\NewManga` 主题/外观树。当前 6 文件定向运行与全量日志中 `NewManga` 树 delta=0，属未来风险。 | `AppOptions.cs:343-348` 默认 `logDirectory` 由 DataRoot 派生，而 ThemeHome 有独立默认；helper 参数列表只有 `--data-root`/`--log-dir`。我对 46 例运行后立即 `-Verify`，`NewManga` 树未变化，说明当前未触发。 | 在 helper 中追加 `--theme-home <root>/theme`（或显式说明「仅隔离 data/log」并禁止在 helper 文件内写主题设置）。 |
| P3-04 | P3 | `verification/FEA-07-RESIDUAL-4/logs/full-solution.log`；`logs/appdata-isolation.log` | 运行日志缺 shell/命令头、时间戳与 EXIT；`appdata-isolation.log` 只有「ZERO-WRITE OK ... delta=0」，没有 before/after 数字与命令头（scope review 的 AC-R4-2 证据计划曾要求含 before/after/delta 与命令头；`doc/templates/REVIEW.md:54` Q-009 要求 EXIT 与 shell 头）。 | 日志首行即测试 DLL 路径 / `SNAPSHOT OK`；无 `EXIT=`、无命令回显；`appdata-before.json` 有 capturedAt 与 14544，after 未入库。 | 在 README 或单独 wrapper 日志中补命令头/EXIT；`-Verify` 输出 before/after 行数（或把 after 快照入库），不改变判别逻辑。 |

## 4. AC 逐项判定

| AC | 结论 | 复核依据 | 说明 |
|---|---|---|---|
| **AC-R4-1**（站点完整） | **PARTIAL** | 16/16 既有站点已隔离：6 文件 diff 的 11 处构造 + `F11HotkeyTests.cs:244` 既有显式 `--log-dir`；`git grep "new MainWindow("` 在 6 个既有文件为 26 处、legacy `MainWindow.Show()` 为 16 处；6 文件内 `new AppOptions()` 为 0（`git grep` exit 1）；46 例定向运行 delta=0。 | 「站点全隔离」子句 **MET**；「守卫出现默认 `AppOptions` + `Show()` 即 RED」子句仅覆盖 6 文件字面构造，**PARTIAL** → P2-01。HEAD 全仓 `new MainWindow(` 为 27 处（含新增测试 1 处）、legacy `MainWindow.Show()` 为 17 处（含新增测试 1 处），卡面 26/16 指既有 6 文件，语义成立。 |
| **AC-R4-2**（真实 AppData 零写入） | **MET** | `evidence/appdata-before.json`：`com.newmanga.desktop` 14544 行、`startup.log` 不存在、`NewManga` 树存在；`-Verify` 对 baseline 复跑 EXIT 0 / delta=0；`logs/appdata-isolation.log` 与 `full-solution.log` 均记录；我审查前后真实 log 14544 → 14544。 | 两棵树相对路径集合/长度/材质行数/startup.log 存在性均在 harness 比较范围内；fail-closed 路径为缺 baseline/异常 → EXIT 1。 |
| **AC-R4-3**（harness 可判别） | **MET** | 实跑 `-SelfTest`：追加 1 行被检出 → `SELFTEST KILL`；无变化比较 → `SELFTEST OK`；EXIT=0；临时根清理，无 `nm-r4-selftest-*` 残留。 | 判别力成立；「exit 1」为 Verify 分支语义而非 self-test 实际退出码 → P3-01。 |
| **AC-R4-4**（产品契约仍成立） | **MET** | `LegacyWindowIsolationTests.LegacyMainWindow_Show_WritesMaterialLogOnlyUnderIsolatedLogDir`（`:73-107`）实跑通过：隔离目录 `window-material.log` ≥1 行；真实 AppData 行数前后相等；cwd 无 `com.newmanga.desktop`；未使用「去掉 `--log-dir`」变异。 | 断言为「隔离目录 ≥1 行 + 真实 AppData 只读不变 + cwd 无标记」，与卡面 AC 一致；该测试未隔离 `--theme-home`（P3-03），但当前运行未写 `NewManga` 树。 |
| **AC-R4-5**（回归/门禁） | **MET** | `build.log` 0 warning / 0 error；`full-solution.log` 8 项目合计 1799/2/107，App.Tests 836/2/11/849；2 失败为 `V2ConformanceTests.AppCSharp_OutsideShellLayout_HasNoRawDesignValues`、`FluentPageTests.FluentShell_BreakpointsA11yShortcutsAndReducedMotion_AreExplicit`；两例输入自 `a49311cbe` 未变、`5108c6640` 为 base 祖先、HEAD 复跑同样失败；`check.ps1` 默认 + `-TaskPath` EXIT 0（3 warnings）；pins 18/18；`git status` 仅本报告。 | 「不新增失败」成立；base 计数引用错误（应为 833/2/11/846 → 836/2/11/849）→ P2-02。 |
| **AC-R4-6**（residual 处置/证据） | **MET** | 卡 + `DEFECTS.md`：D-R4b-7 resolved；L-R4b-2 SPLIT、L-R4b-3 SPLIT/DEFER、L-R4b-4 DEFER、L-R4b-5 已登记、L-R4a-3 DROP；EV 表 9 行、卡内 Resource Manifest、Handoff（`908ad9aa0`）齐全；Owner 未翻 `status`（DSH 在 `908ad9aa0` 写 `in_review`）。 | EV 9/9 存在且 hash 一致；README/DEFECTS 另引用 2 个不存在文件 → P2-03；L-R4b-5 的单 node `1 passed` 无独立日志（UNKNOWN，见 §7）。 |

## 5. 门禁与复跑结果

| # | 检查 | 命令/方法 | 结果 |
|---|---|---|---|
| 1 | EV 9 个 sha256 | `Get-FileHash -Algorithm SHA256` | **9/9 OK**（README、DEFECTS、appdata-before.json、两个 isolation log、build、full-solution、governance、harness） |
| 2 | 工作树 | `git status --porcelain`（审查前/后） | clean（仅本报告待入库） |
| 3 | out_of_scope | `git diff --stat 5ca20036c..86d65d1a9 -- apps/desktop-avalonia/src apps/desktop-avalonia/NewManga.sln doc/plan doc/contracts src tests tools/governance ...` | 空（EXIT 0） |
| 4 | diff 允许面 | `git diff --name-only 5ca20036c..86d65d1a9` | 16/16 ⊆ `allowed_paths` |
| 5 | 新增 3 测试 | `dotnet test ... --no-build --filter "FullyQualifiedName~LegacyWindowIsolationTests"` | **3 passed / 0 failed**，EXIT 0，2 s |
| 6 | 6 文件 + 新增定向 | `--filter "FullyQualifiedName~CredentialUiTests|...|LegacyWindowIsolationTests"` | **46 passed / 0 failed**，EXIT 0，9 s；真实 `window-material.log` 14544 → 14544 |
| 7 | 既有 2 失败复现 | `--filter "FullyQualifiedName~V2ConformanceTests.AppCSharp...|FullyQualifiedName~FluentPageTests.FluentShell..."` | **2 failed**（与 `full-solution.log` 同消息），EXIT 1；真实 log 14544 → 14544 |
| 8 | harness `-Verify` | `pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -Verify .../evidence/appdata-before.json` | **EXIT 0 / ZERO-WRITE OK delta=0** |
| 9 | harness `-SelfTest` | 同上 `-SelfTest` | **EXIT 0**；追加行被检出，无变化比较 delta=0；无临时残留 |
| 10 | 治理 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**，EXIT 0（3 warnings：12 非终态 Task；STATUS 2968B/29L 80%；PLAN 6730B/64L 80%） |
| 11 | 治理（TaskPath） | `... check.ps1 -TaskPath doc/tasks/FEA-07-RESIDUAL-4.md` | **PASS**，EXIT 0（同上 3 warnings） |
| 12 | pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，EXIT 0 |
| 13 | 全量日志自洽 | 解析 `full-solution.log` 8 个 `总计` 行 | passed 1799 / failed 2 / skipped 107 / total 1908；App.Tests 836/2/11/849 |
| 14 | 站点计数 | `git grep -n "new MainWindow("`、`git grep -n "new AppOptions()"` | HEAD 全仓 27 构造 / 17 legacy Show；6 既有文件 26/16；6 文件 `new AppOptions()` = 0 |
| 15 | 真实 AppData | 只读 `[IO.File]::ReadLines` 行数 | 审查前、3 测试后、46 测试后、2 失败用例后、harness 后均 **14544**；`startup.log` 不存在；CSD 无残留 `nm-legacy-ui-*` |

**治理日志差异说明**：`logs/governance.log`（EV，提交 `86d65d1a9`）记录 `doc/REBASELINE_PLAN.md` 6739 bytes/64 lines；当前 `908ad9aa0` 为 6730 bytes/64 lines。差异来自后续文档/状态提交对 PLAN 指针的改写，不属于实现 diff；两次 `check.ps1` 均 PASS。

## 6. 剩余风险

- **回归保护仍偏弱（P2-01）**：当前 16 个站点已隔离，但守卫不能阻止新文件/变量 options/`AppOptions.Parse([])` 重新引入真实 AppData 写入；harness 是手工命令，未接入默认测试。若未来无人运行 harness，默认套件不会自动 RED。
- **证据计数与索引（P2-02/P2-03）**：base 对照计数错误、README/DEFECTS 引用不存在文件，可能误导后续审计；不影响当前代码行为。
- **自检退出码（P3-01）**：`-SelfTest` 未实际执行 `exit 1` 路径，AC-R4-3 的退出码断言依赖代码检查。
- **helper 隔离面（P3-03）**：`LegacyUiTestOptions.Isolated()` 未覆盖 `--theme-home`；当前运行 `NewManga` 树 delta=0，但未来在这些文件内新增主题写入时存在真实每用户目录写入风险。
- **全量未独立复跑**：本审查未重跑 849 例 App.Tests 或全量 sln（见 §7），全量数字来自 `full-solution.log`；定向 46 例与 2 个失败用例已独立复现，覆盖本卡主要风险面。
- **baseline 可信度**：`appdata-before.json` 为操作者采集，harness 不提供防篡改；当前真实状态与 baseline 完全一致（14544 行、两棵树文件集/长度一致），与「全量运行后 delta=0」相容，但无法从工件反推采集与运行的时间顺序。

## 7. 未验证项（UNKNOWN / NOT_RUN）

| ID | 项 | 状态 | 原因/替代验证 |
|---|---|---|---|
| U-1 | 全量 `NewManga.App.Tests`（849 例）未由本审查重跑 | **NOT_RUN** | 约 5 分钟；本审查已跑 3 个新增测试、46 例定向、2 个既有失败；全量数字取自 `full-solution.log`（836/2/11/849，8 项目合计 1799/2/107，自洽）。 |
| U-2 | 全量 `NewManga.sln` 未由本审查重跑 | **NOT_RUN** | 依赖 `full-solution.log`；本卡零生产代码 diff，sln 结果主要用于回归计数。 |
| U-3 | base `a49311cbe` / `77a7459ab` 上「`git stash` 复跑」无日志工件 | **UNKNOWN** | 未执行 stash（只读约束）；已用替代证明：两失败用例的测试与输入文件在 `a49311cbe..86d65d1a9` 零 diff、`5108c6640` 是 base 祖先、HEAD 复跑同消息失败、两测试为确定性静态断言。结论可信，但「base 复跑」过程本身不可核验。 |
| U-4 | pytest 单 node「1 passed in 0.12s」无独立日志 | **UNKNOWN** | 本卡零 Python diff；DEFECTS 只有文字记录；未重跑 pytest。 |
| U-5 | 真实进程 / IPC / 真实 DPI | **NOT_RUN** | 卡面 E9 与本卡零产品改动均不需要；真实 DPI 按 AC5 豁免维持 NOT_RUN。 |
| U-6 | `logs/app-tests-full.log`、`logs/pins.log` | **UNKNOWN（不存在）** | 树内与 `git log --all` 均无此文件；见 P2-03。 |
| U-7 | 证据采集顺序 / 防篡改 | **UNKNOWN** | `appdata-before.json` capturedAt 为 `2026-11-09T18:35:57`，`governance.log` 头为 `18:47:57`，与「先 baseline、后全量、再 verify」相容；但 harness 无签名/时间链。当前真实状态与 baseline 一致，支持 delta=0。 |

## 8. 结论与复审

- **可交 DSH 集成判断**：当前 16 个既有 `MainWindow.Show()` 站点全部使用显式隔离 `--log-dir`，真实两棵 AppData 树零写入已由 harness 与我方定向复跑共同支持；无 P0/P1。
- **批准附条件**：P2-01 扩守卫或收窄卡面/README 表述并登记 follow-up；P2-02 修正 base 计数为 833/2/11/846 → 836/2/11/849（1796/2/107 → 1799/2/107）；P2-03 删除/替换不存在证据引用。若 DSH 将 P2-01 视为阻塞，本 Review 应转为 `changes_requested`，并在新 head 上复审。
- **不再作为本卡内容**：L-R4b-2/3/4/5、L-R4a-3 的 re-home 与 DEFER/SPLIT/DROP 口径与卡面一致，未发现「NOT_RUN 写成 PASS」；唯一计数口径问题是 P2-02，不涉及失败归属。
- 本报告只对 `reviewed_head: 908ad9aa0`（实现 `86d65d1a9`）有效；head 改变后自动失效，需重新审查。
