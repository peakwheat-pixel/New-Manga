---
id: FEA-12-UI-RESIDUAL-1
title: FEA-12-UI 残余 P3 收尾（delete-time capability 防御边 / preview BOOK_NOT_FOUND 刷新 / cleanup retry 提示 / 只读与能力缺失文案）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-12-UI-RESIDUAL-1-scope-r1.md`（fresh subagent `bfb8f132…`，verdict **READY-TO-FREEZE**）；DSH 2026-11-06 裁决（见「Scope Review 裁决」）：接受 **App-only** 范围与四个冻结口径（① defensive invariant only；③ 含最小 `_notify` 修复；④ 双原因文案规则；写域仅 `TrashViewModel.cs` + `TrashUiTests.cs`）；释放为 ready、base `690c77eb0`、Owner=`ui-residual-impl`（DSH Agent Teams）。实施交付 head `8e3bd03d6`（`8e3bd03d6` 实现+测试；卡/Handoff/证据 `323001fec`）；DSH 核验后 2026-11-06 转 `in_review`，Review 由独立上下文 fresh subagent 执行
suggested_owner: zcode
owner: ui-residual-impl
reviewer: 独立上下文 fresh subagent（r1 已指派；不得由实现会话/实例自审；session 与来源见 `doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`）
depends_on:
  - FEA-12-UI
base_commit: 690c77eb0
branch: null
worktree: null
integration_commit: 8e3bd03d6
delivery_head: 8e3bd03d6
canonical_evidence_status: complete
resource_closeout_status: complete
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

> **状态：`done`（r1 approved P0/P1/P2=0/P3=4；交付 head `8e3bd03d6`；Owner=`ui-residual-impl`；base `690c77eb0`）。**
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

> Owner 实施完成后逐项勾选并附证据指针（`delivery_head=8e3bd03d6`，2026-11-06）；**终判（MET/PARTIAL）以独立 Review + DSH 集成验证为准**，本节不代替审查。

- [x] **AC-R1 delete-time capability 防御边**：`TrashDeleteOutcome.CapabilityMissing` 时不设页级 `_capabilityMissing/_capabilityMessage`；列表保持（`ShowList=true`、`ShowCapabilityState=false`、`Items` 数不变）；结果面板 typed `CORE_CAPABILITY_MISSING`、`DeleteResultTitle="删除被拒绝"`、`CanConfirmDelete=false`；零成功提示、零 restore/preview 副作用；能力布尔不变。证据：`Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing`（`TrashUiTests.cs`）+ 变异 M1（`verification/FEA-12-UI-RESIDUAL-1/logs/scope-mutations.log`）；EV-2/EV-8。**defensive invariant only（L-R1）**。 <<MET>>
- [x] **AC-R2 preview `BOOK_NOT_FOUND` 自动刷新**：`_notify` + 关面板 + `ReloadAsync`；恰 2 个 `library_list_trash` 帧（初始+刷新）、0 delete 帧、probe 2 次；刷新后幽灵行清除；不自动重试 preview；其它失败码行为不变。证据：`Preview_BookNotFound_ClosesPanel_AndReloadsTheList` + 变异 M2/M3/M4；EV-2/EV-8。**「其它失败码行为不变」仅结构未变（仅精确 `BOOK_NOT_FOUND` 分支前置，通用分支 diff 未改），未单独回归测试（Review F2，follow-up）**。 <<MET>>
- [x] **AC-R3 cleanup retry `BOOK_NOT_FOUND`**：3 个 delete 帧、三次 `inventory_digest` 与首次逐字节相等、仅 1 preview 帧；NotFound 时用户可见「作品已不存在（`BOOK_NOT_FOUND`）/已刷新」typed 提示；列表刷新（2 list 帧）；`IsCleanupPending=false`、`CanRetryCleanup=false`、面板关闭；不伪报成功、不自动重试、不为 NotFound 重新 preview。证据：`CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` + 变异 M5/M6/M7；EV-2/EV-8。 <<MET>>
- [x] **AC-R4 只读/能力缺口双原因文案**：`ShowHostReadOnlyBanner` 仅由 `_hostReadOnly` 决定；Host 只读 + write/preview 缺口 → 两 banner 同时可见、两个 code 分别出现；Host 只读 + read 缺失 → `ShowCapabilityState=true` 且只读 banner 可见、只读文案不含「可浏览」、能力文案不含 `HOST_READ_ONLY`；单一原因仍单 banner；不改 XAML。证据：`HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses`、`HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason` + 变异 M8/M9；EV-2/EV-8。 <<MET>>
- [x] **AC-R5 写域/门禁/证据**：`git diff --name-only <base>..HEAD` ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`src/**`/Host/CoreClient/DesignSystem/`RecycleBinView.axaml` 零 diff；无新依赖；定向 `TrashUiTests` 40/0（基线 35 + 新增 5）；全量 .NET **1532/0/86**（before 1527/0/86；8 项目分列）；pytest 全量 **3249/10 不降**（实测，零 Python diff）；pins 18/18；API inventory PASS；check PASS(3 warnings)；证据含 changed-files/scope-validation/gates/mutations/计数；L3/L4 `NOT_RUN`。证据：`verification/FEA-12-UI-RESIDUAL-1/**`（EV-1…EV-12）。 <<MET>>

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
- 实测基线：`git rev-parse HEAD=9c6ba2da1`（较卡面 `base_commit 690c77eb0` 多 1 个 docs-only 提交，代码/测试树等价；工作树 clean）。实现+测试 commit **`8e3bd03d6`**（2 files changed, 215 insertions, 8 deletions；`delivery_head`）。**未 push、未创建 worktree。**
- Handoff：`doc/handoffs/FEA-12-UI-RESIDUAL-1-8e3bd03d6.md`。
- Review：独立上下文 fresh subagent `doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`（session `b135fbb8-d81a-4cf6-aeb4-ce2aa7168deb`）→ **approved（P0=0/P1=0/P2=0/P3=4）**；F1–F4 处置见 Closeout Record 与 `EV.md` §7。
- 实际测试（2026-11-06 实测）：
  - 定向 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter FullyQualifiedName~TrashUiTests`：**before 35 passed / 0 failed / 0 skipped → after 40 passed / 0 failed / 0 skipped**（+5 = 新增判别测试）。
  - 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`：**before 1527 passed / 0 failed / 86 skipped → after 1532 passed / 0 failed / 86 skipped**；8 项目分列 before=21+38+253+117+31+185+167+715、after=21+38+253+117+31+185+167+720；skip=86 为既有环境门控（Host 55 / CoreClient 24 / App 7），本卡未新增或改变 skip 条件。
  - 全量 `C:/Python314/python.exe -m pytest tests -q`：**3249 passed / 10 skipped / 0 failed（EXIT=0）**，与基线相同；本卡零 Python diff（`git diff -- src tests` 为空）。
  - `verify_pins.ps1` **18/18 PASS**；`check.ps1` **PASS(3 warnings)**（既有：9 非终态 Task / STATUS 80% / PLAN 80%）；`generate_api_inventory.py --check` **PASS（EXIT=0）**。
  - 变异：**9/9 破坏点全部变红**（M1…M9，EXIT=1，断言失败；pristine 逐字节恢复），日志 `verification/FEA-12-UI-RESIDUAL-1/logs/scope-mutations.log`。
  - 全量 .NET 的既有副作用 `verification/FEA-09/logs/wire-redacted.ndjson` 已 `git checkout -- verification/FEA-09` 恢复；最终 worktree 仅本卡改动。
- **L3/L4 真机走查：`NOT_RUN`**；I-1 为 **defensive invariant only（生产不可达，L-R1）**；FEA-12-UI 历史 AC 未回填。

## Canonical Evidence

（Owner 已填写；终判由独立 Review + DSH 集成验证复核。日志类证据对应代码状态 = 实现+测试 commit `8e3bd03d6`（base `9c6ba2da1`）；证据/卡/Handoff 由紧随其后的证据提交收录，该提交 sha 见 `git log -- verification/FEA-12-UI-RESIDUAL-1`。）

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-1 | AC-R1…AC-R4 定向基线（35/0/0） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-targeted-before.log` | `323001fec` | `ea544fedda4828a02a5652b33ac7ce69ce741c0282eaf86c2ff1b1ab6672d31e` | CANONICAL |
| EV-2 | AC-R1…AC-R5 定向 after（40/0/0，新增 5） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-targeted-after.log` | `323001fec` | `3128e92f44ffea5f4dd1b7d074d95d37d2e22195369a4755739fea95165626f0` | CANONICAL |
| EV-3 | AC-R5 全量 .NET before（1527/0/86） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-dotnet-before.log` | `323001fec` | `baab20fdfc22b9c9ffc479496e5e487dcb9ae624bd36b12de7363f31fe040a88` | CANONICAL |
| EV-4 | AC-R5 全量 .NET after（1532/0/86） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-dotnet-after.log` | `323001fec` | `3fbf0840f9d4d5f07d053a132a846e9b701938298abb8d8d92f112b1f5180c20` | CANONICAL |
| EV-5 | AC-R5 全量 pytest（3249/10，零 Python diff） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-pytest.log` | `323001fec` | `69beb5ca4c805327d2fc47e3290a88eaf700a824b384bb0e1b114af19753704d` | CANONICAL |
| EV-6 | AC-R5 pins 18/18 + check PASS(3 warnings) + API inventory PASS | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-governance.log` | `323001fec` | `2b83261984c08eaf48a8380c122217143fb379d0c0701d6e1db28e4fbb512d76` | CANONICAL |
| EV-7 | AC-R5 scope diff ⊆ allowed_paths；禁止面/依赖/API 零 diff | `verification/FEA-12-UI-RESIDUAL-1/logs/scope-validation.log` | `323001fec` | `a21eede24ea5f701b3ed56f9fe37eb3b941f6973bb2dcc5c3c3a4566319b2894` | CANONICAL |
| EV-8 | AC-R1…AC-R4 判别性（9/9 变红，逐字节恢复） | `verification/FEA-12-UI-RESIDUAL-1/logs/scope-mutations.log` | `323001fec` | `f95d41527212d65005c12a2df3f7c0129ad24455dc4ecee5e1529f11762892de` | CANONICAL |
| EV-9 | AC-R5 门禁汇总（before/after、skip 原因、L3 NOT_RUN） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates.log` | `323001fec` | `d0ad14579d3904b363adbbbd74fc3e416ac488b8bdb519faed142e6b1c79f353` | CANONICAL |
| EV-10 | AC-R5 Resource Manifest（仓外隔离根 10 文件聚合 + 资源处置） | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | `323001fec` | `1c78ec610f5bec011a7850d3bd0697e43f9d482360b72c3dcc9e90247dc80ed7` | CANONICAL |
| EV-11 | AC-R5 变更清单（base..证据 head，逐文件） | `verification/FEA-12-UI-RESIDUAL-1/changed-files.txt` | `323001fec` | `1e0ba244e5bec73c900b45c221a7c3aeeb4da1d74b1879024835d473096f4b50` | CANONICAL |
| EV-12 | AC-R1…AC-R5 证据索引（AC→实现→测试→证据映射、limitation、过程说明；Review F1/F3 处置后） | `verification/FEA-12-UI-RESIDUAL-1/EV.md` | `a70d54c75` | `3a3f1c46a29f78ddc110218ea1f925927092628206d77049b3774b6efb99f304` | CANONICAL |

## Resource Manifest

（Owner 已填写；closeout 由 DSH 复核。）

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；base `9c6ba2da1`） | NOT_APPLICABLE | — | — | 未创建 linked worktree；`git worktree list` 无本卡新增 |
| temp | `G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1\`（agent 脚本 + 原始门禁日志 + pristine 备份） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1\` | `97fdbd1e5bb0fc8d15eb44f42cd88580e76eb43b25b0fa086222abb792d28428` | 仓外隔离根（10 文件聚合；逐文件 sha 见 `RESOURCE-MANIFEST.json`）；无进程持有；产品/测试不引用；仓内 canonical 副本 `verification/FEA-12-UI-RESIDUAL-1/logs/**`（EV-1…EV-9）；保留供 Review |
| test-fixture | `TrashUiTests.cs` 内存 fake controller（无二进制 fixture） | NOT_APPLICABLE | — | — | 5 个新测试全部 VM 级 + fake；无 Avalonia 窗口、无 sleep、无真实 IPC |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未读写真实用户数据/AppData/外部卷/真实回收站/原文件 |
| build-artifact | NOT_APPLICABLE | NOT_APPLICABLE | — | — | `dotnet test` obj/bin 在既有 build 目录，未纳入交付 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson`（既有 `WireLogSourceRedactionTests` 副作用） | NOT_APPLICABLE | — | — | 每次全量 .NET 后重写；每次均 `git checkout -- verification/FEA-09`（EXIT=0）恢复，最终 worktree clean（非本卡资源处置项） |

## Closeout Record

- **Closeout date / DSH**：2026-11-06；DSH（Lead / Architect / Integrator）。
- **交付/集成**：`base_commit=690c77eb0`（实施实测起点 `9c6ba2da1`，仅 docs 差异）；实现+测试 `8e3bd03d6`（`delivery_head` / `integration_commit`）；卡/Handoff/证据 `323001fec`；Review 处置证据 `a70d54c75`（EV.md 重钉，无代码改动）。卡/STATUS/PLAN/LEDGER closeout 提交见本提交。
- **AC 判定**：**AC-R1…AC-R5 全部 MET**（逐项见 `EV.md` §4 与 Canonical Evidence EV-1…EV-12）；无 PARTIAL/BLOCKED。
- **独立 Review**：`doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`（fresh subagent `b135fbb8-d81a-4cf6-aeb4-ce2aa7168deb`，未参与实现/返修）→ **approved（P0=0 / P1=0 / P2=0 / P3=4）**；无代码返修。处置：**F1** 通知先于 `await ReloadAsync()` → 维持冻结文案并在 L-R3 补记（P3 时序限制）；**F2** AC-R2「其它 preview 失败码不变」仅结构未变、未单独回归测试 → 已按此限定并登记 follow-up；**F3** EV.md 自索引缺 EV-12 → §3 增补自引用说明（自引用文件无法内嵌自身 sha；卡面登记）；**F4** `ITrashController is null` + 只读组合未测 → 防御路径、生产两实现非空，登记 follow-up。
- **DSH 集成验证（Lead 实测，HEAD=`a70d54c75`，2026-11-06）**：全量 `pytest tests` 首跑 **3248 passed / 1 failed / 10 skipped**，唯一失败为既有 flaky `tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`（测试内注 `FLAKY-PYTEST-1`，与本卡零 Python 改动无关）；隔离复跑 **3/3 passed**；全量复跑 **3249 passed / 10 skipped（EXIT=0）**。全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` **1532 passed / 0 failed / 86 skipped（EXIT=0）**（8 项目 21+38+253+117+31+185+167+720；skip=86 全为既有环境门控）。`verify_pins.ps1` **18/18 PASS**；`check.ps1` **PASS(3 warnings)**；`generate_api_inventory.py --check` PASS；scope diff = 2 个 allowed App 文件，禁止面/依赖/API 零 diff。每次全量后 `git checkout -- verification/FEA-09`（restore=0），最终 worktree clean。原始日志：`G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1-closeout\`（PRESERVE_REFERENCED）。
- **canonical_evidence_status**：`complete`（EV-1…EV-12；EV-1…EV-11 在 `323001fec`，EV-12 在 `a70d54c75`）。**resource_closeout_status**：`complete`。
- **删除/迁移/归档**：0 文件、0 字节（`PRESERVE_REFERENCED`/`NOT_APPLICABLE`；未删除/移动/归档任何资源；`closeout_counts` 全 0）。
- **未关闭项（如实保留）**：L-R1（I-1 生产不可达，仅 defensive invariant）、L-R2（`CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`，Host/Core 旧债）、L-R3…L-R7（含 Review F1 通知时序）、F2/F4 follow-up；**L3/L4 真机走查 `NOT_RUN`**；**FEA-12-UI 历史 AC 未回填**。不得宣称 ① 生产可达或 L3/L4 通过。
- **指针清理**：STATUS 当前 Task → 无活动 Task（下一候选待定）；PLAN 本节点 in_review→done 事实；TASK_LEDGER 重生成；本卡不再是 READY 节点。
- **push**：**已执行**（2026-11-06，用户「全部授权」覆盖不 push 限制且门禁全过）：`git push origin main` → `690c77eb0..fe44d067b`（PRE_HEAD `fe44d067b`、POST_ORIGIN `fe44d067b`、PUSH_EXIT=0、AHEAD 7→0）；记录 `G:\CODEX\New Manga.workspace\temp\push-record-ui.log`。
