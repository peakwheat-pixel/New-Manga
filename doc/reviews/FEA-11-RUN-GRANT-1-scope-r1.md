---
task: FEA-11-RUN-GRANT-1
title: FEA-11-RUN-GRANT-1 独立 scope review r1（Run-scoped source-read grant：契约缺口、最小 UNFREEZE 面与可测边界）
reviewer: fresh subagent（独立上下文；未参与实现；只读）
session: fresh subagent（Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
worktree: clean
reviewed_head: 91d224b88ce00e1f3498d4805870d7d2a0d7c4de
verdict: READY-WITH-UNFREEZE
---

# FEA-11-RUN-GRANT-1 Scope Review r1（独立只读）

> **结论先行：`READY-WITH-UNFREEZE`。**
>
> - **卡面现状（"复用既有 C-06/C-16 grant 语义与 wire，不新增契约"）不可行**，但不是不可修：真正的缺口不在"Host 不会铸 grant"，而在**"Core 没有任何命令可以把一份已铸 grant 建立成一次 Run 的 page-binding 授权"**。Core 的授权面是进程内的 `SourceReadGrantRegistry._bindings`（grant→`(source,version,entry)` 映射），它的生产者**只有两个**：引用导入（`runtime.py:567-569`）与 sync apply（`sources/service.py:287,295-323`）。Run 命令面（`StartRun`/`PrepareRun`/`AcceptRun`/`ControlRun`/`RetryFailedTargets`/`ResumeBlockedRun`）既不带 grant，也没有旁路能写这条映射 → **除 import/sync 后 ≤300s 窗口（L-R1 已登记）之外**，生产 referenced 页 Run 必在 provider 读图（`SOURCE_ACCESS_DENIED`）与 commit guard（`SourceImportError` → `DB_FAILED`）处 typed 失败。
> - **因此必须 UNFREEZE，且只有两种正当形态**：①**新增一个 Host→Core 的授权建立命令**（推荐：不碰 Run wire、不放宽任何已冻结授权不变量）；②**在裁决层重开 `FEA-09-impl-r1` R1-I002 的"禁止身份/facts 回退"**，改为 Core 侧按签名 facts + scope 匹配（零新命令，但会同时扩张 resolve 读面并弱化 entry 级授权）。本 review 推荐 ①；②必须由 DSH 明确改判，**不得由实现者自行选择**。
> - **不需要改动 Run 请求/响应字节**：`library_start_run → StartRun`（minor 3）的 payload、`PrepareRun`/`AcceptRun`（minor 12）的形状、`preparedDigest`/`idempotency_key` 语义全部可以保持零变化；`CORE_PROTOCOL_MINOR` 仍为 `3`。UNFREEZE 面 = **C-06 v1.2 + C-16 v1.3 两个文件（2/18 pins 重签）+ 独立 byte-level 复核 + 重冻**；M2-C1 是否需要同步修订见 §4.4（本 review 判"可选、非协议变更"）。
> - **必须拆卡**：`PREREQ（UNFREEZE）→ CORE（授权建立命令 + 验证 + 测试）→ HOST（铸造/绑定/刷新/接线 + .NET 测试）`。三卡顺序依赖；若 DSH 坚持单卡，则 scope 冻结时必须把 UNFREEZE 载体写成**前置门**（未重冻不得开工）。
> - **产品级可用性仍有一个必须由 Lead 裁决的口径**：grant 有效期**硬上限 300s**（`source_read_refs.py:164-166`），而书级 Run（OCR/翻译）常态超过 300s。首个切片要么在 Host 侧做"Run 存活期内定期重铸 + 重绑"（复杂度与资源风险上升），要么如实登记 **L-G1：单 grant 语义下，Run 超过窗口后后续提交单元 fail-closed**。**不得**把这条写成"已解决"。

---

## 1. 只读核验基线（review 时点）

