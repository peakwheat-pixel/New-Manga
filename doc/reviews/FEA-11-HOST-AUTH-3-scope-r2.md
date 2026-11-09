# FEA-11-HOST-AUTH-3 scope review r2（独立上下文只读子代理）

| 项 | 值 |
|---|---|
| 审查者 | 独立上下文 fresh subagent（父会话 `session-c08ea2ac-cbcf-47ac-a7a9-0e15254b3fa5`；本会话 id 未在运行提示中暴露；**未参与** FEA-11-HOST-AUTH-1/2/3 的实现、返修、卡面起草、C-17 v1.2 载体/复核） |
| reviewer_kind | `subagent`（由 DSH 派发；只读被审 head；仅写本文件） |
| 模式 | 只读：read/grep/glob + 只读 git + `check.ps1`/`verify_pins.ps1`；未改生产源码、未改契约字节、未跑 gated IPC、未 commit/push |
| 被审 head | `e9ab2ef7c`（`main`；本轮 `git status --porcelain` 为空，本文件写入前） |
| 审查输入 | 卡 `doc/tasks/FEA-11-HOST-AUTH-3.md`；r1 `doc/reviews/FEA-11-HOST-AUTH-3-scope-r1.md`；ZCode 裁决 `doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`；C-17 v1.2 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md` + 冻结记录 `doc/plan/FEA-CONTRACT-FROZEN-C17.md` + 载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-09-C17.md`；相关 Core/Host 源码 |
| **verdict** | **`READY-TO-FREEZE`** —— 载体（C-17 单 pin additive，路线 B + D-4 合批）已按裁决完成 v1.2 重冻且 `verify_pins` **18/18**；实现范围可按 §2 的 **19 条 allowed_paths** 冻结；AC 为 §3 的 **6 条**。**冻结提交必须同时落盘 §6 的 R-r2-01（卡面 3 处字符丢失 + 错误码纠正）**，否则 AC 会建立在与裁决相反的卡面文字上 |
| 结论强度 | 只批准「范围 + AC + 证据计划」；不批准任何实现；本报告不构成 UNFREEZE（C-17 v1.2 已冻结），也不改 `FEA-11-HOST-AUTH-2` 的 `AC-F3 = NOT_APPLICABLE` |

## 0. 一句话结论

r1 的三处判断（错误码 `SOURCE_ACCESS_DENIED`、最省载体 = 只读计划物化投影、D-3 拆出）均被 ZCode 裁决采纳并落成 C-17 v1.2；**载体侧已无阻塞**。实现侧的真正难点不在契约，而在 Host 恢复路径的两个「不能猜」：①重铸 grant 所需的 **source 路径**与 **source_kind** 必须来自既有冻结面（`SourceAccessRegistry.Roots` 与 v1.1 的 `source_list_scan_targets`），不得新增 C-17 v1.3 字段；②`PrepareCompletion` 的 **Core-free seam** 是默认门禁的既有测试约束，物化读取只能放在 `Acknowledge/Recover` 的 Core-backed 段。这两点不写进 AC 就会被实现者用「猜 locator/猜 kind/顺手改契约」绕过。

## 1. 载体与前置事实复核（本轮实测）

| 断言 | 证据 | 判定 |
|---|---|---|
| C-17 v1.2 已冻 | 冻结记录 `FEA-CONTRACT-FROZEN-C17.md:11-17`（v1.2 / 2026-11-09；工作树 `cdeee487…` / blob `2cccc3c6…` / blob SHA-256 `e809cfb3…`）；§附录 `:70-76` | **成立** |
| pin 全绿且只重算 C17 | `tools/governance/verify_pins.ps1` 本轮：`PIN AUDIT: PASS (all 18)`，`C17 cdeee4872e29`，其余 17 项哈希与 r1 记录一致（C16 `67286eec`、C06 `75f8e2b4`、C15 `f9e376a0`） | **成立** |
| 新命令/ DTO / 错误码 / capability 已在契约出现 | `FEA-C17_SOURCE_SYNC_DRAFT.md:231`（`GetSourceSyncPlanMaterialized / source_get_sync_plan_materialized`，请求 `plan_id! ID; plan_digest! H`，closed shape，host-control，零写，§8 闭集）；`:266`（`SourceSyncPlanMaterialization` 12 字段）；`:285`（v1.2 只读守卫）；`:194-196`（capability `source.sync.plan-materialization/1` 只进 `core.ping.capabilities`，`Capabilities` DTO 仍 7 项，不登记 HostCommandRegistry/C-07）；`:371-372`（`SOURCE_PLAN_NOT_FOUND` not_found/false；`SOURCE_PLAN_UNAVAILABLE` internal/true） | **成立** |
| 独立 byte-level 复核 APPROVE | `C17-v1.2-byte-review-r2.md`（r1 CHANGES_REQUESTED P0=0/P1=1/P2=4/P3=6 已处置；r2 P0/P1/P2 未闭合=0） | **成立** |
| 实现侧尚未动工 | `src/`、`apps/desktop-avalonia/src/` `grep source_get_sync_plan|SourcePlanMaterializ|source.sync.plan-materialization` → **0 命中**；`src/application/sources/errors.py` 无两个新码；`core_service.py` 无新命令 | **成立** |
| 治理门禁 | `check.ps1` 默认 + `-TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` 均 **PASS**（3 warnings：12 个非终态 Task / `STATUS.md` 80% / `REBASELINE_PLAN.md` 80%），EXIT=0 | **成立** |

