---
id: FEA-11-RUN-GRANT-1
title: Run-scoped source-read 授权（Core 授权建立命令 + Host 铸造/绑定/接线；CORE+HOST 合并）
kind: implementation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；权威 scope review `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`（fresh subagent `f26b8cec…`，**READY-WITH-UNFREEZE**；U-A）；第二意见 `…-scope-r1-delta.md`（Codex `c3c100ae…`，一致，非权威）；DSH 2026-11-06 裁决（见「DSH 裁决」）：U-A 两阶段交付（PREREQ-1 契约 → 本卡 CORE+HOST 合并）；单 grant 300s 窗口 + L-G1；M2-C1 不改；.NET 证据分工；Host 授权失败不 dispatch 且不新增 Run 面错误码；L-G7 由本卡剪枝解决
suggested_owner: codex
owner: run-grant-impl
reviewer: 独立上下文 fresh subagent（未参与实现/返修；只读交付 head；session 见 `doc/reviews/FEA-11-RUN-GRANT-1-r1.md`）
depends_on:
  - FEA-11-RUN-GRANT-1-PREREQ-1
  - FEA-11-RENDITION-1
base_commit: 2067789ea
branch: null
worktree: null
integration_commit: null
delivery_head: a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-RUN-GRANT-1
allowed_paths:
  - doc/tasks/FEA-11-RUN-GRANT-1.md
  - doc/reviews/FEA-11-RUN-GRANT-1-r*.md
  - doc/handoffs/FEA-11-RUN-GRANT-1-*.md
  - verification/FEA-11-RUN-GRANT-1/**
  - src/infrastructure/resource_channel/source_read_refs.py
  - src/bootstrap/core_service.py
  - tests/core/test_host_control.py
  - tests/core/test_core_service.py
  - tests/fea09/test_referenced_wire.py
  - tests/fea11/test_source_run_grant.py
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs
out_of_scope:
  - UI/XAML/ViewModel/通知/本地化；`NewManga.App/**`（除非停下报 DSH 扩域）
  - 扫描/调度/watcher/删除/回收站/GC/备份；`schema.py` 与迁移
  - C-06/C-16/C-07/C-08/C-15/C-17/M2-C1/ADJ-001 字节（PREREQ-1 已冻结；实现卡不得改）；其余 16 pins
  - Run wire 字节/`CORE_PROTOCOL_MINOR`/新错误码；`core_assembly.py`（默认不列；若必须动，停下报 DSH）
  - 长 Run 定期重铸/重绑（L-G1 登记 limitation + follow-up）；加密 referenced Run（L-G2 limitation）；Core 重启续跑（L-G9 limitation）
  - 真实用户数据/AppData/外部卷/回收站；push
---

# FEA-11-RUN-GRANT-1：Run-scoped source-read 授权（CORE+HOST 合并）

> **状态：`ready`（依赖 `FEA-11-RUN-GRANT-1-PREREQ-1` done；PREREQ 未重冻前不得开工）。**
> 承接 `FEA-11-RENDITION-1` **L-R1**（生产 referenced 页 Run 在读图/提交被 typed 拒绝）。本卡交付「Core 授权建立命令 + Host 铸造/绑定/接线 + 真实装配判别测试」，**不承诺**长 Run/加密源/重启续跑（见 limitations）。

## 来源与依据

1. 权威 scope review：`doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`（**READY-WITH-UNFREEZE**；F1 缺口、U-A 最小变更、AC-G1…G8 草案、allowed_paths）。
2. 第二意见（存档、非权威）：`doc/reviews/FEA-11-RUN-GRANT-1-scope-r1-delta.md`（结论一致）。
3. 契约（PREREQ-1 冻结后）：C-16 v1.3 §2.4 `AuthorizeSourceReadForRun`、§0 能力 `source.read.run/1`；C-06 v1.2 §2.2 第三生产者语义；C-17 §3.3 publication gate；C-15 §4.1 `R(p,t)`；M2-C1 §5.5/§5.7（不改）。
4. 现状：`SourceReadCoordinator.IssueAsync` 可铸四维 grant（`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs:44-122`）；Core 授权面 `_bindings` 仅 import/sync 写入（`src/infrastructure/resource_channel/source_read_refs.py:411-440`、`src/application/importing/referenced/runtime.py:567-569`、`src/application/sources/service.py:287,295-323`）；生产 Run 路径 = `library_start_run → StartRun`（minor 3，`HostCommandRegistry.cs:284`、`HostCommandDispatcher.cs:415-423`、`src/bootstrap/core_service.py:5896-5923`）。

## DSH 裁决（2026-11-06，本卡执行口径）

| # | 裁决 | 内容 |
|---|---|---|
| R-1 | **合并实现** | CORE（命令+验证+Python 测试）与 HOST（铸造/绑定/接线+.NET 测试）合并为本卡；PREREQ-1 不可合并。 |
| R-2 | **300s（L-G1）** | 本卡保持单 grant ≤300s：Run 在窗口内正常工作；窗口后提交单元 fail-closed（typed `DB_FAILED`/`PROVIDER_FAILED`），**如实登记 L-G1 + follow-up**（定期重铸/重绑另卡）；**不得**宣称长 Run 可用。 |
| R-3 | **M2-C1** | 不改字节；HostControl 枚举滞后登记 follow-up（L-P1）。 |
| R-4 | **命令覆盖** | Host 必须在**所有会触发步骤执行的 Run 命令**前完成授权：`StartRun`（`library_start_run`）、`AcceptRun`、`ControlRun`（continue/restart）、`ResumeBlockedRun`、`RetryFailedTargets`；`GetRunSnapshot`/`GetTaskProjection` 等只读命令不授权。 |
| R-5 | **授权失败投影** | 授权失败 → **Host 不 dispatch**；返回授权命令自身 typed code（不重映射、不新增码、不进 `AllowedRunErrorCodes`；App 对未知码既有降级为 category=unknown/retryable=false 的行为不变）。若实现证明必须改 Run 面错误投影，停下报 DSH。 |
| R-6 | **能力缺失** | Core 无 `source.read.run/1` → 不铸 grant、**按现状 dispatch**（旧 Core 兼容；引用页仍 typed 失败）；不得用未知命令探测。 |
| R-7 | **源范围** | Host 为 Run 相关源铸造：优先按 Run 所属 project 过滤（若可解析），否则对 Host 已知全部源铸造并记录成本（L-G8）；**不得**要求 Host 提供 page→binding 映射（binding 解析在 Core）。 |
| R-8 | **L-G7 记账** | `_payloads`/`_grants` 必须有界：过期/撤销/绑定完成后剪枝（测试断言上界）；不得无界增长。 |
| R-9 | **.NET 证据** | 接受分工：Python 真实装配覆盖 Run 级像素/提交（AC-R2/R3/R5），.NET 真实 IPC 覆盖「铸造→绑定→resolve 同授权面」（AC-R4/AC-R6）；不要求 .NET Run 级 E2E。 |
| R-10 | **L-G9** | Core 重启后 referenced Run 不可续跑：登记 limitation；不在本卡解决。 |
| R-11 | **不夸大** | 卡面/Handoff/STATUS 不得写「referenced Run 全场景可用」「L-R1 全修」；只写窗口内可用 + limitations。 |
| R-12 | **允许扩域（2026-11-07，DSH 裁决）** | 能力 `source.read.run/1` 为冻结契约要求；`tests/core/test_core_service.py` 与 `tests/fea09/test_referenced_wire.py` 含 capabilities **精确等值**断言，必须把新能力加入期望列表（**additive，不删除/不弱化既有断言、不新增 skip**）。仅此 2 文件扩入 allowed_paths；其余扩域仍须停下报 DSH。 |

## In（冻结）

### I-1 Core 授权建立命令（CORE）

| 项 | 内容 |
|---|---|
| 落点 | `src/bootstrap/core_service.py`（host-control 命令注册/分发、能力公告、handler）与 `src/infrastructure/resource_channel/source_read_refs.py`（`authorize_run_bindings` 等，复用 `_grants`/`_bindings`/`_checked`） |
| 命令 | `AuthorizeSourceReadForRun`（host-control envelope；请求 `{grant_ids, command, scope}` closed shape；成功响应 `{bound_pages}`；任一目标页不可授权 → 整体 typed `SOURCE_ACCESS_DENIED`（details `{refused_pages}`），**不采用 `{bound_pages, refused}` 形态**） |
| 语义 | 按 C-16 v1.3 §2.4 冻结：校验 grant live/expiry/revoked/session；用**与 Run 相同的 scope 展开器**解析目标页；对每个 healthy binding 按签名 scope 的 `source_id/version/entry(locator\|ordinal\|entry_key)` + facts 校验当前 binding/entry（`source_entries`/`source_locations`，**无路径回退**）；gate open 检查（C-17 §3.3）；refused 非空 → **零绑定写入**整体 typed 失败；成功 → 写进程内 grant→binding 映射（与 `bind_imported_entry` 同构） |
| 零副作用 | 零 DB 写、不建 plan/apply/journal、不发布资源、不延长 TTL、不撤销/复活 grant；幂等（重复调用同结果） |
| 能力 | `core.ping` capabilities 增加 `source.read.run/1`（additive；缺失不探测） |
| 错误 | 复用 C-16 §6 闭集；`details` 仅计数/ID；**不得**新增码 |
| `grant_ids` 封闭形状 | 1..64 且**唯一**；重复 id 视为封闭形状违规 → `INVALID_REQUEST`（Review r1 R1-06 裁决：契约 §2.4 的「去重」解释为调用方必须去重）。 |
| 共享选择器 | 复用 Run 的 scope 展开逻辑（`_parse_run_scope`/`create_run` 的目标展开），**不得**另造第二套 target/page 解析；若必须抽取共享函数，仅限 `core_service.py` 内最小重构且保持既有 Run 行为字节等价 |

### I-2 Host 铸造/绑定/接线（HOST）

| 项 | 内容 |
|---|---|
| 落点 | `SourceReadCoordinator.cs`（新增 `AuthorizeRunAsync`/铸造编排 + 记账剪枝）、`HostRuntime.cs`（Run 前置授权编排、能力探测、源范围解析）、`HostCommandDispatcher.cs`（Run 命令前置委托；仅必要时） |
| 铸造 | 能力 `source.read.run/1` 存在 → 为 Run 相关源调用既有 `IssueAsync` 铸 grant（复用四维 scope/预算/签名；token 不落日志）。**Review r1 R1-01 / r2 R2-04 修订**：Host 侧铸造/能力/registry 失败 → **跳过该源（或整体跳过）并继续 dispatch**；仅 Core 对目标页的 typed 拒绝才阻断（R-5 不变）。 |
| 绑定 | 调 `AuthorizeSourceReadForRun`（`SendHostControlAsync`）；成功（`refused` 空）→ dispatch；失败 → **不 dispatch**，返回该 typed code（R-5） |
| 覆盖 | `library_start_run`、`AcceptRun`、`ControlRun`（continue/restart）、`ResumeBlockedRun`、`RetryFailedTargets`（R-4）；只读命令不触发 |
| 源范围 | 优先 run 所属 project 过滤；否则全部已知源。**Review r1 R1-04 / r2 R2-04 修订**：无法解析的已知源计为 unresolved 并**跳过**（不阻断无关 Run）；若 Run 含其 referenced 页，由 Core 对目标页 typed fail-closed。 |
| 记账 | `_payloads`/`_grants` 有界剪枝（过期/撤销/终态后清理），测试断言上界（R-8） |
| 兼容 | 能力缺失 → 跳过授权、按现状 dispatch；不得改变既有非 referenced Run 行为 |
| 错误面 | 不新增 Run 面错误码、不改 `AllowedRunErrorCodes`、不把 SOURCE_* 投影进 pipeline step（R-5） |

### I-3 测试与证据

- Python：`tests/core/test_host_control.py`（新命令 host-only/closed shape/session/typed 参数化）+ 新 `tests/fea11/test_source_run_grant.py`（真实装配 E2E、fail-closed 矩阵、managed 零回归、判别性破坏点）。
- .NET：新 `Fea11RunGrantIpcTests.cs`（opt-in `NEWMANGA_FEA11_IPC=1`：真实 Core 铸 grant → 新命令绑定 → `resolve_page_resource` 成功/撤销后 typed；wire 无路径泄漏）+ `SourceRegistryTests.cs` 增补（记账剪枝/命令前置钩子单测）。
- 证据：`verification/FEA-11-RUN-GRANT-1/**`（AC 矩阵、logs、discrimination、scope-validation、gates、Resource Manifest）。

### I-4 交付文档

- `doc/handoffs/FEA-11-RUN-GRANT-1-*.md`（固定 head、commit 链、门禁数字、limitations、未宣称项）。
- 卡面 AC 勾选 + `delivery_head` 回填（不改 status）。

## Out（明确不做）

- UI/XAML/ViewModel/通知/本地化；`NewManga.App/**`（除非停下报 DSH）。
- 扫描/调度/watcher/删除/回收站/GC/备份；`schema.py`/迁移；依赖。
- 契约字节（PREREQ-1 已冻结）；其余 16 pins；Run wire/`CORE_PROTOCOL_MINOR`/新错误码。
- 长 Run 定期重铸/重绑（L-G1 follow-up）；加密 referenced Run（L-G2）；Core 重启续跑（L-G9）；L-R11 两读面 gate 统一（L-G10 follow-up）。
- 真实用户数据/AppData/外部卷/回收站；push。

## Acceptance Criteria（v3；每条须有判别性测试）

- [x] **AC-R1 授权建立命令协议面**：host-only（普通面 → `HOST_ONLY_REQUIRED`）、session/credential 校验、closed shape/未知键/空或超限 grant_ids → `INVALID_REQUEST`、缺失 grant → `SOURCE_ACCESS_DENIED`、过期 → `SOURCE_GRANT_EXPIRED`、撤销 → `SOURCE_GRANT_REVOKED`；**全部零 DB 写**（业务表逐表快照相等）；幂等（同请求重复调用同结果）；能力 `source.read.run/1` 公告。证据：`pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` 参数化用例。 <<MET>>
- [x] **AC-R2 真实装配 Run 端到端（判别核心）**：真实 production migrations 库 + 真实 zip/PNG + 真实 grant + `assemble_core_services`；经新命令绑定后 `create_run(page-scope)` 的 provider `page_frame` 像素/尺寸 = 当前 binding 的图（非 managed 旧图），`source_commit_guard` 通过，提交后 region/revision/lineage 行数符合预期；**判别性**：删「写绑定」→ provider `INVALID_INPUT`/commit typed 失败；绑定指错 entry → 仍 fail-closed。证据：`tests/fea11/test_source_run_grant.py` + `logs/discrimination.log`。 <<MET>>
- [x] **AC-R3 fail-closed 全覆盖**：①无 grant ②grant 过期（注入 clock）③撤销 ④scope/facts 不匹配 ⑤gate pending ⑥Run 中途 binding 被 sync 切换 → 全部 typed（Run 面既有 `DB_FAILED`/`PROVIDER_FAILED`/`TARGET_NOT_FOUND` 投影，不新增码）、**零业务写**（region/revision/lineage/保护/进度表不变，`read_entry_bytes`/`source_lease` spy 0 次）、不崩溃。证据：参数化 6 例。 <<MET>>
- [x] **AC-R4 Host 接线与生命周期**：`library_start_run`/`AcceptRun`/`ControlRun`(continue/restart)/`ResumeBlockedRun`/`RetryFailedTargets` 前置授权被调用；授权失败**不 dispatch** 且返回该 typed code（不新增 Run 面码）；能力缺失 → 跳过授权按现状 dispatch；`_payloads`/`_grants` 剪枝上界测试；真实 IPC（opt-in）铸造→绑定→resolve 成功、撤销后 typed、wire 无路径泄漏。证据：`Fea11RunGrantIpcTests.cs`（`NEWMANGA_FEA11_IPC=1` 实跑并记录）、`SourceRegistryTests.cs`；**Review r2 增补**：能力缺失判别性用例（known 源非空 + 计数 authorize；删能力门即变红，判别点 B7）、`HostRuntime.AuthorizePreparedRunForAcceptAsync` 接线 seam（正常路径调用授权、缺失/过期 → `RUN_STALE_PREVIEW`；删接线即变红，B8）、folder kind 判别性用例（真实目录 → folder；删检测即变红，B9）与真实 folder 源 IPC（mint→绑定→resolve）。 <<MET>>
- [x] **AC-R5 managed 零回归（Review r1 修订口径，见「Review r1 处置」）**：①**Core 授权面**：managed 页被跳过（`bound_pages=0`、零映射、零 DB 写）；②**Host 预授权为 best-effort**：mint I/O 失败/能力缺失/无相关源 → **跳过该源或整体跳过，不得阻断 Core 本可接受的 Run**（managed-only Run 必须到达 dispatch，零行为变化；判别性测试覆盖「mint 失败仍 dispatch」）；③managed 页 provider 仍读 Managed Copy、`TargetSnapshot.metadata` 键集合不变；④全量套件不减少。证据：Core managed 用例（`test_managed_targets_are_skipped_not_refused`）+ Host best-effort 判别性测试（`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`；IPC 层 `mint failure -> best-effort skip` / `partial mint failure -> minted=1 bound=1 skipped=1`）+ 全量门禁（pytest 3281/10、.NET 见 EV）。Host 预授权失败不再阻断 Core 本可接受的 Run（R1-01 已修）。 <<MET>>
- [x] **AC-R6 零漂移与门禁**：scope diff ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`schema.py`/依赖/`apps/**`（超出 3 个 Host 文件）/`core_assembly.py` 零 diff；Run wire 请求/响应键集快照不变（`StartRun`/`PrepareRun`/`AcceptRun`）；`CORE_PROTOCOL_MINOR` 仍 3；全量 `pytest tests` **3249/10 不降**（跑后 `git checkout -- verification/FEA-09`）；全量 .NET **1532/0/86 不降**（跑后恢复 FEA-09；已知 flaky 首跑如实记录 + 隔离复跑）；`verify_pins.ps1` **18/18**；`check.ps1`（默认 + `-TaskPath`）PASS；`generate_api_inventory.py --check` PASS。证据：`logs/gates.log`、`scope-validation.log`、`changed-files.txt`。 <<MET>>
- [x] **AC-R7 证据/Handoff/不夸大**：EV 每文件 sha256 + commit；Resource Manifest 真实路径；Handoff 写明 L-G1/L-G2/L-G8/L-G9/L-G10/L-G12（含容器成员 entry 通道）与未宣称项；独立 Review **r1 changes_requested → findings 处置 → r2 窄面复审**（不得以 r1 未批准状态关闭）；卡面未写「全场景可用/ L-R1 全修」。 <<PARTIAL: R1 与 R2 findings 均已处置（见「Review r1/r2 处置记录」）；待独立 r3 窄面复审（Lead 指派）>>

## 已知 limitation（预登记，closeout 必须保留）

- **L-G1（产品级）**：单 grant ≤300s；Run 超过窗口后的提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑未实现（follow-up）。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）；沿 RENDITION-1 L-R2。
- **L-G3**：混合页语义沿 RENDITION-1 L-R5，不在本卡改。
- **L-G7**：Host 授权记账由本卡剪枝收口（若实测无法有界 → 停下报 DSH）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希）；大库未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail，用户重发）。
- **L-G10**：L-R11（assembly `read_gate` 与 resolve 面 `_assert_source_sync_gate` 的「无 publication 行」判定不一致）另立 follow-up；本卡不碰该 gate 语义。
- **L-G11**：binding 解析必须在 Core（Host 不提供 page→binding 映射）；Host 只传 `grant_ids + command + scope`。
- **L-G12（本卡实测新增；Review r1 扩写 / r2 修正，2026-11-07）Host→Core 源身份通道缺失**：①**version 通道**：`source_list_scan_targets` DTO 不含 `version_id`，寒启动枚举 `SourceScanTarget.Version` 固定 `"1"`，而 C-16 v1.3 §2.4 要求 `scope.version == binding.accepted_source_version`（Core `sv-…`）→ 生产 Host 铸出的 grant 通常 version 不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、Host 不 dispatch（fail-closed）。②**容器成员 entry 身份通道**：Host 对 zip/cbz/pdf 只铸**容器单 entry**（`locator=容器文件名`、`ordinal=0`），Core 按成员 `source_entries` 匹配 → **多成员归档只有 Core `ordinal=0` 那页可被授权**（.NET IPC p1 成功/p2 typed 拒绝即实证；该拒绝是 fail-closed、非越权）。**Review r2 R2-01 修正**：Host 侧 folder 识别曾按扩展名误判为 `image`（目录被当文件打开 → 整源跳过）；已修为「声明 kind 优先，否则 `Directory.Exists` → folder」，并新增**真实目录源 IPC 证据**（folder mint → Core 绑定 `bound_pages=1` → `resolve_page_resource` 成功）。因此当前可用边界 = **image 单 entry 源 + folder 源（逐成员 entry 匹配）+ zip/cbz/pdf 的归档首成员（ordinal=0）**；多成员容器其余页与 version 通道缺口仍不可用。缓解候选（另卡 `FEA-11-RUN-GRANT-2`，proposed）：①App/枚举路径传入 Core version；②Host 从 `ScanSourceSync` 结果缓存 `source.version_id`；③容器成员 locator/ordinal 通道；④契约层 facts-only 匹配（需 UNFREEZE）。**不得**表述为「referenced Run 全场景可用」。
- **L-G13**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑，不静默重试。
- **未解决**：L-R1 在本卡后仅「窗口内可用」；不得表述为产品级全场景修复。

## Review r1 处置（DSH 裁决，2026-11-07）

> Review=r1 `doc/reviews/FEA-11-RUN-GRANT-1-r1.md`（独立 fresh subagent `62c6bf16…`；changes_requested P0=0/P1=1/P2=3/P3=7；reviewed_head `7ff49f1cc`）。处置决定：**P1/P2 返修 + AC 口径修订；P3 随返修/文档处置**；修后 r2 窄面复审，r2 approved 前不得 closeout。

| Finding | 裁决 | 执行项（Owner） |
|---|---|---|
| **R1-01（P1）** AC-R5 Host 层 managed 零回归不成立 | **接受**：AC-R5 按「Core 授权面 + Host best-effort 不阻断」修订（见 AC-R5）；实现改为 **mint/能力/无源失败时跳过授权、不阻断 Run**（仅 Core 对目标页的 typed 拒绝才阻断，R-5）；补 Host 层「mint 失败仍 dispatch / managed-only Run 零行为变化」判别性测试 | 代码 + 测试 + AC-R5 证据 |
| **R1-02（P2）** AC-R4 证据覆盖不足 | **接受**：补 ①`library_control_run` pause/stop 不触发 ②能力缺失 → 跳过授权并 dispatch ③`AcceptRun` 前置授权（prepared slice） ④`RunSourceTargets` book 过滤/known=0/unresolved 分支；如某分支无可行判别性测试，登记 limitation 由 DSH 在 r2 裁决 | 测试 + 证据 |
| **R1-03（P2）** L-G12 不完整/口径过大 | **接受**：L-G12 扩写为「version 通道 + 容器成员 entry 身份通道」，可用边界收窄为 image/folder 单 entry + 归档首成员；修正 .NET IPC 测试注释/断言语义；register follow-up 候选 `FEA-11-RUN-GRANT-2`（proposed，不释放） | 文档 + 测试注释 + 卡面 |
| **R1-04（P2）** 预授权错误面不完整 | **接受**：mint I/O 异常映射为 §6 typed（`SOURCE_ENTRY_MISSING`/`FILE_IDENTITY_CHANGED`）；partial unresolved 语义与 R-7 一致（无法解析 → 视为该源不可授权；若 Run 含其 referenced 页则 Core 拒绝并阻断，否则跳过不阻断）+ 测试 | 代码 + 测试 |
| R1-05（P3）卡 I-1 响应形态 | 已修：成功 `{bound_pages}`、整体 typed 失败（本卡 I-1） | 卡面 |
| R1-06（P3）grant_ids 重复语义 | 裁决：重复 id **判 `INVALID_REQUEST`**（请求封闭形状：1..64 唯一）；契约「去重」按「调用方必须去重」解释，测试保持 | 卡面/测试注释 |
| R1-07（P3）`read_entry_bytes` spy / per-page gate 分支 | 补 `read_entry_bytes` spy（可行则补；否则在 EV 说明 `source_lease` 覆盖读取面）；per-page gate refused 分支用 mixed/legacy binding 覆盖（可行则补，否则登记 limitation） | 测试/证据 |
| R1-08（P3）host-only 零写口径 | AC-R1 证据口径改为「`total_changes` + 关键表逐表快照」并在测试注释说明；不弱化断言 | 测试注释/卡面 |
| R1-09（P3）EV 装配描述 | 修 EV 措辞（commit 行数用例为 RENDITION-1 同构 harness，非 `assemble_core_services`） | 证据 |
| R1-10（P3）Handoff「能力缺失有单测」不实 | 返修补测试或删表述；以实际为准 | Handoff |
| R1-11（P3）AcceptRun prepared-slice 行为变化 | 在 Handoff limitations 登记：`AcceptRunAsync` 需先同进程 `PrepareRunAsync`（否则 `RUN_STALE_PREVIEW`）；仓内 App 无调用点 | Handoff |

- **AC 修订记录**：AC-R5 由「managed-only Run 不调用新命令」修订为「Core 授权面 managed 跳过 + Host best-effort 不阻断（判别性测试）+ managed 读/metadata 零回归」；AC-R7 增加「r1→r2 复审链」与 L-G12 容器边界。其余 AC 不变。
- **不得**：以 r1 未批准状态 closeout；不得删/弱化既有断言；不得把 `SOURCE_*` 新增进 Run 面错误码。

## Review r1 处置记录（Owner 回填，2026-11-07；不含 r2 复审结论）

> 权威建议与裁决见 `doc/reviews/FEA-11-RUN-GRANT-1-r1.md` 与上方「Review r1 处置」。返修 commit 链：
> `04317256c`（Host best-effort + 错误面）、`3ffabeb81`（Host/Python 判别性测试；**delivery_head=`3ffabeb8134b355076a9e964305de895e7c5b9d1`**）、
> 证据/卡/Handoff 同批文档提交。

| Finding | 处置 | 证据 |
|---|---|---|
| **R1-01（P1）** | **FIXED**：抽出可单测的 `RunSourceAuthorizer`（best-effort 编排）——能力缺失/探测失败、无相关源、registry 不可读、mint I/O 失败（含部分源失败）全部**跳过并继续 dispatch**；只有 Core 对目标页的 typed 拒绝（`CoreOperationException`）才阻断（R-5 不变）。`SourceReadCoordinator.AuthorizeRunAsync` 改为逐源 best-effort 并返回 `RunAuthorizationResult(BoundPages, MintedGrants, SkippedSources, SkippedCodes)`；全源失败时不发命令。 | `SourceRegistryTests.RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`（mint 失败→SidecarException=到达 dispatch；Core 拒绝→code 原样且未 dispatch）、`RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`、`Fea11RunGrantIpcTests`（missing file / partial） |
| **R1-02（P2）** | **FIXED（4/4）**：①`RunCommandPolicy` pause/stop/abandon 不触发（dispatcher 仍调用钩子，钩子按策略返回）；②能力缺失/探测失败 → 不 mint 且不抛（继续 dispatch）；③`AcceptRun` 经 `PreparedRunSlices` 取冻结 command/scope 后调用 `AuthorizePreparedRunAsync`，缺失/过期 slice → `RUN_STALE_PREVIEW`；④`RunSourceRange` book 过滤 / known=0 / filtered=0 / unresolved 跳过全部有测试。 | `SourceRegistryTests` 新增 12 例（见 EV AC 矩阵）；`.NET IPC` 2 例 |
| **R1-03（P2）** | **FIXED（文档+测试语义）**：L-G12 扩写为「version 通道 + 容器成员 entry 身份通道」，边界收窄为 image/folder 单 entry + 归档首成员；.NET IPC 注释/断言改为「p1=首成员 ordinal 命中、p2=多成员容器限制 fail-closed」；Python entry 粒度用例注明测试侧成员形状非生产 Host-mintable；follow-up 候选 `FEA-11-RUN-GRANT-2`（proposed，不释放）。 | 卡 L-G12、Handoff §3、EV §7、`Fea11RunGrantIpcTests` 注释、`test_source_run_grant.py` docstring |
| **R1-04（P2）** | **FIXED**：mint I/O 异常映射 §6 typed（`SourceReadCoordinator.MapMintFailure`：file/access → `SOURCE_ENTRY_MISSING`、读写中 IO → `FILE_IDENTITY_CHANGED`、参数/路径 → `SOURCE_ACCESS_DENIED`）；partial unresolved 语义 = 跳过该源、由 Core 对目标页 fail-closed（Run 命中其 referenced 页 → typed 阻断；否则不阻断）。 | `SourceRegistryTests.RunSourceAuthorizerMapsMintIoFailuresToFrozenCodes`、`RunSourceRange...`、IPC `mint failure` / `partial` 断言 |
| **R1-05（P3）** | **已修（卡面）**：I-1 命令响应改为「成功 `{bound_pages}`；任一页不可授权 → 整体 typed `SOURCE_ACCESS_DENIED`（`refused_pages`），不采用 `{bound_pages, refused}`」 | 卡 I-1 |
| **R1-06（P3）** | **已修（裁决+注释）**：重复 id → `INVALID_REQUEST`（I-1 形状行 + 测试注释） | 卡 I-1、`tests/core/test_host_control.py` 注释 |
| **R1-07（P3）** | **FIXED**：`read_entry_bytes` spy 与 `source_lease` spy 双零断言；per-page `gate != open` 分支用 **mixed** binding 用例覆盖（pure referenced 页会先被 Run 展开器拒绝）。 | `test_authorization_never_leases_or_reads_the_source`、`test_per_page_gate_refusal_uses_the_shared_gate_predicate` |
| **R1-08（P3）** | **FIXED**：host-only/session 零写证据改为 `total_changes` + **业务表逐表快照**（与 AC-R1 文字一致，不弱化断言） | `tests/core/test_host_control.py::test_authorize_source_read_for_run_is_host_only_and_session_gated` |
| **R1-09（P3）** | **FIXED（EV）**：commit 行数用例描述改为「RENDITION-1 同构 harness（in-memory migrations + `build_run_harness`）」，不再称 `assemble_core_services` | EV §2/§4 |
| **R1-10（P3）** | **FIXED（测试+Handoff）**：补能力缺失跳过单测（见 R1-02②），Handoff 表述以实测为准 | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting` |
| **R1-11（P3）** | **FIXED（Handoff limitation）**：`AcceptRunAsync` 现在要求同 Host 进程内先 `PrepareRunAsync`（否则 `RUN_STALE_PREVIEW`）；仓内 App 无调用点，已登记 limitation | Handoff §3 |

- **AC 修订落实**：AC-R5 已按「Core 授权面 managed 跳过 + Host best-effort 不阻断 + managed 读/metadata 零回归」证据回填；
  AC-R6 门禁重跑；AC-R7 保留「待 r2 窄面复审」标记（复审由 Lead 指派，本回填不替代复审）。
- **未新增/未删除**：无新增 skip、无删除/弱化既有断言、无新 `SOURCE_*` 进入 Run 面错误码、无契约/schema/依赖/wire 改动。

## Review r2 处置记录（Owner 回填，2026-11-07；不含 r3 复审结论）

> 权威建议与裁决见 `doc/reviews/FEA-11-RUN-GRANT-1-r2.md`（P0=0/P1=0/P2=2/P3=2）与上方「Review r1 处置」。返修 commit 链：
> `9e1861ee0`（folder kind 检测 + AcceptRun 接线 seam）、`a11ded0d3`（folder/capability/AcceptRun 判别性测试；
> **delivery_head=`a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`**）、证据/卡/Handoff 同批文档提交。

| Finding | 处置 | 证据 |
|---|---|---|
| **R2-01（P2）** folder 边界不实 | **FIXED**：`RunSourceRange.KindOfSource` 改为「枚举声明 `SourceKind` 优先，否则 `Directory.Exists(normalized)` → `folder`，最后才按扩展名」；新增真实目录源 IPC 用例（真实 Core：folder mint 成功 → `bound_pages=1` → `resolve_page_resource` 成功）与 kind 判别单测；卡/Handoff/EV 的 L-G12 边界改为「image 单 entry + folder（逐成员匹配）+ 归档首成员」。 | `Fea11RunGrantIpcTests.FolderSourceMintsABindableGrantThroughTheProductionRange`、`SourceRegistryTests.RunSourceRangeKindDetectsFolderSources`、判别点 B9 |
| **R2-02（P2）** 能力缺失测试不判别 | **FIXED**：用例改为 known 源非空 + `entries` 非空 + 计数 authorize，经 `AuthorizeSliceAsync` 断言 0 次 mint 且不抛；新增 dispatcher 级「能力缺失仍到达 dispatch」断言；删除能力门 → 该用例变红（判别点 B7）。 | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`、`RunAuthorizerCapabilityMissingStillReachesDispatch`、B7 |
| **R2-03（P3）** AcceptRun 接线未测 | **FIXED**：抽出 `HostRuntime.AuthorizePreparedRunForAcceptAsync`（生产 `AcceptRunAsync` 直接委托），新增接线测试（正常路径用冻结 slice 调用 authorizer；缺失/过期 slice → `RUN_STALE_PREVIEW`；无 authorizer 仍先取 slice）；删授权调用 → 用例变红（判别点 B8）。 | `AcceptRunAuthorizationSeamUsesTheFrozenSlice`、`AcceptRunAuthorizationSeamIsTypedWithoutAUsableSlice`、B8 |
| **R2-04（P3）** 卡 I-2 / Manifest 旧口径 | **FIXED**：I-2「铸造」「源范围」两行改为 best-effort 权威口径；`RESOURCE-MANIFEST.json` 增加 `delivery_head` 字段并由生成器动态写入，worktree 资源 `source_path` 更新为新 delivery head。 | 卡 I-2、`RESOURCE-MANIFEST.json`（`delivery_head`/`source_path`） |
| R2-01 附带 | — | 无新增越权/越权放宽；folder grant 仍是整源授权 + 逐成员 facts 校验（未放宽匹配规则）。 |

- **AC 修订落实**：AC-R4 增补 r2 判别性证据（能力缺失/AcceptRun 接线）；AC-R7 保留「待 r3 窄面复审」标记（复审由 Lead 指派，本回填不替代复审）。
- **未新增/未删除**：无新增 skip、无删除/弱化既有断言、无新 `SOURCE_*` 进入 Run 面错误码、无契约/schema/依赖/wire 改动。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 预期 | 证据 |
|---|---|---|---|---|
| AC-R1/R2/R3/R5 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | 真实 migrations 库 + 真实 zip/PNG + 真实 grant | 全绿；破坏点变红 | `logs/feature.log`、`logs/discrimination.log` |
| AC-R4 .NET IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"` | 真实 Python Core | 铸造→绑定→resolve 成功；撤销后 typed | `logs/host-ipc.log` |
| AC-R4 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | 无 | 剪枝/钩子断言通过 | `logs/host-unit.log` |
| AC-R6 | `pytest tests`、`dotnet test NewManga.sln -c Release`、pins、check、API inventory、scope diff | 仓库根 | 不降/不漂移 | `logs/gates.log` 等 |

## 交付记录（Owner 回填；未改 `status`）

- **实现/测试 commit 链**（显式 pathspec，未 push；均在 `main`）：
  - `85eace738` — `feat(fea-11-run-grant-1)`: Core（`core_service.py` + `source_read_refs.py`）+ Host（`SourceReadCoordinator.cs` / `HostRuntime.cs` / `HostCommandDispatcher.cs`）
  - `7ff49f1cc` — `test(fea-11-run-grant-1)`: Python（`tests/core/test_host_control.py` 增补、`tests/fea11/test_source_run_grant.py` 新增）+ .NET（`Fea11RunGrantIpcTests.cs` 新增、`SourceRegistryTests.cs` 增补）+ R-12 的 2 个 capabilities 期望；**`delivery_head`**
  - 证据/卡面/Handoff 同批文档提交（`verification/FEA-11-RUN-GRANT-1/**`、本卡、`doc/handoffs/FEA-11-RUN-GRANT-1-7ff49f1cc.md`）
- **R-12 扩域（Lead 批准，`218775bca`）**：`tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py` 仅把 `source.read.run/1` additive 加入既有 capabilities 精确期望；未删除/弱化任何断言、未新增 skip。
- **门禁实测（`7ff49f1cc`）**：定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` → **49 passed**；全量 `pytest tests` → **3280 passed / 10 skipped**（卡基线 3249/10）；全量 `dotnet test NewManga.sln -c Release` → **1535 / 0 / 88**（卡基线 1532/0/86）；`NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` → **2 passed**；`verify_pins.ps1` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）**PASS**；`generate_api_inventory.py --check` **EXIT=0**；scope diff ⊆ `allowed_paths`（禁止面全空、`CORE_PROTOCOL_MINOR` 仍 3）；判别性 **5/5 破坏点变红 + 字节级恢复**。
- **未运行项**：无（上述门禁全部实跑）；已知 flaky/环境交互：全量 .NET 首跑 1 例 `FluentResidual2VisualEvidenceTests` 因运行时 `verification/` 工作树快照变化失败，恢复 FEA-09 tracked 字节 + 证据目录稳定后隔离复跑全绿（非产品缺陷，详见 Handoff §2）。
- **证据索引**：`verification/FEA-11-RUN-GRANT-1/EV.md`（每文件 sha256 + AC 矩阵）、`logs/feature.log`、`logs/host-ipc.log`、`logs/host-unit.log`、`logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates-governance.log`、`logs/discrimination.log`、`scope-validation.log`、`changed-files.txt`、`RESOURCE-MANIFEST.json`。
- **不夸大**：本卡交付「窗口内可用 + **image/folder 单 entry 源与归档首成员**（L-G12 边界）」；**不得**表述为「referenced Run 全场景可用」或「L-R1 全修」；L-G1/L-G2/L-G8/L-G9/L-G10/L-G11/**L-G12** 保留。独立 Review 由 Lead 指派（非实现者/非本会话）。

### Review r1 返修（2026-11-07）

- 返修 commit：`04317256c`（Host best-effort 编排 + typed 错误面 + `AuthorizeRunResult`/`PreparedRunSlices`/`RunSourceRange` 可测seam）、`3ffabeb81`（Host 单测 12 例 + IPC 断言更新 + Python 2 例/1 升级；**delivery_head=`3ffabeb8134b355076a9e964305de895e7c5b9d1`**）、证据/卡/Handoff 同批文档提交。
- 门禁重跑（`3ffabeb81`）：定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` → **50 passed**；Host 单测（SourceRegistry）→ **17 passed**；`NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` → **2 passed**；全量 `pytest tests` → **3281 passed / 10 skipped**；全量 `dotnet test NewManga.sln -c Release` → 见 EV §2（clean tree 隔离复跑）；pins/check/API inventory/scope 见 EV §2；判别性 **6/6 破坏点变红 + 字节级恢复**（新增 B6：删除 best-effort 跳过 → managed Run 被阻断的判别）。
- EV 重算每文件 sha256；L-G12 已扩写；R1-11 prepared-slice 行为已在 Handoff limitations 登记。
- **不夸大（不变）**：本卡交付「窗口内可用 + **image/folder 单 entry 源与归档首成员**（L-G12 边界）」；不得表述为「referenced Run 全场景可用」或「L-R1 全修」；待独立 r2 窄面复审后由 Lead closeout。

### Review r2 返修（2026-11-07）

- 返修 commit：`9e1861ee0`（folder kind 检测 + `AuthorizePreparedRunForAcceptAsync` 接线 seam）、`a11ded0d3`（Host 单测 17→21、IPC 2→3；**delivery_head=`a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`**）、证据/卡/Handoff 同批文档提交。
- 门禁重跑（`a11ded0d3`）：定向 `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` → **50 passed**；Host 单测（SourceRegistry）→ **21 passed**；`NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` → **3 passed**（新增真实 folder 源）；全量 `pytest tests` → **3281 passed / 10 skipped**；全量 `dotnet test NewManga.sln -c Release` → **1551 / 0 / 89**；pins **18/18**；check PASS；API inventory EXIT=0；scope **PASS（changed=31 全 ALLOWED）**；判别性 **9/9 破坏点变红 + 字节级恢复**（B7 能力门 / B8 AcceptRun 接线 / B9 folder 检测）。
- EV 重算每文件 sha256；Manifest 记录新 delivery head；L-G12 已按 folder 实证修正边界。
- **不夸大（不变）**：本卡交付「窗口内可用 + image 单 entry 源 + folder 源 + 归档首成员」；不得表述为「referenced Run 全场景可用」或「L-R1 全修」；待独立 r3 窄面复审后由 Lead closeout。
