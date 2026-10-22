# P02PRE-R1H Round6 attempt3 — 独立静态协议 Review（非作者 Reviewer）

## 0. 审查身份与范围

| 项 | 值 |
|---|---|
| Reviewer | DeepSeek Harness CLI（非作者；本轮不写文件） |
| Reviewer 实际模型 | `deepseek-v4.1-flash`（由本 harness 自身 system prompt 自述；非 pins 的 `preferredModel`） |
| Reviewer reasoning effort | UNKNOWN（host 未暴露） |
| pins 中 `preferredModel` | `gpt-6.1-sol/high`（与实际自述模型不一致，按规则记为 UNKNOWN/偏差，见 §7-Q6 说明） |
| Integrator/Adjudicator | Codex `/root`（协议作者、执行器作者 `/root/round6_executor` 亦属 Codex 侧） |
| 审查范围 | 仅冻结执行器 `p02pre-r1h-round6-integrator-20261012.ps1`、attempt3 控制性协议、不可变 attempt2 协议、pins 清单及其列明的 40 项只读输入 |
| 未做 | 未执行执行器/测试/Parser/selfcheck/capability query/File.Replace/Git/Windows API/registry/profile/ACL/Build/Cargo/capture/getter/AC/Windows Sandbox；未创建任何文件 |

---

## 1. Verdict

**VERDICT = CHANGES_REQUESTED**

**P0 = 0；P1 = 1；P2 = 1；P3 = 7**

依据：P0/P1/P2 任一 > 0 ⇒ CHANGES_REQUESTED（本轮 dispatch 规则）。P1-1 为静态可证的确定性阻断缺陷，冻结执行器按现状无法产生任何 integration 证据。同时见 §2：本会话 pin 闸门**未能清空**（非"匹配"，而是"无法核对"），因此**无论如何都不可能给出 APPROVED_STATIC_PROTOCOL**。

本 verdict 仅是对协议/执行器文本的静态否决，**不是**执行结果、Gate 放行、Build/AC 结论，也未改变任何 Gate 原值。

---

## 2. Pin 完整性核对（前后两次）——本会话无法执行，如实报告

### 2.1 关键环境事实（可复核）

本 DSH 会话的 shell 工具**完全不可用**，任何命令（含最小的 `'probe-ok'`）在沙箱初始化阶段即失败，命令体从未执行：

```
Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)
```

- `sandbox_permissions: workspace-write`（当前策略）与 `danger-full-access` 升级重试均失败；升级被拒原文：`sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`。
- 后台作业 `pwsh-3` 同样 `[status: failed, SetNamedSecurityInfoW failed (Win32 5)]`。
- 独立子代理探测得到**同一条原文错误**，并确认未产生任何输出、未读写文件。
- 因此：**无 shell ⇒ 无法计算任何文件的 byte length 与 SHA-256**（`read`/`grep`/`glob` 均不返回字节数或摘要）。
- `diagnose-windows-sandbox-acl` 技能要求在**非受限**模式下运行 ACL 修复脚本，而本会话无审批通道，且 dispatch 明确禁止 ACL 操作 ⇒ 该路径不可用，按技能要求"报为未诊断并停止"。
- `web_search` 亦不可用（HTTP 401，检索端点鉴权失败），故本报告中的 PowerShell/P-Invoke 语义结论**无新取得的一手在线引用**，均标明为静态推理。

### 2.2 实际完成的核对（PRE）

| 核对项 | 数量 | 结果 |
|---|---|---|
| pins 列明输入路径存在且可读（PRE） | **40 / 40** | 全部存在、可读；无缺失项、无 `BLOCKED_PIN_MISMATCH` 触发 |
| byte length 与 SHA-256 核对（PRE） | **0 / 40** | **不可执行**（无 shell）；未核对，故既不能判 MATCH 也不能判 MISMATCH |
| byte length 与 SHA-256 核对（POST） | **0 / 40** | 同上，不可执行 |