| 项 | 事实 | 证据 |
|---|---|---|
| 分支 / 工作树 | `main` / **clean**（review 写入本报告前；含一次测试副作用恢复，见下行） | `git status --porcelain`（两次；均为空） |
| 实测 HEAD | `91d224b88ce00e1f3498d4805870d7d2a0d7c4de`（与任务给定一致，review 期间无漂移） | `git rev-parse HEAD`、`git branch --show-current` |
| 契约 pins | **18/18 PASS** | 实跑 `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → `PIN AUDIT: PASS (all 18)`；C06=`8faa8cd139f2`、C16=`0b9511a55ea1`、C17=`aefa0fa5b17e`、C15=`d8c0a3bcfc21` |
| 治理检查 | **PASS（3 warnings）** | 实跑 `pwsh -NoProfile -File tools/governance/check.ps1`；warnings = 9 个非终态 Task、STATUS 3092B/27 行（80%）、PLAN 6945B/63 行（80%） |
| pytest 基线（本 review 实测） | `pytest tests/fea11` → **145 passed / 8 warnings**（8.91s，与 RENDITION-1 closeout 记录一致） | 实跑 `C:/Python314/python.exe -m pytest tests/fea11 -q`（`PYTHONPATH=src`） |
| pytest 定向（本 review 实测） | `test_source_rendition_gates.py` + `test_source_rendition_run.py` → **21 passed**（1.23s） | 同上 |
| .NET 定向（本 review 实测） | `NewManga.Host.Tests` 过滤 `Grant\|SourceRead\|SourceRegistry` → **4 passed / 6 skipped / 0 failed**（`--no-build`，Release） | 实跑 `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/... -c Release --no-build --filter ...`；6 skipped 为 `NEWMANGA_FEA09_IPC/NEWMANGA_FEA11_IPC` 未置 1 的 opt-in 真 IPC 用例 |
| 测试副作用 | 跑 pytest 后 `verification/FEA-09/logs/wire-redacted.ndjson` 被追加 1 行（timestamp `2026-11-06T14:39:06Z`）；已 `git checkout --` 恢复，工作树复 clean | `git diff`（+1 行）→ `git checkout --` → `git status` 空 |
| 全量 pytest 3249/10 | **NOT_RUN**（review 未跑；引用 RENDITION-1 closeout 记录） | `doc/tasks/FEA-11-RENDITION-1.md:125,134,220` |
| 全量 .NET 1527/0/86 | **NOT_RUN**（review 未跑） | 同上；另见下方"Lead 基线轮异常" |
| API inventory | **NOT_RUN** | 未执行 `python tools/generate_api_inventory.py --check` |
| Lead 基线轮异常（旁证，非本 review 实测） | Lead 在 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\baseline\` 留下的基线：`pytest-baseline.exit = EXIT=0`；**`dotnet-baseline.exit = EXIT=1`**，失败 1 例 = `NewManga.CoreClient.Tests.Commands.RunBindingFixTests.ModelsBuild_BookRun_WithoutInjectedBindings_StillFailsOcrWithProviderNotConfigured`，错误为 `IOException: 另一个程序已锁定文件的一部分… '...\Temp\newmanga-host-client-tests\run-binding-baseline-8b8fe4bbbe\library.db-shm'`（`ModelSidecarFixture.CopyDatabase`） | 已单独发消息给 Lead：疑与本 review 同期跑的 `--no-build` Host 定向测试争用临时 DB；**建议 Lead 复跑该测试项目**，不要把 `EXIT=1` 记成产品回归 |
| 占位卡 | `proposed`；`allowed_paths` 仅卡/Review/Handoff/evidence；`out_of_scope` 含"生产实现" | `doc/tasks/FEA-11-RUN-GRANT-1.md:6,21-28` |
| 依赖卡 | `FEA-11-RENDITION-1` = `done`，`integration_commit=a05a419f7`，L-R1…L-R11 已登记 | `doc/tasks/FEA-11-RENDITION-1.md:1-40,147-160,214-225` |

> 说明：本 review 未修改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据；除本报告外唯一动作是**恢复**一次由测试运行产生的 `verification/FEA-09` 字节（向 HEAD 复原，不是新增内容）。未跑的命令均已标注 `NOT_RUN`；所有数字均为本 review 实测并在上表记录。

---

## 2. 结论与边界（先讲清楚，后面给证据）

### 2.1 一句话结论

**"Host 铸 grant" 是必要但不充分条件。** 缺口是 **Core 侧的授权建立面**：Core 只承认"曾导入/曾同步该 entry 的 grant 可以读该 binding"（`_bindings` 映射），而 Run 既不导入也不同步，所以即使 Host 在 Run 前铸出一份完全合法、四维 scope 正确、签名正确的 grant，Core 也不会用它授权任何一次读或提交——因为它没有"这份 grant 授权了这些 page binding"的记录。

### 2.2 为什么这是"外部行为缺口"而不是纯实现问题

| 事实 | path:line | 含义 |
|---|---|---|
| Core 读面/守卫的唯一授权选择器是 `find_bound_for_source` | `src/bootstrap/core_assembly.py:1773`（Run commit guard）、`src/application/importing/referenced/resolve.py:75-81`（provider 与 resolve 共用 `prepare_referenced_rendition`） | 只查 `_bindings`；**不比较 grant 的签名 scope** |
| `_bindings` 只在两处写入 | `src/infrastructure/resource_channel/source_read_refs.py:411-440`（`bind_imported_entry`）；调用点 = `src/application/importing/referenced/runtime.py:567-569`（import）与 `src/application/sources/service.py:287,295-323`（sync apply） | 生产者是**两条业务命令**，不是通用授权面 |
| Run 命令面不携带任何 grant 标识 | `src/bootstrap/core_service.py:5867-5895`（Prepare/Accept）、`:5896-5923`（StartRun）；`StartRun`/`ControlRun`/`ResumeBlockedRun`/`RetryFailedTargets` 形状见 M2-C1 §5.5 | 没有"把这份 grant 用于这次 Run"的入口 |
| host-control 命令闭集里没有授权建立命令 | `src/bootstrap/core_service.py:355-364`（`_HOST_CONTROL_COMMANDS`）；分发分支 `:1461-1494` | 现有只有 Register/RevokeSourceReadGrant（注册/撤销），没有 bind/authorize |
| `RegisterSourceReadGrant` 只登记 grant，不建映射 | `source_read_refs.py:110-213`（`register`）末尾只写 `_grants` | Host 铸得再多也不会让 Run 可读 |
| 过期即拒 | `source_read_refs.py:164-166`（注册时 `expires_at > now+300` 即拒）、`:559-584`（`_checked` 每次校验 expiry/revoked/generation/session） | 即使 import 时绑过，grant 过期后 binding 映射也**自动失效** → L-R1 的"≤300s 窗口"结论正确且无法通过"延长窗口"修补 |

### 2.3 推荐的最小冻结面（详见 §4/§6）

- **UNFREEZE：需要。** 被改契约 = `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md`（v1.2，§2.2 一句授权建立语义 + §2.3 一行命令）与 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.3，§0 一个 additive 能力 + §2 一个新命令小节）。**不改** Run wire、不改 `schema.py`、不改依赖、不加错误码。
- **交付顺序**：`PREREQ（UNFREEZE 前置卡）→ CORE（命令 + 验证 + Python 测试）→ HOST（铸造/绑定/刷新 + .NET 测试）`。

---

## 3. 逐项代码事实（带 path:line；行号以 `91d224b88` 为准）

### 3.1 Host 侧：能铸 grant，但只被 import/scan 调用

| 事实 | path:line |
|---|---|
| `SourceReadCoordinator.IssueAsync` 完成：能力探测 `source.read/1` → host session → registry `Authorize` →（folder 时枚举排序）→ 逐文件 `FileStream` + `SourceSecurity.Identity` 前后比对 + SHA-256 → 铸四维 scope `{source_id, version, rendition, entries[]}` → HMAC 签名 → `RegisterSourceReadGrant` → 仅入内存 `_payloads/_grants` | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:44-122`（关键：`:53` 能力、`:59/62/83` 三次 `Registry.Authorize`、`:84-94` payload、`:112-115` 签名+注册、`:116-118` 记账） |
| 撤销：`RevokeSourceReadGrant`（按 registry+generation+grant_ids）；Secret-G 克隆：`IssueSecretGrantsAsync` | 同文件 `:191-212`、`:130-181` |
| `SourceAccessRegistry`：持久化 registry（`registry.v1.dat`），`Register/List/Authorize/Revoke/Reset`；`Authorize` 校验 generation + 逐根 identity | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs:8-88` |
| `HostIssuer` 只铸 **import / export** 两类 grant（`ImportGrant`/`ExportGrant`），没有 source-read | `apps/desktop-avalonia/src/NewManga.CoreClient/Issuer/HostIssuer.cs:30-34,47-103` |
| **`_payloads`/`_grants` 从不剪枝**（只有 secret grants 被 `Clear()`）→ 若"每次 Run 都铸 grant"，内存随 Run 次数无界增长 | `SourceReadCoordinator.cs:16,20,116-118,246`；对比 `:194-199`（只清 `_secretGrants`） |

### 3.2 已知 grant 的产生/绑定：**绑定恰好两处**（与 Lead 初判基本一致，但"三处"需分开说）

| # | 产生 | 绑定 | 证据 |
|---|---|---|---|
| 1 | import：App `IssueGrantsAsync` 调 `_sources.IssueAsync(...)`（sourceId = `StableSourceId(path)` 或 folder 的 registryId；version = `"1"`） | Core `runtime.py:567-569` 在每页提交后 `bind_imported_entry(grant_id, source_id, version_id, entry_id)` | `apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs:741-753`、`src/application/importing/referenced/runtime.py:567-569` |
| 2 | sync apply：**Host 不自行铸造**；`HostOperationOrchestrator.ApplyAsync` 只从 payload 收集 `grant_ids` 并随 apply 下发，同时铸的是 `HostAuthorization`（registry 授权摘要，**不是** source-read grant）。仓内 App 无 sync apply 的 UI 调用点（`IssueGrantsAsync` 只被 import 用） | Core `sources/service.py:287` → `_bind_operation_grant`（`:295-323`，对 receipt 里每个 healthy binding 调 `bind_imported_entry`；version 不符时按 kept page 语义跳过） | `apps/desktop-avalonia/src/NewManga.Host/Sources/HostOperationOrchestrator.cs:192-301`（`:213-230` 收集、`:273` mint HostAuthorization、`:300` 传入 operation）、`src/application/sources/service.py:284-323` |
| 3 | scan：`SourceScanScheduler` 每 target 铸 grant（`target.SourceId` = **Core** `src-<uuid>`，`target.Version` = Host 值）后走 `ScanSourceSync` | **不绑定任何 page binding**；Core 只用 `access.resolve(grant_id)` 授权观察容器（`src/application/sources/scanner.py:553`、`runtime.py:226`、`service.py:180`） | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1359-1389`、`src/bootstrap/core_service.py:1495-1525` |

> 净结论：**铸 grant 的可见生产者 = import（App）+ scan（Host）两处**（sync 的 grant_ids 由调用方提供，仓内无 UI 生产者）；**写 grant→binding 映射的 = import + sync 两处**。Run 两者皆无。

### 3.3 Run 通道：**Lead 初判需纠正一处**

