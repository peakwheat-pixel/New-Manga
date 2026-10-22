# P02PRE-R1F Review Round 5 follow-up #6 — 独立只读复核

## Decision

`APPROVED`

counts：`P0/P1/P2/P3 = 0 / 0 / 0 / 0`

- 本轮三项核心命题经逐字核验**全部成立**：冻结 script 的两个 protected-key arrays = **83 + 13 = 96 keys / 96 unique / 0 duplicates**；新增 6 项精确为 self-check5 与 follow-up #6 prompt/stdout/stderr/exit/adjudication；本轮 11 个 pin **全部**在 script 中逐字命中（含易混的 #4/#8/#9/#10/#11）。
- follow-up #5 的唯一 F1/P3（childEngine vs PSEdition 措辞）已按“父进程 executable 标签 vs child PSEdition”口径修正，旧 artifact 未被改写；Codex 对 #5 report pin 编号误映射的纠正**有依据**且结论正确（#8=follow-up#4 stderr→L738、#9=follow-up#4 exit→L739、#11=follow-up#3 adjudication→L734）。
- Gate/risk 状态、release order 与计数在 Task/manifest/script/self-check/adjudication 五者间自洽，无 waiver→PASS、无 build/AC 放行措辞。

## 1. 阅读范围与边界

只读 11 个 pin 文件；pin #3（script，913 行）分 L1–400 / L401–700 / L701–913 读毕；pin #4、#10 为单行 JSON（受工具 2000 字符/行截断）；pin #6（99 行）、#7（29 行）、#5（29 行）、#11（23 行）、#1（102 行）、#2（92 行）全量读毕；pin #8（114 行）全量分段读毕；pin #9 为 `0` + 行尾。

**未执行**任何 shell/grep/rg/PowerShell/测试/getter/hash/R8/capture/Build-Cargo/AC1–AC7；未写文件；未访问未 pin 路径或 `.tmp.driveupload`；未改 Gate。**bytes/SHA 一律未复算**（归 Codex pre-run adjudication，pin #1 L42），下文“一致”仅指 pin 间字面交叉一致。

## 2. protected-key membership（核心，逐字清点）

script 中只有两处写 `$Result.protectedHashes`，其后不再新增键：

| 数组 | 字面量范围 | 数量 | 内容 |
|---|---|---|---|
| 数组 1 | L670–L752（`foreach` L669 → `)) {` L753） | **83** | L670–L728 旧 59 + L729–L740 旧 12 + L741–L746 旧 6 + **L747–L752 本轮新增 6** |
| 数组 2 | L757–L769（`foreach` L756 → `)) {` L770） | **13** | R8 + R4/R4-retry/R4-followup 四件套 |
| 合计 | — | **96 / 96 unique / 0 duplicates** | — |

- **新增 6 项精确为**（L747–L752）：`…r5-followupfix5-selfcheck-20261011.json` + `dsh-…review-r5-followup6-20261011.prompt.md/.stdout.md/.stderr.log/.exit` + `…r5-followup6-review-adjudication-20261011.md`。
- **无交集**：`r4-*`、`…r8-…json` 只在数组 2；数组 1 内 `r3`(L704–707)/`r5`(L708–711)、`followup-`(L717–720)/`followup2-`(L724–727)/`followup3-`(L730–733)/`followup4-`(L736–739)/`followup5-`(L742–745)/`followup6-`(L748–751) 文件名逐条互异，无大小写折叠重复（无仅大小写差异者）。
- **旧 77 项行位未漂移**：L678 Task、L683 manifest、L684 script、L712/L721/L728/L729 adjudications、L734 follow-up#3 adjudication、L735 fix3 selfcheck、L736–L740 follow-up#4 五件、L741 fix4 selfcheck、L742–L746 follow-up#5 五件，与 follow-up #5 report §2 记录的行位**完全一致** → 本轮 script delta 就是“在数组 1 末尾追加 6 个字面量”。
- 与文档一致：pin #1 L25/L34/L38/L42、pin #2 L17/L57/L61、pin #5 L25 均为 96/96 unique；pin #2 L61 的链路 72→84(+12)→90(+6)→96(+6) 与「12+6+6=24 条枚举」逐一对应。

## 3. 本轮 11 pins 在 script 中的精确位置（防编号错配）