**结论**：pin 闸门状态为 **UNVERIFIED（不可执行）**，不是 PASS，也不是已证 MISMATCH。按 dispatch 规则我不调用 `BLOCKED_PIN_MISMATCH`（该 verdict 语义是"已证实不符"），但必须明确：**pin 闸门未清空 ⇒ 本会话输出不得作为静态批准使用**；即使 §4 内容部分全部干净，也只能是"未批准"。

### 2.3 可达的弱证据（明确不等价于 hash 核对）

1. **唯一可确证的字节事实（2/40 的旁证）**：`dsh-review-channel-probe-20261012.stderr.log` 读取结果为 `total 0 lines`，与 pins 的 `bytes: 0` 一致；`dsh-review-channel-probe-20261012.exit.txt` 内容为单行 `0` 且以 CRLF 结束（`0\r\n` = 3 bytes），与 pins 的 `bytes: 3` 一致。
2. **行数一致性（弱）**：全量读取的文件行数与角色相符（执行器 581 行；attempt3 协议 82 行；attempt2 协议 90 行；checkpoint 15 行）。
3. **代码文本级交叉核对（强于行数，仍非字节核对）**：执行器内嵌常量与 pins JSON 完全一致 —— `$OldHash`(行22)=pins `p02pre-r1h-selfcheck.ps1` 摘要；`$NewHash`(行23)=pins Owner selfcheck；`$CaptureHash`(行24)=pins root/Owner capture（两者同摘要）；`$HandoffHash`(行25)=pins Owner handoff；`$IndexHash`(行26)=pins `indexSha256`；行383/385/386/387/388/389 的 57648 / 57812 / 93124 / 3551 / 93124 / 8651 与对应摘要也与 pins 的 `bytes`+`sha256` 逐项相符。这**不能**替代对文件本身的重算。

### 2.4 实际读取对象（逐项，只读）

**A. 清单本体（非 40 项之内，为核对所必需）**：`verification/P02/codex-p02pre-r1h-integration-protocol-pins-round6-attempt3-20261012.json`（330 行，全文）。

**B. 40 项 pins 输入**（全部经 `read` 访问；标 ★ 为全文读取，其余为存在性+首行+总行数读取）：

1. `AGENTS.md` ★(仅首行) ｜ 2. `doc/09_COLLABORATION.md` ｜ 3. `doc/tasks/P02.md` ｜ 4. `doc/tasks/P02PRE-R1H.md` ｜ 5. `doc/REBASELINE_PLAN.md` ｜ 6. `doc/STATUS.md` ｜ 7. `doc/00_INDEX.md` ｜ 8. `verification/P02/p02pre-r1h-manifest-20261012.md` ｜ 9. `…selfcheck-round5-20261012.json` ｜ 10. `…engine-preflight-round5-20261012.json` ｜ 11. `…integration-execution-20261012.json` ｜ 12. `codex-subagent-…-review-r2-20261012.md` ｜ 13. `…-r2-adjudication-20261012.md` ｜ 14. `codex-subagent-…-static-review-round6-r2-20261012.md` ｜ 15. `…round6-review-adjudication-20261012.md` ｜ 16. `codex-…-review-pins-r3-20261012.json` ｜ 17. `codex-…-review-dispatch-r3-20261012.prompt.md` ｜ 18. `…handoff-20261012.md` ｜ 19. `…capture.ps1` ｜ 20. `…selfcheck.ps1` ｜ 21. `codex-p02-human-required-decision-20261010.md` ｜ 22. `…integration-protocol-attempt1-20261012.md` ｜ 23. `codex-subagent-…-review-round6-20261012.md` ｜ 24. `…review-adjudication-round6-20261012.md` ｜ 25. `codex-…-pins-round6-20261012.json` ｜ 26. `codex-…-dispatch-round6-20261012.prompt.md` ｜ 27. `…round6-integration-protocol-20261012.md` **全文** ｜ 28. `codex-…-pins-round6-attempt2-20261012.json` ｜ 29. `codex-…-dispatch-round6-attempt2-…prompt.md` ｜ 30. `codex-subagent-…-review-round6-attempt2-20261012.md` **全文** ｜ 31. `…review-adjudication-round6-attempt2-20261012.md` **全文** ｜ 32. **`…round6-integrator-20261012.ps1` 全文（581 行）** ｜ 33. **`…round6-integration-protocol-attempt3-20261012.md` 全文** ｜ 34. `codex-checkpoint-…-attempt3-active-20261012.md` **全文** ｜ 35–37. `dsh-review-channel-probe-20261012.{stdout.jsonl,stderr.log,exit.txt}` **全文** ｜ 38. `C:/…/p02pre-r1h-codex/verification/P02/p02pre-r1h-selfcheck.ps1` ｜ 39. `C:/…/p02pre-r1h-codex/verification/P02/p02pre-r1h-capture.ps1` ｜ 40. `C:/…/p02pre-r1h-codex/verification/P02/p02pre-r1h-round6-handoff-20261012.md` **全文**