| 事实 | path:line | 说明 |
|---|---|---|
| `HostRuntime.PrepareRunAsync/AcceptRunAsync` 直通 `CoreServiceClient` | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:48-58`；`CoreServiceClient.cs:271-315`（`SendAsync("PrepareRun"/"AcceptRun", 12, ...)`） | **存在但不是生产路径**：App 层只有 `HostController.PrepareRunAsync/AcceptRunAsync`（`apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:2138-2162`；接口 `RunContracts.cs:361-362`）的 API 面，**全 `NewManga.App` 无任何 ViewModel/UI 调用点**；`PrepareRun` 请求键集被 Core 严格校验（`set(payload) - {command,scope,overrides}` → `INVALID_REQUEST`，`core_service.py:5871-5872`），`AcceptRun` 严格 `{prepared_run,idempotency_key}`（`:5889`） |
| **生产 Run 路径 = `library_start_run` → `StartRun`（minor 3）** | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:41-43`（`IsRunCommand`）、`:222-223`（注册）、`:284`（`["library_start_run"] = new("StartRun", 3)`）；payload 写出 `HostCommandDispatcher.cs:415-423` | 因此"只给 Prepare/Accept 加 grant"**不会修好产品**；必须覆盖 `StartRun`（以及任何会触发步骤执行的命令，见 §9 L-G4） |
| Host 侧没有 Run 前置授权钩子 | `HostCommandDispatcher.InvokeAsync`（`HostCommandDispatcher.cs:84-149`）现有注入点只有 `_capabilityGate`/`_journal`/`_operationJournal`/`_hostLocal`；`HostOperationOrchestrator` 只服务 sync | 需要新增一个"Run 前置授权"委托或等价接线（属 HOST 卡） |
| Core 侧 Run 分发无 grant 概念 | `core_service.py:5850-5895`（`PrepareRun`→`pipeline.prepare_run`，`AcceptRun`→`accept_prepared_run`）、`:5896-5923`（`StartRun`→`accept_start_run`） | 结果只有 `run_id`/`status`/`preparedRunId` 等；无 grant 字段 |
| Run 提交时逐页走 guard | `src/infrastructure/sqlite/pipeline.py:897-899`（`leases.enter_context(self.source_commit_guard(current.page_id))`） | 每个提交单元（页）重验 → 与 C-06 约束 11 的"提交边界重验"一致；撤销/过期在下一页提交即 fail-closed |
| 装配把 guard 接到 `_catalog.source_commit_guard` | `core_assembly.py:1757-1780`（`read_gate` → `find_bound_for_source` → `commit_guard`） | 缺 grant → `SourceImportError` → commit 的 `except Exception` → `db_failed` → `DB_FAILED`（RENDITION-1 已实测并固化为 L-R1 负向用例） |

### 3.4 Core 守卫/读面：三个消费者共用一个 gate，一个授权选择器

| 事实 | path:line |
|---|---|
| 唯一 `read_gate(page_id) -> unavailable/pending/open` | `core_assembly.py:1244-1261`（`source_sync_store.current_binding_of_page` + `gate_of_binding`；无 publication 行 = open） |
| 三处消费（Run guard / provider / target catalog） | `core_assembly.py:1750-1753`（catalog 注入）、`:1669-1687`（provider 注入 `source_access=source_read_refs, read_gate=read_gate`）、`:1757-1780`（guard） |
| provider referenced 分支：gate → 单一选择函数 → Secret-G → 渲染 | `core_assembly.py:444-501`（`:461-468` gate、`:470-472` `prepare_referenced_rendition`、`:476-482` `claim_secret_for_binding`、`:483-492` typed 固定文本） |
| 共享选择函数：binding healthy → entry 存在 → `find_bound_for_source`（有则用，否则退化 `find_for_source`）→ generation 比较 → 尺寸/decoder/params | `src/application/importing/referenced/resolve.py:47-139`（`:75-83` 选择器、`:84-90` generation 比较、`:102-118` params/cache_key） |
| 三个选择器：`find_bound_for_source`（唯一生产生效）、`find_for_identity`、`find_for_source` | `source_read_refs.py:442-475`、`:477-519`、`:521-548`；实测生产 `src/**`：`find_for_identity` **0 调用点**；`find_for_source` 只出现在 `resolve.py:82-83` 的**回退分支**（`find_bound = getattr(access, "find_bound_for_source", None)` 为 None 时才走），而生产 `access` 恒为 `SourceReadGrantRegistry`（有该方法）→ 该分支生产不可达；R1-I002 之后身份回退已被退役 |
| resolve 面另有 gate（与 assembly 的 `read_gate` 语义不完全一致 → L-R11） | `core_service.py:4420-4463`（`:4456-4458` `_assert_source_sync_gate`）、`:5072-5103`（previous-binding 链 fail-closed） |

### 3.5 扫描枚举能给 Host 什么、不能给什么

| 事实 | path:line |
|---|---|
| `source_list_scan_targets` 命令存在（application 面，closed `{}`） | `core_service.py:5007-5017`；`CoreServiceClient.ListSourceScanTargetsAsync`（`CoreServiceClient.cs:1541-1569`，先探 `source.sync.enumerate/1` 能力） |
| 实现只做单 SELECT 投影 + 校验 | `src/application/sources/scanner.py:96-177`（`list_scan_targets`，零写） |
| DTO 冻结形状 | C-17 §5.2（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:261`）：`ScanTarget = {source_id, registry_id, generation, source_kind, identity_digest, project_ids}` |
| **不能**据此铸出可用的四维 scope | 没有 `version_id`、没有 `entries[]`（locator/ordinal/facts）、没有 entry_id；`issueAsync` 的 `version` 只是 Host 自报值。即使铸出来，Core 仍缺"这份 grant 绑定到这些 binding"的记录 → **候选路径 ③ 单独不成立** |

### 3.6 可复用通道核实（Lead 问的三条）

| 通道 | 事实 | 结论 |
|---|---|---|
| `SendHostControlAsync` | `CoreServiceClient.cs:551-560`（通用 host-control 发送；`SourceReadCoordinator` 已用它发 Register/Revoke） | **可复用**：新命令不需要新传输层；Host 侧只需新增一个调用点 |
| `HostCommandDispatcher` 委托 | `HostCommandDispatcher.cs:42-80`（`_capabilityGate`/`_journal`/`_operationJournal`/`_hostLocal` 注入模式） | **可复用模式**：新增一个 `runAuthorize` 委托即可，不必改 wire |
| `HostOperationOrchestrator` | `HostOperationOrchestrator.cs:15-300` | **不可复用**：只服务 sync apply/recovery，不接受 Run |
| `HostCommandRegistry.library_start_run` | `:284` 映射到 `StartRun`, minor 3；无 `library_prepare_run`/`library_accept_run` | 新命令若走 `SendHostControlAsync` 直连（像 `RegisterSourceReadGrant` 那样），**不会触发** `tests/fea11/test_source_command_parity.py:34` 的 `len(host)==14` 断言；若登记成 Host 命令则必须同步该断言 |

### 3.7 文档 vs 代码不一致（按"代码/Git 为事实"登记）

| # | 文档说法 | 代码事实 | 处置 |
|---|---|---|---|
| D-1 | C-16 §3.1 step 3：resolve 的 Auth = "存在 live grant 的 **scope 与 binding 的 source/version/entry/rendition 一致**" | 生产实现**不比较 scope**：`prepare_referenced_rendition` 用 `find_bound_for_source` 查 `_bindings`（grant→Core ids）。`verify_scope`（`source_read_refs.py:550-556`）**生产 0 调用点**，仅 `tests/fea09/test_source_grants_unittest.py:60-64` 使用 | 登记。本卡的授权建立面**正是**补这条映射；不要把它改写成"scope 比较"（zip/folder 的 scope 不含 Core entry id，反而无法比较） |
| D-2 | M2-C1 §5.7（rev 2.3）把 `HostControlCommand` 枚举为 `RegisterImportSource \| RevokeImportSource \| RegisterExportTarget \| RevokeExportTarget \| CloseHostSession`（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:182,495`） | 代码已实现 `RegisterSourceReadGrant`/`RevokeSourceReadGrant`（C-16）与 8 条 C-17 source-sync 命令，M2-C1 未登记 | 登记为**文档滞后**（先例：C-16 自行承载，未改 M2-C1）。新命令沿用同一先例，但 §4.4 要求 DSH 明示取舍 |
| D-3 | RENDITION-1 scope review 引用的 `core_assembly.py:1623-1641`、`HostRuntime.cs:861-867` | 本 HEAD 下：guard 在 `core_assembly.py:1757-1780`；`HostRuntime.cs:861-867` 现在是 `HostLocalAsync` 的 source 命令分支，`library_start_run` 走 dispatcher（`HostCommandRegistry.cs:284`） | 登记为行号漂移，供后续审查避免误引 |
| D-4 | C-16 §2 `entries[].entry_id` = "Core EntryId or null on first import" | 没有任何 wire 向 Host 暴露 Core `entry_id`/`version_id`（枚举 DTO 也没有） | 登记：这条契约假设的"Host 可知 Core id 通道"不存在；是 U-A 必须由 Core 侧解析 scope 的根本原因 |

