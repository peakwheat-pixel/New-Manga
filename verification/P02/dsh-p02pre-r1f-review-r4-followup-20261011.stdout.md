# P02PRE-R1F Round 4 follow-up Review（F1 计数争议与 F3 修正）

reviewer: DeepSeek Harness（非作者）
author/owner/integrator/adjudicator: Codex `/root`
baseline: repo `G:/CODEX/New Manga`，branch `main`，HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9`
**decision: `APPROVED`**
**counts: P0=`0` / P1=`0` / P2=`0` / P3=`0`**

> 本轮只读、不写共享文件系统；完整报告仅在本回复正文返回，由外层 Codex wrapper 落入 follow-up 的 stdout/stderr/exit。

## 1. 审查对象与限制

| # | 对象 | pin（bytes / SHA-256） |
|---|---|---|
| 1 | `doc/tasks/P02PRE-R1F.md` | `14,476 / 0C0A8E9D1B20DB6DCDD9026C9BFA65A07942C808F64A49BF8855353F5D576BFD` |
| 2 | `verification/P02/p02pre-r1f-manifest-20261011.md` | `14,116 / 21B62A57BA49FB328381B07B81C2649A3831095A663819C4D2327AED88F9176E` |
| 3 | `verification/P02/p02pre-r1f-capture.ps1` | `56,785 / 666D819646CF9558630356FF7AE7206C6A4587856CBCD2BC3BA317E9105FA980` |
| 4 | R1 来源（交叉核对） | `verification/P02/p02pre-r1-manifest-20261011.md`（`12,615`）、`doc/tasks/P02PRE-R1.md:89`、`verification/P02/p02pre-r1-adjudication-20261011.md:27`、`verification/P02/p02pre-r1-evidence-20261011.json:2627` |

**不可独立核验**：本会话 `pwsh` 工具仍在沙箱准备阶段失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`），因此我**没有复算任何 bytes/SHA-256**；Codex 的 .NET / `Get-FileHash` / `certutil` 三方结果属其本机证据。以下结论完全建立在**文件字面值与十进制/十六进制算术**之上。所有对象均可访问；R7 parser artifact 与 follow-up 三个产物尚不存在，与流程一致。**未执行**任何命令/parser/getter/capture/registry/ACL/build/AC/Sandbox 动作；未修改任何文件。

## 2. 逐问结论

### 问题 1 —— **F1 计数争议：Codex 正确，我上轮的 P2 是误报（`CLOSED`，我方撤回）**

我逐字符重数了字面值
`A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`：

`A551`(1–4) `0774`(5–8) `B47C`(9–12) `17EB`(13–16) `29C5`(17–20) `BF5D`(21–24) `73FE`(25–28) `7B75`(29–32) `5C72`(33–36) `E272`(37–40) `6FC5`(41–44) `280E`(45–48) `7EF1`(49–52) `1A91`(53–56) `A23C`(57–60) `67A7`(61–64)

**恰好 16 组 × 4 = 64 个十六进制字符**，符合 SHA-256 长度；末尾 `7` 是第 64 位（位于末组 `67A7` 内），并不存在第 65 位。我在 R4 retry 报告中把末组误读为 `67A` 并据此宣称“第 65 位”，**该计数错误**，由此提出的 P2（R1F-R4R-F1）**不成立，予以撤回**。

其余两点也随之成立：
- `Task:54`、`Manifest:8` 的“该 64 位 SHA / 64 个十六进制字符”标签**与字面值一致**，不存在自相矛盾；
- 该 pin 与所引 R1 来源字面一致（`P02PRE-R1.md:89`、`p02pre-r1-adjudication-20261011.md:27`、`p02pre-r1-evidence-20261011.json:2627` 的 `length: 12615` 记录、`codex-checkpoint-p02pre-r1-20261011.md:38`），且 `Task:23` 已补充“（64 个十六进制字符）”说明。我未发现任何 R1 Task/manifest/script/evidence 被本轮改写的痕迹（但字节级未改动无法由复算证明——见 §4）。

### 问题 2 —— **F3 已修正（`CLOSED`）**

`Manifest:16` 现文为：“PS 5.1 parser R4 (`D60A…8FEFF`) 实际匹配历史 script；R5 (`20C9…3CBF9F`) 是 Round 2 预定 parser target，但因 Round 2=`CHANGES_REQUESTED` 未创建。**R6=`PARSE_OK` 仅绑定 Round 3 旧脚本，不满足当前候选验收。Round 4 retry Review=`CHANGES_REQUESTED (0/0/1/1)`；其 P3-F3 指出本行最后句仍引用 R6，已更新为最终须先有 R4 follow-up=`APPROVED`，再对冻结 script 产生并核对 R7 parser artifact。**”

- R6 已被明确定性为“**仅**绑定 Round 3 旧脚本的历史证据、不满足当前候选验收”，不再被写成最终 artifact；
- 该行现在与 `Manifest:48`（Release procedure：R4 follow-up `APPROVED` → 对同一 exact script bytes 产出唯一 **R7** parser，且 **R7 必须在 capture 前存在且 source hash/byte count 与 Review-approved script 完全相同**）以及 `Task:32`/`Task:37`（final parser = `…-r7-20261011.json`；R6 为历史）**完全一致**，无残留冲突。

### 问题 3 —— **脚本 delta 纯增量、无行为变化（通过）**

`:617-631` 的受保护 hash 清单为**纯增量**，新增路径全部位于 `verification/P02/`：

