## P02PRE-R1H-R6-EXEC-A5 非作者独立静态 Review（exact pinned inputs）

### 1) 独立 hash 校验状态（先声明限制）

**无法完成任何 SHA-256/bytes 独立校验。** 本环境中所有宿主编排调用（`pwsh -Command`，仅用于 `Get-FileHash` 只读计算）在命令执行前即失败：`Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`；`sandbox_permissions=danger-full-access` 重试亦被拒（无 approval channel）。因此以下**全部未经校验**：

- 12 个 pinned input 的 `bytes`/`sha256`（manifest `inputs[]`，第 13–24 行）；
- `candidateBase` 的 `head`/`tree`（需 Git 对象解析，未执行 Git）；
- `.git/index` 的 `C5CA8884…2B68`（未读取该文件）。

我对 attempt4 与 attempt5 的连接只能做到**内容等价性比对**（line-by-line principal anchors），不能做字节/diff 计算。pins 中 attempt5 执行器 `43464 bytes` 与 attempt4 相同，且我定位到 6 处语义变化、估约 +34 bytes（`attempt-4→5` 与 `attempt4→5` 各 2 处、两个 40 位 hash 各 +1、`round6-attempt4`→`round6-attempt5` +1），如实测字节不是 43464 则说明我未发现的变更存在——该点必须由 Codex 复算闭合。

### 2) 逐问结论

**Q1 — attempt5 vs attempt4 executor：通过（内容层面）。** 两文件均为 638 行，逐区间比对后仅见 6 处语义差异：`...attempt5-20261012.ps1:1` 头注释（attempt4→5 与 attempt-4→attempt-5）、`:34` `schema='P02PRE-R1H-round6-attempt5'`、`:26` `$IndexHash='C5CA8884…2B68'`、`:366` root expectedHead=`343895fb…7607`、`:367` root expectedTree=`e12bd6…ec63`、`:623` FAILURE 注释 attempt4→attempt5。其余全部逐行一致，含 `:7` Owner worktree、`:365` Owner branch、`:366-367` Owner HEAD/tree、`:373` Owner parent `dd5d2e3bc8e…`、`:6/:8/:9` root/pwsh/git 绝对路径、`:11-21` 路径表与 `$NewKeys`、`:22-25` 四个候选 hash、`:27` ACL SDDL、`:60-477` 全部函数体、`:480-638` 全部执行/失败逻辑。**Owner 分支/HEAD/tree pin 与全部执行逻辑未变；`$OldHash/$NewHash/$CaptureHash/$HandoffHash/$ExpectedSddl` 未变。** 用户所列三项变更与第 6 处失败标签变更均在位，未发现额外变更。

**Q2 — attempt5 protocol/Handoff：通过（含 1 项 P2 元数据项）。** attempt5 protocol 固定继承 attempt4 protocol 路径与 hash（`:11`），并把 attempt4 的过期 root 绑定（`cddff584…` / `c25d051a…` / `214767…`，见 attempt4 protocol `:17`、attempt4 executor `:26/:366/:367`）替换为 A4 集成后的 `343895fb…` / `e12bd627…` / `C5CA…`；未发现残留 attempt4 root 基线，仅在 `:15` 把 attempt4 未调用正确描述为 precondition BLOCKED（非 test failure）。Handoff `:7`、`:4`、`:6`、`:10-11` 对 A4 集成与本轮 6 项变更的描述与源码一致；`doc/tasks/P02PRE-R1H.md:287` 的 A5 描述（仅更新 main/index 绑定）与实现一致。未新增权限、路径、API、子进程或恢复行为（见 Q3）。唯一缺口：pins JSON 未声明 checkpoint 是否在输入 pin 集内（P2-002）。

**Q3 — 冻结写入边界：通过。** 单次三参数 `File.Replace` 唯一 destination＝`verification/P02/p02pre-r1h-selfcheck.ps1`（`:543`，仅此一次调用，`$ReplaceCalls++` 于 `:542`）；7 个 `CreateNew` 新路径＝stage/recovery/handoff（`:514-516`）、execution（`:493`）、selfcheckEvidence（`:570/:581`）、engineEvidence（`:594`），共 8 个 executor-owned 写入路径，与 Task（`doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:31`、`:42-44`、`:46`）一致；`AssertAbsent`/`AssertWriteSafe` 先于每次创建。仅两个精确 validation child：`-NoLogo -NoProfile -NonInteractive -File verification/P02/p02pre-r1h-selfcheck.ps1`（`:574`）与 `-Command $query` capability 查询（`:583-584`），CWD 均为 root、映像均为固定 pwsh（`:277-278`）；Git 仅固定 `C:\Program Files\Git\cmd\git.exe`（`:9`），argv 经 `ArgumentList` 逐项传入（`:285`）且无 `-C`/shell/pager/hooks（`:346`）。无 Build/Cargo、无 system AC、无 R1H capture、无 getter/AppContainer/profile/registry/ACL 写入（`Get-Acl`/`Get-Item -Stream` 为只读）、无 Sandbox；无 retry/cleanup/rollback/delete/kill/timeout（`:339`、catch `:609-635`、finally `:636-638`）。

