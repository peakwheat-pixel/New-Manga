---
id: FEA-12-UI-RESIDUAL-1
title: FEA-12-UI 残余 P3 收尾（delete-time capability 防御边 / preview BOOK_NOT_FOUND 刷新 / cleanup retry 提示 / 只读与能力缺失文案）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-12-UI-RESIDUAL-1-scope-r1.md`（fresh subagent `bfb8f132…`，verdict **READY-TO-FREEZE**）；DSH 2026-11-06 裁决（见「Scope Review 裁决」）：接受 **App-only** 范围与四个冻结口径（① defensive invariant only；③ 含最小 `_notify` 修复；④ 双原因文案规则；写域仅 `TrashViewModel.cs` + `TrashUiTests.cs`）；释放为 ready、base `690c77eb0`、Owner=`ui-residual-impl`（DSH Agent Teams）
suggested_owner: zcode
owner: ui-residual-impl
reviewer: 独立上下文 fresh subagent（r1 待指派；不得由实现会话/实例自审；报告须记录 reviewer 与 session）
depends_on:
  - FEA-12-UI
base_commit: 690c77eb0
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-UI-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-12-UI-RESIDUAL-1.md
  - doc/reviews/FEA-12-UI-RESIDUAL-1-*.md
  - doc/handoffs/FEA-12-UI-RESIDUAL-1-*.md
  - verification/FEA-12-UI-RESIDUAL-1/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs
out_of_scope:
  - Host/Core 能力门与可达性（`NewManga.CoreClient/**`、`NewManga.Host/**`、delete-permanently 能力门）→ 另卡
  - `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`/`TrashModels.cs`/`FakeHostController.cs`/`LibraryViewModel.cs`/`HostController.cs`/`NullHostController.cs`
  - `RecycleBinView.axaml(.cs)`、XAML 结构/令牌；`NewManga.DesignSystem/**`；`src/**`（Python）
  - 契约/schema/迁移/依赖/wire/命令集/capability/18 pins；FEA-12-UI 历史 AC 字节
  - 真实用户数据/AppData/外部卷/真实回收站/原文件删除；push；L3/L4 真机走查
---

# FEA-12-UI-RESIDUAL-1：FEA-12-UI 残余 P3 收尾（App-only）

> **状态：`ready`（scope 已冻结；Owner=`ui-residual-impl`；base `690c77eb0`）。**
> 来源：`FEA-12-UI` closeout（`doc/tasks/FEA-12-UI.md`，`a46d4d5c7`）P3 follow-up ①–④；独立 scope review：`doc/reviews/FEA-12-UI-RESIDUAL-1-scope-r1.md`（**READY-TO-FREEZE**）。
> **本卡只做 App 侧（`TrashViewModel.cs` + `TrashUiTests.cs`）四项行为/文案/测试收口**；不改 Host/Core/契约/wire/schema/依赖；**不回填** FEA-12-UI 历史 AC；L3/L4 仍 `NOT_RUN`。

## Scope Review 裁决（DSH，2026-11-06）

| 争议点 | Review 建议 | **DSH 裁决** |
|---|---|---|
| ① delete-time `CORE_CAPABILITY_MISSING` | 只做 defensive invariant；生产不可达；不得加 Host 能力门 | **接受**：只钉住「删除返回能力缺失不得污染页级 read 能力态」；卡/Handoff 明写 defensive invariant only（L-R1）；不宣称修复用户可见 bug |
| ③ cleanup retry `BOOK_NOT_FOUND` | 分支存在但提示被 `ResetPreview` 清空且无 `_notify` → 需最小修复，非纯测试 | **接受**：包含最小 `_notify` + 状态复位修复（I-3），不是纯测试卡 |
| ④ 只读/能力缺口文案 | 冻结「两个独立事实同时展示；只读文案不得声称可浏览」规则 | **接受**：`ShowHostReadOnlyBanner` 仅由 `_hostReadOnly` 决定；组合态两条 banner 同时可见；只读文案移除“可浏览”（L-R5/L-R7） |
| ① 生产可达 / delete 能力门 | 另卡；不得塞进本卡 | **接受**：Out（O-1）；需要时另卡并重新 scope review |
| 写域 | 仅 `TrashViewModel.cs` + `TrashUiTests.cs` | **接受**：其余路径不改；实现需扩域必须先停下报 DSH |
| 契约影响 | 零契约/wire/schema/依赖/pins | **接受**：C-07/`IHostController` 不变；API inventory 应 PASS |

## Scope（冻结）

### In

| # | 冻结项 | 文件/类/方法 | 必须行为 | AC |
|---|---|---|---|---|
| **I-1** | delete-time capability 防御边 | `TrashViewModel.ConfirmDeleteAsync` 的 `TrashDeleteOutcome.CapabilityMissing` 分支 | 不设页级 `_capabilityMissing/_capabilityMessage`；列表保持可见；结果面板 typed `CORE_CAPABILITY_MISSING`；`CanConfirmDelete=false`；不伪造成功；不重新 probe 推断能力 | AC-R1 |
| **I-2** | preview `BOOK_NOT_FOUND` 自动刷新 | `TrashViewModel.BeginPermanentDeleteAsync` preview 失败块 | `BOOK_NOT_FOUND` → `_notify` + 关闭面板 + `await ReloadAsync`；零 delete 帧、零自动重试；其他失败码保持旧行为 | AC-R2 |
| **I-3** | cleanup retry `BOOK_NOT_FOUND` 提示（含最小修复） | `TrashViewModel.RetryCleanupAsync` NotFound 分支 | 同一 digest 重试；NotFound 时 `_notify` 用户可见「已不存在/已刷新」；`ReloadAsync`；`IsCleanupPending=false`、`CanRetryCleanup=false`、面板关闭；不伪报完成 | AC-R3 |
| **I-4** | 只读/能力缺口双原因文案 | `TrashViewModel.ShowHostReadOnlyBanner`、`HostReadOnlyBannerText` | 只读仅由 `_hostReadOnly` 决定；组合态同时展示 `HOST_READ_ONLY` 与 `CORE_CAPABILITY_MISSING`；只读文案不声称「可浏览」；单一原因仍只显示一个 banner；不改 XAML | AC-R4 |
| **I-5** | 测试/证据/门禁 | `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`；`verification/FEA-12-UI-RESIDUAL-1/**` | 4–5 个判别测试 + 4 个变异红日志（`logs/scope-mutations.log`）；全量门禁不降 | AC-R5 |

### Out（明确不做）

- **O-1** Host/Core 能力门与 ① 生产可达性（`NewManga.CoreClient/**`/`NewManga.Host/**`、delete-permanently 能力门）→ 另卡。
- **O-2** 新 command/capability/DTO/错误码/schema/migration/依赖；`CORE_CAPABILITY_MISSING` 加入 `AllowedDeleteTrashErrorCodes`（L-R2 留 Host/Core）。
- **O-3** `IHostController.cs`、`RunContracts.cs`、`FEA-C07_API_INVENTORY.md`、`TrashModels.cs`、`FakeHostController.cs`、`LibraryViewModel.cs`、`HostController.cs`、`NullHostController.cs`。
- **O-4** `RecycleBinView.axaml(.cs)`、XAML 结构/令牌、`NewManga.DesignSystem/**`、`src/**`（Python）。
- **O-5** 批量删除/`PurgeTrash`/页面级章节级删除/缩略图/保留期限/自动清理/Fluent 真实接线（FEA-12-UI L1–L10）。
- **O-6** 修改 `doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`/FEA-12-UI 历史字节。
- **O-7** 真实用户数据/AppData/外部卷/真实回收站/原文件删除；push。
- **O-8** 声称 ① 生产可达、AC 已回填、L3/L4 已通过。

## 实现语义（DSH 冻结口径）

- **① 只做防御不变量**：`CapabilityMissing` 是删除结果，不是页级 read/preview 能力态；不得把页级 `_capabilityMissing` 置 true、不得覆盖 `_capabilityMessage`；不新 probe、不推断 read/write/preview 布尔。
- **② 只刷新一次**：`BOOK_NOT_FOUND` → notify + 关面板 + `await ReloadAsync`；刷新失败不自动重试（L-R3）；其它错误码不并入该分支。
- **③ 提示必须到达用户**：NotFound 的 typed 文案必须在 `ResetPreview()` 之后仍可见（用 `_notify`），列表刷新、面板关闭、状态复位；digest 必须沿用首次逐字节相同值。
- **④ 两个独立事实**：只读与能力缺口各自独立；组合态同时展示；只读文案不得在 read 缺失时声称可浏览；非组合态不新增 banner。
- **测试真实性**：全部在 VM 层、fake controller、无 Avalonia 窗口、无 sleep；四条各做变异（删实现/改坏分支必须变红），红日志入库。
- **不夸大**：Handoff/卡面不得写「修复用户可见能力缺失 bug」「AC 已回填」「L3/L4 通过」。

## Acceptance Criteria

- [ ] **AC-R1 delete-time capability 防御边**：`TrashDeleteOutcome.CapabilityMissing` 时不设页级 `_capabilityMissing/_capabilityMessage`；列表保持（`ShowList=true`、`ShowCapabilityState=false`、`Items` 数不变）；结果面板 typed `CORE_CAPABILITY_MISSING`、`DeleteResultTitle="删除被拒绝"`、`CanConfirmDelete=false`；零成功提示、零 restore/preview 副作用；能力布尔不变。证据：`Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing` + 变异红日志。
- [ ] **AC-R2 preview `BOOK_NOT_FOUND` 自动刷新**：`_notify` + 关面板 + `ReloadAsync`；恰 2 个 `library_list_trash` 帧（初始+刷新）、0 delete 帧、probe 2 次；刷新后幽灵行清除；不自动重试 preview；其它失败码行为不变。证据：`Preview_BookNotFound_ClosesPanel_AndReloadsTheList` + 变异红日志（移除 ReloadAsync/notify/误并入通用分支各 1 红）。
- [ ] **AC-R3 cleanup retry `BOOK_NOT_FOUND`**：3 个 delete 帧、三次 `inventory_digest` 与首次逐字节相等、仅 1 preview 帧；NotFound 时用户可见「作品已不存在（`BOOK_NOT_FOUND`）/已刷新」typed 提示；列表刷新（2 list 帧）；`IsCleanupPending=false`、`CanRetryCleanup=false`、面板关闭；不伪报成功、不自动重试、不为 NotFound 重新 preview。证据：`CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` + 变异红日志（移除 notify/改 digest/移除 ReloadAsync）。
- [ ] **AC-R4 只读/能力缺口双原因文案**：`ShowHostReadOnlyBanner` 仅由 `_hostReadOnly` 决定；Host 只读 + write/preview 缺口 → 两 banner 同时可见、两个 code 分别出现；Host 只读 + read 缺失 → `ShowCapabilityState=true` 且只读 banner 可见、只读文案不含「可浏览」、能力文案不含 `HOST_READ_ONLY`；单一原因仍单 banner；不改 XAML。证据：`HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses`、`HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason` + 变异红日志。
- [ ] **AC-R5 写域/门禁/证据**：`git diff --name-only <base>..HEAD` ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`src/**`/Host/CoreClient/DesignSystem/`RecycleBinView.axaml` 零 diff；无新依赖；定向 `TrashUiTests` 全绿（基线 35 + 新增 4–5）；全量 .NET **≥1527/0/≤86**（before/after 分列）；pytest 全量 **3249/10 不降**（零 Python 改动可 `NOT_RUN`+零 diff 理由，须实测或如实记录）；pins 18/18；API inventory PASS；check PASS；证据含 changed-files/scope-validation/gates/mutations/计数；L3/L4 `NOT_RUN`。证据：`verification/FEA-12-UI-RESIDUAL-1/**`。

## 测试与证据要求

| 场景/AC | 命令/步骤 | 前提/环境 | 预期 | 证据 |
|---|---|---|---|---|
| AC-R1…R4 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter FullyQualifiedName~TrashUiTests` | fake controller；无窗口/无 sleep | 基线 35 + 新增全绿；变异红 | `verification/FEA-12-UI-RESIDUAL-1/logs/` |
| AC-R5 | 全量 .NET、pytest、pins、check、API inventory、scope diff | 仓库根 | 不降/不漂移 | `logs/gates.log`、`logs/scope-validation.log`、`changed-files.txt` |
| 变异 | 每个 AC 至少 1–2 个破坏点 | 临时改 `TrashViewModel.cs` 后恢复 | 目标用例变红 | `logs/scope-mutations.log` |

## 已知 limitation（预登记，closeout 必须如实保留）

- **L-R1（①生产不可达）**：本卡只钉防御不变量；Host 当前不对 `library_delete_book_permanently` 做能力门，Core 不返回该码 → 该分支生产不可达；不得写成「已修复用户可见缺陷」。
- **L-R2（R-002 旧债）**：`CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`；Host 投影会把 category 降为 unknown（code 保留）；属 Host/Core，本卡不修。
- **L-R3（②刷新失败）**：`ReloadAsync` 自身失败只显示列表错误态，不自动重试（有意，不引入循环）。
- **L-R4（③面板关闭）**：NotFound 后关闭结果面板，提示仅通过 notify；若产品要求保留面板需另冻结文案规则。
- **L-R5（④视觉冗余）**：组合态两条 banner 同时出现，接受视觉冗余以不丢原因；合并文案需重新冻结。
- **L-R6（证据层级）**：四项均为 VM 级 fake 测试，不新增真实 Host/Core IPC；cleanup retry NotFound 的真实 wire 行为无 L2 IPC 证据。
- **L-R7（④read 可用时信息量略减）**：只读文案移除「可浏览」；动态文案追加需另加测试。
- **L3/L4**：真机走查仍 `NOT_RUN`；本卡不新增真机证据，不得声称通过。

## 允许修改范围

- `doc/tasks/FEA-12-UI-RESIDUAL-1.md`、`doc/reviews/FEA-12-UI-RESIDUAL-1-*.md`、`doc/handoffs/FEA-12-UI-RESIDUAL-1-*.md`、`verification/FEA-12-UI-RESIDUAL-1/**`。
- 生产代码：`apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs`（仅此一个文件）。
- 测试：`apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`（仅此一个文件）。
- **不在 Owner 写域**：见 Out；实现确需扩域必须先停下报 DSH 增列，不得静默扩；不得 `git add -A`（显式 pathspec）；不 push。

## 禁止范围

- Host/Core/契约/pins/XAML/DesignSystem/Python/依赖；真实用户数据/AppData/外部卷/真实回收站/原文件删除；FEA-12-UI 历史 AC 回填；L3/L4 宣称通过。

## 依赖、风险与阻塞

- 依赖：`FEA-12-UI`（done，`a46d4d5c7`）。
- 风险：① 测试注入生产不可达结果易被误读（AC/Handoff 明写 defensive invariant）；③ `ResetPreview` 清空文案的实现细节；④ 组合态视觉冗余（L-R5）；fake `WritesAllowed` 设置顺序（Enter 前）。
- 阻塞标准：若实现必须改 Host/Core/契约/XAML/fake，Owner 停下报 DSH，不得自行扩域；若要求 ① 生产可达 → 另卡。

## 交付与运行记录

- 实施 Owner：`ui-residual-impl`（DSH Agent Teams teammate）。
- Handoff：`doc/handoffs/FEA-12-UI-RESIDUAL-1-<head>.md`（交付 head 后）。
- Review：独立上下文 fresh subagent（`doc/reviews/FEA-12-UI-RESIDUAL-1-r*.md`）。
- 实际测试：before/after、passed/failed/skipped 与 skip 原因待实施记录。

## Canonical Evidence

（Owner 提交前填写；`in_review` 时必须逐项 pin commit/SHA-256。）

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pending | AC-R1…R5 | pending | pending | pending | CANONICAL |

## Resource Manifest

（closeout 时填写真实路径与 disposition；不适用写 `NOT_APPLICABLE`。）

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| pending | pending | pending | — | — | pending |

## Closeout Record

- 待实施、Review、集成与 closeout 时填写（DSH 保留最终集成/closeout 责任）。
