---
id: DPI-DYNAMIC-1
title: 跨屏动态 DPI 重渲染（消除位图拉伸）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_manual_verify_followups
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: []
base_commit: 4deb9ef3e
branch: task/DPI-DYNAMIC-1
worktree: G:/CODEX/New Manga.workspace/worktrees/DPI-DYNAMIC-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/DPI-DYNAMIC-1
allowed_paths:
  - doc/tasks/DPI-DYNAMIC-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/DPI-DYNAMIC-1/**
  - G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1/**
  - G:/CODEX/New Manga.workspace/worktrees/DPI-DYNAMIC-1/**
---

# DPI-DYNAMIC-1：跨屏动态 DPI 重渲染

## 背景

真机核验（MANUAL-VERIFY-1）发现：把窗口从 100% 屏拖到 200% 屏（4K）后，内容被 DWM **位图拉伸**（发虚、2× 放大）；而**直接在 200% 屏启动**时渲染正确（窗口 DPI=192、UI 尺寸正常）。→ 运行中未按 `WM_DPICHANGED` 重渲染/重排。

## Acceptance Criteria

- [ ] **AC1 跨屏重渲染**：窗口从 100% 屏拖到 200% 屏后，`GetDpiForWindow`=192 且界面**按新 DPI 重渲染**（逻辑尺寸不变、文字锐利，截图与原 200% 启动一致或差异可解释）。
- [ ] **AC2 反向验证**：从 200% 屏拖回 100% 屏同样正确（不残留大字号/模糊）。
- [ ] **AC3 manifest 检查**：确认 `PerMonitorV2` DPI awareness 声明正确（app.manifest / ApplicationManifest），并记录结论。
- [ ] **AC4 回归**：`scripts/test.ps1` 全绿；旧壳 vitest 60/567；pytest 相对基线无新增失败。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff（DPI 处理机制/验收方法/截图）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/DPI-DYNAMIC-1/**`、workspace。

## 禁止范围

不改协议/命令语义/Host 契约；不改旧壳/Python Core；不 push；不得仅靠"重启应用"蒙混（必须是运行中移动生效）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 100%→200% 拖动后截图 + GetDpiForWindow | 本机 2K(100%)+4K(200%) | NOT_RUN | 待填 |
| AC2 | 200%→100% 回拖 | 同上 | NOT_RUN | 待填 |
| AC3/AC4 | manifest 检查 + 全量回归 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/DPI-DYNAMIC-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
