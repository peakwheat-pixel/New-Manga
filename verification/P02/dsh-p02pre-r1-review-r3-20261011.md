# P02PRE-R1 Round 3 非作者独立复审意见

**结论：`CHANGES_REQUESTED`**
本轮新计：P0=`0` / P1=`0` / P2=`1` / P3=`2`
Round 1（11 项）：`CLOSED` 11 项。Round 2（5 项）：`CLOSED` 5 项，但 **P2-3 存在一处未闭合残余**（本轮 P2-1）。
安全侧结论：**未发现越界写入、范围外进程、profile/ACL/registry 变更、canary 写入、build/Cargo/AC 或 Sandbox 接触**；本轮唯一 P2 是**证据字段层面的假 PASS 风险**，不是副作用风险。修掉该行 + 同步一句 manifest 状态后即可放行那一次只读采集。

---

## 一、Review 覆盖与不可核验项

**本轮完整读取（只读）**

- `verification/P02/p02pre-r1-capture.ps1`（**556 行全文**，逐段核对：进程/编码、路径链、目录记录、Git 记录、WER、partial 装配、ACL 复核、计数与停止门、序列化/写盘/抛错）。
- `doc/tasks/P02PRE-R1.md`（72 行全文）、`verification/P02/p02pre-r1-manifest-20261011.md`（73 行全文，含 L16 部分证据新规、L56 注册表错误单列、L63 编码口径、L71 `ACL_UNVERIFIABLE` 分类新规）。
- Round 1 报告 `verification/P02/dsh-p02pre-r1-review-20261011.md`（120 行）与 Round 2 报告 `verification/P02/dsh-p02pre-r1-review-r2-20261011.md`（111 行），逐条对齐原文位置。
- 按需交叉核对 r6 路径表/环境表/WER/证据边界，以及 `.gitignore`（19 行）。
- 读取 `verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.stdout.log`（2 行：`POWERSHELL_VERSION=5.1.26100.9549` + `PARSE_OK`）。
- 确认 `verification/P02/p02pre-r1-evidence-20261011.json` **仍不存在**（glob 实测），符合“capture 前禁止运行”。
- **未读取**任何用户漫画/库/数据库/权重内容；全部审查对象仅为项目文档与脚本。

**不可核验（如实声明）**

1. **bytes/SHA-256 未独立复算**：本会话 `pwsh` 工具仍在沙箱准备阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）；按指令未做 ACL 修改、未提权重试、未绕行、未换 shell。因此 `11866 / 11908 / 37945 / 18951 bytes` 与四个 SHA-256 与 prompt pin 的**匹配未经我独立确认**（内容级审查成立，hash 级绑定未成立，沿用仓库先例「不可核验 ≠ 不匹配」）。
2. **未执行任何命令**：未运行 capture script、未调用 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash、未 build/Cargo/AC、未改 Gate 或 Task 状态、未写任何文件。
3. **无 Round 3 parser 产物可直接核对**：prompt 所述“current 5.1 parser 结果”在仓库内我只能看到 Round 1/2 的 `p02pre-r1-windows-powershell-parse-20261011.*` 与 `...-r2-20261011.*`（均 `PARSE_OK` / exit 0 / stderr 空）；**没有**针对本轮 556 行修订版的保管 parse 产物。我对本轮脚本的 5.1 语法判断是**静态判断**，不等同于已解析证据。
4. 未复核 scratch 实际 HEAD/tree（`7ce3c40c…`/`ce8056b8…`）、未复核 Plan/STATUS/COLLABORATION 当前文本。
5. **静态复审与 parser 输出都不证明脚本已运行、不证明任何宿主/OS 条件通过、不构成 Gate PASS。**

---

## 二、Round 1（11 项）逐项处置

