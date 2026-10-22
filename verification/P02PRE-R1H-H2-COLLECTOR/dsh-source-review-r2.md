---
task_id: P02PRE-R1H-H2-COLLECTOR
reviewer: DeepSeek Harness
author: ZCode
base_commit: 343895fb5f0329c0c07a7104ec321b698f967607
reviewed_head: 72145184b7664f8dcc660db5329fa217320b2be4
decision: changes_requested
---

# DeepSeek Harness R2 focused source review
# P02PRE-R1H-H2-COLLECTOR R2 非作者 focused 复审

- Reviewer：DeepSeek Harness（非作者；只读静态）
- code head：`72145184b7664f8dcc660db5329fa217320b2be4`（`h1-raw-pre-run.ps1` 88345B / `f297f62c…`；`h1-raw-pre-run-selftest.ps1` 38852B / `10f9135d…`）
- doc head：`4a90d820a5d58a54cbc190665fbd87d563bc19af`（root `doc/tasks/P02PRE-R1H-H2-COLLECTOR.md` 16292B / `65a7ce78…`）；base `343895fb`
- 复审判据：`dsh-source-review-r1.md`（R1）＋`source-review-r1-adjudication.md`（Codex 裁决，含 CX-01/02/03）
- **Verdict：`CHANGES_REQUESTED`**（R2-01 P1、R2-02 P2、R2-03 P2 未闭合；拒绝条件为“P0/P1/P2 未解决不批准”）

---

## 一、R1 / CX findings 逐项 closure

