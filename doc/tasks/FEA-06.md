---
id: FEA-06
title: Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）
kind: implementation
governance_version: 3
status: proposed
approval: pending_review
suggested_owner: dsh（Codex 通道故障、ZCode 未安装）
owner: null
reviewer: null
depends_on:
  - FEA-04b
  - FEA-05-PORT-1
base_commit: 1a844f681
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06
allowed_paths:
  - doc/tasks/FEA-06.md
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/IPageNavigation*.cs
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-*.md
---

# FEA-06：Fluent UI 四页实现（Shelf / Workbench / Reader / Settings）

## 来源与授权链

- 设计基线：`doc/design/fluent-v1/`（**FROZEN v1.0.0**，2026-11-02，独立复核 r5 approved；FEA-04b done）。
- 数据/命令面：FEA-05-WIRE-1（Core C078–C083）+ FEA-05-PORT-1（`IHostController` 7 Draft 方法、registry 17 additive）已 done。
- 架构：AD-002（Windows/C# .NET 9 + Avalonia），四页唯一（书架/工作台/阅读器/设置），视觉**参考** Saber-Translator（非 1:1）。
- 方案 §15.2（Fluent 独立 frontend）。

## 任务拆解（按页）

| 页 | 内容 | 设计输入 |
|---|---|---|
| P1 Shell | 顶栏/侧栏/状态带/命令条（17 全局快捷键）+ 四页 Tab 顺序 + 响应式三断点（1024/1280/1600） | `04-layout-responsive.md`、`03-accessibility.md` |
| P2 Shelf | 书架页：网格/列表、筛选、空态、加载态、错误态 | `05-page-shelf.md` |
| P3 Workbench | 工作台页：Region 列表/画布/Inspector/FilmStrip/批量栏；Draft 命令面接入（Open/Patch/Prepare/Apply/Status/Discard） | `06-page-workbench.md` |
| P4 Reader | 阅读器页：页导航、缩放、进度保存、键盘/滚轮 | `07-page-reader.md` |
| P5 Settings | 设置页：C-03 §2.2 字段、保存/校验/错误态 | `08-page-settings.md` |
| P6 设计系统消费 | 令牌绑定（`01-design-tokens.md`）、动效三态（`02-motion.md`）、状态矩阵（`09-state-matrix.md`）、组件清单（`10-component-inventory.md`） | 全部 |

## 验收标准

- [ ] **AC1 Shell + 响应式**：四页 Tab 顺序与 17 快捷键与设计一致；三断点布局；z-order 正确。<<TODO>>
- [ ] **AC2 Shelf**：网格/列表/筛选/空态/加载态/错误态；令牌绑定（`Nm.Color.*`/`Nm.Size.*`）。<<TODO>>
- [ ] **AC3 Workbench**：Region 选择/Inspector/FilmStrip/批量栏 + **Draft 命令面接入**（复用 FEA-05-PORT-1 的 7 方法，含 typed error 映射到 UI 状态）。<<TODO>>
- [ ] **AC4 Reader**：页导航/缩放/进度保存（读 FEA-04 的 `IReaderProgressSink`）；键盘/滚轮。<<TODO>>
- [ ] **AC5 Settings**：C-03 §2.2 字段渲染/保存/校验/错误态。<<TODO>>
- [ ] **AC6 可访问性/动效**：键盘可达（Tab 顺序）、A11y 名称、`motion.categories=off` 语义、reduce-motion 0ms 反馈。<<TODO>>
- [ ] **AC7 回归**：全量 sln 不退化（基线 949/0/57）+ App.Tests 新增用例。<<TODO>>
- [ ] **AC8 证据**：`verification/FEA-06/**`（截图/日志）+ 证据表。<<TODO>>

## 禁止范围

- 不改 Core/契约（FEA-05 已冻结）；不改 schema；不改用户数据；不改 `doc/design/fluent-v1/**`（设计变更走 v1.1 + 重冻结）；不 push。
- 不实现设计基线之外的新交互（超出即范围变更）。

## 附加裁决点（DSH 已裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 设计基线版本 | 唯一输入 `fluent-v1.0.0`（FROZEN）；偏差须走 v1.1 修订 | FEA-04b Closeout |
| W-2 | Draft 命令面接入方式 | 经 `IHostController`（FEA-05-PORT-1）而非直接 CoreClient；typed error（`DraftError` code/category）映射到 UI 状态 | FEA-05-PORT-1 交付 |
| W-3 | 页面拆分 | 每页独立 View/ViewModel，Shell 只做导航与布局 | 设计 `04-layout-responsive.md` |
| W-4 | 视觉实现 | 用 `NewManga.DesignSystem` 令牌 + `NewManga.ThemeEngine`（既有），不新建第二套设计系统 | AC6/AC7 |

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC6 | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests` + Avalonia.Headless | .NET | NOT_RUN | 待补 |
| AC7 | 全量 sln build/test（基线 949/0/57） | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree（main 直接实现）；资源处置在收口时登记。

## Closeout Record

- 待关闭时填写。
