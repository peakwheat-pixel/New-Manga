---
task_id: PIPE-EXCLUSIVE-TRANSPORT-1
reviewer: review-pipe-transport（DSH 派发的独立上下文子 agent；父会话 lead）
reviewer_kind: subagent
author: DSH（被审提交 17c744b268c6）
base_commit: b202b47fbf6f30c4ca9ecce7dd122d050305219f
reviewed_head: 17c744b268c6368147405d802c51615d3c3f2410
decision: approved
verdict: ACCEPT_WITH_LIMITATIONS
---

# Review r1：PIPE-EXCLUSIVE-TRANSPORT-1（E-7 独占下沉到传输层）

## 0. 审查者、来源与被审对象

- **审查者**：`review-pipe-transport`，DSH 在独立上下文中派发的子 agent（父会话 `lead`），
  **未参与**本卡实现、诊断或返修；本轮只读复核。
- **被审 head**：`17c744b268c6368147405d802c51615d3c3f2410`
  （`fix(core-client): 独占下沉到传输层，修复 host_bridge 管道无锁（E-7）`），基线 `b202b47fbf6f30c4ca9ecce7dd122d050305219f`。
- **被审改动**（`git show --stat HEAD`）：`Bridge/HostBridgeClient.cs`（+22/−1）、
  `CoreServiceClient.cs`（+19/−5）、`Transport/SidecarProcess.cs`（+33）、新增
  `tests/NewManga.CoreClient.Tests/Bridge/BridgePipeExclusivityTests.cs`（+92），
  以及卡面 / `verification/PIPE-EXCLUSIVE-TRANSPORT-1/{README.md,four-pieces.log}` / 指针文档。
  `git diff b202b47fb..HEAD -- apps/desktop-avalonia/src apps/desktop-avalonia/tests` 已逐 hunk 阅读。
- **只读约束**：除本报告外未写入仓库。三次实验改动全部用 `git checkout -- <file>` 还原；
  还原后实测 `git status --short` **为空**（§4 末尾）。写入本报告后 `git status --short`
  只应出现本文件（未跟踪）。

## 1. Verdict

**ACCEPT_WITH_LIMITATIONS。**

核心缺陷（E-7 窗口 1：`host_bridge` 管道完全无锁）确实修好了，且**判别测试真能回退变红**（我亲自复现，
见 §4 实验 A）；`SendRawAsync` 的 `_pipeGate` 补位在代码上是正确的（try/finally 平衡）；
无 P0/P1；三项目数字可复现。但本卡**不是**"独占已下沉、四窗口全堵"：

- 窗口 2（`SendRawAsync` 锁外）已修，但**零测试覆盖**（实验 C：删掉锁后全量数字与基线完全一致）。
- 窗口 3（独占下沉传输层）**只做了一半**：传输层有了租约原语，但同一条 core 管道仍用另一套
  `_pipeGate` 锁域，`ExchangeAsync` / `ReadNextResponseLineAsync` 仍是 public 无门禁 ⇒ AC1/AC2 的
  "唯一入口 / 不存在绕过硬调"**不成立**（R-001）。
- 窗口 4（无 `request_id` fail-open）**未修**，且新增的 bridge id 校验本身也是 fail-open
  （缺失/字符串/超 Int32 一律放过），并且**零测试覆盖**（实验 B：删掉校验后 5/5 全绿）（R-002/R-003）。
- AC5（R-002 重同步）**未实现**（R-005）。

