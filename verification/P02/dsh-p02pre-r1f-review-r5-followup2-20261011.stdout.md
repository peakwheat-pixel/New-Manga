# P02PRE-R1F Review Round 5 follow-up #2 独立只读 Review

## Decision

`CHANGES_REQUESTED`

## counts

`P0/P1/P2/P3 = 0 / 0 / 1 / 1`

核心结论：R5F-F1、R5F-F2、R5F-F4 三项已按 follow-up #1 的窄修要求闭合；R5F-F3 的**实质修复**（去重、单次读取）成立，但其**数字见证**不成立。另有一项与 protected-file/hash baseline 直接相关的条件性 P2：脚本把 pinned 证据明确记载“未创建”的 self-check 目标纳入 protected 清单，而脚本对任何非 `PRESENT` 记录一律置 stopReason，会消耗唯一一次 `CreateNew` capture。两项均可窄修，不需要重写候选主体。

---

## Findings

### R5F2-F1 — P2（条件性，静态证据判定）— protected 清单含“从未创建”的目标，会使唯一一次 capture 必然 stop

**可复现原因**：`verification/P02/p02pre-r1f-capture.ps1` L722 的 protected-hash 第一数组包含
`'verification/P02/p02pre-r1f-r5-followupfix-selfcheck-20261011.json'`。
但同一批 pinned 输入之一 `p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md` 末段明确写：*“The unique self-check result target `p02pre-r1f-r5-followupfix-selfcheck-20261011.json` was **not created**.”* 失败的 attempt #1 只留下该 md；成功产物被记为新目标 `…r5-followupfix2-selfcheck-20261011.json`（manifest L17、Task L94，均有 bytes/SHA pin）。manifest 对 `r5-selfcheck`（L11）、`r5-selfcheck-retry`（L12）、`r5-reviewfix-selfcheck`（L14）、`r5-followupfix2-selfcheck`（L17）都给了 pin，唯独**没有**任何 `p02pre-r1f-r5-followupfix-selfcheck-20261011.json` 的存在证据；Task 只在 L55 把它列为“可写路径”，没有任何 evidence 行。

脚本逻辑使该差异成为硬停止：`Get-FileRecord` 对不存在的路径返回 `state='ABSENT'`（L254–L258）→ `$invalidHashCount = @($hashRecords | Where-Object { $_.state -ne 'PRESENT' }).Count`（L795）→ summary 记 `invalidProtectedHashRecords`（L817）→ L848 置 `stopReason='QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE'` → L888 `throw`。而 evidence 已在 L874 用 `FileMode::CreateNew` 写出，Task L71 规定“任何 mismatch/error 保留原始 partial evidence 并停止；不得重试或清理”——即唯一授权的 capture 会被这一次 ABSENT 消耗掉。唯一的缓解是 manifest L57 要求的 Codex pre-run “protected-file baseline” 核对；但见 R5F2-F2，该核对所依据的计数本身就是错的。

**证据**：script L722、L795、L817、L848、L874、L888；wrapper-attempt1 md 末段；manifest L11/L12/L14/L16/L17；Task L55/L71/L94。**边界**：本轮为只读静态审查，我不做存在性探测（不 `Test-Path`、不列目录），因此该 find 以“pinned 证据为真”为前提；若 Codex 在 pre-run 能证明该文件确实存在，本项即降级为文档一致性问题，但 R5F2-F2 仍然成立。

**最小修复**：Codex 在 pre-run adjudication 中显式核对全部 protected 路径存在性；把从未创建的 `p02pre-r1f-r5-followupfix-selfcheck-20261011.json` 从清单移除（它不是冻结证据集的一部分），或为“已退役但允许缺失”的路径引入独立、已声明的非阻塞状态；改后重冻结 script pin 并重新走 follow-up 流程。

### R5F2-F2 — P3 — “63 keys / 63 unique” 与冻结脚本字节不符（实为 72）

