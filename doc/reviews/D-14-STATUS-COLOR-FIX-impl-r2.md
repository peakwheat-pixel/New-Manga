---
task_id: D-14-STATUS-COLOR-FIX
reviewer: DSH 独立子 agent（impl-r2 Reviewer；独立上下文，未参与实现）
reviewer_kind: subagent
author: DSH（D-7 故障转移实施会话；实现 5ecc1e4c6，补正 c48ea5e3c）
base_commit: 195422c2fdf72f0460d2e265b53e22a2c5eff6fd
prompt_head: f38a1a920cc5655e249d24cbe1cb605097b008d7
reviewed_head: f38a1a920cc5655e249d24cbe1cb605097b008d7
implementation_head: 5ecc1e4c6e1b99a9b53ad0d9bcd11d7489ee36e2
delivery_commit: c48ea5e3cc7acd16b4c56ed3fa701bebde7a6b0e
prior_review: doc/reviews/D-14-STATUS-COLOR-FIX-impl-r1.md（changes_requested，P0=0/P1=3/P2=7）
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 1
p2: 5
provenance:
  agent: DSH 独立子 agent（checkpoint §157 记录的 impl-r2 workflow job workflow-fd5083d9e2414d79）
  appointment: 用户本轮 D-14 impl-r2 指令；DSH 按 D-9 派发（2026-10-31 裁决：作者可派独立上下文子 agent）
  implementation_participation: none
  mode: read_only_except_this_report
  date: 2026-11-03
---

# Review：D-14-STATUS-COLOR-FIX（impl-r2）

## 0. 结论

**verdict = changes_requested（P0=0 / P1=1 / P2=5）。**

- **产品代码与测试仍然正确**：`StatusCatalog.ColorKey(StatusKind.NotStarted)` 为 `NmKeys.Color.Text.Secondary`，XML 注释同步，其它八值未变；定向 `D14StatusNotStartedTests` 3/3 PASS；无过滤全量 **1292 passed / 0 failed / 57 skipped**（EXIT=0，逐程序集与日志逐项一致）；build 0 warning / 0 error；check PASS(3)；pins 15/15；四张 FEA-06 PNG SHA 未变；默认运行零仓库写入；未 push；无越权产品改动。
- **唯一 P1 仍是证据纪律未闭合**：补正后的 `impl-verification.log` 增加了 shell/SDK/host/base/head、完整命令、EXIT、逐程序集计数、差值与 `NOT_RUN`，数字复核全部正确；但 (a) 头部的 SDK 行与实测不符（`dotnet --version` 为 **10.0.401**，非 9.x），shell 行未写解释器路径；(b) 57 条 skip 仍只有程序集汇总与“xUnit 环境 skip”笼统原因，没有逐条名称/原因，直接违反 ADJ:149 与 Q-009 ③；(c) `reviewed_head` 仍写 r1 的 `b2c41226d`，本次 r2 的固定头是 `f38a1a920`。故 r1 D14R1-001 只能算“部分闭合”，不能批准。
- **r1 的另两个 P1**：D14R1-002 已按 Q-009 ② 诚实记为 `NOT_RUN`，可接受（但仍无执行 artefact，判别力只有静态证明）；D14R1-003 的 Handoff 已存在且事实基本一致，但不符合 HANDOFF 模板与 09 §5 的“至少记录”字段，降为 P2。
- **5 个 P2**：canonical evidence pin 把 c48 的 worktree SHA 绑在 `5ecc1e4c6` 上（commit/SHA 不可同时复现）；Handoff 模板/字段不完整；STATUS:10 与 Task 生命周期指针滞后；r1 的 7 个 P2 只在 Handoff 登记了 3 个；日志时间戳/base/reviewed_head 口径不一致。均为文档/证据层，**不需要改产品代码**。
- 建议：做一次**纯文档/证据补正提交**（不碰 `Status.cs` 与测试），补齐 57 条 skip 审计、修正头部与 pin、按模板补 Handoff、更新 STATUS/status；随后 r3 只审该增量。

## 1. 范围与依据