| pin | 路径要点 | script 行 | 正确性 |
|---|---|---|---|
| #1 | `doc/tasks/P02PRE-R1F.md` | **L678** | 在册（L676/677 为 R0S6/R1，未混同） |
| #2 | `…p02pre-r1f-manifest-20261011.md` | **L683** | 在册（L680 为 R1 manifest，未混同） |
| #3 | `…p02pre-r1f-capture.ps1` | **L684** | 在册（L681 为 R1 capture.ps1，未混同） |
| #4 | `…r5-followupfix5-selfcheck-…json` | **L747** | 在册（≠L741 fix4、≠L735 fix3） |
| #5 | `…r5-followup5-review-adjudication-…md` | **L746** | 在册（≠L740 follow-up4、≠L734 follow-up3） |
| #6 | `…followup5-….stdout.md` | **L743** | 在册（≠L737 follow-up4 stdout） |
| #7 | `…followup5-….prompt.md` | **L742** | 在册 |
| #8 | `…followup5-….stderr.log` | **L744** | 在册（**≠L738 follow-up4 stderr**） |
| #9 | `…followup5-….exit` | **L745** | 在册（**≠L739 follow-up4 exit**） |
| #10 | `…r5-followupfix4-selfcheck-…json` | **L741** | 在册（≠L747 fix5） |
| #11 | `…r5-followup4-review-adjudication-…md` | **L740** | 在册（**≠L734 follow-up3 adjudication**） |

→ 11/11 全部受保护，与 Task L38/L42「11/11 → 96/96」一致。未按文件名相似度或 pin 序号推断。

## 4. #5 F1（childEngine / PSEdition）核验

- **旧 artifact 未改写**：pin #10（fix4，2154 bytes / `64812B7F…`）与上一轮冻结 pin（follow-up #5 prompt #4：2154 / `64812B7F…`）、pin #11 L15 三处 pin **逐字相同**；其内容仍为 `childEngine="Windows PowerShell"`、`sourceBytes=67071` / `4C01B8F9…`、`childStdoutBytes=584`，child 自报 base64 解码确为 `{"engine":"Desktop","engineVersion":"5.1.26100.9549","sourceBytes":67071,…}` → F1 的事实前提真实存在，且 fix4 未被回改。
- **修正口径与 artifact 实际值一致**：pin #2 L90（fix4：父进程侧 `childEngine` 标签 = Windows PowerShell executable；child JSON `engine` 字段 = `Desktop` = PSEdition，版本 5.1.26100.9549）与 pin #10 完全对得上；pin #1 L25/L38 同口径。
- **fix5 三值显式**：pin #4 顶层 `childEngine="Windows PowerShell"`、`childPSEdition="Desktop"`、`childEngineVersion="5.1.26100.9549"`；其 child 自报 base64 解码 = `{"engine":"Windows PowerShell","edition":"Desktop","engineVersion":"5.1.26100.9549",…}` → 父进程字段与 child 自报字段首次**同名同值**，上一轮的歧义源已消除。Task L38 与 pin #4/L91 三者一致。

## 5. self-check5 绑定核验

pin #4 见证值（均在 2000 字符内，或由 child stdout base64 解码见证）：`sourcePath=verification/P02/p02pre-r1f-capture.ps1`、`sourceBytes=67582`、`sourceSha256=5A3FE118A8758CCDF0BEDBE170D31B34DA6C338101096EAA825DE80DF70E8316`（= 本轮 pin #3 pin）、`childExecutable=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`、`childEngine=Windows PowerShell`、`childPSEdition=Desktop`、`childEngineVersion=5.1.26100.9549`、`childExitCode=0`、`parseResult=PARSE_OK`、`parseErrorCount=0`、7 个 `selectedFunctions`（`Test-UnreadUserDataStagingPath`/`Test-SafeRepositoryRelativePath`/`Get-LinkTypeEvidence`/`Get-InventoryAction`/`Test-ExpectedDetachedBranchResult`/`Assert-InventoryPolicySelfCheck`/`Assert-CommandSerializationSelfCheck`，在 script L107–L169 逐一定义且均为内存纯函数）、`selfCheckResult=PASS`、`selfCheckOutputCount=0`、`childStderrBytes=0`（`childStderrSha256=E3B0C442…B855` = 空字节串 SHA-256）；child 自报 `captureScriptInvoked=false`、`hostGetterInvoked=false`、`registryOrAclWriteInvoked=false`。`childStdoutBytes=615`/`8567C42B…` 与解码长度、`sourceTransport` 字段自洽。Task L38 / manifest L91 的引述与上述逐项相符。

## 6. Codex 对 #5 report pin 编号纠正的依据（复核结论：成立）

