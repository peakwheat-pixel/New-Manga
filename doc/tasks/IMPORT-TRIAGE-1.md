---
id: IMPORT-TRIAGE-1
title: REPACK-5 导入 BLOCKED 诊断（HEAD 回归 vs 数据根）
kind: diagnosis
governance_version: 3
status: ready
approval: user_authorized_2026-10-28_diag
suggested_owner: route-research
owner: null
reviewer: dsh
depends_on: []
base_commit: 3be9ff938
branch: task/IMPORT-TRIAGE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/IMPORT-TRIAGE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/IMPORT-TRIAGE-1
allowed_paths:
  - doc/tasks/IMPORT-TRIAGE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/IMPORT-TRIAGE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/IMPORT-TRIAGE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/IMPORT-TRIAGE-1/**
---

# IMPORT-TRIAGE-1：导入 BLOCKED 诊断

## 背景
RELEASE-REPACK-5（HEAD \6120f91e5\，含三布局主题合并）真机烟测中**导入失败**：UI 状态卡「正在导入文件…」>40s、DB pages 不增、wire 仅 \RegisterImportSource\/\RevokeImportSource\、**无 \ImportPages\**。书架/工作台/默认主题/重复 fixture 均可复现；\ImportExportPanels/HostController\ 相对 REPACK-4 无 diff。REPACK-4（\1b89c5e5\）同流程导入正常（9→10 页）。

## Acceptance Criteria
- [ ] **AC1 干净数据根复测**：用**全新空数据根**（非 REPACK-4 副本）执行一次真实 UI 导入（fixture 书），记录 wire 帧（须出现 \ImportPages\ 或明确错误）。
- [ ] **AC2 判定**：干净根成功 → 结论「数据根/catalog 状态导致」；仍失败 → 结论「HEAD 回归」并继续 AC3。
- [ ] **AC3 二分定位**（仅回归时）：在 \1b89c5e5\（REPACK-4，导入正常）与 HEAD 之间二分（重点怀疑三布局主题合并对 \Pages.cs/MainWindow.axaml(.cs)\ 的替换），给出首个失败提交与根因（如页面 host/事件接线、\ImportPages\ 未发出）。
- [ ] **AC4 修复或隔离**：若为产品回归且可安全修复 → 最小修复 + 测试（headless 覆盖真实接线）+ 真机复验；否则给精确 root cause + 建议补丁范围。
- [ ] **AC5 门禁**：修好时 \	est.ps1\ ≥249、pytest 无新增、check PASS、64-hex pin、Handoff（含 Evidence 与 Record Decision）。

## 允许修改范围
\pps/desktop-avalonia/**\（仅诊断/最小修复）、本卡、STATUS/PLAN/LEDGER、\erification/IMPORT-TRIAGE-1/**\、workspace。

## 禁止范围
不改 Core/协议/Host 契约/旧壳、不 push、不 gc/prune、不伪造证据；**禁止 \git add -A\**。
