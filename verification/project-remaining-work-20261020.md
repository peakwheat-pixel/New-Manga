# 项目剩余未完成项清单（2026-10-20）

**产出**: 2026-10-20 · **性质**: 只读盘点 · **用途**: 供用户裁决「继续补齐」或「授权限项关闭」

## 一、口径说明

仓库有 **312 份 Task 文件**，其中 **248 done、21 closed_with_limitations**，
非终态 43 份。**但绝大多数非终态是历史遗留**（`P02PRE-*`、`T3.2.1-REPAIR-*`、
`TASK-0xx`），不属于当前 DAG。

**唯一的权威口径是 `doc/REBASELINE_PLAN.md` 的 DAG**（42 项 done）。
本文按那个口径列。

## 二、Plan 里的非终态节点（4 项）

| 节点 | Plan 状态 | 真实缺口 |
|---|---|---|
| **`P20`** | `ready` | AC4 的**撕裂项 LIMITATION**（其余 3 项实测 MET）|
| **`ARCH-DOC-REBASELINE`** | `ready / integrated（AC7 消费者裁决待做）` | **远不止 AC7**——见 §三 |
| `GOV-DEBT-CLEANUP-1` | `blocked（待用户裁决）` | 需要用户裁决才能动 |
| `RUST-ENV-BASELINE-1` / `P07` / `P21` | `proposed` | 可选，r29 建议维持 proposed |

**READY 节点只有两个：`ARCH-DOC-REBASELINE`、`P20`。**

## 三、`ARCH-DOC-REBASELINE` 的实际缺口比 Plan 写的大

**Plan 只说「AC7 消费者裁决待做」。实际情况（Task 的 Closeout Record 自述）：**

> **AC1–AC3 = PARTIAL、AC4–AC6 = NOT_RUN**，按 AC7 …

**7 个 AC 全部未勾选。** 逐项：

| AC | 内容 | 实际状态 |
|---|---|---|
| AC1 | AC-DOC-001 逐份核验 01–08 覆盖 | **PARTIAL** |
| AC2 | AC-DOC-002 领域/Pipeline/版本/契约跨文档一致 | **PARTIAL** |
| AC3 | AC-DOC-003 四一级页面/Reader/延期项一致 | **PARTIAL** |
| AC4 | P18 的 JA/KO、无字页、质量 AC 对应新链 | **NOT_RUN** |
| AC5 | P20 的 Tauri/WebView2/sidecar 对应旧条目与新证据 Gate | **NOT_RUN** |
| AC6 | P08-FMT 长期验收追踪（P16/P17 消费前须完成） | **NOT_RUN** |
| AC7 | 固定 head 非作者 Review + Codex 集成 + 逐消费者 Gate 裁决 | **待做** |

**所以 Plan 那一行低估了实际情况。** 这不是数据损坏，是**摘要与源文件不一致**——
本 Session 第三次遇到同一类问题（前两次：`P20` 的 R010 断言数 12 vs 15、
`P15` 的 resource manifest）。

**我没有擅自改 Plan**，先在此记录。改它需要 Codex 授权。

**额外风险**：AC6 说「**P16/P17 在消费对应格式契约前须此项完成**」。
而 P16/P17 在 Plan 里都是 `done`。**若 AC6 的条件尚未满足，那 P16/P17 的 done 是否成立？**
**这需要 Codex 核实。**

## 四、`P20` 的缺口（本轮已查清）

| AC4 子项 | 实测 | 判定 |
|---|---|---|
| 交互延迟 | avg 36.0 ms | **MET** |
| 帧率 · 单页 | avg 16.681 ms，1266 样本，0 excluded | **MET** |
| 帧率 · Webtoon | avg 17.527 ms，1202 样本，0 excluded | **MET** |
| 缩放平移无撕裂 | **未观察**（三次尝试失败：job 回收、CUA session 反复中断）| **LIMITATION** |

Codex r32 裁定：**记为 `LIMITATION / UNOBSERVED`，不声称已确认无撕裂**；
`P20` 保持 `ready`；**不授权**改为 `done` 或 `closed_with_limitations`。

## 五、因此需要用户裁决的问题

Codex r32 的推荐下一步是：

> **由用户明确选择：继续补齐 P20 剩余验收，或接受完整未完成项清单并授权限项关闭。**

**但「剩余验收」现在有两条完全不同的量级：**

| 选项 | 内容 | 量级 |
|---|---|---|
| **A. 关闭 `P20`** | 撕裂记 limitation，`P20` → `closed_with_limitations` | **小**：一次裁决 + 一次 closeout |
| **B. 补齐 `ARCH-DOC-REBASELINE`** | 4–6 个 AC 是 NOT_RUN / PARTIAL，涉及跨文档一致性核验 | **大**：多轮、需架构文档专项 |
| **C. 处理 `GOV-DEBT-CLEANUP-1`** | 现在 `blocked`，等用户裁决 | 未定 |
| **D. 三者都做** | | 很大 |

## 六、我的建议（不作为裁决）

**建议先 A、后 B。**

**理由**：`P20` 是 Windows 发布 Gate，它的 6/7 个 AC 已经完成，最后一项是**验收程序
本身不存在**（不是实现缺陷）。**继续等它，不会让产品更可用。**

**而 `ARCH-DOC-REBASELINE` 的缺口是真实的文档一致性工作**，且 AC6 与
`P16/P17` 的 done 状态有潜在冲突——**那个才需要认真做。**

## 七、本清单的边界

- **只读盘点**，未修改任何 Task、Plan、STATUS。
- 未核实 `ARCH-DOC-REBASELINE` 的 6 份专项证据报告是否可用
  （它们可能存在，只是 AC 未勾选）。
- **未验证 AC6 与 `P16`/`P17` 的冲突是否真实**——只是指出 Plan 的措辞暗示了可能。
