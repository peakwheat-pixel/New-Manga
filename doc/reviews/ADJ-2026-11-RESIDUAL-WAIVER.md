# ADJ-2026-11-RESIDUAL-WAIVER（R0 裁决记录 v2 · 2026-11-08）

> 裁决人：**DSH**（Lead/Architect/Integrator）。裁决依据：用户 2026-11-08 指令（残余收口程序提示词：把 4 个 `closed_with_limitations` 节点逐项收口到 `done`）+ 全权授权；独立 scope review `doc/reviews/RESIDUAL-WAIVER-1-scope-r1.md`（session `4092531d-…`，verdict **NOT_RECOMMENDED**）→ **DSH 接受其结论并据此改写 R0 v1 的分类**。用户可事后推翻本裁决；推翻后节点回到 `closed_with_limitations`。
> 被审 head：`4070f0043`（main，clean）。基线重钉（本轮实测）：pytest **3390 passed / 10 skipped**；.NET **1691 passed / 0 failed / 96 skipped**；pins **18/18**。

## 0. 本裁决不构成什么（必读边界）

- **`NOT_APPLICABLE` ≠ PASS ≠ 实测通过**；`NOT_RUN` 证据一律保留。
- **不删除任何 limitation**：历史 Review/证据/limitation 原文保持原字节；本裁决只在节点翻 `done` 时以 append-only 方式登记 AC 行改写。
- **不宣称可发布**：即使 4 节点 done，`Technical Gate=NOT_SATISFIED`、真机 L3/L4 未执行的事实不变。
- **可重开**：接入交互式原生会话 / 产品新增需求时，本裁决的 NA 项必须重开。
- 不写「FEA-07/FEA-11 完全实现」「L-G1 关闭」「C-17 §3.3 完全实现」。

## 1. R0 v1 被推翻的部分（scope review 结论 + DSH 采纳）

R0 v1 把 10 项笼统判为「不可 CI 关闭」。独立评审给出反证：

| R0 v1 判断 | 评审反证（摘要） | DSH 裁决 |
|---|---|---|
| FEA-07 AC1 整体 C4 | A03 真库/ACK 重连/真实 Run 可用 gated 真实 sidecar 测（`ChapterCreationTests.cs:161-251`、`RunControllerTests.cs:284-440`、`Fea11SourceIpcTests.cs:437`、`tests/fea11/test_source_lineage_run.py:8`） | **拆分**：原生 IME=原生未执行；其余 **C1 进 R4** |
| FEA-07 AC2 整体 C4 | `(SessionId, RegionId)` 单写 owner 在 `WindowBroker.cs:24-66` **尚未实现**；ADJ-2026-11-01 U-03 已冻结语义 → 是功能缺口不是硬件 | **拆分**：单写 owner + Host 生命周期 **C1 进 R4**；真实双屏落位=原生未执行 |
| FEA-07 AC5「无硬件」 | 本机 **2 个活动显示器**（`Screen.AllScreens`）且仓库记录 3 个虚拟适配器（`doc/tasks/P20-MEM-OPT-1.md:32`、`verification/GPU-ORT-PROBE-1/REPORT.md:25`）；`GOAL-PROGRESS:311` 原文是「本机**可能**无双屏」 | **改口径**：不是「无硬件」，是「**原生交互矩阵未执行**」→ 原生未执行（非 NA 的「没有硬件」） |
| FEA-06-RESIDUAL-2 整体 C4 | Tab 遍历与 a11y 属性可在 headless 断言（`FluentFocusPageCoverageTests.cs:42-59`、`V2AccessibilityTests.cs:24,137,201`） | **拆分**：Tab 遍历 + a11y 属性 **C1 进 R2**；原生 a11y 行为/200% DPI/原生截图=原生未执行 |
| FEA-11 AC11-3/L-M1 判「C-15 能力外、无消费者」 | C-15 §3.2 `:230` **明确点名「插页」**需 pixel 证据匹配；`matcher.py:164-194/219-227/307-333` 是真实消费者；PDF 降级导致全页 needs_confirmation | **改判 BLOCKED（能力缺口）**，不 NA；若要 NA 须产品显式决定并写清用户可见后果 |
| FEA-11 AC11-6 判「C-15 冻结规则」 | C-17 `:278` 允许「能证明同一」的 relink（无法证明才转 repoint）；现拒绝源于 folder grant 缺 `container_facts`（`service.py:467-478`）+ folder identity 键疑似不符 C-15 `:216`（`L-S4-2`），且**无测试**（`FEA-11-r7.md:34` R7-05 open） | **不 waive**：进 R3（补判别测试 + 成员重排/多项目 + L-S4-2 缺陷登记） |
| 「其他 L 项都不属节点 AC」 | L-1/L-8/L-9 分别是 AC11-8/AC11-9 的残项；只有 L-11（IPC/App.Tests flake）是纯测试债务；「大库冷启动成本」属 SCAN 线 | **改口径**：逐 L 项映射；仅 L-11 登记测试债务 |
| 「10 项」清单 | PLAN §2 表只有 8 行，且与 DSH 清单不一致 | **以本文件 §2 的 12 项为准**（逐 AC 子项拆分） |

