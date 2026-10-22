# P02PRE-R1H-H2-COLLECTOR — R6 exact-head 非作者静态复审

**被审精确 identity**
- code commit：`3e3fcae4a578e68adaa1aed929b69ddbb5c89304`（reflog：父 `6a59d82c`＝R5 docs head；消息 `commit: fix(P02): close R5 findings (R5-CX-01, R5-CX-03) for H2 collector R6 per source-review-r5-adjudication`）
- docs/worktree head：`39ff1d3f94d98165c603c7c0f5e051ebcae3feae`（reflog 末行：`3e3fcae4 → 39ff1d3f`，`commit: docs(P02): record R6 repair delivery and handoff for H2 collector`）
- branch/worktree：`agent/antigravity/P02PRE-R1H-H2-COLLECTOR-R3` / `G:/CODEX/New Manga.workspace/worktrees/P02PRE-R1H-H2-COLLECTOR-ANTIGRAVITY-R3`

**Verdict：`APPROVED_STATIC_CONTENT`**（无 P0/P1/P2；仅 2 项新 P3 与 2 项已裁决接受的非阻塞限制登记）

> 沙箱限制（诚实声明，未绕过）：本会话 `pwsh` 启动即被拒（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(<worktree>)`），**仅 1 次尝试**，因此 git blob/SHA-256/byte 无法由我复算；Git/PowerShell 未运行。已完整重读两份脚本（collector 1870 行、selftest 824 行），未沿用 R5 verdict。未访问 `.tmp.driveupload`；未写入/修改任何文件。

---

## 逐项结论

### 1. R5-CX-01（meta revisionNote 准确性 + 防倒退断言）— **PASS**
- `h1-raw-pre-run.ps1` **L1254** `revisionNote` 现为：`'R5/R6 repair per source-review-r4-adjudication and source-review-r5-adjudication: shared pure classification/evaluation functions (P2-1), pure static assertions without host path probing (P3-1), hard-stop gate before snapshot and launchers mapping fixed-chain failure to BLOCKED_BY_FAILED_CHECKS exit 4 (P3-2 / R5-CX-03), shared runtime path exclusion guard (P3-3), error fidelity with HResult and linkTargetError (P3-5), and metadata alignment (R5-CX-01).'`
  → 同时引用 R4 与 R5 裁决；逐项对应 R4 裁决的 P2-1/P3-1..3/P3-5 与 R5 裁决的 R5-CX-01/R5-CX-03；**不再自称 "R4 repair"，不再引用 R3 裁决**。旧文本（R5 head 的 L1209）已消失。
- selftest 防倒退断言：**L250-254** `r601-revision-note-not-r4`（全文件不得匹配 `revisionNote\s*=\s*'R4 repair`，且不得含 `source-review-r3-adjudication`）与 `r601-revision-note-cites-r4-and-r5`（必须同时含 `source-review-r4-adjudication`、`source-review-r5-adjudication`）。若回退为旧轮次说明，两条断言同时失败 → 有判别力。执行事实一致（Codex 独立 log L77-78 PASS；Owner R6 log L83-84 PASS）。
- 未发现该断言与其它文本冲突（全文件无 `source-review-r3-adjudication`）。

