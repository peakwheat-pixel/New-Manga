# P02PRE-R1 Round 4 非作者独立复审意见

**结论：`CHANGES_REQUESTED`**
本轮 P0=`0` / P1=`0` / P2=`0` / P3=`1`
三轮历史 finding 全量处置：Round 1（11 项）全 `CLOSED`；Round 2（5 项）全 `CLOSED`（含 Round 2 P2-2 更正为上一轮误报）；Round 3（3 项）全 `CLOSED`。
**唯一未闭合项是 manifest 一处过期文字（P3-DOC-1）**，脚本本身**未发现**任何技术缺陷或副作用风险。就“可否放行一次只读采集”而言：脚本已满足全部技术判据，仅剩的这条文档问题**不需要重跑全量 Review**——但按本 Reviewer 既有的计数口径（任何未闭合项均计入本轮），我不能把本轮判为 `APPROVED`，故如实给出 `CHANGES_REQUESTED`，并建议走**极窄范围**闭环。

---

## 一、Review 覆盖与不可核验项

**本轮完整读取（只读）**

- `verification/P02/p02pre-r1-capture.ps1`（**561 行全文**，逐段复核：进程/编码、路径链、目录记录（含新增 `ACL_QUERY_ERROR`）、Git 记录、WER 记录、partial 装配、ACL 复核、计数与停止门、序列化/写盘/抛错）。
- `doc/tasks/P02PRE-R1.md`（78 行全文，含新增 L34、L68-72、L76）、`verification/P02/p02pre-r1-manifest-20261011.md`（73 行全文，含 L9 轮次声明、L13 执行器、L16-17 写入语义、L71 分类新规）。
- Round 1（120 行）、Round 2（111 行）、Round 3（112 行）三份报告全文，逐条对齐原文位置与最小修复要求。
- 按需交叉核对 R6 路径/环境/WER/证据/受保护清单边界；`.gitignore`（19 行）。
- 读取 `verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stdout.log`（2 行：`POWERSHELL_VERSION=5.1.26100.9549` + `PARSE_OK`）。
- 确认 `verification/P02/p02pre-r1-evidence-20261011.json` **仍不存在**（glob 实测），符合“复审与 adjudication 通过前禁止 capture”。
- **未读取**任何用户漫画/库/数据库/凭据/权重内容；审查对象仅为项目文档与脚本。

**不可核验（如实声明）**

1. **bytes/SHA-256 未独立复算**：本会话 `pwsh` 工具仍在沙箱准备阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）；按指令未做 ACL 修改、未提权重试、未绕行、未换 shell。因此 `14115 / 12489 / 38729 / 17502 bytes` 与四个 SHA-256 与 prompt pin 的**匹配未经我独立确认**（内容级审查成立，hash 级绑定未成立，沿用先例「不可核验 ≠ 不匹配」）。
2. **未执行任何命令**：未运行 capture script、未调用 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash、未 build/Cargo/AC、未改 Gate 或 Task 状态、未写任何文件。
3. **parse 证据只能核对已存在对象**：我核对了 R3 保管的 `...parse-r3-...stdout.log` = `PARSE_OK`（与 45 bytes/`C076120D…` 相符）。**我无法从仓库独立确认该 parse 输入就是本轮 pin 的 38729-byte 脚本**（时间戳/输入快照未在同一产物中绑定）；且 prompt 所述 382-byte stderr（PowerShell 启动进度 CLIXML）我未读取内容。故“本修订版已通过 5.1 解析”这一主张，我只能确认“存在一份 `PARSE_OK` 产物”，**不能确认其输入与本次冻结 bytes 一致**。
4. 未复核 scratch 实际 HEAD/tree（`7ce3c40c…`/`ce8056b8…`）、未复核 Plan/STATUS/COLLABORATION 当前文本。
5. **静态复审与 parser 输出都不证明脚本已运行、不证明任何宿主/OS 条件通过、不构成任何 Gate PASS。**

---

## 二、Round 3 三项修复的独立验证（本轮重点）

