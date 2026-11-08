# FEA-11-RESIDUAL-4A：缺陷、裁决与 re-home（证据侧）

> 本文件是 `doc/tasks/FEA-11-RESIDUAL-4A.md` 交付记录的**证据侧附件**：逐条给出 file:line、复现方式、影响与处置。
> 本卡**不改 Core 语义、不改冻结契约字节、不改 `IHostController`**；下列缺陷均只登记，不修复（除 Core 死 seam 的删除）。

## D-1（本卡新发现）生产 dispatcher 的 host-control payload 双重 object ⇒ `INVALID_JSON`

- **位置**：`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`
  - `InvokeHostControlAsync`（`:319-391`）把 `WriteCorePayload(descriptor.Name, args, writer)`（`:469-889`，**自带 `WriteStartObject/WriteEndObject`**）交给 `CoreServiceClient.SendHostControlAsync`（`CoreServiceClient.cs:551-611`，其回调**已处于 `"payload"` 对象内部**，见 `:585-588`）。
  - journal 分支（`:341-370`）同样把 `finalPayload.WriteTo(writer)`（完整 object）写入已打开的 payload 对象。
- **后果**：`source_scan_sync`、`source_relink/repoint/resync`、`source_apply_sync_plan` 经 `HostCommandDispatcher.InvokeAsync` 时，Core 收到非法帧并回 `INVALID_JSON`（`test/python` 侧对应 `Object must be valid JSON`）。生产 UI 未覆盖该路径（现有 gated 证据均为 Core 直连或 orchestrator 直连）。
- **证据**：`verification/FEA-11-RESIDUAL-4A/evidence/dispatcher-defect-wire.txt`（真实 wire：`? | INVALID_JSON` 紧邻随后的直连有效帧）+ `logs/fea11-ipc-r4a.log`（测试记录 `dispatcher_scan_defect=INVALID_JSON` / `dispatcher_apply_defect=INVALID_JSON`）。
- **修复（需 DSH 授权；不在本卡 allowed_paths）**：把 host-control 分支改为写**字段**（与手写 payload 的既有调用一致），或让 `SendHostControlAsync` 接受完整 object；≤2 行。修好后把 `Fea11Residual4AIpcTests` 的 scan/apply 切回全 dispatcher 路径（测试已留 branch 与证据键）。
- **处置**：本卡如实记录、不修；AC-R3-2 的主链路以 `HostOperationOrchestrator`（生产编排）+ `Commands.InvokeAsync`（plan/preview/confirm/ACK/resolve）覆盖，未伪造。

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

见 `verification/FEA-11-RESIDUAL-4A/logs/mutation-m1.log` / `mutation-m2.log` / `mutation-m3.log`（临时变异 → 观察 RED → `git checkout --` 复原 → 复绿）。