## 2. 裁决表 v2（12 项，逐 AC 子项；不得再用「无硬件」作唯一理由）

| # | 节点 | 目标层 | anchor | 类别 | 裁决 | 依据 / 承载 |
|---|---|---|---|---|---|---|
| W-01 | FEA-07 | AC1 子项「原生 IME」 | `doc/tasks/FEA-07.md:297,380` | C4 | **NA（原生未执行）** | 无可执行的原生 IME 会话；保留 `NOT_RUN`；reopen=接入交互式原生会话 |
| W-02 | FEA-07 | AC1 子项「A03 真库/ACK 重连/真实 Run」 | 同上 | **C1（不 waive）** | **进 R4** | gated 真实 sidecar/真实 SQLite 先例（`ChapterCreationTests.cs:161-251` 等）；「真库」定义=临时根下真实 SQLite（合成内容），与 `:310` 禁止范围不冲突（须在卡面写明） |
| W-03 | FEA-07 | AC2 子项「`(SessionId, RegionId)` 单写 owner + Host 生命周期」 | `doc/tasks/FEA-07.md:298,381` | **C1（不 waive）** | **进 R4** | 功能未实现（`WindowBroker.cs:24-66` 仅角色登记）；ADJ-2026-11-01:20 已冻结语义 |
| W-04 | FEA-07 | AC2 子项「真实双屏 broker 落位」 | 同上 | C4 | **NA（原生未执行）** | 需交互式原生会话；保留 `NOT_RUN` |
| W-05 | FEA-07 | AC5 原生矩阵（双屏/拔屏/DPI 100–200%） | `doc/tasks/FEA-07.md:301,309,379` | C4 | **NA（原生未执行；「无硬件」表述作废）** | 本机 2 活动屏 + 3 虚拟适配器（`P20-MEM-OPT-1.md:32`）；`GOAL-PROGRESS:311` 仅为推测；reopen=在交互式原生会话执行矩阵 |
| W-06 | FEA-06-RESIDUAL-2 | 原生 a11y（Narrator/屏幕阅读器行为）、200% DPI 像素、原生桌面截图 | `doc/tasks/FEA-06-RESIDUAL-2.md:79`；`r2r3-findings-disposition.md:30` | C4 | **NA（原生未执行）** | headless 固定 96 DPI；保留 `NOT_RUN` |
| W-07 | FEA-06-RESIDUAL-2 | 完整 Tab 遍历 + a11y 属性/UIA 树断言 | 同上 | **C1（不 waive）** | **进 R2** | headless 可断言焦点顺序与 `AutomationProperties`；现状仅零星覆盖 |
| W-08 | FEA-11 | AC11-1 / L-STARTUP（启动不做全量内容扫描） | `doc/tasks/FEA-11.md:244-247`；`AD-003:87-93`；`C-01b:84`（SC-25）；`C-17:18` | C3 | **NA（契约解释 + 产品范围）** | 依据：四项封闭检测组合**不含**启动全量扫描（AD-003 §3.6 = C-01b SC-25）；C-17 v1.1 `source_list_scan_targets` **只枚举目标不读内容**。**不得写「C-17 规定不做」**；保留 900s/下次访问延迟边界 |
| W-09 | FEA-11 | AC11-3 / L-M1（PDF 插页 pixel profile） | `C-15:214,218,223-231`；`scanner.py:814-816`；`matcher.py:164-194` | **C2/BLOCKED（不 NA）** | **BLOCKED** | C-15 §3.2 `:230` 明确覆盖「插页」；matcher 是消费者。**若要 NA，须产品显式决定「PDF 插页不做自动匹配、接受全页 needs_confirmation」并由用户/DSH 记录后果**；否则另卡（PDF raster seam + 依赖/许可证评估） |
| W-10 | FEA-11 | AC11-6 folder relink | `doc/tasks/FEA-11.md:108`；`C-17:278`；`C-15:216`；`service.py:467-478`；`runtime.py:978-991` | C2 | **BLOCKED → 进 R3** | 契约允许「能证明同一」；现 fail-closed 源于 grant 形状与 folder identity 键；须补判别测试 + 成员重排/多项目 + 登记 `L-S4-2` |
| W-11 | FEA-11 | L-11（IPC / App.Tests 偶发 flaky） | `FEA-11-r7-acceptance.md:18-28` | C1（基础设施） | **登记为测试债务，不属节点 AC** | 仅此项允许「不属节点 AC」 |
| W-12 | FEA-11 | 「大库冷启动成本未标定」 | `FEA-11-SCAN-1.md:208,226`；`FEA-11-SCAN-2.md:252` | 非本节点 | **不属 FEA-11 节点 AC** | 属 SCAN 线；R0 v1 张冠李戴，纠正 |

