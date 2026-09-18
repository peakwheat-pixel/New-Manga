---
id: TASK-055
title: TASK-021 冻结子集①：日志与诊断
kind: implementation
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-021]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-055-diagnostics
worktree: G:/CODEX/New Manga.worktrees/TASK-055-zcode
integration_commit: null
---

# TASK-055：日志与诊断（TASK-021 冻结子集①，优先子集）

**READY（2026-09-19，ZCode 全权窗口 W8）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。无前置（TASK-021 的 trash 子集已集成）。

## 来源与目标

来源＝[TASK-021](TASK-021.md) 的冻结子集之一（备份恢复 / 缓存·版本·模型清理 / **日志与诊断**）；既有材料：`src/infrastructure/network/diagnostics.py`。

**目标**：交付**可用的日志/诊断能力**（不引入新依赖）：可导出诊断包（应用版本、Schema 版本、设置摘要、最近错误、环境与路径摘要，**凭据零泄漏**），并有界地保留。

## Acceptance Criteria

- [ ] **AC ①（诊断包）**：一键导出诊断信息（脱敏；**不得包含凭据/密钥/用户源文件内容**），字段清单在 Task/Handoff 写明。
- [ ] **AC ②（日志边界）**：日志落盘位置、大小/数量上限与轮转/截断策略明确并实现（不得无限增长）。
- [ ] **AC ③（错误可见面联动）**：与 TASK-052 的错误状态**不冲突**（同一错误码口径；若需要引用则复用，不另造）。
- [ ] **AC ④（白名单按实际结构收紧）**：开工前用 `rg` 核实真实路径后再动手；**草案路径不存在时以实际结构为准并在 Task 内记录**（TASK-021 的白名单曾出现草案路径全不存在的情况）。
- [ ] **AC ⑤（不回归 + 判别力）**：新用例对修前失败（或说明不适用）；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑥** Handoff + `verification/TASK-055/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/**`、`src/infrastructure/**`（诊断/日志相关；**待按实际结构收紧**）
- `tests/**`（对应目录）
- 本 Task、Handoff、`verification/TASK-055/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得新增依赖（`requirements.txt` 零改动）；不得改 Schema/migration（确需 → BLOCKED）；不得改 `AGENTS.md`/其他 Task；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 开立为 `ready`（窗口 W8，本窗口优先子集）。**实施尚未开始。**