### 3.8 本 review 的实测证据（不是推断）

| 证据 | 命令 | 结果 |
|---|---|---|
| L-R1 现状可复现为 typed 失败 | `pytest tests/fea11/test_source_rendition_run.py::test_run_without_a_live_source_grant_is_typed_and_writes_nothing`（含在 21 passed 内） | Run 终态 `FAILED/COMPLETED_WITH_FAILURES`，step code ∈ `{INVALID_INPUT, PROVIDER_FAILED}`，`_region_rows/_revision_rows/_lineage_rows = 0`、detector 0 次（`tests/fea11/test_source_rendition_run.py:632-656`） |
| 真实装配下 guard 缺 grant 必拒、有绑定则开 | `pytest tests/fea11/test_source_rendition_gates.py::test_real_run_commit_guard_refuses_pending_gate_and_missing_grant`（含在 21 passed 内） | pending → `TARGET_NOT_FOUND`；open 但无 grant → `SourceImportError("SOURCE_ACCESS_DENIED")`；`mint_grant` + `bind_imported_entry` 后 guard 通过（`tests/fea11/test_source_rendition_gates.py:286-321`） |
| 真实装配 provider 读到当前 binding 像素 | 同文件 `::test_real_assembly_provider_reads_the_binding_rendition_end_to_end` | 无 grant → `INVALID_INPUT`（detail 含 `SOURCE_ACCESS_DENIED`）；绑定后 `page_frame("pr")` 尺寸 = NEW_B（`:324-362`） |
| Host 定向 .NET 测试可执行、真 IPC 用例默认 skip | 见 §1 | 4 passed / 6 skipped |

> 本 review **没有**自建临时探针脚本、**没有**修改任何文件（报告除外）、**没有**跑全量门禁；上表全部为"跑既有测试"的结果。

---

## 4. Q1 契约充分性（核心问题）

### 4.1 逐条核实：冻结条款覆盖什么