**可复现原因**：Task L38 写“protected-hash keys static recount=`63/63 unique`”，manifest L17 写“Codex static protected-hash path recount=`63 keys / 63 unique / 0 duplicates`”，adjudication L21 写“Codex 对 script 内两数组做静态路径计数：`63 keys / 63 unique / 0 duplicates`”。对同一冻结脚本做只读内容枚举：两个 `foreach ($key in @( … ))` 块共 **72** 条带引号路径字面量——L670–L728 共 59 条、L733–L745 共 13 条——且 72 条互不相同（0 duplicates）。第一数组 59 条与第二数组 13 条之间无交集（r4/r8 仅在第二数组，r1/r2/r3/r5/followup/followup2 仅在第一数组），follow-up #1 指出的 10 个重复 key 确实已消失。也就是说：**去重修复成立，但三个文档引用的数字是错的（差 9）**。这与 F3 所要求的“清单卫生 + 诚实计数”直接相关，并且会削弱 manifest L57 要求的 protected-baseline 核对（若 pre-run 以 63 为基准，可能漏查 9 条、其中包含 R5F2-F1 的 ABSENT 路径）。

**证据**：`grep -c` 语义的枚举结果（72 条匹配，均位于 L670–L745 两个数组内，脚本内无其他同类字面量）；script L669–L729、L732–L746；Task L38；manifest L17；adjudication L21。数字为人工静态清点，未执行任何命令。

**最小修复**：重新清点并把三处数字改为 72/72（或写明计数口径），pre-run baseline 核对使用改后数字；同时据此核对全部 72 条是否 `PRESENT`。

---

## R5F-F1–R5F-F4 四行 disposition

| Finding | 本轮判定 | 依据与边界 |
|---|---|---|
| R5F-F1（陈旧 parser 轮次/命名） | `CLOSED` | manifest L23 已把 R6/R7 写成历史、把 R8 定为“当前最终候选唯一所需 artifact”，L57 Release procedure 同口径；Task L81 显式写 `parser R5`，L91–L95 显式写 `Review Round 5 …`，L34/L43/L82/L94/L97 均指向 r8。未再发现 L20 那类“R7 为最终目标 / R4 follow-up 释放”的矛盾句。非阻塞残留：manifest L21 的现在时 “is repairing” 与 L23 的 “本行最后句仍引用 R6” 属历史叙述残留，不重建 R5/Round-5 歧义 |
| R5F-F2（`LinkType` 缺失/空值） | `CLOSED` | `Get-LinkTypeEvidence`（L119–L123）对属性缺失或空值统一返回 `NOT_AVAILABLE_ON_ENGINE`，非空值原样返回；调用点 L425 位于 `SKIP_TRACKED_SYMLINK` 分支内，L429–L430 立即 `break`，其后无任何 target 的 `Get-*`/hash/ACL；内存断言 L152–L154 覆盖“非空 / 缺失 / 空串”三态。边界：child engine 上 `LinkType` 的真实可用性与实际取值属 host 观测，本轮未执行、未验证 |
| R5F-F3（重复 key / 重复读取） | `CLOSED`（实质）/ 见证数字有误 → R5F2-F2 | 两个数组 72 条全部唯一，同一 artifact 不再被 `Get-FileRecord` 读两次；follow-up #1 点名的 4 组重复（r5 review 四件、r5-reviewfix-selfcheck、r5-followup 四件、r5-adjudication）均已消除。唯一问题是三份文档自报的 `63 keys / 63 unique` 与字节不符 |
| R5F-F4（DOS 8.3 alias 需在 getter 前停止） | `CLOSED` | `Test-SafeRepositoryRelativePath` L114 对任一含 `~[0-9]` 的组件返回 `$false`；调用点 L399 早于第一次 per-candidate `Get-Item`（L419）与 `Get-FileHash`（L437）；断言 L151 覆盖 `TMPDRI~1/183728`；manifest L41 与 Task L44 写明该拒绝与“保守边界”（合法名字含同模式也会安全停止）。边界：`GetFullPath` 不展开 8.3 的根因已由模式拒绝覆盖；hardlink/ADS/瞬时访问闭包仍按 manifest L47 明确声明为范围外 |

---

## 独立检查项（超出四项 finding 的要求）

