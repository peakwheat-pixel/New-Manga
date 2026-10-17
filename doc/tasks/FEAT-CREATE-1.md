---
id: FEAT-CREATE-1
title: 创建作品/章节能力（1/4）——契约冻结 CreateBook / CreateChapter
kind: design
governance_version: 2
status: ready
approval: user_ruling_20261017_A1_project_create_book_feature
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P15-C1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEAT-CREATE-1
---

# FEAT-CREATE-1：契约冻结 CreateBook / CreateChapter（创建能力 1/4）

## 来源（用户 2026-10-17 裁决 A1）
用户要求「空书架应允许新建作品/章节」（裁决 A）。**P19-UI-FIX-3 的硬门核对证明**：`CreateBook` 仅在 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` **§5 提案目录（L139）**，`CreateChapter` **仍是 PROPOSAL（L141）**，host/Core 均无实现（证据：`verification/P19-UI-FIX-3/{codex-blocker-checkpoint-r1.md,hard-gate-conclusion.md}`）。
→ 本功能分四段：**① 契约冻结（本 Task）→ ② Core → ③ host → ④ 前端表单与接线**。

## Acceptance Criteria
- [ ] **AC1**：在 `M2-C1_TYPED_IPC_CONTRACT.md` 中把 **`CreateBook` / `CreateChapter`** 从 proposal 提升为**冻结命令**（或按项目约定另立契约文件并声明与 M2-C1 的关系），给出：命令名、请求/响应 DTO、字段校验规则、错误语义、协议 minor 递增声明、与既有 `library_list_books`/`list_chapters` 的兼容影响。
- [ ] **AC2**：**不得**降低既有阈值或改动既有冻结语义；新增命令须遵守既有 §3 失败语义与安全投影（**不得**在返回/错误/事件中泄露路径、Secret、原始异常）。
- [ ] **AC3**：明确**最小字段集**——作品需至少有"标题"与"书架归属"；章节需至少能挂到作品并承载页面来源（页面来源可指向既有导入/资源通道，**不得**发明新的文件路径暴露面）。
- [ ] **AC4**：给出 **②Core / ③host / ④前端** 三段的范围边界与各自 AC 草案（供后续 Task 冻结使用），并指出**是否需要新的持久化表/迁移**（如需要 → 明确由哪个 Task 负责、是否需用户批准）。
- [ ] **AC5 交付**：固定 commit + **Handoff（必须）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`doc/contracts/**`（新命令定义）、`doc/tasks/FEAT-CREATE-*.md` 中本 Task、`doc/handoffs/FEAT-CREATE-1-*.md`、`verification/FEAT-CREATE-1/**`。
- 禁止：实现产品代码（`src/**`、`apps/**`）；改 Schema/依赖（如确需 → **先上报**）；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**把 proposal 原样"改名"当作冻结（必须补齐校验/错误/兼容语义）。

## 依赖、风险与阻塞
- 前置：`P15-C1`（契约风格与 minor 规则参照）。
- 后继：`FEAT-CREATE-2`（Core）→ `-3`（host）→ `-4`（前端）。**本 Task 关闭后依次释放**。
- 风险：字段设计过宽（暴露路径/任意写入）→ 必须遵守 AC3 的最小面。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据用户裁决 A1。