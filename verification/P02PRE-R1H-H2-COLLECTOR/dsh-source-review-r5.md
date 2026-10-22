# P02PRE-R1H-H2-COLLECTOR — R5 exact-head 非作者静态复审

**Verdict：`APPROVED_STATIC_CONTENT`**

> 独立重读：本会话**重新完整读取** R5 worktree 的两份脚本（collector 1831 行、selftest 760 行），逐行判定，未沿用 R4 verdict。只读；未运行任何 PowerShell/git/collector/getter/子进程/selftest/registry/ACL/profile/executor/Build/AC/Sandbox；未访问 `.tmp.driveupload` 子树（仅对虚构路径做纯字符串判定）；未写入或修改任何文件。

---

## 一、Reviewed identity（精确 code/doc identity）

| 项 | 值 | 验证 |
|---|---|---|
| reviewed code commit | `b4936c35067680fb7309c37405a4afed2b6c0c44` | ✅ reflog：父 `90b9972f`（R4 docs head），消息 `commit: fix(P02): close R4 findings (P2-1, P3-1..03, P3-5) for H2 collector R5 per source-review-r4-adjudication` |
| docs head / worktree HEAD | `6a59d82c6de3a525e3c1ebd49b5879cc1318e6cc` | ✅ reflog 链：`b4936c35 → d8b57590（docs R5）→ 6a59d82c（clarify R5 worktree byte hash semantics）` |
| 前序 code commit | `b2cea30d…`（R4） | ✅ |

