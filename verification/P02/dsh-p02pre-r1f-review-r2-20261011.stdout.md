# Independent Review Round 2：P02PRE-R1F（tracked symlink no-follow）

reviewer: DeepSeek Harness（非作者）
author/owner/integrator/adjudicator: Codex `/root`
base_commit / reviewed_head: `cddff58469b56e181019a8ddfeade80684bc7eb9`（branch `main`；工作树 dirty，以下 exact pins 定义本次交付）

## 一、Reviewed Task ID 与精确 inputs

- Task：`P02PRE-R1F`
  `doc/tasks/P02PRE-R1F.md` = `10,192 bytes / SHA-256 79CD06C91D5091A3320832A9AD3B8606D6EC7E2E3F7912A27C5240F92294C98A`（我读取 73 行全文）
- Manifest：`verification/P02/p02pre-r1f-manifest-20261011.md` = `10,490 bytes / SHA-256 23AF217DBE050CCC4D15990DDBE231CD2DCE3A3E0976637B388430D35C2BE218`（43 行全文）
- Script：`verification/P02/p02pre-r1f-capture.ps1` = `55,065 bytes / SHA-256 20C9D1C2C8FBE87D9EFFA84C14A29B17363958B9D95D7D47C02960BC5A3CBF9F`（753 行全文）
- 上下文（仅用于核 F1–F5 处置与 pin 链）：Round 1 `verification/P02/dsh-p02pre-r1f-review-20261011.stdout.jsonl`、`verification/P02/p02pre-r1f-adjudication-20261011.md`

**可访问性**：四个 pin 与两份上下文全部成功读取，**无不可访问或明显不符的文件**。R5 parser artifact（`…-r5-20261011.json`）**尚不存在**（glob 实测）——与 Manifest `:12`/Task `:30` 声明的“Round 2 通过后再生成”一致，不属缺失。

---

## 二、Architecture / 安全面结论

| 项 | 结论 | 依据 |
|---|---|---|
| 唯一写入口 | `PASS_WITH_EVIDENCE` | 全文仅 `:738` 一处 `[IO.File]::Open(..., CreateNew, Write, None)` = Manifest `:18` 唯一目标；`New-Item/Out-File/Set-Content/Add-Content/Remove-Item/Set-Acl/Set-ItemProperty/New-ItemProperty/Add-Type/Registry::/Start-Process/Invoke-Expression` 检索零命中 |
| 子进程 allowlist | `PASS_WITH_EVIDENCE` | 仅 `git.exe`（`:294` rev-parse、`:296` symbolic-ref、`:310` status、`:324` ls-files、`:326` ls-files --stage）与 `whoami.exe /all`（`:548`）；`UseShellExecute=$false`（`:52`） |
| Git 参数逐字一致 | `PASS_WITH_EVIDENCE` | `:91` 前缀 `--no-optional-locks -c core.quotepath=false -c core.fsmonitor=false -c core.untrackedCache=false -C "<root>"`；五条命令与 Manifest `:17` 列举完全相同 |
| registry 只读 | `PASS_WITH_EVIDENCE` | `:419` `OpenSubKey($subPath, $false)`；`:432` `DoNotExpandEnvironmentNames`；无 SetValue/DeleteKey |
| ACL 仅查询 | `PASS_WITH_EVIDENCE` | `:252`、`:631` 仅 `Get-Acl`；无 `Set-Acl` |
| tracked symlink skip 边界 | `PASS_WITH_EVIDENCE` | `:107-112` 决策矩阵：**仅** `isLeaf ∧ mode=120000 ∧ ReparsePoint` → `SKIP_TRACKED_SYMLINK`；`:371-378` 记 `mode/attributes/linkType/targetRead=NOT_ATTEMPTED/targetHash=NOT_CAPTURED` 后 `break`，**未**调用 `Get-FileHash`/`Get-Content`/`Get-Acl`；`:379` 其余 reparse/mode/container 一律 `STOP`；`:380` 非目录 parent `STOP`；`:357` 路径越界 `STOP` |
| 自检先于一切查询 | `PASS_WITH_EVIDENCE` | `:535-537` 在任何身份/Git/路径查询前依次运行三个内存 self-check（`:114-121`、`:123-128`、`:166-184`） |
| 单命令对象断言 | `PASS_WITH_EVIDENCE` | `:69` `[pscustomobject][ordered]`；`:101-105` 断言单对象且含 `exitCode`；6 处调用（`:295/297/311/325/327/549`） |
| 五态分类未拔高 | `PASS_WITH_EVIDENCE` | `:35` `private_registry_absence=UNPROVABLE`；`:41`/`:709`？→ `:41` `werEffectivePolicy=UNPROVABLE`；`:40`/`:709` `tempCache=UNPROVABLE`（实为 `:709`）；`:39`/`:701` `UNPROVABLE_NOT_MONITORED_IN_R1F`；`:36-37`/`:707`/`:711` `REQUIRES_ACTIVE_TEST`；`:38` `product_build_and_ac1_ac7=NOT_RUN`；`:703` `repositoryProtectedInventory` 仅“无 skip 且无 repo 失败”才 `PASS_WITH_EVIDENCE` |
| 未宣称 registry absence / profile / 有效 WER policy / 瞬时闭包 / hardlink-ADS / 动态子进程 / Build | `PASS_WITH_EVIDENCE` | `:646` ACL scope 自限；Task `:23`/`:41`、Manifest `:33`/`:37`/`:39` 一致 |
| PS 5.1 语法兼容（静态） | `PASS_WITH_EVIDENCE` | 新增 `Set-RepositoryStop`（`:262-268`，普通函数名）、`Dictionary[string,string]::new(comparer)`（`:145`）、`$null =` 抑制、`if` 表达式赋值，均为 5.1 可用构造；未使用 PS7-only API |

