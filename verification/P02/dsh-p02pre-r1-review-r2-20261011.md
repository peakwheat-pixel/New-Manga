# P02PRE-R1 Round 2 非作者独立复审意见

**结论：`CHANGES_REQUESTED`**
本轮新计：P0=`0` / P1=`0` / P2=`3` / P3=`2`
Round 1 处置：11 项中 **`CLOSED` 9 项**、**`PARTIALLY_CLOSED` 2 项**（P1-1、P3-1；其残余以本轮 P2-1、P2-3 重新计分）。
安全侧结论：**未发现越界写入、范围外进程、profile/ACL/registry 变更、canary 写入、build/Cargo/AC 或 Sandbox 接触**；新增问题全部是**证据口径/停止语义**问题，不存在不可接受的副作用风险。因此本轮不建议直接放行那一次调用（修完 3 项 P2 后即可放行）。

---

## 一、Review 覆盖与不可核验项（先行声明）

**本轮完整读取（只读）**

- `doc/tasks/P02PRE-R1.md`（63 行全文，含 L31 解析证据段、L53-57 R1 处置段、L61 停机段）。
- `verification/P02/p02pre-r1-manifest-20261011.md`（73 行全文，含 L13 精确 shell 路径、L16 部分证据规则、L63-64 原始字节/Git metadata、L71 分类语义）。
- `verification/P02/p02pre-r1-capture.ps1`（535 行全文，逐段核对 allowlist、参数、写入、哈希、停止路径与部分序列化分支）。
- Round 1 报告 `verification/P02/dsh-p02pre-r1-review-20261011.md`（120 行全文），逐条对齐 11 项 finding 的原文位置与要求。
- 交叉核对 r6 `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`（本次按需重读其路径表/环境表/WER/证据与 protected 段落）与 `.gitignore`（19 行）。
- 核对 parse 证据内容：`p02pre-r1-windows-powershell-parse-20261011.stdout.log` = 2 行 `POWERSHELL_VERSION=5.1.26100.9549` + `PARSE_OK`（与 45 bytes 相符）；`.exit` = `0`（与 2 bytes `0\r\n` 相符）；`p02pre-r1-evidence-20261011.json` 仍**不存在**（glob 实测），符合“未运行”。
- 12 个 `protectedHashes` 目标中，`doc/tasks/P02PRE-R0S6.md` 与 `verification/P02/p02pre-r0s6-checkpoint-20261011.md` 经 glob 确认存在（不会退化为 ABSENT 记录）。

**不可核验（不得由我的文字替代）**

1. **bytes/SHA-256 未独立复算**：本会话 `pwsh` 工具在沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），按指令未做 ACL 修改、未提权重试、未绕行、未换 shell。因此 `9028 / 11206 / 35725 bytes` 与三个 SHA-256 与 prompt pin 的**匹配未经我独立确认**（内容级审查成立；hash 级绑定未成立，按仓库先例「不可核验 ≠ 不匹配」）。
2. **未执行任何东西**：未运行 capture script、未跑 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash 命令、未做 build/Cargo/AC、未改 Gate 或 Task 状态、未写任何文件。
3. **parser 证据仅证明语法可解析**：`5.1.26100.9549` + `PARSE_OK` + exit 0 是**静态语法**证明，不等于运行时行为、.NET Framework API 可用性、cmdlet/provider 行为或任何宿主条件通过；本轮我未复核该命令 argv/时序（只读其产物）。
4. 未复核 scratch 实际 HEAD/tree（`7ce3c40c…`/`ce8056b8…`）、未复核 Plan/STATUS/COLLABORATION 当前文本、未重审 r1–r5 全部历史证据。
5. **静态复审不构成脚本已运行或任一 OS 条件通过。**

---

## 二、Round 1 逐项处置（含精确行引用）

