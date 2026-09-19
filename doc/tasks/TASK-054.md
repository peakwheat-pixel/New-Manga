---
id: TASK-054
title: TASK-043 R-02：pending_after_cancel 跨层中性改名
kind: refactor
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-043]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-054-cancel-pending-rename
worktree: G:/CODEX/New Manga.worktrees/TASK-054-zcode
integration_commit: 771dbf7
---

# TASK-054：`pending_after_cancel` 跨层中性改名（TASK-043 R-02）

**READY（2026-09-19，ZCode 全权窗口 W7）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。无前置。

## 来源与目标

来源＝[TASK-043 Review](../reviews/TASK-043-d8e9406.md) 的 R-02（P3）：该端口同时服务图片导入，`pending_after_cancel` 的语义比"取消"更宽（失败余页也进同一桶）⇒ 名字误导。

**目标**：把该字段改成**跨层一致的中性名**（例如 `pending`/`pending_pages`），端口/应用/VM/测试全链一致；行为**零变更**。

## Acceptance Criteria

- [x] **AC ①（改名与全链一致）**：新名在 `src/application/importing/**`、`src/ui/viewmodels/**`、`tests/**` 全链一致；不得留两个名字共存。
- [x] **AC ②（行为零变更）**：所有既有断言的**语义不变**（只改名字）；给出"改名前后 passed 数一致"的对照。
- [x] **AC ③（文档与引用）**：Task/Review 引用与代码注释同步；若 D 文档引用了旧名且不在白名单 → 记 BLOCKED（不要越界改）。
- [x] **AC ④（不回归）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [x] **AC ⑤** Handoff + `verification/TASK-054/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/importing/**`、`src/ui/viewmodels/**`
- `tests/import_formats/**`、`tests/library/**`、`tests/ui_shell/**`
- 本 Task、Handoff、`verification/TASK-054/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：[TASK-054-56a429e.md](../handoffs/TASK-054-56a429e.md)。Review：尚无（待窗口独立子对话 Review）。实际测试：改名前全仓 1 次（851/0）+ 改名后全仓 5 次（851/0 ×5，exit 0 ×5）+ 定向 28/0 + 40/0，全部入库 `verification/TASK-054/`。
- **集成完成（2026-09-19，当前）**：独立子对话 Review `approved_subagent`（[TASK-054-88c1562](../reviews/TASK-054-88c1562.md)，固定被审 `88c1562`；R-001/R-002/R-003 均文档卫生级、已随 `51bc5a5` 处置）→ ZCode 按窗口授权代行集成 `771dbf7`（--no-ff），集成后 master 复跑定向 28/0+40/0、全仓 851/0 ×2。历史：2026-09-19 ZCode 实现：`pending_after_cancel` → `pending`（ports 字段 + 两处构造 keyword + 7 处断言），全链 0 残留；行为零变更（前后对照 851/0 ↔ 851/0）；无新用例（无新行为，判别对象为名字存在性，由 grep 残留检查承担，已声明）。实现提交 `56a429e`。`base=8bf8da3`（开工已 merge master `7537136`，含 TASK-046）。

> **2026-09-19 记录补齐（Qoder 后置复审 Q-011）**：本 Task 的 AC 勾选此前遗漏（`status: done` 而方框仍为 `[ ]`），已按 Review/集成记录补齐；达成情况以 [Review](../reviews/) 与 `verification/TASK-054/**` 为准。