| 类别 | 路径 | 行 |
|---|---|---|
| R7 parser（未来产物） | `p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json` | `:618` |
| 第一次 R4 dispatch 失败诊断 | `dsh-p02pre-r1f-review-r4-20261011.{prompt.md,stdout.md,stderr.log,exit}` | `:619-622` |
| R4 retry 产物 | `dsh-p02pre-r1f-review-r4-retry-20261011.{prompt.md,stdout.md,stderr.log,exit}` | `:623-626` |
| 本轮 follow-up 产物 | `dsh-p02pre-r1f-review-r4-followup-20261011.{prompt.md,stdout.md,stderr.log,exit}` | `:627-630` |

- 与 `Task:47` 的写入范围、`Manifest:14`/`:48` 的说明逐项对齐；未出现 R5 路径（零命中）。
- 新路径只经既有 `Get-FileRecord`（`Get-PathChain` + `Get-Item` + `Get-FileHash`）读取，**不新增**子进程、getter 类型或写入。
- 注入扫描**零命中**：`New-Item|Out-File|Set-Content|Add-Content|Remove-Item|Set-Acl|Set-ItemProperty|New-ItemProperty|CreateAppContainerProfile|DeleteAppContainerProfile|Start-Process|Invoke-Expression|Add-Type|Registry::|SHA256.HashData`。
- 三个关键不变量原样保留：`:535` `$null = Assert-InventoryPolicySelfCheck`；`:707` `repositoryOmittedCountKnown`（两仓 `candidateCountKnown=true` 才为 true，否则 `repositoryOmittedPaths=null`）；`:757` 唯一 `[IO.File]::Open($EvidencePath, [FileMode]::CreateNew, Write, None)`。

### 问题 4 —— **既有安全边界与 finding 未回归（通过）**

- 唯一写入仍为 `Manifest:22` 的目标，且在 `:757` 以 `CreateNew` 一次创建；无 append/overwrite/retry/cleanup/transcript/temp。
- 执行器与子进程 allowlist 未变：冻结的 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` + exact argv；仅 `git.exe` 五条固定只读命令与 `whoami.exe /all`；registry 只读（`OpenSubKey(..., $false)`、`DoNotExpandEnvironmentNames`）；ACL 仅 `Get-Acl`。
- tracked-symlink 边界未变：仅 leaf ∧ mode=`120000` ∧ `ReparsePoint` 三条件同时成立才 `SKIP_TRACKED_SYMLINK`，记 metadata（`targetRead=NOT_ATTEMPTED`/`targetHash=NOT_CAPTURED`）后 `break`，不 follow/hash/ACL-query 目标；其余 reparse/mode 不符、submodule、非 regular、非目录 parent、路径越界一律 fail-stop。
- 未新增 profile/API/registry 写/ACL 变更/canary/build/Cargo/AC1–AC7/Sandbox；用户数据（漫画/库/数据库/Lock/Revision/模型/凭据/WER dump 内容）排除未变。
- 历史 finding 状态保持：Round 1 F1–F5 = `CLOSED`；Round 2 R1F-R2-F1/F2/F3 = `CLOSED`；Round 3 通过项未回归；R4 retry 的 F3 本轮 `CLOSED`，其 F1 经复核**撤回**（我方误报）。

## 3. Finding 表

| ID | 级别 | 文件/行 | 结论 |
|---|---|---|---|
| R1F-R4R-F1（R1 pin 65 位计数） | — | `Task:23/54`、`Manifest:8` | **撤回**：字面值为 16 组 × 4 = **64** 位，与标签及 R1 来源一致；系我上轮误读末组。无 open finding |
| R1F-R4R-F3（陈旧 R6 引用） | — | `Manifest:16` | **`CLOSED`**：R6 已定性为历史证据，最终要求为 R4 follow-up `APPROVED` → R7 parser，与 `Manifest:48`、`Task:32/37` 一致 |
| 本轮新增 | — | — | **无**（P0/P1/P2/P3 = 0/0/0/0） |

## 4. 结论

- **`APPROVED`（P0/P1/P2/P3 = 0/0/0/0）**。就本候选的 **Task / manifest / script exact bytes**（`14,476 / 14,116 / 56,785`，SHA 见 §1）而言，无 open finding。
- 本决定**仅释放下一步 R7 PS 5.1 `ScriptBlock::Create` parse-only**：须对**同一组** script bytes 产出 `verification/P02/p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json`，其 source bytes/SHA 必须与 `56,785 / 666D8196…FA980` 完全相同，且 `PARSE_OK`、`captureScriptInvoked=false`。
- 本决定**不释放 capture**（仍须 R7 parser 存在 + Codex pre-run adjudication 逐一核对全部 pins/身份/HEAD/tree/output absent），**也不构成任何 Gate PASS 或 Build 授权**。
- **不可独立核验项**：所有 bytes/SHA-256（含 R1 manifest 的真实值、本候选三文件的真实值）、字符串长度的机器测量、R1 文件字节是否未被改动、R7 parser 的状态。以上均以文件内容与算术为依据，不依赖命令执行；如需 hash 级绑定，应由具备复算能力的一侧完成并在 adjudication 中记录。

**保留的治理状态（原样不变）**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Windows Sandbox 未触碰。

**声明**：静态、只读、基于文件内容的审查不是运行期证据，不证明宿主/仓库/ACL/WER/TEMP-cache 实际状态，也不构成任何 Gate PASS。