| # | Round 1 finding | 处置 | 证据/理由 |
|---|---|---|---|
| P1-1 | 64 MiB 超限即零证据 | **PARTIALLY_CLOSED** | 已改为：超限时写 bounded `PARTIAL_EVIDENCE`，仍用同一 `CreateNew` 一次写入（`ps1:515-522`），partial 保留仓库状态/status SHA/字节数/NUL 计数/每仓前 1000 条 inventory + omitted count（`ps1:278-320`）、二次超限再降级最小 partial（`:519-521`）；`:516` 置 `EVIDENCE_SIZE_LIMIT_PARTIAL` 后非零停止（`:534`）。残余见本轮 **P2-1**（`stopReason` 被覆盖）。 |
| P1-2 | Git status hash 非原始字节 | **CLOSED** | `BaseStream.CopyToAsync` 直接捕获原始字节（`ps1:58-66`），`stdoutBase64/stdoutSha256` 由该字节计算（`:73-74`）；status 的 SHA/Base64/字节数/NUL 计数全部由 `FromBase64String` 还原的真字节派生（`:198-208`）；显示用 Git stdout 用 replacement UTF-8（`:67`，`new UTF8Encoding($false,$false)`）；inventory 用 strict UTF-8（`:213`）。与 `manifest:63` 一致。 |
| P2-1 | HOMEDRIVE+HOMEPATH 未做拼接断言 | **CLOSED** | `ps1:387-401` 组合 `HOMEDRIVE+HOMEPATH` 与 `USERPROFILE` 规范化比较；`:470` 给出 PASS/FAILED/UNPROVABLE；`:495` 单列 `hostHomeConsistency`；`:496` `tempCache` 恒为 `UNPROVABLE`（`manifest:71`）。未把宿主 home 一致性外推到 LPAC scratch 映射（`:397-398` 明示 `NOT_APPLIED_IN_R1`）。 |
| P2-2 | QUERY_ERROR/ACL 停止条件未实现 | **CLOSED**（含本轮 P2-3 细化） | 顶层聚合 `summary.queryErrorCount` 等（`ps1:460-491`）；`:499` 任一 query error / reparse / 缺根 / hash 不完整 / repo 失败 / ACL 变化 / ACL 复核错误 / home FAILED 即置 `QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE`；`:446-452` 记录 ACL 端点前后比较与 `changedCount/queryErrorCount/notComparableCount` 及只测端点的范围声明；`:424` 明确未枚举的 WER scope；`:39`/`:490` 恒标 `UNPROVABLE_NOT_MONITORED_IN_R1`。残余见 **P2-2**（WER registry 未入门）与 **P2-3**（ACL 读取失败静默降级）。 |
| P2-3 | reparse 只查对象自身 | **CLOSED** | `Get-PathChain`（`ps1:97-122`）从 drive root 起逐组件查询并在任一段 reparse/查询错误即返回；所有消费者（`Get-FileRecord:125`、`Get-ExactDirectoryRecord:144`、repo root/`.git`:172-173、ACL 复核:436）均先过该链，非 PRESENT 即早退。 |
| P2-4 | enum 被字符串化为数字 | **CLOSED** | `ps1:254-257`、`:271` 给出 `hive/hiveNumeric`、`view/viewNumeric` 双字段（`$hive.ToString()`、`[int64]$hive`、`[int]$view`）。 |
| P2-5 | 托管枚举显示名依赖运行时 | **CLOSED** | 同 P2-4，名称与数值并存，任一缺失仍可判读；另 `manifest:56` 保留“若 getter 可得”。 |
| P2-6 | `.git` metadata reparse 不停止 | **CLOSED** | `ps1:232-237`：三件 metadata 状态聚合为 `gitMetadataComplete`，`before/after` index 必须 PRESENT，否则 `GIT_METADATA_INVALID` 早退；`indexStable` 仅在两侧 PRESENT 时比较（`:236`），并在 `:238` 参与最终 `CAPTURED` 判定。 |
| P3-1 | finally 抛错掩盖 stopReason | **PARTIALLY_CLOSED** | 序列化/写盘已移出 `finally`，各自 try/catch（`ps1:507-513`、`:523-532`），不再有 `finally` 抛错路径；`stopReason` 在正常与序列化失败分支均保留（`:504`、`:511`）。残余：证据写盘失败时 `:532` 直接 `throw`，其消息未携带既有 `$Result.stopReason`（见本轮 **P3-1**）。 |
| P3-2 | WER last-write 未标记 | **CLOSED** | `ps1:260` `lastWriteMetadata = 'NOT_AVAILABLE_BY_GETTER'`。 |
| P3-3 | NUL 计数口径未注明 | **CLOSED** | `ps1:205-206` `nulSegmentCountApprox` + `countDefinition`；`manifest:63` 同步说明 `--no-renames` 下每条 porcelain record 一个 terminator。 |

**Codex 汇总中未逐条覆盖的两点，需说明**：(a) 汇总第 4 条把“query/ACL 停止”合并描述，但 `manifest:73` 的“权限/API 错误即停止”在 WER registry getter 上**尚未闭合**（本轮 P2-2）；(b) 汇总第 8 条称“preserve stopReason”，实际在 `:516` 会**覆盖**既有 stopReason（本轮 P2-1）。另外汇总未提及 ACL 读取失败仍会产出 PRESENT 记录（本轮 P2-3）。