| # | Round 1 finding | 处置 | 本轮行号证据 |
|---|---|---|---|
| P1-1 | 64 MiB 超限即零证据 | **CLOSED** | L531-539：超限改 bounded partial；L532 先存 `$originalStopReason`；L533 **仅在无既有 stop reason 时**才写 `EVIDENCE_SIZE_LIMIT_PARTIAL`；L534/L537 的 bounded 与 minimal partial 均携带 `originalStopReason`+`stopReason`（L333、L537）；仍同一 `CreateNew` 一次写入（L541）后非零停止（L555）。 |
| P1-2 | Git status hash 非原始字节 | **CLOSED** | L60-66 原始字节捕获（`BaseStream.CopyToAsync` → `MemoryStream`）；L76-77 `stdoutBase64/stdoutSha256` 由该字节计算；L201-211 status 的 SHA/Base64/字节数/NUL 计数全部由 `FromBase64String` 还原的真字节派生；L67 显示用 replacement UTF-8；L216 strict UTF-8（`throwOnInvalidBytes=$true`）。 |
| P2-1 | HOMEDRIVE+HOMEPATH 未做拼接断言 | **CLOSED** | L391-405 组合并与 `USERPROFILE` 规范化比较；L483 PASS/FAILED/UNPROVABLE；L511 单列 `hostHomeConsistency`；L402 明示 LPAC 映射 `NOT_APPLIED_IN_R1`；L512 `tempCache` 恒 `UNPROVABLE`。 |
| P2-2 | QUERY_ERROR/ACL 停止条件未实现 | **CLOSED** | L470-474 + L504 `summary.queryErrorCount`（含 path/wer dir/wer registry/repo/ACL/hash/whoami）；L515 fail-stop；L455-462 ACL 端点比较与 `changed/queryError/notComparable/unverifiable` 计数；L428 未枚举 WER scope；L39/L506 恒 `UNPROVABLE_NOT_MONITORED_IN_R1`。 |
| P2-3 | reparse 只查对象自身 | **CLOSED** | L100-125 `Get-PathChain` 自 drive root 逐组件；消费者 L128、L147、L175-176、L444 均先过链且非 PRESENT 即早退。 |
| P2-4 | enum 被字符串化为数字 | **CLOSED** | L257-260、L274 `hive/hiveNumeric`、`view/viewNumeric` 双字段。 |
| P2-5 | 托管枚举显示名依赖运行时 | **CLOSED** | 同 P2-4；manifest L56 保留“若 getter 可得”。 |
| P2-6 | `.git` metadata reparse 不停止 | **CLOSED** | L235-241：三件 metadata 状态聚合 `gitMetadataComplete`，before/after index 必须 PRESENT，否则 `GIT_METADATA_INVALID` 早退；`indexStable`（L239）参与 `CAPTURED` 判定（L241）。 |
| P3-1 | finally 抛错掩盖 stopReason | **CLOSED** | 序列化（L523-529）与写盘（L540-553）均在 `finally` 之外各自 try/catch；L550 的写失败消息**显式携带** `stopReason=$($Result.stopReason)`；L551 仅内存追加诊断，不清理、不重试。 |
| P3-2 | WER last-write 未标记 | **CLOSED** | L263 `lastWriteMetadata = 'NOT_AVAILABLE_BY_GETTER'`；manifest L56 同步。 |
| P3-3 | NUL 计数口径未注明 | **CLOSED** | L208-209 `nulSegmentCountApprox` + `countDefinition`；manifest L63 同步。 |

**无 Round 1 回归**：逐项重查后 11 项均实质闭合（Round 2 判定的 P1-1/P3-1 残余已在本修订中消除）。

---

## 三、Round 2（5 项）逐项处置

