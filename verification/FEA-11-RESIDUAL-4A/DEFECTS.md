# FEA-11-RESIDUAL-4A：缺陷、裁决与 re-home（证据侧）

> 本文件是 `doc/tasks/FEA-11-RESIDUAL-4A.md` 交付记录的**证据侧附件**：逐条给出 file:line、复现方式、影响与处置。
> 本卡**不改 Core 语义、不改冻结契约字节、不改 `IHostController`**；除 Core 死 seam 删除与 D-1（DSH 2026-11-08 授权扩域）外，下列缺陷均只登记、不修复。

## D-1（已修复，DSH 2026-11-08 授权扩域）wire 帧合法性：dispatcher host-control payload 嵌套 + 两处 capability ping payload 未闭合

> **口径（DSH 红线）**：「dispatcher 的 host-control 路径与 capability ping 帧此前不合法，现已修复并有判别测试」；**不外推**到全 wire，不写「FEA-11 完全实现」。这是**两处独立缺陷**（wire 帧合法性）。

### D-1a dispatcher host-control payload 双重 object

- **位置**：`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`
  - `InvokeHostControlAsync` 非 journal 分支把 `WriteCorePayload`（自带 `WriteStartObject/WriteEndObject`）交给 `CoreServiceClient.SendHostControlAsync`（`CoreServiceClient.cs:585-588` 已打开 `"payload"` 对象）⇒ 帧非法；
  - journal 分支把 `finalPayload.WriteTo(writer)`（完整 object）写入已打开的 payload 对象 ⇒ 同类。
- **修法（本次）**：新增 `WriteHostControlPayload`（把 app-channel 产物按**字段**平铺进已打开 envelope payload）与 `WriteFlattened`（journal 分支平铺）；`WriteCorePayload` 与 app-channel wire 形状**零改动**。
- **判别测试**：`Fea11Residual4AIpcTests.ProductionDispatcherHostControlPayloadIsFlattened`（gated）——scan 经 dispatcher 不抛 `INVALID_JSON`、wire `payload` 为字段平铺、全 wire 无 `INVALID_JSON`。
- **变异 M4**（还原嵌套写法）：`logs/mutation-d1-m4.log` —— RED → 逐字节复原 → GREEN，sha256 `bccc264d…c94f9` 前后一致。

### D-1b 两处 capability ping payload 未闭合

- **位置**：`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`
  - `SourceSyncCapabilityAsync`（原 `:1016-1020`）：`writer => writer.WriteStartObject()` 缺 `WriteEndObject()`；`CoreProtocol.BuildRequest`（`CoreProtocol.cs:33-34`）的 payload 回调必须写**完整 object** ⇒ core.ping 帧未闭合 ⇒ `INVALID_JSON`；
  - `RunCapabilityProbeAsync`（原 `:1082-1086`）同型（其 `catch (CoreOperationException)` 会静默降级）。
- **影响（限定该路径）**：`source_scan_sync` 的 dispatcher capability gate 走 `SourceSyncCapabilityAsync`（`RequiredCapabilities("source_scan_sync")` 为空，见 `HostCommandRegistry.cs:94-101`）⇒ **修复前，任何 source-sync host-control 命令都不可能经生产 dispatcher 跑通**；AC-R3-2 此前的"经生产 dispatcher"路径从未跑通（仅限该路径，不外推其它命令族）。
- **修法（本次，授权严格两处）**：两处回调补 `WriteEndObject()`；HostRuntime 其它逻辑零改动。
- **变异 M5**（还原未闭合）：`logs/mutation-d1-m5.log` —— gated 3 用例 RED → 逐字节复原 → GREEN，sha256 `8226278…54e1` 前后一致。

### before / after（D-1 修复）

| 门禁 | before | after |
|---|---|---|
| gated `Fea11Residual4AIpcTests` | 2 passed（含 `dispatcher_*_defect=INVALID_JSON` fallback；**全 dispatcher 路径不通**） | **3 passed / 0 failed**（全 dispatcher，无 fallback） |
| 判别测试 `ProductionDispatcherHostControlPayloadIsFlattened` | 不存在 | 1 passed（变异 M4 RED→绿） |
| `dotnet test NewManga.Host.Tests` | 301 / 0 / 69 | 301 / 0 / 70（+1 gated skip） |
| 全量 .NET `NewManga.sln` | 1732 / 0 / 100 | 见 §D-1 after 数字（本次复跑） |
| `pytest tests/fea11` | 217 passed | 217 passed |
| `pytest tests` | 3395 / 10 skipped | 3395 / 10 skipped |

**证据**：`logs/fea11-ipc-r4a.log`（3/3 全 dispatcher）、`logs/mutation-d1-m4.log`、`logs/mutation-d1-m5.log`；修复前的真实 wire 保留为 before 证据：`evidence/dispatcher-defect-wire.txt`。

## D-2 `needs_confirmation` 零生产者（→ `FEA-11-DIAG-SURFACE-1`）

