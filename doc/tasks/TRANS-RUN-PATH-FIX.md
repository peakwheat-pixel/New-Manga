---
id: TRANS-RUN-PATH-FIX
title: 自动翻译运行路径收口：修 library_start_run 的 INVALID_REQUEST + RunBindingDefaults 扩展
kind: implementation
governance_version: 3
status: in_progress
disposition: "L1-T-B（2026-11-14 DSH 释放）；依据 MAINT-1-AUTO-TRANSLATE-FEASIBILITY §7 T-B 与 REAL-TRANSLATE-PROVIDER-1 §7.2 遗留"
approval: DSH 2026-11-14 释放（零冻结契约改动；依赖 T-A 已 closed）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - TRANS-BINDING-BRIDGE
base_commit: f8a6185f9
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TRANS-RUN-PATH-FIX
allowed_paths:
  - doc/tasks/TRANS-RUN-PATH-FIX.md
  - doc/reviews/TRANS-RUN-PATH-FIX-*.md
  - verification/TRANS-RUN-PATH-FIX/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/tests/**
  - src/bootstrap/**
  - src/application/**
  - src/infrastructure/**
  - tests/**
out_of_scope:
  - 冻结契约字节（C-01b…C-17、M2-C1、ADJ-001）；不得新增 wire 命令或 IHostController 成员
  - schema/DDL 变更、依赖变更、远端写操作
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# TRANS-RUN-PATH-FIX：自动翻译运行路径收口

## 来源

- 评估 §7 T-B：`TRANS-RUN-PATH-FIX`。
- 遗留缺陷：`verification/REAL-TRANSLATE-PROVIDER-1/REPORT.md:75,80` 记录「隔离根 + REPACK-2 models sidecar 下，Host `library_start_run` 返回 `INVALID_REQUEST`；Core 直连同 payload 可接受」——**未定位**。
- `RunBindingDefaults.DefaultJson = {"ocr":"manga-ocr"}`（`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RunBindingDefaults.cs:23`）默认不注入 translate。

## Acceptance Criteria

- [ ] **AC1 先诊断后修**：定位 `library_start_run` 的 `INVALID_REQUEST` 根因（Host dispatcher 的 payload 形状 vs Core 期望），给出**证据**（文件:行 + 复现步骤 + 实际/期望形状差异）。**不得**在未定位前盲改。
- [ ] **AC2 修复**：按 AC1 的诊断修复；若根因在 Core 侧，改动须最小且不改冻结契约；若确认是 Host 侧传参错误，修 Host。
- [ ] **AC3 RunBindingDefaults 扩展**：默认绑定改为「ocr +（存在 translate 配置时）translate」，且**用户显式 overrides 永远优先**（保持 `RunBindingDefaults.cs:9-15` 既有语义）。
- [ ] **AC4 不新增契约面**：无新 wire 命令、无新 `IHostController` 成员；`generate_api_inventory --check` 维持 `1/80/6=87`；`verify_pins` 18/18。
- [ ] **AC5 判别测试**：至少一条覆盖「默认绑定含 translate」与「显式 override 优先」；若 AC1 的根因可测，补一条回归测试。
- [ ] **AC6 门禁**：`check.ps1`（默认 + 本卡 TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响 `dotnet test` 与 pytest 全绿。
- [ ] **AC7 若根因不可修**：允许 `closed_with_limitations`，但**必须**给出「不可修的客观原因 + 已排除的假设 + 下一步需要的条件」，不得用「未定位」收尾。

## 测试要求

C#：`dotnet test`（CoreClient / Host / App 受影响项目）；Python：定向 + 全量 `pytest` 不得新增 failed。

## 风险

- AC1 的根因可能不在 Host 而在 Core 的 payload 校验；**先取证**，不要按假设改。
- `RunBindingDefaults` 有环境变量覆盖口 `NEWMANGA_RUN_PROVIDER_BINDINGS`，改动须保留它。
- 若发现必须新增 wire 命令才能修，**停下回卡报 DSH**。

## 证据计划

`verification/TRANS-RUN-PATH-FIX/README.md` + `logs/`（诊断证据、测试与门禁原始输出）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |

## Closeout Record

- 未关闭（当前 `in_progress`）。