| 条款 | 覆盖 | 对本卡的判定 |
|---|---|---|
| `C-06 §2.2`（`doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md:33-43`） | grant 字段（四维 scope/entries/budget/secretRef/signature）、**Host 唯一授予方**、`≤300s`、撤销/失联线性化、`SOURCE_ACCESS_DENIED` fail-closed | **覆盖"铸"与"撤"，未覆盖"为某次 Run 建立授权"**；也没有说"grant 只能被导入使用" |
| `C-06 §2.3`（`:45-56`） | `RequestSourceRead`（Host 铸造前语义请求）、`VerifySourceRead`（双侧）、`RevokeSourceReadGrant`（Host→Core） | `RequestSourceRead` 是 **Host 内部**语义动作，不是 Core 命令；三条都不建立 grant→binding |
| `C-06` 约束 10/11（`:69-70`） | 撤销即时、**每个提交单元事务提交前重验** | Run 的 per-page `source_commit_guard`（`pipeline.py:897-899`）**已满足**；撤销/失联语义无需改 |
| `C-16 §2`（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md:36-70`） | `RegisterSourceReadGrant` 字节形状、Core 侧 `VerifySourceRead`（签名/session/operation/expiry/generation/scope/identity）、失败码优先级 | **覆盖"校验一份 grant 本身"**；没有定义 Core 如何把 grant 关联到 page binding（授权面） |
| `C-16 §7` 第 5 条（`:182`） | "Core 只接受 grant 中的路径与 facts；不得以调用方/receipt/UI 路径读取" | 新授权面**不得携带路径**（Host 只传 grant_id + Run scope/page ids）→ 可直接满足 |
| `C-16 §6`（`:149-174`） | 错误码闭集（含 `SOURCE_ACCESS_DENIED/GRANT_EXPIRED/GRANT_REVOKED/BUDGET/PASSWORD/CAPABILITY_MISSING`）与优先级 | **够用，不需要新码** |
| `C-16 §3.1`（`:82-108`） | Secret-G 通道；step 3 要求 "live grant 的 scope 与 binding 一致（Auth）" | 见 D-1：契约文字与实现（bind map）不一致；本卡补的是映射，不是 scope 比较 |
| `C-17 §3.3`（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`） | "R、resolve、issue、**Run 输入**、live edit 在授权校验外必须检查 publication gate；pending → `SOURCE_ACCESS_DENIED`" | **已覆盖 Run 的 gate**；RENDITION-1 已实现（`read_gate`），本卡不改 |
| `C-17 §7.2/§7.3`（`:329-337,339-348`） | resolve 与 issue/**实际资源读取**必须用同一选择结果；**不建第二套匹配规则** | **禁止**在 provider/guard 另造选择规则 → 强化否决"路径 ② 的强形式" |
| `C-15 §4.1 R(p,t)`（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:264`） | referenced 可读 = 有效 source-read grant + **identity digest 匹配**（加密源另需 fresh-grant） | 允许"facts 匹配"的**读法**，但不构成"授权建立机制" |
| `M2-C1 §5.5`（`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:208-231`） | Run wire（`StartRun`/`PrepareRun`/`AcceptRun`/`ControlRun`/… 形状、`RunAccepted`、idempotency、`preparedDigest`） | **本方案不改**；若改 Run 请求字段 → 必须动 §5.5 与 minor（下策） |
| `M2-C1 §5.7`（`:463-552`） | HostControl envelope/session/credential、Host-only 拒绝 | **协议语义已覆盖新增 host-control 命令的会员资格**；只是命令枚举未更新（D-2） |

### 4.2 缺口定义（一句话）

> 冻结契约完整覆盖了 **"grant 怎么铸"（C-06/C-16）**、**"grant 怎么校验"（C-16 §2）**、**"Run 怎么读/怎么门控"（C-17 §3.3/§7.1/§7.2、C-15 §4.1）**，但**没有覆盖"一份已铸 grant 如何被承认为某次 Run 的 page-binding 授权"**——而这个承认关系目前在 Core 里只有 import/sync 两个写入口。

### 4.3 最小变更（U-A，推荐）

| 变更项 | 载体 | 最小内容 |
|---|---|---|
| **新 host-control 命令**（建议名 `AuthorizeSourceReadForRun`；名称由 DSH 定） | **C-16 v1.3 §2.x**（新小节） | Host→Core，host-control envelope（复用 `host_session_id/credential`）；请求 closed shape `{grant_ids: ID[1..N], command: PipelineCommand, scope: PipelineScope}`；响应 `{bound_pages: int, refused: [{page_id, code}]}`（**不含路径/entry 名**）；语义：Core 用**与 Run 相同的 scope 展开器**解析目标页，对每个 healthy binding 找一份 live grant，其签名 facts/scope 覆盖该 binding 的 `(source, accepted_version, entry)`（对 `source_locations`/`source_entries` 校验，无路径回退），命中则写入 `bind_imported_entry` 同构的映射；**零 DB 写**；幂等；失败按 C-16 §6 优先级 typed |
| **授权建立语义（第三生产者）** | **C-06 v1.2 §2.2**（新增一句） | 明确"grant→binding 授权可由该命令建立；不延长 300s；撤销/过期即失效；不得以路径回退；同一 binding 允许多份 grant，选择规则沿用 `find_bound_for_source`（最高 generation）" |
| **能力门（additive）** | **C-16 v1.3 §0** | 新增 `source.read.run/1`（或等价）；Host 缺失 → `CORE_CAPABILITY_MISSING`，**不铸 grant、不 dispatch**（沿 C-16 §0 的"按操作检查、不靠发送后看结果"） |
| 协议 minor | 不需要 | host-control additive；`CORE_PROTOCOL_MINOR` 仍 `3`（C-16 §0 先例：新命令按默认面 minor=3） |
| Run wire | 不需要 | `StartRun`/`PrepareRun`/`AcceptRun`/`ControlRun`/`RetryFailedTargets` **请求/响应字节零变化**；`preparedDigest`/`fingerprint`/`idempotency_key` 语义不受影响（grant 不进 overrides——见 §5 否决项） |
| 错误码 | 不需要 | 复用 C-16 §6 闭集；Run 面投影沿用 C-17 §8:352"旧命令不重映射"（`DB_FAILED`/`PROVIDER_FAILED`/`TARGET_NOT_FOUND` 保持不变） |
| `M2-C1` | **可选** | §5.7 命令枚举补 source-access 命令属"文档一致性"（D-2 已滞后）。若 DSH 认为 M2-C1 枚举必须权威 → 第三个文件进 UNFREEZE；若沿用 C-16 自承载先例 → 不改，但卡面必须登记该滞后 |
| `C-07`（API inventory） | 不需要 | 不新增 `IHostController` 方法；新命令是 Host 内部 `SendHostControlAsync` 直连（与 `RegisterSourceReadGrant` 同构） |
| `schema.py` / 依赖 / 迁移 | 不需要 | 授权映射是 in-process（与现有 `_bindings` 同性质） |

### 4.4 UNFREEZE 判定与复核要求

**判定：需要。**

| 项 | 内容 |
|---|---|
| 被改契约 | ① `doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md` → v1.2（pin `8faa8cd139f2…` 变更）② `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md` → v1.3（pin `0b9511a55ea1…` 变更）③（可选）`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` |
| 变更点 | 见 §4.3 表；**只允许**新增小节/句子与能力字符串，**不得**修改既有 grant 形状、错误码、Run wire 或任何其他 pin 的字节 |
| pin 影响 | 18 项中**恰好 2 项**（C06/C16）重签；其余 16 项必须逐字节不变 → 复核必须给出"16 项 pin 不变 + 2 项按预登记值变化"的证据 |
| 独立 byte-level 复核 | 必须由**未参与该 UNFREEZE 起草**的独立上下文执行：①对改前/改后文件做字节级 diff，确认只有登记段落变化；②重算 sha256 并写入 `FEA-CONTRACT-FROZEN-C06/C16`；③在 `doc/reviews/CONTRACT-UNFREEZE-2026-11-xx.md` 载体记录 pre/post sha256、复核结论（P0/P1=0）、以及"未改动其他契约"的断言；④复核后重跑 `verify_pins.ps1` **18/18** |
| 冻结纪律 | UNFREEZE 未完成前，**实现卡不得开工**；实现卡**不得**顺手改契约字节（AC-G7 强制） |

> 反向选择（**不推荐**）：若 DSH 选择"零新命令、Core 按签名 facts + scope 直接授权"（§5 路径 ②），那就**不是零裁决**：它必须重开 `FEA-09-impl-r1` **R1-I002**（"不能用身份回退代替 scope"），并同步 C-16 §3.1 的 "scope 与 binding 一致" 读法；C-15 §4.1 的 "identity digest 匹配" 可以支撑，但 C-17 §7.3"不建第二套匹配规则"要求 resolve/provider/guard 三面同时改。**该路径的裁决成本高于 U-A，且弱化 entry 级授权，本 review 不推荐。**

---

## 5. Q2 四条候选路径评估（含对 Lead 初判的纠正）

| 路径 | 可行性核实 | 裁决 |
|---|---|---|
| **① Host 预铸 grant + Core 把 Run 目标绑定到该 grant** | **唯一不需要放宽任何不变量**的路径。Host 已能铸（`SourceReadCoordinator.cs:44-122`）；Core 侧的落点就是 `_bindings`（`source_read_refs.py:411-440`）。**但必须新增一个授权建立命令**（§4.3 U-A）：`_HOST_CONTROL_COMMANDS`（`core_service.py:355-364`）无此命令，`register()`（`:110-213`）不建映射，Run 命令也不带 grant。是否 new host-control ⇒ **是 wire 变更**（source-access wire v1.1 → v1.2） | **推荐**；需要 UNFREEZE C-06/C-16 |
| **② Core 把 Run 守卫/读面改为物理身份匹配（`find_for_identity` 式）而非 `find_bound_for_source`** | `find_for_identity` 存在（`source_read_refs.py:477-519`）但**生产 0 调用点**；R1-I002（`doc/reviews/FEA-09-impl-r1.md:160`）已判"不能用身份回退代替 scope"。且 folder 源 `IssueAsync` 产出的是 `folder_entries`，`find_for_identity` 只看 `container_facts` → **folder 直接失配**；zip 只有容器 facts → 授权粒度从 entry 放宽到 source。另与 C-17 §7.2/§7.3（单一选择函数、不建第二套规则）冲突，且会把 resolve 面一起改 | **不推荐**；若采用必须重开 R1-I002 + 改 C-15/C-17 读法（裁决成本 > U-A，安全面变弱） |
| **③ 通过 `source_list_scan_targets` 给 Host 足够信息铸造可命中 `find_bound_for_source` 的 grant** | DTO 只有 `{source_id, registry_id, generation, source_kind, identity_digest, project_ids}`（C-17 §5.2:261），**无 version_id / entries / locator / entry_id**；即便扩展 DTO（C-17 UNFREEZE），Core 仍**没有绑定记录** → 仍缺核心一步 | **单独不成立**；只能作为"Host 选源"的辅助信息，替代不了 ① |
| **④ 维持窗口语义（import/sync 后 ≤300s 可用）** | 已实测：过期后 `_checked` 拒（`source_read_refs.py:568-569`），import 的 binding 映射随之失效；书级 Run 常态 >300s → 首个过期后的提交单元即 `DB_FAILED` | **不可接受为产品修复**；只能作为 legacy 说明登记 |

**对 Lead 初判的纠正/补充（逐条）**

1. **生产 Run 路径是 `StartRun`（minor 3），不是 `PrepareRun`/`AcceptRun`。** `HostRuntime.cs:48-58` 的两个直通方法只为 App 提供 API 面（`HostController.cs:2138-2162`、`RunContracts.cs:361-362`），**全 App 无 ViewModel/UI 调用点**；真实链路是 `library_start_run` → `HostCommandRegistry.cs:284` → `HostCommandDispatcher.cs:415-423` → Core `StartRun`（`core_service.py:5896-5923`）。**只给 Prepare/Accept 接线会留下产品缺口**（除非 DSH 明确本卡只做冻结面、不动 App）。
2. `HostRuntime.cs:861-867`（RENDITION-1 scope review 引用）在当前 HEAD 是 `HostLocalAsync` 的 `source_*` 分支，**不是** `library_start_run`。
3. `find_for_identity` **生产 0 调用点**；`find_for_source` 只在 `prepare_referenced_rendition` 的 `getattr` 回退分支里（`resolve.py:82-83`），生产 `access` 恒有 `find_bound_for_source` → **实际不可达**。也就是说"身份回退"不是"存在但没用"，而是 R1-I002 之后被显式退役的路径。
4. `source_list_scan_targets` **不足以**让 Host 铸出可命中的 grant（DTO 缺 version/entry），但 Host 侧另有路径：`HostRuntime.RegisterSourceScanTarget(sourceId, path, projectIds, version)`（`HostRuntime.cs:106-121`）在导入完成时由 App 登记 → **Host 持有 `source_id → path` 映射**，可据此调 `IssueAsync` 铸造。所以"Host 不知道源路径"**不是**阻塞点；阻塞点仍是 Core 的绑定记录。
5. `IssueAsync` 每次会对容器**整文件 SHA-256 / folder 全量枚举+逐文件哈希**（`SourceReadCoordinator.cs:63-81`）→ 每次 Run 前现铸的 I/O 成本不是零（见 §9 L-G8）。
6. `_payloads`/`_grants` 无剪枝（`SourceReadCoordinator.cs:16,20,116-118`）→ "每 Run 一铸"会带来无界内存增长（§9 L-G7），HOST 卡必须处理或显式登记。
7. Host 无法把 grant 塞进 `overrides` 绕过 wire：`overrides` 参与 Run 快照/指纹语义（`core_service.py:5903-5908`、`src/infrastructure/sqlite/pipeline.py:1792-1809`；C-08 §`preparedDigest` 覆盖 `requestedTargets/settingsSnapshot/providerBindingSnapshot/constraintSnapshotRef`，`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md:43-56`），塞 grant 会污染 fingerprint/idempotency 与快照 → **否决**。

---

## 6. Q3 建议 In / Out / allowed_paths 与拆卡

### 6.1 拆卡建议（推荐三卡，顺序依赖）

| 顺序 | 卡 | 一句话目标 | 依赖 |
|---|---|---|---|
| 1 | `FEA-11-RUN-GRANT-1-PREREQ-1`（契约前置） | 用独立 UNFREEZE 载体把"Run 授权建立命令 + 第三生产者语义 + 能力门"写进 C-06 v1.2 / C-16 v1.3，经独立 byte-level 复核后重冻并重签 2 个 pin | 本 review 冻结 |
| 2 | `FEA-11-RUN-GRANT-1-CORE-1` | 在 Core 实现该 host-control 命令（host-only、closed shape、scope 展开、facts 校验、写 grant→binding 映射、零 DB 写、typed 失败）+ Python 测试 | PREREQ-1 done |
| 3 | `FEA-11-RUN-GRANT-1-HOST-1` | Host 在会触发步骤执行的 Run 命令前铸造+授权绑定（含 300s 窗口策略与记账剪枝），接 `HostRuntime`/dispatcher，补 .NET 测试与真实 IPC 证据 | PREREQ-1 done；CORE-1 提供被调命令 |

**合并选项（若 DSH 要求单卡）**：CORE-1 + HOST-1 可合并为一张实现卡（同一交付可观测），但 **PREREQ-1 不得合并**——契约字节必须先经独立复核并重冻，否则实现过程中任何"顺手改一句契约"都会破坏 pin 纪律。合并时 `allowed_paths` = 下述两卡并集。

### 6.2 建议 allowed_paths（文件级）

**PREREQ-1**

```
doc/tasks/FEA-11-RUN-GRANT-1-PREREQ-1.md
doc/reviews/FEA-11-RUN-GRANT-1-PREREQ-1-*.md
doc/handoffs/FEA-11-RUN-GRANT-1-PREREQ-1-*.md
doc/plan/FEA-C06_SOURCE_AUTH_DRAFT.md
doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
doc/plan/FEA-CONTRACT-FROZEN-C06.md
doc/plan/FEA-CONTRACT-FROZEN-C16.md
doc/reviews/CONTRACT-UNFREEZE-2026-11-*.md
verification/FEA-11-RUN-GRANT-1-PREREQ-1/**
```
（若 DSH 裁定 M2-C1 §5.7 必须同步，则增列 `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`；否则不得触碰。）

**CORE-1**

```
doc/tasks/FEA-11-RUN-GRANT-1-CORE-1.md
doc/reviews/FEA-11-RUN-GRANT-1-CORE-1-*.md
doc/handoffs/FEA-11-RUN-GRANT-1-CORE-1-*.md
verification/FEA-11-RUN-GRANT-1-CORE-1/**
src/infrastructure/resource_channel/source_read_refs.py
src/bootstrap/core_service.py
tests/core/test_host_control.py
tests/fea11/test_source_run_grant.py            # 新文件
```
（`src/bootstrap/core_assembly.py` **默认不列入**：命令只需 registry + host-control 分发；若实现证明必须动 assembly，先停下报 DSH 增列，不得静默扩域。）

**HOST-1**

```
doc/tasks/FEA-11-RUN-GRANT-1-HOST-1.md
doc/reviews/FEA-11-RUN-GRANT-1-HOST-1-*.md
doc/handoffs/FEA-11-RUN-GRANT-1-HOST-1-*.md
verification/FEA-11-RUN-GRANT-1-HOST-1/**
apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs   # 仅当需要新增前置授权委托
apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs          # 新文件
apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs            # 记账/生命周期单测
```
（`NewManga.App/**` **默认 Out**：绑定应由 Host 在 Run 命令前内部完成，App 不需要新接口；若实现证明 App 必须改动，先停下报 DSH。）

### 6.3 Out（三卡共同；明确不做）

- **UI/XAML/ViewModel/通知/Toast/本地化文案**；reader/导出/渲染/core.detect 语义。
- **扫描/调度/watcher/删除/回收站/GC/备份**；`schema.py` 与任何迁移。
- **真实用户数据 / AppData / 外部卷 / 回收站**；`verification/**` 外的仓外产物按 Resource Manifest 处理。
- **修改 18 pins 中除 C06/C16 之外的任何契约字节**；在实现卡里顺手改契约。
- **新增错误码**（尤其把 `SOURCE_*` 投影进 Run 命令面）；**改 Run wire / `CORE_PROTOCOL_MINOR`**。
- **push**；`doc/STATUS.md`/`doc/REBASELINE_PLAN.md`/`doc/TASK_LEDGER.md`（Lead 专属）。
- **宣称"referenced 页 Run 产品可用/全修 L-R1"**，除非 AC 全部实测通过且 L-G1/L-G4 已裁决。

---

## 7. Q4 AC 草案（v3 口径：可判别、可机械验证）

> 每条都必须有"删掉实现/改坏关键分支 → 变红"的判别性证据（记录在 `verification/**/logs/`）。像素断言**禁止 stub**；真实源树/zip/PNG 用 `tmp_path`。

- [ ] **AC-G1（契约在案，先于代码）**：UNFREEZE 载体存在且独立复核 approved；`verify_pins.ps1` **18/18**，其中 C06/C16 pin 等于预登记新值、其余 **16 项逐字节不变**；`git diff` 只含 §4.4 列出的文件。
  测试落点：`pwsh -NoProfile -File tools/governance/verify_pins.ps1` + `git diff --name-only <base>..<head>` + 载体文件自身。命令：见上（无需 pytest）。
- [ ] **AC-G2（授权建立命令的协议面）**：新命令 host-only——普通 application 面调用 → `HOST_ONLY_REQUIRED`；缺/错 session → `HOST_SESSION_INVALID`；payload 非 closed shape / grant_ids 非法 → `INVALID_REQUEST`；不存在的 grant_id → `SOURCE_ACCESS_DENIED`；**全部零 DB 写、零 binding 映射写入**。
  测试落点：`tests/core/test_host_control.py`（沿 `:319-338` 的既有参数化模式新增该命令），新 `tests/fea11/test_source_run_grant.py`。
  命令：`C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`。
- [ ] **AC-G3（真实装配 + 真实 grant 下 referenced Run 端到端，不是 mock 守卫）**：真实 production migrations 库 + 真实 zip/PNG + 真实 `assemble_core_services`（`tests/fea11/test_source_rendition_gates.py:202-213` 的 `real_core`）→ Host 等价流程铸 grant → **通过新命令**建立绑定 → `create_run(page-scope)` → provider `page_frame` 像素/尺寸等于当前 binding 的图（非 managed 旧图）→ `source_commit_guard` 通过 → 提交后 region/revision 行数符合预期。
  **判别性**：删掉"建立绑定"调用 → provider `INVALID_INPUT`、commit `SourceImportError`；把绑定指到错误 entry → 仍 fail-closed。
  测试落点：`tests/fea11/test_source_run_grant.py`（复用 `build_rendition_site`/`_execute` 模板，`test_source_rendition_run.py:131-280`）。
  命令：`C:/Python314/python.exe -m pytest tests/fea11/test_source_run_grant.py -q`。
- [ ] **AC-G4（fail-closed 全覆盖）**：①无 grant；②grant 过期（冻结 clock）；③grant 被 `RevokeSourceReadGrant` 撤销；④binding 与 grant scope/facts 不匹配；⑤publication gate pending；⑥binding 在 Run 中途被 sync 切换 —— 全部 typed（`SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED` → Run 面既有 `DB_FAILED`/`PROVIDER_FAILED` 投影），**零业务写**（region/revision/lineage 行数不变，`read_entry_bytes`/`source_lease` spy 0 次），且**不崩溃**。
  测试落点：`tests/fea11/test_source_run_grant.py`（参数化 6 例）；撤销语义可复用 `test_source_rendition_gates.py:286-321` 模板。
- [ ] **AC-G5（旧 managed 页零回归）**：managed-only Run 的 provider/guard 路径**不调用**新命令、不触碰 grant registry（探针 0 次）；`TargetSnapshot.metadata` 键集合不变；`pytest tests/fea11 tests/providers` 基线不减少。
  测试落点：`tests/fea11/test_source_rendition_source.py`（既有 managed 探针）+ 新用例；命令：`C:/Python314/python.exe -m pytest tests/fea11 tests/providers -q`。
- [ ] **AC-G6（Host 真实 IPC：铸造 + 绑定 + 读取）**：opt-in（`NEWMANGA_FEA11_IPC=1`）下，真实 Python Core：Host `IssueAsync` 铸 grant → 新命令建立绑定 → `resolve_page_resource`（同一授权面）成功发布 rendition，且 wire 出现该命令、无路径泄漏；无 grant / 撤销后 → typed。
  测试落点：新 `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs`（沿 `Fea09RealIpcTests.cs:19-150` 与 `Fea11SourceIpcTests.cs:144-192` 模板）。
  命令：`$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"`。