---

## 三、Round 1 findings 逐项裁定

| ID | 级别 | 处置 | 独立证据 |
|---|---|---|---|
| **F1** | P1 | **`CLOSED`** | 新增统一 `Set-RepositoryStop`（`:262-268`），对每条 fail-stop 分支写入 `state`/`errorOperation`/`error`/`firstBlockingPath`，并在 `candidateCountKnown=true` 时算 `omittedCount`。已逐条核对 12 个调用点：`:276`（root/gitDir 链）、`:284`（Get-Item 失败）、`:289`（root/`.git` 非普通目录）、`:293`（index pre-hash）、`:299`（Git baseline）、`:309`（target mismatch）、`:331`（status/ls-files 非 0，含逐命令退出码）、`:336`（`GIT_FILE_INVENTORY_PARSE_FAILED`）、`:345`（`GIT_INDEX_STAGE_PARSE_FAILED`）、`:390`（`PROTECTED_HASH_FAILED`，带 `$currentOperation`/`$currentRelativePath`）、`:392`（`PROTECTED_INVENTORY_INCOMPLETE`，带计数）、`:401`（`GIT_METADATA_INVALID`，取首个非 PRESENT 记录或 `.git\index`）、`:405`（`TARGET_OR_INDEX_MISMATCH`）。可数性语义成立：初始化 `candidateCountKnown=$false`、`omittedCount=$null`（`:271`）；解析成功置 `true` 并把 `omittedCount` 置为候选总数（`:341-342`）；`:267` 的 `if` 表达式保证“未知不使用 0 冒充”。partial 亦输出 `candidateCountKnown`/`omittedCount`/`firstBlockingPath`/`errorOperation`（`:477`、`:483-489`） |
| **F2** | P2 | **`CLOSED`** | 两条解析路径均显式映射 stop state：`:335-336` → `GIT_FILE_INVENTORY_PARSE_FAILED`；`:344-345` → `GIT_INDEX_STAGE_PARSE_FAILED`，两者均带 `errorOperation` 与异常说明；`:145` 改用 `StringComparer.OrdinalIgnoreCase`；`:174-176` 增加 case-only 碰撞 self-check；`:177-183` 增加两条 invalid UTF-8 必须被拒的 self-check |
| **F3** | P2 | **`CLOSED`** | Manifest `:8` 现为 64 位 `A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A`，并注明“历史 adjudication 的 65 位复制错误在此修正、不改写历史”；与 R1 Task `:52` 记录一致；我**未**发现任何针对旧 R1 文件的改写 |
| **F4** | P3 | **`CLOSED`** | `:372` 字段名已为 `mode`（值 `120000`），与 Manifest `:29` 的字段清单一致 |
| **F5** | P3 | **`CLOSED`** | `:371-378` skip 分支 `break` 后即 `continue`（`:382`），加 `:376` 不变量注释；Manifest `:29` 明确“记录后立即跳出组件检查并继续下一个 candidate，不再对该 path 调用任何 `Get-*`、hash 或 ACL query” |

**其余指定检查项**：受保护清单仍要求 `120000`+live reparse 双条件（`:108`）；mode/属性不符、reparse parent、untracked reparse、`160000`、非 `100644/100755`、非目录 parent、路径越界全部 fail-stop（`:109-110`、`:379-380`、`:357`）— `PASS_WITH_EVIDENCE`。parser/计数 self-check 为纯内存操作，不调用 capture、不触发 host getter — `PASS_WITH_EVIDENCE`。

---

## 四、Round 2 findings

