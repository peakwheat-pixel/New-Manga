---
id: REAL-TRANSLATE-PROVIDER-1
title: 接入真实翻译服务（OpenCode/OpenAI-compatible）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: route-research
owner: null
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/REAL-TRANSLATE-PROVIDER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REAL-TRANSLATE-PROVIDER-1
allowed_paths:
  - doc/tasks/REAL-TRANSLATE-PROVIDER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**; apps/desktop-avalonia/**
  - verification/REAL-TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/REAL-TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/REAL-TRANSLATE-PROVIDER-1/**
---

# REAL-TRANSLATE-PROVIDER-1：接入真实翻译服务（OpenCode / OpenAI-compatible）

## 背景
当前 `identity-translation` 为 experimental 占位（输入=输出）。用户提供 OpenCode key（`oc_sk_…`），要求接入真实翻译。

## Acceptance Criteria
- [ ] **AC1 探测**：确认 OpenCode/OpenAI-compatible endpoint 与可用模型（GET `/models`，记录 base_url/模型名，**不记录 key**）；把探测结论写入证据 JSON（key 仅以存在性标记）。
- [ ] **AC2 密钥安全**：key 从 `%TEMP%\nm-opencode-key.txt` 读取（用户已放置、ACL 限本人）；经 `credential_put` 写入 Windows vault 绑定 provider profile；**不写入仓库/日志/证据/截图**；完成后删除临时文件并记录。
- [ ] **AC3 真实翻译**：创建 provider profile（openai-compatible，base_url/model 按 AC1）+ translate slot binding；对 BOOK-FIXTURE 3 个有文字页跑 translate，断言 completed 且产出与输入不同（真实翻译，非 identity），给耗时。
- [ ] **AC4 降级**：网络失败/超时/4xx 返回 typed 错误并可回退 identity experimental；两条路径可配置切换。
- [ ] **AC5 回归/门禁**：test.ps1 全绿（≥225）；pytest 无新增失败；check.ps1 -TaskPath PASS；64-hex pin；Handoff + Record Decision（provider 语义/密钥处理/回退）。

## 环境
- 命令面：`settings_provider_profiles_create`、`settings_provider_bindings_set`、`credential_put`（均 66/0 已实现）
- BOOK-FIXTURE：`G:\CODEX\New Manga.workspace\task-envs\BOOK-FIXTURE-1\isolated-data`
- models sidecar：`task-envs\RELEASE-REPACK-2\out\NewManga-0.1.0-win-x64-models\app\core-sidecar`
- 私有 `NEWMANGA_EVIDENCE_DIR`

## 允许修改范围

`src/**; apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/REAL-TRANSLATE-PROVIDER-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。
