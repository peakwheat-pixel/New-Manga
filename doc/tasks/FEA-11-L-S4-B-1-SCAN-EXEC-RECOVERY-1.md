---
id: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
title: 扫描执行面恢复（L-S4-B-1：枚举 target 执行使用自身 live registry 身份；Host-only，零契约）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md`（fresh subagent `fc6e9df6-…`，**READY-TO-FREEZE**；推荐 Host-only 形状：枚举 target 执行用其自身已核验的 live `(registry_id, generation)`，不改 `ResolveRegistryEntry` 非枚举语义；**0 UNFREEZE / 18 pins 全不变**）；Codex 不可用 → ZCode 故障转移裁决（见卡）；DSH 裁决 S-1…S-5（见下）
suggested_owner: codex
owner: l-s4b1-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review；只读交付 head；session 见 `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-r1.md`）
depends_on:
  - FEA-11-L-S4-B-AUTO-RECOVERY-1
base_commit: 58395b9a2
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
allowed_paths:
  - doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md
  - doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - doc/handoffs/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-*.md
  - verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanExecutionRecoveryTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs
out_of_scope:
  - `ResolveRegistryEntry` 对非枚举 target 的全局语义（C-17 §5.3 fail-closed；若改需 C-17 UNFREEZE + 安全复核，本卡不改）
  - HostRuntime/RunSourceRange（AC-SER-5 不含；Run 面另卡）
  - `src/infrastructure/sqlite/library.py`/Core/Python、契约/schema/依赖
  - B2 roots 可用性实现、folder（L-S4-2）、L-S4-1、L-R1
  - 自动重新授权/自动重建 identity；真实用户数据；push
---

# FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1：扫描执行面恢复

> **状态：`ready`（Host-only，零契约 0/18 pins）。** 来源：L-S4-B 交付的 **L-S4-B-1**——reattest 后枚举 target 恢复，但 tick 执行仍被 `ResolveRegistryEntry` 对同路径 revoked 旧条目的 exact-match fail-closed 拦住（`SourceScanScheduler.cs:1899-1903` 先命中 revoked 旧条目 → null；即使 live exact 条目在 `:1905` 也不采用 → `Error("SOURCE_ACCESS_DENIED")` → tick `last_result=error`）。

## DSH 裁决（2026-11-07）

| # | 裁决 | 内容 |
|---|---|---|
| S-1 | **形状** | 采纳 scope review 推荐 **Host-only**：枚举 target 执行使用其**自身已被 `VerifyEnumeratedTarget` 核验**的 live `(registry_id, generation)`（不再走按路径 `ResolveRegistryEntry`）；**不改** `ResolveRegistryEntry` 非枚举语义。 |
| S-2 | **零契约** | 0 UNFREEZE / 18 pins 不变；C-17 §5.3 字节零改动；无新命令/能力/错误码/schema/依赖。 |
| S-3 | **红线** | 不得自动重新授权/自动重建 identity/删除旧 revoked 行；扫描前后 registry 结构（除既有 `last_used_at`）不变；未授权/撤销/漂移 target 仍 typed fail-closed。 |
| S-4 | **Run 面不含** | Run 面（**原 AC-SER-5**；现 AC-SER-5 已重编号为「零漂移/门禁」）不在本卡；Run 面若同样问题另卡（登记 limitation）。 |
| S-5 | **B2/folder** | B2 实现延后；folder（L-S4-2）、L-S4-1、L-R1 保留。 |

## In（冻结）

1. `SourceScanScheduler.cs`：枚举 target 的**执行路径**改用 target 自身的 live `(registry_id, generation)`（其 already verified by `VerifyEnumeratedTarget`）；非枚举 target 保持 `ResolveRegistryEntry` 原语义；失败矩阵不变（缺失/撤销/漂移/根替换/整库不可读均 typed、零 grant/零 frame）。
2. 测试：新增 `SourceScanExecutionRecoveryTests.cs`（枚举 target 在「旧 revoked + 新 live 同路径同身份 + Core reattest」下 tick `ok`/`changed`、非枚举语义不变、fail-closed 负例、registry 结构不变）；`Fea11ScanIpcTests.cs` 扩展 gated 真实 IPC：B1 重授权→reattest→枚举恢复→**tick 执行成功**（从 error 变 ok），wire 无绝对路径。
3. 证据/Handoff/卡面。

## Out

- `ResolveRegistryEntry` 全局语义；HostRuntime/RunSourceRange；Core/Python/library.py；契约/schema/依赖；B2/folder/L-S4-1/L-R1；自动重新授权；真实用户数据；push。

## Acceptance Criteria（v3）

- [ ] **AC-SER-1 枚举执行面恢复（主 AC）**：「旧条目 revoked + 新 live 同路径同物理身份 + Core 行 reattest 到 live」状态下，scheduler target 的 RegistryId = live；`ScanAsync` 用 target 自己的 live `(registry_id, generation)` 铸 grant，发送恰 1 个 `ScanSourceSync`，结果 `ok`/`changed`，**不得** error/`SOURCE_ACCESS_DENIED`；wire 无绝对路径。判别性：仍走 path-only resolver → RED。
- [ ] **AC-SER-2 fail-closed 矩阵不变**：target 自身 registry：缺失 → `Skipped(SOURCE_REGISTRY_UNAVAILABLE)`；revoked → `Skipped(SOURCE_GRANT_REVOKED)`；generation 漂移 → `Skipped(SOURCE_REGISTRY_BUSY)`；root 缺失/替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`；整库不可读 → 现有 typed；全部零 grant/零 frame。
- [ ] **AC-SER-3 非枚举语义零变化**：`ResolveRegistryEntry` 对 `!IsEnumerated` 保持 exact-first、revoked-exact→null、containment fallback；既有 `RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` 原样通过。
- [ ] **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构**：扫描前后 `DescribeRegistryEntries`（不含 `last_used_at`）结构相等；无新/撤销条目、无 roots/identity/generation 变化、无 `Register`/`Revoke`/`Reset` 调用；旧 revoked 行保留。
- [ ] **AC-SER-5 零漂移/门禁**：pins 18/18（C16 v1.5 `a7f57ebd…`）；check（默认+`-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3360/10、1644/0/94**）；跑后恢复 `verification/FEA-09`。
- [ ] **AC-SER-6 不夸大**：只承诺**枚举 target 的扫描执行恢复**；不承诺 Run 面恢复、不承诺自动恢复/自愈；L-S4-B-1 剩余面（RunSourceRange）与 B2/folder/L-S4-1/L-R1 保留。

## 已知 limitation（本卡）

- **Run 面（原 AC-SER-5；当前 AC-SER-5 为零漂移/门禁）不含**：`RunSourceRange` 若同路径存在 revoked 旧条目是否仍 unresolved 未测/未修 → 另卡（若复现）。
- B2 实现延后；folder（L-S4-2）；L-S4-1（零交互恢复仅 B1 动作之后）；L-R1 未全修。
- 非枚举 target 的 `ResolveRegistryEntry` 语义不变（C-17 §5.3 零改动）。

## 测试要求

| 场景/AC | 命令 | 预期 | 证据 |
|---|---|---|---|
| 定向 Host | `dotnet test ... --filter "FullyQualifiedName~SourceScanExecutionRecovery"` | 全绿；破坏点 RED | `logs/host-unit.log`、`logs/discrimination.log` |
| gated IPC | `NEWMANGA_FEA11_IPC=1 ... --filter Fea11ScanIpc` | tick 由 error→ok（reattest 后） | `logs/host-ipc.log`、`logs/ipc-closed-loop.json` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- 待实施。
