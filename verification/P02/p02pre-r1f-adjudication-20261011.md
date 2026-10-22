# P02PRE-R1F Round 1 Review Adjudication 与 Pre-run 状态

更新时间=`2026-10-11`；Task=`P02PRE-R1F`；Adjudicator=`Codex /root`。

## Round 1 Review

- 非作者 Reviewer=`DeepSeek Harness`，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`；decision=`CHANGES_REQUESTED`；finding counts=`P0/P1/P2/P3 = 0/1/2/2`。
- Review prompt=`verification/P02/dsh-p02pre-r1f-review-20261011.prompt.md`；原始 stdout=`verification/P02/dsh-p02pre-r1f-review-20261011.stdout.jsonl`（实际正文是 Markdown）；`.md` 文件是 wrapper `DSH_FINAL_EVENT_MISSING` diagnostic，不是 Review 报告。stderr、exit 与 prompt 均保留在对应路径。
- Review 的执行范围为只读 Task/manifest/script/parser 检查；Reviewer 未运行命令或 capture。Capture JSON 与 wrapper stdout/stderr/exit 当时均不存在。

## Codex 对 F1–F5 的裁定与修复

| Finding | Codex 裁定 | 已实施修复 |
|---|---|---|
| F1 P1：fail-stop 分支缺少 blocker/omitted 计数 | 接受；不同阶段的 candidate 数可知性必须明确 | 新增统一 `Set-RepositoryStop`；每个 repository fail-stop return 记录 state、`errorOperation`、error、可定位的 `firstBlockingPath`，并在 `candidateCountKnown=true` 时计算 `omittedCount`。Inventory 未解析时保留 `candidateCountKnown=false`、`omittedCount=null`；完整解析后每个 blocker 都保留未处理数。Partial JSON 同步输出这些字段。 |
| F2 P2：index-stage 严格 UTF-8 解码异常未映射且 comparer 大小写敏感 | 接受 | path 与 index-stage parser 异常分别映射为 `GIT_FILE_INVENTORY_PARSE_FAILED` / `GIT_INDEX_STAGE_PARSE_FAILED`；保存 `errorOperation` 与异常说明。Index mode map 使用 `StringComparer.OrdinalIgnoreCase`，并由内存 self-check 拒绝 case-only duplicate path。 |
| F3 P2：R1 manifest pin 有 65 位字面值 | 接受 manifest 修正；不回写已关闭的 R1 历史 adjudication | R1F manifest 改为 R1 Task 记录的 64 位 `A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A`。Round 1 Review 中提到的 R1 adjudication 复制错误作为历史 transcription typo 保留说明，不据此推断 R1 文件变更。 |
| F4 P3：link inventory 使用 `gitMode` 而 manifest 写 `mode` | 接受 | 输出字段改为 `mode`。 |
| F5 P3：未明示跳过 symlink 后不再查询该路径 | 接受 | 在 skip 分支 `break` 处加入单行不变量注释；manifest 明确记录后立即停止该 candidate，不再调用后续 `Get-*`、hash 或 ACL query。 |

改动文件=`doc/tasks/P02PRE-R1F.md`、`verification/P02/p02pre-r1f-manifest-20261011.md`、`verification/P02/p02pre-r1f-capture.ps1`。Final Task/manifest/script/parser pins 必须由 Round 3 Review prompt 和后续 Codex pre-run adjudication 使用实际 hash 补齐；本文件当前不释放 capture。

## Round 2 Review 与 Codex 裁定

- 非作者 Reviewer=`DeepSeek Harness`，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`；decision=`CHANGES_REQUESTED`；counts=`P0/P1/P2/P3 = 0/0/0/3`；CLI exit=`0`。prompt、stdout、stderr、exit 分别保存在 `dsh-p02pre-r1f-review-r2-20261011.{prompt.md,stdout.md,stderr.log,exit}`。Reviewer 成功读取 Task/manifest/script；未运行命令、capture 或 host getter，也未修改文件；其环境未能独立复算 SHA，hash 结论由 Codex 本机复核。
- R1F-R2-F1 P3：Reviewer 推断 `if` 条件比较结果泄漏到 PowerShell function pipeline。Codex 使用 Windows PowerShell 5.1 parse exact script 并仅执行 AST 抽取的 `Get-InventoryAction` 与 `Assert-InventoryPolicySelfCheck`。证据=`p02pre-r1f-r2-selfcheck-20261011.json`，1548 bytes / SHA-256 `FE1989875B773AF7C02CB3A05CA9ED25AA9F7AB7581F57D4CB3D77CE055DDB96`；source=`55603 bytes / SHA-256 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54`；PS=`5.1.26100.9549`、parse errors=`0`、self-check=`PASS`、pipeline output count=`0`。未调用 capture、host getter 或 registry/ACL write。尽管测试未复现泄漏，调用点仍显式 `$null = Assert-InventoryPolicySelfCheck`，作为输出边界的防御性处理。裁定=`ADDRESSED; R3_REVIEW_REQUIRED`，不把 Reviewer 原因描述成已复现缺陷。
- R1F-R2-F2 P3：接受未知省略数不得聚合成零。summary 新增 `repositoryOmittedCountKnown`；仅当两仓 `candidateCountKnown=true` 时为 true，否则 `repositoryOmittedPaths=null`。
- R1F-R2-F3 P3：接受执行顺序耦合发现。保护清单移除从未创建的 R5 parser artifact，保留最终 R6 parser path；Round 3 `APPROVED` 后先生成并核验 R6，再允许 capture。Task/manifest 均记载 R5 是未生成的历史预定目标。
- 三项 P3 的 owner 处置=`FIXED / DEFENSIVELY ADDRESSED`，均须由 Round 3 非作者 Review 核验后才可进入 parser/capture。该裁定不释放 capture，不改变任何 P02PRE/Build Gate 状态。

