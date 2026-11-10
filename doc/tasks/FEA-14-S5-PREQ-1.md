---
id: FEA-14-S5-PREQ-1
title: FEA-14 S5 口径与地基（七切片裁决 / 共用 wire / 新数据类别 errata / 设置存储形状 / DDL v10 计划）
kind: decision
governance_version: 3
status: in_progress
approval: **DSH 2026-11-10 裁决**（依据只读侦察 `G:\CODEX\New Manga.workspace\temp\FEA-14-planning\recon.md`）：FEA-00 §12.2/§15.6 为**七切片**（LIB/READ/EDIT/AI/FONT/SET/EXPORT）；`FEA-14-SET-1` 为 SET 视觉子集；本卡为 S5 其余切片提供统一口径与共用 wire，**不写产品代码**。
suggested_owner: dsh
owner: dsh
reviewer: null
depends_on:
  - FEA-14-SET-1
base_commit: c543b51cc
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-14-S5-PREQ-1
allowed_paths:
  - doc/tasks/FEA-14-S5-PREQ-1.md
  - doc/reviews/FEA-14-S5-PREQ-1-*.md
  - doc/handoffs/FEA-14-S5-PREQ-1-*.md
  - doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md
  - verification/FEA-14-S5-PREQ-1/**
  - doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md
  - doc/plan/FEA-CONTRACT-FROZEN-C07.md
  - doc/plan/FEA-C07_API_INVENTORY.md
  - doc/plan/FEA-C01b_STORAGE_CONTRACT_DRAFT.md
  - doc/plan/FEA-C09_DELETE_BACKUP_MIGRATION_DRAFT.md
  - doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md
out_of_scope:
  - **不写产品代码**（无 src/**、apps/** 实现改动；不新增命令实现）
  - 不改任何**未授权**契约字节；C-07 的 UNFREEZE 仅按本卡 AC2 一次执行（含独立复核与 pin 重算）
  - 不改 DDL/schema（只出 v10 计划）
  - 不实现 FEA-15 A2/A3/A4（属验收执行，另卡/另行记录）
---

# FEA-14-S5-PREQ-1：口径与地基

## 背景

- FEA-00 §12.2/§15.6 列 FEA-14 **七个切片**：LIB / READ / EDIT / AI / FONT / SET / EXPORT；`doc/plan/FEA-15-INTEGRATION-ACCEPTANCE.md` §3 与已收口的 `FEA-14-SET-1` 旧卡面曾写「六切片」并漏掉 EXPORT。
- `FEA-14-SET-1`（`done`，`c543b51cc`）交付的是 **SET 视觉子集**（设置页字体只读投影），不是真实 SET（托盘/退出协调/启动页/语言/通知/更新/诊断预览）。
- 只读侦察（2026-11-10）结论：五切片（FONT/LIB/READ/EDIT/AI）都需新增 `IHostController` 成员 → 每片会各触发一次 C-07 pin 变更；新数据类别（字体库/书签/问题标记/提示词模板）需 C-01b/C-09 归属 errata；`ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md:35-39` 要求切片的 scope 显式含「数据根指针持久化 + 切换入口」才能解锁 MIGRATE-6。

## Scope 冻结（2026-11-10，DSH）

本卡只做**裁决与地基**，交付五份产物（AC1–AC5），禁止顺手实现：

1. **七切片清单裁决 + FEA-15 注记**（append-only，不改已 MET 的 AC 字节）。
2. **共用 wire 契约包**：五切片所需命令面一次列清（名称/域/minor/payload 形状），走**一次** C-07 UNFREEZE（含独立复核 + pin 重算），避免五次。
3. **新数据类别登记 errata**：字体库文件、书签、问题标记、提示词模板 → C-01b SC-10b（备份默认包含类别）与 C-09 SC-B01a（完整归属表）append-only errata。
4. **设置存储形状**（含「数据根指针持久化 + 切换入口」一行）→ 解锁 `ADJ-2026-11-09-ZCODE` 的 MIGRATE-6 依赖；供 SET-2/READ-1 使用。
5. **DDL v10 计划**：逐切片列新表/新列 + 迁移/回退/备份归属，声明不属于 C-15 v7 冻结 DDL 块（沿用 `FEA-12-CORE-C04B-INDEX-L4-1` 0 pin additive 先例）。

## Acceptance Criteria

- [x] **AC1 七切片裁决**：`doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md` 记录（a）七切片清单（含 EXPORT）与依赖顺序；（b）`FEA-14-SET-1` = SET 视觉子集、真实 SET 另立卡的裁决；（c）`FEA-15-INTEGRATION-ACCEPTANCE.md` §3 的 append-only 注记（不改原句）。`check.ps1` 通过。 <<MET>>
- [ ] **AC2 共用 wire 契约包 + 一次 UNFREEZE**：五切片的命令面清单（`FONT/LIB/READ/EDIT/AI` 各自命令、域、minor、payload 形状）落盘；按 `FEA-CONTRACT-FROZEN-C07.md:42` 在同一 Task 内重跑 inventory 脚本、更新清单、重算 C-07 pin；UNFREEZE 记录含**独立上下文复核**（非本卡作者会话）与 `verify_pins` 全绿（18 pins 计数不变或按裁决记录新数）。
- [ ] **AC3 新数据类别 errata**：C-01b SC-10b + C-09 SC-B01a 的 append-only errata（`fonts/`、`bookmarks`、`issue_markers`、`prompt_templates` 四类的备份默认包含/清理不删/恢复过滤语义），不改历史冻结字节。
- [x] **AC4 设置存储形状**：一页形状（settings section 白名单新增项、数据根指针字段、切换入口语义、迁移约束）落盘，显式写明 MIGRATE-6 释放条件满足情况；不改实现。 <<MET `verification/FEA-14-S5-PREQ-1/settings-storage-shape.md`>>
- [x] **AC5 DDL v10 计划**：逐表/列/迁移步骤/回退/备份归属清单；声明「v10 不属于 C-15 v7 冻结 DDL 块」；不改 schema.py。 <<MET `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md`>>
- [x] **AC6 门禁与零改动**：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 在 AC2 前 18/18、AC2 后按记录；`git diff --name-only` ⊆ allowed_paths；无产品代码 diff；无 DDL 改动。 <<MET（2026-11-10：check PASS、pins 18/18、无 src/apps/DDL diff）>>

## 交付物

| # | 产物 | 位置 |
|---|---|---|
| 1 | S5 口径裁决（七切片/SET 子集/顺序/依赖） | `doc/reviews/ADJ-2026-11-10-FEA14-S5-SCOPE.md` |
| 2 | 共用 wire 清单 + UNFREEZE 记录 | `doc/reviews/FEA-14-S5-PREQ-1-wire-r1.md`（+ C-07 冻结记录/pin） |
| 3 | 新数据类别 errata | C-01b/C-09 冻结文档 append-only 段 + 本卡记录 |
| 4 | 设置存储形状 | `verification/FEA-14-S5-PREQ-1/settings-storage-shape.md` |
| 5 | DDL v10 计划 | `verification/FEA-14-S5-PREQ-1/ddl-v10-plan.md` |
| 6 | 门禁日志 | `verification/FEA-14-S5-PREQ-1/logs/` |

## 风险与回退

| 风险 | 处置 |
|---|---|
| 卡片膨胀成设计文档 | 每份产物 ≤1 页；不写实现/AC 细节 |
| 一次 UNFREEZE 复核成本 | 单独给 C-07 变更派独立上下文复核；pin 重算日志留证 |
| 产品取舍（托盘/语言/provider/分段） | 本卡只登记为「待用户裁决」，不代替用户决定 |
| 范围漂移 | AC6 断言无产品代码/DDL 改动，diff ⊆ allowed_paths |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（文档卡，无需 worktree） | NOT_APPLICABLE | — | — | 未创建 |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-14-planning\recon.md` | keep-evidence（本卡依据） | — | — | 只读 |
| build | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问 |

## Closeout Record

- 未开始（2026-11-10 scope 冻结，`in_progress`）。
