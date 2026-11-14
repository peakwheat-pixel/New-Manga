---
task_id: GATE3-COVERAGE-MATRIX
reviewer: DSH 子 agent `review-gate3-matrix`（lead 派发；独立上下文；未参与实现与 r3 返修）
reviewer_kind: subagent
author: DSH（commit c549cfdd6，author peakwheat-pixel）
base_commit: d86f185ca
reviewed_head: c549cfdd6a98f2d46ba36e721b679bb44d672c47
decision: approved
---

# GATE3-COVERAGE-MATRIX 独立复核 r3

## 0. 审查者、来源、范围与约束

- **审查者**：DSH 子 agent `review-gate3-matrix`（由 root agent `lead` 派发；独立上下文；未参与本卡实现或 r3 返修）。
- **被审 head**：`c549cfdd6a98f2d46ba36e721b679bb44d672c47`（父提交 `84c9a8486`；`git log -1` 提交信息 `fix(gate3): r2 REJECT 返修 …`）。
- **基线**：`d86f185caeda55d246609331b6f99174886610a2`；`git diff --name-status d86f185ca..HEAD` 只含 docs/evidence（无 `src/**`、无既有 `tests/**`）。
- **被审对象**：`doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md`（矩阵 r3）、`doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md` §15、`doc/tasks/GATE3-COVERAGE-MATRIX.md` 的 r1/r2 处置、`verification/GATE3-COVERAGE-MATRIX/{host-skips.txt,coreclient-skips.txt,four-pieces.log}`。
- **只读约束**：除本报告外未修改仓库；r3 只增加文档/证据，测试代码与 r1 相同，因此用 r1 的三项目实测（App 947/0/11/958、Host 321/0/74/395、CoreClient 186/0/26/212）作为基线，再用 r1 的 detailed skip 日志逐项比对 r3 的两个 skip 文件。
- **复核结束**：`git status --short` 只有本报告 `?? doc/reviews/GATE3-COVERAGE-MATRIX-review-r3.md`；无其它改动。

## 1. verdict

**ACCEPT_WITH_LIMITATIONS**

r2 的核心 P1 已实际修正，我逐项验证：

- `HostReaderChaptersIntegrationTests`(2) 与 `HostRegionWorkbenchIntegrationTests`(4) 在 r3 §4.2 已改为 `[BookFixtureFact]` / `[RegionFixtureFact]` 且标 SKIP；6 个测试确实在 `host-skips.txt:45-48,60-61`。**上一版的 false plain/“计入 321 passed”已不存在**。
- `host-skips.txt` 74 行、`coreclient-skips.txt` 26 行，与我 r1 实跑的 detailed skip 日志**逐名比对完全一致（0 差异）**；§4.3 的 9 类计数与 `coreclient-skips.txt` **逐行一致**（6+4+4+3+3+2+2+1+1=26）。
- §4 已不再按类贴 `plain`/`sidecar` 并声称 passed；混合类不再被判为整类 NOT_RUN；方法数/分母已删除；App 的 7+4 与 4 类 gate 已改对；§6 staleness 保留；Gate §15 已登记这次失误并撤回错误表述。
- **现在这份矩阵可以作为“条件 3 NOT MET 的部分证据”**：三项目 passed/skipped 总量、Host 74 / CoreClient 26 的原始 skip 清单、GUI 12/13 + 1 格未覆盖、321/186 passed 都有可复核依据。它不能作为“条件 3 判定依据”（矩阵自己也已这样写，且 100/107 个 skip 未执行）。

**但仍有一组 P2/P3 一致性/完整性问题，不构成 P1**：§4.2 的 Host 类分布表**不完整**（16 行合计 67，而不是它声称的 74；漏了 7 个各 1 skip 的类），`43/31` 的归因与正确的 `30/44` 相反/不符，`107` 与三项目 111 个 skip 不一致，任务卡仍有一处“Host 74 已全部列入”和“§0 已列 AC1 之外流程”的虚假处置，且矩阵 §7/ Gate §15 残留 30/44 的错误撤回表述。这些应在引用 §4.2 作为精确清单前修正，或明确“§4.2 只列主要类，完整清单见 host-skips.txt”。

## 2. r2 P1/P2 处置核验