| # | Round 2 finding | 处置 | 本轮行号证据 |
|---|---|---|---|
| P2-1 | partial 覆盖既有 stopReason | **CLOSED** | L532-534 + L537：`originalStopReason` 与 `stopReason` 双字段同时落盘；L533 仅在为空时才改写为新原因。原停机原因不再丢失。 |
| P2-2 | LocalDumps registry `QUERY_ERROR` 未进 fail-stop | **CLOSED（原分析为误读，非代码缺陷）** | 数据流复核结论：**旧版（Round 2 pin）L461-462 的 `$werQueryErrorCount` 本就 = `$werDirectoryRecords + $registryRecords` 再进入 `$queryErrorCount`，而 `$queryErrorCount>0` 已在旧 L499 停止条件中**。故 Round 2 报告“不含 registry”的断言**不成立**，Registry 错误实际已在停止面内——该报告条目应视为**我的误报**，此处如实更正。本修订 L471-474 拆成 `werDirectoryQueryErrorCount`/`werRegistryQueryErrorCount` 再显式相加并进入 L515，**行为等价但语义无歧义**；L488-489 summary 单列两项与合计，与 manifest L56 一致。 |
| P2-3 | 空 owner/SDDL 可致假 ACL PASS | **CLOSED** | L155：`owner`/`Sddl` 为空白即记 `state='ACL_UNVERIFIABLE'`；L438-442 将前置不可核验记为 `UNVERIFIABLE` 并跳过后续依赖；L447 端点复核不可核验同样记 `UNVERIFIABLE`；L460/L482/L509 使 `hostAclSnapshots` 降为 **`UNPROVABLE`**；L515 把 `aclUnverifiableCount` 纳入 fail-stop。与 manifest L71 新规一致。（残余见本轮 **P2-1**，仅涉另一个分类字段。） |
| P3-1 | 写失败异常未带 stopReason | **CLOSED** | L549-553：先组装含 `stopReason` 的 `$writeError`，追加进 `errors` 后 `throw`。 |
| P3-2 | whoami 文本解码口径未记录 | **CLOSED** | L67 仍按 Git/非 Git 选择编码；L73-75 记录 `stdoutTextEncoding`（`WebName`）、`stdoutTextCodePage`（`CodePage`）与 `textDecodeNote`（明示原始字节为准）；L287 partial 命令摘要同样携带这三项。 |

---

## 四、Round 3 新 findings

### P2-1｜`ACL_UNVERIFIABLE` 仍计入 `hostPathSnapshots` 的 PASS 判定（唯一 P2 残余）
- **位置**：`p02pre-r1-capture.ps1:508`（`hostPathSnapshots` 判定式只排除 `QUERY_ERROR`、`REPARSE_POINT|NOT_DIRECTORY`、`missingInputRoots`）；相关：`:155`（新增 `ACL_UNVERIFIABLE` 状态）、`:482`/`:501`（计数）、`:515`（停止门**已**包含该计数）、`manifest:71`（“PRESENT 目录的 owner 或 SDDL 为空时记录 `ACL_UNVERIFIABLE`”）。
- **触发**：某输入根/输出叶为 PRESENT 目录，但 `Get-Acl` 返回空 `Owner` 或空 `Sddl`（不抛异常）→ 该对象记为 `state='ACL_UNVERIFIABLE'`；它既不是 `QUERY_ERROR`，也不是 `REPARSE_POINT/NOT_DIRECTORY`，而根的存在性检查只看 `reparse`/`NOT_DIRECTORY`（`:148`、`:151`）。
- **影响**：唯一证据文件会同时出现两个互相矛盾的顶层分类——`hostAclSnapshots='UNPROVABLE'`（正确），而 `hostPathSnapshots='PASS_WITH_EVIDENCE'`（**未把 ACL 不可核验算进去**）。由于 `hostPathSnapshots` 是路径/ACL 快照的对外 PASS 字段之一，后续裁决者据此可能把“ACL 端点不可核验”读成“路径快照已通过”，属 manifest L71 明确要避免的“把不可核验写成 PASS”。不会产生副作用，但会污染 R1 的核心交付物。
- **具体修复**（单行级、机械改动）：在 `:508` 判定式中追加 `-and @($pathRecords | Where-Object { $_.state -eq 'ACL_UNVERIFIABLE' }).Count -eq 0`（或复用 `$aclUnverifiableCount`）；若希望保留“路径形态 PASS 但 ACL 未核验”的区分，则拆成 `hostPathShapeSnapshots` 与 `hostAclSnapshots` 两个字段，且不得让 `hostPathSnapshots` 单独宣称 ACL 通过。