| Finding | 级别 | 判定 | 判别依据（R2 行号） |
|---|---|---|---|
| H2-01 A6 冻结状态 `?? ` 与 porcelain v2 argv 矛盾 | P1 | **CLOSED** | `Get-FrozenA6StatusRecords` L346-358 返回 `'? <path>'`；L1331/L1336/L1340 使用并写明 v2 语义；selftest L354-371 断言前缀/条数/路径集合/载荷。我独立复算载荷：`3×2(前缀)+211(三路径)+3(NUL)=220` ✓，与裁决“真实 A6=220B/3 records”一致。历史 223B/`?? ` 仅登记为 AI-01（L165、L1340），未改写旧证据 ✓ |
| H2-02 TEMP==TMP 重复 call/check ID | P2 | **CLOSED** | `New-PathProbePlan` L389-415：`/`→`\` 归一 + `HashSet(OrdinalIgnoreCase)` 去重，折叠项记入 `foldedDuplicates`；`$usedIds` 再兜底唯一 id。主流程 L1233-1257 新增 `path-probe-plan-unique-ids` 判别 check；selftest L377-399 覆盖 TEMP/TMP、大小写变体、清洗后 id 冲突加后缀 ✓ |
| H2-03 PostProcess 异常覆盖 OS exit | P3 | **CLOSED** | `Invoke-ProtectedPostProcess` L417-435 独立捕获并置 `state=POST_PROCESS_ERROR` + `postProcessException`；helper catch（L771-780）**不再** `$obs.exit = $null`；L788 `Require state -eq 'OK'` → 该状态 fail-closed。selftest L405-420 正/负例均有 ✓ |
| H2-04 指针仅前缀校验 | P3 | **CLOSED** | `Add-Check` L626-630 用 `Resolve-JsonPointer` 对当时 `$script:Observations` 实际解析，dangling 即 throw。我逐处核对 R2 全部 `Add-Check` 调用点的 pointer 均指向已 `Save` 的 observation（含 L992/L1019/L1050/L1245/L1442/L1456 等），未引入新的 dangling 风险 ✓ |
| H2-05 H1 Task 硬 pin | P3（PARTIAL） | **CLOSED（按裁决口径）** | 改为 `source-snapshot-h1-task` 只记读取时 snapshot（L1056-1062，Expected 明示 “NOT a runtime pin”）；v2 四 pin 在 meta 标注来源引用（L953-955）✓ 与“禁止把 mutable Task 伪装 immutable 输入”一致 |
| H2-06 protected/index/source before-after；refs top/common-dir 真比较 | P3（须修） | **PARTIAL** | protected before L1065 + after L1449 ✓；source pins before L1093-1105 + after L1437-1446 ✓；index before L1077-1090 ✓、after L1343-1358 **但时序见 R2-04**；refs toplevel/commonDir 已真比较（L1263-1269、L1281-1286），frozen 值 `.git` / `G:/CODEX/New Manga/.git` 与 R1 已核对的 v2 记录一致 ✓ |
| H2-07 nits | P3 | **CLOSED** | `$rootRecords` 已删；`Test-RunIdFormat` 已删、param `ValidatePattern` 保留（L51-55、selftest L310-316）；未新增备用写通道（符合裁决 L13） ✓ |
| CX-01 absent path/WER 缺失 shape | P2 | **CLOSED** | `New-PathProbeAbsentValue` L360-375 与 present 分支 L828-848 字段集一致（含 `path/attributes/reparsePoint/length/probeOnlyNote`）；`Get-PathProbeObservation` L824-827 走完整 shape；WER 缺失 L377-387 + L1182-1185 ✓；selftest L426-440 复现“摘要不再抛” ✓ |
| CX-02 base64 超限可省略仍 PASS | P2 | **CLOSED** | `ConvertTo-RawBytesRecord` L270-314 已无 limit/omit 分支，`base64` 无条件完整；selftest L228-230 断言连 `base64Omitted` 字段都不存在 ✓（残留内存影响见 §四） |
| CX-03 ancestor/reparse/排除/卷 | 必需 | **PARTIAL** | 已做：首次 CreateNew 前的 Require 前置检查 L905-916（排除/链/真实 DriveInfo-NTFS/输出目录 leaf reparse/目标 absent）、固定路径链 L1024-1053、7 target 真实卷+父目录非 reparse L1370-1373、排除 scope check L970-997。**未闭合**：leaf 分量从未分类（→R2-02）、排除守卫只驱动静态清单、动态派生路径未守卫且未记录（→R2-03）|

**无回归（R1 已核项）**：status argv 仍 15 项且排除 pathspec 独立最后（L499-504，selftest L322-331）；唯一写通道仍为 `CreateNew/FileShare.None`（L593-597，无其他写 API）；Gate 原值、`NEW_TIME_EVIDENCE`/`CANNOT_SUBSTITUTE_V2_TIME_EVIDENCE`、historyNote、notRun 块字面未变；NUL 保真/空字节非缺失不变；frozen pins/refs/index/SDDL/7 targets 未变（新增的 toplevel/commonDir 期望值与 v2 记录一致）。禁止面未见新增调用（本会话读取的头部/常量/驱动/主序列区段内无 Add-Type/P-Invoke/Start-Process/Invoke-Expression/AppContainer/Toolhelp/ACL 写；注册表仍仅 `OpenSubKey(..., $false)`）。

---

## 二、新增反例的独立评估（findings）

### R2-01（P1，阻塞，R2 新引入回归）`output-path-chain-volume` **必然 FAIL → 任何 live run 都 exit 4**

**触发链（确定性，与机器/环境无关）**：
1. L918 `$script:Stream = Open-ExclusiveCreateNew -Path $outputFile` —— 此刻 `run-<RunId>.json` 已被创建；
2. L1000-1011 `output-path-chain-volume` getter 在 **L918 之后**执行，其中 L1008 `targetAbsent = (-not (Test-Path -LiteralPath $src.outputFile))`；
3. 文件已存在 → `targetAbsent = $false` → L1012-1016 `$outputSafetyOk` 为假 → L1017-1021 check = `FAIL`；
4. L632 把 `CHECK_FAIL:output-path-chain-volume` 加入 `BlockedReasons` → L1462-1465 → `BLOCKED_BY_FAILED_CHECKS` / exit 4。

**受控 fixture 证据**：`r2/additional-regressions.json` stdout `post_create_targetAbsent:false`、`exclusive_target_exists:true`（Codex 用 AST 抽取 L1008 表达式并在 CreateNew 后求值）；root Task L109 亦登记同一结论。**我独立按源码复算成立**：文件在 L918 创建、全程无删除，`Test-Path` 必为真。

**影响**：这是本交付唯一目的（一次授权运行成功采集）的确定性阻断；且失败证据会以 “output path chain/volume” 形式呈现，误导为非预期漂移。同时 Handoff L43 “output 链/卷/排除检查全部先于首次 CreateNew” 与 L1022 Note “preflight Required the same conditions before the stream opened” 对该项不成立（Require 前置确实在 L905-916，但**证据** getter 在 L1000）。

**最小修复（根因一次）**：把 L1000 的 getter 整体移到 L918 之前（链/卷/排除/absent 四项本就应“首次 CreateNew 前”取证），或把 `targetAbsent` 从 post-open 证据中拆出——post-open 只记链/卷/排除并显式记 `targetExistsNow=$true` 作为期望态。二者都能让 `outputSafetyOk` 恢复可达真值，并使 check 文本与真实时序一致。

### R2-02（P2，CX-03 未闭合）`Test-PathAncestorsOrdinary` 只分类祖先，**leaf 分量的 reparse 永不检测**

**代码事实**：L469-486 的循环首步即 `$parent = Split-Path -Parent $current`，**从未分类传入路径自身**；`allOrdinary`（L490）只由 `reparseComponents/missingComponents/nonDirectoryComponents` 与 `checkedAncestors>0` 决定。受控 fixture（junction 作为 leaf，`-Path $link`）得 `leaf_reparse:true` 且 `ancestor_allOrdinary:true` —— 与代码一致，非 fixture 假象。

**受影响点**：
- L1030-1052 `path-chain-fixed-paths` 的 `Expected` 声称覆盖 RootRepo/CandidateRepo/A6/protected/pins/7 targets 的 ordinary 链，但**这些路径自身的 leaf 不参与分类**：protected selfcheck 若是 symlink/junction，pin 会透过链接读取，`protected-before-pin`（L1066-1068）只比 size/sha/SDDL，**不要求 `reparsePoint=false`**（该字段 L876 已采集却无人消费），链检查照样 PASS。
- L1365-1371 的 7 个 target 用 `[IO.Directory]::Exists`/`[IO.File]::Exists` 判 absent（两者会解引用），**悬挂链接**与“什么都没有”不可区分（`reparsePoint` 亦为 `$null`）。
- 输出目录 leaf 有独立兜底（L912-913）✓，故缺口集中在固定输入路径与 target leaf。
- Handoff L75 自述“selftest 无法构造真实 reparse 负例，reparse 检测逻辑由静态 Review 把关”——Codex 本次 fixture 正是补上了这一负例。

**最小修复**：让 `Test-PathAncestorsOrdinary` 把传入路径自身也纳入分类（或新增 `leaf` 分类字段），并对 protected 文件与 7 个 target/parent 的 leaf 施加 `reparsePoint -eq $false` 的 fail-closed 条件；target 的 absence 判定改为不解引用检测（如 `FileSystemInfo.LinkTarget`/原始 `GetFileAttributes` 属性）并把结论记进同一 observation。

### R2-03（P2，契约第 5 条“不得读取排除路径”＋CX-03 未闭合）排除守卫只驱动**静态清单**，动态派生路径未被守卫也未被记录

**代码事实**：
- `$fixedPaths`（L970-975）是静态常量清单（output/root/candidate/A6/protected/packages/tools/pins/7 targets/`ScratchCacheProbePaths`）；**不含** `$script:RootIndexPath`（L160）、H1 snapshot 字面路径（L1056）、TEMP/TMP 运行值、`$parentDir`（L1366）。
- 真正会出现运行时派生路径并发生 **FS 访问** 的是：L1233-1236 从环境变量取 `TEMP`/`TMP` → L1249-1250 `Get-PathProbeObservation`（`Directory.Exists/File.Exists` + attributes 真实访问），**全程无 `Test-PathUnderExclusion`**；L1366-1367 `$parentDir` 亦无。若运行环境把 `TEMP` 指向排除子树，即违反契约第 5 条与 R1 的“全域排除访问”要求。
- 守卫自身证据不足：L976-990 的 `-GetterInput` 只传 `exclusionSegment/pathCount`（L978），Body 靠闭包读外层 `$fixedPaths`（L982），输出只记 positives（L985-989）→ **closed JSON 无法证明“到底检查了哪些路径”**（契约第 6/7 条“每项 raw pointer / raw output”）。
- 受控 fixture（root Task L109：`excluded_driver_entered:true`、stub 仅字符串、无实际排除路径访问）证明 `Test-PathUnderExclusion` **函数本身**正确（selftest L446-451 亦覆盖嵌套/大小写/近邻），缺口在“驱动对象与记录”。

**最小修复**：把完整路径清单放进 `-GetterInput` 并把每个 `{path, underExclusion}` 记入 observation；对所有将发生 FS 访问的派生路径（TEMP/TMP plan 项、`$parentDir`、target 绝对路径、`RootIndexPath`、H1 snapshot 路径）在访问前统一过排除检查并纳入 `$fixedPaths`/或单设“派生路径全域排除”门。

### R2-04（P3，claim/时序不实）index “after” 采样不在“whole collection”之后

L1342-1358 在 L1343 读取 index after，但 **7 个 `git check-ignore` 子进程在 L1368** 之后才运行（还有 L1384 的文件读取），故 L1354 的 `Expected` “before/after the whole collection” 与 R2 冻结修订 L57 的“关闭前复读”均不成立。实际风险低（`check-ignore --no-index --quiet` 不触索引，且 `GIT_OPTIONAL_LOCKS=0`），但证据表述必须与实际时序一致：把 after 采样移到 `# ---- close ----`（L1461）之前，或收窄 check 文本。