| r2 finding | r3 状态 | 依据 |
|---|---|---|
| **R2-001** HostReaderChapters/Region 标 plain | **FIXED** | 矩阵 `:99,109` 标 `[RegionFixtureFact]`/`[BookFixtureFact]` + SKIP；`host-skips.txt:45-48,60-61` 6 项；Gate §15 `:201-203` 已登记失误。 |
| **R2-002** 按类贴 gate、混合类 | **FIXED（方法）** | §4.2/4.3 只报类级 skip 数，不再声称整类 passed/NOT_RUN；不再有 `plain` 标签（`grep plain` 只剩历史说明 `:76-78`）。 |
| **R2-003** 方法数/分母不可复现 | **FIXED** | §4 已删除“方法数”列与分母；只保留 skip 数。 |
| **R2-004** 44 明细/30 sidecar 归因 | **PARTIAL/OVER-RETRACTED** | r3 把 30/44 整体撤回（矩阵 `:51,113-114,159`；Gate `:199`），但 30/44 本身是可复现的；r3 的新 `43/31` 反而错（见 R3-002）。 |
| **R2-005** App gate 类型 | **FIXED** | 矩阵 `:36`：4 个 attribute 类型 2/2/1/2；与我源码计数一致。 |
| **R2-006** CoreClient 行 | **FIXED（计数）** | §4.3 9 类与 `coreclient-skips.txt` 逐行一致；但未补“这些类测什么流程”的业务描述（r2 已提示，仍为 P3）。 |
| **R2-007** AC2 `文件:行` | **PARTIAL/OPEN** | Region、偏好、主题、整书进度仍无 `文件:行`；矩阵 `:69-70,66`，任务卡 `:118` 自认部分修。 |
| **R2-008** §0 未列 AC1 之外 GUI 流程 | **OPEN** | 矩阵 §0 `:19-20` 仍只有其它项目/legacy/真机；任务卡 `:119` 声称“已列入”，实际未列。 |
| **R2-009** “15 行/12 类”口径 | **PARTIAL** | 矩阵 §4 已改为实测分布，“15 行”仍只在任务卡 r1 处置 `:99`；§5.1 的“12 类”仍与 §3 的 12 行/Host 生命周期在 §4 的口径不清。 |
| **R2-010** 书架只读/设置快捷键借道 | **OPEN** | 矩阵 `:63,71` 仍用 `[WritePolicySidecarFact]` 与 `ConsoleSpace...` 作为书架只读/设置快捷键证据；已标【摘要】/⚠️，但仍是近似。 |
| **R2-011** Gate 基线/four-pieces | **PARTIAL** | Gate §15 仍无 `d86f185ca`；four-pieces 有三项目 summary，仍无命令/EXIT、无 Host 74 明细（但有独立 skip 文件）。 |