| ID | 级别 | 文件/行 | 影响 | 建议修正 |
|---|---|---|---|---|
| **R1F-R2-F1** | **P3** | `p02pre-r1f-capture.ps1:115-120` | `Assert-InventoryPolicySelfCheck` 内 6 条 `if (...) {...}` 的比较结果会被 PowerShell 隐式写到函数输出流（仅失败时 `throw`）。该函数以语句形式调用（`:535`），因此 6 个字符串会在任何真实查询前进入流水线输出，最终混入外层 wrapper 的 stdout 日志。不影响安全与证据内容，但若 wrapper stdout 被机器解析会产生噪声 | 逐行改为 `$null = (Get-InventoryAction ...)`，或在调用处写 `$null = Assert-InventoryPolicySelfCheck` |
| **R1F-R2-F2** | **P3** | `p02pre-r1f-capture.ps1:668`、`:689`；对照 `:267`、Manifest `:31` | `$repoOmittedCount = (@($repoRecords | ForEach-Object { $_.omittedCount } \| Measure-Object -Sum).Sum)`：当某仓 `omittedCount=$null`（`candidateCountKnown=false`，该仓尚未解析文件列表）时，`Measure-Object -Sum` 会把 `$null` 当 0，于是 `summary.repositoryOmittedPaths=0`。这会在“未知省略量”的语义上重新出现 F1 要避免的“未知显示为 0”，虽然仓级 `omittedCount=null` 与 `candidateCountKnown=false` 已如实保留 | 在 summary 增列 `repositoryOmittedCountKnown`（=两仓 `candidateCountKnown` 均为 true），或对含 `$null` 的仓把该聚合值也置 `null`，并在 Manifest 说明该聚合的已知性 |
| **R1F-R2-F3** | **P3** | `p02pre-r1f-capture.ps1:614`（受保护 hash 清单） | 清单已含 R5 parser 目标 `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r5-20261011.json`，但该文件在 Round 2 批准后才创建；若 capture 在 R5 生成前被调用，该条会被 `Get-FileRecord` 记为 `ABSENT`（`:215` 路径）→ `invalidHashCount>0` → `stopReason=QUERY_ERROR_OR_ACL_PATH_DRIFT_OR_HASH_INCOMPLETE`，并按 Manifest `:43` 顺序在“核 pins”阶段本应已被拦住。这不是安全缺陷，而是**执行顺序耦合**：R5 parser 必须先于 capture 存在 | 在 Manifest `:18` 或 Release procedure `:43` 明确“R5 parser artifact 必须在 capture 前的 pin 检查中已存在且匹配”，或在脚本中对未生成的 R5 **预期 ABSENT** 做显式白名单声明 |

**未发现 P0/P1/P2 级问题**：F1–F5 五项均实质闭合且未引入新的安全面扩张；写入面、子进程面、registry/ACL 只读性、分类边界与 R0 已接受的 runner 残余风险声明均与冻结契约一致。

---

## 五、结论

**decision：`CHANGES_REQUESTED`**（仅因 3 项 P3；`P0/P1/P2/P3 = 0/0/0/3`）

- **F1–F5 全部关闭**，且关闭方式可核（统一 stop 函数 + 逐分支字段、两条解析路径显式 stop state、OrdinalIgnoreCase + case-collision self-check、64 位 pin、字段名 `mode`、skip 后不再查询的不变量注释）。
- 三项 P3 均为**可读性/聚合语义/顺序耦合**，不涉及越权读取、写入、profile、registry、ACL、canary、build 或 AC；不影响只读安全边界。
- 若 Codex 选择按上述最小建议修正（预计改动集中在 `:115-120`、`:668`/`:689`、`:614` 附近与 manifest 一句），则需重新冻结三文件 bytes/SHA 并再走一次窄范围复审 + PS 5.1 R5 parse；若选择**不改脚本**，至少应在 adjudication 中把 R1F-R2-F1/F2 记为已接受的已知限制、把 R1F-R2-F3 写进 Release procedure 的前置条件——但**不应**保持现状文字与行为不动而直接放行。
- **建议下一 Task**：无需新 Task；由 Codex 在本 Task 内做上述最小处置，随后以同一非作者 Reviewer 做一次只核三项 P3 与 R5 parser pin 的窄范围复审。

---

## 六、限制与不可核验项

1. **未独立复算任何 bytes/SHA-256**：本会话 `pwsh` 工具仍在沙箱准备阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）。prompt 与 Manifest `:11` 声明的 .NET/`Get-FileHash`/`certutil` 三方一致属 **Codex 本机结果**，我未复现；我完成的仅是**文件内容级**核对（pin 字符串与文件内自述值一致）。**无文件不可访问**。
2. **未运行任何命令**：未执行或解析 capture 脚本、未调用 PowerShell/Git/OS/token/path/ACL/environment/registry/WER、未建删 profile、未改 ACL/registry、未写 canary、未 build/Cargo、未跑 AC1–AC7；未编辑任何文件（本报告由派发方保存）。
3. **未读取**：用户漫画/数据库/Lock/Revision/模型/凭据/WER dump 内容、任何 symlink 目标内容或其解析结果、R1 旧 JSON 的 Base64 与路径清单。
4. **静态审查不产生运行证据**：本 Review 仅证明“按源码与冻结文本，契约自洽、边界受控”；**不证明**宿主身份、仓库状态、ACL/WER/TEMP-cache 实际结果，也不证明脚本能在 5.1 下成功运行（R5 parser 仍 `NOT_RUN`）。R1F capture 亦仍 `NOT_RUN`。
5. **本次 Review 不是 capture release、不是 Gate PASS、不是 Build 授权、也不是任何 AC 结果。** 建议维持：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。
