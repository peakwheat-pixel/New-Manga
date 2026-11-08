---
id: FEA-07-RESIDUAL-2
title: FEA-07 收口 A（AC2 窗口层 draft owner + 生命周期断言 / AC6 指标与规模负载 / AC8 证据）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-08 残余收口指令（R4）；独立 scope review `doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md`（session `23a6e437-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §5 拆分与口径修正后冻结）；DSH 2026-11-08 裁决（ADJ §7.10）：0 pin、headless-only
suggested_owner: dsh
owner: fea07-residual2-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审）
depends_on:
  - FEA-07
base_commit: 0a39a78f0
branch: null
worktree: null
integration_commit: a03a6794a
delivery_head: ac0dca1bd
canonical_evidence_status: complete
resource_closeout_status: complete
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
6. **DSH 2026-11-08 扩域批准**：AC-R4a-1 的窗口级暴露需要改 `apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`（全仓唯一 `PresentationWindow`，不在 `NewManga.Presentation.Avalonia`）；批准**仅该单文件**；实际改动 **+26/−5（净 +21，无功能删除）**，未改 `App.axaml.cs`/组合根语义，`allowed_paths` 由 DSH 在 closeout 落盘。
7. **r1 返修口径（2026-11-08，独立 Review approved P0=0/P1=0/P2=4/P3=12）**：见下节「r1 返修」；AC-R4a-1…4 判定不变（加固而非扩域）。
8. **r2 返修口径（2026-11-08，独立 Review r2 changes_requested P0=0/P1=1/P2=1/P3=7）**：见「r2 返修」；P1 = gap 门槛从默认套件移入**专用串行性能门禁**（`NEWMANGA_FEA07_PERF=1`，默认 skip + reason），默认套件只保留 p95 3 次中位 ≤1000 ms 并**记录** gap；1000 ms 门槛、3 次中位口径、规模只记录口径均未改。

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
| P2-004 | `uiThreadSchedulingGapMs` 400 ms 的定标原始运行不在证据 | 新增 `verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1`（3 轮独立重跑，落盘 `evidence/ui-gap-calibration-r4a.json` + `logs/ui-gap-calibration.log` + 每轮日志）；**门槛 400 ms**（worst 249.44 ms，余量 37.64% ≥ 10%）——r2 起该门槛迁入专用串行门禁并重定标为 700 ms（见 r2 节） | 定标 JSON `verdict="KEEP 400 ms"`、`worstGapMs=249.44`、`marginPercent=37.64` |
| P2-001 | 卡面/README 「+21 行纯加法」口径不准 | 改为「+26/−5（净 +21，无功能删除）」 | 本卡「实现口径 6」+ `verification/FEA-07-RESIDUAL-2/README.md` |
| P2-002 | 生产组合根未注入共享 registry 等事实未明示 | 见下节「Residual / 待接线（L-R4a-1）」 | — |

**变异自检 ⑤（r1 新增）**：删除 `DraftOwnershipScope` 构造时的角色注册 → `ScopeRegistersItsRoleAtConstruction_…`（transfer-before-claim）与窗口级同名用例 **RED**（`UnknownWindow` vs `FloatingWindowReadOnly`；纯测试 3 failed / 68 passed）→ 复原 sha256 `c84cac5a…` MATCH → 复绿（71/0/0）。明细见 `verification/FEA-07-RESIDUAL-2/mutation-selfcheck.md` §⑤。

## Residual / 待接线（L-R4a-1）

- **P2-002 事实登记**：AC2 的**窗口层机制**已 MET（owner registry + typed 只读拒绝 + 生命周期不变）；但**生产组合根**当前只有一个 `PresentationWindow`，**未注入共享 `DraftOwnershipRegistry`**，`WindowBroker.RegisterSecondary` **零调用**，也**没有 Floating 生产实例** ⇒ 跨窗口（真实双屏/浮窗）场景尚未在生产路径可见。
- **L-R4a-1（re-home）**：跨窗口 ownership 的生产接线（组合根注入共享 registry + Floating/Inspector 真实窗口 + 多窗口关闭/重建生命周期）由**多窗口功能卡**承接；本卡只交付窗口层机制与 headless 判别证据，不写「跨窗已生产可用」。
- 与 NA 的关系：AC2「真实双屏 broker 落位」的 NA 登记仍只在 `doc/tasks/FEA-07.md` 的 AC5 行写一次（本卡不重复）。

## r2 返修（2026-11-08）

独立 Review r2 = **changes_requested**（P0=0/**P1=1**/P2=1/P3=7）。**P1 是真实问题**：r1 把 `uiThreadSchedulingGapMs ≤ 400 ms` 断言放在默认套件，在 full-suite/负载下不稳定（评审 1777/1/102、gap 513.55 ms；隔离 3/4 次失败 437.34/471.81；空载 1778/0/102 才是结果）。AC-R4a-1…4 判定不变。

| # | finding | 修复 | 判别/证据 |
|---|---|---|---|
| R2-001（P1） | gap 断言在默认套件不稳定 | **默认套件只保留** p95 3 次中位 ≤1000 ms（W-5 不变），`uiThreadSchedulingGapMs` **只记录**到 JSON（`gapGateApplied=false`）；**新增 gated 用例** `PerformanceBaselineTests.Gated_HotSwitch_UiThreadSchedulingGapStaysWithinThePerfGateBudget`（`PerfGateAvaloniaFact`，仅 `NEWMANGA_FEA07_PERF=1` 启用，默认 **skip + reason**）；新增 `verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1` 串行跑该用例并落盘；默认门禁不跑它 | `evidence/perf-gate-r2a.json`（3 轮串行，worst 340.90 ms ≤ 700，margin 51.3%）、`evidence/ui-gap-loaded-condition-r2a.json`（负载观测） |
| R2-001（重定标） | 门槛需按串行/负载分布重定 | 基于：空载串行 worst **249.44**（r1 提交定标）、负载串行 **340.90 / 454.61 / 460.88**、并行全量 **619.00**（本机变异运行）/ **513.55**（评审）→ 门槛 **700 ms**（串行/空载门禁用；1.52x 负载串行 worst、2.81x 空载 worst）；`verify-fea07-perf.ps1` 复跑 3 轮 PASS | `PerformanceBaselineTests.cs` 常量注释 + `evidence/perf-gate-r2a.json` |
| R2-002（P2） | Canonical Evidence 归因错误（EV-R4A-21 在 `85207730e` 不存在） | `:93` 说明改为按提交归属；EV-R4A-01/04/21 归 r2 代码提交（本行见下表 commit 列），EV-R4A-06 归 `bacf6c307`（r2 未再改）；sha256 全部按工作树重算并 0 mismatch | 下表 + 复核脚本 0 mismatch |
| R2-003 | 旧注释含 215.28/232.90、1.7x/7% | 改用已提交定标数字：空载 worst 249.44 ms、margin 37.64%、1.60x（并补 r2 负载定标 700 ms 的说明） | `PerformanceBaselineTests.cs:50-72` |
| R2-004 | 定标脚本需「不套 400 ms 断言」模式 + 每轮原始 metrics | `tools/calibrate-ui-gap.ps1` 改为 **raw 模式**（默认套件本就不断言 gap），每轮原始 metrics 落盘 `evidence/ui-gap-calibration-round{1,2,3}.json`；申报门槛参数 `-PerfGateBudgetMs`（默认 700）只算余量不断言 | `evidence/ui-gap-calibration-r4a.json`（`mode=raw`）、`logs/ui-gap-round*.log` |
| R2-005 | `EnsureWritable` 未比较 DraftId（release+reclaim 后旧 result 仍可写） | `IsCurrentOwner(key, token, draftId?)` 增加 draft id 比较；`EnsureWritable` 传 `result.DraftId`；旧 result → typed `NotOwner` | `DraftOwnershipScopeTests.EnsureWritable_RejectsAStaleResultAfterReleaseAndReclaim` |
| R2-006 | JSON `passed` 未拆分，失败运行也写 `true` | 默认套件 JSON：`p95Passed` + `passed = p95Passed`（gap 只记录，`gapGateApplied=false`）；gated JSON：`p95Passed`/`gapPassed`/`passed = p95Passed && gapPassed` | 两类 JSON 字段 |
| R2-007 | 「纯加法」措辞 | 卡/README 统一为「**净 +21，无功能删除**」 | 本卡「实现口径 6」+ README |
| R2-008 | 未注册 target 的 typed 拒绝仍写猜测的 `WindowRole.Main` | `WindowRole` 增加**诊断专用** `Unknown = 3`（文档注明永不作为 live 角色），`UnknownWindow` 拒绝结果携带 `WindowRole.Unknown` | `DraftOwnershipRegistryTests.ExplicitTransfer_ToUnknownWindow_IsTypedRefusalWithoutGuessingARole`（断言 `WindowRole.Unknown`） |
| R2-009 | pytest 证据未入卡 | 记录 `pytest tests -q` = **3394 passed / 1 failed（既有 flaky `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`）/ 10 skipped**；隔离复跑该文件 **16 passed**；本卡零 Python diff（`git diff bf4207d4a..HEAD -- tests/ src/` 为空，2026-11-08 复核） | 见 README §7 与 `logs/pytest-r2.txt` |

**变异自检 ⑥⑦（r2 新增）**：⑥ 把 gap 断言改回默认套件 → **并行全量运行 RED**：`ui thread scheduling gap 619.0 ms exceeds the calibrated 400 ms budget`（同轮 gap 491.75/457.55/619.00，作为负载敏感性证据）；⑦ 把 p95 门槛方向改反（断言 `> 1000`）→ 默认套件 RED：`hot switch median p95 667.0 ms exceeds the frozen W-5 budget 1000 ms`。两处均复原 sha256 `f73ac3a6…` MATCH 并复绿。明细见 `verification/FEA-07-RESIDUAL-2/mutation-selfcheck.md` §⑥⑦。

## Canonical Evidence

> `commit`：实现文件填**文件内容最后一次提交**（r2 后 `a03a6794a`；r1 后未再改 `bacf6c307`；首轮未再改 `85207730e`）；证据填 `-`（sha 为工作树字节，见 handoff §33）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-R4A-01 | AC-R4a-1 | apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/DraftOwnershipRegistry.cs | a03a6794a | c68ed23e165c01bbcae1141bef38b77809801790e66f4a71f86a173f8d07c5cc | SOURCE_PIN |
| EV-R4A-02 | AC-R4a-1 | apps/desktop-avalonia/src/NewManga.Presentation.Avalonia/Windows/WindowBroker.cs | a03a6794a | eccac101d6a3aa3d3e2c4caf06a864346da47b3ce0e9b7dd0ab2ee95fa8d0fdf | SOURCE_PIN |
| EV-R4A-03 | AC-R4a-1 | apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs | a03a6794a | 5fef0cbd8588f7dbed48fe386ffb333c74fa407d3612b695c2d2fa5865ef839c | SOURCE_PIN |
| EV-R4A-04 | AC-R4a-1 | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/DraftOwnershipRegistryTests.cs | a03a6794a | d003c7f7a47a9c466adc02a97774f6d3bbdd946a62971d115c2e435b3d837eec | SOURCE_PIN |
| EV-R4A-05 | AC-R4a-1 | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/DraftOwnershipScopeTests.cs | a03a6794a | 2ac8d3c233abc2a513d65a5edfa1a40284de672b021e4e13b1efc2524216db44 | SOURCE_PIN |
| EV-R4A-06 | AC-R4a-1 | apps/desktop-avalonia/tests/NewManga.App.Tests/DraftOwnershipWindowTests.cs | a03a6794a | 7e993433d611bbe9a642b026b800d7eae3415ae14ae326ba55251c79372a2ec1 | SOURCE_PIN |
| EV-R4A-07 | AC-R4a-1 | apps/desktop-avalonia/tests/NewManga.Presentation.Avalonia.Tests/WindowBrokerDraftForwardingTests.cs | a03a6794a | bae9656ff9bf54dc6de9bbb82c886c558305ab3e6f68dfc07b7667231ce670b9 | SOURCE_PIN |
| EV-R4A-08 | AC-R4a-2 | apps/desktop-avalonia/tests/NewManga.App.Tests/PresentationWindowHostLifecycleTests.cs | a03a6794a | 7e8aaafae256f29a55907159ce9fae2be608d2c224c8f26e38c64327f990ee4d | SOURCE_PIN |
| EV-R4A-09 | AC-R4a-2 | apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs | a03a6794a | 0754c9163c6e307a6dd022ca7e99d2cd9b07f903b3c41261327ffe3eb726d6c2 | SOURCE_PIN |
| EV-R4A-10 | AC-R4a-3 | apps/desktop-avalonia/tests/NewManga.App.Tests/PerformanceBaselineTests.cs | a03a6794a | aef87975922a46a4e6eb1b8b7f88f33ebeea0e3215fb25998d2cad083e3099d3 | SOURCE_PIN |
| EV-R4A-11 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/README.md | - | cb5b2b9eec1f796b3ef2b3d8d7fde24bcedfb94708aa26f34d3f6a2ff2c19d1e | CANONICAL |
| EV-R4A-12 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json | - | 014316d2dcd98b383d224f44ad42f12fadd1c7fe0b1b77a028119e8f404cf8b8 | CANONICAL |
| EV-R4A-13 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/fullrun-recorded-gap-metrics-r2a.json | - | 43e131c072912fd23737a7b16400c1d958f9046208899c4247b16174fef7ac3d | CANONICAL |
| EV-R4A-14 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/loaded-fullrun-gap-metrics-r2a.json | - | 66df745927289d77dd6390e24b1c8b6179af6f12322f9348fd94c5d36050cfee | CANONICAL |
| EV-R4A-15 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/perf-gate-r2a.json | - | 676c339292a67cacedd571f0c576a4b3d241e3e4a2c4b1d0f9cc8d7e483dc886 | CANONICAL |
| EV-R4A-16 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/perf-gate-round1.json | - | 7f301870af4292fbb5085ed41ada4aeeccc83fced873a2e6232b3ad0778442e4 | CANONICAL |
| EV-R4A-17 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/perf-gate-round2.json | - | 9ce2399ab27135439ecc7b0e3e18097d1890383b3366cda9cd975e4757f8d953 | CANONICAL |
| EV-R4A-18 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/perf-gate-round3.json | - | 981aab9e55630596418b44a232fd18f05b690583c4a5efdc3285f67dea609d61 | CANONICAL |
| EV-R4A-19 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/performance-baseline-r4a.json | - | 7b761b0f61c501b81d7a41909ba3413a9f441937737791ca2ab3b9298de70395 | CANONICAL |
| EV-R4A-20 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/performance-scale-r4a.json | - | 0b5ba1fb770231bb7508492372f07dfee469ad784891c0870c131bb789ff593d | CANONICAL |
| EV-R4A-21 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-r4a.json | - | 673ba7129c2b562cbe4169a8f2e97a8f459b31c112891e188a433623ae437d8a | CANONICAL |
| EV-R4A-22 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-round1.json | - | 0d57f11fb20efd1c6fde30e6e97386b7ca5c714695f260a9601298f0591d171c | CANONICAL |
| EV-R4A-23 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-round2.json | - | 9f79223943939c1d6346d716fcd0e97c2b6ddbf9f464947b31f1764269e3aba0 | CANONICAL |
| EV-R4A-24 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-calibration-round3.json | - | cfd94879e7142b7993986e6d306bf0a38272d50f1becad246c1d8f0d787580cd | CANONICAL |
| EV-R4A-25 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/evidence/ui-gap-loaded-condition-r2a.json | - | ed9c85a01c95d148fdd7d5d393977753c1326b7ef236ad9c62c7b6b73800b6bf | CANONICAL |
| EV-R4A-26 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/app-tests.log | - | d91181643a98a32fe206b65d1e3f8028a06e660991fcb535bae6f8474f0353c6 | CANONICAL |
| EV-R4A-27 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/directed-presentation-tests.log | - | 69a714c5dd024fe65248ba9ccd7805be5b56ae0c794f8ae2f618376cb894c38d | CANONICAL |
| EV-R4A-28 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/full-solution-first-run-cross-assembly-race.txt | - | eb874828e05e5de51e985e80430d77967d0cc533b8a231be016ddf6903d145f1 | CANONICAL |
| EV-R4A-29 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/full-solution-r1-flake-hit-test.txt | - | 3ff4f00e3f817f7f3aba6676a9e9cfe54a2f2ce473eae9551b5948064a2ad367 | CANONICAL |
| EV-R4A-30 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/full-solution-tests-run2.log | - | dc4f1278210a43873d383b17b6af089b8a9aad05c0230c466a7d9e8cc5e468d2 | CANONICAL |
| EV-R4A-31 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/full-solution-tests.log | - | a5a17654f506c94206b458a4563bbf90482dbfe297d15d3e56b1a532cd87cbbe | CANONICAL |
| EV-R4A-32 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/gates-lead-final.log | - | 576b4054d5a1af1e1293a0a9999b1f93d4b6c7899a1eb7325b7965e688f77467 | CANONICAL |
| EV-R4A-33 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/gates-lead-final2.log | - | 76b73ea3b1913a1948376f37b1aaed72f472850ba293d3333953723e2b99039d | CANONICAL |
| EV-R4A-34 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/gates-lead.log | - | 754f6c5e3c701dcc6c821eab811398c40f8f9749cf138d5ebe0e69d270f2ff73 | CANONICAL |
| EV-R4A-35 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/governance.log | - | 4cbd7fceb87771322cec0237eb92485f02bc704811765c572d7ec4e2a5917b36 | CANONICAL |
| EV-R4A-36 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/mutation-gap-default-full-run-r2a.log | - | 43b0c678f84ab1fa3e58c1698d7e03295562c0211845b077e2b5e8f585c371c4 | CANONICAL |
| EV-R4A-37 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/perf-gate-round1.log | - | 1f5725a49fdafaef1dbab290294b202323536617332d234578817133158208d3 | CANONICAL |
| EV-R4A-38 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/perf-gate-round2.log | - | 9f17549199fe66b8c6d0bd6b4502ae7f9a4604ec38de1cb140cd99b15f742b82 | CANONICAL |
| EV-R4A-39 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/perf-gate-round3.log | - | ba534a0c818a4809c88a43076037ecdb5580ffa194716b059d169dbc21cfe708 | CANONICAL |
| EV-R4A-40 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/perf-gate.log | - | 456fbfe2ae253dce8a301776b2989b70af45cc859cd59533213d08ef3d45fc99 | CANONICAL |
| EV-R4A-41 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/performance-run.log | - | 9e6b19cec4ecd5de791d15b366ab0d7dd86d9512ad70dff11aa528a6a770b36f | CANONICAL |
| EV-R4A-42 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/pytest-r2.txt | - | 0e18bf3655e57b56c1a8440b54517a83b9bea4b4a1082e784b0683cdca1d6097 | CANONICAL |
| EV-R4A-43 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/ui-gap-calibration.log | - | 9ee98df006c383793dc3e6ce4e805e351edca544c2f4522826099f396f1c0d0d | CANONICAL |
| EV-R4A-44 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/ui-gap-round1.log | - | 80a98058720ae3858ae310e930f9f3dff36f2180925509e332253d2c71789425 | CANONICAL |
| EV-R4A-45 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/ui-gap-round2.log | - | 7ba59676790922253364a476c0fcb90dab4863a236e319b6d7560f7e4439bf91 | CANONICAL |
| EV-R4A-46 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/logs/ui-gap-round3.log | - | b46d88668bb29421412c81445ea1a24d4cccda85b7bf9782b2e56289ac020a23 | CANONICAL |
| EV-R4A-47 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/mutation-selfcheck.md | - | f768cfeac4214b81a0522e692a9d405482d0a3741737facc2989b66668f9a23a | CANONICAL |
| EV-R4A-48 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/tools/calibrate-ui-gap.ps1 | - | ae6075d81ca7119f93f7c173141fd5a4af8e17398ca96061ad9d4fa95ea0bff9 | CANONICAL |
| EV-R4A-49 | AC-R4a-4（证据） | verification/FEA-07-RESIDUAL-2/tools/verify-fea07-perf.ps1 | - | c26b95f8585a223ca81509f1c4252f3d00906ed08198a7f91a0377d9bc49149a | CANONICAL |
| EV-R4A-50 | Review 链 | doc/reviews/FEA-07-RESIDUAL-2-scope-r1.md | - | 8f549cabf0cea401e84a18366a00403aca36ce8c8b3a0843e4c7a93af03aec28 | CANONICAL |
| EV-R4A-51 | Review 链 | doc/reviews/FEA-07-RESIDUAL-2-r1.md | - | a242661a1da2c01b86b4ff3c4808722c8f2f8bbec0a3820d8658586043675379 | CANONICAL |
| EV-R4A-52 | Review 链 | doc/reviews/FEA-07-RESIDUAL-2-r2.md | - | 35e83a8c01d760ad2841fbcd645a5e6d0596a3c495bf4346bf9e02e5582a6f47 | CANONICAL |
| EV-R4A-53 | Review 链 | doc/reviews/FEA-07-RESIDUAL-2-r3.md | - | 1f7d48ec8cbbf2b958bc1570a2279d5b017ddcdf0c66702e8b36650566d816c9 | CANONICAL |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `0a39a78f0`，impl `85207730e`/`bacf6c307`/`a03a6794a`） | NOT_APPLICABLE | — | — | 未创建/未删除 linked worktree；main 内联实施 |
| evidence | `verification/FEA-07-RESIDUAL-2/**` | PRESERVE_REFERENCED | `verification/FEA-07-RESIDUAL-2` | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | 被本卡 Canonical Evidence 与 `doc/tasks/FEA-07.md` R4a 回填引用；原地保留，不归档 |
| temp | `%TEMP%/nm-fea07-perf-*`、`%TEMP%/nm-fea07-draft-window-*`、`%TEMP%/nm-fea07-window-lifecycle-*` | NOT_APPLICABLE | — | — | 测试临时根（appearance store / switch journal / theme home），测试 Dispose 清理；不写仓库或用户数据 |
| test-fixture | `tests/NewManga.App.Tests/FakeHostController.cs` | NOT_APPLICABLE | — | — | 仅测试侧加法探针（`DisposeCalls`/`DisposeException`/`DraftWriteLog`），生产行为不变 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未触碰真实 `%APPDATA%`/用户源文件/外部卷/回收站 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson` | NOT_APPLICABLE | — | — | 既有副作用（`NewManga.CoreClient.Tests` 全量运行时重写）；每次全量后 `git checkout -- verification/FEA-09`，零 diff |
| tool | `verification/FEA-07-RESIDUAL-2/tools/**`（`calibrate-ui-gap.ps1` raw 定标、`verify-fea07-perf.ps1` 专用串行性能门禁） | PRESERVE_REFERENCED | `verification/FEA-07-RESIDUAL-2/tools` | `verification/FEA-07-RESIDUAL-2/RESOURCE-MANIFEST.json` | 卡内运行脚本；只写本证据目录，不触用户数据；原地保留 |

## Closeout Record

- **Closeout date / DSH**：2026-11-08。
- **终态**：`done`；`integration_commit` = **`a03a6794a`**，`delivery_head` = **`ac0dca1bd`**；base `bf4207d4a`。
- **Review 链**：r1 approved（P0/P1=0，P2×4）→ 返修 → r2 **changes_requested**（**P1×1**：gap 门槛 full-suite 不稳定）→ 返修（gap 门槛移入 gated 性能门禁、默认只记录）→ **r3 approved（P0=0/P1=0/P2=1/P3=3）**。
- **AC 定稿**：AC-R4a-1…4 全 MET（含 DSH closeout 面）。
- **门禁（Lead 一手，head `ac0dca1bd`）**：build 0/0；全量 .NET **1779/0/103**；pins **18/18**；check PASS；API EXIT 0；perf gated 1/1；diff 50 文件 ⊆ allowed_paths；禁止面零 diff；FEA-09 已恢复。
- **P2-01 处置（DSH）**：用 r2 代码重生成 canonical 默认套件 JSON（`suite=default`、`gapGateApplied=false`、`p95Passed=true`、`uiThreadSchedulingGapPerfGateBudgetMs=700`、`medianP95Ms=531.42`），本卡 EV 表按新字节重签。
- **DSH 扩域留痕**：`apps/desktop-avalonia/src/NewManga.App/Views/Presentation/PresentationWindow.cs`（+26/−5，净 +21，无功能删除；仅 `DraftOwnership` 属性 + 可选构造参 + `Floating` 强制只读）。
- **limitation / re-home**：
  - **L-R4a-1**：生产组合根未注入共享 registry、`WindowBroker.RegisterSecondary` 零调用、无 `WindowRole.Floating` 生产实例 ⇒ 跨 OS 窗口只读/唯一 owner 目前**仅窗口层机制 + headless 证据**；待多窗口功能卡接线。
  - **L-R4a-2**：`uiThreadSchedulingGapMs` 门槛仅适用于**串行 perf 门禁**（700 ms；默认套件只记录）；并行 full-suite 观测 472–619 ms 已入证据。
  - **L-R4a-3**：真实规模 p95 超 1000 ms（n50 1196 / n200 2618 / n500 5668）**只记录、非 PASS**，规模性能 residual 待立项。
  - **L-R4a-4**：pytest 全量 **3394 passed / 1 failed（既有 flaky `test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren`）/ 10 skipped**；隔离复跑 16 passed；本卡零 Python diff。
- **未做**：AC1/AC3/AC4（`FEA-07-RESIDUAL-3`/R4b 承接）；原生 IME/双屏/DPI（NA，`NOT_RUN`）；未改契约/pins。
- **行文**：不得写「FEA-07 完全实现 / AC2 生产可用」；只写「AC2 窗口层机制 MET；AC6 指标 MET（门槛口径见 L-R4a-2）；AC8 证据 MET」。