- **固定点**：`reviewed_head = f38a1a920cc5655e249d24cbe1cb605097b008d7`（本报告唯一有效头；仅 checkpoint 文档变更）。`base_commit = 195422c2f`；实现提交 `5ecc1e4c6`（`c1619cede..5ecc1e4c6`，3 文件 +52/−2）；补正提交 `c48ea5e3c`（`b2c41226d..c48ea5e3c`，4 文件 +164/−9）。
- **交付范围**：`git show --name-only 5ecc1e4c6` = `Status.cs`、`D14StatusNotStartedTests.cs`、`impl-verification.log`；`git show --name-only c48ea5e3c` = Handoff、r1 Review、Task 卡、证据日志。全部落在 Task `allowed_paths`（`:21–27`）；`git diff --stat 5ecc1e4c6 HEAD -- apps/desktop-avalonia` 为空（补正未改产品代码）。
- **依据**：[ADJ-2026-11-03-D14-STATUS-NOTSTARTED](ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md) 裁决 A（`:20`）、§4 实施/测试要求（`:122–137`）、可复制验证（`:149`）；[Task D-14](../tasks/D-14-STATUS-COLOR-FIX.md) `allowed_paths`（`:21–27`）、IN/OUT（`:38–39`）、验收（`:42–49`）、交付（`:52`）；[09 协作协议](../09_COLLABORATION.md) §4（`:63–89`）、§5 Handoff（`:191–199`）、§12 Q-009（`:288`）；[HANDOFF 模板](../templates/HANDOFF.md) front matter（`:2–8`）、交付/验证（`:12–22`）、下一任务建议（`:28–40`）、风险（`:42–44`）；[REVIEW 模板](../templates/REVIEW.md) 证据纪律（`:54`）与批准门槛（`:56`）。
- **未覆盖/不覆盖**：HighContrast 主题与原生 200% DPI 实机；V2 Studio/Shell 的运行时渲染（Task `:39` 已列 OUT）；旧 FEA-06 证据的重新审查（只核字节未变）；r1 报告本身不重审。

## 2. Standards（可选视角，executed）

- **写域**：交付/补正提交的全部文件均在 allowed_paths；`Styles/**`、`Themes/**`、`Generated/**`、`App/**`、`Host/**`、`ApplicationCore/**` 在 `c1619cede..5ecc1e4c6` 与 `5ecc1e4c6..HEAD` 的产品路径 diff 为空。**PASS**。
- **裁决 A 实现面**：只改一个映射与一条注释；未新增颜色令牌、枚举值或 API 字段；未改其它八值、样式、令牌、生成物。**PASS**。
- **证据纪律**：09 `:288` Q-009 ①③、ADJ `:149` 要求 shell/解释器、环境、base/head、逐命令 EXIT、逐程序集、**逐条 skip 原因**。补正版增加了大部分字段，但 SDK 行与实测不符、shell 无路径、57 条 skip 未逐条列出。**FAIL → D14R2-001（P1）**。
- **判别力 artefact**：日志显式记 **NOT_RUN**，符合 Q-009 ② 的降级口径；静态可证映射断言在修前必失败（修前返回 Disabled，测试断言 Secondary），但没有执行 red-run。**PASS（NOT_RUN，接受）**，残余见 §8。
- **Handoff**：文件已存在，提交/变更/验证/限制/交接事实基本一致；但缺 HANDOFF 模板 front matter、AC 逐项表、实际命令表、独立的未跑项清单（red-run `NOT_RUN` 只在证据行一句带过；HighContrast/DPI、V2 运行时未列）、下一任务建议（模板标“必填”），且未引用证据 SHA，却自称“完整格式”。**PARTIAL → D14R2-003（P2）**。
- **Canonical Evidence pin**：Task `:59,65` 的 SHA 289384 与当前 worktree 一致，但同一行 `commit 5ecc1e4c6` 处的该文件是旧 12 行版本（原始 blob SHA-256 `4451e3ae…`），c48 的 LF blob 为 `d57d0caf…`；check.ps1 在 `in_progress` 下不校验证据表，即使进入 `in_review` 也只查“commit 含路径 + worktree SHA”，不查 SHA 是否等于该 commit 的 blob。**FAIL → D14R2-002（P2）**。
- **生命周期/指针**：`doc/STATUS.md:10` 仍写“下一步：实施 D-14（ready；owner=codex…）”，与 `:7` 的 in_progress/已实施矛盾；Task `status: in_progress` 而 r2 Review 已派发（09 `:73` 要求 reviewed head 固定后进入 `in_review`）。**FAIL → D14R2-004（P2）**。
- **Fowler baseline**：仍命中既有 **possible Duplicated Source of Truth**（V2 三处 NotStarted 前景与 catalog 分裂）与 **possible Obsolete Comment**（FEA-06 测试仍写“catalog still says Text.Disabled”）；均为既有债、本卡 OUT，未扩大。**判断项，非硬性违规**。