**批准范围 = 本 commit 可合入**；**不**批准"AC1–AC6 全 MET"或以此卡关闭 E-7。
Task 关闭前需 DSH 裁决：把 AC4 后半 + AC5 移出到后续卡并改卡面 AC，否则应维持 `in_progress`。

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC1** 传输层唯一独占入口（"取锁→写→读→（跳事件帧）→释放"不可分割） | **PARTIAL** | 原语存在且正确：`SidecarProcess.cs:34-57`（`_exchangeGate`=SemaphoreSlim(1,1)、`AcquireExchangeLeaseAsync`、`ExchangeLease`）。但它**不是唯一入口**：`ExchangeAsync`（`:219-284`）与 `ReadNextResponseLineAsync`（`:292-342`）仍 public 且不自取租约，`CoreServiceClient` 仍用 `_pipeGate`（`:426`）而非租约 ⇒ 传输层无法强制独占，只能靠调用方自觉。事件帧跳过循环只在 core 侧的存在（`CoreServiceClient.cs:2437-2442`），由 `_pipeGate` 而非租约覆盖。 |
| **AC2** 所有调用方走该入口、仓库内无绕过硬调 | **NOT MET（字面）/ 当前无绕过缺陷** | 字面要求不成立：`CoreServiceClient.cs:699-701`、`:2431` 仍**直调** `_process.ExchangeAsync`（在 `_pipeGate` 内，但不在传输层租约内）；`SendRawAsync`（`:2386`）也是 `_pipeGate`。仓库内当前所有调用点**确有某种锁**，所以没有"无锁直调"（AC2 的意图部分达成），但"单入口"没有达成。见 R-001。 |
| **AC3** host_bridge 并发判别测试（先写、必须先红） | **MET** | 新测试 2 个（`BridgePipeExclusivityTests.cs:22-43`、`:46-83`），真并发（12 ping / 6 ping+6 resolve）。**我实测回退变红**：删掉 `HostBridgeClient` 两处 `using var lease`（`:269`、`:292`）后 2 FAIL，异常 `InvalidOperationException: The stream is currently in use by a previous operation on the stream`（被包成 `ProcessExited`）；还原后 2 PASS，连续 3 次稳定（§4 实验 A）。"先写先红"的**原始 base 运行输出**仓内没有（只有 README 手写记录），我以"等价回退"复现替代。 |
| **AC4** id 校验覆盖两条管道 + 无 `request_id` fail-closed | **NOT MET（一半）** | ① bridge 侧新增校验（`HostBridgeClient.cs:319-333`）**只在 `id` 为 JSON Number 且 `TryGetInt32` 成功时生效**；缺失 id、字符串 id、超 Int32 全部放过 ⇒ fail-open。当前 `host_bridge.exe` 回显数字 id（wire log 实测 `"id":1`，错误帧同样带 `"id":9`）⇒ 对当前二进制有效，但对 sidecar 行为变化静默失效。② core 侧 `EnsureResponseBelongsToRequest`（`CoreServiceClient.cs:2403-2415`）对 `null` 仍 fail-open，E-6 的"文档测试"原样保留（`PipeResponsePairingValidationTests.cs:57-65`）。③ 新增 bridge 校验**无任何测试**（实验 B）。卡面 AC4 明确要求 fail-closed，未做。 |
| **AC5** R-002 重同步（丢弃直到匹配 / poison + typed 错误） | **NOT MET** | 未实现（证据 README §5 自认）。`_poisoned` 只在读超时置位（`SidecarProcess.cs:250-258`、`:310-318`）；id 失配、取消、异常帧都不置位、不排空。见 R-005（含"在途取消"这一更现实的触发路径）。 |
| **AC6** 不回归（App 950/0/11、Host 321/0/74、CoreClient 189/0/27；带夹具不劣于 2~3 / 4） | **MET（数字可复现，skip 计数需按 +2 读）** | 我用自己环境复跑：无夹具 App **950/0/11/961**（EXIT 0）、Host **321/0/74/395**、CoreClient **189/0/29/218**；带夹具 CoreClient **214/4/0/218**、Host **350/1/44/395**。4 个 CoreClient 失败均为 E-6 已登记的 "Frozen Core 前提过期" 类（`B1Commands_ExecuteAgainstFrozenCore`、`B2Commands_ExecuteAgainstFrozenCore`、`Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`、`Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame`，报错为 `INVALID_REQUEST` / capability 列表断言，非 pipe 错误）；Host 唯一失败为 `Fea11WatchHostRuntimeTests.Ready_ArmsWatcher…` 的 `SOURCE_REGISTRY_BUSY`（E-6 已归为 flaky 类，非 pipe 错误）。AC6 字面写 CoreClient skip=27，实为 29：`+2` 恰为新增 2 个 `[SidecarFact]` 在无夹具下的 SKIP，总数 216→218、pass 189 未变，**不是放宽断言**（与 E-6 同一口径）。"Host 失败 9→1"的**归因**见 R-009。 |