**Q4 — 停止条件/冲突/S0–S3/闭包/哈希/ACL/streams/status/Gate：通过。** S0-root→S0-owner→pre-stage-owner→S1→(re-pin)→REPLACE→S2→VALIDATION→S3（`:495-608`）与 protocol §4 八步一一对应；`AssertDelta` 期望集合精确为 S1 的 stage+recovery+handoff、S2 的 recovery+apiBackup+handoff、S3 的 selfcheckEvidence+engineEvidence（`:519`、`:560`、`:598`）；status argv 含独立末位 pathspec `:(exclude).tmp.driveupload`（`:390`）且 `AssertChain` 拒绝该路径（`:87`）；输出冲突即 `throw "Output collision"`（`:110`），`check-ignore` 逐项 exit=1（`:487`）；进程闭包以 `WaitAll(…,5000)` + `KnownChildren`/PID 归属校验 fail-closed（`:309-312`、`:253-258`）；index/ACL/streams 前后复算（`:384-385`、`:437/:539/:557-559`、`:600-605`）；Gate 值 `:40-47` 与 Task `:68`、manifest `:41-42`、protocol `:87-95` 完全一致，`NOT_RUN/NOT_VERIFIED/NOT_SATISFIED/UNPROVABLE/BLOCKED` 未被提升为 PASS。

**Q5 — A4 集成后基线更新是否引入 blocker：未引入内容型 blocker。** `verification/P02/codex-p02pre-r1h-attempt4-integration-verify-20261012.json:9/:13/:101` 记录 integrated `343895fb…7607`、tree `e12bd627…ec63`，与 attempt5 root pin 及 executor `:366-367` 一致；`p02pre-r1h-attempt4-review-adjudication-20261012.md:6/:25` 记录 A4 owner lineage 与同一 tree。因此跳变来源可归因，不是矛盾。`depends_on`/base/allowlist 与 A4（`doc/tasks/P02PRE-R1H-R6-EXEC-A4.md:11-12`、`:48-57`）一致，8 路径 allowlist 未被扩大。唯一“新引入”的风险不是基线值本身，而是**我无法复核该基线**（P2-001），以及前次沙箱 ACL 变更尝试可能已扰动 root 工作区安全描述符，需在 final pre-run 以只读方式再证（P2-001 的处置项）。

### 3) Findings