---

## 三、Round 2 新 findings

### P2-1｜部分证据分支覆盖既有 `stopReason`，且丢失原始停止原因
- **位置**：`p02pre-r1-capture.ps1:516`（`$Result.stopReason = 'EVIDENCE_SIZE_LIMIT_PARTIAL'`），对照 `:499`、`:507-513`；`manifest:16`。
- **触发**：任何已置 `stopReason` 的运行（例如 `QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE`、`MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED`、`WHOAMI_QUERY_FAILED`）同时其 JSON 超过 64 MiB。
- **影响**：唯一证据文件里的 `stopReason` 变成“体积超限”，**原始停机原因只存在于各分支记录中**，顶层聚合无法区分“超限本身”与“超限+已发生 ACL/路径漂移”。R1 P1-1/P3-1 明确要求“retaining explicit stop reason”，此处属未完全闭合；裁决者若只看 `stopReason` 会误判。
- **具体修复**：先保存 `originalStopReason`，再仅在为空时写入 `EVIDENCE_SIZE_LIMIT_PARTIAL`；partial/最小 partial 中同时输出 `originalStopReason` 与 `stopReason`（数组或双字段），并保证 `errors` 保留。

### P2-2｜WER registry 的 `QUERY_ERROR` 未进入停止门（停止面与 manifest 不一致）
- **位置**：`ps1:462`（`$queryErrorCount = $pathQueryErrorCount + $werQueryErrorCount`，**不含** `$registryRecords`）、`:461`（`$werQueryErrorCount` 只由 `$werDirectoryRecords + $registryRecords` 组成，且**只用于 summary/分类**）、`:497`（`werQueriedFields` 因该错误被标 FAILED）、`:499`（停止条件只看 `$queryErrorCount`、`$invalidPathCount` 等）；对照 `manifest:73`「权限/API 错误……停止所有依赖对象」、`manifest:71`「`FAILED`=查询异常」。
- **触发**：任一 LocalDumps key 打开失败（拒绝访问、view 不可用、`OpenBaseKey` 异常）→ `Get-WerRecord` 产出 `state='QUERY_ERROR'` 记录（`ps1:271`）。
- **影响**：证据显示 `werQueriedFields=FAILED`、`summary.werQueryErrors>0`，但**顶层不停机**、`whoami`/路径/ACL 检查照常继续。同一文档下的“任意查询异常即停机”在这一个 getter 上不成立，属停止语义与 manifest 的实质偏差（不会造成副作用，但会让一次运行在已发生查询异常时仍然“正常收尾”，后续裁决必须自行发现 summary 里的计数）。
- **具体修复**：把 `@($registryRecords | Where-Object { $_.state -eq 'QUERY_ERROR' }).Count` 并入 `$queryErrorCount`（或单列 `werRegistryQueryErrorCount` 并加入 `:499` 条件），保持 evidence 不变、分类不变。

### P2-3｜ACL 读取失败被静默降级（记录为 PRESENT 且不含 owner/SDDL），可产生假 PASS
- **位置**：`ps1:146-168`（`Get-ExactDirectoryRecord`：`Get-Acl` 失败落入 `:165-167` 的 `QUERY_ERROR` 记录），但 `:147`/`:148` 之后的**提前 `return` 子句**（`NOT_DIRECTORY` 在 `:148`、以及 `:145` 的链失败）之外的正常路径中，若 `Get-Item` 成功而 `Get-Acl` 抛错，则走 catch 返回 `QUERY_ERROR`（可计数）；**真正的问题在成功路径的字段缺失**：`:150-161` 的 `owner`/`securityDescriptorSddl` 仅在 `Get-Acl` 成功时存在，一旦 catch 走 `:165`，记录**没有** `pathChain` 且 `state='QUERY_ERROR'`（可计数）——但**若 `Get-Acl` 返回对象而语义为空/不可核验**（例如 ACL 读取返回但不含可比较端点），记录仍是 `state='PRESENT'` 且带空 `owner`/`Sddl`。
- **触发**：ACL 端点不可核验（返回空/异常语义）而非抛错时。
- **影响**：`:492` 的 `hostPathSnapshots` 判定只看 `pathQueryErrorCount`、`REPARSE_POINT/NOT_DIRECTORY`、`missingInputRoots`——**空 owner/SDDL 的 PRESENT 目录不会拉低该项**，可能得 `PASS_WITH_EVIDENCE`；这与 `manifest:71`“ACL 快照仅当所有可比较端点未变化且无 query error 才可 PASS”不符，属新的假 PASS 面。R1 P2-2 要求的“ACL endpoint 变化/不可核验即失败”在此未完全闭合。
- **具体修复**：为 PRESENT 记录增加可核验性断言（`owner`/`securityDescriptorSddl` 为空即置 `state='ACL_UNVERIFIABLE'` 或追加计数），并把该计数并入 `:492` 与 `:499`；对 `NOT_COMPARABLE` 保持 `UNPROVABLE`（现状正确）。

