---
id: NS-WIRE-B2
title: 剩余 NOT_SUPPORTED 命令接线（以 registry 实际 11 条为准）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: ui-stack-research
owner: null
reviewer: dsh
depends_on: []
base_commit: 27b5a4005
branch: task/NS-WIRE-B2
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-WIRE-B2
allowed_paths:
  - doc/tasks/NS-WIRE-B2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-B2/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-B2/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-B2/**
---

# NS-WIRE-B2：剩余 NOT_SUPPORTED 命令接线

## 背景

命令面已达 **55 IMPLEMENTED / 11 NOT_SUPPORTED**（NS-WIRE-A1/B1、RUN-EXPORT、S4、GRANT 合计）。NS-RECLASSIFY-1 已证明多数旧 NS 是 S2 探针错误；剩余 11 条需逐条核实后接线。

## Acceptance Criteria

- [ ] **AC1 清单**：从 `HostCommandRegistry`（`CommandParityContractTests` 断言 notSupported=11）导出当前 11 条 NS 清单，逐条标注 Core 路由/参数/返回/Core 是否已支持（参考 `verification/NS-RECLASSIFY-1/reclassification.json`）。
- [ ] **AC2 接线**：可执行的接入 dispatcher/domain service，对冻结 sidecar **真实执行**断言；`list_region_revisions` 路由探针已 ok:true，应优先接。
- [ ] **AC3 真缺口**：Core 无等价命令或需 grant/翻译链的，如实标 BLOCKED 并写明原因（不得把验证不了的标 IMPLEMENTED）。
- [ ] **AC4 parity/回归**：`extract-command-surface.py --check` 零漂移；`scripts/test.ps1` 全绿（≥177）；vitest 60/567；pytest 无新增确定性失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-B2/**`、workspace。

## 禁止范围

不改 Python Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不抢 TRANSLATE/RACE 范围；验证不了的不许标 IMPLEMENTED。
