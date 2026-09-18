---
id: TASK-057
title: TASK-021 冻结子集③：备份与恢复
kind: implementation
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-021, TASK-053]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-057-backup-restore
worktree: G:/CODEX/New Manga.worktrees/TASK-057-zcode
integration_commit: null
---

# TASK-057：备份与恢复（TASK-021 冻结子集③）

**READY（2026-09-19，ZCode 全权窗口 W10）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-053 已集成**（备份/恢复必须建立在 purge/孤儿文件语义已收口之上）。既有材料：`src/infrastructure/sqlite/backup.py`、`backup_records` 表。

## 来源与目标

来源＝TASK-021 冻结子集之一。**目标**：可用的库备份与恢复（DB + 清单一致性），**不破坏用户源文件**，失败可诊断、可重试。

## Acceptance Criteria

- [ ] **AC ①（备份完整性）**：备份产物包含 DB 与必要清单（形状自定但须写明），并在完成后校验可读；`backup_records` 落记录。
- [ ] **AC ②（恢复语义）**：恢复路径明确**覆盖/合并**语义；恢复后指针（current/pinned/translated）与 Managed Copy 一致性有断言。
- [ ] **AC ③（安全边界）**：备份/恢复**不写用户源文件目录**；路径必须落在受控范围内；异常时不留半成品（原子/可回滚）。
- [ ] **AC ④（幂等与失败可诊断）**：失败返回 typed 原因；重复操作用例。
- [ ] **AC ⑤（不回归 + 判别力）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑥** Handoff + `verification/TASK-057/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/**`、`src/infrastructure/sqlite/**`（备份/恢复相关；**待按实际结构收紧**）
- `tests/storage/**`、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-057/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration（确需 → BLOCKED）、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`，前置 TASK-053）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 开立为 `ready`（窗口 W10）。**实施尚未开始。**