| 检查项 | 结论 | 依据 |
|---|---|---|
| surrounding call order | `PASS`（静态） | L15 evidence target 不存在检查 → L17–L18 T0 → L590–L592 三个纯内存 self-check（先于任何 getter）→ 身份（L593–L616）→ main（L619）→ scratch（L624）→ env/paths/WER（L629–L668）→ protected hashes（L669–L748）→ ACL 端点对比（L749–L779）→ summary → 单次写入（L874）。与 manifest 的 T0/停止顺序一致 |
| Windows PowerShell 5.1 语法兼容 | `PASS`（静态；仍需 R8） | 未发现 PS7-only 构造：无 `??`、无三元 `? :`、无 `-Parallel`；使用的 `::new()`、`-in/-notin`、`[ordered]@{}`、`[pscustomobject][ordered]@{}`、`$segments[-1]`、`Flush($true)`、`CopyToAsync/GetAwaiter().GetResult()`、`RegistryKey::OpenBaseKey`、`Get-FileHash` 均在 5.1 可用；`catch [System.IO.IOException]` 与 `GetValueKind` 缺失值的语义匹配。**未执行**，parse-only R8 仍需按 AC L43 产出 |
| `.tmp.driveupload` no-content-read 边界 | `PASS`（静态） | 先 `Test-SafeRepositoryRelativePath`（L399，含 `~[0-9]`）→ 分隔符规范化 + `OrdinalIgnoreCase` repo-boundary（L401–L402）→ canonical relative 一致性（L403–L404）→ 唯一的 staging 判定（L405–L410，`continue`）→ 才进入 L419 起的逐组件 `Get-Item` 与 L437 hash；`status` argv 亦排除该子树（L353）；只记 `unreadUserDataCount`/`firstUnreadUserDataPath`。Git 内部访问未被 OS 级监测的限制在 manifest L28/L38、Task L44 有明文，未夸大 |
| protected-file/hash baseline | `CHANGES_REQUESTED` 源 | 见 R5F2-F1、R5F2-F2：72 条字面量 vs 自报 63；其中一条被 pinned 证据判定未创建，且脚本对非 `PRESENT` 一律停止 |
| 唯一 `CreateNew` 输出 | `PASS`（静态） | L15 预检 + L874 `FileMode::CreateNew`/`FileAccess::Write`/`FileShare::None`；脚本内无 append/覆盖/临时文件；registry 为 `OpenSubKey(..., $false)`、`Get-Acl` 只读；无 profile/canary 写；>64 MiB 时仍写同一目标（L864–L872） |
| 子进程 / 写入范围 | `PASS`（静态） | 子进程仅 `whoami.exe /all`（L603）与 5 次固定 git 调用（L335/L337/L353/L367/L369），`Invoke-Git` 前缀固定 `--no-optional-locks -c core.quotepath=false … -C <root>`（L91）；无 shell/网络/compiler/COM |
| R8 parse 与 pre-run 序列描述 | `PASS`（文字自洽） | Task L34/L43/L65/L96–L98 与 manifest L57 一致：follow-up #2=`APPROVED` → Codex adjudication → 对同一组冻结 script bytes 做 5.1 `ScriptBlock::Create` parse-only、落唯一 `…-r8-20261011.json`（`captureScriptInvoked=false`）→ Codex pre-run adjudication（pins、身份/SID/token、main/scratch roots/refs、输出目标 absent、status/index 稳定、路径范围、protected baseline）→ 才允许 manifest exact argv 运行一次。Task L68 的 argv 与 manifest L27 逐字一致，无矛盾 |

---

## 证据边界与未决限制（明示）

1. **未复算 bytes/SHA**：本轮禁止执行命令，故七份 pin 的 `bytes / SHA-256` 只做**字面一致性**核对（Task L38、manifest L17、self-check JSON L5–L6、adjudication L26–L29 相互一致），独立复算为 `UNPROVEN`，须由 Codex 在 adjudication 中用 `Get-FileHash` 完成。
2. **R1 继承清单未对账**：12 个 input roots、13 个 output leaves、3 个 canary、35 个环境变量、getter 顺序、protected 集合与 R1 manifest 的逐项等价性，因 R1 manifest 不在本次七文件授权范围内，`UNPROVEN`（仅核对了 35 的计数与形态，见 script L629；并与 follow-up #1 的 UNPROVEN 结论一致）。
3. **host 行为未观测**：`LinkType` 在 `5.1.26100.9549` 上的可用性与取值、`.tmp.driveupload` 实际候选数、72 条 protected 路径的实际存在性（尤其 R5F2-F1 那一项）均未执行验证。
4. **self-check 属 Codex 自有产物**：`p02pre-r1f-r5-followupfix2-selfcheck-20261011.json` 的 `PARSE_OK / 7 pure functions PASS` 来自 Codex 的隔离自检，本轮只核对其字段与 pin 的自洽（含 base64 child stdout 的解码内容自洽），**不是**独立验证，也不是 Gate PASS。
5. 我未打开 R1 manifest、R1 script/evidence、任何 parser artifact 或仓库其他文件；未读取 `.tmp.driveupload` 内容或 metadata（连目录列举也未做）。
6. 本 Review 为**纯静态**结论，不替代 R8 parse-only、Codex pre-run adjudication、post-run 五态裁定。

