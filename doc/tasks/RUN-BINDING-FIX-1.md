---
id: RUN-BINDING-FIX-1
title: Host 侧 StartRun 携带 provider bindings（零 Core 改动）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_run_fix_a_b
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: b993e68bb
branch: task/RUN-BINDING-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RUN-BINDING-FIX-1
allowed_paths:
  - doc/tasks/RUN-BINDING-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/RUN-BINDING-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1/**
---

# RUN-BINDING-FIX-1：Host 侧 StartRun 携带 provider bindings（零 Core 改动）

## 背景

RUN-OCR-DIAG-1 实证：OCR `PROVIDER_NOT_CONFIGURED` 根因是 Core `pipeline_defaults.provider_bindings_json='{}'`，`_chain()` 取不到 `ocr` 绑定。**只加 `overrides.provider_bindings={"ocr":"manga-ocr"}` → OCR 步骤 completed**（13/13 region 有文本），零 Core 改动。

## Acceptance Criteria

- [ ] **AC1 接线**：Host 侧 StartRun 调用携带 `overrides.provider_bindings`（默认 `{"ocr":"manga-ocr"}`，允许配置/关闭覆盖；不覆盖用户显式传入的 overrides）。
- [ ] **AC2 同构建复验**：在 models 包构建 `2b36bfeb…4ec519b` 上整书 8 页复跑，断言 `ocr` step **不再出现 `PROVIDER_NOT_CONFIGURED`**；允许仍停在 color/translate 且错误类型可判定（区分「OCR 已通」与「整链已通」）。证据含 run 快照/step_runs/日志。
- [ ] **AC3 语义测试**：有/无 override 两态单测；参数边界与覆盖优先级；unknown provider 返回 typed 错误。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 相对基线（3F/2746P/9S）无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（默认绑定/覆盖策略）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/RUN-BINDING-FIX-1/**`、workspace。

## 禁止范围

**不得改 Python Core**（本 Task 是零 Core 改动路线）；不改协议/Host 契约语义、不改旧壳、不 push、不 gc/prune；不得把「OCR 通」写成「整链通」。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
