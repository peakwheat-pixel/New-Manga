---
task_id: GATE3-COVERAGE-MATRIX
reviewer: DSH 子 agent `review-gate3-matrix`（lead 派发；独立上下文；未参与实现与 r2 返修）
reviewer_kind: subagent
author: DSH（commit 84c9a8486，author peakwheat-pixel）
base_commit: d86f185ca
reviewed_head: 84c9a84868d29c66b50b6612ea937a0a6e647eae
decision: changes_requested
---

# GATE3-COVERAGE-MATRIX 独立复核 r2

## 0. 审查者、来源、范围与约束

- **审查者**：DSH 子 agent `review-gate3-matrix`（由 root agent `lead` 派发；独立上下文；未参与本卡实现或 r2 返修）。
- **被审 head**：`84c9a84868d29c66b50b6612ea937a0a6e647eae`（父提交 `73d2b3d81`；`git log -1` 提交信息 `fix(gate3): r1 REJECT 返修 …`）。
- **基线**：`d86f185caeda55d246609331b6f99174886610a2`；`git diff --name-status d86f185ca..HEAD` 只含 docs/evidence（无 `src/**`、无既有 `tests/**`）。
- **被审对象**：`doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`（下称“矩阵 r2”）、`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §15、`doc/tasks/GATE3-COVERAGE-MATRIX.md` 的 r1 disposition、`verification/GATE3-COVERAGE-MATRIX/four-pieces.log`。
- **只读约束**：除本报告外未修改仓库；r2 只增加文档，测试代码与 r1 相同，因此沿用 r1 的三项目实测：App.Tests **947/0/11/958**、Host.Tests **321/0/74/395**、CoreClient.Tests **186/0/26/212**；本轮重点是对照源码属性和 r1 的 detailed skip 日志复核 §4。
- **复核结束**：`git status --short` 只有本报告 `?? doc/reviews/GATE3-COVERAGE-MATRIX-review-r2.md`；无其它改动。

## 1. verdict

**REJECT（changes requested）**

r1 的两个 P1（R-002 结论口径、R-003 的 7+4 总数）和 P2 的 reader 只读、staleness、P3 的 62/9/825 都已实质修正；§0 也真的把范围扩到了三层。这些改进应保留。

但 r1 R-001 要求的“Host/Core 三层盘点”在新增的 **§4 表**里出现了新的 **P1 事实错误**：

1. **`HostReaderChaptersIntegrationTests`(2) 和 `HostRegionWorkbenchIntegrationTests`(4) 被标成 `plain` / “✅ 本地可跑（计入 321 passed）”，实际两者分别是 `[BookFixtureFact]`、`[RegionFixtureFact]`，Skip 原因都是 `needs sidecar fixture`，本轮 6 个测试全部 SKIP，不在 321 passed 中。** 这两个类恰好是 lead 点名要核的两行；它们不是 plain。
2. §4 的其余行大量按“类”贴一个 gate，而不是按测试方法：`WritePolicyTests` 3/6 plain passed、`CredentialPortTests` 6/7 plain passed、`HostRuntimeIntegrationTests` 1/4 plain passed、`SourceRegistryResilienceTests` 8/9 plain passed、`D4SecurityHarnessTests` 6/6 passed、`CoreTileEmitEndToEndTests` 1/1 passed、`SidecarLifecycleTests` 4/4 passed；但表里分别写成 sidecar/NOT_RUN 或 opt-in/“默认门禁外”。CoreClient 的 `CommandWiringB1/B2` 也在“plain ✅”行里，实际 5 个测试 skipped。
3. §5.2、Gate §15 和 task card disposition 都复述了“区域链 4、章节链 2 … 已在 321/186 passed 中真实执行”这一错误结论；错误已经进入 Gate 评估。

因此**不能按 ACCEPT_WITH_LIMITATIONS 处理**：这不是“只剩 P3/表述”，而是 r2 新增的核心表把“未执行”写成了“已执行”，会直接误导条件 3 的判定。修正 §4（以及 §5.2/Gate §15/task card）后，本矩阵可以作为**三层覆盖清单（部分证据）**；但在那之前，它连“Host/Core 层的准确盘点”都还不能算。

## 2. r1 findings 的 r2 状态

| r1 finding | r2 状态 | 依据 |
|---|---|---|
| **R-001 范围** | **PARTIAL / REOPEN** | §0 已声明三层，§4 也新增了 17 行表；但 §4 的 plain/gate/status 分类错误（见 R2-001/R2-002），结论仍不可用。 |
| **R-002 11 类/2 类口径** | **FIXED** | §5.1 改为“唯一完全无覆盖是设置页错误态一格”；§3 设置错误态改 ❌；不再出现“2 类”。 |
| **R-003 sidecar 计数** | **PARTIAL** | 7+4 总数正确；但“4 类 gate”清单错误（R2-005），`RunBookFixtureFact` 未计入。 |
| **R-004 阅读器只读** | **FIXED** | §3 只读·阅读器引 `ReaderProgressTests.cs:194`，我逐行核对了该测试的只读断言（见 §4）。 |
| **R-005 100 skip 全 E-2** | **PARTIAL** | 已撤回原说法；30/44 总数与我的实测一致；但 §1.1 的 44 明细不是 skip 组成（R2-004）。 |
| **R-006 AC2 每格 `文件:行`** | **PARTIAL / OPEN** | Region、阅读偏好、主题、整书进度等仍无 `文件:行`；task card 也承认“部分修”。 |
| **R-007 AC3 gate 分类** | **PARTIAL / OPEN** | App 的 gate 清单仍错；Host 的 `BookFixtureFact`/`RegionFixtureFact` 不在 §4 的 gate 图例里。 |
| **R-008 staleness** | **FIXED** | §6 明确“快照、无自动失效检测、后续 Task 必须登记可能过时”；结论诚实。 |
| **R-009 数字** | **PARTIAL** | 62、9、删除 825 已修；但 §4 的方法数/总数仍大面积不可复现（R2-003）。 |
| **R-010 证据** | **PARTIAL** | four-pieces 补了三项目 summary 和 App 11 skip 明细；仍无 Host 74 明细、无 exit code/命令。 |
| **R-011 标签/口径** | **PARTIAL** | Host 行已移入 §4；但“15 行”实为 17 行，“12/13 类”口径仍含糊（R2-009）。 |

## 3. 新 findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| **R2-001** | **P1** | 矩阵 `:80,82,97-99`；Gate §15 `:194-196`；task card `:99` | `HostReaderChaptersIntegrationTests`(2) 和 `HostRegionWorkbenchIntegrationTests`(4) 被标 `plain`/“✅ 计入 321 passed”，实际是 `[BookFixtureFact]`/`[RegionFixtureFact]`，两者都先查 sidecar，再查 book/region fixture；本环境 6 个全部 SKIP（原因 `needs sidecar fixture`）。§1.1 自己又把它们算进“30 sidecar”。结论“区域链 4、章节链 2 … 已在 321/186 passed 中真实执行”因此为假。 | `HostReaderChaptersIntegrationTests.cs:34,73`（`[BookFixtureFact]`）；`HostRegionWorkbenchIntegrationTests.cs:36,197,239,303`（`[RegionFixtureFact]`）；`Support/BookFixture.cs:9-20`、`Support/RegionFixture.cs:12-23` 均先 `HostFixture.TryGetSidecarDirectory` 再查 fixture；r1 实跑 74 skip 名单含这两个类共 6 项，原因为 `needs sidecar fixture`。 | 把两行 gate 改为 **sidecar + book/region fixture**，状态改为 **NOT_RUN（E-2）**；从 §5.2、Gate §15、task card disposition 删除“plain/已在 321 passed 执行”的表述；§4 增加 fixture gate 图例。 |
| **R2-002** | **P1** | 矩阵 `:79-95` | §4 按“类”贴一个 gate，掩盖了混合类：`WritePolicyTests` 6 个里 3 个 `[Fact]` 已 passed、3 个 `[HostSidecarFact]` skipped；`CredentialPortTests` 7 个里 6 个 passed、1 个 skipped；`HostRuntimeIntegrationTests` 4 个里 1 个 passed、3 个 skipped；`SourceRegistryResilienceTests` 9 个里 8 个 passed、1 个 skipped；`D4SecurityHarnessTests` 6/6、`CoreTileEmitEndToEndTests` 1/1、`SidecarLifecycleTests` 4/4、`SidecarFailureTests` 3/4 已 passed；`CommandWiringB1/B2` 有 5 个 `[SidecarFact]`/`[S4RegionFixtureFact]` skipped。按行标 sidecar/NOT_RUN 或 opt-in/“默认门禁外”会同时**低估已跑覆盖**、**高估未跑块**。 | `WritePolicyTests.cs:36,49,58,94,127,172`；`CredentialPortTests.cs:42,74,104,130,154,188,196`；`HostRuntimeIntegrationTests.cs:14,61,95,140`；`SourceRegistryResilienceTests.cs`（8 `[Fact]` + 1 `SourceRegistryIpcFact`）；`D4SecurityHarnessTests.cs`（6 `[Fact]`，0 skip）；`CoreTileEmitEndToEndTests.cs:29`（`[Fact]`，0 skip）；`SidecarLifecycleTests.cs:96,110,146,186`（4 passed）；`SidecarFailureTests.cs:14,35,64,104`（3 passed + 1 skip）；`Commands/CommandWiringB1Tests.cs:123,266`、`B2Tests.cs:266,417,463`（skipped）。 | §4 改为“逐测试方法”或至少给每行 `plain passed / fixture-sidecar skipped / opt-in skipped` 三个计数；不要把混合类压成单一 gate/状态。 |
| **R2-003** | **P2** | 矩阵 `:79-95`；Gate §15 `:194-196` | “代表测试文件（方法数）”数字大面积不可复现：我按“带测试 attribute 的方法”数到 `SourceScanSchedulerTests` **50**（文档 57；另有 1 Theory + 12 InlineData，约 62 cases）、`RunGrantRenewalTests` **22**（23）、`HostUnitTests` **12**（14；2 Theory + 7 InlineData）、`CredentialPortTests` **7**（11）、`SourceRecoveryIpcTests` **1**（5）、`SourceRegistryResilienceTests` **9**（10）、`D4SecurityHarnessTests` **6**（7）。这些数字像是把 public helper 方法或不同口径混在一起；文档没有给计数命令。 | 逐文件脚本：attribute 后继方法计数；见 §4 表。`HostUnitTests.cs` 实际是 3 个类（`SingleInstanceTests` 4、`CoexistenceTests` 4、`DataSafetyTests` 4）。 | 明确口径（测试方法 / 测试 case / 全部 public 方法），用可复现命令重算；不要给“方法数”这种混合口径。 |
| **R2-004** | **P2** | 矩阵 `:43-48,136` | §1.1 的 44 明细不是“Host 74 skip 的组成”，而是 **env var 在源码中的出现次数**：`NEWMANGA_FEA11_IPC` 22 处/7 文件、`FEA09_IPC` 5/2、`FEA10_IPC` 2/1、`FEA11_CRASH_STATE` 4/1、`CORE_TILE_E2E` 1/1、`FEA07_A03` 1/1、`FEA11_CRASH_NEGATIVE` 1/1，合计 36（且 `CORE_TILE_E2E` 的测试是 `[Fact]`，已 passed；`FEA11_CRASH_STATE` 是 `Fea11HostAuthIpcTests` 内部的 crash 变量，不是独立 skip gate）。§7 还说“来自 r1 复核的实测”，但 r1 报告给的是另一个组成（FEA09/FEA11/FEA10/FEA07/FEA12），并未给出这份列表。 | 上述 grep 结果；`CoreTileEmitEndToEndTests.cs:16,29`（env 仅决定 artifact 路径，缺 artifact 时 return 不 skip）；`Fea11HostAuthIpcTests.cs:211,269,280`；r1 报告 §5/§6.2。 | 二选一：①按 74 个 skip 的 reason 逐条重数，给出真正的组成；②保留 30/44 总数，删除具体 env 明细，注明“44 = 74-30 的 opt-in 组，本卡未逐条重数”；不要把它归给 r1，也不要列 `CORE_TILE_E2E`。 |
| **R2-005** | **P2** | 矩阵 `:36`；task card `:101` | App.Tests 的 sidecar gate 不是“4 类”清单里写的那样：实际 4 个 **attribute 类型**是 `[HostSidecarFact]`×2、`[RunSidecarFact]`×2、`[RunBookFixtureFact]`×1、`[WritePolicySidecarFact]`×2（共 7 个测试）。文档把 `RunBookFixtureFact` 并进 `RunSidecarFact×3`，又把 `WritePolicySidecarFact` 写成两条 ×1。 | `ChapterCreationTests.cs:163,229`；`RunControllerTests.cs:290,436`（RunSidecar）与 `:344`（RunBookFixture）；`WritePolicyUiTests.cs:54`、`StartupSelfCheckUiTests.cs:14`。 | 改为 4 个 attribute 类型、计数 2/2/1/2；`RunBookFixtureFact` 单独标注“sidecar + BOOK-FIXTURE”。 |
| **R2-006** | **P2** | 矩阵 `:93,95` | CoreClient 两行不可靠：①“wire 命令契约 … CommandWiringB1/B2 plain ✅”实际 B1/B2 有 5 个 skipped；且 26 个 CoreClient skip 中的 `CommandIntegrationTests`(6)、`CoreServiceIntegrationTests`(4)、`HostBridgeIntegrationTests`(3)、`S4RegionReaderCommandTests`(1)、`RunBindingFixTests`(4)、`TransRunPathFixTests`(2) 没有出现在表里。②“sidecar 生命周期/失败 … sidecar NOT_RUN”实际 `SidecarLifecycleTests` 4/4 passed、`SidecarFailureTests` 3/4 passed，只有 1 个 `[SidecarFact]` skipped。 | `Commands/CommandWiringB1Tests.cs:123,266`、`B2Tests.cs:266,417,463`；CoreClient detailed log 的 26 skip 类；`SidecarLifecycleTests.cs:96,110,146,186`；`SidecarFailureTests.cs:14,35,64,104`。 | 把 CoreClient 行拆成“plain command contract/parity（CommandContractV11R 7 + CommandParity 5 等）”与“sidecar command integration（CommandIntegration 6、B1 2、B2 3、RunBinding 4、TransRunPath 2、S4RegionReader 1、CoreService 4、HostBridge 3）”；Sidecar 行单独给 4+3 passed / 1 skipped。 |
| **R2-007** | **P2** | 矩阵 `:61,64-68,93`；卡面 AC2 `:52-53` | AC2 仍不满足：Region 编辑（4 个方法名，无文件/行）、阅读偏好（3 个类名）、主题（`V2ThemeStudioTests` 类名）、整书进度（无文件/行）、书签/工作台只读只有文件无行；导入/导出/渲染仍是 `(:NNN)`，文件靠邻格推断。文档自己承认“【摘要】格以方法名”。 | 矩阵上述行；task card `:103` 也写“部分修”。 | 为每格补 `文件:行`；未读断言的格明确写“未核对（不得作为覆盖依据）”，不要写“断言了 X”；至少把 Region、偏好、主题、整书进度补齐，再谈“12 核查”。 |
| **R2-008** | **P2** | 矩阵 `:13-20,103-113`；Gate §15 `:201` | §0 的“不在本矩阵内”只列了其它测试项目、legacy shell、真机走查；没有列 **AC1 13 类之外的 GUI 关键流程**（回收站 `TrashUiTests`(45 attrs)、命令面板 `V2ShellUiTests`、源恢复 `SourceRecoveryUiTests`、沉浸 F11 `V2ImmersiveReaderTests`、Region 文本比较 `RegionTextComparePanelTests`）。§5.1 的“12 类”和“真无覆盖仅 1 格”只在 13 类范围内成立，Gate §15 没有这个限定。 | 矩阵 §0/§5；上述测试文件；`TrashUiTests` 45 个 attribute；`RegionTextComparePanelTests` 14。 | 在 §0 写“GUI 只覆盖 AC1 的 13 类，不含回收站/命令面板/源恢复 UI 等”，或补这些流程；Gate §15 的“真无覆盖仅 1 格”加“在 13 类内”限定。 |
| **R2-009** | **P3** | 矩阵 `:72-99,103`；task card `:99` | “15 行”实际是 17 个数据行；“四页 × 13 类流程中 12 类”与 §3 的 12 个流程行（+渲染）以及 §4 的 Host 生命周期行不对齐（Host 生命周期从 §3 移入 §4，但 §5 仍按“13 类”计数）。 | 矩阵 §4 数据行计数 17；§3 流程行 13（12 流程 + 渲染）；§4 有 Host 运行时行。 | 修正行数；明确 13 类中哪 12 类在 §3、哪 1 类（Host 生命周期）在 §4；或把 §3 缺的 Host 行补回并交叉引用 §4。 |
| **R2-010** | **P3** | 矩阵 `:61,69` | “只读·书架”仍借 `[WritePolicySidecarFact]` 的 `WritePolicyUiIntegrationTests`（HostController 写策略，不是书架页 UI）；“快捷键·设置”仍用 `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry`（导航/空间测试，不是快捷键）。两处都标了【摘要】/⚠️，但“覆盖”语义仍偏。 | 矩阵上述行；`WritePolicyUiTests.cs:52-128`；`FluentPageTests.cs:166-193`。 | 把书架只读改成“未见书架页独立只读测试，借 Host 写策略测试不可替代”，或降级为未覆盖；设置快捷键格找真正快捷键测试或标“无对应测试”。 |
| **R2-011** | **P3** | Gate §15 `:186-204`；§6 `:121-128`；four-pieces `:1-21` | §6 要求“Gate 裁决引用本矩阵必须注明基线 commit”，但 Gate §15 只写日期/r2 版，没有 `d86f185ca`；four-pieces 补了三项目 summary，仍无命令/exit code、无 Host 74 明细；§4 的 30/44 与 74 明细无法从证据复原。 | Gate §15 第 186-204 行；four-pieces 21 行；矩阵 §6 第 121-128 行。 | Gate §15 加“基线 `d86f185ca`”；four-pieces 补三项目命令/EXIT 与 Host skip 明细（或说明“仅汇总”）；§4 的计数给出复现命令。 |

## 4. 我实际核对的 §4 行（本轮重点）

“文档”= 矩阵 r2 §4 的写法；“实际”= 源码 attribute + r1 detailed skip 日志。

| §4 行 | 文档写法 | 我的核对 | 结论 |
|---|---|---|---|
| `HostReaderChaptersIntegrationTests` `:80` | `(2)`，**plain**，✅ 计入 321 passed | 2 个方法，均 `[BookFixtureFact]`（`HostReaderChaptersIntegrationTests.cs:34,73`）；两个都在 74 skip 名单，reason `needs sidecar fixture`；`Support/BookFixture.cs:9-20` 明确先查 sidecar。 | **错误（P1）** |
| `HostRegionWorkbenchIntegrationTests` `:82` | `(4)`，**plain**，✅ 本地可跑 | 4 个方法，均 `[RegionFixtureFact]`（`:36,197,239,303`）；4 个全 skip，reason `needs sidecar fixture`；`Support/RegionFixture.cs:12-23` 先查 sidecar。 | **错误（P1）** |
| `SourceScanSchedulerTests` `:86` | `(57)`，plain ✅ | **50** 个 `[Fact]` 方法（0 skip）；另有 1 `[Theory]` + 12 `[InlineData`（约 62 cases）。 | plain 对；**数字错**（P2/P3） |
| `RunGrantRenewalTests` `:89` | `(23)`，plain ✅ | **22** 个 `[Fact]` 方法，0 skip。 | plain 对；数字差 1 |
| `HostUnitTests` `:92` | `(14)`，plain ✅ | **12** 个测试方法，分布在 3 个类（`SingleInstanceTests` 4、`CoexistenceTests` 4、`DataSafetyTests` 4）；0 skip；2 Theory + 7 InlineData。 | plain 对；数字错 |
| `WritePolicyTests` `:84` | `(6)`，sidecar，NOT_RUN | **6** 个方法 = 3 `[Fact]`（36,49,127；passed）+ 3 `[HostSidecarFact]`（58,94,172；skipped）。 | 混合；**行级 NOT_RUN 过强**（P1/P2） |
| `CredentialPortTests` `:85` | `(11)`，sidecar，NOT_RUN | **7** 个方法 = 6 `[Fact]` passed + 1 `[HostSidecarFact]`（196）skipped。 | 数字/gate/status 均错 |
| `HostRuntimeIntegrationTests` `:79` | `(4)`，sidecar，NOT_RUN | 4 个方法 = 3 `[HostSidecarFact]` skipped + 1 `[Fact]`（95）passed。 | 混合；NOT_RUN 过强 |
| `SourceRegistryResilienceTests` `:88` | `(10)`，opt-in，默认门禁外 | **9** 个方法 = 8 `[Fact]` passed + 1 `SourceRegistryIpcFact` skipped。 | 混合；数字错 |
| `D4SecurityHarnessTests` `:90` | `(7)`，opt-in `NEWMANGA_EVIDENCE_DIR`，默认门禁外 | **6** 个 `[Fact]`，0 skip（passed）；env 只影响 evidence 目录。 | 分类/状态错（实际全 passed） |
| `CoreTileEmitEndToEndTests` `:91` | `(1)`，opt-in `NEWMANGA_CORE_TILE_E2E`，默认门禁外 | **1** 个 `[Fact]`，0 skip（passed）；env 只决定 artifact 路径，缺 artifact 时写 `executed=false` 并 return，不 skip。 | “默认门禁外”不准确；测试实际执行且 passed（缺 artifact 时早退不校验） |
| `SidecarLifecycleTests` / `SidecarFailureTests` `:95` | sidecar，NOT_RUN | `SidecarLifecycleTests` **4** 个 `[Fact]` 全 passed；`SidecarFailureTests` **3** 个 `[Fact]` passed + 1 个 `[SidecarFact]` skipped。 | 行级 sidecar/NOT_RUN 严重过强 |
| wire 行 `:93` | plain ✅（含 `CommandWiringB1/B2`） | `CommandWiringB1Tests` 有 2 个 `[SidecarFact]` skipped；`B2Tests` 有 2 个 `[SidecarFact]` + 1 个 `[S4RegionFixtureFact]` skipped；CoreClient 26 skip 里的 `CommandIntegrationTests`(6)、`CoreServiceIntegrationTests`(4)、`HostBridgeIntegrationTests`(3)、`S4RegionReaderCommandTests`(1)、`RunBindingFixTests`(4)、`TransRunPathFixTests`(2) 未入表。 | **错误/不完整** |
| `HostReaderProgressIntegrationTests` `:81` | `(3)`，sidecar，NOT_RUN | 3 个方法 = 2 `[BookFixtureFact]` + 1 `[HostSidecarFact]`，全部 skipped。 | NOT_RUN 对；gate 应写 sidecar+book fixture |
| `ExportE2ETests` `:83` | `(2)`，sidecar + `NEWMANGA_EXPORT_*`，NOT_RUN | 2 个 `[HostSidecarFact]`，2 skip。 | 基本对（opt-in 细节需确认） |
| `SourceRecoveryIpcTests` `:87` | `(5)`，opt-in，默认门禁外 | **1** 个方法（`RecoveryIpcFact`）skipped。 | 分类对；数字错 |
| `HostRuntimeIntegrationTests` 之外的 `HostReaderProgress`/`Credential` 等 | — | 见上。 | — |

**抽查结论**：§4 不是“逐测试方法”的盘点，而是“按类名猜 gate”的表；至少 2 行把 skip 写成 passed（P1），6 行把混合类写成单一 sidecar/opt-in（P1/P2），7 行方法数不可复现（P2），CoreClient 两行不完整（P2）。

## 5. 数字复核（r2）

| 指标 | 文档 r2 | 我的复核 | 结论 |
|---|---|---|---|
| `[AvaloniaFact]` 文件 | 62 | **62**（491 个 attribute） | ✅ |
| `ReaderPreferencePersistenceTests` | 9 | **9** | ✅ |
| App.Tests | 947 / 0 / 11 / 958 | 947 / 0 / 11 / 958（r1 实测，r2 代码未变） | ✅ |
| Host.Tests | 321 / 0 / 74 / 395 | 321 / 0 / 74 / 395 | ✅ |
| CoreClient.Tests | 186 / 0 / 26 / 212 | 186 / 0 / 26 / 212 | ✅ |
| App sidecar / 非 sidecar | 7 / 4 | **7 / 4**（sidecar：HostSidecarFact 2 + RunSidecarFact 2 + RunBookFixtureFact 1 + WritePolicySidecarFact 2） | 总数 ✅；gate 清单 ❌（R2-005） |
| Host 74 skip | 30 sidecar + 44 opt-in | **30 + 44**（30 = HostSidecarFact 22 + BookFixture 4 + RegionFixture 4；44 = 74-30） | 总数 ✅；44 明细 ❌（R2-004） |
| §4 方法数 | 57/23/14/11/5/10/7/6/… | 50/22/12/7/1/9/6/6（测试方法） | ❌（R2-003） |
| 12 strict【核对】格 | 12 | **12**（另有 5 个 qualified 格；合计 17 个“核对”字样格） | ✅ 口径成立 |
| §4 数据行 | task card 称“15 行” | **17 行** | ❌（R2-009） |

## 6. §5/§6/§7 的诚实性

- **§5.1**（GUI）：reader 只读已改判并引对测试；设置错误态改 ❌；“唯一完全无覆盖一格”在 13 类范围内成立。这一节比 r1 诚实、准确。
- **§5.2**（Host/Core）：**不诚实/不准确**——把 `HostRegionWorkbench`、`HostReaderChapters` 列为 plain 且“已在 321 passed 执行”，实际是 sidecar+fixture skip；这是 r2 的主要问题。另“plain 部分相当广”整体上仍成立（SourceScan 50、RunGrant 22、HostUnit 12、Credential 6、D4 6、CoreTile 1 等确实 passed），但引用的例子错，必须重写。
- **§5.3**（缺口三分类）：30/44 的算术对（63 + 48 = 111 skip），但“E-2 阻塞”把 Host 30 全部归为 E-2（30 个 skip 的 reason 是 `needs sidecar fixture`，可以；BookFixture/RegionFixture 也先查 sidecar，OK）；“默认门禁外 44”的明细来自 §1.1，需按 R2-004 修正；“真无覆盖仅 1 格”只在 13 类 GUI 内，Gate §15 没有限定（R2-008）。
- **§6**（staleness）：诚实、完整；但 Gate §15 没有按它自己的要求注明基线 commit（R2-011）。
- **§7**（自限）：诚实承认【摘要】不能当已验证、未统计其它项目、未核 legacy/真机；但“§1.1 30/44 来自 r1 实测”这一句把 44 明细误归给 r1，且自认未逐条重数 74（R2-004）。如果保留 30/44 总数、删除 44 明细，这句可改诚实。

## 7. 能否作为条件 3 的判定依据

- **as-is：不能。** 不是因为“还有摘要格”，而是因为 §4 把 6 个实际 skipped 的测试写成已执行，并把至少 6 个混合类写成整类 NOT_RUN/“默认门禁外”；用它判条件 3 会同时高估/低估覆盖。Gate §15 已经复制了其中一条错误（“区域链 4、章节链 2 … 已在 321 passed 执行”）。
- **修正 R2-001/R2-002 后：** 可以成为**三层覆盖清单 / 负面判定（NOT MET）的部分证据**；它仍不能单独证明“条件 3 MET”，因为 30 个 Host sidecar skip + 26 个 CoreClient skip + 7 个 App sidecar 测试未执行，44 个 opt-in real-IPC 也未执行；要判 MET，必须实际执行这些测试（E-2 解 / opt-in 环境）或 Owner 明确接受边界。
- **成为判定依据还缺什么**：
  1. §4 逐测试方法的 gate/status 表（或每行 plain passed / sidecar skipped / opt-in skipped 三计数）；
  2. 修正 §5.2、Gate §15、task card 的“区域链/章节链已执行”表述；
  3. §4 覆盖全部 key Host/Core 流程（至少补齐 Fea09/10/11/12 IPC、GrantIssuer、ExportStalePolicyWire、LegacyShellReal、RealTranslateProvider、CoreClient CommandIntegration/CoreServiceIntegration/HostBridge/S4RegionReader/B1/B2/RunBinding/TransRunPath，或明确写“选样、不穷尽”）；
  4. §1.1 的 30/44 明细可复现（或删除明细，只留总数）；
  5. AC2 的 `文件:行` 补齐（至少 Region/偏好/主题/整书进度）；
  6. §0 明确 AC1 之外的 GUI 流程不在范围（或补上）；
  7. Gate §15 注明基线 `d86f185ca`。

## 8. 我没有验证的面

- E-2 的事实（sidecar 2026-10-23 构建、PyPI 不可达）：沿用既有 finding，未独立验证。
- 44 个 opt-in real-IPC / 崩溃注入测试的实际内容：未设置 env、未用仓库 Python 运行；只核了源码 gate 和 skip 原因。
- 其它测试项目（Presentation.Avalonia/DesignSystem/ApplicationCore/ThemeEngine/Appearance）：未统计。
- `--shell=legacy`、真机人工走查：未核验。
- r2 只改文档，测试代码与 r1 相同；我没有重跑三项目（r1 实跑数据仍适用），但本轮逐文件核对了 §4 的属性和 skip 状态。
- 我没有逐条核完 §4 的 17 行；上表核了 15 行，`ExportE2ETests` 的 `NEWMANGA_EXPORT_*` 细节和 `SidecarLifecycle/Failure` 的 8 个方法只做了属性/skip 计数，没有逐行读断言。

## 9. 最小修复集（按优先级）

1. **R2-001**：`HostReaderChaptersIntegrationTests`、`HostRegionWorkbenchIntegrationTests` 改 `sidecar + book/region fixture`、`NOT_RUN`；删除 §5.2/Gate §15/task card 的“plain/已在 321 passed 执行”。
2. **R2-002/R2-006**：§4 改成逐测试方法（或每行三计数）；修正 WritePolicy/Credential/HostRuntime/SourceRegistry/D4/CoreTile/SidecarLifecycle/SidecarFailure/CommandWiringB1/B2 的混合状态；补 CoreClient CommandIntegration/CoreServiceIntegration/HostBridge/S4RegionReader/B1/B2/RunBinding/TransRunPath 的 sidecar 行。
3. **R2-003**：方法数改为测试方法计数（SourceScan 50、RunGrant 22、HostUnit 12、Credential 7、SourceRecovery 1、SourceRegistry 9、D4 6；Theory 另列 cases），并给计数命令。
4. **R2-004**：删除 §1.1 的 44 明细或按 74 skip 逐条重数；不要列 `CORE_TILE_E2E`，不要归给 r1。
5. **R2-005**：App gate 改为 4 个 attribute 类型、2/2/1/2。
6. **R2-007**：补 Region/偏好/主题/整书进度的 `文件:行`，未读断言的格标“未核对”。
7. **R2-008**：§0 明确 GUI 仅 AC1 13 类；Gate §15 加“在 13 类内”。
8. **R2-009/010/011**：修正“15 行/12 类”口径；设置快捷键/书架只读改标；Gate §15 加基线 commit；four-pieces 补命令/EXIT 与 Host 明细。

---

**审查者声明**：本报告只对 `84c9a84868d29c66b50b6612ea937a0a6e647eae` 有效；未参与实现或返修；结论以上述源码行、r1 detailed skip 日志和属性计数为证据。复核期间除本报告外未修改仓库；`git status --short` 只剩本报告 `??`。