## 3. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | P2（设计/AC 缺口，非当前缺陷） | `Transport/SidecarProcess.cs:34-57,219-284,292-342`；`CoreServiceClient.cs:426,699-701,2431,2386` | 同一条 core 管道上存在**两套互不排他的锁域**：`CoreServiceClient._pipeGate` 与 `SidecarProcess._exchangeGate`。`ExchangeAsync` 不检查租约，所以"持租约"与"走 `SendAsync`"可以真正并发 ⇒ 传输层独占是**可选约定**而非不变量。任何新增直调 `_process.ExchangeAsync` 的代码仍天然在锁外（正是本卡要消灭的窗口 3）。 | 代码路径；grep 全仓 `ExchangeAsync` 直调仅 2 处（均在 `_pipeGate` 内），租约仅 bridge 两处。 | 让 `ExchangeAsync`/`ReadNextResponseLineAsync` 自己取租约（或改成 `RunExclusiveAsync(Func<Task<T>>)` 单入口并把裸方法 internal 化），`CoreServiceClient` 改用租约、删 `_pipeGate`；否则把 AC1/AC2 改写成"bridge 管道独占 + core 继续用 `_pipeGate`"的实话。 | open |
| R-002 | P2 | `Bridge/HostBridgeClient.cs:319-333`；`CoreServiceClient.cs:2403-2415`；`Wire/CoreProtocol.cs:63-65` | id 校验 fail-open：bridge 仅在 `id` 是 Number 且 Int32 时比较；core 在 `request_id` 缺失/非字符串时直接放过。`host_bridge` 当前回显数字 id（我读 wire log 确认），故今天有效；一旦 sidecar 改成字符串 id 或省略 id，校验**静默消失**，且无任何测试会红。AC4 后半（fail-closed）未做。 | 代码路径 + wire log（`%TEMP%\newmanga-host-client-evidence\wire\bridge-pipe-mixed.ndjson`：`{"result":{...},"id":1}`、`{"error":{...},"id":9}`）。 | 缺失/非数字 id 也判为 `MalformedResponse`（fail-closed），并补确定性单测；core 侧同步改掉 E-6 的 fail-open 文档测试。 | open |
| R-003 | P2 | `Bridge/BridgePipeExclusivityTests.cs` 全文；`HostBridgeClient.cs:319-333` | **新增 id 校验零测试覆盖**：删掉 `:319-333` 整块后，bridge 2 个新测试 + 3 个既有 `HostBridgeIntegrationTests` **5/5 全绿**（§4 实验 B）⇒ 删掉 AC4 的实现不会有任何测试变红。与 E-6 r1 R-005 完全同型。 | 实验 B：`dotnet test --filter "FullyQualifiedName~BridgePipeExclusivityTests|FullyQualifiedName~HostBridgeIntegrationTests"` → `已通过! … 通过: 5，总计: 5`。 | 加确定性单测：stub/可注入 sidecar，或把 `ParseResponse` 提成 internal 静态纯函数（`InternalsVisibleTo`），断言"id 不匹配 / 缺失 / 字符串"三种输入都抛 typed 错误。 | open |
| R-004 | P2 | `CoreServiceClient.cs:2381-2398` | `SendRawAsync` 新增的 `_pipeGate` **零测试覆盖**：删掉锁（回到基线写法）后带夹具全量仍是 `214/4/218`，与有锁时**逐数字相同**（§4 实验 C）。实现本身正确（`WaitAsync` 在 try 之外、`Release` 在 finally 内，异常/取消均平衡），但"修了"没有任何回归护栏。 | 实验 C：全量 CoreClient（有夹具）→ `失败: 4，通过: 214，已跳过: 0，总计: 218`（与 head 完全一致）。 | 在 `CoreServiceIntegrationTests`/新测试里并发混跑 `SendRawAsync` 与正常命令（raw 用合法帧），或至少加一个"raw 与 SendAsync 交错不乱序"的用例。 | open |
| R-005 | P2 | `CoreServiceClient.cs:2431-2451`；`SidecarProcess.cs:235-262,250-258`；`HostBridgeClient.cs:292-294` | **AC5/R-002 未实现**，且真实触发点比卡面写的"错配"更常见：**在途取消**。写请求后、读响应前被取消（用户取消导入/扫描/翻页）⇒ 响应稍后落到流里成为残留帧；此后每个命令读到的都是上一条响应 ⇒ id 失配 ⇒ 每条命令都抛 `MalformedResponse`，**core 通道永久不可用直到重启**。`_poisoned` 不置位、不排空、不重启；`ShutdownAsync` 也救不回来（同样会失配/挂起）。 | 代码推断（未构造取消注入实验，见 §6）。`Fea09UiImportIpcTests.CancelKeepsCommittedPagesOverRealStdio` 在带夹具全量里也是 **SKIP**，未能证明取消路径已被覆盖。 | 把"写入后取消"也视为致命失步：poison + 丢帧直到能匹配 id（有界），或杀进程并由 Host 重建 client；至少暴露 typed "管道已失步，需重建"。 | open |
| R-006 | P3 | `HostBridgeClient.cs:255-264`；`SidecarProcess.cs:349-415`；`CoreServiceClient.cs:2620-2631` | **Dispose 路径不在租约内**：`DisposeAsync → StopAsync` 直接关 stdin、3s 后 kill，与在途交换无协调；在途命令得到 `ProcessExited`（而非完成或可重试错误）。`_disposed` 亦非线程安全。生产侧 `HostRuntime.DisposeAsync:1123-1151` / `StopSidecarsAsync:1678-1698` 先停 watcher/scheduler/renewal，暴露面有限，但"管道访问全部独占"的字面说法不包括此路径。`_exchangeGate` 从不 Dispose（无 wait handle，无实际影响）。 | 代码路径（未构造 dispose 竞争实验，见 §6）。 | Dispose 先 `WaitAsync` 租约（或取消所有在途命令并等待它们的租约释放）再停进程；或在文档里明确"独占只覆盖 exchange，不覆盖 teardown"。 | open |
| R-007 | P3 | `SidecarProcess.cs:40-44` | 租约获取**无超时、无 poison/HasExited 预检**；`SemaphoreSlim` 非重入。当前仓库无嵌套调用（`SendRawAsync` 无生产调用者，仅测试 `CoreServiceIntegrationTests.cs:117`、`HostBridgeIntegrationTests.cs:67`），但将来一次嵌套/忘记 `using` 就是**永久挂起**（`WaitAsync` 只受调用方 CT 约束，默认无 CT）。 | 代码路径 + grep 调用点。 | 租约获取纳入请求超时预算，超时抛 typed `RequestTimeout`；或 `Debug` 下做重入检测。 | open |
| R-008 | P3 | `SidecarProcess.cs:238-241,259-262` | `InvalidOperationException`（"stream in use"）被包成 **`ProcessExited`**，报错文本说"process exited (code=unknown)"，但进程其实活着 ⇒ 诊断误导（本次判别实验里我第一次看到的正是这行，容易把并发 bug 误判为崩溃）。既有问题，非本卡引入。 | 实验 A 的失败输出。 | 增加独立错误码（如 `TRANSPORT_BUSY` / `PROTOCOL_VIOLATION`），保留 inner exception。 | open |
| R-009 | P3 | `verification/PIPE-EXCLUSIVE-TRANSPORT-1/README.md:36`、`:59` | "Host 失败 9→1"的**增量归因**不可由单点 head 测量证明：我实测 head 是 `350/1/44/395`，唯一失败正是 E-6 已归为 **flaky** 的 `SOURCE_REGISTRY_BUSY`（E-6 证据自己的区间就是 2~3）。因此"→1"可能只是该 flaky 这次没触发，不能当作本卡的收益证据；可成立的表述是"当前不劣于 2~3"。 | 我的带夹具 Host 全量（§4）+ E-6 README 的 2~3 区间。 | 若要归因，需在同一环境、同一 sidecar 下分别测 base 与 head 各 N 次并给中位数/失败名单；否则把结论改成"无新增失败"。 | open |
| R-010 | P3 | `doc/tasks/PIPE-EXCLUSIVE-TRANSPORT-1.md:56-89,104-121` | 文档卫生（与 E-6 r1 R-008 同型）：AC1–AC6 全未勾选、"测试要求"表 5 行全 `NOT_RUN`、"Handoff/Review/实际测试：尚无"、`canonical_evidence_status: pending`，与 `verification/.../README.md` 的实际结果不一致；AC6 写的 skip 27 与实测 29 未在卡面更新（只在证据 README 解释）。`git diff` 后的 TASK_LEDGER（614/8 non-terminal）与 `check.ps1` 的 8 一致，无矛盾。 | 卡面与证据 README 对照；`git diff b202b47fb..HEAD -- doc/`。 | 关闭前补齐卡面 AC 勾选 / 测试表 / Handoff，并把 AC4b、AC5 明确标 deferred 或移出。 | open |

