---
id: P19-UI-FIX-3
title: 修复「新建作品/章节」不可用（用户裁决 A：应允许在空书架创建）
kind: bugfix
governance_version: 2
status: superseded
approval: user_ruling_20261017_A_allow_create_work_on_empty_shelf
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [P12, P19-UI-FIX-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: complete
evidence_dir: verification/P19-UI-FIX-3
---

# P19-UI-FIX-3：新建作品/章节不可用

## 来源（用户 2026-10-17 裁决 A）
实测：`+ 新建作品` **`IsEnabled=False`**（UIA Invoke 抛异常），印证 `verification/P19/create-work-and-import-r6.md`。**用户裁决 A：空书架应允许新建作品/章节** → 该禁用是**缺陷**，须修复。

## Acceptance Criteria
- [ ] **AC1**：空书架下 `+ 新建作品` **可用**（`IsEnabled=True`），点击后出现**创建作品表单**（可与 `settings` 表单同风格，字段按现有产品能力；若需新 wire/契约 → **停下上报**，不得自行发明）。
- [ ] **AC2**：创建成功后：书架出现该作品；可**创建章节**（或产品既有的等价结构）；创建结果由 host→Core 持久化（隔离数据根内）。
- [ ] **AC3**：创建完成后**不再阻断导入**——`导入作品` 在存在目标时可用（沿用 P19-UI-FIX-2 的反馈口径：有目标→选择器，无目标→可见原因）。
- [ ] **AC4**：新增前端测试（空书架可新建作品）；既有 **274** 不回归；`npm run build` exit 0。
- [ ] **AC5 真实 GUI 复验**：重建产品（`npm run build`+`build_sidecar.ps1 -Force`+`cargo build`，**校验 bundle==resource hash 一致**）+ 隔离数据根（复制 `%APPDATA%` 的 `catalog`/`data` 后加空 `derived`，**不得改用户数据**），用 UIA 实测：`+ 新建作品` 可用 → 建作品/章节成功 → 导入入口转为可用。
- [ ] **AC6 交付**：固定 commit + **Handoff（必须，P19-UI-FIX-2 曾漏）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`apps/desktop/frontend/**`、`verification/P19-UI-FIX-3/**`、本 Task、`doc/handoffs/P19-UI-FIX-3-*.md`。
- 禁止：改契约/Schema/依赖（**需新命令/新 wire → 先上报**）；改 `src/**`（需 Core 配合先上报）；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用"把按钮改成始终可点但无后端"的假实现。

## 依赖、风险与阻塞
- 前置：P12（书架/导入面）、P19-UI-FIX-1（done）。
- **风险/阻塞**：若「新建作品」需要**尚未冻结的 wire 命令**，则本修复必须先走契约 Task → **停下上报**，不得自造接口。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据用户裁决 A。

## 阻塞（2026-10-17，Coordinator 采信）

硬门核对证明创建能力从未实现（契约仍 proposal、host/Core 无 create）。用户已裁决 **A1：立项 FEAT-CREATE-1..4** 补齐该能力，本 UI Task 由该功能链取代 → locked。证据：erification/P19-UI-FIX-3/hard-gate-conclusion.md。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| NOT_APPLICABLE | - | NOT_APPLICABLE | - | - | 本 Task 无持久资源；只读扫描/证据不改变工作区，终态收口不涉及迁移或删除 |

## 历史收口（2026-10-21，dsh）

- 收口状态：`superseded`。空书架新建作品/章节的能力已由 `FEAT-CREATE-1`–`FEAT-CREATE-4`（均 `done`）交付：前端 `BookshelfPage` 通过 `library_create_book` 创建并有 Vitest 覆盖；本 Task 未执行，不声称其 AC 完成。
- 依据：`verification/V1-FINALIZE-20261021/legacy-task-closure-adjudication.md`；原阻塞（需要新 wire）已由 FEAT-CREATE 链的冻结契约解决。
