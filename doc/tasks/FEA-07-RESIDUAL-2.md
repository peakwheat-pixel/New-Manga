---
id: FEA-07-RESIDUAL-2
title: FEA-07 收口 A（AC2 窗口层 draft owner + 生命周期断言 / AC6 指标与规模负载 / AC8 证据）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R4）；独立 scope review `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md`（session `23a6e437-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §5 拆分与口径修正后冻结）；DSH 2026-11-08 裁决（ADJ §7.10）：0 pin、headless-only
suggested_owner: dsh
owner: fea07-residual2-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审）
depends_on:
  - FEA-07
base_commit: 0a39a78f0
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-07-RESIDUAL-2
allowed_paths:
  - doc/tasks/FEA-07-RESIDUAL-2.md
  - doc/tasks/FEA-07.md
  - doc/reviews/FEA-07-RESIDUAL-2-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-07-RESIDUAL-2-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/**
  - apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/**
  - apps/desktop-avalonia/tests/NewManga.App.Tests/**
  - verification/FEA-07-RESIDUAL-2/**
out_of_scope:
  - 原生 IME、AC5 双屏/拔屏/DPI 矩阵、真实双屏 broker 落位（`NOT_APPLICABLE: 原生交互未执行（保留 NOT_RUN）+ 用户 2026-11-08 授权豁免`）
  - 冻结契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins（只**引用** C-13 SC-D03，**不复述**规则）
  - 不改 `AppearanceCoordinator`/`FrontendSelector`/组合根语义；不改 `NewManga.DesignSystem/**`、`NewManga.Appearance/**`；不改 `Switching/**` 事务逻辑
  - R4b 面（AC1 A03/ACK、AC3 跨进程崩溃、AC4 真实入口）→ `FEA-07-RESIDUAL-3`
  - 真实用户数据/AppData/外部卷/回收站；L3/L4 真机（NOT_RUN）
---

# FEA-07-RESIDUAL-2：FEA-07 收口 A（headless，0 pin）

> **状态 `ready`**（base `0a39a78f0`；0 pin；headless-only）。目标：完成 `FEA-07` AC2（窗口层 draft owner + 生命周期）、AC6（指标与规模负载）、AC8（证据）；AC1/AC3/AC4 由 `FEA-07-RESIDUAL-3`（R4b）承接，**两卡都 MET 后 FEA-07 才翻 done**。
> **AC2 冻结解释（DSH，scope review §2）**：「第二窗口」= **独立 OS 窗口**（`WindowBroker.WindowRole.Floating`）→ 只读或独立 Session；「同 Session 主画布 + 浮动面板」= **同一窗口内浮动面板**→ 按 **C-13 SC-D03**（`doc/plan/FEA-C13_DRAFT_PROTECTION_DRAFT.md:55-66`）共享 DraftId 可编辑。owner 键 = `(SessionId, RegionId)`；跨 Session ReadOnly；转移显式。**只引用不复述 SC-D03。**

## Acceptance Criteria（冻结）

- [x] **AC-R4a-1（AC2 窗口层 draft owner）**：新增 `(SessionId,RegionId)` 窗口层 owner registry（App/Presentation 层）：同一 key 跨 **OS 窗口** 只有一个 owner；第二个 `Floating` 窗口 claim 得 `ReadOnly`，其写入尝试被 typed 拒绝且 **Host 零写入**（`FakeHostController` 计数为 0）；同窗口内浮动面板共享同一 `DraftId`（**不得**拒绝，符合 SC-D03）；显式转移后 owner 互斥且幂等；`Release` 后可再 claim；并发 claim 只有一个 owner。 <<MET>>
- [x] **AC-R4a-2（AC2 生命周期）**：窗口关闭/重建/切换前后 `FakeHostController.StartCalls`/`StartRequests`/`LifecycleLog` 逐项不变；`PresentationWindow` 不调用 `StartAsync`/`DisposeAsync`（计数 + 事件断言）；补窗口级判别测试。 <<MET>>
- [x] **AC-R4a-3（AC6 指标与规模）**：热切换 p95 门槛 **1000 ms 不变**（W-5 冻结），断言改为 **3 次独立运行的 p95 中位数 ≤ 1000 ms**，记录每轮 p95/max；新增 **`uiThreadSchedulingGapMs`**（UI 线程心跳最大间隔）并首轮基线定标后写死阈值；**真实规模合成负载** N∈{50,200,500}（`FakeHostController.ReadySnapshot`），记录 p50/p95；冷启动单独记录不入门槛。 <<MET>>
- [x] **AC-R4a-4（AC8 证据 + 治理）**：EV/Resource Manifest/门禁日志；`FEA-07` AC1/AC2/AC3/AC4/AC6/AC8 行 **append-only** before/after 登记（本卡先登记 AC2/AC6/AC8，R4b 完成后再登记 AC1/AC3/AC4）；AC5/AC1-IME/AC2-双屏三条 **NA 只写一次**（在 AC5 行）；`check.ps1` PASS、pins 18/18（0 pin）；pytest ≥3395/10、.NET ≥1733/0/102 不降。 <<MET>>

## 实现口径

1. 新增 `Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs`（线程安全、不可变结果）；`WindowBroker` 薄转发（`TryClaimDraft/ReleaseDraft/RequestDraftTransfer`），保持现有 API 不破。
2. `PresentationWindow` 暴露 `DraftOwnership`；`Floating` 窗口构造时强制 `CanEdit=false`（只读策略）。
3. **只引用** C-13 SC-D03（给行号），禁止复述规则句（双权威判例 `FEA-C10-r1.md:83`）。
4. AC6 指标：保留既有 p95 采集（4 预热 + 20 测量），改 3 次取中位；新增心跳指标与基线文件；不得改 1000 ms 门槛。
5. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。
6. **DSH 2026-11-08 扩域批准**：AC-R4a-1 的窗口级暴露需要改 `apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`（全仓唯一 `PresentationWindow`，不在 `NewManga.Presentation.Avalonia`）；批准**仅该单文件**；实际改动 **+26/−5（净 +21 行，纯加法，无功能删除）**，未改 `App.axaml.cs`/组合根语义，`allowed_paths` 由 DSH 在 closeout 落盘。
7. **r1 返修口径（2026-11-08，独立 Review approved P0=0/P1=0/P2=4/P3=12）**：见下节「r1 返修」；AC-R4a-1…4 判定不变（加固而非扩域）。

## 行文口径（红线）

- 不得写「FEA-07 完全实现 / 全部 limitation 关闭 / 可发布」；只写「AC2/AC6/AC8 达成；AC1/AC3/AC4 由 R4b 承接；原生项 NA（NOT_RUN）」。
- `NOT_RUN` 不得写成 PASS；像素/UI 观感不得作为 AC 判据。

## r1 返修（2026-11-08）

独立 Review r1 = **approved**（P0=0/P1=0/P2=4/P3=12）；本轮只做 3 项必修 + 1 项证据补齐，AC-R4a-1…4 判定不变（加固而非扩域）。

| # | finding | 修复 | 判别测试 |
|---|---|---|---|
| P2-003 | `PresentationWindow` 构造不注册角色，registry 对未知 token 默认 `Main` ⇒ 先构造 `Floating`、后 transfer 可让只读 token 成为 owner（原 owner 失编辑） | `DraftOwnershipScope` 构造即 `RememberWindow(WindowToken, Role)`；`RequestTransfer` 对**未注册 target** typed 拒绝（新增 `DraftDenialReason.UnknownWindow`），不再猜测角色 | `DraftOwnershipScopeTests.ScopeRegistersItsRoleAtConstruction_SoAFloatingTransferTargetIsRefusedBeforeAnyClaim`（transfer-before-claim 判别）、`ExplicitTransfer_ToUnknownWindow_IsTypedRefusalWithoutGuessingARole`、`DraftOwnershipWindowTests.TransferToAConstructedButUnclaimedFloatingWindow_IsRefusedAndTheOwnerKeepsEdit`（原 owner 不被夺走） |
| P3-001 | 转移后旧 owner 重复 transfer 仍返回 `CanEdit=true` | 幂等分支按**请求方**给 `CanEdit`：旧 owner 重复得 `Retained` + `CanEdit=false` + `NotOwner`；当前 owner 重复仍 `Retained` 且可编辑 | `ExplicitTransfer_IsIdempotent`、`DraftOwnershipWindowTests.ExplicitTransferBetweenWindows_MovesOwnershipExclusively` |
| P3-010 | `EnsureWritable` 只校验 `result.CanEdit`，可被过期/他人 result 绕过 | 增加身份与实时 owner 校验：`result.WindowToken == scope.WindowToken` 且 `registry.IsCurrentOwner(result.Key, scope.WindowToken)`；不满足抛 typed（他人/过期 → `NotOwner`），并保留原 read-only 拒绝原因 | `DraftOwnershipScopeTests.EnsureWritable_RejectsAResultIssuedToAnotherWindow`、`EnsureWritable_RejectsAStaleResultAfterATransfer`、`EnsureWritable_AcceptsTheCurrentOwnerResult` |
| P3-008 | 类注释受压规则句（“panels share one DraftId” 等），有 C-13 双权威风险 | 删除复述，改为 API 面描述 + 只引用 C-13 SC-D03 行号（`FEA-C10-r1.md:83` 判例） | 人工核对 `DraftOwnershipRegistry.cs` 类级/`TryClaim` 注释 |
| P2-004 | `uiThreadSchedulingGapMs` 400 ms 的定标原始运行不在证据 | 新增 `verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1`（3 轮独立重跑，落盘 `evidence/ui-gap-calibration-r4a.json` + `logs/ui-gap-calibration.log` + 每轮日志）；**门槛仍 400 ms**（worst 249.44 ms，余量 37.64% ≥ 10%） | 定标 JSON `verdict="KEEP 400 ms"`、`worstGapMs=249.44`、`marginPercent=37.64` |
| P2-001 | 卡面/README 「+21 行纯加法」口径不准 | 改为「+26/−5（净 +21 行，纯加法，无功能删除）」 | 本卡「实现口径 6」+ `verification/FEA-07-RESIDUAL-2/README.md` |
| P2-002 | 生产组合根未注入共享 registry 等事实未明示 | 见下节「Residual / 待接线（L-R4a-1）」 | — |

**变异自检 ⑤（r1 新增）**：删除 `DraftOwnershipScope` 构造时的角色注册 → `ScopeRegistersItsRoleAtConstruction_…`（transfer-before-claim）与窗口级同名用例 **RED**（`UnknownWindow` vs `FloatingWindowReadOnly`；纯测试 3 failed / 68 passed）→ 复原 sha256 `c84cac5a…` MATCH → 复绿（71/0/0）。明细见 `verification/FEA-07-RESIDUAL-2/mutation-selfcheck.md` §⑤。

## Residual / 待接线（L-R4a-1）

- **P2-002 事实登记**：AC2 的**窗口层机制**已 MET（owner registry + typed 只读拒绝 + 生命周期不变）；但**生产组合根**当前只有一个 `PresentationWindow`，**未注入共享 `DraftOwnershipRegistry`**，`WindowBroker.RegisterSecondary` **零调用**，也**没有 Floating 生产实例** ⇒ 跨窗口（真实双屏/浮窗）场景尚未在生产路径可见。
- **L-R4a-1（re-home）**：跨窗口 ownership 的生产接线（组合根注入共享 registry + Floating/Inspector 真实窗口 + 多窗口关闭/重建生命周期）由**多窗口功能卡**承接；本卡只交付窗口层机制与 headless 判别证据，不写「跨窗已生产可用」。
- 与 NA 的关系：AC2「真实双屏 broker 落位」的 NA 登记仍只在 `doc/tasks/FEA-07.md` 的 AC5 行写一次（本卡不重复）。

## Canonical Evidence

> `commit`：实现/测试文件填其所在提交 `85207730e`；证据文件填 `-` 并以**工作树字节 sha256** pin（2026-11-08 r1 返修后重算；证据文件在同分支 `fix(fea-07-residual-2): r1 返修…` 提交）。证据索引：`verification/FEA-07-RESIDUAL-2/README.md`。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-R4A-01 | AC-R4a-1（owner store + scope） | apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs | 85207730e | c84cac5a41fd146eb9b96570f0656e5354d27442796d3b47af9a31b1383dac67 | SOURCE_PIN |
| EV-R4A-02 | AC-R4a-1（broker 薄转发） | apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/WindowBroker.cs | 85207730e | 4ac2be6167b0175da316fb5bd9089907c4bca1bdc9dfcdf42115139a7cb21905 | SOURCE_PIN |
| EV-R4A-03 | AC-R4a-1（窗口暴露 + Floating 只读） | apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs | 85207730e | 5fef0cbd8588f7dbed48fe386ffb333c74fa407d3612b695c2d2fa5865ef839c | SOURCE_PIN |
| EV-R4A-04 | AC-R4a-1（registry 23） | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/DraftOwnershipRegistryTests.cs | 85207730e | ae793615aa1cc1b24bafba5940f1400876e656900f9ade876c9fa52cc7a7e0b6 | SOURCE_PIN |
| EV-R4A-05 | AC-R4a-1（broker 转发 5） | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/WindowBrokerDraftForwardingTests.cs | 85207730e | bae9656ff9bf54dc6de9bbb82c886c558305ab3e6f68dfc07b7667231ce670b9 | SOURCE_PIN |
| EV-R4A-06 | AC-R4a-1（窗口级 8，Host 零写入 + transfer-before-claim） | apps/desktop-avalonia/tests/NewManga.App.Tests/DraftOwnershipWindowTests.cs | 85207730e | 7e993433d611bbe9a642b026b800d7eae3415ae14ae326ba55251c79372a2ec1 | SOURCE_PIN |
| EV-R4A-07 | AC-R4a-2（生命周期 3） | apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationWindowHostLifecycleTests.cs | 85207730e | 7e8aaafae256f29a55907159ce9fae2be608d2c224c8f26e38c64327f990ee4d | SOURCE_PIN |
| EV-R4A-08 | AC-R4a-3（三次中位 + UI gap + 规模） | apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs | 85207730e | 5d90f84f502cc3e6b210a0211fd458923e69b4af9d1c9ab7c9ee767e7c62be21 | SOURCE_PIN |
| EV-R4A-09 | AC-R4a-1/2（测试侧计数与写入日志） | apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs | 85207730e | 0754c9163c6e307a6dd022ca7e99d2cd9b07f903b3c41261327ffe3eb726d6c2 | SOURCE_PIN |
| EV-R4A-10 | AC-R4a-4（证据索引） | verification/FEA-07-RESIDUAL-2/README.md | - | 254c994ba19bdadbf11530d909f98c65d9ac98c7df9df7c341e125ddbb31c6c1 | CANONICAL |
| EV-R4A-11 | AC-R4a-4（Resource Manifest） | verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json | - | 45a00ec301b7552bdd0d3c784d060321045a94362c7648338b37b293b8e4cf63 | CANONICAL |
| EV-R4A-12 | AC-R4a-3（热切换基线 JSON） | verification/FEA-07-RESIDUAL-2/evidence/performance-baseline-r4a.json | - | 44b47fce050903532affa8ccf3e5077bafe1e3f899cf32632aa448266390e77b | CANONICAL |
| EV-R4A-13 | AC-R4a-3（规模 JSON） | verification/FEA-07-RESIDUAL-2/evidence/performance-scale-r4a.json | - | 0b5ba1fb770231bb7508492372f07dfee469ad784891c0870c131bb789ff593d | CANONICAL |
| EV-R4A-14 | AC-R4a-4（定向日志） | verification/FEA-07-RESIDUAL-2/logs/directed-presentation-tests.log | - | 8598dbc4d102543ebc7308a55fab14f6a8c39f9eebe48f8dce633955afef9bff | CANONICAL |
| EV-R4A-15 | AC-R4a-4（App 日志） | verification/FEA-07-RESIDUAL-2/logs/app-tests.log | - | e96a8e60df65ef50124b745186aa3a74ac1d25e7e76e73dfdd3decfa3f4e5924 | CANONICAL |
| EV-R4A-16 | AC-R4a-4（全量日志） | verification/FEA-07-RESIDUAL-2/logs/full-solution-tests.log | - | bd36e46c556fb00a524eb7696572f859adbf16493696a808c380ea7b00c44e0b | CANONICAL |
| EV-R4A-17 | AC-R4a-4（性能运行日志） | verification/FEA-07-RESIDUAL-2/logs/performance-run.log | - | 9e6b19cec4ecd5de791d15b366ab0d7dd86d9512ad70dff11aa528a6a770b36f | CANONICAL |
| EV-R4A-18 | AC-R4a-4（门禁日志：check.ps1 + pins） | verification/FEA-07-RESIDUAL-2/logs/governance.log | - | acaab6eebda9c8d0ecb317e2dfc6538c6099b5eeb31178fd6757911e3db123dc | CANONICAL |
| EV-R4A-19 | AC-R4a-4（跨程序集 race 原始摘录） | verification/FEA-07-RESIDUAL-2/logs/full-solution-first-run-cross-assembly-race.txt | - | eb874828e05e5de51e985e80430d77967d0cc533b8a231be016ddf6903d145f1 | CANONICAL |
| EV-R4A-20 | AC-R4a-1/2/3（变异自检 5 组） | verification/FEA-07-RESIDUAL-2/mutation-selfcheck.md | - | 6205bb7b46af277052ad26ce37b4247c2291bd6fce2fbbeec3afe630c055bdb7 | CANONICAL |
| EV-R4A-21 | AC-R4a-1（r1 scope 5：构造注册/身份绑定/过期 result） | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/DraftOwnershipScopeTests.cs | 85207730e | f772ae23ad6c34cb0be765390e95ff9fd0c0d277dcde62ac776ba761491bf89a | SOURCE_PIN |
| EV-R4A-22 | AC-R4a-3（r1 P2-004 UI gap 3 轮定标 JSON） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-r4a.json | - | d7795c74443175c647244f060a6dd65569b798576b62d4b593afb02cc3e78e1f | CANONICAL |
| EV-R4A-23 | AC-R4a-3（r1 P2-004 定标脚本） | verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1 | - | d722df640796fe4274c52327764f5fef974c012e4a226d243f2b9f0766b2bfa9 | CANONICAL |
| EV-R4A-24 | AC-R4a-3（r1 P2-004 定标日志） | verification/FEA-07-RESIDUAL-2/logs/ui-gap-calibration.log | - | 1f84a0585a38393ea88e876814173e86567904a31419f314bd4faeed901cb660 | CANONICAL |
| EV-R4A-25 | AC-R4a-4（全量 hit-test flake 原始摘录） | verification/FEA-07-RESIDUAL-2/logs/full-solution-r1-flake-hit-test.txt | - | 3ff4f00e3f817f7f3aba6676a9e9cfe54a2f2ce473eae9551b5948064a2ad367 | CANONICAL |
| EV-R4A-26 | AC-R4a-4（Lead r1 门禁历史日志，返修前 head） | verification/FEA-07-RESIDUAL-2/logs/gates-lead.log | - | 754f6c5e3c701dcc6c821eab811398c40f8f9749cf138d5ebe0e69d270f2ff73 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `0a39a78f0`，impl `85207730e`） | NOT_APPLICABLE | — | — | 未创建/未删除 linked worktree；main 内联实施 |
| evidence | `verification/FEA-07-RESIDUAL-2/**` | PRESERVE_REFERENCED | `verification/FEA-07-RESIDUAL-2` | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | 被本卡 Canonical Evidence 与 `doc/tasks/FEA-07.md` R4a 回填引用；原地保留，不归档 |
| temp | `%TEMP%/nm-fea07-perf-*`、`%TEMP%/nm-fea07-draft-window-*`、`%TEMP%/nm-fea07-window-lifecycle-*` | NOT_APPLICABLE | — | — | 测试临时根（appearance store / switch journal / theme home），测试 Dispose 清理；不写仓库或用户数据 |
| test-fixture | `tests/NewManga.App.Tests/FakeHostController.cs` | NOT_APPLICABLE | — | — | 仅测试侧加法探针（`DisposeCalls`/`DisposeException`/`DraftWriteLog`），生产行为不变 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未触碰真实 `%APPDATA%`/用户源文件/外部卷/回收站 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson` | NOT_APPLICABLE | — | — | 既有副作用（`NewManga.CoreClient.Tests` 全量运行时重写）；每次全量后 `git checkout -- verification/FEA-09`，零 diff |
| tool | `verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1` | PRESERVE_REFERENCED | `verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1` | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | 卡内定标脚本（3 轮独立重跑）；只写本证据目录，不触用户数据；原地保留 |
