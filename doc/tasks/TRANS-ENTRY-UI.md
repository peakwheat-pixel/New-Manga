---
id: TRANS-ENTRY-UI
title: 自动翻译入口与错误文案：工作台前置门 + 四类错误可读化 + 设置页如实表述
kind: implementation
governance_version: 3
status: in_progress
disposition: "L1-T-C（2026-11-14 DSH 释放）；依据 MAINT-1-AUTO-TRANSLATE-FEASIBILITY §7 T-C 与 T-A/T-B/L2 的五条前置约束"
approval: DSH 2026-11-14 释放（零冻结契约改动；依赖 T-A/T-B 已闭环）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - TRANS-BINDING-BRIDGE
  - TRANS-RUN-PATH-FIX
base_commit: 6019a2c53
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TRANS-ENTRY-UI
allowed_paths:
  - doc/tasks/TRANS-ENTRY-UI.md
  - doc/reviews/TRANS-ENTRY-UI-*.md
  - verification/TRANS-ENTRY-UI/**
  - apps/desktop-avalonia/src/NewManga.App/**
  - apps/desktop-avalonia/src/NewManga.CoreClient/**
  - apps/desktop-avalonia/src/NewManga.Host/**
  - apps/desktop-avalonia/tests/**
out_of_scope:
  - 冻结契约字节；不得新增 wire 命令或 IHostController 成员
  - src/**（Python Core 侧改动；若必须改则 STOP 报 DSH）
  - schema/DDL、依赖、远端写
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（DSH 维护）
---

# TRANS-ENTRY-UI：自动翻译入口与错误文案

## 五条前置约束（来自 T-A / T-B / L2 的实测，逐条都必须满足）

1. **走同一 Core 命令面**：任何 Host 侧改配置路径必须经 `settings_commands` 的同一 seam，否则 `provider_runtime_mirror` 只在一半路径生效。
2. **必须提示「配置后需重启 Core」**：provider 在装配期一次性构建（`core_assembly.py:1421-1426`）；不重启只会把失败前移为 `ProviderUnavailable`。
3. **scoped 展示面 ≠ 执行面**（R-6/R2-003）：执行链只读**扁平** `provider_bindings`，book/chapter 绑定**不驱动执行**。UI 若展示 scoped 绑定，必须同时说明其不参与执行，不得让用户误以为按书配置会生效。
4. **章节空时给可读文案**：Core 把 `EMPTY_TARGET_SELECTION` 折叠成 `INVALID_REQUEST / Run request is invalid`（T-B 已证）；UI 须先经 `list_chapter_pages` 探测，命中空章时给「本章没有可处理的页面」类文案，而不是透出通用错误。
5. **Host 默认 translate 值须来自当前 binding**：`RunBindingDefaults` 现从环境变量取值（T-B limitation）；UI 侧须让默认值反映当前翻译 binding，环境变量只作兜底。

## Acceptance Criteria

- [ ] **AC1 工作台前置门**：`WorkbenchViewModel` 的「开始处理」在 provider 未配置时**不发 StartRun**，改为可读提示（含"去设置"引导），文案覆盖 `PROVIDER_NOT_CONFIGURED`。
- [ ] **AC2 四类错误可读化**：`PROVIDER_NOT_CONFIGURED` / `PROVIDER_AUTH_FAILED`（401/403，不可重试）/ 模型名校验（404、402 目前都落 `INVALID_INPUT`，需给出可辨文案）/ `PROVIDER_RATE_LIMITED`（可重试）四类在 UI 文案上**可区分**，不得全部显示同一句。
- [ ] **AC3 空章可读文案**（约束 4）：在 StartRun 前探测 `list_chapter_pages`；空章 → 「本章没有可处理的页面」，**不得**透出 `INVALID_REQUEST / Run request is invalid`。
- [ ] **AC4 重启提示**（约束 2）：设置页/首个翻译尝试处显式说明「修改模型配置后需重启应用生效」。
- [ ] **AC5 scoped 绑定如实表述**（约束 3）：若设置页允许按书/章配置 provider，必须标注「当前仅全局绑定驱动执行」；若不做 scoped 配置入口，则登记为「未提供」。
- [ ] **AC6 修正过期文案**：`StudioInspectorPanel.cs:256` 的「能力待接入」按实际状态改写。
- [ ] **AC7 零契约面**：无新 wire 命令、无新 `IHostController` 成员；`generate_api_inventory --check` 维持 `1/80/6=87`；`verify_pins` 18/18。
- [ ] **AC8 判别测试**：每类文案至少一条测试（断言**用户可见字符串**，不是内部枚举）；空章探测与前置门各一条。
- [ ] **AC9 门禁**：`check.ps1`（默认 + 本卡 TaskPath）、`verify_pins`、`generate_api_inventory --check`、受影响 `dotnet test` 全绿。

## 测试要求

C#：`dotnet test`（App.Tests 为主）；不得新增 skip/xfail；若既有 UI 结构断言因文案改动失效，**同步更新并说明**，不得删除。

## 风险

- 文案改动可能撞既有结构断言（4B 的教训）；先 `grep` 既有断言里的中文串。
- AC3 的前置探测会增加一次 Core 往返；须在页面已加载后调用并处理失败（探测失败**不得**阻断翻译尝试，只能降级为不提示）。
- 若某类错误在 wire 上不可区分（例如 402/404 都是 `INVALID_INPUT`），**不要**在 UI 层编造区分；如实写「请求被拒绝（可能是模型名或额度）」并登记限制。

## 证据计划

`verification/TRANS-ENTRY-UI/README.md` + `logs/`（测试与门禁原始输出、文案对照表）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | `G:\CODEX\New Manga`（main） | NOT_APPLICABLE | - | - | 复用主工作树 |

## Closeout Record

- 未关闭（当前 `in_progress`）。
