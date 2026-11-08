# FEA-12-UI-RESIDUAL-2 Canonical Evidence（回收站恢复后书架同步 + 空态/分页诚实性 + 计数文案，App-only）

> **结论先行：本卡只做 App 侧行为与测试（2 个 ViewModel + 3 个测试文件），修三条缺陷：**
>
> - **A（AC-R1/R2）**：回收站内「恢复」成功后书架不刷新（用户可见状态残留）→ 恢复成功后（部分成功也算）经构造注入的 `Func<Task>` 回调 `await RefreshAsync()`（`forceHostRead:true`）重读书架；全失败不刷新、不伪报。**唯一活动入口**是 `RecycleBinView.axaml:120` 绑定的 `Trash.RestoreCommand`，回调在 `TrashViewModel.RestoreSelectedAsync` 内一次覆盖全部入口。
> - **B（AC-R3/R4）**：`IsEmpty` 不看 `_nextCursor` + `ShowList` 要求 `Items.Count>0` ⇒ 首页被恢复/彻底删除清空但仍有下一页时显示「回收站是空的」且「加载更多」不可达。修法：`IsEmpty` 增 `&& _nextCursor is null`；`ShowList` 改 `(Items.Count > 0 || HasMore)`；不改 XAML、不自动重载。
> - **A′（AC-R6，第二轮独立评审发现）**：`IsRecycleBinView` setter 不重发 `BookCountText`/`ListStatusText` ⇒ 进入回收站时 bar 仍显示「N / M 作品」、返回后可能残留「回收站」。修法：setter 的 `OnPropertyChanged` 补两个属性名。
> - **零契约/wire/schema/迁移/依赖变更；18 pins 不变；XAML 零改动；`IHostController`/`ITrashController`/`TrashModels` 零 diff；死代码 `RecycleRestoreCommand` 按裁决保留（L-3）。**

| 项 | 值 |
|---|---|
| task | `FEA-12-UI-RESIDUAL-2`（冻结卡 `doc/tasks/FEA-12-UI-RESIDUAL-2.md`；scope review `doc/reviews/FEA-12-UI-RESIDUAL-2-scope-r1.md`，两轮独立评审均 **READY-TO-FREEZE**） |
| Owner | `ui-residual-2-impl`（DSH Agent Teams teammate，fresh；Lead=`lead`） |
| Review | 独立上下文 fresh subagent（session `897f3928-3df7-4336-ad18-036b486ecc6a`；未参与实现）；报告 `doc/reviews/FEA-12-UI-RESIDUAL-2-r1.md`；**approved，P0=0 / P1=0 / P2=1 / P3=5** |
| base | `54e5d69db`（main，clean） |
| 实现 + 测试 commit | **`85356c22a`**（5 files changed, 461 insertions, 8 deletions） |
| 冻结卡 commit | `b7c63bc50`（卡面 + scope review + PLAN READY + STATUS 指针 + ledger） |
| 证据/卡/Handoff | 本目录所在证据提交（本卡 closeout 的 docs 提交；sha 见 handoff §27 与 `git log -- verification/FEA-12-UI-RESIDUAL-2`） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree） |
| 环境 | Windows 11 10.0.26300；.NET SDK 10.0.401（net9.0 目标）；CPython 3.14.6；PowerShell 7 |
| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`src/**`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`*.axaml` 全空 diff；pins 18/18） |
| 依赖 | **零新增**（无 `.csproj`/`props`/`targets`/`pyproject`/lock 文件 diff） |

## 1. 门禁实测（before → after，Lead DSH 亲自实跑）