**未 waive 且必须由实现关闭的项**：W-02/W-03/W-07/W-09-能力面/W-10 + FEA-07 AC3/AC4/AC6 + FEA-06-RESIDUAL-2 五个依赖格 + FEA-11 AC11-7/AC11-9/L-M4/AC11-5 回填 + R1 的 ACK fresh grant。

## 3. 治理前置：翻 `done` 的 AC 行改写（必须显式授权并逐条登记）

- **事实**：`check.ps1:814-851` 要求 `status: done` 时不得存在未勾选或 `<<PARTIAL>>/<<BLOCKED>>` 的 AC 行；4 张节点卡共有 **17 条**未勾选 AC（FEA-07 7、FEA-11 9、HOST-AUTH-1 1；RESIDUAL-2 的 AC1–4 已勾选）。翻 done **必须**把相关行改为 `[x] <<MET>>` 或 `[x] <<NOT_APPLICABLE: 原因>>`。
- **冲突**：`09_COLLABORATION:79` 规定 `closed_with_limitations` 「除新授权外不恢复实施」；`FEA-11-HOST-AUTH-1` 的 Codex 终裁（`doc/tasks/FEA-11-HOST-AUTH-1.md:95`）要求「AC3 保持 PARTIAL，不改写为 PASS」。
- **DSH 裁决**：用户 2026-11-08 指令（要求把 4 节点「逐项收口到 done」）构成 **新授权**，可翻转上述终态；执行方式：
  1. **按节点逐个翻转**，且仅在该节点全部 C1 项完成并 MET 之后；
  2. 翻转时在**本文件追加**「AC 行 before/after + 依据 + 被取代的旧裁决」逐条清单（append-only）；
  3. **不改**任何 Review/证据/limitation 原文；旧 Codex 终裁以「用户 2026-11-08 新授权取代 2026-11-05 委托裁决」明写；
  4. 若某节点 C1 项未完成 → **保持 `closed_with_limitations`**，不得先改状态后补证据。
- `<<NOT_APPLICABLE: 原因>>` 的原因必须写「原生交互验收未执行（保留 NOT_RUN）+ 用户 2026-11-08 授权豁免」，**不得**写「已通过」或「无硬件」。

## 4. 节点翻转条件（终局矩阵 v2）

