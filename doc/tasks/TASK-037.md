---
id: TASK-037
title: 修复已定性 flaky（webtoon 滚动保存）与 TASK-036 R-01 诊断数值用法
kind: maintenance
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode（窗口内子 agent，结论仅 approved_subagent）
depends_on: [TASK-036]
base_commit: e96b3eb880bdfcfca182aa1350d9ff56798556c1
branch: agent/zcode/TASK-037-flaky-diagnostic-fix
worktree: G:/CODEX/New Manga.worktrees/TASK-037-zcode
integration_commit: null
---

# TASK-037：修复已定性 flaky（webtoon 滚动保存）与 TASK-036 R-01

**READY（2026-09-17 ZCode 全权窗口 W1，用户批准）**：Owner=`ZCode`、Reviewer=窗口内子 agent（结论**只能** `approved_subagent`/`changes_requested`）、base=`e96b3eb`、branch/worktree 见顶部元数据。开工前把 `status` 改为 `in_progress`。

## 来源与目标

本切片是窗口内**必做保底项（W1）**，目的是把仓库级的"证据不可信"问题收掉——它此前多次污染"全仓 N passed"类记录。

| 项 | 来源 | 已定性结论 |
|---|---|---|
| **flaky** | [STATUS](../STATUS.md)「已知 flaky 测试（跟踪条目）」第 1 条（TASK-017 R-007 首次登记 → **TASK-036 首次定性**：[registered-flaky-signature.md](../../verification/TASK-036/registered-flaky-signature.md)） | 失败用例 `tests/reading_export/test_qml_contract.py::test_reader_webtoon_swaps_in_vertical_viewer`，断言在 `:312`（`scroll_offset_y is saved through the service`）。签名 `pump(2s): iterations=98 elapsed_ms=2000 ok=False scroll_contentY=-0.0 saved_scroll_offset_y=0.0` → `setProperty("contentY", 240.0)` **被 Flickable 按 `StopAtBounds` 夹回 0**（前一处断言只保证 `contentHeight > 0`、未保证内容能容纳 240）→ 值未变 → `onContentYChanged` 不触发 → 节流保存不启动。**非"事件循环饥饿"** |
| **R-01** | [TASK-036 Review R-01](../reviews/TASK-036-c931db0.md)（P3） | `safe_property()` 在 `RuntimeError` 时返回**字符串**占位，却被用在**数值比较**的等待条件里（`(safe_property(...) or 0) > 0`）→ 占位串为真值 → `str > int` 抛 **TypeError**，把"RuntimeError 掩蔽 AssertionError"换成"TypeError 掩蔽" |

## Acceptance Criteria

- [ ] **AC ①（flaky 根因）**：把该用例的滚动准备改为**成立的前置条件**——例如先有界等待 `contentHeight` 足够容纳目标偏移（≥ 240 或 `contentHeight - height ≥ 240`）**再**设 `contentY`，或设值后**断言 `contentY == 240`** 再等保存。**不得放宽任何断言、不得新增 `skip`/`xfail`、不得删除已有诊断**。
- [ ] **AC ②（R-01）**：消除 `safe_property` 的数值用法缺陷（例如新增 `safe_number(obj, name, default=0)` 用于数值比较，`safe_property` 继续服务字符串/诊断场景），并**保持**"诊断不得掩蔽真实失败"这一性质。
- [ ] **AC ③（对照证据，必须）**：给出**修复前 vs 修复后**的失败率对照：每侧**≥10 次**运行（`pytest tests/reading_export -q -rf` 或含该用例的最小命令），逐次记录**退出码 + passed/failed + 命中用例名**。修复后应 **0 命中**；若仍命中，如实登记并给出新签名（**不得记为通过**）。
- [ ] **AC ④（回归与分列）**：`tests/reading_export` 全绿；`tests/providers`、`tests/core`、`tests/editing` 通过数**不减少**；全仓串跑**≥5 次**逐次记录 passed/skipped 与退出码（本环境全仓非 100% 稳定）。
- [ ] **AC ⑤（STATUS 口径）**：更新 STATUS「已知 flaky 测试（跟踪条目）」第 1 条的状态与证据（首次登记/证据/状态三列），并说明本次修复依据；**不得**把历史命中记录删掉。
- [ ] **AC ⑥** 交付 Handoff、实际测试/审阅记录与未完成项，经**窗口内子 agent** Review（按 Review 模板）与集成后才能 done。

## 允许修改范围

- `tests/reading_export/**`
- `doc/tasks/TASK-037.md`、`doc/handoffs/TASK-037-*.md`、`verification/TASK-037/**`
- `doc/STATUS.md`（仅 AC ⑤ 的 flaky 条目）

## 禁止范围

- **不得修改生产 `src/**`**：若在修复过程中发现根因确实在生产侧（例如阅读器 ViewModel/QML 的值夹取语义），**停下并在 Task 中留证、交 Codex 裁决**，不得自行改生产码。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`；不得把命中记为通过。
- 不得修改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task。
- 不得把 flaky 的**历史**登记记录删改。

## 测试要求

- 主命令：`python -m pytest tests/reading_export -q -p no:cacheprovider -rf`（AC ③ 需 ≥10 次）。
- 回归：`python -m pytest tests/providers tests/core tests/editing -q -p no:cacheprovider -rs`；全仓 `python -m pytest -q -p no:cacheprovider -rs -rf`（AC ④ 需 ≥5 次）。
- 记录 commit、OS/依赖、准确命令、退出码、passed/skipped 与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-036](TASK-036.md)（已集成 `2725324`，本 Task 的 R-01 与 flaky 定性均来自它）。

阻塞：无。

风险：
- **修复可能只是降低频率**：若 AC ③ 的 ≥10 次仍偶发命中，说明还有第二个触发路径 → 如实登记并与 Codex 讨论，**不得**为了让证据好看而放宽断言。
- 该用例依赖真实 QML/PySide6 时序；**不得**用"增大等待预算"作为修复手段（预算变更是放宽，须回抛）。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-17 23:2x 由 ZCode 在窗口内开工（W1，status→`in_progress`）；分支起点按用户指令 `git merge master` 快进至 `c3dabc8`（Task 元数据 `base=e96b3eb` 之上仅两笔纯文档时间戳修正，无代码差异）；修前对照取证进行中（`tests/reading_export` ×30 + 全仓 ×2）。
