---
id: FEA-09-UI-1
title: 引用源导入最小 UI/适配接线（V2 ImportDock：plan 预览、密码、取消、进度）
kind: implementation
governance_version: 3
status: in_progress
approval: **RELEASE APPROVED（2026-11-04，DSH）**：scope 冻结 + Appointment——owner=ZCode（新 headless 会话）、reviewer=Codex（全新上下文）、base_commit `19a5894282`（释放 commit；Appointment base `19a71b396`）；范围/AC/门禁见 `doc/reviews/FEA-09-UI-1-appointment.md`
suggested_owner: zcode
owner: zcode（Appointment 2026-11-04；2026-11-04T00:38:20Z 认领；交付于 2026-11-04T01:05:00Z 置 in_review——工作树未提交，base `1a5894282` + 本卡变更清单，由 DSH 提交）
reviewer: codex（独立实现 Review r1 changes_requested：P0=0/P1=5/P2=2，`doc/reviews/FEA-09-UI-1-impl-r1.md`，reviewed_head `e40c0f74`；DSH 处置 `doc/reviews/FEA-09-UI-1-impl-r1-adjudication.md`；返修后需全新上下文 Codex 复审）
depends_on:
  - FEA-09-PREREQ-1
  - FEA-09
base_commit: 19a71b396eb177627f872d829c59dd7e440ebbbe
branch: main
worktree: G:\CODEX\New Manga
integration_commit: null
delivery_head: 工作树未提交（base `1a5894282`；变更见「变更记录」与 Handoff；由 DSH 提交后回填）
canonical_evidence_status: pending（工作树 SHA-256 已登记 Canonical Evidence 表；commit pin 待 DSH 提交后回填）
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

## Acceptance Criteria（scope 冻结；Owner 交付自评——待 Codex 独立 Review + DSH 集成验证）

- [x] **AC-1**：plan 预览经真实 Host IPC 生成并可确认/取消；确认前源变化时 UI 呈现拒绝或更新预览，不静默提交。 <<MET>>
- [x] **AC-2**：密码重试路径经真实 IPC 走通（支持的加密子格式），密码不出现在日志/快照/错误文案/证据；AES ZIP 显示 typed unsupported。 <<MET>>
- [x] **AC-3**：运行中取消可触发；已提交项目保留、未提交不出现；重试不重复提交；汇总计数与 FEA-09 receipt 一致。 <<MET>>
- [x] **AC-4**：以隔离 fixture + 真实 production adapter 断言 UI 可观察结果（非 fake controller、非进程内替代）；证据含 UI 状态/原因/计数。 <<MET>>
- [x] **AC-5**：不改变旧 managed 导入路径行为；旧 FEA-06 四 PNG 不变；无真实用户数据；全量测试不减少；未 push。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`。`apps/desktop-avalonia/src/NewManga.App/Services/` 仅在 FEA-09 冻结的命令适配所需文件内改动（实施时由 DSH 指定精确文件，不与 FEA-09 重叠写）。共享组合根（`App.axaml`/`App.axaml.cs`/`NewManga.App.csproj`/`NewManga.sln`）仍仅 DSH 单点提交。

## 禁止范围

Core/Host 契约与实现、Schema、授权、wire、持久化；其它页面；设计基线；真实用户数据/外部卷/回收站；以 fake/进程内证据替代真实 IPC/UI；push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC-1…AC-4 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test … -c Release --no-build`；`NEWMANGA_FEA09_IPC=1 NEWMANGA_BUILD_PYTHON=<python> dotnet test tests/NewManga.Host.Tests -c Release --no-build --filter "FullyQualifiedName~Fea09UiImportIpcTests"`；headless：`--filter "FullyQualifiedName~ReferencedImportUiTests"` | 主工作树；隔离 fixture（workspace `FEA-09-UI-1/ipc-*` + 冻结 FEA-09 fixture）；不碰真实 AppData | build **0/0**；全量 **1313/0/63**；真实 IPC **5/5**；VM **13/13** | `verification/FEA-09-UI-1/logs/gates.json`、`ipc/ui-import-ipc.json`、`ipc/ui-import-ipc.wire.ndjson`、`AC-MATRIX.md` |
| AC-5 | 同全量基准（Appointment 1300/0）；旧四 PNG hash 对照；`git diff --name-only` 对照 allowed_paths；`verify_pins` 17/17；`check.ps1` | 同上 | 1313/0（≥基准）；PNG **4/4 UNCHANGED**；diff 全部 allowed_paths 内；pins **17/17**；check **FAIL 1 error**（READY DAG 滞后，PLAN 同步属 DSH 集成步骤；3 既有 warning） | 同上 |