## 3. 新 findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| **R3-001** | **P2** | 矩阵 `:94-114`；`host-skips.txt` | §4.2 声称“74 个 skip 按实测类分布”，但表内 16 行**合计 67**；漏了 **7 个各 1 skip 的类**：`SourceRecoveryIpcTests`（host-skips:10）、`LegacyShellRealTests`(:20)、`SourceRegistryResilienceTests`(:40)、`ExportStalePolicyWireTests`(:56)、`Fea11Scan2HostRuntimeTests`(:62)、`RealTranslateProviderTests`(:65)、`CredentialPortTests`(:66)。因此“合计 74”与表不符；任务卡 `:117` 的“Host 74 已全部列入 §4.2”也不成立。 | 逐类计数：`Select-String`/Group-Object 得 27 类、74 行；§4.2 只列 15 类 + 5 个 1 类行 = 20 类，合计 67；上述 7 行在 host-skips 中存在但矩阵无对应行。 | 补 7 行（各 1），或把最后一行改为“其余 12 类各 1（列出全部 12 个类名）”；让表行合计真正等于 74。 |
| **R3-002** | **P2** | 矩阵 `:51,113-114,159,178`；Gate `:199`；task card `:102,116` | r3 两次说“30 sidecar / 44 opt-in 无法复现/已撤回”（矩阵 §1.1、§4.2、§5.5；Gate §15），但按 `host-skips.txt` + 源码 attribute 映射，**30/44 是正确的**：sidecar/fixture = HostSidecarFact 22（含 `Fea11WatchHostRuntimeTests` 1，r3 把它误记为 opt-in）+ BookFixture 4 + RegionFixture 4 = **30**；opt-in = Fea09 17（11+5+1）+ Fea11 22（HostAuth 4 + Residual 4 + RunGrant 7 + Scan 4 + Source 3）+ Fea10 1 + Fea12 1 + Fea07 1 + SourceRecovery 1 + SourceRegistry 1 = **44**。r3 的“43/31”是漏 7 类 + 把 Fea11Watch 归错后的结果；r2 错在 44 的明细，不在 30/44 总量。 | host-skips 27 类；上述逐类求和；`Fea11WatchHostRuntimeTests.cs:21` 是 `[HostSidecarFact]`；`StartupSelfCheckTests.cs:106,152,161`、`GrantIssuerTests.cs:63,117,186,229` 也是 `[HostSidecarFact]`（§4.2 写成 fixture/fixture-host-control）。 | 不要撤回 30/44；改为“30 = HostSidecarFact 22 + BookFixture 4 + RegionFixture 4；44 = 其余 opt-in（列 7 项）”；删除 §7 `:178` 的残留 30/44 句；Gate §15 `:199` 的“无法复现”改掉。 |
| **R3-003** | **P2** | 矩阵 `:149,153`；task card `:122` | “被 skip 的集成面：Host 74 + CoreClient 26 + App 7 = **107**”与 §2 的“App 11 skip = 7 sidecar + 4 非 sidecar”冲突；**实际三项目 skip 总数是 74+26+11=111**。107 只算了 App 的 7 个 sidecar，漏了 4 个非 sidecar（perf/真实进程/崩溃注入×2）。若主张“要判 MET 必须执行 107 个”，这 4 个也被 skip，且真实进程/崩溃注入与 Host 恢复相关，不能无说明排除。 | 矩阵 §2 `:34,37` 自己写 App 11；§5.3 `:149` 写 App 7；74+26+11=111；107=74+26+7。 | 改为“107 个 sidecar/集成相关 + 4 个 App 非 sidecar（perf/真实进程/崩溃注入）＝111 个 skip”，或明确“107 只指 sidecar/集成面，另 4 个非 sidecar 不计入该子集”。 |
| **R3-004** | **P2** | task card `:117,119` | 任务卡称“Host 的 74 已全部列入 §4.2（含 Trash/GrantIssuer/Export）”与“§0 未列 AC1 之外的 GUI 流程 — 已列入（其它测试项目、legacy shell、真机走查）”；两句均不成立：§4.2 漏 7 类；§0 `:19-20` 的“不在本矩阵内”没有列回收站/命令面板/源恢复 UI/沉浸 F11 等 AC1 之外 GUI 流程。 | 见 R3-001；矩阵 §0 `:19-20`；`TrashUiTests`、`V2ShellUiTests`、`SourceRecoveryUiTests`、`V2ImmersiveReaderTests` 不在 §0/§3/§4 的任何一格。 | 任务卡 `:117` 改为“17 个主要类，完整 74 项见 host-skips.txt”；`:119` 改为“AC1 之外 GUI 流程仍未列入，属已知限制”，或真的补进 §0。 |
| **R3-005** | **P2** | task card `:99,101,102`（r1 处置） | r1 处置表仍写“HostReaderChapters/Region plain”“RunSidecarFact×3”“30 sidecar + 44 opt-in 已修”；这些已被 r2/r3 处置否决，但表未标“已被取代”。历史表可以保留，但不能让读者以为它仍是 current。 | task card `:99-102` vs `:113-116`；Gate `:199`。 | 在 r1 处置表前加“已被 r2/r3 处置取代；以 r2/r3 与矩阵 §4 为准”，或逐行加删除线/更正注记。 |
| **R3-006** | **P3** | 矩阵 `:100,107,111` | §4.2 的“性质”列有错：`GrantIssuerTests` 标“fixture/host-control”实为 `[HostSidecarFact]`；`StartupSelfCheckTests` 标“fixture”实为 `[HostSidecarFact]`；`Fea11WatchHostRuntimeTests` 标“opt-in IPC”实为 `[HostSidecarFact]`。表头已写“据类名/attribute 判断，未逐条核实”，所以是“未核实标签”，不是已证结论。 | `GrantIssuerTests.cs:63,117,186,229`；`StartupSelfCheckTests.cs:106,152,161`；`Fea11WatchHostRuntimeTests.cs:21`。 | 要么逐类核 attribute 后重写“性质”列，要么把该列改为“未核实（仅供类名索引）”；不要用 fixture/opt-in 字样误导。 |
| **R3-007** | **P3** | 矩阵 `:1,178`；Gate `:186`；task card `:99` | 残留过期表述：矩阵标题仍写“r2 返修版”；§7 `:178` 仍说“§1.1 的 30/44 拆分数字来自 r1 复核的实测”（§1.1 `:51` 已撤回 30/44）；Gate `:186` 标题仍“r2 返修版”；task card `:99` 仍“15 行”。 | 上述行；实际是 r3 head、§4 17 行表（r3 后已重写为 §4.2/4.3）、30/44 已在 §1.1 撤回。 | 标题改 r3；删/改 §7 `:178`；Gate 标题改 r3；task card 的 15 行改“r3 §4.2/4.3”。 |
| **R3-008** | **P2** | 矩阵 `:63,66-70,71`；task card `:118` | AC2 仍未满足：Region（4 个方法名，无文件/行）、阅读偏好（3 个类名）、主题（`V2ThemeStudioTests` 类名）、整书进度（无文件/行）；设置快捷键仍用 `ConsoleSpaceUsesWorkbenchConsoleAndSettingsRemainANonSpaceEntry`（空间/导航测试，不是快捷键），书架只读仍借 HostController 写策略测试。文档标【摘要】/⚠️并声明不是已验证，但这些格不能作为“覆盖”证据。 | 矩阵上述行；任务卡 `:118` 自认“部分修”。 | 补 `文件:行`；未读断言的格写“未核对（仅索引）”；把设置快捷键/书架只读改为“无对应测试”或找真正测试。 |
| **R3-009** | **P3** | 矩阵 `:19-20,144-145`；Gate `:205` | §0 的“不在本矩阵内”只说其它项目/legacy/真机，未说“GUI 只覆盖 AC1 的 13 类，不含回收站/命令面板/源恢复 UI/沉浸”；§5.1 的“12 类/唯一 1 格”只在 13 类内成立，Gate `:205` 的“真无覆盖仅 1 格”没有限定。 | 矩阵 §0；`TrashUiTests`、`V2ShellUiTests`、`SourceRecoveryUiTests`、`V2ImmersiveReaderTests` 未入矩阵；任务卡 `:119` 误称已列。 | §0 加“GUI 仅 13 类”；Gate `:205` 加“在 13 类内”；或补 AC1 之外流程。 |
| **R3-010** | **P3** | Gate `:186-205`；four-pieces `:1-22` | §6 要求“Gate 裁决引用本矩阵必须注明基线 commit”，Gate §15 仍无 `d86f185ca`；four-pieces 只有 summary，无命令/EXIT；§4.2 的 74 分布不能从 four-pieces 复原（需依赖 host-skips.txt）。 | Gate §15；four-pieces；独立 skip 文件完整。 | Gate §15 加基线；four-pieces 加命令/EXIT 或明确“明细见 host-skips/coreclient-skips”。 |