未读取任何未列明路径；未做目录遍历；未运行 Git；未访问 `.tmp.driveupload`。

---

## 3. 逐条 Finding

### P1-1（阻断）Toolhelp 观察器用 `0` 作"无 child"哨兵，与 System Idle Process（PID 0）冲突 ⇒ 首个 Git child 之前即 fail-stop

- **文件**：`verification/P02/p02pre-r1h-round6-integrator-20261012.ps1`
- **行号**：`212`（`function ObserveProcesses($Record, [int]$ChildPid)`）、`226`（`$observed = @($all | Where-Object { $related.Contains($_.pid) -or $_.pid -eq $ChildPid })`）、`228-232`（Require 判定）、`230`（关键 `Require`）、调用点 `261`（`ObserveProcesses $record 0`，在 `$process.Start()` 之前）与 `418`（`AssertWriteSafe` 内）。
- **证据链（静态可证）**：
  1. `CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS,0)` 的快照**必然包含 System Idle Process，其 `th32ProcessID = 0`**（该 PID 是快照第一条记录，不可被过滤掉）。
  2. 行 `261` 以 `$ChildPid = 0` 调用；行 `226` 的 `-or $_.pid -eq $ChildPid` 因此把 PID 0 记录纳入 `$observed`。
  3. 行 `229` 仅跳过 `$entry.pid -eq $PID`（root，非 0）；PID 0 进入行 `230`：`Require ($entry.pid -eq $ChildPid -and $entry.parentPid -eq $PID -and $KnownChildren.ContainsKey($entry.pid))`。第三项 `$KnownChildren.ContainsKey(0)` 永远为 false（`KnownChildren` 只在行 `263` 于子进程启动后才写入，且执行器从不以 PID 0 启动任何子进程），故该 `Require` **必然抛出**。
  4. 抛出被行 `233` 的 `catch` 捕获并置 `$script:ProcessClosureBlocked = $true` 后重抛。
- **触发路径**：行 `430` `AssertRefs` → 行 `307` `GitValue` → 行 `297` `InvokeGit` → 行 `294` → 行 `235` `InvokeChild` → 行 `261`。
- **影响**：执行器在**任何 Git 身份查询之前**即终止；此时 execution evidence 尚未 `CreateNew`（行 `440` 未到达），故行 `552-578` 的失败路径只向 stderr 打印 `BLOCKED:` 并重抛，**不创建任何输出**。结论：`File.Replace`、Parser、selfcheck、capability query、S3 及全部 Round6 证据**在本冻结执行器下永不可达**；attempt3 集成无法给出任何执行结果。
- **安全性评估**：fail-closed，无写入、无数据损失、无越权，故定为 P1（非 P0）；但按 attempt3 协议 §3 第 34 行"any discrepancy in the static Review blocks execution"，本发现直接阻断执行授权。
- **最小修复**：行 `226` 删除 `-or $_.pid -eq $ChildPid`，或在 `$ChildPid -gt 0` 时启用该分支（哨兵改用 `-1`/`[int]::MinValue`）；预启动快照本就不应期待当前 child 存在，其 PID 归属由行 `263` 之后写入的 `$KnownChildren` + 后续快照覆盖。修复后需重新独立静态复核（本 Reviewer 不得自行修复）。
- **证据强度**：静态可证（不依赖运行）。

