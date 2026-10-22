# P02PRE-R1H-H2-COLLECTOR 非作者静态源码 Review

- Reviewer：DeepSeek Harness（非作者；只读、静态）
- 实现 head：`831e368b2d564a27859a188e5efa575c8ff7fb7e`（`agent/zcode/P02PRE-R1H-H2-COLLECTOR`，base `343895fb5f0329c0c07a7104ec321b698f967607`）
- 文档 head：`af151e79043e93d8e71f83886ac8732685310f42`；Owner=ZCode，Integrator=Codex
- 审查对象：`tools/p02/h1-raw-pre-run.ps1`（1160 行）、`tools/p02/h1-raw-pre-run-selftest.ps1`（393 行）、两份证据日志、Task/Handoff，以及契约第 2 条点名的 frozen inputs（只读）
- **Verdict：`CHANGES_REQUESTED`（H2-01 P1、H2-02 P2 未闭合）**

**Reviewer 环境限制（必须披露）**：本会话 shell 完全不可用——workspace provisioning 阶段 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`，且无审批通道可升级，因此我**没有**运行 git / Parser / selftest / 任何 hash 命令，也**没有**运行 live collector 或任何 getter。以下结论全部来自逐行静态阅读（read/grep/glob 可正常读取 workspace 内文件与 frozen inputs）。因此：(a) 我未独立复算 4 个交付文件的 sha256/bytes（selftest 日志 SUMMARY-JSON 内的 `collectorSha256=44E7654C…` 可佐证 collector 一个文件，selftest 脚本与两份日志的 hash 在本交付内无自证）；(b) scope/越界与 EOL/blob 一致性按 Codex 已核验结论采信。

---

## 一、发现（Findings）

### H2-01（P1，运行阻塞）A6 冻结状态记录用 porcelain v1 的 `?? ` 前缀，与同一脚本冻结的 `--porcelain=v2` argv 自相矛盾 → `status-a6` 必然 FAIL

**位置**：`tools/p02/h1-raw-pre-run.ps1:161-165`（`FrozenA6StatusRecords`）、`:360-365`（`New-StatusArgv`，含 `--porcelain=v2`）、`:1013-1024`（`status-a6` 用 `Compare-Object -CaseSensitive` 比较**含前缀的**记录文本）。

**证据链（三条独立证据，全部可复现）**：

1. 契约第 2 条要求静态读取的 frozen input——A6 delivery 的 attempt6 executor（pin `43527 / 1C8D6220…`）——自己在 `verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1:417` 构造预期的 untracked 记录：
   `$key = [Convert]::ToBase64String($Utf8.GetBytes('? ' + $path))`
   即 `'? '`（**2 字符**），并在 `:399` 用 `^(1 |2 |u |\? |! )` 校验记录。collector 却冻结为 `'?? '`（3 字符）。
2. git 官方手册（本机 Git 2.52，手册 2.53.0，注明 `2.45.1 → 2.52.0 no changes`）：短格式用 `??`；**Porcelain Format Version 2 → "Other Items"：`? <path>`**（ignored 为 `! <path>`）。`-z` 只改路径引号与终止符，不改状态前缀。
3. 字节算术闭合：三条相对路径长度 68 + 76 + 67 = **211**；`223 = 211 + 3×3 + 3×NUL` ⇒ 前缀 3 字符（`?? `）；v2 形式应为 `211 + 3×2 + 3 = 220`。

**后果**：live run 时 `$a6RecordTexts` 为 `'? <path>'`，与冻结的 `'?? <path>'` 逐条不等 → `Compare-Object` 非空 → `status-a6` = FAIL → `BlockedReasons` 非空 → `BLOCKED_BY_FAILED_CHECKS`（exit 4）。这是**按构造必然发生**的失败，而证据会呈现为“A6 status drift”，与事实（无漂移）不符。失效方向是 fail-closed（不会误记 PASS、无数据风险），但交付物唯一目的（可授权运行一次并完成采集）不可达。

**修复建议**：改为 `'? ' + path`，或按 executor `AssertDelta` 的语义在比对前剥离 2 字节状态字段后只比路径；并在 selftest 增加“FrozenA6StatusRecords 前缀符合 v2 格式”的大小写敏感断言，防回归。

---

### H2-02（P2，违反契约第 6 条 “call ID 唯一”）`TEMP == TMP` 时产生重复 observation / check ID

**位置**：`h1-raw-pre-run.ps1:934-944`（`foreach ($probePath in (@(TEMP, TMP) + $script:ScratchCacheProbePaths))`，`$safeId = ($probePath -replace '[^A-Za-z0-9._-]', '_')`，无去重、无序号）。

**事实**：脚本自身 `:932` 记录 “historical v2 observed both at `C:\Users\49745\AppData\Local\Temp`”，即历史与当前环境下 `TEMP == TMP` 成立 → 同一 `path-probe-C__Users_49745_AppData_Local_Temp` 会出现 **2 条 observation + 2 条 check**（`Add-ObservationRecord`/`New-CheckRecord` 均无唯一性校验）。

**后果**：closed JSON 的 `observations[].id` 与 `checks[].id` 各重复一次，违反契约第 6 条 “call ID 唯一”；指针仍按 seq 可解析，故不产生错误 PASS，但报告不可按 ID 唯一索引，审计歧义。**修复**：按大小写不敏感去重（或按出现序加 `-1/-2` 后缀），并加唯一性断言。

---

### H2-03（P3）helper 异常路径会丢弃已捕获的 OS exit（AC2 证据保真）

**位置**：`:603`（`$obs.exit = $process.ExitCode`）→ `:609`（`PostProcess`，status 派生记录即在此）→ `:610-618` catch 中 **无条件** `$obs.exit = $null`。

进程已成功退出、但 `PostProcess` 抛异常（如 `Split-NulRecords` OOM）时，真实 OS exit 被覆盖为 `null`。契约第 3 条/AC2 要求 OS exit 完整保存。建议仅在“未曾退出/未曾启动”时置空（或用标志位保护）。

### H2-04（P3）`.tmp.driveupload` 之外的 check 指针只做前缀校验，不校验存在性

**位置**：`New-CheckRecord:426` 仅要求 `StartWith('/observations/')`；`Resolve-JsonPointer`（`:320-348`）在 collector 运行时**从未被调用**（只在 selftest 用）。契约第 6 条 “checks raw pointer 必须存在”。当前全部 20 处 `Add-Check` 我逐条核对均能解析（见第三节），但机制上 `/observations/999/…` 这类悬空指针会被接受。建议在 `Add-Check` 或写 closed 行前对 `$script:Observations` 做解析断言，fail-closed。

### H2-05（P3）契约第 2 条点名的 frozen input `doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md` 未被 pin

`FrozenSourcePins`（5 项）+`FrozenV2EvidencePins`（4 项）均与 v2 JSON / attempt6 protocol / R6-ZCODE-H1 Task 记录一致（见第三节），但 V2 四文件 pin 的来源文档本身没有 size/sha256 pin，冻结溯源链缺一环。建议补 pin。

### H2-06（P3，contract-literal）契约第 7 条 “closed JSON 包含 before/after protected/index/source pins” 只对 protected 有前后对照

- protected：`:787` / `:1118` + `:1123-1127` 前后比对 ✓
- index：`:1027-1040` 单次读取（且发生在 git status 子进程**之后**），与 attempt6 冻结值比较——无法区分“运行前既有漂移”与“本次 git 子进程导致的漂移”
- frozen source pins / v2 pins：`:799-811` 单次读取，无 after 复核

注：契约第 3 条把“前后”明确只挂在 protected 上（“protected selfcheck … 前后”），故本条可能属第 7 条措辞的口径问题，**建议 Codex 裁决**；无论裁决如何，补 after 读+比对都能显著增强“collector 未扰动源/索引”的可证性。

### H2-07（P3 / nit 集合）

- `:992` `$rootRecords` 定义后未使用（死变量）。
- `Open-ExclusiveCreateNew` 成功但 `StreamWriter` 构造失败时（`:739`），catch 走 Writer 为 null 分支（`:1152-1153`），仅写 stderr；保留下来的空 run 文件没有 closed 行/disposition，与第 7 条“保留部分失败证据”不完全吻合（建议直接向 stream 写最小 closed 行）。
- `Test-RunIdFormat`（`:350-353`）collector 内无调用点（仅 selftest 使用）；实际由 param `ValidatePattern` 兜底，属可接受但不必要的定义。

---

## 二、供 Codex 裁决的输入（非本交付缺陷）

**AI-01**：H2-01 的算术表明，被 collector 静态继承的历史 v2 状态快照 **不是**由其冻结 argv（`--porcelain=v2 -z`）产生的：
- `e-agy-status`：`223 B / sha256 25316B54…`（v2 JSON；stdout log `:1145-1148` 亦以 `?? ` 呈现）——v2 语义应为 `220 B`；
- `e-root-status`：`1137 NUL / 79291 B` ——若同样每条多 1 字节，真实 v2 载荷应为 `78154 B`，sha `0DB72CDA…` 随之不成立。

即“记录文本/字节/sha 与冻结 argv 不一致”，属 **P2-1/H1 证据链**的上游问题，不能由 H2 代为修复，但会影响”H1 gate input“的取值口径，建议 Codex 在 adjudication 中显式登记。

---

## 三、静态核对为“一致/正确”的部分（平衡记录）

1. **写通道与禁止面**：全脚本仅一处 `[IO.FileMode]::CreateNew` + `[IO.FileShare]::None`（`:444`），无其他 `Out-File/Set-Content/New-Item/Remove-Item/Copy/Move/Delete/WriteAll*`；无 `Add-Type/P-Invoke/Start-Process/Invoke-Expression/AppContainer/Toolhelp/Process32*/Set-Acl/icacls/Registry 写 API`；注册表仅 `[Microsoft.Win32.Registry]::LocalMachine.OpenSubKey(path, $false)`（`:887`）且只取 `SubKeyCount/GetSubKeyNames/ValueCount/GetValueNames`。selftest 的 AST 断言与此独立一致。
2. **frozen 常量逐项对齐**（我读了原始 frozen inputs 逐条比对）：`attempt6-protocol 14084/DDDFDF58…`、`attempt6-owner-handoff 13190/6F1E908C…`、`attempt6-executor 43527/1C8D6220…`、`actual-owner-handoff 9505/E13C7148…`、`protected-selfcheck 57648/977C9943…` 与 v2 JSON `frozen_pins` 一致；`v2-json/stdout/stderr/exit` 四 pin 与 R6-ZCODE-H1 Task 的 v2 登记一致；`root main@343895fb… tree e12bd627…`、`candidate agent/codex/P02PRE-R1H@c1cc2681… tree 96e7273d… parent dd5d2e3b…`、`a6 …-EXEC-A6@343895fb…`、`index C5CA8884…`、SDDL 字符级一致、7 个 executor targets 与 protocol §2 逐条一致、`GateBaseline` 10 项与 protocol §6 一致。**唯一矛盾是 H2-01。**
3. **executor 静态契约检查可通过**：`:1065-1109` 断言的 15 条 literal，我在 pinned executor 中逐条定位到原文（`:6-9, 278, 283, 285, 290, 297, 346, 390, 487, 574, 584`）→ 该 check 运行时应 PASS。
4. **child 契约**：`contextNames` 列表与 executor `:286` 完全相同；GIT_TRACE* 仅移除并记名，GIT_CONFIG*/context 继承时 fail-stop 不启动；`GIT_OPTIONAL_LOCKS=0`/`GIT_TERMINAL_PROMPT=0`；`UseShellExecute=$false` + `ArgumentList` + `BaseStream.CopyToAsync` 原始字节捕获（避开编码与死锁）；status argv 恰 15 项、排除 pathspec 独立且最后。
5. **指针自查**：全部 20 处 `Add-Check` 的 `ObservedPointer` 均指向真实 observation 的 `output/value` 或 `output/stdout`（按 seq = 数组下标可解析）；`ConvertTo-RawBytesRecord` 对空字节/含 NUL/非法 UTF-8/超限的处理与 AC2 一致（NUL 计数 + base64 + sha256，空字节不视为缺失）。
6. **证据日志内部自洽**：我数出 pure-selftest 日志中 `[ASSERT PASS]` 恰 90 行、FAIL 0 行、SKIP 6 行（全部为契约禁止的 live 范围并逐项写明原因），SUMMARY-JSON `assertsPassed=90/assertsFailed=0`，与 Task/Handoff 声明一致；Parser 日志两脚本 `errors=0`。
7. **Gate 原值与证据分级**：`GateBaseline` 原值整块保留；meta/closed 均带 `NEW_TIME_EVIDENCE`/`CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE`、`historyNote` 与 `notRun` 块，未给 H1/X6 授予任何通过。

---

## 四、DISPOSITION

| 项 | 级别 | 状态 |
|---|---|---|
| H2-01 A6 状态前缀与 v2 argv 矛盾（必然 FAIL） | P1 | OPEN（阻塞） |
| H2-02 TEMP==TMP 重复 call ID | P2 | OPEN（阻塞） |
| H2-03 helper 异常路径丢弃 OS exit | P3 | OPEN |
| H2-04 指针仅前缀校验、无存在性断言 | P3 | OPEN |
| H2-05 R6-ZCODE-H1 Task 未 pin | P3 | OPEN |
| H2-06 第 7 条 before/after 仅 protected | P3 | OPEN（待 Codex 裁决口径） |
| H2-07 nit 集合 | P3 | OPEN |
| AI-01 上游 v2 状态快照与冻结 argv 不一致 | adjudication input | 交 Codex |

**本次 Review 未运行（一律不作为 PASS）**：live collector、profile/LPAC liveProbe、任何 registry/WER/ACL/AppContainer live getter、git 子进程、executor、ProcessObserver/Toolhelp、Build/Cargo、AC1–AC7、Windows Sandbox；亦未在 Reviewer 侧执行 Parser/selftest（纯测试不能替代 live 证据，亦不能覆盖 H2-01/02/03/04 这类 live/结构层问题）。我未写任何仓库文件（本报告为 stdout Markdown，由 Codex 捕获落盘）。

**不改变的历史结论**：H1 v2 23 PASS（24 checks = 23 PASS/1 NOT_VERIFIED）、P2-1 OPEN、Gate 原值（Technical `NOT_SATISFIED`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo `NOT_RUN`、AC1–AC7 `BLOCKED / NOT_RUN`）全部保持；本 Task 产物不得作为 X6 S0。

---

## 五、推荐下一步

1. **ZCode**（同一 allowlist，新 commit）修复 H2-01、H2-02，并处理 H2-03/H2-04/H2-05；H2-06 待 Codex 裁决。
2. **DeepSeek Harness** 对新固定 head 做 exact-head 静态复核（仅 H2-01/02 的闭合判别 + 无回归）。
3. **Codex /root** 做 pin pre/post verification、裁决 H2-06/AI-01，并决定是否释放 live-run Task（另行冻结 RunId 与 exact targets）。

可直接转发给 ZCode 的指令：

> 对 `agent/zcode/P02PRE-R1H-H2-COLLECTOR` 从 `831e368b2d564a27859a188e5efa575c8ff7fb7e` 继续返修，仍在原 allowlist（`tools/p02/h1-raw-pre-run.ps1`、`tools/p02/h1-raw-pre-run-selftest.ps1`、`verification/P02PRE-R1H-H2-COLLECTOR/`、`doc/tasks/P02PRE-R1H-H2-COLLECTOR.md`）内：
> (1) **P1**：`FrozenA6StatusRecords` 现为 `'?? <path>'`，但同一脚本冻结的 argv 是 `--porcelain=v2 -z`，git v2 的 untracked 记录是 `'? <path>'`；被契约第 2 条要求静态读取的 attempt6 executor（`verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1:417`）自己就是 `'? ' + $path`。字节算术（三条路径 211B，`223 = 211+3×3+3`）亦证明历史 `223 B/25316B54…` 不是 v2 产物。请改为 v2 语义（`'? ' + path`，或剥离状态字段后只比路径），并在 selftest 增加大小写敏感断言防回归。
> (2) **P2**：`h1-raw-pre-run.ps1:934-944` 对 `TEMP`/`TMP` 无去重；历史与当前 `TEMP == TMP`，会产生重复 observation/check ID，违反契约第 6 条 “call ID 唯一”。请去重或加序号，并加唯一性断言。
> (3) **P3**：helper catch 中 `$obs.exit = $null` 会覆盖已捕获的真实 exit（PostProcess 抛异常时），请保护；`New-CheckRecord` 只校验 `/observations/` 前缀，请增加指针可解析断言；补 `doc/tasks/P02PRE-R1H-R6-ZCODE-H1.md` 的 size/sha256 pin。第 7 条 “before/after protected/index/source pins” 的 before/after 范围待 Codex 裁决后再决定是否补 after 读。
> 完成后固定新 delivery head、更新 Handoff/Task 证据表（含复跑 Parser 与 selftest 的完整日志、环境、exit），交 DeepSeek Harness 非作者 exact-head 复核；**不得运行 live collector**。

若 Codex 裁决 H2-01/H2-02 不予接受（例如认定 H2-06 式口径问题），则本条即改为“无需下一步操作”。