## 依赖、风险与阻塞

- `depends_on`：FEA-09-PREREQ-1（契约）、FEA-09（Core/Host 命令）。二者为已登记 Task；本卡在 FEA-09 交付前只可做只读准备，不得实施。
- 风险：①FEA-09 命令面未冻结前接线会返工；②UI 证据易被 fake/进程内测试冒充——必须真实 production adapter；③密码输入与日志安全需独立负测；④与 FEA-09 写域重叠（App/Services）必须由 DSH 指定单一写者。
- 阻塞解除：FEA-09 scope-r2 approved + PREREQ-1 done 后本卡提交 scope review。

## Canonical Evidence

（工作树 SHA-256；commit 列由 DSH 提交后回填——实现者不得自提交）

| evidence_id | 证据说明 | 仓库路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-001 | 逐 AC 证据矩阵（AC-1…AC-5 MET + 限制） | `verification/FEA-09-UI-1/AC-MATRIX.md` | pending | `1127d7d2122641840ccf8808cd537ea7017b45880528738bd310c81bb9fb9121` | CANONICAL |
| EV-002 | 真实 IPC 案例摘要（plan/AES/密码重试/取消 + 密码审计） | `verification/FEA-09-UI-1/ipc/ui-import-ipc.json` | pending | `8417a47893f8008e1883e8d379d3f5a044f71dfe12634ff8a214c6fc60bd99d0` | CANONICAL |
| EV-003 | 真实 IPC wire 记录（路径脱敏、密码 0 命中） | `verification/FEA-09-UI-1/ipc/ui-import-ipc.wire.ndjson` | pending | `1c657d52a099762f71c3da9316f5c4f7c1d672cff025fa1d849d30ec91aae4dd` | CANONICAL |
| EV-004 | Owner 门禁结果（build/test/真实 IPC/check/pins/diff/PNG） | `verification/FEA-09-UI-1/logs/gates.json` | pending | `3a4a15209475ff923dd8d6eb53877e5deb24773524712d7bcd0865ddda888bba` | CANONICAL |
| EV-005 | Owner Handoff（变更清单/命令/结果/风险） | `doc/handoffs/FEA-09-UI-1-1a5894282.md` | pending | `b7a7a25d92712a71d316fab5fc0bf4194d057da71e54560ea2b3bec10edf2845` | CANONICAL |
| EV-006 | DSH 集成验证结果（build/全量/真实 IPC/C-07/pins） | `verification/FEA-09-UI-1/logs/dsh-integration.json` | pending | `9415f574712a205ccea2207fe9c53f1b7441207e6ee02e0a992be9782c9c675f` | CANONICAL |
| EV-007 | DSH 集成范围 diff（工作树路径清单） | `verification/FEA-09-UI-1/logs/dsh-scope-diff.txt` | pending | `c181ed057e4d592f1e19806ffafa98cfd10dad64d04a279eb4c0665f98ce98c8` | CANONICAL |


## Closeout Record

- Owner 交付（2026-11-04，ZCode）：实现 + 测试 + 证据 + Handoff；Task `in_review`。
- DSH 复核返修（2026-11-04）：撤回 `IHostController` 新增，改独立 `ISourceImportController`；`generate_api_inventory.py --check` PASS（C-07 冻结清单不变，无需 UNFREEZE）。
- DSH 集成验证：build 0/0；全量 .NET 1313/0/63；真实 IPC 5/5；pins 17/17；范围 diff 合规（DSH 集成文件 PLAN/STATUS/TASK_LEDGER 除外）；FEA-09 canonical 证据复跑污染已恢复。
- 未提交：工作树；未 push；由 DSH 提交后回填 commit 列。
- 已知事项：见 AC-MATRIX「限制」（FEA-09 canonical 证据可被常规测试复跑重写的债务候选；folder 逐文件 grant 接线限制）。

## 变更记录

