# P02PRE-R1F Round 5 修复版 follow-up 独立只读 Review

## Decision

`CHANGES_REQUESTED`

## counts

`P0/P1/P2/P3 = 0/0/0/4`

核心结论：Round 5 首轮的 F1、F2、F3 三项实质修复（parent 目录可遍历、`$null` index mode 保留、危险路径形式先拒绝 + 只用 canonical relative 排除）在冻结字节上**静态成立**，F5、F6、F7（计数）、F8（argv 与文档限制）也已闭合；不存在 P0/P1/P2。剩余 4 项均为 P3：其中 R5F-F1 是 F4 类"陈旧 parser 轮次/目标"在 manifest 内的残留，且与 Codex adjudication 自称的"最终 parser 目标已统一为 R8"不完全相符，是本轮唯一与"修复是否完整"直接相关的开放项；其余 3 项为证据保真度、保护清单卫生与剩余路径别名类的诚实披露问题。四项均可窄修或由 Codex 明确 adjudicate 后释放 R8，不需重写候选。

---

## Findings

### R5F-F1 — P3 — `verification/P02/p02pre-r1f-manifest-20261011.md` L20（次要证据：`doc/tasks/P02PRE-R1F.md` L81、L91–L93）

**可复现原因**：manifest L20 最后一句仍写"…已更新为最终须先有 R4 follow-up=`APPROVED`，再对冻结 script 产生并核对 **R7** parser artifact"。但当前最终 parser 目标在三处已冻结为 R8：manifest L52（"store unique R8"）、Task L34（"以 …-r8-20261011.json 保存最终 R8"）、Task L43/L82/L94（"final parser 输出为 …-r8"、"final artifact target r8"）。因此同一 manifest 内部 L20 与 L52 对"最终 parser artifact"给出互相矛盾的答案，且 L20 把释放前提写成"R4 follow-up=APPROVED"，与当前释放链（Review Round 5 follow-up → Codex adjudication → R8）不一致。这正是首轮 F4 所指的"陈旧 R6 行"同类残留：Task L82 已修好，manifest L18 已改为 R8，但 L20 尾句未同步。另外 adjudication L17 自称"文中分别称 `Review Round 5` 与 parser R5–R8"，而 Task 表格 L81 以裸 `R5` 指 parser R5、L91–L93 以裸 `R5` 指 Review Round 5，命名区分并未落成该描述。

**最小修复**：把 L20 尾句改写为历史陈述并指向 R8，例如"…R4 时期的最终目标曾为 R7；R7 已作为旧候选历史 artifact 保留，当前最终 parser 目标见本 manifest Release procedure 的 R8"；同时把 Task L81/L91–L93 的轮次显式写成 `parser R5` / `Review Round 5`（或沿用 Task L34 的 "Round 5 首轮 Review" 写法），使 adjudication 的表述与字节一致。

### R5F-F2 — P3 — `verification/P02/p02pre-r1f-capture.ps1` L415（相关：L302、L130–L152）

**可复现原因**：manifest L39 要求 tracked symlink skip 记录必须逐项包含 `LinkType`，实现取 `linkType = [string]$item.LinkType`。该取值在冻结 child engine（Windows PowerShell 5.1.26100.9549，.NET Framework 运行时）上是否被稳定填充，本轮**无法判定**（我不运行命令）；而 `Assert-InventoryPolicySelfCheck`（L130–L152）与 self-check JSON 的 `selectedFunctions`（6 个纯函数）都没有构造任何 reparse 条目，因此该字段的填充与否**没有任何断言或证据覆盖**。若该属性在目标 engine 上不可用，`[string]$null` 会静默得到 `''`，最终 evidence JSON 会出现空的 `linkType`，既无 `NOT_AVAILABLE_ON_ENGINE` 之类标记，也不会触发任何 fail-stop——属于"记录字段存在但语义未证"的证据保真度问题（不涉及内容读取，安全性无变化）。

**最小修复**：加显式兜底与自述语义，例如
`linkType = if ($null -ne $item.PSObject.Properties['LinkType']) { [string]$item.LinkType } else { 'NOT_AVAILABLE_ON_ENGINE' }`，
或把"LinkType 未取得"记入 manifest L39 的限制；若坚持记录真实值，应由 Codex 在 pre-run 阶段对实际 `.codex/skills/ask-matt` 条目观测一次该字段后再释放 capture。

### R5F-F3 — P3 — `verification/P02/p02pre-r1f-capture.ps1` L659–L710 与 L714–L737

