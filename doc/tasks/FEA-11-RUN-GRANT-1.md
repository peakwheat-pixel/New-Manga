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
base_commit: 116a711babe1fbb10ea94d77fd4961997462fd92
branch: null
worktree: null
integration_commit: null
delivery_head: null
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

## In（冻结）

### I-1 Core 授权建立命令（CORE）

| 项 | 内容 |
|---|---|
| 落点 | `src/bootstrap/core_service.py`（host-control 命令注册/分发、能力公告、handler）与 `src/infrastructure/resource_channel/source_read_refs.py`（`authorize_run_bindings` 等，复用 `_grants`/`_bindings`/`_checked`） |
| 命令 | `AuthorizeSourceReadForRun`（host-control envelope；请求 `{grant_ids, command, scope}` closed shape；响应 `{bound_pages, refused}`） |
| 语义 | 按 C-16 v1.3 §2.4 冻结：校验 grant live/expiry/revoked/session；用**与 Run 相同的 scope 展开器**解析目标页；对每个 healthy binding 按签名 scope 的 `source_id/version/entry(locator\|ordinal\|entry_key)` + facts 校验当前 binding/entry（`source_entries`/`source_locations`，**无路径回退**）；gate open 检查（C-17 §3.3）；refused 非空 → **零绑定写入**整体 typed 失败；成功 → 写进程内 grant→binding 映射（与 `bind_imported_entry` 同构） |
| 零副作用 | 零 DB 写、不建 plan/apply/journal、不发布资源、不延长 TTL、不撤销/复活 grant；幂等（重复调用同结果） |
| 能力 | `core.ping` capabilities 增加 `source.read.run/1`（additive；缺失不探测） |
| 错误 | 复用 C-16 §6 闭集；`details` 仅计数/ID；**不得**新增码 |
| 共享选择器 | 复用 Run 的 scope 展开逻辑（`_parse_run_scope`/`create_run` 的目标展开），**不得**另造第二套 target/page 解析；若必须抽取共享函数，仅限 `core_service.py` 内最小重构且保持既有 Run 行为字节等价 |

### I-2 Host 铸造/绑定/接线（HOST）

| 项 | 内容 |
|---|---|
| 落点 | `SourceReadCoordinator.cs`（新增 `AuthorizeRunAsync`/铸造编排 + 记账剪枝）、`HostRuntime.cs`（Run 前置授权编排、能力探测、源范围解析）、`HostCommandDispatcher.cs`（Run 命令前置委托；仅必要时） |
| 铸造 | 能力 `source.read.run/1` 存在 → 为 Run 相关源调用既有 `IssueAsync` 铸 grant（复用四维 scope/预算/签名；token 不落日志）；失败 → typed，不 dispatch |
| 绑定 | 调 `AuthorizeSourceReadForRun`（`SendHostControlAsync`）；成功（`refused` 空）→ dispatch；失败 → **不 dispatch**，返回该 typed code（R-5） |
| 覆盖 | `library_start_run`、`AcceptRun`、`ControlRun`（continue/restart）、`ResumeBlockedRun`、`RetryFailedTargets`（R-4）；只读命令不触发 |
| 源范围 | 优先 run 所属 project 过滤；否则全部已知源；无法解析 → typed（不静默放行） |
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

