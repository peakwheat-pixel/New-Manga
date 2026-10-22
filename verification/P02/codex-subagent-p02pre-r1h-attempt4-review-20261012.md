我已完成对 allowlist 内 16 个输入的内容审查（13–16 号按 owner worktree 相对路径解析）。以下为报告。

---

# P02PRE-R1H Round6 attempt4 — 独立静态 Review（非作者）

- **verdict＝`APPROVED_STATIC_CONTENT`**
- **P0＝0；P1＝0；P2＝0；P3＝4**
- 审查对象：Reviewed HEAD=`c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427`，tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，parent=`237c25d734d78609d2d9933d5e94ecfb8b3ee1db`，base=`cddff58469…`
- 本 verdict 仅为静态文本结论：**不是**执行器运行、不是 Codex 集成、不是 P02PRE PASS、不是 Build Gate 放行、不是 AC1–AC7 结果。

## 1. 审查范围与实际读取对象

| # | 输入 | 读取情况 |
|---|---|---|
| 1–2 | `AGENTS.md`、`doc/09_COLLABORATION.md` | 全文 |
| 3–5 | `doc/tasks/P02PRE-R1H-R6-A4.md`、`doc/tasks/P02PRE-R1H.md`(1–236 行)、`doc/tasks/P02.md` | A4 全文；R1H 主要段落；P02 存在性 |
| 6 | `verification/P02/p02pre-r1h-manifest-20261012.md` | 全文 |
| 7 | `…round6-integration-protocol-20261012.md`（不可变 attempt2） | 全文 |
| 8 | `…round6-integrator-20261012.ps1`（attempt3 对照） | 全文 581 行 |
| 9–12 | attempt3 协议、attempt3 Review、attempt3 adjudication、attempt3 definitions-check | 全文 |
| 13–16 | attempt4 executor / protocol / selfcheck / Handoff（owner worktree） | 全文 |

未访问任何未列明路径、未枚举目录、未访问 `.tmp.driveupload`、未写任何文件。

**不可独立核验项（如实声明）**：本会话按 dispatch 要求**未执行任何命令**，因此**未计算任何 byte length/SHA-256**，也未运行 Git/Parser/selfcheck/API。§下方所有 hash、字节数、`assertionsPassed=73`、exit=0 均为**文本记录**，其复核权归 Codex pin verifier。协议第 102、105 行与此一致。

## 2. attempt3 阻断项修复确认

### 2.1 P2-1 → 升级 P1：`$definitions` 嵌套数组 ⇒ **已修复（静态确认）**

- `GetToolhelpDefinitions`（executor 164–187）改为**扁平 `@(...)` + 具名字段**（`name`/`returnType`/`parameterTypes`），四条定义与 selfcheck 期望签名逐项一致：`CreateToolhelp32Snapshot(uint32,uint32)→IntPtr`、`Process32FirstW(IntPtr,byte[])→bool`、`Process32NextW(IntPtr,byte[])→bool`、`CloseHandle(IntPtr)→bool`。
- attempt3 缺陷根因是每个元素前置一元逗号 `,@(...)`（attempt3 executor 167–170），Codex 实测首元素 `Count=1`、`[1]/[2]` 越界并抛 `IndexOutOfRangeException`（definitions-check JSON 13–19）。attempt4 已无该构造；生产路径 194 行 `$definitions = GetToolhelpDefinitions` 直接消费。
- selfcheck 覆盖真实候选 AST：ParseFile → `Find` 按名抽取 4 个 `FunctionDefinitionAst` → `Invoke-Expression` 仅注入这 4 个纯函数（selfcheck 27–38），随后断言 4 条定义具名属性、名称、返回类型、参数个数与逐个参数类型（72–86），并在内存 `TypeBuilder.DefineMethod` 中真实调用 4 个签名并断言 `Name`/`ReturnType`（99–110）。
- **符合** AC“不调用 native、不持久化 assembly”：全程无 `.Invoke(`、无 `CreateType()`（故无 `.dll` 落盘）、无文件写入。**判别力充分**：若复现 attempt3 的嵌套形态，`$definitions[0].name` 在 StrictMode Latest 下即失败。

### 2.2 P1-1：PID 0 与“无 child”哨兵冲突 ⇒ **已修复（静态确认）**

