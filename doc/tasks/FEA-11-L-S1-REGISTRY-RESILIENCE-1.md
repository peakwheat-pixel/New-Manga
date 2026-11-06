---
id: FEA-11-L-S1-REGISTRY-RESILIENCE-1
title: Registry 读取韧性（A：文件级损坏与根身份当前不可用分离；零 wire）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（fresh subagent `976c9d16-…`，**READY-WITH-UNFREEZE**：仅 C-15 §5 单条、1 pin；C-16/C-17 零改）；Codex 不可用（product limit）→ ZCode 故障转移裁决（记录见 PREREQ 卡）；DSH 裁决 D-1…D-9（见下）；契约前置 `FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1`（C-15 v1.5）
suggested_owner: codex
owner: run-grant-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-r1.md`）
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
base_commit: 55306cb84
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1
allowed_paths:
  - doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md
  - doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md
  - doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-*.md
  - verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryResilienceTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - `SourceScanScheduler.cs`/`HostRuntime.cs`/`SourceWatcher.cs`（需要时走 scope 修订；D-6）
  - App 自动重注册/自动恢复（D-4）；`.corrupt-*` 复制策略（D-5，C 项 limitation）
  - C-16/C-17/其它契约字节；Core/Python；wire/错误码/能力/schema/依赖；UI；真实用户数据；push
---

# FEA-11-L-S1-REGISTRY-RESILIENCE-1（A）：Registry 读取韧性

> **状态：`ready`（依赖 C-15 v1.5 PREREQ；零 wire）。** 来源：`FEA-11-SCAN-2` L-S1——单根缺失/替换导致整库 `SOURCE_REGISTRY_UNAVAILABLE`。

## DSH 裁决（2026-11-07）

- 采用 scope review 的 A/B/C 拆分：**A（本卡）= 读取韧性**；B（恢复/重授权 UI，依赖 L-S4）另卡；C（`.corrupt-*` 无界复制）登记 limitation。
- 红线：**文件级损坏仍整库 fail-closed**；根级不可用只影响该根相关请求；`Authorize` 必须逐请求重核验根 identity（只从 `Load` 删除校验而不补 `Authorize` = 安全回退，禁止）；缺失根 ≠ 无授权；不自动重建 identity/重授权；错误码零新增（复用 `SOURCE_REGISTRY_UNAVAILABLE`）。
- 不含：App 自动重注册（D-4）、`.corrupt-*` 策略（D-5）、`SourceScanScheduler/HostRuntime/SourceWatcher`（D-6，需要时走 scope 修订）。

## In（冻结）

1. `SourceAccessRegistry.Load()`：仅做**文件级**校验（magic/version/长度/DPAPI/JSON/条目结构）；**不再因根 identity 当前不可用/不匹配判整库损坏**。
2. 条目/根读取投影：`List` 可用；不可用根以「当前不可用」状态呈现（不删除条目、不静默丢弃）。
3. `Authorize`：对请求路径所属根**逐请求重新核验 identity**（路径存在/可读/卷+file id 与登记一致）；不可用/不匹配 → 该请求 typed `SOURCE_REGISTRY_UNAVAILABLE`、**零写**；其余根请求不受影响。
4. 文件级损坏路径保持不变（fail-closed、不创建空文件、不覆盖、复制 `.corrupt-<utc>`、整库不可用）。
5. 恢复/撤销语义不变（恢复 `source_reset_registry` 仅文件级损坏；撤销 generation+1/`revoked_at`/C-16 ACK 不变）。
6. 测试：混合 registry（有效根 + 缺失根 + 被替换根）单测；1 条 gated 真机 IPC（D-7）；判别性破坏点（只删 Load 校验不补 Authorize → RED；缺失根当无授权/自动恢复 → RED；文件级损坏放宽 → RED）。

## Out

- B（恢复/重授权 UI）、C（corrupt 复制）、App/UI、Core/Python、契约（PREREQ 已冻）、schema/依赖、真实用户数据、push。

## Acceptance Criteria（v3）

- [ ] **AC-L1 文件级损坏仍整库 fail-closed**：magic/version/长度/DPAPI/JSON 任一不合法 → `SOURCE_REGISTRY_UNAVAILABLE`、corrupt 复制、不创建空文件/不覆盖（判别性：放宽该路径 → RED）。
- [ ] **AC-L2 根级不可用不再整库不可读**：有效根 + 缺失/被替换根的混合 registry：`List` 可用、有效根相关操作/授权正常；缺失根相关请求 typed 拒绝且零写；其余根不受影响（判别性）。
- [ ] **AC-L3 授权期逐请求校验（安全核心）**：`Authorize` 对路径所属根重新核验 identity；只删 `Load` 校验不补 `Authorize` → 目标用例 RED（被替换根不得重新获得授权）；缺失根 ≠ 无授权。
- [ ] **AC-L4 不自动重建/恢复/重授权**：代码与测试证明不存在自动重建 identity、自动恢复、自动重授权路径；恢复仍仅显式 `source_reset_registry`（文件级损坏）。
- [ ] **AC-L5 错误码/语义零新**：沿用既有 `SOURCE_REGISTRY_UNAVAILABLE`；无新码、无 wire/schema/依赖/C-16/C-17 变化；撤销/ACL/加密边界不变。
- [ ] **AC-L6 测试/证据**：混合 registry 单测 + 1 条 gated 真机 IPC（D-7）；判别性 ≥3 破坏点 RED + 字节级恢复；EV 每文件 sha256 + Handoff。
- [ ] **AC-L7 零漂移/门禁**：pins 18/18（C15 v1.5）；check（默认 + `-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3305/10 / 1562/0/91**）；跑后恢复 `verification/FEA-09`。
- [ ] **AC-L8 不夸大**：不得把本卡写成「恢复已可用/根级问题全解」；B/C limitation 保留；不得宣称自动恢复。

## 已知 limitation（本卡）

- **B（恢复/重授权 UI）不存在**：`source_reset_registry`/`source_revoke_root` App 侧 0 调用；根级恢复需用户显式操作但入口未接线 → 另卡。
- **C（`.corrupt-*` 无界复制）**：每失败复制一份且无清理 → 登记 limitation。
- 错误码复用 `SOURCE_REGISTRY_UNAVAILABLE` 的码义收窄（文件级损坏或该请求根不可用）→ 词表细化另案。
- `SourceScanScheduler/HostRuntime/SourceWatcher` 的可用性投影不在本卡（D-6）。

## 测试要求

| 场景/AC | 命令或步骤 | 预期 | 证据 |
|---|---|---|---|
| 混合 registry 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceRegistryResilience"` | 全绿；破坏点 RED | `logs/host-unit.log`、`logs/discrimination.log` |
| 真机 IPC（gated） | `NEWMANGA_FEA11_IPC=1 ... --filter Fea11RunGrant` 或既有 Host IPC 模式 | 有效根可用 + 缺失根 typed | `logs/host-ipc.log` |
| 回归 | `--filter SourceRegistry`、`pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | 不降 | `logs/regression.log` |
| 门禁 | 全量 pytest/.NET、pins、check、API、scope | 不降/不漂移 | `logs/gates.log` |

## 交付记录（Owner 回填；不改 status）

- 待实施。
