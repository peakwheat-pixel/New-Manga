---
task_id: FEA-07-RESIDUAL-4
review_round: r2
reviewer: DSH 主会话 session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5 派发的独立上下文只读子代理（subagent，review r2）
reviewer_kind: subagent
author: dsh
base_commit: 77a7459ab
reviewed_head: df0593ac0
decision: approved
---

# Review：FEA-07-RESIDUAL-4（r2 复审）

## 0. 审查者来源与独立性

- 本报告由 DSH 主会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5` 派发的**独立上下文只读子代理**完成。该子代理未参与本 Task 的实现（`86d65d1a9`）或 r2 返修（`df0593ac0`），未持有其实现会话上下文，与 r1 审查者亦为独立子任务。
- 全程只读：未修改生产源码、测试源码、任务卡、契约、pins、`verification/**` 既有字节；未 commit / push；唯一写入为本报告。
- 实际执行（均不触碰真实用户目录写权限）：`dotnet build`（App.Tests）、`dotnet test --no-build --filter LegacyWindowIsolationTests`、harness `-SelfTest` / `-Verify`、`check.ps1`（默认 + `-TaskPath`）、`verify_pins.ps1`、只读行数统计。真实 `%APPDATA%\com.newmanga.desktop\logs\window-material.log` 审查前/后均为 **14544** 行，`LastWriteTime` 保持 `2026-11-09T16:42:25`（今日未发生写入）。

## 1. 被审 head 与范围

| 项 | 值 |
|---|---|
| 被审 head | `df0593ac0`（fix: 处置 Review r1） |
| 提交链 | base `77a7459ab` → 冻结 `5ca20036c` → 实现 `86d65d1a9` → in_review `908ad9aa0` → r2 `df0593ac0`（已核实 `77a7459ab`/`86d65d1a9`/`a49311cbe` 均为 `df0593ac0` 的祖先） |
| r2 diff | `908ad9aa0..df0593ac0`：13 文件，+605/−289 |
| diff 构成 | `LegacyWindowIsolationTests.cs`（守卫 +77/−9）、`appdata-isolation-check.ps1`（+103/−…，子进程 self-test）、卡/Handoff/README/DEFECTS、9 份 EV 证据全部按 r2 重新生成、r1 报告入库 |
| `out_of_scope` | `apps/desktop-avalonia/src`、`NewManga.sln`、`doc/plan`、`doc/contracts`、Python `src/`、`tests/`、`tools/governance`、6 个既有测试文件 = **空 diff**（EXIT 0） |
| 生命周期文件 | `doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md` 在 `86d65d1a9..df0593ac0` 内被 DSH 改写，属卡面明示的 DSH 生命周期写入，不计 Owner 越界 |

## 2. Verdict

**`approved`（附条件）**：P0 = 0 / P1 = 0 / **P2 = 2（均为证据/工作树收尾类，非代码缺陷）** / P3 = 2。

r1 的三项 P2 与四项 P3 中被要求处置的部分**已全部落实**（P3-04 为 PARTIAL）。本轮**新增 2 项 P2**，均不影响「16 个既有站点全部隔离、真实 AppData delta=0、harness 可判别」的实测结论，但其中一项使 `AC-R4-5` 的**随附证据自相矛盾**，关账前应处置：

- **C-1（无 head 变更）**：恢复工作树 `verification/FEA-09/logs/wire-redacted.ndjson`（当前 +1 行未提交）；
- **C-2（需一次证据重生成提交）**：重新生成 `logs/governance.log`（当前入库的是 **FAIL/EXIT=1** 版本）并同步 `EV-R4-GOV` 的 sha256 与 `commit` 列。

C-2 会改变 EV 字节与 head；届时只需对「`governance.log` + 卡内 EV 行」做增量复核，无需重跑代码侧门禁（本轮已由我实跑复现 PASS）。

## 3. r1 findings 逐条判定

| ID | r1 级别 | 判定 | 一句依据 |
|---|---|---|---|
| P2-01 | P2 | **FIXED** | 守卫改为 `StripComments()` 后匹配并明确限定「6 个已知文件」（`LegacyWindowIsolationTests.cs:22-26,52`）；卡 `:58` / README 顶部「守卫范围说明」/ DEFECTS `R-LEGACY-GUARD` 均已删除「全仓即 RED」表述，改为登记 follow-up；6 文件 `Isolated()` 计数实测 1/1/1/3/1/4，与守卫期望值（含已修正的 `ThemeRetirementR4Tests=4`）一致，`new AppOptions()` 为 0。 |
| P2-02 | P2 | **FIXED** | 卡 `:54,62`、Handoff `:34,47`、DEFECTS 统一为 base **833/2/11/846**（sln 1796/2/107）→ 交付 **836/2/11/849**（1799/2/107）；`full-solution.log` 8 项目合计实测 passed 1799 / failed 2 / skipped 107 / total 1908，与 846+3=849、833+3=836 自洽；无工件的「base `git stash` 复跑」表述已替换为「输入零 diff + `5108c6640` 为祖先 + HEAD 同消息复现」。 |
| P2-03 | P2 | **FIXED** | README/DEFECTS/卡/Handoff 内 `app-tests-full.log`、`pins.log` 引用 grep 命中 **0**；`verification/FEA-07-RESIDUAL-4/` 树内仅 9 份 EV 文件，`Test-Path` 两文件均 False；证据索引改指 `full-solution.log` / `governance.log`。 |
| P3-01 | P3 | **FIXED** | `-SelfTest` 改为 `Start-VerifyChild` 起**子进程**跑 `-Verify`（`appdata-isolation-check.ps1:151-161,211-233`）；我实跑得 `SELFTEST KILL`（子进程脏根 **EXIT 1**，含 `logs\window-material.log 24 -> 32` 与 `lines: 3 -> 4`）→ `SELFTEST OK`（新基线 **EXIT 0**）→ 父进程 **EXIT 0**，临时根无残留。 |
| P3-02 | P3 | **FIXED** | `StripComments()` 剥离 `//` 与 `/* */`；6 个文件内不存在含 `//` 的字符串字面量（实测 0 命中），故当前无误判/漏判；注释中的同文本不再触发 RED。 |
| P3-03 | P3 | **FIXED** | `LegacyUiTestOptions.Isolated()` 追加 `--theme-home <root>\theme` 并预建目录（`:220-222,238`）；`AppOptions.cs:225` 确认该开关受支持；helper 注释同步声明「log/data/theme 三根隔离」。 |
| P3-04 | P3 | **PARTIAL** | harness 两份日志已补命令头/`before: 14544 → after: 14544`/`EXIT=`；但 `build.log`（26 行）与 `full-solution.log`（265 行）仍**无 shell/命令头、无时间戳、无 `EXIT=`**（实测 EXIT-lines=0）。 |

