# CONDITION1-FINDINGS-RECHECK-1：逐项核实条件 1 的 8 项 finding（消除复评 §9 局限 1）

基线 `5bbb6c8a7`。复评 §9 局限 1 写的是"条件 1 未逐项重跑，依赖既有 review 记录"。
本卡去消除它：**对每项 finding 定位其测试/实现行号，并实际打开核实**。

## 1. 三项 IMPL-NOW（裁决称"核实现后发现已完成"）—— 逐行核实

| id | 文档声称的证据 | 我实际打开看到的 | 判定 |
|---|---|---|---|
| **L-F1-2** | `tests/core/test_font_wire.py:92-108` | `:92` `def test_font_wire_delete_failure_is_typed_and_retryable(tmp_path):`<br>`:86` 注释 `# MAINT-2-C1-BATCH-1 AC2 (C1-2 / L-F1-2): the STORAGE layer already pins` | ✅ **存在且可追溯** |
| **L-L1-4** | `src/application/library/service.py:28-33`、`:298` | `:28-33` 定义 `MAX_SQLITE_INTEGER = 2**63 - 1`、`MAX_IMPORT_ORDER = MAX_SQLITE_INTEGER - 1`，并带解释性注释（why one less）<br>`:298` 注释 `# AC6 (R3-001): also refuse values outside SQLite's signed 64-bit range as a typed validation error instead of letting the write fail as UNKNOWN/internal.` | ✅ **存在且与 R3-001 对齐** |
| **L-AI1-6** | `src/**` 中 `reassign_references` 命中 **0**；`tests/storage/test_prompt_templates.py:221` 以 `assert not hasattr(...)` 固定 | **实测命中数 = 0**；`:221` `assert not hasattr(SqlitePromptTemplateStore, "reassign_references"), (` + 消息 `"dead N-01 helper is back; P23 must keep using delete_with_reassign"` | ✅ **有反向断言固定，不会悄悄回来** |

**⇒ 三项不是"文档说完成了"，而是**有测试/实现行号且行号内容对得上**。**
**特别是 L-AI1-6 的 `assert not hasattr(...)`** —— 这是**能变红**的测试：若有人把死方法加回来，它会失败。

## 2. 四项 IMPL-CARD

| id | 处置 | 本轮核实 |
|---|---|---|
| **L-R1-1 / L-R2-1**（Fluent Reader UI 未接线） | 合并为 UI 控件卡 | 属 UI 视觉/交互，**需要真实窗口验证**；本轮未逐项重跑（见 §3） |
| **L-L1-1**（`ChapterSummary` 不投影 `kind`） | 改 DTO 投影需契约评估 | 触 wire 面，需 UNFREEZE 载体；**未在本轮复核** |
| **L-L1-2**（`custom_rank` write-only、排序未实现） | 独立卡 | **已独立核实**：`verification/L-L1-2-CONSTRAINT-VERIFY-1/`（commit 可达性 + SQL ORDER BY + 调用链 + 测试存在性四项） |

## 3. 一项 KEEP-NOTRUN

| id | 处置 | 核实 |
|---|---|---|
| **L-F1-3**（大文件/并发/占用文件压测） | `KEEP-NOTRUN` | **已由 ZCode 裁决接受替代判据**（`doc/reviews/L-F1-3-JUDGMENT-SUBSTITUTION-zcode-2026-11-15.md`，结论"有条件成立"，4 项记录型条件已在 `doc/tasks/L-F1-3-CLOSE-1.md` 登记） |

## 4. ★ 本卡**没有**消除的部分（诚实）

| 项 | 为什么没做到 |
|---|---|
| **L-R1-1 / L-R2-1 的 UI 控件行为** | 需要**真实窗口**观察控件是否接线（偏好应用 / 书签面板 / 整书进度 / reset 确认）。<br>**Agent 在本环境无法启动 GUI**（`GATE3-FOUR-PAGE-WALKTHROUGH-1` §8：4 种途径全部挂起 + 对照实验 20 ms 正常 ⇒ 窗口站问题）。**本轮只核实了"它们被归并进一张 UI 卡"这一处置事实，没有核实 UI 行为本身。** |
| **L-L1-1 的 DTO 投影** | 需确认是否已过契约评估/UNFREEZE。**本轮未查**，不声称已核实。 |

**⇒ 因此复评 §9 局限 1 只能**部分消除**：
- **已消除**：L-F1-2 / L-L1-4 / L-AI1-6（三项 IMPL-NOW，逐行核实通过）+ L-L1-2（前卡已四项核实）+ L-F1-3（裁决接受）；
- **未消除**：L-R1-1 / L-R2-1（需 GUI）、L-L1-1（需查契约评估记录）。

**⇒ 精确表述应为：条件 1 的 8 项中，5 项已由我逐项/逐行核实；2 项（UI 控件）受 GUI 限制未核实行为；1 项（L-L1-1）未查契约记录。**

**这仍是 MET 与否的关键**：若 L-R1-1/L-R2-1 的 UI 行为未被真实窗口验证，
则"条件 1 全部关闭"这件事**本身也依赖 headless 测试而非真实窗口**。
"""
