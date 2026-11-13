---
id: CORE-01-SIDECAR-LIFECYCLE-1
title: 侧车进程取消/Dispose 生命周期收敛（NM-AUD-0001 P2）
kind: implementation
governance_version: 3
status: ready
resume_status: ready
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [SEC-03-RESTORE-TYPED-ERROR-1]
base_commit: baeda3042
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CORE-01-SIDECAR-LIFECYCLE-1
allowed_paths:
  - apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/tests/**
  - verification/CORE-01-SIDECAR-LIFECYCLE-1/**
  - doc/tasks/CORE-01-SIDECAR-LIFECYCLE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# CORE-01-SIDECAR-LIFECYCLE-1：侧车进程取消/Dispose 生命周期收敛（NM-AUD-0001 P2）

## 来源与目标

`NM-AUD-0001`（P2，TRIAGED）：受控 helper 经真实 `SidecarProcess` API 验证：pre-cancel 和 `DisposeAsync` 路径返回时，忽略 EOF 的 helper 子进程仍存活。根因候选为 dispose 状态与底层 stop 顺序短路，以及 spawn 后失败/取消的清理覆盖不足。目标：建立幂等 stop/cleanup 所有权，确保取消/Dispose 返回后 child/tree 已退出；不改变既有正常启动/退出语义。

## Acceptance Criteria

- [ ] **AC1**：静态核对 `SidecarProcess.cs` 生命周期状态机与 HostBridge/HostRuntime 调用路径，记录根因与修改点。
- [ ] **AC2**：实现幂等 stop/cleanup：pre-cancel、spawn 后 cancel、EOF 正常退出、忽略 EOF 超时与 Host shutdown 均有明确收敛路径；dispose 返回后 child/tree 已退出。
- [ ] **AC3**：可运行的回归验证（helper 测试或等效隔离测试）覆盖上述路径，记录命令/EXIT；若 TestHost/环境阻塞，保留原结果并标 BLOCKED/NOT_RUN，不伪称通过。
- [ ] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs`（必要时 CoreClient 内相关文件）
- `apps/desktop-avalonia/tests/**`（新增/调整 helper 生命周期测试）
- `verification/CORE-01-SIDECAR-LIFECYCLE-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

产品 UI/Host 契约、共享 Schema、依赖、真实用户数据、远端、发布/安装、历史改写。

## 测试要求

helper 级别回归；Avalonia TestHost 已知 8/8 runner EXIT 1、TRX 0（BLOCKED-TESTHOST-ACCESS），不得把该结果写成通过；NET build 与可运行测试分别记录。
