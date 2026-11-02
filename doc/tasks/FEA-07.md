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
base_commit: 682fe17ae94ddce5740aa0a2a4a74bde19057024
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
  - apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Appearance.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**
  - apps/desktop-avalonia/NewManga.sln
  - apps/desktop-avalonia/Directory.Build.props
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
- **顺序裁决（用户 2026-11-02）**：用户指示「按原来的顺序进行」→ 按 PLAN DAG 先做 FEA-07，**不插队** `FEA-06-RESIDUAL-1` 的 UI 打磨。
- **H2/H3 假设**：方案 §12.1 将 H2（稳定 Window + 内容替换承接双屏 Inspector）、H3（热切换性能/比例范围）列为 FEA-07 前置；当前无独立验证 Task → **H2/H3 的验证纳入本卡 AC5/AC7**（合成数据真机矩阵 + 性能 baseline），不单独拆前置。

## 任务拆解（初稿，待 scope 复核细化）

| # | 内容 | 依据 |
|---|---|---|
| P1 | 运行期双 UI 切换：`FrontendSelector` + `AppearanceCoordinator.SaveAsync` 的切换事务，切前校验/切后回滚；不重启 sidecar、不丢 Draft/Run | 方案 §7.1 |
| P2 | Windows 窗口身份/生命周期：WindowBroker（主窗/弹窗/浮窗归属与复用）、关闭/重建不 Dispose Host、不隐式 Start | 方案 §7.3、FEA-04 R-STATE-4 |
| P3 | switch journal：切换步骤可恢复（崩溃/失败回退到上一 UI），无部分切换状态 | 方案 §7.1/§7.2 |
| P4 | 安全启动（safe startup）：坏包/坏设置/缺 frontend 时 fail-safe 到 Current V2 + 可诊断告知 | 方案 §7.2；PREREQ-2 selector fallback 基础 |
| P5 | 双屏/拔屏、DPI 变化、窗口位置/尺寸 memento（含 FEA-06 R-1 的 DPI 原生验收） | 设计 `04-layout-responsive.md` §4/§5、G-4 |
| P6 | H2/H3 验证：稳定 Window/双屏 Inspector 承接、热切换性能 baseline（p50/p95/峰值、最大 UI 冻结时长、内存/句柄） | 方案 §15.x H2/H3、§12.3 A08 |
| P7 | 测试与证据：切换矩阵/失败矩阵/性能报告/双屏与 DPI 原生验收；全量回归 | 方案 §12.1/§12.3 |

## 验收标准

- [ ] **AC1（A01/A02/A03/A05）**：Current↔Fluent 往返 100 次（含草稿/Reader/Run）：同一个 Host/sidecar、相同 Session/Draft/Run/Intent，原生主窗标识不变；未失焦 IME/文本输入不丢不误提交；旧结果仅 candidate；ACK 丢失/重连后同 Intent 不双启动；失败保留旧 UI 与未保存状态。 `<<TODO>>`
- [ ] **AC2**：WindowBroker 主窗/弹窗/浮窗归属正确；关闭/重建不 Dispose Host、不隐式 Start；退出协调归进程级 ExitCoordinator。 `<<TODO>>`
- [ ] **AC3（A06）**：switch journal 崩溃恢复；暂停/进程中断后无部分切换状态、未完成步骤可追溯、interrupted 不自动执行。 `<<TODO>>`
- [ ] **AC4**：safe startup fallback 可诊断（trace/用户可见提示）；坏设置/坏包/缺 frontend 均 fail-safe 到 Current V2。 `<<TODO>>`
- [ ] **AC5（A08/H2）**：双屏/拔屏/DPI 100–200%/换主屏矩阵：主窗+Inspector 浮窗归属与可见可操作、不丢屏外、目标不支持浮动则安全停靠、快捷键不重复执行；原生桌面验收（不得以 headless 断言代替）。 `<<TODO>>`
- [ ] **AC6（H3）**：热切换性能 baseline 报告（p50/p95/峰值、最大 UI 冻结时长、内存/句柄变化）；候选预算 p95 ≤1s（DSH 冻结门槛后验收，超预算需登记处置）。 `<<TODO>>`
- [ ] **AC7**：全量回归不退化（届时基线，当前 1034/0/57）+ 证据（日志/截图/矩阵表/性能报告）。 `<<TODO>>`

## 禁止范围

- 不改 Core/契约/schema/生成物/冻结设计；不替换 Current 视觉；不 push；不新增第五页/SpaceId；不引入第三 UI。
- 双屏/DPI 的原生桌面验收不得用 headless 模拟替代（W-11 口径）。
- 测试夹具只用**合成数据**、Unicode 路径、重复页与故障注入；**不得使用真实漫画或真实 `%APPDATA%`**；不触真实用户数据。

## 附加裁决点（DSH 已裁/待裁）

| # | 问题 | 裁决 | 依据 |
|---|---|---|---|
| W-1 | 本卡写域边界 | 只做「运行期切换 UI 内容树 + 窗口/启动安全」；`FrontendSelector` 语义与 `AppearanceCoordinator` 唯一写者不改（PREREQ-2 冻结）；`App.axaml.cs`/`Program.cs` 用于切换装配，须保持 V2/legacy 行为不退化 | FEA-06-PREREQ-2/scope-r2 |
| W-2 | 原生验收口径 | 双屏/DPI 以原生桌面矩阵为证据；headless 仅作回归，不替代原生验收 | 方案 §12.3；FEA-06 W-11 |
| W-3 | owner 指派 | 范围冻结后由 DSH 指定（Codex 通道已验证可用；Codex 2026-11-02 起承接 FEA 实现） | 用户 2026-11-02 |
| W-4 | H2/H3 归属 | 无独立 Task → 验证纳入本卡 AC5/AC6，不拆前置 | 方案 §12.1 |
| W-5 | 性能门槛 | p95 ≤1s 为候选预算，最终门槛由 DSH 在范围冻结时确认；记录机器/规模/冷热/峰值 | 方案 §12.3 |
| W-6 | Presentation.Avalonia 模块落点 | 方案 §12.1 要求 `Presentation.Avalonia`；本卡可在写域内新建 `NewManga.Presentation.Avalonia` 项目并登记 sln/`Directory.Build.props`。**依赖方向不变**：Presentation 可引用 ApplicationCore/Appearance/DesignSystem，**不得**让 Host/Core/ApplicationCore 引用 Presentation/UI；不改既有项目 TFM/依赖方向 | 方案 §3/§4、§12.1；AD-002 |

## 测试要求

| 场景/AC | 计划命令/步骤 | 前提 | 实际 | 证据 |
|---|---|---|---|---|
| AC1–AC4 | `dotnet test apps\desktop-avalonia\tests\NewManga.App.Tests`（切换/恢复/失败矩阵，合成数据 + 故障注入） | .NET 9 / Avalonia.Headless + Host（`NEWMANGA_CORECLIENT_SIDECAR_DIR`） | NOT_RUN | 待补 |
| AC5 | 原生双屏/拔屏/DPI 矩阵（100/150/200%、换主屏、拔副屏） | Windows 11 原生桌面；隔离 `--data-root`/`--theme-home` | NOT_RUN | 待补 |
| AC6 | 热切换性能 baseline（p50/p95/峰值、冻结时长、内存/句柄） | 固定机器 + 合成规模数据 | NOT_RUN | 待补 |
| AC7 | 全量 sln + 两 `--check` + `check.ps1`/`verify_pins` | 全量 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Closeout Record

- 待关闭时填写。
