# P02PRE-R1F Round 3 独立 Review

reviewer: DeepSeek Harness（非作者）
author/owner/integrator/adjudicator: Codex `/root`
baseline: repo `G:/CODEX/New Manga`，branch `main`，HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9`；工作区既有 dirty/untracked 内容按原样保留

## 1. 本次审查的确切对象与访问限制

| # | 对象 | pin（bytes / SHA-256） | 我实际读到的内容 |
|---|---|---|---|
| 1 | `doc/tasks/P02PRE-R1F.md` | `11,487 / 736C470C01199D268E64C65CEE0497A26026EB8F3441A9879DDAC9FA32E05F21` | 76 行全文 |
| 2 | `verification/P02/p02pre-r1f-manifest-20261011.md` | `12,368 / C19171CC5991733DD419C4C7E6BD74B506FA6E649196EFBBE261E19E3EDA9F98` | 47 行全文 |
| 3 | `verification/P02/p02pre-r1f-capture.ps1` | `55,603 / 4FB853E696D2BDF86BA48D5C7C45E006D90356C66EB450D6856AD55B89F37D54` | 755 行全文 |
| 4 | `verification/P02/p02pre-r1f-r2-selfcheck-20261011.json` | `1,548 / FE1989875B773AF7C02CB3A05CA9ED25AA9F7AB7581F57D4CB3D77CE055DDB96` | 29 行全文 |
| 5 | `verification/P02/dsh-p02pre-r1f-review-r2-20261011.stdout.md`（仅 finding 上下文） | — | 引用其 R1F-R2-F1/F2/F3 三行定义 |

**限制**：本会话 `pwsh` 工具在沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），因此我**没有独立复算任何 bytes/SHA-256**，Codex 声明的 .NET/`Get-FileHash`/`certutil` 三方一致属其本机结果，我未复现。我完成的是**内容级**核对：pin 字面值与其在文件内自述、以及跨文件引用的一致性。**五个对象全部成功读取，无不可访问文件。**

**未执行**：未运行任何命令、PowerShell parser、capture script、host getter、OS/token/path/ACL/TEMP-cache/WER/registry 查询、Build/Cargo、AC1–AC7；未编辑或创建任何仓库文件。R3 Review artifacts（`dsh-p02pre-r1f-review-r3-*`）与 R6 parser artifact（`…-r6-20261011.json`）此刻均**尚不存在**（glob 实测），与其在 Task/Manifest 中的“待生成”状态一致，不属缺失。

## 2. 决定与计数

**决定：`APPROVED`**（无 open finding）
**计数：P0=`0` / P1=`0` / P2=`0` / P3=`0`**

## 3. Findings 与逐项裁定

### 3.1 Round 2 三项 P3（本次重点）

| ID | 级别 | 位置 | 证据 | 裁定 |
|---|---|---|---|---|
| **R1F-R2-F1** | P3 | 调用点 `capture.ps1:535`；函数 `:114-121` | `:535` 现为 `$null = Assert-InventoryPolicySelfCheck`，显式丢弃函数输出；`:115-120` 六条 `if (...)` 的比较结果因而不再进入流水线。旁证：`p02pre-r1f-r2-selfcheck-20261011.json:7/11-26` 记录 `sourceSha256=4FB853E6…F37D54`、`parsedErrors=0`、`extractedFunctions=["Get-InventoryAction","Assert-InventoryPolicySelfCheck"]`、`policySelfcheck=PASS`、`capturedPipelineOutputCount=0`、`captureScriptInvoked=false`、`hostGetterInvoked=false`、`registryOrAclWriteInvoked=false` | **`CLOSED`**。**范围界定**：该证据是 **Codex 自己的、范围受限的 PS 5.1.26100.9549 隔离自检**（Manifest `:14` 亦明确标注“不是独立 Review 或 Gate PASS”，Task `:69` 记为 `PASS_WITH_EVIDENCE`）。它只证明“在 5.1 下抽取这两个纯内存函数并运行后，流水线输出计数为 0”；我确认这与 `:535` 的 `$null =` 语义、以及 `:115-120` 不产生其它 Write-Output 的事实相符。它**不**提供任何宿主执行证据，也不证明整个 capture 脚本可在 5.1 下成功运行 |
| **R1F-R2-F2** | P3 | `capture.ps1:668`、`:669`、`:690-691` | `:668` `$repoOmittedCountKnown = @($repoRecords \| Where-Object { $_.candidateCountKnown -ne $true }).Count -eq 0`（两仓均 `true` 才为 `$true`，包括“仓记录缺失/未解析”时 `candidateCountKnown` 非真 → 判 false）；`:669` `if ($repoOmittedCountKnown) { Measure-Object -Sum } else { $null }`；`:690-691` 分别落 `repositoryOmittedCountKnown` 与 `repositoryOmittedPaths`（后者可为 `null`）。与 Manifest `:36` 逐字要求一致 | **`CLOSED`** |
| **R1F-R2-F3** | P3 | 受保护清单 `capture.ps1:614` | 清单中**已无** `…-r5-20261011.json`（该路径从未生成，Task `:30`/`:71` 说明 Round 2=`CHANGES_REQUESTED` 故未创建）；现含 `…-r6-20261011.json`（当前清单中唯一的最终 parser 目标；r5 字符串全文检索为 0 命中）。Manifest `:47` 明确“**R6 parser artifact 必须在 capture 前存在且其 source hash/byte count 与 Review-approved script 完全相同**”，Task `:35` 同步 | **`CLOSED`**。附注：脚本仍会把尚未生成的 R6 记录为 `ABSENT`，但 Release procedure 已把“R6 必须存在且 hash 匹配”写成 capture 前置条件，`pre-run adjudication` 会先行拦截，语义闭环 |

### 3.2 更早的 Round 1 F1–F5（复核确认，未被本次改动破坏）

| ID | 级别 | 证据 | 裁定 |
|---|---|---|---|
| F1 | P1 | `Set-RepositoryStop`（`:262-268`）仍存在，12 个 fail-stop 调用点齐全（`:276/284/289/293/299/309/331/336/345/390/392/401/405`），`omittedCount` 依据 `candidateCountKnown`（`:267`）区分“未知 → `null`”与“已知 → `max(0,count-processed)`”；`:271` 初始化 `candidateCountKnown=$false`/`omittedCount=$null`，`:341-342` 解析成功后置真 | `CLOSED` |
| F2 | P2 | `:145` `StringComparer.OrdinalIgnoreCase`；`:336` `GIT_FILE_INVENTORY_PARSE_FAILED`；`:345` `GIT_INDEX_STAGE_PARSE_FAILED`（均带 `errorOperation` 与异常说明）；`:174-183` case-only 碰撞与 invalid UTF-8 的 self-check | `CLOSED` |
| F3 | P2 | Manifest `:8` 为 64 位 `A5510774…A23C67A`，并声明只修正本 manifest、不改历史 adjudication | `CLOSED` |
| F4 | P3 | `:372` 字段名 `mode`（值 `120000`） | `CLOSED` |
| F5 | P3 | `:371-378` skip 后 `break`，`:376` 不变量注释，`:382` `continue`；Manifest `:32` 同步该不变量 | `CLOSED` |

### 3.3 本轮新发现

**无。** 在记录范围内未发现问题。

## 4. 范围 / 安全面核查（明确通过项）

- **只读范围**：`:738` 仍是全脚本**唯一**写入点（`[IO.File]::Open($EvidencePath, FileMode::CreateNew, Write, None)` = Manifest `:21` 唯一目标）；全文检索 `New-Item/Out-File/Set-Content/Add-Content/Remove-Item/Set-Acl/Set-ItemProperty/New-ItemProperty/Add-Type/Start-Process/Invoke-Expression/Registry::` **零命中**；无 profile create/delete、无 canary 写、无 build/Cargo/AC、无 Sandbox。
- **子进程 allowlist 未扩张**：仅 `git.exe` 五条固定命令（`:295` rev-parse、`:297` symbolic-ref、`:311` status、`:325` ls-files、`:327` ls-files --stage）与 `whoami.exe /all`（`:549`）；`:91` 前缀（`--no-optional-locks` + 三项 `-c` + `-C "<root>"`）与 Manifest `:20` 一致；无 shell/package manager/compiler/network/COM/helper。
- **身份与 Git 目标门**：`:560-566` 先判 `whoami` exit 与 user/SID，通过后才取 main，再取 scratch（`:568-572`）；两仓均以固定 root/common-dir/HEAD/tree/branch 比对（`:308`）。
- **tracked-symlink 语义**：`:107-112` 决策矩阵仍为“**仅** leaf ∧ mode=`120000` ∧ `ReparsePoint` → `SKIP_TRACKED_SYMLINK`”；`:371-378` 只记 `path/mode/attributes/linkType/targetRead=NOT_ATTEMPTED/targetHash=NOT_CAPTURED` 后 `break`，**未**调用 `Get-FileHash`/`Get-Content`/`Get-Acl`；`:379` 其余 reparse/mode/container、`:380` 非目录 parent、`:357` 路径越界一律 fail-stop。
- **注册表只读 / ACL 只查**：`:419` `OpenSubKey(path, $false)`、`:432` `DoNotExpandEnvironmentNames`；`:252`、`:631` 仅 `Get-Acl`。
- **分类未被拔高**：`:35` `private_registry_absence=UNPROVABLE`；`:41` `werEffectivePolicy=UNPROVABLE`；`:40`/`:709`？→ `tempCache` 恒 `UNPROVABLE`（`:709` 附近）；`:39`/`:701` `process_and_path_access_closure` 恒 `UNPROVABLE_NOT_MONITORED_IN_R1F`；`:36-37`/`:707`/`:711` 恒 `REQUIRES_ACTIVE_TEST`；`:38` `product_build_and_ac1_ac7=NOT_RUN`；`:703` `repositoryProtectedInventory` 仅“无 repo 失败且无 skip”才 `PASS_WITH_EVIDENCE`。
- **PS 5.1 静态兼容**：本次改动仅新增 `$null =` 抑制（`:535`）、一个布尔聚合与一个 `if` 表达式赋值（`:668-669`）、清单字符串增删（`:614`），均为 5.1 合法构造；全文检索 `SHA256.HashData` **零命中**（R2 wrapper 因 PS 5.1 缺该 .NET API 而失败的教训已被避开）。
- **Task/Manifest/script 对齐**：Task `:30`/`:35`/`:69-72` 与 Manifest `:11-15`/`:34-36`/`:47` 的轮次、pin、R4/R5/R6 归属与 `NOT_RUN` 状态相互一致；Manifest `:47` 的 Release procedure 已包含“Round 3 `APPROVED` → R6 parser 必须先于 capture 存在且 hash 匹配 → pre-run adjudication 核对全部 pins”，未见指向旧 pin 的过期待办。

## 5. 声明

- **静态审查不是运行证据**：本 Review 不证明任何宿主身份、仓库状态、ACL/WER/TEMP-cache 实际结果，也不证明该脚本可在 Windows PowerShell 5.1 下成功运行；R6 parser 与 R1F capture 均为 `NOT_RUN`。
- **本 Review 不释放 capture、不构成任何 Gate PASS、不是 Build 授权、也不是任何 AC 结果。**
- **保留的治理状态（原样不变）**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`；Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。未查询、安装、启用或启动 Windows Sandbox。
- **建议下一步（非本 Review 授权）**：Codex 在本 Task 内记录 Round 3 `APPROVED (0/0/0/0)` 的 adjudication，随后按 Manifest `:47` 生成 `p02pre-r1f-parser-windows-powershell-5.1-r6-20261011.json` 并核对 source bytes/hash 为 `55,603 / 4FB853E6…F37D54`，再做 pre-run pins 核对；全部符合后方可执行唯一一次 capture。