- 哨兵语义：`SelectProcessRecords`（238–260）签名 `[Nullable[int]]$ExpectedChildPid = $null`；240 行 `Require ($null -eq $ExpectedChildPid -or $ExpectedChildPid -gt 0)` 使 **PID 0 不可作为哨兵**（selfcheck 6.2 正例覆盖）。
- PID 0 排除：`$observed` 取 `related.Contains(pid)` 或 `pid -eq $ExpectedChildPid`（253）。真实快照中 System Idle 记录为 `pid=0,parentPid=0`，`related` 只由 `$PID`（`Require $RootPid -gt 0`，239）与 `KnownChildren` 键扩展，二者恒为正 PID（`Process.Id`），故 0 永不进入 `related`，也永不被观察、永不被 254–258 的 `Require` 判为“未列明 child”。**P1-1 在实现层确已消除**（详见 P3-2：selfcheck 未直接证明这一机制，但缺陷本身已不存在）。
- 调用点全部改用显式语义：预启动与写前快照传 `$null`（300、471），运行期传 `$process.Id`（306、307）。
- fail-closed 覆盖（selfcheck 6.4–6.7 合成用例）：未知孙进程、预启动 rogue child、child 可执行名不匹配、已退出父 PID 的存续子进程——均抛 `Unlisted child/descendant…` 或 `Unexpected child executable…`。`KnownChildren` 保留已退出父 PID 作为种子（243–245）与 attempt3 218 行意图一致。

## 3. 其余必需审查项

### 3.1 `InvokeChild` 全分支 fail-closed（269–344）⇒ 通过

- 单一 `try(275–320) / catch(321–331) / finally(332–343)` 包裹**从入口到返回的全部操作**：closure 检查、executable/CWD 白名单、record 构造、`$Evidence.processes.Add`、`ProcessStartInfo`、环境清理与 `$contextInherited` 判定、`Process`/`MemoryStream` 创建、预启动观测、`Start()`、pid 登记、异步管道、`WaitForExit(10)` 循环、退出码、`WaitAll(5000)`、退出码校验、Git stderr 校验。
- catch 先置 `$script:ProcessClosureBlocked = $true`（322）再 `throw`；finally 在 `-not $succeeded` 时再置位（333–335）。`$succeeded` 仅在 319 行全部校验通过后为真，故**任何非成功离开路径（含 catch 内二次异常）都必然置位**。这两处均为 attempt3 缺失项（attempt3 281–285 catch 不置位、286–290 finally 不置位）的修补。
- catch 内取证（324–329）与 finally 内清理（337、340–342）逐项套 `try/catch`，**清理异常被吞但记录安全**（`$record` 已含 error/stdout/stderr/finishedUtc），不会覆盖原始异常。Handoff 第 30–31 行描述与实现一致。
- 置位后的下游约束确实生效：`AssertWriteSafe` 468 行 `Require (-not $ProcessClosureBlocked)`；失败路径 630 行在置位时记 `NOT_RUN: process observation or closure blocked` 且**不再启动 Git child**。
- 未引入 kill/retry：全文件无 `Kill`；`WaitForExit(10)` 轮询（306）在 51 行 `childTimeoutLimit` 中明确声明“无限等待、不杀、不自动重试”，**与 P3-5 保留要求一致**。

### 3.2 Replace 前重钉与 `FileShare.None`（437、538–543、463、493）⇒ 通过

- Replace 前顺序为：`AssertWriteSafe`（537）→ `AssertPin` 全量重钉（bytes+sha256，538）→ attributes/ACL SDDL 直比（539）→ `AssertStable $initial.destination $destinationPreReplace` 漂移比对（540）→ 记账（541）→ `$ReplaceCalls++`（542）→ **全文件唯一一次**三参数 `[IO.File]::Replace`（543）。任一漂移即 `Require` 中断，不调用 Replace。
- 全文件 `::Replace(` 仅 543 行一处；`ReplaceCalls` 仅 542 行自增，并随 77 行写入证据。
- 执行证据流改为 `[IO.File]::CreateNew/Write/FileShare.None`（493），与 attempt3 的 `FileShare.Read`（attempt3 440）相比**收窄**；`CreateBytes` 亦为 `FileShare.None`（463）。
- 写入面**未扩大**：`FullPath` 白名单仍为 8 个 `$Paths` 值 + `capture.ps1` + 旧 handoff（64）；文件内**无** `Remove-Item/Delete/Move/Copy/Set-Acl/New-Item/Start-Process/Add-Type/Registry/WriteAll`（检索为空）。

### 3.3 P3-3 / P3-5 保留（50–51、306）⇒ 通过