### P2-1（须动态确认，若成立为独立第二阻断）`$definitions` 每个元素都带前置一元逗号 `,@(`，可能使 `$definition[1]/[2]` 越界为空 ⇒ 观察器初始化即失败

- **文件/行号**：同上；`166-171`（`$definitions = @( ,@('CreateToolhelp32Snapshot', …) ,@('Process32FirstW', …) … )`）、`172-180`（`foreach ($definition in $definitions)` 后取 `$definition[0]`、`$definition[1]`、`$definition[2]`、`$definition[0]`）。
- **证据/机理**：`$definitions` 的四个元素均写作 `,@(...)`。若 PowerShell 将该列表作为**单个逗号表达式**求值，则其值应为 `Object[4]{ Object[1]{defA}, Object[1]{defB}, … }`；`@()` 只做一层枚举，`foreach` 得到的 `$definition` 是 `Object[1]` 包装数组，于是 `$definition[0]` 是整个定义数组、`$definition[1]`/`$definition[2]` 越界（`Set-StrictMode -Version Latest`，行 `3`），行 `173` 的 `$builder.DefineMethod(..., $null, $null)` 必然绑定失败（`returnType` 为 null）。反之，若 PowerShell 在此处对一元逗号做了展开，则代码正确。
- **影响（若成立）**：行 `429` `InitializeProcessObserver` 立即抛出 ⇒ 与 P1-1 同为"首个 child 之前 fail-stop"，执行器仍完全不可用。
- **为何是 P2 而非 P1**：结论取决于 PowerShell 逗号/数组子表达式的精确语义，**本会话无法执行 PowerShell 验证**（无 shell、无 web 检索），故不满足"静态可证"；但必须在重新审查前定案。
- **确认命令（只读、纯内存、不触碰仓库，供 Codex 在 pwsh 7.6.6 执行）**：
  `pwsh -NoLogo -NoProfile -Command "$d=@( ,@('a',[int],@([uint32])) ,@('b',[int],@([uint32])) ); $d.Count; $d[0].Count; $d[0][1]"` —— 若输出为 `2` / `1` / 空，则本缺陷成立（`$d[0]` 是包装层而非定义数组）。
- **最小修复**：删除四个元素的前置一元逗号（元素保持各自数组字面量；逗号表达式值即为四个定义数组），或把取值改为 `$definition[0][0..2]`，或改为哈希表/PSObject 数组。

### P3-1 Reviewer 报告通道：冻结协议与本次 dispatch 冲突（文件写入 vs stdout）

- **协议行**：attempt3 协议 `82`（"Reviewer … writes only the designated attempt3 report target with CreateNew"）。
- **冲突**：本轮 dispatch（本 session 指令）明确"不要创建 Review 文件；将报告返回到本次 DSH session stdout，由 Codex 原样保存到唯一 report target"；pins `reviewTargets`（`260-295`）同时把 `dsh-…stdout.jsonl`/`.stderr.log`/`.exit` 与 `codex-subagent-…-attempt3-….md` 列为待创建目标。
- **实际处置**：依 dispatch 执行 —— **本 Reviewer 未创建任何文件**。请 Codex 在 adjudication 中明确以哪条通道为准并记录该偏差。

### P3-2 pins 清单内部矛盾：`checkpointExcludedFromInputPins: true` 但 checkpoint 被列为输入

- **文件/行**：`…pins-round6-attempt3-20261012.json` 行 `329`（`"checkpointExcludedFromInputPins": true`）与行 `179-181`（inputs 第 34 项 = `codex-checkpoint-…-attempt3-active-20261012.md`，`bytes: 4957`）。
- **影响**：仅清单语义歧义，不影响执行器行为。**最小修复**：删除该字段或删除该 input 项，二选一并说明。

### P3-3 S2 顺序：文件/ACL/stream 证明晚于 S2 状态快照一个 child