### 2. R5-CX-03（链 FAIL → BLOCKED_BY_FAILED_CHECKS / exit 4，且硬停更早）— **PASS**
- 共用纯分类 helper：**L449-491** `Get-CollectorFailureClassification`（order：`OUTPUT_PRECHECK_FAILED*`→2/`BLOCKED_OUTPUT_PRECHECK` L459-464；`SOURCE_PIN_DRIFT*`→3/`BLOCKED_SOURCE_PIN_DRIFT` L465-470；`FIXED_PATH_CHAIN_CHECK_FAILED*` 或 `*Fixed path-chain validation failed*` 或 `blockedReasons` 含 `CHECK_FAIL:path-chain-fixed-paths`→4/`BLOCKED_BY_FAILED_CHECKS` L471-486；其余→5/`BLOCKED_EXCEPTION_FAIL_CLOSED` L487-490）。
- 生产 catch **确实调用**该 helper：**L1856-1858**（`-Message $message -BlockedReasons $script:BlockedReasons`），并在 **L1859** 追加 `EXCEPTION: <type>: <message>` → **原 CHECK_FAIL 与异常详情都保留在 `blockedReasons`**，未吞原因、未改 PASS。
- 硬停位置与顺序：链 observation **L1336-1366** → check **L1368-1373**（FAIL 时 L901 记入 `CHECK_FAIL:path-chain-fixed-paths`）→ **L1376** `Require $fixedChainsOk "FIXED_PATH_CHAIN_CHECK_FAILED: …"`，严格早于 H1 snapshot 读取 **L1379**、protected **L1388**、index-before **L1401**、pins **L1417-1429**、`tools-pwsh` 运行时探测（守卫 **L1446**、`File.Exists` **L1453**）、`git --version` **L1466**、`whoami` **L1500**。
- 其它退出码保持：output precheck exit 2（L1201-1212 触发）、source pin drift exit 3（L1427 触发）、普通未知异常 exit 5。
- selftest 全分支 + 反转负例（**L706-749**）：`r604-fixed-chain-msg-maps-to-exit-4`(L711-713)、`r604-fixed-chain-blocked-reason-maps-to-exit-4`(L716-718)、`r604-output-precheck-maps-to-exit-2`(L721-723)、`r604-source-pin-drift-maps-to-exit-3`(L726-728)、`r604-unknown-exception-maps-to-exit-5`(L731-733)，以及 4 条反转负例 `r604-reversal-*`(L735-749) —— 互换映射即失败，有判别力。另有 `r602-catch-calls-shared-classification`(L256-258) 与新增 `r603-fixed-chain-require-halts-before-runtime-pwsh-probe`(L260-264)。helper 经 `$requiredFunctions`（**L124**）从 collector AST 提取后由测试直接驱动 → 生产/测试共用同一实现。
- 逻辑复核：若同时存在 drift 与链 FAIL，drift 分支先命中（L465）→ exit 3，符合"特定消息优先"；链硬停紧随 check，不存在先执行 launcher 再判定的窗口。

### 3. R5-CX-02（Task Handoff pin）与 R6 identity/相互引用 — **PASS**
- Owner Task 的 R5 Handoff 行已修正：`doc/tasks/P02PRE-R1H-H2-COLLECTOR.md` **L91** `h2-r5-handoff` = `bee4e019a3e0c4437c0c38ed5df5772d7d376d2b7a8b357fb7a2875d87e4622b`（commit `6a59d82c`，class SOURCE_PIN），**L192** 明示 10,193 bytes。该值与 R5 独立核验记录 `source-review-r5-input-verification.json` **L105-110**（`manifestBytes=postBytes=10193`、`manifestSha256=postSha256=bee4e019…`）及 R5 裁决 L22 完全一致；旧的 `bc907f62…` 已不存在。
- R6 code/doc identity 与字段：manifest（L18/L20、L26/L28、L34/L36、L42/L44、L50/L52、L58/L60）与 R6 Handoff 表（**L23-26**）、Task canonical 行（**L82-86**）、Codex 独立核验 `codex-r6-independent-verification.json`（L20-31：bytes/sha256/gitBlob/gitBlobBytes；L5-10：code commit、docs head、worktreeClean）**四处一致**：collector 110261/`69dbe8ff…`/`482240df…`/108391；selftest 65874/`11737e6e…`/`af3df7dc…`/65050；Handoff 8275/`a3b096ee…`；logs `91a94e64…`/`f9b71f6f…`。
- **不混淆**：worktree bytes 与 git blob bytes 分列；我可独立复算的自洽性——`110261−108391=1870`（collector 行数）、`65874−65050=824`（selftest 行数），Handoff 8275/8275（LF 无差额）与 parser log 971/971 亦自洽。
- 相互引用正确：R6 parser log 头部写 `per source-review-r5-adjudication`（**L4**）；Handoff frontmatter `base_commit=6a59d82c`、`delivery_head=3e3fcae4`、`previous_delivery_head=b4936c35`（L5-7）；Task `delivery_head=3e3fcae4`（L18）、worktree 行（L114）一致。

