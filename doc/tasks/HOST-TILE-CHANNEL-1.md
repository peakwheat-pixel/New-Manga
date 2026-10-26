---
id: HOST-TILE-CHANNEL-1
title: S5-A Host tile 通道 + per-tile SHA-256 + ≤1s 授权缓存 + containment
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [UI-WORKBENCH-READER-1]
base_commit: 2885861fa
branch: task/HOST-TILE-CHANNEL-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-TILE-CHANNEL-1
integration_commit: null
delivery_head: c8ab135d10f0232d6717ff4471f7e568f099f613
canonical_evidence_status: pinned
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

- [x] **AC1 tile 通道**：Host 提供 `tile` 服务：issue（返回不透明句柄 + size + identity + per-tile digest 清单）→ read（按 tile 读，返回字节 + 校验）→ revoke；UI 不接触 OS 路径/digest。 <<MET>>
- [x] **AC2 授权缓存**：授权状态查询带 ≤1s TTL 缓存；revoke 必须能**打断缓存**（事件驱动失效）；expiry 生效。 <<MET>>
- [x] **AC3 containment**：从已打开句柄重导最终路径并校验在允许根内；越界/junction/reparse 拒绝（为 S5-B 提供基础，测试覆盖最小集）。 <<MET>>
- [x] **AC4 内容完整性**：per-tile SHA-256 校验；**等长原地重写必拒**；篡改 tile 保尺寸 → 拒绝（typed error）。 <<MET>>
- [x] **AC5 接线与回归**：阅读器/工作台改用 tile 通道（可保留旧 fixture 兜底开关）；`scripts/test.ps1` 全绿；旧壳 vitest 60/567、pytest 基线不变。 <<MET>>
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（缓存失效语义、digest 计算时机、误差边界）。 <<MET>>

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
| E1-issue-read-revoke | AC1 | verification/HOST-TILE-CHANNEL-1/security/issue-read-revoke.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 79b3fe4f03a133f2d4e80b4ec2d801d2315d0ccabffd99ddf95f040f4dfc12b4 | CANONICAL |
| E2-cache-revoke | AC2 | verification/HOST-TILE-CHANNEL-1/security/cache-revoke.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | ed698acbd558105ffae35e61ea6a5afeb61834ed4d81b09fe4a078aec7ff85d2 | CANONICAL |
| E3-expiry | AC2 | verification/HOST-TILE-CHANNEL-1/security/expiry.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 90515e49f26cdef3c634c5d7242a4c9a0c0c90a5de007e4bbad16ec21bdb9f07 | CANONICAL |
| E4-containment | AC3 | verification/HOST-TILE-CHANNEL-1/security/containment.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 5aebde7aec847deb4eb8f4e7626bf6efd262b9fc59a9ca198ffd3689e83279f9 | CANONICAL |
| E5-equal-length-rewrite | AC4 | verification/HOST-TILE-CHANNEL-1/security/equal-length-rewrite.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | a66ebed787579ffeb17da723c5e7b1f02b2eaf6026bdcf2fbb0409bf4495f6d9 | CANONICAL |
| E6-tampered-tile | AC4 | verification/HOST-TILE-CHANNEL-1/security/tampered-tile.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 90d59d30365d428e089fdae4cf836415239d8ba1e5cff5d37bc94e0c46c663e6 | CANONICAL |
| E7-identity-change | AC4 | verification/HOST-TILE-CHANNEL-1/security/identity-change.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | f704845118f7bf16f5b7c4520a4038d1585e1b8208ee764466213f0e1cde6a05 | CANONICAL |
| E8-ui-reader | AC5 | verification/HOST-TILE-CHANNEL-1/security/reader-tile-channel.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | ae94bfb0b9b96851e2149f2889c2085e94fe1c57ba9a7255ea7d804c60e8594e | CANONICAL |
| E9-ui-workbench | AC5 | verification/HOST-TILE-CHANNEL-1/security/workbench-tamper.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | fd3baeb60e04d2848092a6c86eb3046b010fdfc6d091644c8f330a8c38c89c53 | CANONICAL |
| E10-perf | AC1/AC5 | verification/HOST-TILE-CHANNEL-1/performance/tile-read.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | 4511c508d188cefb19be52aa287c866b7145ccbb48eed508cf5af9e41b962afe | CANONICAL |
| E11-manifest | 全 AC | verification/HOST-TILE-CHANNEL-1/MANIFEST.json | c8ab135d10f0232d6717ff4471f7e568f099f613 | d8f5cd008228e62884f3f4921e6383469163ec360a8d751ebf06c177eb6b11d1 | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-TILE-CHANNEL-1 | d8f5cd008228e62884f3f4921e6383469163ec360a8d751ebf06c177eb6b11d1 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pinned`（E1–E11，commit c8ab135d1）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