- **行号**：执行器 `489`（`ReadStatus 'S2-root'`）先于 `490-503`（destination/apiBackup ACL、stream、hash 校验）；attempt2 协议行 `74`（"Immediately after return, query destination, stage, recovery, API backup and Handoff"）；attempt3 协议行 `54`（"capture S2-root as the first child after return"）。
- **评估**：attempt3 §4.6 明确以 S2-root 为 Replace 后第一个 **child**，故不构成违规（进程内查询不计 child）；但"Replace 返回至文件状态被证明"之间多了一个 Git child 的时间窗（约 10–100 ms），该窗口内的外部改动会体现在文件证据中而不体现在 S2 status 中。建议 Codex 在裁决中记录该解释。

### P3-4 `InvokeChild` 的 catch 未置 `$ProcessClosureBlocked`（Start 失败时可能已有残余子进程）

- **行号**：执行器 `281-285`（catch 仅记录 `$record.error` 并重抛）、`262`（`Require ($process.Start()) …`）、`567`（失败路径依据 `-not $ProcessClosureBlocked` 决定是否运行 FAILURE status）。
- **影响**：置位动作只存在于行 `183`、`233`、`271`、`415`。若 `Process.Start()` 在进程已创建后抛错，失败诊断仍可能启动 Git child，与 attempt3 §3 行 `32`"monitor failure / 未列明 child ⇒ 阻断"的意图不完全一致。**最小修复**：在行 `281` 的 catch 中先置 `$script:ProcessClosureBlocked = $true` 再重抛。

### P3-5 子进程生命周期无总时限（潜在挂起）

- **行号**：执行器 `267`（`do { ObserveProcesses $record $process.Id } while (-not $process.WaitForExit(10))`）。
- **影响**：只有退出后的管道排空有 5 s 上限（行 `270`）；若 Git/pwsh child 永久挂起，执行器将无限循环并保持 execution evidence 句柄打开，最终状态永不落盘。协议未规定超时。**最小修复**：增加墙钟超时，超时即视为 blocked 并 fail-stop（保留 partial 证据）。

### P3-6 `File.Replace` 前未紧邻重钉 destination（TOCTOU 加固缺口，无数据损失）

- **行号**：最后一次 destination pin 校验 `468`（S1），Replace 在 `486`，中间隔着 S1 status、多项 `AssertStable`/`AssertAbsent`（行 `473-481`）与 `SaveExecution`（行 `482`）。
- **影响**：若此窗口内 destination 被外部改写，进入 `apiBackup` 的将是改写后内容（冻结的 Round5 字节仍由 recovery 副本 `462` 保全，故**无数据损失**，仅证据语义被削弱）。**最小修复**：Replace 前紧邻再做一次 `AssertPin`/`AssertStable(destination)`。

### P3-7 执行证据流以 `FileShare.Read` 打开（允许第三方读取中间态）

- **行号**：执行器 `440`（`[IO.FileStream]::new(…,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write,[IO.FileShare]::Read)`）。
- **评估**：attempt2 §4 只对 stage/recovery/Handoff 复制要求 `FileShare.None`（执行器 `410` 已满足），未规定证据文件共享模式，故不违规；但写入中途可被其他进程读取到非最终态。**建议**：如无他因，改为 `FileShare.None` 或在裁决中说明需要可读性的理由。

**非 finding 的残余边界说明（记录而不计为缺陷）**：执行器的 Git 继承环境清理名单（行 `246`）严格等于 attempt2 §3.1 行 `46` 冻结的清单 + `GIT_CONFIG*`/`GIT_TRACE*`；`GIT_ALTERNATE_OBJECT_DIRECTORIES`、`GIT_OBJECT_DIRECTORY` 等未列入，且 attempt3 §4 行 `46` 明确"不得扩大或重新解释该边界"，执行器正确未自行扩大。该残余属冻结协议层面，不是执行器缺陷。

---

## 4. 七项独立判断结论

