# P02PRE-R1F Review Round 5 follow-up #4 — 独立只读复核

## Decision

`CHANGES_REQUESTED`

counts：`P0/P1/P2/P3 = 0 / 0 / 0 / 1`

- 本轮请求的核心命题——“新候选是否闭合 R5F3-CI1 的 protected path 覆盖缺口、84/84 unique、release 顺序与 Gate 措辞无误”——我逐字核验后判定**成立**（见 §2、§3）。
- 但 11 个 pins 内部存在 1 项可直接复现的文档/证据矛盾（manifest 对**当前** self-check 的 stderr 陈述与 pin #4 自身字段冲突），故不给出 `APPROVED`。该 finding 不涉及 script 字节，也不改变 path membership 结论。

## 1. 阅读范围与边界声明

- 只读 11 个 pin 文件；`read` 全量读毕：Task 100 行、manifest 78 行、script 901 行（L1–L400 / L401–L700 / L701–L901 分段读毕）、pin #4 43 行、pin #5 29 行、pin #6 104 行、pin #7 27 行、pin #8 42 行、pin #9 23 行、pin #10 11 行、pin #11（stderr.log，739 行）读毕首 40 行与末 46 行。
- **未执行**任何 shell / grep / rg / PowerShell / 测试 / getter / hash / R8 / capture / Build-Cargo / AC1–AC7；未写文件；未访问 `.tmp.driveupload` 或任何未列路径；未改 Gate。
- 因此全部 bytes/SHA 由我**未复算**（`UNPROVEN`）；下表只做 pins 之间的字面交叉核对与 script 内字面量清点。文件存在性/哈希复算按 Task L42/L43 归 Codex pre-run adjudication。

## 2. protected-key membership 核验（核心，逐字匹配，不用行号或相似名推断）

冻结 script 中只有两处写入 `$Result.protectedHashes`：

| 数组 | 行范围 | 字面量数 |
|---|---|---|
| 数组 1 | `foreach ($key in @(` L669 → `)) {` L741，键 L670–L740 | **71** |
| 数组 2 | `foreach ($key in @(` L744 → `)) {` L758，键 L745–L757 | **13** |
| 合计 | — | **84** |

- 旧 72 = 数组 1 的 L670–L728（59）+ 数组 2 的 L745–L757（13）；新增 12 = **恰好 L729–L740**。旧 72 与新增 12 无交集，两数组亦无交集（`r4-*` 只在数组 2；`r1/r2/r3/r5/followup*` 只在数组 1）。逐条比对无重复，含大小写归一后仍为 84 个互异键（script L32 的 `[ordered]@{}` 字符串键默认大小写不敏感，我已按该语义检查，无 case-only 重复）。→ manifest L17/L61 与 Task L38、pin #5 L15 的 `84 keys / 84 unique / 0 duplicates` **正确**。
- 新增 12 条与 manifest L63–L74 逐条**同序同名**：L729→(1)、L730–L733→(2)–(5)、L734→(6)、L735→(7)、L736–L739→(8)–(11)、L740→(12)。

本轮 11 个 pin 在 script 中的**精确字面位置**（逐字符串匹配，非行号/相似名推断）：

| pin | 路径 | script 行 |
|---|---|---|
| #1 | `doc/tasks/P02PRE-R1F.md` | L678 |
| #2 | `verification/P02/p02pre-r1f-manifest-20261011.md` | L683 |
| #3 | `verification/P02/p02pre-r1f-capture.ps1` | L684 |
| #4 | `...p02pre-r1f-r5-followupfix3-selfcheck-20261011.json` | **L735** |
| #5 | `...p02pre-r1f-r5-followup3-review-adjudication-20261011.md` | **L734** |
| #6 | `...dsh-...review-r5-followup3-20261011.stdout.md` | **L731** |
| #7 | `...dsh-...review-r5-followup3-20261011.prompt.md` | **L730** |
| #8 | `...p02pre-r1f-r5-followupfix-selfcheck-20261011.json` | L722 |
| #9 | `...p02pre-r1f-r5-followup2-review-adjudication-20261011.md` | **L729** |
| #10 | `...p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md` | L716 |
| #11 | `...dsh-...review-r5-followup3-20261011.stderr.log` | **L732** |

- Review focus 点名要求的条目全部在册：本轮 Codex adjudication（L734）、follow-up #2 的两个 adjudication（旧名 L728 `p02pre-r1f-r5-followup2-adjudication-…` 与 pin #9 的 `…-review-adjudication-…` L729，两者是不同文件、同时存在）、follow-up #3 prompt/stdout/stderr/exit（L730–L733）、自检3（L735）、预定 follow-up #4 prompt/stdout/stderr/exit/adjudication（L736–L740）、R8 目标（L745）。
- R5F3-CI1 的原始错配可在此复现其成因：旧候选只有 L728 的 `…followup2-**adjudication**…`，上一轮 Reviewer（pin #11 L722）把 pin #5 映射到 L728 属**相似文件名误配**；当前正确路径为 L729，已修复。

