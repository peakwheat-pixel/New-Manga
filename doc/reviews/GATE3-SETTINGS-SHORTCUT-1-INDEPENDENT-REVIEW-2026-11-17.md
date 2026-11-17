---
task_id: GATE3-SETTINGS-SHORTCUT-1
reviewer: reviewer-g3dc
reviewer_kind: subagent
reviewer_source: DSH 子 agent `reviewer-g3dc`（独立上下文，未参与该卡实现或返修；由父 agent `lead` 派发）
author: DSH
base_commit: 411dada59
reviewed_head: 89b36c3f2
review_time: "2026-11-17T12:57:00–13:12:36+08:00"
decision: ACCEPTED_WITH_FINDINGS
template_decision: approved
p0: 0
p1: 0
p2: 2
p3_observations: 2
---

# Review（独立复核）：GATE3-SETTINGS-SHORTCUT-1

> **审查者来源**：`reviewer-g3dc`，DSH 子 agent，独立上下文，未参与本卡实现。
> **被审 head**：`89b36c3f2`（main）。相对交付提交 `1ef6a2ebd`，`89b36c3f2` 只增加文档/证据（`git diff --name-only 1ef6a2ebd 89b36c3f2` = 6 个 `doc/**` 与 `verification/**` 文件），`apps/**` 无改动；被测代码与测试在 `1ef6a2ebd` 与 `89b36c3f2` 上等价。
> **本复核不构成产品发布验收**：不关闭 Release Gate，也不把条件 3 判为 MET。

## 1. 范围与依据