Positive notes（不计 finding）：

- `SendAsync` 的 `requestId` 在**取租约之前**分配，所以并发时线上请求顺序可能与 id 顺序不同；用 **id 匹配**（而非顺序）判断响应当前是正确做法，租约 + id 校验组合起来恰好堵住"顺序 ≠ id"的隐患。桥侧 id 数字回显已在 wire log 验证。
- 新增测试是**真并发**（12/6+6 个 Task 同时进入 client），回退实验证明它能抓住真实缺陷；不是"把并发测试改串行"作弊（§4 实验 A）。
- `ExchangeLease.Dispose` 的 `Interlocked.Exchange(ref _gate, null)` **正确**：重复 Dispose 第二次拿到 null，不会 `Release`，因此**不会** `SemaphoreFullException`；`using var` 在异常路径也必定释放（桥侧两个测试里 6 个 resolve 抛 typed 错误、6 个 ping 仍成功，若泄漏会挂死）。
- `HostBridgeClient` 的所有**命令方法**（ping/issue/resolve/revoke/revoke_resource/shutdown、`StartAsync` 握手）都汇入 `SendAsync` 一个入口，所以"加一处租约覆盖六个命令"成立。

## 4. 判别力实验记录（我亲自跑，pwsh / dotnet 10.0.401 / net9.0 / Debug / 2026-11-15 04:14–04:26 +08:00）