| 节点 | 翻转前置（全部必须） | 可 NA 项 |
|---|---|---|
| FEA-11-HOST-AUTH-1 | R1 完成：ACK/recovery fresh grant + ACK 重发/恢复 gated e2e + 崩溃点 + AC11-8 | 无 |
| FEA-06-RESIDUAL-2 | R2 完成：5 个依赖格 + Tab 遍历 + a11y 属性/UIA | W-06 |
| FEA-11 | R3 完成：AC11-7 诊断接线、AC11-9 生产链路、L-M4、AC11-5/8 回填、folder relink 判别测试 + L-S4-2 登记；R1 的 AC11-8 结果并入 | W-08；W-09 仅在产品显式决定时 |
| FEA-07 | R4 完成：AC1(A03/ACK/Run)、AC2(单写 owner/Host 生命周期)、AC3 崩溃注入 + 保护状态、AC4 启动矩阵、AC6 真实负载 | W-01、W-04、W-05 |

## 5. 基线重钉

- pytest **3390/10**、.NET **1691/0/96**、pins **18/18**、check PASS(3w)（本轮实跑，HEAD `4070f0043` 后）。
- `doc/STATUS.md:20` 原写 `.NET 1683/0/96`（UI-RESIDUAL-2 +8 之前的旧值）→ **本轮已修正为 1691/0/96**；`DSH-AUTORUN-PROMPT` 已为 1691，二者现已一致。

## 6. 与 scope review 的差异（DSH 说明）

- 评审建议「R0 应立可校验 Task 卡」。**DSH 裁决**：R0 是**纯裁决+文件**（无实现、无状态翻转），按 `09_COLLABORATION` 以本 ADJ + handoff 记录即可；机器可校验性由 R1–R4 的实现卡在 closeout 时引用本 ADJ 达成（避免为一张纯文档卡再走一轮完整流水线）。
- 评审建议「原生项标 BLOCKED 而非 NA」。**DSH 裁决**：在**翻 done 之前**它们确实是 BLOCKED；翻 done 时 `check.ps1` 不接受 BLOCKED，故必须二选一：保持 `closed_with_limitations`（不翻），或按用户授权以 `NOT_APPLICABLE: 原因（保留 NOT_RUN + reopen 条件）` 落地。本程序采用后者，且**逐条保留 reopen 条件**，不把 NA 写成通过。

## 7. 节点翻转登记（append-only，逐条 before/after）

### 7.1 `FEA-11-HOST-AUTH-1`：`closed_with_limitations` → `done`（2026-11-08）

| 项 | before | after | 依据 |
|---|---|---|---|
| front matter `status` | `closed_with_limitations` | `done` | 用户 2026-11-08 指令（R1）+ 本节 |
| AC3 行 | `- [ ] **AC3**：… <<PARTIAL: 顺序+失败语义+retry … 完整 HostRuntime→Core e2e 与 ACK 重发/崩溃点矩阵待补（FEA-11 L-8/L-9 limitation）>>` | `- [x] **AC3**：… <<MET>>` | 承接卡 `FEA-11-HOST-AUTH-2` `f7016d3fb`（fresh 授权 + gated ACK 重发/恢复 2/2）；崩溃点 re-home `FEA-11-HOST-AUTH-3` |
| 历史 Review/证据字节 | 不变 | 不变 | 只 append-only closeout 段 |
| Codex 2026-11-05 终裁 | 有效 | **被用户 2026-11-08 新授权取代**（终裁原文保留） | 用户指令优先 |

### 7.2 `FEA-11-HOST-AUTH-2`：`ready` → `done`（2026-11-08，integration `f7016d3fb`）

AC-F1/F2/F5 MET；AC-F3 → `NOT_APPLICABLE` + re-home `FEA-11-HOST-AUTH-3`；AC-F4 → `NOT_APPLICABLE` + re-home `FEA-11-HOST-AUTH-5`。re-home 载体：`FEA-11-HOST-AUTH-3/4/5`（`proposed`，须先 scope review）。

### 7.3 未翻转（保持现状）

`FEA-11`、`FEA-06-RESIDUAL-2`、`FEA-07` 仍为 `closed_with_limitations`（R2/R3/R4 未完成）。

