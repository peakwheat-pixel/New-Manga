---
id: FEA-11-L-S4-B-AUTO-RECOVERY-1
title: 重授权后的零交互恢复（L-S4-B：reattest 条件写 + Host 触发 + App 成功分支；C-16 v1.5）
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH」；权威 scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`（fresh subagent `6f75eb58-…`，**BLOCKED 按旧卡面**；推荐形状 = C-16 v1.5 `source.reattest/1` + `ReattestSourceLocation` 条件写 + `roots_available` 字段，1/18 pins）；Codex 不可用 → ZCode 故障转移裁决（见 PREREQ 卡）；DSH 裁决 D-1…D-8（见下）；依赖 PREREQ（C-16 v1.5 UNFREEZE）；ZCode 裁决：接受 b3 形状（1 pin），补充 AC-LS4B-9/10
suggested_owner: codex
owner: l-s4b-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修/scope review）：r1 `5ad3bb8a-…`（**approved** P0=0/P1=0/P2=0/P3=5 非阻断；reviewed_head `30bdeb4ce`）；报告 `doc/reviews/FEA-11-L-S4-B-AUTO-RECOVERY-1-r1.md`
depends_on:
  - FEA-11-L-S4-B-PREREQ-1
base_commit: a7360839d
branch: null
worktree: null
integration_commit: 30bdeb4ce
delivery_head: 30bdeb4ce
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-LS4B-1 能力门禁/四象限**：`source.reattest/1` 缺失（旧 Core）→ Host 不发送、行为与现状一致（target 仍 typed skip）；新×新才生效；能力探测异常不发。 <<MET>>
- [x] **AC-LS4B-2 Host 候选精确性**：仅「旧条目已撤销、恰 1 根、live 候选唯一且恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、kind 非 folder」进入候选；其余零 wire。 <<MET>>
- [x] **AC-LS4B-3 Core 身份门禁与零写**：请求 closed shape；host-only/session；grant live/未过期/未撤销；`grant.scope.source_id == source_id`；grant facts 四键等于当前 location；拒绝/无匹配零写。 <<MET>>
- [x] **AC-LS4B-4 单行写/幂等/单调**：成功只改 `registry_id/authorization_generation` 两列（`last_verified_at` 保持原值、不刷新审计时间）；location 行数不变；其余列逐列不变；重复调用 `updated:0` 且零写（字节不变）；同 registry 代次不倒退、跨 registry 允许 1。 <<MET>>
- [x] **AC-LS4B-5 无授权/无 identity 重建/不扩面**：Core 不创建/复活 grant；Host Registry 不新增/撤销/改 roots/identity/generation（仅既有 `last_used_at`）；不新增 source/version/entry；无新错误码/能力（除冻结的 `source.reattest/1`）/wire minor/schema/依赖。 <<MET>>
- [x] **AC-LS4B-6 触发与恢复**：B1 重授权成功后（App 成功分支）触发 reattest → 冷启动/下一次 refresh 枚举不再丢该 source（真实 IPC 闭环）；失败 typed 且不自动重试成自动恢复。 <<MET>>
- [x] **AC-LS4B-7 零漂移/门禁**：pins 18/18（C16 v1.5）；check（默认+`-TaskPath`）PASS；API inventory PASS；scope diff ⊆ allowed_paths；全量 pytest/.NET 不降（基线 **3317/10、1617/0/93**）；跑后恢复 `verification/FEA-09`。 <<MET>>
- [x] **AC-LS4B-8 不夸大**：只承诺「B1 显式重授权后无需重导入/apply，扫描枚举恢复」；不承诺撤销后自动恢复、不承诺自动重新授权、不承诺 folder；`source_reset_registry` 后无旧条目可桥接 → limitation；L-R1 未全修。 <<MET>>
- [x] **AC-LS4B-9 每轮至多一次 reattest**：同一 refresh 轮中每个 target 至多一次 `ReattestSourceLocation`，无重试风暴；失败 typed 即止（不循环重试成自动恢复）。 <<MET>>
- [x] **AC-LS4B-10 措辞红线**：「零交互」严格限定为「B1 显式动作之后的传播」；卡/Handoff/EV/UI 禁止出现「自动恢复/自愈/自动重新授权」承诺。 <<MET>>

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

- **Owner**：`l-s4b-impl`（DSH Agent Teams；Lead `lead`）；交付日期 2026-11-07。
- **实现起点**：`c6ca1aa3c`（`main`，工作树 clean）；卡 `base_commit=a7360839d`。
- **delivery_head=`30bdeb4ce`**；commit 链：
  - `ec171f0d3` Core `ReattestSourceLocation`（`src/application/sources/reattest.py` + `src/bootstrap/core_service.py`）
  - `3ccb0509e` Host 能力探测/`SourceRootReattestPlanner`/枚举 pre-pass/`HostRuntime` 接线
  - `f76620e39` App B1 成功分支触发既有 scan refresh
  - `c4345a632` 测试（Core 矩阵 / Host / App / gated IPC）
  - `30bdeb4ce` DSH 批准扩域的既有 capability 断言 +`source.reattest/1`（仅预期 1 行）
- **AC-LS4B-1…10 全 MET**（逐项证据见 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/EV.md` §1 与 Handoff `doc/handoffs/FEA-11-L-S4-B-AUTO-RECOVERY-1-30bdeb4ce.md`）。
- **实跑门禁**：Core 定向 100 passed；回归 89 passed；Host 24/0/0；App 18/0/0；gated 真 IPC 4/0/0；
  判别性 11/11 RED_AS_EXPECTED；全量 pytest **3360/10**（基线 3317/10）；全量 .NET **1644/0/94**（基线 1617/0/93）；
  pins **18/18（C16 `a7f57ebd…`）**；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；
  scope **PASS**（diff ⊆ allowed_paths、zero-drift=[]、`PROTOCOL_MINOR=3`、C07 registry 无新命令）；跑后 `verification/FEA-09` CLEAN。