**汇总：FIXED 6 / PARTIAL 1 / OPEN 0。**

## 4. 本轮新增 findings

| ID | 级别 | 文件:行 | 问题 | 依据 | 建议 |
|---|---|---|---|---|---|
| N-01 | **P2** | `verification/FEA-07-RESIDUAL-4/logs/governance.log:1-53`；卡 `:62,89`；README 证据表 | 入库的 EV-R4-GOV 记录的是 **失败**的门禁：两次 `check.ps1` 均输出 `FAIL: Evidence SHA-256 不匹配`（6 项：`appdata-before.json`、`appdata-isolation.log`、`appdata-isolation-selftest.log`、`build.log`、`full-solution.log`、`appdata-isolation-check.ps1`）与 `Governance check: FAIL (6 errors, 3 warnings)`、`EXIT=1`；而卡 E7/AC-R4-5 与 README 均写「check.ps1 PASS / EXIT 0」。 | 我在 `df0593ac0` 现状实跑：`check.ps1` 默认与 `-TaskPath` 均 `PASS (3 warnings)` / **EXIT 0**，`verify_pins` 18/18 / EXIT 0 —— 说明日志是「证据重生成后、EV 表更新前」的中间态，作者改了 EV 哈希却**未重跑门禁**，把 FAIL 日志原样入库。`governance.log` 头时间 `19:17:46` 晚于 self-test 与全量运行，可排除「日志早于修复」。 | 在 EV 表已修正的 head 上重跑 `check.ps1`（默认 + `-TaskPath`）与 `verify_pins` 覆盖该日志，令其记录 PASS/EXIT 0；同步更新 `EV-R4-GOV` sha256 与 `commit` 列。 |
| N-02 | **P2** | 工作树；卡 `:62,95`；README「说明」 | `git status --short` 在 `df0593ac0` 上**不干净**：` M verification/FEA-09/logs/wire-redacted.ndjson`（+1 行，`mtime 2026-11-09T19:12:04`，早于本次审查开始）。而卡 AC-R4-5 写「`git status` 仅预期文件」、运行纪律写「命中 FEA-09 wire 文件既有改写，已 `git checkout` 恢复」。 | 我在任何写操作前采集的首次 `git status` 已含该修改；本轮我只读，命令后仍为同一路径。该行由 E5 全量运行追加，与 `86d65d1a9`/`908ad9aa0` 时「已恢复」的表述不符，且与 r1 报告 §5「审查前后 clean」矛盾。 | 关账前 `git checkout -- verification/FEA-09/logs/wire-redacted.ndjson`（或按 DSH 资源处置裁决登记），并把 §运行纪律 的「已恢复」表述改为可核对的事实（该文件每次全量运行会被重写）。此项不改变 head。 |
| N-03 | P3 | `logs/appdata-isolation-selftest.log`（55 行） | 该 CANONICAL 证据以**追加模式**记录，导致同一文件内并存：r1 时代两行旧格式输出（含被 r1 指为不成立的 `EXIT 1 by design`）、两次**中间失败**（`SELFTEST FAIL: changed root must make -Verify exit 1, got EXIT=0` @19:04:44、`SELFTEST FAIL: unchanged root must make -Verify exit 0, got EXIT=1` @19:05:06）、最后一次 PASS（@19:05:20）。表面阅读与 README「子进程：脏根 EXIT 1、新基线 EXIT 0」冲突。 | 末次运行与我的独立复跑一致（脏根 1 / 干净 0 / 父进程 0），结论成立；问题仅在证据文件未截断，保留了调试期失败行。 | 重生成时用覆盖写（或 `Clear-Content`）只保留最终一次运行；如保留迭代历史，请在 README 明确「日志含调试中间态，以最后一次 `EXIT=` 为准」。 |
| N-04 | P3 | 卡 `:69-77,88`；`logs/build.log`、`logs/full-solution.log` | EV 表 `commit` 列 9 行仍全部写 `86d65d1a9`，但 9 份 EV 文件的最后一次改动均在 **`df0593ac0`**（`git log -1 -- <path>` 逐个实测）；证据血缘指针过期。 | 哈希本身 9/9 与当前字节一致（`Get-FileHash` 全 OK），仅 commit 列失真。 | 将 EV 表 `commit` 列改为 `df0593ac0`（或增列 `evidence_commit`），与证据重生成保持一致。 |

