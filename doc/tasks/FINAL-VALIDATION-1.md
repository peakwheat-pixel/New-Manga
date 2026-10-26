---
id: FINAL-VALIDATION-1
title: 终验与发布重建——按新 spec 重建侧车 + 重打包 + 许可复验 + 全量回归
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-SLIM-2, RELEASE-PACKAGE-1]
base_commit: d3f081870
branch: task/FINAL-VALIDATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FINAL-VALIDATION-1
allowed_paths:
  - doc/tasks/FINAL-VALIDATION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - scripts/**
  - packaging/**
  - verification/FINAL-VALIDATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/**
  - G:/CODEX/New Manga.workspace/worktrees/FINAL-VALIDATION-1/**
---

# FINAL-VALIDATION-1：终验与发布重建

## 目标

把「新架构 + 新 Core 闭包」真正装成一个可运行发布件并全量复核。

## Acceptance Criteria

- [ ] **AC1 侧车重建**：用新 spec（`packaging/m2ac5/core_sidecar.spec`，无 Qt/无 torch）重建 `core_service`/`host_bridge` 等 entry，记录体积表；启动/协议 smoke 通过。
- [ ] **AC2 重打包**：`apps/desktop-avalonia/scripts/package.ps1` 产出安装包（含 Core 侧车与模型分发策略），体积 ≤2GB（含基础模型）/≤150MB（不含模型）；包内许可三件套逐字节一致。
- [ ] **AC3 全量回归**：`scripts/test.ps1` 全绿；pytest 相对基线 3F/2739P/9S 无新增失败；旧壳 vitest 60/567 不变；`command_allowlist` parity 快照 `--check` 零漂移。
- [ ] **AC4 安装 smoke**：安装→启动→窗口→退出无残留（复用 RELEASE-PACKAGE-1 的 `install-smoke.ps1`，新包复跑）。
- [ ] **AC5 收尾文档**：AD-002 标记 S0–S5 完成；`DISPLAY-PERF-DECISION-1` 关闭；产出 `MANUAL_VERIFY.md` 最新版（真机 5 项）。
- [ ] **AC6 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`apps/desktop-avalonia/**`、`scripts/**`、`packaging/**`、本卡、STATUS/PLAN/LEDGER、`verification/FINAL-VALIDATION-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不删除能力；不 push；不 gc/prune；不伪造成安装成功。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 重建 + 启动/协议 smoke | 无标签副本 | NOT_RUN | 待填 |
| AC2/AC4 | 打包 + 安装 smoke | 干净目录 | NOT_RUN | 待填 |
| AC3/AC6 | 全量回归 + 治理 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