### 4. R2/R3/R4/R5 既有闭合行为回归 — **PASS（未发现回归）**
只核对相关代码，未重做前轮研究：
- **CreateNew / fail-closed 输出路径**：纯字符串预检 L1202-1203 → `New-OutputPreflightCapture` L1206（函数体未变：L709-736，排除检查先于 FS）→ `Require` L1207-1212 → CreateNew **L1214** → post facts **L1216** → check pointer **L1321-1326**；冲突仍由 L1212（exit 2）或 L866 `FileMode.CreateNew`（走 catch → exit 5）fail-closed。唯一写通道仍是 `CreateNew + FileShare.None`（L866），全文件无其它写 API。
- **reparse / no-dereference**：`Test-PathAncestorsOrdinary` L609-707 未变（lstat leaf L639-650；真缺失 vs 查询错误 L659-671；祖先 reparse L687-689；nonDirectory L690-691）；probe L1115-1140 对 reparse leaf **只读 LinkTarget**、`Length` 仅在非 reparse 文件分支（L1131-1137）。
- **排除路径保护**：getter 入口 L958-960、helper 入口 L990、pin/probe/protected L1077/L1097/L1146、输出路径 L1202-1203、运行时 PSHOME L1446 + manifest L1267-1293 —— 均在访问前。
- **before-use guards**：链验证（L1336）→ 硬停（L1376）→ snapshot/读取/launcher（L1379 起）。
- **status argv/顺序、index-after-last**：status argv 仍 15 项且 `:(exclude).tmp.driveupload` 独立最后（L762-767）；`root-index-hash-after` 在最后子进程（L1726）与全部源文件读取（L1813）之后、close（L1846）之前（L1829-1844）。
- **raw evidence 保真**：`Split-NulRecords`/`ConvertTo-RawBytesRecord`（L240-314）无省略分支、NUL 计数/base64 完整；`Add-Check` 运行期指针解析（L888-903）；Gate 原值块（L188-199）与 `:(exclude).tmp.driveupload` 字面未变。

### 5. allowlist 与两项非阻塞限制的如实登记 — **PASS**
- R6 Handoff **L38-41** 明确列出并如实描述两项限制，且**均声明为保留/未修复**（"保留现状"、"保留此限制可见"），未说成 PASS 或已修：(1) null/null 分类输入 → 共享纯函数会抛异常并由外层 catch fail-closed，不会被伪装为 absence/PASS；(2) 链 helper 的 `LinkTarget` 可选读取异常细节不单独记录，但 reparse leaf 已先加入 `reparseComponents` 并导致 ordinary-chain 门控失败、在 launcher/snapshot 之前硬停、不解引用、不放行。两者与代码一致（probe 分类 L412-418 + L428；链 helper L651-657）。
- allowlist：R6 变更可静态确认落在 Owner Task 允许范围（两份 `tools/p02/*.ps1`、`doc/tasks/P02PRE-R1H-H2-COLLECTOR.md`、`verification/P02PRE-R1H-H2-COLLECTOR/` 的 Handoff 与 Parser/selftest 日志）；未见对 `verification/P02/`、frozen 输入或根仓库文件的写入。**限制**：无法在不使用 Git 的情况下枚举 commit 的完整文件清单（见 §未运行范围）。

### 6. 其它 P0–P3 发现
无 P0/P1/P2。见下方 2 项新 P3 与 2 项已接受限制。

### 7. 未运行范围 → 见末节

---

## Findings

**P3-1（测试未隔离 fallback 分支；Handoff 表述略宽）** — mapper 的 `blockedReasons`-only 回退分支（collector L473-480）未被单独驱动：selftest **L716-718** 传的 `-Message 'Fixed path-chain validation failed'` 本身即命中 `*Fixed path-chain validation failed*`（L472），因此该用例不能证明"仅凭 `CHECK_FAIL:path-chain-fixed-paths` 也能映射 exit 4"。Handoff **L35** 的"全分支覆盖"因此略有夸张。影响：仅为防御性冗余分支的覆盖声明，不影响生产映射（生产必然带 `FIXED_PATH_CHAIN_CHECK_FAILED` 前缀）。最小修复：在 selftest L706-749 增加一例中性消息 + 该 blocked reason（期望 4/`BLOCKED_BY_FAILED_CHECKS`）与一例中性消息 + 无关 reason（期望 5/`BLOCKED_EXCEPTION_FAIL_CLOSED`）。

