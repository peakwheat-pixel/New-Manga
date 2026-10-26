---
id: HOST-RESOURCE-SECURITY-1
title: S5-B 资源安全等价 harness（D4-1/3/5/6）+ digest 预算重测 + tile 契约冻结
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [HOST-TILE-CHANNEL-1]
base_commit: 09d7e76c1
branch: task/HOST-RESOURCE-SECURITY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-RESOURCE-SECURITY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-RESOURCE-SECURITY-1
allowed_paths:
  - doc/tasks/HOST-RESOURCE-SECURITY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-RESOURCE-SECURITY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-RESOURCE-SECURITY-1/**
---

# HOST-RESOURCE-SECURITY-1：S5-B 安全等价 harness

## 来源

S5 拆分（`LEGACY-SHELL-REMOVAL-1` BLOCKED 段）、[ADR-0002](../design/ADR-0002_RESOURCE_CHANNEL_SECURITY_V2.md) D4；S5-A 已交付 tile 通道与 D4-2/4 基础（集成 `09d7e76c1`）。

## Acceptance Criteria

- [ ] **AC1 D4-1 等长原地重写**：同一页被等长改写 → 必然拒绝（不得依赖 mtime）；测试含"改写后同 size、同 mtime 粒度"场景。
- [ ] **AC2 D4-3 越界/escape**：越界路径、junction、reparse point、UNC/符号链接逃逸全部拒绝（issue 与 read 两处）。
- [ ] **AC3 D4-5 身份变化**：文件被替换（同路径新文件）→ `TileIdentityMismatch`；volume/file index 变更检测。
- [ ] **AC4 D4-6 大页性能**：单页冷加载 **≤60ms**、**digest 开销占页加载预算 ≤10%**（按 G5 口径重测，不沿用 5.39× 缓存口径）。
- [ ] **AC5 tile 契约**：冻结 Core→Host 的 tile 生成与 per-tile digest 下发契约（文档 + 契约测试；Core 侧改动若需则只在新的独立 Task，本卡不改 Core）。
- [ ] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`scripts/test.ps1` 全绿；vitest 60/567；pytest 基线不变；证据 64-hex pin；Handoff + Record Decision。

## 允许修改范围

`apps/desktop-avalonia/**`（测试/harness 可加、生产代码只改安全缺陷）、本卡、STATUS/PLAN/LEDGER、`verification/HOST-RESOURCE-SECURITY-1/**`、workspace。只读：ADR-0002、S5-A Handoff、旧 Rust 通道（语义参考）。

## 禁止范围

不改旧壳（S5-C 才归档）、不改 Python Core、不 push、不 gc/prune、不为过测放宽校验/伪造数字。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 等长改写（同 size/mtime 粒度） | 无标签副本 | NOT_RUN | 待填 |
| AC2 | 越界/junction/reparse/UNC 负例 | 同上 | NOT_RUN | 待填 |
| AC3 | 替换同路径文件 | 同上 | NOT_RUN | 待填 |
| AC4 | 大页冷加载 + digest 占比 | 真实页夹具 | NOT_RUN | 待填 |
| AC5/AC6 | 契约测试 + 全量门禁 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-RESOURCE-SECURITY-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