### 其余 nit（P4，不单独阻断）

- L461/L488 `nonDirectoryComponents` **从未被写入**（祖先为文件时被归入 `missingComponents`，因为 `[IO.Directory]::Exists` 为假）：`allOrdinary` 仍 fail-closed，但 L1018/L1049 的 `Expected` 宣称的“non-directory component”判别实际未实现，属证据精度问题。
- L1243-1248 `path-probe-plan-unique-ids` 的 pointer 指向 `temp-tmp-env` observation，plan 本身不是 observation；结论数据仅在 summary/Note（各 entry 的 id/path 由随后 per-entry probe observation 承载，影响有限）。
- CX-02 采纳“完整保存、无上限”后，超大 stdout 会被整段 base64 进 closed 行（内存/体积）；这是裁决允许的选择，异常仍 fail-closed，仅作残留登记。

---

## 三、验证方式与限制

- 本会话 **未运行** 任何 shell/git/hash/live collector/getter/executor/Build/AC/Sandbox，**未修改任何文件**；结论全部来自只读阅读源码与 Codex 已固定的证据文件。
- 已读：collector 全文（分 4 段，L1-1491）、selftest L200-529、root Task（含 R2 冻结修订 L57 与 R2 记录 L109）、R2 Handoff、`source-review-r1-adjudication.md`、`r2/verification.json`、`r2/additional-regressions.json`；R1 的 frozen-input/WER/executor literal 交叉核对沿用同 session R1 结论（未改内容不重复读取）。
- **未覆盖（明确）**：selftest L1-199（AST 禁止项/parser 段与 126 断言全文）、R2 的 parser/selftest 原始日志（`r2/parser.*.log`、`r2/selftest.*.log` 未在本次 8 文件输入内；仅以 Codex 独立复跑的 Parser 0 / 126 PASS 6 SKIP 与 `verification.json` 摘要采信）；未复算任何 hash（按指令免复算）；为定位 `additional-regressions.json` 与 exact-head pins，本会话还读过 Codex 自身 workspace 的 `r2/review-r2-pins.json` 与目录清单，未读其他仓库历史。
- **纯 126 PASS ≠ live 预运行通过**：R2-01（CreateNew 后取 absent 证据）恰恰是纯测试与 AST 断言无法覆盖的时序缺陷，正是 Codex 受控 fixture 才暴露；R2-01 未修前，任何 live run 都会以 exit 4 结束。

