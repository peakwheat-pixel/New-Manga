---
id: NS-WIRE-B1
title: 高置信 NS 命令接线（18 条）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_ns_b1_grant
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 45efe7f00
branch: task/NS-WIRE-B1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-WIRE-B1
allowed_paths:
  - doc/tasks/NS-WIRE-B1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-B1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B1/**
---

# NS-WIRE-B1：高置信 NS 命令接线（第一批 18 条）

## 背景

NS-RECLASSIFY-1 重探测证明 42 条 NOT_SUPPORTED 中 35 条实际可执行（24 high / 11 medium）。本批接线 **high 置信中不与其它 Task 重叠的 18 条**。

## 范围（18 条，来源 `verification/NS-RECLASSIFY-1/reclassification.json`）

backup_delete、cleanup_retry_pending、library_control_run、library_delete_book_permanently、library_get_run_snapshot、library_get_task_projection、library_resume_blocked_run、library_retry_failed_targets、library_start_run、plugins_audit_list、plugins_set_plugin_enabled、settings_network_profile_default_clear、settings_network_profile_default_set、settings_network_profiles_create、settings_network_profiles_delete、settings_network_profiles_update、settings_provider_bindings_clear、settings_provider_bindings_resolve、settings_provider_run_snapshot_get。

**排除**：region 4 + reader 2（S4-CMD-BATCH-1 负责）、import/export 5 + 2 shell 动作（GRANT-ISSUER-1 负责）、medium 11 条（后续批次）。

## Acceptance Criteria

- [ ] **AC1 逐条**：按 `reclassification.json` 的 `core_command`/`face`/证据 payload，在 C# `HostCommandRegistry`/dispatcher/domain service 接线；每条对冻结 sidecar **真实执行**断言（成功或 typed 域错误均算实证）。
- [ ] **AC2 契约**：参数边界校验（INVALID_ARGUMENTS）+ Core 业务错误码透传；P15 settings minor=7、Create minor=8、DELETE 面 minor=10（避免踩 NS-RECLASSIFY 记录的版本坑）。
- [ ] **AC3 parity**：`extract-command-surface.py --check` 零漂移；快照 18 条 NOT_SUPPORTED→IMPLEMENTED；证据 `verification/NS-WIRE-B1/**`（含逐条 probe-result）。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿（含新增）；vitest 60/567；pytest 相对基线（3F/2746P/9S）无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（分批策略/与 S4/C 批边界）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-B1/**`、workspace。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 Host 契约语义/旧壳、不抢 S4/GRANT 范围、不 push、不 gc/prune；验证不了的不许标 IMPLEMENTED。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