- [ ] **AC-R1 授权建立命令协议面**：host-only（普通面 → `HOST_ONLY_REQUIRED`）、session/credential 校验、closed shape/未知键/空或超限 grant_ids → `INVALID_REQUEST`、缺失 grant → `SOURCE_ACCESS_DENIED`、过期 → `SOURCE_GRANT_EXPIRED`、撤销 → `SOURCE_GRANT_REVOKED`；**全部零 DB 写**（业务表逐表快照相等）；幂等（同请求重复调用同结果）；能力 `source.read.run/1` 公告。证据：`pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py` 参数化用例。
- [ ] **AC-R2 真实装配 Run 端到端（判别核心）**：真实 production migrations 库 + 真实 zip/PNG + 真实 grant + `assemble_core_services`；经新命令绑定后 `create_run(page-scope)` 的 provider `page_frame` 像素/尺寸 = 当前 binding 的图（非 managed 旧图），`source_commit_guard` 通过，提交后 region/revision/lineage 行数符合预期；**判别性**：删「写绑定」→ provider `INVALID_INPUT`/commit typed 失败；绑定指错 entry → 仍 fail-closed。证据：`tests/fea11/test_source_run_grant.py` + `logs/discrimination.log`。
- [ ] **AC-R3 fail-closed 全覆盖**：①无 grant ②grant 过期（注入 clock）③撤销 ④scope/facts 不匹配 ⑤gate pending ⑥Run 中途 binding 被 sync 切换 → 全部 typed（Run 面既有 `DB_FAILED`/`PROVIDER_FAILED`/`TARGET_NOT_FOUND` 投影，不新增码）、**零业务写**（region/revision/lineage/保护/进度表不变，`read_entry_bytes`/`source_lease` spy 0 次）、不崩溃。证据：参数化 6 例。
- [ ] **AC-R4 Host 接线与生命周期**：`library_start_run`/`AcceptRun`/`ControlRun`(continue/restart)/`ResumeBlockedRun`/`RetryFailedTargets` 前置授权被调用；授权失败**不 dispatch** 且返回该 typed code（不新增 Run 面码）；能力缺失 → 跳过授权按现状 dispatch；`_payloads`/`_grants` 剪枝上界测试；真实 IPC（opt-in）铸造→绑定→resolve 成功、撤销后 typed、wire 无路径泄漏。证据：`Fea11RunGrantIpcTests.cs`（`NEWMANGA_FEA11_IPC=1` 实跑并记录）、`SourceRegistryTests.cs`。
- [ ] **AC-R5 managed 零回归**：managed-only Run 不调用新命令/不触碰 grant registry（探针 0 次）；`TargetSnapshot.metadata` 键集合不变；`pytest tests/fea11 tests/providers` 不减少（基线 fea11 145 + providers 559/4）。证据：探针用例 + 定向日志。
- [ ] **AC-R6 零漂移与门禁**：scope diff ⊆ allowed_paths；`doc/plan`/`doc/contracts`/`schema.py`/依赖/`apps/**`（超出 3 个 Host 文件）/`core_assembly.py` 零 diff；Run wire 请求/响应键集快照不变（`StartRun`/`PrepareRun`/`AcceptRun`）；`CORE_PROTOCOL_MINOR` 仍 3；全量 `pytest tests` **3249/10 不降**（跑后 `git checkout -- verification/FEA-09`）；全量 .NET **1532/0/86 不降**（跑后恢复 FEA-09；已知 flaky 首跑如实记录 + 隔离复跑）；`verify_pins.ps1` **18/18**；`check.ps1`（默认 + `-TaskPath`）PASS；`generate_api_inventory.py --check` PASS。证据：`logs/gates.log`、`scope-validation.log`、`changed-files.txt`。
- [ ] **AC-R7 证据/Handoff/不夸大**：EV 每文件 sha256 + commit；Resource Manifest 真实路径；Handoff 写明 L-G1/L-G2/L-G8/L-G9/L-G10 与未宣称项；独立 Review approved（P0/P1=0 或 findings 已处置）；卡面未写「全场景可用/  L-R1 全修」。

## 已知 limitation（预登记，closeout 必须保留）

- **L-G1（产品级）**：单 grant ≤300s；Run 超过窗口后的提交单元 fail-closed（typed），需重发 Run；定期重铸/重绑未实现（follow-up）。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）；沿 RENDITION-1 L-R2。
- **L-G3**：混合页语义沿 RENDITION-1 L-R5，不在本卡改。
- **L-G7**：Host 授权记账由本卡剪枝收口（若实测无法有界 → 停下报 DSH）。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希）；大库未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail，用户重发）。
- **L-G10**：L-R11（assembly `read_gate` 与 resolve 面 `_assert_source_sync_gate` 的「无 publication 行」判定不一致）另立 follow-up；本卡不碰该 gate 语义。
- **L-G11**：binding 解析必须在 Core（Host 不提供 page→binding 映射）；Host 只传 `grant_ids + command + scope`。
- **L-G13**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑，不静默重试。
- **未解决**：L-R1 在本卡后仅「窗口内可用」；不得表述为产品级全场景修复。

## 测试要求

| 场景/AC | 命令或步骤 | 前提/环境 | 预期 | 证据 |
|---|---|---|---|---|
| AC-R1/R2/R3/R5 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | 真实 migrations 库 + 真实 zip/PNG + 真实 grant | 全绿；破坏点变红 | `logs/feature.log`、`logs/discrimination.log` |
| AC-R4 .NET IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"` | 真实 Python Core | 铸造→绑定→resolve 成功；撤销后 typed | `logs/host-ipc.log` |
| AC-R4 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | 无 | 剪枝/钩子断言通过 | `logs/host-unit.log` |
| AC-R6 | `pytest tests`、`dotnet test NewManga.sln -c Release`、pins、check、API inventory、scope diff | 仓库根 | 不降/不漂移 | `logs/gates.log` 等 |