## 4. skip 文件与 §4.2/§4.3 的逐行核对

### 4.1 原始文件可信度

- `host-skips.txt` 74 行、`coreclient-skips.txt` 26 行；我把两个文件的名字与 r1 的 `--logger detailed` 日志逐名比对：**host 74/74、coreclient 26/26，0 差异**。文件是真实运行的 skip 输出，不是手写摘要。
- `host-skips.txt` 按类计数（27 类）与上述 74 一致；`coreclient-skips.txt` 按类计数为 26（`Commands.*` 18 + `CoreServiceIntegrationTests` 4 + `HostBridgeIntegrationTests` 3 + `SidecarFailureTests` 1）。

### 4.2 §4.3（CoreClient）——逐行一致

| 类 | 表 | 文件行 | 一致 |
|---|---:|---:|---|
| `CommandIntegrationTests` | 6 | coreclient `:16-21` | ✅ |
| `CoreServiceIntegrationTests` | 4 | `:3-6` | ✅ |
| `RunBindingFixTests` | 4 | `:12-15` | ✅ |
| `CommandWiringB2Tests` | 3 | `:9-11` | ✅ |
| `HostBridgeIntegrationTests` | 3 | `:22-24` | ✅ |
| `CommandWiringB1Tests` | 2 | `:7-8` | ✅ |
| `TransRunPathFixTests` | 2 | `:1-2` | ✅ |
| `S4RegionReaderCommandTests` | 1 | `:26` | ✅ |
| `SidecarFailureTests` | 1 | `:25` | ✅ |
| **合计** | **26** | 26 行 | ✅ |