---

## 四、结论与下一步

| 项 | 级别 | 状态 |
|---|---|---|
| R2-01 post-CreateNew `targetAbsent` → `output-path-chain-volume` 必败 | P1 | OPEN（阻塞） |
| R2-02 leaf 分量 reparse 未分类（CX-03 未闭合） | P2 | OPEN（阻塞） |
| R2-03 排除守卫仅静态清单 + 动态路径无守卫/无记录（契约 5、CX-03） | P2 | OPEN（阻塞） |
| R2-04 index after 采样时序与 claim 不符 | P3 | OPEN |
| H2-01/02/03/04/05/07、CX-01、CX-02 | — | CLOSED |
| H2-06 / CX-03 | — | PARTIAL（见 R2-02/03/04） |

历史 v2 P2-1/PRE_RUN_PASS、Gate 原值（Technical `NOT_SATISFIED`、`private_registry_absence UNPROVABLE`、BuildGate `BLOCKED`、HardBuildBarrier `EFFECTIVE`、BuildCargo `NOT_RUN`、AC1–AC7 `BLOCKED / NOT_RUN`）与 Owner waiver 均不变；本 Task 产物仍不得作为 X6 S0，live-run、X6、Build、AC 仍 `BLOCKED / NOT_RUN`。

**推荐下一步**：ZCode 在同一 allowlist/同一 worktree 从 `72145184` 续修 R2-01（必须）+ R2-02/R2-03（P2）+ R2-04，固定新 code head 后由 DeepSeek Harness 做 exact-head focused 复审，再由 Codex pin/adjudicate（AI-01 仍只登记不改写）。

