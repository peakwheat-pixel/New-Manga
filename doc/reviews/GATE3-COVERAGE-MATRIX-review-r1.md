---
task_id: GATE3-COVERAGE-MATRIX
reviewer: DSH 子 agent `review-gate3-matrix`（lead 派发；独立上下文；未参与实现）
reviewer_kind: subagent
author: DSH（commit 73d2b3d8，author peakwheat-pixel）
base_commit: d86f185ca
reviewed_head: 73d2b3d812856e9375fdbbe1d01231a68ca357e7
decision: changes_requested
---

# GATE3-COVERAGE-MATRIX 独立复核 r1

## 0. 审查者、来源、范围与约束

- **审查者**：DSH 子 agent `review-gate3-matrix`（由 root agent `lead` 派发；独立上下文；未参与本卡实现、未参与矩阵编写）。
- **被审 head**：`73d2b3d812856e9375fdbbe1d01231a68ca357e7`（父提交 `d86f185ca`；`git log -1` 提交信息含 `docs(gate3)`）。
- **基线**：`d86f185caeda55d246609331b6f99174886610a2`。
- **被审对象**：`doc/tasks/GATE3-COVERAGE-MATRIX.md`、`doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`（下称“矩阵”）、`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §15（下称“Gate §15”）、`verification/GATE3-COVERAGE-MATRIX/four-pieces.log`。
- **只读约束**：除本报告外未修改仓库文件；所有实验只运行测试、读源码和写 `$env:TEMP` 日志。复核结束时的 `git status --short` 只有本报告 `?? doc/reviews/GATE3-COVERAGE-MATRIX-review-r1.md`，没有其他跟踪/未跟踪改动（`bin/`、`obj/` 为 Git 忽略产物，见 §5）。
- **实际执行**：
  - `git show --stat HEAD`、`git diff d86f185ca..HEAD`；
  - `dotnet test .../NewManga.App.Tests.csproj -c Debug`（4.6 分钟）：**947 passed / 0 failed / 11 skipped / 958 total**；
  - `dotnet test .../NewManga.Host.Tests.csproj -c Debug`：**321 / 0 / 74 / 395**；
  - `dotnet test .../NewManga.CoreClient.Tests.csproj -c Debug`：**186 / 0 / 26 / 212**；
  - 源码/属性计数与 12 个 strict【核对】格的逐格对照（详见 §4、§5）。

## 1. verdict

**REJECT（changes requested）**

矩阵的“逐格测试引用”总体质量比其自我评价更好：12 个 strict【核对】格中，11 个的行号、方法名和断言描述都能对上；剩下的“阅读偏好”格我核了方法数与部分断言，发现数字差 1（§4、§9）。【摘要】也不是偷懒，多数摘要描述与真实断言一致（§4）。它没有把 NOT_RUN 直接汇总成“条件 3 已满足”，也在 §0/§4 明确声明了证据强度——这两点值得保留。

但以下三点是**结论/范围错误**，不是措辞瑕疵，因此不能按 AC2/AC6 接受，也**不能作为条件 3 的判定依据**：

1. **范围错位**：条件 3 原文是“完整 GUI / Core / Host 关键流程”（`audit/V1-FULL-AUDIT/reports/13_RELEASE_GATE.md:27`），矩阵只盘 GUI 四页；“Host 生命周期/恢复”一行全是 ⚠️/NOT_RUN 且只给了 `HostController_…`，没有 Core/Host 流程清单，§4 也没有声明“本矩阵只覆盖 GUI 层”。结论“剩余缺口没有一项是 GUI 没做”因此是拿 GUI 层的结论去替代 GUI/Core/Host 的结论（R-001）。
2. **结论数字自相矛盾**：§3 先说“13 类中 11 类在 headless 下有真实断言”，再说“完全无覆盖仅 2 类（设置错误态、阅读器只读）”。按矩阵自己的口径，11 类 = 至少有一格【核对】的类，则没有【核对】的两类是 **主题/外观**（只有【摘要】）和 **Host 生命周期/恢复**（全 ⚠️），不是它列的两个 cell；而“阅读器独立只读”实际有测试 `ReaderProgressTests.cs:194`（R-002、R-004）。同时“推进路径不是继续补 headless 测试”与它自己列出的“设置错误态无覆盖”冲突——那一项正是补一条 headless 测试就能闭合的。
3. **sidecar 结构性论断错误**：`[HostSidecarFact]` 确实只有 2 个，但 App.Tests 需要 sidecar 的测试类是 **4 个、共 7 个测试**（`CreateChapterHostIntegrationTests` 2、`RunControllerHostIntegrationTests` 3、`WritePolicyUiIntegrationTests` 1、`StartupSelfCheckUiTests` 1），其中 `RunControllerHostIntegrationTests` 正是 run 生命周期集成；“GUI 层几乎不依赖 sidecar / 只有 2 个测试类需要”不成立，§2.2 的 sidecar 清单也漏了 run/self-check/write-policy（R-003）。

**结论**：本矩阵可以保留为**仓库级覆盖清单的起点**，返修后最多只能作为“**GUI 层部分证据**”；在 R-001/R-002/R-003 修正前不能进入集成，Gate §15 也不应继续引用这些结论。

## 2. 逐 AC 判定

| AC | 判定 | 依据 |
|---|---|---|
| **AC1 矩阵结构** | **PASS（结构）/ PARTIAL（范围）** | 表有 14 行：AC1 要求的 13 类流程 + 额外的“四页 headless 渲染”；四页齐。但“Host 生命周期/恢复”行无测试依据（仅 `HostController_…` + E-2 NOT_RUN），Core/Host 流程整体不在表内；见 R-001。 |
| **AC2 逐格代码依据** | **FAIL** | 多格没有 `文件:行`：阅读偏好（只有类名）、Region 编辑（只有 4 个方法名，无文件/行）、主题/外观的 `V2ThemeStudioTests`、焦点格的 `FluentShell_…`、Host 行、整书进度（只有文件）；导入/导出/进度/渲染多格只有 `(:NNN)`，文件名靠邻格推断。且多格断言描述是“类/方法名级”（例如 Region“双向”、偏好“部分 patch 语义”），属于 AC2 明确禁止的“仅凭测试方法名推断覆盖面”。作者用【摘要】披露了这一点，但披露不能替代 AC2 的强制要求。 |
| **AC3 可执行性标注** | **PARTIAL** | 没有逐格标 `[AvaloniaFact]`/`[Fact]`/`[SidecarFact]`；只在一格把 `WritePolicyUiIntegrationTests` 误标成 `[HostSidecarFact]`（实际 `[WritePolicySidecarFact]`，`WritePolicyUiTests.cs:54`）；也没有列出 `RunSidecarFact`、`RunBookFixtureFact`、`WritePolicySidecarFact`、`Fea07CrashParkFact` 等自定义 gate（见 R-005、R-007）。 |
| **AC4 NOT_RUN 归因** | **PARTIAL** | 每个 NOT_RUN 格基本有原因，但 Host 行三格只写“同左”；§2.2 把 Host.Tests 74 skip 的共同原因写成 E-2 sidecar，而其中至少 44 个是 `NEWMANGA_FEA09/10/11/12/07` 显式 opt-in 的 real-IPC 测试，原因不是 E-2（R-005）。 |
| **AC5 零改动** | **PASS** | `git show --stat HEAD` 只有 7 个 doc/evidence 文件（含三指针），无 `src/**`、无既有 `tests/**`；`git diff --stat d86f185ca..HEAD` 一致；复核结束 `git status --short` 除本报告外为空。 |
| **AC6 结论诚实** | **FAIL** | 没有把条件 3 判 MET，这点正确；但“11 类 / 2 类”的口径冲突、“阅读器只读”事实错误、“剩余缺口没有一项是 GUI 没做”与“设置错误态无覆盖”冲突、“不是继续补 headless 测试”与可补的设置错误态测试冲突；§15 原样复制了这些错误（R-002、R-004、R-011）。 |

## 3. Findings

状态均为 `open`（本报告为 r1；返修后在本文件追加 disposition 或开 r2）。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| **R-001** | **P1** | 矩阵 `:4,6-12,47,67-79`；Gate §15 `:198-200`；`audit/.../13_RELEASE_GATE.md:27` | 条件 3 是 GUI/Core/Host 关键流程；矩阵只盘四页 GUI 的 13 类，Host 行全 ⚠️，Core 流程完全未盘点；AC1 列表之外的 GUI 关键流程（回收站、命令面板/Shell 路由、源恢复、沉浸阅读）也未纳入。结论“剩余缺口没有一项是 GUI 没做”把范围缩成 13 类 GUI，无法支撑条件 3 判定。 | 矩阵 §1 只有四个页面列 + 一行 Host；`Host.Tests`/`CoreClient.Tests` 的 `HostRegionWorkbenchIntegrationTests`、`HostReaderProgressIntegrationTests`、`HostRuntimeIntegrationTests`、`ExportE2ETests`、`CommandIntegrationTests`、`S4RegionReaderCommandTests` 等测试类在矩阵里没有出现；`TrashUiTests`（45 个测试 attribute）、`SourceRecoveryUiTests`、`V2ShellUiTests`（命令面板）、`V2ImmersiveReaderTests` 等也未被 13 类覆盖；§4 限制未提 Core/Host 或这些 GUI 流程。 | 在 §0 明确写“本矩阵只覆盖 GUI 四页的 13 类流程”；新增 Core/Host 流程清单（run 生命周期、region 写、导出后端、host 恢复、reader 进度持久化等），每项给测试类/文件/skip 原因；同时列出 AC1 之外的 GUI 流程（回收站、命令面板、源恢复等）是否在范围内；否则把 §3 结论降级为“GUI 层部分结论”。 |
| **R-002** | **P1** | 矩阵 `:62-65,67-79,84`；Gate §15 `:194-196` | “13 类中 11 类有真实断言”按“有【核对】格”口径成立，但紧接着的“完全无覆盖仅 2 类”列的是两个 **cell**（设置错误态、阅读器只读），不是两个 class；按同一口径没有【核对】的是主题/外观（仅【摘要】）和 Host 生命周期/恢复（全 ⚠️）。读者会把“2 类”误当成“只剩两个类没覆盖”，从而低估 Host 类缺口。 | 13 类逐行计数：有至少一个【核对】/“核对（…）；其余摘要”格的为 11 类；主题只有【摘要】，Host 行无任何✅/【核对】。矩阵没有 class 级汇总表。另“剩余缺口没有一项是 GUI 没做”与 §2.3 的“设置错误态无覆盖”直接冲突；后者可用一条 headless 测试闭合。 | 增加“类 × 证据强度”汇总表；把“完全无覆盖”拆成“完全无测试的 cell（设置错误态）”与“无【核对】证据的类（主题、Host 生命周期）”；删除或改写“推进路径不是继续补 headless 测试”为“GUI 还剩 1 个可补的 headless 缺口，Core/Host 另有清单”。 |
| **R-003** | **P1** | 矩阵 `:18-25,37,47,56-60`；测试文件 | `[HostSidecarFact]` = 2 是字面事实，但“只有 2 个测试类需要 sidecar”错误：App.Tests 有 4 个类/7 个测试被 sidecar gate 跳过，其中包括 run 生命周期（`RunControllerHostIntegrationTests`，2×`[RunSidecarFact]` + 1×`[RunBookFixtureFact]`）和 `StartupSelfCheckUiTests`。§2.2 只列了 ChapterCreation 和 WritePolicy，漏了 run/self-check；Host 行里 `HostController_…` 也没有指向这些类。 | `WritePolicyUiTests.cs:52,54`；`StartupSelfCheckUiTests.cs:14`；`RunControllerTests.cs:288,290,344,436`；App.Tests 实跑 11 个 skip 名单中 7 个是 sidecar（`CreateChapterHostIntegrationTests`×2、`RunControllerHostIntegrationTests`×3、`WritePolicyUiIntegrationTests`、`StartupSelfCheckUiTests`）。 | 把 §0 改为“`[HostSidecarFact]` 2 个；sidecar-gated 测试共 4 类 7 个”；§2.2 补全四类；Host 行至少引用 `RunControllerHostIntegrationTests` 的 3 个测试（注明 skip 原因）；`WritePolicyUiIntegrationTests` 的属性改回 `[WritePolicySidecarFact]`。 |
| **R-004** | **P2** | 矩阵 `:37,64`；`ReaderProgressTests.cs:193-213` | 矩阵称“Reader 本身无独立只读测试”“借道设置页同型覆盖”，但 `ReaderProgressTests.ReadOnlyHost_DoesNotPersist_ButReaderKeepsWorking`（`[AvaloniaFact]`，`ReaderProgressTests.cs:194`）就是 Reader 页的独立只读测试，断言：保存结果为 `ReadOnly`、Host 无进度写入、Reader 继续翻页、下一轮保存成功。跨页“借道”也不能证明 Reader 页的只读行为。 | 上述文件行；断言 `LastProgressResult.Status == ReadOnly`、`Progress.TryGet("chapter-1") == null`、`TurnPageAsync` 后 `IsSaved`。 | 把该测试写入“只读·阅读器”格（✅，最好【核对】）；从 §2.3“完全无覆盖”删除；保留“Settings 只读”格独立。 |
| **R-005** | **P2** | 矩阵 `:56-60,74`；Host.Tests/CoreClient.Tests 实跑 | “Host/CoreClient 的 100 个 skip 全部卡在 E-2 sidecar”不成立：Host.Tests 74 skip 中 30 个是 sidecar fixture，至少 44 个是 `NEWMANGA_FEA09_IPC`（17）、`NEWMANGA_FEA11_IPC`（24）、`NEWMANGA_FEA10_IPC`（1）、`NEWMANGA_FEA07_A03`（1）、`NEWMANGA_FEA12_UI_IPC`（1）显式 gate 的 real-IPC 测试；CoreClient 26 全部为 sidecar；App.Tests 11 skip 中 7 个 sidecar、2 个 crash injection、1 个 startup-process、1 个 perf gate。E-2 不能解释全部 100 个。 | 我跑的 `--logger detailed` 输出：Host 321/0/74，reason 计数 30 sidecar + 17 FEA09 + 24 FEA11 + 1 FEA10 + 1 FEA07 + 1 FEA12；CoreClient 186/0/26 全部 sidecar；App.Tests 11 skip 名单见 §5。 | 把“100 个”拆成“56 个 sidecar（Host 30 + CoreClient 26）+ 44 个 opt-in real-IPC（Host）”；说明后者需要 `NEWMANGA_FEAxx_IPC=1` 与仓库 Python（不是单纯 E-2）；§2.2 的“共同原因”只适用于 56 个。 |
| **R-006** | **P2** | 矩阵 `:37,40-47`；卡面 AC2 `:52-53` | 多格缺 `文件:行`，且有些格只有方法名/类名级描述。AC2 原文要求“每格写 `测试名 (文件:行)` 并说明该测试断言了什么；不得仅凭测试方法名推断覆盖面”。【摘要】披露的是“我没读断言”，但不改变 AC2 未满足的事实；读者仍可能把摘要格当覆盖依据。 | 阅读偏好格只有 `ReaderPreferencePersistenceTests（8）+ ReaderPreferenceWiringTests（4）+ ReaderReadingPreferencesTests（7）`，无文件/行；Region 格只有 4 个方法名；主题格 `V2ThemeStudioTests` 无文件/行；Host 行 `HostController_…` 无文件/行；导入/导出/进度/渲染格只有 `(:NNN)`。 | 每个引用的测试补 `文件:行`；对未读断言的格统一写“未核对（不得作为覆盖依据）”，不要写“断言了 X”；把“类摘要”从覆盖结论中剔除。 |
| **R-007** | **P2** | 矩阵 `:19,37`；卡面 AC3 `:54` | AC3 要求区分 `[AvaloniaFact]`/`[Fact]`/`[SidecarFact]`/`[HostSidecarFact]`；矩阵没有逐格属性，且把 `WritePolicyUiIntegrationTests` 写成 `[HostSidecarFact]`（实际 `[WritePolicySidecarFact]`）。自定义 gate 还有 `RunSidecarFact`、`RunBookFixtureFact`、`Fea07CrashParkFact`、`Fea07CrashRecoverFact`、`FEA07StartupProcessFact`、`GitBackedAvaloniaFact`、`PerfGateAvaloniaFact`，矩阵未列。 | `WritePolicyUiTests.cs:132-140`；`RunControllerTests.cs:489-514`；`StartupDiagnosticsTests.cs:463-479`；`Fea07Residual3CrashTests.cs:301-340`；`FluentResidual3VisualEvidenceTests.cs:35-42`；`PerformanceBaselineTests.cs:609-619`。 | 每格加属性列/前缀；§0 增加完整 gate 清单与计数；修正 WritePolicy 的错误标注。 |
| **R-008** | **P2** | 矩阵 `:81-87`；卡面“测试要求”`:74-79` | 本卡无新增测试，矩阵是快照；没有 guard 能让“测试被删/改名/行号漂移”时暴露矩阵过时。行号引用天然脆弱，且 `four-pieces.log` 只是时间点摘要。若未来覆盖率倒退，矩阵不会红，Gate 可能继续引用旧结论。 | 文档-only 变更（AC5 证明零测试改动）；矩阵无 checksum/测试名 guard；`four-pieces.log` 无 skip 名单。 | 在 §4 登记 limitation：“矩阵随 App.Tests 源码漂移而过时；每次 Gate 复核或 App.Tests 变更后必须重跑/重核”；建议加一个只读检查脚本（grep 引用的测试名/行号，找不到即 WARN），或在 check.ps1 加入过期提示。 |
| **R-009** | **P3** | 矩阵 `:17-22` | 数字错误/不可复现：`[AvaloniaFact]` 文件 61 → 我数 **62**（491 个 attribute）；“825 个可见测试方法”无法复现（我数 846 个带测试 attribute 的方法：491 AvaloniaFact + 316 Fact + 2 HostSidecarFact + 20 Theory + 17 AvaloniaTheory；非 Theory 809）；`ReaderPreferencePersistenceTests` 写 8 → 实际 **9** 个 `[Fact]`。这些小数字被 §0/§15 当作“结构性事实”，会削弱整份文档的可信度。 | `Select-String -Path *.cs -Pattern '^\s*\[AvaloniaFact\]\s*$'` → 491 occurrences / 62 files；`ReaderPreferencePersistenceTests.cs:43-225` 共 9 个 `[Fact]`。 | 用可复现命令重算并给出“命令 + 口径”；825 若指别的口径（如去重/排除 helper）要写明；61→62、8→9。 |
| **R-010** | **P3** | `verification/GATE3-COVERAGE-MATRIX/four-pieces.log:12-16`；卡面 Canonical Evidence `:94-97` | 证据文件只有 App.Tests 一行摘要；Host.Tests 74 / CoreClient.Tests 26 不在本卡证据里（我用重跑才验证），11 个 skip 的名字也不在；`four-pieces.log` 没有 EXIT 码、命令和原始输出。按仓库证据纪律，“skip 逐条给原因”没有做到。 | 日志 16 行：check/pins/inventory/App.Tests summary；无 Host/CoreClient 行；无 skip 名单；无 exit code。 | 把三个测试项目的命令、exit code、summary 与 skip 名单（或完整日志路径）写入 `verification/GATE3-COVERAGE-MATRIX/`；至少让 74/26 与 11 个 skip 可追溯。 |
| **R-011** | **P3** | 矩阵 `:35,47,62-65` | 标签/口径细节：Host 行标【摘要】，但内容是“E-2 NOT_RUN、headless 侧仅错误态”，没有可摘要的测试，应写【未覆盖】/NOT_RUN；§2.3 说“2 类”却列了 3 项（设置错误态、阅读器只读、真实窗口人工矩阵）；“四页 headless 渲染”是矩阵额外加的第 14 行，未注明不计入 AC1 的 13 类（§3 说“13 类”）。 | 矩阵原文上述行；表共 14 个流程行。 | 统一标签；把“2 类”改为“2 个 cell + 1 项人工验证”或按 class 汇总；给渲染行加“额外证据，不计入 13 类”。 |

## 4. 我实际核对过的格（逐格对照源码）

“行号/方法匹配”= 指针是否指向矩阵所称的方法；“断言匹配”= 矩阵描述是否与真实断言一致；“结论”= 该格是否可信。

| 格（矩阵行） | 测试 `文件:行` | 行号/方法匹配 | 断言匹配 | 结论 |
|---|---|---|---|---|
| 进入与空态·书架 | `FluentPageTests.cs:25` | ✅（`[AvaloniaFact]` 在 24，方法在 25） | ✅ `State==Error`、`CurrentPage==Library`、`NavigationButton(Workbench)!=null`。注意测试名含 “RetrySurface” 但正文没有 retry 断言；矩阵没有声称有，不算错。 | 一致 |
| 进入与空态·工作台 | `FluentPageTests.cs:38` | ✅（37/38） | ✅ `State==Empty`、`RegionCanvas!=null`、三次 tab 点击 → `ActiveTab` + `selected` class + token 颜色/圆角。 | 一致 |
| 进入与空态·阅读器 | `FluentPageTests.cs:90` | ✅（89/90） | ✅ `State==Error`、`FluentPageHost.Content` 是 `ReaderPageView`。 | 一致（“recoverable”是测试名，正文只断言 Error） |
| 进入与空态·设置 | `FluentPageTests.cs:104` | ✅（103/104） | ✅ `State==ReadOnly`、`IsReadOnly==true`、Content 是 `SettingsPageView`。 | 一致 |
| 四页 headless 渲染 | `FluentPageTests.cs:258` | ✅（257/258） | ✅ 四帧 shelf/workbench/reader/settings，`Assert.All(... PixelSize.Width>0 && Height>0)`；PNG 落盘仅在 `NEWMANGA_CAPTURE_FLUENT_PNGS=1`。 | 一致；不是“视觉正确”，只是非空帧（矩阵已用“可选落盘”限定） |
| 错误态·书架 | `ImportExportUiTests.cs:229` | ✅（228/229） | ✅ `IMPORT_SOURCE_UNAVAILABLE` 在面板文本、`RefreshCalls` 不变、`ImportFileCalls` 单次。 | 一致 |
| 错误态·阅读器 | 同 `FluentPageTests.cs:90` | ✅ | ✅ | 一致（与“进入与空态·阅读器”重复引用） |
| 只读·设置 | 同 `FluentPageTests.cs:104` | ✅ | ✅ | 一致（与进入格重复引用） |
| 阅读偏好 | `ReaderPreferencePersistenceTests.cs` + 两个类 | ✅ 方法存在 | ⚠️ 断言描述（在途/切书/合并/失败可见）与真实测试一致；但该类实际 **9** 个 `[Fact]`，矩阵写 8；`ReaderPreferenceWiringTests`=4、`ReaderReadingPreferencesTests`=7 正确。 | 基本一致，数字需修正 |
| 书签 | `ReaderVisibleControlsTests.cs:58` | ✅（57/58） | ⚠️ 面板隐藏→打开→列出“标记”→添加（Host count 2、p1）→删除（Host count 1、列表无“标记”）。矩阵写“空态”，实际没有显式 empty-state 文案断言，只是“列表里没有旧项”。 | 基本一致，“空态”用词过强 |
| 快捷键·书架 | `FluentPageTests.cs:119` | ✅（118/119） | ✅ 18 gestures、`Conflicts` 为空、Ctrl+D2→Workbench、Tab→Batch、文本聚焦时不吞键。 | 一致 |
| 快捷键·工作台 | 同 `FluentPageTests.cs:119` | ✅ | ✅（Tab→Batch） | 一致 |
| 焦点/a11y | `FluentFocusPageCoverageTests.cs:42` | ✅（41/42） | ✅ 遍历四页；`Focusable && IsEffectivelyVisible && IsEffectivelyEnabled && Bounds>0` 的控件，`Take(8)`，逐个 `Focus(Tab)` 直到可见 focus ring，`Assert.True(ringFound)`。 | 一致（“遍历结构”限定准确） |
| 只读·工作台（摘要） | `RegionWorkbenchUiTests.cs:233` | ✅（232/233） | ✅ 断言读面 2 个 region、`LoadedPageId="p1"`、写控件全禁用、`ReadOnlyBanner` 可见且含“只读”、直接写返回 `ReadOnly`/`HOST_READ_ONLY`、`SetRegionTypeCalls`/`RerenderCalls` 为空。 | 摘要可信；其实比“摘要”更充分 |
| 错误态·工作台（摘要） | `FluentResidualBatchATests.cs:80` | ✅（79/80） | ✅ `State==Error`、“打开控制台”按钮存在、点击后 `ActiveTab==Console` 且 `SpaceConsole` 有 `selected`。 | 摘要可信 |
| 导入（限定核对） | `ImportExportUiTests.cs:153/196/229/251` | ✅ | ✅ 文件：picker 2 个路径、chapter、skip、refresh、状态文本；文件夹：folder path、`import_as_new`；失败：typed code + 不刷新；取消：面板关闭、“未选择文件”、无调用。 | 全部一致 |
| 导出（限定核对） | `ImportExportUiTests.cs:316`、`:420` | ✅ | ✅ 316：导出按钮→面板→Start→running(1/2)→Completed→history→Reveal 全链路；420：三种 scope + 顺序预览 `1.p1`/`2.p2`。`ExportStalePolicyTests.cs` 存在（矩阵未逐项核，标“策略摘要”）。 | 一致 |
| 阅读进度（限定核对） | `LibraryProgressRefreshTests.cs:103/133/166/205` | ✅ | ✅ 103：save 后 shelf 行与 reader 一致、`ProgressRefreshes` 增加；133：close 触发真实 Host 重读；166：导入后 page 数/百分比更新；205：只读拒绝不伪刷新、`Progress.Entries` 为空。 | 一致 |
| Region 编辑（限定核对） | `RegionWorkbenchUiTests.cs:150` 等 | ✅ | ✅ 150：列表→模型、画布→列表+模型双向；171/82/279 也真实存在（我只逐行读了 150 和 233）。 | 主要格一致；该格无 file:line（AC2 问题） |
| 整书进度 | `ReaderVisibleControlsTests.cs:30` | ✅（`Reader_ShowsWholeBookProgressFromTheHostProjection` 在 30） | 未逐行读完整断言；矩阵标“核对（整书进度）”，我只确认方法/行存在。 | 未完全核对（§8） |
| 主题/外观（摘要） | `AppearanceThemeSettingsSinkTests.cs:24` | ✅（23/24，`[Fact]`） | ✅ 把 ThemeSettings 每字段写入 canonical document 并逐项断言；`V2ThemeStudioTests` 类存在（23 个 AvaloniaFact），但矩阵未给行号。 | 摘要可信；属性是 `[Fact]` 而非 `[AvaloniaFact]`（AC3 问题） |

**抽查结论**：矩阵的 strict【核对】格不是“编的”，行号与断言描述整体可靠；问题集中在**摘要格被用于覆盖结论**、**部分格没有 file:line**、以及**结论层的统计/范围**。

## 5. 数字独立复核

| 指标 | 矩阵/§15 | 我的复核 | 方法/备注 |
|---|---|---|---|
| `[HostSidecarFact]` | 2 | **2** | `Select-String -Path *.cs -Pattern '^\s*\[HostSidecarFact\]\s*$'`，均在 `ChapterCreationTests.cs:163,229`。✅ |
| `[AvaloniaFact]` 文件 | 61 | **62** | 491 个 clean attribute，分布在 62 个 `.cs`；无注释/非 attribute 行。❌ 差 1。 |
| 可见测试方法 | 825 | **846**（491+316+2+20+17）；非 Theory **809** | 属性携带方法计数；825 无法由该口径、去重名（846 unique）或 `[Fact]`-only 复现。⚠️ 口径不明。 |
| App.Tests | 947 / 0 / 11 / 958 | **947 / 0 / 11 / 958**（4.6 分钟） | 我的 `dotnet test` 实跑。✅ |
| Host.Tests | 321 / 0 / 74 | **321 / 0 / 74 / 395** | 实跑。✅ |
| CoreClient.Tests | 186 / 0 / 26 | **186 / 0 / 26 / 212** | 实跑。✅ |
| `ReaderPreferencePersistenceTests` | 8 | **9** | `[Fact]`：ToggleDoublePage、ToggleDirection、ZoomControls、FailedSave、SuccessfulSave、RapidZoomClicks、PendingChange、ChangeInFlight、FailedSaveAfterLeaving。❌ |
| 12 个 strict【核对】格 | 12 | **12 strict**（另有 5 个“核对（…）；其余摘要”限定格，合计 17 个“核对”字样格） | 按文档口径“严格【核对】”是 12，数字本身成立；但 5 个限定格的内容有部分行号核对，未被计入 12。✅（口径需说明） |

App.Tests 的 11 个 skip（我实跑名单）：
- sidecar（7）：`CreateChapterHostIntegrationTests`×2、`RunControllerHostIntegrationTests`×3、`WritePolicyUiIntegrationTests`、`StartupSelfCheckUiTests`；
- 非 sidecar（4）：`Fea07Residual3CrashTests`×2（crash injection 环境变量）、`StartupDiagnosticsTests.RealProcessLaunchMatrix`（`NEWMANGA_FEA07_STARTUP_PROCESS=1` + 交互桌面）、`PerformanceBaselineTests.Gated_HotSwitch...`（perf gate）。

复核结束时：`git status --short` 除本报告（`??`）外为空；`bin/`、`obj/` 是 `git status --ignored` 下的既有构建产物，未跟踪、未提交。

## 6. 结构性论断复核

### 6.1 “GUI 层几乎不依赖 sidecar / 只有 2 个测试类需要”

**不成立（按“测试类”口径）。** 逐属性扫描：

| 文件/类 | gate | 测试数 | 实跑状态 |
|---|---|---|---|
| `ChapterCreationTests.cs` / `CreateChapterHostIntegrationTests` | `[HostSidecarFact]` | 2 | skip（sidecar） |
| `RunControllerTests.cs` / `RunControllerHostIntegrationTests` | `[RunSidecarFact]`×2 + `[RunBookFixtureFact]`×1 | 3 | skip（sidecar） |
| `WritePolicyUiTests.cs` / `WritePolicyUiIntegrationTests` | `[WritePolicySidecarFact]` | 1 | skip（sidecar） |
| `StartupSelfCheckUiTests.cs` / `StartupSelfCheckUiTests` | `[WritePolicySidecarFact]` | 1 | skip（sidecar） |

合计 **4 类 / 7 个测试**；“GUI 层几乎不依赖 sidecar”在 7/958 的比例上可以勉强成立，但“只有 2 个测试类需要”是错误陈述，且漏掉的 `RunControllerHostIntegrationTests` 正是 run 生命周期（Core/Host 关键流程）。

### 6.2 “E-2 的阻塞集中在 Host.Tests(74) 与 CoreClient.Tests(26)”

**不完整。** 实测：
- `Host.Tests` 74 skip = **30** 个 `needs sidecar fixture` + **44** 个 opt-in real-IPC（`NEWMANGA_FEA09_IPC` 17、`NEWMANGA_FEA11_IPC` 24、`NEWMANGA_FEA10_IPC` 1、`NEWMANGA_FEA07_A03` 1、`NEWMANGA_FEA12_UI_IPC` 1）；
- `CoreClient.Tests` 26 skip = 26 个 sidecar；
- `App.Tests` 11 skip = 7 个 sidecar + 4 个其他 gate。
因此“100 个 skip 全部卡在 E-2”错误；E-2 只能解释其中 56 个（Host 30 + CoreClient 26），Host 的 44 个是“默认不跑的 real-IPC 选项”，与 E-2 是不同阻塞。

### 6.3 “11 类有覆盖”与“完全无覆盖仅 2 类”

按 AC1 的 13 类逐类计：

| 类 | 至少一个 headless ✅ cell | 至少一个【核对】（含限定） | 结论 |
|---|---|---|---|
| 进入与空态 | ✅ 4 页 | ✅ | 覆盖 |
| 错误态 | ✅ 3 页（设置 ⚠️） | ✅ | 覆盖（设置 cell 未覆盖） |
| 只读 | ✅ 工作台/设置 | ✅ 设置 | 覆盖（Library 卡 sidecar；Reader 实际有测试，矩阵漏了） |
| 导入 | ✅ | ✅（限定） | 覆盖 |
| 导出 | ✅ | ✅（限定） | 覆盖 |
| 阅读进度 | ✅ | ✅（限定） | 覆盖 |
| 阅读偏好 | ✅ | ✅ | 覆盖 |
| 书签 | ✅ | ✅ | 覆盖 |
| Region 编辑 | ✅ | ✅（限定） | 覆盖 |
| 主题/外观 | ✅（仅【摘要】） | ❌ | **无核对证据** |
| 快捷键 | ✅ | ✅ | 覆盖 |
| 焦点/a11y | ✅ | ✅（限定） | 覆盖 |
| Host 生命周期/恢复 | ❌（全 ⚠️） | ❌ | **无 headless 覆盖** |

即：**12/13 类有至少一个 headless ✅ cell；11/13 类有【核对】级证据；没有【核对】的两类是主题/外观和 Host 生命周期/恢复**。矩阵的“11 类”可以用“11 类有【核对】”解释，但它的“完全无覆盖仅 2 类（设置错误态、阅读器只读）”既不是这个 11 类的补集，也不是“类”级统计；其中阅读器只读还有独立测试。**结论层的口径必须重写。**

### 6.4 Core/Host 流程遗漏

条件原文（`audit/.../13_RELEASE_GATE.md:27`）明确是 GUI / Core / Host。矩阵只列 GUI 四页 + 一行 Host 生命周期；实际的 Core/Host 流程测试类包括（均被 skip 或部分覆盖）：
- `HostRegionWorkbenchIntegrationTests`：region 读写、stale revision、只读拒绝、overlay 几何；
- `HostReaderProgressIntegrationTests`：进度持久化/重启恢复/只读拒绝/未知页 typed rejection；
- `HostRuntimeIntegrationTests`：ready/parity/只读/单实例；
- `ExportE2ETests` / `ExportStalePolicyWireTests`：导出后端与 stale 策略；
- `HostReaderChaptersIntegrationTests`：章节/投影读；
- `StartupSelfCheckTests` / `WritePolicyTests`：启动自检与写策略；
- `CommandIntegrationTests` / `S4RegionReaderCommandTests` / `CommandWiringB1/B2Tests`：Core 命令面与 region/reader 写。

矩阵没有给这些类任何一格；因此“条件 3 的剩余缺口没有一项是 GUI 没做”即使对 GUI 成立，也不能代表 Core/Host 缩口。**需要明确写“本矩阵只覆盖 GUI 层”，并把上述清单作为 Core/Host 的后续盘点范围。**

另外，AC1 的 13 类之外还有明显的 GUI 关键流程：回收站（`TrashUiTests`，45 个测试 attribute）、命令面板/Shell 路由（`V2ShellUiTests`）、源恢复（`SourceRecoveryUiTests`）、沉浸阅读 F11（`V2ImmersiveReaderTests`，4）、Region 文本比较（`RegionTextComparePanelTests`，14）等。矩阵没有声称覆盖它们（AC1 也没列），但“完整 GUI 关键流程”若按条件原文理解，这些也是缺口；§3/§15 的“GUI 没做”表述应限定为“AC1 的 13 类 GUI 流程”。

## 7. 可固定性（这份文档未来怎么失效才会被发现）

- 本卡无新增测试（AC5 证据是 `git show --stat HEAD` 只有 docs/evidence），矩阵是**时间点快照**。测试改名、删除、行号漂移都不会让任何测试变红；矩阵与 Gate §15 仍会保留旧结论。
- 行号引用（`:25`、`:258`、`:153` 等）天然脆弱；作者也没有在矩阵里登记“下次重核触发条件”。`four-pieces.log` 只有一行 App.Tests 摘要，连 11 个 skip 名字都不在，无法作为漂移检测基线。
- **应作为 limitation 登记**：建议在 §4 增加“本矩阵在 `d86f185ca` 时点有效；App.Tests/Host.Tests/CoreClient.Tests 任何测试改名、删除或 skip 状态变化后必须重核；未重核前不得引用 §3 结论”。更好的做法是加一个只读 guard 脚本（检查引用的测试名/行号是否存在，缺失即 WARN），或在 `check.ps1` 增加过期提示。这是 R-008。

## 8. 我没有验证的面

- E-2 的具体事实（sidecar 构建日期 2026-10-23、PyPI 不可达、重建需 PyInstaller）：我沿用既有 finding，未独立验证。
- 44 个 `NEWMANGA_FEAxx_IPC` opt-in real-IPC 测试的实际内容/覆盖：没有设置 env、没有仓库 Python 3.14 的情况下运行；只核了它们的 skip 原因。
- `NewManga.Presentation.Avalonia.Tests`、`DesignSystem.Tests`、`ApplicationCore.Tests`、`ThemeEngine.Tests`、`Appearance.Tests` 对 UI/Core 的覆盖：未统计（矩阵也声明未统计）。
- `--shell=legacy` 旧界面路径：未核验（矩阵声明未核验）。
- 真机手动走查、四页视觉正确性：未做；只确认 `PixelSize>0`。
- 矩阵 12 个 strict【核对】格中，我逐行核对了 11 个；`阅读偏好` 只核了方法数与部分断言。另有 qualified 的 `整书进度` 格只核了方法/行存在。
- 我没有重新扫全仓库去找“所有流程的所有测试”；R-004 是定向搜索发现的漏项，不能排除还有别的漏项（例如其他页面的只读/错误态测试）。

## 9. 能否进入集成 / 能否作为条件 3 判定依据

- **能否进入集成（as-is）**：**不能**。按本仓库 Review 规则“P0/P1 未解决或关键验证缺失时不可批准”，R-001/R-002/R-003 未解决；当前只能作为 r1 changes requested。
- **返修后能做什么**：修正 R-001–R-005 后，可以把矩阵作为“**GUI 层四页的覆盖清单（部分证据）**”进入仓库；它的 strict【核对】格与导入/导出/进度/Region 主路径的引用是可靠的，值得保留。
- **能否作为条件 3 的判定依据**：**不能**。条件 3 是 GUI/Core/Host；本矩阵没有 Core/Host 流程清单，Host 行无覆盖，且 44 个 Host skip 不是 E-2；即使 GUI 四页全部覆盖，也不足以判条件 3。条件 3 仍应为 **NOT_MET / 部分证据**，直到：
  1. 增加 Core/Host 流程矩阵（或明确 Owner 接受“只做 GUI 层矩阵”的边界）；
  2. 对 56 个 sidecar skip 与 44 个 opt-in real-IPC skip 分别给出“可执行/不可执行”的处置；
  3. 修正 §3/§15 的结论口径。
- **Gate §15 必须同步返修**：它原样复制了“11 类/2 类/只有 2 个 [HostSidecarFact]/100 个 skip 全部 E-2”这些错误；若只改矩阵不改 §15，Gate 评估会继续引用旧结论。

## 10. 建议的最小返修清单（按优先级）

1. **R-001**：§0 加“本矩阵只覆盖 GUI 层”；新增 Core/Host 流程清单（至少 §6.4 的类），或明确声明不在本卡范围并删除/降级 §3 的越界结论。
2. **R-002**：增加“类 × 证据强度”表；把“完全无覆盖仅 2 类”改为实际统计（1 个未覆盖 cell：设置错误态；主题只有【摘要】；Host 无 headless 生命周期）；删除“不是继续补 headless 测试”的绝对句。
3. **R-003**：把 sidecar 统计改为 4 类/7 测试并列出；§2.2 补全；修正 `WritePolicyUiIntegrationTests` 的 `[HostSidecarFact]` 误标。
4. **R-004**：加入 `ReaderProgressTests.cs:194`，从“完全无覆盖”删除阅读器只读。
5. **R-005**：拆分 100 个 skip（56 sidecar + 44 opt-in real-IPC），不要写“全部卡在 E-2”。
6. **R-006/R-007**：每格补 `文件:行` 与属性；未读断言的格明确写“未核对”，不写“断言了 X”。
7. **R-008**：在 §4 登记本矩阵的时点/失效条件，建议加 guard。
8. **R-009/R-010**：修正 62/846/9 等数字；把三个测试项目的 summary + skip 名单写进 evidence。
9. **R-011**：统一 Host 行标签、修正“2 类/3 项”、注明额外渲染行不计入 13 类。
10. 同步修正 Gate §15 的对应段落。

---

**审查者声明**：本报告只对 `73d2b3d812856e9375fdbbe1d01231a68ca357e7` 有效；未参与实现；所有结论以上述命令/源码行为证据，未引用聊天或旧路径。复核期间除本报告外未修改仓库；`git status --short` 只剩本报告一条 `??`。