| ID | 级别 | 精确 pin 路径 / 行 | 影响 | 要求修正 |
|---|---|---|---|---|
| P2-001 | P2 | `verification/P02/codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json:13-24`（12 输入）、`:8-10`（head/tree/indexSha256） | 本环境无法 hash；Task AC1/AC3 要求的逐路径 diff 与 SHA-256、`.git/index` 绑定、head/tree 归因均无独立字节证据；且本会话沙箱曾对 `G:\CODEX\New Manga` 尝试写入 ACL（Win32 5），root/`.git/index` 的 ACL 与 hash 状态需在 final pre-run 以只读方式再证，否则 executor `:384-385/:437` 的 `IndexState`/ACL 断言可能直接 fail-stop | 执行前由 Codex 独立复算 12 输入 + attempt5 三件套 + `.git/index` 的 bytes/SHA-256 并记录 `MATCH`；同批次只读复核 root 路径链 ACL/streams 无漂移。本 Review 不据此放行 |
| P2-002 | P2 | `.../p02pre-r1h-attempt5-exec-review-pins-20261012.json:1-39`（无 `checkpointIncludedInInputPins`）；`.../p02pre-r1h-round6-integration-protocol-attempt5-20261012.md:11`（“all other … constraints remain unchanged”） | 继承的 attempt4 protocol §7 “Pin manifest consistency (P3-2)”（attempt4 protocol `:104-105`）要求 metadata 与输入 pin 列表严格一致并显式声明 checkpoint 是否入集；A4 先例明确为 `checkpointIncludedInInputPins=false`（`p02pre-r1h-attempt4-review-adjudication-20261012.md:8`）。attempt5 pins 缺该字段，事后无法从被审输入直接判定 checkpoint 是否属于 pin 集 | 在 pins metadata 增加 `checkpointIncludedInInputPins: false`（或列入 reinforcement checkpoint），使 metadata 与 `inputs[]` 自洽；此为文本修正，不影响 attempt4 冻结件 |
| P3-001 | P3 | `.../p02pre-r1h-attempt5-exec-review-pins-20261012.json:25-38` | `executionEvidence: NOT_RUN`、`gateState.BuildCargo: NOT_RUN`、`SystemAC1toAC7: BLOCKED / NOT_RUN`、`scope` 与 protocol §1/§6 一致，未把计划/静态项写成 PASS；仅 Task `doc/tasks/P02PRE-R1H-R6-EXEC-A5.md:60` 行仍为 `NOT_RUN/待生成`，需在 Review 落地后回填 | Codex adjudication 时按实回填 Task 表行与证据链接 |
| P3-002 | P3 | `.../p02pre-r1h-round6-integration-protocol-attempt5-20261012.md:6` 与 `.../p02pre-r1h-round6-interaction-protocol-attempt4-20261012.md:6`（原文冲突，前者因继承不变） | 行文将 Reviewer 写作 “DeepSeek Harness **CLI**”，而本 A5 派发说明为 “DSH stdout response”；`doc/09_COLLABORATION.md:157-163` 区分 CLI 与 Web 可见性，A4 adjudication 记录 “reviewer model was not reported”。若按 “CLI 会话” 读，本次会话可能被误记为 CLI 证据 | 由 Codex 在 adjudication 中记录实际投递通道/模型可得性（`reviewer_model=UNKNOWN` 等），避免通道口径歧义 |
| P3-003 | P3 | `.../p02pre-r1h-round6-integration-protocol-attempt5-20261012.md:107`（原文 “independent `APPROVED_STATIC_PROTOCOL`”，继承自 attempt4 `:107`） | 本 Task 允许的 Reviewer verdict 集合为 `APPROVED_STATIC_CONTENT / CHANGES_REQUESTED / BLOCKED`，其中无 `APPROVED_STATIC_PROTOCOL`；放行条件字面上不可由本 Task 出具的 verdict 满足（A4 同处亦已存在该错配，`p02pre-r1h-attempt4-review-adjudication-20261012.md:12` 为 `APPROVED_STATIC_CONTENT`） | 在协议或 adjudication 中把放行条件对齐为 `APPROVED_STATIC_CONTENT` + Codex pin 复算 + adjudication，避免事后“Gate 未满足”歧义 |

**Counts：P0＝0，P1＝0，P2＝2，P3＝3。**

### 4) 声明与放行边界

- 本次为 **static-only Review**：**未运行** attempt5 executor、`File.Replace`、任何 OS/API 或 P/Invoke 调用、动态隔离、Build/Cargo、system AC1–AC7、R1H capture 或 Windows Sandbox；未写、未改、未创建任何仓库文件；未读取 pinned 输入以外的文件、未枚举目录、未访问 `.tmp.driveupload`，亦未使用 grep/search。
- **任何输入均无法独立 hash 校验**（原因见 §1）：12 个 pinned input 的 bytes/SHA-256、`.git/index` SHA-256、`main` head/tree 全部属 `NOT_VERIFIED`。「attempt4 与 attempt5 执行器仅 6 处差异」是逐行内容比对结论（两个文件同为 638 行，逐区间核对一致），**不是**字节或 SHA-256 结论。
- 本 verdict `APPROVED_STATIC_CONTENT` 仅覆盖 attempt5 执行器/协议/Handoff 的静态内容与继承一致性，**不等于执行证据、`PRE_RUN_PASS`、Gate 或 AC PASS**；不授权跳过 final pre-run。执行放行条件：Codex 复算全部 pins 为 `MATCH`（含 `.git/index`）、处置 P2-001/P2-002 后 adjudicate，再按 attempt5 protocol §4 完成 final pre-run（身份/SID/token、profile/registry/ACL 只读态、TEMP/cache/scratch、main/Owner refs/status/index、protected hashes、child image/argv/CWD、路径/ACL/streams 与全部输出 absent/unignored），全通过后方可最多调用一次 attempt5 executor；任何不符即 `BLOCKED`，不重试、不清理、不回滚。

（说明：本环境的一次 `SetNamedSecurityInfoW Win32 5` 失败发生在命令执行前，属环境/权限层问题，非 attempt5 制品缺陷；但因其可能触及 root 工作区 ACL，已计入 P2-001 的 pre-run 复核项。）
