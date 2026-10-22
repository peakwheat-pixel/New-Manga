# P02PRE-R1 Round 4 窄范围复核意见

**结论：`CHANGES_REQUESTED`**
本轮计数：P0=`0` / P1=`0` / P2=`0` / P3=`1`（`P3-DOC-1` 的 manifest 文字部分已闭合；新开 **P3-PIN-1**：prompt pin 的脚本 SHA 与仓库内所有产物不一致）。
**范围已按要求收窄**：只核 manifest `:9`/`:13`、parser JSON 绑定、脚本未变更、Gate/风险状态未被改动。**未重跑全量源码审查**。

---

## 一、四项必查项的独立结果

### 检查 1｜manifest `:9` → **通过（CLOSED）**
现文（`manifest:9`）：「本对象=`R4_REVISION_FROZEN_FOR_INDEPENDENT_REVIEW`；当前 manifest/script bytes 须经**第四轮**独立 Review 与 Codex adjudication 后，才可按本 Task 运行一次只读采集。前三轮 Review 均为 `CHANGES_REQUESTED`，已逐轮记录并修订；**R3 发现项（路径快照状态、manifest 轮次文字、`Get-Acl` 失败时保留直接 entry count）已按 R4 修订，等待本轮 Review 与 Codex adjudication**。」

- ✅ 三项 R3 发现项被逐项点名（路径快照状态 = R3-P2-1；manifest 轮次文字 = R3-P3-1；`Get-Acl` 失败保留 count = R3-P3-2）。
- ✅ 明确“已修订 + 等待本轮 Review/adjudication”，**未出现任何“已通过/已批准”字样**，与前三轮均为 `CHANGES_REQUESTED` 的事实一致。
- ✅ 不再有“R2 冻结”的滞后声明（R3 窄范围复核时该段末括注与 R4 头部不同步的问题已消除）。

### 检查 2｜manifest `:13` → **通过（CLOSED）**
现文（`manifest:13`）：「……R4 parser command 只用 Windows PowerShell 5.1 `ScriptBlock::Create` 解析脚本，不执行脚本；**host capture 仅在当前 R4 冻结内容通过独立 Review 和 Codex adjudication 后单独调用**。」

- ✅ “第二轮 Review”这一过期前置条件（R3-P3-1 的残余）已删除。
- ✅ 指向**当前 R4** 独立 Review + Codex adjudication，与 `:9` 一致，无自相矛盾。
- ✅ 仍保留“执行 shell 精确路径/参数/CWD”与“parser 不执行脚本”的边界描述，未被改写。

**附带确认**：`manifest` 仅 `:9`/`:13` 两行被改，其余段落（12 根/13 leaf/3 canary/36 环境变量/WER 两键四值/4 组 Git 命令/protected 清单/`:16-17` 写入语义/`:71` 分类新规/`:73` 停机规则）与 R4 复核时逐字一致，未见夹带变更。

### 检查 3｜parser JSON 内容与绑定 → **字段与内部一致性全部通过；外部 hash 绑定见 P3-PIN-1**
`verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json`（33 行，2086 bytes）：

| 要求 | JSON 实际内容 | 结果 |
|---|---|---|
| Windows PowerShell `5.1.26100.9549` | `childParseResult.powershellVersion` = `5.1.26100.9549`（与 `processExitCode`、child stdout 内 JSON 一致） | ✅ |
| `ScriptBlock::Create` | `parser` = `[System.Management.Automation.ScriptBlock]::Create` | ✅ |
| `PARSE_OK` | `parseStatus` = `PARSE_OK`，`parseError` = `null` | ✅ |
| 进程 exit `0` | `childParseResult.processExitCode` = `0` **且** 顶层 `processExitCode` = `0` | ✅ |
| `captureScriptInvoked=false` | 同名布尔字段 = `false`（父/子两处 JSON 一致） | ✅ |
| 精确脚本 byte count | `inputByteCount` = `38729`（子、父两处一致） | ✅ |
| 精确脚本 SHA | `inputSha256` = 子/父/child stdout 内 JSON **三处一致** | ⚠ 与 prompt pin 不符，见 P3-PIN-1 |
| 进程内父级复核匹配 | `parentRecheck.matchesChildInput` = `true`，且字节数/SHA 与 child 相同 | ✅（绑定设计成立） |
| 保留原始 stderr bytes/hash/base64 | `childStderr.byteCount` = `382`、`sha256` = `4F2B…B1EF`、`base64` 齐备；解码可见 `#< CLIXML` 与 `System.Management.Automation.PSCustomObject`/`Progress`/记录文本，与“仅 PowerShell 启动进度、非脚本错误”一致 | ✅ |
| 子进程 stdout 原始证据 | `childStdout.byteCount` = `351` + `sha256` + 内嵌 `utf8` 文本 | ✅（超出要求） |