### 7.4 `FEA-06-RESIDUAL-2` 的 BLOCKED 表重开与 `FEA-06-RESIDUAL-3` 冻结（2026-11-08）

- 独立 scope review（`doc/reviews/FEA-06-RESIDUAL-3-scope-r1.md`，`NOT_RECOMMENDED`）→ **DSH 采纳其 5 项改写后冻结 `FEA-06-RESIDUAL-3`（ready）**：
  1. **格 3（RegionBox 冲突态「查看对照」）降级 re-home** → `FEA-06-RESIDUAL-4`：补数据必须过 `IHostController`（C-07 additive），违反本卡 0 pin。
  2. **格 4（书架满态统计）改口径**：FEA-12 四卡是删除/回收站线、冻结命令表无 statistics 命令 → 改为既有投影自洽聚合（`FilteredBooks.Count / Books.Count` + `ΣPageCount`，null→「—」）。
  3. **格 2 依赖归属更正**：阅读器数据面由 `READER-LIBRARY-WIRE-1`/`READER-PROGRESS-1` 交付（早于 FEA-09）→ 该格是纯 UI 缺口。
  4. **Tab 遍历口径裁决（方案 a）**：`03-accessibility.md:13` 优先 → `Tab` 仅三空间遍历；Studio 断言 `Tab`=模式切换 + 补页签条 `←/→`；**不改全局 Tab 绑定**（避免触 03 冻结 + FEA-07 输入路由）。
  5. **术语落表**：七状态 = `Queued/Running/Done/Failed/Blocked/Stale/Skipped`；9 行 = `RunId/RunStatus/OverallProgress/CurrentPageId/CurrentStepType/Completed/Failed/Skipped/Blocked`。
- **allowed_paths 收窄**：`Views/Fluent/**` + `ViewModels/Fluent/**`（原草案 `Views/**` 会踩 `Views/V2/**`，与 RESIDUAL-2 禁令冲突）。
- **冻结基线**：`.NET 1705/0/98`、pytest `3390/10`、pins 18/18（STATUS:20 现网值，> plan §11.4 的 1691/0/96）。
- **done 口径不变**：`FEA-06-RESIDUAL-2` done 时必须显式声明「done 不覆盖 BLOCKED 表」+ 逐格 before/after + 格 3 re-home 具名卡；原生项 NA（保留 `NOT_RUN`）。

### 7.5 `FEA-06-RESIDUAL-2` → `done`（2026-11-08，integration `ddc29ecb3`）

| 项 | before | after | 依据 |
|---|---|---|---|
| front matter `status` | `closed_with_limitations` | `done` | 用户 2026-11-08 指令（R2）+ 本节 |
| BLOCKED 表 6 格 | 全部 BLOCKED | 4 格关闭、1 格 re-home（`FEA-06-RESIDUAL-4`）、1 格拆为「Tab/a11y 关闭 + 原生 NA」 | 承接卡 `FEA-06-RESIDUAL-3`（`ddc29ecb3`；r4 approved P0=0/P1=0） |
| 显式声明 | — | **本卡 done 不覆盖 BLOCKED 表** | ADJ §11.3 / 评审 R3-006 |
| limitation | 原生 DPI/a11y | 原 limitation 字节保留；新增 L-R3-1…L-R3-7 并具名 re-home | 不改历史字节 |

### 7.6 `FEA-06-RESIDUAL-3`：`ready` → `done`（2026-11-08）

Review 链 r1→r2→r3→**r4 approved（P0=0/P1=0/P2=0/P3=5）**；AC-1…AC-6 MET；格 3 与原生项不在本卡（re-home / NA）。

### 7.7 `FEA-11` 收口卡冻结（`FEA-11-RESIDUAL-4A`，2026-11-08）

