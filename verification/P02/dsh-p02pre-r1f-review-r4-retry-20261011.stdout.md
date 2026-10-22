# P02PRE-R1F Round 4 retry 独立 Review：修正继承 manifest hash pin

reviewer: DeepSeek Harness（非作者）
author/owner/integrator/adjudicator: Codex `/root`
baseline: repo `G:/CODEX/New Manga`，branch `main`，HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9`
**decision: `CHANGES_REQUESTED`**
**counts: P0=`0` / P1=`0` / P2=`1` / P3=`1`**

> 本轮按要求**只读、不写共享文件系统**；完整报告仅在本回复正文中返回，由外层 Codex wrapper 落盘到 retry 的 stdout/stderr/exit。

## 1. 审查对象与访问限制

| # | 对象 | pin（bytes / SHA-256） |
|---|---|---|
| 1 | `doc/tasks/P02PRE-R1F.md` | `13,685 / 4F58CEA9C751E20751C3587B0353F3E46527D57050225AD9B33B9FEB6AC31330` |
| 2 | `verification/P02/p02pre-r1f-manifest-20261011.md` | `13,682 / 91818614AB08DF6C49DF40572C101796DFC40494A2184D7FCCD00BBD5D8A8A42` |
| 3 | `verification/P02/p02pre-r1f-capture.ps1` | `56,449 / 99B1D9B158C6E9534A9CDE946AE0380C0034D0A407C67D75A8CB902E2E4E1FC7` |
| 4 | R1 交叉核对（只读字面值） | `verification/P02/p02pre-r1-manifest-20261011.md`（`12,615`）、`doc/tasks/P02PRE-R1.md:89`、`verification/P02/p02pre-r1-adjudication-20261011.md:27`、`verification/P02/p02pre-r1-evidence-20261011.json:2627`、`verification/P02/codex-checkpoint-p02pre-r1-20261011.md:38` |

**不可独立核验**：本会话 `pwsh` 工具在沙箱准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`）。因此我**没有复算任何 bytes/SHA-256**；Codex 报告的 .NET / `Get-FileHash` / `certutil` 三方一致属其本机结果。我完成的是**文件内容与字面值核对**，下述结论不依赖复算，也不依赖字符串长度的机器测量。所有对象均可访问，无不可读文件。R7 parser artifact 尚不存在，与 Release procedure 的“R4 通过后再生成”一致。

**未执行**：未运行命令、parser、getter、capture、registry/profile/ACL 操作、build/Cargo、AC1–AC7、canary 或 Windows Sandbox 动作；未修改任何文件；未写共享仓库文件。

## 2. 逐项结论

### 问题 1 —— **未通过**（R1F-R4R-F1，P2）

- `Task:54`、`Task:23` 与 `Manifest:8` 引用的 R1 manifest pin 字面值均为
  `A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7`，且**同一句**把它称为“该 64 位 SHA”（`Task:54`、`Manifest:8`）。
- 该字面值**不是 64 个十六进制字符**：按 4 字符分组为
  `A551 0774 B47C 17EB 29C5 BF5D 73FE 7B75 5C72 E272 6FC5 280E 7EF1 1A91 A23C 67A7`
  —— 16 组 + 末组 4 字符之外仍有可见的第 65 位（末段为 `67A7` 而非 `67A`），即 **65 位**。SHA-256 恒为 64 位，故此 pin 仍不可解析。**更正后仍是 65 位 → `Task:23/54`、`Manifest:8` 的“64 位”标签与字面值自相矛盾。**
- **但“是否与所引 R1 来源一致”这一半在第 4 轮已成立**：我逐条读取的 R1 来源同样含 `…C67A7`（`P02PRE-R1.md:89`、`p02pre-r1-adjudication-20261011.md:27`、`p02pre-r1-evidence-20261011.json:2627` 的 `length: 12615` 记录、`codex-checkpoint-p02pre-r1-20261011.md:38`）。也就是说：**R1 的四份冻结记录本身就把该 manifest 记成 65 位（一个不可能的 SHA-256 长度），R4 之前 R1F 少写一位、现在与这些来源对齐。**
- 因此本条**不能**靠“再补/再删一位”闭合，而必须由能执行命令的一侧做**权威复算**：对磁盘上的 `verification/P02/p02pre-r1-manifest-20261011.md`（`12,615 bytes`）实际计算一次 SHA-256（结果必为 64 位），据此：
  1. 把 `Task:23`、`Task:54`、`Manifest:8` 的 pin 换成复算所得的 64 位值；
  2. 若复算值即 `…C67A`，同时把 `Task:54`/`Manifest:8` 的“R1 Task、R1 adjudication、R1 evidence 与本机三法一致为 64 位”改为准确表述；
  3. 把“R1 冻结记录（含 R1 evidence 的 `sha256` 字段与 checkpoint）以 65 位字面值记录该 manifest”作为**历史不一致事实**单独留证（不改写 R1 历史文件），并说明权威值来源。