**Q1 protocol↔executor 一致性 / 写入面**
一致。写入目标由 `FullPath`（行 `61-64`）白名单收口（仅 `$Paths` 的 8 个值 + `capture.ps1` + 旧 handoff 两个只读例外）；实际写入仅两类：`CreateBytes`（行 `407-413`，`FileMode.CreateNew` + `FileShare.None`，写前 `AssertAbsent`+`AssertWriteSafe`）与**唯一一次**三参数 `[IO.File]::Replace`（行 `486`，`grep` 确认全文件仅此一处 `::Replace(`；行 `302` 的 `.Replace('/','\')` 是字符串方法）。全文件无 `Delete`/`Remove-Item`/`Move`/`Copy`/`Rename`/`Set-Acl`/`New-Item`/`Start-Process`/`Add-Type`/`Registry`/`Temp`/`WriteAll`/`WriteAllText`（grep 结果均为 `[Array]::Copy`、`CopyToAsync`、环境字典 `Remove` 等良性命中）。无清理、无回滚、无重试、无临时文件。

**Q2 状态时序 / 一次替换 / S2-S3 / 失败诊断**
`ReadStatus`（行 `335-336`）内部硬性 `Require ($null -ne $EvidenceStream)`，且 `434-441` 的次序为 identity → check-ignore → AssertAbsent → 快照 → `CreateNew` 证据 → `SaveExecution`，之后才 `S0-root`(443)/`S0-owner`(444) ⇒ **CreateNew 前严格无 status**。随后 `PRE_STAGE_RECHECK`(447) → `AssertHost`/`AssertRefs` → **独立的 `pre-stage-owner`**(450，非 S0/S1/S2/S3 标签，要求 clean) → 再 `PrecheckFiles`+`AssertStable`(452-453) → stage/recovery/handoff 三 `CreateNew`(461-463) → `S1-root`(465) + 三项精确 delta(466)。`File.Replace` **恰好一次**(485-486)，S2 为 Replace 返回后第一个 child(487-489)，S2/S3 的文件/ACL/stream/hash/delta 断言与 attempt2 §4、attempt3 §4.6-4.7 相符（唯一次序细节见 P3-3）。失败诊断(552-578)只在证据文件已存在时运行、状态标 `BLOCKED`、`ACTUAL_UNADJUDICATED`（行 `571` 传 `$false`）、不重试/不清理，符合 attempt3 §5。

**Q3 Git child 边界 / 固定 identity / 状态解析**
executable 与 CWD 由行 `237-238` 白名单硬约束（Git 仅 root/Owner，pwsh 仅 root）；`UseShellExecute=false`、逐项 `ArgumentList`、`--no-pager -c core.fsmonitor=false -c core.hooksPath=NUL` 前缀（行 `293`）与 attempt2 §3.1 逐字一致；环境清理与 `GIT_OPTIONAL_LOCKS=0`/`GIT_TERMINAL_PROMPT=0`（行 `246-257`）一致，且继承 `GIT_DIR`/`GIT_CONFIG*` 时在 `Start()` **之前** fail-stop。固定 refs（`304-324`，含 Owner `HEAD^`=`dd5d2e3b…`）、index 摘要（`325-334`，`$IndexHash`）与 `--porcelain=v2 -z` 参数表（`337`）一致，**`:(exclude).tmp.driveupload` 是独立 ArgumentList 项且为末项**。status parser（`340-351`）fail-closed：空记录、未知前缀、rename/ignored、缺失末尾 NUL、解码用 `throwOnInvalidBytes` UTF-8（行 `28`）全部 `Require`；delta comparator（`358-380`）在 `Enforce` 时要求 multiset **精确相等**，失败路径显式降级为 `ACTUAL_UNADJUDICATED`。

