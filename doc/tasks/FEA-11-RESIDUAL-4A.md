---
id: FEA-11-RESIDUAL-4A
title: FEA-11 收口（AC11-7 诊断出口 / AC11-9 Host 级生产链路 / AC11-6 folder 用例 / L-M4 裁决 / AC 回填）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-08 残余收口指令（R3）；独立 scope review `doc/reviews/FEA-11-RESIDUAL-4A-scope-r1.md`（session `88de37b5-…`，verdict **NOT_RECOMMENDED** → DSH 按其 §5 改写后冻结）；DSH 2026-11-08 裁决（ADJ §7.7）：0 pin、窄口径 done（L-M1/L-M4 具名 re-home）
suggested_owner: dsh
owner: fea11-residual4a-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 于实现交付后指派）
depends_on:
  - FEA-11
base_commit: c5bd49276
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RESIDUAL-4A
allowed_paths:
  - doc/tasks/FEA-11-RESIDUAL-4A.md
  - doc/tasks/FEA-11.md
  - doc/reviews/FEA-11-RESIDUAL-4A-*.md
  - doc/reviews/ADJ-2026-11-RESIDUAL-WAIVER.md
  - doc/handoffs/FEA-11-RESIDUAL-4A-*.md
  - verification/FEA-11-RESIDUAL-4A/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - tests/fea11/test_source_relink.py
  - tests/fea11/test_source_sync.py
  - tests/fea11/conftest.py
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/HostFixture.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - src/infrastructure/sqlite/source_sync.py
out_of_scope:
  - 冻结契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins（**L-M4 需 C-17 UNFREEZE → 本卡只 re-home，不实现**）
  - `IHostController.cs`（加方法即改 C-07 pin → 1 pin，0 pin 不允许）、`src/bootstrap/**`（除死 seam 处置经 DSH 预批外）
  - Core 语义修改：`needs_confirmation` 写入者修复（本卡只登记缺陷并 re-home `FEA-11-DIAG-SURFACE-1`）；folder 身份键修复（只登记 `L-S4-2`）；PDF raster seam（L-M1 re-home）
  - 崩溃点矩阵（已 re-home `FEA-11-HOST-AUTH-3`）；UI 用户流程；真实用户数据/AppData/回收站；push；新依赖
---

# FEA-11-RESIDUAL-4A：FEA-11 收口（0 pin）

> **状态 `ready`**（base `c5bd49276`；0 pin）。目标：把 `FEA-11`（`closed_with_limitations`）翻 `done`，方式 = **5 条 AC 回填 + 4 条 AC 补做（其中 2 条按裁决 re-home 子项）**。
> **术语/口径**：
> - `[x] <<MET>>` **不得带原因**（`check.ps1:838-845`）；limitation 只能写 closeout/ADJ。
> - **L-STARTUP**（AC11-1 子项）→ `NOT_APPLICABLE: 契约解释+产品范围（AD4-003 §3.6 / C-01b SC-25 四项组合不含启动全量扫描；保留 NOT_RUN）`。
> - **L-M1（PDF 插页）/ L-M4（旧证据重算）→ BLOCKED 具名 re-home**（`FEA-11-MATCH-1` 承接卡后另立：L-M1 → `FEA-11-PDF-RECONCILE-1`；L-M4 → `FEA-11-LEGACY-RECOMPUTE-1`，需 C-17 UNFREEZE）。

## 缺陷/缺口（base `c5bd49276`，scope review 已核）

- AC11-1/3/4/5/8：已有承接卡/证据，**卡面 AC 行未回填**（append-only 补登）。
- AC11-6：folder relink typed 拒绝**无测试**；成员重排/多项目**无用例**；folder repoint/resync 逃生路径**无证据**。
- AC11-7：无 binding-status 查询面；`needs_confirmation` **零生产者**（`source_sync.py:885-911`、`library.py:2461-2471` 调用点全 `healthy`）；Core 死 seam `source_sync.py:1030-1047` 零调用者；`defer` 不改状态 ⇒ 与 C-17:273 不符（缺陷）。
- AC11-9：现有 gated 用例 **Core 直连**、未走 HostRuntime/dispatcher、sync 前未 resolve 旧绑定。
- AC11-10：证据/manifest 停旧 head；最终 head 无 approved Review。
- 治理：`doc/STATUS.md:8` 与 `doc/REBASELINE_PLAN.md:53` 仍写 HOST-AUTH-1 `closed_with_limitations`（实际已 done）。

