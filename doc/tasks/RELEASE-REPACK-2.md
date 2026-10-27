---
id: RELEASE-REPACK-2
title: 第二次 sidecar 重打包（identity provider + 缓存竞态修复）与 8 页全链复验
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 2980608e0
branch: task/RELEASE-REPACK-2
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-2
allowed_paths:
  - doc/tasks/RELEASE-REPACK-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-2/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2/**
---

# RELEASE-REPACK-2：第二次 sidecar 重打包与 8 页全链复验

## 背景

`TRANSLATE-PROVIDER-1`（identity-experimental provider）与 `RUN-STORE-CACHE-RACE-FIX-1`（缓存竞态）已合入 main，但 sidecar 仍是第一次重打包的构建（不含 identity provider）。需第二次重打包，并在**同一新构建**上验证 8 页全链到 render，再推进 Export。

## Acceptance Criteria

- [ ] **AC1 重打包**：用当前 `src/` 重打 base+models sidecar；记录新旧 sha256/大小；torch-free 闭包断言。
- [ ] **AC2 同构建 8 页全链**：新 models 构建 + BOOK-FIXTURE 私有副本 + identity 绑定（`pipeline_defaults` 或 StartRun override）：translate 3/3 completed、segment/inpaint/render 22/22 completed、页 4–8 completed(0)；**0 条 PROVIDER_NOT_CONFIGURED**；给每步耗时。
- [ ] **AC3 projection-fresh 并发复验**：新构建上跑 `verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py`（或等价），断言 0 卡 running、0 regionless INVALID_INPUT。
- [ ] **AC4 发布件与文档**：重打 base/models zip（`task-envs/RELEASE-REPACK-2/out`），install-verify/install-smoke（幂等、console 0、许可证一致）；更新 `VERSION.json.sidecar_build`；**补 `apps/desktop-avalonia/docs/UPGRADE.md` 安装说明**（本次 allowed_paths 已含）。
- [ ] **AC5 门禁**：`scripts/test.ps1` 全绿（≥177）；pytest 相对基线 4F/2760P/9S 无新增；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-REPACK-2/**`、workspace。

## 禁止范围

不改 Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不得伪造全链结果。
