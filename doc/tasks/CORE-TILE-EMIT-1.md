---
id: CORE-TILE-EMIT-1
title: Core 侧 tile 生成 + per-tile SHA-256 下发（对齐 TILE-CHANNEL-CONTRACT-V1）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [HOST-RESOURCE-SECURITY-1]
base_commit: 744eccb61
branch: task/CORE-TILE-EMIT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-TILE-EMIT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CORE-TILE-EMIT-1
allowed_paths:
  - doc/tasks/CORE-TILE-EMIT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - verification/CORE-TILE-EMIT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CORE-TILE-EMIT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CORE-TILE-EMIT-1/**
---

# CORE-TILE-EMIT-1：Core 出 tile + per-tile 摘要

## 目标

对齐 `apps/desktop-avalonia/docs/TILE-CHANNEL-CONTRACT-V1.md`（Host 侧已冻结）：Core 在生成/交付页面渲染图时，同时输出 **tile 清单 {index, offset, length, sha256}** 与资源元数据（resource_id/revision/size），使 Host 的 `TileChannel` 能端到端校验真实数据而非本地 fixture。

## Acceptance Criteria

- [ ] **AC1 tile 生成**：对渲染输出按契约 tile 尺寸（默认 2048 高/整宽，或契约值）切块，产出租约要求的清单结构。
- [ ] **AC2 摘要一致性**：per-tile SHA-256 与 Host 端独立计算一致（跨进程验证，中文路径/unicode 文件名不炸）。
- [ ] **AC3 契约测试**：Core 输出 JSON 通过契约校验（字段/类型/错误码），Host 侧消费端到端测试（真实 Core 产物 → TileChannel → 校验通过）。
- [ ] **AC4 回归**：`python -m pytest` 相对基线（3F/2687P/9S）无新增失败；`scripts/test.ps1` 全绿；协议版本 2.3 语义与 57 命令契约不变（新增字段向后兼容）。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（tile 尺寸、契约版本、性能影响）。

## 允许修改范围

`src/**`、`tests/**`、本卡、STATUS/PLAN/LEDGER、`verification/CORE-TILE-EMIT-1/**`、workspace。只读：契约文档、Host 侧 TileChannel 代码。

## 禁止范围

不改 Host 侧契约（如需变更走版本化）、不改旧壳、不 push、不破坏既有 57 命令语义、不 gc/prune。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 生成 tile + Host 侧比对摘要 | 隔离 env | NOT_RUN | 待填 |
| AC3 | 契约校验 + 端到端 | 同上 | NOT_RUN | 待填 |
| AC4/AC5 | pytest + scripts/test.ps1 + check.ps1 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-TILE-EMIT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-TILE-EMIT-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