## 5. 门禁与复跑结果（本审查亲自执行）

| # | 检查 | 命令/方法 | 结果 |
|---|---|---|---|
| 1 | EV 9 个 sha256 | `Get-FileHash -Algorithm SHA256` | **9/9 OK**（README/DEFECTS/snapshot/2 isolation log/build/full-solution/governance/harness） |
| 2 | 构建 | `dotnet build ...NewManga.App.Tests.csproj -c Debug --nologo` | **EXIT 0**，0 warning / 0 error，9.11 s |
| 3 | 3 个新增测试 | `dotnet test ... --no-build --filter "FullyQualifiedName~LegacyWindowIsolationTests"` | **3 passed / 0 failed**，**EXIT 0**，428 ms |
| 4 | harness `-SelfTest` | `pwsh -NoProfile -File verification/FEA-07-RESIDUAL-4/tools/appdata-isolation-check.ps1 -SelfTest` | **EXIT 0**；子进程脏根 **EXIT 1**、新基线 **EXIT 0**；`nm-r4-selftest-*` 残留 0 |
| 5 | harness `-Verify`（不传 `-LogPath`，只读） | 同上 `-Verify .../evidence/appdata-before.json` | **EXIT 0**，`before: 14544 / after: 14544`，`ZERO-WRITE OK delta=0` |
| 6 | 治理（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS**，**EXIT 0**（3 warnings：12 非终态 Task；STATUS 2968B/29L 80%；PLAN 6730B/64L 80%） |
| 7 | 治理（`-TaskPath`） | 同上 `-TaskPath doc/tasks/FEA-07-RESIDUAL-4.md` | **PASS**，**EXIT 0**（同上 3 warnings） |
| 8 | pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，**EXIT 0** |
| 9 | 真实 AppData 行数 | 只读 `[IO.File]::ReadLines` | 审查前 **14544** → 3 测试后 **14544** → self-test/verify 后 **14544**；`LastWriteTime` 恒为 `2026-11-09T16:42:25`（未写入） |
| 10 | 工作树 | `git status --short` | **不干净**：` M verification/FEA-09/logs/wire-redacted.ndjson`（审查开始前即存在，见 N-02） |
| 11 | out_of_scope | `git diff --stat 908ad9aa0..df0593ac0 -- <生产/契约/治理/Python/6 既有测试>` | **空**（EXIT 0） |
| 12 | 计数自洽 | 解析 `full-solution.log` 8 个 `总计` 行 | passed **1799** / failed **2** / skipped **107** / total 1908；App.Tests **836/2/11/849**；base 833/2/11/846 与之自洽 |
| 13 | 守卫覆盖负向探针 | 同一条正则对 4 种形态取样（PowerShell 侧） | `new MainWindow(c,new AppOptions())`=True；变量 options / `Parse(Array.Empty<string>())` / `AppOptionsStore.Current`=False —— 与卡面「仅覆盖 6 文件字面构造 + follow-up」口径一致，不再宣称全仓 |