- 独立 scope review（`doc/reviews/FEA-11-RESIDUAL-4A-scope-r1.md`，`NOT_RECOMMENDED`）→ **DSH 采纳其 §5 后冻结**：AC11-1/3/4/5/8 **仅回填**；AC11-6 **纯测试**（4 类用例 + `L-S4-2` 登记）；AC11-9 **纯测试**（Host 级 gated，复用 `Fea09ProductionFixture`；仓库无 `Fea11ProductionFixture`）；AC11-7 **Host journal 只读投影（operation 作用域）**，`needs_confirmation` 零生产者缺陷 re-home `FEA-11-DIAG-SURFACE-1`（需 C-17 additive）；**L-M4 不实现** → re-home `FEA-11-LEGACY-RECOMPUTE-1`（需 C-17 UNFREEZE）；**L-M1** → `FEA-11-PDF-RECONCILE-1`；L-STARTUP 子项 `NOT_APPLICABLE`（契约解释+产品范围，保留 NOT_RUN）。
- **口径**：`[x] <<MET>>` 不得带原因；limitation 只进 closeout/EV；不把任何整 AC 写 NA。
- 治理修正：`doc/STATUS.md:8`、`doc/REBASELINE_PLAN.md:53` 的 HOST-AUTH-1 陈旧表述已改为 `done`（实际 `5cbec0e82` 已翻）。

### 7.8 `FEA-11` → `done`（2026-11-08，integration `fbe337f95`）

| 项 | before | after | 依据 |
|---|---|---|---|
| front matter `status` | `closed_with_limitations` | `done` | 用户 2026-11-08 指令（R3）+ 本节 |
| AC11-1/3/4/5/6/7/8/9/10 | `- [ ]` | `- [x] … <<MET>>` | 承接卡（SCAN-1/WATCH-1/SCAN-2、MATCH-1、AC4-GAPS-1、LINEAGE-1、HOST-AUTH-1/2）+ R4A |
| L-STARTUP 子项 | PARTIAL | `NOT_APPLICABLE`（契约解释+产品范围，保留 NOT_RUN） | ADJ W-08 |
| L-M1 / L-M4 / needs_confirmation | open | re-home `FEA-11-PDF-RECONCILE-1` / `FEA-11-LEGACY-RECOMPUTE-1` / `FEA-11-DIAG-SURFACE-1` | R4A scope review + 本节 |
| 历史 Review/证据字节 | 不变 | 不变（只 append-only + AC 行 + pin 重签） | §3 |

### 7.9 `FEA-11-RESIDUAL-4A`：`ready` → `done`（2026-11-08）

Review 链 r1 changes_requested（P1=1：D-1c）→ **r2 approved（P0/P1/P2=0）**；AC-R3-1…R3-6 全 MET；D-1 三处 wire 帧缺陷（D-1a/D-1b/D-1c）修复并有判别测试。

### 7.10 `FEA-07` 收口：拆分与冻结（2026-11-08）

- 独立 scope review（`doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md`，`NOT_RECOMMENDED`）→ **DSH 采纳**：
  1. **AC2 冻结解释**：「第二窗口」= 独立 OS 窗口（`WindowBroker.Floating`）→ 只读/独立 Session；同 Session 主画布+浮动面板 = 同一窗口内面板 → 按 **C-13 SC-D03** 共享 DraftId 可编辑；**只引用不复述**。
  2. **AC3 可做**：FEA-11 的 grant 阻塞不迁移（崩溃对象是 `switch-journal.json`）→ 外部驱动 park/kill/recover。
  3. **AC6 改口径**：1000 ms 门槛不变（W-5），p95 改 **3 次中位数**；新增 `uiThreadSchedulingGapMs`（首轮基线定标）；真实规模 N∈{50,200,500}。
  4. **AC4 加最小 `StartupDiagnostics` sink**（App 侧 ≤5 行接线）；不改 `tools/e2e/**`/`scripts/**`。
  5. **拆分**：`FEA-07-RESIDUAL-2`（R4a，headless：AC2/AC6/AC8，已冻结 ready）与 `FEA-07-RESIDUAL-3`（R4b，gated/进程：AC1/AC3/AC4，proposed）；**两卡都 MET 后 FEA-07 翻 done**。
- 口径更正：FEA-07 的 ADJ 锚点是 §2（W-01…W-05）+ §4 矩阵，非 §7.4。

### 7.11 `FEA-07-RESIDUAL-2`（R4a）→ `done`（2026-11-08，integration `a03a6794a`）