- 复核对象：`doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md`（status `in_review`，AC1–AC6 均 `<<MET>>`）与其证据目录 `verification/GATE3-SETTINGS-SHORTCUT-1/`。
- 依据：`AGENTS.md`、`doc/09_COLLABORATION.md`、本卡 AC 与允许/禁止范围、`doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md` §3/§9。
- 只读边界：本复核未修改产品代码、卡片 frontmatter、`verification/**` 既有字节；本文件是唯一写入。测试运行把证据变量外置到 `G:\CODEX\New Manga.workspace\tmp\review-g3dc\`，未写仓库证据。

**工作区基线（实测，非假设）**：派单称「工作区干净」，实测**不净**——复核开始时 `git status --porcelain` 已有 `M doc/tasks/GIT-CLEAN-PUBLICATION-1.md`（12:58:26，Lead 改派复核者字段）；12:59:18 又出现 `M doc/handoffs/NEXT-SESSION-STARTER.md`（Lead 并发更新）。两处均早于/独立于本次测试，且 `git status --porcelain -- apps/ verification/` 为空。故「测试后 `git status --porcelain` 为空」无法按字面复现；可复现的等价事实是：**本次测试未向仓库写入任何文件**（`apps/`、`verification/` 状态为空）。

## 2. A1：定向测试重跑（实测）

```powershell
cd 'G:\CODEX\New Manga'
$env:NEWMANGA_EVIDENCE_DIR = 'G:\CODEX\New Manga.workspace\tmp\review-g3dc\evidence'
$env:NEWMANGA_READER_OVERLAY_EVIDENCE_DIR = 'G:\CODEX\New Manga.workspace\tmp\review-g3dc\overlay'
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Debug --filter "FullyQualifiedName~SettingsSpaceShortcutTests"
```

实测输出尾部（2026-11-17，head `89b36c3f2`，Debug，无夹具）：

```text
已通过! - 失败:     0，通过:     1，已跳过:     0，总计:     1，持续时间: 1 s - NewManga.App.Tests.dll (net9.0)
EXITCODE=0
```

结论：**1 passed / 0 failed / 0 skipped / 1 total，EXIT=0**，与卡面 AC2 测试表、Closeout 记录一致。构建阶段 `NewManga.App`、`NewManga.App.Tests` 均重新编译成功。

## 3. A2：覆盖判定——是否真的覆盖「从 Console 空间按 Ctrl+K 仍生效」

**结论：真覆盖，不是同义反复。** 依据（均按 `89b36c3f2` 读码）：

| 环节 | 事实 | 位置 |
|---|---|---|
| 测试入口 | 测试调用 `shell.HandleKeyForTest(...)`；`AppShellV2.HandleKeyForTest` 只是把键转交 `_viewModel.HandleKey(key, modifiers, textInputFocused)`——与窗口真实键盘路径共用同一个 ViewModel funnel | `SettingsSpaceShortcutTests.cs:55/62/67/73`；`AppShellV2.axaml.cs:167-168` |
| 真实注册 | `AppShellV2` 构造时注册 `new ConsoleWorkspaceView(_viewModel.Console)`；`State.GetWorkspace(SpaceId.Console)` 返回该实例 | `AppShellV2.axaml.cs:51-53`；`ShellState.cs:369-370` |
| 路由结构 | `HandleKey` 先让 workspace 拒绝：`workspace.TryHandleKey(...)` 返回 true 才短路，否则落到 `HandleKeyCore`（KeyMap） | `AppShellViewModel.cs:950-970` |
| Console 适配器 | `ConsoleWorkspaceView.TryHandleKey(...) => false`（常量） | `WorkspaceAdapters.cs:69` |
| Ctrl+K | 全局命令（`SpaceId` 为 null）：`G(Key.K, KeyModifiers.Control)`；`HandleKeyCore` 的 `case Key.K` → `OpenPalette()` | `ShellCommands.cs:67`；`AppShellViewModel.cs:1083/1122` |
| 测试断言 | 先断言 `State.CurrentSpace == SpaceId.Console`，再断言 Ctrl+K 被处理且 `IsPaletteOpen` 为 true；Esc 关闭；Ctrl+D2 回 `SpaceId.Studio` | `SettingsSpaceShortcutTests.cs:58/61-64/67-69/72-76` |

**判别力**：若把 `ConsoleWorkspaceView.TryHandleKey` 改成 `=> true`，按 `AppShellViewModel.cs:956-960` 的短路结构，Ctrl+K 根本到不了 KeyMap，第 64 行 `IsPaletteOpen` 断言必然失败。因此该测试确实守护「Console/设置空间不吞全局快捷键」，不是「因为适配器返回 false 所以断言 false」的空转。AC3 的探针日志（`verification/GATE3-SETTINGS-SHORTCUT-1/ac2-ac3-2026-11-17.log:34-63`）与此一致：注入后 `1 failed`、消息 `Ctrl+K did not open the command palette from Settings`、`:64`、EXIT=1；还原后源文件 sha256 `5227fce80cdeca0dcf743c64a187c976c99160a85c488a4efac88ca6ccdcc3b2` 与实测一致（工作树与 HEAD blob 均为该值），源文件无 `PROBE` 残留。

**未重跑探针的说明**：探针需要临时改写 `WorkspaceAdapters.cs`（产品源码），超出只读复核边界，故只核验日志 + 还原哈希 + 代码路径，不宣称本人重跑过注入。

**覆盖边界（P3 观察，不否定 AC2）**：该测试走的是 ViewModel funnel，不是真实 Avalonia 窗口事件；也未显式把焦点放进某个 Settings 控件。由于 Console 适配器是「与段无关的常量 false」、且 Ctrl+K 不是 `IsPlainTypingKey` 的纯打字键，空间级结论成立；但严格说，它证明的是「Console（设置所在空间）不吞键」，不是「设置页某个 TextBox 获得焦点时的逐控件行为」。

## 4. A3：AC5 数字核对（用原始 TRX，不重跑 6 分钟全量）

按派单要求未重跑全量，改用交付时留下的两个 TRX 逐项核对：

| 口径 | 来源 | total | passed | failed | notExecuted/skipped | 本卡测试 |
|---|---|---|---|---|---|---|
| 带 sidecar 夹具（权威 `test.ps1`） | `G:\CODEX\New Manga.workspace\tmp\r17\gate3\testps1\test\results-app.trx` | **973** | **969** | 0 | 4（NotExecuted） | `SettingsSpaceShortcutTests.ConsoleSpace_DoesNotSwallowGlobalShortcuts` = **Passed** |
| 无夹具 App.Tests | `G:\CODEX\New Manga.workspace\tmp\r17\gate3\evidence\app-tests-nofixture-clean.trx` | **973** | **962** | 0 | 11（NotExecuted） | 同上 = **Passed** |

`ac5-testps1-summary-2026-11-17.json` 自洽性（实测逐项复算）：CoreClient 258+0=258；Host 364+44=408；App 969+4=973；合计 passed 258+364+969=**1591**，skipped 0+44+4=**48**，total 258+408+973=**1639**，且 1591+48=1639。与 `ac5-testps1-2026-11-17.log`、`ac5-app-nofixture-2026-11-17.log` 的结论行一致。入库的 summary 与 workspace 原始 `summary.json` **逐字节相同**（1343 B，sha256 `74b0830a…`）；卡片登记的是 HEAD blob 摘要 `ed1c19c3…`（`sha256_basis: BLOB`；工作树为 CRLF，`git cat-file blob` 为 LF），二者关系正确，不是 pin 错误。

## 5. A4：`951 / 0 / 11 / 962` → `962 / 0 / 11 / 973` 是否如实更正

**判定：属于如实更正，不是掩盖回归。** 依据：

1. **旧读数在当时是自洽的**：951 passed + 11 skipped = 962 total；不是「passed 与 total 不同源」。
2. **增量方向不支持回归**：passed +11、total +11、skipped 不变（11）、failed 0；若是回归被掩盖，passing 数应下降而非上升。
3. **增量有独立来源**：`13d295f69`（2026-11-15，加入本卡测试）到 R16 `45af57007`（2026-11-16）之间 App.Tests 无测试文件删除（`git log --diff-filter=D --name-only 13d295f69..HEAD -- apps/desktop-avalonia/tests/NewManga.App.Tests` 输出为空）；R16 时的交接文档已记录 `App 969/0/4`（总数 973），说明 973 在本次复核前就已存在，不是本轮临时凑数。
4. **旧数字确实过期**：`13d295f69`/`24c573d1b` 两版卡面都写 951/0/11/962；本轮用两个独立 TRX 复测得 962/0/11/973，且测试表、Closeout 均同步改为新值，属于更正而非「改数字掩盖」。
5. **但更正理由 ② 不成立（P2，见 R-001）**：卡面 `:131` 写「② 原写法的 passed 与 total 不同源」——实测 951+0+11=962，旧写法自洽；真实原因只有 ①（旧读数之后新增了 11 个运行时用例）。这句应删或改写。

## 6. 实测覆盖表

| # | 场景 / AC | 实际执行的命令或步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|---|
| A1 | AC2 定向测试重跑 | `dotnet test ... --filter "FullyQualifiedName~SettingsSpaceShortcutTests"`（证据变量外置） | `89b36c3f2`，Debug，无夹具 | **1 passed / 0 failed / 0 skipped，EXIT=0** | `%TMP%\review-g3dc\dotnet-test.log` |
| A2 | AC2 覆盖判定（读码） | 读测试、`AppShellV2`、`AppShellViewModel.HandleKey`、`WorkspaceAdapters`、`ShellState.GetWorkspace`、`ShellCommands` | `89b36c3f2` | 真覆盖；非同义反复 | 本文 §3 行号 |
| A3 | AC3 探针（复核日志，不重跑注入） | 读 `ac2-ac3-2026-11-17.log:34-63`；实测源文件 sha256 与 `PROBE` 残留 | `89b36c3f2` | SHA `5227fce8…` 一致；`PROBE`=0；注入即按代码路径变红 | 证据 log + `Get-FileHash` |
| A4 | AC4 矩阵格 | 读 `MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:71`（行内容 ✅ + FQN） | `89b36c3f2` | 该格已 ✅ 并给 FQN | 矩阵 `:71` |
| A5 | AC5 无夹具数字 | 解析 `app-tests-nofixture-clean.trx` | `89b36c3f2` | **973 / 962 / 0 / 11** | 见 §4 |
| A6 | AC5 权威 test.ps1 数字 | 解析 `results-app.trx`、`results-host.trx`、`results-coreclient.trx`、summary json | `89b36c3f2` | **1591 / 1639、48 skipped、0 failed**；三项目合计自洽 | 见 §4 |
| A7 | AC6 边界声明 | 读卡 `:132-135`；核对条件 3 未判 MET | `89b36c3f2` | 与矩阵 §9.1 一致：条件 3 仍不 MET | 卡 `:132-135` |
| N1 | 6 分钟全量重跑 | 未执行（按派单「不必重跑」） | — | **NOT_RUN** | 以原始 TRX 代替 |
| N2 | 探针注入重跑 | 未执行（只读边界：需改产品源码） | — | **NOT_RUN** | 以日志 + SHA + 代码路径核验 |

## 7. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R-001 | **P2** | `doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md:131` | 「数字更正（如实登记）」的理由 ② 不成立：旧写法 `951/0/11/962` 实测自洽（951+11=962），不存在「passed 与 total 不同源」。影响：更正叙述不严谨，但不影响 AC5 新数字成立。 | 实测旧版卡（`13d295f69`、`24c573d1b`）均为 951/0/11/962；算术 951+0+11=962 | 删除理由 ②，只保留「旧读数之后新增 11 个运行时用例」；必要时补一句「旧读数在当时自洽，属过期而非错算」 | open |
| R-002 | **P2** | `doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md:160-161,170` | 矩阵 §5 仍写「仍有 **2 个 ⚠️ 格**」「剩下的是 2 个 ⚠️ 格」，与同文件 §9.1 `:255-258`「⚠️ 格：0」自相矛盾。该陈旧段在 §8.1 时已过时，但本卡 AC4 新增 §9 时未同步，削弱「矩阵内 ❌/⚠️ 均已清零」的可读性。 | `Select-String -Path doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md -Pattern '⚠️ 格'`：`:160/:161/:170` 与 `:258` 冲突 | 把 §5 第 1/4 条改为「0 个 ⚠️ 格」或加「已被 §8.1/§9 取代」的失效标注（矩阵在卡 allowed_paths 内） | open |
| O-001 | P3（观察） | `SettingsSpaceShortcutTests.cs:55-76`；`AppShellV2.axaml.cs:167-168` | 测试走 ViewModel funnel（`HandleKeyForTest`），不是真实窗口键盘事件；AC2 称「用户行为级」略有拔高。因 funnel 与真实窗口共用，且 Console 适配器与段无关，不影响结论。 | 读码 + A1 实测 | 可在卡面把「用户行为级」改为「同一 HandleKey funnel 的行为级」；或后续补真实窗口事件测试（非本卡必需） | 记录 |
| O-002 | P3（台帐） | `doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md:11,18` | `in_review` 卡 `reviewer: null`、`delivery_head: null`；本次改派与交付 head 未回填。`doc/reviews` 已记录本审查者，故不违反「Review 须记录身份」。 | `git show HEAD:doc/tasks/GATE3-SETTINGS-SHORTCUT-1.md` 前 20 行 | 收口时补 `reviewer: reviewer-g3dc（DSH 子 agent，独立上下文）`、`delivery_head: 1ef6a2ebd`（参照 GCP1 改派写法） | 记录 |

**P0 = 0，P1 = 0，P2 = 2。**

## 8. Architecture / Verification 结论

- **Architecture**：本卡只新增测试与文档，未改产品代码、共享契约、依赖或数据边界（`git diff --name-only 24c573d1b 89b36c3f2 -- apps/` 为空；测试文件在 `13d295f69` 新增，全部落在 allowed_paths `apps/desktop-avalonia/tests/NewManga.App.Tests/**`）。测试通过 shell 的既有 test seam 驱动真实 ViewModel/适配器，没有绕过生产路由。**PASS**。
- **Verification**：AC1/AC2/AC4/AC6 由读码 + 实测确认；AC3 由探针日志 + 源文件 SHA + 无残留确认；AC5 由两个独立 TRX + summary 复算确认（未重跑 6 分钟全量，按派单以原始 TRX 为准）。**PASS（带 P2 记录）**。

## 9. 结论与复审

**decision = ACCEPTED_WITH_FINDINGS**（模板口径 `approved`：P0/P1 = 0）。

**能否从 `in_review` 翻为 `done`：可以。** 理由：AC1–AC6 均有可复核的实测支撑；P0/P1 为 0；两条 P2 都不影响 AC 成立（一条是更正叙述的理由句，一条是矩阵历史段落未同步）。建议在同一个收口提交里顺带修掉 R-001 与 R-002（两处都在本卡 allowed_paths 内、均为文本级改动），以免 done 卡永久保留自相矛盾的表述；**若 DSH 选择不改，P2 不阻塞收口，但应在 Closeout 注明以 AC 与证据为准**。

**边界重申**：本卡只闭合条件 3 矩阵的「设置 / 快捷键」格，**不**把条件 3 判为 MET；带夹具 skip 仍 48（Host 44 + App 4）、§0 未纳范围的 GUI 流程与真机走查仍未完成。**本复核不构成产品发布验收。**

## 10. 未审到 / 限制

- 未重跑 6 分钟无夹具全量：按派单以交付时 TRX 为准（两份 TRX 仍在 workspace，可复算）。
- 未重跑探针注入：只读复核不允许改产品源码；以日志、SHA 一致性、代码路径推导核验。
- 未重跑 `test.ps1`（含 sidecar 夹具）；仅解析其 TRX 与 summary。
- 未审 Release Gate 条件 3 全量（本卡只负责一个格）。
