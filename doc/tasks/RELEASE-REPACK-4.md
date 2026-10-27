---
id: RELEASE-REPACK-4
title: 最终发布包（含 PDF UI/工具/修复）与端到端验收
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_goal_all_authorized
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: d2f66a19e
branch: task/RELEASE-REPACK-4
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-4
allowed_paths:
  - doc/tasks/RELEASE-REPACK-4.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**; apps/desktop-avalonia/scripts/**; apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-4/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-4/**
---

# RELEASE-REPACK-4：最终发布包（含 PDF UI / 翻译工具 / 最终修复）

## 背景
REPACK-3（repo_head dd2408869）之后合入了 PDF-EXPORT-UI-1（PDF 面板）、REAL-TRANSLATE-PROVIDER-1 工具与测试修复。需要一次**最终**打包，并做端到端验收（含 PDF 导出）。

## Acceptance Criteria
- [ ] **AC1 重打包**：当前 HEAD 重打 base+models zip（记录新旧 sha256/大小/HEAD；torch-free 断言）。
- [ ] **AC2 全流程**：全新安装 → 导入 → 阅读 → 沉浸 Esc/H → 导出 ZIP → 导出 PDF（面板选 PDF/searchable_dual_layer）→ 打开导出目录；每步截图/耗时。
- [ ] **AC3 真机 5 项**：Mica（actual/取色）、4K@200% DPI（若环境不满足如实记录并给显示器状态）、工作集、Esc/H 键盘（前台自动化）、IME 标 N/A（需人工）。
- [ ] **AC4 稳定性**：0 残留、console 0、卸载干净。
- [ ] **AC5 门禁**：干净 worktree test.ps1 全绿（≥241）；pytest 0F/2773P/10S 无新增；check.ps1 -TaskPath PASS；64-hex pin；Handoff。

## 允许修改范围
`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、`verification/RELEASE-REPACK-4/**`、本卡/STATUS/PLAN/LEDGER、workspace。

## 禁止范围

不改 Python Core 语义/协议/Host 契约/旧壳、不 push、不 gc/prune；不得伪造结果；**禁止 `git add -A`（主工作树有其它会话改动）**。