- P3-3：证据对象新增 `observationRaceLimit`（50），协议第 52 行明示“S2 status 与后续 destination/recovery/backup hash/ACL/stream 断言之间为非原子外部窗口，不声称原子快照”。
- P3-5：`childTimeoutLimit`（51）与协议第 53 行明示“无总时限、挂起子进程会无限等待、不杀不重试”。
- 与 attempt3 一致的 `processObservationLimit`、`nativeInteropLimit`、`metadataLimits` 均保留；无 kill/retry/超时策略引入。

### 3.4 传输通道与 checkpoint 元数据（protocol 99–105）⇒ 通过

- 通道唯一化为“DSH 经 stdout 返回 Markdown；Codex wrapper 捕获 stdout/stderr/exit 并以 `CreateNew`+`FileShare.None` 另写报告体；DSH 不写仓库、不初始化沙箱权限”，与本次 dispatch 及 attempt3 adjudication 的 `FIX_REQUIRED` 一致。
- checkpoint 元数据：协议要求“**当**checkpoint 在输入 pins 中时才须声明 `true`”，与 manifest 实际 16 项、`checkpointIncludedInInputPins=false` **一致**（正是 attempt3 P3-2 缺陷的正确闭合形态）。

### 3.5 Task/manifest/协议/Gate 一致性 ⇒ 基本一致（见 P3-1）

