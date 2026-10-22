# P02PRE-R1H-H2-COLLECTOR — R4 exact-head 非作者静态复审

**Verdict：`CHANGES_REQUESTED`**

> 独立重读：本会话**重新完整读取** `b2cea30d` worktree 下的 collector（1792 行）与 selftest（728 行），未沿用 R3 verdict。只读；未运行任何脚本/collector/getter/子进程/Build/AC/Sandbox/注册表/ACL/profile 查询；未写入或修改任何文件。

---

## 一、Reviewed identity（commit / blob）

| 项 | 值 | 我的验证 |
|---|---|---|
| reviewed code commit | `b2cea30d05fd66b731bf8caf18358912eb66ebe6` | ✅ 见下 reflog |
| 父（前一文档）commit | `8bba48bd9c0f08ffe6e81a5fd2277514595d0d27` | ✅ |
| branch | `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` | ✅ 与 manifest/Task 一致 |

`G:/CODEX/New Manga/.git/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3/logs/HEAD`（git 自身写入的文本）第 5 行：

```
8bba48bd… → b2cea30d…  commit: fix(P02): close R3 findings (R3-CX-01..04) for H2 collector R4 per source-review-r3-adjudication
```

- **Git 被沙箱阻断（诚实声明）**：本会话 `pwsh` 在启动阶段即被拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`），一次尝试后我**未做任何绕过/提权重试**，因此**没有**独立复算 git blob SHA-1 或 SHA-256。
- **交叉印证（非我复算）**：manifest(`review-input-manifest-r4.json` L13/L15、L21/L23) 记 `gitBlob == worktreeBlob`（collector `2f066061…`、selftest `fd109a0f…`）；Codex 独立 run record（L20-23）复算一致；两次独立执行（Owner R4 log 与 Codex R4 log L213）均把同一 worktree 路径哈希为 `3824AD50…` / `AA68881F…`。
- ⚠️ **证据不一致（需 Codex 复算裁定）**：R4 Handoff L23/L24 记 `107386 / 3824ad50…` 与 `58641 / aa68881f…`，而 manifest L13/L21 记 `107299 / 3824ad50…` 与 `57555 / aa68881f…`。**SHA-256 相同、byte 数不同**，二者不可能同时为真（详见 P3-4）。

---

## 二、Codex adjudication R3-CX-01..04 逐项判定

### R3-CX-01（真缺失 vs 非缺失属性错误；check 不得 PASS）— **代码 PASS / 要求的判别力 selftest FAIL（未闭合）**

| 要求 | 代码证据（collector） | 判定 |
|---|---|---|
| 仅 FileNotFound/DirectoryNotFound 视为 absent | L1012-1021：解构 `InnerException`（L1015），仅两类 NotFound → `New-PathProbeAbsentValue`（L1017），否则 → `New-PathProbeErrorValue`（L1019） | ✅ PASS |
| 其它 GetAttributes 错误原样记录 | `New-PathProbeErrorValue` L379-397：`absent=$false`、`attributeError="<type>: <msg>"`、`probeOnlyNote` 明示非法缺失 | ✅ PASS（仅缺 HResult，见 P3-5） |
| 对应 check 不得 PASS | moniker L1457-1463 → `NOT_VERIFIED`；plan 逐项 probe L1541-1547 → `NOT_VERIFIED`；7 target L1646-1652 经 `$targetChain.leafAbsent`（L556-568）→ FAIL | ✅ PASS |
| false absence/error 不得进入最终 gate | 门控类 check 全部与严格链分类 `-and`：`$absentOk` L1646-1648、`$parentOk` L1649-1652；错误导致 `leafAbsent=$false` 或 `exists=$false` → FAIL → `BlockedReasons`(L798) → exit 4 | ✅ PASS（无 fail-open） |
| **新增"meaningful selftest 区分真缺失与非缺失错误"** | selftest L217-219 仅 **字符串包含**断言；L605-619 只调用两个 shape 工厂 + **内联复制**映射表达式（L616-617），未驱动 `Get-PathProbeObservation` 的分类分支；且 L606 的 `$missingPath` 建了却从未被探测 | ❌ **FAIL** |

**为何判 FAIL 而非视为达标**：adjudication 对 CX-01 只给了"meaningful selftest"一项，而对 CX-02 明确允许"a focused selftest **or** a precise source assertion"（L27）——这一措辞对比说明 CX-01 要求的是**行为**判别。现有 r401 在"错误 → absent/PASS"这一危险回归方向下**仍会全部 PASS**（工厂不变、token 仍在），因此不是判别力负例；Handoff L34 的"r401 系列断言完整覆盖"属过度声明。

**最小修复（两处，均为测试面）**：把分类与结果映射抽成纯函数（例如 `New-PathProbeValueFromAttributes -Path … -Attributes … -AttrException …` 与 `Get-ProbeCheckResult -Value …`），由 collector 主序列的两个 check 点调用；selftest 用 AST 提取后直接驱动三例：(a) `$null` 属性 + `FileNotFoundException` → absent shape；(b) `$null` 属性 + `UnauthorizedAccessException` → error shape 且结果为 `NOT_VERIFIED`；(c) 真实属性 → present shape。

### R3-CX-02（reparse leaf 不解引用目标、保留 link target）— **PASS**

- 代码 L1037-1056：`if ($isReparse)` 分支**只**读 `LinkTarget`（L1042-1046），**不再**触碰 `FileInfo.Length`；`Length` 仅在 `-not $isReparse -and -not $isDir` 时读取（L1050-1054）。全文件仅此一处 `Length` 读取（grep 确认）。
- 悬挂链接证据保留：`LinkTarget` 不解析目标，dangling 仍返回存储目标；selftest L621-631 以真实 junction（先 live 后删除 target 造 dangling）断言 `LinkTarget` 保留 —— execution fact 在 Codex 独立 log L196-197 均 PASS。
- 为 `$null` 属性/错误分支提供完整 shape（L364-397），StrictMode 安全。

### R3-CX-03（运行时 PSHOME 派生路径守卫 + raw observation + fail-closed）— **PASS**

- `$fixedPaths` 显式纳入 `$PSHOME` 与 `(Join-Path $PSHOME 'pwsh.exe')`（L1188）；`exclusion-scope-fixed-paths` observation（L1194-1216）在**任何 probe 之前**（早于 L1348）以纯字符串产出完整 `{path, underExclusion}` manifest，L1210 `Require` fail-closed（exit 5）。
- `tools-pwsh`（L1346-1371）：L1346-1347 捕获真实 `$PSHOME`；`GetterInput` 显式带 `runtimePsHome`/`runtimePwshExe`（L1355-1356）→ 入口守卫 L856（纯字符串，先于任何 FS API）；body 内 L1360-1362 再次守卫；之后才 `[IO.File]::Exists($src.runtimePwshExe)`（L1369）。body 不再读实时 `$PSHOME`，记录值与探测值同一对象。
- fail-closed 三路：**under-exclusion** → L1210 Require 或 L1360 throw → getter state=ERROR → L872 `Require` → 外层 catch exit 5（越界路径记入 observation.exception）；**漂移** → `$tv.psHome -ceq ExpectedPsHome` 或 `pwshExeExists` 为假 → `tools-pwsh` FAIL → exit 4（L1373-1379）；**异常** → 同上 exit 5。

### R3-CX-04（launcher 与 H1 snapshot 进入 chain 验证，且在用前）— **代码 PASS / 测试约束偏差（P3-1） + 停止语义偏差（P3-2）**

- `$chainPaths` 现含 `$script:GitExe`、`$script:WhoamiExe`、`$script:PwshExe`、`(Join-Path $PSHOME 'pwsh.exe')` 与 H1 Task snapshot 绝对路径（L1246-1249），并在 L1253-1290 断言 `allOrdinary` + `noLeafReparse`。
- 时序：chain 检查（L1253）**先于** H1 snapshot 读取（L1293）、先于 `git --version`（L1382）、先于 `whoami /all`（L1416）——满足"检查发生在被执行/读取前"。
- ❌ 偏差一：adjudication L29 明令 "**do not probe or modify system paths to test this**"，但 R4 selftest L641-654 对 `C:/Program Files/Git/cmd/git.exe`、`C:/Windows/System32/whoami.exe`、`C:/Program Files/PowerShell/7/pwsh.exe` 与 root Task 文档做**实时** `[IO.File]::Exists` + `Test-PathAncestorsOrdinary`；Codex 独立 log L199-202 显示 4 条 `r404-launcher-ordinary-*` 实际执行并 PASS（即确实探测了系统路径）。
- ❌ 偏差二：该验证是 FAIL check 而非用前硬停（详见 P3-2）。

---

## 三、原 R2/P4 项是否仍闭合 —— 全部仍闭合，未发现回归

| 项 | 证据（R4 行号） | 判定 |
|---|---|---|
| R2-01 CreateNew 前/后 output facts + pointer | 纯字符串检查 L1119-1120 → preflight 捕获 L1123（`Test-PathUnderExclusion` 先于 L616-619 的 FS 访问）→ CreateNew L1131 → post facts L1133 → check L1238-1243（pointer `…/output/value`，`Add-Check` L794-796 运行期解析） | ✅ |
| R2-01 冲突 fail-closed | L1129 `Require targetAbsent` → exit 2；竞态由 L763 `FileMode.CreateNew` 抛 → L1770 catch → exit 5 | ✅ |
| R2-02 leaf/祖先 reparse、dangling absence、nonDirectory | `Test-PathAncestorsOrdinary` L506-604（未变）：lstat leaf L537-547、真缺失 vs 查询错误 L556-568、祖先 reparse L581-586、`nonDirectoryComponents` L587-588 并被 L598-602/L1125/L1284 消费；target absence L1646-1648 | ✅ |
| R2-03 全入口纯字符串排除守卫 | 逐一枚举全部 FS/子进程入口（见下表），全部在访问前有本地守卫 | ✅ |
| R2-03 动态 TEMP/TMP manifest | L1467-1481 取值 → L1490-1497 plan（入口守卫 L856）→ **L1517-1531** `{path, underExclusion}` raw observation（早于 L1539 probe）→ L1533-1537 check | ✅ |
| R2-04 index-after 最后采样 | L1745-1760，晚于最后子进程（L1642 loop）与全部源文件读取，早于 closed L1762 | ✅ |
| P4 plan pointer / nonDirectoryComponents | L1503-1508 pointer 指向含完整 plan 的 observation；L598-602 实际消费 | ✅ |

**R4 全部 FS/子进程入口与守卫对照**（grep 枚举，14→20 处）：L537（守 L514）、L581/587（守 L514）、L746-747（守 L743）、L763（守 L760）、L900-901（守 L887）、L982（守 L974+L856）、L1008（守 L994+L1002+L856）、L1073/1076/1080（守 L1063+L856）、L1124（守 L1119+preflight L611-612）、L1320（守 L856）、**L1369（守 L1360+L856+L1210）**、L1387-1388（`$fixedPaths` L1186 + Require L1210 + chain L1248）、L1669（守 L856）、L1750（守 L856）。唯一写入通道仍为 L763 `CreateNew + FileShare.None`；全文件无 `WriteAll*`/`New-Item`/`Remove-Item`/`Set-Content`/`Out-File`/`Add-Type`/`Start-Process`/`Invoke-Expression`/`DllImport`/Toolhelp/AppContainer 调用；注册表仍 `OpenSubKey(name,$false)`（L1431）；status argv 15 项且排除 pathspec 独立最后（L659-664）；Gate 原值与标签未变（L188-202）。

---

## 四、Findings

### P2-1（阻塞）R3-CX-01 明令要求的判别力 selftest 未实质交付

- 位置：`tools/p02/h1-raw-pre-run-selftest.ps1` **L217-219**（`r401-probe-distinguishes-absence-from-error` = 纯 `Contains` 字符串断言）与 **L605-619**（只调用 `New-PathProbeAbsentValue`/`New-PathProbeErrorValue` 两个工厂；L616-617 为**内联复制**的 check 结果映射，未调用 collector 的 L1458/L1542 逻辑；L606 的 `$missingPath` 从未被探测）。
- 触发条件：任何人把 collector L1016-1019 的分类**反转**（错误 → absent shape）或在 L1458/L1542 取消 `NOT_VERIFIED` 映射 —— 全部 r401 断言仍 PASS，selftest 无法发现。
- 后果：adjudication 对 R3-CX-01 的验收条件（"Add a meaningful selftest distinguishing genuine absence from a non-absence attribute error"）未完成；证据面只覆盖"形状与字面量存在"，不覆盖"判别行为"。代码本身正确（见 §二），因此这是**验收条件未闭合**，非运行时缺陷。
- 最小修复：抽取纯函数（分类 + 结果映射）供 collector 调用并由 selftest 直接驱动三例（真缺失 / 强制非缺失错误 / 真实存在），断言 `absent`、`attributeError`、check 结果；并修正 Handoff L34 的"完整覆盖"表述。

### P3-1 R3-CX-04 明令禁止的"探测系统路径"发生在 selftest 中

- 位置：selftest **L641-654**（对三个系统可执行文件与 root Task 文档做实时 `[IO.File]::Exists` 与 `Test-PathAncestorsOrdinary`）；执行事实见 Codex R4 log L199-202。
- 触发条件：任何一次 selftest 运行。
- 后果：违反 adjudication L29 "do not probe or modify system paths to test this"；只读、无状态改写；同时使断言数随机器变化（L649 的 `if` 在路径缺失时静默跳过整条断言，覆盖率不确定）。
- 最小修复：删除该系统路径探测块，改为(a) 对 `$chainPaths` 的**源码断言**（含 launcher 与 snapshot 路径条目），或(b) 在授权 temp fixture 内造等价路径验证。与 P2-1 同一补丁即可。

### P3-2 CX-04 "before use" 缺硬停：chain FAIL 后仍会执行启动器

- 位置：collector L1253-1290（`path-chain-fixed-paths` 为 FAIL check，L1285-1289）先于 L1293 读取 H1 snapshot、L1382 启动 `git.exe`、L1416 启动 `whoami.exe`；最终 L1763-1766 才以 exit 4 结束。
- 触发条件：`C:/Program Files/Git/cmd/git.exe`（或 whoami/pwsh）为 reparse point。
- 后果：可疑二进制在被阻断前已被执行（含后续 12 个 git 子进程）；风险窗口窄（需对 Program Files/System32 具备写权限，且 run 最终 exit 4、证据不可用）。
- 最小修复：把 launcher/快照判定改为用前 `Require`（如 `Require $fixedChainsOk '…'` 紧随 L1290，或对每个 launcher 在首次使用前单独断言），使 FAIL 立即 throw → exit 5。

### P3-3 `r403` 排除路径测试是自证式（未驱动 collector 代码）

- 位置：selftest **L633-639**：body 内重新实现 `Test-PathUnderExclusion` + throw，未调用 `tools-pwsh` 的 getter。真实覆盖只来自 L224-225 的 `Select-String` 源码断言（该断言有价值，但同样只证明"存在"不证明"先于 File.Exists"）。
- 最小修复：与 P2-1 同一重构后，直接以 `runtimePwshExe` 为 under-exclusion 输入调用抽取出的守卫/分类函数并断言抛出（或断言 `GetterInput` 守卫先于 body 执行）。

### P3-4 代码文件 byte 数与 SHA-256 的证据自相矛盾

- 位置：R4 Handoff **L23** `107386 / 3824ad50…`、**L24** `58641 / aa68881f…` vs `review-input-manifest-r4.json` **L13** `"bytes": 107299, "sha256": "3824ad50…"`、**L21** `"bytes": 57555, "sha256": "aa68881f…"`。
- 后果：同一 SHA-256 对应两组不同 byte 数，至少一方错误；我无法在本会话复算（git/shell 被沙箱阻断），因此**代码文件与 `b2cea30d` 的字节级同一性仍未被任何一方以自洽数字固定**。这直接影响随后写入 Task Canonical Evidence 的 pin 质量。
- 最小修复：由具备 Git 的一方在固定 head 上复算 `git cat-file -s` 与 sha256，统一 manifest、Handoff 与 Task Canonical Evidence 的数字，并保留旧值于历史记录。

### P3-5 记录保真度小项（非阻塞）

- `New-PathProbeErrorValue`（collector L379-397）只记 type+message，未记 `HResult`，与 `Add-ObservationException`（L700-705）不一致；
- probe reparse 分支的 `catch { }`（L1048）在 `LinkTarget` 取值失败时静默留 `$null`，无 `linkTargetError` 字段；
- selftest L221 的 `r402` 负例正则 `if\s*\(\$isReparse\)[^}]+Length` 不能跨越 `}`，只对"紧跟同级块"的写法有效，建议改为对 reparse 分支做括号感知的提取断言。

---

## 五、未运行范围（明确）

- 未运行：任何 shell/git/hash 命令（沙箱在启动阶段拒绝，仅 1 次尝试、无绕过，故 **git blob/文件 SHA-256 未经我复算**）、live collector、任何 getter、子进程、注册表/WER/ACL/profile、executor、Build/Cargo、AC1–AC7、Windows Sandbox。
- 仅作为**执行事实**采信（未替代源码审查）：Codex R4 run record（`parseExit 0`、`selftestExit 0`、`sourceBefore==sourceAfter==3824AD50…/AA68881F…`、`gitBlob==worktreeBlob`）与其 R4 log（`assertsPassed 174 / assertsFailed 0 / skipped 6`、L61-66 与 L192-202 的 r401–r404 断言）；Owner R4 日志与 Handoff 声称同值。
- 未复核：R4 Handoff/Task 副本中除代码身份与逐项声明外的文字；历史 R1–R3 日志原文；`dsh-source-review-r3.md` 全文（仅读前 60 行用于确认 CX 编号）；R3 旧代码版本内容（无法 checkout）。
- 不改变任何状态：H2-RUN 仍 proposed、live collector 未释放；v2 P2-1 仍 OPEN、Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`；本 R4 head 不得作为 X6 S0。

