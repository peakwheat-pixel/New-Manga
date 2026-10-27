---
id: PDF-EXPORT-UI-1
title: PDF 导出 UI 选项（导出面板格式选择）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: saber-ui-spec
owner: null
reviewer: dsh
depends_on: []
base_commit: 170878dc4
branch: task/PDF-EXPORT-UI-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PDF-EXPORT-UI-1
allowed_paths:
  - doc/tasks/PDF-EXPORT-UI-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/PDF-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-UI-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-UI-1/**
---

# PDF-EXPORT-UI-1：PDF 导出 UI 选项

## 背景
Core 已支持 PDF 导出（`QtFreePdfComposer`：`image_only` 无损 RGB / `searchable_dual_layer` CJK 文本层；baseline-scout 真机验证 3 页 8.7MB、文本层 277/204/120 字符、engine 级 8 页尺寸匹配）。但**导出 UI 面板仍是「ZIP 图片包」**（`Views/ImportExportPanels.cs`），PDF 用户不可达。

## Acceptance Criteria
- [ ] **AC1 格式选择**：导出面板新增格式选项（ZIP 图片包 / PDF；PDF 可选 image_only / searchable_dual_layer）→ 参数正确传给 `library_start_export`。
- [ ] **AC2 结果展示**：导出完成显示真实文件路径 + sha256 + 页数/格式；PDF 与 ZIP 提示区分。
- [ ] **AC3 测试**：Headless 覆盖格式参数传递（ZIP/PDF 两种 + 模式）、完成态展示、错误提示；真机截图一次（导出面板含 PDF 选项）。
- [ ] **AC4 回归**：test.ps1 全绿（≥225）；vitest 60/567；pytest 无新增失败。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围
`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/PDF-EXPORT-UI-1/**`、workspace。

## 禁止范围
不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不伪造导出结果；不得把 ZIP 文案留成唯一选项。