- 在完成上述复算与改写前，任何后续步骤（R7 parse、pre-run adjudication、capture）都会带着一个**不可解析且自称长度错误**的继承 pin 往前走，故不能判 `APPROVED`。
- **关于“R1 未被修改”**：我未复算 R1 任何文件，只能做一致性比对——R1 evidence 中该 manifest 的 `length` 仍为 `12,615`（`json:2625`），retry prompt 给出的 R1 源 pin 与我读到的字面值一致，且我未在任何 R1 文件中发现 R4 改写的痕迹。故我**未发现** R1 Task/manifest/script/evidence 被改动的证据，但这不等于我核验了它们的字节。

### 问题 2 —— **通过**（R1F-R4R-F2），但附一条文档不一致（P3）

脚本 delta 与声明一致、无行为变化：

- 新增块 `:617-629`（相对上一版 `:614-619` 的扩展）仅向受保护 hash 清单追加 9 个路径，全部位于 `verification/P02/`：
  - R7 parser（未来产物）：`p02pre-r1f-parser-windows-powershell-5.1-r7-20261011.json`（`:618`）；
  - 第一次 R4 dispatch 的失败诊断：`dsh-p02pre-r1f-review-r4-20261011.{prompt.md,stdout.md,stderr.log,exit}`（`:619-622`）；
  - 本轮 retry 产物：`dsh-p02pre-r1f-review-r4-retry-20261011.{prompt.md,stdout.md,stderr.log,exit}`（`:623-626`）。
- 新路径只经既有 `Get-FileRecord`（`Get-PathChain` + `Get-Item` + `Get-FileHash`）读取；**注入扫描零命中**：`New-Item|Out-File|Set-Content|Add-Content|Remove-Item|Set-Acl|Set-ItemProperty|New-ItemProperty|CreateAppContainerProfile|DeleteAppContainerProfile|Start-Process|Invoke-Expression|Add-Type|Registry::|SHA256.HashData`。
- 未引入任何新子进程、新 getter 类型、新写入或新执行路径；`ps1` 行数由 758 → 768，增量可完全由该清单展开解释。
- **P3（R1F-R4R-F3）**：`Manifest:16` 仍写“最终 Round 3 frozen script 必须先 Review=`APPROVED`，再产生并核对 **R6** parser artifact”，与 `Manifest:48`（R4 retry → **R7** parser）及 `Task:32/37` 的 R7 目标不一致。属陈旧 R3 视角行；若被当作最终 parser 目标会与 Release procedure 冲突。

### 问题 3 —— **通过**（安全/验收边界与既有 finding 无回归）

- **唯一写入未变**：`:753` 仍为 `[IO.File]::Open($EvidencePath, [IO.FileMode]::CreateNew, [IO.FileAccess]::Write, [IO.FileShare]::None)`，即 `Manifest:22` 的唯一目标；无 append/overwrite/retry/cleanup/transcript/temp。
- **执行器与子进程 allowlist 未变**：冻结的 `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` 与 exact argv；仅 `git.exe` 五条固定只读命令（rev-parse / symbolic-ref / status / ls-files / ls-files --stage）与 `whoami.exe /all`；registry 只读（`OpenSubKey(..., $false)`、`DoNotExpandEnvironmentNames`）；ACL 仅 `Get-Acl`。
- **tracked-symlink 边界未变**：仅 leaf ∧ mode=`120000` ∧ `ReparsePoint` 三条件同时成立才 `SKIP_TRACKED_SYMLINK`，记 metadata（`targetRead=NOT_ATTEMPTED`/`targetHash=NOT_CAPTURED`）后 `break`，不 follow/hash/ACL-query 目标；其余 reparse/mode 不符、submodule、非 regular、非目录 parent、路径越界一律 fail-stop。
- **未新增** profile/API/registry 写/ACL 变更/canary/build/Cargo/AC1–AC7/Sandbox 动作；**用户数据排除未变**（受保护 hash 目标仍仅限项目治理文档与 `verification/P02/**`）。
- **先前 finding 未回归**：R1F-R2-F1（`:535` 仍 `$null = Assert-InventoryPolicySelfCheck`）、R1F-R2-F2（`:703` `repositoryOmittedCountKnown` 仍要求两仓 `candidateCountKnown=true`，否则 `repositoryOmittedPaths=null`）、R1F-R2-F3（清单无 R5，含 R6 与 R7；r5 零命中）均保持 Round 3 已关闭状态。

