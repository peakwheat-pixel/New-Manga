---
id: MICA-FIX-1
title: Mica 材质可见化（透明背景+诊断+回退）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: []
base_commit: 4deb9ef3e
branch: task/MICA-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/MICA-FIX-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/MICA-FIX-1
allowed_paths:
  - doc/tasks/MICA-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/MICA-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/MICA-FIX-1/**
---

# MICA-FIX-1：Mica 材质可见化

## 背景

真机核验（MANUAL-VERIFY-1）判定 FAIL：`MainWindow.axaml:10` 根窗口 `Background="{DynamicResource AppBg}"`、`:18` TitleBar `Background="{DynamicResource HeaderBg}"` 为不透明背景，把 `TransparencyLevelHint="Mica,Blur,None"` 完全盖住 → 用户看到纯白标题栏，材质不生效。

## Acceptance Criteria

- [ ] **AC1 Mica 可见**：Win11 上 Mica 生效时，窗口标题栏/根背景为透明或半透明，壁纸颜色能透出；用「同窗口放在纯色壁纸区 vs 图案区」两张截图证明标题栏取色随壁纸变化（或贴色差数值）。
- [ ] **AC2 诊断输出**：启动时（或 `--diagnostics`）输出 `ActualTransparencyLevel` 与 `WindowMaterialKind` 到日志/证据，证明确实拿到 Mica 而非回退 None。
- [ ] **AC3 Win10/不支持环境回退**：仍是不透明 `MicaFallback`，不得出现黑边/透明穿透；OS 判定分支有单测。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿（含新增 UI 测试）；旧壳 vitest 60/567；pytest 相对基线（3F/2739P/9S）无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（透明策略/回退策略/取色方法）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/MICA-FIX-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不改旧壳/Python Core；不 push；不 gc/prune；不得用"抹掉背景色"造成文字不可读（对比度需自查）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 真机 Win11 截图 A/B（纯色/图案壁纸） | 本机 1080p 主屏 | NOT_RUN | 待填 |
| AC2 | 启动诊断输出 ActualTransparencyLevel | 本机 | NOT_RUN | 待填 |
| AC3/AC4 | 单测 + test.ps1 + vitest + pytest | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/MICA-FIX-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
