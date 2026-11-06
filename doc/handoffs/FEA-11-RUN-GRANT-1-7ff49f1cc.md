---
task_id: FEA-11-RUN-GRANT-1
author: run-grant-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 2067789ea
delivery_head: 7ff49f1cc
status: in_review
---

# Handoff — FEA-11-RUN-GRANT-1（Run-scoped source-read 授权：Core 命令 + Host 铸造/绑定/接线）

- Task：`doc/tasks/FEA-11-RUN-GRANT-1.md`（Owner=`run-grant-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-06（Asia/Shanghai）
- 交付基线：卡 `base_commit=2067789ea`；实现自 `a94052ba7`（main 工作树）开始；**未 push、未创建 worktree**
- 交付实现 commit：`85eace738`（Core：`core_service.py` + `source_read_refs.py`；Host：`SourceReadCoordinator.cs` / `HostRuntime.cs` / `HostCommandDispatcher.cs`）、`7ff49f1cc`（测试：`tests/fea11/test_source_run_grant.py` 新增、`tests/core/test_host_control.py` 增补、.NET `Fea11RunGrantIpcTests.cs` 新增 + `SourceRegistryTests.cs` 增补、R-12 的 2 个 capabilities 期望；**`delivery_head`**）
- 证据/卡面/本 Handoff：`verification/FEA-11-RUN-GRANT-1/**` + `doc/tasks/FEA-11-RUN-GRANT-1.md` + 本文件（同批文档提交；`delivery_head` 只指向实现+测试提交，沿 RENDITION-1 先例）
- 环境：Windows 11 10.0.26300 / PowerShell 7 / CPython 3.14.6 / .NET（net9.0 测试目标）；无新依赖、无 schema/migration/契约/wire 改动
- 范围依据：冻结卡 `In`（I-1…I-4）与 DSH 裁决 R-1…R-11；权威 scope review `doc/reviews/FEA-11-RUN-GRANT-1-scope-r1.md`（READY-WITH-UNFREEZE，U-A）；契约 C-16 v1.3 §2.4/§0、C-06 v1.2 §2.2/§2.3（PREREQ-1 已重冻）
- **R-12 扩域（Lead 2026-11-06 批准，提交 `218775bca`）**：`core.ping` capabilities 追加 `source.read.run/1` 是冻结契约要求，而两处既有测试把 capabilities 写成精确等值 → 最小扩域 2 个测试文件（`tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`），只 additive 加入该字符串，未删除/弱化任何断言、未新增 skip。详见 §范围 与 `verification/FEA-11-RUN-GRANT-1/scope-validation.log`。

## 1. 交付结果（逐项对照 In / AC）

| 项 | 结果 | 交付内容 |
|---|---|---|
| **I-1** Core 授权建立命令 | 完成 | `src/bootstrap/core_service.py`：`_HOST_CONTROL_COMMANDS` 注册 `AuthorizeSourceReadForRun` + host-control 分发分支（普通 application 面 → `HOST_ONLY_REQUIRED`；session/credential → `HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）；handler `_authorize_source_read_for_run` 按冻结顺序 ①host-only ②closed shape `{grant_ids 1..64 唯一, command, scope}`（未知/缺键/类型错/空/超限 → `INVALID_REQUEST`）③每个 grant live（`_checked` 的 §6 优先级：缺失/会话不符 → `SOURCE_ACCESS_DENIED`、过期 → `SOURCE_GRANT_EXPIRED`、撤销 → `SOURCE_GRANT_REVOKED`）④**与 Run 同一** `_parse_run_scope` + 同一 target 展开器 `pipeline._catalog.expand(scope)`（失败 → `INVALID_REQUEST`，零映射）。能力列表追加 `source.read.run/1`（additive，`core.ping`）。 |
| **I-1** 授权建立语义（`source_read_refs.py`） | 完成 | 新增 `SourceReadGrantRegistry.RUN_GRANT_LIMIT=64`、`live_grant_scopes()`、`authorize_run_bindings()`：per-page = 无 binding（managed）→ 跳过；binding 非 healthy 或 publication gate 非 open（**沿用 Run 目标/commit guard 的同一 `read_gate` 谓词**，无 publication 行 = open）→ 不可授权；否则在 `grant_ids` 中找 live grant，签名 scope 的 `source_id`/`version` 匹配 binding，entry 满足 `entry_key==entry_id` / `locator` / `ordinal`，并核验 facts：容器源单 entry ↔ `source_locations`（四键全等）、folder 逐成员 facts ↔ `source_entries`（含 manifest 重算 + 总大小），**无路径回退**；任一页不可授权 → **整体 typed `SOURCE_ACCESS_DENIED`（`details={"refused_pages": n}`）且零映射写入**；全部可授权 → 写入与 `bind_imported_entry` 同构的进程内映射并返回 `{"bound_pages": n}`。零 DB 写、不建 plan/apply/journal、不发布资源、不延长 TTL、不撤销/复活 grant；幂等。 |
| **I-2** Host 铸造/绑定/接线 | 完成 | `SourceReadCoordinator.cs`：能力探测 `source.read.run/1`（`core.ping`，缓存）、`AuthorizeRunAsync`（对 Run 相关源调用**既有 `IssueAsync`** 铸 grant → `SendHostControlAsync("AuthorizeSourceReadForRun")`；Core typed 错误以 `CoreOperationException` 原样上抛）；**记账有界**（R-8/L-G7）：`_payloads`/`_grants`/`_expiries` 在过期/撤销/达上界时剪枝（`MaxTrackedPayloads=256`，`PruneExpired()`/`Track()` 有界断言）。`HostRuntime.cs`：能力缺失 → **不铸/不绑定、按现状 dispatch**（R-6）；Run 源范围（R-7）优先按 scope 的 `book_id` 过滤 Host 已知源，否则全部已知源；已知源无法解析 → typed 不静默放行；`AcceptRunAsync` 用 PrepareRun 时捕获的冻结 `{command, scope}` 前置授权。`HostCommandDispatcher.cs`：为**会触发步骤执行**的 Run 命令（`library_start_run`、`library_control_run` continue/restart、`library_resume_blocked_run`、`library_retry_failed_targets`，以及 `AcceptRun` 走同一 `AuthorizeRunSliceAsync`）加前置授权钩子；授权失败 → **不 dispatch**、返回授权自身 typed code（不新增 Run 面码、不改 `AllowedRunErrorCodes`）；只读命令不触发。 |
| **I-3** 测试与证据 | 完成 | Python：`tests/core/test_host_control.py`（+13 参数化用例：host-only/session/closed shape/§6 typed/零 DB 写/能力公告）+ 新 `tests/fea11/test_source_run_grant.py`（13 用例：真实 migrations 库 + 真实 zip/PNG + 真实签名 grant + `assemble_core_services`；Run 目标/provider 像素/commit guard/真实 commit 行数；fail-closed 6 类；managed 零回归）。.NET：新 `Fea11RunGrantIpcTests.cs`（opt-in `NEWMANGA_FEA11_IPC=1`，真实 Core 铸→绑定→resolve→撤销 typed、wire 无路径）+ `SourceRegistryTests.cs` 增补（剪枝上界/钩子不 dispatch/只读不触发）。证据：`verification/FEA-11-RUN-GRANT-1/**`（EV、Manifest、changed-files、scope-validation、logs 6 份、判别 5 破坏点）。 |
| **I-4** 交付文档 | 完成 | 本 Handoff + 卡面 AC 勾选/证据行/`delivery_head`（不改 `status`）。 |

### AC 判定

| AC | 判定 | 判据（摘要） |
|---|---|---|
| **AC-R1** | **MET** | host-only（普通面 `HOST_ONLY_REQUIRED`）、session/credential（`HOST_SESSION_INVALID`/`CORE_SESSION_MISMATCH`）、closed shape/未知键/空/65 项/重复 ID/非字符串/越域 command/region scope 与 page 命令 → `INVALID_REQUEST`；缺失 grant `SOURCE_ACCESS_DENIED`、过期 `SOURCE_GRANT_EXPIRED`、撤销 `SOURCE_GRANT_REVOKED`（全部 §6 category=authorization）；业务表逐表快照相等（零 DB 写）；错误 JSON 无 fixture 路径/credential 泄漏；同请求重复调用同结果（真实装配用例）；`core.ping` 公告 `source.read.run/1`。 |
| **AC-R2** | **MET** | 真实 production migrations 库 + 真实 zip/PNG + 真实 HMAC grant + `assemble_core_services`：经新命令绑定后 `create_run(page-scope)` targets 正确、provider `page_frame` 尺寸/像素 = 当前 binding 的B图（非 managed 旧图）、`source_commit_guard` 通过；real Run（RENDITION-1 同构真实 pipeline + 真实 store，经**生产 handler**授权）提交后 region/revision/lineage ≥1；判别性：无授权 → typed `INVALID_INPUT`/`PROVIDER_FAILED` 且 region/revision/lineage 0；绑定指错 entry / facts 不符 → typed 且零绑定（`logs/discrimination.log` B1/B2/B3）。 |
| **AC-R3** | **MET** | ①无 grant → `SOURCE_ACCESS_DENIED`；②过期（注入 clock）→ `SOURCE_GRANT_EXPIRED`；③撤销 → `SOURCE_GRANT_REVOKED`；④scope/facts 不匹配 → `SOURCE_ACCESS_DENIED{refused_pages:1}` 且零映射；⑤pending gate：Run 面 `TARGET_NOT_FOUND`（既有 family），授权面经同一 gate 的展开/逐页判定 typed 拒绝且零业务写；⑥Run 中途 binding 被 sync 切换到新 version → provider typed `INVALID_INPUT`、commit guard typed、region/revision/lineage 不变；授权命令全程 `source_lease` spy **0 次**（不读源字节）、不崩溃。 |
| **AC-R4** | **MET** | dispatcher 前置钩子在 4 个可分发 Run 命令上被调用、授权失败不 dispatch 且返回该 typed code、只读 Run 命令不触发（`SourceRegistryTests`）；`AcceptRun` 经同一 `AuthorizeRunSliceAsync`（HostRuntime 薄封装）；能力缺失 → 跳过授权按现状 dispatch（代码路径 + 单测）；`_payloads`/`_grants` 剪枝上界（`MaxTrackedPayloads`）与撤销/过期剪枝断言；真实 IPC（`NEWMANGA_FEA11_IPC=1`，实跑记录）铸造→绑定→`resolve_page_resource` 成功、他 entry typed 拒绝、撤销后 typed、wire/stderr 无 fixture 路径。 |
| **AC-R5** | **MET** | managed-only 页在授权面 `bound_pages=0`（跳过、不拒绝）、零 DB 写、`_bindings` 空；managed 页 provider 仍读 Managed Copy；`TargetSnapshot.metadata` 键集合不变（6 键：5+既有 `context_pages`）；全量 `pytest tests` **3280 passed / 10 skipped**（卡基线 3249/10，+31 = 本卡新增，未减少）、全量 .NET **1535 / 0 / 88**（基线 1532/0/86，+3 passed +2 opt-in skipped）。 |
| **AC-R6** | **MET** | scope diff ⊆ `allowed_paths`（含 R-12 的 2 个测试文件）；`doc/plan`/`doc/contracts`/`schema.py`/迁移/依赖/`core_assembly.py`/`NewManga.App/**`/其它 `apps/**` **零 diff**；Run wire 请求/响应字节未改、`CORE_PROTOCOL_MINOR` 仍 3；`verify_pins.ps1` **18/18 PASS**；`check.ps1`（默认 + `-TaskPath`）PASS；`generate_api_inventory.py --check` PASS。 |
| **AC-R7** | **MET** | EV 每文件 sha256 + commit；Resource Manifest 真实路径（仓外隔离根 461 文件聚合 sha256、零仓内删除）；Handoff 写明 L-G1/L-G2/L-G8/L-G9/L-G10/L-G11 与未宣称项；卡面未写「全场景可用/L-R1 全修」。**独立 Review 由 Lead 指派**（本 Handoff 未自审）。 |

## 2. 验证证据（实际命令 + 数字）

| AC/场景 | 命令 | 环境/被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| AC-R1/R2/R3/R5 定向 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | CPython 3.14.6 / Win11；`7ff49f1cc` | **PASS（49 passed：36 + 13）** | `logs/feature.log` |
| AC-R4 .NET IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"` | 同上；真实 Python Core（隔离 fixture 根） | **PASS（2 passed）** | `logs/host-ipc.log` |
| AC-R4 单测 | `dotnet test ... --filter "FullyQualifiedName~SourceRegistry"` | 同上 | **PASS（5 passed）** | `logs/host-unit.log` |
| AC-R6 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | 同上 | **PASS（3280 passed / 10 skipped）**；跑后 `git checkout -- verification/FEA-09` | `logs/full-pytest.log` |
| AC-R6 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | 同上；跑前工作树 clean | **PASS（1535 / 0 / 88）**；跑后 `git checkout -- verification/FEA-09` | `logs/full-dotnet.log` |
| AC-R6 治理 | `verify_pins.ps1`；`check.ps1`（默认 + `-TaskPath`）；`generate_api_inventory.py --check` | 仓库根 | **18/18 PASS**；**PASS(3 warnings)**；**PASS EXIT=0** | `logs/gates-governance.log` |
| AC-R6 范围 | `git diff --name-status a94052ba7..7ff49f1cc` + 禁止面零 diff 校验 | 同上 | **12 文件全部 ALLOWED；禁止面全空；minor=3** | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-RUN-GRANT-1/tools/discrimination.py`（破坏→跑目标用例→字节级恢复+sha 复核→重建） | 同上 | **5/5 变红（RED_AS_EXPECTED），5/5 字节级 RESTORED，final_rebuild exit 0** | `logs/discrimination.log` |

未运行项：无（上述门禁全部实跑）。已知 flaky：本卡交付期间全量 .NET 首跑出现 1 个**环境交互**失败 `NewManga.App.Tests.FluentResidual2VisualEvidenceTests.Captures_Residual2_Visual_Inventory_Only_When_Opted_In`——失败原因是该用例比较 `git status --porcelain -- verification` 前后快照，而当时 `verification/FEA-11-RUN-GRANT-1/` 恰在运行中新建（另有前一次全量 pytest 遗留的 FEA-09 tracked 字节未恢复）；`git checkout -- verification/FEA-09` + 证据目录稳定后**隔离复跑全量 .NET 全绿（1535/0/88）**，非产品缺陷（`logs/full-dotnet.log`）。全量 pytest 10 skipped 与 .NET 88 skipped 均为既有环境门控（无 provider 权重/GPU、sidecar/UI 集成 opt-in、本卡 2 个 `NEWMANGA_FEA11_IPC` 未设时跳过），本卡未新增 skip 条件。

## 3. 已知 limitation（预登记，closeout 必须保留）

- **L-G1（产品级）**：单 grant ≤300s（C-06/C-16 冻结）；Run 超过窗口后的提交单元 fail-closed（typed `DB_FAILED`/`PROVIDER_FAILED`），需重发 Run；定期重铸/重绑未实现（follow-up）。**不得**宣称长 Run 可用。
- **L-G2**：加密 referenced 源仍不可 Run（`SOURCE_PASSWORD_REQUIRED` typed，不崩溃）；沿 RENDITION-1 L-R2。
- **L-G8**：铸造 I/O 成本与源大小线性相关（容器整文件 SHA-256 / folder 全量哈希）；Host 每次 Run 前为源范围铸 grant（计数日志 `run source-read authorization sources=N bound_pages=M`），大库成本未标定。
- **L-G9**：Core 重启后 `_bindings`/grants 丢失，referenced Run 不可续跑（typed fail，用户重发）。
- **L-G10**：L-R11（assembly `read_gate` 与 resolve 面 `_assert_source_sync_gate` 的「无 publication 行」判定不一致）另立 follow-up；本卡不碰该 gate 语义。
- **L-G11**：binding 解析必须在 Core（Host 不提供 page→binding 映射）；Host 只传 `grant_ids + command + scope`。
- **L-G12（本卡实测新增，待 DSH 裁决/立项）**：Host 侧没有“Core source_id/version”通道——`source_list_scan_targets` DTO 只有 `source_id/registry_id/generation/source_kind/identity_digest/project_ids`（无 version_id），`SourceScanTarget.Version` 在寒启动枚举路径被固定为 `"1"`；而 Core 侧 §2.4 匹配要求 `scope.version == binding.accepted_source_version`（Core 生成的 `sv-…`）。因此**生产 Host** 用既有 `IssueAsync` 铸出的容器 grant 与真实 binding version 通常不匹配 → 授权 typed `SOURCE_ACCESS_DENIED`、Host 不 dispatch（fail-closed，不是静默放行；比 L-R1 的“跑到步骤才失败”更早、更明确）。本卡证据证明：**机制在 Core 级完整可用**（真实 grant/facts/entry 匹配），Host 接线在 Host 已知源携带正确 version 时可用（.NET IPC 用冻结 fixture 的 `s1`/`sv1` 实跑成功）；生产可用性受此 version 通道缺口限制。缓解候选（另卡）：①枚举 DTO/注册路径由 App 传入 Core version；②Host 从 `ScanSourceSync` 结果缓存 `source.version_id` 并在 Run 铸造时使用；③契约层允许 facts-only 匹配（需 UNFREEZE）。**不得**把本卡表述为「referenced Run 全场景可用」。
- **L-G13（沿卡）**：已知 flaky（`library.db-shm` 锁、`test_sandbox_job_kills_grandchildren`）——首跑失败如实记录 + 隔离复跑，不静默重试。
- **未解决**：L-R1 在本卡后仅“**窗口内可用 + Host 源范围/version 已知时可用**”；不得表述为产品级全场景修复。

## 4. 范围与授权

- 交付范围（`allowed_paths` + DSH R-12 扩域）：
  1. Core：`src/bootstrap/core_service.py`、`src/infrastructure/resource_channel/source_read_refs.py`
  2. Host：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs`、`apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs`、`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`
  3. 测试：`tests/core/test_host_control.py`、`tests/fea11/test_source_run_grant.py`、`apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11RunGrantIpcTests.cs`、`apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs`
  4. **R-12 扩域（Lead 批准）**：`tests/core/test_core_service.py`、`tests/fea09/test_referenced_wire.py`（仅 capabilities 期望 additive +1）
  5. 文档/证据：`doc/tasks/FEA-11-RUN-GRANT-1.md`、`doc/handoffs/FEA-11-RUN-GRANT-1-*.md`、`verification/FEA-11-RUN-GRANT-1/**`
- 未改：`STATUS`/`PLAN`/`TASK_LEDGER`、卡 `status`、任何契约字节（C-06/C-16/冻结记录）、`core_assembly.py`、`schema.py`/迁移/依赖、`NewManga.App/**`、其它任何文件（见 `scope-validation.log`：禁止面全空）。
- 提交方式：显式 pathspec（未用 `git add -A`）；**未 push**；未修改/回退他人未提交内容（交付开始工作树 clean，HEAD=`a94052ba7`）。

## 5. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；卡 base `2067789ea`，实现起点 `a94052ba7`，实现 head `85eace738`，**`delivery_head=7ff49f1cc`**（未 push、未建 worktree）。
- 复现（期望值）：
  1. `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` → **49 passed**
  2. `C:/Python314/python.exe -m pytest tests -q` → **3280 passed / 10 skipped**（跑后 `git checkout -- verification/FEA-09`）
  3. `$env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Fea11RunGrant"` → **2 passed**（不设 env 时 2 skipped）
  4. `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` → **1535 / 0 / 88**（跑后 `git checkout -- verification/FEA-09`）
  5. `pwsh -NoProfile -File tools/governance/verify_pins.ps1` → **PASS(18/18)**；`... check.ps1` → **PASS(3 warnings)**；`C:/Python314/python.exe tools/generate_api_inventory.py --check` → **EXIT=0**
  6. `Python verify：verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` → **PASS**；`discrimination.py` → **5/5 RED_AS_EXPECTED + 字节级恢复**
- 接收者下一步具体检查：①逐条核对卡面 AC 与测试名（`EV.md` AC 矩阵）；②以**独立上下文**运行 §5 命令并记录 session/来源；③复跑判别性脚本确认 5 个破坏点真变红且文件恢复；④重点复核 L-G12（Host version 通道缺口）的处置口径与“不夸大”边界；⑤Lead 判定 `integration_commit`/closeout，并决定 L-G12 follow-up 是否立项。

## 6. 下一任务建议

- Task ID / 标题：**无（本卡尚未 Review/集成，不释放后续实现卡）**；候选 follow-up：`FEA-11-RUN-GRANT-2`（Host Core source_id/version 通道：从 `ScanSourceSync` 结果缓存 `version_id` 或由 App 传入，解决 L-G12/L-G1 定期重铸）——由 Lead 决定是否立项，且必须在本卡 Review/集成后另行释放。
- 推荐 Agent / Reviewer：Reviewer 由 DSH 指派**独立上下文**（非本会话/非实现者；fresh subagent 或未参与实现的 ZCode/Codex）；实现 Owner 不自审。
- 推荐原因与前置依赖：L-G12 是本卡唯一“生产可用性”缺口，直接影响 referenced Run 能否在窗口内真正跑通；其前置是本卡集成完成（`_bindings` 第三生产者与 Host 接线）。
- Recovery point：`G:\CODEX\New Manga`，`main`；实现 head `7ff49f1cc`（未 push）；未创建 worktree；证据/卡/Handoff 同批文档提交在其后。
- 允许修改路径：本卡 `allowed_paths`（含 R-12 扩域的 2 个测试文件）不变。
- 禁止范围与新增授权条件：不得改 `STATUS`/`PLAN`/`TASK_LEDGER`、卡 `status`、契约字节、`core_assembly.py`、`schema.py`/迁移/依赖、`NewManga.App/**`；不得 `git add -A`；不 push；如需扩域先停下报 DSH。