### Round 3 P2-1｜`ACL_UNVERIFIABLE` 曾可致 `hostPathSnapshots=PASS_WITH_EVIDENCE` → **`CLOSED`**
- **分类新逻辑**（`ps1:513`）：`hostPathSnapshots` = 若 `pathQueryErrorCount>0`、或存在 `REPARSE_POINT|NOT_DIRECTORY`、或 `missingInputRootCount>0` → `FAILED`；**否则若 `pathAclUnverifiableCount>0` → `UNPROVABLE`**；否则 `PASS_WITH_EVIDENCE`。
- **计数链路**：`pathAclUnverifiableCount`（`ps1:475`）= `pathRecords` 中 `state='ACL_UNVERIFIABLE'` 的数量，而该状态仅在 `owner`/`Sddl` 空白时置位（`ps1:168-172`）。
- **结论**：只要任一适用路径 ACL 不可核验，`hostPathSnapshots` 必然是 `UNPROVABLE`（不可能 PASS）；`hostAclSnapshots` 同时因 `aclUnverifiableCount>0` 为 `UNPROVABLE`（`ps1:514`），两者一致；`ps1:520` 的停止门也包含 `$aclUnverifiableCount`，遂置 `QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE`。与 `manifest:71`「`hostAclSnapshots` 与 `hostPathSnapshots` 均不得标 PASS，前者=`UNPROVABLE`，后者=`UNPROVABLE`」逐字一致。
- **query error / 缺根分类未回归**：`pathQueryErrorCount`（`ps1:473`）现同时统计 `QUERY_ERROR` 与新增 `ACL_QUERY_ERROR`；`missingInputRootCount`（`ps1:480`）仍只对 12 个输入根的 `ABSENT` 计数；二者分别进入 `FAILED` 分支，语义未被削弱。

### Round 3 P3-1｜manifest 轮次自述 → **`CLOSED`（附本轮 P3-DOC-1 残余）**
- `manifest:9` 现为 `本对象=R4_REVISION_FROZEN_FOR_INDEPENDENT_REVIEW`，并写明“须经**第四轮**独立 Review 与 Codex adjudication 后才可运行一次只读采集”，同时如实记录前三轮均为 `CHANGES_REQUESTED`。**未出现任何“已批准/已通过”的虚假声明** —— 符合 prompt 对 P3-1 的验收表述。
- 残余：同段末尾括注仍把 R3 发现项限定为“路径快照状态、manifest 轮次文字和 ACL getter 失败时保留直接 entry count”，未含 R3 的第三项修复已完成；`manifest:13` 又写“host capture 仍须**第二轮** Review 与 Codex adjudication 后单独调用”。二者与 R4 头部不一致（见 P3-DOC-1）。

### Round 3 P3-2｜`Get-Acl` 异常丢弃 metadata/count → **`CLOSED`**
- 新结构（`ps1:152-173`）：先建 `$record`（含 `fullName/attributes/creationTimeUtc/lastWriteTimeUtc/pathChain`，`ps1:152-161`）；`directEntryCount` 在独立 try/catch 内取得（`ps1:162-165`）；**随后**才 `Get-Acl`（`ps1:166`），失败即 `$record.state='ACL_QUERY_ERROR'` 并**携带已取得的全部 metadata 与 `directEntryCount`** 返回（`ps1:167`）；成功但 `owner`/`Sddl` 空白则原来地置 `ACL_UNVERIFIABLE`（`ps1:168-172`）。
- **已知正数用于非空判定**：`ps1:472` 的非空叶计数改为 `if ($null -ne $leafRecord.directEntryCount -and $leafRecord.directEntryCount -gt 0)`，**不再要求 `state='PRESENT'`** —— 因此 ACL 查询失败的叶只要已取得正数 count，仍会被计入 `nonemptyScratchOutputLeaves`（`ps1:507`），并正确驱动 `outputLeafState='FAILED_FOR_REUSE; no leaf changed'`（`ps1:510`）。满足 prompt 要求的“uses a known positive count to detect a nonempty scratch leaf even if its ACL query fails”。
- **仍不可得的唯一情形**：`Get-ChildItem` 自身失败时 count 不可得（`ps1:164` 置 `QUERY_ERROR` + `errorOperation='Get-ChildItem'` 后返回，尚未取 count），此时记录不会伪装成已知；与 `manifest:71`「若失败发生在读取 entry count 时，该 count 不可得」一致。方向保守，无假 PASS。