**Q4 Toolhelp 观察器真实边界**
静态上**成立**的部分：`DefineMethod` + `PinvokeImpl` + 显式 `MethodImplAttributes.PreserveSig`（行 `173-174`）与 BCL `TypeBuilder.DefinePInvokeMethod` 的内部实现同构，避免把返回 BOOL 的 native 函数误判为 HRESULT/retval 形式；`DllImportAttribute` 以命名**字段**注入 `SetLastError=true, ExactSpelling=true, CharSet=Unicode, CallingConvention=Winapi`（行 `176-178`），`ExactSpelling=true` 是必需的（否则 `CharSet=Unicode` 会去探测 `CreateToolhelp32SnapshotW`）；`bool` 返回按默认 4 字节 BOOL 编组、`SetLastError` 使 `Marshal.GetLastPInvokeError()`（行 `187/196/201`）在调用后立即读取有效；`byte[]` 为 blittable、按固定指针传入，native 写入对托管侧可见（`DefineParameter(2, In|Out)` 行 `179` 只是加强语义）；`PROCESSENTRY32W` 布局正确 —— `dwSize` 568(x64)/556(x86)（行 `189`，44+260×2 对齐 8 / 36+260×2）、`th32ProcessID` 偏移 8（行 `198`）、`th32ParentProcessID` 32/24（行 `190`）、`szExeFile` 44/36 且读取 520 字节（行 `191/198`），与 Microsoft Learn 结构定义一致；`CloseHandle` 置于 `finally` 且失败即 `Require` 抛错（行 `209`）⇒ 句柄关闭失败 fail-closed；根 PID 必须在快照中唯一出现（行 `206`）。**静态不成立/必须运行后才能验证**的部分：PID 0 哨兵缺陷（P1-1）实际破坏归属判定；`$definitions` 构造风险（P2-1）；Reflection.Emit 生成类型的实际 ABI、`GetLastPInvokeError` 的真实传播、x86 分支、以及"取样快照不能排除短于采样间隔的瞬时子进程"本身（执行器行 `49-50` 与协议 §3 行 `34` 已如实声明为 NOT_VERIFIED）。管道排水采用 `BaseStream.CopyToAsync`（行 `265-266`）+ 退出后 `Task.WaitAll(...,5000)`（行 `270`），无死锁且超时即置 blocked（行 `271`），设计正确；但缺总时限见 P3-5。

**Q5 文件状态/ACL/stream/index/hash/parent/保护输入/失败处理**
覆盖充分且 fail-closed：`AssertChain`（`83-104`）逐级拒绝 reparse 与非目录祖先并硬拒 `.tmp.driveupload`；`FileState`（`110-126`）校验普通文件、默认流唯一且长度一致，并记录 SDDL/流/字节/摘要；`ParentState`（`132-140`）校验父目录与命名流；`AssertStable`（`404-406`）以 JSON 全量比对冻结状态；protected 输入（root capture、旧 handoff、Owner source/capture/handoff）在 S1 与 S3 后反复重钉（`475-480`、`543-544`）。数据损失防护充分：仅 `CreateNew`（碰撞即失败，绝不覆盖）+ 一次 `File.Replace`，且旧字节同时存在于 recovery 与 apiBackup 两份（`462`、`493`、`501`），失败路径仅只读枚举实际状态并保留全部 partial 证据（`556-575`），无删除/回滚/重试。残余见 P3-6（Replace 前重钉窗口）。

