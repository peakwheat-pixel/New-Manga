---
task_id: D-14-STATUS-COLOR-FIX
reviewer: DSH 独立子 agent（impl-r1 Reviewer；独立上下文，未参与实现）
reviewer_kind: subagent
author: DSH（D-7 故障转移实施会话，commit 5ecc1e4c6）
base_commit: 195422c2fdf72f0460d2e265b53e22a2c5eff6fd
reviewed_head: b2c41226d96a77515a4c778b8f24722fcf731666
prompt_head: 0d2a02202ea515559ff8ea2dd384fd7e234ae55c
implementation_head: 5ecc1e4c6e1b99a9b53ad0d9bcd11d7489ee36e2
delivery_commit: 5ecc1e4c6e1b99a9b53ad0d9bcd11d7489ee36e2
prior_review: null（本卡首轮）
decision: changes_requested
verdict: changes_requested
p0: 0
p1: 3
p2: 7
provenance:
  agent: DSH 独立子 agent（checkpoint §156 记录的 workflow job workflow-33d5550690bf4ac5）
  appointment: 用户本轮 D-14 独立 impl Review 指令；DSH 按 D-9 派发（2026-10-31 裁决：作者可派独立上下文子 agent 审查）
  implementation_participation: none
  mode: read_only_except_this_report
  date: 2026-11-03
---

# Review：D-14-STATUS-COLOR-FIX（impl-r1）

## 0. 结论

**verdict = changes_requested（P0=0 / P1=3 / P2=7）。**

- **产品代码与测试本身正确**：`StatusCatalog.ColorKey(NotStarted)` 单点改为 `NmKeys.Color.Text.Secondary`，XML 注释同步；新增 `D14StatusNotStartedTests`（映射断言 + light/dark × `Bg.Canvas`/`Bg.Panel` 的 WCAG 复算）。本轮独立复算 4 个测试组合全部 ≥4.5:1（Disabled 对照组全部 <4.5:1，判别有效）；无越权改动；build 0/0；无过滤全量复跑 **1292/0/57**（EXIT=0）；check PASS(3)；pins 15/15；旧 FEA-06 四 PNG SHA 逐字节一致；禁止范围 diff 为空；默认运行零仓库写入；未 push。
- **阻断项全部在“证据/交付纪律”层**，不是行为缺陷：① canonical 证据日志不满足 ADJ:149 与 Q-009 ①③（无 shell/SDK/head 头、无逐程序集计数、无 57 条 skip 原因、命令为省略写法）；② 缺“修前失败”的判别力 artefact（ADJ:134 明列的 AC；Q-009 ② 下记 `NOT_RUN`）；③ 缺 Task 交付条款与 09 §4 要求的 Handoff（`doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md` 不存在）。
- 其余 7 个 P2 是记录/一致性/测试设计问题（FEA-06 旧特判与过时注释、Task 卡 NUL 损坏、V2 三处 NotStarted 前景、对比度用例取键方式、ADJ AC 覆盖缺口、STATUS/基线数字滞后、Host 偶发 flake），可在集成或后续卡处置，但**不得据此把 D-14 写成“产品状态前景已统一”**。

## 1. 范围与依据

- **被审交付**：`c1619cede`（D-14 实际父提交）→ `5ecc1e4c6`，共 3 个文件、+52/−2：
  - `apps/desktop-avalonia/src/NewManga.DesignSystem/Controls/Status.cs`（`git show 5ecc1e4c6`：`:75` 注释、`:85` 映射，各 1 行）；
  - `apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/D14StatusNotStartedTests.cs`（新增 38 行）；
  - `verification/D-14-STATUS-COLOR-FIX/impl-verification.log`（新增 12 行，SHA256 `030245d641342e84b86a57121aac4ed7b52e1cad08ac52fe52d818fedb3a7e5a`，本轮实算一致）。
