---
id: NS-WIRE-A1
title: NS 命令接线第一批（settings/plugins/backup/cleanup）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/NS-WIRE-A1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-WIRE-A1
allowed_paths:
  - doc/tasks/NS-WIRE-A1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1/**
---

# NS-WIRE-A1：设置/插件/备份/清理类 NOT_SUPPORTED 接线（第一批）

## 背景

S2 交付时 66 条生产命令中 16 条已实现、50 条显式 NOT_SUPPORTED；S3/S4 已登记 18 条计划批次（S3-A/B/C 8 条、S4-A/B/C 10 条）。本任务做 **A 组第一批 = S3-A/B/C 类（settings / plugins / backup / cleanup 语义）** 的命令接线。

## Acceptance Criteria

- [ ] **AC1 清单**：从 `doc/handoffs/HOST-COMMAND-MIGRATION-1-handoff.md` 与 `verification/HOST-COMMAND-MIGRATION-1/parity/` 列出 S3-A/B/C 对应命令（预期 8 条），逐条标注 Core 路由/参数/返回。
- [ ] **AC2 实现**：在 C# `HostCommandRegistry`/dispatcher 与 domain service 中接线；每条命令对冻结 sidecar 真实执行，参数/返回/错误码与旧壳 parity 一致。
- [ ] **AC3 parity 更新**：`extract-command-surface.py --check` 零漂移；parity 快照中这些命令从 NOT_SUPPORTED → IMPLEMENTED，证据 JSON 落 `verification/NS-WIRE-A1/`。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿（新增命令测试）；旧壳 vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-A1/**`、workspace。只读参考：旧 Rust host 命令面、S2 Handoff。

## 禁止范围

不改 Python Core 语义、不改 Host 契约（如确需，先回报 DSH）、不改旧壳、不 push、不 gc/prune；不得把未验证命令标 IMPLEMENTED。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 逐命令真实 sidecar 执行 | 无标签副本 + 隔离 env | NOT_RUN | 待填 |
| AC3/AC4/AC5 | parity --check + 全量回归 + 治理 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
