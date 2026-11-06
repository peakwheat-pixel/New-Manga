---
task: FEA-11-RUN-GRANT-1
title: FEA-11-RUN-GRANT-1 r2 窄面复审（Review r1 findings 返修；Host best-effort / AC-R5 / L-G12）
reviewer: fresh subagent（独立上下文；未参与实现/返修/证据生成；只读被审 head）
session: fresh subagent（Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
worktree: clean（本报告写入前；写入后仅本报告为 untracked）
reviewed_head: 3ffabeb8134b355076a9e964305de895e7c5b9d1
verdict: changes_requested
---

# FEA-11-RUN-GRANT-1 r2 窄面复审

> **结论先行：`changes_requested`。P0=0 / P1=1→0（R1-01 已关闭）/ P2=2 / P3=2。**
>
> - **R1-01（P1）已实质修复，不是只改注释**：`04317256c` 新增可单测的 `RunSourceAuthorizer`，把能力探测失败、无相关源、registry 不可读、mint I/O 失败（含部分源）改为 **best-effort skip**；只有 `CoreOperationException`（Core 对请求/目标页的 typed 拒绝）原样抛出并阻断 dispatch。我独立实跑 `SourceRegistry` **17 passed**、真实 IPC **2 passed**，并自选破坏点（把 `SourceReadCoordinator.AuthorizeRunAsync` 的逐源 catch 改回 `throw;`）→ 目标 IPC 用例变红 → 按原字节恢复 + sha 复核一致。
> - **门禁数字全部为真**：定向 Python **50 passed**；`tests/core tests/fea09 tests/fea11` **1276 passed**；全量 pytest **3281 passed / 10 skipped**（我独立重跑，241.20s）；全量 .NET **1547 / 0 / 88**（我独立重跑，exit 0）；pins **18/18**；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；EV **27/27 sha256** 全匹配；`git diff 218775bca..3ffabeb81` **29 文件全部 ⊆ allowed_paths**、禁止面零 diff。
> - **不能 approve 的原因（均为小修，不是核心机制问题）**：
>   1. **R2-01（P2）**：L-G12/Handoff/EV/卡面把可用边界写成「image/**folder** 单 entry 源 + 归档首成员」，但 `RunSourceRange.Resolve` 用扩展名 `KindOf()` 判 kind，folder 目录被误判为 `image`，mint 时 `FileStream` 打不开目录 → `SOURCE_ENTRY_MISSING` 跳过。**folder 源在 Run 预授权路径上必然被跳过，folder 页仍不可用**；该边界声明不成立，且无 folder 测试。这是「口径不实」而非新增越权/数据问题。
>   2. **R2-02（P2）**：R1-02② 的「能力缺失 → 不 mint 且不抛」测试使用 `known: []`，即使把能力门整段删掉（甚至删掉目标范围检查）该测试仍会绿——**不判别**，因此 AC-R4 该子项的证据不成立。
>   3. **R2-03（P3）**：R1-02③ 只测了 `PreparedRunSlices` 与 `AuthorizePreparedRunAsync` seam；没有任何测试驱动 `HostRuntime.AcceptRunAsync` 的接线（删掉 `HostRuntime.cs:80-85` 的授权调用不会红）。
>   4. **R2-04（P3）**：卡 I-2 仍写「铸造失败 → typed，不 dispatch」「无法解析 → typed（不静默放行）」，与权威「Review r1 处置」及实现（best-effort skip）冲突；`RESOURCE-MANIFEST.json` 的 `source_path` 仍写 delivery head `7ff49f1cc`。
>
> **没有 P0/P1**；没有授权放宽、静默放行、数据破坏或未登记 wire/schema/依赖变化。R1-01/R1-04 的核心修复真实有效，但 R1-02②、R1-03（folder 口径）尚未闭合，故 r2 不能判 approved。

---

## 0. 复核对象、方法与边界

- 仓库 `G:\CODEX\New Manga`，`main`；复核开始 `HEAD=781523aab9f02f4c7a89a3cee98f77470b31b92e`（docs/evidence）；
  实现+测试 delivery head = `3ffabeb8134b355076a9e964305de895e7c5b9d1`（`git rev-parse` 实测）；
  修复 commit = `04317256c68a126321a6823bc5f8629890e58b44`；工作树 clean。
- 只读事实以 `3ffabeb81` 的实现/测试字节为准；工作树（`781523aab`）中代码/测试与 `3ffabeb81` 的对应文件逐字节一致（EV 27/27 复核可证）。
- 本复核**未参与**该卡实现、返修或证据生成；未 `git add`/`commit`/`push`；未删除/移动任何文件。
  唯一写入为 `doc/reviews/FEA-11-RUN-GRANT-1-r2.md`。
- 我运行了**仓内生成型工具** `verification/FEA-11-RUN-GRANT-1/tools/scope_validation.py` 与全量 .NET；
  两者分别重写了 tracked 的 `scope-validation.log`/`changed-files.txt` 与 `verification/FEA-09/logs/wire-redacted.ndjson`。
  已按原字节恢复并 sha256 复核（详见 §6.3）；恢复后工作树 clean。全量 .NET 的已知 FEA-09 副作用与 r1 一致，属运行副作用而非交付变更。
- 未运行 `tools/discrimination.py` 全脚本（它会重写被审的 `logs/discrimination.log`，本 Review 不得改写证据）；
  改为逐行核对 6 个破坏点定义/目标 + 独立复现 1 个自选破坏点（§6）。

### 0.1 本 Review 实跑命令与结果（全部实测）

| # | 命令 | 实测结果 |
|---|---|---|
| 1 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **50 passed** in 4.45s |
| 2 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"` | **17 passed / 0 failed / 0 skipped** |
| 3 | `$env:NEWMANGA_FEA11_IPC=1; dotnet test … --no-build --filter "FullyQualifiedName~Fea11RunGrant"` | **2 passed / 0 failed / 0 skipped** |
| 4 | `C:/Python314/python.exe -m pytest tests/core tests/fea09 tests/fea11 -q` | **1276 passed** in 79.64s |
| 5 | `C:/Python314/python.exe -m pytest tests -q` | **3281 passed / 10 skipped / 10 warnings** in 241.20s |
| 6 | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1547 passed / 0 failed / 88 skipped**（8 assemblies，exit 0；21+38+253+117+31+200+167+720） |
| 7 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，exit 0 |
| 8 | `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | `Governance check: PASS (3 warnings)`，exit 0 |
| 9 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md` | `Governance check: PASS (3 warnings)`，exit 0 |
| 10 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | EXIT=0（rendered counts match FEA-C07） |
| 11 | `git diff --name-status 218775bca..3ffabeb81` | **29 文件**，全部 ⊆ 卡 `allowed_paths`；禁止面零 diff；`CORE_PROTOCOL_MINOR=3` / `CoreProtocol.DefaultMinor=3` |
| 12 | EV.md 27 个 sha256 逐文件复算 | **OK=27 / MISMATCH=0 / MISSING=0** |
| 13 | 自选破坏性复跑（§6.1） | **RED + 字节级 RESTORED + sha 一致（218ed792…）** |

> `scope_validation.py` 在 `781523aab` 上重跑的结论为 `result=PASS changed=30 out_of_scope=[]`（多出的 1 个是 docs commit 新增的 r1 返修 Handoff；committed 证据是在 `3ffabeb81` 上生成的 `changed=29`，两者均 PASS；见 §6.3）。

---

## 1. 结论与判定摘要

| 项 | 判定 |
|---|---|
| P0 | **0** |
| P1 | **0**（R1-01 已关闭） |
| P2 | **2**（R2-01 L-G12 folder 边界不实；R2-02 能力缺失测试不判别） |
| P3 | **2**（R2-03 AcceptRun 接线未测；R2-04 卡 I-2/Manifest 旧口径残留） |
| A. R1-01 关闭 | **PASS** |
| B. AC-R5 修订口径 | **PASS**（Core managed + Host best-effort 均成立；folder 问题归入 L-G12/R2-01） |
| C. R1-02 四类测试 | **FAIL（部分）**：①④ 成立；② 不判别；③ 只到 seam，未测 HostRuntime 接线 |
| D. R1-03 L-G12/边界 | **FAIL**：扩写与 IPC 注释已改，但「folder 单 entry 源可用」不成立 |
| E. R1-04 typed 错误面/partial | **PASS**（代码 + 单测 + 真实 IPC partial） |
| F. P3 R1-05…R1-11 | **PASS（保留）**：R1-10 测试存在但弱（并入 R2-02） |
| G. 回归与证据 | **PASS**（50/1276/3281/1547/18/18/PASS/EXIT=0/EV 27/27/scope 29 文件） |
| H. 返修新问题 | **FAIL**（R2-01…R2-04） |
| AC-R1 | **MET** |
| AC-R2 | **MET（保留）** |
| AC-R3 | **MET（保留）** |
| AC-R4 | **PARTIAL**（②③） |
| AC-R5 | **MET**（Core managed + Host best-effort；folder 属 L-G12 口径问题） |
| AC-R6 | **MET** |
| AC-R7 | **PARTIAL**（L-G12 folder 边界；r2 未批准） |

---

## 2. A–H 逐项核验

### A. R1-01（P1）关闭：Host 预授权 best-effort —— **PASS**

- **代码是真实实现，不是注释**（`04317256c`）：
  - `SourceReadCoordinator.AuthorizeRunAsync`（`SourceReadCoordinator.cs:136-211`）逐源 `try/catch`；mint 失败仅累计 `skippedCodes`（`:160-179`）；**全部源失败时不发 Core 命令**并返回 `RunAuthorizationResult(0,0,...)`（`:180-184`）；部分失败继续为其余源铸 grant 并发命令（`:185-208`）。
  - `MapMintFailure`（`:215-222`）：`FileNotFound/DirectoryNotFound/UnauthorizedAccess → SOURCE_ENTRY_MISSING`、`IOException → FILE_IDENTITY_CHANGED`、`ArgumentException/NotSupportedException → SOURCE_ACCESS_DENIED`，无裸 `IOException` 逃逸；`IssueLockedAsync` 的 `FileStream` 打开/哈希/identity 读取均已包住（`:325-351`）。
  - `HostRuntime` 的新 `RunSourceAuthorizer`（`:1724-1912`）：
    - 能力缺失/探测异常 → `ProbeAsync` 返回 false → skip（`:1776-1779`、`:1893-1904`）；
    - 无相关源 → `targets.Count==0` → skip（`:1854-1857`）；
    - registry 不可读/无 known targets → catch 后 skip（`:1836-1847`）；
    - mint 失败（含 partial 结果 `result.Skipped`）→ skip（`:1858-1867`、`:1879-1883`）；
    - **只有 `CoreOperationException` 原样 rethrow**（`:1873-1878`），dispatcher 不 dispatch 并由 `ProjectRunError` 保留 code（`HostCommandDispatcher.cs:147-178`）。
  - dispatcher 钩子只在 4 个 step-triggering 命令上调用（`HostCommandDispatcher.cs:76-83,154-158`）；`RunCommandPolicy`（`HostRuntime.cs:1627-1634`）对 pause/stop/abandon 与只读命令返回 false。
- **独立实测**：`SourceRegistry` **17 passed**；真实 IPC **2 passed**；定向 Python **50 passed**。
- **自选破坏点**（§6.1）：把 coordinator 的逐源 catch 改回 `throw;` → `MintBindResolveAndRevoke_TypedWithNoPathLeak` 变红；恢复 sha 一致。
- **结论**：R1-01 的核心语义成立；Host 侧预授权失败不会再阻断一个 Core 本可接受的 managed-only/unrelated Run。

### B. AC-R5 修订口径 —— **PASS**

- 卡 AC-R5 新文本（`:129`）与「Review r1 处置」一致：**Core 授权面 managed 跳过 + Host best-effort 不阻断**；我核对实现与测试：
  - Core 面：`test_managed_targets_are_skipped_not_refused`（`tests/fea11/test_source_run_grant.py:942-971`）断言 `{"bound_pages": 0}`、`_bindings == {}`、逐表零写、provider 仍读 Managed Copy（宽高 = managed 旧图）、`TargetSnapshot.metadata` 键集合不变；该用例包含在 50 passed 中。
  - Host 面：`RunAuthorizationBestEffortSkipReachesDispatch_CoreRefusalDoesNot`（`SourceRegistryTests.cs:453-488`）真判别：
    - (a) mint（fake authorize）抛 `SourceAccessException` → dispatcher 走到真实 dispatch（无 Core 时 `SidecarException(ProcessExited)`），证明**没有被预授权阻断**；
    - (b) Core typed 拒绝 → `CoreOperationException` 原 code，且未 dispatch（未出现 `SidecarException`）。
  - 另有 `RunAuthorizerTreatsMintFailuresAsBestEffortSkips`、`RunAuthorizerSkipsWhenTheRegistryCannotBeRead`、`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`（后者不判别，见 R2-02）、IPC 的 missing/partial。
- **保留**：managed-only 的 Host 层「零行为变化」没有专门的 managed 页面测试（Host 不接触 page），但行为不依赖页面类型；AC-R5 要求的「mint 失败仍 dispatch」判别成立。
- **结论**：AC-R5 修订口径本身成立；folder 的可用性声明不在 AC-R5 文本内，归入 L-G12（R2-01）。

### C. R1-02（P2）四类测试 —— **FAIL（部分：2/4 判别）**

| 子项 | 判定 | 证据与问题 |
|---|---|---|
| ① pause/stop/abandon 不触发 | **PASS** | `RunCommandPolicyAuthorizesOnlyStepTriggeringCommands`（`SourceRegistryTests.cs:207-238`）+ `RunAuthorizerControlActionsPauseStopDoNotAuthorize`（`:347-364`）断言 pause/stop/abandon 下 `minted==0`、`resolved==0`；dispatcher 仍对 `library_control_run` 调用钩子（`HostCommandDispatcher.cs:154-158`），策略层消化。 |
| ② 能力缺失不 mint 不抛 | **FAIL（不判别）** | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`（`:296-308`）使用 `known: []`；即使删除 `AuthorizeForCommandAsync`/`AuthorizeSliceAsync` 的能力门，甚至删除 targets 检查，`_authorize` 仍不会被调用（无源可铸），`minted==0` 恒成立。没有「known 源 + probe=false + 计数 authorize」的用例。见 R2-02。 |
| ③ AcceptRun prepared slice | **FAIL（只到 seam）** | `PreparedRunSlicesTakeRequiresASameProcessPreparedRun`（`:410-438`）验证缺失/过期 → `RUN_STALE_PREVIEW`；`RunAuthorizerAcceptSeamUsesThePreparedSliceCommandAndScope`（`:389-408`）直接调 `AuthorizePreparedRunAsync`。**没有测试驱动 `HostRuntime.AcceptRunAsync`**（`HostRuntime.cs:71-88`），删掉 `:80-85` 的授权调用无测试会红。 `Fea10RunIpcTests` 用的是 `CoreServiceClient`，不经过 `HostRuntime`。见 R2-03。 |
| ④ RunSourceRange book/known=0/filtered=0/unresolved | **PASS** | `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`（`:240-272`）：book b1 过滤出 s1/s3；known=0 空；book b9 filtered=0 空；outside-root s4 计入 unresolved=1。语义与 R1-04 处置一致（unresolved 跳过，由 Core 对目标页 fail-closed）。 |

- **结论**：四类测试均存在，但 ② 的测试不能判别、③ 的生产接线未测；R1-02 不能按「FIXED（4/4）」关闭。

### D. R1-03（P2）L-G12/边界 —— **FAIL（边界包含 folder，但 folder 不可用）**

- **已做到的部分**：
  - 卡 L-G12（`:143`）已扩写为「version 通道 + 容器成员 entry 身份通道」，明确「多成员归档只有 ordinal=0 首成员可被授权」、follow-up 候选 `FEA-11-RUN-GRANT-2`；
  - Handoff §3（`:58`）、EV §7（`:160`）同步扩写；
  - `.NET IPC` 注释/断言语义已改为「p1 = 首成员 ordinal 命中、p2 = 多成员容器 fail-closed」（`Fea11RunGrantIpcTests.cs:80-84,106-116`），断言仍为 p1 `bound_pages=1` / p2 `SOURCE_ACCESS_DENIED`；
  - Python entry 粒度用例 docstring 已注明测试侧成员形状非生产 Host-mintable（`tests/fea11/test_source_run_grant.py:515-524`）。
- **未成立的部分（R2-01）**：三处文档均把可用边界写成「**image/folder** 单 entry 源 + 归档首成员」，但：
  - `RunSourceRange.Resolve` 用 `KindOf(normalized)`（`HostRuntime.cs:1700`），`KindOf` 只看扩展名（`:1706-1712`）：目录路径（folder 源）→ 无扩展名 → **`image`**；
  - `IssueLockedAsync` 对 `image` 走 `FileStream` 打开目录 → `UnauthorizedAccessException` → `MapMintFailure` → `SOURCE_ENTRY_MISSING` → 该源被 skip；
  - 若 Run 只有 folder 源（或 folder 页所在源），预授权整体 skip → Core 无 `_bindings` → folder 页 provider/commit 仍 typed 失败。**folder 不在可用边界内**。
  - 我用反射直接调用已构建的 `NewManga.Host.RunSourceRange.KindOf("...\\folder-source")` 得 **`image`**（zip → `zip`，png → `image`）；`FileStream` 打开目录实测抛 `UnauthorizedAccessException`（"Access to the path … is denied"）。这是代码路径级实证，不是猜测。
  - 该问题不是返修新引入的（r1 版本同样用扩展名 `KindOf`），但返修把 folder 写进 L-G12/Handoff/EV 的「可用边界」，构成 **R-11 不夸大** 与 R1-03 登记完整性的新缺口；且无任何 folder 预授权测试。
- **结论**：容器成员通道的扩写/注释是正确进展；「image/folder 单 entry 源」应改为「image 单 entry 源 + 归档首成员」，或修复 kind 检测并补 folder 用例。见 R2-01。

### E. R1-04（P2）MapMintFailure / partial unresolved —— **PASS**

- `MapMintFailure` 把 mint I/O/权限/路径错误映射到 C-16 §6 闭集（`SOURCE_ENTRY_MISSING`/`FILE_IDENTITY_CHANGED`/`SOURCE_ACCESS_DENIED`），单测 `RunSourceAuthorizerMapsMintIoFailuresToFrozenCodes`（`SourceRegistryTests.cs:440-451`）覆盖 4 类；真实 IPC 的 missing file（2b）实际走到 `SOURCE_ENTRY_MISSING`/`SOURCE_ACCESS_DENIED` 之一并被 skip（`Fea11RunGrantIpcTests.cs:118-135`）。
- partial：`AuthorizeRunAsync` 逐源跳过、其余继续 mint；IPC 2c 断言 `BoundPages=1, MintedGrants=1, SkippedSources=1`（`:137-149`）。
- partial unresolved：`RunSourceRange.Resolve` 将 registry 不匹配/路径不可规范化/超 64 的源计入 `unresolved` 并跳过（`HostRuntime.cs:1676-1703`）；`RunAuthorizerSkipsWhenTheRegistryCannotBeRead` 与 range 单测覆盖；`AuthorizeSliceAsync` 只记计数日志（`:1849-1853`），不阻断。与「Review r1 处置」R1-04 的「跳过该源、由 Core 对目标页 fail-closed」一致。
- **保留**：没有「unresolved 源对应的 referenced 页被 Core 拒绝」的专门端到端用例（Core 拒绝面由 AC-R3/其它用例覆盖）；不构成 P2。

### F. P3 R1-05…R1-11 —— **PASS（R1-10 保留）**

| Finding | 判定 | 证据 |
|---|---|---|
| R1-05 卡 I-1 响应形态 | **CLOSED** | 卡 `:83` 成功 `{bound_pages}`、整体 typed `SOURCE_ACCESS_DENIED`（`refused_pages`）、明确「不采用 `{bound_pages, refused}`」；实现 `core_service.py:5043-5044`。 |
| R1-06 grant_ids 重复 | **CLOSED** | 卡 `:88` 形状行「1..64 且唯一；重复 id → INVALID_REQUEST」；实现 `core_service.py:4970-4980`；测试注释 `tests/core/test_host_control.py:714-719`。 |
| R1-07 双 spy / per-page gate | **CLOSED** | `test_authorization_never_leases_or_reads_the_source`（`:908-934`）同时 spy `source_lease` 与 `read_entry_bytes` 并断言双 0；`test_per_page_gate_refusal_uses_the_shared_gate_predicate`（`:837-906`）用 mixed page 让 `authorize_run_bindings` 的 per-page `gate != open` 分支可达，断言 `refused_pages=1`、零映射、逐表零写。 |
| R1-08 host-only 零写口径 | **CLOSED** | host-only/session 用例新增 `_business_table_snapshot` 断言（`tests/core/test_host_control.py:651-687`），与 AC-R1 的「逐表快照」文字一致，未弱化 `total_changes`。 |
| R1-09 EV 装配描述 | **CLOSED** | EV §4 AC-R2 改为「RENDITION-1 同构 harness（in-memory migrations + `build_run_harness`），非 assemble —— R1-09 修正」；未再称 `assemble_core_services`。 |
| R1-10 Handoff 能力缺失单测 | **CLOSED（有保留）** | 测试存在（`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`），Handoff 表述与实测一致；但该测试不判别（R2-02）。 |
| R1-11 AcceptRun prepared-slice 行为 | **CLOSED（登记）** | Handoff §3 L-G14（`:60`）、EV §7（`:161`）登记「同进程先 PrepareRunAsync，否则 RUN_STALE_PREVIEW；App 无调用点」；实现 `HostRuntime.cs:80-85`。 |

### G. 回归与证据 —— **PASS**

- 实跑数字见 §0.1：50 / 1276 / 3281/10 / 1547/0/88 / 18/18 / PASS / EXIT=0；与 Handoff §2（`:39-48`）、EV §2（`:35-44`）、Lead 数（3281/10、1547/0/88）一致。
- EV 27/27 sha256 全匹配（11 实现/测试 + 14 证据 + 2 文档；EV 排除自身）。
- `git diff --name-status 218775bca..3ffabeb81` = 29 文件，全部 ⊆ allowed_paths；`doc/plan`、`doc/contracts`、`schema.py`、迁移、依赖、`core_assembly.py`、`NewManga.App/**`、`apps/**` 超出 3 个 Host 文件之外均零 diff；`PROTOCOL_MINOR=3`。
- 判别性 6/6 记录可信性：
  - B1（写绑定删除）、B2（facts 删除）、B3（原子性删除）、B4（command 域删除）、B5（dispatcher 钩子删除）、B6（Host best-effort 删除）的破坏文本与目标测试逐行核对（`tools/discrimination.py:29-103`）；目标测试均存在且与破坏语义对应；
  - 我未重跑全脚本（会改写被审证据）；我独立复现了一个**等价的 coordinator 级 best-effort 破坏**（§6.1）并取得 RED + RESTORED。
- **保留**：全量 .NET 会重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`（本次 sha `5a6dd7f8…`，5838 bytes），已按原字节恢复为 `548de629…`（5004 bytes）并复核；`scope_validation.py` 会重写自身日志（§6.3）。这是工具副作用，不是交付缺陷。

### H. 返修引入/暴露的新问题 —— **FAIL**

- **R2-01（P2）**：L-G12「folder 可用」不实（§D）；`KindOf` 的 kind 误判使 folder 预授权必然 skip；无 folder 测试。
- **R2-02（P2）**：能力缺失测试不判别（§C②）。
- **R2-03（P3）**：AcceptRun 生产接线未测（§C③）。
- **R2-04（P3）**：卡 I-2 旧口径与 Manifest 旧 head 残留（§7）。
- 未发现：授权放宽/静默放行、新 Run 面错误码、wire/minor/schema/依赖变化、测试删除或弱化、Token/路径泄漏、`SOURCE_*` 进入 `AllowedRunErrorCodes`。

---

## 3. R1-01…R1-11 逐条判定

| Finding | 判定 | 说明 |
|---|---|---|
| **R1-01（P1）** | **CLOSED** | `04317256c` 真实实现 best-effort；17/2/50 实跑；自选破坏点 RED+RESTORED；只有 Core typed 拒绝阻断（R-5）。 |
| **R1-02（P2）** | **OPEN（部分）** | ①④ PASS；② 测试不判别（R2-02）；③ 只测 seam，未测 `HostRuntime.AcceptRunAsync`（R2-03）。 |
| **R1-03（P2）** | **OPEN（部分）** | version + 容器成员 entry 扩写、IPC 注释、follow-up 均到位；但「folder 单 entry 源」不可用（R2-01），边界需收窄或修 kind。 |
| **R1-04（P2）** | **CLOSED** | MapMintFailure §6 映射 + 单测 + IPC missing/partial；partial unresolved 跳过语义有 range 单测。 |
| **R1-05（P3）** | **CLOSED** | 卡 I-1 响应形态已按契约；实现 `{bound_pages}`。 |
| **R1-06（P3）** | **CLOSED** | 1..64 唯一；重复 → `INVALID_REQUEST`；卡/测试注释一致。 |
| **R1-07（P3）** | **CLOSED** | `source_lease` + `read_entry_bytes` 双 spy；mixed per-page gate 用例。 |
| **R1-08（P3）** | **CLOSED** | `total_changes` + 业务表逐表快照；未弱化。 |
| **R1-09（P3）** | **CLOSED** | EV 改为 RENDITION-1 同构 harness。 |
| **R1-10（P3）** | **CLOSED（有保留）** | 单测存在，但不判别（并入 R2-02）；Handoff 文字已改为实测口径。 |
| **R1-11（P3）** | **CLOSED（登记）** | L-G14 已登记；App 无调用点。 |

---

## 4. AC-R1…R7 判定

| AC | 判定 | 理由 |
|---|---|---|
| **AC-R1** | **MET** | 50 passed 中 host-only/session、closed shape/未知键/空/65/重复/非字符串、缺失/过期/撤销 typed、零 DB 写（含逐表快照）、幂等、能力公告均有测试；错误 JSON 无路径。 |
| **AC-R2** | **MET（保留）** | 真实 `assemble_core_services` + 真实 zip/PNG/签名 grant；绑定后 provider 像素 = 当前 binding（12×7，非 managed 30×20）、commit guard 打开；commit 行数用 RENDITION-1 同构 harness（EV 已改正）。保留：grant 为测试侧成员 entry 形状（非 Host-mintable），已在 docstring/EV 说明。 |
| **AC-R3** | **MET（保留）** | 6 类 fail-closed typed、零业务写、不崩溃；`source_lease`+`read_entry_bytes` 双 0；mixed per-page gate 分支。保留：⑥ 仍是 provider/guard 面而非真在跑的 Run。 |
| **AC-R4** | **PARTIAL** | dispatcher 4 命令钩子、失败不 dispatch、低层 IPC、剪枝上界、range 过滤、pause/stop 成立；但 ② 能力缺失测试不判别、③ AcceptRun 生产接线未测。 |
| **AC-R5** | **MET** | Core managed `bound_pages=0`/零映射/零业务写/Managed Copy/metadata 6 键；Host best-effort 判别（mint 失败→dispatch；Core 拒绝→不 dispatch）；全量套件不降。folder 可用性属 L-G12 口径（R2-01），不在 AC-R5 文本。 |
| **AC-R6** | **MET** | 29 文件 ⊆ allowed_paths；禁止面零 diff；minor=3；Run wire 零改动；pins/check/API inventory 独立实测；全量 pytest/.NET 独立重跑不降。 |
| **AC-R7** | **PARTIAL** | EV 27/27、Handoff limitations（L-G1/2/8/9/10/11/12/13/14）、未宣称项均到位；但 L-G12 的 folder 边界不实（R2-01），r2 未批准，不能回填 MET。 |

---

## 5. 破坏性复跑记录（备份 / 变红 / 恢复 / sha）

### 5.1 自选破坏点（独立于证据 B6 的 coordinator 级变体）

| 项 | 内容 |
|---|---|
| 文件 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs` |
| 原始 sha256 | `218ed792496a4a8efb723da62abbbf8ceb8f935c43373b21417f83cdb1b969c7`（= EV §5.1） |
| 破坏内容 | 删除逐源 best-effort 的 `catch (…){ skipped++; skippedCodes.Add(…); }`，改为 `throw;`（mint 失败重新阻断） |
| 目标用例 | `NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrantIpcTests.MintBindResolveAndRevoke_TypedWithNoPathLeak`（真实 Python Core；命中 missing-file 分支） |
| 实测 | `dotnet test` **EXIT=1**，`1 failed / 1 passed`；失败栈穿过 `SourceReadCoordinator.AuthorizeRunAsync`（正是被破坏的逐源 catch） |
| mutated sha256 | `b825cfb903b277d77fa1fa93c4fefa4b0fdab62edb6719723f8d10dcf5c4f447` |
| 恢复 | 原始字节 `Copy` 回写；`RESTORED_SHA=218ed792…`，`RESTORE_MATCH=True`；`git status --porcelain -- <file>` 为空；`dotnet build NewManga.sln -c Release` exit 0 |
| 结论 | **RED + RESTORED（sha 一致）**；真实 IPC 的 best-effort 不是「注释级」实现 |

> 证据 B6（`logs/discrimination.log`）破坏的是 `HostRuntime.AuthorizeSliceAsync` 的最外层 catch，目标 `RunAuthorizationBestEffortSkipReachesDispatch`；我核对了脚本 `tools/discrimination.py:74-88` 与日志的 RED/RESTORED/sha `0114b580…`，并独立做了 coordinator 级等价破坏。两者互补：B6 证明编排层 skip 被测试判别，我的破坏证明真实 mint 层 skip 被 IPC 判别。

### 5.2 证据 B1–B5 的可信性（未重跑全脚本）

- B1 写绑定删除 → `test_real_assembly_bound_grant_opens_the_run_target_provider_and_guard`；B2 facts 删除 → `test_scope_and_facts_mismatch_is_refused`；B3 原子性删除 → `test_authorization_is_entry_granular_and_refuses_other_pages`；B4 command 域删除 → `test_forged_shape_requests_are_invalid_requests`；B5 dispatcher 钩子删除 → `SourceRegistryTests.RunAuthorizationHookBlocksDispatchAndIsNotCalledForReadOnlyRuns`。
- 逐行核对：破坏文本与目标测试语义一一对应（`tools/discrimination.py:29-103`）；目标测试在 50/17 实跑中均存在；日志的 `exit_code=1 verdict=RED_AS_EXPECTED`、`restore=RESTORED sha256=…` 与 EV 中对应文件 sha 一致；`final_rebuild exit_code=0`。可信。
- 未重跑原因：`discrimination.py` 会重写被审的 `logs/discrimination.log`，本 Review 不得改写证据字节。

### 5.3 运行副作用与逐字节恢复

| 文件 | 运行后 sha256 | 恢复后 sha256 | 复核 |
|---|---|---|---|
| `verification/FEA-11-RUN-GRANT-1/changed-files.txt` | （被 scope_validation.py 重写） | `8df8ea434a09364b67bc770aa26ca9015877b3dfb61c33aa82f32c26ff6446b1` | 与 HEAD blob/EV 一致；`git status` clean |
| `verification/FEA-11-RUN-GRANT-1/scope-validation.log` | （被 scope_validation.py 重写） | `3dd4c89ed5212c88bfc7c21e2fbb0252eccea8ce8bd39b116d3102a9ca05c613` | 与 HEAD blob/EV 一致；`git status` clean |
| `verification/FEA-09/logs/wire-redacted.ndjson` | `5a6dd7f82c950bc4a73c2297b3f92d031eff41913b7611c2e3b24f10dad520ea`（5838 bytes，全量 .NET 副作用） | `548de629d163d80b9cd8d1e62251de2016782e46a0c48a48575749d2a059d593`（5004 bytes） | **一致**；`git status` clean |

- 恢复方式：从 HEAD blob / 运行前备份读取**原始字节**回写（不经过文本重编码），再对相同 Git OID 的索引项做 stat 刷新（`git update-index --cacheinfo <mode>,<oid>,<path>`；OID 未变、无内容 staged）。未使用 `git add`/`commit`/`push`。
- `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/fixtures/` 下新增的测试夹具目录为仓外运行产物，未删除（与 r1 一致）；仓内 tracked 字节最终零变化。

---

## 6. 新 findings

| ID | 严重度 | 事实 | 最小修复 | 是否阻断 |
|---|---|---|---|---|
| **R2-01** | **P2** | **L-G12 的「folder 单 entry 源可用」不成立，且无测试**：`RunSourceRange.Resolve` 用 `KindOf(normalized)`（`HostRuntime.cs:1700`），`KindOf` 只看扩展名（`:1706-1712`）；folder 目录 → `image`；`IssueLockedAsync` 对 image 走 `new FileStream(directoryPath, …)` → `UnauthorizedAccessException` → `MapMintFailure` → `SOURCE_ENTRY_MISSING` → skip（`SourceReadCoordinator.cs:325-334,215-222`）。folder-only/unrelated Run 会整体 skip 预授权，folder 页仍无 `_bindings`。反射实证：`RunSourceRange.KindOf("<…>\\folder-source")` = `image`；`FileStream` 打开目录抛 `UnauthorizedAccessException`。卡 `:143`、Handoff `:58`、EV `:160` 均写「image/folder 单 entry 源 + 归档首成员」。这不是新增越权/数据问题，但与 R-11「不夸大」及 R1-03 完整性冲突。 | ①在 `RunSourceRange.Resolve` 使用 `target.SourceKind`（冷启动枚举已携带 `folder`），并以 `Directory.Exists` 兜底；或 ②把 L-G12/Handoff/EV/AC-R7 的边界改为「image 单 entry 源 + 归档首成员」并登记 folder limitation；无论哪种，补一个 folder 预授权测试（或明确登记无法判别）。 | 是（当前交付自述与行为不一致；小修） |
| **R2-02** | **P2** | **R1-02② 的测试不判别**：`RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`（`SourceRegistryTests.cs:296-308`）用 `known: []`、`entries: []`；能力门/目标检查即使全部删除，`_authorize` 也不会被调用，`minted==0` 恒成立。R1-02 的「能力缺失 → 不 mint 且不抛」证据不成立，AC-R4 该子项不能算判别性覆盖。 | 改为 `known: [ScanTarget(...)]` + `entries: [RegistryEntry(...)]`，`authorize` 计数；`probe:false` 下断言 0 调用、不抛；并做一次「删 probe 门 → 测试变红」验证（可选）。 | 是（AC-R4 证据；小修） |
| **R2-03** | **P3** | **R1-02③ 只测 seam，未测生产接线**：`PreparedRunSlicesTakeRequires…` 与 `RunAuthorizerAcceptSeamUsesThePreparedSliceCommandAndScope` 分别测 ledger 与 `AuthorizePreparedRunAsync`；`HostRuntime.AcceptRunAsync`（`HostRuntime.cs:71-88`）的 `_preparedSlices.Take` + `AuthorizePreparedRunAsync` 调用没有测试驱动；`Fea10RunIpcTests` 使用 `CoreServiceClient`，绕开 `HostRuntime`。删掉 `HostRuntime.cs:80-85` 不会红。 | 增加一个 `HostRuntime` 级测试（fake Core/authorizer 或内部 seam），断言 AcceptRun 正常路径调用授权、缺失/过期 slice → `RUN_STALE_PREVIEW`；若不可行，按处置允许的方式在 Handoff/EV 登记 limitation，不由 AC-R4 宣称判别。 | 否（但 AC-R4 维持 PARTIAL） |
| **R2-04** | **P3** | **卡 I-2 仍写旧口径**：`:96` 「失败 → typed，不 dispatch」、`:99` 「无法解析 → typed（不静默放行）」，与「Review r1 处置」R1-01/R1-04 及实现（Host 侧失败 skip；只有 Core typed 拒绝阻断）冲突。另 `RESOURCE-MANIFEST.json` 的 `source_path` 仍写 `delivery head 7ff49f1cc`（应为 `3ffabeb81`）。 | 在 I-2 行加「Review r1 修订」注记（best-effort skip；unresolved 跳过、由 Core 对目标页 fail-closed）；重生成 Manifest 的 source_path/head（不改变 973 文件聚合事实）。 | 否（文档/证据精度） |

> 说明：R2-01 不是返修新引入的代码行为（r1 版同样用扩展名 `KindOf`）；但返修把「folder」写进了 L-G12 可用边界与 AC-R7 的验收叙述，属于本次交付必须修正的**口径**问题。R2-02 是返修新增测试的判别力问题。R2-03/R2-04 是覆盖/文档残留。

---

## 7. 返修行为审计（是否引入新回归/未登记 API/测试弱化）

- **API 变更**：`SourceReadCoordinator.AuthorizeRunAsync` 返回类型由 `Task<int>` 改为 `Task<RunAuthorizationResult>`；新增 Host 程序集 public 类型 `RunAuthorizationResult`/`PreparedRunSlices`/`RunCommandPolicy`/`RunSourceRange`/`RunSourceAuthorizer`。仓内调用点只有 IPC 测试与 `RunSourceAuthorizer`（已更新）；`NewManga.App` 无调用点；API inventory `--check` EXIT=0。未登记的外部 API 面不变。
- **行为变更**：`HostRuntime.AcceptRunAsync` 仍要求同进程 `PrepareRunAsync`（R1-11/L-G14 已登记）；`RunAuthorizationResult` 的 `Skipped` 仅在「一个 grant 都没铸出」时为 true，partial 不为 true（IPC 2c 实证）。`PreparedRunSlices` 的 `Take` 在成功后不删除（名字略宽，但不影响 bounded 32 上界与 Core 侧幂等）；未发现数据/安全问题。
- **测试弱化/删除**：`git diff 218775bca..3ffabeb81 -- tests/` 无删除既有断言（R-12 两文件仅 capabilities 期望 +1 + 注释）；新增 skip 仅 2 个既有 opt-in IPC；未发现「删断言换绿」。
- **注释与实现**：`RunSourceAuthorizer`/`PreparedRunSlices`/`RunSourceRange` 的注释与实现基本一致；唯一注释与行为冲突的是卡 I-2 的旧口径（R2-04，文档而非代码注释）。`HostCommandDispatcher` 的钩子注释称「a typed authorization failure … means the Run command is NEVER dispatched」——在 best-effort 下只有 `CoreOperationException` 才会阻止；代码先由 `RunSourceAuthorizer` 消化 Host 失败，所以注释在「typed」范围内仍成立（Host 失败不是 typed 拒绝），不是新错误。
- **无 `SOURCE_*` 进入 Run 面错误码**：`HostCommandRegistry.AllowedRunErrorCodes` 未新增；dispatcher 对非白名单 code 仍降级 category=unknown（`HostCommandDispatcher.cs:188-207`）。

---

## 8. 最终 verdict 与理由

**`changes_requested`。**

- **通过的部分**：R1-01 的 Host best-effort 修复真实、可判别（17/2/50 实跑 + 自选破坏点 RED/RESTORED）；R1-04 typed 错误面闭合；R1-05…R1-11 文档/测试处置基本到位；全量门禁（pytest 3281/10、.NET 1547/0/88、pins 18/18、check PASS、API EXIT=0、EV 27/27、scope 29 文件）全部为真；没有 P0/P1、越权、静默放行或数据破坏。
- **不能 approve 的部分**：
  1. **R2-01（P2）**：L-G12/Handoff/EV/AC-R7 的「folder 可用边界」与实现不符（folder 预授权必然 skip），且无测试；这是 R1-03 的完整性缺口，也是 R-11 的诚实性缺口。
  2. **R2-02（P2）**：R1-02② 的能力缺失测试不判别，AC-R4 的证据不能按「判别性测试」计。
  3. **R2-03（P3）**：AcceptRun 生产接线未测（只到 seam）。
  4. **R2-04（P3）**：卡 I-2 旧口径与 Manifest 旧 head 残留。
- **最小返修建议**（不改变 Core 机制）：
  1. `RunSourceRange.Resolve` 用 `target.SourceKind`（或 `Directory.Exists`）判定 folder，补 folder 预授权用例；若暂不支持 folder，则把 L-G12/Handoff/EV/AC-R7 的边界收窄为「image 单 entry 源 + 归档首成员」并登记 folder limitation。
  2. 把能力缺失用例改成「known 源 + probe=false + 计数 authorize」并断言 0 调用。
  3. 增加 `HostRuntime.AcceptRunAsync` 的接线测试，或按处置允许的方式登记 limitation。
  4. 修卡 I-2 的旧口径；重生成 Manifest 的 `source_path`/head（或加注记）。
- **复审建议**：上述 1/2 修完后由 Lead 做一次 r3 窄面复核（或由 DSH 以书面裁决接受 P2 降级并登记 limitation）；在 r2 未批准前不得 closeout。

---

## 9. 真实性声明

- 本报告是 fresh 上下文独立只读 Review：未参与 `FEA-11-RUN-GRANT-1`（或 PREREQ-1）的实现、返修、证据生成或 Handoff 编写；未在同一会话中实现该变更。
- 唯一写入是 `doc/reviews/FEA-11-RUN-GRANT-1-r2.md`（本文件）。未修改实现、测试、证据、卡、契约、STATUS/PLAN/LEDGER；未 `git add`/`commit`/`push`；未删除/移动/归档任何文件。
- 破坏性复跑记录见 §5：修改前备份、运行目标用例、按原始字节恢复、sha256 复核一致（`218ed792…`），`git status --porcelain -- <file>` 为空；随后 `dotnet build` exit 0。
- 运行副作用已恢复：`scope_validation.py` 重写的 `changed-files.txt`/`scope-validation.log` 与全量 .NET 重写的 `verification/FEA-09/logs/wire-redacted.ndjson` 均按原始字节恢复并 sha 复核（`8df8ea43…`、`3dd4c89e…`、`548de629…`）；最终 `git status --porcelain` 为空。
- 全量 pytest/.NET、定向测试与真实 IPC 在仓外隔离根 `G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/fixtures/` 下生成测试夹具目录；这是测试运行的预期产物，未删除。
- 未执行项（`tools/discrimination.py` 全脚本、folder Run 端到端实跑）已明确标注；folder 结论由代码路径 + `KindOf` 反射 + `FileStream` 目录行为实证，未以静态判断冒充实测。
- 本报告所有「实测」均有命令与结果记录；门禁数字与 EV/Handoff 对照见 §0.1/§G。
