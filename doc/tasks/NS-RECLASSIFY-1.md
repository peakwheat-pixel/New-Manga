---
id: NS-RECLASSIFY-1
title: NOT_SUPPORTED 重探测与重分类（只出证据）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_a2_extra
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: 171529b5d
branch: task/NS-RECLASSIFY-1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-RECLASSIFY-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-RECLASSIFY-1
allowed_paths:
  - doc/tasks/NS-RECLASSIFY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-RECLASSIFY-1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-RECLASSIFY-1/**
---

# NS-RECLASSIFY-1：42 条 NOT_SUPPORTED 重探测与重分类（只出证据，不改代码）

## 背景

`READER-PROGRESS-1` 实现方发现：registry 中 `library_save_reading_progress` 仍标 NOT_SUPPORTED，原因是 S2 时 parity 探针 **payload 错误**（不是真没实现）。类似可能还有别的误分类。本任务把 42 条 NS 全部用**正确 payload** 重探测一遍，给出重分类建议。

## Acceptance Criteria

- [ ] **AC1 重探测**：对 `verification/HOST-COMMAND-MIGRATION-1/parity/**` 快照中的 42 条 NOT_SUPPORTED，按旧壳 Rust 签名构造正确 payload，对冻结双 sidecar 逐一探测，记录：可执行/需先实现 Core 路由/需模型/缺契约。
- [ ] **AC2 分类建议**：产出 `verification/NS-RECLASSIFY-1/reclassification.json`，每条给 `current_status / proposed_status(IMPLEMENTED|NEEDS_IMPLEMENTATION|NEEDS_MODEL|BLOCKED) / evidence / reason`；注明哪些是 S2 探针错、哪些是真未实现。
- [ ] **AC3 不改代码**：本任务**只产出证据与建议**，不修改 registry/parity 快照/冻结证据；应用改动由 DSH 在后续 Task 中做。
- [ ] **AC4 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff（含建议应用顺序与风险）。

## 允许修改范围

`verification/NS-RECLASSIFY-1/**`、本卡、STATUS/PLAN/LEDGER、workspace。**只读**：registry、parity 快照、sidecar。

## 禁止范围

不改任何产品源码/冻结证据/协议、不 push、不 gc/prune、不伪造探测结果。命不中签名的命令标 BLOCKED 写原因。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-RECLASSIFY-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