- [ ] **AC-G7（零漂移）**：scope diff ⊆ allowed_paths；`doc/plan`/`doc/contracts`（除 PREREQ-1 已冻结的 2 文件）/`src/infrastructure/sqlite/schema.py`/依赖文件/`apps/**`（超出 HOST-1 列出的 4 个文件）**零 diff**；Run wire 请求/响应字节不变（`StartRun`/`PrepareRun`/`AcceptRun` payload 键集与响应键集快照断言）；`CORE_PROTOCOL_MINOR` 仍为 3；`check.ps1` PASS、`verify_pins` 18/18、API inventory PASS。
  命令：`git diff --name-only`、`pytest`、`pwsh tools/governance/check.ps1`、`python tools/generate_api_inventory.py --check`。
- [ ] **AC-G8（判别性自检，独立复跑）**：至少 4 个破坏点各自使目标用例变红——①删新命令的 facts 校验；②删"写 grant→binding 映射"；③让 guard 回退到 `find_for_source`；④让撤销不生效。**由独立 reviewer 自行破坏至少 1 条复跑**（沿 RENDITION-1 A-3 裁决），证据入 `verification/**/logs/discrimination.log`。

---

## 8. Q5 测试可行性

### 8.1 Python 侧（可覆盖，成本低）

| 能力 | 现状 | 复用方式 |
|---|---|---|
| 真实 grant 铸造（签名/facts/session） | `tests/fea11/conftest.py:161-229`（`mint_grant`）+ `:82`（`registry` fixture） | 新测试直接用；**不要**改 conftest（属冻结测试面） |
| 真实源树/binding/entry | `conftest.py:242-333`（`add_referenced_page`/`add_source_tree`）、`tests/fea11/support/` | 同上 |
| 真实装配 + gate + guard + provider | `tests/fea11/test_source_rendition_gates.py:202-362`（`real_core`、`test_real_run_commit_guard_*`、`test_real_assembly_provider_reads_the_binding_rendition_end_to_end`） | 新测试复制同一 fixture 结构；**不得**用 `_StubImages` |
| Run 级执行模板 | `tests/fea11/test_source_rendition_run.py:131-280`（`RunHarness`，含与生产等价的 `run_source_guard`） | 新测试复用；**注意**它是"行为等价复刻"，真实装配 identity 由 gates.py 覆盖（R1-08 follow-up） |
| host-control 命令测试模板 | `tests/core/test_host_control.py:319-338`（host-only 参数化）、`:341-510`（session/revoke） | 新命令照抄模式 |
| 命令名 parity | `tests/fea11/test_source_command_parity.py:34`（`len(host)==14`） | 若新命令走 `SendHostControlAsync` 直连则**不触发**；若登记成 Host 命令则必须同步该断言 |

