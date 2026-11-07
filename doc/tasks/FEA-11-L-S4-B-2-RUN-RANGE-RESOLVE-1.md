---
id: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
title: Run 源范围解析恢复（L-S4-B-2：枚举 Run target 复用自身 live registry 身份；Host-only 零契约）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md`（fresh subagent `0f28cb0d-…`，**READY-TO-FREEZE**；推荐 Host-only：`RunSourceRange.Resolve` 对枚举 target 复用 L-S4-B-1 的 `SelectEnumeratedEntry`，非枚举保持 `ResolveRegistryEntry`；**0 UNFREEZE / 18 pins**）；Codex 不可用 → ZCode 故障转移裁决（见卡）；DSH 裁决 R-1…R-7（见下）
suggested_owner: codex
owner: l-s4b1-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review）：r1 `d7f8c2b3-…`（**approved** P0=0/P1=0/P2=0/P3=7 非阻断；reviewed_head `fad1ec776`）；报告 `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-r1.md`
depends_on:
  - FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
base_commit: 2ef3f1024
branch: null
worktree: null
integration_commit: fad1ec776
delivery_head: fad1ec776
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-RUN-1 枚举 target 的 Run 范围恢复（主 AC）**：给定「旧条目已 revoked（同 locator/root path）+ 同路径新 live 条目（同一物理身份）+ 枚举 target 携带 live `(registry_id, generation)`」，`RunSourceRange.Resolve` 必须把该 source 计入 `Targets`（RegistryId/Generation = live）、`Unresolved=0`；scope path/kind/version/容器成员与现行为一致。判别性：仍走 path-only resolver → 同 fixture `Unresolved=1`、`Targets` 空 RED。 <<MET>>
- [x] **AC-RUN-2 fail-closed 矩阵与不回落 sibling**：target 自身 registry 缺失/revoked/generation 漂移 → `Unresolved`；即使同路径存在 live sibling 也不采用；全部零 grant、零 `AuthorizeSourceReadForRun` 帧；判别性：删 own-id/撤销/代次检查或接受 sibling → RED。 <<MET>>
- [x] **AC-RUN-3 非枚举 target 语义零变化**：`ResolveRegistryEntry` 字节不变；非枚举 Run target 在同状态（同路径 revoked+live）下仍 `Unresolved`；既有 `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`、`RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources` 原样通过。 <<MET>>
- [x] **AC-RUN-4 冷源 on-demand 分类恢复**：枚举 target 为 live 但 Core version 不在 `SourceIdentityCache` → 进 `ColdSources`（不是 `Unresolved`）；authorizer 恰 1 次 bounded on-demand scan；第二次 Resolve 后进 `Targets` 参与 mint；预算/超时/失败仍 skip（`MaxOnDemandScansPerSlice=8`、30s）。 <<MET>>
- [x] **AC-RUN-5 无自动授权/无 identity 重建/不写 registry/不抛**：解析前后 `DescribeRegistryEntries`（不含 `last_used_at`）结构相等；无 `Register`/`Revoke`/`Reset`；旧 revoked 行保留；解析对 Host 侧失败最多 `unresolved`，不得向 `AuthorizeSliceAsync` 抛新异常。 <<MET>>
- [x] **AC-RUN-6 gated 真实 IPC 闭环（before/after）**：真实 Core + Registry + referenced 页；before=`Unresolved=1`/无 bind/页读拒绝；after=`Targets` 含 live、`bound_pages≥1`、`resolve_page_resource` OK；wire 无绝对路径。 <<MET>>
- [x] **AC-RUN-7 零契约/零漂移**：C15/C16/C17 blob 零漂移、`PROTOCOL_MINOR=3`、pins 18/18；无新命令/能力/错误码/schema/依赖。 <<MET>>
- [x] **AC-RUN-8 门禁/不夸大/触发口径**：check（默认+`-TaskPath`）PASS；全量 pytest/.NET 不低于本卡起点重测值；跑后恢复 `verification/FEA-09`；卡/Handoff/EV 不写「自动恢复/自愈/自动重新授权/撤销后放行/扫描面恢复/B2/folder/2C」；恢复口径固定为「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」。 <<MET>>

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

- **交付完成（2026-11-07）**：`delivery_head=fad1ec776`；commit 链 `f6b5a761a`（`HostRuntime.cs` 的 `RunSourceRange.Resolve` 枚举分支复用 `SelectEnumeratedEntry`，+ XML 注释；非枚举保持 `ResolveRegistryEntry` 字节不变）→ `fad1ec776`（新增 `SourceRunRangeResolutionTests.cs` 9 例 + gated `Fea11RunGrantIpcTests` B1 live-entry→Run 范围→bind→resolve 闭环）；随后同批 docs/evidence 提交（本卡面/Handoff/`verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**`）。
- **AC 判定**：AC-RUN-1…8 **全 MET**（逐项 `<<MET>>`；见 `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/EV.md` §1）。
- **实跑门禁**：build **PASS 0/0**；Host 新单测 **9/0/0**；回归（`SourceRegistryTests`）**32/0/0**；gated 真 IPC **6/0/0**（before path_resolver=null/页读拒绝/0 帧 → after targets=1/unresolved=0/bound_pages=1/minted=1/resolve p1 OK）；定向 pytest **89 passed**；全量 pytest **3360/10**（起点基线同值）；全量 .NET **1661/0/95**（起点 1652/0/94；+9 单测、+1 新 gated skip）；pins **18/18**；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**（61 不变）；scope **PASS**（delivery 全 ALLOWED、禁止面零 diff、C16/C17 blob 零漂移、`PROTOCOL_MINOR=3`）；判别性 **5/5 RED_AS_EXPECTED**；跑后 `verification/FEA-09` CLEAN。
- **before/after**：同一 gated 测试内 before=`path_resolver=null` + `resolve_page_resource` typed 拒绝 + `authorize_frames=0`；after=`targets=1/unresolved=0/registry_id=live/bound_pages=1/minted=1/resolve p1 OK`（`logs/ipc-closed-loop.json`）。
- **措辞红线**：只承诺「B1 显式重授权 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」；不写「Run 全面恢复/自动恢复/自愈/自动重新授权/撤销后自动放行/扫描面恢复/B2/folder/2C」。
- **登记 limitation**：managed-only Run 无需 source 授权；Host 侧 mint 仍可能 typed skip（best-effort）；Scheduler 未启动/枚举失败时 `known` 为空；gated 的 Core `source_locations` 用测试侧 `AlignRegistryAsync` 对齐（本卡不发 reattest，往返由 L-S4-B 证据覆盖）；2C 长 Run 与 B2/folder/L-S4-1/L-R1 保留。
- **证据目录**：`verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/`（`EV.md`、`RESOURCE-MANIFEST.json`、`scope-validation.log`、`changed-files.txt`、`logs/**`、`tools/**`）。未 push、未建 worktree；`status` 未改（由 Lead 维护）。

## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 r1 `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-r1.md`（`d7f8c2b3-…`；reviewed_head `fad1ec776`）：**approved，P0=0/P1=0/P2=0/P3=7 非阻断**；AC-RUN-1…8 全 MET；独立复跑 build/Host 9/0/0/回归 32/0/0/gated 6/0/0/pytest 89/pins 18/18/check×2/API 全 PASS；破坏点独立 RED+恢复。
- **flaky 复核**：Lead 集成门禁全量 .NET 唯一失败 `FluentR2ReworkTests.R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline`（App.Tests UI 时序）→ 隔离复跑 5×9/0/0（45/45 PASS）且 App.Tests 全量 770/0/7 EXIT=0 → **既有 flaky，非本卡回归**；原始失败堆栈未入库（P3-F7 登记）。
- **P3 处置（登记接受）**：证据容器/文档精度/覆盖注释/可维护性（manifest pyc、起点基线日志、changed-files 自指、flaky 堆栈未入库等）→ 后续证据维护批规整；不改变产品行为/AC 判定。
- 不改变实现/测试字节（`fad1ec776`）与 AC-RUN-1…8 MET 判定。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/changed-files.txt | ca929aade | a883fdcb6d2b505cfc8f85bc8b0ddeb3c60bb8355e68924c487c61e53f13f1ba | CANONICAL |
| EV-02 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/build.log | ca929aade | 6bf2cce9acf80391de12367a34a80145c871cc41b70e6fa6958dfaf7b6f1705f | CANONICAL |
| EV-03 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/discrimination.log | ca929aade | a31e00740ada711d0b276e0cdfcbd83ef88fe0dd8b4e37adb58f773cb6518248 | CANONICAL |
| EV-04 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/full-dotnet.log | ca929aade | d6b418a73a1ad0df536f4377a11f0773f4ef0aeaf37755531bd61884a82bff63 | CANONICAL |
| EV-05 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/full-pytest.log | ca929aade | 1d09c6946a163c163e5aba6fe3cbead368a689ce878b6711c678a0fbff93ff26 | CANONICAL |
| EV-06 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/gates.log | ca929aade | 324a7c237a9776f8d05bf5539e5cd5c708f1a52a2afbe4d5e8a7fdfc206ad2e9 | CANONICAL |
| EV-07 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/host-ipc.log | ca929aade | 190d543e1dbc0b3910f803d6d5e81a1ac81890cffed4d7552736ac39f56d2750 | CANONICAL |
| EV-08 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/host-unit.log | ca929aade | c4bdc85748637be02c065cccddce7ad9d0e90b55d7ca69023ceaf0aedbdbe4b8 | CANONICAL |
| EV-09 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/ipc-closed-loop.json | ca929aade | 7f31dccaca6345ec04ccda500434d2b8e90722fd0d54a519830ab7387cbed160 | CANONICAL |
| EV-10 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/ipc-closed-loop.txt | ca929aade | 25ba1210169fba3149546fea2953758943a179a52a72dc507c366cddd767a20f | CANONICAL |
| EV-11 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/ipc-fixture.txt | ca929aade | 27c5559f4acbe4850ddd52b1b9d70597788b90e15325b66a1b82151088bd025e | CANONICAL |
| EV-12 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/regression-74.log | ca929aade | 73ccef2755c61b86a3322e009aab76df180f2e40c69b78efb7a68dec89c1195c | CANONICAL |
| EV-13 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/logs/regression.log | ca929aade | 38cc1e8db4c5c6652dc4cee24594a5a0e7cffc25a1a3c582d77dde0f963e5282 | CANONICAL |
| EV-14 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/RESOURCE-MANIFEST.json | ca929aade | 4186cf077a29b31acef98db8b5983a2b4159b7d3b38a25bcfbb226e66bccf6a2 | CANONICAL |
| EV-15 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/scope-validation.log | ca929aade | 732494c6fb934868388a7315fed6105c6cb519ed8e6caf021561db5fb0f35305 | CANONICAL |
| EV-16 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/discrimination.py | ca929aade | d09b00e0a152e145fa67385505f417bcd6da81804a2faf0a2b36934031f77c01 | CANONICAL |
| EV-17 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/gen_manifest.py | ca929aade | b4a4770d9b84ec52607999dcca0935d6c5d2d11f4471fb8775ed0cc05ec5f466 | CANONICAL |
| EV-18 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/tools/scope_validation.py | ca929aade | 5c760b83b72d029a68190fdf5f9fa6cf02a6624b877b49fbb2d6e0597b89dcc0 | CANONICAL |
| EV-19 | AC-RUN-7 | verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/EV.md | ca929aade | f8b80e3ba2b010fb6d735d78564a5995989d0d5f67b43991f577f0360437e678 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；review/handoff 不在 evidence_dir，按卡面/Handoff 引用。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 `HostRuntime.cs` + 测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根与 fixture 保留 |

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `fad1ec776`（实现 `f6b5a761a` + 测试 `fad1ec776`；docs/evidence `ca929aade`）。
- **AC 判定**：AC-RUN-1…AC-RUN-8 **全 MET**；无 PARTIAL/BLOCKED。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=0/P3=7 非阻断）**；flaky 已隔离复核为既有问题；P3 登记接受。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3360/10 → 3360/10**（EXIT 0）；全量 .NET **1652/0/94 → 1660/1(既有 flaky)/95**（EXIT 1 后隔离复跑 5×9/0/0 PASS、App.Tests 770/0/7 EXIT=0）；Host 新单测 9/0/0；回归 `SourceRegistryTests` 32/0/0；gated 真实 IPC 6/0/0（before `Unresolved=1`/页读拒绝 → after `Targets=1`/`bound_pages=1`/resolve OK；wire 无路径）；定向 pytest 89；pins **18/18**（C16 v1.5 `a7f57ebd…`；C16/C17 blob 零漂移）；check（默认+`-TaskPath`）PASS；API inventory PASS（61 不变）；scope **24 文件全 ALLOWED**、禁止面零 diff、`PROTOCOL_MINOR=3`；判别性 **5/5**；跑后恢复 `verification/FEA-09`。
- **limitations（保留）**：Run 面只承诺「预授权/冷源分类恢复」≠「Run 全面恢复」（managed-only Run 无需 source 授权；mint 仍可能 best-effort typed skip）；Scheduler 未启动/枚举失败时 `known` 为空（既有配置行为）；gated Core 行由测试侧 `AlignRegistryAsync` 对齐（本卡不发 reattest）；扫描面（L-S4-B-1 done）/`ResolveRegistryEntry` 非枚举语义/B2/folder（L-S4-2）/L-S4-1/L-R1/多根 first-root 保留；2C 长 Run、L-R11、C-04b、SCAN-RH、UI P3 排队。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根与 fixtures PRESERVE_REFERENCED。
- **指针清理**：STATUS 无活动 Task；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