**P3-2（静态断言作用域过宽，易误报）** — selftest **L251-252** `r601-revision-note-not-r4` 对**整个 collector 文本**要求不含 `source-review-r3-adjudication`。若后续轮次因历史注记需要在别处引用 R3 裁决，该断言会误报失败，而非检测 revisionNote 本身。最小修复：把断言收窄到 revisionNote 字面量（例如对该赋值做正则匹配），保留"不得自称 R4 repair"的核心判别力。

**P3-3（已裁决接受的非阻塞限制，登记用，无需动作）** — (a) `Get-PathProbeValueFromAttributes` 在 `Attributes` 与 `Exception` 皆 `$null` 时于 L428 抛错（生产不可达，且 fail-closed）；(b) `Test-PathAncestorsOrdinary` L651-657 读取 `LinkTarget` 的异常未单独记录（reparse 已分类并阻断）。两项已由 R5 Codex adjudication 第 4/5 条接受为非阻塞限制，R6 Handoff L38-41 如实登记且未声称为 PASS/已修复 —— 与本 reviewer 判断一致，不构成本轮新 finding。

---

## 未运行范围（明确）

- **未运行**：任何 PowerShell/pwsh 脚本、selftest、collector、getter、Git 子进程、registry/WER/ACL/profile/AppContainer 查询、executor、ProcessObserver/Toolhelp、Build/Cargo、AC1–AC7、Windows Sandbox。
- **未执行**：git blob / SHA-256 / byte count 复算与 `git status`（沙箱在启动阶段拒绝，一次尝试、未绕过）；因此上述数值的准确性来自 manifest + R6 Handoff + Owner Task + Codex 独立核验记录的**四处一致**，以及我做的行数—字节差自洽复算（1870、824 恰好等于文件行数），而非我本地重算。allowlist 的**完整 commit 文件清单**与"根仓库未被修改"亦无法由我核实（需 Git）。
- **未读取**：`dsh-source-review-r5.md` 全文（采用 R5 裁决对它的转述）、`repair-r6/` 的 Owner prompt、`r6-owner-input-manifest.json`、dispatch/stdout 元数据、Codex parser stderr（0 bytes）、R4 裁决以外的历史报告原文。
- **未访问**：`.tmp.driveupload` 子树（仅对虚构路径做纯字符串判定）。执行证据（Parser 0 errors、纯 selftest `196 PASS / 0 FAIL / 6 SKIP`、`collectorSha256=69DBE8FF…`，Owner 与 Codex 两次独立运行一致）仅作旁证，未替代源码审查。

---

## 结论与推荐下一步

R5 裁决的三项必修（**R5-CX-01** meta 说明、**R5-CX-02** Task Handoff pin、**R5-CX-03** 链 FAIL 的 disposition/exit 映射并在使用前硬停）均已在 `3e3fcae4` 真实闭合，且 R2-01..04、P4、R3-CX-02/03、R4 P2-1/P3-1..5、R5 P3-1..3 的行为无回归；两项非阻塞限制如实登记。**verdict = `APPROVED_STATIC_CONTENT`**，仅 2 项 P3（建议随下一轮或 Codex 收尾一并处理，不阻塞）。

**推荐下一步**：
1. **Codex /root**：在冻结 docs head `39ff1d3f`（code `3e3fcae4`）上做 pin pre/post 独立复算与 adjudication；如需，可将 P3-1（补 fallback 分支测试）、P3-2（收窄 r601 断言作用域）纳入同一 allowlist 的极小补丁，或明确登记为保留的测试面限制。
2. 本复审**不授权 live-run**；H2-RUN 仍为独立 `proposed` Task，须由 Codex 另行冻结 RunId 与 exact targets 后方可运行。Technical Gate `NOT_SATISFIED`、`private_registry_absence=UNPROVABLE`、Build Gate `BLOCKED`、Hard Build Barrier `EFFECTIVE`、Build/Cargo 与 AC1–AC7 `NOT_RUN`、v2 P2-1 `OPEN` 原值不变；本 evidence 不得用作 X6 S0。