---

## 六、结论与推荐下一步

四项 R3-CX 的 **collector 代码**全部真实修复且 fail-closed，R2-01/02/03/04 与 P4 保持闭合、未见回归、未见新绕过；但 **R3-CX-01 要求的判别力 selftest 未实质交付**（P2-1），另有 CX-04 的测试约束偏差、用前硬停缺失、byte/hash 证据矛盾等 P3 项，故本轮为 `CHANGES_REQUESTED`——修复面很窄，全部落在 selftest 与证据数字，**collector 主逻辑无需改动**。

**推荐下一步（可直接转发）**：

> 对 `agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3`（R4 code head `b2cea30d05fd66b731bf8caf18358912eb66ebe6`）在同一 allowlist 内做 R5 收尾补丁：
> (1) **P2**：`h1-raw-pre-run-selftest.ps1:217-219,605-619` 的 `r401` 不是判别力测试（字符串 `Contains` + 工厂 shape + 内联复制映射）。请把 `h1-raw-pre-run.ps1:1012-1021` 的分类与 `:1458/:1542` 的结果映射抽成纯函数，由主序列调用，并让 selftest 直接以"真缺失 / 强制非缺失错误 / 真实存在"三例驱动，断言 `absent`、`attributeError` 与 check 结果；同时修正 Handoff L34 的"完整覆盖"表述。
> (2) **P3**：删除 selftest `:641-654` 对系统可执行文件与 root Task 文档的实时探测（adjudication 明令 "do not probe or modify system paths to test this"），改为源码断言或授权 temp fixture。
> (3) **P3**：把 `h1-raw-pre-run.ps1:1253-1290` 的 launcher/H1-snapshot 链判定改为首次使用前的硬停（`Require`），避免 `:1382/:1416` 执行后才以 exit 4 结束。
> (4) **P3**：由 Codex 复算并统一 `git cat-file -s`/SHA-256，消除 Handoff L23-24 与 manifest L13/L21 的 byte 数矛盾，再写入 Canonical Evidence。
> 完成后固定新 delivery head、更新 Handoff/Task 与 Parser/pure selftest 证据，交 DSH 非作者 exact-head 复审；**不得**运行 live collector/registry/ACL/profile。