- **绑定机制评价**：父进程把**自己重新计算的** `inputByteCount`/`inputSha256` 与子进程 stdout 内嵌 JSON 做 `matchesChildInput` 对照 —— 这正是本次要求的“同一证据中 parser 输入/hash/result 绑定”，在**该证据内部自洽**（三处 SHA 相同、字节数与 pin 相同、exit/状态一致）。相对 R3 的缺陷（我当时指出“parse 输入与冻结 bytes 未绑定”），**该缺口已在证据层面闭合**。
- **唯一未能闭合的部分**：我无法验证“证据里记录的 38729 bytes / SHA”就是**磁盘上这份 capture 脚本**（本环境无法复算，见 §二），而且 prompt 给出的该 SHA 与证据记录不一致（P3-PIN-1）。

### 检查 4｜脚本未变更 → **通过（无需重跑全量审查）**
- 窄范围定点核对了本修订版最关键的 12 处锚点，全部与 R4 全量审查时的行号/文本一致：`ps1:167`（`ACL_QUERY_ERROR`）、`:172`（`ACL_UNVERIFIABLE`）、`:336`/`:537`/`:539`/`:542`（`originalStopReason` 双字段）、`:442`（复核映射 `QUERY_ERROR`）、`:473`/`:474`（含 `ACL_QUERY_ERROR` 的错误计数）、`:475`（`pathAclUnverifiableCount`）、`:513`（`hostPathSnapshots` 分层判定）、`:546`（**唯一** `CreateNew` 写入）。
- 全文件对 `New-Item`/`Out-File`/`Set-Content`/`Add-Content`/`Remove-Item`/`Set-Acl`/`Set-ItemProperty`/`New-ItemProperty`/`CreateAppContainerProfile`/`DeleteAppContainerProfile` 的检索**零命中** —— 写入面仍只有那一次 `CreateNew`，无 registry/ACL/profile/canary 变更。
- 结论：脚本内容与 R4 已审版本一致（`grep` 行号与 R4 报告引用逐项吻合），**未发现需要重开全量源码审查的材料性不一致**。

### 检查 5｜Gate 与 owner-risk 状态未被改动 → **通过**
- 本次修订只改 manifest `:9`/`:13` 两行文字，未触及任何 Gate/风险字段。
- 全库检索确认以下状态**原样保留**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Windows Sandbox 仍在范围外。
- `verification/P02/p02pre-r1-evidence-20261011.json` 经 glob 确认**仍不存在**（唯一运行结果未产生），符合“复审/adjudication 通过前禁止 capture”。
- **本 Review 不是 Gate PASS，也不授权任何 Gate 变更。**

---

## 二、Review 范围与不可核验项（如实声明）

**本轮已做（只读）**

- 读取 `manifest` `:1-20` 与 `:44-73`（覆盖全部 73 行中被改动段落与其上下文）、`parse-r4-20261011.json` 全 33 行；对 capture 脚本作窄范围定点核对（行号锚点 + 禁止写入操作检索）；确认证据 JSON 不存在。

**明确不可核验**

1. **bytes/SHA-256 未独立复算**：本会话 `pwsh` 工具仍在沙箱准备阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）；按指令未做 ACL 修改、未提权重试、未绕行、未换 shell。因此 Task `16148`/manifest `12598`/script `38729`/R4 报告 `18995`/parser JSON `2086` bytes 与各自 SHA-256 的**匹配均未经我独立确认**（内容级审查成立，hash 级绑定未成立）。
2. **未执行任何命令**：未运行 capture、未调用 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash、未 build/Cargo/AC、未改 Gate 或 Task 状态、未写任何文件。
3. 未读取任何用户漫画/库/数据库/凭据/权重内容；未重跑 R4 全量源码审查（按指令，仅在脚本未变的前提下收窄）；未复核 scratch 实际 HEAD/tree；未复核 Plan/STATUS/COLLABORATION 文本。
4. **静态复核与 parser 证据都不证明脚本已运行或任何宿主/OS 条件通过。**