- **扩域（DSH 已批准）**：`tests/core/test_core_service.py`（2 处）、`tests/fea09/test_referenced_wire.py`（1 处）
  精确 capability 列表各 +1 行 `"source.reattest/1",`；零行为改动；.NET 侧未使用预批。
- **措辞红线**：只承诺「B1 显式重授权后无需重导入/apply，**枚举**恢复」；不写「自动恢复/自愈/自动重新授权」。
- **登记 limitation**：**L-S4-B-1** 扫描执行面仍被既有 `ResolveRegistryEntry` revoked-exact-match 拦住（tick typed error），
  本卡不宣称扫描执行成功；B2 `roots_available` 实现延后；folder（L-S4-2）；`source_reset_registry` 后无旧条目可桥接；L-S4-1/L-R1 未全修。
- **证据目录**：`verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/`（`EV.md`、`RESOURCE-MANIFEST.json`、`scope-validation.log`、
  `changed-files.txt`、`logs/**`、`tools/**`）。未 push、未建 worktree。

## Review r1 处置（DSH，2026-11-07；append-only）

- 独立 r1 `doc/reviews/FEA-11-L-S4-B-AUTO-RECOVERY-1-r1.md`（`5ad3bb8a-…`；reviewed_head `30bdeb4ce`）：**approved，P0=0/P1=0/P2=0/P3=5 非阻断**；AC-LS4B-1…10 全 MET；独立复跑 Core 100/回归 89/Host 24/App 18/gated IPC 4/全量 pytest 3360/10/pins 18/18/check/API 全 PASS；2 个破坏点独立 RED。
- **P3 处置（登记接受，均非阻断）**：R1-P3-01 Manifest worktree/autocrlf 口径；R1-P3-02 discrimination 日志未记运行 HEAD；R1-P3-03 scope 工具命令数常量为打印常量；R1-P3-04 「16 表快照」措辞 vs 实际 36 表全表/15 表扫描相关；R1-P3-05 gated fixture 沿用既有 scan 根（已披露、无 tracked 副作用）。均不改变产品行为/AC 判定，登记后续维护批可改进。
- **不得外扩**：扫描执行面（`ResolveRegistryEntry`）→ 另卡 `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`（proposed）；B2/folder/L-S4-1/L-R1 保留。
- 不改变实现/测试字节（`30bdeb4ce`）与 AC-LS4B-1…10 MET 判定。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/changed-files.txt | 9dda04b75 | 91950b0667aacbb77e84a24ac9e271bd69aaf0ac320986f2978e85441fbedb95 | CANONICAL |
| EV-02 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/EV.md | 9dda04b75 | 21063152ed0854d00cd5870579084d325b326fd0bf528035280144c2850bf04e | CANONICAL |
| EV-03 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/app-unit.log | 9dda04b75 | 1bccd5074c3101d2ce02d8c43746a7ae8bf28d75d2d5a9883944055cf67812b0 | CANONICAL |
| EV-04 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/discrimination.log | 9dda04b75 | b95f9f7d7f0a0e04474a3b2d3d2b535c9d54ef6302ec13596b8a59b2e1786ffd | CANONICAL |
| EV-05 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/feature.log | 9dda04b75 | 6c3d51d16ac3346e0a3000b36c5740185af37a3c9ca85629c76c7dcc019d9f9f | CANONICAL |
| EV-06 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/full-dotnet.log | 9dda04b75 | f9f8f8eefe6e05a044cfdb22129fa7dd7056a4b4b7ca90103056b168c965ad27 | CANONICAL |
| EV-07 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/full-pytest.log | 9dda04b75 | 490455e92cade6d6ed7b09da34bcd9067ff58b01456e40107cd1420b33c57650 | CANONICAL |
| EV-08 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/gates.log | 9dda04b75 | 28778864dd07179bbfd70910cb823f7074a1524584958c39929839892d1be001 | CANONICAL |
| EV-09 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/host-ipc.log | 9dda04b75 | df0efff67e2ee229643ca1f28f0e86454e0996ca0337a7554dda9ea704d0bfea | CANONICAL |
| EV-10 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/host-unit.log | 9dda04b75 | 0b781c5e433ae6d047caa767abaec30cdcd5c0c58ab558c527ad67a00c1ad38d | CANONICAL |
| EV-11 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json | 9dda04b75 | ce5b4be470d3e9b1f1e760b13eae9f46ddcc4550547b5e78c94196b20ccab18c | CANONICAL |
| EV-12 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.txt | 9dda04b75 | cc38ff01b63e02c9cc59787dc87d9f43c6c407b6e433ff01d6d034e843617eab | CANONICAL |
| EV-13 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/regression-74.log | 9dda04b75 | 057b8fcd1cd9b90e36c645457be03bcf2e9718ee9900b5eee5f78f3109495f9d | CANONICAL |
| EV-14 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/RESOURCE-MANIFEST.json | 9dda04b75 | 449386861ed42066fc08d6abe93697ff1dbcfdf626a676c3b2a960d7551e60fc | CANONICAL |
| EV-15 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/scope-validation.log | 9dda04b75 | f28dd4b04fd756c40b000ff409e25f3c8159143e9ebc39e86c9375462c8d3ab5 | CANONICAL |
| EV-16 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/discrimination.py | 9dda04b75 | 8628074385f89122fa3500c27557ee5ccba54e2b653708e94981841869116593 | CANONICAL |
| EV-17 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/gen_manifest.py | 9dda04b75 | 8fa63cb69e9fd279cbcdfb85c4a972adb6b72a5e46feb9cf6fe70f6fbaa6e962 | CANONICAL |
| EV-18 | AC-LS4B-8/9 | verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/scope_validation.py | 9dda04b75 | c48044b2bc9df528c6a4487ba5c9f235a6bfe69bef4e044bd7495f48f6703181 | CANONICAL |