### 4.3 §4.2（Host）——列出的类计数对，但表不完整

- 表内 16 行逐类计数与 `host-skips.txt` 的类计数**一致**（Production 11、RunGrant 7、UiImport 5、Region 4、GrantIssuer 4、HostAuth 4、Residual 4、Scan 4、Source 3、HostRuntime 3、Progress 3、Startup 3、WritePolicy 3、Chapters 2、ExportE2E 2、5 个各 1）。
- 但 16 行合计 **67**，不是表尾的 **74**；`host-skips.txt` 还有 7 个各 1 的类未入表：
  - `SourceRecoveryIpcTests`（`host-skips.txt:10`）
  - `LegacyShellRealTests`（`:20`）
  - `SourceRegistryResilienceTests`（`:40`）
  - `ExportStalePolicyWireTests`（`:56`）
  - `Fea11Scan2HostRuntimeTests`（`:62`）
  - `RealTranslateProviderTests`（`:65`）
  - `CredentialPortTests`（`:66`）
- 因此任务卡 `:117` “Host 的 74 已全部列入 §4.2”不成立；矩阵 `:113` 的“合计 74”是期望值，不是表内行之和。

### 4.4 30/44 的正确映射（r3 过度撤回）

| 类别 | 数量 | 组成 |
|---|---:|---|
| sidecar + fixture | **30** | `HostSidecarFact` 22 + `BookFixtureFact` 4（Chapters 2 + Progress 2）+ `RegionFixtureFact` 4（Region 4） |
| opt-in | **44** | Fea09 17（Production 11 + UiImport 5 + Real 1）+ Fea11 22（HostAuth 4 + Residual 4 + RunGrant 7 + Scan 4 + Source 3）+ Fea10 1 + Fea12 1 + Fea07 1 + SourceRecovery 1 + SourceRegistry 1 |
| 合计 | 74 | — |

r3 的 `43/31` 与上表差 1/1：它把 `Fea11WatchHostRuntimeTests`（`[HostSidecarFact]`，1）算进 opt-in，又把 `SourceRecovery`/`SourceRegistry` 两个 opt-in 算进 fixture/sidecar（连同其余 5 个 omitted sidecar），所以得到 43/31。**正确的总量 30/44 不是“二手结论”，可以从两个 skip 文件 + attribute 类型复现**；r2 的问题是 44 的明细列表，不是 30/44 总量。

## 5. 数字与残留表述

| 项 | 结果 | 说明 |
|---|---|---|
| App.Tests | 947/0/11/958 | 与 r1 实测一致 |
| Host.Tests | 321/0/74/395 | 与 r1 实测一致 |
| CoreClient.Tests | 186/0/26/212 | 与 r1 实测一致 |
| host-skips 行数 | 74 | 与我 r1 detailed 日志 0 差异 |
| coreclient-skips 行数 | 26 | 与我 r1 detailed 日志 0 差异 |
| §4.2 行合计 | **67** | 表尾 `:113` 写 74；漏 7 类（R3-001） |
| 30/44 | **30/44 正确** | r3 `43/31` 错；r3/Gate 的“30/44 无法复现”错（R3-002） |
| 三项目 skip 总数 | **111** | 74+26+11；矩阵 `:149,153` 的 107 只计 App 7 sidecar（R3-003） |
| 12 strict【核对】格 | 12 | 与矩阵 `:174` 一致 |
| 矩阵/Gate 标题 | 仍“r2 返修版” | 应为 r3（R3-007） |

**残留引用已撤回数字**：
- 矩阵 §7 `:178` 仍写“§1.1 的 30/44 拆分数字来自 r1 复核的实测…”，但 §1.1 `:51` 已说 30/44 撤回；这句应删/改。
- Gate §15 `:199` 仍写“30 sidecar / 44 opt-in 两说法均已撤回…后者我实测无法复现”；30/44 是可复现的（R3-002）。
- task card `:102,116` 一个说 30/44 “已修”，一个说“已撤回”；r1 处置表 `:99,101` 仍写 plain/RunSidecar×3，未标“已被 r2/r3 取代”（R3-005）。