---

## 三、新 finding

### P3-PIN-1｜prompt pin 的脚本 SHA 与仓库内全部产物不一致（第三位十六进制字符分歧）
- **位置**：prompt 声明 `capture=38729 bytes / SHA-256 97400A9E**F16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`；而 `parse-r4-20261011.json` 的 `childParseResult.inputSha256`、`parentRecheck.inputSha256`、`childStdout.utf8` 内嵌 JSON **三处一致**为 `97D00A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`；manifest `:2-3` 同步的字节数与我在 R4 报告中从中读取的字节数也均为 38729。
- **触发**：无所谓运行触发，是一处**文字/证据 pin 分歧**；在无法复算 hash 的环境下无法自行判定哪一侧为真。
- **影响**：(a) 我**无法确认** `parse-r4` 产物所解析的 38729-byte 文件就是 prompt 所指的、R4 已审脚本（外部 hash 绑定未成立）；(b) 若分歧出在 prompt pin（更可能，因为仓库内三处证据互相一致，且该值与我 R4 报告中引用的值相同），则仅需更正 pin 文字；(c) 若分歧出在证据侧（即磁盘文件自 R4 报告后发生了变化），则意味着当前冻结对象可能未被完整审查——这会推翻本轮“脚本未变更”的前提。
- **最小修复（二选一，均为机械操作，无需重跑全量审查）**：
  1. 由具备复算能力的一方（Codex，非本 Reviewer 环境）对 `verification/P02/p02pre-r1-capture.ps1` 计算 SHA-256：
     - 若得 `97D0…84AB`（与 `parse-r4` 证据一致）→ 在 Round 4 窄范围 prompt/manifest 引用处更正 pin 文字为 `97D0…84AB`，并在 Task 中记录该笔误更正即可；
     - 若得 `9740…84AB`（与 prompt pin 一致）→ 说明 `parse-r4` 产物的 `inputSha256`（三处）写错或所解析文件非本脚本，必须重出 parser 证据并在证据中绑定修正后的 hash（此时需重开**聚焦**复核，仍可不必重跑源码审查）。
  2. 可选加强：在 parser 证据中增加“解析前后对同一路径各算一次 hash 并比对”的字段，使“所解析字节 = 所声明字节”在同一次运行内可得证，而非依赖父进程二次读取。
- **不构成放行阻塞**：该项**不影响脚本正确性，也不引入任何副作用风险**；它只影响“本轮 pin 的脚本 == R4 已审脚本”这一**绑定声明**的可证性。

---

## 四、历史 finding 处置总表（本轮最终）

**Round 1（11 项）**：`P1-1` 64 MiB 零证据 → `CLOSED`；`P1-2` Git status 非原始字节 → `CLOSED`；`P2-1` home 拼接断言 → `CLOSED`；`P2-2` QUERY_ERROR/ACL 停止条件 → `CLOSED`；`P2-3` reparse 祖先链 → `CLOSED`；`P2-4` enum 数值化 → `CLOSED`；`P2-5` 枚举显示名 → `CLOSED`；`P2-6` `.git` metadata reparse → `CLOSED`；`P3-1` finally 掩盖 stopReason → `CLOSED`；`P3-2` WER last-write 标记 → `CLOSED`；`P3-3` NUL 计数口径 → `CLOSED`。（依据：R4 全量审查 + 本轮 `ps1:167/172/336/442/473-475/513/537-542/546` 锚点复核。）

**Round 2（5 项）**：`P2-1` partial 覆盖 stopReason → `CLOSED`（`ps1:336/537/539/542`）；`P2-2` WER registry 未进 fail-stop → `CLOSED`（**更正为上一轮误报**，旧版已含；现为显式拆分 `ps1:473-478`）；`P2-3` 空 owner/SDDL 假 PASS → `CLOSED`（`ps1:172/442/475/513`）；`P3-1` 写失败异常未带 stopReason → `CLOSED`（`ps1:555`）；`P3-2` whoami 解码口径 → `CLOSED`（`ps1:73-75/290`）。

