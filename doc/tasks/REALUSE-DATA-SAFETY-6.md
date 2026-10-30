---
id: REALUSE-DATA-SAFETY-6
title: 自查收尾——进度刷新、旧库迁移策略、derived 双份、安装脚本隔离
kind: quality
governance_version: 3
status: ready
approval: user_authorized_2026-10-30_self_audit_remaining_items
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-5
base_commit: 896029a3f
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-6
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-6.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/REALUSE-DATA-SAFETY-6-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-6-*.md
  - apps/desktop-avalonia/src/**
  - apps/desktop-avalonia/tests/**
  - src/**
  - scripts/**
  - verification/REALUSE-DATA-SAFETY-6/**
---

# REALUSE-DATA-SAFETY-6：自查收尾的 4 条

## 来源

REALUSE-DATA-SAFETY-5 的核对结论：9 条里修了 6 条，剩下 4 条明确记录为「仍成立、未修」。本 Task 承接它们。

## 逐条说明（依据见 DEFECTS.md 复核记录）

1. **MA-09 阅读进度刷新**：`HostController.SaveReadingProgressAsync` 存在，但阅读器保存后与导入后的界面刷新未接。用户保存进度后回到书架/阅读器看到的仍是旧值。
2. **MA-11 旧库迁移**：`src/infrastructure/sqlite/upgrade_legacy_layout.py` 已实现，但真实数据根没有跑过（无 `upgrade-legacy.log`），旧壳仍可写另一份 `data/library.db`。**这条涉及用户数据与旧壳共存策略，需要用户裁决后才能动**。
3. **MA-19 `derived/` 全尺寸副本**：managed 原图与 derived 各一份，磁盘 2×，无自动清理。改动涉及资源通道设计，不能贸然删。
4. **MA-20 安装脚本隔离**：`apps/desktop-avalonia/scripts/install.ps1` 的 `$DataRoot` 默认就是真实 `%APPDATA%`，验证/安装流程可在未隔离情况下触碰真实数据。

## 验收标准

- [ ] **AC1 MA-09 进度刷新**：保存进度后书架与阅读器显示一致的当前进度；导入后进度信息不陈旧。有测试证明刷新确实发生（不是只看代码）。 <<PARTIAL: 待实现>>
- [ ] **AC2 MA-19 derived 冗余**：给出 derived 是否必需的结论（读资源通道代码 + 真实数据印证），能安全去掉冗余副本或明确记录为什么必须保留。 <<PARTIAL: 待实现>>
- [ ] **AC3 MA-11 / MA-20 需要裁决的部分**：这两条都涉及用户数据或部署流程，**先写清楚可选方案与各自影响，交用户/DSH 裁决**，不擅自实施。 <<PARTIAL: 待实现>>

## 禁止范围

- 不删除任何用户数据；不擅自执行迁移；不改冻结契约；不 push 远端。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet test --filter Progress` | net9.0 | NOT_RUN | 待补 |
| AC2 | 代码 + 真实数据核对 | 只读 | NOT_RUN | 待补 |
| AC3 | 方案文档 | — | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-5 | doc/handoffs/REALUSE-DATA-SAFETY-5-handoff.md | 前五批 worktree 全部保留；本 Task 尚未开 worktree |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
