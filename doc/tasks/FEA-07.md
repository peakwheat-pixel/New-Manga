---
id: FEA-07
title: 运行期切换与窗口（双 UI 切换、WindowBroker、switch journal、安全启动）
kind: implementation
governance_version: 3
status: proposed
approval: pending_scope_review
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-00A-IMPL-1
  - FEA-04
  - FEA-05-PORT-1
  - FEA-06
base_commit: b26840acdf682d69cf531bec3161d17bf90cf9f4
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07
allowed_paths:
  - doc/tasks/FEA-07.md
  - apps/desktop-avalonia/src/NewManga.App/App.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/App.axaml
  - apps/desktop-avalonia/src/NewManga.App/Program.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/**
  - apps/desktop-avalonia/src/NewManga.App/Shell/**
  - apps/desktop-avalonia/src/NewManga.App/Services/**
  - apps/desktop-avalonia/src/NewManga.App/Controls/**
  - apps/desktop-avalonia/src/NewManga.App/Styles/**
  - apps/desktop-avalonia/src/NewManga.Appearance/**
  - apps/desktop-avalonia/src/NewManga.DesignSystem/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Appearance.Tests/**
  - verification/FEA-07/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-07-*.md
  - doc/handoffs/FEA-07-*.md
---

# FEA-07：运行期切换与窗口（双 UI）

## 来源与授权链

- **方案**：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §12.1 FEA-07（运行期切换/窗口）与 §7（切换事务、窗口、失败回退）、§15.6。
- **前置**：`FEA-06` **done**（集成 `b26840acd`；Fluent 四页 + 双壳 selector 就绪）；`FEA-04`（Current 适配）、`FEA-05-PORT-1`（Draft 端口）、`FEA-00A-IMPL-1`（数据安全门）均 done。
- **契约**：C-02（V-05/V-08b）、C-03（外观持久化/唯一写者，PREREQ-1/2 已交付）、C-05（页可见性）。
- **用户指派（承前）**：FEA 线实现 owner 在 FEA-06 起由 Codex 承接（2026-11-02）；FEA-07 具体 owner 由 DSH 在范围冻结时确认。

## 任务拆解（初稿，待 scope 复核细化）

| # | 内容 | 依据 |
|---|---|---|
| P1 | 运行期双 UI 切换：`FrontendSelector` + `AppearanceCoordinator.SaveAsync` 的切换事务，切前校验/切后回滚；不重启 sidecar、不丢 Draft/Run | 方案 §7.1 |
| P2 | Windows 窗口身份/生命周期：WindowBroker（主窗/弹窗/浮窗归属与复用）、关闭/重建不 Dispose Host、不隐式 Start | 方案 §7.3、FEA-04 R-STATE-4 |
| P3 | switch journal：切换步骤可恢复（崩溃/失败回退到上一 UI），无部分切换状态 | 方案 §7.1/§7.2 |
| P4 | 安全启动（safe startup）：坏包/坏设置/缺 frontend 时 fail-safe 到 Current V2 + 可诊断告知 | 方案 §7.2；PREREQ-2 selector fallback 基础 |
| P5 | 双屏/拔屏、DPI 变化、窗口位置/尺寸 memento（含 FEA-06 R-1 的 DPI 原生验收） | 设计 `04-layout-responsive.md` §4/§5、G-4 |
| P6 | 测试与证据：切换矩阵、失败矩阵、双屏/DPI 原生验收；全量回归 | 方案 §12.1 验收 |

## 验收标准（初稿）

- [ ] **AC1**：运行期双 UI 切换在 Draft/Run 进行中、Host 忙/断线、坏设置等场景下均可回退到上一可用 UI，无数据丢失/重复 Start。 `<<TODO>>`
- [ ] **AC2**：WindowBroker 主窗/弹窗/浮窗归属正确；关闭/重建不 Dispose Host、不隐式 Start。 `<<TODO>>`
- [ ] **AC3**：switch journal 崩溃恢复；无部分切换状态。 `<<TODO>>`
- [ ] **AC4**：safe startup fallback 可诊断（trace/用户可见提示）。 `<<TODO>>`
- [ ] **AC5**：双屏/拔屏/DPI memento 行为符合设计；原生桌面验收（非 headless 断言代替）。 `<<TODO>>`
- [ ] **AC6**：全量回归不退化（届时基线）+ 证据（日志/截图/矩阵表）。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/生成物/冻结设计；不替换 Current 视觉；不 push；不新增第五页/SpaceId。
- 双屏/DPI 的原生桌面验收不得用 headless 模拟替代（W-11 口径）。

## 测试要求

| 场景/AC | 计划命令/步骤 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC3 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests` + Host 故障注入 | .NET 9 / Avalonia.Headless | NOT_RUN | 待补 |
| AC5 | 原生双屏/DPI 手工矩阵 | Windows 11 原生桌面 | NOT_RUN | 待补 |
| AC6 | 全量 sln + 两 `--check` + `check.ps1`/`verify_pins` | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Closeout Record

- 待关闭时填写。