### P3-1｜manifest 自述状态滞后于当前轮次
- **位置**：`manifest:9`「本对象=`R2_REVISION_FROZEN_FOR_INDEPENDENT_REVIEW`；……才可按本 Task 运行一次只读采集」；对照 `manifest:13`/`:16-17`（已写入 R3 的 partial/写失败新规）与 `task:60`（Codex 自述 R3 修订）。
- **触发**：无条件（纯文档）。
- **影响**：manifest 头部仍把对象标为“R2 修订待第二轮 Review”，与内容（已含第三轮修订）不一致；易被后续读者误判冻结轮次与已完成的 Review 轮数。属证据可追溯性瑕疵，不影响脚本行为。
- **具体修复**：把 `:9` 更新为第三轮状态（例如 `R3_REVISION_FROZEN_FOR_INDEPENDENT_REVIEW`），并注明前两轮 Review 结论与轮次。

### P3-2｜`Get-Acl` 抛错时 `directEntryCount` 被一并丢弃
- **位置**：`:152`（`Get-Acl … -ErrorAction Stop`）→ `:168-170` 的 catch 记录只有 `path/state/pathChain/errorType/error`；对照 `manifest:46`/`:48`（输出叶与 canary 叶要求“metadata/ACL **和**直接 entry count”）。
- **触发**：目录可读、`Get-Item` 成功，但 `Get-Acl` 抛异常（拒绝读取安全描述符等）。
- **影响**：该叶的 `directEntryCount` 完全缺失，输出叶“是否非空/可否复用”的判据（`:469` 依赖 `directEntryCount`）随之无法评估：非空但 ACL 读取失败的叶不会被计入 `nonemptyScratchOutputLeaves`。方向偏保守（不会误判为可复用），但会以“计数缺失”而非“不可核验”的形态出现在证据里。
- **具体修复**：把 `Get-Acl` 单独 try/catch；失败时仍返回 `state='ACL_UNVERIFIABLE'`（或 `QUERY_ERROR`）并保留已可得的 `directEntryCount`/attributes，在记录中显式标注 ACL 不可核验。

---

## 五、范围与“无回归”核对（明确通过的部分）

- **写入面仍最小且唯一**：全脚本唯一写操作是 `:541` 的 `[IO.File]::Open($EvidencePath, FileMode::CreateNew, Write, None)`，等于 `manifest:15` 的唯一证据路径；无 append/overwrite/retry/move/delete，无 `New-Item/Out-File/Set-Content/Add-Content`，无 registry/ACL/owner/label 写，无 profile Create/Delete，无 canary 写，无 build/Cargo/AC，无下载，无 Sandbox。
- **存在性门仍在一切查询之前**：`:15` 命中即抛错、零查询、零写入，且位于 try 之外（不会产生第二份证据或 partial）。
- **子进程 allowlist 未扩大**：仅 `git.exe` 四组固定参数（`:186`、`:187`、`:200`、`:213`）与 `whoami.exe /all`（`:372`）；`UseShellExecute=false`（`:51`）、无 shell/COM/network/compiler；`--no-optional-locks` 与四项 `-c`、`-C "<root>"` 引号与 `manifest:62` 逐字一致。
- **对象集合逐项一致、无新增**：12 输入根（`:406-419`）、13 output leaves（`:421`）、3 canary leaves（`:423`）、3 WER 目录（`:425`）、WER 2 键×2 view×4 value（`:245-279`）、36 个环境变量（`:389`）、12 个 protected hashes（`:429`）与 r6 表/`manifest:27-64` 完全对齐。
- **身份/目标门仍先于取数**：`:375-376` 先判 `whoami` exit 与 user/SID；通过后才取 main，再取 scratch（`:383-387`），两仓均校验固定 HEAD/tree/branch/common-dir（`:198-199`）。
- **未把未知改写成 PASS（重点复核）**：`hostIdentity` 初值 `UNPROVABLE`→仅在身份校验通过后置 `PASS_WITH_EVIDENCE`（`:34`、`:378`）；`private_registry_absence` 恒 `UNPROVABLE`（`:35`）；`tempCache` 恒 `UNPROVABLE`（`:512`）；`werEffectivePolicy` 恒 `UNPROVABLE`（`:41`）；`process_and_path_access_closure`/`accessClosure` 恒 `UNPROVABLE_NOT_MONITORED_IN_R1`（`:39`、`:506`）；`profile_api_path_and_store`、`lpac_write_and_child_closure`、`effectiveAccessAndWriteClosure`、`fullProtectedInvariantsAndDynamicWriteClosure` 恒 `REQUIRES_ACTIVE_TEST`（`:36-37`、`:510`、`:514`）；`product_build_and_ac1_ac7` 恒 `NOT_RUN`（`:38`）；`werQueriedFields` 仅在 registry+目录均无 error 时 PASS（`:513`）。未见“getter 成功 = 有效 WER policy”“快照成功 = 无瞬时写/无范围外访问”的越权推断。**唯一例外即本轮 P2-1。**
- **partial 分支不伪造成功**：`captureStatus='PARTIAL_EVIDENCE'`、`partialReason`、`originalStopReason`、`omittedFullInventory=true`（`:325-351`），并仍以非零退出（`:555`）。
- **Windows PowerShell 5.1 静态兼容**：本修订仅新增 `if` 表达式赋值（`:155`）、`-match` 过滤、`[Text.UTF8Encoding]::new($false,$false)`、`WebName/CodePage` 属性、`[ordered]@{}` 与 `ConvertTo-Json -Depth`——均为 5.1 已支持构造；`Get-Acl -LiteralPath` 经 5.1 文档确认为 ByLiteralPath 参数集。**但本轮无对应 parse 产物可核（见 §一.3），仍属静态判断。**