## 3. 文档、证据与 release 顺序核验

- **计数与措辞**：Task L38、manifest L17、pin #5 L15 三处 `84/84 unique` 与我的清点一致；pin #9 L17/L21 的 `72/72` 与 `63` 属其历史轮次记录，已被 pin #5 L15 与 Task L96/L97 明确 supersede，无残留误导。
- **旧 self-check pin #8**：manifest L78 已补该 pin 行（`2307 / FE2277D0…4F237C`、`phase=R5_FOLLOWUPFIX_ISOLATED_SELFCHECK`、旧 source pin），与 pin #8 内容（`sourceBytes 65530 / 3B143481…32A3`）及 pin #9 L16 的 `Length=2307 / FE2277…` 一致；上一轮 O4 已关闭。
- **结构化 skip counts**：manifest L47 要求数量落在结构化字段，script L834 `repositorySkippedSymlinks`、L835 `repositoryUnreadUserDataPaths` 均在；L852 的 note 仅说明原因的分支不重复数字，与 manifest L47 措辞一致。上一轮 O2 已按最小文档修正关闭。
- **当前 PS 5.1 self-check 的 source/exit 证据**：pin #4 `sourceBytes=66560 / sourceSha256=F55F195E…` 与 pin #3、Task L38、manifest L17/L77 完全一致；`childExitCode=0`、`parseErrorCount=0`、`selfCheckResult=PASS`、`selfCheckOutputCount=0`、三个 `false` 字段与 Task L38 一致。**但 stderr 一项不一致 → 见 §4 F1。**
- **release 顺序**：Task L25/L34/L38/L42/L43/L46 与 manifest L57 一致 = follow-up #4 `APPROVED` + Codex pin/path-membership adjudication → Windows PowerShell 5.1 `ScriptBlock::Create` parse-only（唯一 R8 artifact）→ 独立 pre-run adjudication（identity/SID/token、roots/refs、output absence、status/index、exact path scope、**84 条** protected 存在性与 hash）→ 单次 exact argv capture。R8 未声称已跑（Task L99、manifest L23 `NOT_RUN`）。
- **waiver / Build / AC 未被误记**：Task L38/L51、manifest L53、pin #5 L29 一致保留 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`；Task AC 列表仍为未勾选 `[ ]`；script 内 `classifications` 亦未把 waiver 写成 PASS（L35/L42 保持 `UNPROVABLE`）。**无 waiver→PASS、无 build/AC 放行措辞。**
- script 侧路径策略与 AC3/AC4/AC6/AC7 对齐：staging 在 `Get-Item`/`Get-FileHash`/`Get-Acl` 前按 canonical relative path 排除（L405–L410）、`~[0-9]` 等不安全形式在文件系统访问前拒绝（L114/L399）、偏移 base64 精确映射 `DETACHED`（L126/L339–L350）、`LinkType` 缺失显式 `NOT_AVAILABLE_ON_ENGINE`（L121/L425）、计数器字段齐全（L312）。

## 4. Findings

### F1 — P3：manifest 对当前 self-check 的 `child stderr=0` 陈述与 pin #4 自身证据矛盾

- **位置**：`verification/P02/p02pre-r1f-manifest-20261011.md` L77（`child stderr=0` 子句，属 “Current exact-script self-check” 句）。
- **反证**：`verification/P02/p02pre-r1f-r5-followupfix3-selfcheck-20261011.json` L35–L37：`childStderrBytes: 404`、`childStderrSha256: 821020161208F807E91B67BA4ADD7B4B0A659459C070046085D1BFED51BDA719`、`childStderrBase64` 非空且解码为 `#< CLIXML` 序列化 progress record（`<Obj S="progress" …>`）。即当前 self-check 的 child stderr **非 0**（是 PowerShell 进度记录的序列化噪声，非错误文本；`childExitCode=0` 不变）。
- **影响**：manifest 是被冻结并将在 pre-run adjudication 中逐条复算的 pin；其中一条关于**当前**候选 self-check 的数值断言与同轮 pin #4 冲突。这属于“证据陈述与所引证据不一致”，会让 R8 前的 pin 复核在 manifest/lf artifact 之间出现无法闭合的差异，并使 “stderr 干净” 这一未成立的前提进入冻结记录（其余同类断言 `2927/18BD55A9…`、`66560/F55F195E…`、`parse errors=0`、`assertion output=0`、三个 `false` 均与 pin #4 一致，仅此一项）。
- **最小修复**（不改 script 字节、不改任何 artifact）：把 L77 的 `child stderr=0` 改为与 pin #4 相符的表述，例如 `child stderr=404 bytes (serialized CLIXML progress record only; no error text)`，或直接删除该子句（Task L38 本来就未声明 stderr 为 0）。注意：manifest 字节因此变化，pin #2 的 `23135 / 9D008645…` 随即失效，须由 Codex 同步更新 pins、重跑 exact-script self-check 说明并在下一轮 Review 前重新冻结（或明确以 pin adjudication 记录该句为已更正的历史子句）；**不得**为“保持一致”而改动 `p02pre-r1f-capture.ps1`（会连带使 pin #3/#4 失效）。

