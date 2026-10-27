---
id: CORE-PIPELINE-FIX-1
title: color analyzer 替换 + 空检测语义（Core 语义小改）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_run_fix_a_b
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: ce181ce0b
branch: task/CORE-PIPELINE-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-PIPELINE-FIX-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CORE-PIPELINE-FIX-1
allowed_paths:
  - doc/tasks/CORE-PIPELINE-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/CORE-PIPELINE-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CORE-PIPELINE-FIX-1/**
---

# CORE-PIPELINE-FIX-1：color analyzer 替换 + 空检测语义（Core 语义小改，已授权）

## 背景

RUN-OCR-DIAG-1 实证两个 Core 侧阻断点：
1. `color` 步骤 `PROVIDER_FAILED: '_StubStyleAnalyzer' object has no attribute 'analyze'`（`core_service.py:654/715` ↔ `application/translation/color/service.py:30`）；仓库内已有 `PillowSourceStyleAnalyzer`。
2. 检测器正常返回 0 候选时被映射为 `INVALID_INPUT`（`handlers.py:296`），导致无文字页整页失败。

## Acceptance Criteria

- [ ] **AC1 color analyzer**：把 `_StubStyleAnalyzer` 替换为可用的 `PillowSourceStyleAnalyzer`（或等价已验证实现），`color` 步骤不再 `PROVIDER_FAILED`；失败仍 typed。
- [ ] **AC2 空检测语义**：检测结果为 0 候选时按 **completed(0 region)** 或 `skipped` 处理（可用 `empty_detection_policy` 配置，默认不失败）；错误输入仍按原语义报错。
- [ ] **AC3 同构建复验**：models 包构建 `2b36bfeb…4ec519b` 上整书 8 页 Run：`color` 通过、4–8 页无文字页不再整页失败；给出每页状态与耗时；未到 render 的部分如实记录。
- [ ] **AC4 单测/回归**：新增 color analyzer 与空检测语义单测；pytest 相对基线（3F/2746P/9S）无新增失败；`scripts/test.ps1`（App/Host 侧）全绿；vitest 60/567 不变。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（Core 语义变更理由/影响面/回退开关）。

## 允许修改范围

`src/**`（仅 color 组装点、检测语义与相关测试）、本卡、STATUS/PLAN/LEDGER、`verification/CORE-PIPELINE-FIX-1/**`、workspace。

## 禁止范围

不改协议/Host 契约、不改旧壳、不 push、不 gc/prune；不得放宽检测/OCR 的输入校验；不得把 0 候选静默当成成功而不留记录（需可观测）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-PIPELINE-FIX-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
