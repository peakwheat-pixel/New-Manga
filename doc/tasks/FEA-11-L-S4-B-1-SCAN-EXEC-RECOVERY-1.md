---
id: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
title: 扫描执行面恢复（L-S4-B-1：枚举 target 执行使用自身 live registry 身份；Host-only，零契约）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md`（fresh subagent `fc6e9df6-…`，**READY-TO-FREEZE**；推荐 Host-only 形状：枚举 target 执行用其自身已核验的 live `(registry_id, generation)`，不改 `ResolveRegistryEntry` 非枚举语义；**0 UNFREEZE / 18 pins 全不变**）；Codex 不可用 → ZCode 故障转移裁决（见卡）；DSH 裁决 S-1…S-5（见下）
suggested_owner: codex
owner: l-s4b1-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review）：r1 `9403610b-…`（**approved** P0=0/P1=0/P2=0/P3=9 非阻断；reviewed_head `bcc88e4a2`）；报告 `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-r1.md`
depends_on:
  - FEA-11-L-S4-B-AUTO-RECOVERY-1
base_commit: 58395b9a2
branch: null
worktree: null
integration_commit: bcc88e4a2
delivery_head: bcc88e4a2
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-SER-1 枚举执行面恢复（主 AC）**：「旧条目 revoked + 新 live 同路径同物理身份 + Core 行 reattest 到 live」状态下，scheduler target 的 RegistryId = live；`ScanAsync` 用 target 自己的 live `(registry_id, generation)` 铸 grant，发送恰 1 个 `ScanSourceSync`，结果 `ok`/`changed`，**不得** error/`SOURCE_ACCESS_DENIED`；wire 无绝对路径。判别性：仍走 path-only resolver → RED。 <<MET>>
- [x] **AC-SER-2 fail-closed 矩阵不变**：target 自身 registry：缺失 → `Skipped(SOURCE_REGISTRY_UNAVAILABLE)`；revoked → `Skipped(SOURCE_GRANT_REVOKED)`；generation 漂移 → `Skipped(SOURCE_REGISTRY_BUSY)`；root 缺失/替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`；整库不可读 → 现有 typed；全部零 grant/零 frame。 <<MET>>
- [x] **AC-SER-3 非枚举语义零变化**：`ResolveRegistryEntry` 对 `!IsEnumerated` 保持 exact-first、revoked-exact→null、containment fallback；既有 `RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` 原样通过。 <<MET>>
- [x] **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构**：扫描前后 `DescribeRegistryEntries`（不含 `last_used_at`）结构相等；无新/撤销条目、无 roots/identity/generation 变化、无 `Register`/`Revoke`/`Reset` 调用；旧 revoked 行保留。 <<MET>>
- [x] **AC-SER-5 零漂移/门禁**：pins 18/18（C16 v1.5 `a7f57ebd…`）；check（默认+`-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3360/10、1644/0/94**）；跑后恢复 `verification/FEA-09`。 <<MET>>
- [x] **AC-SER-6 不夸大**：只承诺**枚举 target 的扫描执行恢复**；不承诺 Run 面恢复、不承诺自动恢复/自愈；L-S4-B-1 剩余面（RunSourceRange）与 B2/folder/L-S4-1/L-R1 保留。 <<MET>>

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

- **交付完成（2026-11-07）**：`delivery_head=bcc88e4a2`；commit 链 `8709d6159`（`SourceScanScheduler.cs` 枚举 target 执行面改用自身已核验 live entry + 纯函数 `SelectEnumeratedEntry`）→ `bcc88e4a2`（新增 `SourceScanExecutionRecoveryTests.cs` 8 例 + `Fea11ScanIpcTests.cs` gated 闭环 tick 由 error 升级为 ok）；随后同批 docs/evidence 提交（本卡面/Handoff/`verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**`）。
- **AC 判定**：AC-SER-1…6 **全 MET**（逐项 `<<MET>>`；见 `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/EV.md` §1）。
- **实跑门禁**：build **PASS 0/0**；Host 新单测 **8/0/0**；回归（registry/scheduler/reattest）**123/0/1 skip**；gated 真 IPC **4/0/0**（tick `ok`、`scan_frames=1`）；定向 pytest **89 passed**；全量 pytest **3360/10**（起点同值）；全量 .NET **1652/0/94**（起点 1644/0/94，+8 本卡）；pins **18/18**（C16 `a7f57ebd…`）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**（61 不变）；scope **PASS**（delivery 全 ALLOWED、禁止面零 diff、C16/C17 blob 零漂移、`PROTOCOL_MINOR=3`）；判别性 **6/6 RED_AS_EXPECTED**；跑后 `verification/FEA-09` CLEAN。
- **before/after**：before = L-S4-B gated 证据 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json`（`last_result="error"`）；after = `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.json`（`last_result="ok"`、`scan_frames=1`、wire 无路径）。
- **措辞红线**：只承诺**枚举 target 的扫描执行恢复**（B1 显式重授权 → 既有 refresh/reattest → 枚举 → 下一个未被既有 backoff 抑制的 tick）；不写「Run 面恢复/自动恢复/自愈/自动重新授权/撤销后自动放行」。
- **登记 limitation**：Run 面（`HostRuntime.RunSourceRange` 仍按路径解析，未测未修）→ 另卡 `L-S4-B-2-RUN-RANGE-RESOLVE`（若复现）；B2 `roots_available` 延后；folder（L-S4-2）；L-S4-1、L-R1、多根 first-root 保留；backoff 延迟口径已写明；revoked 行累积为 B1 既有行为（本卡只读）。
- **证据目录**：`verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/`（`EV.md`、`RESOURCE-MANIFEST.json`、`scope-validation.log`、`changed-files.txt`、`logs/**`、`tools/**`）。未 push、未建 worktree；`status` 未改（由 Lead 维护）。

## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 r1 `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-r1.md`（`9403610b-…`；reviewed_head `bcc88e4a2`）：**approved，P0=0/P1=0/P2=0/P3=9 非阻断**；AC-SER-1…6 全 MET；独立复跑 Host 8/0/0、回归 123/0/1、gated IPC 4/0/0（before error→after ok）、pytest 89、pins 18/18、check/API 全 PASS；2 个破坏点独立 RED+恢复。
- **P3 处置（登记接受，均非阻断；权威清单以 r1 报告 §5 为准）**：①Manifest 混入未跟踪 gitignored pyc；②`repo_head_at_generation=d87416514` 为 amend 前提交；③scope 23 vs 实际 24（manifest 生成晚于 scope 快照）；④`ipc-fixture.txt` 首行西里尔字符；⑤`VerifyEnumeratedTarget` out 参注释精度；⑥测试以 NRE 作「越过授权门」信号（fixture 脆弱）；⑦无独立 ZCode 裁决文件/会话 ID（仅卡面/Handoff 摘要）；⑧AC-SER-2 未区分既有「无匹配 root→Skipped」子场景；⑨EV 未复述 C-17 §5.3 主体解释（0-pin 前提）。→ 下次证据维护批规整；不改变产品行为/AC 判定。
- **Run 面**：本卡不含（`HostRuntime.RunSourceRange` 仍按路径解析，零 diff）→ 另卡 `FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1`（proposed）。
- 不改变实现/测试字节（`bcc88e4a2`）与 AC-SER-1…6 MET 判定。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/changed-files.txt | 0c1390b2a | e25f4525885e663585f5b94136d1cf8285ef25053f508f3e3e4e7c0d38df84ad | CANONICAL |
| EV-02 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/build.log | 0c1390b2a | 1e45040d243e6957dc23a0e35077e24fee55894871bb7327d7ebcfa98d85c665 | CANONICAL |
| EV-03 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/discrimination.log | 0c1390b2a | 2e4ba50d49f114ef7c2c934bc0de023fa3349a2e25bce681ab86af5279e7de9b | CANONICAL |
| EV-04 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/full-dotnet.log | 0c1390b2a | 09cdee66dd24710ed29675108f0660762bb1027c9e2328db443e5d0cc21a5351 | CANONICAL |
| EV-05 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/full-pytest.log | 0c1390b2a | fb611e962c53954d98cc6fddc0b8d8e56c3440776cfd149e4f28c80a436b82e1 | CANONICAL |
| EV-06 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/gates.log | 0c1390b2a | 9cbfcff5219c0e2d4c725b5745cb162d667a81bcbd2f1ae8c39921d22a688253 | CANONICAL |
| EV-07 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/host-ipc.log | 0c1390b2a | c098b45270eaa21a89736c1b7ce2a4543c2bc534ab0441d0b605a0ac0be0f1c3 | CANONICAL |
| EV-08 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/host-unit.log | 0c1390b2a | 4b5300bbc1addb21247e067cb79a15346ad79644c64246c09a3157102c843be9 | CANONICAL |
| EV-09 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.json | 0c1390b2a | 1f91df56a86e2976e3b0fbb87c357211799f58ddad0fd69cb53b996d784fdb4b | CANONICAL |
| EV-10 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-closed-loop.txt | 0c1390b2a | 91710e438431b0c4c9a7b428b57b60fa856773864311b87eb961a7d76668c305 | CANONICAL |
| EV-11 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/ipc-fixture.txt | 0c1390b2a | 18a7aef03730dd3cb33dfc52bb5697e3b82957483cf4bb86dbca7fbbb8113e2d | CANONICAL |
| EV-12 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/regression-74.log | 0c1390b2a | 200db0f43512671cb231d56c411992e2b921cf2e793506107c8d02df25931d71 | CANONICAL |
| EV-13 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/logs/regression.log | 0c1390b2a | 9c8f1770c650c1d80c66f0dd35ad9196768ab9507fdbef52c17d6d57950b78e6 | CANONICAL |
| EV-14 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/RESOURCE-MANIFEST.json | 0c1390b2a | 3a2d165756e96fed23ffd6539327ce2452e34ea6d649e094e7946abac62bfad1 | CANONICAL |
| EV-15 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/scope-validation.log | 0c1390b2a | 3ca4303f556beb14b9afef5e6c1cff9da7a6e1fa2e8e9018965495b2d63f332a | CANONICAL |
| EV-16 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/discrimination.py | 0c1390b2a | 1d804064839cb7f02b7ebd158baca6eb186a6e561d3b61af7b071ace0f6c0c10 | CANONICAL |
| EV-17 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/gen_manifest.py | 0c1390b2a | 324d75fe15bfeac35fec21204982f272abcf10d9440e42309f217bdb1e609c44 | CANONICAL |
| EV-18 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/tools/scope_validation.py | 0c1390b2a | 001ceeb3624b69796341f9bfca7f93ad418e7ba2d0a2107682077e7628593f1d | CANONICAL |
| EV-99 | AC-SER-5 | verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/EV.md | 0c1390b2a | 38d73fd885c8477e3beffe7ae7ed9a9c171d03e088928e25b6c91f887823aaf9 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；review/handoff 不在 evidence_dir，按卡面/Handoff 引用。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 Host `SourceScanScheduler.cs` + 测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根与既有 `FEA-11/fixtures`（已披露）保留 |

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `bcc88e4a2`（实现 `8709d6159` + 测试 `bcc88e4a2`；docs/evidence `0c1390b2a`）。
- **AC 判定**：AC-SER-1…AC-SER-6 **全 MET**；无 PARTIAL/BLOCKED。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=0/P3=9 非阻断）**；P3 登记接受。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3360/10 → 3360/10**；全量 .NET **1644/0/94 → 1652/0/94**（+8 本卡 Host 测试）；Host 新单测 8/0/0；回归 123/0/1 skip；gated 真实 IPC 4/0/0（tick error→ok，`scan_frames=1`，before/after 证据）；定向 pytest 89；pins **18/18**；check（默认+`-TaskPath`）PASS；API inventory PASS；scope **24 文件全 ALLOWED**、禁止面零 diff、`CORE_PROTOCOL_MINOR=3`、C16/C17 blob 零漂移；判别性 **6/6**；跑后恢复 `verification/FEA-09`。
- **limitations（保留）**：**Run 面未含**（`HostRuntime.RunSourceRange` 仍按路径解析；另卡 `FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1`）；B2 `roots_available` 实现延后；folder（L-S4-2）；L-S4-1/L-R1 保留；backoff 口径=「下一个未被既有 backoff 抑制的 tick」；只承诺枚举 target 的扫描执行恢复；不宣称自动恢复/自愈/自动重新授权/撤销后放行。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根与既有 fixtures PRESERVE_REFERENCED。
- **指针清理**：STATUS 无活动 Task；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