**沿用 r1 的事实（本轮抽检仍成立，不重做全量）**：grant registry 仅进程内存（`source_read_refs.py:106-121`、`:3-4`）；register 窗口 ≤300s（`:178-180`）；整树 kill 后未注册 grant 的码是 **`SOURCE_ACCESS_DENIED`**（`:855-861`），`_verify_fresh` 原样转出（`runtime.py:224-228`）；`PrepareCompletion` 复用 journal `GrantIds`（`SourceOperationCoordinator.cs:298-300`）；journal 无 source/version/entries（`:67-84`）。

**本轮新增的关键事实（决定 AC 写法）**

1. `_verify_fresh` 只核对 **grant 的物理 identity**（`container_facts` 或 `folder_entries[0][1]` → `identity_digest_of(sha256,volume,file_id,size)`）与 `authorization` 基线，**不核对 entries 的 locator/ordinal/内容摘要**（`runtime.py:229-260`）。⇒ 恢复重铸的 grant 只要能对同一物理源重新生成可被 `RegisterSourceReadGrant` 接受的 payload，就能通过 ACK；entries 不必与 plan 逐条相同（但必须真实、不得伪造）。
2. 重铸输入在当前冻结面内**可凑齐**：`registry_id`/`generation`/`identity_digest` 在 journal `authorization_json`；**source 路径** = `SourceAccessRegistry` 条目 `Roots`（生产两条登记面都只传一个 root：`SourceImportModels.cs:243-251`、`SourceRecoveryModels.cs:213-226`（后者明写「entry 的 OWN persisted `roots[0]`」，是「只取 roots[0]、不猜路径」的直接先例）；`SourceAccessRegistry.cs:34-52`）；**source_kind** = v1.1 已冻结的 `source_list_scan_targets` 的 `ScanTarget.source_kind`（`FEA-C17…:264`），`version_id` + `entries` = 新命令物化投影；`IssueAsync` 已具备 `containerEntries` 入参与 folder 枚举（`SourceReadCoordinator.cs:471-537`）。**无需 C-17 v1.3 字段**。
3. `source_sync_plans` 行的 `body_json` 只存计划子集，`state`/`expires_at` 是表列，`get_plan` 一次 SELECT 已全含（`source_sync.py:222-230`）⇒ Core 侧无需改 store/port，只需新增薄投影模块。
4. 生产入口 `RegisterRoot` 单 root；但 registry 格式允许多 root（`Register(locator, roots)`）。恢复路径必须要求「恰好 1 个 readable root」，否则 typed fail-closed —— 否则就是猜源。

## 2. 实现范围冻结（allowed_paths，19 条）

> 口径：`diff ⊆ allowed_paths`；契约字节（C-17 v1.2 = `cdeee487…`）、其余 17 份契约、`doc/contracts/FEA-C07_API_INVENTORY.md`、`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`、`src/infrastructure/resource_channel/source_read_refs.py`、`src/application/sources/runtime.py` **均为零改动**；需要改它们即说明设计越界，**停并回 DSH**。

### 2.1 Core（5 条）

| # | 文件 | 精确改动 | 依据 |
|---|---|---|---|
| 1 | `src/bootstrap/core_service.py` | ①`_HOST_CONTROL_COMMANDS` 增 `"GetSourceSyncPlanMaterialized"`；②`_dispatch_host_control` 的 source-sync 元组/分支接入（typed 失败走 `SourceSyncError` 信封，保留 §8 闭集）；③`handle_ping` 的 `source_sync` 分支增 `"source.sync.plan-materialization/1"`（只进 ping）；④`_dispatch_source_sync` 增分支调用新模块 | `:355-371`、`:1544-1574`、`:1669-1677`、`:5373-5384`；契约 `:194-196`、`:231` |
| 2 | `src/application/sources/materialization.py`（**新增**） | 单函数 `materialize(store, payload)`：closed shape（`set(payload) == {"plan_id","plan_digest"}`，未知/缺键 → `INVALID_REQUEST`）；`get_plan`；不存在 → `SOURCE_PLAN_NOT_FOUND`；`plan_digest` 不匹配 → `SOURCE_PLAN_STALE`；`body_json` 解析失败/缺 kind/source_id/entries/reference_set_digest → `SOURCE_PLAN_UNAVAILABLE`；`entries` 按 ordinal 升序 + ordinal 唯一；`target.status=missing` → `version_id`/`content_digest` 为 null 且 `entries=[]`；响应恰好 12 字段（`format/plan_id/plan_digest/kind/source_id/version_id/content_digest/entries/reference_set_digest/state/expires_at`）；**不判 plan TTL 过期**（契约 `:274`：恢复已提交 receipt/ACK 不受 plan TTL 影响）；**零写** | 契约 `:231`、`:266`、`:274`、`:285`；`source_sync.py:222-230` |
| 3 | `src/application/sources/errors.py` | `SOURCE_SYNC_ERROR_RULES` 增两条：`SOURCE_PLAN_NOT_FOUND: ("not_found", False)`、`SOURCE_PLAN_UNAVAILABLE: ("internal", True)` | 契约 `:371-372`；现表 `:18-47` |
| 4 | `tests/fea11/test_source_plan_materialization.py`（**新增**） | 形状/类型/未知键负例；not_found / stale / unavailable / budget；ordinal 排序唯一；missing 目标 null；**过期 plan 仍返回**（state/expires_at 直读表列）；零写（前后逐表相等，口径沿契约 §6.2）；不返回绝对路径/secret | AC-H3-2 |
| 5 | `tests/fea11/test_source_command_parity.py` | 新命令断言：在 `_HOST_CONTROL_COMMANDS`、不在 `_SOURCE_SYNC_APP_COMMANDS`；Host 侧新增常量存在。（现有 `len(host)==14` 是 HostCommandRegistry 口径，新命令**不**进该表，保持 14） | 现文件 `:31-70`；契约 `:196` |