| 日期 | 变更 | 依据 |
|---|---|---|
| 2026-11-03 | 建立 scope 草案（proposed）：最小 UI/适配接线，作为 FEA-09 的 UI 证据协同切片 | `doc/reviews/FEA-09-scope-r1.md` R1-005；提案 `:1040`；现有 ImportDock 现状 |
| 2026-11-04 | ZCode 认领（in_progress）；实现交付（工作树）：新增 `Services/SourceImportModels.cs`（UI 模型+payload+`SourceImportCoordinator` 生产编排：register→issue→plan / 密码 DPAPI secret_ref→重签 Secret-G→重 plan→start / receipt 轮询+终态清理 / cancel）；`IHostController`+`HostController`+`NullHostController` 增 4 方法（Plan/Start/GetReceipt/Cancel，typed 不抛）；`ImportDockViewModel`+`ImportDockView.axaml` 引用导入面（plan 预览/密码框/确认/取消/重试/进度，旧路径零改动）；`FakeHostController` 补 scripted 面；Host.Tests 引用 App；新测试 `ReferencedImportUiTests`（13）+`Fea09UiImportIpcTests`（5，真实 stdio）；证据 4 件。**HostCommandDispatcher/Registry 零改动**（source 命令 pass-through 已由 FEA-09 交付，核实无缺口）。Task → in_review | 本卡 Appointment；`verification/FEA-09-UI-1/**`；Handoff |
| 2026-11-04 | **DSH 复核返修 r1**：IHostController 改动撤回 → 独立 `ISourceImportController`；`generate_api_inventory.py --check` PASS（C-07 冻结面未变）；DSH 复跑 build 0/0、全量 1313/0/63、真实 IPC 5/5、pins 17/17；证据补 DSH 集成日志/范围 diff | DSH 集成；`doc/reviews/FEA-09-UI-1-appointment.md` |

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
## 返修 r1（2026-11-04，DSH 复核 / ZCode 执行）

- **触发**：Owner 首版把 4 个方法加进 `IHostController` → `tools/generate_api_inventory.py --check` FAIL（C-07 FROZEN 清单 54 方法基线被改），需要 C-07 UNFREEZE，超出本 Task 授权。
- **返修**：改为**独立接口** `ISourceImportController`（`Services/SourceImportModels.cs`；4 个 typed 方法），`HostController`/`NullHostController`/测试 fake 同时实现；`ImportDockViewModel` 通过 `controller as ISourceImportController` 能力探测（缺失=typed unavailable，旧 managed 路径不变）；`IHostController.cs` 恢复 HEAD 原字节。
- **结果**：`python tools/generate_api_inventory.py --check` **PASS**（C-07 冻结面未变）；build 0/0；全量 .NET/真实 IPC/门禁结果见 `verification/FEA-09-UI-1/logs/dsh-integration.log`。
- **C-07 待办撤销**：不再需要 UNFREEZE 载体；本 Task 未改任何冻结契约字节。
- 文档同步：Handoff / AC-MATRIX 中“IHostController +4 / C-07 UNFREEZE”描述作废，以本节为准。
## Implementation Review r1 处置（DSH，2026-11-04）

| ID | 级别 | DSH 处置 | 状态 |
|---|---|---|---|
| R1 | P1 | 接受：token 创建即登记清理上下文；所有未 accepted 出口统一 Delete+Revoke；补失败负测 | 返修中 |
| R2 | P1 | 接受：receipt 暂时失败保持运行中状态，可恢复轮询/取消；终态才释放 | 返修中 |
| R3 | P1 | 接受 + **DSH 接缝裁决**：folder 交 Host `IssueAsync` 枚举（App 不递归/排序/授权）；最小改动不可行则入口 typed unavailable 并如实登记 | 返修中 |
| R4 | P1 | 接受：补真实 `HostController`+`ImportDockViewModel`→IPC 闭环（普通/AES/单加密源重试/取消守恒/源变化拒绝） | 返修中 |
| R5 | P1 | 接受：>1 加密源 App 层 typed 拒绝，逐源独立确认/token；不扩 Core wire | 返修中 |
| R6 | P2 | 接受：绑定并显示每项 CountsText；补测试 | 返修中 |
| R7 | P2 | 接受：分别显示 skipped_pages/skipped_sources；补整源跳过测试 | 返修中 |