### P3-1｜证据写入失败时异常消息不携带既有 `stopReason`
- **位置**：`ps1:532`；对照 `manifest:17`「保留外层异常、原 stopReason……的事实」。
- **触发**：`CreateNew` 打开/写盘失败（例如父目录不可用、磁盘满、并发出现目标）。
- **影响**：外层只能看到 `EVIDENCE_WRITE_FAILED`，已判定的 `stopReason` 不在异常文本中，也未回写任何记录（按规则不清理、不重试，故无法补救）；与“保留原 stopReason”的字面要求有差。
- **具体修复**：把 `StopReason=$($Result.stopReason)` 拼入该 throw 消息，并在抛错前尝试把 `$Result.errors` 追加该项（不写盘、不清理）。

### P3-2｜重定向管道下 `whoami` 人类可读文本的编码
- **位置**：`ps1:67`（非 Git 子进程用 `[Console]::OutputEncoding` 解码）、`:75`（`stderr` 同）。
- **触发**：`whoami.exe /all` 的输出经匿名管道重定向（`RedirectStandardOutput=$true`）时，其代码页与宿主控制台输出代码页可能不同（区域设置相关）。
- **影响**：`identity.whoami.stdout` 的**人类可读文本**可能乱码；但同一记录的 `stdoutBase64`/`stdoutSha256`（`:73-74`）是**原始字节**，证据本身不受影响，故仅 P3。SID/权限/完整性 SID 多为 ASCII，实际风险低。
- **具体修复**：为非 Git 子进程显式使用确定性编码（例如 `[Text.Encoding]::UTF8` 或记录 `GetConsoleOutputCP()`），或对 `whoami` 只保留原始字节字段并在文档中说明文本字段仅供阅读。

---

## 四、范围与“无回归”核对（明确通过的部分）

- **写入面仍最小**：全脚本唯一写操作是 `ps1:524` 的 `[IO.File]::Open($EvidencePath, FileMode::CreateNew, Write, None)`，路径为 `manifest:15` 的唯一证据文件；无 append/overwrite/retry/move/delete，无 `New-Item/Out-File/Set-Content/Add-Content`，无 registry/ACL/owner/label 写，无 profile Create/Delete，无 canary 写，无 build/Cargo/AC，无下载，无 Sandbox。
- **存在性门仍在最前**：`ps1:15` 先判目标存在即抛错、零查询、零写入，且该分支在 try 之外，不会产生第二份证据或 partial。
- **子进程 allowlist 未扩大**：仍仅 `git.exe` 固定四组参数（`:183`、`:184`、`:197`、`:210`）与 `whoami.exe /all`（`:368`），`UseShellExecute=false`、无 shell/COM/network/compiler；`--no-optional-locks` 与四项 `-c`、`-C "<root>"` 引号与 `manifest:62` 逐字一致。
- **对象集合逐项一致**：12 输入根（`:402-415`）、13 output leaves（`:417`）、3 canary leaves（`:419`）、3 WER 目录（`:421`）、WER 两键×两 view×四 value（`:242-276`）、36 个环境变量（`:385`）、12 个 protected hashes（`:425`）与 r6 表/`manifest:27-64` 完全对齐，**无新增路径、无遗漏**（仅相对路径尾斜杠书写差异，不影响 `Join-Path`）。
- **身份/目标门仍先于取数**：`:371-372` 先判 `whoami` exit 与 user/SID，不匹配只留有限身份证据即停；`:379-383` 在 identity 通过后才取 scratch，且两仓均以固定 HEAD/tree/branch/common-dir 校验（`:195-196`、`:380`）。
- **未把未知改写成 PASS（重点核对）**：`hostIdentity` 初值 `UNPROVABLE`（`:34`）、仅在身份校验通过后才置 `PASS_WITH_EVIDENCE`（`:374`）；`private_registry_absence` 恒 `UNPROVABLE`（`:35`）；`tempCache` 恒 `UNPROVABLE`（`:496`）；`werEffectivePolicy` 恒 `UNPROVABLE`（`:41`）；`process_and_path_access_closure`/`accessClosure` 恒 `UNPROVABLE_NOT_MONITORED_IN_R1`（`:39`、`:490`）；`profile_api_path_and_store`、`lpac_write_and_child_closure`、`effectiveAccessAndWriteClosure`、`fullProtectedInvariantsAndDynamicWriteClosure` 恒 `REQUIRES_ACTIVE_TEST`（`:36-37`、`:494`、`:498`）；`product_build_and_ac1_ac7` 恒 `NOT_RUN`（`:38`）。ACL 快照在 `NOT_COMPARABLE>0` 时降为 `UNPROVABLE`（`:493`），未见“getter 成功 = 有效 policy”或“快照成功 = 无瞬时写”的越权推断。
- **partial 分支不伪造成功**：`captureStatus='PARTIAL_EVIDENCE'`、`omittedFullInventory=true`、附 `stopReason`/`errors`/`summary`/分类（`:322-348`），并在 `:534` 非零退出；`manifest:16` 的“超限仍写同一证据并停止”成立。

