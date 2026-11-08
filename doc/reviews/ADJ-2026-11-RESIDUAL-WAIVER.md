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