**Round 3（3 项）**：`P2-1` `ACL_UNVERIFIABLE` 可致 `hostPathSnapshots=PASS` → `CLOSED`（`ps1:513` 先 `FAILED`、再 `UNPROVABLE`）；`P3-1` manifest 轮次自述 → `CLOSED`（`manifest:9` 现为 R4，含“须第四轮 Review”，无虚假批准；`manifest:13` 已完成本轮针对性修改，见 §一.2）；`P3-2` `Get-Acl` 异常丢弃 metadata/count → `CLOSED`（`ps1:152-167` 先建记录/先取 count 再取 ACL；`:472` 用已知正数判非空）。

**Round 4 全量审查的 `P3-DOC-1`（manifest 两处过期文字）→ 本轮判定 `CLOSED`**：`:9` 与 `:13` 均已改为指向当前 R4 Review/adjudication，无残留“第二轮 Review”前置，无虚假批准声明。本轮新增 `P3-PIN-1` 属**pin 证据绑定**问题，与文档文字问题不同源。

---

## 五、是否可进入 Codex adjudication / 放行一次调用

- **脚本侧**：未发现新缺陷、未发现副作用面扩大；唯一写入仍是 `ps1:546` 的单次 `CreateNew`；R4 判定的“无脚本缺陷、无不可接受副作用”未被本轮推翻。
- **文档侧**：`P3-DOC-1` 已闭合；manifest 不再自相矛盾。
- **结论**：**可以进入 Codex adjudication**；但请 adjudicator 先用一次只读 hash 复算消解 **P3-PIN-1**，并在 adjudication 记录中明确写出“本轮 pin 的脚本 SHA 取 `97D0…84AB`（与 `parse-r4` 证据及 R4 报告一致）”，或按 §三.1 的另一分支重出 parser 证据。该复算与文字更正**不改变脚本字节**，因此**不需要重跑全量源码审查**；只需非作者 **极窄确认**（一行 pin 更正或一份新 parser 证据）即可。
- **在 P3-PIN-1 于 adjudication 记录中显式处置之前**，我不把本轮计为 `APPROVED`（脚本本身无开放 finding，但“pin == 已审 bytes”的绑定声明尚不可证）。上述处置完成后，本 Reviewer 认为该冻结脚本可获准执行**唯一一次**宿主只读采集（受 Codex adjudication 约束）。
- **Gates/状态保持原样**（本 Review 不授权任何变更）：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；`p02pre-r1-evidence-20261011.json` 仍不存在。

---

## 六、给下一步的最小指令（供 Codex 转发；非我方执行）

> 致 Codex（P02PRE-R1 Owner/Adjudicator）：Round 4 窄范围复核结果 `CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/0/1`。已确认：manifest `:9`（R4 冻结 + R3 三项发现已修订、等待本轮 Review/adjudication、无虚假批准）与 `:13`（host capture 指向当前 R4 Review + adjudication、无“第二轮 Review”前置）**均通过**；`parse-r4-20261011.json` 字段齐备（`5.1.26100.9549` / `ScriptBlock::Create` / `PARSE_OK` / exit 0 / `captureScriptInvoked=false` / 38729 bytes / 父级 `matchesChildInput=true` / 382-byte stderr 原始 bytes+hash+base64）且内部自洽；capture 脚本未变更（关键锚点与 R4 审查逐项吻合，写入面仍仅 `ps1:546` 一次 `CreateNew`）。唯一未闭合项 `P3-PIN-1`：窄范围 prompt 的脚本 SHA 写为 `97400A9E…84AB`，而 `parse-r4` 证据三处一致为 `97D00A9EF16E…`——请在具备复算能力的环境对 `verification/P02/p02pre-r1-capture.ps1` 执行一次只读 SHA-256：若得 `97D0…84AB`，则在 Round 4 窄范围 prompt/manifest 引用处更正该 pin 文字并在 Task 记录笔误更正；若得 `9740…84AB`，则重出 parser 证据（并在证据内绑定“解析前后同路径 hash 比对”）后交非作者极窄确认。上述处置记入 adjudication 后，方可放行**唯一一次**宿主只读采集；其间不得运行 capture、不得创建证据 JSON，Gates/barrier 维持现状。

**（本报告为静态只读窄范围复核，不证明脚本已运行，也不证明任何宿主/OS 条件通过；hash 级独立绑定未成立，见 §二.1 与 §三。）**