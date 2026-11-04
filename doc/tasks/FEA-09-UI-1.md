---
id: FEA-09-UI-1
title: 引用源导入最小 UI/适配接线（V2 ImportDock：plan 预览、密码、取消、进度）
kind: implementation
governance_version: 3
status: ready
approval: **RELEASE APPROVED（2026-11-04，DSH）**：scope 冻结 + Appointment——owner=ZCode（新 headless 会话）、reviewer=Codex（全新上下文）、base_commit `19a71b396eb177627f872d829c59dd7e440ebbbe`；范围/AC/门禁见 `doc/reviews/FEA-09-UI-1-appointment.md`
suggested_owner: zcode
owner: zcode（Appointment 2026-11-04；认领后置 in_progress）
reviewer: codex（独立实现 Review 会话；未参与本 Task 实现/返修）
depends_on:
  - FEA-09-PREREQ-1
  - FEA-09
base_commit: 19a71b396eb177627f872d829c59dd7e440ebbbe
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 未开始
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-09-UI-1
allowed_paths:
  - doc/tasks/FEA-09-UI-1.md
  - doc/handoffs/FEA-09-UI-1-*.md
  - doc/reviews/FEA-09-UI-1-*.md
  - verification/FEA-09-UI-1/**
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/**
out_of_scope:
  - Core/Host 契约、wire、持久化与授权实现（FEA-09 / FEA-09-PREREQ-1 写域）
  - 其它页面/组件/设计基线与 Fluent 视觉重设计（FEA-14 系列/设计基线 v1.1）
  - 真实用户数据/真实外部卷/真实取消/回收站
  - 以 fake controller 或进程内断言冒充真实 IPC/UI 证据
  - push
---

# FEA-09-UI-1：引用源导入最小 UI/适配接线

> 来源：`doc/reviews/FEA-09-scope-r1.md` §2.3/R1-005（提案 `:1040` 要求「每项用隔离数据断言 Core→Host→UI 结果」；现有 V2 `ImportDock` 只有旧 `ImportPages` 路径、无密码/plan 确认/运行中取消入口；`ImportExportUiTests` 使用 fake controller 不能作为真实 IPC 证据）。本 Task 是 FEA-09 的**协同交付**切片，不替 FEA-09 决定 Core/Host 语义。
> 本卡为 scope 草案（`proposed`），实施前须由 DSH 复审冻结；不得先写代码。

## 来源与目标

- FEA-09 交付 Core/Host 的引用源读取、导入 plan/receipt、授权与取消语义；本 Task 只做**最小 UI/适配接线**：让真实 V2 用户路径可达并产出可观察证据。
- 目标：在现有 `ImportDock`（V2 Library）上接线——导入预览（plan）确认、加密项目密码输入（短期安全引用）、运行中取消、逐项进度与成功/失败/跳过汇总；消费 FEA-09 冻结的命令面，不新增业务真值。
- 约束：Avalonia UI 不直接访问数据库、任意 OS 路径或模型；只经 Host/IPC adapter；不改变 Current V2 既有行为（旧 `ImportPages` 路径保留）。

## 范围（草案）

1. `ImportDockViewModel`/`ImportDockView` 接线 FEA-09 的 plan/receipt/取消/进度命令（真实 Host 命令，不经 fake controller）。
2. 密码输入：仅经短期安全引用传递；UI 不持久化、不写日志、不出现在错误文案；取消/失败清理引用。
3. 取消与重试：运行中取消入口；已提交/未提交结果按 FEA-09 冻结的提交单元展示；重试不重复提交。
4. 汇总：按当前项目显示进度与成功/失败/跳过/待处理逐项原因；不支持/损坏/加密（含 AES ZIP typed unsupported）逐项可读。
5. 可访问性/键盘：新交互沿用既有 V2 控件与 Fluent 语义，不新增设计令牌/组件变体；超出即停等 DSH 裁决（设计基线 v1.1 或 OUT）。

## Acceptance Criteria（草案，scope review 冻结）

- [ ] **AC-1**：plan 预览经真实 Host IPC 生成并可确认/取消；确认前源变化时 UI 呈现拒绝或更新预览，不静默提交。
- [ ] **AC-2**：密码重试路径经真实 IPC 走通（支持的加密子格式），密码不出现在日志/快照/错误文案/证据；AES ZIP 显示 typed unsupported。
- [ ] **AC-3**：运行中取消可触发；已提交项目保留、未提交不出现；重试不重复提交；汇总计数与 FEA-09 receipt 一致。
- [ ] **AC-4**：以隔离 fixture + 真实 production adapter 断言 UI 可观察结果（非 fake controller、非进程内替代）；证据含 UI 状态/原因/计数。
- [ ] **AC-5**：不改变旧 managed 导入路径行为；旧 FEA-06 四 PNG 不变；无真实用户数据；全量测试不减少；未 push。

## 允许修改范围

见 frontmatter `allowed_paths`。`apps/desktop-avalonia/src/NewManga.App/Services/` 仅在 FEA-09 冻结的命令适配所需文件内改动（实施时由 DSH 指定精确文件，不与 FEA-09 重叠写）。共享组合根（`App.axaml`/`App.axaml.cs`/`NewManga.App.csproj`/`NewManga.sln`）仍仅 DSH 单点提交。

## 禁止范围

Core/Host 契约与实现、Schema、授权、wire、持久化；其它页面；设计基线；真实用户数据/外部卷/回收站；以 fake/进程内证据替代真实 IPC/UI；push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-1…AC-4 | 计划：`dotnet build apps\desktop-avalonia\NewManga.sln --nologo`；`dotnet test ... --settings ...runsettings`；headless UI 场景脚本（待 scope 冻结登记精确命令） | 主工作树；隔离 fixture；不碰真实 AppData | NOT_RUN（planned） | `verification/FEA-09-UI-1/` |
| AC-5 | 同全量基准 1292/0/57；旧四 PNG hash 对照；`git diff --name-only` 对照 allowed_paths | 同上 | NOT_RUN（planned） | 同上 |

## 依赖、风险与阻塞

- `depends_on`：FEA-09-PREREQ-1（契约）、FEA-09（Core/Host 命令）。二者为已登记 Task；本卡在 FEA-09 交付前只可做只读准备，不得实施。
- 风险：①FEA-09 命令面未冻结前接线会返工；②UI 证据易被 fake/进程内测试冒充——必须真实 production adapter；③密码输入与日志安全需独立负测；④与 FEA-09 写域重叠（App/Services）必须由 DSH 指定单一写者。
- 阻塞解除：FEA-09 scope-r2 approved + PREREQ-1 done 后本卡提交 scope review。

## Closeout Record

- 未开始（proposed 草案）。

## 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立 scope 草案（proposed）：最小 UI/适配接线，作为 FEA-09 的 UI 证据协同切片 | `doc/reviews/FEA-09-scope-r1.md` R1-005；提案 `:1040`；现有 ImportDock 现状 |
## Release / Appointment（2026-11-04，DSH）

- 用户指令释放本 Task；范围冻结与 Appointment 见 `doc/reviews/FEA-09-UI-1-appointment.md`。
- Owner：**ZCode**（新 headless 会话；认领后 Task → `in_progress`）；Reviewer：**Codex**（全新上下文，实现完成后独立 Review）；DSH Integrator。
- base_commit：`19a71b396eb177627f872d829c59dd7e440ebbbe`。
- 精确 allowed_paths 已冻结（见 frontmatter）：仅 App 层 ImportDock/Services、CoreClient command adapter 既有 source 命令 pass-through、App/Host 测试、本 Task 文档与 evidence。
- AC-1…AC-5 冻结；验证门禁：`dotnet build`、`dotnet test`（基准 1300/0）、真实 IPC（`NEWMANGA_FEA09_IPC=1`）、`check.ps1`、`verify_pins.ps1`（17/17）、范围 diff；证据 `verification/FEA-09-UI-1/`。
- 禁止：改 C-05/C-15/C-16 冻结字节、改 FEA-08/FEA-09 closeout 文件、fake/进程内冒充真实 IPC、push。发现需扩围 → 停并写「待裁决」交 DSH。
- 完成路径：实现 + 测试 + Evidence + Handoff → `in_review` → Codex 独立 Review → DSH 集成验证 → `done`。
