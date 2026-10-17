---
id: FEAT-CREATE-2
title: 创建作品/章节能力（2/4）——Core 实现 CreateBook / CreateChapter（Core 2.8）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261017_after_FEAT_CREATE_1
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [FEAT-CREATE-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEAT-CREATE-2
---

# FEAT-CREATE-2：Core 实现 CreateBook / CreateChapter

## 来源
`FEAT-CREATE-1`（done）已把 M2-C1 升至 **rev 2.8**，冻结 `CreateBook {title}` → `BookSummary`、`CreateChapter {book_id,title,chapter_number?}` → `ChapterNavSummary`，含 **§5.10 安全投影**、**未知字段 fail-closed**、Core 为唯一校验/写入方，并判定**无需迁移**。

## Acceptance Criteria
- [ ] **AC1**：按 §5.10 **逐字**实现两条 Core 命令（命令名/DTO/响应/错误）；**未知字段 fail-closed**；`title` 非空与长度上限按契约；`CreateChapter` 的 `book_id` 必须存在且未删除。
- [ ] **AC2**：持久化到既有 `books`/`chapters` 表（**不新增表、不加迁移**，与 FEAT-CREATE-1 结论一致）；写入须在既有事务/约束内，失败不留半成品。
- [ ] **AC3**：响应**只**含 §5.10 白名单字段（`BookSummary`/`ChapterNavSummary`）；错误只走既有稳定 envelope；**不得**返回路径/Secret/原始异常。
- [ ] **AC4**：命令在 `core_service` 实现**并**在 `core_assembly`/分发处注册（与既有导航命令同机制）；协议 minor 按 **2.8** 门控；既有命令语义零变化。
- [ ] **AC5 测试**：覆盖成功路径 + 反例（未知字段、空标题、超长标题、不存在/已删除 `book_id`、重复/冲突），并断言**失败不留部分数据**；`pytest tests/core` **不得回归（基线 515）**。
- [ ] **AC6**：commit + **Handoff（必须）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`src/**`、`tests/core/**`、本 Task、`doc/handoffs/FEAT-CREATE-2-*.md`、`verification/FEAT-CREATE-2/**`。
- 禁止：改契约（wire 已冻结；有问题**停下上报**并引行号）；改 Schema/迁移/依赖；改 `apps/**`（host 注册属 FEAT-CREATE-3）；改 STATUS/PLAN；碰用户 19 项 dirty。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-1（done）。**后继**：FEAT-CREATE-3（host）、FEAT-CREATE-4（前端）。
- 风险：为图方便加字段/加表 → AC2 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。