### 追加要求｜`ACL_QUERY_ERROR` 的全链路（prompt 明确要求核查）→ **正确，不可被读成 PASS，也未静默漏报**
| 环节 | 行号 | 行为与结论 |
|---|---|---|
| 产生 | `ps1:167` | `Get-Acl` 异常 → `state='ACL_QUERY_ERROR'`（带 `errorOperation='Get-Acl'`、异常类型/消息），metadata 与 count 保留 |
| 目录/路径记录计数 | `ps1:473`、`ps1:474` | `pathQueryErrorCount` 与 `werDirectoryQueryErrorCount` 均用 `-in @('QUERY_ERROR','ACL_QUERY_ERROR')` 纳入 |
| 汇总 | `ps1:478`、`ps1:490` | 进入 `$queryErrorCount`（`ps1:509` 的 `summary.queryErrorCount`）与 `summary.pathQueryErrors` |
| ACL 复核映射 | `ps1:441-444` | `before.state='ACL_QUERY_ERROR'` → 比较记录 `state='QUERY_ERROR'`（`ps1:442` 显式分支），被 `ps1:461` 的 `queryErrorCount` 正则统计 |
| 分类 | `ps1:513`、`ps1:514` | `hostPathSnapshots` 与 `hostAclSnapshots` **均为 `FAILED`** |
| 停止门 | `ps1:520` | `$queryErrorCount>0` 与 `$aclQueryErrorCount>0` 任一即置 `QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE` |
| 其他分类 | `ps1:518` | WER 对象发生 `ACL_QUERY_ERROR` 时 `werQueriedFields='FAILED'` |
| 证据落盘 | `ps1:555` | 仍以非零退出（stopReason 已在唯一证据文件中） |

未发现任何“`ACL_QUERY_ERROR` 被读成 PASS”或“静默丢弃”的路径。

---

## 三、Round 4 新 finding

### P3-DOC-1｜manifest 两处过期文字（残留“R2/R3 视角”），可能误导后续审查/执行者
- **位置**：`verification/P02/p02pre-r1-manifest-20261011.md:13`（`host capture 仍须第二轮 Review 与 Codex adjudication 后单独调用`）与 `:9` 段末括注（R3 发现项枚举与当前 R4 状态不同步）。
- **触发**：无条件；纯文档。
- **影响**：与 `manifest:9` 头部（R4 冻结、须第四轮 Review）**互相矛盾**。后续读者若只读 `:13`，可能误以为存在“第二轮 Review 通过”这一前置条件已被满足，从而高估冻结对象的审查覆盖；也不会影响脚本行为或产生任何副作用。
- **最小修复**：把 `:13` 的“第二轮 Review”改为“当前冻结轮次（R4）独立 Review 与 Codex adjudication”；并把 `:9` 段末括注改为“R3 发现项（路径快照状态、manifest 轮次文字、Get-Acl 失败保留 direct entry count）已在 R4 修订，待本轮 Review”。

---

## 四、全量历史 finding 处置表

**Round 1（11 项）**

| # | finding | 处置 | 现位置证据 |
|---|---|---|---|
| R1-P1-1 | 64 MiB 超限即零证据 | `CLOSED` | `ps1:536-544`（`$originalStopReason` 先行保存；`:538` 仅空时改写；`:539`/`:542` 双 partial 均带 `originalStopReason`）；`:546` 同一 `CreateNew` 一次写入；`:560` 非零停止 |
| R1-P1-2 | Git status hash 非原始字节 | `CLOSED` | `ps1:60-66,76-77`（原始字节）；`:204-214`（status 全部量由真字节派生）；`:67` 显示用 replacement UTF-8；`:219` strict UTF-8 |
| R1-P2-1 | HOMEDRIVE+HOMEPATH 未断言 | `CLOSED` | `ps1:394-408` 组合比较；`:487` 状态；`:516` 单列 `hostHomeConsistency`；`:517` `tempCache` 恒 `UNPROVABLE` |
| R1-P2-2 | QUERY_ERROR/ACL 停止条件缺失 | `CLOSED` | `ps1:473-478,509,520`；`:458-465` ACL 端点比较与四类计数；`:431` 未枚举 WER scope；`:39`/`:511` 恒 `UNPROVABLE_NOT_MONITORED_IN_R1` |
| R1-P2-3 | reparse 只查对象自身 | `CLOSED` | `ps1:100-125` 逐组件；消费者 `:128`、`:147`、`:178-179`、`:447` |
| R1-P2-4 | enum 字符串化为数字 | `CLOSED` | `ps1:260-263`、`:277` `hive/hiveNumeric`、`view/viewNumeric` |
| R1-P2-5 | 托管枚举显示名依赖运行时 | `CLOSED` | 同 P2-4；`manifest:56` 保留“若 getter 可得” |
| R1-P2-6 | `.git` metadata reparse 不停止 | `CLOSED` | `ps1:238-244`（`gitMetadataComplete` + `indexStable` 参与 `CAPTURED`） |
| R1-P3-1 | finally 抛错掩盖 stopReason | `CLOSED` | `ps1:528-534`、`:545-558`（均在 `finally` 之外）；`:555` 消息含 `stopReason` |
| R1-P3-2 | WER last-write 未标记 | `CLOSED` | `ps1:266` `NOT_AVAILABLE_BY_GETTER` |
| R1-P3-3 | NUL 计数口径未注明 | `CLOSED` | `ps1:211-212` `nulSegmentCountApprox`+`countDefinition` |