夹具：`NEWMANGA_CORECLIENT_SIDECAR_DIR=G:\CODEX\New Manga\apps\desktop-avalonia\build\sidecar\core-sidecar\core-sidecar`（`host_bridge.exe` 存在，2026-11-15 03:16）。

| 实验 | 操作 | 命令 | 结果（原文） | EXIT |
|---|---|---|---|---|
| 基线 | head 原样 | `dotnet test …CoreClient.Tests.csproj -c Debug --filter "FullyQualifiedName~BridgePipeExclusivityTests"` | `已通过! - 失败: 0，通过: 2，已跳过: 0，总计: 2，持续时间: 579 ms` | 0 |
| **A 回退→红** | 删除 `HostBridgeClient.cs:269` 与 `:292` 两行 `using var lease = await _process.AcquireExchangeLeaseAsync(...)`，其余不动 | 同上 | `失败! - 失败: 2，通过: 0，已跳过: 0，总计: 2，571 ms`；两个测试均为 `SidecarException [ProcessExited] … --- System.InvalidOperationException : The stream is currently in use by a previous operation on the stream`（`SidecarProcess.cs:235/248`） | 1 |
| **A 还原→绿** | `git checkout -- apps/desktop-avalonia/src/NewManga.CoreClient/Bridge/HostBridgeClient.cs` | 同上，再跑 | `git status --short` 为空、`git diff --stat` 为空；`已通过! - 失败: 0，通过: 2，总计: 2，579 ms` | 0 |
| A 稳定性 | 再跑 2 次 | 同上 | `通过: 2`（582 ms）、`通过: 2`（568 ms） | 0 |
| **B id 校验零覆盖** | 删除 `HostBridgeClient.cs:319-333` 整个 id 校验块（租约保留） | `--filter "FullyQualifiedName~BridgePipeExclusivityTests\|FullyQualifiedName~HostBridgeIntegrationTests"` | `已通过! - 失败: 0，通过: 5，已跳过: 0，总计: 5，1 s` ⇒ **删掉 AC4 实现无测试变红** | 0 |
| **C `SendRawAsync` 锁零覆盖** | 把 `CoreServiceClient.SendRawAsync` 还原成基线（无 `_pipeGate`），其余不动 | 全量 `NewManga.CoreClient.Tests`（带夹具） | `失败! - 失败: 4，通过: 214，已跳过: 0，总计: 218，46 s` ⇒ **与有锁时逐数字相同**（无判别力） | 1（预期 4 个） |
| B/C 还原 | `git checkout --` 两个文件 | — | `git status --short` 为空、`git diff --stat` 为空 | 0 |
| 全量无夹具 | 不设 env | CoreClient → Host → App 顺序跑 | CoreClient `已通过! - 失败: 0，通过: 189，已跳过: 29，总计: 218，21 s`；Host `失败: 0，通过: 321，已跳过: 74，总计: 395，6 s`；App `失败: 0，通过: 950，已跳过: 11，总计: 961，4 m 44 s` | 0 / 0 / 0 |
| 全量带夹具 | 设 env | CoreClient → Host | CoreClient `失败: 4，通过: 214，已跳过: 0，总计: 218，46 s`；Host `失败: 1，通过: 350，已跳过: 44，总计: 395，41 s` | 1 / 1（预期内） |