| Gate | Before（base `54e5d69db`） | After（`85356c22a`） | 结果 | 证据 |
|---|---|---|---|---|
| 定向 `TrashUiTests\|V2ShellUiTests` | 63 个事实/用例（37 + 26） | **74 passed / 0 failed / 0 skipped**（含 Theory 展开；新增 8 个用例：TrashUiTests +7、V2ShellUiTests +1） | PASS | EV-11（logs/gates.log）、EV-12…EV-26（logs/reviewer-mutations/*） |
| 全量 App.Tests | **770 passed / 0 failed / 7 skipped（总 777）** | **778 passed / 0 failed / 7 skipped（总 785；+8 = 新增用例，skip 不变）** | PASS（不降） | EV-11 |
| 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1683 passed / 0 failed / 96 skipped（总 1779）** | **1691 passed / 0 failed / 96 skipped（总 1787）** | PASS（+8，0 failed） | EV-11 |
| 全量 `pytest tests -q` | **3390 passed / 10 skipped** | **3390 passed / 10 skipped**（254.51 s，EXIT=0；`src/**` 零 diff） | PASS（不降） | EV-11 |
| `verify_pins.ps1` | 18/18 | **PIN AUDIT: PASS (all 18)** | PASS | EV-11 |
| `check.ps1`（默认 + `-TaskPath`） | PASS(3 warnings) | **PASS (3 warnings) ×2** | PASS | EV-11 |
| `generate_api_inventory.py --check` | PASS | **OK: rendered counts match FEA-C07 doc**（54/6/1，合计 61，EXIT=0） | PASS | EV-11 |
| build | — | **0 warning / 0 error**（Release） | PASS | EV-11 |
| scope diff ⊆ allowed_paths | — | 实现提交 5 文件全部 ⊆ 卡面 allowed_paths；禁止面（`src/`、`doc/contracts`、`plan`、XAML、Host、CoreClient、`Services/`、`FEA-12-UI.md`、`verification/FEA-12-UI`、csproj）**零 diff** | PASS | EV-11 |
| 判别性（变异） | — | **7 组变异：6 组 RED（M1 3 / M2 1 / M3 2 / M4 2 / M5 3 / M6b 4）；M6a 0 RED 已登记 P3-01**；逐字节复原 sha256 MATCH 后 74 全绿 | PASS（含登记缺口） | EV-12…EV-26 |
| L3/L4 真机走查 | NOT_RUN | **NOT_RUN**（本卡不新增真机证据） | NOT_RUN | 本文件 |

**skip 原因（before/after 相同，共 96）**：`Host.Tests` 65 + `CoreClient.Tests` 24 + `App.Tests` 7 —— 既有真实 IPC / frozen sidecar / 环境门控集成测试；本卡未新增或改变任何 skip 条件。

**已知副作用（既有，已恢复）**：全量 .NET 会重写 tracked 文件 `verification/FEA-09/logs/wire-redacted.ndjson`（`WireLogSourceRedactionTests` 既有副作用）；Lead 全量后执行 `git checkout -- verification/FEA-09`（EXIT=0），最终 worktree 仅本卡改动。

## 2. 判别性验证（删掉实现必须变红）

由**独立 Review 子代理**在 `85356c22a` 上实测（流程：pristine 副本 → 改工作树 → 定向 `dotnet test` → 从 pristine 逐字节复原 → `Get-FileHash` 比对 MATCH → touch mtime 强制重编译 → 复绿）。原始日志：`logs/reviewer-mutations/M*.log`、`full-sln.log`。

| 变异 | 破坏点 | 目标用例 | 实测 | 复原 |
|---|---|---|---|---|
| **M1** A 修复 | `TrashViewModel.cs:625-628` 删除 `await _onBooksRestored()` | T1 / T2(部分成功) / T7 | **失败 3 / 通过 71** | sha256 MATCH → 74/0/0 |
| **M2** A 边界 | 回调改无条件 await（去掉成功判定） | T2（全失败分支） | **失败 1 / 通过 73**（`RefreshCalls` 0→1） | MATCH → 74/0/0 |
| **M3** B(`IsEmpty`) | 去掉 `&& _nextCursor is null` | T3（恢复）/ T4（彻底删除） | **失败 2 / 通过 72** | MATCH → 74/0/0 |
| **M4** B(`ShowList`) | 改回 `Items.Count > 0` | T3 / T4 | **失败 2 / 通过 72** | MATCH → 74/0/0 |
| **M5** A′ | 去掉两个 `nameof(...)` | T6(VM) / T7 / V2Shell Esc | **失败 3 / 通过 71** | MATCH → 74/0/0 |
| **M6a**（处方变异，未变红） | `ShowList` 去掉 `!_capabilityMissing` | T5 / 能力态 | **失败 0 / 通过 74** | MATCH → 74/0/0 |
| **M6b**（等价更强变异） | `IsEmpty` 去掉 `!_capabilityMissing && !_probeFailed` | T5 + 3 既有能力态用例 | **失败 4 / 通过 70** | MATCH → 74/0/0 |

复原指纹：`TrashViewModel.cs = B47532BC…AF3DF1`、`LibraryViewModel.cs = 98F4FBF2…E5C9BA`（与 `85356c22a` worktree 逐字节一致）。

**M6a 未变红机理（如实登记为 L-4/P3-01）**：能力缺失态与 probe 失败态在描画列表前早退，此时 `Items.Count==0 && _nextCursor==null`，`(Items.Count > 0 || HasMore)` 恒 false，故 `ShowList` 的能力守卫当前只有结构性保护、无变异级判别。

## 3. AC 判定（全部由独立 Review 判定，DSH 复核）

| AC | 判定 | 关键判别测试 |
|---|---|---|
| AC-R1 恢复成功后书架一致 | **MET** | `RestoreFromRecycleBin_ThroughTheRealCommands_ReputsTheBookOnTheShelf`（真实入口链 + `Books`/`AllBooks`/`BookCountText` + `RefreshCalls` 恰 +1） |
| AC-R2 部分成功/全失败边界 | **MET** | `RestoreFailureBoundary_OnlySuccessRefreshes_AndBothCountsStayHonest` |
| AC-R3 空态与分页诚实性 | **MET**（短路子句判别力缺口见 L-4） | `EmptyStateIsHonestOnlyWhenThereIsNeitherRowNorCursor`、`RestoreEmptyingTheFirstPage_…` |
| AC-R4 两条删除路径同构 | **MET** | `RestoreEmptyingTheFirstPage_…` + `PermanentDeleteEmptyingTheFirstPage_…`（M3/M4 各 2 RED） |
| AC-R5 门禁与禁止面 | **MET** | §1 门禁表 + scope/禁止面零 diff |
| AC-R6 计数文案双向一致 | **MET** | `BookCountText_FollowsTheRecycleBinView_BothWays` + `RecycleBin_BookCountText_FollowsTheEscPathBackToTheShelf` + `ReturningToTheShelfAfterAnInRecycleBinRefresh_NeverLeavesTheRecycleBinCopy` |

## 4. limitations（如实保留，不得夸大）

- **L-2（接受）**：恢复成功触发的 `RefreshAsync` 在「选择为空」时按既有语义自动选中 `Books[0]`（并读一次 chapters），与移入回收站/撤销同构；本卡不修，AC 只断 `Books`/`AllBooks`/`BookCountText`，未断言选中态。
- **L-3（登记，另卡）**：`LibraryViewModel.RecycleRestoreCommand` 为死代码（零 XAML 引用；`RecyclePurgeCommand` 仍活），本卡按裁决不删。
- **L-4（登记 P3-01 处置）**：`ShowList` 的 `!_capabilityMissing`/`!_probeFailed` 短路子句当前**只有结构性保护、无变异级判别测试**（M6a 0 RED）；`IsEmpty` 的同一子句由 M6b 4 RED 判别。**不得**据此声称 AC-R3 的回归栅栏已被变异钉住。
- **L-5（P3 登记）**：恢复回调是 `RestoreCommand` fire-and-forget 链上的新 await 点；`RefreshAsync` 只捕获 `InvalidOperationException`/`SidecarException`，其它异常会成为未观察异常（不崩、书架静默旧数据）；`RefreshAsync` 无重入闸（与移入/撤销同构，本卡未劣化）。
- **L-6（P3 登记）**：T2(a) 的等待谓词 `Trash.HasStatus` 不判别（「正在恢复…」阶段即为 true），当前确定性依赖 fake 同步语义；fake 改真异步时须收紧。
- **L-7（P3 登记）**：T7 的 `DoesNotContain("回收站", ListStatusText)` 恒真（`ListStatusText` 无该分支），属空断言；`ListStatusText` 重发为防御性通知（AC-R6 明文要求），UI 只消费 `BookCountText`。
- **L-8**：证据级别为 **VM 级 headless + fake controller**；真实 Core/IPC 端到端与 L3/L4 真机走查 **NOT_RUN**。`FEA-12-UI` 的 L1（批量 OUT）、L2（无总数/缩略图）、L3（真机 NOT_RUN）等 limitation **原样保留**。

## 5. 不构成什么

- 不构成「回收站已完全修复」「UI L1–L10 已关闭」「回收站功能完备」。
- 不构成批量彻底删除 / `library_purge_trash` / 缩略图 / 总数 / 页面级回收站的任何实现。
- 不改变任何契约、wire 命令、能力、错误码、schema、迁移或依赖；不改 `FEA-12-UI` 历史 AC 与已 pin 证据字节。