## Acceptance Criteria（冻结）

- [ ] **AC-R3-1（AC11-7 诊断出口）**：Host 只读投影从 durable journal/receipt 读 `bindings[].status ∈ {missing,needs_confirmation}`，**不新增 Core 命令/能力/wire 字段、不改 `IHostController`**；断言「不扩 V(p,t)」（缺失页在 reader/`list_chapter_pages` 仍不可见）；Core 死 seam `tombstone_pages_of_source` **接线或删除**二选一并记录；`needs_confirmation` 零生产者作为具名缺陷登记（→ `FEA-11-DIAG-SURFACE-1`，需 C-17 additive）。 <<MET>>
- [ ] **AC-R3-2（AC11-9 Host 级生产链路）**：gated（`NEWMANGA_FEA11_IPC=1`）经 `Fea09ProductionFixture` launcher + `HostRuntime/Commands.InvokeAsync` 生产 dispatcher 完成 scan→plan→preview→confirm→apply→ACK→resolve；**sync 前**读出旧绑定字节（记录 resource id + sha256），**ACK 后**断言新键/新字节 + 旧资源键/摘要不可变；源 hash/mtime/文件数守恒、应用零写源；缺能力/撤销 fail-closed；默认 skip 且逐条记原因。 <<MET>>
- [ ] **AC-R3-3（AC11-6）**：folder relink **typed 拒绝**判别用例 + folder **resync 成功**用例 + **SC-S11 成员重排保序** + **多项目不误改**；`L-S4-2` 以缺陷登记（`runtime.py:986-991` vs C-15:216 逐项）；**不改 Core 语义**。 <<MET>>
- [ ] **AC-R3-4（L-M4 裁决）**：书面裁决（实现须写 pin 与 UNFREEZE → 明确不做）；re-home `FEA-11-LEGACY-RECOMPUTE-1`（含 reopen 条件：C-17 UNFREEZE + 新 capability）；**不得**出现「已按冻结参数重算旧证据」表述。 <<MET>>
- [ ] **AC-R3-5（回填与翻转）**：AC11-1/3/4/5/8 逐条 before/after 登记（append-only，不改历史 Review/证据字节）；`[x] <<MET>>` 不带原因；L-STARTUP 子项 NA；L-M1/L-M4 具名 re-home；`check.ps1` PASS 且 `done` 无 `<<PARTIAL>>/<<BLOCKED>>`。 <<MET>>
- [ ] **AC-R3-6（证据与治理）**：EV + Resource Manifest 在 R3 head 重生成；pins 18/18 保持（或显式登记变更）；修正 STATUS/PLAN 的 HOST-AUTH-1 陈旧表述；最终 head 取得独立 Review；全量 pytest ≥3390/10、.NET ≥1731/0/98 不降。 <<MET>>

## 实现口径

1. AC11-7 走 **Host journal 只读枚举**（`SourceOperationCoordinator` 加只读 list/lookup，不改 `IHostController`）；`needs_confirmation` 只登记不修（改写入者属 Core 语义 → `FEA-11-DIAG-SURFACE-1`）。
2. AC11-9 复用 `Fea09ProductionFixture` 的 launcher 手法（**仓库无 `Fea11ProductionFixture`**），不碰 bundled sidecar；断言用既有 `RunPythonAsync` 查库，.NET 测试不直连 SQLite。
3. AC11-6 仅补测试 + 登记；**不改** `service.py` 拒绝分支、不改身份模型。
4. L-M4/L-M1 只登记 re-home；不得改契约字节。
5. 提交显式 pathspec，禁 `git add -A`；含中文改动用 edit/Python UTF-8。

## 行文口径（红线）

- 不得写「FEA-11 全部 limitation 关闭 / C-17 §3.3 完全实现 / RH-3 已清理」；只写「AC11-1/3/4/5/8 回填；AC11-6/7/9 达成；L-STARTUP 子项 NA；L-M1/L-M4 re-home」。
- 崩溃点 `NOT_RUN`、原生/真机 `NOT_RUN` 不得写成 PASS。