**结论**：租约的判别力**成立**（A：红→绿→稳定绿，且红的原因与证据 README 记录一致）；但 **AC4 的 id 校验与窗口 2 的 `SendRawAsync` 锁都没有判别力**（B/C），属"能回退而不变红"的实现。

## 5. `HostBridgeClient` 管道访问点清单（哪些在租约内、哪些在租约外）

| # | 位置 | 访问的是什么 | 在租约内？ | 说明 |
|---|---|---|---|---|
| 1 | `HostBridgeClient.cs:292-294`（`SendAsync`） | `_process.ExchangeAsync` 写+读 | **是**（`:292` 取，`using` 覆盖到 `:294` 返回） | 六个命令 + `StartAsync` 握手全经此；异常/取消也释放 |
| 2 | `HostBridgeClient.cs:269-272`（`SendRawAsync`） | `_process.ExchangeAsync` 写+读 | **是** | 但 `:272` **不传** `expectedId` ⇒ raw 响应不校验 id（fail-open，仅测试钩子使用） |
| 3 | `HostBridgeClient.cs:238-253`（`ShutdownAsync`） | 经 `SendAsync` 发 `shutdown` | **是** | 语义竞争：shutdown 会排在在途命令之后；**排在其后的排队命令**将得到 `ProcessExited`（调用方契约问题，不是竞态） |
| 4 | `HostBridgeClient.cs:255-264`（`DisposeAsync`） | `_process.DisposeAsync` → `StopAsync` 关 stdin / 3s 后 kill | **否** | 与在途交换无协调；在途命令得到 `ProcessExited`。见 R-006 |
| 5 | `HostBridgeClient.cs:81`（`Wire`） | `_process.Log` | 否（无需） | 只在 `ExchangeAsync` 内部 `Log.Add`，本身不碰 stdin/stdout |
| 6 | `HostBridgeClient.cs:83`（`StderrTail`） | `_process.StderrTail` | 否（无需） | stderr 有独立的 `_stderrGate`（`SidecarProcess.cs:109`） |
| 7 | `HostBridgeClient.cs:85-151`（`StartAsync`） | 起进程 + 握手 `PingAsync` | 握手**是**（经 `SendAsync`） | 失败路径 `client.DisposeAsync()` 无并发调用者 |