## 6. 剩余风险

- **守卫仍为文件白名单（已明示）**：`R-LEGACY-GUARD` 只在 6 个已知文件生效；变量 options、`AppOptions.Parse(Array.Empty<string>())`、`AppOptionsStore.Current`、以及其他文件新增 `Show()` 仍可绕过。卡/README/DEFECTS 已如实收窄表述，属已披露残余风险，不作为阻塞项。
- **harness 为手工命令**：默认套件不会自动跑 `-Verify`；`delta=0` 依赖操作者纪律。与本卡冻结范围一致（自动接入不在 allowed scope）。
- **证据血缘/可核验性**：`appdata-before.json` 无签名/时间链，且 9 份 EV 现均产自 `df0593ac0` 的单轮运行；可核验性依赖日志头时间戳（`19:05:27` capture → `19:10:57` verify，顺序自洽）。
- **`governance.log` 冲突（N-01）**：若直接关账，后续审计者在证据目录内会读到 `Governance check: FAIL`，与卡面 PASS 冲突；这是本轮唯一的「结论正确但证据反证」项。
- **`StripComments()` 对字符串字面量不敏感**：若未来 6 文件内出现含 `//` 或 `/*` 的字符串，会截断行内后续代码，可能造成**漏判**（当前 0 命中）。属极低概率，记录备查。

## 7. 未验证项（UNKNOWN / NOT_RUN）

| ID | 项 | 状态 | 原因/替代验证 |
|---|---|---|---|
| U-1 | 全量 `NewManga.App.Tests`（849 例）由本审查重跑 | **NOT_RUN** | 约 5.5 分钟，超出本轮 10 分钟预算；计数取自 `full-solution.log`（1799/2/107、836/2/11/849，与 8 项目明细自洽），代码侧关键面（3 个新增测试、harness）已独立复跑。 |
| U-2 | 全量 `NewManga.sln` 由本审查重跑 | **NOT_RUN** | 同上；本卡零生产代码 diff。 |
| U-3 | base 计数 833/2/11/846 的实际 base 运行 | **UNKNOWN** | 需在 base 上 stash/checkout（只读约束禁止）；已用算术（849−3=846、836−3=833、1799−3=1796）+ 两处既有失败输入零 diff + `5108c6640` 为 base 祖先替代印证。 |
| U-4 | 守卫的**负向控制**（临时写入违规构造后应 RED） | **NOT_RUN** | 需改动被审源码；仅以正则探针 + 代码阅读确认判别力。 |
| U-5 | pytest（L-R4b-5 单 node） | **NOT_RUN** | 本卡零 Python diff；沿用 DEFECTS 文字登记。 |
| U-6 | 真实进程 / IPC / 真实 DPI | **NOT_RUN** | 卡面 E9 声明不需要；AC5 豁免维持。 |

## 8. 结论

- 无 **P0/P1**；实现目标（16/16 既有 legacy `MainWindow.Show()` 站点显式隔离、真实两棵 AppData 树 delta=0、harness 具备真实退出码判别力）经本轮独立复跑成立。
- r1 的 3 项 P2 全部 FIXED，P3 中 6 项 FIXED / 1 项 PARTIAL，**无 OPEN**。
- **verdict：`approved`（附条件）**——C-1 恢复 `verification/FEA-09/logs/wire-redacted.ndjson`；C-2 重生成 `governance.log` 并同步 `EV-R4-GOV`（sha256 + commit 列，建议同时把 9 行 commit 更新为 `df0593ac0`）。两项均为证据/工作树收尾，不涉及代码，不改变本报告对功能面的判定。
- 本报告仅对 `reviewed_head: df0593ac0` 有效；C-2 产生新 head 后，应按增量范围（`governance.log` + 卡内 EV 行）复核，代码侧无需重审。
