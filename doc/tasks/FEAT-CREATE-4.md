---
id: FEAT-CREATE-4
title: 创建作品/章节能力（4/4）——前端表单与接线（空书架可新建 → 导入不再阻断）
kind: feature
governance_version: 2
status: ready
approval: coordinator_release_20261017_after_FEAT_CREATE_3
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [FEAT-CREATE-3]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEAT-CREATE-4
---

# FEAT-CREATE-4：前端表单与接线（创建能力 4/4）

## 来源
①`FEAT-CREATE-1` 冻结 M2-C1 **rev 2.8**（`CreateBook`/`CreateChapter` + Tauri `library_create_book`/`create_chapter`）→ ②`FEAT-CREATE-2` Core 实现（535 passed）→ ③`FEAT-CREATE-3` host 注册（production **51** 命令、source 107/0/1、packaged 12/0）。本段接前端。

## Acceptance Criteria
- [ ] **AC1 空书架可新建**：空书架下 `+ 新建作品` **可用**（`IsEnabled=True`），点击出现创建表单（标题必填）；提交经 `library_create_book` 成功后在书架**出现该作品**。
- [ ] **AC2 可建章节**：选中作品后可**新建章节**（经 `create_chapter`），章节出现在章节列表，且可在阅读器进入。
- [ ] **AC3 导入不再阻断**：存在作品/章节后，`导入作品` 入口**转为可用**（沿用 P19-UI-FIX-2 的反馈口径：有目标→选择器；无目标→可见原因）。
- [ ] **AC4 错误与安全**：失败走 §5.10 封闭投影（稳定类别 + 脱敏文案），**不得**显示路径/Secret/原始异常；重复标题**允许**（契约 L616）、**不设长度上限**（L614）。
- [ ] **AC5 测试**：新增前端测试（空书架可建、提交调用正确命令、失败显示脱敏文案、重复允许）；既有 **274** 不回归；`npm run build` exit 0。
- [ ] **AC6 真实 GUI 复验（必做）**：重建产品（`npm run build` → `build_sidecar.ps1 -Force` → `cargo build`，**校验 bundle==resource hash 一致**）+ 隔离 `NEWMANGA_DATA_ROOT`（复制 `%APPDATA%` 的 `catalog`/`data` + 空 `derived`，**不得改用户真实数据**）→ UIA 实测：`+ 新建作品` 可用 → 建作品 → 建章节 → 导入入口转可用；留 GUI 证据。
- [ ] **AC7**：commit + **Handoff（必须）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`apps/desktop/frontend/**`、本 Task、`doc/handoffs/FEAT-CREATE-4-*.md`、`verification/FEAT-CREATE-4/**`。
- 禁止：改契约、`src/**`、`apps/desktop/src-tauri/**`（Core/host 已交付；如需改动**先上报**）、Schema/迁移/依赖；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用前端假数据伪造"创建成功"。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-3（done）。**后继**：P19 的 AC2 主流程可开始。
- 风险：前端自造 wire/字段 → 必须以 §5.10 为准；伪造成功 → 明确禁止。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6）。