**对照：同进程类里其他会碰 core 管道的位置**（回答"是否只剩单入口"）：

| 位置 | 在租约内？ | 在 `_pipeGate` 内？ |
|---|---|---|
| `CoreServiceClient.cs:699-708`（`SendHostControlAsync` 写+读+跳事件帧） | 否（core 无租约） | **是** |
| `CoreServiceClient.cs:2389-2392`（`SendRawAsync`） | 否 | **是**（本卡新增） |
| `CoreServiceClient.cs:2431-2442`（`SendAsync` 写+读+跳事件帧） | 否 | **是** |
| `CoreServiceClient.cs:2629`（`DisposeAsync` → `StopAsync`） | 否 | **否**（与 bridge 同型问题） |
| `SidecarProcess.cs:219-284` / `:292-342`（裸 `ExchangeAsync` / `ReadNextResponseLineAsync`） | 否（不检查租约） | 由调用方决定 |

**第三条管道？** `src` 内**没有**。全仓 `SidecarProcess.StartAsync` 只有两处：`CoreServiceClient.cs:459`、`HostBridgeClient.cs:105`；
`RedirectStandardInput` 只在 `SidecarProcess.cs`；`src` 内无 `NamedPipe`/`AnonymousPipe`/额外 `Process.Start` 管道。
测试里的 `acceptance_bridge.exe` / `sfx_detect_probe.exe` 是夹具，不构成生产管道。
`HostCommandDispatcher` 同时持有 `_core` 与 `_bridge`（`HostCommandDispatcher.cs:43-44`），但那是**两条已有管道**，各自独立加锁，无共享锁 ⇒ 无跨管道死锁。

## 6. 我没有验证的面

1. **没有在 base `b202b47fb` 上实跑**（要 checkout/worktree 才能做，属于改动仓库）。因此：证据里"修复前 2 FAIL"的原始输出、"Host 9→2~3→1"的历史曲线，我只能用"等价回退"（删两行租约，复现代码差异）间接验证；AC6 的"baseline 数字"用的是 E-6 证据 README 的 `189/0/27/216` 做算术核对。
2. **没有构造"sidecar 把 id 回成字符串/省略 id"的实验**（需要自制 stub sidecar，超出只读范围）。R-002 的 fail-open 结论来自 `ParseResponse` 代码路径 + 当前 wire log 的 id 回显。
3. **没有实测"写在途取消 → 残留帧 → 永久失配"**（需要注入取消时刻的确定性钩子）。R-005 是代码推断；可参考的是带夹具全量里取消类测试 `CancelKeepsCommittedPagesOverRealStdio` 仍是 SKIP，未覆盖。
4. **没有实测 Dispose 与在途 exchange 的竞争**（R-006 为代码推断 + Host 侧 quiesce 顺序阅读）。
5. **没有跑 `tools/governance/check.ps1` / `verify_pins.ps1`**；只读了 `verification/.../four-pieces.log` 里记录的 PASS 结果，未独立复算。
6. **没有复核证据里"定向合跑（bridge + core pipe + 既有 host bridge）9 passed"**：我只跑了 bridge(2)+HostBridgeIntegration(3)=5 passed（实验 B）以及各全量。
7. **没有审 Python sidecar 源码**（不在仓库/冻结范围），`host_bridge` 行为仅由二进制 + wire log 观测。
8. **没有跑带夹具的 App.Tests**（AC6 只要求 App 无夹具数字；已复现 950/0/11）。
9. 未审 `doc/` 指针的治理正确性（只核对 TASK_LEDGER 计数与 check.ps1 输出一致）。