**可复现原因**：protected-hash 清单由两段拼接，第二段本意是"新增保护项"，但与第一段有 4 组完全重复的 key：L698–L701 与 L718–L721（`dsh-p02pre-r1f-review-r5-*` 四件）、L705 与 L716（`p02pre-r1f-r5-reviewfix-selfcheck-…json`）、L706–L709 与 L722–L725（`dsh-p02pre-r1f-review-r5-followup-*` 四件）、L710 与 L717（`p02pre-r1f-r5-adjudication-…md`）。后果是同一 artifact 被 `Get-FileRecord` 读取/哈希两次，且由于 OrderedDictionary 以同 key 覆盖，最终 evidence 记录的是**第二次**读取值；若两次读取之间文件发生变化（例如同目录下 wrapper 仍在写 `.exit`），记录值会与 Review 绑定的字节静默不一致，也不会触发任何断言或 fail-stop。

**最小修复**：哈希前先做去重（把两段合并为一个有序清单，或用 `[System.Collections.Generic.HashSet[string]]` 过滤重复），或显式说明第二段是"并集补充"并保持单次读取；重复项不改变"唯一写入仍是一次 `CreateNew`"的结论（L866、L15）。

### R5F-F4 — P3 — `verification/P02/p02pre-r1f-capture.ps1` L389–L399（相关文档：`p02pre-r1f-manifest-20261011.md` L38、`doc/tasks/P02PRE-R1F.md` L44）

**可复现原因**：修复后的排除链是纯字符串语义：L389 拒绝绝对/空/`.`/`..`/ADS/尾随点或空格段 → L390–L394 规范化 + repo boundary + canonical relative 一致性 → L395 用 canonical relative 匹配 `.tmp.driveupload` 前缀 → 之后才进入 L405 起的逐组件 `Get-Item`。该顺序对首轮 F3 列举的全部形式都正确，但 `[IO.Path]::GetFullPath` 不做 Win32 别名展开，因此仍存在一类未被冻结枚举覆盖、也不被任何文档声明为限制的别名：索引中若出现指向暂存目录的 8.3 短名（如 `TMPDRI~1/...`）等由文件系统解析的等价形式，字符串前缀不匹配而 `Get-Item`/`Get-FileHash` 会命中 `.tmp.driveupload` 内对象。触发需要构造 index 条目且卷上存在对应短名，可达性低；但 Task/manifest 的措辞是在**任何** per-candidate getter 之前排除，故这属于应显式声明的剩余风险，而不是已闭合的形式类（硬链接/junction 已被 manifest 的 hardlink/ADS 范围声明与 parent-reparse STOP 分别处置，不属本项）。

**最小修复**：沿用 F8 的诚实披露模式，在 manifest L38 与 Task L44 的 user-staging 段落加一句"排除基于规范化后的相对路径字符串；`GetFullPath` 不展开 8.3 短名等文件系统别名，本 Task 不对该类别名作 no-read 保证"；若确需闭合，应在 pre-run 阶段对候选实际路径做一次句柄级 real-path 核对（属新增范围，不建议在本轮扩大）。

---

## 重点 1–8 逐项结论

