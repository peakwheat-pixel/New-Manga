---
id: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
title: Run 源范围解析恢复（L-S4-B-2：枚举 Run target 复用自身 live registry 身份；Host-only 零契约）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md`（fresh subagent `0f28cb0d-…`，**READY-TO-FREEZE**；推荐 Host-only：`RunSourceRange.Resolve` 对枚举 target 复用 L-S4-B-1 的 `SelectEnumeratedEntry`，非枚举保持 `ResolveRegistryEntry`；**0 UNFREEZE / 18 pins**）；Codex 不可用 → ZCode 故障转移裁决（见卡）；DSH 裁决 R-1…R-7（见下）
suggested_owner: codex
owner: l-s4b2-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review；只读交付 head；session 见 `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-r1.md`）
depends_on:
  - FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md
  - doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-*.md
  - verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRunRangeResolutionTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
out_of_scope:
  - `ResolveRegistryEntry` 全局语义（C-17 §5.3；本卡零字节）
  - `SourceScanScheduler.cs`（L-S4-B-1 已 done；`SelectEnumeratedEntry` 为 `public static`，直接复用，不改其字节）
  - C-16/C-17/Core/Python/schema/依赖
  - B2 roots 可用性、folder（L-S4-2）、L-S4-1、L-R1
  - 自动重新授权/自动重建 identity；真实用户数据；push
---

# FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1：Run 源范围解析恢复

> **状态：`ready`（Host-only，零契约 0/18 pins）。** 来源：L-S4-B-1 的 Run 面 limitation——`RunSourceRange.Resolve` 仍按路径 `ResolveRegistryEntry`（`HostRuntime.cs:1785`），遇同路径 revoked 旧条目立即 `null`（`SourceScanScheduler.cs:1911-1915`）→ 该 source `Unresolved`（`HostRuntime.cs:1786-1790`）→ 不进 `Targets`/`ColdSources`；目标页属该 source 时 Core 可能整体 `SOURCE_ACCESS_DENIED` → **Run 不 dispatch**。

## DSH 裁决（2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| R-1 | **形状** | 采纳 focus review 推荐：`RunSourceRange.Resolve` 对 `IsEnumerated` target 复用 `SourceScanScheduler.SelectEnumeratedEntry`（public static）选 target 自身 live `(registry_id, generation)`；非枚举保持 `ResolveRegistryEntry`。不改 `ResolveRegistryEntry`/C-17 字节。 |
| R-2 | **零契约** | 0 UNFREEZE / 18 pins 不变（沿用 L-S4-B-1 S-2 的 §5.3 口径：fail-closed 主体 = target 自己的 registry）。mint 仍由 `Registry.Authorize` 逐请求复核 live/generation/根包含/卷-文件身份。 |
| R-3 | **单卡独立** | 不并入 L-S4-B-1（已 done/冻结）；不并入 B2/2C。 |
| R-4 | **gated 轻量闭环** | 用既有 `AlignRegistryAsync` + Host revoke/register 构造状态（Core per-page 匹配不看 registry_id），before=`Unresolved=1`/无 bind/页读拒绝 → after=`Targets` 含 live/`bound_pages≥1`/`resolve_page_resource` OK，wire 无路径。 |
| R-5 | **不抛** | Run 范围解析对 Host 侧失败最多计 `unresolved`，不得向 `AuthorizeSliceAsync` 抛新异常（best-effort）。 |
| R-6 | **红线** | 不自动重新授权/不重建 identity/不写 registry 结构（除既有 `last_used_at`）/旧 revoked 行保留/不回落 sibling live。 |
| R-7 | **基线** | clean head 重测，pytest/.NET 不低于 **3360/10、1652/0/94**（STATUS 基线已更新）。 |

## In（冻结）

1. `HostRuntime.cs`：`RunSourceRange.Resolve` 中对 `target.IsEnumerated` 分支改用 `SourceScanScheduler.SelectEnumeratedEntry(entries, target, out verdict)` 选自身 live entry；非枚举分支保持 `ResolveRegistryEntry`；失败（null/异常）→ `Unresolved`（best-effort，不抛）；枚举 target 为 live 但 Core version 冷 → 进 `ColdSources`（恢复 on-demand 分类）。
2. 新增 `SourceRunRangeResolutionTests.cs`：纯函数矩阵（主 AC、不回落 sibling、缺失/撤销/漂移 unresolved、非枚举零变化、冷源分类恢复、无 registry 写、不抛）。
3. `Fea11RunGrantIpcTests.cs`：gated 真实 IPC 闭环（before/after）。
4. 证据/Handoff/卡面。

## Out

- `ResolveRegistryEntry` 全局语义；`SourceScanScheduler.cs`；C-16/C-17/Core/Python/schema/依赖；B2/folder/L-S4-1/L-R1；自动重新授权/自动重建 identity；真实用户数据；push。

## Acceptance Criteria（v3）

- [ ] **AC-RUN-1 枚举 target 的 Run 范围恢复（主 AC）**：给定「旧条目已 revoked（同 locator/root path）+ 同路径新 live 条目（同一物理身份）+ 枚举 target 携带 live `(registry_id, generation)`」，`RunSourceRange.Resolve` 必须把该 source 计入 `Targets`（RegistryId/Generation = live）、`Unresolved=0`；scope path/kind/version/容器成员与现行为一致。判别性：仍走 path-only resolver → 同 fixture `Unresolved=1`、`Targets` 空 RED。
- [ ] **AC-RUN-2 fail-closed 矩阵与不回落 sibling**：target 自身 registry 缺失/revoked/generation 漂移 → `Unresolved`；即使同路径存在 live sibling 也不采用；全部零 grant、零 `AuthorizeSourceReadForRun` 帧；判别性：删 own-id/撤销/代次检查或接受 sibling → RED。
- [ ] **AC-RUN-3 非枚举 target 语义零变化**：`ResolveRegistryEntry` 字节不变；非枚举 Run target 在同状态（同路径 revoked+live）下仍 `Unresolved`；既有 `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`、`RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources` 原样通过。
- [ ] **AC-RUN-4 冷源 on-demand 分类恢复**：枚举 target 为 live 但 Core version 不在 `SourceIdentityCache` → 进 `ColdSources`（不是 `Unresolved`）；authorizer 恰 1 次 bounded on-demand scan；第二次 Resolve 后进 `Targets` 参与 mint；预算/超时/失败仍 skip（`MaxOnDemandScansPerSlice=8`、30s）。
- [ ] **AC-RUN-5 无自动授权/无 identity 重建/不写 registry/不抛**：解析前后 `DescribeRegistryEntries`（不含 `last_used_at`）结构相等；无 `Register`/`Revoke`/`Reset`；旧 revoked 行保留；解析对 Host 侧失败最多 `unresolved`，不得向 `AuthorizeSliceAsync` 抛新异常。
- [ ] **AC-RUN-6 gated 真实 IPC 闭环（before/after）**：真实 Core + Registry + referenced 页；before=`Unresolved=1`/无 bind/页读拒绝；after=`Targets` 含 live、`bound_pages≥1`、`resolve_page_resource` OK；wire 无绝对路径。
- [ ] **AC-RUN-7 零契约/零漂移**：C15/C16/C17 blob 零漂移、`PROTOCOL_MINOR=3`、pins 18/18；无新命令/能力/错误码/schema/依赖。
- [ ] **AC-RUN-8 门禁/不夸大/触发口径**：check（默认+`-TaskPath`）PASS；全量 pytest/.NET 不低于本卡起点重测值；跑后恢复 `verification/FEA-09`；卡/Handoff/EV 不写「自动恢复/自愈/自动重新授权/撤销后放行/扫描面恢复/B2/folder/2C」；恢复口径固定为「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」。

## 已知 limitation（本卡）

- 不修 `ResolveRegistryEntry` 非枚举语义、不修扫描执行面（已 done）、不实现 B2/folder/L-S4-1/L-R1。
- 「Run 预授权/冷源分类恢复」不等于「Run 全面恢复」；managed-only Run 本就无需 source 授权。
- 多根 first-root 启发式保留。

## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| 纯函数矩阵 | `dotnet test ... --filter "FullyQualifiedName~SourceRunRangeResolution"` | 全绿；破坏点 RED | `logs/host-unit.log`、`logs/discrimination.log` |
| gated 闭环 | `NEWMANGA_FEA11_IPC=1 ... --filter Fea11RunGrantIpc` | before/after 按 AC-RUN-6 | `logs/host-ipc.log`、`logs/ipc-closed-loop.json` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- 待实施。