- 路径：A4 Task 允许范围四条与 Handoff §2 四条、owner worktree 实际存在文件**逐条一致**，均在 `verification/P02/`。
- 沿用常量未变：`$OldHash`、`$NewHash`、`$CaptureHash`、`$HandoffHash`、`$IndexHash`、`$ExpectedSddl`、8 个输出路径、宿主身份/SID、`7.6.6/Core/FullLanguage`（156–158）与 attempt2/3 冻结值逐字一致。
- Gate 原文在 executor 41–47、protocol 88–95、Handoff 111–120、A4 Task 64 四处一致：`private_registry_absence=UNPROVABLE`、`Technical Gate=NOT_SATISFIED`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER`、`Build Authorization=AUTHORIZED_WITH_EXCEPTION`、residual 原文、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`Build/Cargo=NOT_RUN`、`system AC1–AC7=BLOCKED / NOT_RUN`。
- 非作者性保持：Reviewer=DSH；executor 作者 `/root/round6_executor`、协议作者、adjudicator 均在 Codex 侧；Owner 交付=Antigravity。
- attempt3 文件未被改写：attempt4 以“attempt3 协议 SHA-256 `CAA5984B…` 为只读历史”引用，未声称修改。

## 4. Findings（P3 全部为非阻断）

**P3-1｜Task 测试要求表仍记 `NOT_RUN`，与交付报告的实际结果并存**
- 文件/行：`doc/tasks/P02PRE-R1H-R6-A4.md` 55–59（“实际结果”列 = `NOT_RUN`）；`verification/P02/p02pre-r1h-round6-attempt4-handoff-20261012.md` 62–97、77–78。
- 触发条件：A4 Task 第 73–76 行已承认 Owner 报告 parser exit=0/errors=0 与 selfcheck exit=0/73 断言，但 Task 表未登记该 `实际结果`；表格末行“Executor/Replace/OS/Build/AC=NOT_RUN”正确，前两行与“Parser”行则属陈旧状态。
- 影响：非技术阻断，但同一 Task 内出现“未跑”与“已跑且有结果”两种表述，易被后续读者误读。
- 建议：将三行改为 `PASS（Owner 报告）/ 待 Codex 独立复跑`，并把证据列指向 Handoff §3.1–3.2。

**P3-2｜PID 0 排除由“图可达性”保证，selfcheck 仅以合成快照间接覆盖**
- 文件/行：executor 253（`$related.Contains` 过滤）；selfcheck 120、129–134（用例 6.1）。
- 触发条件：用例 6.1 的合成快照**不含** `pid=0` 且 `parentPid∈related` 的记录，因此 134 行断言并不能区分“因不在 `related` 而被排除”与“显式排除 PID 0”。真实路径（208–234 快照含 Idle 记录）已被我静态证明为安全，故不构成缺陷；但该断言对“PID 0 过滤”主张的证明力弱于其字面表述。
- 建议：补一条用例——快照加入 `{pid=0,parentPid=<rootPid>}` 并断言抛错，或在断言语义上改写为“PID 0 永不可作为哨兵（240 已证）+ 永不被观察”。

**P3-3｜selfcheck 未覆盖 `SetImplementationFlags` / DllImport 属性构造**
- 文件/行：executor 197–202；selfcheck 99–110。
- 触发条件：`InitializeProcessObserver` 的属性构造（`SetLastError/ExactSpelling=true`、`CharSet=Unicode`、`CallingConvention=Winapi`、`PreserveSig`、`DefineParameter(2,In|Out)`）未被内存测试触及，而这些正是 attempt3 P2-1 之后仍需动态验证的 ABI 关键面（51 行 `nativeInteropLimit` 已如实列为 NOT_VERIFIED）。
- 建议：若需提高静态置信，可断言 `$method.GetMethodImplementationFlags()` 含 `PreserveSig`，或在自检中记录“属性构造未验证”一行。

**P3-4｜Handoff 提交谱系留占位符、缺 tree/parent**
- 文件/行：Handoff 9–11。
- 触发条件：第 11 行“Follow-up delivery commit: follow-up commit closing preparation exception closure gap”未填入 `c7c7879e…`，且未记 tree/parent。
- 影响：Handoff 自身 hash 依协作协议 §5 由外部 pin 冻结本属正当，但**交付 commit 标识不是自指数据**，应可写实；现依赖 `doc/tasks/P02PRE-R1H.md` 73 行与外部 pins 交叉补全。
- 建议：补入 `follow-up commit=c7c7879e8ae90ad23b29d9d8cc6ea97e3eff5427; tree=e12bd627…; parent=237c25d7…`。

## 5. 接受为限制、不计为 finding 的事项

1. **采样间隔外瞬态进程**（executor 49；protocol 未反驳）：Toolhelp 快照无法排除短于采样间隔的进程——已如实声明。
2. **`AssertWriteSafe` 快照与实际写入之间的窗口**（468–471 → 464/493）：属 P3-3 已声明“非原子观测窗口”的自然外延；未新增未声明能力主张。
3. **受允许 child 的存续后代将 fail-close**（306–307 + 256）：git 若派生存续孙进程（如 helper 或 `cmd.exe`），执行器会阻断；selfcheck 6.4 以 `cmd.exe` 孙进程显式确认此语义。属**期望的 fail-closed**，代价是集成可能被真实阻断为 `BLOCKED`，非安全缺陷。
4. **`finally` 不杀存活 child**（340）：与 51 行“不杀/不重试”声明一致，仅在已置位 blocked 状态下发生。
5. **属性/时间戳/file identity 不保证**（53）：`metadataLimits` 如实声明。
6. **executor 不比对注入 payload**（578、583、588 的 `$summary.Count -eq 9`、`$capability.Count -eq 7`）：这些契约针对被固定的 Round6 selfcheck/capability 子进程，与本 Task 的 attempt4 selfcheck（task=`P02PRE-R1H-R6-A4`）不是同一对象，**不构成冲突**。

## 6. 结论与最小安全下一步

- **verdict＝`APPROVED_STATIC_CONTENT`；P0/P1/P2/P3＝0/0/0/4。** 无 P0/P1/P2，故不触发 `CHANGES_REQUESTED`；四条 P3 均为证据严谨性/文本一致性建议，不阻断。
- attempt3 两项升级阻断（P2-1、P1-1）与四项 `FIX_REQUIRED`（P3-1/2/4/6/7）在文本层面均已闭合，P3-3/P3-5 按要求保留；**未发现新增阻断问题**。
- **最小安全下一步**（按序，且任一步失败即停）：
  1. 由 Codex（非 Reviewer）对 16 项 pins 做 **pre-post 双重 byte/SHA-256 复算**；本 Reviewer 未提供 hash attestation，不得据本报告推断 MATCH。
  2. Codex adjudication：接受或要求补齐 §4 的 P3-1、P3-4 文本项（二者均可在不重跑独立 Review 的范畴内由 Owner 补 commit 或以 adjudication 记录，若改动交付字节则须重新冻结 pins）。
  3. 仅在同一 adjudication 通过后，按协议 §1 冻结态**由 Codex 执行** attempt4 executor；保持 `Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`Build/Cargo=NOT_RUN`、系统 AC1–AC7=`BLOCKED / NOT_RUN` 不动，且不得据本静态批准声称执行、闭包、Build 或 AC PASS。
- 未执行项（本会话）：parser、selfcheck、capability query、File.Replace、Git、任何 Windows API/registry/profile/ACL、进程枚举、Build/Cargo、capture/getter、system AC1–AC7、Windows Sandbox——全部 `NOT_RUN`。