- **固定点**：派发时 HEAD `0d2a02202`；审查期间仓库前进 1 个 **仅 checkpoint 文档**的提交，故 `reviewed_head` 取实际当前 HEAD `b2c41226d`（`git show --stat b2c41226d` = `doc/checkpoints/GOAL-PROGRESS-2026-11-02.md` 5 行）。代码/测试/证据 blob 在 `0d2a02202` 与 `b2c41226d` 完全相同，不影响结论。
- **依据**：[ADJ-2026-11-03-D14-STATUS-NOTSTARTED](ADJ-2026-11-03-D14-STATUS-NOTSTARTED.md) 裁决 A（`:20`）、§4 实施与测试要求（`:122–137`）、§5 验证边界（`:151–160`）、可复制验证要求（`:149`）；[Task D-14](../tasks/D-14-STATUS-COLOR-FIX.md) `allowed_paths`（`:21–27`）、IN/OUT（`:38–39`）、验收（`:42–49`）、交付（`:52`）；[09 协作协议](../09_COLLABORATION.md) §4 生命周期（`:73`）、§5 Handoff（`:191–199`）、§12 证据纪律 Q-009（`:288`）；`AGENTS.md` 写域与“未提交内容归原作者所有”。
- **未审到/不覆盖**：原生 200% DPI 与 a11y 实机；真实运行时换肤截图；Current V2 Studio/Library 的实机渲染（Task `:39` 已列为 OUT）；HighContrast 主题下 NotStarted 文字（由既有 `BadgeCompositeContrastTests` 间接覆盖，见 §5）。

## 2. Standards（可选视角，executed）

按仓库记录在案的标准逐条核对；除下列三处硬性 FAIL 外，另命中 2 个 Fowler 判断项（非硬性违规）：

- **写域**（Task `:21–27`）：交付提交 3 个文件全部命中 allowed_paths；`Styles/**`、`Themes/**`、`Generated/**`、`NewManga.App/**`、`NewManga.Host/**`、`NewManga.ApplicationCore/**` 在 `c1619cede..5ecc1e4c6` 的 diff 为空。**PASS**。
- **裁决 A 的实现面**（ADJ `:20`）：只改一个映射 + 一条注释；未新增颜色令牌、枚举值或 API 字段；未改其它八值映射；未改 `MutedColorKey`。**PASS**。
- **证据纪律**（09 `:288` Q-009 ①③、ADJ `:149`）：证据日志不满足“shell/解释器头、base/head、逐程序集计数、逐条 skip 原因、完整命令”。**FAIL → D14R1-001**。
- **判别力 artefact**（09 `:288` Q-009 ②、ADJ `:134`）：无修前失败日志/探针输出。**FAIL → D14R1-002**。
- **Handoff**（09 `:73`、`:191–199`；Task `:52`）：交付要求 `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md`，全仓不存在任何 D-14 handoff。**FAIL → D14R1-003**。
- **Fowler baseline**：命中 1 个判断项 **possible Duplicated Source of Truth**（catalog 与 V2 本地 `Statuses.BrushKey`/`StudioTheme.axaml`/`V2LocalStyles.axaml` 各存一份 NotStarted 前景），非硬性违规，记 **D14R1-006**；另 1 个 **possible Obsolete Comment**（FEA-06 交叉断言注释），记 **D14R1-004**。

## 3. Spec（可选视角，executed）

- **A 的核心要求已忠实实现**：`StatusCatalog.ColorKey(NotStarted)` 现返回 `NmKeys.Color.Text.Secondary`（`Status.cs:85`），注释改为 `Nm.Color.Status.*/Nm.Color.Text.Secondary` 并注明“NotStarted is a real state, readable >= 4.5:1”（`Status.cs:75`），与 `Controls.Status.axaml:35–38`（glyph）、`:65–67`（普通状态文字/Chip 标签）一致。**MET**。
- **ADJ §4 的 AC 未全部落地**（Task 卡已把范围收窄，故记 P2 而非阻断）：
  - “其他八值映射、`○`、‘未开始’、`ClassName`、`MutedColorKey(NotStarted)==null` 保持原义”：`CustomControlsTests.cs:33` 只断言 `ColorKey` 前缀 `Nm.Color.`，未逐值断言；本轮只能以 diff 证明八值未变（P2，D14R1-010）。
  - “覆盖 `StudioStates.ColorTokenKey(NotStarted)`”：`V2StudioMathTests.cs:127` 仍只断言前缀（P2，D14R1-010）；且 App.Tests 不在本卡 allowed_paths。
  - “移除 IN-2A NotStarted 交叉断言特判”（ADJ `:123`，且 `:137` 说明条件已可由本卡满足）：未执行，Task `:39` 将其列为 OUT（P2，D14R1-004）。
  - ADJ `:125` 建议同卡纳入的两处 V2 NotStarted 前景：未纳入（P2，D14R1-006）。
