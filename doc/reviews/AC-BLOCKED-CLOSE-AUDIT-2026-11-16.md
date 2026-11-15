# 41 条「可闭合」AC 的当前状态核实（2026-11-16）

- 作者：DSH（Lead / Integrator）
- 依据：`verification/AC-BLOCKED-CLASSIFY-1/classification-v2.md`（历史快照）
- 方法：按该文件给出的「卡 + 行号 + AC 标识」定位到当前 `doc/tasks/*.md`，读**当前**的勾选状态

## 为什么要核实

`classification-v2.md` 是 2026-11-15 的一次性全量判定，其中 **RERUN + DOC + IMPL = 41 条**
被判为「可由 Agent 闭合」。

但 `GOAL-C-DEBT-AUDIT-1` 在核对时发现：至少一条（`V11R-C-RESEARCH-1` AC5）**已经被后续工作落盘了**
（`[x]` + `<!-- verified -->` 注释）。

⇒ **历史分类是快照，不能当作当前待办清单。** 先核实真实状态，再决定做什么。

## 核实结果

**41 条中：已勾 `[x]` = 8 条，未勾 `[ ]` = 33 条，行未定位 = 0，文件缺失 = 0。**

### 已闭合的 8 条（无需再做）

| # | 卡 | 行 | AC | 类别 | 当前状态 |
|---|---:|---|---|---|---|
| 3 | `V11R-D-1` | 51 | AC8 | IMPL | `[x]` |
| 44 | `M2-REGION-RETYPE-CORE` | 29 | AC3 | RERUN | `[x]` |
| 50 | `TASK-056` | 29 | ① | RERUN | `[x]` |
| 51 | `TASK-056` | 30 | ② | RERUN | `[x]` |
| 52 | `TASK-056` | 31 | ③ | RERUN | `[x]` |
| 53 | `TASK-056` | 32 | ④ | RERUN | `[x]` |
| 54 | `TASK-056` | 33 | ⑤ | RERUN | `[x]` |
| 56 | `V11R-C-RESEARCH-1` | 40 | AC5 | DOC | `[x]`（含 `<!-- verified: delivery_head ba59a6c0d -->`） |

`V11R-C-RESEARCH-1` AC5 的 `verified` 注释还带了**可复算依据**：
「`git show --stat ba59a6c0d` = 10 个 doc 文件 / 0 个生产文件」—— 本轮已复跑确认该 commit 确实只动 doc。

### 真实待处置的 33 条

按类别：

| 类别 | 条数 | 说明 |
|---|---:|---|
| `DOC` | 8 | 纯文档补齐 |
| `RERUN` | 5 | 需在当前架构重跑取证 |
| `IMPL` | 20 | 需补测试或实现 |

按卡（未勾）：

| 卡 | 未勾条数 | 主要缺口 |
|---|---:|---|
| `FEA-04` | 8 | 「范围冻结完成、实现未开始」—— **最大的单块** |
| `V11R-B-5` | 4 | SCREEN_SPECS 章节 / 上下文保留断言 / 六态 / 裸间距 |
| `MICA-FIX-1` | 3 | `--diagnostics` 原始日志 / `test.ps1` 回归 / 门禁记录 |
| `GATE3-COVERAGE-MATRIX` | 3 | 矩阵文档三节 |
| `FEA-07-AC5-NATIVE-1` | 2 | 快捷键断言 / 独立 Review |
| `V11R-B-4` | 2 | Partial 断言 / 裸间距 |
| `GOV-RESIDUAL-RUNTIME-IDENTITY-IMPL-1` | 2 | 第 7 类负例 / integration 证据 |
| `V11R-C-1` / `V11R-B-3` / `V11R-A-3` / `V11R-C-3` / `RUN-IPC-1` / `M2-SFX-CORRECTION-EXPORTER` / `CHAPTER-MANUAL-SORT` / `M2-REGION-RETYPE-CORE` / `RELEASE-PACKAGE-1` / `TASK-056` | 各 1 | 见明细 |

## 处置建议（分批）

| 批次 | 内容 | 条数 | 风险 |
|---|---|---:|---|
| **B1** | `DOC` 类（纯文档补齐） | 8 | 低 |
| **B2** | `RERUN` 类（重跑取证） | 5 | 中（依赖测试环境） |
| **B3** | `IMPL` 类 - 小额缺口（裸间距/断言/负例） | 12 | 中 |
| **B4** | `FEA-04` 的 8 条 | 8 | **高**（是实现而非补证据，需另立实现卡） |

**B4 是唯一需要"实现"而非"补证据"的一块** —— `FEA-04` 的判定依据明确写
「范围冻结完成、实现未开始（8 条同源），实现需另立卡」。

## 本报告不做什么

- **不修改任何 `doc/tasks` 历史卡**（本报告只做状态核实）；
- **不更新 `classification-v2.md`**（它是历史证据，按治理规则应保持原字节）；
- **不宣称这 33 条可以批量关闭** —— 每一条都需要各自的处置依据。

## 可复算

本报告的每一条都能用 `verification/AC-BLOCKED-CLOSE-1/verify_state.py` 复现：
它按 `classification-v2.md` 的「卡 + 行号 + AC」定位当前文件并读取勾选状态。