pin #7（follow-up #5 prompt）实际编号：**#8 = follow-up #4 stderr.log（118238 bytes）→ script L738**；**#9 = follow-up #4 exit（3 bytes）→ L739**；**#11 = follow-up #3 review adjudication（4500 / `98F2AF2B…`）→ L734**；另 #5 = follow-up #4 review adjudication（4000 / `1CFE92BE…`）→ L740、#10 = fix3 selfcheck（2927 / `18BD55A9…`）→ L735、#6/#7 = follow-up #4 stdout/prompt → L737/L736。三条均在册 → pin #6（follow-up #5 report）§2 表中「#8/#11 不在 protected key 中」及其 O3 属**false positive**（该 report 本身在 L28 又列出 `followup4-（L736–L739）`，自相矛盾）。Codex 书面纠正与 script 实际行号、pin 文件内容三者吻合。

## 7. manifest 关于 #4 Review outputs 的范围措辞

pin #2 L70–L73 已把 follow-up #4 的 prompt/stdout/stderr/exit 四件与 L74 的 adjudication 明确枚举，且 script L736–L740 全部在册；L57「R8, the enumerated Review artifacts and adjudications through follow-up #6, and review-fix self-checks are in the current protected inventory」为**限定式**（enumerated）表述，与实际 inventory（含 R8 L757、R4 三组四件套 L757–L769、followup #1–#6 四件套、9 个 self-check）一致，无 overclaim。上一轮报告的边界模糊（O3）已随 #4 stderr/exit 在册而消解。

## 8. 数值 / review status / release order / Gate 一致性