## 3. Spec（可选视角，executed）

- **A 的核心要求已忠实实现**：`Status.cs:85` = `NmKeys.Color.Text.Secondary`，`:75` 注释同步；与 `Controls.Status.axaml` 的 glyph/普通状态文字 Secondary 一致；未改其它八值与 `MutedColorKey`。**MET**。
- **AC 覆盖缺口（既有 P2，非本卡新增）**：ADJ `:130` 要求“其他八值映射、`○`、‘未开始’、`ClassName`、`MutedColorKey(NotStarted)==null` 保持原义，覆盖 `StudioStates.ColorTokenKey(NotStarted)`”；现状 `CustomControlsTests.cs:33` 与 `V2StudioMathTests.cs:127` 只有前缀断言，八值精确键、`MutedColorKey`、`StudioStates.ColorTokenKey` 的 Secondary 均无断言（D14R1-010，仍 open）。本卡 diff 只改一行，事实未变。
- **ADJ `:123` 的 FEA-06 特判**与 **`:125` 的 V2 两处前景**未在本卡执行；Task `:39` 将其列为 OUT，Handoff 已登记，但不能宣称“产品状态前景已统一”。
- **无 scope creep**：除 3 个交付文件与文档补正外，无行为改动；未改生成物、冻结设计、Schema、Core、Host/IPC、依赖或用户数据。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| D14R2-001 | P1 | `verification/D-14-STATUS-COLOR-FIX/impl-verification.log:3,13`；同见 Handoff `:13`、checkpoint `:1018` | canonical evidence 仍未满足 ADJ `:149` / Q-009 ①③：① shell 仅“pwsh 7”，无解释器路径；SDK 写“.NET 9（dotnet --version 9.x）”，但本机 `dotnet --version` = **10.0.401**（SDK 9.0.308/10.0.401 并存、无 global.json），同日早些时候 FEA-06 Handoff 也记 SDK 10.0.401/net9.0；② 57 条 skip 只有“Host 28 + CoreClient 22 + App 7 = 57（xUnit 环境 skip）”，没有逐条名称/原因，且实际原因不是“xUnit 环境”，而是 fixture 自跳过（`NEWMANGA_CORECLIENT_SIDECAR_DIR` 未设置/sidecar 缺失，App 另有 BOOK-FIXTURE）；③ `reviewed_head: b2c41226d` 是 r1 头，r2 固定头为 `f38a1a920`。影响：同一 P1 仍未闭合，证据日志按 Q-009 仍属“不可复核”的摘要；事实数字正确不能替代 artefact。 | `dotnet --version`；`dotnet --list-sdks`；全量日志 57 条 `[SKIP]`；`HostFixture.TryGetSidecarDirectory`/`SidecarFixture`/`RunControllerTests` 的 reason 字符串；`git rev-parse HEAD` = `f38a1a920` | 追加 `skip-audit`（57 条测试名 + 逐条 reason，可挂 TRX/console 原件）；头部改为 `pwsh 7.6.8 (C:/Program Files/PowerShell/7/pwsh.exe)`、`dotnet SDK 10.0.401 / net9.0`、`baseline_commit 832103393`、`head 5ecc1e4c6`、`reviewed_head f38a1a920`；同步修正 Handoff/checkpoint 的“57 skip 原因/完整格式”措辞。数字 1292/0/57 可保留。 | open |
| D14R2-002 | P2 | `doc/tasks/D-14-STATUS-COLOR-FIX.md:59,65` | Task 的 Canonical Evidence 行把 `sha256=289384…` 绑在 `commit=5ecc1e4c6`：5ecc 处该文件是旧 12 行版（原始字节 SHA-256 `4451e3ae…`，Git blob `0d11916d3`）；c48 的 LF blob 为 `d57d0caf…`（2108 bytes），当前 worktree 为 CRLF 2125 bytes、SHA-256 `289384…`。即同一 (commit, sha) 不对应同一 artefact；check.ps1 在 `in_progress` 下跳过证据表，进入 `in_review` 后也只校验 commit 含路径 + worktree SHA，抓不到该错配。影响：pin 不能从记录的 commit 复现；跨 LF checkout 时 289384 也会失配。 | `git cat-file blob 5ecc1e4c6:…` → 4451e3ae；`git cat-file blob c48ea5e3c:…` → d57d0caf；worktree `Get-FileHash` → 289384；check.ps1 `:660–714` | 把 commit 改为 `c48ea5e3c` 并改用 LF blob SHA `d57d0caf…`（同时加 `.gitattributes` `verification/D-14-STATUS-COLOR-FIX/** text eol=lf`，与仓库其他 pinned evidence 一致）；或保留 289384 但在 Task/Handoff 明确标注“Windows worktree/CRLF 口径”并加 eol 规则。 | open |
| D14R2-003 | P2 | `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md:1–21` | Handoff 已存在，5ecc/3 文件/1292/0/57/限制/交接事实基本一致；但不符合 HANDOFF 模板与 09 `:193–195` “至少记录”：无 front matter（task_id/author/recipient/base_commit/delivery_head/status）、无 AC 逐项表、无实际命令表、无独立未跑项清单（red-run `NOT_RUN` 只在证据行一句带过；HighContrast/DPI、V2 运行时未列）、无启动/复现方式、无模板标“必填”的下一任务建议、未引用证据 SHA；`:13` 自称“完整格式”而实际不完整，`:18` “未实现：无”易被读成“无未测项”。影响：恢复/集成/closeout 字段缺失。 | 逐行对照模板 `:2–8,:12–22,:28–40,:42–44`；`Get-Content` 全文 21 行 | 按模板重写（front matter、AC 对照表、命令/结果、未跑项、残余 P2 全表、下一任务建议、证据 SHA），保留 5ecc 与 c48 引用；`未实现` 改为“范围未实现=无；未测项=…” | open |
| D14R2-004 | P2 | `doc/STATUS.md:7,10`；`doc/tasks/D-14-STATUS-COLOR-FIX.md:6,10,49` | STATUS `:10` 仍写“下一步：实施 D-14-STATUS-COLOR-FIX（ready；owner=codex…）”，与 `:7` 的 in_progress/已实施矛盾；Task `status: in_progress`，但 r2 Review 已派发，09 `:73` 要求交付 head/AC/Handoff/canonical evidence 就绪后进入 `in_review`；Task `:49` 写“基线 1292/0/57”，把修后数当基线，未写 1289→1292。影响：恢复入口与门禁口径仍误导（D14R1-008 未闭合）。 | 三处对照；`git rev-parse HEAD`；本轮全量 1292 | 在补正提交中把 Task 置 `in_review`、更新 STATUS `:10` 为“impl-r2 审查中/待集成”，Task `:49` 改为“基线 1289→交付 1292，只增不减”；保留历史字节。 | open |
| D14R2-005 | P2 | `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md:17`；r1 findings D14R1-004/006/007/008/009/010 | Handoff 的“已知 P2”只列 3 项（FEA-06 特判、V2 三处、NUL 历史债），r1 的另外 4 项未在 Handoff/Task 当前记录中登记：D14R1-007（对比度用例直接取 `Text.Secondary`，不从 catalog 解析；`D14StatusNotStartedTests.cs:30`）、D14R1-008（STATUS 滞后）、D14R1-009（Host TileChannel 偶发 flake；本轮未复现）、D14R1-010（`CustomControlsTests.cs:33`/`V2StudioMathTests.cs:127` 仅前缀断言，无 `MutedColorKey`/StudioStates 精确断言）。已核实的 open 项：FEA-06 注释仍称“catalog still reports Text.Disabled”（`FluentResidual2StateEffectiveTests.cs:529–531,558–563`）；V2 三处仍 Disabled（`StudioTheme.axaml:49–50`、`V2LocalStyles.axaml:191–192`、`Statuses.cs:71`），而 `StudioStateKind.cs:58` 经 catalog 返回 Secondary，分裂仍在；全仓仍有 14 个受跟踪 md 含 NUL（D-14 卡/Handoff/日志已无 NUL/VT）。影响：残余 P2 可能在后续卡丢失，或误以为已统一。 | 逐项代码/样式对照；`git ls-files '*.md'` 字节扫描；r1 报告 | 在 Handoff 增“残余 P2 登记”表，逐项列 7 个 r1 P2 + 本轮新增 P2 的 disposition（deferred/open）；明确 D-14 **未**统一 V2 前景；NUL 债务给出数量与代表路径，另立清理项。 | open |
| D14R2-006 | P2 | `impl-verification.log:1,3`；`Handoff:1`；`checkpoint:1015,1018` | 元数据口径不一致：日志“07:55 补正”/Handoff“07:56”/checkpoint“08:00”，而 c48 提交时间为 **07:50:37**（文件 mtime 07:50:30）；日志 `base: 832103393` 是 1289 基线提交，Task `base_commit` 是 `195422c2f`，应标 `baseline_commit`；`reviewed_head: b2c41226d` 是 r1 头，r2 为 `f38a1a920`。影响：恢复/复核时口径混淆，不改变事实数字。 | `git show --format=fuller c48ea5e3c`；三文件对照 | 与 D14R2-001/002 同一次补正：改时间戳、`baseline_commit`、`reviewed_head`（或标 `r1_reviewed_head`）；checkpoint 保留历史记录但加“实际提交 07:50:37”。 | open |