## 交付记录（`fea11-residual4a-impl`，2026-11-08，append-only）

> 冻结口径以 front matter 与 `doc/reviews/FEA-11-RESIDUAL-4A-scope-r1.md` 为准；本节只登记实现/测试/裁决结果，不改既有冻结文本。

### AC-R3-1（AC11-7 诊断出口）— 已做
- `NewManga.Host/Sources/SourceOperationCoordinator.cs` 新增只读投影 `ListBindingDiagnostics(operationId)`（+ `BindingDiagnostic` record）：按 operationId 读 durable journal 的 `CommitReceipt.bindings[]`，只返回 `status ∈ {missing, needs_confirmation}` 的页（确定性按 `page_id` 排序）；坏 receipt → typed `SOURCE_SYNC_STATE_CONFLICT`；未知 operation → 空（不抛，不全局枚举）。
- **零扩展**：不新增 Core 命令/能力/wire 字段；`IHostController.cs` 零改动（测试反射断言无 `Source`/`Sync`/`Missing` 成员）；C-07 pin 不动。
- Core 死 seam `src/infrastructure/sqlite/source_sync.py` 的 `tombstone_pages_of_source`（原 1030-1047）**删除**（零调用者；接线需新 Core 命令 = 1 pin 且不能扩 V(p,t)）。结论与理由留在删除处注释。
- 测试：`tests/fea11/test_source_sync.py::test_missing_binding_is_diagnosable_without_widening_v_pt`（missing binding 页在 `get_page`/`list_pages` 仍不可见 = 不扩 V(p,t)；page 行/顺序保留）+ `Fea11SourceIpcTests.cs::OperationJournalProjectionReportsOnlyDiagnosticBindings`（非 gated，journal 投影/typed 冲突/无新命令/无 IHostController 面）。
- `needs_confirmation` 零生产者 → **具名缺陷 re-home `FEA-11-DIAG-SURFACE-1`**（需 C-17 additive；本卡不改 Core 语义）。
- limitation：投影是 **operation 作用域**（无全局枚举）。

### AC-R3-2（AC11-9 Host 级生产链路）— 已做（全 dispatcher；D-1 已修复，2026-11-08 DSH 授权扩域）
- 新增 `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11Residual4AIpcTests.cs`（gated `NEWMANGA_FEA11_IPC=1`，默认 skip + 原因）：复用 Fea09 launcher 手法（csc launcher + 仓内 `src` prelude；仓库无 `Fea11ProductionFixture`），`HostRuntime.StartAsync` 起真实 Host + 真实 Python Core；bundled sidecar 未使用/未修改。
- `ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved`：scan→plan→preview→confirm→apply→ACK→resolve **全部经生产 `HostRuntime.Commands.InvokeAsync`**（apply 走 dispatcher 的 journal 分支 + `HostOperationOrchestrator`，Host 自签）。断言：ACK 前 resolve → `SOURCE_ACCESS_DENIED`；ACK 后 → `page-rendition-v2-*` 新键 + `ReadPageImageAsync` 新字节解码 4×3 蓝色（新容器）≠ 旧红色；旧 binding `verified_digest`（旧已发布摘要）不变（superseded）、旧 entry `content_digest` 不变、`page-rendition-p1` 从不出现在 `rendition_cache`；两 zip 的 sha256/size/mtime + zip 集合前后一致；`Registry.Revoke` 后 Host 发 grant → `SOURCE_GRANT_REVOKED`；wire 级断言 scan/apply payload 为**字段平铺**且全 wire 无 `INVALID_JSON`。
- `ProductionDispatcherMissingCapabilityFailsClosed`：生产 dispatcher + Host capability gate（注入探测结果）→ `CORE_CAPABILITY_MISSING` 且 **零 wire 帧**。
- `ProductionDispatcherHostControlPayloadIsFlattened`（D-1 判别测试，gated）：host-control 命令经 dispatcher 的 wire `payload` 为字段平铺、无嵌套、无 `INVALID_JSON`。
- `ProductionDispatcherFailureRecordIsFlattenedAndKeepsGatesPending`（D-1c 判别测试，gated）：`source_record_operation_failure` 经 dispatcher → Host journal `failed`、wire `payload` 键恰为 `[code, operation_id, request_digest]`、Core 响应无错误、页解析仍 `SOURCE_ACCESS_DENIED`（失败不打开 gates）。
- `FailureRecordHostControlPayloadStaysFlat`（D-1c 源码哨兵，**非 gated**，默认门禁即跑）。
- **D-1（本卡新发现，已修复，DSH 三次授权扩域；review r1 P1-1 已闭合）**：**三处独立的 wire 帧合法性缺陷** —— ① D-1a `HostCommandDispatcher.InvokeHostControlAsync` 把完整 payload object 交给已打开 payload 的 `SendHostControlAsync`（现改为 `WriteHostControlPayload`/`WriteFlattened` 平铺，app-channel 不变）；② D-1b `HostRuntime.SourceSyncCapabilityAsync` 与 `RunCapabilityProbeAsync` 的 `core.ping` payload 未闭合（补 `WriteEndObject`，严格两处）；③ D-1c（P1-1）`RecordSourceOperationFailure` 回调向已打开 payload 再写完整 object（客户端 `InvalidOperationException`，失败记录从未发出）→ 改为平铺三字段。修复前**该 dispatcher host-control 路径**从未跑通（不外推其它命令族）。证据与 before/after：`verification/FEA-11-RESIDUAL-4A/DEFECTS.md` D-1、`logs/mutation-d1-m{4,5}.log`、`logs/mutation-d1c.log`、`logs/fea11-ipc-r4a.log`（4/4）。
- **限制**：seeded 旧绑定无 import-time grant mapping（C-16 R1-I002）⇒ sync 前对旧绑定的 Core resolve 为 typed `SOURCE_ACCESS_DENIED`；"旧绑定字节/摘要"以源文件字节 + DB 旧行记录，**未伪称已 resolve 旧绑定**。