## 3. Finding 表

| ID | 级别 | 文件/行 | 证据 | 影响 | disposition |
|---|---|---|---|---|---|
| **R1F-R4R-F1** | **P2** | `doc/tasks/P02PRE-R1F.md:23`、`:54`；`verification/P02/p02pre-r1f-manifest-20261011.md:8` | 三处 pin 字面值为 65 位 `A5510774…C67A7`（分组计数 16×4 + 第 65 位），却自称“该 64 位 SHA”；同一 65 位字面值亦见 `P02PRE-R1.md:89`、`p02pre-r1-adjudication-20261011.md:27`、`p02pre-r1-evidence-20261011.json:2627`、`codex-checkpoint-p02pre-r1-20261011.md:38`（即 R1 记录本身即为 65 位） | 继承 pin 仍不可解析，且“64 位”标签与字面值矛盾；会把**未权威复算**的 pin 带入 R7 parse、pre-run adjudication 与 capture，并可能让后续裁决误以为该 pin 已被核对 | **open**；由可执行命令的一侧对 `p02pre-r1-manifest-20261011.md`（`12,615 bytes`）复算 SHA-256，按 §2 问题 1 的 1/2/3 改写 `Task:23/54` 与 `Manifest:8`，并把“R1 记录以 65 位字面值记录该 manifest”作为历史不一致留证 |
| **R1F-R4R-F3** | P3 | `verification/P02/p02pre-r1f-manifest-20261011.md:16` | 仍写“最终 Round 3 frozen script……再产生并核对 **R6** parser artifact”，与 `:48`（R4 retry → **R7**）及 `Task:32/37` 不一致 | 同一 manifest 内 parser 轮次命名冲突；若被当作最终 parser 目标，会与 Release procedure 的前置条件冲突 | **open**；与 F1 同批把 `:16` 更新为 R4/R7，或显式标注“历史行，最终以 `:48` 为准” |

**未发现 P0/P1 问题**：本轮脚本 delta 纯为受保护 hash 清单增量，未扩张执行、getter 或写入面；唯一 `CreateNew` 输出、执行器与子进程范围、tracked-symlink no-follow、registry/ACL 只读性、用户数据排除与五态风险分类均与冻结契约一致。

## 4. 结论

- **`CHANGES_REQUESTED`（P0/P1/P2/P3 = 0/0/1/1）**。按本 Task 放行标准（须“无 open finding 的 `APPROVED`”），本轮**不释放** R7 parse-only、capture 或任何 Gate。
- 最小必要修复：仅需一次权威 SHA-256 复算 + `Task:23/54`、`Manifest:8` 的 pin 与其“64 位/来源一致”表述改写（并顺带 `Manifest:16` 的 R6→R7 陈旧行）。**脚本本身无需再改**；若其字节不变，可继续使用 `56,449 / 99B1D9B1…4E1FC7`，但 Task/manifest 需重新冻结 bytes/SHA 并由非作者窄范围复审。
- **不可独立核验项**：全部 bytes/SHA-256（含 R1 manifest 的真实值）；字符串长度的机器测量；R7 parser 是否存在与是否 `PARSE_OK`；R1 文件字节是否未被改动（仅做了一致性比对，未复算）。本轮结论完全建立在**文件内字面值与结构核对**上。

**保留的治理状态（原样不变）**：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`；Windows Sandbox 未触碰。

**声明**：静态、只读、基于文件内容的审查**不是运行期证据**，不证明宿主身份、仓库状态或 ACL/WER/TEMP-cache 实际结果，也不构成任何 Gate PASS 或 Build 授权。