**结论**：Python 侧**完全可覆盖** AC-G2/G3/G4/G5（含真实装配与真实像素）。基线 `pytest tests/fea11` = **145 passed**（本 review 实测）；新增预计 15–30 例，增量门禁成本可忽略（fea11 全量约 9s）。

### 8.2 .NET 侧（可覆盖"铸造+绑定+授权"；Run 级真实 provider 端到端不可行）

| 能力 | 现状 | 判断 |
|---|---|---|
| 真实 Core stdio IPC + 真实 grant 铸造 | `Fea09RealIpcTests.cs:19-150`（import + `ResolvePageResourceAsync` + wire 断言 `RegisterSourceReadGrant`）；`Fea11SourceIpcTests.cs:144-192`（`IssueAsync` + `ScanSourceSync` 端到端）、`:194-...`（sync 链） | **可直接扩展**：新增 `Fea11RunGrantIpcTests` 跑"铸 → 新命令绑定 → resolve"，覆盖 AC-G6 |
| Run 级真实执行 | `Fea10RunIpcTests.cs:13-75`（Prepare/Accept/重放）说明 Run wire 可跑，但**不执行真实 provider**；`RunBindingFixTests` 用真实 Core 但断言 `PROVIDER_NOT_CONFIGURED` | **Run 级"读图+提交"在 .NET 内不可行**（需要真实 detector/OCR）。建议：Run 级像素/commit-guard 判别放 **Python 真实装配**（AC-G3/G4），.NET 只断言"授权建立 + resolve 同源读取"（同一 `find_bound_for_source` 面） |
| opt-in 门禁 | 三个真 IPC 类均需 `NEWMANGA_FEA09_IPC=1`/`NEWMANGA_FEA11_IPC=1`；默认 skip（本 review 实测 6 skipped） | 证据必须显式置环境变量并记录；不得用默认 skip 当"通过" |
| 单测面 | `SourceRegistryTests.cs`（registry 持久化/authorize）、`HostUnitTests.cs`、`GrantIssuerTests.cs`（多为 opt-in） | HOST 卡可加"授权委托在命令前被调用/异常时不 dispatch"的单测 |

### 8.3 全量门禁成本与已知 flaky

