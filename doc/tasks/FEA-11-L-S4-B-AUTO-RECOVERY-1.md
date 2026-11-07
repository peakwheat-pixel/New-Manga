---
id: FEA-11-L-S4-B-AUTO-RECOVERY-1
title: 重授权后的零交互恢复（L-S4-B：reattest 条件写 + Host 触发 + App 成功分支；C-16 v1.5）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`（fresh subagent `6f75eb58-…`，**BLOCKED 按旧卡面**；推荐形状 = C-16 v1.5 `source.reattest/1` + `ReattestSourceLocation` 条件写 + `roots_available` 字段，1/18 pins）；Codex 不可用 → ZCode 故障转移裁决（见 PREREQ 卡）；DSH 裁决 D-1…D-8（见下）；依赖 PREREQ（C-16 v1.5 UNFREEZE）；ZCode 裁决：接受 b3 形状（1 pin），补充 AC-LS4B-9/10
suggested_owner: codex
owner: null
reviewer: null
depends_on:
  - FEA-11-L-S4-B-PREREQ-1
base_commit: a7360839d
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-AUTO-RECOVERY-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-*.md
  - doc/handoffs/FEA-11-L-S4-B-*.md
  - verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**
  - src/bootstrap/core_service.py
  - src/application/sources/reattest.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceRootReattestPlanner.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/ImportDockViewModel.cs
  - tests/core/test_host_control.py
  - tests/fea11/test_source_reattest.py
  - tests/core/test_core_scan_target_commands.py
  - tests/core/test_core_service.py
  - tests/fea09/test_referenced_wire.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceReattestTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/SourceRecoveryUiTests.cs
out_of_scope:
  - `src/infrastructure/sqlite/library.py`（只复用既有唯一 SQL，不得新增第二份）
  - `doc/plan/**` 契约字节（PREREQ 卡负责）；C-15/C-17/C-06/C-07/M2-C1
  - B2 实现（`roots_available` 只冻结字段，无消费者前不实现；另卡）
  - 自动重新授权/自动重建 identity/撤销后自动放行；folder（L-S4-2）；UI 新命令；schema/依赖；真实用户数据；push
---

# FEA-11-L-S4-B-AUTO-RECOVERY-1（L-S4-B）：重授权后的零交互恢复

> **状态：`ready`（依赖 C-16 v1.5 PREREQ；C-16 v1.5 = `source.reattest/1` + `ReattestSourceLocation` + `roots_available` 字段，1/18 pins）。**
> 「零交互」严格限定为：**用户完成 B1 的显式「重新授权」动作之后**，系统不再要求第二次交互（不是撤销后自动恢复、不是自动重新授权）。

## 来源与裁决（2026-11-07）

- 权威 scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`：旧卡面机制不可行（只读命令无法改 Core `source_locations`；Host-only 重证会改 C-17 §5.3 fail-closed 语义）→ 推荐 b3 形状；B2 只冻结字段。
- **DSH 裁决 D-1…D-8**（详见 PREREQ 卡）：D-1 零 DB 写只约束枚举/投影（reattest 允许条件单行写）；D-2 形状 b3；D-3 B2 冻结字段、实现延后；D-4 1/18 pins，错误码复用；D-5 红线；D-6 C-15 零字节；D-7「零交互/周期枚举」措辞修正；D-8 基线 3317/10、1617/0/93。

## In（冻结）

1. **Core**：`ReattestSourceLocation` host-control handler（§2.5）——校验 live grant/session/expiry/revoked、`grant.scope.source_id`、facts 四键、唯一 location 行；条件写 `registry_id/authorization_generation` 两列（复用 A 卡唯一 SQL；`last_verified_at` 保持原值、不刷新审计时间）；拒绝/无匹配零写；幂等/单调；folder 排除；成功响应 closed shape。
2. **Host**：能力探测 `source.reattest/1`（旧 Core 不发送）；`SourceRootReattestPlanner` 精确候选（旧条目已撤销、恰 1 根、live 候选唯一且恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、非 folder）；`SourceReadCoordinator` 发送 reattest；`SourceScanScheduler`/`HostRuntime` 成功后触发既有 refresh（`RequestSourceScanRefresh`）。
3. **App**：B1 重授权成功分支调用（不新增 UI→Host 命令；复用既有端口）；after-reattest 成功/失败文案（fail-closed）。
4. **测试**：Core 矩阵（身份/撤销/幂等/单调/零写/folder/响应形状）、Host 候选精确性/能力门禁、App 成功分支、gated 真实 IPC（B1 重授权→reattest→扫描枚举恢复→旧源不再丢失）、判别性 ≥4。

## Out

- `library.py` 新 SQL；契约字节（PREREQ）；B2 实现；自动重新授权/自动重建 identity；folder 身份键；新 UI 命令；schema/依赖；真实用户数据；push。

## Acceptance Criteria（v3）

- [ ] **AC-LS4B-1 能力门禁/四象限**：`source.reattest/1` 缺失（旧 Core）→ Host 不发送、行为与现状一致（target 仍 typed skip）；新×新才生效；能力探测异常不发。
- [ ] **AC-LS4B-2 Host 候选精确性**：仅「旧条目已撤销、恰 1 根、live 候选唯一且恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、kind 非 folder」进入候选；其余零 wire。
- [ ] **AC-LS4B-3 Core 身份门禁与零写**：请求 closed shape；host-only/session；grant live/未过期/未撤销；`grant.scope.source_id == source_id`；grant facts 四键等于当前 location；拒绝/无匹配零写。
- [ ] **AC-LS4B-4 单行写/幂等/单调**：成功只改 `registry_id/authorization_generation` 两列（`last_verified_at` 保持原值、不刷新审计时间）；location 行数不变；其余列逐列不变；重复调用 `updated:0` 且零写（字节不变）；同 registry 代次不倒退、跨 registry 允许 1。
- [ ] **AC-LS4B-5 无授权/无 identity 重建/不扩面**：Core 不创建/复活 grant；Host Registry 不新增/撤销/改 roots/identity/generation（仅既有 `last_used_at`）；不新增 source/version/entry；无新错误码/能力（除冻结的 `source.reattest/1`）/wire minor/schema/依赖。
- [ ] **AC-LS4B-6 触发与恢复**：B1 重授权成功后（App 成功分支）触发 reattest → 冷启动/下一次 refresh 枚举不再丢该 source（真实 IPC 闭环）；失败 typed 且不自动重试成自动恢复。
- [ ] **AC-LS4B-7 零漂移/门禁**：pins 18/18（C16 v1.5）；check（默认+`-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3317/10、1617/0/93**）；跑后恢复 `verification/FEA-09`。
- [ ] **AC-LS4B-8 不夸大**：只承诺「B1 显式重授权后无需重导入/apply，扫描枚举恢复」；不承诺撤销后自动恢复、不承诺自动重新授权、不承诺 folder；`source_reset_registry` 后无旧条目可桥接 → limitation；L-R1 未全修。
- [ ] **AC-LS4B-9 每轮至多一次 reattest**：同一 refresh 轮中每个 target 至多一次 `ReattestSourceLocation`，无重试风暴；失败 typed 即止（不循环重试成自动恢复）。
- [ ] **AC-LS4B-10 措辞红线**：「零交互」严格限定为「B1 显式动作之后的传播」；卡/Handoff/EV/UI 禁止出现「自动恢复/自愈/自动重新授权」承诺。

## 已知 limitation（本卡）

- B2 `roots_available` 字段已冻结但 B2 实现延后（无消费者）；多根扫描 first-root 启发式未修。
- folder 排除（L-S4-2）；`source_reset_registry` 后无旧条目可桥接（需重导入）。
- 周期 loop 只 tick 不重枚举 → 恢复依赖冷启动/下一次 refresh（措辞不得写「tick 自动恢复」）。
- 不自动重新授权/不自动重建 identity；撤销后不放行。
- **扫描执行面限制（DSH 裁决补充）**：reattest 后枚举 target 恢复成立，但扫描执行仍会被既有 `ResolveRegistryEntry` 的「同路径 revoked 旧条目 fail-closed」拦住（tick typed error）；本卡按冻结 AC 只承诺**枚举恢复**，不宣称扫描执行成功；该限制登记为 **L-S4-B-1**，后续另卡（与 B2/roots 管理一同设计）。

## DSH 裁决补充（2026-11-07；scope 扩域）

- **批准扩域（仅断言预期，不改行为）**：C-16 v1.5 §0 新增能力 `source.reattest/1` 使既有「精确 capability 列表」断言失败（`tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`）。参照 v1.3 `source.read.run/1` 先例，**允许**在上述 2 个既有测试文件中仅追加 `"source.reattest/1",` 预期；不得改任何产品行为/契约/其它断言。
- **.NET 侧同类扩域预先批准（同一模式）**：若全量 .NET 出现精确 capability 列表断言需 +1 行（如 CoreClient 能力解析测试），允许在**对应既有测试文件**中仅追加预期；实施者须在交付中逐文件列出。
- **扫描执行面 limitation（L-S4-B-1）**：枚举恢复成立；扫描执行仍被 `ResolveRegistryEntry` 对同路径 revoked 旧条目的 fail-closed 拦住 → tick typed error；本卡不宣称扫描执行成功，后续另卡。

## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| Core 矩阵 | `pytest tests/core/test_host_control.py tests/fea11/test_source_reattest.py -q` | 全绿；破坏点 RED | `logs/feature.log`、`logs/discrimination.log` |
| Host 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceReattest"` | 全绿 | `logs/host-unit.log` |
| gated 闭环 | `NEWMANGA_FEA11_IPC=1 ... --filter Fea11ScanIpc`（或新 IPC 用例） | 重授权→reattest→枚举恢复 | `logs/host-ipc.log` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- 待实施。