## 6. 能否作为“条件 3 NOT MET 的部分证据”

**可以，但有明确限制。**

支持“NOT MET 部分证据”的部分：
1. 三个项目的 passed/skipped 总量有 r1 实测与 r3 four-pieces 双份支持；`host-skips.txt` / `coreclient-skips.txt` 与我 r1 的 detailed skip 日志逐名一致（74/74、26/26），是真实的 skip 清单。
2. Host 74 + CoreClient 26 = 100 个 skip 在默认无夹具环境确实 NOT_RUN；App 11 skip（7 sidecar + 4 非 sidecar）也真实存在。
3. GUI 12/13 有测试、唯一完全无覆盖是设置页错误态；`ReaderProgressTests.cs:194` 的 reader 只读断言我已在 r2 逐行核对。
4. 矩阵已明确“不能作为条件 3 判定依据”；这与我 r1/r2 的结论一致。

限制（在引用 §4.2 作为精确清单前应修）：
1. §4.2 不是完整 74 类分布（67/74；漏 7 类）；引用时应以 `host-skips.txt` 为准，或在矩阵补 7 行。
2. `30/44` 的正确总量被错误撤回、`43/31` 与 `107` 数字不对；`107` 与 111 的差额（App 4 个非 sidecar）需说明。
3. AC2 的 Region/偏好/主题/整书进度仍无 `文件:行`；§0 未列 AC1 之外 GUI 流程；这些使“GUI 12/13”只能作为 13 类内的部分证据。
4. 任务卡 r1 处置表残留 plain/Run×3/30+44；Gate 标题/基线、矩阵标题/§7 残留需清理。

**结论**：本矩阵现在可以作为**“条件 3 NOT MET 的部分证据”**（结论有 skip 文件和三项目实测支持），但**不能**作为“条件 3 判定依据”，也不能把 §4.2 当作精确的 74 类分布；修正 R3-001/R3-002/R3-003 后，§4 的类分布才可作为精确附录引用。

## 7. 我没有验证的面

- E-2 的具体事实（sidecar 构建日期、PyPI）：沿用既有 finding，未独立验证。
- 44 个 opt-in real-IPC / 崩溃注入测试的断言与内容：未设置 env、未用仓库 Python 运行；只核了 skip 文件/attribute 名称。
- 其它测试项目、legacy shell、真机走查：未核。
- 我没有重跑三项目（r3 只改文档；r1 的 947/321/186 数据仍适用）；我用 r1 的 detailed 日志核对了 r3 的 skip 文件。
- §4.2 的 27 类我只核了计数与 7 个缺失类的行号；没有逐条读每个 skip 的 reason（r3 表头也声明“据类名/attribute 判断，未逐条核实”）。
- AC2 的 12 个 strict【核对】格沿用 r1/r2 的逐行核对，r3 未新增断言核对。

## 8. 最小修复集（P2/P3，不阻塞“部分证据”用途）

1. **R3-001**：§4.2 补 7 个 1-skip 类（或把最后一行改成完整 12 个类名），让表行合计真正 74；任务卡 `:117` 改为“主要类 + 完整清单见 host-skips.txt”。
2. **R3-002**：恢复 30/44 的正确映射；删除“无法复现/已撤回”与 §7 `:178` 残留；Gate `:199` 同步改。
3. **R3-003**：107 → 111，或明确“107 = sidecar/集成面，App 另有 4 个非 sidecar skip”；矩阵 `:149,153`、任务卡 `:122` 同步。
4. **R3-004**：任务卡 `:117`/`:119` 的虚假“已全部/已列入”改正。
5. **R3-005**：r1 处置表标“已被 r2/r3 取代”，或更正 plain/Run×3/30+44。
6. **R3-008/R3-009**：补 AC2 的 `文件:行`；§0 明确 GUI 仅 13 类（或补回收站/命令面板/源恢复等）。
7. **R3-007/R3-010**：标题改 r3；Gate §15 加基线 `d86f185ca`；four-pieces 加命令/EXIT。

---

**审查者声明**：本报告只对 `c549cfdd6a98f2d46ba36e721b679bb44d672c47` 有效；未参与实现或返修；结论以上述 skip 文件逐名比对、源码行和 r1 detailed 日志为证据。复核期间除本报告外未修改仓库；`git status --short` 只剩本报告 `??`。