**Q6 Reviewer 非作者性 / verdict 边界 / 残余与 waiver**
Reviewer 为非作者（pins 行 `6` "DeepSeek Harness CLI; non-author; static only"；协议行 `6-8`），执行器作者、协议作者、Adjudicator 均在 Codex 侧，无自审。协议行 `82` 明确 verdict 只能是不被阻断的 `APPROVED_STATIC_PROTOCOL`，且"Static approval is not execution, Gate or AC PASS"。残余风险原句与 Gate 原值在协议 `70-77` 与执行器 `40-47` **逐字保留**：`private_registry_absence=UNPROVABLE`、`Technical Gate=NOT_SATISFIED`、`Owner Risk Acceptance=APPROVED`、`Gate Disposition=WAIVED_BY_OWNER`、`Build Authorization=AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`、`Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`Build/Cargo=NOT_RUN`、系统 AC1–AC7=`BLOCKED / NOT_RUN`。协议 `78` 与执行器 `1-2` 亦未越权授权 capture/getter/profile/registry/ACL/Build/Cargo/AC/Windows Sandbox。补充：pins 声称 `preferredModel=gpt-6.1-sol/high`，而本会话实际自述模型为 `deepseek-v4.1-flash`、effort 未暴露 ⇒ 建议 Codex 按历史做法记为 `UNKNOWN`/偏差，不要据 pins 推断模型。

**Q7 Finding 总览**
见 §3：P0=0、P1=1（P1-1）、P2=1（P2-1）、P3=7（P3-1…P3-7）。两条与执行器本体直接相关（P1-1、P2-1）均集中在 attempt3 新增的 Toolhelp 观察器；其余为协议/清单/加固类问题。

---

## 5. 未验证限制（NOT_VERIFIED / NOT_RUN）

1. **任何动态行为均未验证**：执行器、File.Replace、Parser/selfcheck/capability query、capture/getter、AppContainer/profile/registry/ACL API、动态隔离、Build/Cargo、系统 AC1–AC7、Windows Sandbox —— 全部 NOT_RUN（与 pins `execution`(行 `297-309`) 及协议 §1/§8 一致）。
2. **pin 的 byte length 与 SHA-256 未经本 Reviewer 核对**（0/40，原因见 §2）；PRE/POST 双次核对机制在本会话不可执行。Round5 AC2=FAILED 是历史结论，本轮未复测。
3. **P2-1 的 PowerShell 语义未在本会话定案**；web 检索不可用（401），故本报告未附新的一手 API 文档引用，P/Invoke 结论仅为静态推理（与协议 §3 自身声明一致）。
4. Rust/实际工具链、refs/index/status 的真实运行值、ACL/stream/卷/路径链、子进程闭包与 Replace 后状态，均须由后续执行阶段实际取证；静态文本与静态审查**不构成**任何 PASS。
5. 未验证 `$capability.Count -eq 7`、`$summary.Count -eq 9` 等冻结契约字段是否与 selfcheck/capability 实际输出完全一致（依赖运行）。

## 6. 未运行 / 未修改输入的确认

- 未运行 `p02pre-r1h-round6-integrator-20261012.ps1`，未运行任何测试、Parser/selfcheck、capability query、Git 命令、Windows API、profile/registry/ACL 操作、Build/Cargo、capture/getter、AC 或 Windows Sandbox。
- 未修改、覆盖、删除或创建任何 input；未做自动修复；**未创建 Review 文件**（依 dispatch），本报告仅以文本返回本 session stdout，由 Codex 原样保存到唯一 report target。
- 唯一的写方向操作尝试（`pwsh` 调用）在沙箱初始化阶段即失败于 ACL 授予（Win32 5），从未执行命令体，因此不构成对仓库的任何写入。
- 本会话对仓库的全部动作均为只读：`read`/`grep` 与失败的 `pwsh` 探测。

---

## 7. 推荐下一步

**无需由本 Reviewer 继续操作。** 建议 Codex `/root` 执行：

1. 在具备可用 shell 的环境中**独立复算** attempt3 pins 的 40/40 byte length + SHA-256（本会话的 pin 闸门记录为 UNVERIFIED，不得据本报告推断 MATCH）；并把 DSH 的 `SetNamedSecurityInfoW Win32 5 / grantWrite(G:\CODEX\New Manga)` 环境故障作为 DSH 通道限制记入 checkpoint（如需 DSH 出具独立 hash attestation，须在有审批通道/可用 shell 的会话重派）。
2. 对 P1-1 与 P2-1 判为 `REQUIRES_CHANGE`：修 P1-1（行 `226` 去掉/守卫 `-or $_.pid -eq $ChildPid`），并用 §3-P2-1 的单行 PowerShell 检查对 `$definitions`（行 `166-180`）定案后修正；随后**必须重新 dispatch 独立静态 Review**（新执行器哈希 + 新 pins），不得沿用本轮结论。
3. 把 P3-1…P3-7 记入 attempt3 adjudication 的 finding 台账（P3 不阻断，但必须记录），并特别处理 P3-1（报告通道）与 P3-2（pins 字段）两处清单一致性。
4. 在静态批准前，保持 `Build Gate=BLOCKED`、`Hard Build Barrier=EFFECTIVE`、`Build/Cargo=NOT_RUN`、系统 AC1–AC7=`BLOCKED / NOT_RUN`，不因本轮 Review 释放任何 Gate/AC。
