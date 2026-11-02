---
id: FEA-06-RESIDUAL-1
title: Fluent 四页规格补齐（FEA-06 AC1–AC7 residual）
kind: implementation
governance_version: 3
status: ready
approval: scope_review_r1_pending_2026-11-02（DSH 释放第一批范围冻结 v1；FEA-06 residual 转入）
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
base_commit: 82529a3d5864a39f362e414b67bca774d743f862（FEA-07 closeout head；2026-11-02 释放时刷新）
branch: main
worktree: G:\CODEX\New Manga
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
- **Owner**：Codex（沿用用户 2026-11-02 指派；scope 冻结后按 W-10 派发）。`n- **顺序**：用户 2026-11-02 裁决「按原来的顺序进行」→ 本卡不插队，FEA-07 优先；本卡按端口就绪分批释放。

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

## 释放范围（第一批 v1，2026-11-02 DSH 冻结，待 scope-r1 独立复核）

- **范围原则**：只释放不依赖未落地端口、且不触碰冻结设计/契约/Core/生成物的 UI 与技术债项；端口依赖项与原生 D-1 项保持 blocked，不用模拟数据/假实现充数。
- **本批 IN（可实施）**：
  - R-1a：Fluent 页面级 UI memento 恢复（折叠/滚动等页面状态；不改变 FEA-07 窗口状态语义）。
  - R-1b：Library/Workbench 列表-详情分栏折叠（符合 `doc/design/fluent-v1/` 冻结基线）。
  - R-5a：设置页「离开未保存确认 + Esc」（复用 FEA-07 退出保护与 confirmed-draft 语义，不新增端口）。
  - R-6：组件 full 状态（normal/hover/pressed/disabled/浮层开关）逐项补齐，登记「组件×状态×测试」矩阵。
  - R-7：焦点环 + 三类 motion 状态（headless 可验证部分；原生 a11y 验收 blocked）。
  - R-8：四 Fluent VM 拆分（`FluentPageViewModels.cs` 1373 行 → 四页各自 VM 文件；纯重构，行为等价，既有测试不改弱）。
- **本批 OUT（blocked，登记不实施）**：R-2（回收站/扫描/满态统计，依赖 FEA-12/10 端口）、R-3（Run/BatchMatrix，依赖 FEA-10）、R-4（阅读器数据面，依赖 FEA-09/11）、R-5b 备份字段（依赖 FEA-13）、R-7 原生 a11y 验收、R-1c 与全部 200% DPI/原生桌面验收（D-1 无硬件）、R-9 `Nm.Elevation.*` 阴影（设计/令牌冻结确认缺失前 blocked）。
- **AC 映射**：AC1–AC5 编号不改；IN 项在对应 AC 下逐项登记证据，OUT 项在该 AC 下以 `BLOCKED` 记录原因，不用假实现。
- **交付物**：代码 + 测试 + `verification/FEA-06-RESIDUAL-1/`（日志、组件状态矩阵、全量回归、生成器/治理）+ Handoff。
- **约束**：不改 Core/契约/schema/用户数据/生成物/冻结设计/组合根/`FrontendSelector`/Current V2；不 push；测试临时根；R-8 为行为等价重构，必须既有测试全绿。
- **拆分**：本批不拆子 Task；OUT 项待对应端口 Task done 后由 DSH 再冻结第二批。


## 验收标准

- [ ] **AC1 四页与 Shell residual 补齐**：R-1/R-2/R-3/R-4 中不依赖未就绪端口的 UI 部分先闭环；依赖端口的项在端口 Task done 后逐项闭环并登记证据。 `<<TODO>>`
- [ ] **AC2 组件与动效/A11y 全状态**：R-6/R-7 逐项登记（组件 × 状态 × 测试）。 `<<TODO>>`
- [ ] **AC3 设置与确认流**：R-5 中可在本卡实现的确认流/错误态闭环；备份字段随 FEA-13。 `<<TODO>>`
- [ ] **AC4 技术债**：R-8/R-9 完成或明确登记转后续。 `<<TODO>>`
- [ ] **AC5 证据与回归**：`verification/FEA-06-RESIDUAL-1/**` 日志/截图/组件表；全量不退化（届时基线）；两生成器 `--check`；治理 PASS。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/用户数据/生成物/冻结设计/组合根/`FrontendSelector`/Current V2；不 push；不扩大设计基线之外交互。
- 依赖端口未就绪的残项**不得**用模拟数据/假实现充数；应登记为 blocked 并等待对应 Task。

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