### AC-R3-3（AC11-6 folder 用例）— 已做
- `tests/fea11/test_source_relink.py` 新增 4 用例：`test_folder_relink_is_typed_refused`（`SOURCE_SYNC_STATE_CONFLICT` + "folder relink cannot prove the same physical source" + 零 binding 写）、`test_folder_resync_is_a_real_escape_path`（folder 新增成员 → 新 version + 新页 + 旧页顺序不变）、`test_member_reorder_keeps_bound_page_user_order`（SC-S11）、`test_scope_current_resync_leaves_the_other_project_untouched`（多项目只改确认集合）。
- `tests/fea11/conftest.py`：`add_source_tree(..., source_kind="zip")`（folder 场景诚实播种，默认行为不变）。
- **不改** `src/application/sources/service.py` 拒绝分支与身份模型。
- `L-S4-2` 具名缺陷登记：`src/application/importing/referenced/runtime.py:978-991`（folder identity 取首成员 `folder_entries[0][1].volume_serial/_file_id`、`_container_size` 为成员和）vs `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:216`（目录 identity）；另 `scanner.py` 的 authorizations/`_resolve_grants` 同取首成员。详见 `verification/FEA-11-RESIDUAL-4A/DEFECTS.md`。

### AC-R3-4（L-M4 裁决）— 裁决：不实现
- **书面裁决**：L-M4「按冻结参数重算旧证据」不是 0 pin 项 —— `FEA-11-MATCH-1.md:188` 自述需旧字节 + 新 grant；C-17 `:213` 的 `ScanSourceSync` 请求闭集只给目标侧 `grant_ids`、`:238` `SourceBase` 仅 (source_id, version_id, content_digest)；`scanner.py:540-587` 只保留首个 grant、`:324-328/:401-407` 旧条目只从 DB 行读 ⇒ 实现必须改 pinned C-17（18 pins 之一）。
- **本卡不实现**，**不写**「已按冻结参数重算旧证据」；re-home **`FEA-11-LEGACY-RECOMPUTE-1`**（reopen 条件 = C-17 UNFREEZE + 新 capability）；L-M1 → `FEA-11-PDF-RECONCILE-1`。

