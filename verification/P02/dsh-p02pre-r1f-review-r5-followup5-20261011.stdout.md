# P02PRE-R1F Review Round 5 follow-up #5 — 独立只读复核

## Decision

`CHANGES_REQUESTED`

counts：`P0/P1/P2/P3 = 0 / 0 / 0 / 1`

- 本轮三个核心命题经逐字核验**成立**：两个 protected-key arrays = **77 + 13 = 90 keys / 90 unique / 0 duplicates**；本轮 11 个 pin 中所有应受保护的 9 条路径均在冻结 script 中精确逐字命中；follow-up #4 的唯一 F1/P3（manifest 把当前 self-check 的 child stderr 写成 `0`）已按 pin #4 实际证据修正。
- 但存在 1 项可直接复现的**证据双层措辞矛盾**（同一 self-check artifact 内部 `childEngine` 与 child 自报 `engine` 不一致，而 manifest 的该轮描述与二者之一不能同时精确成立），按本 Task 既有 P3 先例不给出 `APPROVED`。该 finding 不涉及 script 字节，也不改变 90/90 与 Gate 结论。

## 1. 阅读范围与边界声明

- 只读 11 个 pin 文件；`read` 全量或分段读毕：pin #1（101 行）、pin #2（85 行）、pin #3（907 行，L1–400 / L400–599 / L600–779 / L781–907 分段读毕）、pin #4（单行 JSON）、pin #5（23 行）、pin #6（91 行）、pin #7（28 行）、pin #9（43 行）、pin #10（29 行）、pin #11（118238 bytes / 834 行；读首 40 行与 L690–749）。
- **未执行**任何 shell / grep / rg / PowerShell / 测试 / getter / hash / R8 / capture / Build-Cargo / AC1–AC7；未写文件；未访问 `.tmp.driveupload` 或任何未 pin 路径；未改 Gate。本轮我曾发起一条只读 `pwsh` 探测命令，被 DSH 沙箱以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite` 直接拒绝，**命令未运行**，此后全部核验仅用 `read`。
- 因此 pin 表中的 bytes/SHA 我一律**未复算**（`UNPROVEN`）；下文“一致”仅指 pins 之间的字面交叉一致。独立复算归 Codex pre-run adjudication（pin #1 L42/L43）。

## 2. protected-key membership（核心）

冻结 script 中只有两处写 `$Result.protectedHashes`，其后（L767 起）不再新增键：

| 数组 | 行范围 | 字面量数 | 明细 |
|---|---|---|---|
| 数组 1 | `foreach ($key in @(` L669 → `)) {` L747 | **77**（L670–L746） | 旧 65（L670–L728）+ follow-up#3 轮新增 12（L729–L740）+ 本轮新增 6（L741–L746） |
| 数组 2 | `foreach ($key in @(` L750 → `)) {` L764 | **13**（L751–L763） | r8 + r4 / r4-retry / r4-followup 四件套 |
| 合计 | — | **90** | — |

- 逐条字面清点：L670–L746 共 77 行全为 `'...'` 路径字面量（末项 L746 无逗号）；L751–L763 共 13 行同理。两数组**无交集**：`r4-*`、`…r8-…json` 仅出现在数组 2；`r1/r2/r3/r5/followup*` 仅出现在数组 1。数组 1 内相邻易混的 `r3`（L704–L707）与 `r5`(L708–L711)、`followup-`(L717–L720) 与 `followup2-`(L724–L727)、`followup3-`(L730–L733)、`followup4-`(L736–L739)、`followup5-`(L742–L745) 文件名逐条互异。
- → `90 keys / 90 unique / 0 duplicates` 成立，与 pin #2 L17/L61、pin #1 L25/L38、pin #5 L19 一致。**R5F3-CI1 的 84→90 扩展按“旧路径 + 已知未来产物路径”规则闭合**：L729 `p02pre-r1f-r5-followup2-review-adjudication-…`（与旧 L728 `…followup2-adjudication-…` 是不同文件、同时存在）、L730–L733 follow-up #3 prompt/stdout/stderr/exit、L734 follow-up #3 adjudication、L735 selfcheck3、L736–L740 预定 follow-up #4 五件、**L741 selfcheck4**、**L742–L745 预定 follow-up #5 prompt/stdout/stderr/exit**、**L746 预定 follow-up #5 Codex adjudication**。
- 本轮 11 个 pin 在 script 中的**精确命中位置**（逐字符串匹配，非相似名/行号推断）：

| pin | 路径 | script 行 | 状态 |
|---|---|---|---|
| #1 | `doc/tasks/P02PRE-R1F.md` | L678 | 在册 |
| #2 | `verification/P02/p02pre-r1f-manifest-20261011.md` | L683 | 在册 |
| #3 | `verification/P02/p02pre-r1f-capture.ps1` | L684 | 在册 |
| #4 | `…r5-followupfix3-selfcheck-20261011.json` | L735 | 在册 |
| #5 | `…r5-followup3-review-adjudication-20261011.md` | L734 | 在册 |
| #6 | `…review-r5-followup3-….stdout.md` | L731 | 在册 |
| #7 | `…review-r5-followup3-….prompt.md` | L730 | 在册 |
| #9 | `…r5-followup2-review-adjudication-20261011.md` | L729 | 在册 |
| #10 | `…followupfix-selfcheck-wrapper-attempt1-….md` | L716 | 在册 |
| #8 | `…review-r5-followup4-….stderr.log` | **不在 protected key 中** | 见下 |
| #11 | `…review-r5-followup4-….exit` | **不在 protected key 中** | 见下 |

- pin #8/#11（follow-up #4 的 stderr/exit）未列入 protected inventory，与 pin #2 L57「enumerated Review artifacts and adjudications through follow-up #5」的措辞存在边界模糊：stderr/exit 属“Review artifacts”但**本 Task 从未把它们纳入 hash inventory**（历史上 follow-up #1/#2/#3 的 prompt/stdout/stderr/exit 在 #3 轮被整体加入，唯独 #4 的 stderr/exit 未加，而 #4 的 prompt/stdout/adjudication 已加）。这不是本轮新增缺陷（#4 轮的 84 条已如此），也不构成 release 阻塞——pin #8/#11 的 bytes/SHA 已由本 Review 与 Codex 以 pin 形式冻结——故只作 O3 观察，不计入 counts。

## 3. follow-up #4 F1/P3 修复核验

- **旧值如实保留**：pin #4（`…followupfix3-selfcheck-….json`，2927 bytes / `18BD55A9…`）保留 `sourceBytes=66560` / `sourceSha256=F55F195E…`、`childStderrBytes=404`、`childStderrSha256=821020161208F807E91B67BA4ADD7B4B0A659459C070046085D1BFED51BDA719`，且 `childStderrBase64` 非空（解码为 `#< CLIXML` progress record）。旧 artifact 未被改写。
- **新值如实修入**：pin #2 L83 现记录 fix3 的「child stderr=404 bytes / SHA-256 82102016… (one CLIXML PowerShell progress record)」，L84 记录 fix4 的「parse errors=0, assertion output=0, child exit=0, child stderr=0」；pin #5 L13–L15 以同一组数值 adjudicate。即上一轮 F1/P3 的“文档矛盾”已闭合，**未再出现把 404 写成 0 或把 0 写成错误文本**的反向错误。
- **fix4 artifact 与 pin #3 精确绑定**：pin #4 内部字段 `sourcePath=verification/P02/p02pre-r1f-capture.ps1`、`sourceBytes=67071`、`sourceSha256=4C01B8F9F0A6225B25398733B16D7286C40BBF22C4958E82BDD7A7710BADB25D`，与 pin #3 声明 pin、pin #1 L38、pin #2 L17/L84 完全一致；`childExecutable=C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`、`childEngineVersion=5.1.26100.9549`、`childExitCode=0`、`parseResult=PARSE_OK`、`parseErrorCount=0`、`selfCheckResult=PASS`、`selfCheckOutputCount=0`、7 个 selectedFunctions 与 pin #1 L38、pin #2 L84 一致。
- **stderr=0 已直接见证**：pin #4 尾部 `childStderrBytes=0`、`childStderrSha256=E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`（空字节串的 SHA-256）、`childStderrBase64=""`——三者内部自洽，且把 stderr 噪声从 fix3 的 404 bytes 降到 0 的差异，机制上与 `sourceTransport` 由“命令行/标准输入传源码”改为“child 直接读固定文件路径”（无 `-EncodedCommand` 载荷 → 无 CLIXML progress 输出）相符。
- **capture/getter/registry/ACL write=false 有双证据**：pin #4 的 `childStdoutBase64` 解码出 child 自报对象，其中 `captureScriptInvoked=false`、`hostGetterInvoked=false`、`registryOrAclWriteInvoked=false`、`selfCheckOutputCount=0`、`sourceBytes=67071`、`sourceSha256=4C01…B25D`；与 pin #1 L38「capture/getter/write=false」、pin #2 L84 一致。

## 4. Task / manifest / script / pin 与 release 顺序核验

- **计数与 supersede 链**：pin #1 L25/L34/L38/L98、pin #2 L17/L57/L61 一致为 90/90 unique；pin #4 L19（84/84）、pin #6（84/84）、pin #10 L17/L21（72/72）均为其历史轮次记录，已被 pin #1 L25/L98 与 pin #2 L57 明确标为 superseded，无残留误导。
- **release 顺序无矛盾**：pin #1 L25/L34/L42/L43/L65/L99–L101、pin #2 L57 一致 = follow-up #5 `APPROVED` + Codex pin/path-membership adjudication → Windows PowerShell 5.1 `ScriptBlock::Create` parse-only（唯一 R8 artifact `p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`，`captureScriptInvoked=false`）→ 独立 pre-run adjudication（身份/SID/token、roots/refs、输出目标 absent、status/index、exact path scope、**90 条** protected 存在性与 hash）→ 单次 exact argv capture。R8 未声称已跑（pin #1 L100、pin #2 L57）；capture=BLOCKED/NOT_RUN（pin #1 L101）。仅有的措辞差异是 pin #5 L19「pin/path-membership adjudication」与 pin #6 的 disposition 行「pin/path adjudication」对上位权限表述略有出入，**不构成矛盾/计数/顺序冲突**，不计 finding（O2）。
- **Gate 与风险状态未被误记**：pin #1 L38/L51、pin #2 L53/L57、pin #5 L23 一致保留 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；pin #1 L40–L51 的 AC 项仍为未勾选 `[ ]`；pin #3 L34–L35/L42 的 `classifications` 仍为 `UNPROVABLE`（未把 waiver/self-check 写成 PASS）。**无 waiver→PASS、无 build/AC 放行措辞。**
- **script 侧路径策略与 AC 对齐**：staging 排除在任何 `Get-Item`/`Get-FileHash`/`Get-Acl` 之前（L399–L410）、`~[0-9]`/ADS/尾随点空格/`.`/`..` 在文件系统访问前拒绝（L112–L115）、偏移 base64 精确映射 `DETACHED`（L126/L339–L350）、`LinkType` 缺失显式 `NOT_AVAILABLE_ON_ENGINE`（L119–L123）、计数器字段齐全（L312/L803–L853）；两个数组之后不再有 `protectedHashes` 赋值，`invalidHashCount`（L813）会对 90 条中任一非 `PRESENT` 记录计数并进入 stopReason（L866）。

## 5. Findings

### F1 — P3：当前 self-check artifact 的工程标识存在双层不一致，manifest/pin 引述无法对两者同时精确成立

- **位置**：
  - `verification/P02/p02pre-r1f-manifest-20261011.md` **L84**（`Windows PowerShell 5.1.26100.9549 parsed source 67071 bytes …`）；
  - `doc/tasks/P02PRE-R1F.md` L38（同轮 `Windows PowerShell 5.1.26100.9549 self-check4=…`）；
  - 反证在 pin #4 自身：`verification/P02/p02pre-r1f-r5-followupfix4-selfcheck-20261011.json` 的顶层字段 `"childEngine":"Windows PowerShell"`，而同一 artifact 的 `childStdoutBase64` 解出 child **自报** `{"engine":"Desktop","engineVersion":"5.1.26100.9549",…}`。
- **性质**：该 artifact 同时携带两种工程标识（写者声明的 `childEngine` 与 child 自报 `engine`），二者不同名；manifest L84 / Task L38 只引用了版本号 `5.1.26100.9549`（与两者都相符），但其句式“`Windows PowerShell 5.1.26100.9549 parsed source …`”“Child read the exact source path”会被读成“child 自报为 Windows PowerShell”。上一轮 F1/P3 已因同一 artifact 的另一字段（stderr）触发一轮，同类“artifact 字段 vs 冻结文档措辞”问题仍在。
- **影响**：不改变数值（版本号、bytes、exit、stderr 均可对上），也不改变 capture 行为；但在 pre-run adjudication 逐条复算时，`childEngine` 与 child 自报 `engine` 这两个字段的引述会再次出现“文档说的是哪一个”的歧义，与上轮被接受的 F1 属同一风险类别。
- **最小修复**（不改 script 字节、不改任何既有 artifact）：在 pin #2 L84 与 pin #1 L38 把工程标识写成 artifact 的实际值，例如 `childEngine=Windows PowerShell（child 自报 engine=Desktop）/ version 5.1.26100.9549`，或直接只保留 `5.1.26100.9549 child exit=0` 而不写 engine 名。**注意**：pin #2 与 pin #1 的字节会因此变化，pin #2（24689 / `9CAEE9C9…`）与 pin #1（21603 / `BEFFCA43…`）的现行 pin 随即失效，须由 Codex 同步重冻并重跑/重述 self-check 说明后，再派发下一轮非作者 Review；**不得**为“对齐措辞”改动 `p02pre-r1f-capture.ps1`（会连带使 pin #3/#4 失效）。

## 6. 非阻塞观察（不计入 counts）

- **O1（上轮 O1 延续）**：pin #4 的 `sourceTransport`（`child read the exact pinned file path; no source on command line or stdin`）仍是叙述性自报字段，无可测值（stdin 读取字节数、命令行长度）；pin #2 L84 将其复述为“Child read the exact source path; source bytes were not passed on command line or stdin”。建议后续 self-check artifact 增加可测字段（读取字节数或 harness 编码命令 SHA），本项按 pin #5 L21 既有 `UNPROVEN / NON_BLOCKING` 处理。
- **O2**：pin #5 L19 的 `pin/path-membership adjudication` 与 pin #6 disposition 行的 `pin/path adjudication` 用词略有差异，含义一致，不构成 release 顺序矛盾。
- **O3**：follow-up #4 的 `stderr.log`/`exit`（本轮 pin #8/#11）未进入 protected inventory，与 pin #2 L57「Review artifacts … through follow-up #5 都在 protected inventory」的措辞边界不清；同为 follow-up #5 的 prompt/stdout/stderr/exit 已列入（L742–L745），建议后续统一口径（要么全部 Review 四件套入册，要么把该句限定为“prompt/stdout/adjudication”）。
- **O4**：90 条路径在 pre-run 时刻的**存在性**无法在本审查边界内验证（L742–L745 的 follow-up #5 产物、L751 的 R8 均须在产生后才存在；任一 ABSENT/hash 漂移会按 L813/L866 计满并停止）。这是 Codex pre-run 的独立职责，非本轮 finding。

## 7. Scope limitations（残余限制）

- **bytes/SHA 全部未复算**：无 shell/hash/getter 可用，pin 表中“一致”仅指 pins 间字面一致；文件数量（如“907 行”）不出现在任何 pin 中，故我核对的数组行号/计数是本轮独立清点，**不是**对 67071 bytes 这一声明的复算。
- **pin #4 尾部不可全读**：该文件为单行 JSON，`read` 工具按行截断（`line truncated to 2000 chars`）。我实际见证到 `childStderrBytes=0`、`childStderrSha256=E3B0C442…B855`、`childStderrBase64=""`，以及 `childStdoutBase64` 中的 `captureScriptInvoked=false` / `hostGetterInvoked=false` / `registryOrAclWriteInvoked=false`；但 `sourceHashMatchedBetweenParentAndChild`、`createdUtc` 等尾部字段未能在本轮读取边界内看到。若需 100% 逐字段见证，须由 Codex 在下一轮以多行 JSON 或纯文本形式重出该 artifact（见 §6 O1 建议）。
- **pin #11（stderr.log）** 我只读首 40 行与 L690–749，未逐行核对全文；其内容为上一轮 Reviewer 的完整 reasoning trace（含其越界 grep 的自我披露）。
- 本 Review 为纯静态，不替代 R8、pre-run adjudication、capture 与 post-run 五态裁定，也不构成任何 Gate PASS。

## 8. 不授权声明

本 Review 不授权 R8、capture、Build/Cargo、AC1–AC7 或任何 Gate；`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN` 一律不变。

---

## 推荐下一步（可直接转发给 Codex /root）

> **Task=`P02PRE-R1F`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。DSH Review Round 5 follow-up #5=`CHANGES_REQUESTED (0/0/0/1)`。已逐字核验：冻结 script 两个 protected-key arrays = **77（L670–L746，其中 L741–L746 为本轮新增 6）+ 13（L751–L763）= 90 keys / 90 unique / 0 duplicates**；本轮 11 pin 中 9 条应受保护路径全部精确在册（含 L729 follow-up#2 review-adjudication、L730–L733 follow-up#3 四件套、L734 follow-up#3 adjudication、L735 selfcheck3、L736–L740 follow-up#4 五件、L741 selfcheck4、L742–L746 follow-up#5 五件）；follow-up #4 的唯一 F1/P3 已按 pin #4 实际证据修正（fix3 的 404 bytes/`82102016…` 如实保留，fix4 的 `childStderrBytes=0`、`parseErrorCount=0`、`childExitCode=0`、三个 write/invoke=false 与 pin #3 的 `67071 / 4C01…B25D` 精确绑定）。唯一开放项：**F1 / P3** —— pin #4 的 `"childEngine":"Windows PowerShell"` 与其 `childStdoutBase64` 解出的 child 自报 `{"engine":"Desktop"}` 不一致，而 `verification/P02/p02pre-r1f-manifest-20261011.md` L84 与 `doc/tasks/P02PRE-R1F.md` L38 的引述无法对二者同时精确成立（版本号 `5.1.26100.9549` 两者皆符，故不影响数值）。请 (1) 仅修正这两处工程标识措辞，**不得**改动 `p02pre-r1f-capture.ps1`；(2) 因 Task/manifest 字节改变，重新冻结并公布 Task/manifest/script/self-check/adjudication exact pins（建议同时把该 self-check artifact 以多行 JSON 或纯文本重出，解决单行 2000 字符不可全读的边界问题，并考虑 O3 的 stderr/exit 口径统一）；(3) 再派发一轮非作者只读 Review 取得 `APPROVED (0/0/0/0)` 后，才可执行 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only 并落唯一 `p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`（`captureScriptInvoked=false`）；(4) R8=`PARSE_OK` 后再做独立 pre-run adjudication（身份/SID/token、roots/refs、输出目标 absent、status/index、exact path scope、**90 条** protected 存在性与 hash），唯此才可按 manifest exact argv 运行一次 capture；任何 mismatch 保留 partial evidence 并停止，不重试、不清理。若 F1 被裁定为无需修改，请以 pin adjudication 明确记录该 engine 字段歧义及其不改字节的理由。

在收到 Codex 的上述处置前，无需其他 Agent 动作。