## 5. 先前 findings 处置

| 先前 ID | r1 级别 | 本轮处置 | 说明 |
|---|---|---|---|
| D14R1-001 | P1 | **部分闭合，仍 P1** | 日志结构大幅补全、数字正确；SDK/路径、57 条 skip 逐条原因、reviewed_head 仍不合 Q-009/ADJ:149 → D14R2-001。 |
| D14R1-002 | P1 | **闭合为 NOT_RUN（接受）** | 日志 `:15` 显式记 `NOT_RUN`，不以推断冒充；静态判别成立（修前 Disabled ≠ Secondary）。仍无执行 red-run artefact，属残余风险，不阻断。 |
| D14R1-003 | P1 | **部分闭合，降 P2** | Handoff 已存在且事实基本一致；模板/必填字段缺失 → D14R2-003。 |
| D14R1-004 | P2 | open/deferred | FEA-06 特判与旧注释仍在（已核实），本卡 OUT。 |
| D14R1-005 | P2 | **D-14 卡已闭合** | Task/Handoff/日志无 NUL/VT；全仓 14 个受跟踪 md 仍有 NUL，归入 D14R2-005 的债务登记。 |
| D14R1-006 | P2 | open/deferred | V2 三处 Disabled 与 catalog Secondary 分裂仍在（已核实）。 |
| D14R1-007 | P2 | open/deferred | 对比度用例仍直接取 `Text.Secondary`（`:30`），未从 catalog 解析。 |
| D14R1-008 | P2 | open | STATUS `:10` 未改；Task `:49` 改为 1292 但口径仍不理想 → D14R2-004/006。 |
| D14R1-009 | P2 | watch | 本轮全量未复现 Host TileChannel flake；仍登记为潜在时序抖动。 |
| D14R1-010 | P2 | open/deferred | `CustomControlsTests:33`、`V2StudioMathTests:127` 仍只有前缀断言。 |

