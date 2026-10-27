---
id: TRANSLATE-PROVIDER-1
title: 翻译 provider 最小可用接线
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: null
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/TRANSLATE-PROVIDER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TRANSLATE-PROVIDER-1
allowed_paths:
  - doc/tasks/TRANSLATE-PROVIDER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1/**
---

# TRANSLATE-PROVIDER-1：翻译 provider 最小可用接线（让 Run 过 translate）

## 背景

CORE-PIPELINE-FIX-1 后 Run 链停在 `translate`：typed `PROVIDER_NOT_CONFIGURED`（无 provider binding）。需要最小可用翻译 provider 让流水线可继续到 render（不追求翻译质量，但必须真实产出、可观测、可替换）。

## Acceptance Criteria

- [ ] **AC1 清单**：列出 Core 侧现有 translate provider 实现与注册方式（`providers/` 与 `providers/registry`），判定哪个可离线运行；如无，则建立最小 `identity` provider（输入=输出，明确标注 experimental）并注册。
- [ ] **AC2 绑定与装配**：通过 provider binding（start_run override 或默认绑定）接入 `translate` 步骤；失败仍 typed。
- [ ] **AC3 同构建复验**：RELEASE-REPACK-1 的新 sidecar 上 8 页 Run：`translate` 3/3 completed（页 1–3），页 4–8 保持 completed(0)；链路推进到 render（若 render 有独立前置，如实记录卡点，不许伪造）。
- [ ] **AC4 单测/回归**：provider 单测 + 绑定单测；pytest 相对基线（3F/2753P/9S）无新增失败；`scripts/test.ps1` 全绿。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（provider 语义/质量声明/替换路径）。

## 允许修改范围

`src/**`（providers/registry/装配与测试）、本卡、STATUS/PLAN/LEDGER、`verification/TRANSLATE-PROVIDER-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得把 machine/identity 翻译当成品宣发（必须在 Handoff 明确「experimental/占位」）；不得放宽输入校验。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
