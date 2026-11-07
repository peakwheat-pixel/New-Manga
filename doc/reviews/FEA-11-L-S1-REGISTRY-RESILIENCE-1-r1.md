---
task: FEA-11-L-S1-REGISTRY-RESILIENCE-1
title: FEA-11-L-S1-REGISTRY-RESILIENCE-1 独立实现 Review r1（A：Registry 读取韧性；C-15 v1.5 §5）
reviewer: fresh subagent（独立上下文；未参与本卡实现/返修、未参与 RUN-GRANT 系列实现；只读）
session: 954a2ded-b8ed-4f8b-811b-e76e2d3d71ae
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b
reviewed_evidence_head: 89757f193d26bf7ba257a37766cbffea4c1b6617
verdict: approved
---

# FEA-11-L-S1-REGISTRY-RESILIENCE-1 独立实现 Review r1

> 审查对象：卡 `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`；契约 `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` **v1.5 §5**（pin `f9e376a0…`，载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C15.md`）；实现 `1ac8cc0b7`（`SourceAccessRegistry.cs`）+ 测试 `b56c5a0e6`（`SourceRegistryResilienceTests.cs`，delivery head）；证据/卡/Handoff `89757f193`。
> 事实口径：代码/测试以 `b56c5a0e6` 字节为准，卡/Handoff/证据以 `89757f193` 字节为准；`b56c5a0e6` 之后出现的 `6dd36aad7`/`0ebb234bf` 及其后的 L-S4 docs 提交不属于本卡。审查结束时工作树 HEAD 已被并发 L-S4 docs 推进（`4e8bda6e1`），但本卡 scoped 文件与证据相对上述两个 pin **零 diff**（已实测），故本报告仍对 `b56c5a0e6`/`89757f193` 有效。
> 本报告只读；未改实现/测试/证据/卡/契约；未 `git add/commit/push`。

## 0. 结论先行

**verdict：`approved`。P0 = 0 / P1 = 0 / P2 = 0 / P3 = 7（全部非阻断）。**

1. **安全核心已正确补位**：`Load()` 只保留文件级校验，逐根 identity 探针已移除；`Authorize()` 在**同一 `Locked()` 内、读盘之后**、按“请求路径所属注册根”**逐请求**调用 `VerifyRootIdentity`，失败在**任何 `Save` 之前**抛出 typed `SOURCE_REGISTRY_UNAVAILABLE`，无跨调用缓存、无 identity 回写、无自动重授权/恢复；缺失根不会被当作“无授权”放行。
2. **文件级损坏路径未放宽**：magic/长度/DPAPI/JSON/`format_version`/重复 id/generation/roots 结构校验，以及 `.corrupt-<utc>` 复制、不建空文件、不覆盖、整库 typed 失败全部保留；实现 diff 在 `Load` 内只删了 identity 两行并加注释。
3. **独立实跑全部符合预期**：build 0/0；`SourceRegistry` filter **40 passed / 0 failed / 1 skipped**；gated 真机 IPC **1 passed**（receipt 复现）；定向 pytest **74 passed**；自选 2 个破坏点均 **RED_AS_EXPECTED + 字节级 RESTORED + final rebuild EXIT 0**。
4. **证据/门禁一致**：EV 表内 sha256、Manifest 14/14 evidence 文件、仓外隔离根 33/33 文件聚合均复算一致；pins **18/18**（C15 `f9e376a0ed4c`）；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；scope 19 个变更文件全在 allowed_paths；`CORE_PROTOCOL_MINOR` 仍 **3**。
5. **保留的 P3（不影响批准）**：(a) 全量 pytest 的 3317 实际跑在“delivery HEAD + 同期 L-S4 未提交工作树”上，Handoff/EV 的“已提交”措辞与运行时刻不符（`+12` 归属 L-S4 正确）；(b) 卡面测试要求表引用了不存在的 `logs/regression.log`/`logs/gates.log`；(c) `SourceScanScheduler.cs:1568-1571` 注释过时（已登记 D-6）；(d) `Authorize` 对空 `paths` 无防御性拒绝；(e) 新增测试未覆盖 reparse 祖先负例（代码路径未改）；(f) `List` 未显式输出可用性字段（按“零新增字段 + 派生状态”口径可接受，B 卡解决展示）；(g) 多根条目 apply 会按整条目 roots 授权，缺失兄弟根会使该条目 apply 整体 typed 失败（保守，非回归）。

## 1. 审查基线

| 项 | 值 |
|---|---|
| 仓库/分支 | `G:\CODEX\New Manga` / `main` |
| 卡 | `FEA-11-L-S1-REGISTRY-RESILIENCE-1`（`base_commit=55306cb84`；实现起点 `db12dc5e5`） |
| reviewed head | `b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b`（实现 `1ac8cc0b7` + 测试 `b56c5a0e6`） |
| reviewed evidence head | `89757f193d26bf7ba257a37766cbffea4c1b6617`（卡/Handoff/EV/Manifest/logs/tools） |
| 审查时工作树 HEAD | 已被并发 L-S4 docs 推进（审查结束 `4e8bda6e1`）；本卡 scoped 文件/证据对上述 pin 零 diff（实测） |
| 契约 | C-15 **v1.5** §5（`doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md:293-318`；pin `f9e376a0ed4c…`） |
| 环境 | Windows 11 / .NET SDK（net9.0，Release）/ CPython 3.14.6；Windows 交互用户（真实 DPAPI） |
| 工作树卫生 | 审查开始/结束 `git status` 仅见 L-S4 的未跟踪/已提交 docs；本卡 scoped 文件 clean；FEA-09 已按快照逐字节恢复；仓外 task 隔离根恢复到 Manifest 的 33 文件聚合 |

**变更面（本卡自有 commit 集）**

```text
1ac8cc0b7  M apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs
b56c5a0e6  A apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryResilienceTests.cs
89757f193  A/M doc/tasks/...、doc/handoffs/...、verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/**
```

`SourceRegistryTests.cs` 本卡零 diff（既有 DPAPI/字节级/Reset 覆盖原样保留）。

## 2. A–F 逐项核对

### A. 契约 v1.5 一致性：**PASS**

- **`Load` 只做文件级校验**：`SourceAccessRegistry.cs:150-191` 的 magic/长度（`:157`）、DPAPI（`:160`）、JSON 长度/反序列化（`:164-167`）、`format_version`/重复 `registry_id`（`:168-170`）、`generation≥1`/`roots` 非空（`:173-174`）、root normalize + `Readable` 结构位（`:179`）全部保留；逐根 `SourceSecurity.Identity()` 比对已删除。`1ac8cc0b7` 的 diff 在该区域只删两行 identity 比对并加注释，**失败路径（`:184-190`）逐字未改**：`.corrupt-<utc>` 复制、原文件保留、不建空文件、`throw SOURCE_REGISTRY_UNAVAILABLE`。
- **根身份不可用的新语义**：`List()`（`:60`）返回全部条目；`Authorize()`（`:62-98`）对请求路径所属根逐请求核验；`VerifyRootIdentity()`（`:131-139`）只读探针，失败 typed 且不写回。契约 `:312`（文件级）与 `:313`（根级）逐条对应实现；恢复（`:314`）/撤销（`:315`）语义未动。
- **零 wire / 零持久字段**：`SourceAuthorization`/`SourceRoot`/`RegistrySnapshot` 记录形状未变；`format_version` 仍 1；无新错误码/命令/能力/schema/依赖；`List` 只加 XML 注释。C-16/C-17/`doc/contracts`/`schema.py` 在本卡 commit 集零 diff（见 §2.E）。
- **`List` 的“当前不可用呈现”**：实现采用“条目原样返回、不可用为派生状态、不新增持久字段”，与契约“不新增字段”及 PREREQ 载体 §6 的裁决一致；未在 `source_list_roots` 暴露 availability，属 B 卡展示面（见 R1-P3-06）。**不构成契约偏离**。

### B. 安全核心：**PASS**

- **同锁、读盘后、逐请求**：`Authorize` 全程在 `Locked()`（`:227-251`）内；`Load()`（`:64`）先读盘；`:85-93` 循环对每个 path 先 `Normalize`，用 `entry.Roots.FirstOrDefault(r => r.Readable && SourceSecurity.Contains(r.Root, path))` 定位**所属注册根**（无根 → `SOURCE_ACCESS_DENIED`），再 `VerifyRootIdentity(root)`；`Save` 在循环之后的 `:96`，任何失败都先抛异常，**零 registry 字节写**。
- **逐请求 & 无缓存**：`HashSet<string> verified` 是每次调用的局部量，同一调用内每根至多探针一次，**不跨调用缓存**；`RootIdentityIsReProbedOnEveryAuthorize`（先成功、再删根、第二次即 typed）正向钉住。
- **不可用/不匹配 → 该请求 typed 拒绝**：`VerifyRootIdentity` 的 `catch` 覆盖 `SourceSecurity.Identity` 的 exception（含缺失/不可读/reparse 祖先）→ `SOURCE_REGISTRY_UNAVAILABLE`；`identity.Volume/Id` 与登记不符同样该码（`:131-139`）。无新码。
- **缺失根 ≠ 无授权**：缺失根相关 path 走 containment 后探针失败 → typed，而不是 `SOURCE_ACCESS_DENIED` 或放行；`MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact` 覆盖根外/前缀兄弟/`..`/相对路径，全部精确拒绝。
- **containment/reparse 未放宽**：`SourceSecurity.Contains` 未改；`RejectReparseAncestors(path)` 仍在 `:92` 调用（只把顺序放在根探针之后，见下方 P3 与 §2.A）。对健康根，reparse 祖先仍 `SOURCE_ACCESS_DENIED`；对不可用根，typed 先于 reparse（旧实现下整库已不可读，无可观察放宽）。
- **无自动重建/重授权/恢复**：`VerifyRootIdentity` 只读；失败路径无 `Save`；`Register` 只在显式命令下追加；`Revoke`/`Reset` 语义未动；`ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity` 断言 registry 字节不变、持久化 volume/file id 仍为原（错误）值；`RevokeAndExplicitResetAreUnaffectedByAnUnavailableRoot` 断言撤销/显式 reset 不变。
- **其余根不受影响**：混合 registry 单测（`List`=2、健康根 mint 成功且只持久化自身 `last_used_at`、缺失根 typed 零写/无 `.corrupt-*`、`Register` 成功）与真机 IPC 均覆盖；`IssueAsync` 的三个 `Authorize` 调用点（`SourceReadCoordinator.cs:400,403,467`）与 apply（`HostOperationOrchestrator.cs:132,296`）全部走同一 `Authorize`，无旁路。
- **未发现 P0/P1/P2**：`VerifyRootIdentity` 对 `SourceSecurity.Identity(root.Root)` 的异常统一映射为 UNAVAILABLE；无身份回写；无自动路径；无 containment 回退。

### C. 独立实跑：**PASS**

| 场景 | 实际命令/步骤 | 实测结果 | 结论 |
|---|---|---|---|
| 构建 | `cd apps/desktop-avalonia; dotnet build NewManga.sln -c Release` | **成功 0 warning / 0 error**，`BUILD_EXIT=0`（增量 2.18s） | PASS |
| 定向 Host 单测 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"` | **40 passed / 0 failed / 1 skipped（41）**，`TEST_EXIT=0`（761ms） | PASS |
| gated 真机 IPC | `$env:NEWMANGA_FEA11_IPC=1; dotnet test ... --filter "FullyQualifiedName~Ipc_MixedRegistry"` | **1 passed / 0 / 0**，`IPC_EXIT=0`（644ms）；新 receipt：`source_list_roots=2`、`IssueAsync(healthy)=grant minted`、`IssueAsync(missing)=SOURCE_REGISTRY_UNAVAILABLE zero_write=1 no_corrupt_copy=1`、`source_register_root=registered`、`registry.List()=3` | PASS |
| 定向 Core 回归 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **74 passed**，1 warning，`PYTEST_EXIT=0`（7.21s） | PASS |
| 恢复后复核 | `dotnet test ... --no-build --filter "FullyQualifiedName~SourceRegistryResilience"` | **8 passed / 1 skipped**，`POST_RESTORE_EXIT=0` | PASS |
| 自选破坏点 ×2 | 见 §4 | 2/2 `RED_AS_EXPECTED` + 2/2 `RESTORED` + final rebuild EXIT 0 | PASS |

- **FEA-09 写入卫生（诚实披露）**：既有 `SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` 仍按原设计向 `verification/FEA-09/native-registry/<guid>/` 写隔离 fixture。本次跑 filter 产生了 1 个新的 GUID 目录（5 个文件）；我在运行前对 FEA-09 全目录做了 3699 文件 sha256 快照，运行后**只删除该新增 GUID 目录**并复核快照：**FEA-09 3699/3699 文件逐字节一致、`git status verification/FEA-09` clean**，未触碰既有字节。
- **仓外隔离根**：本次 gated IPC 在 `G:\CODEX\New Manga.workspace\FEA-11-L-S1-REGISTRY-RESILIENCE-1\fixtures\ipc-<guid>\` 新增一个 fixture 目录（含 receipt）；复核后将 reviewer 产物移到 `…-review-r1\` 并删除该新增 fixture，使 task 隔离根恢复为 Manifest 的 33 文件/聚合 `c3a46705…`（复算一致）。本次未手工创建 FEA-09 fixture；上述既有测试副作用是唯一写入，已按新增 GUID 删除并恢复；未触碰其他生产路径/用户数据。

### D. 证据/判别性：**PASS**

- **EV sha256 逐一复算**：EV §5.1/§5.2/§5.3 列出的实现/测试（2）、证据与工具（changed/scope + 8 logs + 3 tools = 13）、卡面/Handoff（2）全部与 `Get-FileHash` 一致（实现 `0b0d524a…`、测试 `cb0eee27…`、卡面 `c18a2a34…`、Handoff `22b902f6…`）。`EV.md` 自身不自我列入、Manifest 覆盖其 sha，属既定口径。
- **Manifest**：`canonical-evidence` 组 14/14 文件 sha256 与磁盘一致（含 `EV.md`，按生成规则排除 Manifest 自身）；`temp` 组 33/33 文件、逐 child 聚合/总数与磁盘一致；`discrimination/` 5 个 `.orig` 备份 sha 均等于实现交付 sha。
- **判别性**：`logs/discrimination.log` 记录 5/5 `RED_AS_EXPECTED` + 5/5 `RESTORED sha256=0b0d524a…` + `final_rebuild exit_code=0`；B1（恢复 Load 预探针）、B2（删除 Authorize 补位）、B3（缺失根当无授权）、B4（放宽文件级损坏）、B5（根外回退）与卡 AC-L1…L4 一一对应。我的独立 2 个破坏点复现了 B1/B2 的 RED 与字节级恢复（§4），未发现该日志夸大。
- **scope**：本卡自有 commit 集共 19 个变更路径，**全部 ALLOWED**（代码 2 + 卡/Handoff/证据 17）；`doc/plan/**`、`doc/contracts/**`、`src/**`（Python Core）、`tests/**`、schema/migrations、依赖、`NewManga.App/**`、`NewManga.CoreClient/**`、`STATUS/PLAN/TASK_LEDGER` 在 delivery commit 集全 `ZERO_DIFF`（我另以 `git diff --name-only db12dc5e5 b56c5a0e6 -- <surfaces>` 复核为空）。
- **协议**：`src/bootstrap/core_service.py:320` `PROTOCOL_MINOR = 3`；本卡无 `src` diff，`CORE_PROTOCOL_MINOR=3`。

### E. 零漂移/门禁：**PASS（含 1 个 P3 证据口径）**

| 门禁 | 实测 | 证据对照 |
|---|---|---|
| pins | `verify_pins.ps1` **18/18 PASS**；C15 `f9e376a0ed4c`；C16 `ad25fb3c89bb`；C17 `aefa0fa5b17e` | `logs/gates-governance.log` 同 |
| 治理 | `check.ps1`（默认）**PASS(3 warnings)**；`-TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md` **PASS(3 warnings)** | 同（10 非终态、STATUS 3119B、PLAN 6797B） |
| API inventory | `generate_api_inventory.py --check` **EXIT=0**（61 接口：54+6+1） | 同 |
| 全量 pytest | 证据日志 **3317 passed / 10 skipped**（262.47s，EXIT 0）；`+12` 属同期 L-S4，不属本卡 | 见下方 P3 口径 |
| 全量 .NET | 证据日志逐 assembly 汇总 **1570 passed / 0 failed / 92 skipped**（App 720/7、Host 223/61、CoreClient 167/24、ApplicationCore 31/0、DesignSystem 117/0、ThemeEngine 253/0、Presentation 38/0、Appearance 21/0；合计 1570/92） | `logs/full-dotnet.log` |
| scope | 19 路径全 allowed；禁止面零 diff；zero-drift 全空 | `scope-validation.log`/自算 |
| 工作树 | 跑后 FEA-09 恢复 `CLEAN`；当前 HEAD 仅被并发 L-S4 docs 推进，本卡 scoped 文件/证据零 diff | 实测 |

**全量 pytest 证据口径（P3，非阻断）**：`logs/full-pytest.log` 的 `repo_head=b56c5a0e6`、`generated_at_utc=2026-11-07T00:03:07Z`；而 L-S4 的 `6dd36aad7`/`0ebb234bf` 在 `2026-11-07 08:07:14/08:07:19 +0800`（= `00:07:14Z/00:07:19Z`）才提交。`b56c5a0e6` 的 Python 测试函数为 2665，HEAD（含 L-S4）为 2677（**+12**），而 full pytest 为 **3317 = 3305 + 12**——这 12 个新测试若缺少 L-S4 的 `src` 变更不会全绿。因此该次 3317 实际跑在“**delivery HEAD + 同期 L-S4 未提交工作树（至少 tests，且其 src 在 4 分钟后提交）**”，不是干净的 delivery-head 字节。`+12` 归属 L-S4 正确、本卡零 Python diff 也成立；但 Handoff/EV 的“**已提交**”措辞与“在 delivery head 跑全量 pytest”的隐含口径不准确，建议 closeout 改为“delivery HEAD + 同期 L-S4 工作树（后提交）/或在干净 head 重跑”。这不改变本卡 AC-L7 的“不降”结论（3305 基线 + 74 定向 + 零 Python diff 已足够判别），也不影响代码/测试交付。

### F. 不夸大：**PASS**

- 卡/Handoff/EV 均保留 **B（恢复/重授权入口不存在，`source_reset_registry`/`source_revoke_root` App 侧 0 调用）**、**C（`.corrupt-*` 无界复制未修）**、**`SOURCE_REGISTRY_UNAVAILABLE` 码义收窄**、**D-6（scheduler/watcher 可用性投影未改、`SourceScanScheduler.cs:1568-1571` 注释过时）**、**调度器级 mixed-registry 未覆盖**、**被替换根使用确定性“登记侧 identity 不匹配”夹具（非物理删除+重建）**、**`SourceRegistryTests.cs` 未改**。
- 全文未出现“恢复已可用/根级问题全解/L-R1 全修/调度器级混合矩阵已覆盖”等表述；明确写“不宣称”。
- 卡面 AC-L8 与实际文字一致；未把“条目级不可用”写成持久字段或自动恢复。

## 3. AC-L1…L8 判定

| AC | 判定 | 依据（独立复核） |
|---|---|---|
| **AC-L1 文件级损坏仍整库 fail-closed** | **MET** | `Load` 文件级校验与 `catch` 路径逐字保留（`SourceAccessRegistry.cs:157-181,184-190`）；`FileLevelCorruptionStaysWholeFileFailClosed` 12 例矩阵（短/截断/magic/length/JSON/format_version/重复 id/generation 0/空 roots/非规范 root/readable=false/**真实 DPAPI 篡改**）逐例断言原字节保留 + corrupt 副本 + `List`/`Authorize` typed；既有 `SourceRegistryTests.EncryptedPersistenceGenerationCorruptionAndExplicitReset` 在 40/0/1 中保持绿；判别 B4 已记录且我复核了其红线。 |
| **AC-L2 根级不可用不再整库不可读** | **MET** | `MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne`（2 条、root/generation 不变、`List` 零字节写、新 `Register` 成功）；`MixedRegistry_HealthyRootAuthorizeSucceedsAndOnlyPersistsItsLastUse`；`MissingRoot_AuthorizeIsTypedAndWritesNothing`（typed + 字节不变 + 无 `.corrupt-*`）；gated IPC 复跑 1 passed（`source_list_roots=2`、healthy mint、missing typed zero_write=1 no_corrupt_copy=1、register、`List=3`）；判别 B1。 |
| **AC-L3 授权期逐请求校验（安全核心）** | **MET** | `Authorize` 同 `Locked()`/读盘后/逐请求 `VerifyRootIdentity`（`:85-93,131-139`），失败先于 `Save`；`ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity`（typed、字节不变、持久化 volume/file id 保持原值）；`RootIdentityIsReProbedOnEveryAuthorize`（无跨调用缓存）；`MissingRoot_NeverAuthorizesAnyPathAndContainmentStaysExact`（根外/前缀/`..`/相对路径均 DENIED）；判别 B2/B3/B5；我独立复跑 B2 的“删除补位 → 被替换根重新授权”RED。 |
| **AC-L4 不自动重建/恢复/重授权** | **MET** | `VerifyRootIdentity` 只读、失败零 `Save`；`ReplacedRoot_*` 断言 registry 字节与持久 identity 不变；`RevokeAndExplicitResetAreUnaffectedByAnUnavailableRoot`（generation+1/`revoked_at`；`Reset(false)`→`INVALID_REQUEST`、`Reset(true)`→quarantine+空库）；无自动重注册代码路径。 |
| **AC-L5 错误码/语义零新** | **MET** | 仅复用 `SOURCE_REGISTRY_UNAVAILABLE`；无新码/命令/字段/能力/schema/依赖；`doc/plan`/`doc/contracts`/`schema.py`/migrations/`NewManga.App/**`/`NewManga.CoreClient/**` 在 delivery commit 集零 diff；pins 18/18；API EXIT=0。 |
| **AC-L6 测试/证据** | **MET** | 8 个新单测 + 1 条 gated IPC（40/0/1；IPC 1/0/0）；`discrimination.log` 5/5 RED + 5/5 RESTORED + final rebuild 0；EV 全表 sha256 复算一致；Manifest 14/14 evidence + 33/33 仓外资源；Handoff 存在且数字一致。 |
| **AC-L7 零漂移/门禁** | **MET（带 P3 证据口径）** | pins 18/18、check PASS(3w)×2、API EXIT=0、scope 19 全 allowed/禁止面零 diff、`CORE_PROTOCOL_MINOR=3`、FEA-09 恢复 CLEAN；全量 pytest 3317/10 与 .NET 1570/0/92 数字和日志一致（`.NET` 逐 assembly 汇总核对）；全量 pytest 的“已提交/干净 delivery head”措辞需按 §2.E 修正，不影响本卡零 Python diff 与 74 定向通过。 |
| **AC-L8 不夸大** | **MET** | B/C/码义/D-6/调度器未覆盖/确定性替换夹具等 limitation 全部保留；无“恢复已可用/根级问题全解/L-R1 全修/调度器级混合矩阵已覆盖”表述；未把派生不可用写成持久状态。 |

## 4. 破坏性复跑记录（独立）

**方法**：以 `b56c5a0e6` 的交付字节 `SourceAccessRegistry.cs`（sha256 `0b0d524ae52cfdc13f5622defd118fe922fd91a041e3cef21cd241044f1b4de3`）为基线；每次只改一处，`dotnet build tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release` 后跑**一个**目标用例，要求 exit≠0；随后按原字节写回、sha256 复核，最后重建 solution。脚本与日志在仓外 reviewer 隔离目录 `G:\CODEX\New Manga.workspace\FEA-11-L-S1-REGISTRY-RESILIENCE-1-review-r1\`（不属于交付证据）。

| 破坏点 | 改动 | 目标用例 | 实测 | 恢复 |
|---|---|---|---|---|
| **R1-B1** | 在 `Load` 的 root 结构校验后恢复 `SourceSecurity.Identity(root.Root)` + volume/file id 比对（单根缺失再次整库判损坏） | `FullyQualifiedName~MixedRegistry_ListReturnsEveryEntryIncludingTheUnavailableOne` | `target_test_exit=1`，**RED_AS_EXPECTED** | `RESTORED`，sha256 `0b0d524a…` |
| **R1-B2** | 删除 `Authorize` 的 `if (verified.Add(root.Root)) VerifyRootIdentity(root);`（只删 Load、不补 Authorize） | `FullyQualifiedName~ReplacedRoot_AuthorizeIsTypedAndPersistsNoNewIdentity` | `target_test_exit=1`，**RED_AS_EXPECTED**（被替换根未再被拒绝） | `RESTORED`，sha256 `0b0d524a…` |

- 两次 break build 均 `EXIT=0`，目标测试均 exit 1；恢复后 `final_rebuild_exit=0`；恢复后 `SourceRegistryResilience` 复跑 **8 passed / 1 skipped**。
- **未复跑** Owner 的其余 3 个破坏点（B3/B4/B5）；`logs/discrimination.log` 的 5/5 记录与代码路径一致，我复核了 B1/B2 的可判别性，并确认 B4/B5 的断言语义（文件级放宽 → `FileLevelCorruption...` 红；根外回退 → containment 用例红）。

## 5. Findings

| ID | 级别 | 位置 | 事实与影响 | 复现/证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R1-P3-01 | **P3** | `doc/handoffs/...-b56c5a0e6.md:31,58`；`EV.md:41`；`logs/full-pytest.log:3` | full pytest 3317 跑在“delivery HEAD + 同期 L-S4 未提交工作树”，Handoff/EV 称 `+12` 来自 L-S4“已提交”测试，运行时刻表述不准确；`+12` 归属 L-S4 正确、本卡零 Python diff 仍成立，AC-L7 不降结论不变。 | full-pytest `repo_head=b56c5a0e6`、`generated_at=00:03:07Z`；L-S4 commit `6dd36aad7`/`0ebb234bf` 时间 `00:07:14Z/00:07:19Z`；`b56c5a0e6`/HEAD 测试函数 2665/2677（+12）；full pytest 3317=3305+12 | closeout 将措辞改为“delivery HEAD + 同期 L-S4 工作树（后提交）”，或在干净 `b56c5a0e6` 重跑（预期 3305/10）；不需要改实现/测试 | open（非阻断） |
| R1-P3-02 | **P3** | `doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md:80-83` | 卡面“测试要求”表引用 `logs/regression.log`、`logs/gates.log`；证据目录实际为 `feature.log`/`host-unit.log`/`gates-governance.log`/`full-*.log`（目录共 15 文件：EV/Manifest/changed/scope + 8 logs + 3 tools）。不影响 AC（Handoff/EV 使用实际文件名），但会误导复现。 | 证据目录 15 文件清单（§2.C/§2.D） | 卡面改为实际日志名，或标注“占位名，以 Handoff/EV 为准” | open（非阻断） |
| R1-P3-03 | **P3** | `SourceScanScheduler.cs:1568-1571` | 注释仍写“missing/replaced production file-root makes the persistent registry unreadable as a whole”，与 v1.5 后 List 可用、target 级 typed 的行为不符。Handoff §3 已登记；行为本身由既有 scheduler 单目标用例保持绿。 | `VerifyEnumeratedTarget`（`:1564-1630`）实测仍对 cold-start 缺失/替换返回 `Error(SOURCE_REGISTRY_UNAVAILABLE)`；`SourceScanSchedulerTests:1178,1200` 保持绿（全量 .NET 证据） | 随 D-6/维护卡更新注释；不要在本卡扩写域 | open（非阻断） |
| R1-P3-04 | **P3** | `SourceAccessRegistry.cs:85-96` | `Authorize(registryId, generation, [])` 会跳过所有根探针并 `Save` `last_used_at` 后成功返回。当前所有调用点（`SourceReadCoordinator.cs:400,403,467`、`HostOperationOrchestrator.cs:132,296`）均传非空数组，无现实利用；属防御性 API 缺口。 | 代码走查；三个 Authorize 调用点输入非空（HostOperationOrchestrator 在 `:126-131` 显式拒绝空 roots） | 可加 `if (paths.Count == 0) throw INVALID_REQUEST;`（需另卡/测试） | open（非阻断） |
| R1-P3-05 | **P3** | `SourceRegistryResilienceTests.cs:124-155`；`SourceAccessRegistry.cs:92` | AC-L3 的 reparse 祖先负例未被新增测试覆盖；代码仍调用 `RejectReparseAncestors(path)`，行为未放宽，但若后续删掉该调用，现有用例不会变红。 | 只有 D4/Tile 测试覆盖 reparse；新测试覆盖 outside/prefix/`..`/relative，未含 reparse | 在 D-6/B 或后续维护卡补一条 reparse 负例（不扩本卡写域） | open（非阻断） |
| R1-P3-06 | **P3** | `SourceAccessRegistry.cs:54-60`；`SourceReadCoordinator.cs:622` | `List` 返回条目原样，不显式标记“当前不可用”；`source_list_roots` 也无 availability 字段。契约/PREREQ 明确“不新增字段、派生状态”，B 卡负责展示；因此不构成 AC-L2 偏离，但对“呈现”一词需按派生语义理解。 | AC-L2 证据只要求 List 可用/其余根不受影响；B limitation 保留 | closeout 文案明确“派生状态、无字段”；展示归 B | open（非阻断） |
| R1-P3-07 | **P3** | `HostOperationOrchestrator.cs:112,122-132`（以及 `:286-296`） | apply/journal 对条目把**全部** `Roots` 传给 `Authorize`；多根条目中一个根不可用时，该条目 apply 会整体 typed 失败（即使目标路径属于健康根）。这是保守的 all-or-nothing，不是安全回归（旧实现整库失败），但与“其余根不受影响”的直觉有差异。 | 代码走查；单测/混合 IPC 使用不同条目，未覆盖同条目多根 | 记录到 D-6/B；若要求条目内逐根可用性，另卡改调用面 | open（非阻断） |

**在记录范围内未发现 P0/P1/P2。** 上表 P3 均非阻断，不要求返修实现/测试；R1-P3-01/02/03/06 为文档/证据口径，R1-P3-04/05/07 为后续加固项。

## 6. 最终 verdict

**`approved`**（对 `reviewed_head=b56c5a0e6` + evidence head `89757f193`）。

- 安全核心（AC-L3）、文件级 fail-closed（AC-L1）、根级可用性（AC-L2）、无自动恢复（AC-L4）、零 wire/码（AC-L5）、测试/判别性/证据（AC-L6）、门禁（AC-L7）、不夸大（AC-L8）均成立；P0/P1/P2=0。
- P3 只要求 closeout 措辞/后续卡登记；不阻断集成。若 Lead 选择在干净 `b56c5a0e6` 重跑 full pytest，预期 3305/10（+12 归 L-S4），并在证据/Handoff 注明，可进一步消除 R1-P3-01。
- 本报告不构成集成授权、不替 DSH 处置 findings；closeout/status/集成由 Lead/DSH 维护。

## 7. 真实性声明

1. 本报告由 **fresh 上下文 subagent** 产出（session `954a2ded-b8ed-4f8b-811b-e76e2d3d71ae`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）；**未参与**本卡实现/返修，也未参与 RUN-GRANT 系列实现；全程只读，仅在仓库新增本报告文件。
2. 事实来源：`b56c5a0e6` 的实现/测试字节、`89757f193` 的卡/Handoff/证据字节；代码行号与契约行号均按该两 pin；未用 Handoff/卡面自述替代代码事实。
3. **实际执行**：`git` 只读检查；`dotnet build NewManga.sln -c Release`（0/0）；`dotnet test ... --filter "FullyQualifiedName~SourceRegistry"`（40/0/1）；`NEWMANGA_FEA11_IPC=1 ... --filter "FullyQualifiedName~Ipc_MixedRegistry"`（1 passed）；`pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`（74 passed）；`verify_pins.ps1`（18/18）；`check.ps1` 默认与 `-TaskPath`（PASS 3 warnings）；`generate_api_inventory.py --check`（EXIT 0）；2 个自选破坏点 + 恢复 + final rebuild（§4）；EV/Manifest/FEA-09 逐文件 sha256 复算。
4. **NOT_RUN（不写 PASS）**：独立重跑全量 `pytest tests` 与全量 `dotnet test apps/desktop-avalonia/NewManga.sln`（Lead 证据日志已核数字与汇总；因共享工作树正被并发 L-S4 会话使用，本次不并发重跑）；Owner 的 B3/B4/B5 破坏点（日志已核，B1/B2 独立复现）。本报告未把未跑项写成实测 PASS。
5. **写入/恢复声明**：除本报告外，仓库 tracked 字节最终零 diff；FEA-09 的既有测试副作用产生 1 个新 GUID fixture，我在删除前对 FEA-09 全目录做 3699 文件 sha256 快照，仅删除该新目录后复核**逐字节一致**；仓外 task 隔离根恢复到 Manifest 的 33 文件聚合；reviewer 脚本/日志放在 `G:\CODEX\New Manga.workspace\FEA-11-L-S1-REGISTRY-RESILIENCE-1-review-r1\`，不写入 canonical evidence。未执行 `git add/commit/push`。
6. 审查期间共享工作树 HEAD 被并发 L-S4 docs 推进（审查结束 `4e8bda6e1`）；本卡 scoped 文件与证据对 `b56c5a0e6`/`89757f193` 零 diff，已实测；并发会话的提交/未提交内容不被本报告作为本卡事实。