| 项 | before | after | 依据 |
|---|---|---|---|
| front matter `status` | `ready` | `done` | 本节 |
| AC-R4a-1…4 | `- [ ]` | `- [x] … <<MET>>` | AC2 窗口层机制/生命周期/AC6 指标/AC8 证据 |
| allowed_paths | 无 `PresentationWindow.cs` | **已扩域**（+26/−5，净 +21；DSH 授权留痕） | 本行 |
| P2-01 | canonical 默认 JSON 为 r1 旧 schema | 用 r2 代码重生成并重签 | DSH |
| limitation | — | L-R4a-1（生产跨窗未接线）、L-R4a-2（gap 门槛仅串行 perf 门禁）、L-R4a-3（规模 p95 超门槛只记录）、L-R4a-4（pytest 既有 flaky） | 本卡 closeout |

### 7.12 `FEA-07-RESIDUAL-3`（R4b）进入 READY 队列（proposed → 待 scope review）

### 7.13 `FEA-07-RESIDUAL-3`（R4b）冻结（2026-11-08）

- scope 依据：**同一独立 scope review** `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md` §3（AC3 崩溃最小方案）、§4（AC4/AC6 增量）、§5.2（R4b 面）+ 风险 R-1…R-9；DSH 采纳并冻结：AC1 gated 真库 A03 + ACK/Intent；AC3 外部驱动 park/kill/recover + 暂停期保护状态两断言；AC4 最小 `StartupDiagnostics` sink（`App.axaml.cs` ≤5 行）+ 4 组真实进程 + 9 类 warning 矩阵。
- 0 pin；禁止面含 `doc/plan/**`、`doc/contracts/**`、18 pins、`tools/e2e/**`、`scripts/**`、`src/**`、`Switching/**`；`App.axaml.cs` 仅 ≤5 行接线。

### 7.14 `FEA-07` → `done`（2026-11-09，integration `8e9420f41`）—— 残余收口程序 4/4 节点完成

| 项 | before | after | 依据 |
|---|---|---|---|
| front matter `status` | `closed_with_limitations` | `done` | 用户 2026-11-08 指令（R4）+ 本节 |
| AC1/AC2/AC3/AC4/AC6/AC8 | PARTIAL/BLOCKED | `[x] … <<MET>>`（R4a：AC2/AC6/AC8；R4b：AC1/AC3/AC4） | 两卡 Review approved |
| AC5 | BLOCKED/D-1 | **唯一 `NOT_APPLICABLE`**（原生矩阵；`NOT_RUN`） | ADJ W-05 |
| limitation | 原生/真机 | L-R4a-1…4 + L-R4b-1…5 具名登记；既有 legacy 测试隔离缺口 re-home | 本卡 closeout |
| 显式声明 | — | **done 不覆盖原生交互矩阵** | 本节 |

### 7.15 `FEA-07-RESIDUAL-3`（R4b）：`ready` → `done`（2026-11-09）

Review 链 r1 approved（P2 升 P1：真实 AppData 写入）→ 返修 → r2 changes_requested（P1-01：RenderScaling 分支绕过 `--log-dir`）→ 返修 → **r3 approved（P0=0/P1=0/P2=0/P3=4）**；gated AC4 16/16 且真实 AppData delta=0。

### 7.16 残余收口程序收官（4 节点全部 done）

`FEA-11-HOST-AUTH-1`（R1）、`FEA-06-RESIDUAL-2`（R2）、`FEA-11`（R3）、`FEA-07`（R4a+R4b）均已 `done`；各节点均经独立上下文 Review（P0/P1=0）与 Lead 亲自门禁；0 pin 全局保持（18/18）。
### 7.17 `FEA-07` AC5 原生矩阵：部分执行与口径收窄（2026-11-09）