- **无 scope creep**：除上述 3 个文件外无任何行为改动；未改生成物、冻结设计、Schema、Core、Host/IPC、依赖。

## 4. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| D14R1-001 | P1 | `verification/D-14-STATUS-COLOR-FIX/impl-verification.log:6–10` | 该文件是 canonical evidence，但只有摘要：无 shell/解释器与 .NET SDK 头、无 base/head、无逐程序集 passed/failed/skipped（只写“DS 117 = 114+3；App 653；其余程序集不变”）、无 57 条 skip 来源与原因、命令写成 `dotnet test ...` 省略式。按 Q-009 ①（09 `:288`）与 ADJ `:149`，此类日志“不可复核，按未提供处理”，回归门禁只能由 Reviewer 复跑替代，卡片自身不满足证据纪律。 | 逐行核对日志；本轮独立复跑得到相同数字（§5），证明**事实**成立、**artefact** 不合规。 | DSH 在 `verification/D-14-STATUS-COLOR-FIX/` 追加一次合规日志（shell/pwsh 版本、SDK、base/head、完整命令、逐程序集计数、57 条 skip 原因、前后 `git status`），保留旧文件字节或另存 r2；随后以新 head 复审该增量。 | open |
| D14R1-002 | P1 | 同上；ADJ `:134` | 缺“修前失败”的判别力 artefact。ADJ 明列 AC：“新增的精确 catalog 断言在本 reviewed_head 应失败（实际 Disabled），修复后通过”；卡片证据只有修后 PASS，无 pre-fix red-run 日志或探针输出。按 Q-009 ② 应记 `NOT_RUN`，不能以散文或 `3/3 PASS` 代替。 | 静态可证：`git show c1619cede:…/Status.cs` 原值 `NmKeys.Color.Text.Disabled` ≠ `Text.Secondary`；且 Disabled 在四个测试组合上仅 2.45/2.20/1.80/1.99:1（本轮复算），若断言改取 catalog 必失败。但仓库内无执行 artefact。 | 在修前 head（`c1619cede` 或 `195422c2f`）用 worktree/临时副本运行 `D14StatusNotStartedTests` 并把失败输出入库（不改现有证据字节）；或在证据中显式标 `NOT_RUN` 并接受降级，由 DSH 裁决。 | open |
| D14R1-003 | P1 | `doc/tasks/D-14-STATUS-COLOR-FIX.md:52`；`doc/handoffs/`（无 D-14 文件） | Task 交付条款要求 `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md`；`Get-ChildItem doc/handoffs -Filter '*D-14*'` 为空。09 `:73` 要求“Handoff 和 canonical evidence 就绪后请求独立 Review”，本卡在两者均未就绪时已派发 Review。影响：恢复/集成记录缺失，无法进入 `in_review`→集成→closeout。 | 目录列举 + Task `:52`；`doc/handoffs` 最新文件为 FEA-06 系列（06:52）。 | DSH 按 [HANDOFF 模板](../templates/HANDOFF.md) 补 `D-14-STATUS-COLOR-FIX-impl.md`，引用 `5ecc1e4c6`、证据 SHA 与 OUT/残余（V2、特判、HighContrast/DPI 未测）。 | open |
| D14R1-004 | P2 | `apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/FluentResidual2StateEffectiveTests.cs:529–531, 558–563` | 注释仍写“StatusCatalog.ColorKey still reports Text.Disabled; track until DSH fixes the catalog”，在 HEAD 已为假；`if (kind != StatusKind.NotStarted)` 跳过已无必要（现返回 Secondary，交叉断言会通过）。ADJ `:123` 把移除该特判列为“必改”，Task `:39` 将 FEA-06 已提交测试列为 OUT。影响：九值交叉断言仍缺 NotStarted 直接覆盖，注释误导；但 `D14StatusNotStartedTests.cs:19` 已独立断言映射，`:531/:546` 已断言 glyph 有效前景为 Secondary，一致性被传递覆盖。 | 代码对照；本轮全量中该用例 PASS。 | 在集成或后续卡移除特判并更正注释；不覆盖 FEA-06 旧证据字节。 | deferred |
| D14R1-005 | P2 | `doc/tasks/D-14-STATUS-COLOR-FIX.md:59, 65` | 该受跟踪文档含 2 个 NUL 字节（offset 3308/3629）：Canonical Evidence 行的路径成为 `\0erification/…`、SHA 成为 `\0`+`30245d…`（前导 `0` 被吞）；文件被判为 binary（`read` 工具拒读）。影响：canonical evidence 指针按原文不可解析，`check.ps1` 未覆盖此形态。**系统性**：全仓 29 个受跟踪 md 含同类 NUL（多为反引号/首位字符被 NUL 替换，如 `HOST-TILE-CHANNEL-1.md`、`WORKTREE_SAFETY_INVENTORY.md`），非本卡独有。 | 字节扫描（`nul_files=29`）+ `git diff --numstat 5ecc1e4c6 HEAD` 显示该文件 `Bin 2625 → 4034`；正确 SHA 可由证据文件实算。 | 集成时修掉本卡 2 处 NUL（路径与 SHA 还原）；把“受跟踪文档含 NUL”登记为单独清理项。本报告不修改原文件。 | open |
| D14R1-006 | P2 | `Views/V2/Studio/StudioTheme.axaml:49–50`；`Shell/V2/Statuses.cs:71`；`Views/V2/Shell/Theme/V2LocalStyles.axaml:191–192` | 三处 V2 NotStarted 前景仍为 `Nm.Color.Text.Disabled`。D-14 只改 DS catalog，于是 `StudioStates.ColorTokenKey(NotStarted)`（`StudioStateKind.cs:58` → catalog → Secondary）与 `studio-state-notstarted` 样式（Disabled）**现在不一致**；`Statuses.BrushKey(NotStarted)` 与 V2 本地 badge 符号也仍 Disabled。ADJ `:111` 已预告此缺口、`:125` 要求同卡对齐，Task `:39` 将其排除。影响：无渲染变化（样式未改），但 catalog 查询与真实前景在 V2 上分裂；**不得据此宣称产品状态前景已统一**。 | `rg -n "notstarted|NotStarted"` + 样式文件对照；`V2StudioMathTests.cs:127` 只断言前缀，仍 PASS。 | 后续卡（或经 DSH 范围裁决）把两处 V2 前景与 `BrushKey` 对齐 Secondary，并补 V2 断言；在此之前保持 ADJ §3 的缺口登记。 | deferred |
| D14R1-007 | P2 | `D14StatusNotStartedTests.cs:30–35` | 对比度用例直接取 `NmKeys.Color.Text.Secondary`，未从 `StatusCatalog.ColorKey(NotStarted)` 解析；判别力因此拆成两个用例（映射断言 + 令牌断言）。若未来 catalog 与令牌被同时改成低对比组合，两用例仍会同时通过。另：用例未断言 light/dark 解析出的颜色不同，主题切换正确性依赖共享 `ThemeTestHarness`（`ThemeManagerTests.cs:50–56` 已独立覆盖）。 | 代码对照 + 本轮复算。 | 让对比度用例以 `StatusCatalog.ColorKey(NotStarted)` 解析前景，并可断言两主题前景色不同；单用例即可判别。 | deferred |
| D14R1-008 | P2 | `doc/STATUS.md:10`；`doc/tasks/D-14-STATUS-COLOR-FIX.md:49` | STATUS `:10` 仍写“下一步：实施 D-14-STATUS-COLOR-FIX（ready；owner=codex…）”，与 STATUS `:7` / `REBASELINE_PLAN:23`（in_progress、已实施 `5ecc1e4c6`）矛盾；Task `:49` 验收基线仍为 1274/0/57（实际基线 1289/0/57，交付 1292/0/57）。影响：恢复入口误导、门禁数字口径滞后。 | 三处对照；本轮全量实得 1292/0/57。 | DSH 在集成时更新 STATUS 与 Task 数字（保留历史字节）。 | open |
| D14R1-009 | P2 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/TileChannelTests.cs:219–235` | 同一全量命令的第二次复跑出现 `EqualLengthRewrite_SameSize_RejectedAsDigestMismatch` 失败（Expected `TileDigestMismatch`，Actual `NO_ERROR`）；该用例单独重跑 3/3 PASS，且与 D-14 改动无文件交集（Host 程序集未改）。影响：全量 1292/0/57 的复现存在时序抖动，集成复跑若再遇不应归因 D-14。 | 第二次全量 1291/1/57；单跑 3×PASS；第三次全量 1292/0/57（§5）。 | DSH 集成时以一次干净全量为准；若复现则另立诊断卡，不在本卡处理。 | open |
| D14R1-010 | P2 | `CustomControlsTests.cs:33`；`V2StudioMathTests.cs:127` | ADJ §4 首条 AC 要求“其他八值映射、`○`、‘未开始’、`ClassName`、`MutedColorKey(NotStarted)==null` 保持原义”并“覆盖 `StudioStates.ColorTokenKey(NotStarted)`”；现状只有前缀断言，八值精确键与 `MutedColorKey` 无断言，`StudioStates.ColorTokenKey(NotStarted)` 无 Secondary 断言。事实层已由 diff 证明未变（仅 1 行映射），但缺回归断言。 | 代码对照 + diff。 | 后续卡在 DS 测试补八值键表与 `MutedColorKey(NotStarted)==null`，在 App.Tests 补 `ColorTokenKey(NotStarted)==Text.Secondary`。 | deferred |

## 5. 验证

环境：Windows、`pwsh 7.6.8`、仓库 `G:\CODEX\New Manga`、`reviewed_head=b2c41226d`。所有命令均在默认（非 opt-in）配置下执行；日志副本在仓外 `G:\CODEX\New Manga.workspace\D-14-review\`（非交付物）。

| 场景 | 命令或步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 交付范围 | `git diff --name-only c1619cede 5ecc1e4c6` | b2c41226d | **PASS**：仅 3 文件，全在 allowed_paths | 本报告 §1 |
| 越权/禁止范围 | `git diff --name-only c1619cede 5ecc1e4c6 -- …/Styles …/Themes …/Generated …/App …/Host …/ApplicationCore` | 同上 | **PASS**：空 | 命令输出 |
| 映射与注释 | 读 `Status.cs:75,85`；`git show 5ecc1e4c6` | 同上 | **PASS**：仅 NotStarted→`Text.Secondary`；注释同步；无新令牌/枚举/API | diff |
| 对比度独立复算（Reviewer 自写 WCAG 实现，读 `Tokens.Dark/Light.axaml`） | PowerShell `L=0.2126R+0.7152G+0.0722B`、`(Lmax+0.05)/(Lmin+0.05)` | 同上 | **PASS**：Dark Canvas **7.9566**、Panel **7.1372**；Light Canvas **6.3497**、Panel **7.0459**（≥4.5）。六面全量：Dark App 7.6312 / Raised 6.4253 / Overlay 5.7039 / Sunken 8.1790；Light App 6.6963 / Raised 6.2380 / Overlay 7.0459 / Sunken 5.8606。**Disabled 对照**：Dark 2.3522/2.4525/2.1999/1.9805/1.7581/2.5211、Light 1.8951/1.7970/1.9940/1.7654/1.9940/1.6585，全部 <4.5 ⇒ 判别方向成立 | 与 ADJ §2 矩阵逐值一致 |
| 新测试判别性（静态） | 读 `D14StatusNotStartedTests.cs:16–37`；`git show c1619cede:…/Status.cs` | 同上 | **PASS（行为）/ 缺 artefact**：`:19` 等值断言对修前 `Text.Disabled` 必失败；`:30–35` 由真实资源栈取色并用 `ContrastMath` 复算，非静态字符串/近似值。但无执行 red-run（见 D14R1-002） | 代码 + 复算 |
| 定向测试 | `dotnet test …/NewManga.DesignSystem.Tests.csproj --no-build --filter FullyQualifiedName~D14StatusNotStartedTests` | 同上 | **PASS** 3/3，EXIT=0 | 命令输出 |
| build | `dotnet build apps/desktop-avalonia/NewManga.sln --nologo` | 同上 | **PASS** 0 warning / 0 error，EXIT=0 | 命令输出 |
| 无过滤全量（第 1 次） | `dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings …/NewManga.runsettings --nologo` | 同上 | **PASS** **1292 / 0 / 57**，EXIT=0（App 653/0/7、CoreClient 128/0/22 在尾部可见） | 命令输出 |
| 无过滤全量（第 2 次，复跑） | 同上 | 同上 | **1291 / 1 / 57**：`NewManga.Host.Tests.TileChannelTests.EqualLengthRewrite_SameSize_RejectedAsDigestMismatch`（Actual `NO_ERROR`）；单跑 3/3 PASS；与 D-14 无交集 | 仓外日志 + 单跑输出；见 D14R1-009 |
| 无过滤全量（第 3 次，确认） | 同上 | 同上 | **PASS** **1292 / 0 / 57**，EXIT=0；逐程序集：Appearance 21、Presentation 38、Host 51（skip 28）、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、CoreClient 128（skip 22）、App 653（skip 7） | `full-test-review-run3.log` |
| 治理检查 | `pwsh -NoProfile -File tools/governance/check.ps1` | 同上 | **PASS** `Governance check: PASS (3 warnings)`，EXIT=0；15 current documents；警告为 9 个非终态 Task 与 STATUS/PLAN 体量 80%，均为既有项 | 命令输出 |
| 证据 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 同上 | **PASS** `PIN AUDIT: PASS (all 15)`，EXIT=0 | 命令输出 |
| 旧 FEA-06 四 PNG | `Get-FileHash -Algorithm SHA256 verification/FEA-06/screens/*.png` | 同上 | **PASS**：reader `8533c263…78b2`、settings `fd30b166…a162`、shelf `307f8f67…8b0a`、workbench `d5d878bb…2df5`，与 `doc/tasks/FEA-06-RESIDUAL-2.md:84,128` 全值一致 | 命令输出 |
| 默认运行零写入 | build + 全量前后 `git status --porcelain=v1`（含 untracked） | 同上 | **PASS**：空；未出现 `verification/**` 或截图写入 | 命令输出 |
| 旧证据字节 | `git diff --name-only 5ecc1e4c6 HEAD`；`git diff --name-only c1619cede 5ecc1e4c6 -- verification/FEA-06` | 同上 | **PASS**：交付后仅 5 个 doc 文件（Task/STATUS/PLAN/LEDGER/checkpoint）；FEA-06 证据未动 | diff |
| 未 push | `git branch -r --contains 5ecc1e4c6`；`git rev-parse origin/main` | 同上 | **PASS**：无远端分支/tag 含交付提交；`origin/main=b1c1f5a56` | 命令输出 |
| 消费者 rg | `rg -n "ColorKey|NotStarted|nm-status-notstarted|StatusBadge|CountChips"` 全仓 | 同上 | 见 D14R1-004/006/010；无失败断言（`CustomControlsTests`、`BadgeCompositeContrastTests`、`FluentResidual2StateEffectiveTests` 全 PASS） | 检索结果 |
| HighContrast / 九值 badge 可读性 | 既有 `BadgeCompositeContrastTests.Status_badge_glyph_contrast_is_measured_against_the_rendered_composited_background` | 同上 | **PASS**（全量内执行）：九值 × 4 模式 × 3 面（Panel/Raised/Overlay），采样真实渲染背景，glyph 与 label 均 ≥4.5:1 | 全量日志 |

## 6. Architecture 结论

**PASS。** 变更限于 DesignSystem 的 catalog 映射与 DS 测试；无共享 wire/Schema/依赖/数据访问变化，无新增颜色令牌或双重色契约，无分层越界；生成物 `Generated/**` 未动（`StatusCatalog.g.cs` 只含符号常量，`ColorKey` 非生成代码）。V2 的重复映射属既有架构债，已在 ADJ §3 登记，本次未扩大。

## 7. Verification 结论

- **行为/证据事实层 PASS**：build 0/0、无过滤 1292/0/57（两次）、定向 3/3、check PASS(3)、pins 15/15、四 PNG SHA 不变、禁止范围 diff 空、零写入、未 push；对比度由 Reviewer 独立复算并与 ADJ 矩阵逐值吻合。
- **交付纪律层 FAIL**：D14R1-001（证据日志不合 Q-009 ①/ADJ:149）、D14R1-002（无修前失败 artefact，Q-009 ②/ADJ:134）、D14R1-003（缺 Handoff，Task:52/09:73）。三项均需在**新 head** 上补齐后复审；本轮不复用本报告的批准。
- 残余风险：V2 三处前景与 catalog 的分裂（D14R1-006）在样式未改前不会造成视觉回归，但会让“catalog 是唯一来源”的注释继续失真；Task 卡 NUL（D14R1-005）会让后续读者/工具无法按原文解析 canonical evidence。

## 8. 结论与复审

**本 head 不可交 DSH 集成。** 代码与测试可按裁决 A 接受，但三处 P1 属“关键验证/交付缺失”，按 [REVIEW 模板](../templates/REVIEW.md) 与 09 `:283` 不得批准。建议处置顺序：

1. 补合规证据日志与修前失败 artefact（可合并在一次证据追加提交），修 Task 卡 NUL，补 Handoff；
2. 同步 STATUS:10 与 Task 基线数字（可与 1 同一次文档提交）；
3. 以新 head 重跑一次干净全量并请求 r2 复审；r2 只需审增量与三项 P1 的闭合，不重复审已确认的代码面；
4. 复审通过后再由 DSH 集成、登记 `integration_commit` 与资源 closeout；**不得**把 D-14 写成“产品状态前景已统一”，V2 两处与 FEA-06 特判仍为 open/deferred。

**复审追加**：新 head + 逐条 findings disposition（不抹掉本记录）；旧证据字节保持原样。

## 9. 可转发指令

> 请 DSH 接收 `doc/reviews/D-14-STATUS-COLOR-FIX-impl-r1.md`（changes_requested，P0=0/P1=3/P2=7；reviewed_head=`b2c41226d`，实现=`5ecc1e4c6`）。代码面已核实：裁决 A 单点执行、对比度独立复算全 ≥4.5、build 0/0、全量 1292/0/57、check PASS(3)、pins 15/15、旧四 PNG SHA 不变、禁止范围空、零写入、未 push。请先闭合三项 P1：① 在 `verification/D-14-STATUS-COLOR-FIX/` 追加带 shell/SDK/base/head/完整命令/逐程序集/57 条 skip 原因的合规日志；② 补“修前 head 运行 D14 测试失败”的 artefact（或显式标 NOT_RUN 并裁决）；③ 补 `doc/handoffs/D-14-STATUS-COLOR-FIX-impl.md`。同时修 Task 卡 `:59,65` 的 2 处 NUL 与 `:49` 基线数字、`doc/STATUS.md:10` 的过时“下一步”，并在 Handoff 记录 V2 两处前景、FEA-06 特判与 HighContrast/DPI 未测。完成后以新 head 重跑一次干净全量并派 r2 复审；不要写 D-14 达成、不要动 FEA-06 旧证据字节、不要 push。
