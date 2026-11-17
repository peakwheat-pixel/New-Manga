---
id: AC-BLOCKED-CLOSE-1
title: 41 条「可闭合」AC 的当前状态核实 —— 8 条已闭合，真实待处置 33 条
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: 未派（本卡为状态核实卡，输出为可复算统计，不需实现复核）
depends_on:
  - GOAL-C-DEBT-AUDIT-1
integration_commit: 9c160b546
approval: 用户 2026-11-15「全部授权」；目标 C「AC blocked 项中可归因闭合项」
base_commit: 56c9b0474
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/AC-BLOCKED-CLOSE-1
canonical_evidence_status: complete
resource_closeout_status: complete
allowed_paths:
  - doc/tasks/AC-BLOCKED-CLOSE-1.md
  - doc/reviews/AC-BLOCKED-CLOSE-AUDIT-2026-11-16.md
  - doc/TASK_LEDGER.md
  - verification/AC-BLOCKED-CLOSE-1/**
---

# AC-BLOCKED-CLOSE-1：41 条可闭合 AC 的状态核实

## 为什么先核实而不是直接做

`GOAL-C-DEBT-AUDIT-1` 更正了目标 C 第 3 项的口径：目标指的是
`verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md` 的 **72 条 AC 级判定**，
其中 **RERUN + DOC + IMPL = 41 条**被判为「可由 Agent 闭合」。

但在核对时发现至少一条（`V11R-C-RESEARCH-1` AC5）**已经被后续工作落盘了**。

⇒ **历史分类是 2026-11-15 的快照，不能当当前待办清单。** 本卡先核实真实状态。

## 核实方法与结果

按 `classification-v2.md` 给出的「卡 + 行号 + AC 标识」定位到当前 `doc/tasks/*.md`，
读取**当前**的勾选状态（脚本：`verification/AC-BLOCKED-CLOSE-1/verify_state.py`）。

| 结果 | 条数 |
|---|---:|
| 已勾 `[x]`（已被后续工作闭合） | **8** |
| 未勾 `[ ]`（真实待处置） | **33** |
| 行未定位 | 0 |
| 文件缺失 | 0 |
| **合计** | **41** |

### 已闭合的 8 条

`V11R-D-1` AC8、`M2-REGION-RETYPE-CORE` AC3、`TASK-056` ①②③④⑤（5 条）、
`V11R-C-RESEARCH-1` AC5。

最后一条的 `<!-- verified: delivery_head ba59a6c0d -->` 注释带可复算依据
（`git show --stat ba59a6c0d` = 10 doc 文件 / 0 生产文件），本轮已复跑确认。

### 真实待处置的 33 条

| 类别 | 条数 |
|---|---:|
| `DOC`（纯文档） | 8 |
| `RERUN`（重跑取证） | 5 |
| `IMPL`（补测试/实现） | 20 |

其中 **`FEA-04` 独占 8 条**，判定依据明确写「范围冻结完成、**实现未开始**，实现需另立卡」
—— 它是唯一需要"实现"而非"补证据"的一块。

## 分批处置建议

| 批次 | 内容 | 条数 | 风险 |
|---|---|---:|---|
| B1 | `DOC` 类 | 8 | 低 |
| B2 | `RERUN` 类 | 5 | 中（依赖测试环境） |
| B3 | `IMPL` 小额缺口 | 12 | 中 |
| B4 | `FEA-04` 8 条 | 8 | **高**（需另立实现卡） |

## Acceptance Criteria

- [x] **AC1 逐条定位**：41 条全部按「卡 + 行号 + AC」定位到当前文件，0 条未定位。 <<MET>>
- [x] **AC2 状态读取**：读取当前勾选状态，区分已勾 8 / 未勾 33。 <<MET>>
- [x] **AC3 已闭合项可复算**：至少核验一条的 `verified` 依据（`V11R-C-RESEARCH-1` AC5）。 <<MET>>
- [x] **AC4 分类保持**：33 条仍按 DOC/RERUN/IMPL 分类，并指出 `FEA-04` 是唯一需实现块。 <<MET>>
- [x] **AC5 不改历史卡**：本卡不修改任何 `doc/tasks` 历史卡的 AC 状态。 <<MET>>
- [x] **AC6 脚本可复现**：核实脚本落盘，任何读者可重跑得到相同数字。 <<MET>>

## 禁止范围

- 不得修改 `doc/tasks` 历史卡的 AC 勾选（本卡只核实）；
- 不得更新 `classification-v2.md`（历史证据保持原字节）；
- 不得宣称 33 条可批量关闭。

## 说明

这份核实的价值在于：**把「41 条待办」修正为「8 条已闭合 + 33 条待处置」**，
并给出可执行的分批方案。若直接按历史快照开工，会做 8 条无用功。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-ABC-01 | AC1/AC2/AC3 逐条状态核实输出 | verification/AC-BLOCKED-CLOSE-1/state-verified.out | 9c160b546 | b03b2b8934df85963d84a5a71daf21e669fb25e5fbdaf81401cae85a64b77233 | CANONICAL | BLOB |
| EV-ABC-02 | AC6 可复现脚本 | verification/AC-BLOCKED-CLOSE-1/verify_state.py | 9c160b546 | 421f2df4a9e945f63c34caf7457ec842a6e6ca8db91314fa32457fc89427ed05 | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/AC-BLOCKED-CLOSE-1/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH。
- **核实结果**：classification-v2.md 的 41 条「可闭合」中，**8 条已被后续工作闭合**（[x]），
  **33 条真实待处置**（[ ]），0 条行未定位、0 条文件缺失。
- **已闭合的 8 条**：V11R-D-1 AC8、M2-REGION-RETYPE-CORE AC3、TASK-056 ①②③④⑤、
  V11R-C-RESEARCH-1 AC5（末条带 verified 注释 + 可复算依据，已复跑确认）。
- **33 条分布**：DOC 8 / RERUN 5 / IMPL 20；其中 **FEA-04 独占 8 条**，
  判定依据明写「实现未开始，需另立卡」⇒ 它是唯一需要实现而非补证据的块。
- **价值**：把「41 条待办」修正为「8 条已闭合 + 33 条待处置」+ 四批处置方案。
  若按历史快照直接开工，会做 8 条无用功。
- **本卡不改任何历史卡 AC**，也不宣称 33 条可批量关闭。
- **门禁**：check.ps1 PASS (3 warnings)｜verify_pins 18/18｜api_inventory 1/80/6=87。
- **未关闭项**：33 条待处置本身（B1–B4）不在本卡范围，需后续卡承接；
  FEA-04 的 8 条需要独立的实现卡。