---

## 六、是否可以放行一次只读调用

- **副作用风险面**：未发现范围外路径/进程/写入、覆盖/截断、reparse 跟随（祖先链已校验）、用户数据内容越权读取。就“不会造成不可接受副作用”而言，**无阻塞项**。
- **本轮不给出放行**：仅因 **P2-1** 会让 R1 唯一交付物中的 `hostPathSnapshots` 可能与 `hostAclSnapshots` 相互矛盾，等于把“ACL 不可核验”写成路径快照 PASS——正是 Task/manifest 禁止的“未知变 PASS”。P3-1/P3-2 属文档与计数可读性，可同批处理。
- **建议顺序**：修 `:508` 一行 + `:168-170` 计数保留 + `manifest:9` 状态 → 重新冻结三个文件 bytes/SHA，并**必须补一份针对本修订版的 5.1 只读 `ScriptBlock::Create` parse 产物**（当前仓库内没有本轮的）→ 非作者**聚焦复审**（仅核 P2-1 与两 P3，无需重跑全量静态审查）→ Codex adjudication → 才允许**唯一一次**调用；在此之前禁止创建 `p02pre-r1-evidence-20261011.json`。
- **Gates 保持原样**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Windows Sandbox 不查询/不安装/不启用/不启动。**`APPROVED` 亦仅是本 Review 的判断，不通过任何 Gate。**

---

## 七、给下一步的最小可执行指令（供 Codex 转发；非我方执行）

> 致 Codex（P02PRE-R1 Owner）：Round 3 复审 `CHANGES_REQUESTED`，新计 P0/P1/P2/P3=`0/0/1/2`；Round 1 十一项全 `CLOSED`，Round 2 五项全 `CLOSED`（其中 Round 2 P2-2 经数据流复核确认为**上一轮 Reviewer 误报**，旧代码已含 registry 错误，本修订的拆分只是消除歧义）。请闭环：(1) `capture.ps1:508` 的 `hostPathSnapshots` 判定加入 `ACL_UNVERIFIABLE` 排除（或拆分为路径形态/ACL 两个字段），确保 ACL 不可核验时不会出现 `PASS_WITH_EVIDENCE`；(2) `:168-170` 的 catch 分支在 `Get-Acl` 失败时仍保留 `directEntryCount` 与 attributes 并标 `ACL_UNVERIFIABLE`；(3) 把 `manifest:9` 的状态文字更新为当前轮次。改后重新冻结 Task/manifest/script 的 bytes/SHA，**补一份本修订版的 Windows PowerShell 5.1 只读 parse 产物**（`ScriptBlock::Create`，不调用脚本），再交非作者聚焦复审与 Codex adjudication；复审通过前不得运行 capture、不得创建证据 JSON，Gates 与 barrier 维持现状。

**（本报告为静态只读复审，不证明脚本已运行，也不证明任何宿主/OS 条件通过；hash 级绑定未成立，见 §一.1。）**