---

## 我执行了什么 / 未执行什么

- **读取**：仅本次给定的七份文件，且全部读毕（Task 101 行、manifest 57 行、script 889 行、self-check JSON 42 行、adjudication 38 行、prior Review 84 行、wrapper-attempt1 11 行）；另对其中 script/Task/manifest 三份文件做了**内容检索**（grep）以清点 72 条 protected 字面量与 `63`/`followupfix-selfcheck` 引用——检索对象仍只在这七份文件内。
- **未执行**：没有运行任何命令、脚本、测试、capture、host getter、registry/ACL API；没有 `Get-FileHash`/`Test-Path`/`Get-ChildItem`/`glob` 等文件系统探测；没有创建、修改、删除或移动任何文件；没有写共享仓库；没有读取 `.tmp.driveupload` 内容或 metadata；没有复算 hash/字节数。
- **不改写**：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE` 一律不变；isolated self-check、本 Review 与既有 owner waiver 都**不是** Gate PASS。

---

## 非阻塞观察（不单独计为 finding）

1. manifest L47 要求排除/跳过时“以单独 note 说明跳过数量/原因”，而 script L840 仅 symlink 跳过的分支字符串只陈述原因、未含 `$repoSymlinkSkipCount`（含 unread 的分支则带计数）。按 R1 preflight（每仓 2148 条 staging 候选），实际大概率走“两者皆非零”的分支，故 materiality 低；建议顺手补上计数或在 manifest 收窄措辞。
2. self-check JSON 的 `childArguments` 只有 `-EncodedCommand`，没有 stdin 相关字段，因此 Task L38/manifest/adjudication 所述“改用 redirected stdin”这一机制在 pinned artifact 内**未被直接见证**（若为“短 bootstrap 走 -EncodedCommand、source 走 stdin”则两者可并存）。属证据粒度问题，不影响 hash 一致性的结论。
3. `Get-GitIndexModes`（L201）对同 path 不同 stage（merge 冲突的 1/2/3）也 fail-stop；manifest 只明文要求“仅大小写不同的碰撞 fail-stop”。这是更保守的额外 fail-stop，未违反安全边界，但未被文档覆盖。

---

## 推荐下一步

1. Codex 先做两项窄修：**(a)** 核对并从 protected 清单移除/退役 `p02pre-r1f-r5-followupfix-selfcheck-20261011.json`（或证明其存在），并确认 72 条全部 `PRESENT`；**(b)** 将 Task L38、manifest L17、adjudication L21 的 `63 keys / 63 unique` 更正为按字节清点的数字（72/72）。可选：补 manifest L47 要求的 symlink-only note 计数。
2. 修后重冻结 script/Task/manifest pins，再派发一次非作者只读 follow-up（#3）；在 follow-up=`APPROVED` 且 Codex 完成 pin 核对之前，**不产生 R8、不释放 capture**。
3. 之后依次执行：Windows PowerShell 5.1 parse-only R8（`captureScriptInvoked=false`）→ Codex pre-run adjudication（pins、身份/SID、roots/refs、输出目标 absent、status/index 稳定、路径范围、**protected baseline 逐条存在性**）→ 仅在全部匹配时按 manifest exact argv 运行一次 capture；任何 mismatch 保留原始 partial evidence 并停止，不重试、不清理。

本次 `CHANGES_REQUESTED`；未对任何候选字节给出批准，也不授权 R8、capture、Build/Cargo、AC1–AC7 或任何 Gate PASS。