- **Git/PowerShell 被沙箱拒绝（诚实声明）**：本会话 `pwsh` 在启动阶段即被拒绝（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`）；**仅一次尝试、未做任何绕过**，因此**未由我复算** git blob/SHA-256。
- **身份交叉印证（非我复算，但可交叉核对）**：Codex R5 run record `reviewHead=d8b57590` 记录 `commitBlob == worktreeBlob`（collector `42c1bb21…` / selftest `3b056864…`）且 `worktreeBytes 108765/60719`；Codex 独立 selftest 日志 `collectorSha256=82B235818A07…`（对磁盘文件的 `Get-FileHash`）与 manifest 的 worktree `sha256`、R5 Handoff 表一致。结合 reflog（b4936c35 之后仅两条 docs commit），可判定：**当前 worktree 的两份代码文件即 b4936c35 交付内容**。
- manifest 14 项输入中，代码/日志 pin 自洽；唯一不一致见 **P3-2**（Handoff 文件自身的 pin）。

---

## 二、逐项结论（对应指令 1–8）

### 1. R4 P2-1（PASS）
- `Get-PathProbeValueFromAttributes`（collector **L404-437**，纯分类）**由生产 `Get-PathProbeObservation` 调用**：**L1070**（`$attr=$null`/`$attrEx=$_.Exception` 后统一交给该函数）。生产不再内联判别。
- `Get-ProbeCheckResult`（**L439-447**）**由实际 check 调用点调用**：**L1497**（`profile-moniker-packages-probe`）、**L1581**（probe plan 逐项）。
- non-absence `UnauthorizedAccessException`/I/O error 始终得 error shape：L412-418 → 非 NotFound 分支 `New-PathProbeErrorValue`（L381-402：`exists=$false, absent=$false, attributeError` 显式、`hresult` 保留）→ 评定 `NOT_VERIFIED`（L443-445），绝非 PASS。文件不存在（`FileNotFoundException`/`DirectoryNotFoundException`）才 `absent=$true`、`attributeError=$null` → PASS。
- **false absence/error 不能进入最终 gate**：门控类 check 不用该映射，而是与严格链分类 `-and`（L1685-1691，`$targetChain.leafAbsent` 在 L616-626 独立判别）→ 错误必 FAIL。
- selftest **直接驱动共享函数**：L626-654 覆盖 (a) FNF/DNF → absent shape + PASS、(b) UnauthorizedAccess/IOException → error shape（含 `hresult`）+ `NOT_VERIFIED`、(c) `Normal` attributes → present shape + PASS；**反转负例** L656-660：即使 `absent=$true`，只要 `attributeError` 存在就必须 `NOT_VERIFIED`（可捕获映射反转）；L627/L639 也能捕获分类反转。→ **PASS**

### 2. R4 P3-1（PASS）
- R4 中对 Git/Whoami/PowerShell 安装路径与 root Task 文件的实时探测块已**删除**；全文件再无 `[IO.File]::Exists`/`Test-PathAncestorsOrdinary` 作用于系统路径（grep 复核：命中仅 collector 源码读取 L107/L188/L211/L742、`Z:\definitely-missing-…` 异常源 L368、以及 fixture）。
- 改为 source/AST 静态断言：**L237-238** 断言 `$chainPaths` 含三个 launcher 与 H1 snapshot/运行时 pwsh；**L241-247** 断言硬停行号早于 snapshot 与 launcher。→ **PASS**

### 3. R4 P3-2（PASS）
- **L1330-1331**：`path-chain-fixed-paths` observation（L1291-1321）+ check（L1323-1328）之后**立即** `Require $fixedChainsOk`；其位置严格早于 H1 Task snapshot 读取（**L1334**）、protected/index/pins 读取、`tools-pwsh` 运行时路径探测（L1408）、`git --version`（**L1421**）、`whoami /all`（**L1455**）及后续全部 git 子进程。
- 失败时证据不丢：`Add-Check` 已把 `CHECK_FAIL:path-chain-fixed-paths` 记入 blockedReasons（L856），随后 catch 写 closed 行（L1821-1822），非零退出。
- static assertion 有判别力：`r504-fixed-chain-require-halts-before-snapshot-or-launchers`（selftest L241-247）若 `Require` 被移除，`Find-LineNumber` 返回 -1 → 断言失败。→ **PASS**（唯一未断言的是 `tools-pwsh` 探测点，但由行序 L1331 < L1408 客观保证；见 P3-3 备注）

### 4. R4 P3-3（PASS）
- 共用纯字符串守卫 `Assert-RuntimePathNotUnderExclusion`（collector **L556-562**）；生产调用点 **L1401**（`tools-pwsh` body 内，先于 L1408 的 `[IO.File]::Exists`）。
- selftest 直接调用**同一函数**（L674-686）：虚构路径 `G:/CODEX/New Manga/.tmp.driveupload/fake/pwsh.exe` → 抛异常（L675-677）；干净伪路径 → 不抛（L679-686）。全程无 filesystem API 触及该子树。
- `GetterInput` 早于 body 的验证保留：collector L913-915，selftest L197-200 断言；另 L231-234 断言 guard 行号早于 `File.Exists` 行。→ **PASS**

### 5. R4 P3-4（PASS，另见 P3-2 的文档 pin 问题）
- R5 manifest **明确分列四个量**：`bytes`（worktree 磁盘字节）、`sha256`（worktree 内容）、`gitBlob`（Git blob ID）、`gitBlobBytes`（LF 规范化大小）：collector 108765 / `82b23581…` / `42c1bb21…` / 106934；selftest 60719 / `4e6d07d2…` / `3b056864…` / 59959。
- R5 Handoff **L21-24** 用同一 4 列呈现相同数值，并在 **L38** 明确纠正 R4 的 107,386/58,641 → 107,299/57,555（worktree）与 105,507/56,827（LF blob），不改写历史。
- **我可独立复算的部分（无需 Git）**：R5 collector 1831 行、selftest 760 行（读取工具报告的行数），而 `108765−106934=1831`、`60719−59959=760`；R4 的 1792/728 行亦满足 `107299−105507=1792`、`57555−56827=728`。即 CRLF worktree 字节数 = LF blob 字节数 + 行数，**两组数字各自自洽且未混淆**。→ **PASS**

### 6. R4 P3-5（PASS）
- `HResult`：`New-PathProbeErrorValue`（**L386、L399**，`'0x{0:X8}' -f …`）✓；selftest L641 断言非空。
- `LinkTarget` 读取异常字段：字段 L374/L397/L432；记录点 **L1083-1085**（`linkTargetError`）。Handoff L39 的声明与该实现范围一致（仅主张 probe 路径，未越界宣称链 helper）。
- reparse 分支 AST 提取强化：selftest **L223-229** 用 `IfStatementAst` 取条件含 `reparsePoint` 的 `Clauses[0].Item2` 正文，断言不含 `\bLength\b`（collector L1072-1085 确实无 `Length`；`Length` 只在 L1086-1093 的非 reparse 分支）。→ **PASS**

### 7. 既有 closures 无回归（PASS）
| 项 | R5 证据 | 判定 |
|---|---|---|
| R2-01 CreateNew 前后 + pointer + 冲突 | L1156-1167 纯字符串/preflight Require → L1169 CreateNew → L1171 post facts → L1276-1281 check（pointer `…/output/value`）；冲突：L1167 `Require targetAbsent`（exit 2）或 L821 `FileMode.CreateNew` 抛（exit 5） | ✅ |
| R2-02 leaf/祖先 reparse、dangling absence、nonDirectory | L564-661（lstat leaf L595-613；真缺失 vs 查询错误 L614-626；祖先 reparse L639-644；nonDirectory L645-646 且被 L656-660/L1317-1318 消费）；target absence L1685-1691 | ✅ |
| R2-03 全入口纯字符串守卫 | 逐一枚举：L595（守 L572）、L639/645（守 L572）、L677/707（守 L669-670）、L821（守 L818）、L958-959（守 L945）、L1040（守 L1032+L913）、L1066/1077/1080/1089（守 L1052+L1060+L913）、L1111/1114/1118（守 L1101+L913）、L1162（守 L1157+preflight）、L1361（守 L913）、L1408（守 L1401+L913+L1248）、L1426-1427（守 L945+L1248+L1331）、L1708/L1750/L1789（守 L913） | ✅ |
| R2-03 动态 TEMP/TMP manifest | L1506-1520 取值 → L1529-1536 plan（入口守卫）→ L1556-1570 `{path,underExclusion}` observation（早于 L1578 probe） | ✅ |
| R2-04 index-after 最后 | L1784-1799，晚于最后子进程（L1681）与全部源文件读取（L1768），早于 close L1801 | ✅ |
| P4 plan pointer / nonDirectory 消费 | L1542-1547 pointer 指向含完整 plan 的 observation；L656-660 与 L1317-1318 | ✅ |
| R3-CX-02 reparse 不解引用 | L1072-1093：reparse → 仅 `LinkTarget`（+ `linkTargetError`），非 reparse 文件才读 `Length` | ✅ |
| R3-CX-03 运行时 PSHOME | L1223-1226 纳入 `$fixedPaths` → L1232-1254 manifest + L1248 Require → L1387-1410 显式输入 + L1401 守卫 + L1413 漂移判定 | ✅ |
| status argv / Gate / NUL / 唯一写通道 | L717-722 仍 15 项且排除 pathspec 独立最后；L188-202 Gate 原值；L240-314 NUL 保真；唯一 `CreateNew+FileShare.None`（L821），无 `WriteAll*`/`Remove-Item`/`Set-Content`/`Out-File`/`Add-Type`/`Start-Process`/`Invoke-Expression`/`DllImport`/Toolhelp/AppContainer | ✅ |

### 8. 其他静态问题（见下 P3 findings，无 P0/P1/P2）

---

## 三、Findings（全部 P3，非阻塞）

**P3-1（证据自述陈旧）** collector **L1209** `revisionNote` 与 R4 逐字相同（"R4 repair per source-review-r3-adjudication: R3-CX-01…R3-CX-04"），**未更新为 R5 内容**。后果：任何 R5 run 的 `meta` 行会自称 R4 修复轮，且不提 R5 的行为改动（共享分类/评定函数、L1331 用前硬停、共享运行时守卫）。最小修复：把该字符串改为 R5 描述（含 "R4 P2-1/P3-1..03/P3-5 per source-review-r4-adjudication" 与硬停说明）。

**P3-2（canonical pin 不一致，需 Codex 复算）** Task Canonical Evidence 行 `h2-r5-handoff`（Task **L84**）记 sha256 `bc907f62…`，而 R5 review manifest **L60** 对**同一路径**记 `bee4e019…`（10,193 bytes）。二者不可能同时为当前值；结合最后一条 docs commit 标题 "clarify R5 worktree byte hash semantics"（很可能改写了 Handoff 的字节语义表 L21-24/L38），最可能是 **Task 该行未随最终 docs commit 重新 pin**（代码文件 4 个 pin 全部一致，不受影响）。最小修复：由具备 Git 的一方在冻结 docs head 上复算 Handoff 的 sha256/bytes 并更新该行（或修正 manifest），保留旧值于历史；不重写历史。

**P3-3（fail-closed 分类语义与 Task 自述映射不一致）** 链校验 FAIL 现在经 **L1331** `Require` 抛异常 → catch（L1809-1820）→ disposition `BLOCKED_EXCEPTION_FAIL_CLOSED` / **exit 5**；而 Task L119 记录的实现映射是"任一 FAIL check → `BLOCKED_BY_FAILED_CHECKS`（exit 4）"。后果：运行仍被阻断且 `blockedReasons` 同时含 `CHECK_FAIL:path-chain-fixed-paths` 与 EXCEPTION（证据不丢），但 disposition/exit 分类与 Task 叙述不一致，下游按键值分流的消费者可能误判。最小修复：为该硬停引入专用 disposition/exit（如 `BLOCKED_PATH_CHAIN_FAILED` = 4），或在 Task/Handoff 明确记录该映射变更。

**P3-4（分类函数未定义"两个输入都为 $null"的输出）** `Get-PathProbeValueFromAttributes`（**L404-437**）在 `$Exception -eq $null` 且 `$Attributes -eq $null` 时落入 L420-436，最终 `$Attributes.ToString()`（**L428**）抛错。后果：不会被误报为 missing（getter catch → exit 5，fail-closed），且当前生产调用点（L1063-1069 必设其一）不可达；但作为共享纯函数的契约不完整。最小修复：显式分支返回 `New-PathProbeErrorValue`（message 如 "attributes not observed and no exception supplied"）。

**P3-5（链 helper 的 LinkTarget 异常仍静默）** `Test-PathAncestorsOrdinary` **L606-613** 的 `catch { }` 仍不记录错误，而 probe 侧已有 `linkTargetError`（L1084）。属 R4 adjudication 未要求范围的保真度不对称。最小修复：增加对称的 `leafLinkTargetError` 字段（或在 Handoff/Task 登记为保留限制）。

> 备注（非 finding）：selftest `r504-fixed-chain-require-halts-before-snapshot-or-launchers`（L241-247）未单独断言硬停早于 `tools-pwsh` 的运行时路径探测；该顺序由 L1331 < L1408 客观成立，建议后续补一条行序断言即可。

---

## 四、未运行范围（明确）

- **未运行**：任何 PowerShell/pwsh 脚本、selftest、collector、getter、Git 子进程、registry/WER/ACL/profile/AppContainer 查询、executor、ProcessObserver/Toolhelp、Build/Cargo、AC1–AC7、Windows Sandbox。
- **未执行**：git blob/SHA-256/字节数复算（沙箱拒绝，一次尝试、无绕过）；因此 `gitBlob`/`sha256` 的**数值准确性来自 manifest、R5 Handoff 与 Codex 独立 run record/log 的交叉一致**，加上我做的行数—字节差自洽复算，而非我本地重算。
- **未复核**：R1–R4 历史日志与旧 Handoff 原文；`dsh-source-review-r4.md` 全文（仅用其被 Codex 裁决转述的条目）；Owner R5 Parser/selftest 日志正文（仅采信 Handoff 与 Codex 独立 log 的执行事实：Parser 0 errors、纯 selftest `182 PASS / 0 FAIL / 6 SKIP`、`collectorSha256=82B23581…`）。
- **未访问**：`.tmp.driveupload` 子树（仅虚构路径的纯字符串判定）。
- **不授予**：本文不构成任何 live-run 授权。H2-RUN 仍是独立 `proposed` Task，需 Codex 另行冻结 RunId 与 exact targets；v2 P2-1 仍 OPEN，Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN` 原值不变；本 R5 证据不得用作 X6 S0。

