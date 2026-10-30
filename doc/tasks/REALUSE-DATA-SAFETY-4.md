---
id: REALUSE-DATA-SAFETY-4
title: Console 三处「待接入」分区接线——模型/设备、缓存与版本清理、插件与 Hooks
kind: feature
governance_version: 3
status: ready
approval: user_authorized_2026-10-30_self_audit_split_from_REALUSE-DATA-SAFETY-3
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - REALUSE-DATA-SAFETY-3
base_commit: 026c5eacc
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REALUSE-DATA-SAFETY-4
allowed_paths:
  - doc/tasks/REALUSE-DATA-SAFETY-4.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/contracts/V11R_COMMAND_CONTRACT_V1.md
  - doc/handoffs/REALUSE-DATA-SAFETY-4-handoff.md
  - doc/reviews/REALUSE-DATA-SAFETY-4-*.md
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/**
  - src/**
  - verification/REALUSE-DATA-SAFETY-4/**
---

# REALUSE-DATA-SAFETY-4：Console 三处「待接入」分区接线

## 来源

从 [REALUSE-DATA-SAFETY-3](REALUSE-DATA-SAFETY-3.md) 的 AC1 拆出（DSH 拆分，2026-10-30）。审计 `DEFECTS.md` MA-06：控制台 9 个分区中仍有 3 个标记「待接入」——**设备与模型**、**缓存与版本清理**、**插件与 Hooks**（备份与恢复已由 REALUSE-DATA-SAFETY-1 接线）。

体量评估：三个分区分别对应不同的 Host/Core 能力面，其中「模型与设备」是 MA-02（Provider 未配置指引）的真正落点——用户被指引到「设置 → Provider 与凭据」，但那页当前只是占位。因此本 Task 的价值不只是补 UI，而是让那条指引真实可走通。

## 范围

- **设备与模型**：Provider/模型配置的真实入口（复用已有 `ProviderProfileInfo` / Settings 能力面，不新增契约）。要求：能列出、选择、验证 Provider；未配置时与 REALUSE-DATA-SAFETY-2 的指引文案一致。
- **缓存与版本清理**：若 Core 无对应命令，保留占位但**明确写清缺失原因与前置条件**，不得用假按钮。
- **插件与 Hooks**：同上。已有 `plugins` 装配点（`core_assembly.py` 的 `plugins` 参数），若命令未冻结则只做只读状态展示 + 诚实说明。

## 验收标准

- [ ] **AC1 设备与模型分区可用**：用户能从控制台看到并管理 Provider（至少：列出、选中、显示当前绑定），未配置时给出与 MA-02 指引一致的下一步。 <<PARTIAL: 待实现>>
- [ ] **AC2 三处占位不再静默**：缓存清理与插件分区若无法真实接线，必须显示「为什么还不能用 + 前置条件 + 追踪标识」，不得只写「待接入」三个字。 <<PARTIAL: 待实现>>
- [ ] **AC3 契约边界**：任何新增命令必须先在本 Task 记录契约变更提案并交 DSH 裁决；不擅自修改冻结契约。 <<PARTIAL: 待实现>>

## 禁止范围

- 不修改用户数据根；不新增依赖；不 push 远端；不伪造能力（宁可见到诚实占位，也不要假开关）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 Provider 管理 | headless UI 测试 + 真实数据根 | net9.0 | NOT_RUN | 待补 |
| AC2 占位诚实性 | XAML/VM 断言（无假按钮） | net9.0 | NOT_RUN | 待补 |
| AC3 契约 | 人工核对冻结契约 diff | — | NOT_RUN | 待补 |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-3 | doc/handoffs/REALUSE-DATA-SAFETY-3-handoff.md | 前三批 worktree 保留；本 Task 尚未开 worktree |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