## 7. 明确回答两个问题

**Q1：`host_bridge` 管道现在是否真的独占？**

**交换（exchange）层面：是。** `HostBridgeClient` 的**全部命令**（ping/issue/resolve/revoke/revoke_resource/shutdown + `StartAsync` 握手）都经 `SendAsync`，`SendAsync` 与 `SendRawAsync` 两处 `ExchangeAsync` 都被租约包住；回退实验证明这条租约真的在挡并发（2 FAIL），所以"host_bridge 请求/响应不再互相踩流"成立。
**但不是"这条管道的所有访问都独占"**：`DisposeAsync`/`StopAsync`（关 stdin、kill）在租约外（R-006），且租约是**约定而非强制**——裸 `ExchangeAsync` 仍可被直调（R-001）。
**另外**：`SendRawAsync` 不校验 id（`HostBridgeClient.cs:272`），raw 帧即使在独占下也可能拿到非预期响应（仅测试钩子使用，P3 级）。

**Q2：有没有"两条管道之外的第三条"或死锁风险？**

- **没有第三条生产管道**（§5 证据：只有 core_service 与 host_bridge 两个 `SidecarProcess`；无 named/anonymous pipe；测试夹具不算）。
- **死锁**：当前仓库**无**可触发的死锁。理由：① 桥侧没有任何嵌套 `SendAsync`/`SendRawAsync` 调用（`ResolveAsync`→`SendAsync`，`ShutdownAsync`→`SendAsync`，均是单层）；② `_pipeGate`（core）与 `_exchangeGate`（bridge/SidecarProcess）从未被同一段代码同时持有；③ `StreamWriter/StreamReader` 的"共享 stream"争用已被锁消除。
  **但有两点必须盯住**：① **若将来有人在持租约时调用 `SendAsync`（或 `SendAsync` 间嵌套），会自死锁**——`SemaphoreSlim` 非重入且租约获取无超时（R-007）；② 同一条 core 管道上的两套锁域（R-001）意味着"持租约"并不排斥 `SendAsync`——这不会死锁，但会让"独占"失效，属于 AC1/AC2 未真正达成的根因。

## 8. 结论与复审

- **可交 DSH 集成**：本 commit 修复方向正确、无 P0/P1、无回归（三项目数字全部复现）、主缺陷有真判别测试且回退会变红。合入风险低。
- **不可据此关闭 Task**：AC2/AC4b/AC5 未达成，AC1 部分达成；证据 README §5 也自认未完成。建议 DSH 二选一：(a) 把 AC4 后半 + AC5 + 窗口 3 完整下沉拆成后续卡并改本卡 AC 与 `disposition`，然后本卡按"E-7 窗口 1 + 窗口 2"范围关闭；(b) 维持 `in_progress` 并让 Owner 继续做 fail-closed + 重同步 + 单一入口。
- 若走 (a)，后续卡至少应包含：`ExchangeAsync` 自持租约（或单入口封装）、缺失/非数字 id fail-closed、取消/失配后的 poison + 有界重同步、`ExchangeLease` 获取超时、以及 R-003/R-004 的两条确定性单测。
- 本 Review 只对 `17c744b268c6368147405d802c51615d3c3f2410` 有效；head 变更后自动转为历史记录，需按新 head 复审（findings disposition 追加，不抹旧记录）。
