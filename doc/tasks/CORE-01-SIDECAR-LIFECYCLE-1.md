---
id: CORE-01-SIDECAR-LIFECYCLE-1
title: 侧车进程取消/Dispose 生命周期收敛（NM-AUD-0001 P2）
kind: implementation
governance_version: 3
status: done
resume_status: done
approval: user_authorized_2026-11-14 (所有任务交 DSH、自动裁决/规划、全部授权、无需用户介入)
suggested_owner: DSH
owner: DSH
reviewer: "DSH auto-adjudication (2026-11-14 owner directive); independent sub-agent review optional"
depends_on: [SEC-03-RESTORE-TYPED-ERROR-1]
base_commit: baeda3042
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 8d358c9a08488fe8a6f3288c43570722c2ad54d6
delivery_head: 8d358c9a08488fe8a6f3288c43570722c2ad54d6
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1**：静态核对 `SidecarProcess.cs` 生命周期状态机与 HostBridge/HostRuntime 调用路径，记录根因与修改点。 <<MET>>
- [x] **AC2**：实现幂等 stop/cleanup：pre-cancel、spawn 后 cancel、EOF 正常退出、忽略 EOF 超时与 Host shutdown 均有明确收敛路径；dispose 返回后 child/tree 已退出。 <<MET>>
- [x] **AC3**：可运行的回归验证（helper 测试或等效隔离测试）覆盖上述路径，记录命令/EXIT；若 TestHost/环境阻塞，保留原结果并标 BLOCKED/NOT_RUN，不伪称通过。 <<MET>>
- [x] **AC4**：证据 pin、四项门禁、资源 closeout、DSH 自动裁决。 <<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| CORE01-SOURCE-1 | AC2 | `apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs` | `8d358c9a08488fe8a6f3288c43570722c2ad54d6` | `AA2CFC9EABA32E9765286F56E20854CF153282D8E59CED410610869F2F2A80AC` | CANONICAL | BLOB |
| CORE01-TEST-1 | AC3 | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/SidecarLifecycleTests.cs` | `8d358c9a08488fe8a6f3288c43570722c2ad54d6` | `60AB782E79F4FC54B619F8168B3D53E7327E8071A8C7BAAA0F9AAD3BB834FE80` | CANONICAL | BLOB |
| CORE01-TEST-LOG-1 | AC3 | `verification/CORE-01-SIDECAR-LIFECYCLE-1/logs/dotnet-test-lifecycle-fixed.log` | `8d358c9a08488fe8a6f3288c43570722c2ad54d6` | `2964C9F3E8ECA1478C54BE9AAD0E2AA384D7BF1C7A1E3BD335925F063BFCBDD0` | CANONICAL | BLOB |
| CORE01-DISCRIMINATING-LOG-1 | AC3 | `verification/CORE-01-SIDECAR-LIFECYCLE-1/logs/discriminating-power-old-code.log` | `8d358c9a08488fe8a6f3288c43570722c2ad54d6` | `C362849E491178772DAA9682B87598D761F5997CD366667AF8DFA1E600025AED` | CANONICAL | BLOB |
| CORE01-EVIDENCE-1 | AC4 | `verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json` | `8d358c9a08488fe8a6f3288c43570722c2ad54d6` | `538CEF0096DDEECD24B82D55A3A74FE28C2D827A04DA0A3727D74EB2136F105C` | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga | PRESERVE_REFERENCED | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 主工作区保留 |
| task-env | - | NOT_APPLICABLE | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 无独立 task-env |
| agent-output | - | NOT_APPLICABLE | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 无 agent-output |
| artifact | verification/CORE-01-SIDECAR-LIFECYCLE-1 | PRESERVE_REFERENCED | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 测试证据保留 |
| dataset/model/test-material | - | NOT_APPLICABLE | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 合成 fixture |
| exchange | - | NOT_APPLICABLE | doc | verification/CORE-01-SIDECAR-LIFECYCLE-1/evidence/core01-lifecycle.json | 无外部传输 |

## 允许修改范围

- `apps/desktop-avalonia/src/NewManga.CoreClient/Transport/SidecarProcess.cs`（必要时 CoreClient 内相关文件）
- `apps/desktop-avalonia/tests/**`（新增/调整 helper 生命周期测试）
- `verification/CORE-01-SIDECAR-LIFECYCLE-1/**`
- 本 Task 卡、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`

## 禁止范围

产品 UI/Host 契约、共享 Schema、依赖、真实用户数据、远端、发布/安装、历史改写。

## 测试要求

helper 级别回归；Avalonia TestHost 已知 8/8 runner EXIT 1、TRX 0（BLOCKED-TESTHOST-ACCESS），不得把该结果写成通过；NET build 与可运行测试分别记录。