- **位置**：`src/infrastructure/sqlite/source_sync.py:885-911` 与 `src/infrastructure/sqlite/library.py:2461-2471` 的 binding 写入调用点均传 `'healthy'`；`supersede_binding`→`superseded`、`mark_binding_missing`→`missing`；`src/application/sources/service.py:536-537` 的 `defer` 不改状态 ⇒ 旧 binding 仍 `healthy`。
- **后果**：C-17:273「defer 后旧绑定保持 needs_confirmation」在运行时不可达；歧义页仍满足 C-05 P8 而可见（V 不扩的反面）。
- **处置**：本卡不改 Core 语义；**具名 re-home `FEA-11-DIAG-SURFACE-1`**（需 C-17 additive）。AC-R3-1 的 Host 投影按冻结 receipt 的 `status` 字段实现（生产者缺失不影响投影正确性）。

## D-3 `L-S4-2` folder identity 取首成员（→ 只登记，不修）

- **位置**：`src/application/importing/referenced/runtime.py:978-991` —— `_volume_serial()`/`_file_id()` 在无 `container_facts` 时返回 `folder_entries[0][1]`（**首个成员**的 volume/file id），`_container_size()`（`:994-997`）返回成员 size 之和。
- **契约**：`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:216`（folder 行）要求 **目录 identity = volume serial + file id**（目录本身），content digest 为 `folder-manifest/1`。
- **后果**：folder 源的 location identity 随首成员变化；`_ensure_target_version` 会据此新建 location 行（`service.py:725-761`），与「目录身份稳定」不符；`source_sync.py` 的 `_resolve_grants`（首成员 facts）同源问题。
- **处置**：本卡只登记（AC-R3-3 的 folder 用例证明 fold relink 被 typed 拒绝、resync 逃生可用，不改语义）。修复需新卡（身份模型）。

## D-4 `L-M4` 裁决：不实现（→ `FEA-11-LEGACY-RECOMPUTE-1`）

- **事实**：`doc/tasks/FEA-11-MATCH-1.md:188` 自述「按冻结参数重算旧证据」需**旧字节 + 新 grant**；`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` §5.1 `ScanSourceSync`（scope review 记 `:213`）请求闭集只给目标侧 `grant_ids`、§5.3 `SourceBase`（记 `:238`）仅 `(source_id, version_id, content_digest)`；`src/application/sources/scanner.py:540-587` 只保留首个 grant、`:324-328`/`:401-407` 旧条目只从 DB 行读。
- **裁决**：若实现必须改 pinned C-17（18 pins 之一）⇒ **不是 0 pin 项**。本卡**不实现**，且**不写**「已按冻结参数重算旧证据」。
- **re-home**：`FEA-11-LEGACY-RECOMPUTE-1`；**reopen 条件 = C-17 UNFREEZE + 新 capability（旧证据/旧字节 grant 面）**。
- **L-M1（PDF 插页 pixel profile）**：BLOCKED，re-home `FEA-11-PDF-RECONCILE-1`（未在本卡做；不得写 NA/PASS）。

## D-5 AC11-9 的旧绑定 pre-sync resolve 限制（诚实登记，非缺陷修复项）

- **事实**：`seen` 的旧绑定由 `tests/fea11/support/ipc_seed.py` 直接播种，没有 import-time grant→binding 映射（C-16 R1-I002：`prepare_referenced_rendition` 只认 `find_bound_for_source`，`src/application/importing/referenced/resolve.py:73-90`）。
- **后果**：同步前对旧绑定的 Core `resolve_page_resource` 是 typed `SOURCE_ACCESS_DENIED`，**不能**读出旧资源字节。
- **本卡做法**：sync 前记录旧 binding 行（`binding_id/verified_digest`）+ 旧 entry `content_digest` + 源容器字节；ACK 后断言旧摘要行逐字不变、`page-rendition-p1` 从未发布、新 v2 键/新字节（蓝）成立。**未伪称已 resolve 旧绑定**。
- **re-home 建议**：真实导入产生的旧绑定可在同一 Core 进程内通过 `AuthorizeSourceReadForRun` 建立映射后读取（C-16 v1.3 §2.4）；若需要 gated 证据，建议在后续卡以「真实 import → sync」链路补。

## D-6 HOST-AUTH-1 陈旧表述核对（无需修改）

- `doc/STATUS.md:8` 与 `doc/REBASELINE_PLAN.md:14/53` 均已写 HOST-AUTH-1 `done`（ADJ §7.7 已修，实际 `5cbec0e82` 翻转）。本卡只读核对，未改字节。

## D-7 变异自检

- AC 层（前次）：`logs/mutation-m1.log`（删 folder 拒绝分支 → AC-R3-3 RED）、`mutation-m2.log`（ACK 前放行 gate → AC-R3-2 RED）、`mutation-m3.log`（投影返回全部页 → AC-R3-1 RED）；均逐字节复原并复绿。
- D-1 层（本次）：`logs/mutation-d1-m4.log`（还原 dispatcher 嵌套 → 判别测试 RED）、`mutation-d1-m5.log`（还原 capability ping 未闭合 → gated 3 用例 RED）；均记录变异前/变异后/复原后 sha256（复原后与变异前一致），复原后 GREEN。