## 6. 验证

环境：Windows 11（NT 10.0.26300.0）、`pwsh 7.6.8`、仓库 `G:\CODEX\New Manga`、`reviewed_head=f38a1a920`、`dotnet --version=10.0.401`（SDK 9.0.308/10.0.401 并存）。全量日志副本在仓外 `G:\CODEX\New Manga.workspace\agent-output\DSH\D-14-STATUS-COLOR-FIX\impl-r2-review\full-test-run.log`（非交付物）。

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 交付范围 | `git show --name-only 5ecc1e4c6`；`git show --name-only c48ea5e3c` | f38a1a920 | **PASS**：5ecc 3 文件、c48 4 文件，均在 allowed_paths；产品代码在 5ecc 后无改动 | 命令输出 |
| 映射与注释 | 读 `Status.cs:75,85`；`git diff c1619cede 5ecc1e4c6 -- …/Status.cs` | 同上 | **PASS**：仅 NotStarted→Secondary + 注释；其它八值/`MutedColorKey`/样式/令牌未动 | diff |
| 对比度独立复算（Reviewer 自写 WCAG，读 `Tokens.Dark/Light.axaml`） | `L=0.2126R+0.7152G+0.0722B`，`(Lmax+0.05)/(Lmin+0.05)` | 同上 | **PASS**：Dark Canvas **7.9566**、Panel **7.1372**；Light Canvas **6.3497**、Panel **7.0459**（均 ≥4.5）。**Disabled 对照**：Dark 2.4525/2.1999、Light 1.7970/1.9940（均 <4.5）⇒ 方向成立 | 复算脚本输出 |
| 新测试判别力（静态） | 读 `D14StatusNotStartedTests.cs:16–37`；`git show c1619cede:…/Status.cs` | 同上 | **PASS（行为）/ NOT_RUN（artefact）**：`:19` 对修前 Disabled 必失败；`:30–35` 用真实资源栈取色并复算，非静态字符串。日志已诚实记 NOT_RUN | 代码 + 复算 |
| 定向测试 | `dotnet test …/NewManga.DesignSystem.Tests.csproj --no-build --settings …/NewManga.runsettings --filter FullyQualifiedName~D14StatusNotStartedTests --nologo` | 同上 | **PASS** 3 passed / 0 failed / 0 skipped，EXIT=0 | 命令输出 |
| build | `dotnet build apps\desktop-avalonia\NewManga.sln --nologo` | 同上 | **PASS** 0 warning / 0 error，EXIT=0 | 命令输出 |
| 无过滤全量 | `dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings …/NewManga.runsettings --nologo` | 同上 | **PASS 1292 / 0 / 57**，EXIT=0；逐程序集：Appearance 21、Presentation 38、Host 51(+28 skip)、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、CoreClient 128(+22 skip)、App 653(+7 skip)；总 1349 | 仓外 `full-test-run.log`；与日志 `:12` 逐项一致 |
| skip 逐条审计（Reviewer） | 全量日志 57 条 `[SKIP]`；读 fixture reason | 同上 | **57 条名称可列**；原因均为 fixture 自跳过（sidecar 环境变量/BOOK-FIXTURE）；日志 `:13` 未逐条记录 → D14R2-001 | 日志 + fixture 源 |
| 治理检查 | `pwsh -NoProfile -File tools\governance\check.ps1` | 同上 | **PASS** `Governance check: PASS (3 warnings)`，EXIT=0；警告为 9 个非终态 Task、STATUS/PLAN 80% 预算。**注意**：Task 为 in_progress，check.ps1 不校验其 Canonical Evidence 表 | 命令输出；`check.ps1:660` |
| 证据 pin | `pwsh -NoProfile -File tools\governance\verify_pins.ps1` | 同上 | **PASS** `PIN AUDIT: PASS (all 15)`，EXIT=0；仅 15 份冻结契约，不覆盖 Task evidence pin | 命令输出 |
| 旧 FEA-06 四 PNG | `Get-FileHash -Algorithm SHA256 verification/FEA-06/screens/*.png` | 同上 | **PASS**：reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…2df5`，与 FEA-06 卡一致；`git diff 5ecc HEAD -- verification/FEA-06` 空 | 命令输出 |
| 默认运行零写入 | build/全量前后 `git status --porcelain=v1`（含 untracked） | 同上 | **PASS**：空；未写 `verification/**` 或截图 | 命令输出 |
| 未 push | `git for-each-ref --contains 5ecc1e4c6 refs/remotes`；`--contains c48ea5e3c` | 同上 | **PASS**：0 个远端 ref 含两提交；`origin/main=b1c1f5a568` | 命令输出 |
| Task 卡 NUL/VT | 字节扫描 Task/Handoff/日志 | 同上 | **PASS**：3 文件 0 个非法控制字节；Task 卡的路径/SHA 文本已恢复（pin 的 commit 绑定问题见 D14R2-002） | 字节扫描 |
| 全仓文档字符损坏 | `git ls-files '*.md'` 字节扫描 | 同上 | **14 个受跟踪 md 仍含 NUL**（如 `doc/WORKTREE_SAFETY_INVENTORY.md`、若干 tasks）；D-14 自身干净，系统性债务仍在 | 扫描结果；D14R2-005 |
| Handoff | 读全文；对照模板 | 同上 | **PARTIAL**：存在、事实基本一致；模板字段缺失 → D14R2-003 | 文件 + 模板 |
| Canonical evidence pin | 原始 blob/工作区 SHA-256 对照 | 同上 | **FAIL（P2）**：289384 是 c48 worktree CRLF，5ecc 是旧 12 行版 → D14R2-002 | `git cat-file blob` + `Get-FileHash` |
| STATUS/生命周期 | 读 STATUS `:7,10`、Task `:6,10,49` | 同上 | **FAIL（P2）**：STATUS `:10` 与 Task 状态滞后 → D14R2-004 | 文件对照 |

## 7. Architecture 结论

**PASS。** 变更限于 DesignSystem 的 `StatusCatalog.ColorKey` 单点映射与 DS 测试；无共享 wire/Schema/依赖/数据访问变化，无新增颜色令牌或双重色契约，无分层越界；`Generated/**`、`StatusCatalog.g.cs` 未动。V2 的重复映射属既有架构债（`Statuses.cs:71`、`StudioTheme.axaml:49–50`、`V2LocalStyles.axaml:191–192`），ADJ `:125` 已预告，本卡未扩大。

## 8. Verification 结论

- **行为/回归事实层 PASS**：build 0/0；定向 3/3；无过滤 1292/0/57（逐程序集逐项吻合）；check PASS(3)；pins 15/15；四 PNG SHA 不变；禁止范围 diff 空；零写入；未 push；对比度独立复算与 ADJ 矩阵一致；代码自 5ecc 未变。
- **证据纪律层仍 FAIL（P1）**：D14R2-001（SDK/路径、57 条 skip 未逐条、reviewed_head 滞后）。r1 D14R1-001 只能算部分闭合。
- **残余风险**：D14R1-002 的 red-run 仍为 `NOT_RUN`（只有静态判别）；D14R1-007 的对比度用例不随 catalog 判别；D14R1-009 的 Host flake 仍可能在全量复跑中出现；V2 三处与 FEA-06 特判仍 open/deferred，不能宣称“产品状态前景已统一”；全仓 14 个 NUL 文档为历史债。
- 本轮未发现新的产品行为/架构缺陷；补正提交未改产品代码，未引入回归。

## 9. 结论与复审

**本 head 不可按 `approved` 交 DSH 集成。** 阻断项只有 D14R2-001（P1），且全部是证据/文档修正，**不需要改 `Status.cs` 或测试**。建议处置顺序：

1. 在同一文档/证据提交中：补 57 条 skip audit（名称+fixture reason）与正确的 shell/SDK/base/head 头；把 `reviewed_head` 改为 `f38a1a920`；
2. 把 Task `:59,65` 的 commit/SHA 改为 c48 + LF blob（或加 eol 规则并注明口径）；按 HANDOFF 模板补 Handoff；更新 STATUS `:10`、Task `status` 为 `in_review`、Task `:49` 基线口径；
3. 在 Handoff 补全 r1 7 个 P2 的残余登记，明确 V2/FEA-06 特判仍 deferred；
4. 以新 head 做一次干净全量（1292/0/57 应保持）后派 r3 **只审该增量**；approved 后 DSH 集成、写 `integration_commit`、完成资源 closeout；
5. 若 DSH 认为 57 条 skip 的“按程序集+统一 fixture 原因”已足够，应在 Task/ADJ 中显式记录该裁决与理由（Q-009 的默认口径仍是逐条），否则不得视为闭合。

**复审追加**：新 head + 逐条 findings disposition，不抹掉本记录；旧证据/旧 Review 字节保持原样。

## 10. 可转发指令

> 请 DSH 接收 `doc/reviews/D-14-STATUS-COLOR-FIX-impl-r2.md`（changes_requested，P0=0/P1=1/P2=5；reviewed_head=`f38a1a920`，实现=`5ecc1e4c6`，补正=`c48ea5e3c`）。代码面已核实：裁决 A 单点执行、对比度 Dark 7.9566/7.1372、Light 6.3497/7.0459、Disabled 对照全<4.5、build 0/0、定向 3/3、全量 1292/0/57、check PASS(3)、pins 15/15、四 PNG SHA 不变、零写入、未 push。请只做文档/证据补正：① 补 57 条 skip 逐条名称+reason，修正 shell/SDK 头（实际 `dotnet --version`=10.0.401，SDK 10.0.401/net9.0；解释器路径 `C:/Program Files/PowerShell/7/pwsh.exe`），`reviewed_head` 改 `f38a1a920`；② Task `:59,65` 的 pin 改为 `c48ea5e3c` + LF SHA `d57d0caf…`（或加 eol 规则），或明确标注 CRLF 口径；③ 按 HANDOFF 模板补 Handoff（front matter/AC 表/命令/未跑项/下一任务建议/证据 SHA）；④ STATUS `:10` 与 Task `status`/`:49` 更新；⑤ Handoff 补全 r1 7 个 P2 的残余登记。不要改 `Status.cs`/测试、不要动 FEA-06 旧证据字节、不要 push；完成后新 head 重跑干净全量并派 r3 只审增量。