### AC-R3-5（回填与翻转）— 已做
- `doc/tasks/FEA-11.md`：AC11-1…10 行 → `- [x] … <<MET>>`（MET 不带原因）；`status: closed_with_limitations → done`；文件末尾 append-only `## AC 回填登记（FEA-11-RESIDUAL-4A，2026-11-08）`（逐条 before/after + L-STARTUP 子项 NA + L-M1/L-M4 re-home）。历史 limitation 原文（§Closeout Record L-1…L-11）逐字保留。
- 说明：AC11-10 的 EV/Manifest/独立 Review 属 **DSH closeout**；本卡只交付实现/测试与 AC 行翻转，未伪造 EV。

### AC-R3-6（证据/治理）— 已做
- `verification/FEA-11-RESIDUAL-4A/`：`README.md`（索引）、`DEFECTS.md`（缺陷/re-home/裁决）、`tools/`（`build_plan_body.py`/`inspect_state.py`/`probe_png.py`）、`logs/`（pytest/Host 定向/全量 .NET/gated IPC）、`evidence/`（真实运行输出 + wire 证据）。
- HOST-AUTH-1 陈旧表述：核对 `doc/STATUS.md:8` 与 `doc/REBASELINE_PLAN.md:14/53` 已为 `done`（ADJ §7.7 已修正）→ 本卡无需再次修改，登记于 `DEFECTS.md`。

### 门禁数字（本卡实跑，Windows 本机，2026-11-08；D-1a/b/c 修复后复跑）
- `pytest tests/fea11 -q` → **217 passed / 0 failed**（`logs/pytest-fea11.log`）。
- `pytest tests -q` → **3395 passed / 10 skipped**（基线 3390/10；+5 = 本卡 4 个 folder/SC-S11/多项目用例 + 1 个不扩 V(p,t) 用例；`logs/pytest-full.log`）。
- `dotnet test NewManga.Host.Tests` → **302 passed / 0 failed / 71 skipped**（基线 300/0/67；+2 非 gated（投影测试 + D-1c 哨兵）、+4 gated skipped；`logs/dotnet-host-tests.log`）。
- `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` → **1733 passed / 0 failed / 102 skipped**（基线 1731/0/98；+2 passed、+4 gated skipped；`logs/dotnet-full.log`；跑后 `verification/FEA-09` 已恢复）。
- `NEWMANGA_FEA11_IPC=1` 定向 `Fea11Residual4AIpcTests` → **4 passed / 0 failed**（全 dispatcher：主链/判别/失败路径/缺能力；默认 skip 且带原因；`logs/fea11-ipc-r4a.log`）。
- 变异自检（6 项，逐字节复原 + sha256 前后一致 + 复绿）：`logs/mutation-m{1,2,3}.log`（AC 层：删 folder 拒绝分支 → AC-R3-3 RED；ACK 前放行 gate → AC-R3-2 RED；投影改返回全部页 → AC-R3-1 RED）+ `logs/mutation-d1-m{4,5}.log`（D-1 层：还原 dispatcher 嵌套 → 判别测试 RED；还原 capability ping 未闭合 → gated 用例 RED）+ `logs/mutation-d1c.log`（D-1c：还原失败帧嵌套 → gated 失败路径 + 非 gated 哨兵双 RED）。
- `check.ps1` PASS（3 warnings）；`verify_pins.ps1` **18/18 PASS**（C-07/API inventory pin 未动）。

### 待 DSH 处置（本卡不越界）
1. （已关闭）D-1a/D-1b（`5c2ac5eeb`）与 D-1c（review r1 P1-1，本提交）：授权扩域修复完成，before 证据保留在 `verification/FEA-11-RESIDUAL-4A/evidence/dispatcher-defect-wire.txt`（已订正归因）、after 证据在 `evidence/after-full-chain.txt` / `after-failure-record.txt` / `d-1-fixed-wire.txt`。
2. `FEA-11-DIAG-SURFACE-1`（`needs_confirmation` 零生产者 / 管理诊断全局面，需 C-17 additive）。
3. `FEA-11-LEGACY-RECOMPUTE-1`（C-17 UNFREEZE + 新 capability）、`FEA-11-PDF-RECONCILE-1`（L-M1）。
4. `L-S4-2` folder identity 缺陷（本卡只登记，未修）。
5. FEA-11 卡的 EV/Manifest/独立 Review 与 `check.ps1` 终验。
