---
id: REALUSE-DATA-SAFETY-4
title: Console 三处「待接入」分区接线——模型/设备、缓存与版本清理、插件与 Hooks
kind: feature
governance_version: 3
status: closed_with_limitations
approval: user_authorized_2026-10-30_self_audit_split_from_REALUSE-DATA-SAFETY-3
suggested_owner: dsh
owner: dsh-lead
reviewer: antigravity-headless
review_history:
  - round: 1
    verdict: FAIL_WITH_MUST_FIX
    report: doc/reviews/REALUSE-DATA-SAFETY-4-antigravity-r1.md
    must_fix: M1 plugin disable read as failure (Core echoes the new state); M2 write-path refresh blocked by its own busy flag; M3 pending retries hidden behind an empty target list; M4 unloaded provider list reported as unbound; M5 cleanup.retry_pending unreachable from the UI
  - round: 2
    verdict: PASS
    report: doc/reviews/REALUSE-DATA-SAFETY-4-antigravity-r2.md
depends_on:
  - REALUSE-DATA-SAFETY-3
base_commit: b8039aec8
branch: task/REALUSE-DATA-SAFETY-4
worktree: G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4
integration_commit: PENDING
delivery_head: 37dcd6d9f
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [ ] **AC1 设备与模型分区可用**：用户能从控制台看到并管理 Provider（至少：列出、选中、显示当前绑定），未配置时给出与 MA-02 指引一致的下一步。 <<PARTIAL: 设备分区已改为诊断式（从 ProviderProfiles 推导检测能力绑定，未绑定明确说明会返回 PROVIDER_NOT_CONFIGURED 并给跳转 ② 的入口；设备/权重状态如实标注 Core 未暴露），3 个用例通过；完整设备/权重答案依赖 doc/proposals/REALUSE-DATA-SAFETY-4-device-status-contract.md，未实施>>
- [x] **AC2 三处占位不再静默**：缓存清理与插件分区若无法真实接线，必须显示「为什么还不能用 + 前置条件 + 追踪标识」，不得只写「待接入」三个字。 <<MET>>
- [x] **AC3 契约边界**：任何新增命令必须先在本 Task 记录契约变更提案并交 DSH 裁决；不擅自修改冻结契约。 <<MET>>

## 禁止范围

- 不修改用户数据根；不新增依赖；不 push 远端；不伪造能力（宁可见到诚实占位，也不要假开关）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 设备诊断 | `dotnet test --filter DevicesSection_` | net9.0 | PASS 3/3（未绑定说明 + 已绑定 + 未启用/非检测能力均判为未绑定） | `V2ConsoleUiTests.cs` |
| AC2 缓存清理 | `dotnet test --filter StorageSection_` | net9.0 | PASS 3/3（预览→确认→执行、空预览拒绝、待重试数透出） | `V2ConsoleUiTests.cs` |
| AC2 插件分区 | `dotnet test --filter PluginsSection_` | net9.0 | PASS 4/4（清单+确认后开关、全局关闭时单插件禁用、被拒绝插件显示 reason、写入被拒显示 typed code） | `V2ConsoleUiTests.cs` |
| AC3 契约 | 人工核对：冻结契约未改动 | — | PASS（仅新增提案文档；`git diff` 不含 contracts/ 变更） | `doc/proposals/REALUSE-DATA-SAFETY-4-device-status-contract.md` |

## Canonical Evidence

进入独立审查前逐项填写（当前为空）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-AC2-CLIENT | AC2 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs` | `282ad43fa` | `-` | CANONICAL |
| E-AC2-STORAGE | AC2 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Console/ConsoleViewModel.cs` | `6ea2e817a` | `-` | CANONICAL |
| E-AC2-UI | AC2 | `apps/desktop-avalonia/tests/NewManga.App.Tests/V2ConsoleUiTests.cs` | `4238fdbb8` | `-` | CANONICAL |
| E-REVIEW-R1 | Gate | `doc/reviews/REALUSE-DATA-SAFETY-4-antigravity-r1.md` | `3844851e8` | `-` | CANONICAL |
| E-AC3-PROPOSAL | AC3 | `doc/proposals/REALUSE-DATA-SAFETY-4-device-status-contract.md` | `4238fdbb8` | `-` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REALUSE-DATA-SAFETY-4 | doc/handoffs/REALUSE-DATA-SAFETY-4-handoff.md | 前四批 worktree 全部保留，未删除 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