**明确不改**：`src/infrastructure/sqlite/source_sync.py`、`src/application/sources/ports.py`（`get_plan` 已够）、`src/application/sources/runtime.py`（R-03 属独立缺陷卡）、`src/infrastructure/resource_channel/source_read_refs.py`（C-16 grant 形状/校验不变）。

### 2.2 Host（7 条，其中 1 条条件项）

| # | 文件 | 精确改动 | 依据 |
|---|---|---|---|
| 6 | `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs` | 新常量 `SourceGetSyncPlanMaterializedCommand = "source_get_sync_plan_materialized"`、`SourcePlanMaterializationCapability = "source.sync.plan-materialization/1"`；新方法 `GetSourceSyncPlanMaterializedAsync(planId, planDigest, ct)`：先 `RequireCapabilitiesAsync`，再 `SendHostControlAsync`（不得用 app 面 `SendAsync`） | 先例 `:1544-1573`；契约 `:196`、`:231` |
| 7 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs` | ①`AcknowledgeAsync`/`RecoverAsync` 在 `PrepareCompletion` **之前**取物化（Core-backed）；②新增内部 `Material` 结构（source_id/version_id/kind/entries/state）；③重铸：按 baseline 逐 registry 用 `SourceReadCoordinator` mint ≤300s fresh grant，**替换** `:298-300` 的 journal `GrantIds`；④Host 侧前置拒绝：`material.state != "applied"` / `material.source_id` 与 journal 不符 / `baselines.Count != 1` / 若干 registry 无法**唯一**解析 root → typed 拒绝、**零 completion 帧**、journal 授权字节不变；⑤`PrepareCompletion` 保持 **Core-free**（物化由调用方注入），默认门禁不退化 | 现约束 `:185-187`、`:298-300`、`:316-317`、`:421-422`；契约 `:285` |
| 8 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs` | 仅加窄 mint seam：公开 `IssueForRecoveryAsync(registryId, generation, path, sourceKind, sourceId, version, containerEntries, ct)`，内部复用 `IssueLockedAsync` + `RenditionFor`；**不改** `_checked`/`RegisterSourceReadGrant`/budget/TTL 语义，不新增 grant 形状 | `:471-537`、`:821`；契约 `:285`（校验路径不变） |
| 9 | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | `SourceOperationCoordinator` 注入 `Sources`（构造顺序已是 Sources 先于 Operations，`:1236-1243`）；不改命令面/派发 | `:1236-1243` |
| 10 | `apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs` | **条件项**：仅当新码需要经 Host journal/`record_failure` 校验时把两个新码加入 `IsKnown`（及 `RetryableCodes` 仅指 `SOURCE_PLAN_UNAVAILABLE`）。**不得**为它们新造投影 | 现闭集 `:22-31` |
| 11 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs` | 默认门禁单测：物化注入 + 重铸拒绝矩阵（≥6：state!=applied、source 不符、多 baseline、root 非唯一、identity 漂移、material 不可得），断言零 completion 帧、journal 不变；`PrepareCompletion` 仍可 Core-free 调用 | AC-H3-3 |
| 12 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs` | gated 真 IPC：新增 `CrashPoint_Park` / `CrashPoint_Recover`（复用本文件私有 `IpcFixture`，不新建 Support 文件）；恢复失败反例（替换源文件 → typed、gates pending） | AC-H3-4/5 |

**明确不改**：`HostCommandRegistry.cs` / `HostCommandDispatcher.cs`（契约 `:196`：不登记/C-07 零增量）；`HostController.cs`（无 UI 面）；`SourceScanScheduler.cs`（恢复不依赖内存 identity cache）。

### 2.3 证据与治理（7 条）

| # | 路径 | 说明 |
|---|---|---|
| 13 | `verification/FEA-11-HOST-AUTH-3/**` | 自有崩溃驱动 `tools/crash-ack.ps1`（从 HOST-AUTH-2 骨架**复制**后改，禁止原地改）、wirelog、DB 前后导出、日志。`verification/FEA-11-HOST-AUTH-2/**` 保持原字节 |
| 14 | `doc/tasks/FEA-11-HOST-AUTH-3.md` | 冻结：status/allowed_paths/AC/卡面 errata（R-r2-01、R-r2-06） |
| 15 | `doc/handoffs/FEA-11-HOST-AUTH-3-*.md` | 实施交接 |
| 16 | `doc/reviews/FEA-11-HOST-AUTH-3-*.md` | 实施后独立 Review（本 r2 保持原字节） |
| 17 | `doc/STATUS.md` | DSH 生命周期（Owner 不得改） |
| 18 | `doc/REBASELINE_PLAN.md` | DSH 生命周期 |
| 19 | `doc/TASK_LEDGER.md` | DSH 生命周期 |