## Round 3 Review 与 Codex Adjudication

- 非作者 Reviewer=`DeepSeek Harness`，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`；decision=`APPROVED`；counts=`P0/P1/P2/P3 = 0/0/0/0`；DSH CLI exit=`0`。prompt=`dsh-p02pre-r1f-review-r3-20261011.prompt.md`（4682 bytes / SHA-256 `719FE454A22DA4FD4BD91EF656F9F0973FCF0B87CAAA94956836E6852C36A2DC`）；stdout=`dsh-p02pre-r1f-review-r3-20261011.stdout.md`（9922 / `113D7F63100309F8172D4A2616BCA499E4CDD55E0CD470EBE6701F3E8EA970CB`）；stderr=`dsh-p02pre-r1f-review-r3-20261011.stderr.log`（6302 / `E27A5B9E5CF2F57AAD85E49A27017A32027598397CD463CB343FBCCE162E2D4A`）；exit file=`dsh-p02pre-r1f-review-r3-20261011.exit` (`0`, 1 byte / `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9`).
- Reviewer reports reading the exact Task (`11487 / 736C470C01199D268E64C65CEE0497A26026EB8F3441A9879DDAC9FA32E05F21`), manifest (`12368 / C19171CC5991733DD419C4C7E6BD74B506FA6E649196EFBBE261E19E3EDA9F98`), script (`55603 / 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54`) and self-check JSON (`1548 / FE1989875B773AF7C02CB3A05CA9ED25AA9F7AB7581F57D4CB3D77CE055DDB96`). DSH explicitly did not independently hash files or run commands; Codex independently recalculated each frozen input and the prompt/stdout/stderr/exit bytes using .NET SHA-256, `Get-FileHash`, and `certutil`, and all three methods matched the dispatched pins.
- Round 3 independently confirmed R1F-R2-F1/F2/F3 closed, Round 1 F1–F5 still closed, and found no new issues. Codex accepts the Review content conclusion. F1 self-check remains limited to two extracted pure functions; it is not whole-script or host execution evidence. R6 parser and capture remain `NOT_RUN` at the time of adjudication.
- Codex adjudication=`REVIEW_ACCEPTED; RELEASE_FOR_R6_PARSE_ONLY`. This releases only a Windows PowerShell 5.1 `ScriptBlock::Create` parse-only against the exact reviewed script bytes. It does not release capture: after parser success, Codex must separately verify all pre-run pins, identity, roots/HEAD/tree, output target absence and protected baseline, then write a pre-run adjudication before the single capture call.

## Parse、执行与 Gate 状态

- R4 parser 曾对 protected-hash list 修改前的旧 script bytes 解析成功：`PARSE_OK`、exit `0`、`captureScriptInvoked=false`，旧 source=`54,988 bytes / D60A06FA09B3688093D4E1721B529212D514B7A476F5DB096D752DECE388FEFF`；artifact=`verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r4-20261011.json`。其 source pin 不匹配当前 script，故为历史检查，不作为 Round 2 Gate evidence。
- Round 3 Review=`APPROVED (0/0/0/0)`；R6 Windows PowerShell 5.1 parse-only 已释放但在本 adjudication 写入时仍=`NOT_RUN`。它只解析 `55,603 bytes / 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54` exact source bytes，不调用 capture。
- R1F capture=`NOT_RUN`；唯一结果目标 `verification/P02/p02pre-r1f-evidence-20261011.json` 尚未创建。Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
- 保持 `private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`，Hard Build Barrier=`EFFECTIVE`。

## R6 parser 结果与执行前 pin 复核（Round 3 bytes）

- R6 parse-only=`PARSE_OK`，Windows PowerShell=`5.1.26100.9549`，exit=`0`，`captureScriptInvoked=false`；input/child/parent-recheck 均为 `55603 bytes / 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54`。artifact=`verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r6-20261011.json`，`1337 bytes / D4E1911D9FA8ABFDA93D405A39380BECE73A50CFF29872D95A16C1926BE5E18D`。该证据只绑定 Round 3 旧脚本 bytes；没有调用 host getter/capture。
- Codex 执行前复核发现，R1F Task/manifest 将继承 R1 manifest 的 hash 少记最后一位 `7`。R1 manifest=`12615 bytes`；.NET SHA-256、PowerShell `Get-FileHash`、`certutil -hashfile` 三者均为 `A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`，与 R1 Task、R1 adjudication 和 R1 evidence 记录一致。原 R1F Round 3 bytes 中的该 pin 是 63 位字面值，虽然 Round 3 Review 报告误记为 64 位；这不是 R1 源文件变更。
- Codex 已把 Task/manifest pin 更正为 64 位实际 SHA，并在 capture script protected-hash inventory 中加入 R4 Review prompt/stdout/stderr/exit 与 R7 parser artifact。当前候选 Task=`12812 bytes / 51BD45ECAF08F67F0824CA989B20F1DD0211BE966846E07683DF58D2B25AD2AB`；manifest=`13263 bytes / 15FD7795833A3D62D7AD0B322D4DA7B8E7AFF41C4FC88C67AA17947C307F21F0`；script=`56051 bytes / 1CBED581B0A774DA78C619F80272B98C4CB1D7B3DB633A2722FEA5673C507737`。必须由非作者 DeepSeek Harness R4 Review 对这些精确 bytes 复核，之后再以 R7 对更新脚本做 PS 5.1 parse-only。
- 执行前 adjudication=`BLOCKED / NOT_RELEASED_PENDING_R4_REVIEW_AND_R7_PARSE`；R1F capture=`NOT_RUN`。R3 Review/R6 parser 不构成新候选的 Review 或 parse 证据。用户授权仍有效；没有任何 Gate 被解除，Build/Cargo=`NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`。

## R4 retry 独立 Review 与 Codex adjudication

- 非作者 Reviewer=`DeepSeek Harness`，session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`；CLI exit=`0`。R4 retry report=`verification/P02/dsh-p02pre-r1f-review-r4-retry-20261011.stdout.md` (`11248 bytes / SHA-256 3BAE16F162D845575DE392BDA457729A6F2F4CFF2592C0C9F218CE0A1E61B9DA`)，stderr=`15811 bytes / 38C67886D4EB0719C7345E2C74862B4D6700BBB4DEB82C8BFEE9DC4CBE268057`，exit file=`0` (`1 byte / 5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9`)；prompt=`3900 bytes / A606CDB0CA16D6BA4B41C076AB578783B8DC39F32B2876B9D1F2192F9197BDFA`。decision=`CHANGES_REQUESTED`，counts=`0/0/1/1`。DSH 未运行命令或写文件，Codex wrapper 分别保存 CLI stdout/stderr/exit。
- R1F-R4R-F1 P2（pin 有 65 位）=`REJECTED_BY_CODEX_AS_FALSE_POSITIVE`。报告正文列出的 hexadecimal 分组为 `A551 0774 B47C 17EB 29C5 BF5D 73FE 7B75 5C72 E272 6FC5 280E 7EF1 1A91 A23C 67A7`，共 16 组、每组 4 位，即 64 位；它并未列出额外第 65 位。PowerShell 字符计数=`64`。R1 manifest 文件的真实 SHA-256=`A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`，.NET SHA-256、`Get-FileHash`、`certutil` 三法一致；R1 Task/adjudication/evidence 交叉记录相符。Reviewer 未能在其沙箱复算 hash，但这个限制不改变 Codex 的本机三法证据。未修改任何 R1 文件。
- R1F-R4R-F3 P3（manifest line 16 仍将旧 R3 candidate 写作 R6 final parser）=`ACCEPTED_AND_FIXED`：R6 明确为旧候选 historical parser；最终只有 R4 follow-up=`APPROVED` 后才执行 R7 parse-only。当前更新后的 Task/manifest/script 必须由非作者 DeepSeek Harness 再次独立 Review，路径=`verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.*`。
- 本次 follow-up 尚未完成：R7 parser=`NOT_RUN`；capture=`NOT_RUN`；pre-run adjudication=`BLOCKED / NOT_RELEASED_PENDING_R4_FOLLOWUP_AND_R7_PARSE`。`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。

## R4 follow-up Review 与 Codex adjudication

- 非作者 DeepSeek Harness follow-up=`APPROVED`，counts=`0/0/0/0`，CLI exit=`0`。Report=`verification/P02/dsh-p02pre-r1f-review-r4-followup-20261011.stdout.md` (`9395 bytes / SHA-256 439D116517F3DA34790306E59E7EAAB6BCB6A7C8779A55382E0BC17B159E3E04`)；stderr=`2516 bytes / 10CD455EA82F7C18EB32D893A61E894B052E305CD5E224FC6412C956A28DDB29`；exit file=`0` (`1 byte / 5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9`)；prompt=`4191 bytes / D5B17F38502121AAD19C6A8F33DD7E404124F10F9394E6C001A9BF9F96FC5120`。Reviewer 逐字符复核后撤回 F1 的 65 位计数错误，确认 F3 的 R6/R7 文字已一致，且无新增 finding。DSH 的 `pwsh` 仍因 sandbox Win32 5 无法运行命令，故不声称 Reviewer 自行复算 bytes/SHA。
- Codex 独立核验 R4 follow-up 所审 Task=`14476 bytes / 0C0A8E9D1B20DB6DCDD9026C9BFA65A07942C808F64A49BF8855353F5D576BFD`、manifest=`14116 bytes / 21B62A57BA49FB328381B07B81C2649A3831095A663819C4D2327AED88F9176E`、script=`56785 bytes / 666D819646CF9558630356FF7AE7206C6A4587856CBCD2BC3BA317E9105FA980`。每项均由 .NET SHA-256、PowerShell `Get-FileHash`、`certutil` 三法复算且完全一致。R1 manifest 的真实 pin=`A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`，字面长 64 位；F1 所指 mismatch 不存在。R1 文件未被本轮改写。
- Codex adjudication=`REVIEW_ACCEPTED; RELEASE_FOR_R7_PARSE_ONLY`。R7 仅允许对上述 `56785 / 666D…FA980` script bytes 使用 Windows PowerShell 5.1 `ScriptBlock::Create` parse-only，不得调用/执行 capture。捕获、pre-run release、任何技术 Gate 均尚未通过；R7 后仍须 Codex 独立核对全部当前 pins、身份、HEAD/tree/status、目标 absent 和 protected-file 基线。
- 当前状态：R7 parser=`NOT_RUN`；R1F capture=`NOT_RUN`；pre-run adjudication=`BLOCKED_PENDING_R7_AND_FINAL_PRE-RUN_CHECKS`。风险值与 Build Gate/Hard Barrier 均原样保持；Build/Cargo=`NOT_RUN`，AC1–AC7=`BLOCKED / NOT_RUN`。