| 项 | 成本/基线 | 备注 |
|---|---|---|
| `pytest tests` | ~10 min；**3249 passed / 10 skipped**（RENDITION-1 closeout） | 本 review NOT_RUN；跑完必须 `git checkout -- verification/FEA-09`（本 review 已实测该副作用会追加一行） |
| `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | ~5 min；**1527 passed / 0 failed / 86 skipped** | Lead 基线轮出现 1 例 `library.db-shm` 锁冲突（§1），属**并发/临时目录争用**，非产品回归；复跑应以项目或解决方案单跑为准 |
| 已知 flaky | ①FEA-09 临时 DB 写竞争（`library.db-shm` 复制）；②`test_sandbox_job_kills_grandchildren`（R1-09 记录） | 命中时隔离复跑并在证据中说明，不得静默重试 |
| 定向（推荐门禁） | `pytest tests/fea11 tests/core/test_host_control.py`；`dotnet test ... --filter Fea11RunGrant` + `SourceRegistryTests` | 秒级到十余秒 |

---

## 9. Q6 风险 / limitation（逐条给判定）

| # | 风险 | 事实 | 判定 |
|---|---|---|---|
| **L-G1** | **grant ≤300s 生命周期 vs Run 时长** | Core 注册即拒 `expires_at > now+300`（`source_read_refs.py:164-166`）；`_checked` 逐次校验（`:568-569`）；书级 OCR/翻译 Run 常态超过 300s | **必须由 Lead 裁决**：①HOST 卡做"Run 存活期内定期重铸+重绑"（复杂度/内存/竞态↑）；②否则登记 limitation（窗口后提交单元 `DB_FAILED`，用户需重发 Run）。**不得**写成已解决 |
| **L-G2** | 加密 referenced 源（RENDITION-1 L-R2） | `claim_secret_for_binding` 要求 grant 的 `secret_ref` 且 scope 的 locator/ordinal 命中 binding（`source_read_refs.py:307-409`）；Host 为 zip 铸的 scope 只有容器（`IssueAsync` 的 `paths=[path]`），无法命中成员 locator/ordinal | **登记 limitation（本卡不解决）**：加密源 Run 仍 typed `SOURCE_PASSWORD_REQUIRED`，不崩溃；沿 L-R2 |
| **L-G3** | 混合页（RENDITION-1 L-R5） | provider 按 binding 读，旧门槛只在目标进入层；`_referenced_page_image` 已覆盖 | **登记引用**：本卡不改语义，AC-G5 只保证 managed 零回归 |
| **L-G4** | Run 中途撤销/失联 | 每个提交单元走 `source_commit_guard`（`pipeline.py:897-899`）→ 撤销/过期/EOF 下一页即 fail-closed；已提交单元保留（不声称原子） | **本卡解决（验证）**：AC-G4 覆盖；语义与 C-06 约束 10/11 一致 |
| **L-G5** | 多源 Run | Host 持有 `source_id→path`（`RegisterSourceScanTarget`），可为每个源铸 grant 并一次绑定多个 `grant_ids` | **本卡解决**：AC-G3 增加"两个源各一页"用例；注意 mint 成本 |
| **L-G6** | Run 中途 binding 被 sync 切换 | guard 用**当前** binding 查映射；新 binding 无映射 → typed fail-closed；已提交保留 | **本卡解决（验证）**：AC-G4 ⑥；与 L-R5/L-R11 不冲突 |
| **L-G7** | Host `_payloads`/`_grants` 无界增长 | `SourceReadCoordinator.cs:16,20,116-118` 从不剪枝（仅 secret grants 清理）→ 每 Run 一铸会无界增长 | **HOST 卡必须处理**（过期/撤销/完成后剪枝）或明确登记 follow-up；不得静默忽略 |
| **L-G8** | 铸造 I/O 成本 | `IssueAsync` 对容器整文件 SHA-256、folder 全量枚举逐文件哈希（`:63-81`） | **登记 limitation/设计注记**：Run 前铸造成本与源大小线性相关；可考虑复用 scan 已知 facts（需评估，不在本卡承诺） |
| **L-G9** | Core 重启 / 调度器自动恢复 pending Run | `core_service.py:1297-1301` 调度循环 `run_pending_once()`；`_bindings` 与 grants 均为 in-process，重启即空 | **登记 limitation**：referenced 页 Run 跨 Core 重启不可续跑（typed fail，用户重发）；不在本卡解决 |
| **L-G10** | L-R11 两读面 gate 不一致 | assembly `read_gate` 与 `resolve` 面 `_assert_source_sync_gate` 对"无 publication 行"判定不同（RENDITION-1 L-R11） | **另立 follow-up**（本卡 Out，不碰 `core_service` gate 语义） |
| **L-G11** | Host 无 DB 的 binding 信息缺口 | Host 只能给 `grant_ids + Run scope`，binding 解析必须在 Core（这正是 U-A 让 Core 做 scope 展开的原因） | **本卡解决（设计约束）**：命令**不得**要求 Host 提供 page→binding 映射 |
| **L-G12** | push / 18 pins 风险 | 实现卡若顺手改契约 → pin 漂移；push 需 DSH 授权 | **AC-G1/G7 强制**；本卡不 push；pins 只允许 PREREQ-1 改 2 项 |
| **L-G13** | 测试竞态 flaky | `library.db-shm` 锁（本次基线已命中）、`test_sandbox_job_kills_grandchildren` | **登记**：全量证据必须附复跑说明；不要与本次并发运行混跑 |

---

## 10. DSH 裁决要点（需要 Lead 决定什么）

1. **契约路径三选一**：①采用 §4.3 **U-A**（新 host-control 授权建立命令，需 C-06 v1.2 + C-16 v1.3 UNFREEZE）；②改判 **U-C**（Core 按签名 facts/scope 直接授权，零新命令，但重开 `FEA-09-impl-r1` R1-I002 且弱化 entry 级授权、需同步改 resolve 面）；③判 **BLOCKED** 并维持 L-R1。**本 review 推荐 ①。**
2. **300s 生命周期口径（L-G1）**：HOST 卡是否包含"Run 存活期定期重铸+重绑"？还是单 grant 语义 + 明确 limitation？这直接决定本卡能否宣称"产品级可用"。
3. **M2-C1 §5.7 是否同步**：仅文档一致性（D-2 已滞后）还是必须进 UNFREEZE 清单（影响 3 个文件/3 个 pin vs 2 个）。
4. **拆卡形态**：三卡（推荐）还是"CORE+HOST 合并、PREREQ 独立"；以及是否复用 `FEA-11-RUN-GRANT-1` 作为 HOST 卡、另建 `-PREREQ-1`/`-CORE-1`。
5. **绑定的命令覆盖面**：仅 `StartRun`，还是 `StartRun + ControlRun(continue/restart) + ResumeBlockedRun + RetryFailedTargets + AcceptRun`（凡是会触发步骤执行的命令）？本 review 建议**后者**，否则超时/恢复后的 Run 会 fail-closed。
6. **.NET 证据口径**：接受"resolve 级真实 IPC（同一授权面）+ Python Run 级真实装配"作为 AC-G6/G3 的分工，还是要求投入 fake-provider 测试设施做 .NET Run 级 E2E（成本明显更高）。
7. **L-G9（Core 重启不可续跑）**是否接受为 limitation；若不接受，需另立"Host 重绑/续跑"跟随卡。

---

## 11. 摘要

- **verdict：`READY-WITH-UNFREEZE`**（不是 `READY-TO-FREEZE`：占位卡"复用既有 wire、零契约"的目标不可达；也不是 `BLOCKED`：存在明确、可冻结、可测的最小路径）。
- **核心事实**：Host 能铸 grant（`SourceReadCoordinator.cs:44-122`），但 Core 的授权面是 in-process `_bindings`，生产者只有 import（`runtime.py:567-569`）与 sync apply（`sources/service.py:287,295-323`）；Run 命令不带 grant、host-control 闭集无授权建立命令、scan 铸而不绑 → 除 import/sync 后 ≤300s 窗口外，生产 referenced Run 必在 provider/commit guard 处 typed 失败（`core_assembly.py:1773`、`pipeline.py:897-899`）。
- **推荐最小变更**：新增一个 host-control 授权建立命令（Core 解析 Run scope → 校验 grant facts → 写映射），**不改 Run wire、不改 schema/依赖、不加错误码**；UNFREEZE 面 = C-06 + C-16（2/18 pins），独立 byte-level 复核 + 重冻。
- **纠正**：生产 Run 走 `StartRun`（minor 3），不是 `PrepareRun`/`AcceptRun`；`find_for_identity` 生产 0 调用、`find_for_source` 仅不可达回退分支；`source_list_scan_targets` 的 DTO 缺 version/entry，单独不足以支撑铸造可命中的 grant；Host 已知源路径（`RegisterSourceScanTarget`），真正的缺口是 Core 的绑定记录。
- **必须拆卡**：`PREREQ-1（UNFREEZE）→ CORE-1（命令+验证）→ HOST-1（铸造/绑定/刷新+接线）`；单卡时 UNFREEZE 必须写成前置门。
- **产品口径待裁**：300s grant 与长 Run（L-G1）、Core 重启不可续跑（L-G9）、.NET 证据分工。
- **本 review 实测**：HEAD `91d224b88` clean；pins 18/18；check PASS(3w)；`pytest tests/fea11` 145 passed；rendition 两文件 21 passed；Host 定向 4 passed/6 skipped；全量 pytest/.NET/API inventory 均 **NOT_RUN**。另已向 Lead 报告其 dotnet 基线 `EXIT=1` 的临时 DB 锁 flake（疑与并发定向测试争用）。

---

> **真实性声明**：本报告为 fresh 上下文独立只读审查，未参与 `FEA-11-RUN-GRANT-1` 或 `FEA-11-RENDITION-1` 的实现/返修；未修改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据（唯一一次文件变动是把测试副作用 `verification/FEA-09/logs/wire-redacted.ndjson` 恢复到 HEAD 字节）；未 `git add`/`commit`/`push`；未删除/移动任何文件；唯一写入是本报告 `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`。所有"实测"均有对应命令与结果记录，所有未执行项均标注 `NOT_RUN`。
