---
id: FEA-12-UI-RESIDUAL-2
title: 回收站 UI 状态一致性收口（恢复后书架刷新 / 空态与分页诚实性；App-only）
kind: implementation
governance_version: 3
status: done
approval: 用户 AUTORUN 指令（2026-11-08「全部授权/自主裁决/不询问用户」）；独立 scope review `doc/reviews/FEA-12-UI-RESIDUAL-2-scope-r1.md`（两轮独立评审 session `402ec34a-…`/`986a9e4c-…`，均 **READY-TO-FREEZE**）；DSH 2026-11-08 裁决（见「Scope Review 裁决」）：判据 (a) 用户可见缺陷 + App-only + 0 pin；base `54e5d69db`、Owner=`ui-residual-2-impl`（DSH Agent Teams）；实现交付 `85356c22a`；独立 Review r1 **approved（P0=0/P1=0/P2=1/P3=5）**（`doc/reviews/FEA-12-UI-RESIDUAL-2-r1.md`）
suggested_owner: dsh
owner: ui-residual-2-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 指派于实现交付后，session 与来源记入 `doc/reviews/FEA-12-UI-RESIDUAL-2-r1.md`）
depends_on:
  - FEA-12-UI
base_commit: 54e5d69db
branch: null
worktree: null
integration_commit: 85356c22a
delivery_head: 85356c22a
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-12-UI-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-12-UI-RESIDUAL-2.md
  - doc/reviews/FEA-12-UI-RESIDUAL-2-*.md
  - doc/handoffs/FEA-12-UI-RESIDUAL-2-*.md
  - verification/FEA-12-UI-RESIDUAL-2/**
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
out_of_scope:
  - Host/Core/IPC：`apps/desktop-avalonia/src/NewManga.Host/**`、`NewManga.CoreClient/**`、`src/**`（Python）、`IHostController.cs`、`ITrashController`、`TrashModels.cs`、`TrashCopy`
  - XAML 与设计系统：`Views/V2/Library/RecycleBinView.axaml(.cs)`、`NewManga.DesignSystem/**`、令牌
  - 契约与生成物：`doc/contracts/**`、`doc/plan/**`、wire 命令集/capability/DTO/错误码/schema/migration/依赖、18 pins、`FEA-C07_API_INVENTORY.md`
  - 冻结证据：`doc/tasks/FEA-12-UI.md` 正文与 `verification/FEA-12-UI/**` 的 AC/EV 字节（本卡只新增自己的证据）
  - 产品级功能：批量彻底删除、`library_purge_trash`、回收站缩略图/总数、页面级回收站（FEA-12-UI L1/L2/L8 OUT-2 不变）
  - 治理清理：删除死代码 `RecycleRestoreCommand`（DSH 裁决：另卡，不在本卡）
  - 真实用户数据/AppData/外部卷/真实回收站/原文件；L3/L4 真机走查（NOT_RUN 保持）
---

# FEA-12-UI-RESIDUAL-2：回收站 UI 状态一致性收口（App-only）

> **状态：`ready`（已冻结，base `54e5d69db`；Owner=`ui-residual-2-impl`；Reviewer=独立上下文 fresh subagent）。**
> 来源：本轮两个并行独立只读审计推翻 handoff §26「可推进项耗尽」结论，DSH 逐行复核确认两条**未登记**的 App-only 缺陷；独立 scope review `doc/reviews/FEA-12-UI-RESIDUAL-2-scope-r1.md` 判 **READY-TO-FREEZE**。
> **本卡只做 App 侧行为与测试**；不改 Host/Core/契约/wire/schema/依赖/XAML；**0 pin、无 UNFREEZE**；不回填 `FEA-12-UI` 历史 AC/证据字节。

## Scope Review 裁决（DSH，2026-11-08）

| 争议点 | Review 建议 | **DSH 裁决** |
|---|---|---|
| 判据 | (a) 用户可见 + App-only | **接受**：恢复的唯一目的即把作品放回书架；旧行为使用户判为「恢复没生效」。 |
| 缺陷 B 范围 | 恢复与彻底删除两条路径同构 | **接受**：AC-R4 要求两条路径各有判别断言，不得只修恢复。 |
| 实现方案 | 构造注入 `Func<Task>? onBooksRestored`；不用 event | **接受**：可 await、headless 可断言；两个构造点不受影响；不新增 `IHostController` 成员。**禁止**在 `CloseRecycleBin` 无条件刷新（撞帧数断言）。 |
| Fake 支持 | 可选**默认关闭**回填开关 + 测试内预置 Snapshot | **接受**：默认关闭保证既有用例零扰动；新用例显式开启。 |
| 死代码 `RecycleRestoreCommand` | 确认死代码（`RecyclePurgeCommand` 是活的） | **本卡不删**：清死代码属治理清理，另卡；避免扩大口。登记 P3。 |
| 空态修复 | `IsEmpty` 加 `_nextCursor is null`；`ShowList` 加 `|| HasMore`；不改 XAML、不自动重载 | **接受**：最小可判定；「加载更多」留在 `ShowList` 内即恢复可达。 |
| 冻结 AC/证据 | 不得改写 `FEA-12-UI.md` AC1 与 pin | **接受**：`doc/tasks/FEA-12-UI.md` 字节零改动。 |
| A′（第二轮评审发现） | 必须并入，否则 AC-R1 计数断言不可 MET | **接受**：并入本卡（AC-R6）；只补 setter 两参数通知，不改 XAML。 |
| `RefreshAsync` 自动选中副作用 | 接受并登记 limitation | **接受**：登记 **L-2**；不新增参数改选中语义。 |
| UNFREEZE | 不需要 | **接受**：0 pin。 |

## 缺陷（冻结事实，base `54e5d69db`）

- **A 恢复后书架不刷新（用户可见）**：`TrashViewModel.RestoreSelectedAsync`（`TrashViewModel.cs:545-599`）成功/部分成功后只从 `Items` 移除行（`:572-579`），不通知书架；唯一活动入口是 `RecycleBinView.axaml:120` 绑定的 `Trash.RestoreCommand`；`LibraryViewModel.CloseRecycleBin()`（`:886-895`）只切视图；`_allBooks` 仅在 `RefreshAsync`（`:628-654`）重建，而移入回收站（`:981`）与撤销（`:1020`）都会刷新。⇒ 恢复后返回书架仍是进入回收站前的快照。
- **B 空态/分页不诚实**：`TrashViewModel.cs:216 IsEmpty` 不看 `_nextCursor`、`:222 ShowList` 要求 `Items.Count > 0`；「加载更多」位于 `ShowList` 容器内（`RecycleBinView.axaml:84-92`）。恢复（`:572-579`）与彻底删除（`RemoveDeletedRow` `:877-893`）都只删行、不清 `_nextCursor`（仅 `ReloadAsync:396-406` 清）⇒ 首页清空但仍有下一页时显示「回收站是空的」（`RecycleBinView.axaml:57-62`）且「加载更多」消失。
- **A′ 计数文案不重发（第二轮独立评审发现，DSH 裁决并入）**：`LibraryViewModel.IsRecycleBinView` setter（`:418-433`）只重发 `ShowGrid/ShowSideDetail/…`，不重发 `BookCountText`/`ListStatusText`（取值依赖 `IsRecycleBinView`，绑定在常驻 library bar `LibraryView.axaml:17`）⇒ ①进入回收站时 bar 仍显示「N / M 作品」；②本卡修复后刷新发生在回收站内，`RaiseListStates()` 把文案刷成「回收站」，返回书架后不再重发 ⇒ bar **停在「回收站」**。不修 A′ 则 AC-R1 的计数断言不可 MET。

## Scope（冻结）

### In

| # | 冻结项 | 位置 | 必须行为 | AC |
|---|---|---|---|---|
| **I-1** | 恢复成功后书架同步 | `TrashViewModel`（构造注入回调 + `RestoreSelectedAsync`）、`LibraryViewModel`（构造点订阅） | `SucceededIds.Count > 0` 时 `await` 注入回调；生产连接 `LibraryViewModel` 侧 `RefreshAsync()`；部分成功同样刷新；全部失败不刷新、不伪报 | AC-R1 / AC-R2 |
| **I-2** | 空态与分页诚实性 | `TrashViewModel.IsEmpty` / `ShowList` | `Items.Count == 0 && _nextCursor is null` 才是真空；`Items.Count > 0 || HasMore` 才显示列表容器（含「加载更多」）；不改 XAML、不自动重载 | AC-R3 / AC-R4 |
| **I-2b** | 计数文案双向一致（A′） | `LibraryViewModel.IsRecycleBinView` setter | setter 的 `OnPropertyChanged` 增 `nameof(BookCountText)`、`nameof(ListStatusText)`；进入回收站 bar 显示「回收站」，返回书架恢复「N / M 作品」 | AC-R6 |
| **I-3** | 测试支持 | `FakeHostController`（默认关闭回填开关）、`TrashUiTests` / `V2ShellUiTests` 新用例 | 断言落到「书重回 `Books`」而非仅帧数；两页脚本（`ScriptedTrashPages`）覆盖恢复与彻底删除两条路径 | AC-R4 / AC-R5 |
| **I-4** | 证据与门禁 | `verification/FEA-12-UI-RESIDUAL-2/**` | 判别性变异证据 + 全量门禁不降 | AC-R5 |

### Out（明确不做）

见 front matter `out_of_scope`。补充：**不得**删除 `RecycleRestoreCommand`（死代码另卡）；**不得**顺手 `Trash.RefreshAsync()`（撞 `TrashUiTests:842` 的 `ListTrash==2`）；**不得**改 `RecycleBinView.axaml`。

## Acceptance Criteria（冻结，逐条可判定）

- [x] **AC-R1 恢复成功后书架一致**：回收站恢复成功（`SucceededIds.Count > 0`）后，`RefreshBooksAsync` 恰被调用 **+1**，且被恢复作品重新出现在 `Library.Books` / `AllBooks`，`BookCountText` 随之更新；`Trash.Items` 不再含该书。判别测试走真实入口链路：`ShowRecycleBinCommand` → 选中 → `Trash.RestoreCommand`（恢复按钮绑定）→ `CloseRecycleBinCommand`。若只断言帧数、不断言书内容 → 不判 MET。 <<MET>>
- [x] **AC-R2 部分成功 / 全部失败边界**：`SucceededIds>0 && FailedItems>0` → 刷新 1 次、逐项原因保留、状态文案同时含「已恢复 X 项」与「Y 项未恢复」；`SucceededIds==0`（全失败） → `RefreshCalls` **不变**、不称成功、原列表行保留。 <<MET>>
- [x] **AC-R3 空态与分页诚实性**：`Items.Count==0 && _nextCursor != null` → `IsEmpty==false`、`ShowEmptyState==false`、`ShowList==true`、`HasMore==true`，且 `LoadMoreAsync()` 以原 cursor 发第二帧（`TrashListCursors` 断言）；`Items.Count==0 && _nextCursor==null` → 空态照旧（`IsEmpty/ShowEmptyState==true`、`ShowList/HasMore==false`）；**回归栅栏**：能力缺失态与 probe 失败态仍 `ShowList=false`、不显示空态（短路顺序不得被打乱）。 <<MET>>
- [x] **AC-R4 两条删除路径同构覆盖**：AC-R3 的「首页清空 + 有下一页」必须分别在**恢复**与**彻底删除**两条路径各有一个判别用例；实现不得只修其中一条。 <<MET>>
- [x] **AC-R5 门禁与禁止面**：定向 App 测试全绿（含 `TrashUiTests`/`V2ShellUiTests`/`StartupReadDedupTests`）；全量 pytest ≥ **3390 passed / 10 skipped**、全量 .NET ≥ **1683 passed / 0 failed / 96 skipped**（新增用例后 passed 只增不减）；pins **18/18**；`check.ps1` PASS；`generate_api_inventory.py --check` PASS；全程 0 帧 `library_purge_trash`、0 帧批量彻底删除；`git diff --name-only -- src/ doc/contracts doc/tasks/FEA-12-UI.md verification/FEA-12-UI` 为空；变异判别（破坏实现→RED→逐字节复原 sha256 MATCH→复绿）留日志。 <<MET>>
- [x] **AC-R6 计数文案双向一致（A′）**：`IsRecycleBinView` 切换必须同时重发 `BookCountText` 与 `ListStatusText`：进入回收站 → bar 文案为「回收站」（不再残留「N / M 作品」）；返回书架（含 Esc 与「返回书架」按钮两路径）→ 恢复为「N / M 作品」且数值与刷新后的 `Books`/`AllBooks` 一致；无任何路径出现「回收站」文案残留在书架。判别测试直接断言属性值，并断言切换后收到对应 `PropertyChanged`。 <<MET>>

## 实现口径（冻结，偏离须先回 DSH）

1. `TrashViewModel` 构造增可选参 `Func<Task>? onBooksRestored = null`（默认 null，保证既有构造点不破）；在 `RestoreSelectedAsync` 的 `result.SucceededIds.Count > 0` 分支末尾（全失败早退与 generation 守卫之后）`await _onBooksRestored()`；**不得**用 C# `event`（async void 竞态）。
2. `LibraryViewModel` 装配（`:70`）传 `onBooksRestored: () => RefreshAsync()`；`RefreshAsync()` 默认 `forceHostRead:true`（恢复改变了 Core 书架，须真实重读而非复用旧快照）。
3. `IsEmpty` 加 `&& _nextCursor is null`；`ShowList` 改 `(Items.Count > 0 || HasMore)`；保持 `_capabilityMissing`/`_probeFailed`/`HasError` 的短路顺序；不改 XAML、不改 `_nextCursor` 生命周期。
4. A′：`IsRecycleBinView` setter 的 `OnPropertyChanged` 列表补 `nameof(BookCountText)`、`nameof(ListStatusText)`（一行）。
5. 测试支持：`FakeHostController` 增**默认关闭**开关（如 `RestoreRepopulatesSnapshot`，默认 `false`），开启时按 `SucceededIds` 把书加回 `Snapshot.Books`（镜像 `:1738-1747` 移除逻辑）；新用例开启开关并在**触发恢复前**预置快照。**AC 必须断言 VM 集合/文案（`Books`/`AllBooks`/`BookCountText`），不得只断 `RefreshCalls`/`Snapshot.Books`**（改动前也会 GREEN）。
6. 提交：显式 pathspec，禁 `git add -A`；含中文改动用 edit/UTF-8，禁 PowerShell `Replace+Set-Content`。

## 已登记 limitation（本卡引入/接受，如实保留）

- **L-2（DSH 裁决接受）**：本卡修复后，恢复成功触发的 `RefreshAsync` 在「选择为空」时会按既有语义自动选中 `Books[0]`（`LibraryViewModel.cs:656-672`，与移入回收站/撤销同构）⇒ 返回书架可能出现首本被选中与一次 `list_chapters` 读。**不修**（新增参数改选中语义会扩大口）；AC 只断言 `Books`/`AllBooks`/`BookCountText`，**不得**断言选中态为 null。
- **L-3（登记，不在本卡）**：`LibraryViewModel.RecycleRestoreCommand`（`:104`/`:173`）为死代码（零 XAML 引用；`RecyclePurgeCommand` 仍活）——清死代码属治理清理，另卡。
- `FEA-12-UI` 的 L1/L2/L3/L4/L8 等 limitation **原样保留**；L3/L4 真机走查 **NOT_RUN**。

## 行文口径（红线）

- 不得写「回收站已完全修复」「UI L1–L10 全部关闭」「回收站功能完备」；只写本卡两条缺陷的行为修复。
- `FEA-12-UI` 的 L1（批量 OUT）、L2（无总数/缩略图）、L3（真机 NOT_RUN、`cleanup_pending` 会话内重试）、L8 等 limitation **原样保留**；L3/L4 真机走查保持 `NOT_RUN`。
- 未落地的不写「已修复」；`NOT_RUN` 不得写成 PASS。

## 交付要求（实现者）

- 仅写 `allowed_paths`；实现 + 测试；跑定向 `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --build`；输出改动摘要、定向测试结果、`git diff --stat`；**不要** commit（由 DSH 集成）或按 DSH 指定方式提交。
- 若发现需要扩大写域（例如必须改 XAML/`TrashModels`）→ **停下报 DSH**，不得自行扩口。

## Canonical Evidence

> `commit` 列：实现/冻结文件填其所在提交；本卡 closeout 证据文件填 `-`（其所在提交即本轮 closeout/证据提交，sha 见 handoff §27 与 `git log -- verification/FEA-12-UI-RESIDUAL-2`）。`sha256` 为工作树字节口径（`Get-FileHash`）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-R1/R2 | apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs | 85356c22a | b47532bcfce1f423c211c63f9c1cf09dfb7c9d2e8ca940f916bc7cf376af3df1 | SOURCE_PIN |
| EV-02 | AC-R1/R6 | apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs | 85356c22a | 98f4fbf29f8e634556b0eb4c6660df062ffee1b31080ccaf9bc5df7472e5c9ba | SOURCE_PIN |
| EV-03 | AC-R1/R3 | apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs | 85356c22a | 5a9aa45910f2eaaf2fc75c4a6fe00c490ffba73f86ed4920bb17d7e268835caa | SOURCE_PIN |
| EV-04 | AC-R1…R4/R6 | apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs | 85356c22a | f8fdbce8d069f79e0a3c75d2672931c3c88785b2f115011693180182d1cce3d1 | SOURCE_PIN |
| EV-05 | AC-R6 | apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs | 85356c22a | 3a7b9cb6fd0e22f2bc07c2162e17f844d136d4471b85db71dee12183e367f990 | SOURCE_PIN |
| EV-06 | 冻结面 | doc/reviews/FEA-12-UI-RESIDUAL-2-scope-r1.md | b7c63bc50 | 0fd638a5f8eda042100b8fd4789b6da0eaf252e46d2f6e675d09295d60d36c55 | CANONICAL |
| EV-07 | 独立 Review r1（approved；P0/P1=0） | doc/reviews/FEA-12-UI-RESIDUAL-2-r1.md | - | fd53c0fe0ab4c7237cfb03f6d910c597d91a36c8a1b3f018ef5d42e8371fee20 | CANONICAL |
| EV-08 | AC-R5（证据总览） | verification/FEA-12-UI-RESIDUAL-2/EV.md | - | 28dbc6d7595864ad02333255ce45cdf0b3baf35c0334d0430406ccef46913bc1 | CANONICAL |
| EV-09 | AC-R5（资源清单） | verification/FEA-12-UI-RESIDUAL-2/RESOURCE-MANIFEST.json | - | a31628bc435f097fd400b56bcdd9cd760244f83ff58156e87cd9c06ce4b09c22 | CANONICAL |
| EV-10 | AC-R5（改动清单） | verification/FEA-12-UI-RESIDUAL-2/changed-files.txt | - | 64568d23dfd680d836a1876c90f300e67e034019962164d80b77a38ca1e35fdb | CANONICAL |
| EV-11 | AC-R5（Lead 门禁日志） | verification/FEA-12-UI-RESIDUAL-2/logs/gates.log | - | f55193337234d71357a467ed81dc39054be45f8639552f4b76f45b5c20b01b27 | CANONICAL |
| EV-12 | 判别性变异/复跑（M1-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M1-green.log | - | 2ac81126d39923b95e40de444befe942239b92d4d2fafd360adda609c4e660e2 | CANONICAL |
| EV-13 | 判别性变异/复跑（M1-green2.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M1-green2.log | - | 0e6e4a8c4280f604820a1c23bbbae14eab6de7bdb5eb9c5f608b14f82fda8314 | CANONICAL |
| EV-14 | 判别性变异/复跑（M1.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M1.log | - | a32d3fcc9d7381d423d8231d3330f354a238da9447f04bd3f7c61be830bc63d6 | CANONICAL |
| EV-15 | 判别性变异/复跑（M2-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M2-green.log | - | 3f1236d83eb8d0540e440cb67cd554ea2cc84c8900f4d3e0766403897eb7ca07 | CANONICAL |
| EV-16 | 判别性变异/复跑（M2.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M2.log | - | 730b85bd6de3dcdfe9e4574d7e252f22f156145f87cf115b4de1d5e212a70c83 | CANONICAL |
| EV-17 | 判别性变异/复跑（M3-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M3-green.log | - | 31e36527ebd7d2dd5d83cb75b3801239397c34f4868fe5c788aed032865f1638 | CANONICAL |
| EV-18 | 判别性变异/复跑（M3.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M3.log | - | d3b2bf351423fd801348785e43fc328535bdd11f04b5e8470d09f2c24dd1650c | CANONICAL |
| EV-19 | 判别性变异/复跑（M4-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M4-green.log | - | 0e6e4a8c4280f604820a1c23bbbae14eab6de7bdb5eb9c5f608b14f82fda8314 | CANONICAL |
| EV-20 | 判别性变异/复跑（M4.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M4.log | - | 6c2f777974e65163b32dbf944ad8a4e8cf76491e43a8768cefc6e663fc19d775 | CANONICAL |
| EV-21 | 判别性变异/复跑（M5-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M5-green.log | - | 432a32b8986b97076de0cf54190f3d140a4be2e6936a47f5dc42a53650c394d0 | CANONICAL |
| EV-22 | 判别性变异/复跑（M5.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M5.log | - | 0bbb2837a580a2a534b13c938592a7b54c7b70d0f34fb8fe3716454286cf3de3 | CANONICAL |
| EV-23 | 判别性变异/复跑（M6a.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M6a.log | - | 0e6e4a8c4280f604820a1c23bbbae14eab6de7bdb5eb9c5f608b14f82fda8314 | CANONICAL |
| EV-24 | 判别性变异/复跑（M6b-green.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M6b-green.log | - | 3f1236d83eb8d0540e440cb67cd554ea2cc84c8900f4d3e0766403897eb7ca07 | CANONICAL |
| EV-25 | 判别性变异/复跑（M6b.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/M6b.log | - | c64e7eed233ae377aebd11c47e01bffd95e7c594b981472ed5fca48ce6ffb71a | CANONICAL |
| EV-26 | 判别性变异/复跑（full-sln.log） | verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/full-sln.log | - | 4274d0f38f1c0240f9ff43c353794a362fa7a7dbd370f63ce36d628244a980bc | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；base `54e5d69db`，实现 `85356c22a`） | NOT_APPLICABLE | — | — | 未创建 linked worktree；`git worktree list` 无本卡新增 |
| temp | `G:\CODEX\New Manga.workspace\temp\residual2-review\`（reviewer pristine 副本 + M1…M6b 日志 + full-sln.log） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\temp\residual2-review\` | `verification/FEA-12-UI-RESIDUAL-2/RESOURCE-MANIFEST.json` | 仓外隔离根；无进程持有；产品/测试不引用；canonical 副本已逐字节归档于 `verification/FEA-12-UI-RESIDUAL-2/logs/reviewer-mutations/**`（EV-12…EV-26）；保留供审计 |
| test-fixture | `FakeHostController.cs`（内存 fake；新增 `RestoreRepopulatesSnapshot` **默认 false**） | NOT_APPLICABLE | — | — | 8 个新用例全为 VM 级；既有 770 个 App 用例零扰动（全量绿）；无二进制 fixture、无真实 IPC |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未读写真实用户数据/AppData/外部卷/真实回收站/原文件；未新增删除帧（既有 ZeroPurge/ZeroBatch 用例仍绿） |
| build-artifact | NOT_APPLICABLE | NOT_APPLICABLE | — | — | `dotnet build/test` 产物留在既有 bin/obj，不入交付 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson`（既有 `WireLogSourceRedactionTests` 副作用） | NOT_APPLICABLE | — | — | 每次全量 .NET 后重写；Lead 全量后 `git checkout -- verification/FEA-09`（EXIT=0）恢复；最终 worktree 仅本卡文件 |

## Closeout Record

- **Closeout date / DSH**：2026-11-08 / DSH（Lead/Architect/Integrator）。
- **终态**：`done`；`integration_commit` = `delivery_head` = **`85356c22a`**（实现 + 测试）；冻结卡 `b7c63bc50`；证据/closeout 提交见 handoff §27。
- **Review 链**：冻结前两轮独立 scope review（session `402ec34a-…`、`986a9e4c-…`）均 **READY-TO-FREEZE**（第二轮独立发现 A′）；实现后独立 Review r1 **approved（P0=0/P1=0/P2=1/P3=5**；session `897f3928-…`），含 7 组变异实测（M1/M2/M3/M4/M5/M6b 共 15 RED；M6a 未变红登记 P3-01）。
- **AC 定稿**：**AC-R1…AC-R6 全 MET**（AC-R3 的 `ShowList` 能力/probe 短路子句仅有结构性保护，按 **L-4** 如实降级表述，不写「回归栅栏已被变异钉住」）。
- **门禁（Lead 亲自实跑）**：build 0/0；全量 pytest **3390 passed / 10 skipped**（不降）；全量 .NET **1691 passed / 0 failed / 96 skipped**（+8 新用例，0 failed）；pins **18/18**；`check.ps1`（默认 + `-TaskPath`）PASS(3w)×2；`generate_api_inventory.py --check` EXIT=0；scope 5 文件 ⊆ allowed_paths、禁止面零 diff；跑后 `verification/FEA-09` 已恢复。
- **P2/P3 处置**：**P2-01**（交付 head 无证据目录）→ 已由本目录（EV-08…EV-26）与 reviewer 日志归档闭合；**P3-01**（`ShowList` 短路子句无判别力）→ 登记 **L-4**，后续候选（补「已加载行 + 能力翻转 + RefreshAsync」用例）；**P3-02**（T2 等待谓词）→ **L-6**；**P3-03**（`ListStatusText` 无 UI 消费者）→ 记录（AC-R6 明文要求，防御性）；**P3-04**（App.Tests 口径）→ 已更正为「778 通过 / 7 跳过 / 总 785」；**P3-05**（回调异常面/重入）→ **L-5**。
- **残余 limitation**：L-2（自动选中副作用）、L-3（死代码另卡）、L-4（短路子句无变异判别）、L-5（异常面/重入，既有结构）、L-6（T2 谓词）、L-7（T7 一处空断言）、L-8（证据级别 VM headless；真实 IPC/L3/L4 **NOT_RUN**）；`FEA-12-UI` 的 L1/L2/L3/L8 原样保留。
- **删除/迁移/归档数量**：0 / 0 / 0（仅新增卡、评审与证据文件；仓外 reviewer scratch 保留不删）。
- **当前指针清理**：PLAN `READY 节点` 回填 `无`、DAG 记 `FEA-12-UI-RESIDUAL-2 done`；STATUS 更新为「无活动 Task + 下一候选」；`task_ledger.py --write` 已重跑。

