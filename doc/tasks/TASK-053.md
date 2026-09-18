---
id: TASK-053
title: TASK-044 遗留收口（R-03 pipeline_runs 累积 / R-04 不可重试孤儿文件）
kind: bugfix
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-044]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-053-run-files-leak
worktree: G:/CODEX/New Manga.worktrees/TASK-053-zcode
integration_commit: null
---

# TASK-053：TASK-044 遗留 R-03 / R-04 收口

**READY（2026-09-19，ZCode 全权窗口 W6）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。无前置（TASK-044 已集成）。

## 来源与目标

来源＝[TASK-044 Review](../reviews/TASK-044-7cd59d5.md) 与其 integration 记录登记的 accepted/deferred 项：

- **R-03**：`purge_pages` 不删 `pipeline_runs`（run 跨多页）⇒ 永久删除后可能累积**无 target 的运行记录**；
- **R-04**：`trash.purge_batch` 改为"先删行、后删文件"后，若**文件删除失败**会留下**不可重试**的孤儿文件（行已不存在，无从重建清单）。

**目标**：两条都变成**可诊断、可重试/可清理**的状态，并给出可复现证据。

## Acceptance Criteria

- [ ] **AC ①（先取证）**：用探针复现两条现状（无 target 的 run 累积；文件删除失败后的孤儿文件），留证。
- [ ] **AC ②（R-04 方案）**：把待删文件清单**持久化**（例如写入既有 batch manifest 或等价记录），使失败后可**重试清理**；给出"删除失败 → 重试成功"的用例。
- [ ] **AC ③（R-03 方案）**：明确 `pipeline_runs` 的保留/清理策略并实现（传播删除 或 明确保留 + 提供清理入口 + 记录理由）；给出"页永久删除后不再残留无 target run（或残留可被清理入口回收）"的用例。
- [ ] **AC ④（TRIGGER 纪律）**：涉及删除/级联的改动**必须先枚举 `sqlite_master` 的 TRIGGER** 并证明不被触发器拒绝（TASK-044 的教训）；证据入 `verification/TASK-053/**`。
- [ ] **AC ⑤（判别力 + 不回归）**：新用例对修前失败；`tests/storage/**`、`tests/core/**` 既有断言逐条不变；全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑥** Handoff + `verification/TASK-053/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/infrastructure/sqlite/**`、`src/application/**`（trash/purge 相关）
- `tests/storage/**`、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-053/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration（确需 → BLOCKED 转下一项）；不得改 `requirements.txt`、`AGENTS.md`、其他 Task；不得放宽断言/新增 skip；不得用 `PRAGMA foreign_keys = OFF` 绕过；不 push。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 开立为 `ready`（窗口 W6）。**实施尚未开始。**
