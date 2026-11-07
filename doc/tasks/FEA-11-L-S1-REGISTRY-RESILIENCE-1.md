---
id: FEA-11-L-S1-REGISTRY-RESILIENCE-1
title: Registry 读取韧性（A：文件级损坏与根身份当前不可用分离；零 wire）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（fresh subagent `976c9d16-…`，**READY-WITH-UNFREEZE**：仅 C-15 §5 单条、1 pin；C-16/C-17 零改）；Codex 不可用（product limit）→ ZCode 故障转移裁决（记录见 PREREQ 卡）；DSH 裁决 D-1…D-9（见下）；契约前置 `FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1`（C-15 v1.5）
suggested_owner: codex
owner: l-s1-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修）：r1 `954a2ded-b8ed-4f8b-811b-e76e2d3d71ae`（**approved** P0=0/P1=0/P2=0/P3=7 非阻断；reviewed_head `b56c5a0e6`）；报告 `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-r1.md`
depends_on:
  - FEA-11-L-S1-REGISTRY-RESILIENCE-1-PREREQ-1
base_commit: 55306cb84
branch: null
worktree: null
integration_commit: b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b
delivery_head: b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-L1 文件级损坏仍整库 fail-closed**：magic/version/长度/DPAPI/JSON 任一不合法 → `SOURCE_REGISTRY_UNAVAILABLE`、corrupt 复制、不创建空文件/不覆盖（判别性：放宽该路径 → RED）。 证据：`SourceAccessRegistry.Load()` 的 magic/长度/DPAPI/JSON/结构校验与「`.corrupt-<utc>` 复制 + 不覆盖 + 不建空文件 + typed」路径保持原字节；`SourceRegistryResilienceTests.FileLevelCorruptionStaysWholeFileFailClosed` 12 例矩阵（短文件/截断/magic/length/JSON/format_version/重复 id/generation 0/空 roots/非规范 root/readable=false/**真实 DPAPI 篡改**）逐例断言原字节保留 + corrupt 副本 + `List`/`Authorize` typed；既有 `SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` 保持绿；判别性 B4（放宽为「空 registry」→ RED）见 `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/discrimination.log`。 <<MET>>
- [x] **AC-L2 根级不可用不再整库不可读**：有效根 + 缺失/被替换根的混合 registry：`List` 可用、有效根相关操作/授权正常；缺失根相关请求 typed 拒绝且零写；其余根不受影响（判别性）。 证据：`MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne`（2 条全返回、root/generation 不变、`List` 零字节写、新 `Register` 成功）、`MixedRegistry_HealthyRootAuthorizeSucceedsAndOnlyPersistsItsLastUse`（有效根成功且只持久化自身 `last_used_at`）、`MissingRoot_AuthorizeIsTypedAndWritesNothing`（typed + 字节不变 + 无 `.corrupt-*`）、gated 真机 IPC `Ipc_MixedRegistry_ListRegisterMintSucceedAndMissingRootIsTyped`（真实 Core：`source_list_roots`=2、有效根铸造成功、缺失根 typed 零写、`source_register_root` 成功、`List`=3）；判别性 B1（恢复 Load 预探针 → RED）见 `logs/discrimination.log`。 <<MET>>
- [x] **AC-L3 授权期逐请求校验（安全核心）**：`Authorize` 对路径所属根重新核验 identity；只删 `Load` 校验不补 `Authorize` → 目标用例 RED（被替换根不得重新获得授权）；缺失根 ≠ 无授权。 证据：`Authorize` 在同一 `Locked()` 内、读盘后按请求路径所属注册根调 `VerifyRootIdentity`（存在/可读/volume+file id），失败 → `SOURCE_REGISTRY_UNAVAILABLE` 且循环先于任何 `Save`（零写）；不跨调用缓存（`RootIdentityIsReProbedOnEveryAuthorize`）；被替换根不获授权（`ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity`，且持久化 identity 保持原值）；缺失根不回退（`MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact`：根外/前缀兄弟/`..`/相对路径仍 `SOURCE_ACCESS_DENIED`）；判别性 B2（删除逐请求补位 → 被替换根重新授权 RED）、B3（缺失根当无授权 → RED）、B5（根外回退 → RED）。 <<MET>>
- [x] **AC-L4 不自动重建/恢复/重授权**：代码与测试证明不存在自动重建 identity、自动恢复、自动重授权路径；恢复仍仅显式 `source_reset_registry`（文件级损坏）。 证据：`VerifyRootIdentity` 只读探针、不写回，`Authorize` 失败路径零 `Save`；`ReplacedRoot_*` 断言不匹配后 registry 字节不变且持久化 volume/file id 仍为原（错误）值；`RevokeAndExplicitResetAreUnaffectedByAnUnavailableRoot`（`Revoke` generation+1/`revoked_at` 不变；`Reset(false)`→`INVALID_REQUEST`、`Reset(true)`→quarantine+空库）；无自动重注册代码路径。 <<MET>>
- [x] **AC-L5 错误码/语义零新**：沿用既有 `SOURCE_REGISTRY_UNAVAILABLE`；无新码、无 wire/schema/依赖/C-16/C-17 变化；撤销/ACL/加密边界不变。 证据：`scope-validation.log`（`doc/plan`/`doc/contracts`/`schema.py`/migrations/依赖/`NewManga.App/**`/`NewManga.CoreClient/**` 全 `ZERO_DIFF`；changed=2 全 ALLOWED）；`logs/gates-governance.log`（pins 18/18 含 C15 `f9e376a0ed4c`、C16 `ad25fb3c89bb`、C17 `aefa0fa5b17e` 未变；API inventory EXIT=0）；测试断言错误码文本等于 `SOURCE_REGISTRY_UNAVAILABLE`（无新码）。 <<MET>>
- [x] **AC-L6 测试/证据**：混合 registry 单测 + 1 条 gated 真机 IPC（D-7）；判别性 ≥3 破坏点 RED + 字节级恢复；EV 每文件 sha256 + Handoff。 证据：`SourceRegistryResilienceTests`（8 单测 + 1 gated IPC）；`logs/host-unit.log`（40 passed / 1 skipped）、`logs/host-ipc.log`（1 passed + 隔离 receipt）、`logs/discrimination.log`（5/5 RED_AS_EXPECTED + 5/5 字节级 RESTORED + final rebuild EXIT=0）；`EV.md` 逐文件 sha256；`doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-b56c5a0e6.md`。 <<MET>>
- [x] **AC-L7 零漂移/门禁**：pins 18/18（C15 v1.5）；check（默认 + `-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3305/10 / 1562/0/91**）；跑后恢复 `verification/FEA-09`。 证据：`logs/gates-governance.log`（PIN AUDIT PASS 18/18；Governance PASS(3 warnings) ×2；API inventory EXIT=0；`FEA09_STATUS=CLEAN`）；`scope-validation.log`（changed=2 全 ALLOWED、zero-drift 全空）、`changed-files.txt`；`logs/full-pytest.log`（3317 passed / 10 skipped——其中 +12 来自同期 L-S4 已提交测试，不归属本卡）、`logs/full-dotnet.log`（1570 / 0 / 92；基线 1562/0/91：+8 单测 +1 opt-in IPC skip）；build 0 warning/0 error（`logs/build.log`）。 <<MET>>
- [x] **AC-L8 不夸大**：不得把本卡写成「恢复已可用/根级问题全解」；B/C limitation 保留；不得宣称自动恢复。 证据：本卡「已知 limitation」与 Handoff §3 保留 B（恢复/重授权入口不存在）、C（`.corrupt-*` 无界复制）、码义收窄、D-6 投影/过时注释；明写「不宣称恢复已可用/根级问题全解/L-R1 全修/调度器级混合矩阵已覆盖」。 <<MET>>

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

- **实现 commit 链**（起点 `db12dc5e5`（工作树 clean，实测）；卡 `base_commit=55306cb84`）：
  - `1ac8cc0b7` — `feat(fea-11-l-s1)`: `SourceAccessRegistry.Load` 拆分为「文件级损坏」与「根身份当前不可用」；`Authorize` 逐请求重核验请求路径所属根的 identity（同一 `Locked()` 内、读盘后、零写、无跨调用缓存、不自动重建/重授权/恢复）；`List` 保留全部条目。
  - `b56c5a0e6` — `test(fea-11-l-s1)`: `SourceRegistryResilienceTests`（8 单测 + 1 条 gated 真机 IPC）；**`delivery_head`**。
  - 证据/卡/Handoff 同批文档提交（`verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**`、本卡、`doc/handoffs/FEA-11-L-S1-REGISTRY-RESILIENCE-1-b56c5a0e6.md`）。
- **门禁实测**（`delivery_head=b56c5a0e6`；均真跑）：`dotnet build NewManga.sln -c Release` **0 warning / 0 error**；`SourceRegistry` → **40 passed / 0 failed / 1 skipped**；gated `Ipc_MixedRegistry` → **1 passed**（含隔离 receipt）；定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **74 passed**；全量 `pytest tests` → **3317 passed / 10 skipped**；全量 `dotnet test NewManga.sln -c Release` → **1570 / 0 / 92**（基线 1562/0/91：+8 单测、+1 opt-in IPC skip）；`verify_pins` **18/18**；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope **PASS（changed=2 全 ALLOWED；zero-drift 全空）**；判别性 **5/5 破坏点 RED_AS_EXPECTED + 5/5 字节级 RESTORED + final rebuild EXIT=0**。跑后均 `git checkout -- verification/FEA-09`（`FEA09_STATUS=CLEAN`）。
- **未运行/限定**：调度器级 mixed-registry 用例未新增（`SourceScanSchedulerTests.cs` 不在本卡 frozen write domain，D-6）→ 以「registry 级混合单测 + 既有单目标 scheduler 用例保持绿（缺失/替换根仍 `Error(SOURCE_REGISTRY_UNAVAILABLE)`）+ 真实 IPC 混合」组合证据替代，**不**宣称调度器级混合矩阵已覆盖；被替换根采用「注册侧 identity 与当前不匹配」确定性夹具（NTFS FileId 复用 flaky 风险，scope review R4）。
- **共享工作树披露**：同期 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 的 commit `6dd36aad7`/`0ebb234bf`（Python `src/**`+`tests/**`）落在本卡 head **之后**，**不属于本交付**；本卡零 Python/契约/STATUS/PLAN/LEDGER diff，未暂存/提交其任何文件（全量 pytest 的 +12 passed 归属该会话）。
- **limitation（保留）**：B（恢复/重授权入口不存在）、C（`.corrupt-*` 无界复制）、`SOURCE_REGISTRY_UNAVAILABLE` 码义收窄（整库 vs 单根）、D-6 可用性投影与 `SourceScanScheduler.cs:1570-1571` 过时注释。
- **独立 Review**：待 Lead 指派（本会话不自审；`status`/closeout 字段由 Lead 维护）。

## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 r1 `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-r1.md`（`954a2ded-…`；reviewed_head `b56c5a0e6`）：**approved，P0=0/P1=0/P2=0/P3=7**；安全核心（Authorize 逐请求补位）、文件级 fail-closed、独立实跑（40/0/1、IPC 1 passed、pytest 74、2 破坏点 RED+RESTORED）、证据/pins/scope 全 PASS。
- P3-1（全量 3317 实际跑在 delivery head + 同期 L-S4 工作树）：卡/Handoff 已在 closeout 注明口径（+12 pytest 归 L-S4；全量 .NET 1570/0/92 由 L-S4 在 combined code 运行）。
- P3-2（测试要求表引用不存在的 `logs/regression.log`/`logs/gates.log`）：以实际 `logs/{build,host-unit,host-ipc,discrimination,full-pytest,full-dotnet,feature}.log` 为准，卡面描述按本补充纠正。
- P3-3（`SourceScanScheduler.cs` 注释过时）：D-6 已登记为后续 scope 修订，不在本卡。
- P3-4（`Authorize` 空 `paths` 无防御性拒绝）：登记 follow-up（维护卡），不改变本卡 AC 与安全结论。
- P3-5（reparse 祖先负例未新增）：代码路径未改，registry 级负例以既有 `SourceSecurity` 覆盖；登记接受。
- P3-6（`List` 未显式输出可用性字段）：按「零新增持久字段 + 派生状态」口径接受，B 卡解决展示。
- P3-7（多根条目 apply 保守整条目失败）：非回归，登记接受（B/C 设计输入）。
- 不改变 AC-L1…L8 MET 判定与 r1 approved 结论。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/changed-files.txt | 89757f193 | 517690346ac8d5c41d7f417fd80eff0b17c8564c53c910ce4ec40b6f841fb7e0 | CANONICAL |
| EV-02 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/EV.md | 89757f193 | 293a93b0c0a8acac1e0ec95b6bf90630e88ed2761e8ba00a2fa1a67feee04a83 | CANONICAL |
| EV-03 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/build.log | 89757f193 | 7cee7cf2649f9cfb2b3cdce6a65caf3301b8d27a849dfcaf0f6b29527f44edfc | CANONICAL |
| EV-04 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/discrimination.log | 89757f193 | 93ddc335db6d7179e321ff57908c36869c9cdb4d3abd61cff0b703380bdb9082 | CANONICAL |
| EV-05 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/feature.log | 89757f193 | 6e97cf0521897ed97d97ad0c017edab9fb0811d23bf625accbf10b43df12e4cc | CANONICAL |
| EV-06 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/full-dotnet.log | 89757f193 | 0465c582e3661a9c659b6a368057e18ef052189939336cd221b3eccdf3cc2ace | CANONICAL |
| EV-07 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/full-pytest.log | 89757f193 | 6ba6fe09025c475076b0656e2d077d36dfa935627215fd692284caf8804267e3 | CANONICAL |
| EV-08 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/gates-governance.log | 89757f193 | 42a7f77b97bb6f5a7f133ac5740c2c28eb071839131072bcda80f4f2d4092ea0 | CANONICAL |
| EV-09 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/host-ipc.log | 89757f193 | eb1c9eb223bc1e124a1ec9ac85cc9b9c2201da6538e1aa7390554101c29eefdb | CANONICAL |
| EV-10 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/logs/host-unit.log | 89757f193 | 41a00278b8e38c8d222cdac8c2fcc5f6d4d2e2ab519a72b0071d726d917d7140 | CANONICAL |
| EV-11 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/RESOURCE-MANIFEST.json | 89757f193 | 84bcc3a4f25039cc13bb6cdd473c84dd1c3b11ee05bb636aed8cacbeef679637 | CANONICAL |
| EV-12 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/scope-validation.log | 89757f193 | beba8426139e3bc5ffb9b3228d6bb916de6192d4f2bc35d0341532ddbda89b75 | CANONICAL |
| EV-13 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py | 89757f193 | 7d6074657c5b1263d9a033fce3d4c21a1bf5dbc499e9a62b1b3a2170a9bf4573 | CANONICAL |
| EV-14 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/gen_manifest.py | 89757f193 | 91897243fa2c51297e3bc75201649747607bd43b192769a65ea942dbd7e6de31 | CANONICAL |
| EV-15 | AC-L6/T7 | verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py | 89757f193 | 7886534e67c7040b747d9ffc8b3c9556b5f6467f2d87410021205d9c9a83b503 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；`EV.md` 自身亦在表中。Review r1 独立复算 14/14 一致。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 Host 源/测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S1-REGISTRY-RESILIENCE-1/` 保留（IPC fixture/日志/备份，无独有产品数据） |

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b`（实现 `1ac8cc0b7` + 测试 `b56c5a0e6`；docs/evidence `89757f193`）。
- **AC 判定**：AC-L1…AC-L8 **全 MET**；无 PARTIAL/BLOCKED。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=0/P3=7 非阻断）**；P3 逐项登记（见上）。
- **门禁数字（before → after；Lead 实测）**：基线 pytest **3305/10**、.NET **1562/0/91**；本卡交付实跑 pytest **3317/10**（含 L-S4 +12）、.NET **1570/0/92**（含 L-S1 +8/+1 opt-in skip；Lead combined 全量 .NET 曾命中已知 flaky `FluentResidual2VisualEvidenceTests`，隔离复跑 1 passed）；SourceRegistry **32→40/0/1**；gated 真机 IPC 1 passed；pins **18/18**（C15 v1.5）；check（默认+`-TaskPath`）PASS；API PASS；scope **changed=2 全 ALLOWED**、禁止面零 diff、`CORE_PROTOCOL_MINOR=3`；判别性 **5/5**。
- **limitations（保留）**：B（恢复/重授权入口不存在）、C（`.corrupt-*` 无界复制）、`SOURCE_REGISTRY_UNAVAILABLE` 码义收窄、D-6 调度器投影/过时注释、Authorize 空 paths follow-up；**不宣称「恢复已可用/根级问题全解」**；L-R1 未全修。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根 PRESERVE_REFERENCED。
- **指针清理**：STATUS/PLAN 更新；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
