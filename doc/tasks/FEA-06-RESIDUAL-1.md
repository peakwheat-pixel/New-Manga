---
id: FEA-06-RESIDUAL-1
title: Fluent 四页规格补齐（FEA-06 AC1–AC7 residual）
kind: implementation
governance_version: 3
status: proposed
approval: pending_scope_review（FEA-06 closeout residual 转入）
suggested_owner: codex
owner: codex
reviewer: null
depends_on:
  - FEA-06
  - FEA-07
  - FEA-09
  - FEA-10
  - FEA-11
  - FEA-12
  - FEA-13
base_commit: b26840acdf682d69cf531bec3161d17bf90cf9f4
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-06-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-1.md
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/**
  - apps/desktop-avalonia/src/NewManga.App/Controls/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.DesignSystem.Tests/**
  - verification/FEA-06-RESIDUAL-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-06-RESIDUAL-1-*.md
  - doc/handoffs/FEA-06-RESIDUAL-1-*.md
---

# FEA-06-RESIDUAL-1：Fluent 四页规格补齐（AC1–AC7 residual）

## 来源与授权链

- **来源**：`FEA-06` done（集成 `b26840acd`；scope-r3 + impl-r2 approved）；AC8–AC10 MET，**AC1–AC7 为 PARTIAL**，经 DSH 处置转为本卡 residual（见 `doc/tasks/FEA-06.md` Closeout Record 与 `doc/reviews/FEA-06-impl-r1.md` / `-r2.md`）。
- **设计基线**：`doc/design/fluent-v1/`（FROZEN v1.0.0，唯一设计输入；偏差走 v1.1 重冻结）。
- **依赖**：多数 residual 需后续 Task 的 Host 端口/数据面落地后才能闭环（见 §残项与依赖）；**本卡不阻塞 FEA-07**，按端口就绪程度分批释放（可再拆子 Task）。
- **Owner**：Codex（沿用用户 2026-11-02 指派；scope 冻结后按 W-10 派发）。

## 残项清单（来自 FEA-06 impl-r1/r2 与 Closeout）

| # | AC | 残项 | 依赖/阻塞 |
|---|---|---|---|
| R-1 | AC1 | 分栏折叠、UI memento 恢复、200% DPI 原生验收、原生桌面验收 | FEA-07（窗口/memento/DPI） |
| R-2 | AC2 | 回收站入口仅空面板（恢复/删除操作缺失）、扫描进度逐项、错误卡「控制台入口」、满态统计 | FEA-12（回收站端口）、FEA-10（Run 投影）、本卡补 UI |
| R-3 | AC3 | Run 投影/暂停停止控制、BatchMatrix 数据绑定、9 行状态全实现、未保存圆点、冲突「查看对照」 | FEA-10（Run/批量端口）、FEA-07（未保存确认） |
| R-4 | AC4 | 双页第二图、滚动模式、工具条自动隐藏、源不可用只读警示 | 阅读器数据面（FEA-09/11） |
| R-5 | AC5 | 网络超时/并发、备份目录/频率字段、完整错误/部分状态、离开未保存确认/Esc | FEA-13（备份字段）、FEA-07（离开确认） |
| R-6 | AC6 | 组件 full 状态（normal/hover/pressed/disabled/浮层开关）逐项补齐 | 本卡 UI |
| R-7 | AC7 | 焦点环、三类 motion 状态覆盖、原生 a11y 验收 | 本卡 UI + FEA-07 原生验收 |
| R-8 | P2 | 四 Fluent VM 拆分（`FluentPageViewModels.cs` 1373 行）、PNG 采证测试改 opt-in | 本卡技术债 |
| R-9 | P2 | `Nm.Elevation.*` 阴影样式（当前 1px 边框替代） | 设计/令牌冻结确认后补 |

## 验收标准

- [ ] **AC1 四页与 Shell residual 补齐**：R-1/R-2/R-3/R-4 中不依赖未就绪端口的 UI 部分先闭环；依赖端口的项在端口 Task done 后逐项闭环并登记证据。 `<<TODO>>`
- [ ] **AC2 组件与动效/A11y 全状态**：R-6/R-7 逐项登记（组件 × 状态 × 测试）。 `<<TODO>>`
- [ ] **AC3 设置与确认流**：R-5 中可在本卡实现的确认流/错误态闭环；备份字段随 FEA-13。 `<<TODO>>`
- [ ] **AC4 技术债**：R-8/R-9 完成或明确登记转后续。 `<<TODO>>`
- [ ] **AC5 证据与回归**：`verification/FEA-06-RESIDUAL-1/**` 日志/截图/组件表；全量不退化（届时基线）；两生成器 `--check`；治理 PASS。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/用户数据/生成物/冻结设计/组合根/`FrontendSelector`/Current V2；不 push；不扩大设计基线之外交互。
- 依赖端口未就绪的残项**不得**用模拟数据/假实现充数；应登记为 blocked 并等待对应 Task。

## 待 DSH 范围冻结事项

- 释放时机：FEA-07 完成（至少 memento/DPI/窗口验收）后，按端口就绪情况分批；首批可先做 R-2（UI 部分）/R-3（UI 部分）/R-6/R-7。
- 是否拆分多个子 Task（例如 UI-only 与 data-port 依赖分离）在 scope 复核时确定。
- 本卡 `base_commit`/`allowed_paths` 在释放时刷新。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests`（Avalonia.Headless） | .NET 9 | NOT_RUN | 待补 |
| AC5 | 全量 sln + `TokenGen/ThemeGen -- --check` + `check.ps1`/`verify_pins` | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Closeout Record

- 待关闭时填写。