**不列入（越界即停）**：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`、`doc/reviews/CONTRACT-UNFREEZE-2026-11-09-C17.md`（v1.2 已冻，需改 = 新 UNFREEZE）、`doc/plan/FEA-C16_*`、`FEA-C15_*`、`FEA-C06_*`、`FEA-C07_API_INVENTORY.md`、`FEA-CONTRACT_FREEZE_MATRIX.md`、C-17 §6 CAS/§7 lineage、`SourceReadCoordinator` 的 grant 校验语义、`tests/fea11/test_source_operation.py`（既有 ACK 语义测试只应因新码/新 seam 被动通过，不得改断言放宽）。

## 3. AC（6 条，可观察、可判别）

> 所有 AC 必须给出「实测 / NOT_RUN」二值，不得把 gated 未跑写成 PASS。

### AC-H3-1（载体与字节，已由前置满足，实施期只验证「不回退」）
- `verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`，其中 C17 = `cdeee4872e29…`；**其余 17 项哈希零变化**。
- `git diff --name-only` 不含 §2 末尾的「不列入」清单；C-17 工作树 SHA-256 仍为 `cdeee4872e29b56c7d67de65dabd6ca9b31006eecde61d99b83e29fe5a4fc96c`。
- 若任何一步需要重算 pin ⇒ 本卡停止，回 DSH；**不得**自行 UNFREEZE。

### AC-H3-2（Core 新命令：只读 / closed shape / host-control / typed 错误 / capability）
同一 fixture 前后逐表相等（沿契约 §6.2 零写口径），且无新 plan/scan/operation/receipt/grant/journal 行：
- **能力**：`core.ping.capabilities` 含 `source.sync.plan-materialization/1` **仅当** `_core.source_sync` 装配；`GetSourceSyncCapabilities` 的 `Capabilities` DTO 仍**恰好 7 项**（无第 8 项）。
- **通道**：普通 application 面（`channel` 缺省）调用 → `HOST_ONLY_REQUIRED`（`core_service.py:6526-6530` 路径），且**零写**；`host-control` + 新 host session 下成功。
- **形状**：`{}` / 多键 / 缺键 / `plan_id` 非 string / `plan_digest` 非 64hex → `INVALID_REQUEST`（逐例）。
- **typed 矩阵**：不存在 → `SOURCE_PLAN_NOT_FOUND`（category `not_found`、retryable false）；`plan_digest` 与 live 行不符 → `SOURCE_PLAN_STALE`；`body_json` 缺 `kind/source_id/entries/reference_set_digest` 或非 JSON → `SOURCE_PLAN_UNAVAILABLE`（`internal`、retryable true）；entries >10000 或响应 >8MiB → `SOURCE_BUDGET_EXCEEDED`（不截断）。
- **语义**：`entries` 按 `ordinal` 升序且唯一；`target.status=missing` → `version_id`/`content_digest` = null、`entries=[]`（不得伪造）；**`expires_at` 已过期但 `state=applied` 的 plan 仍返回**（`SOURCE_PLAN_STALE` 不得被用作 TTL 拒绝；契约 `:274`）；
- **脱敏**：响应体与 wirelog **0 命中**绝对路径 / `signing_key` / `signature` / `secret_ref`（沿 C-16 §7 与契约 `:270`）。
- 判别性：把投影实现改成「顺手 `mark_*`」或「写一条 receipt」→ 零写断言必须失败。

### AC-H3-3（Host 重铸 fresh grant，不再复用 journal grant）
- completion 路径**不再**使用 journal `GrantIds`（代码断言 + 运行时：`material.GrantIds` 与 journal `GrantIds` **无交集**）。
- 对每个 baseline registry：`SourceAccessRegistry.Authorize(registryId, liveGeneration, root)` 后 mint，`expires_at ≤ now+300`；authorization 的 `generation` = live（≥ 基线）、`identity_digest` = 基线（不得用 live 重算值替换基线，除非相等）。
- **拒绝矩阵（≥6，全部 typed、零 completion 帧、journal 授权字节与状态不变、gates 仍 pending）**：`material.state != "applied"`；`material.source_id` ≠ journal/plan；baselines.Count ≠ 1；registry 撤销；root 不可读/identity 变；registry root 数 ≠ 1（**不得猜源**）。拒绝码只用 §8 闭集（`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_REVOKED`/`SOURCE_REGISTRY_UNAVAILABLE`/`SOURCE_PLAN_STALE`）。
- 判别性：把拒绝改成「回退 journal GrantIds」→ 必须出现 typed 失败（见 AC-H3-5），不得静默通过。

### AC-H3-4（核心：真实 kill 后新进程恢复**一次**，含三重防伪）
外部驱动两阶段（§4）：
1. phase `park`：真实链跑到 journal `core-committed`，写 `park.json`（`journal_state/operation_id/commit_digest/old_grant_ids/old_core_session_id/old_host_pid/old_python_pids/db_counts/source_sha256`）。
2. 外部 `Process.Kill(entireProcessTree:true)`；**断言 dotnet 子进程与全部 Python Core PID 均消失**（枚举 `Win32_Process` 后代，轮询 30s）；未证实 → `CRASH_POINT=FAIL reason=sidecar_not_proven_dead`，记 **NOT_RUN**，不得进入 phase 2 冒充 PASS。
3. phase `recover`：**新 dotnet 进程**（PID 不同）+ 新 Core（`core_session_id` 不同）+ 新 host session，执行 recovery/ACK **成功一次**，写 `recover.json`。

断言（全部满足才算 PASS）：
- `acknowledged`（或 `recovered`，仅一次；二次调用 **0 新帧**、返回原 receipt/原 state）；
- 该 operation 在 `source_binding_publications` 的 `read_gate` **0 pending**；
- `page_bindings` / `source_binding_publications` / `pages` **行数不变**；
- `commit_digest` 与 phase1 一致；`page_bindings` 相关字段与 phase1 导出逐字节一致（除 `updated_at` 类既有时间列按口径豁免并书面列明）；
- 源文件 sha256 不变；
- **三重防伪**：①`recover.json.host_pid != park.json.host_pid`；②`recover.json.core_session_id != park.json.core_session_id`（且 `host_session_id` 不同）；③`recover.json.used_grant_ids ∩ park.json.old_grant_ids = ∅`，且 **`used_grant_ids` 不出现在任何 journal 文件字节中**（`grep` 断言）。
- 反例（同 harness）：phase1→phase2 之间替换源文件 → typed 拒绝（`SOURCE_ACCESS_DENIED`/`FILE_IDENTITY_CHANGED`）、零写、gates pending、`crash` 退出码非 0。

### AC-H3-5（变异判别，必须有，不允许「恒真」）
在**同一 harness** 上逐个注入、每次必须让预期断言失败（变异体 PASS = AC 失败）：
| 变异 | 期望 |
|---|---|
| M1：重铸改为复用 journal `GrantIds` | phase2 typed `SOURCE_ACCESS_DENIED`（"not registered"），gates pending，行数不变 |
| M2：新命令从 `_HOST_CONTROL_COMMANDS` 移除（落回 app 面）且不另加守卫 | app 面调用得 `HOST_ONLY_REQUIRED`，且 host-control 下 `INVALID_REQUEST`（不得可用） |
| M3：投影实现写库（`mark_*`/插入 receipt） | 零写断言（逐表相等）失败 |
| M4：`plan_digest` 校验删除 | 用错 digest 调用的负例**必须**非 `SOURCE_PLAN_STALE` 被判失败（即测试能抓到） |
| M5：把 `state != applied` 拒绝删除 | AC-H3-3 拒绝矩阵对应例失败 |
| M6：把 source 路径/kind 改为从文件名或 `PlanBody` 猜 | 明确负例：路径不在授权 root / kind 与 `ScanTarget.source_kind` 不符 → typed 拒绝；猜的实现必须被该负例抓住 |
变异证据（每个变异的 diff + 失败输出）入 `verification/FEA-11-HOST-AUTH-3/mutations/`。

### AC-H3-6（门禁、范围与不夸大）
- `check.ps1`（默认 + `-TaskPath`）**PASS**；`verify_pins` **18/18**；`python tools/generate_api_inventory.py --check` EXIT 0（C-07 零增量）。
- `git diff --name-only <base>..<head>` **⊆ allowed_paths**；无 commit/push 越权；工作树 clean。
- 全量 `pytest`：不低于当轮基线（r1 记录 3390 passed / 10 既有失败；实际数值以实施当轮基线为准并写明命令与时间）；全量 .NET `failed=0`，passed 只增；新增 gated 用例默认 **skip 且逐条写原因**。
- 证据：`verification/FEA-11-HOST-AUTH-3/` 含 `crash-ack.ps1`、`park.json`、`recover.json`、kill 证据（PID 列表前后）、DB 前后导出、wirelog（脱敏后）、两次 ACK 帧计数、源文件 sha256、变异目录、`README.md` 状态表（每项 `PASS`/`FAIL`/`NOT_RUN`）。
- **禁止措辞**（出现即 AC 失败）：任意崩溃点均可恢复 / grant 已持久化 / 自动重新授权 / limitation 3 或 4 已闭合 / 无副作用。FEA-11-HOST-AUTH-2 的 `AC-F3` 仍为 `NOT_APPLICABLE`。

## 4. 证据计划（gated IPC / 真实进程 / 崩溃注入）

### 4.1 三层

| 层 | 入口 | 内容 | 证据落点 |
|---|---|---|---|
| 默认门禁（无 Core） | `dotnet test ... --filter FullyQualifiedName~Fea11HostAuth` | 物化注入 + 重铸 + ≥6 拒绝矩阵 + `PrepareCompletion` Core-free 不退化；`tests/fea11` 新投影单测（含过期 plan、missing 目标、ordinal 唯一、零写） | 测试输出；不写仓库 |
| gated 真 IPC（`NEWMANGA_FEA11_IPC=1`） | `dotnet test ... --filter FullyQualifiedName~Fea11HostAuthIpcTests` | apply→`core-committed`→ACK 前 resolve 得 `SOURCE_ACCESS_DENIED`→ACK 后开门；二次 ACK 0 帧；新命令在 app 面 `HOST_ONLY_REQUIRED`；错 digest → `SOURCE_PLAN_STALE` | 隔离 root（`G:\CODEX\New Manga.workspace\FEA-11\...`），**禁止**写 `verification/FEA-09/**` |
| 崩溃注入（本卡唯一不可替代） | `pwsh -NoProfile -File verification/FEA-11-HOST-AUTH-3/tools/crash-ack.ps1` | `park → kill(entireProcessTree) → 证明 sidecar 死 → recover(新进程)`；断言 §3 AC-H3-4 全部项 | `verification/FEA-11-HOST-AUTH-3/crash/<run-id>/`（`park.json`/`recover.json`/`kill.json`/`db_before`/`db_after`/`frames.txt`/`sha256.txt`） |

### 4.2 崩溃驱动细节（`crash-ack.ps1` 必写项）

- `$ErrorActionPreference='Stop'`；**env gate**：`NEWMANGA_FEA11_IPC=1` 否则 `CRASH_POINT=NOT_RUN reason=env_gate` + exit 2（沿用 HOST-AUTH-2 骨架 `:43-46`，但文件复制到本卡目录后再改）。
- 退出码：`0`=PASS（全部断言）；`10`=park 未到 `core-committed`；`11`=kill 未被证明（含 sidecar 未死）；`12`=recover 被 typed 拒绝或断言不足；`13`=幂等/行数/digest 漂移；`2`=NOT_RUN/环境缺失。**任何 `11/12/13` 不得输出 `CRASH_POINT=PASS`**。
- kill 证明：用 `Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -in $tree }` 递归取 dotnet 后代 → 记录 `python.exe`（或 `core_service.exe`）PID 集 → kill → 轮询 30s 断言全部 `Get-Process -Id` 抛错；`kill.json` 记录前后 PID 集与时间。
- recover 新进程：`Start-Process dotnet` 的 **PID 与 park 不同**；新 Core 的会话 id 从 wirelog/`recover.json` 读取；恢复前先断言**旧 grant id 的 resolve 为 `SOURCE_ACCESS_DENIED`**（新 Core 无 registry 的硬证据），再由新命令重铸。
- 幂等：recover 后再执行一次 ACK/recovery → wirelog 帧数**不增**（Host 早退 `acknowledged/recovered` 或 Core 幂等返回原 receipt，二者都算，须在日志里区分哪一层短路）。
- 脱敏：脚本对 wirelog 只做 `grep` 断言（路径/signing_key/secret_ref 0 命中），**不复制**敏感原文进证据。

### 4.3 NOT_RUN 纪律

- 每个 AC 行在 `verification/.../README.md` 状态表落 `PASS`/`FAIL`/`NOT_RUN` 与命令、时间、head、退出码。
- 未设 `NEWMANGA_FEA11_IPC=1`、无 Python sidecar、Kill 未证实、Core 未起、目录缺失 → 一律 `NOT_RUN`（exit 2/11），**不得**以「骨架存在」「park 文件存在」「代码级推断」代替。
- 本 scope review **不跑** gated IPC（UNKNOWN-2），r2 的任何「可恢复」表述都只是代码级推断。

## 5. 风险、回退与 FEA-13 边界

| 风险 | 处置 |
|---|---|
| 把「恢复」做成「自动重新授权」（红线） | 只对 journal `core-committed` 且 plan `applied` 的 operation 重铸；registry 撤消失败即拒；**不**为新源/新内容签 grant；authorization 仍走 `HostAuthorizationMinter` + `VerifyOperationReceipt`（既有守卫不改） |
| 新读回面成为越权读取面 | host-control + closed shape + 零写 + 只回传 Host 已提交过的同一 plan 子集；wirelog 脱敏 0 命中；读回值不构成授权（契约 `:285`） |
| 用「猜路径/猜 kind」凑齐重铸输入 | 路径只取 `SourceAccessRegistry` 唯一 readable root；kind 只取 `ScanTarget.source_kind`；任一不唯一/缺失 → typed 拒绝（AC-H3-3/5 M6） |
| TTL 被变相延长 | 每次重铸新 grant、各自 ≤300s；禁止写 journal/DB；`grep` 断言新 grant id 不入 journal |
| Windows 上 `Kill(entireProcessTree)` 未覆盖 Python sidecar | AC-H3-4 显式 PID 断言；未证实记 NOT_RUN（沿用 r1 UNKNOWN-1） |
| 多 baseline / 多 root 的边界被忽略 | AC-H3-3 强制 `baselines==1` 且 root 唯一；否则 fail-closed |
| 实现期发现必须改 C-17 字段（例如需要 DTO 增 `source_kind`） | **停**：不得以「小 additive」自行扩；回 DSH 走新的 C-17 v1.3 UNFREEZE（本卡不再吸收） |

**回退**：无 schema/migration、无数据迁移。回退 = 恢复 C-17 v1.2 已有字节不变（pin 不动）+ 移除 Host 重铸路径（`Acknowledge/Recover` 回到复用 journal `GrantIds` 的旧行为）+ 保留 fail-closed 崩溃证据（新进程 ACK → `SOURCE_ACCESS_DENIED` / gates pending）。成本低，无需数据修复。

**与 FEA-13 的边界（不得越权）**：
- FEA-13 拥有 **备份/恢复、数据根迁移、跨机恢复**（ADR：数据根指针 Host 独占、两阶段切换）。本卡**不**改 `backup.*`、`restore`、`DataRoot`、`host/source-access/registry.v1.dat` 格式、DPAPI 封装、`FEA-13-SRC-6`（包内源引用/授权元数据）。
- 本卡只做「同机、同 DataRoot、Host+Core 同死后的进程内 grant 重铸」；**不**声称跨机恢复、**不**声称备份包含授权元数据、**不**声称 reinstall 后可恢复授权（ZCode 裁决 §2 的 DPAPI CurrentUser 限制仍成立）。
- 若崩溃注入触及备份窗口（备份进行中 kill），记 `NOT_RUN` 并移交 FEA-13，不在本卡扩 AC。

## 6. Findings（r2 新增/更新）

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 |
|---|---|---|---|---|---|
| R-r2-01 | **P1** | `doc/tasks/FEA-11-HOST-AUTH-3.md:39`、`:57`、`:60`、`:61` | ①`:39` 仍写 `SOURCE_GRANT_EXPIRED`，与裁决 R-01 要求（`SOURCE_ACCESS_DENIED`）**相反**，直接违反「须落进卡面与 AC」；②`:57` `version_id/entries` → `ersion_id/ntries`、`:60` `verify_pins` → `erify_pins`、`:61` `approval` → `pproval`（字符丢失，U+FFFD=0，属真实丢字符，非显示问题）。AC 若照抄卡面会不可满足 | `git show HEAD:doc/tasks/FEA-11-HOST-AUTH-3.md` 同字节；`Select-String` 复现 | 冻结提交内修正 4 行；AC 以 `SOURCE_ACCESS_DENIED` 为期望码，并另测「已注册但过期」→ `SOURCE_GRANT_EXPIRED` 保留两码可判别 |
| R-r2-02 | **P1** | r1 `§4.2 AC-H3-2`（`FEA-11-HOST-AUTH-3-scope-r1.md:127`）vs 契约 `FEA-C17…:266`、`:285` | r1 写「只对 `applied`/`core-committed` 的 operation 返回」，但 v1.2 DTO `state` 是 5 值闭集且守卫只要求 `plan_id/plan_digest` 与 live plan 一致 ⇒ 若 Core 过滤 `applied`，**超出冻结语义**；若不过滤，r1 AC 判失败。属 AC 与冻结字节冲突 | 契约两处原文 | r2 定稿：**Core 不过滤 state**（照 §5.3 返回）；`state == "applied"` 是 **Host** 恢复前置（AC-H3-3），不是 Core 的拒绝条件 |
| R-r2-03 | **P2** | 契约 `:266`（DTO 无 `source_kind`/`path`）；`SourceAccessRegistry.cs:34-52`、`SourceImportModels.cs:243-251`、`SourceRecoveryModels.cs:213-226` | 重铸输入的两个缺口没有在卡面/AC 里落规则，实现者极易「猜文件名=locator」或「把 registry root 当父目录」；一旦猜错，identity 校验会拒绝（好事），但错误会表现为随机失败而非可诊断规则 | 源码 + 契约 | 冻结时写入：path = 唯一 readable `Roots[0]`（沿 `SourceRecoveryModels.cs:213-226` 先例）；kind = `source_list_scan_targets.source_kind`；`baselines != 1` / root 不唯一 → typed 拒绝；**禁止**为补字段改契约 |
| R-r2-04 | **P2** | `SourceOperationCoordinator.cs:185-187`（Core-free 注释）、`Fea11HostAuthTests.cs:494`（默认门禁依赖） | 物化读取是 async Core 调用，若塞进 `PrepareCompletion` 会破坏既有默认门禁与 Core-free 约束，导致「为跑测试而改生产签名」的连锁改动 | 源码 + 测试类 | 冻结时写死 seam：`PrepareCompletion` 保持同步 Core-free，接收已取得的 material；Core 调用放 `Acknowledge/Recover` |
| R-r2-05 | **P3** | `FEA-CONTRACT-FROZEN-C17.md:3`（仍写 `FROZEN v1.1`）vs `:11`（v1.2）与 `:70-76`；`CONTRACT-UNFREEZE-2026-11-09-C17.md:55`（`§6 复冻记录（待回填）`）与 `:71`（「不构成 UNFREEZE 完成」） | 冻结记录/载体内部状态行自相矛盾；pins 已证明 v1.2 生效，故属**记录文字**问题，不影响实现 | 三处原文 | DSH 在 lifecycle 提交里统一状态行；**不得**由实现者改（改了三指纹即变） |
| R-r2-06 | **P3** | `doc/tasks/FEA-11-HOST-AUTH-3.md:7`（`approval` 仍写「未过 UNFREEZE 流程前不得实施」）vs `:73`（已满足） | 卡面 `approval` 与正文末尾结论不一致，易被误读为仍 blocked | 两处原文 | 冻结时把 `approval` 改为「UNFREEZE 已完成（C-17 v1.2），scope 冻结中/已冻结」 |
| R-r2-07 | **P3** | `HostErrorCodes.cs:22-31` | 新码是否进 Host 闭集取决于它们是否被 journal/`record_failure` 校验；若不进，Host 诊断层对 `SOURCE_PLAN_*` 的可读性较差 | 源码 | 由实施者在 AC-H3-3 的拒绝矩阵里决定并写证据；**不得**为它们新造 category/retryable |
| R-r2-08 | **P3** | `tests/fea11/test_source_command_parity.py:31-70` | 现有断言 `len(host)==14` 与 `if/elif` 结构对「新命令不进 HostCommandRegistry」的**漏检**是常态：新命令加错通道不会被抓 | 源码 | 新命令的通道断言必须显式写（AC-H3-2），不能只靠 parity 文件 |

## 7. UNKNOWN（如实登记）

- **UNKNOWN-1**：`Kill(entireProcessTree:true)` 在本机是否**确实**覆盖真正的 Python Core 进程（PyInstaller onefile / `python.exe` 子进程），本轮未跑；AC-H3-4 以显式 PID 断言兜底，未证实记 NOT_RUN。
- **UNKNOWN-2**：本轮**未跑**任何 gated IPC / 崩溃注入（未设 `NEWMANGA_FEA11_IPC=1`，未起真实 Core）；「新进程恢复一次」当前只是代码级推断（§1 新增事实 1/2），不是实测证据。
- **UNKNOWN-3**：`Roots` 多 root 的**实际发生率**未统计；本报告只证明生产 `RegisterRoot` 传单 root，registry 格式允许多 root。实现必须以 fail-closed 处理，不得猜。
- **UNKNOWN-4**：`body_json` 的 8MiB 预算与 `entries` >10000 的真实组合未实测；AC-H3-2 只要求 typed `SOURCE_BUDGET_EXCEEDED` 不截断。
- **UNKNOWN-5**：wirelog 脱敏器是否覆盖新命令 payload 的嵌套 `entries`（`EntryEvidence` 是否含可识别路径/locator）未逐字段核；AC-H3-2 以「0 命中」断言兜底，实施须先看 `C-16 §7` 脱敏实现（本轮未读）。
- **UNKNOWN-6**：恢复路径的「恰好一次」在 Host 重启两次、并发两个 recover 进程时的行为未建模；AC 只覆盖串行二次调用幂等（0 新帧）。

## 8. 门禁只读复核（本轮实测）

| 项 | 命令 | 结果 |
|---|---|---|
| 治理默认 | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**；**EXIT=0**（warning：12 个非终态 Task / `STATUS.md` 3009 bytes·29 lines 80% / `REBASELINE_PLAN.md` 6891 bytes·64 lines 80%） |
| 治理指定卡 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-HOST-AUTH-3.md` | **PASS (3 warnings)**；**EXIT=0** |
| 契约 pin | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **`PIN AUDIT: PASS (all 18)`**；C17 `cdeee4872e29`；**EXIT=0** |
| 工作树 | `git status --porcelain` | 空（本文件写入前） |
| 实现前置 | `grep source_get_sync_plan|SourcePlanMaterializ|source.sync.plan-materialization`（`src/`+`apps/desktop-avalonia/src/`） | **0 命中**（确认未动工） |

> 本报告不跑全量 `pytest`/全量 .NET（scope review 非必需，且会引入与本卡无关的 flake 噪声）；由 AC-H3-6 在实施轮承担。

## 9. 结论

- **verdict：`READY-TO-FREEZE`。**
  - **冻结范围**：§2 的 **19 条 allowed_paths**（Core 5 / Host 7（含 1 条件项）/ 证据与治理 7；§2 明确「不改」的清单同样是冻结的一部分）。
  - **AC**：§3 的 **6 条**；其中 **AC-H3-4 唯一不可替代**，AC-H3-5 是其防伪，AC-H3-2/3 是前置，AC-H3-1/6 是边界与诚实性。
  - **崩溃注入方案（一句话）**：外部 `crash-ack.ps1` 两阶段——真链跑到 journal `core-committed` 写 `park.json` → `Kill(entireProcessTree:true)` 并轮询证明 dotnet 子进程与全部 Python Core PID 已死 → 新 dotnet 进程 + 新 Core + 新 host session 用新命令物化读回、重铸 fresh grant、ACK 成功一次，断言「PID 不同 / core_session_id 不同 / 新 grant id ∉ journal」三重防伪 + gates 全开 + 行数不变 + digest 一致 + 二次 0 帧；未证明 sidecar 死即 NOT_RUN。
  - **冻结前置（必须随冻结一起落盘）**：R-r2-01（卡面 4 行：错误码 + 3 处字符丢失）、R-r2-02（AC 口径）、R-r2-03/04（把「不许猜源」「Core-free seam」写进卡面），否则冻结的 AC 与卡面文字自相矛盾。
- **是否需要额外 UNFREEZE**：**否**。C-17 v1.2 即载体，pin 已 18/18；实现若发现必须改契约字段（如 DTO 增 `source_kind`），**停**并回 DSH 另走 v1.3，不在本卡吸收。
- **不批准项**：本报告不批准任何实现，不改变 `FEA-11-HOST-AUTH-2` 的 `AC-F3 = NOT_APPLICABLE`，不构成对 `approval` 的解冻；R-03（空 `grant_ids` 子句不可达）仍按裁决另立缺陷卡。
- **复审口径**：若 DSH 冻结时改动 §2 的文件集合或 §3 的 AC 语义，本报告需重做 r3；若只改卡面文字（R-r2-01/06）与文档措辞（R-r2-05），无需复审。