> 证据树逐文件 sha256 以本表为准；Review r1 独立复算 32/32 worktree 匹配（committed blob 与 worktree 的 CRLF 差异见 R1-P3-01）。review/handoff 不在 evidence_dir，按卡面/Handoff 引用。

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档 | - | NOT_APPLICABLE | - | - | 本卡仅改 Core/Host/App 源与测试 + 卡/Handoff/证据；仓内 0 删除/0 移动/0 归档；仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1/` 与既有 `FEA-11/fixtures`（已披露）保留（无独有产品数据） |

## Closeout Record（2026-11-07）

- **状态**：`done`；`delivery_head`/`integration_commit` = `30bdeb4ce`（实现 `ec171f0d3` + Host `3ccb0509e` + App `f76620e39` + 测试 `c4345a632` + 扩域 `30bdeb4ce`；docs/evidence `9dda04b75`）。
- **AC 判定**：AC-LS4B-1…AC-LS4B-10 **全 MET**；无 PARTIAL/BLOCKED（L-S4-B-1 为已知 limitation，AC-LS4B-6 只承诺枚举恢复）。
- **Review 处置**：独立 r1 **approved（P0=0/P1=0/P2=0/P3=5 非阻断）**；P3 逐项登记接受。
- **门禁数字（before → after；Lead 实测）**：全量 pytest **3317/10 → 3360/10**（+43 本卡）；全量 .NET **1617/0/93 → 1644/0/94**（+27 单测、+1 gated skip）；Core 定向 100；回归 89；Host `SourceReattest` 24/0/0；App `SourceRecovery` 18/0/0；gated 真实 IPC 4/0/0（含 B1→reattest→枚举恢复闭环）；pins **18/18**（C16 v1.5 `a7f57ebd…`）；check（默认+`-TaskPath`）PASS；API inventory PASS；scope **changed=35 全 ALLOWED**、禁止面零 diff、`CORE_PROTOCOL_MINOR=3`、C-07 registry 无新命令（111 不变）；判别性 **11/11**；跑后恢复 `verification/FEA-09`。
- **limitations（保留）**：**L-S4-B-1**（扫描执行面仍被 `ResolveRegistryEntry` 同路径 revoked fail-closed 拦住，tick typed error；本卡只承诺枚举恢复）→ 另卡 `FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1`；B2 `roots_available` 实现延后；folder（L-S4-2）；`source_reset_registry` 后无旧条目；L-S4-1/L-R1 保留；「零交互」仅指 B1 显式动作之后；不宣称扫描恢复/自动恢复。
- **Resource Manifest / 资源处置**：仓内删除/移动/归档 0；仓外隔离根与既有 fixtures PRESERVE_REFERENCED。
- **指针清理**：STATUS 无活动 Task；PLAN 本节点 done；TASK_LEDGER 重生成。
- **push**：Lead 统一 push（PRE/POST/AHEAD 记录见状态文件）。