---

## 五、是否可以放行一次调用

- **副作用风险面**：本脚本仍是纯宿主只读采样；未发现范围外路径/进程/写入、覆盖、截断、reparse 跟随（祖先链已校验）、用户数据内容读取越权（Git inventory 中 `.gitignore` 已排除模型权重/训练数据 PNG；未跟踪非忽略文件按 r6/task 授权的受保护清单口径处理）。就“不会造成不可接受副作用”而言，**未发现阻塞项**。
- **本轮不作为放行**：P2-1/P2-2/P2-3 都会让**证据口径与 manifest 的停止/PASS 语义不一致**——而 R1 的全部价值就是产出可被独立裁决的宿主基线。按 Task 自身规则（`task:36`、`task:39`、`task:61`；`manifest:9`、`manifest:71`），证据口径不闭合时不应执行。
- **建议顺序**：修 P2-1、P2-2、P2-3（P3-1/P3-2 可同批）→ 重新冻结 bytes/SHA（含新一轮 `5.1` parse 证据）→ 非作者复审这 5 项 → Codex adjudication → 才允许**唯一一次**调用；期间禁止创建 `p02pre-r1-evidence-20261011.json`。
- **Gates 保持**：`private_registry_absence=UNPROVABLE`、Technical Gate=`NOT_SATISFIED`、Owner Risk Acceptance=`APPROVED`、Gate Disposition=`WAIVED_BY_OWNER`、Build Authorization=`AUTHORIZED_WITH_EXCEPTION`、`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`、Hard Build Barrier=`EFFECTIVE`、Build/Cargo=`NOT_RUN`、AC1–AC7=`BLOCKED / NOT_RUN`。**`APPROVED` 亦仅是本 Review 的判断，不通过任何 Gate**——本轮更未给出可执行放行。

---

## 六、给下一步的最小可执行指令（供 Codex 转发；非我方执行）

> 致 Codex（P02PRE-R1 Owner）：Round 2 复审 `CHANGES_REQUESTED`，新计 P0/P1/P2/P3=`0/0/3/2`；R1 十一项中 9 项 `CLOSED`、P1-1 与 P3-1 记 `PARTIALLY_CLOSED`。请闭环：(1) `ps1:516` 改为“仅在 `stopReason` 为空时写 `EVIDENCE_SIZE_LIMIT_PARTIAL`”，并在 partial/最小 partial 中同时输出 `originalStopReason`；(2) 把 WER registry 的 `QUERY_ERROR` 计数并入 `ps1:462`/`:499` 的停止门（或单列并加入条件），保持分类与证据不变；(3) 为 PRESENT 目录记录增加 `owner`/`securityDescriptorSddl` 可核验性断言并把不可核验计数并入 `:492`/`:499`，避免假 `PASS_WITH_EVIDENCE`；(4) `ps1:532` 的写失败异常消息携带既有 `stopReason`；(5) 明确非 Git 子进程文本编码口径。改后重新冻结 Task/manifest/script 的 bytes/SHA 与新一轮 Windows PowerShell 5.1 只读 parse 证据，输出 11 项 + 5 项的逐条处置表，再交非作者复审与 Codex adjudication；在复审通过前不得运行 capture、不得创建证据 JSON，Gates 与 barrier 维持现状。

**（本报告为静态只读复审，不证明脚本已运行，也不证明任何宿主/OS 条件通过。）**