---

## 五、结论与推荐下一步

R4 adjudication 的全部 R5 验收项——**P2-1**（共享分类/评定函数由生产调用 + 三门类行为测试 + 反转负例）、**P3-1**（删除系统路径实时探测、改静态断言）、**P3-2**（链 observation 后立即硬停、早于 snapshot/launcher）、**P3-3**（生产与测试共用纯字符串守卫且不触碰排除子树）、**P3-4**（worktree bytes / worktree SHA-256 / Git blob ID / Git blob bytes 四分列且自洽、R4 数字明确纠正）、**P3-5**（hresult / linkTargetError / reparse 分支结构断言）——均已在 `b4936c35067680fb7309c37405a4afed2b6c0c44` 真实闭合；R2-01..04、P4、R3-CX-02/03 无回归。仅存 5 项 P3（自述文本、文档 pin、硬停 disposition 分类、纯函数边界、链 helper 保真度不对称），不阻塞。

**推荐下一步**：

> (1) **Codex** 对 R5 code head `b4936c35067680fb7309c37405a4afed2b6c0c44` / docs head `6a59d82c6de3a525e3c1ebd49b5879cc1318e6cc` 做 post-review pin 复算与 adjudication，并优先解决 **P3-2**（Task `h2-r5-handoff` 行 `bc907f62…` vs manifest `bee4e019…` 的 Handoff pin 分歧，需在冻结 docs head 上统一）。
> (2) 是否将 P3-1（`revisionNote` 更新为 R5）与 P3-3（链硬停 disposition/exit 语义对齐）纳入同一 allowlist 的收尾补丁，由 Codex 决定；若维持现状，须在 Task/Handoff 明确登记为保留的非阻塞限制。
> (3) 通过后方可另行冻结 H2-RUN 的 RunId 与 exact targets；**本 Review 不代表 live-run 授权**。