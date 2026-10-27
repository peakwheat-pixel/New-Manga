---
id: EXPORT-E2E-CLOSE-1
title: Export 端到端真跑（新 sidecar + translated 产物 + grant）
kind: verification
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: null
reviewer: dsh
depends_on: []
base_commit: e30149258
branch: task/EXPORT-E2E-CLOSE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/EXPORT-E2E-CLOSE-1
allowed_paths:
  - doc/tasks/EXPORT-E2E-CLOSE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/EXPORT-E2E-CLOSE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/EXPORT-E2E-CLOSE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/EXPORT-E2E-CLOSE-1/**
---

# EXPORT-E2E-CLOSE-1：Export 端到端真跑

## 背景

RELEASE-REPACK-2 新 sidecar 上 Run 已 **terminal=completed**（translate/render 22/22，86.43s），translated 产物已具备；GRANT-ISSUER-1 已实现 host_issuer grant（`RegisterExportTarget`）。此前 `StartExport` 卡在 `EXPORT_INPUT_UNAVAILABLE`（无 translated 页），现在前置已解除。

## Acceptance Criteria

- [ ] **AC1 前置复验**：新 sidecar（`c5531930…` models / `091a201d…` base）上确认 translated 产物存在且可定位（GetExportHistory/投影）。
- [ ] **AC2 Export 真跑**：通过 Host 命令面 + grant 链（RegisterExportTarget → StartExport）对 BOOK-FIXTURE 书执行导出 → **真实产物**（PDF/图片包/项目文件），校验大小/页数/可打开 + SHA-256。
- [ ] **AC3 get/cancel 成功路径**：`library_get_export_snapshot`/`library_cancel_export` 在真实导出记录上验证（成功与取消各一次）。
- [ ] **AC4 回归/证据**：test.ps1 全绿（≥182）；pytest 相对基线（3F/2764P/9S）无新增；check.ps1 -TaskPath PASS；64-hex pin；Handoff。
- [ ] **AC5 门禁**：同上 + 产物与命令面证据入库。

## 允许修改范围

`apps/desktop-avalonia/**`（仅验证脚本/测试，必要时最小接线）、本卡、STATUS/PLAN/LEDGER、`verification/EXPORT-E2E-CLOSE-1/**`、workspace。

## 禁止范围

不改 Python Core 语义/协议/旧壳、不 push、不 gc/prune；**不得伪造导出产物**；若仍 BLOCKED 需给可判定证据与前置缺口。
