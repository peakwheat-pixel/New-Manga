---
id: TASK-054
title: TASK-043 R-02：pending_after_cancel 跨层中性改名
kind: refactor
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-043]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-054-cancel-pending-rename
worktree: G:/CODEX/New Manga.worktrees/TASK-054-zcode
integration_commit: null
---

# TASK-054：`pending_after_cancel` 跨层中性改名（TASK-043 R-02）

**READY（2026-09-19，ZCode 全权窗口 W7）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。无前置。

## 来源与目标

来源＝[TASK-043 Review](../reviews/TASK-043-d8e9406.md) 的 R-02（P3）：该端口同时服务图片导入，`pending_after_cancel` 的语义比"取消"更宽（失败余页也进同一桶）⇒ 名字误导。

**目标**：把该字段改成**跨层一致的中性名**（例如 `pending`/`pending_pages`），端口/应用/VM/测试全链一致；行为**零变更**。

## Acceptance Criteria

- [ ] **AC ①（改名与全链一致）**：新名在 `src/application/importing/**`、`src/ui/viewmodels/**`、`tests/**` 全链一致；不得留两个名字共存。
- [ ] **AC ②（行为零变更）**：所有既有断言的**语义不变**（只改名字）；给出"改名前后 passed 数一致"的对照。
- [ ] **AC ③（文档与引用）**：Task/Review 引用与代码注释同步；若 D 文档引用了旧名且不在白名单 → 记 BLOCKED（不要越界改）。
- [ ] **AC ④（不回归）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [ ] **AC ⑤** Handoff + `verification/TASK-054/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/importing/**`、`src/ui/viewmodels/**`
- `tests/import_formats/**`、`tests/library/**`、`tests/ui_shell/**`
- 本 Task、Handoff、`verification/TASK-054/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际测试：尚无（`ready`）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 开立为 `ready`（窗口 W7）。**实施尚未开始。**