可直接转发给 ZCode 的指令：

> 对 `agent/zcode/P02PRE-R1H-H2-COLLECTOR`（当前 R2 head `72145184b7664f8dcc660db5329fa217320b2be4`）在同一 allowlist 内返修：
> (1) **P1**：`h1-raw-pre-run.ps1:1000-1011` 的 `output-path-chain-volume` getter 在 `:918` CreateNew 之后运行，`:1008 targetAbsent` 必为 false，导致 `:1017` 该 check 恒 FAIL、`:1462` 恒 exit 4。请把该证据 getter 整体移到 `:918` 之前（链/卷/排除/absent 四项本就应在首次 CreateNew 前取证），或把 `targetAbsent` 拆出、post-open 只记链/卷/排除并显式以 `targetExistsNow=$true` 为期望态；同时让 check 文本与实际时序一致。
> (2) **P2**：`Test-PathAncestorsOrdinary`（`:451-492`）只分类祖先，leaf 不参与，受控 fixture 已证 leaf junction 得 `allOrdinary=true`。请把传入路径自身纳入分类（或新增 leaf 字段），并对 protected selfcheck 与 7 个 target/parent 的 leaf 加 `reparsePoint -eq $false` 的 fail-closed 条件（protected 的 `reparsePoint` 已在 `:876` 采集但无人消费）；target 的 absence 判定改为不解引用检测，避免悬挂链接被当成 absent。
> (3) **P2**：排除守卫 `:970-991` 只覆盖静态 `$fixedPaths`，而 `:1233-1236 → :1249-1250` 的 `TEMP/TMP`（运行时值）与 `:1366-1367` 的 `$parentDir` 等派生路径会真实访问 FS 却无 `Test-PathUnderExclusion`；且该 getter 的 `-GetterInput` 未含路径清单（`:978`）、Body 闭包读外层变量（`:982`），closed JSON 无法证明检查了哪些路径。请把清单放入 `-GetterInput` 并逐项记录 `{path, underExclusion}`，对所有将发生 FS 访问的派生路径在访问前统一过排除检查。
> (4) **P3**：`root-index-hash-after`（`:1343`）在 7 个 `check-ignore` 子进程（`:1368`）之前采样，与 `:1354` “before/after the whole collection”及 R2 冻结修订“关闭前复读”不符，请移到 close 前或收窄表述。
> 完成后固定新 delivery head、更新 Handoff/Task 证据（含复跑 Parser 与纯回归日志、环境、exit），交 DeepSeek Harness 非作者 exact-head 复审；**不得运行 live collector/registry/ACL/profile**。

若 Codex adjudication 认定 R2-02/R2-03 属可选加固而仅接受 R2-01 为阻塞，则本轮结论改记 “CHANGES_REQUESTED（仅 R2-01 P1）”，其余降为非阻断登记。
