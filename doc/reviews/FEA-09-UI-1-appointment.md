# FEA-09-UI-1 Appointment / Scope Freeze（DSH，2026-11-04）

状态：**RELEASE APPROVED — scope frozen；owner/reviewer 已指派；不 push**
Task：`doc/tasks/FEA-09-UI-1.md`（proposed → ready）
依据：用户 2026-11-04 指令（释放 FEA-09-UI-1，范围限定 ImportDock plan 预览/密码入口/进度/取消接线）；`doc/tasks/FEA-09-UI-1.md` scope 草案；FEA-09 closeout（AC-1…AC-10 MET、C-16 v1.1 冻结、Host 命令面已交付）。

## 1. 角色

| 角色 | Agent | 说明 |
|---|---|---|
| Owner（实现） | **ZCode**（新 headless 会话；Appointment 后认领 Task） | UI/UX 主责；只写 allowed_paths；不得自审 |
| Reviewer（独立实现 Review） | **Codex**（全新上下文会话，未参与本 Task 实现；不参与 FEA-09-UI-1 返修） | 只读 reviewed_head；报告原字节归档 `doc/reviews/` |
| Integrator / 裁决 | **DSH** | 范围冻结、Appointment、提交、门禁、集成、closeout |

## 2. Scope 冻结（最终）

**IN（只做最小接线，不扩展产品面）**
1. `ImportDockViewModel`/`ImportDockView`（V2 Library）消费 FEA-09 已冻结的 Host/Core 命令：`plan_import_references`、`start_import_references`、`get_import_receipt`、`cancel_import`、`resolve_page_resource`；真实 production adapter，不可 fake。
2. 密码入口：只经短期 `secret_ref`（Host `SourceSecretStore` 生成的 DPAPI token；FEA-09 冻结的 C-16 v1.1 §3 语义）；UI 不持久化、不写日志/快照/错误文案；取消/失败清理。
3. 运行中取消、重试不重复提交；按冻结提交单元展示已提交/未提交结果。
4. 逐项汇总：成功/失败/跳过/待处理与原因；AES ZIP 显示 typed unsupported。
5. 旧 managed 导入路径保持不变；不新增设计令牌/组件变体；可访问性沿用既有 V2 控件。
6. 仅补 V2 command adapter 缺口（payload pass-through），不新增/修改 Core/Host 契约、Schema、wire、授权、持久化。

**OUT（不得写）**
- Core/Host/Python/契约/Schema/wire/授权实现（FEA-09 写域）；C-05/C-15/C-16 任何字节。
- 其他页面/组件/设计基线（FEA-14 系列、设计基线 v1.1）。
- fake controller / 进程内替代真实 IPC 的“证据”。
- 真实用户数据/外部卷/AppData/回收站；push；`git` 提交（由 DSH 提交）。

## 3. 精确 allowed_paths（冻结；越界即停）

```text
doc/tasks/FEA-09-UI-1.md
doc/handoffs/FEA-09-UI-1-*.md
doc/reviews/FEA-09-UI-1-*.md
verification/FEA-09-UI-1/**
apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml
apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/ImportDockView.axaml.cs
apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs
apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
apps/desktop-avalonia/src/NewManga.App/Services/ImportExportContracts.cs
apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs（新文件；如需）
apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs（仅既有 source 命令 descriptor/minor 修正）
apps/desktop-avalonia/tests/NewManga.App.Tests/**
apps/desktop-avalonia/tests/NewManga.Host.Tests/**
```

- 共享组合根（`App.axaml`/`App.axaml.cs`/`NewManga.App.csproj`/`NewManga.sln`）仍仅 DSH 单点提交；实现者不得改。
- 不得修改 FEA-09/FEA-08 已 closeout 文件（含 `src/bootstrap/**`、`src/infrastructure/**`、`doc/tasks/FEA-09.md`、`doc/tasks/FEA-08.md`）。

## 4. AC（冻结；实现完成后逐项填 <<MET>>/PARTIAL）

- **AC-1**：plan 预览经真实 Host IPC 生成并可确认/取消；确认前源变化时 UI 呈现拒绝或更新预览，不静默提交。
- **AC-2**：密码重试路径经真实 IPC 走通（支持的加密子格式）；密码不出现在日志/快照/错误文案/证据；AES ZIP 显示 typed unsupported。
- **AC-3**：运行中取消可触发；已提交项保留、未提交项不出现；重试不重复提交；汇总计数与 receipt 一致。
- **AC-4**：隔离 fixture + production adapter 的真实 UI/IPC 可观察证据（非 fake/进程内替代）；证据含 UI 状态/原因/计数，存 `verification/FEA-09-UI-1/`。
- **AC-5**：不改变旧 managed 导入路径；旧 FEA-06 四 PNG hash 不变；无真实用户数据；全量测试不减少；未 push。

## 5. 验证门禁（实现者必跑并记录；DSH 复核）

```text
dotnet build apps/desktop-avalonia/NewManga.sln -c Release
dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build        # 基准：1300 passed / 0 failed
NEWMANGA_FEA09_IPC=1 NEWMANGA_BUILD_PYTHON=<python> dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests -c Release --no-build --filter "FullyQualifiedName~Fea09"
pwsh -NoProfile -File tools/governance/check.ps1
pwsh -NoProfile -File tools/governance/verify_pins.ps1                      # 17/17
git diff --name-only   # 对照 allowed_paths；禁止碰 C-05/C-15/C-16 冻结文件
```

- 证据：`verification/FEA-09-UI-1/`（含真实 IPC 输出/摘要；不含密码/绝对路径/用户数据）；Handoff `doc/handoffs/FEA-09-UI-1-<head>.md`。
- 完成定义：实现 + 测试 + Evidence + Handoff → Task `in_review` → **Codex 独立 Review**（新上下文）→ DSH 集成验证（重跑门禁 + 范围 diff）→ Task `done`。任一 P0/P1 返修后重新走 Review。
- 不 push；由 DSH 提交。

## 6. 交接注意

- 只消费 FEA-09 已交付命令面（C-16 v1.1 §0/§3/§4）；发现需要改契约/命令面 → **停**并写 Task「待裁决」交 DSH，不得自行扩围。
- 密码只经短期 secret_ref：UI 只能持有 token/path 的**元数据**用于交给 Host 命令，不得读明文文件、不得持久化；明文密码只存在于内存输入控件短暂生命周期。
- 运行中取消采用 FEA-09 `cancel_import`；不要引入新取消语义。
- 旧 `ImportPages` 路径保留并回归。
- 记录 command/payload/异常摘要，不记录密码、绝对源路径或用户数据。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-04 | 用户指令释放；DSH scope 冻结；owner=ZCode、reviewer=Codex（fresh）；精确 allowed_paths/AC/门禁；ready | 本文件；`doc/tasks/FEA-09-UI-1.md` |