## 5. 非阻塞观察（不计入 counts）

- **O1**：pin #4 的 `sourceTransport`（`child read the exact pinned file path; no source on command line or stdin`）是叙述性自报字段，未记录 stdin 字节数/命令行长度等可测值；pin #10 所声明的 “retry will stream source bytes through redirected stdin” 机制仍**未被任何 artifact 直接见证**（pin #8 无该字段，pin #4 只覆盖自己的 fix3 轮次）。pin #5 L21 已将其记为 `UNPROVEN / NON_BLOCKING`，故不构成 finding；后续若再产出 self-check artifact，建议增加可测字段（stdin 读取字节数或 harness 编码命令的 SHA）而非纯叙述。
- **O2**：84 条路径在 pre-run 时刻的**存在性**无法在本审查边界内验证（本轮 11 个 pins 已全部在册，这一点已核；但 L736–L740 的 follow-up #4 产物、L745 的 R8、以及 Task L84 记录的 r4 中断轮 `.exit`（L749）等须由 Codex pre-run 按 `invalidHashCount` 逻辑实测）。任何一条 ABSENT/hash 漂移都会按 script L807/L860 计满并停止。
- **O3**：pin #5 L23 声称范围外 grep 命中的治理层（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/tasks/P02.md`、checkpoint）已在派发后同步；该同步不在 11 个 pins 内，无法由我验证，属 Codex pre-run 独立确认项。

## 6. 残余限制

- bytes/SHA 全部未由我复算（无命令/无 hash/getter），pin 表中“一致”仅指 pins 间字面一致；独立复算仍为 `UNPROVEN`，按 Task L42 由 Codex 完成。
- pin #4 的 base64 字段我按顶层字段与可读前缀交叉核对，未做完整解码复算；pin #11 我只读首尾段落，未逐行核对全文与其余 pins 的叙述一致性（其内容为上一轮 Reviewer 的完整 reasoning trace，与 pin #6 的披露一致）。
- 本 Review 为纯静态，不替代 R8、pre-run adjudication、capture 与 post-run 五态裁定，也不构成任何 Gate PASS。

## 7. 不授权声明

本 Review 不授权 R8、capture、Build/Cargo、AC1–AC7 或任何 Gate；`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE` 一律不变。

---

## 推荐下一步（可直接转发给 Codex /root）

> **Task=`P02PRE-R1F`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`。DSH Review Round 5 follow-up #4=`CHANGES_REQUESTED (0/0/0/1)`。已由我逐字核验：冻结 script 两个 protected-key 数组 = 71（L670–L740，其中 L729–L740 为新增 12）+ 13（L745–L757）= **84 keys / 84 unique / 0 duplicates**，本轮 11 个 pins 全部在册（含 L729 `p02pre-r1f-r5-followup2-review-adjudication-20261011.md`、L730–L733 follow-up #3 prompt/stdout/stderr/exit、L734 follow-up #3 adjudication、L735 自检3、L736–L740 预定 follow-up #4 四件+adjudication），R5F3-CI1 的覆盖缺口已闭合；release 顺序、R8 未运行、capture `NOT_RUN` 与 waiver/Build/AC 措辞均无误。唯一开放项：**F1 / P3** —— `verification/P02/p02pre-r1f-manifest-20261011.md` L77 的 `child stderr=0` 与 pin #4 `p02pre-r1f-r5-followupfix3-selfcheck-20261011.json` L35–L37（`childStderrBytes=404` + 非空 `childStderrBase64`，解码为 `#< CLIXML` progress record）矛盾。请 (1) 仅修正该子句（或删除），**不得**改动 capture script 字节；(2) 因 manifest 字节改变，重新冻结并公布 Task/manifest/script/self-check/adjudication exact pins，再派发一轮非作者只读 Review 取得 `APPROVED (0/0/0/0)` 后，才可执行 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only 并落唯一 `p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`；(3) R8=`PARSE_OK` 后再做独立 pre-run adjudication（身份/SID、roots/refs、输出目标 absent、status/index、84 条 protected 存在性与 hash），唯此才可按 manifest exact argv 运行一次 capture，任何 mismatch 保留 partial evidence 并停止，不重试、不清理。若 F1 被裁定为无需修改，请以 pin adjudication 明确记录该子句与 pin #4 的关系及不改字节的理由。

在收到 Codex 的上述处置前，无需其他 Agent 动作。
