---
id: PDF-EXPORT-1
title: PDF 导出（Pillow 合成，不引入 Qt）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_round_2_5
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: 13cf26f6c
branch: task/PDF-EXPORT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/PDF-EXPORT-1
allowed_paths:
  - doc/tasks/PDF-EXPORT-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/PDF-EXPORT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/PDF-EXPORT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/PDF-EXPORT-1/**
---

# PDF-EXPORT-1：PDF 导出（Pillow 合成，不引入 Qt）

## 背景
导出已支持 ZIP 图片包（真机真跑验证）；PDF 未覆盖。历史 Qt composer 已随 CORE-SLIM 移除，**不得重新引入 PySide6/Qt**。

## Acceptance Criteria
- [ ] **AC1 方案**：确认 Core 导出格式扩展点；用 **Pillow（现有依赖）** 把已渲染页合成多页 PDF（尺寸/DPM/顺序正确），记录方案与影响面。
- [ ] **AC2 实现**：导出支持 PDF 格式（命令参数/格式枚举，保持与 ZIP 兼容），产出真实 PDF 文件。
- [ ] **AC3 验证**：对 BOOK-FIXTURE 8 页（3 个有译文页）导出 PDF → 校验页数、每页尺寸、可被 PDF 解析器打开（如 pypdf，若无则用 Pillow 回读 + 文件头校验），SHA-256 入库。
- [ ] **AC4 回归**：pytest 相对基线（3F/2772P/9S）无新增失败；`scripts/test.ps1` 全绿；闭包不新增 Qt 依赖（spec 断言）。
- [ ] **AC5 门禁**：check.ps1 -TaskPath PASS；64-hex pin；Handoff + Record Decision。

## 允许修改范围

`src/**`、本卡、STATUS/PLAN/LEDGER、`verification/PDF-EXPORT-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**不得把任何 API key/secret 写入仓库、日志或证据**。
