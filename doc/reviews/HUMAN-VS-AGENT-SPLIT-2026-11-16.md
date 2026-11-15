# 33 条待处置 AC 的人侧甄别（2026-11-16）

- 作者：DSH（Lead / Integrator）
- 依据：`doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md`（33 条待处置）
- 目的：把 33 条分成「Agent 可做」与「HUMAN-REQUIRED」两类，为后续分批处置与目标 D 提供依据

## 结论摘要

**33 条中，明确属 HUMAN-REQUIRED 的只有 1 条**（`MICA-FIX-1` AC2），
**另 1 条含 HUMAN 子项但主体可做**（`FEA-07-AC5-NATIVE-1` AC-N2）。

其余 31 条均**可由 Agent 独立完成**（补文档 / 补断言 / 重跑取证 / 实现）。

**这个结论纠正了一个可能的误判**：blocked 不等于"人才能做"，
`classification-v2.md` 把它们归入 `IMPL`/`RERUN`/`DOC` 正是因为它们本就可做。

## HUMAN-REQUIRED（1 条）

### `MICA-FIX-1` AC2 诊断输出（部分人侧）

> 启动时（或 `--diagnostics`）输出 `ActualTransparencyLevel` 与 `WindowMaterialKind`
> 到日志/证据，**证明确实拿到 Mica 而非回退 None**。

| 部分 | 归谁 |
|---|---|
| 加诊断输出代码、跑 `--diagnostics`、归档日志 | Agent |
| **判定"确实拿到了 Mica"** | **人**（需真实 Win11 桌面 + 人眼确认材质生效） |

⇒ **拆开做**：Agent 补代码与日志，人做最终判定。已并入 `HUMAN-REQUIRED` 清单的 H-01（Mica 真机验收）。

## 含 HUMAN 子项（1 条）

### `FEA-07-AC5-NATIVE-1` AC-N2 浮动窗口归属

> Inspector 浮窗置于副屏 → 可见/可操作；主窗与浮窗跨屏拖动不丢屏外；
> 目标屏不支持浮动时安全停靠（回主窗）；**快捷键不重复执行**。

卡面自述（`:97`）：

> **部分 / limitation** —— 主窗跨屏归属与可见可操作 MET；**Inspector 浮窗不存在**
> （`RegisterSecondary` 零生产调用，L-R4a-1）→ 该子项 NA。可操作性/快捷键 `NOT_RUN`。

| 子项 | 归谁 |
|---|---|
| Inspector 浮窗置于副屏 | **NA**（浮窗不存在） |
| 主窗跨屏归属/可见 | 已完成 |
| **快捷键不重复执行** | Agent（补断言） |
| 跨屏拖动手测 | 人（但浮窗 NA 后此项不适用） |

⇒ **主体是「补快捷键断言」**，Agent 可做。

## Agent 可做（31 条）

| 类别 | 条数 | 代表性条目 |
|---|---:|---|
| `DOC` 纯文档 | 8 | `GATE3-COVERAGE-MATRIX` 三节、`RELEASE-PACKAGE-1` AC6 Handoff、`V11R-B-5` AC1 |
| `RERUN` 重跑取证 | 5 | `MICA-FIX-1` AC4（`test.ps1` 全绿）、`CHAPTER-MANUAL-SORT` AC10、`M2-REGION-RETYPE-CORE` AC6 |
| `IMPL` 补测试/实现 | 18 | `FEA-04` 8 条、`V11R-B-*` 裸间距与断言、`RUN-IPC-1` AC4 |

### 需要澄清的一条

`FEA-07-AC5-NATIVE-1` **AC-N5** 原本看起来像 HUMAN（要求"真实桌面截图，含两块屏"），
但卡面 `:100` 明确：

> **证据齐**（`verification/FEA-07-AC5-NATIVE-1/README.md`、`evidence/matrix-summary.json`、截图）；
> **独立 Review 与 AC5 行翻转待完成**。

⇒ 截图**已经存在**，缺的是**独立上下文 Review**（Agent 可派子 agent 做）与**行状态翻转**。
**AC-N5 不是 HUMAN-REQUIRED。**

## 对后续分批方案的影响

原方案（`AC-BLOCKED-CLOSE-AUDIT`）：

| 批次 | 内容 | 条数 | 变化 |
|---|---|---:|---|
| B1 | `DOC` | 8 | 不变，全部 Agent 可做 |
| B2 | `RERUN` | 5 | 不变 |
| B3 | `IMPL` 小额缺口 | 12 | 不变 |
| B4 | `FEA-04` | 8 | 不变 |
| — | **HUMAN 剥离** | **1** | `MICA-FIX-1` AC2 的判定部分并入 H-01 |

## 本报告不做什么

- 不修改 `HUMAN-REQUIRED-2026-11-15.md`（作者是当时的 DSH 会话，本报告作为其补充）；
- 不宣称 31 条可批量关闭；
- 不改任何历史卡的 AC 状态。