| # | 结论 | 证据范围（仅静态阅读） |
|---|---|---|
| 1 | `PASS` | `Get-InventoryAction` L123–L128 只在 `$IsLeaf` 时应用 `$IsContainer`/mode 限制；L125 的 `$IsReparsePoint` 分支对任意组件（含 parent）仍 STOP；L405–L424 调用点对非 leaf 仅拦截"非目录 parent"；断言 L132（tracked symlink 候选的 parent 因 leaf mode 不被误判）、L133（普通 parent 目录可继续）、L134（leaf 目录 stop）、L135/L136（reparse leaf stop）与实现一致。首轮 P1（深层路径必然 fail-stop）已消除。未在 host 上执行 |
| 2 | `PASS` | L123 形参为 `[object]$GitMode`，调用点 L412 显式 `else { $null }`，L126 用 `$null -ne $GitMode` 守卫；无 index mode 的 untracked regular leaf → `HASH_REGULAR_FILE`（断言 L137），untracked reparse leaf → STOP（L136），reparse/directory/`160000`/mode-不符 → STOP（L125/L126、L135/L138/L139）；manifest L40、Task L47 已把"untracked regular leaf 允许 hash"写成明文，消除首轮 F2 的未声明行为歧义。限定：untracked **directory** leaf 的 STOP 未单列断言（逻辑上由 L125 无条件成立） |
| 3 | `PASS` | L111–L117 先拒绝空/绝对/`.`/`..`/含 `:`/尾随点/尾随空格/空段（含重复分隔符）；L390–L394 再做分隔符规范化、`OrdinalIgnoreCase` 边界检查（`$rootFull` 带尾随 `\`，L382，不会误匹配 `New MangaXYZ`）、canonical relative 与规范输入一致性校验；L395 是第一个（也是唯一）暂存排除判定，位于 L405 起任何 per-candidate `Get-Item`/`Get-FileHash` 之前；大小写由 OrdinalIgnoreCase 与 L146 断言覆盖，`/` 与 `\` 两侧都处理。断言 L141–L144 覆盖 reviewer 给出的三种别名 + ADS + 越界 + 空段 |
| 4 | `FAIL` | F5 部分已闭合：Task L38/L89 与 manifest L11 精确写出首次 wrapper failure 绑定替换前 source `60662 / AA99D7C4…A884`、注明"在 parse/self-check 前退出、harness failure、不是脚本 parse/自检失败"，artifact 原样保留 → `PASS`。F4 部分未闭合：manifest L20 仍把 R7 写成最终 parser 目标且把前提写成 R4 follow-up，与 manifest L52 / Task L34 / L43 / L82 / L94 的 R8 冲突 → `FAIL`，见 R5F-F1 |
| 5 | `PASS`（含一处 UNPROVEN 子项） | L302 的 repository 初值已含 `errorOperation = $null; error = $null`，成功与失败路径（含 L307/L315/L320/L324/L332/L342/L364/L369/L378/L433/L444/L448）的 record 都带这两个键，`Get-PartialRepository` L534–L546 也一致；env 清单 L619 我逐项点数为 **35**，与 manifest L8"35 个环境变量"一致，且 `summary.environmentVariables = $envNames.Count`（L826）。UNPROVEN 子项：与固定 R1 manifest 的**逐项名称/顺序**对账超出本轮授权读取范围（R1 manifest 不在输入清单内），只能采信 adjudication L20 的 Codex 结论 |
| 6 | `PASS` | L343 的 `status` argv 与 manifest L25 逐字一致（含 `-- . :(exclude).tmp.driveupload`）；manifest L25/L38 与 Task L44 都显式写明"Git status 内部访问未做 OS 级监测 / pathspec 只是命令参数证据，不是 OS 级 no-read 证明"，未夸大（且 L831 排除数非零时判 `UNPROVABLE`）。限定：adjudication L21 的 main=`701 records / 44443 bytes`、stderr=0、`.git/index` 前后 SHA 等**运行证据属 Codex 提供**，我未复现。次要注意：evidence 内 `repositoryProtectedInventoryNote`（L832）只陈述脚本自身"未 open/hash"，未复述同一段 Git-internals 边界；L39/L829 的 `…_NOT_MONITORED_IN_R1F` 分类仍在，故不单独列为 finding |
| 7 | `PASS` | L659–L740 清单在本次读取中可逐条枚举（首轮 L639 被截断的问题不再存在）；`.tmp.driveupload` 之外的四组目标均在保护内：新 self-check（L705）、Round 5 首轮 Review 四件（L698–L701）、Round 5 follow-up Review 四件（L706–L709）、`p02pre-r1f-r5-adjudication`（L710）、R8 artifact `…-r8-20261011.json`（L715）；列表本身不含正在创建的 `p02pre-r1f-evidence-20261011.json`（正确，否则会 ABSENT fail-stop）。唯一写入仍为 L866 的一次 `FileMode.CreateNew` 单次写，L15 预先拒绝已存在目标；Git 以 `--no-optional-locks` + 关闭 fsmonitor/untrackedCache 运行（L91），无 transcript/temp/log 写入。卫生问题见 R5F-F3 |
| 8 | `PASS` | pins 在三份冻结文件间字面自洽（script `64626 / 83C0…8E91`、self-check `2694 / F2FCE…7FE39F`：Task L38/L92、manifest L14、self-check JSON L5–L6 一致）；自检 engine 归属正确（child=`Windows PowerShell 5.1.26100.9549` 为执行断言的引擎，parent=`7.6.6` 仅编排；adjudication L26 与 Task L38 未互相误称）；self-check 被反复标注"不是独立 Review 或 Gate PASS"（manifest L14/L19、adjudication L8/L27、Task L42/L51）；状态处处为 `capture=BLOCKED / NOT_RUN`、`READY / DISPATCH_PENDING`、`Build/Cargo=NOT_RUN`、`AC1–AC7=BLOCKED/NOT_RUN`（Task L38/L93/L95/L96），未暗示 capture 已运行；Gate 状态（L98）未被改写。限定：isolated self-check 只覆盖 6 个纯函数，不含 `Get-GitNulPaths`/`Get-GitIndexModes`/`Assert-InventoryParserSelfCheck`/`Get-RepositoryRecord`，该覆盖边界应视为该自检的证据上限（脚本自身在 L580–L582 于任何 getter 前仍会执行三个内存自检） |

## 首轮 F1–F8 关闭状态（供对照，不替代 Codex 裁定）

| 首轮 finding | 本轮判定 | 依据 |
|---|---|---|
| F1 (P1) parent 目录被误判 | `CLOSED` | L123–L128、L405–L424、断言 L132–L135 |
| F2 (P2) `$null` 被 `[string]` 归一 | `CLOSED` | L123 `[object]`、L412–L413、断言 L136–L137、manifest L40 / Task L47 |
| F3 (P2) 路径形式绕过排除 | `CLOSED`（限冻结枚举形式） | L111–L117、L389–L399、断言 L141–L144；剩余别名类见 R5F-F4 |
| F4 (P3) 陈旧 parser final r6 | `PARTIAL` | Task L82 已改 r8；manifest L20 仍写 R7 → R5F-F1 |
| F5 (P3) wrapper failure 未标源 pins | `CLOSED` | Task L38/L89、manifest L11 |
| F6 (P3) 成功 record 缺 error keys | `CLOSED` | L302、L534–L546 |
| F7 (P3) 环境变量计数 | `CLOSED`（计数 35/35） | manifest L8、L619、L826；逐项 R1 对账 UNPROVEN |
| F8 (P3) status 先于排除 + 边界表述 | `CLOSED`（argv + 文档诚实性） | L343、manifest L25/L38、Task L44；运行证据为 Codex 提供 |

## 证据范围与声明

- 我只阅读了本次给定的 6 个文件：`doc/tasks/P02PRE-R1F.md`、`verification/P02/p02pre-r1f-manifest-20261011.md`、`verification/P02/p02pre-r1f-capture.ps1`（881 行）、`verification/P02/p02pre-r1f-r5-reviewfix-selfcheck-20261011.json`、`verification/P02/dsh-p02pre-r1f-review-r5-20261011.stdout.md`、`verification/P02/p02pre-r1f-r5-adjudication-20261011.md`。**未创建、修改或删除任何文件**，未写共享仓库，未访问 `.tmp.driveupload` 内容或其 metadata，未运行 capture 脚本、任何 host getter、registry 或 ACL API。
- **如实披露一处越界尝试**：本 Review 开始时我尝试执行过一条仅用于核对文件 bytes/SHA 的只读命令（`Get-ChildItem` + `Get-FileHash`），被 DSH 文件沙箱在授权阶段以 `SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)` 拒绝，**未产生任何输出、未读写任何文件**；此后未再运行任何命令。因此：所有 bytes/SHA 只按**字面值**核对，独立复算必须由 Codex 在 adjudication 中用 `Get-FileHash` 完成 → 该子项 `UNPROVEN`。
- 未打开 `p02pre-r1f-r1-manifest-20261011.md`（不在授权读取清单内），R1 继承 allowlist（12 input roots / 13 output leaves / 3 canary / 35 环境变量逐项名称 / 保护文件集合逐项等价）只能核对形态与计数，**不能**核对逐项一致 → 该子项 `UNPROVEN`（并据此限定重点 5 的结论）。
- 所有 F1–F8 修复结论均为纯静态代码/文档语义推演，**尚未在 host 上执行验证**；R5F-F2 的 `LinkType` 可用性亦属未证事项，需 Codex 在 pre-run 阶段观测或加兜底。
- 本 Review（以及被审的 Codex isolated self-check）**不是** P02PRE Gate、Technical Gate 或 Build Gate 的 PASS，也不改变 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`。
- 本 Review **不能替代、也不建议跳过** Windows PowerShell 5.1（`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`）对同一冻结 script bytes 的 `ScriptBlock::Create` parse-only R8，亦不能替代 Codex pre-run adjudication 与 post-run 五态裁定。

## 推荐下一步

1. Codex（作者）对 R5F-F1 做窄修（manifest L20 的 R7/前提句 + Task L81/L91–L93 轮次命名），并对 R5F-F2、R5F-F3、R5F-F4 分别选择"窄修"或"adjudicate 后以明文限制接受"；F1–F3、F5–F8 无需改动。
2. 修复/裁定产生新的 exact bytes 后重新冻结 Task/manifest/script/self-check（或只冻结文档变更后的 Task/manifest）pins，并派发一次非作者只读 follow-up Review；在该 follow-up=`APPROVED` 且 Codex 完成 pin 核对之前，不产生 R8、不释放 capture。
3. 之后依次执行：Windows PowerShell 5.1 parse-only R8（`captureScriptInvoked=false`，落 `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r8-20261011.json`）→ Codex pre-run adjudication（pins、身份/SID、main/scratch roots 与 refs、输出目标 absent、status/index 稳定、路径范围、保护文件基线）→ 仅在全部匹配时按 manifest 的 exact argv 运行**一次** capture；任何 mismatch 一律保留原始 partial evidence 并停止，不重试、不清理。