- 继承性精确数值可对：manifest L8/L51 的 **35 个环境变量**（script L629 恰 35 项）、**12 input roots**（L647–L659）、**13 output leaves**（L661）、**3 canary leaves**（L663）、**3 WER 目录**（L665）、**2 hive × 2 view × 4 value**（L464–L467）、`-z` NUL/终止 split 计数（L179/L193）、`symbolic-ref` Base64 `ZmF0YWw6IHJlZiBIRUFEIGlzIG5vdCBhIHN5bWJvbGljIHJlZgo=` 解码 = `fatal: ref HEAD is not a symbolic ref\n`（38 bytes，与 manifest L29 一致）、R1 manifest `12615 / A5510774…C67A7`（Task L62 = manifest L8；尾字符 `7` 已修正）。
- review status 链：follow-up #1 `(0/0/0/4)`、#2 `(0/0/1/1)`、#3 `APPROVED (0/0/0/0)`、#4 `(0/0/0/1)`、#5 `(0/0/0/1)`、#6 `READY/DISPATCH_NEXT` 在 Task L95–L100、manifest L15/L57、pin #5 L7、pin #11 L7 间一致；R3 候选因路径覆盖未释放（L97/pin #2 L57）表述一致。
- release order：五处一致 = follow-up #6 `APPROVED` + Codex pin/path-membership adjudication → Windows PowerShell 5.1 `ScriptBlock::Create` parse-only（唯一 `…-r8-…json`，`captureScriptInvoked=false`）→ 独立 pre-run adjudication（exact pins/身份/roots/输出 absent/status/index/path scope/**96 条**存在性与 hash）→ 单次 exact argv capture（Task L34/L42–L43/L65/L99–L101、manifest L57、pin #5 L25）。R8/capture 均 `NOT_RUN`/`BLOCKED`，AC 项仍为 `[ ]`。
- Gate 状态未被误写：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`（Task L38/L51、manifest L53/L57、pin #5 L29、pin #11 L23）。script L34–L42 `classifications` 仍为 `UNPROVABLE`/`REQUIRES_ACTIVE_TEST`/`NOT_RUN`，未把 waiver/self-check/Review 写成 Gate PASS。

## 9. 非阻塞观察（不计入 counts）

- **O1**：Task **L42**「follow-up #5 的**两个** F1/P3 文档事项」——该轮判定为 `(0/0/0/1)`、唯一 F1，且 pin #5 的修复点正是**两个文档**（Task L38 与 manifest L84/L90–L91）。按“两处文档措辞”读法成立且与计数不冲突；若愿意更严格，可写成「唯一 F1/P3（Task 与 manifest 两处措辞）」。**不构成 AC 证伪**（L42 的可验证条件均成立），故不计 finding；注意任何改动都会使当前 Task pin（22425 bytes）失效。
- **O2**：pin #6（follow-up #5 report）§2 明细「旧 65（L670–L728）+ 12 + 6」自相失算（L670–L728 实为 59，59+12+6=77），其 77/90 总数正确；同 report §6 O1 引用的「pin #5 L21 `UNPROVEN / NON_BLOCKING`」亦对不上 pin #5 内容。属**历史冻结 artifact**，当前候选文档未复述该错值，无需（也不应）改写。
- **O3**：pin #5 称 #5 report「mis-numbered three inputs」，实际错配涉及该表 6 行（#4/#6/#7/#9/#10/#11 → 4 个真实 pin 未被实际核对），只是其纠正结论（11/11 在册、O3 为 false positive）经验证**正确**；措辞可更精确，不影响释放。
- **O4**：Task L38 用 `self-check5=PASS_WITH_EVIDENCE`，artifact 字段为 `selfCheckResult=PASS`；这是 Task 表格既有约定（L79/L90/L92/L94 同式），manifest L91 亦明确「Codex self-check evidence, not independent Review or Gate PASS」，不产生可误导的歧义。
- **O5（上轮 O1 延续）**：`sourceTransport="child read the exact pinned file path; …"` 仍为叙述性自报字段（无 stdin 字节数/命令哈希可测值），manifest L91 复述之；与既有 `UNPROVEN / NON_BLOCKING` 归类一致，建议后续 self-check 增可测字段。

## 10. Scope limitations（残余限制）

1. **bytes/SHA 全部未复算**：无 shell/hash 可用；「一致」仅指 pins 与 Task/manifest/adjudication 间字面一致（独立复算为 Codex pre-run 职责，pin #1 L42）。
2. **单行 JSON 截断**：pin #4（及 #10）第 2000 字符后的字段（`childStderrBase64`、`sourceHashMatchedBetweenParentAndChild`、`createdUtc` 等）**不可见**；本次已重试一次，截断点相同。所幸 Task/manifest 未依赖这些隐藏字段（三个 false 标志由 child 自报 base64 见证）。
3. **pin #2 L57 尾部被 2000 字符截断**（截到「roots/refs, out…」），故 L57 全句未逐字读毕；可见部分与 L61 枚举、script 实际 inventory 自洽。
4. **script 全量 diff 不可验**：无法证明 67582-byte script 相对 67071-byte 前一候选「仅追加 6 个路径字面量」，只能证明 L670–L746 的 77 项内容与行位与上轮报告记录完全一致（强证据，非全量 diff）。
5. **未 pin 的旧 artifact 不可验**：fix3 selfcheck（2927 / `18BD55A9…`）不在本轮 11 pins 内，「旧 artifact 未被改写」只能对 fix4（pin #10 与上轮 pin 逐字相同）与 fix5（新）给出；fix3/fix2/fix1 内容未读。
6. **Codex 对 fix4 的 `engine` 字段来源（`PSVersionTable.PSEdition`）解释不可从 pins 独立证明**（self-check harness 源码未 pin）；仅由 fix5 显式分列 `engine`/`edition` 得到旁证。
7. 本 Review 为纯静态，不替代 R8、pre-run adjudication、capture、post-run 五态裁定，也不构成任何 Gate PASS；Review **不授权** R8/capture/Build-Cargo/AC1–AC7。

## 11. 推荐下一步（可直接转发给 Codex /root）

> **Task=`P02PRE-R1F`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。DSH Review Round 5 follow-up #6=`APPROVED (0/0/0/0)`**（无 P0/P1/P2/P3；O1–O5 为非阻塞观察）。已逐字核验：script 两个 protected-key arrays = **83（L670–L752，其中 L747–L752 为本轮新增 6）+ 13（L757–L769）= 96 keys / 96 unique / 0 duplicates**；本轮 11 pins **全部**在册（#1→L678、#2→L683、#3→L684、#4→L747、#5→L746、#6→L743、#7→L742、#8→L744、#9→L745、#10→L741、#11→L740）；self-check5 精确绑定 `67582 / 5A3FE118…8316`、Windows PowerShell 5.1.26100.9549（PSEdition=Desktop）、PARSE_OK、7 个纯函数、PASS、assert output=0、child exit=0、stderr=0、capture/getter/registry/ACL write=false；#5 的 childEngine/PSEdition 文档口径已修正且 fix4 未被改写；Codex 对 #5 report pin 编号误映射的纠正有据（follow-up #4 stderr=L738、exit=L739，follow-up #3 adjudication=L734，均为 protected）。请：(1) 以 Codex adjudication 记录本轮 APPROVED 与 pin/path-membership 结论（O1–O5 可择机在**下一次**冻结时一并精修，勿在 R8 前改动 Task/manifest 字节，否则 pins 失效）；(2) 对同一组 frozen exact script bytes 执行 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only 并落唯一 `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`（记录输入 bytes/SHA、进程 exit、stdout/stderr，`captureScriptInvoked=false`）；(3) R8=`PARSE_OK` 后另做独立 pre-run adjudication（身份/SID/token、roots/refs、输出目标 absent、status/index、exact path scope、**96 条** protected 存在性与 hash）；唯此才可按 manifest exact argv 运行**一次** capture，任何 mismatch 保留 partial evidence 并停止，不重试、不清理。`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN` 一律不变；Review/self-check/waiver 不等于 Gate PASS。