**Round 2（5 项）**

| # | finding | 处置 | 现位置证据 |
|---|---|---|---|
| R2-P2-1 | partial 覆盖既有 stopReason | `CLOSED` | `ps1:536-543`（`originalStopReason` 与 `stopReason` 并存，仅在空时改写） |
| R2-P2-2 | LocalDumps registry 错误未进 fail-stop | `CLOSED`（**更正为上一轮误报**） | 旧版 `$werQueryErrorCount` 已含 registry 并进入停止门；现 `ps1:474-478` 拆分显式相加，`:492-493` 单列 |
| R2-P2-3 | 空 owner/SDDL 可假 ACL PASS | `CLOSED` | `ps1:168-172`（`ACL_UNVERIFIABLE`）；`:441-444`（`UNVERIFIABLE`）；`:463,486,505,514`（`hostAclSnapshots=UNPROVABLE`）；`:520` 停止 |
| R2-P3-1 | 写失败异常未带 stopReason | `CLOSED` | `ps1:554-558` |
| R2-P3-2 | whoami 文本解码口径未记录 | `CLOSED` | `ps1:73-75`、`:290`（encoding/code page/note；原始字节为准） |

**Round 3（3 项）**

| # | finding | 处置 | 现位置证据 |
|---|---|---|---|
| R3-P2-1 | `ACL_UNVERIFIABLE` 可致 `hostPathSnapshots=PASS` | `CLOSED` | `ps1:475`、`:513`（先 FAILED 判定，再退 `UNPROVABLE`）；`:520` 停止 |
| R3-P3-1 | manifest 轮次自述滞后 | `CLOSED`（残留见 P3-DOC-1） | `manifest:9` 已写 R4 冻结与“须第四轮 Review” |
| R3-P3-2 | `Get-Acl` 异常丢弃 metadata/count | `CLOSED` | `ps1:152-167`（先建记录、先取 count、再取 ACL）；`:472`（不依赖 `PRESENT` 的非空判定） |

---

## 五、范围与“无回归”核对（明确通过）

- **写入面仍唯一且最小**：全脚本唯一写操作是 `ps1:546` 的 `[IO.File]::Open($EvidencePath, FileMode::CreateNew, Write, None)`，即 `manifest:15` 的唯一证据路径；无 append/overwrite/retry/move/delete，无 `New-Item/Out-File/Set-Content/Add-Content`，无 registry/ACL/owner/label 写，无 profile Create/Delete，无 canary 写，无 build/Cargo/AC，无下载，无 Sandbox 接触。
- **存在性门仍在最前**：`ps1:15` 命中即抛错、零查询、零写入，且位于 try 之外（不会产生第二份证据或 partial）。
- **子进程 allowlist 未扩大**：仅 `git.exe` 四组固定参数（`:189`、`:190`、`:203`、`:216`）与 `whoami.exe /all`（`:375`）；`UseShellExecute=false`（`:51`）；无 shell/COM/network/compiler；`--no-optional-locks` 与四项 `-c`、`-C "<root>"` 引号与 `manifest:62` 逐字一致。
- **对象集合逐项一致、无新增**：12 输入根（`:409-422`）、13 output leaves（`:424`）、3 canary leaves（`:426`）、3 WER 目录（`:428`）、WER 2 键×2 view×4 value（`:248-282`）、36 环境变量（`:392`）、12 protected hashes（`:432`）与 R6 表/`manifest:27-64` 完全对齐。
- **身份/目标门仍先于取数**：`:378-379` 先判 `whoami` exit 与 user/SID；通过后才取 main，再取 scratch（`:386-390`），两仓均校验固定 HEAD/tree/branch/common-dir（`:201-202`）。
- **未把未知改写成 PASS（逐项复核）**：`hostIdentity` 初值 `UNPROVABLE`→仅身份校验通过后 `PASS_WITH_EVIDENCE`（`:34`、`:381`）；`private_registry_absence` 恒 `UNPROVABLE`（`:35`）；`tempCache` 恒 `UNPROVABLE`（`:517`）；`werEffectivePolicy` 恒 `UNPROVABLE`（`:41`）；`process_and_path_access_closure`/`accessClosure` 恒 `UNPROVABLE_NOT_MONITORED_IN_R1`（`:39`、`:511`）；`profile_api_path_and_store`、`lpac_write_and_child_closure`、`effectiveAccessAndWriteClosure`、`fullProtectedInvariantsAndDynamicWriteClosure` 恒 `REQUIRES_ACTIVE_TEST`（`:36-37`、`:515`、`:519`）；`product_build_and_ac1_ac7` 恒 `NOT_RUN`（`:38`）；`werQueriedFields` 仅在无任何 WER 目录/注册表错误时 `PASS_WITH_EVIDENCE`（`:518`）；ACL 快照仅在无变化、无 query error、无 unverifiable 时才 `PASS_WITH_EVIDENCE`（`:514`）。未发现“getter 成功 = 有效 WER policy”“快照成功 = 无瞬时写/无范围外访问”的越权推断。
- **Windows PowerShell 5.1 静态兼容**：本轮新增构造仍为 5.1 已支持项（`if` 表达式赋值、`-in` 数组运算、`[ordered]@{}`、`ConvertTo-Json -Depth`、`Get-Acl -LiteralPath`（5.1 文档确认 ByLiteralPath 参数集）、`Get-ChildItem -LiteralPath`）；`ps1:167` 的 `$record.state=…; return $record` 与 `:441-444` 的 `elseif` 写法均为合法语句。**但这些只是静态判断，见 §一.3。**

