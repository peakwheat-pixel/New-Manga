---
id: HUMAN-VS-AGENT-SPLIT-1
title: 33 条待处置 AC 的人侧甄别 —— 仅 1 条真 HUMAN，其余 31 条 Agent 可做
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: 未派（甄别卡，输出为原文摘录与归属判断，不需实现复核）
depends_on:
  - AC-BLOCKED-CLOSE-1
integration_commit: 22d3c08f8
approval: 用户 2026-11-15「全部授权」；目标 D「剩余仅物理设备/人眼/外部账号类事项逐条登记」
base_commit: 087364874
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/HUMAN-VS-AGENT-SPLIT-1
canonical_evidence_status: complete
resource_closeout_status: complete
allowed_paths:
  - doc/tasks/HUMAN-VS-AGENT-SPLIT-1.md
  - doc/reviews/HUMAN-VS-AGENT-SPLIT-2026-11-16.md
  - doc/TASK_LEDGER.md
  - verification/HUMAN-VS-AGENT-SPLIT-1/**
---

# HUMAN-VS-AGENT-SPLIT-1：33 条的人侧甄别

## 为什么做

`AC-BLOCKED-CLOSE-1` 核实出 33 条待处置 AC。目标 D 要求「剩余仅物理设备/人眼/外部账号类事项
逐条登记为 HUMAN-REQUIRED」。

⇒ 必须先判断这 33 条里**哪些真的是人才能做**，否则会把"Agent 该做的工作"误塞进 HUMAN 清单。

## 结论

**33 条中，明确属 HUMAN-REQUIRED 的只有 1 条；另 1 条含 HUMAN 子项但主体可做；其余 31 条 Agent 可做。**

### HUMAN-REQUIRED（1 条，需拆分）

`MICA-FIX-1` AC2：

| 部分 | 归谁 |
|---|---|
| 加诊断输出代码、跑 `--diagnostics`、归档日志 | Agent |
| **判定「确实拿到了 Mica 而非回退 None」** | **人**（真实 Win11 桌面 + 人眼确认材质） |

⇒ 并入 `HUMAN-REQUIRED` 清单的 **H-01（Mica 真机验收）**。

### 含 HUMAN 子项（1 条）

`FEA-07-AC5-NATIVE-1` AC-N2：Inspector 浮窗子项已 **NA**（浮窗不存在），
「跨屏拖动手测」随浮窗 NA 而不适用；**主体是「快捷键不重复执行」需补断言** ⇒ Agent 可做。

### 一个必须澄清的误判

`FEA-07-AC5-NATIVE-1` **AC-N5** 字面要求「真实桌面截图，含两块屏」，看起来像 HUMAN。
但卡面 `:100` 明确写：**证据齐**（`verification/FEA-07-AC5-NATIVE-1/README.md` +
`evidence/matrix-summary.json` + 截图），**缺的是独立 Review 与行状态翻转**。

⇒ **截图已存在**，缺的是**独立上下文 Review** —— 那是 Agent 派子 agent 就能做的。
**AC-N5 不是 HUMAN-REQUIRED。**

### Agent 可做（31 条）

| 类别 | 条数 |
|---|---:|
| `DOC` | 8 |
| `RERUN` | 5 |
| `IMPL` | 18 |

## 核心判断：blocked ≠ 人才能做

`classification-v2.md` 把这 33 条归入 `IMPL`/`RERUN`/`DOC`，正是因为它们**本就可做**，
只是当时没做。把它们整体塞进 HUMAN 清单会是**错误的归因**。

## Acceptance Criteria

- [x] **AC1 逐卡甄别**：33 条涉及的 16 张卡都给出了归属判断。 <<MET>>
- [x] **AC2 HUMAN 仅 1 条**：明确 `MICA-FIX-1` AC2 的拆分（代码/日志 = Agent，判定 = 人）。 <<MET>>
- [x] **AC3 AC-N5 澄清**：说明它是 Agent 可做（证据已齐，缺 Review），不是 HUMAN。 <<MET>>
- [x] **AC4 blocked ≠ HUMAN**：明确这一判断，避免错误归因。 <<MET>>
- [x] **AC5 对分批方案的影响**：给出 B1–B4 的更新。 <<MET>>
- [x] **AC6 不改历史卡**：本卡不修改任何 `doc/tasks` 历史卡。 <<MET>>

## 禁止范围

- 不得把 Agent 可做的工作塞进 HUMAN-REQUIRED 清单；
- 不得修改 `HUMAN-REQUIRED-2026-11-15.md` 原文件（本报告作为补充）；
- 不得改任何历史卡的 AC 状态。

## 说明

本卡的价值：**把「33 条待处置」中的 1 条正确归入 HUMAN，其余 31 条明确为 Agent 可做** ——
这避免了两类错误：把 Agent 工作当成人侧阻塞，以及把真人侧判定伪装成 Agent 完成。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-HVA-01 | AC1/AC2/AC3 原文摘录（AC2、AC-N2、AC-N5） | verification/HUMAN-VS-AGENT-SPLIT-1/split-evidence.log | 22d3c08f8 | cf0b847a42a8e80952438ea78a926f8d5e5956614130de16df7a044499373e31 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/HUMAN-VS-AGENT-SPLIT-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH。
- **结论**：33 条待处置 AC 中，**真 HUMAN-REQUIRED 仅 1 条**（MICA-FIX-1 AC2 的
  「判定确实拿到 Mica」部分）；另 1 条含 HUMAN 子项（FEA-07-AC5-NATIVE-1 AC-N2 的浮窗子项已 NA，
  主体是补快捷键断言 ⇒ Agent 可做）；**其余 31 条 Agent 可做**。
- **澄清一处易误判**：FEA-07-AC5-NATIVE-1 **AC-N5** 字面要求「真实桌面截图含两块屏」看似 HUMAN，
  但卡面明写**证据齐**（README + matrix-summary.json + 截图），缺的只是**独立 Review 与行翻转**
  ⇒ Agent 派子 agent 即可完成，**不是 HUMAN-REQUIRED**。
- **核心判断**：locked ≠ 人才能做。classification-v2.md 把这 33 条归入 IMPL/RERUN/DOC
  正因它们本就可做；整体塞进 HUMAN 清单是**错误归因**。
- **门禁**：check.ps1 PASS (3 warnings)｜erify_pins 18/18｜pi_inventory 1/80/6=87。
- **未关闭项**：31 条 Agent 可做的实际处置（B1–B4）不在本卡范围；
  MICA-FIX-1 AC2 的人侧判定需并入 H-01，本卡**未改** HUMAN-REQUIRED-2026-11-15.md 原文件。
