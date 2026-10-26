---
id: HOST-TILE-CHANNEL-1
title: S5-A Host tile 通道 + per-tile SHA-256 + ≤1s 授权缓存 + containment
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [UI-WORKBENCH-READER-1]
base_commit: 2885861fa
branch: task/HOST-TILE-CHANNEL-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-TILE-CHANNEL-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-TILE-CHANNEL-1
allowed_paths:
  - doc/tasks/HOST-TILE-CHANNEL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-TILE-CHANNEL-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-TILE-CHANNEL-1/**
---

# HOST-TILE-CHANNEL-1：S5-A tile 通道与最小安全面

## 来源

S5 拆分（见 `LEGACY-SHELL-REMOVAL-1` BLOCKED 段）、[ADR-0002](../design/ADR-0002_RESOURCE_CHANNEL_SECURITY_V2.md) D1–D4。目标：在新 C# Host 内实现 tile 资源通道与**最小**安全面，先覆盖 D4-2（revoke/expiry/1s 缓存失效）与 D4-4（篡改 tile 保尺寸拒绝），供 S5-B 做完整 D4 harness。

## Acceptance Criteria

- [ ] **AC1 tile 通道**：Host 提供 `tile` 服务：issue（返回不透明句柄 + size + identity + per-tile digest 清单）→ read（按 tile 读，返回字节 + 校验）→ revoke；UI 不接触 OS 路径/digest。
- [ ] **AC2 授权缓存**：授权状态查询带 ≤1s TTL 缓存；revoke 必须能**打断缓存**（事件驱动失效）；expiry 生效。
- [ ] **AC3 containment**：从已打开句柄重导最终路径并校验在允许根内；越界/junction/reparse 拒绝（为 S5-B 提供基础，测试覆盖最小集）。
- [ ] **AC4 内容完整性**：per-tile SHA-256 校验；**等长原地重写必拒**；篡改 tile 保尺寸 → 拒绝（typed error）。
- [ ] **AC5 接线与回归**：阅读器/工作台改用 tile 通道（可保留旧 fixture 兜底开关）；`scripts/test.ps1` 全绿；旧壳 vitest 60/567、pytest 基线不变。
- [ ] **AC6 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（缓存失效语义、digest 计算时机、误差边界）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/HOST-TILE-CHANNEL-1/**`、workspace。只读：ADR-0002、S2/S3/S4 Handoff、旧 Rust `resource_protocol.rs`（只读参考）。

## 禁止范围

不得改动/删除旧壳 `apps/desktop/**`（S5-C 才归档）；不改 Python Core；不 push；不 gc/prune；不得跳过 digest 校验。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | issue→read→revoke + 缓存打断 ≤1s | 无标签副本 | NOT_RUN | 待填 |
| AC3 | 越界/junction/reparse 负例 | 同上 | NOT_RUN | 待填 |
| AC4 | 等长重写/篡改保尺寸负例 | 同上 | NOT_RUN | 待填 |
| AC5/AC6 | `scripts/test.ps1` + check.ps1 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