- 用户 2026-11-09 提供真实双屏（AOC 2K 2560×1440 + Philips 4K 3840×2160）并授权脚本切换显示模式/缩放。
- 新卡 `FEA-07-AC5-NATIVE-1`（`closed_with_limitations`，integration `0bcdeb9fc`）执行：7 组混合 DPI 拖动（4K 100/125/150/175/200 × 2K 100/125/150 子集）、OS 级拔屏（成功 1 次、失败 1 次如实保留）、逐屏缩放 UIA 切换、PerMonitorV2 源码+exe 证据、窗口持久化探测（产品无实现）。
- `FEA-07` 的 AC5 行**保持 `[x] <<NOT_APPLICABLE: ...>>`**（不改为 MET）；理由按本卡收窄为「原生矩阵已部分执行；Inspector 浮窗不存在、未 flush 编辑态/IME/换主屏/全屏/物理拔线未执行（NOT_RUN）；用户授权豁免保留」。
- 未做项不写成 PASS；`FEA-07` 节点状态保持 `done`（不重开节点）。

### 7.18 `FEA-07-IMMERSIVE-F11-1`：F11 沉浸显示失败兜底（2026-11-09）

- 缺陷 D-AC5-2：真实桌面按 F11 后主窗被最小化、沉浸 `ReaderWindow` 未出现（`FEA-07-AC5-NATIVE-1/DEFECTS.md`）。
- 修复：`TryOpenImmersiveReader()` 捕获显示失败 → 恢复主窗（不残留最小化）、状态栏常驻提示、写 `immersive-open.log`、reader 入口不再抛未处理异常、失败回退来源页；`OpenImmersiveReader()` 成功路径不变。
- 回归：`F11HotkeyTests` 9/9（含新增故障注入 + 日志断言）；全量 .NET 除 1 例既有并发 flake（单独运行通过）外全绿。
- 原生复测：本会话键盘无法进入应用（浏览器 F11 正常、应用无事件/状态/日志）→ AC5 记 `PARTIAL`，需本地控制台补测；**未写 PASS**。

### 7.19 `FEA-07-IMMERSIVE-F11-1` r1 处置与关账裁决（2026-11-09）

- r1（独立子代理，`c298fe8f6`）= `changes_requested`：P1=1（R-001 证据表与 AC 不对应）、P2=4（R-002 Minimized 断言恒真、R-003 成功不清提示、R-004 静默不可见无兜底、R-005 terminal 早于 Review）、P3=6。
- 整改（`dc3526b76`）：状态文本收敛到 `RefreshStatusText()`（成功清提示）；`Show()` 后校验 `IsVisible`，不可见即走同一 fallback；`_openingImmersive` 重入保护；`LastImmersiveWindow` 成功后发布；restore 二次异常保护；日志兜底扩到 `NotSupportedException`/`SecurityException`；测试改为 **先最小化** 再注入失败并断言恢复 `Normal`、断言状态栏文本、覆盖 reader 入口与「失败→成功」重试。
- 证据表重映射：AC1–AC3 → headless 运行记录（9/9）；AC3 成功路径 → 20/20；AC4 → 测试源；AC5 → 原生 NOT_RUN JSON；早期构建 JSON 标 SUPERSEDED。
- **关账裁决（DSH）**：用户 2026-11-09 的任务定义明确包含兜底分支（“失败时主窗不消失且给出提示”），未要求原生必达；本会话键盘不可达属环境阻塞，AC5 记 `PARTIAL`，任务以 `closed_with_limitations` 收口，不写 PASS。

### 7.20 `FEA-07-IMMERSIVE-F11-1` r2 处置（2026-11-09）

- r2 = `changes_requested`：P1=1（N-001 原生证据壳错误）、P2=2（N-002 证据未绑定壳/args、N-003 `IsVisible` 分支零测试）、P3=6。
- 整改：legacy 壳原生复测（F11→全屏、Esc 恢复，JSON 记录 `shell/args`）；补静默不可见回归（`ImmersiveShowOverride = _ => { }`）与 `TryOpenImmersiveReader()==false` 断言；失败提示统一走 `RefreshStatusText()`（N-008）；证据表去空行重排（N-005）；修正 `approval` 去重（N-007）；D-AC5-2 记录更正（删除 `-32000` 误述）；display 试验产物移出仓库（N-009）。
- 关账口径：AC5 `PARTIAL`（legacy 成功路径已验证；物理 2K/4K 复测时不在系统中，全屏落在 1920×1080；v2 默认壳无入口）；不写 PASS。