---

## 六、是否可以放行一次只读调用

- **副作用风险面**：未发现范围外路径/进程/写入、覆盖/截断、reparse 跟随（祖先链已校验）、用户数据内容越权读取、profile/ACL/registry 变更、canary 写入或 Sandbox 接触。就“不会造成不可接受副作用”而言，**无任何阻塞项**。
- **技术判据**：Round 3 遗留的三项（P2-1、P3-1、P3-2）以及 prompt 追加要求核查的 `ACL_QUERY_ERROR` 全链路，**均已在本次冻结 bytes 中正确闭合**；未发现新的技术 finding。
- **本轮不判 `APPROVED` 的唯一原因**：`manifest:13`（及 `:9` 括注）与 R4 头部自相矛盾的过期文字（**P3-DOC-1**）。按本 Reviewer 一贯口径，凡有未闭合项即不计 `APPROVED`；此项不影响脚本正确性，也**不需要重跑全量 Review**。
- **建议放行路径**：修 `manifest:13` 一句 + `:9` 括注 → 重新冻结 manifest（script/Task 未变则无需重算；若一并改 script 则必须重算并重解析）→ 由本轮 Reviewer **极窄范围**确认该两行与 R4 头部一致（+ 可选：把 parse 输入与 pin bytes 在同一产物中绑定）→ Codex adjudication → 即可执行**唯一一次**宿主只读采集。在此之前禁止创建 `p02pre-r1-evidence-20261011.json`。
- **Gates 保持原样**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。**`APPROVED` 亦仅是本 Review 的判断，不通过任何 Gate。**

---

## 七、给下一步的最小可执行指令（供 Codex 转发；非我方执行）

> 致 Codex（P02PRE-R1 Owner）：Round 4 聚焦复审结论 `CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/0/1`；Round 1 十一项、Round 2 五项、Round 3 三项**全部 `CLOSED`**，且 `ACL_QUERY_ERROR` 已确认经 `pathQueryErrorCount`(`ps1:473`)/`werDirectoryQueryErrorCount`(`:474`)/ACL 复核(`:441-444`)/`hostPathSnapshots`+`hostAclSnapshots`(`:513-514`)/停止门(`:520`) 全链路生效，不会被读成 PASS。唯一未闭合项为文档：`manifest:13` 仍写“host capture 仍须**第二轮** Review 与 Codex adjudication”，与 `manifest:9` 的 R4 冻结声明矛盾；`manifest:9` 段末括注的 R3 发现项枚举也与 R4 状态不同步。请只改这两处（“第二轮”→“当前冻结轮次（R4）”并同步括注），然后 (a) 重新计算并记录 manifest 的新 bytes/SHA（script/Task 若未改动则保持原 pin），(b) 把 Windows PowerShell 5.1 `ScriptBlock::Create` parse 的**输入 hash 与输出 `PARSE_OK` 绑定在同一产物**（消除“parse 输入是否为本次冻结 bytes”的不可核验点），(c) 交非作者极窄范围确认后由 Codex adjudicate；在 adjudication 完成前不得运行 capture、不得创建证据 JSON，Gates/barrier 维持现状。

**（本报告为静态只读复审，不证明脚本已运行，也不证明任何宿主/OS 条件通过；hash 级独立绑定未成立，见 §一.1/§一.3。）**